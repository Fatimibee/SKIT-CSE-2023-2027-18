"""
test_document_verifier.py
--------------------------
Unit tests for document_verifier.py.

The behaviour these tests pin down most carefully is the distinction
between MISSING information (fine - do not reject the document) and
INVALID information (flag it).

All test data is SYNTHETIC.
"""

import os
import sys
from datetime import date, timedelta

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from document_verifier import verify_extracted_data  # noqa: E402
from field_extractor import calculate_age, extract_fields  # noqa: E402


def _fields(**overrides):
    """Build a full field dict that is valid by default, then override
    whichever fields a test wants to poke at."""
    data = {
        "name": "Rahul Sharma",
        "date_of_birth": "12/05/2002",
        "age": calculate_age("12/05/2002"),
        "gender": "Male",
        "category": "OBC",
        "annual_income": 180000,
        "state": "Rajasthan",
        "district": "Jaipur",
        "address": "Jaipur, Rajasthan",
        "document_type": "Income Certificate",
    }
    data.update(overrides)
    return data


# ===========================================================================
# The happy path
# ===========================================================================

def test_fully_valid_data_passes():
    result = verify_extracted_data(_fields())

    assert result["is_valid"] is True
    assert result["issues"] == []
    assert result["missing_fields"] == []
    assert len(result["extracted_fields"]) == 10


def test_response_always_has_the_expected_shape():
    result = verify_extracted_data(_fields())
    assert set(result.keys()) == {
        "is_valid", "issues", "missing_fields", "extracted_fields", "qr_verified",
    }


# ===========================================================================
# Missing information must NOT invalidate the document
# ===========================================================================

def test_missing_optional_fields_do_not_make_the_document_invalid():
    result = verify_extracted_data(_fields(
        date_of_birth=None, age=None, gender=None, category=None,
    ))

    assert result["is_valid"] is True
    assert result["issues"] == []
    assert set(result["missing_fields"]) == {
        "date_of_birth", "age", "gender", "category",
    }


def test_everything_missing_is_still_not_invalid():
    empty = {field: None for field in _fields()}
    empty["document_type"] = "Unknown"

    result = verify_extracted_data(empty)

    assert result["is_valid"] is True
    assert result["issues"] == []
    assert len(result["missing_fields"]) == 10
    assert result["extracted_fields"] == []


def test_unknown_document_type_counts_as_missing_not_invalid():
    result = verify_extracted_data(_fields(document_type="Unknown"))

    assert result["is_valid"] is True
    assert "document_type" in result["missing_fields"]


# ===========================================================================
# Robustness - must never crash
# ===========================================================================

@pytest.mark.parametrize("bad_input", [None, {}, {"name": "Rahul Sharma"}])
def test_partial_or_empty_input_does_not_crash(bad_input):
    result = verify_extracted_data(bad_input)
    assert isinstance(result["is_valid"], bool)
    assert isinstance(result["issues"], list)


# ===========================================================================
# Invalid date of birth
# ===========================================================================

def test_impossible_date_of_birth_is_flagged():
    result = verify_extracted_data(_fields(date_of_birth="32/13/2002", age=None))

    assert result["is_valid"] is False
    assert "Invalid date of birth" in result["issues"]


def test_future_date_of_birth_is_flagged():
    tomorrow = date.today() + timedelta(days=1)
    result = verify_extracted_data(_fields(
        date_of_birth=tomorrow.strftime("%d/%m/%Y"), age=None,
    ))

    assert result["is_valid"] is False
    assert "Date of birth is in the future" in result["issues"]


def test_unrealistically_old_date_of_birth_is_flagged():
    result = verify_extracted_data(_fields(date_of_birth="01/01/1850", age=None))

    assert result["is_valid"] is False
    assert "Date of birth is unrealistically old" in result["issues"]


# ===========================================================================
# Age
# ===========================================================================

@pytest.mark.parametrize("bad_age", [-5, 200, 999])
def test_unreasonable_age_is_flagged(bad_age):
    result = verify_extracted_data(_fields(age=bad_age, date_of_birth=None))

    assert result["is_valid"] is False
    assert any("outside the expected range" in issue for issue in result["issues"])


def test_age_that_contradicts_the_date_of_birth_is_flagged():
    # DOB says early 2000s, but the document claims age 70.
    result = verify_extracted_data(_fields(date_of_birth="12/05/2002", age=70))

    assert result["is_valid"] is False
    assert "Age does not match the date of birth" in result["issues"]


def test_age_within_one_year_of_the_date_of_birth_is_accepted():
    # Certificates often state an age "as on 1st January", so a one-year
    # difference is tolerated on purpose.
    real_age = calculate_age("12/05/2002")
    result = verify_extracted_data(_fields(date_of_birth="12/05/2002",
                                           age=real_age - 1))

    assert result["is_valid"] is True


def test_non_integer_age_is_flagged():
    result = verify_extracted_data(_fields(age="twenty four", date_of_birth=None))

    assert result["is_valid"] is False
    assert "Age is not a whole number" in result["issues"]


# ===========================================================================
# Gender
# ===========================================================================

def test_unsupported_gender_value_is_flagged():
    result = verify_extracted_data(_fields(gender="Xyz"))

    assert result["is_valid"] is False
    assert any("Gender is not one of the supported values" in issue
               for issue in result["issues"])


@pytest.mark.parametrize("gender", ["Male", "Female", "Other"])
def test_supported_gender_values_pass(gender):
    assert verify_extracted_data(_fields(gender=gender))["is_valid"] is True


# ===========================================================================
# Category
# ===========================================================================

@pytest.mark.parametrize("category", ["SC", "ST", "OBC", "EWS", "GENERAL", "OTHER"])
def test_supported_categories_pass(category):
    assert verify_extracted_data(_fields(category=category))["is_valid"] is True


def test_unnormalised_category_is_flagged():
    result = verify_extracted_data(_fields(category="ZZZZ"))

    assert result["is_valid"] is False
    assert any("could not be normalised" in issue for issue in result["issues"])


# ===========================================================================
# Annual income
# ===========================================================================

def test_negative_income_is_flagged():
    result = verify_extracted_data(_fields(annual_income=-5000))

    assert result["is_valid"] is False
    assert "Annual income cannot be negative" in result["issues"]


def test_non_numeric_income_is_flagged():
    result = verify_extracted_data(_fields(annual_income="1,80,000"))

    assert result["is_valid"] is False
    assert "Annual income is not a number" in result["issues"]


def test_absurdly_high_income_is_flagged():
    # Catches an Aadhaar/account number accidentally read as an income.
    result = verify_extracted_data(_fields(annual_income=999_999_999_999))

    assert result["is_valid"] is False
    assert "Annual income is unrealistically high" in result["issues"]


def test_zero_income_is_valid():
    # A genuinely zero declared income is legitimate, not an error.
    assert verify_extracted_data(_fields(annual_income=0))["is_valid"] is True


# ===========================================================================
# Name garbage detection
# ===========================================================================

@pytest.mark.parametrize("garbage_name", ["|||###", "@@@@", "1234567", "X"])
def test_garbage_name_is_flagged(garbage_name):
    result = verify_extracted_data(_fields(name=garbage_name))

    assert result["is_valid"] is False
    assert "Extracted name does not look like a valid name" in result["issues"]


@pytest.mark.parametrize("good_name", [
    "Rahul Sharma", "D'Souza", "Anne-Marie Fernandes", "Priya",
])
def test_plausible_names_pass(good_name):
    assert verify_extracted_data(_fields(name=good_name))["is_valid"] is True


def test_empty_state_string_is_flagged():
    result = verify_extracted_data(_fields(state="   "))

    assert result["is_valid"] is False
    assert "State was extracted but is empty" in result["issues"]


# ===========================================================================
# "Label was present but unreadable" - needs the raw text
# ===========================================================================

def test_unreadable_income_label_is_reported_as_an_issue():
    text = "INCOME CERTIFICATE\nName: Rahul Sharma\nAnnual Income: Rs. ABCDEF"
    data = extract_fields(text)

    result = verify_extracted_data(data, raw_text=text)

    assert data["annual_income"] is None
    assert result["is_valid"] is False
    assert "Annual income could not be parsed" in result["issues"]


def test_income_never_mentioned_is_missing_not_an_issue():
    text = "CASTE CERTIFICATE\nName: Rahul Sharma\nCaste: OBC"
    data = extract_fields(text)

    result = verify_extracted_data(data, raw_text=text)

    assert result["is_valid"] is True
    assert result["issues"] == []
    assert "annual_income" in result["missing_fields"]


def test_unreadable_name_label_is_reported_as_an_issue():
    text = "INCOME CERTIFICATE\nName: |||###\nDistrict: Jaipur"
    data = extract_fields(text)

    result = verify_extracted_data(data, raw_text=text)

    assert result["is_valid"] is False
    assert "Name could not be read reliably from the document" in result["issues"]


def test_stated_age_missing_is_not_an_issue_when_dob_gives_us_the_age():
    text = "Name: Rahul Sharma\nDate of Birth: 12/05/2002"
    data = extract_fields(text)

    result = verify_extracted_data(data, raw_text=text)

    assert data["age"] is not None
    assert result["is_valid"] is True


def test_verification_of_the_canonical_sample_passes_end_to_end():
    text = (
        "INCOME CERTIFICATE\n\n"
        "Name: Rahul Sharma\n"
        "Date of Birth: 12/05/2002\n"
        "Gender: Male\n"
        "Category: OBC\n"
        "Annual Income: Rs. 1,80,000\n"
        "State: Rajasthan\n"
        "District: Jaipur\n"
    )
    data = extract_fields(text)
    result = verify_extracted_data(data, raw_text=text)

    assert result["is_valid"] is True
    assert result["issues"] == []


def test_qr_vs_ocr_mismatch_flags_issue():
    text = "Name: Rahul Sharma"
    data = extract_fields(text)
    qr_payload = '{"name": "Suresh Kumar"}'
    result = verify_extracted_data(data, raw_text=text, qr_data=[qr_payload])

    assert result["is_valid"] is False
    assert "Name in QR code payload does not match name in document text" in result["issues"]


def test_qr_vs_ocr_match_sets_qr_verified():
    text = "Name: Rahul Sharma"
    data = extract_fields(text)
    qr_payload = '{"name": "Rahul Sharma"}'
    result = verify_extracted_data(data, raw_text=text, qr_data=[qr_payload])

    assert result["is_valid"] is True
    assert result["qr_verified"] is True

