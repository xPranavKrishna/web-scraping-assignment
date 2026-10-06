from urllib.parse import urljoin

from .base_scraper import BaseScraper


class BooksScraper(BaseScraper):
    def __init__(self):
        super().__init__("https://books.toscrape.com/", "article.product_pod")

    def parse_record(self, item, page_url: str):
        link = item.select_one("h3 > a")
        price = item.select_one("p.price_color")
        rating = item.select_one("p.star-rating")

        if not link:
            raise ValueError("missing book title/link")

        return {
            "source": "Books to Scrape",
            "source_url": urljoin(page_url, link.get("href", "")),
            "name_or_title_raw": link.get("title") or link.get_text(),
            "category_raw": None,
            "price_raw": price.get_text() if price else None,
            "rating_raw": " ".join(rating.get("class", [])) if rating else None,
            "author_raw": None,
            "tags_raw": None,
            "description_raw": None,
        }
