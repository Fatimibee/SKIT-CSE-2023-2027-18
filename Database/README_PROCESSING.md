# Scheme Data Processing Layer

Add this section to the project README.

---

## Data pipeline

India.gov.in is the **primary source** for scheme data. PIB RSS is not used
yet; when it is added it will act as an update/news signal that points back
to an India.gov.in record, never as a second source of schemes.

```
India.gov.in scraper            (existing - unchanged)
        |
        v
government_schemes.csv          raw scraped output, 9 columns
        |
        v
schemes_processing.py           normalize -> deduplicate -> extract
        |
        v
government_schemes_processed.csv   33 columns
        |
        v
future RAG / recommendation engine
```

`schemes_processing.py` does not touch the scraper. It reads the CSV the
scraper already produces, so scraping keeps working exactly as before.

## How to run

```bash
# full dataset
python schemes_processing.py government_schemes.csv

# with a quality report
python schemes_processing.py government_schemes.csv -r quality_report.json

# quick check on the first 50 rows
python schemes_processing.py government_schemes.csv --sample 50 -o sample.csv
```

Output defaults to `<input>_processed.csv`. The step is **reproducible** —
running it twice on the same input gives byte-identical output, so the
processed dataset never needs editing by hand.

## How to run the tests

```bash
python -m pytest test_schemes_processing.py -v
```

## Schema

### Existing columns — unchanged

`title`, `ministry`, `schemeCategory`, `description`, `beneficiaryState`,
`npiMinistry`, `slug`, `tags`, `__typename`

All nine are preserved with their original names and values, so anything
that reads the CSV today keeps working. Normalized values go into **new**
columns rather than overwriting these.

### Normalized (new)

| Column | Notes |
|---|---|
| `categories_normalized` | JSON array. Trimmed, de-duplicated, canonical casing |
| `tags_normalized` | JSON array. Same, plus literal `None` entries removed |

### Content (new — populated once the scraper reads detail pages)

`eligibility`, `beneficiaries`, `benefits`, `documents_required`,
`application_process`, `application_mode`, `state`, `department`

**These are empty today.** The current scraper reads an India.gov.in
*search* endpoint — every row carries `__typename: "Search"` — and that
response does not contain these sections. They live on each scheme's detail
page, which needs a separate request per scheme keyed on `slug`. The columns
exist now so the layout does not change again when that is added.

### Raw source text (new)

`eligibility_raw`, `beneficiaries_raw`, `benefits_raw`,
`documents_required_raw`

The source wording is kept next to the cleaned value, so extraction logic
can be improved and re-run later without re-scraping. Also empty until
detail-page scraping lands.

### Structured eligibility (new — derived)

| Column | Extracted from |
|---|---|
| `age_min` | "between 18 and 60 years", "above 18 years", "at least 21 years" |
| `age_max` | "below 40 years", "up to 18 years of age", "not exceeding 35 years" |
| `gender` | `Female` / `Male`. Empty when both are mentioned |
| `income_max` | "not exceed Rs. 2,50,000", "below ₹8,00,000", "up to 2.5 lakh" |
| `category` | `SC`, `ST`, `OBC`, `EWS`, `BPL`, `Minority`, `PwD`, `General` |
| `occupation` | `Farmer`, `Student`, `Artisan`, `Weaver`, `Labourer`, ... |
| `eligibility_state` | Matched against the 36 states and UTs |

### Provenance (new)

`source_url`, `official_url`, `last_updated`

**Deliberately empty.** Building an India.gov.in URL out of the slug would
be fabrication. These stay empty until the scraper records the page it
actually fetched.

## Normalization

Two values are merged **only** when they differ purely by casing or
whitespace. When several spellings exist, the one appearing most often in
the dataset wins; ties prefer non-ALL-CAPS, then alphabetical order — so the
choice comes from the data and is reproducible.

Values are never merged for merely looking similar. "Skills & Employment"
and "Education & Learning" stay separate because they mean different things.

Measured on the current dataset: categories were already clean (15 distinct,
no collisions); tags had **28 case-only collision groups** — `PWD`/`PwD`,
`SCHOLARSHIP`/`Scholarship`, `Startup`/`StartUp` — plus 3 rows containing a
literal `None`.

## Deduplication

Identity is taken from the most reliable key available:

1. `source_url` — the exact page the record came from
2. `official_url`
3. `slug` + normalized `title` together
4. normalized `title` alone

Title alone is not used as the primary key, and neither is slug: in this
dataset there are **91 slug collisions and 77 title collisions** across
3,680 records, so slug is actually *less* unique than title. Requiring both
to match avoids collapsing two genuinely different schemes.

When duplicates carry complementary information they are merged field by
field — an existing value is never overwritten, only empty fields are
filled, so no information is lost.

## Results on the current dataset

| | |
|---|---|
| Records in | 3,680 |
| Duplicates removed | 81 |
| Unique schemes out | 3,599 |
| Columns | 9 → 33 |
| Records with any structured eligibility | 2,953 |
| Validation issues | 0 |

Structured eligibility field coverage:

| Field | Records |
|---|---|
| `eligibility_state` | 1,875 |
| `occupation` | 1,589 |
| `category` | 658 |
| `gender` | 474 |
| `age_min` | 87 |
| `age_max` | 41 |
| `income_max` | 32 |

## Validation

`validate()` checks that all nine original columns survive, every record has
a title, ages fall within 0–120, `income_max` is non-negative and plausible,
and any URL present starts with `http://` or `https://`. The quality report
adds per-field populated/empty counts and deduplication statistics.

## Limitations

- **Eligibility currently comes from `description`, not a real eligibility
  section.** The description is a summary, so coverage is thin — only 32
  records state an income limit and 87 an age. This is a fallback; once
  detail-page scraping lands, `eligibility_raw` becomes the source and
  coverage should rise sharply. The fallback is documented in code and can
  be switched off by passing no `fallback_text`.
- `ministry` is null in 84% of records (3,094 of 3,680) at source.
- `beneficiaryState` is null in **100%** of records and `npiMinistry` is `[]`
  in all of them — both columns are kept for compatibility but carry no data.
- `__typename` is `"Search"` in every row. It is a GraphQL artifact, not
  scheme data, and is retained only for backward compatibility.
- Extraction is regex-based, so unusual phrasing is missed. That is the
  intended trade-off: every rule is traceable and explainable, and it fails
  by returning nothing rather than by guessing.
