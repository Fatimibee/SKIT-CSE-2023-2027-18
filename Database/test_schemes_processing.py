"""
test_schemes_processing.py
---------------------------
Tests for schemes_processing.py.

All test data here is written by hand for the tests. Nothing is taken from
a real citizen record.

Run with:

    python -m pytest test_schemes_processing.py -v
"""

import json

import pandas as pd
import pytest

from schemes_processing import (
    ELIGIBILITY_COLUMNS,
    EXISTING_COLUMNS,
    OUTPUT_COLUMNS,
    build_canonical_forms,
    build_dedup_key,
    clean_text,
    deduplicate,
    extract_age_range,
    extract_gender,
    extract_income_max,
    extract_state,
    extract_structured_eligibility,
    is_empty,
    merge_records,
    normalize_list_values,
    parse_list_field,
    process_dataframe,
    validate,
)


# ===========================================================================
# Reading the CSV's list-in-a-string fields
# ===========================================================================

def test_parse_list_field_reads_a_literal_list():
    assert parse_list_field("['Health & Wellness']") == ["Health & Wellness"]


def test_parse_list_field_drops_none_entries():
    # The scraper writes a literal None into some tag lists.
    value = "['Health Insurance', 'Critical Illnesses', None]"
    assert parse_list_field(value) == ["Health Insurance", "Critical Illnesses"]


def test_parse_list_field_handles_empty_list():
    assert parse_list_field("[]") == []


@pytest.mark.parametrize("value", ["", None, "nan", float("nan")])
def test_parse_list_field_handles_empty_values(value):
    assert parse_list_field(value) == []


def test_parse_list_field_handles_a_plain_string():
    assert parse_list_field("Health & Wellness") == ["Health & Wellness"]


# ===========================================================================
# Normalization
# ===========================================================================

def test_normalize_trims_whitespace():
    assert normalize_list_values(["  Health & Wellness  "]) == ["Health & Wellness"]


def test_normalize_collapses_inner_whitespace():
    assert normalize_list_values(["Health   &    Wellness"]) == ["Health & Wellness"]


def test_normalize_removes_case_insensitive_duplicates():
    values = ["Scholarship", "SCHOLARSHIP", "scholarship"]
    assert len(normalize_list_values(values)) == 1


def test_normalize_drops_empty_values():
    assert normalize_list_values(["Farmer", "", "   ", "Subsidy"]) == [
        "Farmer", "Subsidy",
    ]


def test_normalize_preserves_order():
    values = ["Housing & Shelter", "Social welfare & Empowerment"]
    assert normalize_list_values(values) == values


def test_normalize_does_not_merge_different_meanings():
    # These look similar but are distinct categories - both must survive.
    values = ["Skills & Employment", "Education & Learning"]
    assert len(normalize_list_values(values)) == 2


def test_canonical_form_prefers_the_more_common_spelling():
    # "Financial Assistance" appears twice, "FINANCIAL ASSISTANCE" once.
    lists = [
        ["Financial Assistance"],
        ["Financial Assistance"],
        ["FINANCIAL ASSISTANCE"],
    ]
    canonical = build_canonical_forms(lists)
    assert canonical["financial assistance"] == "Financial Assistance"


def test_canonical_form_applied_during_normalization():
    canonical = {"pwd": "PwD"}
    assert normalize_list_values(["PWD"], canonical) == ["PwD"]


# ===========================================================================
# Age extraction
# ===========================================================================

@pytest.mark.parametrize("text,expected", [
    ("Applicant must be between 18 and 60 years of age", (18, 60)),
    ("beneficiaries between 18 to 59 years", (18, 59)),
    ("students between 13 and 18 years", (13, 18)),
    ("age group of 12 to 20 years", (12, 20)),
])
def test_age_range_is_extracted(text, expected):
    assert extract_age_range(text) == expected


def test_age_minimum_only():
    age_min, age_max = extract_age_range("applicants above 18 years may apply")
    assert age_min == 18
    assert age_max == ""


def test_age_maximum_only():
    age_min, age_max = extract_age_range("women below 40 years are eligible")
    assert age_min == ""
    assert age_max == 40


def test_no_age_returns_empty():
    assert extract_age_range("the scheme provides financial support") == ("", "")


def test_backwards_age_range_is_rejected():
    # "between 60 and 18" is a misread, not a range.
    assert extract_age_range("between 60 and 18 years") == ("", "")


def test_impossible_age_is_rejected():
    assert extract_age_range("above 99 years") == (99, "")
    assert extract_age_range("minimum age of 00 years")[0] == 0


# ===========================================================================
# Income extraction
# ===========================================================================

@pytest.mark.parametrize("text,expected", [
    ("annual income should not exceed Rs. 2,50,000", 250000),
    ("family income below \u20b98,00,000", 800000),
    ("income does not exceed \u20b91,80,000", 180000),
    ("annual income up to 2.5 lakh", 250000),
    ("income less than 1 crore", 10000000),
    ("income not exceeding Rs 50 thousand", 50000),
    ("total income under INR 300000", 300000),
])
def test_income_max_is_extracted(text, expected):
    assert extract_income_max(text) == expected


@pytest.mark.parametrize("text", [
    "",
    "the scheme provides a subsidy to farmers",
    "income certificate is required",          # no limit stated
    "beneficiaries receive Rs. 5,000 monthly",  # a benefit, not an income cap
])
def test_no_income_limit_returns_empty(text):
    assert extract_income_max(text) == ""


def test_implausible_income_is_rejected():
    # A 12-digit figure is a misread number, not an income limit.
    assert extract_income_max("income below Rs. 999999999999") == ""


# ===========================================================================
# Gender / category / occupation / state
# ===========================================================================

@pytest.mark.parametrize("text,expected", [
    ("scheme for women entrepreneurs", "Female"),
    ("available to girl students", "Female"),
    ("widows of ex-servicemen", "Female"),
    ("for male candidates only", "Male"),
    ("boys residing in hostels", "Male"),
])
def test_gender_is_extracted(text, expected):
    assert extract_structured_eligibility(text)["gender"] == expected


def test_female_is_not_misread_as_male():
    assert extract_structured_eligibility("female applicants")["gender"] == "Female"


def test_gender_absent_returns_empty():
    result = extract_structured_eligibility("all residents of the state")
    assert result["gender"] == ""


@pytest.mark.parametrize("text,expected", [
    ("belonging to Scheduled Caste", "SC"),
    ("Scheduled Tribe families", "ST"),
    ("Other Backward Class candidates", "OBC"),
    ("economically weaker section", "EWS"),
    ("families below poverty line", "BPL"),
    ("persons with disabilities", "PwD"),
])
def test_category_is_extracted(text, expected):
    assert extract_structured_eligibility(text)["category"] == expected


@pytest.mark.parametrize("text,expected", [
    ("small and marginal farmers", "Farmer"),
    ("students pursuing higher education", "Student"),
    ("handloom weavers", "Weaver"),
    ("registered artisans", "Artisan"),
    ("young entrepreneurs", "Entrepreneur"),
])
def test_occupation_is_extracted(text, expected):
    assert extract_structured_eligibility(text)["occupation"] == expected


def test_state_is_extracted():
    assert extract_state("residents of Rajasthan are eligible") == "Rajasthan"


def test_multi_word_state_is_extracted():
    assert extract_state("scheme of Madhya Pradesh government") == "Madhya Pradesh"


def test_most_mentioned_state_wins():
    text = "Government of Kerala. Applicants in Kerala. Also mentions Goa."
    assert extract_state(text) == "Kerala"


def test_no_state_returns_empty():
    assert extract_state("a central government scheme") == ""


# ===========================================================================
# Structured eligibility as a whole
# ===========================================================================

def test_full_eligibility_extraction():
    text = (
        "Applicant must be a woman between 18 and 60 years of age, "
        "belonging to Scheduled Caste, residing in Rajasthan, and the "
        "annual family income should not exceed Rs. 2,50,000."
    )
    result = extract_structured_eligibility(text)

    assert result["age_min"] == 18
    assert result["age_max"] == 60
    assert result["gender"] == "Female"
    assert result["category"] == "SC"
    assert result["income_max"] == 250000
    assert result["eligibility_state"] == "Rajasthan"


def test_vague_text_extracts_nothing_rather_than_guessing():
    result = extract_structured_eligibility(
        "Eligibility is decided by the competent authority as applicable."
    )
    assert all(value == "" for value in result.values())


def test_empty_text_returns_all_empty():
    result = extract_structured_eligibility("")
    assert set(result.keys()) == set(ELIGIBILITY_COLUMNS)
    assert all(value == "" for value in result.values())


def test_description_used_only_as_a_fallback():
    # When real eligibility text exists it wins over the description.
    result = extract_structured_eligibility(
        eligibility_text="applicants above 21 years",
        fallback_text="scheme for persons between 40 and 50 years",
    )
    assert result["age_min"] == 21
    assert result["age_max"] == ""


# ===========================================================================
# Deduplication
# ===========================================================================

def test_source_url_is_preferred_as_the_dedup_key():
    kind, _ = build_dedup_key({
        "source_url": "https://india.gov.in/scheme/thasp",
        "slug": "thasp",
        "title": "Tripura Health Scheme",
    })
    assert kind == "source_url"


def test_slug_and_title_used_when_no_url():
    kind, _ = build_dedup_key({"slug": "thasp", "title": "Tripura Health Scheme"})
    assert kind == "slug+title"


def test_title_alone_is_the_last_resort():
    kind, _ = build_dedup_key({"title": "Some Scheme"})
    assert kind == "title"


def test_same_slug_different_scheme_is_not_merged():
    # Slug alone is unreliable in this dataset, so two different schemes
    # sharing a slug must stay separate.
    records = [
        {"slug": "abc", "title": "Housing Scheme", "description": "one"},
        {"slug": "abc", "title": "Pension Scheme", "description": "two"},
    ]
    unique, stats = deduplicate(records)
    assert stats["records_after"] == 2


def test_identical_records_are_merged():
    records = [
        {"slug": "thasp", "title": "Tripura Health Scheme", "description": "x"},
        {"slug": "thasp", "title": "Tripura Health Scheme", "description": "x"},
    ]
    unique, stats = deduplicate(records)
    assert stats["records_after"] == 1
    assert stats["duplicates_removed"] == 1


def test_duplicates_are_merged_without_losing_information():
    records = [
        {"slug": "s", "title": "T", "description": "full text", "benefits": ""},
        {"slug": "s", "title": "T", "description": "", "benefits": "Rs 5000"},
    ]
    unique, _ = deduplicate(records)
    assert len(unique) == 1
    # Both rows contributed - nothing was thrown away.
    assert unique[0]["description"] == "full text"
    assert unique[0]["benefits"] == "Rs 5000"


def test_merge_never_overwrites_an_existing_value():
    base = {"description": "original"}
    merged = merge_records(base, {"description": "replacement"})
    assert merged["description"] == "original"


def test_dedup_reports_statistics():
    records = [{"slug": "a", "title": "A"}, {"slug": "a", "title": "A"}]
    _, stats = deduplicate(records)
    assert stats["records_before"] == 2
    assert stats["duplicates_removed"] == 1
    assert stats["records_after"] == 1


# ===========================================================================
# End-to-end
# ===========================================================================

@pytest.fixture
def sample_scraped_df():
    """A small dataframe shaped exactly like the scraper's CSV output."""
    return pd.DataFrame([
        {
            "title": "Tripura Health Insuarance Scheme For Poor",
            "ministry": None,
            "schemeCategory": "['Health & Wellness']",
            "description": (
                "The scheme provides cashless treatment to families below "
                "poverty line in Tripura whose annual income does not "
                "exceed Rs. 1,80,000."
            ),
            "beneficiaryState": None,
            "npiMinistry": "[]",
            "slug": "thasp",
            "tags": "['Health Insurance', 'Critical Illnesses', None]",
            "__typename": "Search",
        },
        {
            "title": "Him Kukkut Palan Yojna",
            "ministry": "Ministry Of Agriculture and Farmers Welfare",
            "schemeCategory": "['Agriculture,Rural & Environment']",
            "description": (
                "Subsidy for farmers in Himachal Pradesh engaged in poultry "
                "farming, for applicants above 18 years."
            ),
            "beneficiaryState": None,
            "npiMinistry": "[]",
            "slug": "hkpy",
            "tags": "['Farmer', 'FARMER', 'Subsidy']",
            "__typename": "Search",
        },
        {
            # An exact duplicate of the first record.
            "title": "Tripura Health Insuarance Scheme For Poor",
            "ministry": None,
            "schemeCategory": "['Health & Wellness']",
            "description": (
                "The scheme provides cashless treatment to families below "
                "poverty line in Tripura whose annual income does not "
                "exceed Rs. 1,80,000."
            ),
            "beneficiaryState": None,
            "npiMinistry": "[]",
            "slug": "thasp",
            "tags": "['Health Insurance', 'Critical Illnesses', None]",
            "__typename": "Search",
        },
    ])


def test_pipeline_keeps_every_existing_column(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    for column in EXISTING_COLUMNS:
        assert column in result.columns


def test_pipeline_preserves_existing_values(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    row = result[result["slug"] == "hkpy"].iloc[0]

    assert row["title"] == "Him Kukkut Palan Yojna"
    assert row["ministry"] == "Ministry Of Agriculture and Farmers Welfare"
    assert row["schemeCategory"] == "['Agriculture,Rural & Environment']"
    assert row["__typename"] == "Search"


def test_pipeline_adds_the_full_schema(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    assert list(result.columns) == OUTPUT_COLUMNS


def test_pipeline_removes_the_duplicate(sample_scraped_df):
    result, stats = process_dataframe(sample_scraped_df)
    assert stats["records_before"] == 3
    assert stats["duplicates_removed"] == 1
    assert len(result) == 2


def test_pipeline_normalizes_tags(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    row = result[result["slug"] == "hkpy"].iloc[0]
    tags = json.loads(row["tags_normalized"])

    # "Farmer" and "FARMER" collapse into one; the None entry is gone.
    assert tags == ["Farmer", "Subsidy"]


def test_pipeline_drops_none_from_normalized_tags(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    row = result[result["slug"] == "thasp"].iloc[0]
    assert json.loads(row["tags_normalized"]) == [
        "Health Insurance", "Critical Illnesses",
    ]


def test_pipeline_extracts_eligibility_from_description(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    row = result[result["slug"] == "thasp"].iloc[0]

    assert row["income_max"] == 180000
    assert row["category"] == "BPL"
    assert row["eligibility_state"] == "Tripura"


def test_pipeline_leaves_unavailable_fields_empty(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    row = result.iloc[0]

    # These come from the scheme detail page, which the scraper does not
    # fetch yet - they must be empty, never invented.
    for column in ("eligibility", "benefits", "documents_required",
                   "source_url", "official_url", "last_updated"):
        assert is_empty(row[column]), f"{column} should be empty, got {row[column]!r}"


def test_pipeline_output_passes_validation(sample_scraped_df):
    result, _ = process_dataframe(sample_scraped_df)
    assert validate(result) == []


def test_pipeline_handles_an_empty_dataframe():
    empty = pd.DataFrame(columns=EXISTING_COLUMNS)
    result, stats = process_dataframe(empty)
    assert len(result) == 0
    assert stats["records_after"] == 0


def test_pipeline_is_deterministic(sample_scraped_df):
    first, _ = process_dataframe(sample_scraped_df.copy())
    second, _ = process_dataframe(sample_scraped_df.copy())
    assert first.equals(second)


# ===========================================================================
# Small helpers
# ===========================================================================

@pytest.mark.parametrize("value", [None, "", "   ", "nan", "None", float("nan")])
def test_is_empty_true(value):
    assert is_empty(value)


@pytest.mark.parametrize("value", ["Rajasthan", 0, "0"])
def test_is_empty_false(value):
    assert not is_empty(value)


def test_clean_text_collapses_whitespace():
    assert clean_text("  a   b \n c ") == "a b c"


def test_clean_text_on_empty_returns_empty_string():
    assert clean_text(None) == ""


# ===========================================================================
# Income false positives - a benefit amount is not an income limit
# ===========================================================================

@pytest.mark.parametrize("text", [
    "loans for income-generating activities with a maximum cost of up to \u20b915,00,000",
    "health coverage of up to Rs. 5,00,000 for low income families",
    "income support: subsidy of up to Rs. 10,000 per year",
    "scholarship of up to Rs. 50,000 for students with low income",
    "monthly pension of up to Rs. 3,000 for low income seniors",
])
def test_benefit_amount_is_not_read_as_income_limit(text):
    assert extract_income_max(text) == ""


def test_genuine_income_limit_still_extracted_alongside_benefit_wording():
    # A real cap must still be found even in a sentence about benefits.
    text = "annual family income does not exceed \u20b91,80,000"
    assert extract_income_max(text) == 180000


# ===========================================================================
# Gender - schemes open to both genders are not a restriction
# ===========================================================================

@pytest.mark.parametrize("text", [
    "Scholarships for meritorious boys and girls",
    "Divyang Boys/ Girls Marriage Incentive Grant",
    "available to all men and women of the state",
])
def test_both_genders_mentioned_returns_empty(text):
    assert extract_structured_eligibility(text)["gender"] == ""


@pytest.mark.parametrize("text,expected", [
    ("Girl Students Health & Hygiene Scheme", "Female"),
    ("Widow B.Ed Scheme", "Female"),
    ("assistance in marriage of man workers", "Male"),
])
def test_single_gender_still_extracted(text, expected):
    assert extract_structured_eligibility(text)["gender"] == expected
