import logging
import time
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

logger = logging.getLogger(__name__)


class BaseScraper:
    def __init__(self, start_url: str, record_selector: str, delay: float = 0.5):
        self.start_url = start_url
        self.record_selector = record_selector
        self.delay = delay
        self.session = self._create_session()

    @staticmethod
    def _create_session() -> requests.Session:
        session = requests.Session()
        session.headers.update({
            "User-Agent": "ScrapingAssignment/1.0 (learning project)"
        })
        retries = Retry(
            total=3,
            backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retries)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        return session

    def fetch_page(self, url: str):
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = "utf-8"
        return response

    def next_url(self, soup, current_url: str):
        next_link = soup.select_one("li.next > a")
        if not next_link or not next_link.get("href"):
            return None
        return urljoin(current_url, next_link["href"])

    def scrape(self):
        from bs4 import BeautifulSoup

        records = []
        url = self.start_url
        page_number = 1

        while url:
            logger.info("Page %d: %s", page_number, url)
            try:
                response = self.fetch_page(url)
            except requests.RequestException as exc:
                logger.error("Failed to fetch %s: %s", url, exc)
                break

            soup = BeautifulSoup(response.text, "lxml")
            for item in soup.select(self.record_selector):
                try:
                    record = self.parse_record(item, url)
                    if record:
                        records.append(record)
                except Exception as exc:
                    logger.warning("Skipped record on %s: %s", url, exc)

            url = self.next_url(soup, url)
            page_number += 1
            if url:
                time.sleep(self.delay)

        return records

    def parse_record(self, item, page_url: str):
        raise NotImplementedError
