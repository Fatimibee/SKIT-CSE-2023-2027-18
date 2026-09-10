"""
test_field_extractor.py
------------------------
Unit tests for field_extractor.py (no HTTP layer, no OCR involved - these
feed in plain strings that stand in for OCR output).

All test text is SYNTHETIC. No real person's document, Aadhaar number,
phone number or address appears anywhere in this repository.
"""

import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from field_extractor import (  # noqa: E402
    FIELD_NAMES,
    calculate_age,
    clean_district,
    detect_document_type,
    extract_date_of_birth,
    extract_fields,
    normalize_category,
    normalize_gender,
    normalize_text,
    parse_income,
)


# ---------------------------------------------------------------------------
# The canonical sample from the task description.
# ---------------------------------------------------------------------------
INCOME_CERTIFICATE_TEXT = """
INCOME CERTIFICATE

Name: Rahul Sharma
Date of Birth: 12/05/2002
Gender: Male
Category: OBC
Annual Income: Rs. 1,80,000
State: Rajasthan
District: Jaipur
"""


@pytest.fixture
def income_certificate_fields():
    return extract_fields(INCOME_CERTIFICATE_TEXT)


# ===========================================================================
# 1-7. The individual fields, using the canonical sample
# ===========================================================================

def test_extract_name(income_certificate_fields):
    assert income_certificate_fields["name"] == "Rahul Sharma"


def test_extract_date_of_birth(income_certificate_fields):
    assert income_certificate_fields["date_of_birth"] == "12/05/2002"


def test_extract_gender(income_certificate_fields):
    assert income_certificate_fields["gender"] == "Male"


def test_extract_category(income_certificate_fields):
    assert income_certificate_fields["category"] == "OBC"


def test_extract_annual_income(income_certificate_fields):
    assert income_certificate_fields["annual_income"] == 180000


def test_extract_state(income_certificate_fields):
    assert income_certificate_fields["state"] == "Rajasthan"


def test_extract_district(income_certificate_fields):
    assert income_certificate_fields["district"] == "Jaipur"


def test_age_is_derived_from_date_of_birth(income_certificate_fields):
    # Calculated against today's date, so we compare against the same
    # helper rather than hard-coding a number that would rot over time.
    assert income_certificate_fields["age"] == calculate_age("12/05/2002")


def test_extract_fields_always_returns_every_supported_field():
    fields = extract_fields(INCOME_CERTIFICATE_TEXT)
    assert set(fields.keys()) == set(FIELD_NAMES)


# ===========================================================================
# 8. Document type detection
# ===========================================================================

def test_detect_income_certificate(income_certificate_fields):
    assert income_certificate_fields["document_type"] == "Income Certificate"


def test_detect_caste_certificate():
    text = "CASTE CERTIFICATE\nName: Priya Verma\nCaste: Scheduled Caste"
    assert detect_document_type(text) == "Caste Certificate"


def test_detect_residence_certificate():
    text = "DOMICILE CERTIFICATE\nThis is to certify permanent resident status."
    assert detect_document_type(text) == "Residence Certificate"


def test_detect_aadhaar_document():
    text = "GOVERNMENT OF INDIA\nUnique Identification Authority of India\nAadhaar"
    assert detect_document_type(text) == "Aadhaar Card"


def test_unrecognised_document_type_is_unknown():
    text = "Some random scanned page with no useful heading at all."
    assert detect_document_type(text) == "Unknown"


def test_empty_text_document_type_is_unknown():
    assert detect_document_type("") == "Unknown"


# ===========================================================================
# 9. Missing fields
# ===========================================================================

def test_missing_fields_return_none_and_do_not_crash():
    # Only a name is present; everything else must come back as None
    # rather than being guessed at.
    fields = extract_fields("Name: Sunita Devi")

    assert fields["name"] == "Sunita Devi"
    for field in ("date_of_birth", "age", "gender", "category",
                  "annual_income", "state", "district", "address"):
        assert fields[field] is None, f"{field} should not have been guessed"


def test_completely_empty_text_returns_all_none():
    fields = extract_fields("")

    assert fields["document_type"] == "Unknown"
    for field in FIELD_NAMES:
        if field != "document_type":
            assert fields[field] is None


def test_none_input_does_not_crash():
    fields = extract_fields(None)
    assert fields["name"] is None
    assert fields["document_type"] == "Unknown"


# ===========================================================================
# 10. Invalid date of birth
# ===========================================================================

def test_impossible_date_is_still_reported_not_silently_dropped():
    # 32/13/2002 is not a real date. The extractor keeps it (so the
    # verifier can flag it) instead of pretending the field was absent.
    fields = extract_fields("Date of Birth: 32/13/2002")
    assert fields["date_of_birth"] == "32/13/2002"
    # An unusable date must not produce a made-up age.
    assert fields["age"] is None


def test_dob_with_no_date_in_it_returns_none():
    assert extract_date_of_birth("not available") is None


def test_calculate_age_returns_none_for_invalid_date():
    assert calculate_age("32/13/2002") is None
    assert calculate_age(None) is None


def test_calculate_age_returns_none_for_future_date():
    tomorrow = date.today() + timedelta(days=1)
    assert calculate_age(tomorrow.strftime("%d/%m/%Y")) is None


def test_calculate_age_is_exact_on_a_birthday():
    today = date(2026, 6, 15)
    assert calculate_age("15/06/2000", today=today) == 26
    # One day before the birthday, they are still 25.
    assert calculate_age("16/06/2000", today=today) == 25


# ===========================================================================
# 11. Invalid / varied income
# ===========================================================================

@pytest.mark.parametrize("raw_value,expected", [
    ("Rs. 1,80,000", 180000),
    ("\u20b9180000", 180000),          # rupee symbol
    ("INR 1,80,000/- per annum", 180000),
    ("180,000", 180000),
    ("1.8 Lakh", 180000),
    ("2 Crore", 20000000),
    ("Rs 95,000 (Rupees Ninety Five Thousand Only)", 95000),
    ("0", 0),
])
def test_income_formats_are_parsed(raw_value, expected):
    assert parse_income(raw_value) == expected


@pytest.mark.parametrize("raw_value", ["", None, "not stated", "N/A", "ABCDEF"])
def test_unparseable_income_returns_none(raw_value):
    assert parse_income(raw_value) is None


def test_unparseable_income_in_document_returns_none():
    fields = extract_fields("INCOME CERTIFICATE\nAnnual Income: Rs. ABCDEF")
    assert fields["annual_income"] is None


# ===========================================================================
# 12. Noisy OCR text
# ===========================================================================

NOISY_TEXT = """
GOVERNMENT  OF  RAJASTHAN
CASTE   CERTIFICATE

NAME  -   PRIYA   VERMA
Father's Name: Suresh Verma
D.O.B  :  05-11-1998
Sex : Female
Caste : Scheduled Caste
District  :  Kota
"""


def test_noisy_ocr_text_is_still_extracted():
    fields = extract_fields(NOISY_TEXT)

    # Extra spaces collapsed, SHOUTED name converted to Title Case,
    # "-" used as the separator instead of ":".
    assert fields["name"] == "Priya Verma"
    # "D.O.B" label and a "-" separated date normalised to DD/MM/YYYY.
    assert fields["date_of_birth"] == "05/11/1998"
    assert fields["gender"] == "Female"
    assert fields["category"] == "SC"
    assert fields["district"] == "Kota"
    # No "State:" label anywhere - picked up from the header instead.
    assert fields["state"] == "Rajasthan"
    assert fields["document_type"] == "Caste Certificate"


def test_relatives_name_is_not_used_as_the_applicant_name():
    fields = extract_fields(NOISY_TEXT)
    assert "Suresh" not in (fields["name"] or "")


def test_name_of_father_layout_is_also_rejected():
    text = "Name of Father: Suresh Kumar\nName of Applicant: Ramesh Kumar"
    assert extract_fields(text)["name"] == "Ramesh Kumar"


def test_several_fields_on_one_line_are_all_extracted():
    # OCR frequently flattens a printed form onto a single line.
    text = "Name: Anita Devi   DOB: 01/01/1990   Gender: F"
    fields = extract_fields(text)

    assert fields["name"] == "Anita Devi"
    assert fields["date_of_birth"] == "01/01/1990"
    assert fields["gender"] == "Female"


def test_label_alone_on_its_line_reads_the_value_below():
    text = "INCOME CERTIFICATE\nName\nSunita Devi\nAnnual Income\nRs 95,000"
    fields = extract_fields(text)

    assert fields["name"] == "Sunita Devi"
    assert fields["annual_income"] == 95000


def test_document_heading_is_not_mistaken_for_a_field_value():
    # "INCOME CERTIFICATE" contains the word "income" and "CASTE
    # CERTIFICATE" contains "caste" - neither may become a field value.
    income = extract_fields("INCOME CERTIFICATE\nName: Rahul Sharma")
    assert income["annual_income"] is None

    caste = extract_fields("CASTE CERTIFICATE\nName: Rahul Sharma")
    assert caste["category"] is None


def test_address_containing_a_field_word_is_not_read_as_that_field():
    # "Near State Bank" must not be read as State = "Bank".
    fields = extract_fields("Address: Near State Bank, Talwandi\nDistrict: Kota")
    assert fields["state"] is None
    assert fields["district"] == "Kota"


def test_pure_garbage_text_extracts_nothing_and_does_not_crash():
    fields = extract_fields("@@@ ###\n|||| ~~~~\n8237 ***")
    assert fields["name"] is None
    assert fields["document_type"] == "Unknown"


# ===========================================================================
# Hindi (Devanagari) labels
# ===========================================================================

def test_hindi_labels_are_supported():
    text = (
        "\u0928\u093e\u092e: \u0930\u093e\u0939\u0941\u0932 "
        "\u0936\u0930\u094d\u092e\u093e\n"
        "\u091c\u0928\u094d\u092e \u0924\u093f\u0925\u093f: 12/05/2002\n"
        "\u0932\u093f\u0902\u0917: \u092a\u0941\u0930\u0941\u0937\n"
        "\u0935\u093e\u0930\u094d\u0937\u093f\u0915 \u0906\u092f: 180000\n"
        "\u0930\u093e\u091c\u094d\u092f: "
        "\u0930\u093e\u091c\u0938\u094d\u0925\u093e\u0928\n"
    )
    fields = extract_fields(text)

    assert fields["name"] == "\u0930\u093e\u0939\u0941\u0932 \u0936\u0930\u094d\u092e\u093e"
    assert fields["date_of_birth"] == "12/05/2002"
    assert fields["gender"] == "Male"
    assert fields["annual_income"] == 180000
    # Hindi state name normalised to its English spelling.
    assert fields["state"] == "Rajasthan"


# ===========================================================================
# Normalization helpers
# ===========================================================================

@pytest.mark.parametrize("raw_value,expected", [
    ("Male", "Male"), ("MALE", "Male"), ("m", "Male"), ("M", "Male"),
    ("Female", "Female"), ("f", "Female"), ("FEMALE", "Female"),
    ("Transgender", "Other"), ("Other", "Other"),
    ("\u092a\u0941\u0930\u0941\u0937", "Male"),
    ("\u092e\u0939\u093f\u0932\u093e", "Female"),
])
def test_gender_normalization(raw_value, expected):
    assert normalize_gender(raw_value) == expected


@pytest.mark.parametrize("raw_value", ["", None, "Xyz", "12345"])
def test_unrecognised_gender_returns_none(raw_value):
    assert normalize_gender(raw_value) is None


@pytest.mark.parametrize("raw_value,expected", [
    ("SC", "SC"), ("Scheduled Caste", "SC"), ("S.C.", "SC"),
    ("ST", "ST"), ("Scheduled Tribe", "ST"),
    ("OBC", "OBC"), ("Other Backward Class", "OBC"), ("O.B.C.", "OBC"),
    ("EWS", "EWS"), ("Economically Weaker Section", "EWS"),
    ("General", "GENERAL"), ("GEN", "GENERAL"), ("Unreserved", "GENERAL"),
    ("Other", "OTHER"),
])
def test_category_normalization(raw_value, expected):
    assert normalize_category(raw_value) == expected


def test_unrecognised_category_is_kept_not_forced_into_a_bucket():
    # We neither guess nor discard - the verifier flags it instead.
    assert normalize_category("Zzzz") == "ZZZZ"


@pytest.mark.parametrize("raw_value,expected", [
    ("12/05/2002", "12/05/2002"),
    ("12-05-2002", "12/05/2002"),
    ("12.05.2002", "12/05/2002"),
    ("2002-05-12", "12/05/2002"),      # ISO order
    ("12 May 2002", "12/05/2002"),
    ("5/6/2002", "05/06/2002"),        # zero padded
    ("DOB is 12/05/2002 as recorded", "12/05/2002"),
])
def test_date_formats_are_normalized_to_ddmmyyyy(raw_value, expected):
    assert extract_date_of_birth(raw_value) == expected


def test_district_trailing_word_and_pincode_are_stripped():
    assert clean_district("Jaipur District") == "Jaipur"
    assert clean_district("Kota 324005") == "Kota"


def test_normalize_text_collapses_whitespace_but_keeps_lines():
    assert normalize_text("  a   b  \n\n  c  ") == "a b\n\nc"


def test_extraction_is_deterministic():
    # Same input must always give the same output - important for the viva
    # demo and for any teammate relying on this module.
    first = extract_fields(INCOME_CERTIFICATE_TEXT)
    second = extract_fields(INCOME_CERTIFICATE_TEXT)
    assert first == second
