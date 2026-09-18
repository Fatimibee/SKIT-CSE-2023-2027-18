import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from html import unescape
from html.parser import HTMLParser

try:
    from bs4 import BeautifulSoup
    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False

DEFAULT_INPUT_CSV = "government_schemes.csv"
DEFAULT_OUTPUT_CSV = "government_schemes_detailed_raw.csv"
CACHE_DIR = ".cache_html"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) YojanaSahayakDataCollector/1.0"
MAX_RETRIES = 3
DEFAULT_DELAY_SEC = 0.5

BASE_SCHEME_URL = "https://www.india.gov.in/my-government/schemes/"


class SimpleTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.fed = []
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "head", "title", "meta", "[document]"):
            self.ignore = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "head", "title", "meta", "[document]"):
            self.ignore = False

    def handle_data(self, d):
        if not self.ignore and d.strip():
            self.fed.append(d.strip())

    def get_data(self):
        return " ".join(self.fed)


def clean_html_text(html_content):
    if not html_content:
        return ""
    if HAS_BS4:
        soup = BeautifulSoup(html_content, "html.parser")
        for script in soup(["script", "style", "head"]):
            script.decompose()
        text = soup.get_text(separator=" ")
    else:
        parser = SimpleTextExtractor()
        try:
            parser.feed(html_content)
            text = parser.get_data()
        except Exception:
            text = re.sub(r"<[^>]+>", " ", html_content)

    text = unescape(text)
    return re.sub(r"\s+", " ", text).strip()


def get_cache_path(identifier):
    os.makedirs(CACHE_DIR, exist_ok=True)
    safe_name = re.sub(r"[^a-zA-Z0-9_\-]", "_", str(identifier))
    return os.path.join(CACHE_DIR, f"{safe_name}.html")


def fetch_url(url, delay=DEFAULT_DELAY_SEC, cache_key=None):
    if cache_key:
        cache_file = get_cache_path(cache_key)
        if os.path.exists(cache_file):
            with open(cache_file, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

    headers = {"User-Agent": USER_AGENT}
    req = urllib.request.Request(url, headers=headers)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            time.sleep(delay)
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read().decode("utf-8", errors="ignore")
                if cache_key:
                    cache_file = get_cache_path(cache_key)
                    with open(cache_file, "w", encoding="utf-8") as f:
                        f.write(content)
                return content
        except Exception:
            if attempt == MAX_RETRIES:
                return ""
            time.sleep(delay * (2 ** attempt))

    return ""


def construct_source_url(slug):
    if not slug or str(slug).strip() in ("", "nan", "none"):
        return ""
    slug_str = str(slug).strip().lower()
    return f"{BASE_SCHEME_URL}{slug_str}"


def extract_section_text(html_text, header_keywords):
    if not html_text:
        return ""

    for kw in header_keywords:
        pattern = r"(?i)\b" + re.escape(kw) + r"\b[\:\s\-\–\—]*([^.\n]{10,500}\.)"
        match = re.search(pattern, html_text)
        if match:
            return match.group(1).strip()

    return ""


def extract_official_url(html_content, source_url):
    if not html_content:
        return ""

    urls = re.findall(r'href=["\'](https?://[^\s"\'>]+)["\']', html_content, re.IGNORECASE)
    for u in urls:
        u_lower = u.lower()
        if "india.gov.in" not in u_lower and ("gov.in" in u_lower or "nic.in" in u_lower or "apply" in u_lower):
            return u.strip()

    return ""


def extract_last_updated(html_text):
    if not html_text:
        return ""

    match = re.search(r"(?i)(?:last\s+updated|updated\s+on|date)\s*[:\-]?\s*(\d{1,2}[\/\-\s]+[A-Za-z0-9]+[\/\-\s]+\d{2,4})", html_text)
    if match:
        return match.group(1).strip()

    return ""


def extract_application_mode(html_text):
    if not html_text:
        return ""

    has_online = bool(re.search(r"(?i)\b(online|portal|website|digital|apply online)\b", html_text))
    has_offline = bool(re.search(r"(?i)\b(offline|in-person|physical form|post|office|csc|center)\b", html_text))

    if has_online and has_offline:
        return "Hybrid"
    elif has_online:
        return "Online"
    elif has_offline:
        return "Offline"

    return ""


def parse_scheme_detail(row, delay=DEFAULT_DELAY_SEC, mock_html=None):
    slug = row.get("slug", "")
    title = row.get("title", "")
    description = row.get("description", "")
    source_url = construct_source_url(slug)

    if mock_html is not None:
        html_content = mock_html
    elif source_url:
        html_content = fetch_url(source_url, delay=delay, cache_key=slug or title)
    else:
        html_content = ""

    text = clean_html_text(html_content) if html_content else ""
    full_context = f"{text} {description}".strip()

    eligibility_text = extract_section_text(full_context, ["eligibility criteria", "eligibility", "who can apply", "eligible beneficiaries"])
    benefits_text = extract_section_text(full_context, ["benefits", "scheme benefits", "financial assistance", "subsidy", "incentive"])
    documents_text = extract_section_text(full_context, ["documents required", "documents", "required documents", "enclosures"])
    app_process_text = extract_section_text(full_context, ["how to apply", "application process", "procedure", "application procedure"])
    app_mode = extract_application_mode(full_context)

    official_url = extract_official_url(html_content, source_url)
    last_updated = extract_last_updated(text)

    enriched_row = dict(row)
    enriched_row["source_url"] = source_url
    enriched_row["official_url"] = official_url
    enriched_row["last_updated"] = last_updated
    enriched_row["eligibility_raw"] = eligibility_text or (description if not eligibility_text else "")
    enriched_row["eligibility"] = eligibility_text
    enriched_row["benefits_raw"] = benefits_text
    enriched_row["benefits"] = benefits_text
    enriched_row["documents_required_raw"] = documents_text
    enriched_row["documents_required"] = documents_text
    enriched_row["application_process"] = app_process_text
    enriched_row["application_mode"] = app_mode
    enriched_row["beneficiaries_raw"] = ""
    enriched_row["beneficiaries"] = ""
    enriched_row["state"] = row.get("beneficiaryState", "")
    enriched_row["department"] = row.get("ministry", "")

    return enriched_row


def run_scraper(input_csv=DEFAULT_INPUT_CSV, output_csv=DEFAULT_OUTPUT_CSV, sample=None, delay=DEFAULT_DELAY_SEC):
    if not os.path.exists(input_csv):
        print(f"Error: Input file '{input_csv}' not found.")
        sys.exit(1)

    print(f"Reading input CSV: {input_csv}")
    with open(input_csv, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        records = list(reader)

    if sample:
        records = records[:sample]
        print(f"Running scraper in SAMPLE mode on first {sample} records...")
    else:
        print(f"Running scraper on all {len(records)} records...")

    extra_fields = [
        "eligibility", "beneficiaries", "benefits", "documents_required",
        "application_process", "application_mode", "state", "department",
        "eligibility_raw", "beneficiaries_raw", "benefits_raw", "documents_required_raw",
        "source_url", "official_url", "last_updated"
    ]

    out_fieldnames = list(fieldnames)
    for ef in extra_fields:
        if ef not in out_fieldnames:
            out_fieldnames.append(ef)

    enriched_records = []
    success_count = 0

    for idx, row in enumerate(records, 1):
        print(f"[{idx}/{len(records)}] Processing: {row.get('title', 'Untitled')[:50]}...", end="\r")
        enriched = parse_scheme_detail(row, delay=delay)
        enriched_records.append(enriched)
        if enriched.get("source_url") or enriched.get("eligibility_raw"):
            success_count += 1

    print("\nWriting output CSV...")
    with open(output_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fieldnames)
        writer.writeheader()
        writer.writerows(enriched_records)

    print("=" * 60)
    print("Detail Scraper Execution Completed!")
    print(f"Input records     : {len(records)}")
    print(f"Output records    : {len(enriched_records)}")
    print(f"Enriched items    : {success_count}")
    print(f"Output saved to   : {output_csv}")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Detail page scraper for Yojana Sahayak scheme dataset.")
    parser.add_argument("-i", "--input", default=DEFAULT_INPUT_CSV, help="Input listing CSV file")
    parser.add_argument("-o", "--output", default=DEFAULT_OUTPUT_CSV, help="Output detailed raw CSV file")
    parser.add_argument("-s", "--sample", type=int, default=None, help="Process only first N records")
    parser.add_argument("-d", "--delay", type=float, default=DEFAULT_DELAY_SEC, help="Delay between HTTP requests in seconds")

    args = parser.parse_args()
    run_scraper(input_csv=args.input, output_csv=args.output, sample=args.sample, delay=args.delay)


if __name__ == "__main__":
    main()
