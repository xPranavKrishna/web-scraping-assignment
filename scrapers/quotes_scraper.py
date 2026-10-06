from urllib.parse import urljoin

from .base_scraper import BaseScraper


class QuotesScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://quotes.toscrape.com/", "div.quote")

    def parse_record(self, item, page_url: str):
        quote = item.select_one("span.text")
        author = item.select_one("small.author")
        tags = item.select("a.tag")

        if not quote or not author:
            raise ValueError("missing quote text or author")

        return {
            "source": "Quotes to Scrape",
            "source_url": page_url,
            "name_or_title_raw": quote.get_text(),
            "category_raw": None,
            "price_raw": None,
            "rating_raw": None,
            "author_raw": author.get_text(),
            "tags_raw": [tag.get_text() for tag in tags],
            "description_raw": None,
        }
