from processing.validation import validate_record


def test_valid_record():
    record = {
        "source": "Books to Scrape",
        "source_url": "https://books.toscrape.com/catalogue/test_1/index.html",
        "name_or_title": "Test Book",
        "price": 10.5,
        "rating": 4,
    }
    assert validate_record(record) == []


def test_invalid_record():
    record = {
        "source": "Unknown",
        "source_url": "bad-url",
        "name_or_title": "",
        "price": -1,
        "rating": 6,
    }
    assert set(validate_record(record)) == {
        "unknown_source", "missing_name", "invalid_url", "invalid_price", "invalid_rating"
    }
