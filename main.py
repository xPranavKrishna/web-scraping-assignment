import csv
import json
import logging
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from processing.cleaning import clean_record
from processing.deduplication import find_duplicates
from processing.validation import validate_record
from scrapers.books_scraper import BooksScraper
from scrapers.quotes_scraper import QuotesScraper

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "scraper.log"
CSV_FILE = OUTPUT_DIR / "final_dataset.csv"
SUMMARY_FILE = OUTPUT_DIR / "summary_report.json"

COLUMNS = [
    "source", "source_url", "name_or_title", "category", "price", "rating",
    "author", "tags", "description", "scraped_at"
]


def setup_logging():
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


def scrape_source(scraper, source_name):
    try:
        return scraper.scrape()
    except Exception as exc:
        logging.error("Source %s failed: %s", source_name, exc)
        return []


def add_scraped_at(records, timestamp):
    for record in records:
        record["scraped_at"] = timestamp


def write_csv(records):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with CSV_FILE.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(records)


def write_summary(stats):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with SUMMARY_FILE.open("w", encoding="utf-8") as handle:
        json.dump(stats, handle, indent=4)


def process_source(raw_records, source_name, scraped_at, stats):
    stats["collected_per_source"][source_name] = len(raw_records)
    cleaned_records = []
    rejected = Counter()

    for raw in raw_records:
        record = clean_record(raw)
        record["scraped_at"] = scraped_at
        problems = validate_record(record)
        if problems:
            for problem in problems:
                rejected[problem] += 1
            logging.warning(
                "Rejected %s record: %s",
                source_name,
                ", ".join(problems),
            )
            continue
        cleaned_records.append(record)

    stats["cleaned_per_source"][source_name] = len(cleaned_records)
    stats["rejected_by_source"][source_name] = dict(rejected)
    return cleaned_records


def main():
    setup_logging()
    start = time.perf_counter()
    start_time = datetime.now(timezone.utc)
    scraped_at = start_time.isoformat()

    stats = {
        "collected_per_source": {},
        "cleaned_per_source": {},
        "rejected_by_source": {},
        "duplicates_detected": 0,
        "final_record_count": 0,
        "start_time": scraped_at,
        "end_time": None,
        "duration_seconds": None,
    }

    logging.info("Starting scraping assignment")

    books_raw = scrape_source(BooksScraper(), "Books to Scrape")
    quotes_raw = scrape_source(QuotesScraper(), "Quotes to Scrape")

    books = process_source(books_raw, "Books to Scrape", scraped_at, stats)
    quotes = process_source(quotes_raw, "Quotes to Scrape", scraped_at, stats)

    all_cleaned = books + quotes
    unique_records, duplicate_records = find_duplicates(all_cleaned)
    stats["duplicates_detected"] = len(duplicate_records)

    write_csv(unique_records)

    end_time = datetime.now(timezone.utc)
    stats["end_time"] = end_time.isoformat()
    stats["duration_seconds"] = round(time.perf_counter() - start, 3)
    stats["final_record_count"] = len(unique_records)
    write_summary(stats)

    logging.info("Duplicates detected: %d", len(duplicate_records))
    logging.info("Final record count: %d", len(unique_records))
    logging.info("Finished in %.3f seconds", stats["duration_seconds"])


if __name__ == "__main__":
    main()
