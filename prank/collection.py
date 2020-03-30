from notion.block import HeaderBlock, TextBlock, SubheaderBlock
from notion.collection import Collection
from dataclasses import dataclass
from urllib.request import urlopen
from bs4 import BeautifulSoup
from functools import lru_cache
from prank.converter import Converter
from prank.original import Article


@lru_cache(maxsize=32)
def _get_soup_from_url(url):
    webpage = urlopen(url).read()
    return BeautifulSoup(webpage, "html.parser")


def _get_title_from_url(url) -> str:
    soup = _get_soup_from_url(url)
    titles = soup.find_all("title")
    if titles:
        return titles[0].text
    else:
        return None


def _get_medium_from_url(url) -> str:
    if url.startswith("https://www.youtube.com"):
        return "Video"
    else:
        return "Article"


@dataclass
class NotionCollection:

    collection: Collection

    def enrich_rows(self):
        for row in self.collection.get_rows():
            url = row.url
            if not row.title:
                row.title = _get_title_from_url(url)
            if not row.medium:
                row.medium = _get_medium_from_url(url)

    def save_highlights(self):
        for row in self.collection.get_rows():
            medium = row.medium
            if medium == "Article":
                article = Article(row.title, row.url)
                highlights = article.get_highlights(row.title)
                row.children.add_new(HeaderBlock, title="Highlights")
                for highlight in highlights:
                    if highlight["type"] == "chapter":
                        row.children.add_new(SubheaderBlock, title=highlight["content"])
                    if highlight["type"] == "highlight":
                        row.children.add_new(TextBlock, title=highlight["content"])

    def save_status(self):
        for row in self.collection.get_rows():
            article = Article(row.title, row.url)
            complete = article.is_complete(row.title)
            if complete:
                row.status = "Complete"
            else:
                row.status = "Due"

    def save_timespent(self):
        for row in self.collection.get_rows():
            article = Article(row.title, row.url)
            time_read = article.get_time_read(row.title)
            row.time_read = time_read

    def save_to_epubs(self):
        for row in self.collection.get_rows():
            medium = row.medium
            if medium == "Article":
                url = row.url
                title = row.title
                converted = Converter(url, title)
                converted.generate_epub()
