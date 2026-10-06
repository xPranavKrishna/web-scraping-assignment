VALID_SOURCES = {"Books to Scrape", "Quotes to Scrape"}


def validate_record(record):
    problems = []
    if record.get("source") not in VALID_SOURCES:
        problems.append("unknown_source")
    if not record.get("name_or_title"):
        problems.append("missing_name")
    if not str(record.get("source_url") or "").startswith(("http://", "https://")):
        problems.append("invalid_url")

    price = record.get("price")
    if price is not None and (not isinstance(price, (int, float)) or price < 0):
        problems.append("invalid_price")

    rating = record.get("rating")
    if rating is not None and (not isinstance(rating, int) or rating not in (1, 2, 3, 4, 5)):
        problems.append("invalid_rating")

    return problems
