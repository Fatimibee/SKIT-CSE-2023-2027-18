"""
schemes_processing.py
----------------------
Processing layer for the Yojana Sahayak scheme dataset.

WHERE THIS SITS IN THE PIPELINE

    India.gov.in scraper  (existing - NOT touched by this file)
            |
            v
    government_schemes.csv          <-- raw scraped output
            |
            v
    schemes_processing.py           <-- THIS FILE
            |  - normalize categories / tags
            |  - deduplicate schemes
            |  - add the extended field schema
            |  - extract structured eligibility where clearly stated
            v
    government_schemes_processed.csv
            |
            v
    future RAG / recommendation engine

DESIGN RULES

1. The existing scraper is not modified. This file only reads the CSV it
   produces, so the current scraping code keeps working exactly as before.
2. All nine original columns are preserved unchanged. Nothing is dropped
   or renamed, so any existing consumer of the CSV keeps working.
3. Nothing is ever invented. A field we cannot read from the source is
   written as empty, not guessed.
4. Pure standard library plus pandas (already needed to read the CSV).

Run it with:

    python schemes_processing.py government_schemes.csv
"""

import argparse
import ast
import json
import os
import re
import sys
from collections import Counter

import pandas as pd


# ===========================================================================
# SCHEMA
# ===========================================================================

# The nine columns the existing scraper already produces. These are kept
# exactly as they are - order, name and value all unchanged.
EXISTING_COLUMNS = [
    "title",
    "ministry",
    "schemeCategory",
    "description",
    "beneficiaryState",
    "npiMinistry",
    "slug",
    "tags",
    "__typename",
]

# Content fields that live on the individual scheme DETAIL page on
# India.gov.in, not in the search response the scraper currently reads.
# They are added to the schema now (empty) so that the column layout is
# already correct when the scraper is extended to fetch detail pages.
CONTENT_COLUMNS = [
    "eligibility",
    "beneficiaries",
    "benefits",
    "documents_required",
    "application_process",
    "application_mode",
    "state",
    "department",
]

# Raw source text, kept alongside the cleaned version so that extraction
# logic can be improved later and re-run without re-scraping.
RAW_COLUMNS = [
    "eligibility_raw",
    "beneficiaries_raw",
    "benefits_raw",
    "documents_required_raw",
]

# Structured eligibility, derived from the raw text by this file.
ELIGIBILITY_COLUMNS = [
    "age_min",
    "age_max",
    "gender",
    "income_max",
    "category",
    "occupation",
    "eligibility_state",
    "education",
    "disability",
]

# Provenance.
PROVENANCE_COLUMNS = [
    "source_url",
    "official_url",
    "last_updated",
]

# Normalized copies of the list fields. The originals are left untouched
# so nothing that reads `schemeCategory` or `tags` today breaks.
NORMALIZED_COLUMNS = [
    "categories_normalized",
    "tags_normalized",
]

OUTPUT_COLUMNS = (
    EXISTING_COLUMNS
    + NORMALIZED_COLUMNS
    + CONTENT_COLUMNS
    + RAW_COLUMNS
    + ELIGIBILITY_COLUMNS
    + PROVENANCE_COLUMNS
)


# ===========================================================================
# SMALL HELPERS
# ===========================================================================

def is_empty(value):
    """True for anything we treat as "no data": None, NaN, blank, 'nan'."""
    if value is None:
        return True
    if isinstance(value, float) and pd.isna(value):
        return True
    text = str(value).strip()
    return text == "" or text.lower() in ("nan", "none", "null")


def clean_text(value):
    """Collapse whitespace in a free-text value. Returns "" if empty.

    This is deliberately gentle - it only touches whitespace, so no
    wording, punctuation or casing from the source is lost.
    """
    if is_empty(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def parse_list_field(value):
    """Read a list that was stored in the CSV as a Python-literal string.

    The scraper writes these as e.g. "['Health & Wellness', None]", so we
    parse them back and drop the None/empty entries.
    """
    if is_empty(value):
        return []

    if isinstance(value, (list, tuple)):
        items = list(value)
    else:
        try:
            parsed = ast.literal_eval(str(value))
            items = parsed if isinstance(parsed, (list, tuple)) else [parsed]
        except (ValueError, SyntaxError):
            # Not a literal list - treat it as a single plain value.
            items = [value]

    return [str(i).strip() for i in items if not is_empty(i)]


# ===========================================================================
# NORMALIZATION
# ===========================================================================

def normalize_list_values(values, canonical_forms=None):
    """Tidy a list of category/tag values.

    Steps: trim whitespace, drop empties, collapse inner spacing, remove
    duplicates (case-insensitively), and keep the original order.

    `canonical_forms` maps a lowercase key to the preferred spelling, which
    is how "FINANCIAL ASSISTANCE" and "Financial Assistance" end up as one
    value. Two values are only merged when they differ purely by casing or
    whitespace - never because they merely look similar, since that would
    change their meaning.
    """
    canonical_forms = canonical_forms or {}

    result = []
    seen = set()

    for value in values:
        value = re.sub(r"\s+", " ", str(value)).strip()
        if not value:
            continue

        key = value.lower()
        value = canonical_forms.get(key, value)

        if key not in seen:
            seen.add(key)
            result.append(value)

    return result


def build_canonical_forms(all_value_lists):
    """Decide the preferred spelling for values that differ only by case.

    We pick whichever spelling appears most often in the dataset, so the
    choice comes from the data rather than from a hard-coded guess.

    On a tie we prefer the spelling that is not entirely uppercase, since
    "Financial Assistance" reads better than "FINANCIAL ASSISTANCE" and
    ALL-CAPS values in this dataset are usually accidental. Any remaining
    tie is broken alphabetically so the result is always reproducible.
    """
    counts = Counter()
    for values in all_value_lists:
        for value in values:
            counts[re.sub(r"\s+", " ", str(value)).strip()] += 1

    by_key = {}
    for value, count in counts.items():
        by_key.setdefault(value.lower(), []).append((count, value))

    canonical = {}
    for key, candidates in by_key.items():
        if len(candidates) > 1:
            # Highest count wins, then non-ALL-CAPS, then alphabetical.
            candidates.sort(
                key=lambda pair: (-pair[0], pair[1].isupper(), pair[1])
            )
            canonical[key] = candidates[0][1]

    return canonical


# ===========================================================================
# STRUCTURED ELIGIBILITY EXTRACTION
# ===========================================================================
# Every pattern below requires the fact to be stated explicitly. When the
# wording is vague the field stays empty and the raw text is preserved, so
# the recommendation engine is never fed a guess.
# ===========================================================================

MIN_PLAUSIBLE_AGE = 0
MAX_PLAUSIBLE_AGE = 120

# "between 18 and 60 years", "between 18 to 59 years"
_AGE_RANGE_PATTERNS = (
    r"between\s+(\d{1,2})\s*(?:and|to|-|&)\s*(\d{1,2})\s*years",
    r"\b(\d{1,2})\s*(?:to|-)\s*(\d{1,2})\s*years\s+of\s+age",
    r"age\s+(?:group\s+)?of\s+(\d{1,2})\s*(?:to|-|and)\s*(\d{1,2})\s*years",
)

# "above 18 years", "minimum age of 21 years", "at least 18 years"
_AGE_MIN_PATTERNS = (
    r"(?:above|over|minimum\s+age\s+of|not\s+less\s+than|at\s+least)\s+"
    r"(?:the\s+age\s+of\s+)?(\d{1,2})\s*years",
    r"(\d{1,2})\s*years\s+(?:of\s+age\s+)?(?:and|or)\s+above",
)

# "below 60 years", "maximum age of 35 years", "up to 18 years of age"
_AGE_MAX_PATTERNS = (
    r"(?:below|under|maximum\s+age\s+of|not\s+more\s+than|not\s+exceeding|up\s*to)\s+"
    r"(?:the\s+age\s+of\s+)?(\d{1,2})\s*years",
    r"(\d{1,2})\s*years\s+(?:of\s+age\s+)?or\s+(?:less|below|younger)",
)

# "income should not exceed Rs. 2,50,000", "income below ₹8,00,000",
# "annual income up to 2.5 lakh"
_INCOME_MAX_PATTERN = (
    r"income[^.]{0,60}?"
    r"(?:not\s+exceed(?:ing)?|does\s+not\s+exceed|less\s+than|below|under|"
    r"up\s*to|upto|maximum\s+of|within)"
    r"[^\d₹]{0,25}"
    r"(?:rs\.?|₹|inr)?\s*"
    r"([\d][\d,]*(?:\.\d+)?)"
    r"\s*(lakhs?|lacs?|crores?|thousand)?"
)

# Words that mean the amount we matched is a BENEFIT (a loan, a subsidy, a
# coverage limit), not a cap on the applicant's income. Checked against the
# matched span, because "income-generating activities with a maximum cost of
# up to Rs 15,00,000" otherwise reads as an income limit of 15 lakh.
_INCOME_FALSE_POSITIVE_PATTERN = (
    r"income[-\s]*generat"
    r"|\b(?:cost|loan|coverage|cover|subsidy|assistance|grant|premium"
    r"|pension|scholarship|stipend|reimbursement|benefit)\b"
)

_SCALE_MULTIPLIERS = {
    "lakh": 100_000, "lakhs": 100_000, "lac": 100_000, "lacs": 100_000,
    "crore": 10_000_000, "crores": 10_000_000,
    "thousand": 1_000,
}

# An annual income above this is treated as a misread figure, not a limit.
MAX_PLAUSIBLE_INCOME = 100_000_000

# Gender. Female is checked first so "female" is never read as "male".
_GENDER_PATTERNS = (
    ("Female", (r"\bwom[ae]n\b", r"\bfemales?\b", r"\bgirls?\b", r"\bwidows?\b",
                r"\bmothers?\b", r"\bunmarried\s+girls?\b")),
    ("Male", (r"\bm[ae]n\b", r"\bmales?\b", r"\bboys?\b")),
)

# Social category. Only explicit mentions count.
_CATEGORY_PATTERNS = (
    ("SC", (r"\bscheduled\s+caste", r"\bsc\b", r"\bsc/st\b")),
    ("ST", (r"\bscheduled\s+tribe", r"\bst\b")),
    ("OBC", (r"\bother\s+backward\s+class", r"\bobc\b")),
    ("EWS", (r"\beconomically\s+weaker\s+section", r"\bews\b")),
    ("BPL", (r"\bbelow\s+poverty\s+line", r"\bbpl\b")),
    ("Minority", (r"\bminority\b", r"\bminorities\b")),
    ("PwD", (r"\bpersons?\s+with\s+disabilit", r"\bdivyang", r"\bpwd\b",
             r"\bdifferently\s+abled\b")),
    ("General", (r"\bgeneral\s+category\b", r"\bunreserved\b")),
)

_OCCUPATION_PATTERNS = (
    ("Farmer", (r"\bfarmers?\b", r"\bkisan\b", r"\bcultivators?\b",
                r"\bagriculturists?\b")),
    ("Student", (r"\bstudents?\b", r"\bscholars?\b", r"\bpupils?\b")),
    ("Artisan", (r"\bartisans?\b", r"\bcraftsmen\b", r"\bhandicraft\b")),
    ("Weaver", (r"\bweavers?\b", r"\bhandloom\b")),
    ("Fisherman", (r"\bfishermen\b", r"\bfisherman\b", r"\bfisher\s*folk\b")),
    ("Labourer", (r"\blabou?rers?\b", r"\bworkers?\b", r"\bshramik\b")),
    ("Entrepreneur", (r"\bentrepreneurs?\b", r"\bstart-?ups?\b",
                      r"\bself-?employed\b")),
    ("Teacher", (r"\bteachers?\b", r"\bfaculty\b")),
    ("Ex-Serviceman", (r"\bex-?servicem[ae]n\b", r"\bveterans?\b")),
)

_EDUCATION_PATTERNS = (
    ("Post Graduate", (r"\bpost[-\s]*graduate\b", r"\bmaster'?s\b", r"\bpost[-\s]*graduation\b", r"\bpg\b")),
    ("Graduate", (r"\bgraduate\b", r"\bbachelor'?s\b", r"\bgraduation\b", r"\bdegree\b")),
    ("Diploma", (r"\bdiploma\b", r"\biti\b", r"\bpolytechnic\b")),
    ("12th Pass", (r"\b12th\b", r"\bhigher\s+secondary\b", r"\b10\+2\b", r"\bintermediate\b")),
    ("10th Pass", (r"\b10th\b", r"\bmatriculate\b", r"\bmatriculation\b", r"\bsecondary\b")),
    ("Literate", (r"\bliterate\b", r"\bcan\s+read\s+and\s+write\b")),
)

_DISABILITY_PATTERNS = (
    ("Yes", (r"\bpersons?\s+with\s+disabilit", r"\bdivyang", r"\bpwd\b",
             r"\bdifferently\s+abled\b", r"\bdisabled\b", r"\bhandicapped\b")),
)

INDIAN_STATES_AND_UTS = (
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal", "Andaman and Nicobar Islands", "Chandigarh",
    "Dadra and Nagar Haveli", "Daman and Diu", "Delhi", "Jammu and Kashmir",
    "Ladakh", "Lakshadweep", "Puducherry",
)


def _first_pattern_match(text, rules):
    """Return the label of the first rule whose pattern appears in text."""
    for label, patterns in rules:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return label
    return ""


def extract_gender(text):
    """Read a gender restriction from the text.

    Returns "" when the scheme is not restricted by gender. Crucially, a
    scheme that mentions BOTH genders - "Scholarships ... To Meritorious
    Boys and Girls", "Divyang Boys/Girls Marriage Grant" - is open to
    everyone, so recording it as Female would wrongly exclude half the
    applicants from any future matching.
    """
    if not text:
        return ""

    matched = set()
    for label, patterns in _GENDER_PATTERNS:
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matched.add(label)
                break

    # Both mentioned - not a restriction at all.
    if len(matched) != 1:
        return ""

    return matched.pop()


def extract_age_range(text):
    """Read an age range from eligibility text. Returns (min, max).

    Either value may be "" when the text does not state it.
    """
    if not text:
        return "", ""

    for pattern in _AGE_RANGE_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            low, high = int(match.group(1)), int(match.group(2))
            # A "range" that runs backwards is a misread, not a range.
            if low <= high and MIN_PLAUSIBLE_AGE <= low and high <= MAX_PLAUSIBLE_AGE:
                return low, high

    age_min = age_max = ""

    for pattern in _AGE_MIN_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            if MIN_PLAUSIBLE_AGE <= value <= MAX_PLAUSIBLE_AGE:
                age_min = value
            break

    for pattern in _AGE_MAX_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = int(match.group(1))
            if MIN_PLAUSIBLE_AGE <= value <= MAX_PLAUSIBLE_AGE:
                age_max = value
            break

    # Contradictory bounds mean we misread one of them - drop both rather
    # than store something impossible.
    if age_min != "" and age_max != "" and age_min > age_max:
        return "", ""

    return age_min, age_max


def extract_income_max(text):
    """Read an upper income limit as a plain number of rupees.

    Handles "Rs. 2,50,000", "₹8,00,000", "2.5 lakh", "up to 1 crore".
    Returns "" when no limit is stated.
    """
    if not text:
        return ""

    match = re.search(_INCOME_MAX_PATTERN, text, re.IGNORECASE)
    if not match:
        return ""

    # Reject the match if the wording shows this is a benefit amount rather
    # than a limit on the applicant's income.
    if re.search(_INCOME_FALSE_POSITIVE_PATTERN, match.group(0), re.IGNORECASE):
        return ""

    digits = match.group(1).replace(",", "").rstrip(".")
    if not digits:
        return ""

    try:
        amount = float(digits)
    except ValueError:
        return ""

    scale = (match.group(2) or "").lower()
    amount *= _SCALE_MULTIPLIERS.get(scale, 1)

    if amount <= 0 or amount > MAX_PLAUSIBLE_INCOME:
        return ""

    return int(round(amount))


def extract_state(text):
    """Find an Indian state or UT named in the text.

    When several are named the most frequently mentioned one wins, with the
    earliest mention breaking a tie, so the result is always reproducible.
    """
    if not text:
        return ""

    hits = {}
    for state in INDIAN_STATES_AND_UTS:
        matches = list(re.finditer(
            r"(?<![A-Za-z])" + re.escape(state) + r"(?![A-Za-z])",
            text, re.IGNORECASE,
        ))
        if matches:
            hits[state] = (len(matches), -matches[0].start())

    if not hits:
        return ""

    return max(hits, key=lambda state: hits[state])


def extract_structured_eligibility(eligibility_text, fallback_text=""):
    """Build the structured eligibility fields from raw text.

    `eligibility_text` is the scheme's eligibility section, which is the
    reliable source. `fallback_text` (the description) is only used when
    no eligibility section exists yet - the scraper does not fetch detail
    pages today, so without the fallback every field would be empty.

    Every value is either clearly supported by the text or left as "".
    """
    primary = clean_text(eligibility_text)
    text = primary or clean_text(fallback_text)

    if not text:
        return {column: "" for column in ELIGIBILITY_COLUMNS}

    age_min, age_max = extract_age_range(text)

    return {
        "age_min": age_min,
        "age_max": age_max,
        "gender": extract_gender(text),
        "income_max": extract_income_max(text),
        "category": _first_pattern_match(text, _CATEGORY_PATTERNS),
        "occupation": _first_pattern_match(text, _OCCUPATION_PATTERNS),
        "eligibility_state": extract_state(text),
        "education": _first_pattern_match(text, _EDUCATION_PATTERNS),
        "disability": _first_pattern_match(text, _DISABILITY_PATTERNS),
    }


# ===========================================================================
# DEDUPLICATION
# ===========================================================================

def build_dedup_key(record):
    """Pick the most reliable identity available for a scheme.

    Tried in order of trustworthiness, because in this dataset neither the
    slug nor the title is unique on its own (91 slug collisions and 77 title
    collisions across 3,680 records):

        1. source_url     - the exact page the record came from
        2. official_url   - the department's own site
        3. slug + title   - together, far more reliable than either alone
        4. normalized title

    Returns (key_kind, key_value).
    """
    for field, kind in (("source_url", "source_url"),
                        ("official_url", "official_url")):
        value = clean_text(record.get(field))
        if value:
            return kind, value.lower().rstrip("/")

    slug = clean_text(record.get("slug")).lower()
    title = re.sub(r"[^a-z0-9]+", " ", clean_text(record.get("title")).lower()).strip()

    if slug and title:
        return "slug+title", f"{slug}|{title}"
    if slug:
        return "slug", slug

    return "title", title


def merge_records(base, incoming):
    """Fill gaps in `base` using `incoming`, without overwriting anything.

    Duplicate rows often carry complementary information, so we keep every
    value already present and only fill the fields that were empty.
    """
    merged = dict(base)
    for key, value in incoming.items():
        if is_empty(merged.get(key)) and not is_empty(value):
            merged[key] = value
    return merged


def deduplicate(records):
    """Collapse duplicate schemes into one canonical record each.

    Returns (unique_records, stats).
    """
    canonical = {}
    order = []
    key_kinds = Counter()

    for record in records:
        kind, key = build_dedup_key(record)
        key_kinds[kind] += 1

        if key in canonical:
            canonical[key] = merge_records(canonical[key], record)
        else:
            canonical[key] = record
            order.append(key)

    unique = [canonical[key] for key in order]

    stats = {
        "records_before": len(records),
        "duplicates_removed": len(records) - len(unique),
        "records_after": len(unique),
        "key_kind_counts": dict(key_kinds),
    }
    return unique, stats


# ===========================================================================
# MAIN PIPELINE
# ===========================================================================

def process_dataframe(df):
    """Run the full processing pipeline over the scraped dataframe.

    The input is copied first, so the caller's dataframe is never modified.
    """
    df = df.copy()

    # Make sure every expected column exists, so a CSV produced before the
    # scraper is extended still processes cleanly.
    for column in OUTPUT_COLUMNS:
        if column not in df.columns:
            df[column] = ""

    raw_records = df.to_dict(orient="records")

    # --- Normalization ------------------------------------------------
    # Work out the preferred spellings once, across the whole dataset,
    # before normalizing any individual row.
    category_lists = [parse_list_field(r.get("schemeCategory")) for r in raw_records]
    tag_lists = [parse_list_field(r.get("tags")) for r in raw_records]

    category_canonical = build_canonical_forms(category_lists)
    tag_canonical = build_canonical_forms(tag_lists)

    processed = []
    for record, categories, tags in zip(raw_records, category_lists, tag_lists):
        row = dict(record)

        row["categories_normalized"] = json.dumps(
            normalize_list_values(categories, category_canonical), ensure_ascii=False
        )
        row["tags_normalized"] = json.dumps(
            normalize_list_values(tags, tag_canonical), ensure_ascii=False
        )

        # --- Raw preservation ----------------------------------------
        # Keep the source wording for each content field. These are empty
        # until the scraper fetches detail pages; the columns exist now so
        # the layout does not change again later.
        for content_column, raw_column in (
            ("eligibility", "eligibility_raw"),
            ("beneficiaries", "beneficiaries_raw"),
            ("benefits", "benefits_raw"),
            ("documents_required", "documents_required_raw"),
        ):
            if is_empty(row.get(raw_column)) and not is_empty(row.get(content_column)):
                row[raw_column] = str(row[content_column]).strip()

        # --- Structured eligibility ----------------------------------
        row.update(extract_structured_eligibility(
            row.get("eligibility_raw") or row.get("eligibility"),
            fallback_text=row.get("description"),
        ))

        # --- Provenance ----------------------------------------------
        # Deliberately left as-is. Inventing an India.gov.in URL from the
        # slug would be fabrication, so these stay empty until the scraper
        # records the page it actually fetched.
        for column in PROVENANCE_COLUMNS:
            if is_empty(row.get(column)):
                row[column] = ""

        processed.append(row)

    # --- Deduplication ------------------------------------------------
    unique, dedup_stats = deduplicate(processed)

    result = pd.DataFrame(unique, columns=OUTPUT_COLUMNS)
    return result, dedup_stats


def build_quality_report(before_df, after_df, dedup_stats):
    """Summarise what the pipeline produced, for eyeballing after a run."""
    def populated(column):
        if column not in after_df.columns:
            return 0
        return int(after_df[column].apply(lambda v: not is_empty(v)).sum())

    total = len(after_df)

    report = {
        "records_scraped": int(len(before_df)),
        "records_before_dedup": dedup_stats["records_before"],
        "duplicates_removed": dedup_stats["duplicates_removed"],
        "unique_schemes": dedup_stats["records_after"],
        "dedup_key_used": dedup_stats["key_kind_counts"],
        "fields_populated": {c: populated(c) for c in OUTPUT_COLUMNS},
        "fields_empty": {c: total - populated(c) for c in OUTPUT_COLUMNS},
        "records_with_any_structured_eligibility": int(
            after_df[ELIGIBILITY_COLUMNS]
            .apply(lambda row: any(not is_empty(v) for v in row), axis=1)
            .sum()
        ),
        "records_with_eligibility_raw": populated("eligibility_raw"),
        "records_with_source_url": populated("source_url"),
        "records_with_official_url": populated("official_url"),
        "records_with_last_updated": populated("last_updated"),
    }
    return report


def validate(after_df):
    """Basic sanity checks on the final dataset. Returns a list of issues."""
    issues = []

    for column in EXISTING_COLUMNS:
        if column not in after_df.columns:
            issues.append(f"existing column '{column}' is missing from the output")

    missing_title = int(after_df["title"].apply(is_empty).sum())
    if missing_title:
        issues.append(f"{missing_title} records have no title")

    for column in ("age_min", "age_max"):
        values = after_df[column]
        bad = values.apply(
            lambda v: not is_empty(v)
            and not (MIN_PLAUSIBLE_AGE <= int(v) <= MAX_PLAUSIBLE_AGE)
        ).sum()
        if bad:
            issues.append(f"{bad} records have an out-of-range {column}")

    bad_income = after_df["income_max"].apply(
        lambda v: not is_empty(v) and (float(v) < 0 or float(v) > MAX_PLAUSIBLE_INCOME)
    ).sum()
    if bad_income:
        issues.append(f"{bad_income} records have an implausible income_max")

    for column in ("source_url", "official_url"):
        bad_url = after_df[column].apply(
            lambda v: not is_empty(v) and not str(v).startswith(("http://", "https://"))
        ).sum()
        if bad_url:
            issues.append(f"{bad_url} records have a malformed {column}")

    return issues


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clean, normalize and deduplicate the scraped scheme dataset."
    )
    parser.add_argument("input_csv", help="scraped CSV, e.g. government_schemes.csv")
    parser.add_argument(
        "-o", "--output",
        help="output CSV (default: <input>_processed.csv)",
    )
    parser.add_argument(
        "-r", "--report",
        help="write the quality report as JSON to this path",
    )
    parser.add_argument(
        "--sample", type=int, default=0,
        help="process only the first N rows (useful for a quick check)",
    )
    args = parser.parse_args(argv)

    if not os.path.exists(args.input_csv):
        print(f"error: {args.input_csv} not found", file=sys.stderr)
        return 1

    # utf-8-sig strips the byte-order mark the scraper's CSV starts with.
    before_df = pd.read_csv(args.input_csv, encoding="utf-8-sig", dtype=str)
    if args.sample:
        before_df = before_df.head(args.sample)

    after_df, dedup_stats = process_dataframe(before_df)

    output_path = args.output or (
        os.path.splitext(args.input_csv)[0] + "_processed.csv"
    )
    after_df.to_csv(output_path, index=False, encoding="utf-8-sig")

    report = build_quality_report(before_df, after_df, dedup_stats)
    issues = validate(after_df)
    report["validation_issues"] = issues

    print(f"input   : {args.input_csv}  ({len(before_df)} records)")
    print(f"output  : {output_path}  ({len(after_df)} records)")
    print(f"columns : {len(before_df.columns)} -> {len(after_df.columns)}")
    print(f"removed : {dedup_stats['duplicates_removed']} duplicates")
    print(f"eligibility extracted for "
          f"{report['records_with_any_structured_eligibility']} records")
    print(f"validation issues: {len(issues)}")
    for issue in issues:
        print(f"  - {issue}")

    if args.report:
        with open(args.report, "w", encoding="utf-8") as handle:
            json.dump(report, handle, indent=2, ensure_ascii=False)
        print(f"report  : {args.report}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
