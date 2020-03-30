from dataclasses import dataclass, field
from typing import List, Dict, Any
from urllib.request import urlopen
from bs4 import BeautifulSoup
import html2epub


@dataclass
class Converter:

    url: str
    title: str = None
    soup: Any = None
    chapters: List[Dict] = field(default_factory=list)

    def _generate_soup(self):

        webpage = urlopen(self.url).read()
        self.soup = BeautifulSoup(webpage, "html.parser")
        self.soup.prettify()

    def _generate_chapter_segments(self):

        h2tags = self.soup.find_all("h2")

        def next_element(elem):
            while elem is not None:
                elem = elem.next_sibling
                if hasattr(elem, "name"):
                    return elem

        for h2tag in h2tags:
            chapter = [str(h2tag)]
            elem = next_element(h2tag)
            while elem and elem.name != "h2":
                chapter.append(str(elem))
                elem = next_element(elem)
            self.chapters.append({"title": h2tag.text, "content": "\n".join(chapter)})

    def _generate_title(self):

        try:
            self.title = self.soup.find_all("title")[0].text
        except:
            self.title = ""

    def _convert_chapters_to_epub(self, output_dir):

        epub = html2epub.Epub(self.title)
        for chapter in self.chapters:
            chapter_epub = html2epub.create_chapter_from_string(
                chapter["content"], self.url, chapter["title"]
            )
            epub.add_chapter(chapter_epub)
        epub.create_epub(output_directory=output_dir)

    def generate_epub(self):

        self._generate_soup()
        self._generate_chapter_segments()
        self._generate_title()
        self._convert_chapters_to_epub("/media/oliveryh/KOBOeReader/PRANK")
