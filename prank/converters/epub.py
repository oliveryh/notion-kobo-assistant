from typing import List, Dict, Any
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import html2epub
from pathlib import Path

class EpubConverter:

    def __init__(self, url):
        self.url: str = url
        self.title: str = None
        self.soup: Any = None
        self.chapters: List[Dict] = []
        self.epub: html2epub.Epub = None

    def _generate_soup(self):

        headers = {"User-Agent": "Magic Browser"}
        req = Request(url=self.url, headers=headers)
        webpage = urlopen(req).read()
        self.soup = BeautifulSoup(webpage, "html.parser")
        self.soup.prettify()

    def _generate_chapter_segments(self):

        if len(self.soup.find_all("h1")) > 1:
            level = "h1"
        else:
            level = "h2"
        htags = self.soup.find_all(level)

        def next_element(elem):
            while elem is not None:
                elem = elem.next_sibling
                if hasattr(elem, "name"):
                    return elem

        for htag in htags:
            chapter = [str(htag)]
            elem = next_element(htag)
            while elem and elem.name != level:
                chapter.append(str(elem))
                elem = next_element(elem)
            self.chapters.append({"title": htag.text, "content": "\n".join(chapter)})

    def _generate_title(self):

        try:
            self.title = self.soup.title.string
        except:
            self.title = "Unknown Title"

    def _convert_chapters_to_epub(self):

        domain_name = urlparse(self.url).netloc

        epub = html2epub.Epub(
            self.title,
            creator=domain_name
        )
        for chapter in self.chapters:
            chapter_epub = html2epub.create_chapter_from_string(
                chapter["content"], self.url, chapter["title"]
            )
            epub.add_chapter(chapter_epub)
        self.epub = epub

    def _save_epub(self, output_dir):
        self.epub.create_epub(output_directory=output_dir)

    def generate_epub(self, book_store: Path):

        if self.url.strip() == "":
            print("Skipping empty URL")
        else:
            self._generate_soup()
            self._generate_chapter_segments()
            self._generate_title()
            self._convert_chapters_to_epub()
            self._save_epub(book_store)
