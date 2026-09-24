import os
import pytest
from scheme_detail_scraper import (
    clean_html_text,
    construct_source_url,
    extract_application_mode,
    extract_last_updated,
    extract_official_url,
    extract_section_text,
    parse_scheme_detail,
)


def test_construct_source_url():
    assert construct_source_url("thasp") == "https://www.india.gov.in/my-government/schemes/thasp"
    assert construct_source_url("") == ""


def test_clean_html_text_removes_tags():
    html = "<div><h1>Scheme Title</h1><p>Eligibility Criteria: Must be 18+ years old.</p></div>"
    clean = clean_html_text(html)
    assert "Scheme Title" in clean
    assert "Eligibility Criteria: Must be 18+ years old." in clean


def test_extract_section_text():
    text = "Overview of scheme. Eligibility criteria: Applicants must be permanent residents of Rajasthan. Benefits: Monthly stipend of Rs 5000."
    elig = extract_section_text(text, ["eligibility criteria", "eligibility"])
    assert "Applicants must be permanent residents of Rajasthan." in elig
    ben = extract_section_text(text, ["benefits"])
    assert "Monthly stipend of Rs 5000." in ben


def test_extract_official_url():
    html = '<p>Visit official portal at <a href="https://rajasthan.gov.in/scheme_portal">Official Site</a></p>'
    url = extract_official_url(html, "https://www.india.gov.in/my-government/schemes/test")
    assert url == "https://rajasthan.gov.in/scheme_portal"


def test_extract_last_updated():
    text = "Scheme information. Last Updated: 15/08/2026. Official details."
    date = extract_last_updated(text)
    assert date == "15/08/2026"


def test_extract_application_mode():
    assert extract_application_mode("Submit application online via official portal.") == "Online"
    assert extract_application_mode("Submit physical form at district office in-person.") == "Offline"
    assert extract_application_mode("Apply online or submit form offline at CSC center.") == "Hybrid"


def test_parse_scheme_detail_with_mock_html():
    row = {
        "title": "Test Health Scheme",
        "slug": "test-health",
        "ministry": "Ministry of Health",
        "beneficiaryState": "Rajasthan",
        "description": "Health coverage scheme."
    }
    mock_html = '''
    <html>
      <body>
        <h1>Test Health Scheme</h1>
        <p>Eligibility Criteria: Applicants must be women aged between 18 and 50 years.</p>
        <p>Benefits: Health coverage up to Rs 5,00,000 per family.</p>
        <p>Documents Required: Aadhaar card and Income certificate.</p>
        <p>Last Updated: 20-08-2026</p>
        <a href="https://health.rajasthan.gov.in/apply">Apply Online</a>
      </body>
    </html>
    '''
    enriched = parse_scheme_detail(row, mock_html=mock_html)
    assert enriched["source_url"] == "https://www.india.gov.in/my-government/schemes/test-health"
    assert enriched["official_url"] == "https://health.rajasthan.gov.in/apply"
    assert enriched["last_updated"] == "20-08-2026"
    assert "women aged between 18 and 50 years" in enriched["eligibility_raw"]
    assert "Health coverage up to Rs 5,00,000" in enriched["benefits_raw"]
    assert "Aadhaar card" in enriched["documents_required_raw"]