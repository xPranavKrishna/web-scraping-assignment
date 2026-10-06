# Multi-Source Web Scraping & Data Consolidation

## Overview

This project scrapes the two practice websites required by the assignment:

- Books to Scrape: https://books.toscrape.com/
- Quotes to Scrape: https://quotes.toscrape.com/

The pipeline follows this flow:

**Scrape -> Clean -> Validate -> Deduplicate -> Consolidate -> Save**

The only command needed for a full run is:

```bash
python main.py
```

## Python version

Python 3.10, 3.11, or 3.12.

## Project structure

```text
scraping_assignment/
├── scrapers/
│   ├── __init__.py
│   ├── base_scraper.py
│   ├── books_scraper.py
│   └── quotes_scraper.py
├── processing/
│   ├── __init__.py
│   ├── cleaning.py
│   ├── validation.py
│   └── deduplication.py
├── tests/
│   ├── __init__.py
│   ├── test_cleaning.py
│   ├── test_validation.py
│   └── test_deduplication.py
├── output/
├── logs/
├── main.py
├── requirements.txt
├── README.md
└── AI_USAGE.md
```

## Setup

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The program creates:

- `output/final_dataset.csv`
- `output/summary_report.json`
- `logs/scraper.log`

## Source exploration

### Books to Scrape

- Record: `article.product_pod`
- Title/link: `h3 > a`
- Price: `p.price_color`
- Rating: class on `p.star-rating`
- Next page: `li.next > a`

### Quotes to Scrape

- Record: `div.quote`
- Quote: `span.text`
- Author: `small.author`
- Tags: `a.tag`
- Next page: `li.next > a`

The scraper follows the next-page link until there is no next link. Page numbers are not hard-coded.

## Data model

| Column | Books to Scrape | Quotes to Scrape |
|---|---|---|
| `source` | Books to Scrape | Quotes to Scrape |
| `source_url` | Book detail URL | Page URL where quote appeared |
| `name_or_title` | Book title | Quote text |
| `category` | Empty | Empty |
| `price` | Numeric price | Empty |
| `rating` | Integer 1-5 | Empty |
| `author` | Empty | Author name |
| `tags` | Empty | Lowercase sorted tags joined with `;` |
| `description` | Empty | Empty |
| `scraped_at` | UTC timestamp | UTC timestamp |

Category and description are left empty for books because the listing pages do not provide them. Fetching every book detail page would add roughly 1,000 extra requests and is not necessary for the required common dataset. No values are guessed.

## Cleaning

- Extra whitespace, tabs, newlines, and non-breaking spaces are collapsed.
- Curly quotation marks around quote text are removed.
- Prices such as `£51.77` become numeric `51.77`.
- Rating words such as `Three` become integers.
- Tags are lowercased, sorted, de-duplicated, and joined with `;`.
- URLs are normalized and checked for an HTTP/HTTPS scheme.

Cleaning is kept separate from scraping.

## Validation

A record is rejected when:

- its source is unknown;
- its main name/title is missing;
- its URL is not HTTP/HTTPS;
- its price is invalid or negative when present;
- its rating is outside 1-5 when present.

Rejected records are counted by reason and written to the summary report. They are also logged as warnings.

## Deduplication

Duplicates are removed before writing the final CSV.

For books, the fingerprint uses source + title.

For quotes, it uses source + author + the first 50 characters of the quote.

The fingerprint lowercases text, removes punctuation, collapses whitespace, and hashes the normalized value with SHA-256. This means differences such as capitalization and extra spaces do not create separate records.

The test suite also includes deliberate duplicate samples.

## Error handling

Requests use a shared `requests.Session` with a User-Agent, timeout, and retries for HTTP 429, 500, 502, 503, and 504 responses. There is a 0.5 second pause between pages.

A failed page is logged as an error and stops that source only. The other source is still processed. Missing individual fields and individual record parsing errors do not stop the full run.

## Outputs

`final_dataset.csv` contains the final unique valid records from both sources.

`summary_report.json` contains:

- records collected per source;
- records after cleaning per source;
- rejected records by reason and source;
- duplicate count;
- final record count;
- start time;
- end time;
- duration in seconds.

`logs/scraper.log` contains timestamped page requests, warnings, errors, and run information.

## Testing

Run the tests with:

```bash
pytest -q
```

The tests cover cleaning, validation, and duplicate detection and do not require internet access.

## Assumptions and limitations

- Only the two practice websites specified in the assignment are scraped.
- The program relies on the current HTML structure of those practice sites.
- Book category and description are not fetched from detail pages; they remain empty rather than being guessed.
- Quote `source_url` is the page where the quote was found.
- Real source data is expected to contain unique records, so duplicate tests use deliberate sample duplicates.

## AI usage

See `AI_USAGE.md` for the required record of AI assistance and verification.
