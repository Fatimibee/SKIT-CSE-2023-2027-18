"""
field_extractor.py
-------------------
Turns RAW OCR TEXT into STRUCTURED CITIZEN FIELDS.

This file has no web-framework code and no OCR code. It takes a plain
string in and returns a plain dictionary out, which makes it trivial to
unit test and easy for a teammate to reuse later (e.g. the scheme
recommendation engine can import `extract_fields` directly).

Approach (deliberately simple and explainable, no LLM / no API calls):

    1. Split the OCR text into lines.
    2. For each field, look for a known LABEL on a line
       ("Name:", "DOB -", "वार्षिक आय:", ...) and capture what follows it.
    3. Normalize that captured value with small, readable helpers
       (dates -> DD/MM/YYYY, "Rs. 1,80,000" -> 180000, "M" -> "Male", ...).
    4. Detect the document type by counting keyword hits.

Everything is deterministic: the same OCR text always produces the same
output. The only exception is `age`, which depends on today's date when
it has to be calculated from a date of birth (that is unavoidable).

GOLDEN RULE: if a field cannot be confidently identified, we return
None. We never guess and never invent citizen information.
"""

import re
from datetime import date, datetime

# ---------------------------------------------------------------------------
# The fields this module tries to extract, in a fixed order so the JSON
# response always looks the same.
# ---------------------------------------------------------------------------
FIELD_NAMES = (
    "name",
    "date_of_birth",
    "age",
    "gender",
    "category",
    "annual_income",
    "state",
    "district",
    "address",
    "document_type",
)

# Fields that come from a "Label: value" line in the document. `age` and
# `document_type` are handled separately (age can be derived from the DOB,
# and document_type comes from keyword detection, not from a label).
LABEL_BASED_FIELDS = (
    "name",
    "date_of_birth",
    "age",
    "gender",
    "category",
    "annual_income",
    "state",
    "district",
    "address",
)


# ---------------------------------------------------------------------------
# LABEL DICTIONARY
# ---------------------------------------------------------------------------
# Each entry is a list of small regex fragments describing how that field's
# label might appear in an OCR'd Indian government document, including
# common Hindi (Devanagari) labels.
#
# `\s*` between words absorbs the extra/missing spaces OCR loves to add.
# The longest fragments are tried first (see _sort_labels_longest_first).
# ---------------------------------------------------------------------------
FIELD_LABELS = {
    "name": [
        r"name\s*of\s*(?:the\s*)?(?:applicant|candidate|student|holder|beneficiary|person)",
        r"(?:applicant|candidate|student|holder|beneficiary)(?:'s)?\s*name",
        r"full\s*name",
        r"name",
        r"नाम",
    ],
    "date_of_birth": [
        r"date\s*of\s*birth",
        r"birth\s*date",
        r"d\s*[.]?\s*o\s*[.]?\s*b",
        r"जन्म\s*तिथि",
        r"जन्म\s*दिनांक",
    ],
    "age": [
        r"age\s*in\s*years",
        r"age",
        r"आयु",
        r"उम्र",
    ],
    "gender": [
        r"gender",
        r"sex",
        r"लिंग",
    ],
    "category": [
        r"(?:social\s*|caste\s*)?category",
        r"caste",
        r"जाति",
        r"वर्ग",
    ],
    "annual_income": [
        r"total\s*annual\s*(?:family\s*)?income",
        r"annual\s*(?:family\s*|household\s*)?income",
        r"yearly\s*income",
        r"family\s*income",
        r"income\s*per\s*annum",
        r"income",
        r"वार्षिक\s*आय",
        r"आय",
    ],
    "state": [
        r"state",
        r"राज्य",
    ],
    "district": [
        r"district",
        r"distt?\b",
        r"जिला",
        r"ज़िला",
    ],
    "address": [
        r"(?:permanent|residential|present|full)\s*address",
        r"address",
        r"पता",
    ],
}


def _sort_labels_longest_first(labels_by_field):
    """Regex alternation picks the FIRST alternative that matches, so a
    short label like `dob` must be tried AFTER `date of birth`, otherwise
    "Date of Birth: 12/05/2002" could match on the wrong fragment.
    Sorting by pattern length (longest first) gives us that for free.
    """
    return {
        field: sorted(labels, key=len, reverse=True)
        for field, labels in labels_by_field.items()
    }


FIELD_LABELS = _sort_labels_longest_first(FIELD_LABELS)

# Characters that may sit between a label and its value: "Name: X",
# "NAME - X", "Name = X", "Name : - X", or nothing at all ("Name X").
_SEPARATOR = r"\s*[:\-\u2013\u2014=|]*\s*"

# Letters we consider "word characters" for boundary checks. Python's `\b`
# is ASCII-oriented by default, so we spell out Latin + Devanagari.
_LETTER = r"A-Za-z\u0900-\u097F"

# A single regex that matches ANY known label followed by a separator.
# Used to (a) stop a captured value from swallowing the next field on the
# same line, and (b) know when a multi-line address has ended.
_ANY_LABEL_PATTERN = "|".join(
    sorted(
        (label for labels in FIELD_LABELS.values() for label in labels),
        key=len,
        reverse=True,
    )
)
_ANY_LABEL_REGEX = re.compile(
    rf"(?<![{_LETTER}])(?:{_ANY_LABEL_PATTERN})\s*[:\-\u2013\u2014=]",
    re.IGNORECASE | re.UNICODE,
)

# Words that mean the name on this line belongs to SOMEBODY ELSE (the
# applicant's father, mother, spouse, guardian...), not to the applicant.
_RELATIVE_KEYWORDS_REGEX = re.compile(
    r"father|mother|husband|wife|spouse|guardian|parent|son|daughter"
    r"|s\s*/\s*o|d\s*/\s*o|w\s*/\s*o|c\s*/\s*o"
    r"|\u092a\u093f\u0924\u093e|\u092e\u093e\u0924\u093e"
    r"|\u092a\u0924\u093f|\u092a\u0924\u094d\u0928\u0940",
    re.IGNORECASE | re.UNICODE,
)


def _is_relative_name_line(line):
    """True if this line is about a relative's name rather than the
    applicant's.

    We only inspect the LABEL part of the line (everything before the
    first separator), so "Father's Name: Suresh" and "Name of Father -
    Suresh" are both rejected, while an applicant genuinely called
    "Sonia" is not rejected just because her name contains "son".
    """
    label_part = re.split(r"[:\-\u2013\u2014=|]", line, maxsplit=1)[0]
    # Guard against a line with no separator at all: only the first few
    # words can plausibly be the label.
    label_part = " ".join(label_part.split()[:4])
    return bool(_RELATIVE_KEYWORDS_REGEX.search(label_part))

# Honorifics stripped from the front of a name.
_HONORIFIC_REGEX = re.compile(
    r"^(?:mr|mrs|ms|miss|shri|sri|smt|smt\.|kum|kumari|dr|master)\.?\s+",
    re.IGNORECASE,
)

# Anything that is not a letter, space, dot, apostrophe or hyphen is not
# part of a person's name (OCR speckle, stray digits, box-drawing, ...).
_NON_NAME_CHARS_REGEX = re.compile(rf"[^{_LETTER}\s.'\-]")


# ---------------------------------------------------------------------------
# STATES AND UNION TERRITORIES
# ---------------------------------------------------------------------------
# Used both to normalize a state's spelling/casing and as a fallback when
# there is no explicit "State:" label (very common - the state name often
# only appears in the document header, e.g. "GOVERNMENT OF RAJASTHAN").
# ---------------------------------------------------------------------------
INDIAN_STATES_AND_UTS = (
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
)

# Alternative spellings OCR / older documents may produce, plus the most
# common Hindi state names (the project is Hindi/English bilingual).
STATE_ALIASES = {
    "orissa": "Odisha",
    "pondicherry": "Puducherry",
    "uttaranchal": "Uttarakhand",
    "new delhi": "Delhi",
    "nct of delhi": "Delhi",
    "\u0930\u093e\u091c\u0938\u094d\u0925\u093e\u0928": "Rajasthan",
    "\u092e\u0927\u094d\u092f \u092a\u094d\u0930\u0926\u0947\u0936": "Madhya Pradesh",
    "\u0909\u0924\u094d\u0924\u0930 \u092a\u094d\u0930\u0926\u0947\u0936": "Uttar Pradesh",
    "\u092c\u093f\u0939\u093e\u0930": "Bihar",
    "\u092e\u0939\u093e\u0930\u093e\u0937\u094d\u091f\u094d\u0930": "Maharashtra",
    "\u0917\u0941\u091c\u0930\u093e\u0924": "Gujarat",
    "\u0939\u0930\u093f\u092f\u093e\u0923\u093e": "Haryana",
    "\u092a\u0902\u091c\u093e\u092c": "Punjab",
    "\u0926\u093f\u0932\u094d\u0932\u0940": "Delhi",
}


# ---------------------------------------------------------------------------
# CATEGORY NORMALIZATION
# ---------------------------------------------------------------------------
SUPPORTED_CATEGORIES = ("SC", "ST", "OBC", "EWS", "GENERAL", "OTHER")

# Checked in this order, so "scheduled caste" wins before a bare "sc".
_CATEGORY_RULES = (
    ("SC", (r"scheduled\s*caste", r"\bs\s*[./]?\s*c\b", r"अनुसूचित\s*जाति")),
    ("ST", (r"scheduled\s*tribe", r"\bs\s*[./]?\s*t\b", r"अनुसूचित\s*जनजाति")),
    ("OBC", (r"other\s*backward\s*class(?:es)?", r"\bo\s*[./]?\s*b\s*[./]?\s*c\b",
             r"backward\s*class", r"अन्य\s*पिछड़ा", r"पिछड़ा\s*वर्ग")),
    ("EWS", (r"economically\s*weaker\s*section(?:s)?",
             r"\be\s*[./]?\s*w\s*[./]?\s*s\b")),
    ("GENERAL", (r"general", r"\bgen\b", r"unreserved", r"\bur\b", r"सामान्य")),
    ("OTHER", (r"^others?$", r"^अन्य$")),
)


# ---------------------------------------------------------------------------
# GENDER NORMALIZATION
# ---------------------------------------------------------------------------
SUPPORTED_GENDERS = ("Male", "Female", "Other")

_GENDER_RULES = (
    # "female" is checked before "male" so it is never mis-read as male.
    ("Female", (r"^f$", r"female", r"woman", r"महिला", r"स्त्री", r"मादा")),
    ("Male", (r"^m$", r"male", r"\bman\b", r"पुरुष", r"पुल्लिंग")),
    ("Other", (r"transgender", r"third\s*gender", r"^t$", r"^o$", r"^other$",
               r"ट्रांसजेंडर", r"अन्य")),
)


# ---------------------------------------------------------------------------
# DOCUMENT TYPE DETECTION
# ---------------------------------------------------------------------------
DOCUMENT_TYPES = (
    "Aadhaar Card",
    "Income Certificate",
    "Caste Certificate",
    "Residence Certificate",
    "Unknown",
)

# Keyword -> weight. Weighted so a real title ("income certificate") counts
# for more than a passing mention of a single word ("income").
_DOCUMENT_TYPE_KEYWORDS = {
    "Aadhaar Card": (
        (r"aadhaar", 3), (r"aadhar", 3), (r"आधार", 3),
        (r"unique\s*identification\s*authority", 3), (r"\buidai\b", 3),
        (r"enrol?ment\s*no", 1), (r"vid\s*:", 1),
    ),
    "Income Certificate": (
        (r"income\s*certificate", 5), (r"आय\s*प्रमाण\s*पत्र", 5),
        (r"certificate\s*of\s*income", 5),
        (r"annual\s*income", 2), (r"वार्षिक\s*आय", 2),
    ),
    "Caste Certificate": (
        (r"caste\s*certificate", 5), (r"जाति\s*प्रमाण\s*पत्र", 5),
        (r"certificate\s*of\s*caste", 5),
        (r"community\s*certificate", 4),
        (r"caste\s*category", 2), (r"scheduled\s*caste", 1),
        (r"scheduled\s*tribe", 1), (r"other\s*backward\s*class", 1),
    ),
    "Residence Certificate": (
        (r"residence\s*certificate", 5), (r"domicile\s*certificate", 5),
        (r"residential\s*certificate", 5), (r"निवास\s*प्रमाण\s*पत्र", 5),
        (r"मूल\s*निवास", 4),
        (r"\bdomicile\b", 3), (r"permanent\s*resident", 2),
    ),
}

# Below this score we are not confident enough to name a document type.
_MIN_DOCUMENT_TYPE_SCORE = 3


# ---------------------------------------------------------------------------
# DATE PATTERNS
# ---------------------------------------------------------------------------
_MONTH_NAMES = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9,
    "oct": 10, "october": 10, "nov": 11, "november": 11,
    "dec": 12, "december": 12,
}

# 12/05/2002, 12-05-2002, 12.05.02
_DATE_DMY_REGEX = re.compile(r"\b(\d{1,2})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(\d{2,4})\b")
# 2002-05-12 (ISO style)
_DATE_YMD_REGEX = re.compile(r"\b(\d{4})\s*[/\-.]\s*(\d{1,2})\s*[/\-.]\s*(\d{1,2})\b")
# 12 May 2002 / 12-May-2002
_DATE_TEXT_MONTH_REGEX = re.compile(
    r"\b(\d{1,2})\s*[-/\s]\s*([A-Za-z]{3,9})\s*[-/\s,]\s*(\d{4})\b"
)

# The canonical output format for every date this module returns.
DATE_OUTPUT_FORMAT = "%d/%m/%Y"

# Ages outside this range are almost certainly OCR noise, not a real person.
MIN_REASONABLE_AGE = 0
MAX_REASONABLE_AGE = 120


# ===========================================================================
# SMALL TEXT HELPERS
# ===========================================================================

def normalize_text(text):
    """Tidy up raw OCR text without changing its meaning.

    - converts fancy unicode punctuation to plain ASCII equivalents
    - collapses runs of spaces/tabs
    - strips trailing spaces from every line
    - drops completely empty leading/trailing lines

    Line breaks are preserved, because our extraction is line-based.
    """
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    # Common OCR/unicode lookalikes -> plain ASCII.
    text = (text
            .replace("\u2018", "'").replace("\u2019", "'")
            .replace("\u201c", '"').replace("\u201d", '"')
            .replace("\u00a0", " "))

    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t]+", " ", line).strip()
        lines.append(line)

    return "\n".join(lines).strip("\n")


def _truncate_at_next_label(value):
    """Stop a captured value from swallowing the next field.

    OCR often puts several fields on one line:
        "Name: Rahul Sharma   DOB: 12/05/2002"
    Capturing everything after "Name:" would give us the DOB too, so we
    cut the value at the next label that is followed by a separator.
    """
    match = _ANY_LABEL_REGEX.search(value)
    if match:
        return value[:match.start()]
    return value


def _strip_surviving_label_fragment(value):
    """Drop a leftover label fragment we did not have a pattern for.

    Example: a line "Name of Guardian's Ward: Rahul" may leave us with
    "of Guardian's Ward: Rahul". If what sits before a colon is short and
    has no digits, it was a label fragment, so we keep only what follows.
    """
    if ":" not in value:
        return value

    before, _, after = value.partition(":")
    if len(before) <= 25 and not re.search(r"\d", before) and after.strip():
        return after
    return value


def _clean_captured_value(value):
    """Final tidy-up of a value captured from a label line."""
    value = _truncate_at_next_label(value)
    value = _strip_surviving_label_fragment(value)
    value = re.sub(r"\s+", " ", value)
    # Strip decorative punctuation OCR leaves at the edges.
    return value.strip(" \t.,;:-\u2013\u2014|_*/()[]")


def _looks_like_a_label_line(line):
    """True if this line starts a new field (used to end a multi-line
    address)."""
    return bool(_ANY_LABEL_REGEX.search(line))


# Words that name a KIND of document rather than a citizen's detail.
_DOCUMENT_WORDS_REGEX = re.compile(
    r"certificate|card|form|declaration|receipt|acknowledgement"
    r"|\u092a\u094d\u0930\u092e\u093e\u0923\s*\u092a\u0924\u094d\u0930"
    r"|\u092a\u094d\u0930\u092e\u093e\u0923\u092a\u0924\u094d\u0930",
    re.IGNORECASE | re.UNICODE,
)

# A captured value that is nothing but a document word is a leftover from
# a heading, not a real value.
_ONLY_DOCUMENT_WORD_REGEX = re.compile(
    r"^(?:certificate|card|form|declaration"
    r"|\u092a\u094d\u0930\u092e\u093e\u0923\s*\u092a\u0924\u094d\u0930"
    r"|\u092a\u0924\u094d\u0930)$",
    re.IGNORECASE | re.UNICODE,
)

# A heading is short - beyond this many words it is probably a real
# sentence or address that merely happens to mention "certificate".
MAX_TITLE_LINE_WORDS = 5


def _looks_like_a_title_line(line):
    """True if this line is the document's HEADING, not a field.

    This matters because a heading such as "INCOME CERTIFICATE" contains
    the word "income", and would otherwise be captured as the value of
    the Annual Income field ("CERTIFICATE"). Likewise "CASTE CERTIFICATE"
    would poison the Category field.

    A heading is recognised as: no "label = value" separator, mentions a
    kind of document, and is only a few words long.
    """
    if ":" in line or "=" in line:
        return False
    if len(line.split()) > MAX_TITLE_LINE_WORDS:
        return False
    return bool(_DOCUMENT_WORDS_REGEX.search(line))


def _is_plausible_raw_value(field, value):
    """Sanity-check a captured value BEFORE we accept it for a field.

    A label can match a line that was never really that field (headings,
    department names, footers). Requiring the value to at least look like
    the right kind of thing lets extraction skip the false match and keep
    searching the rest of the document.
    """
    if not value:
        return False

    # These three are always numeric on a real document.
    if field in ("date_of_birth", "age", "annual_income"):
        return bool(re.search(r"\d", value))

    # These two must map onto a known set of values to be meaningful.
    if field == "gender":
        return normalize_gender(value) is not None

    if field == "name":
        return clean_name(value) is not None

    return True


def _build_line_start_label_regex(label_fragment):
    """Regex for one label at the START of a line.

    The leading `[^letters]*` lets us skip list markers and OCR speckle,
    so "1. Name :", "* NAME -" and "|Name|" all still work. Here the
    separator is OPTIONAL, because "Name Rahul Sharma" is unambiguous
    when the label opens the line.
    """
    return re.compile(
        rf"^[^{_LETTER}]*(?:{label_fragment})\s*[:\-\u2013\u2014=|.]*\s*(.*)$",
        re.IGNORECASE | re.UNICODE,
    )


def _build_mid_line_label_regex(label_fragment):
    """Regex for one label appearing PART WAY THROUGH a line.

    OCR very often flattens a form onto one line:
        "Name: Anita Devi   DOB: 01/01/1990   Gender: F"

    Here a separator is MANDATORY. Without that rule an address like
    "Near State Bank, Jaipur" would match the `state` label and capture
    "Bank, Jaipur" as the state.
    """
    return re.compile(
        rf"(?<![{_LETTER}])(?:{label_fragment})\s*[:\-\u2013\u2014=|]\s*(.*)$",
        re.IGNORECASE | re.UNICODE,
    )


# Pre-compile every label regex once, at import time.
_LINE_START_REGEXES = {
    field: [_build_line_start_label_regex(label) for label in labels]
    for field, labels in FIELD_LABELS.items()
}

_MID_LINE_REGEXES = {
    field: [_build_mid_line_label_regex(label) for label in labels]
    for field, labels in FIELD_LABELS.items()
}


# ===========================================================================
# STEP 1: FIND THE RAW VALUE SITTING NEXT TO EACH LABEL
# ===========================================================================

def extract_label_values(text):
    """Find the raw (un-normalized) text next to each known label.

    Returns a dict with one key per label-based field. The value is the
    raw captured string, or None if that label never appeared.

    This is kept as a separate, public step because `document_verifier`
    uses it to tell the difference between:
      - the label was never in the document        -> field is MISSING
      - the label WAS there but we could not read it -> field is INVALID
    """
    normalized = normalize_text(text)
    lines = normalized.split("\n")

    # Values that look right for their field - what we actually want.
    values = {field: None for field in LABEL_BASED_FIELDS}
    # Values whose label was clearly present but whose content we could
    # not make sense of. Kept so the verifier can tell "not in the
    # document" apart from "in the document but unreadable".
    unreadable = {field: None for field in LABEL_BASED_FIELDS}

    for index, line in enumerate(lines):
        if not line:
            continue

        # Document headings are titles, not fields - skip them entirely.
        if _looks_like_a_title_line(line):
            continue

        for field in LABEL_BASED_FIELDS:
            if values[field] is not None:
                # Keep the FIRST good match only. On these documents the
                # first occurrence is the real field; later ones are
                # usually footers, declarations or repeated headers.
                continue

            # A line about someone else's name is not the applicant's name.
            if field == "name" and _is_relative_name_line(line):
                continue

            captured = _capture_value_for_field(field, line, lines, index)
            if not captured:
                continue

            if _is_plausible_raw_value(field, captured):
                values[field] = captured
            elif unreadable[field] is None:
                unreadable[field] = captured

    # Prefer a usable value; fall back to the unreadable one purely so the
    # verification layer knows the label existed.
    return {
        field: values[field] or unreadable[field]
        for field in LABEL_BASED_FIELDS
    }


def _capture_value_for_field(field, line, lines, index):
    """Try to pull this field's value out of a single line.

    Two passes, in order of confidence:
      1. the label opens the line ("District : Jaipur")
      2. the label appears mid-line ("... DOB: 01/01/1990 Gender: F")
    """
    for regexes, is_line_start in ((_LINE_START_REGEXES[field], True),
                                   (_MID_LINE_REGEXES[field], False)):
        for regex in regexes:
            match = regex.match(line) if is_line_start else regex.search(line)
            if not match:
                continue

            captured = _clean_captured_value(match.group(1))

            if field == "address":
                captured = _extend_address(captured, lines, index)

            if not captured and is_line_start:
                # Label sat alone on its line ("Name:" then the value on
                # the next line) - a very common printed-form layout.
                captured = _value_from_next_line(lines, index)

            # A capture that is nothing but a document word (e.g. the
            # "CERTIFICATE" left over from an "INCOME CERTIFICATE:"
            # heading) is not a value at all - throw it away completely.
            if captured and _ONLY_DOCUMENT_WORD_REGEX.match(captured.strip()):
                captured = ""

            if captured:
                return captured
            break

    return ""


def _value_from_next_line(lines, index):
    """Look one line below for a value, when the label had nothing after it."""
    if index + 1 >= len(lines):
        return ""
    next_line = lines[index + 1]
    if not next_line or _looks_like_a_label_line(next_line):
        return ""
    return _clean_captured_value(next_line)


# An address may wrap onto the following lines; take at most this many.
MAX_ADDRESS_CONTINUATION_LINES = 2


def _extend_address(captured, lines, index):
    """Collect an address that wraps onto the next line or two.

    We stop as soon as we hit a blank line or a line that starts a new
    field, so we never absorb unrelated content.
    """
    parts = [captured] if captured else []

    for offset in range(1, MAX_ADDRESS_CONTINUATION_LINES + 1):
        position = index + offset
        if position >= len(lines):
            break
        line = lines[position]
        if not line or _looks_like_a_label_line(line):
            break
        parts.append(_clean_captured_value(line))

    return ", ".join(part for part in parts if part)


# ===========================================================================
# STEP 2: NORMALIZE EACH RAW VALUE
# ===========================================================================

def clean_name(raw_value):
    """Normalize a captured name, or return None if it is unusable.

    - strips honorifics ("Shri", "Mrs.")
    - removes characters that cannot be part of a name (digits, symbols)
    - converts SHOUTED names to Title Case, leaves mixed case alone
    """
    if not raw_value:
        return None

    value = _HONORIFIC_REGEX.sub("", raw_value.strip())
    value = _NON_NAME_CHARS_REGEX.sub(" ", value)
    value = re.sub(r"\s+", " ", value).strip(" .-'")

    # Too short to be a real name - treat as unreadable rather than guess.
    if len(value) < 2:
        return None

    # "RAHUL SHARMA" -> "Rahul Sharma". Mixed case is left untouched so we
    # don't mangle names like "McDonald" or "D'Souza".
    if value.isupper():
        value = value.title()

    return value


def extract_date_of_birth(raw_value):
    """Pull a date out of a captured value and return it as DD/MM/YYYY.

    NOTE: this only checks the SHAPE of the date, not whether it is a real
    calendar date. "32/13/2002" is returned as-is on purpose, so that
    `document_verifier` can report "Invalid date of birth" instead of us
    silently dropping information the document clearly contained.
    """
    if not raw_value:
        return None

    match = _DATE_DMY_REGEX.search(raw_value)
    if match:
        day, month, year = match.groups()
        return _format_date_parts(day, month, year)

    match = _DATE_YMD_REGEX.search(raw_value)
    if match:
        year, month, day = match.groups()
        return _format_date_parts(day, month, year)

    match = _DATE_TEXT_MONTH_REGEX.search(raw_value)
    if match:
        day, month_name, year = match.groups()
        month = _MONTH_NAMES.get(month_name.lower())
        if month:
            return _format_date_parts(day, month, year)

    return None


def _format_date_parts(day, month, year):
    """Assemble DD/MM/YYYY from loose parts, expanding 2-digit years."""
    day, month, year = int(day), int(month), int(year)

    if year < 100:
        # A 2-digit year: 02 -> 2002, 85 -> 1985. Anything that would land
        # in the future must belong to the previous century.
        current_two_digit = date.today().year % 100
        century = 2000 if year <= current_two_digit else 1900
        year += century

    return f"{day:02d}/{month:02d}/{year:04d}"


def parse_date(date_string):
    """Parse a DD/MM/YYYY string into a real date, or None if impossible.

    Shared by this module and `document_verifier` so both agree on what a
    valid date means.
    """
    if not date_string:
        return None
    try:
        return datetime.strptime(date_string.strip(), DATE_OUTPUT_FORMAT).date()
    except (ValueError, TypeError):
        return None


def calculate_age(date_of_birth, today=None):
    """Whole years between a DOB (DD/MM/YYYY) and today. None if unusable."""
    born = parse_date(date_of_birth)
    if born is None:
        return None

    today = today or date.today()
    if born > today:
        return None

    # Subtract one year if this year's birthday has not happened yet.
    had_birthday = (today.month, today.day) >= (born.month, born.day)
    return today.year - born.year - (0 if had_birthday else 1)


def parse_age(raw_value):
    """Read an explicitly stated age, e.g. "24", "24 Years", "about 24"."""
    if not raw_value:
        return None
    match = re.search(r"\b(\d{1,3})\b", raw_value)
    if not match:
        return None
    return int(match.group(1))


def normalize_gender(raw_value):
    """Map any recognized gender wording to Male / Female / Other."""
    if not raw_value:
        return None

    value = raw_value.strip().lower()
    for normalized, patterns in _GENDER_RULES:
        for pattern in patterns:
            if re.search(pattern, value, re.IGNORECASE | re.UNICODE):
                return normalized
    return None


def find_gender_without_label(text):
    """Fallback for documents that print the gender with no label at all
    (Aadhaar cards typically just say "MALE" on its own line)."""
    match = re.search(
        r"(?<![A-Za-z])(female|male|transgender|महिला|पुरुष)(?![A-Za-z])",
        text, re.IGNORECASE | re.UNICODE,
    )
    if not match:
        return None
    return normalize_gender(match.group(1))


def normalize_category(raw_value):
    """Map a caste/category value onto SC / ST / OBC / EWS / GENERAL / OTHER.

    If the wording is not recognized we return the cleaned original text
    rather than forcing it into a bucket. `document_verifier` then flags it
    as un-normalized, which is honest: we neither guess nor throw away what
    the document said.
    """
    if not raw_value:
        return None

    value = raw_value.strip()
    for normalized, patterns in _CATEGORY_RULES:
        for pattern in patterns:
            if re.search(pattern, value, re.IGNORECASE | re.UNICODE):
                return normalized

    cleaned = re.sub(r"\s+", " ", value).strip()
    return cleaned.upper() if cleaned else None


def parse_income(raw_value):
    """Turn a written income into a plain integer number of rupees.

    Handles the shapes that actually turn up on Indian certificates:
        "Rs. 1,80,000"                  -> 180000
        "₹180000"                       -> 180000
        "INR 1,80,000/- per annum"      -> 180000
        "1.8 Lakh"                      -> 180000
        "Rs 180000 (Rupees One Lakh...)"-> 180000

    Returns None when there is no number to read.
    """
    if not raw_value:
        return None

    text = str(raw_value)

    # Drop the "(Rupees One Lakh Eighty Thousand Only)" style restatement -
    # the digits before it are what we want.
    text = re.sub(r"\([^)]*\)", " ", text)

    # Remove currency markers and noise.
    text = text.replace("\u20b9", " ")                      # ₹
    text = re.sub(r"\b(?:rs|inr|rupees?|only)\b\.?", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"/\s*-", " ", text)                       # trailing "/-"
    text = re.sub(r"\bper\s*annum\b|\bp\.?a\.?\b", " ", text, flags=re.IGNORECASE)

    # Indian scale words act as multipliers.
    multiplier = 1
    if re.search(r"\bcrores?\b|\bcr\b", text, re.IGNORECASE):
        multiplier = 10_000_000
    elif re.search(r"\blakh?s?\b|\blac?s?\b", text, re.IGNORECASE):
        multiplier = 100_000
    elif re.search(r"\bthousand\b", text, re.IGNORECASE):
        multiplier = 1_000

    # First number in the string. Commas are allowed inside it (both
    # Indian "1,80,000" and Western "180,000" grouping), spaces are not,
    # so we never accidentally glue two separate numbers together.
    match = re.search(r"\d[\d,]*(?:\.\d+)?", text)
    if not match:
        return None

    digits = match.group(0).replace(",", "").rstrip(".")
    if not digits or not re.search(r"\d", digits):
        return None

    try:
        amount = float(digits) * multiplier
    except ValueError:
        return None

    return int(round(amount))


def normalize_state(raw_value):
    """Match a captured value against the official state/UT list.

    Returns the canonical spelling ("RAJASTHAN" -> "Rajasthan"). If it is
    not a recognizable state we return the cleaned text unchanged, so a
    newly-formed or misspelt state is not silently discarded.
    """
    if not raw_value:
        return None

    value = re.sub(r"\s+", " ", raw_value).strip()
    if not value:
        return None

    lowered = value.lower()

    if lowered in STATE_ALIASES:
        return STATE_ALIASES[lowered]

    for state in INDIAN_STATES_AND_UTS:
        if lowered == state.lower():
            return state

    # The value may contain the state plus extra words ("Rajasthan 302001").
    for state in INDIAN_STATES_AND_UTS:
        if re.search(rf"(?<![{_LETTER}]){re.escape(state)}(?![{_LETTER}])",
                     value, re.IGNORECASE):
            return state

    return value


def find_state_without_label(text):
    """Look for a state name anywhere in the document.

    Useful because the state is often only in the header
    ("GOVERNMENT OF RAJASTHAN") with no "State:" label anywhere.

    If several different states appear we take the most frequent one, and
    break ties by earliest position - a fixed rule, so the result is
    always reproducible.
    """
    if not text:
        return None

    hits = {}
    for state in INDIAN_STATES_AND_UTS:
        matches = list(re.finditer(
            rf"(?<![{_LETTER}]){re.escape(state)}(?![{_LETTER}])",
            text, re.IGNORECASE,
        ))
        if matches:
            hits[state] = (len(matches), -matches[0].start())

    if not hits:
        return None

    # Highest count wins; on a tie the earliest mention wins.
    return max(hits, key=lambda state: hits[state])


def clean_district(raw_value):
    """Tidy a district value, e.g. "Jaipur District" -> "Jaipur"."""
    if not raw_value:
        return None

    value = re.sub(r"\s+", " ", raw_value).strip()
    # Drop a trailing "District"/"Distt"/"जिला" repeated after the name.
    value = re.sub(r"\s*(?:district|distt?\.?|जिला)\s*$", "", value,
                   flags=re.IGNORECASE | re.UNICODE).strip(" .,-")
    # Remove pincode-like trailing digits.
    value = re.sub(r"[\s,-]*\b\d{6}\b\s*$", "", value).strip(" .,-")

    if len(value) < 2:
        return None

    return value.title() if value.isupper() else value


def clean_address(raw_value):
    """Tidy a captured address. Kept permissive - addresses are messy."""
    if not raw_value:
        return None

    value = re.sub(r"\s+", " ", raw_value)
    value = re.sub(r"(,\s*)+", ", ", value).strip(" .,;-|")

    if len(value) < 3:
        return None

    return value


# ===========================================================================
# STEP 3: DOCUMENT TYPE DETECTION
# ===========================================================================

def detect_document_type(text):
    """Identify the document type by scoring keyword hits.

    Every keyword carries a weight so a real title ("Income Certificate")
    outranks an incidental mention ("annual income"). If the best score is
    below `_MIN_DOCUMENT_TYPE_SCORE`, or two types tie, we return
    "Unknown" instead of picking one at random.
    """
    if not text:
        return "Unknown"

    normalized = normalize_text(text)

    scores = {}
    for document_type, keywords in _DOCUMENT_TYPE_KEYWORDS.items():
        score = 0
        for pattern, weight in keywords:
            if re.search(pattern, normalized, re.IGNORECASE | re.UNICODE):
                score += weight
        if score:
            scores[document_type] = score

    if not scores:
        return "Unknown"

    best_score = max(scores.values())
    if best_score < _MIN_DOCUMENT_TYPE_SCORE:
        return "Unknown"

    winners = [name for name, score in scores.items() if score == best_score]
    if len(winners) != 1:
        # Genuinely ambiguous (e.g. a caste-cum-income certificate).
        return "Unknown"

    return winners[0]


# ===========================================================================
# QR CODE PAYLOAD PARSING
# ===========================================================================

import json
import xml.etree.ElementTree as ET


def parse_qr_data_fields(qr_data_list):
    """Parse a list of QR code string payloads (JSON or XML or key-value format)
    and return a dict of extracted citizen attributes.
    """
    if not qr_data_list:
        return {}

    extracted = {}
    for qr_item in qr_data_list:
        if not qr_item or not isinstance(qr_item, str):
            continue

        item_str = qr_item.strip()

        # Try JSON parsing
        if (item_str.startswith("{") and item_str.endswith("}")) or (item_str.startswith("[") and item_str.endswith("]")):
            try:
                data = json.loads(item_str)
                if isinstance(data, dict):
                    for k, v in data.items():
                        lk = str(k).lower().replace("_", "").replace("-", "")
                        v_str = str(v).strip() if v is not None else ""
                        if not v_str:
                            continue
                        if lk in ("name", "applicantname", "username", "fullname"):
                            extracted["name"] = v_str
                        elif lk in ("dob", "dateofbirth", "birthdate"):
                            extracted["date_of_birth"] = v_str
                        elif lk in ("gender", "sex"):
                            extracted["gender"] = v_str
                        elif lk in ("income", "annualincome", "familyincome", "totalincome"):
                            extracted["annual_income"] = v_str
                        elif lk in ("category", "caste", "socialcategory"):
                            extracted["category"] = v_str
                        elif lk in ("state",):
                            extracted["state"] = v_str
                        elif lk in ("district", "dist"):
                            extracted["district"] = v_str
                        elif lk in ("address", "addr"):
                            extracted["address"] = v_str
                        elif lk in ("doctype", "documenttype"):
                            extracted["document_type"] = v_str
            except Exception:
                pass

        # Try XML parsing (e.g. Aadhaar QR code format)
        elif "<" in item_str and ">" in item_str:
            try:
                if not item_str.startswith("<?xml") and not item_str.startswith("<"):
                    start_idx = item_str.find("<")
                    item_str = item_str[start_idx:]
                root = ET.fromstring(item_str)
                attribs = root.attrib if hasattr(root, "attrib") and root.attrib else {}
                if not attribs:
                    for child in root.iter():
                        if child.attrib:
                            attribs.update(child.attrib)
                for k, v in attribs.items():
                    lk = k.lower()
                    if lk in ("name", "n"):
                        extracted["name"] = v
                    elif lk in ("dob", "yob"):
                        extracted["date_of_birth"] = v
                    elif lk in ("g", "gender"):
                        extracted["gender"] = v
                    elif lk in ("state",):
                        extracted["state"] = v
                    elif lk in ("dist", "district"):
                        extracted["district"] = v
                    elif lk in ("house", "street", "loc", "vtc", "po", "subdist"):
                        if "address_parts" not in extracted:
                            extracted["address_parts"] = []
                        extracted["address_parts"].append(v)
                extracted["document_type"] = "Aadhaar Card"
            except Exception:
                pass

    if "address_parts" in extracted:
        extracted["address"] = ", ".join(extracted.pop("address_parts"))

    return extracted


# ===========================================================================
# MAIN ENTRY POINT
# ===========================================================================

def extract_fields(text, qr_data=None):
    """Convert raw OCR text and optional QR code data into structured citizen fields.

    Args:
        text: raw OCR output (may be None, empty, or very noisy).
        qr_data: optional list of decoded QR code string payloads.

    Returns:
        A dict with exactly the keys in FIELD_NAMES. Every value is either
        a confidently extracted value or None. `document_type` is the only
        field that never returns None - it falls back to "Unknown".
    """
    normalized = normalize_text(text)

    # Start with everything unknown, so a crash-free empty result is the
    # default rather than something we have to remember to build.
    data = {field: None for field in FIELD_NAMES}
    data["document_type"] = detect_document_type(normalized)

    if normalized:
        raw = extract_label_values(normalized)

        data["name"] = clean_name(raw["name"])
        data["date_of_birth"] = extract_date_of_birth(raw["date_of_birth"])

        # Age: prefer what the document states; otherwise work it out from the
        # date of birth. Never invented when neither is available.
        data["age"] = parse_age(raw["age"])
        if data["age"] is None:
            data["age"] = calculate_age(data["date_of_birth"])

        data["gender"] = normalize_gender(raw["gender"])
        if data["gender"] is None:
            data["gender"] = find_gender_without_label(normalized)

        data["category"] = normalize_category(raw["category"])
        data["annual_income"] = parse_income(raw["annual_income"])

        data["state"] = normalize_state(raw["state"])
        if data["state"] is None:
            data["state"] = find_state_without_label(normalized)

        data["district"] = clean_district(raw["district"])
        data["address"] = clean_address(raw["address"])

        # If the document had no "Address:" label but we did find a district
        # and a state, compose a coarse address from those two extracted
        # values. This is DERIVED from data already found in the document -
        # nothing new is invented.
        if data["address"] is None and data["district"] and data["state"]:
            data["address"] = f"{data['district']}, {data['state']}"

    # Merge QR-extracted fields if present (QR payloads provide high precision)
    if qr_data:
        qr_fields = parse_qr_data_fields(qr_data)
        if qr_fields.get("name") and not data["name"]:
            data["name"] = clean_name(qr_fields["name"])
        if qr_fields.get("date_of_birth") and not data["date_of_birth"]:
            parsed_dob = extract_date_of_birth(qr_fields["date_of_birth"])
            if parsed_dob:
                data["date_of_birth"] = parsed_dob
                if data["age"] is None:
                    data["age"] = calculate_age(parsed_dob)
        if qr_fields.get("gender") and not data["gender"]:
            data["gender"] = normalize_gender(qr_fields["gender"])
        if qr_fields.get("annual_income") is not None and data["annual_income"] is None:
            data["annual_income"] = parse_income(str(qr_fields["annual_income"]))
        if qr_fields.get("category") and not data["category"]:
            data["category"] = normalize_category(qr_fields["category"])
        if qr_fields.get("state") and not data["state"]:
            data["state"] = normalize_state(qr_fields["state"])
        if qr_fields.get("district") and not data["district"]:
            data["district"] = clean_district(qr_fields["district"])
        if qr_fields.get("address") and not data["address"]:
            data["address"] = clean_address(qr_fields["address"])
        if qr_fields.get("document_type") and data["document_type"] == "Unknown":
            data["document_type"] = qr_fields["document_type"]

    return data
