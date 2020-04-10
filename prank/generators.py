from prank.ptypes import Medium
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from functools import lru_cache
import re
from urllib.parse import urlparse

# Utility Functions
@lru_cache(maxsize=32)
def _get_soup_from_url(url) -> BeautifulSoup:
    headers = {"User-Agent": "Magic Browser"}
    req = Request(url=url, headers=headers)
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, "html.parser")


class TitleGenerator:
    """
    Generates a title from the given URL and medium
    e.g. http://www.myblog.com/thisblog -> "My Blog Name"
    """

    def get_title(self, url, medium):
        generator = self._get_title(medium)
        return generator(url)

    def _get_title(self, medium: Medium):
        return self._title_from_generic

    def _title_from_generic(self, url) -> str:
        soup = _get_soup_from_url(url)
        titles = soup.find_all("title")
        return titles[0].text if titles else None


DOMAINS = {}
DOMAINS[Medium.VIDEO] = ["www.youtube.com"]


class MediumGenerator:
    def get_medium(self, url):
        # Check domain
        url_domain = urlparse(url).netloc
        for medium in DOMAINS.keys():
            if url_domain in DOMAINS[medium]:
                return medium
        return Medium.ARTICLE
