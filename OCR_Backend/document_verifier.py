"""
document_verifier.py
---------------------
The VERIFICATION / VALIDATION layer that runs after field extraction.

>>> IMPORTANT <<<
This does NOT verify a document against any government database, and it
cannot tell you whether a certificate is genuine or forged. It performs
LOCAL, INTERNAL sanity checks only: "is the information we extracted
self-consistent and usable by the rest of the system?"

The three outcomes we care about are kept strictly separate:

    MISSING     the field was simply not in the document.
                -> reported in `missing_fields`, does NOT make the
                   document invalid.

    INVALID     the field WAS in the document but is unusable
                (impossible date, negative income, unreadable name).
                -> reported in `issues`, DOES make the document invalid.

    EXTRACTED   the field was found and passed its checks.
                -> reported in `extracted_fields`.

That distinction is the whole point of this file: an income certificate
that never mentions a gender is perfectly fine and must not be rejected,
whereas one claiming a date of birth of 32/13/2002 needs flagging.
"""

from datetime import date

import field_extractor
from field_extractor import (
    FIELD_NAMES,
    LABEL_BASED_FIELDS,
    MAX_REASONABLE_AGE,
    MIN_REASONABLE_AGE,
    SUPPORTED_CATEGORIES,
    SUPPORTED_GENDERS,
)

# The earliest birth year we are willing to believe. Anything older is
# almost certainly an OCR misread rather than a real citizen.
EARLIEST_PLAUSIBLE_BIRTH_YEAR = 1900

# An annual income above this is treated as OCR noise (for example an
# Aadhaar or account number accidentally read as an income figure).
# 100 crore is far beyond any government-scheme applicant.
MAX_PLAUSIBLE_ANNUAL_INCOME = 1_000_000_000

# `age` and `date_of_birth` are allowed to disagree by this much, because
# rounding and "as on 1st January" style wording is common on certificates.
AGE_DOB_TOLERANCE_YEARS = 1

# Friendly message used when a label was clearly present in the document
# but its value could not be understood.
_UNREADABLE_MESSAGES = {
    "name": "Name could not be read reliably from the document",
    "date_of_birth": "Date of birth could not be parsed",
    "age": "Age could not be parsed",
    "gender": "Gender could not be recognised",
    "annual_income": "Annual income could not be parsed",
    "state": "State could not be read reliably from the document",
    "district": "District could not be read reliably from the document",
    "address": "Address could not be read reliably from the document",
}


def verify_extracted_data(extracted_data, raw_text=None):
    """Run all internal validity checks on a dict of extracted fields.

    Args:
        extracted_data: dict as produced by
            `field_extractor.extract_fields`. Missing keys are tolerated,
            so this never crashes on a partial dict.
        raw_text: the original OCR text (optional). When provided we can
            additionally spot the "the label was there but we could not
            read its value" case and report it as an issue rather than
            silently calling the field missing.

    Returns:
        {
            "is_valid": bool,          # True when `issues` is empty
            "issues": [str, ...],      # invalid information
            "missing_fields": [...],   # not present in the document
            "extracted_fields": [...], # found and valid
        }
    """
    data = dict(extracted_data or {})

    issues = []

    # --- 1. Name --------------------------------------------------------
    name = data.get("name")
    if name is not None:
        if not _looks_like_a_real_name(name):
            issues.append("Extracted name does not look like a valid name")

    # --- 2. Date of birth ----------------------------------------------
    date_of_birth = data.get("date_of_birth")
    born = None
    if date_of_birth is not None:
        born = field_extractor.parse_date(date_of_birth)
        if born is None:
            issues.append("Invalid date of birth")
        elif born > date.today():
            issues.append("Date of birth is in the future")
        elif born.year < EARLIEST_PLAUSIBLE_BIRTH_YEAR:
            issues.append("Date of birth is unrealistically old")

    # --- 3. Age ---------------------------------------------------------
    age = data.get("age")
    if age is not None:
        if not isinstance(age, int) or isinstance(age, bool):
            issues.append("Age is not a whole number")
        elif not MIN_REASONABLE_AGE <= age <= MAX_REASONABLE_AGE:
            issues.append(
                f"Age is outside the expected range "
                f"({MIN_REASONABLE_AGE}-{MAX_REASONABLE_AGE})"
            )
        elif born is not None:
            # Internal consistency: a stated age must roughly agree with
            # the stated date of birth.
            age_from_dob = field_extractor.calculate_age(date_of_birth)
            if (age_from_dob is not None
                    and abs(age_from_dob - age) > AGE_DOB_TOLERANCE_YEARS):
                issues.append("Age does not match the date of birth")

    # --- 4. Gender ------------------------------------------------------
    gender = data.get("gender")
    if gender is not None and gender not in SUPPORTED_GENDERS:
        issues.append(
            "Gender is not one of the supported values: "
            + ", ".join(SUPPORTED_GENDERS)
        )

    # --- 5. Category ----------------------------------------------------
    category = data.get("category")
    if category is not None and category not in SUPPORTED_CATEGORIES:
        issues.append(
            f"Category '{category}' could not be normalised to one of: "
            + ", ".join(SUPPORTED_CATEGORIES)
        )

    # --- 6. Annual income ----------------------------------------------
    annual_income = data.get("annual_income")
    if annual_income is not None:
        if isinstance(annual_income, bool) or not isinstance(
            annual_income, (int, float)
        ):
            issues.append("Annual income is not a number")
        elif annual_income < 0:
            issues.append("Annual income cannot be negative")
        elif annual_income > MAX_PLAUSIBLE_ANNUAL_INCOME:
            issues.append("Annual income is unrealistically high")

    # --- 7. State / district / address ----------------------------------
    for field, label in (
        ("state", "State"),
        ("district", "District"),
        ("address", "Address"),
    ):
        value = data.get(field)
        if value is not None and not str(value).strip():
            issues.append(f"{label} was extracted but is empty")

    # --- 8. Labels we saw but could not read ----------------------------
    issues.extend(_find_unreadable_labels(data, raw_text))

    missing_fields, extracted_fields = _split_missing_and_extracted(data)

    return {
        "is_valid": len(issues) == 0,
        "issues": issues,
        "missing_fields": missing_fields,
        "extracted_fields": extracted_fields,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# A believable name is mostly letters. OCR garbage such as "|1@#~" or
# "XX//__" fails this check.
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 80
MIN_NAME_LETTER_RATIO = 0.6


def _looks_like_a_real_name(name):
    """Cheap, explainable garbage filter for OCR'd names.

    A name passes when it is a sensible length, contains at least one run
    of two or more letters, and is mostly made of letters (spaces are not
    counted either way).
    """
    if not isinstance(name, str):
        return False

    name = name.strip()
    if not MIN_NAME_LENGTH <= len(name) <= MAX_NAME_LENGTH:
        return False

    # At least one real word of two or more letters.
    if not any(len(part) >= 2 for part in _letter_runs(name)):
        return False

    non_space = [character for character in name if not character.isspace()]
    if not non_space:
        return False

    letters = [character for character in non_space if character.isalpha()]
    return (len(letters) / len(non_space)) >= MIN_NAME_LETTER_RATIO


def _letter_runs(text):
    """Split text into consecutive runs of alphabetic characters."""
    runs = []
    current = ""
    for character in text:
        if character.isalpha():
            current += character
        elif current:
            runs.append(current)
            current = ""
    if current:
        runs.append(current)
    return runs


def _find_unreadable_labels(data, raw_text):
    """Report fields whose label was in the document but whose value we
    could not understand.

    Without this check, "Annual Income: Rs. ABCDEF" would look exactly
    like a document that never mentioned income at all - but the first is
    a data-quality problem the user should know about, and the second is
    perfectly normal.
    """
    if not raw_text:
        return []

    issues = []
    label_values = field_extractor.extract_label_values(raw_text)

    for field in LABEL_BASED_FIELDS:
        if field not in _UNREADABLE_MESSAGES:
            continue
        label_was_present = bool(label_values.get(field))
        value_was_understood = data.get(field) is not None

        if label_was_present and not value_was_understood:
            # Special case: a stated age is not an issue when we could
            # still work the age out from the date of birth.
            if field == "age" and data.get("date_of_birth"):
                continue
            issues.append(_UNREADABLE_MESSAGES[field])

    return issues


def _split_missing_and_extracted(data):
    """Sort every field into "not found" vs "found", for the response.

    `document_type` counts as found only when it is not "Unknown".
    """
    missing_fields = []
    extracted_fields = []

    for field in FIELD_NAMES:
        value = data.get(field)

        if field == "document_type":
            found = bool(value) and value != "Unknown"
        else:
            found = value is not None

        (extracted_fields if found else missing_fields).append(field)

    return missing_fields, extracted_fields
