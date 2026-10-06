# AI Usage

## Tool used

**ChatGPT**

## What it was used for

ChatGPT was used to help with:

- planning the project structure;
- drafting the Requests + BeautifulSoup scraper structure;
- implementing cleaning, validation, and duplicate-detection functions;
- writing unit tests;
- drafting the README and checking the assignment requirements;
- reviewing the final pipeline for missing required steps.

## Representative prompts

1. "Read the placement assignment and build the complete Python project according to the requirements, without adding unnecessary features."
2. "Implement separate Books to Scrape and Quotes to Scrape scrapers with dynamic next-link pagination, shared requests handling, cleaning, validation, deduplication, logging, and output files."
3. "Review the project against the assignment and add only the required tests and documentation."

## AI-assisted parts

The initial implementation of the scraper modules, processing modules, main pipeline, tests, and documentation was AI-assisted.

## Changes and verification after AI output

The implementation was kept intentionally simple and aligned with the assignment rather than adding optional features such as databases, asynchronous scraping, Docker, or CLI options.

The book scraper does not make unnecessary detail-page requests for category and description. Those fields are left empty and the limitation is documented in the README, as allowed by the assignment.

The duplicate logic was checked against the required rule: books use source + title, while quotes use source + author + the first 50 characters of the quote text, after normalization.

## Testing

The final code includes offline pytest tests for:

- whitespace and text cleaning;
- quote stripping;
- price conversion;
- rating conversion;
- tag normalization;
- valid and invalid record validation;
- duplicate detection with differences in case and whitespace.

The complete scraper was also run against both public practice sites to generate the submitted CSV, summary report, and log.
