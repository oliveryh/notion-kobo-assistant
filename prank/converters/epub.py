from typing import List, Dict, Any
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from bs4 import BeautifulSoup
import html2epub
from pathlib import Path
import subprocess
import os

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

        # if len(self.soup.find_all("h1")) > 1:
        #     level = "h1"
        # else:
        #     level = "h2"


        # def next_element(elem):
        #     while elem is not None:
        #         elem = elem.next_sibling
        #         if hasattr(elem, "name"):
        #             return elem


        # def get_chapters_from_level(level):
        #     chapters = []
        #     htags = self.soup.find_all(level)
        #     for htag in htags:
        #         chapter = [str(htag)]
        #         elem = next_element(htag)
        #         while elem and elem.name != level:
        #             chapter.append(str(elem))
        #             elem = next_element(elem)
        #         chapters.append({"title": htag.text, "content": "\n".join(chapter)})
        #     return chapters

        # level_found = False

        # for level in ["h1", "h2", "h3"]:
        #     chapters = get_chapters_from_level(level)
        #     if len(chapters) > 3:
        #         level_found = True
        #         self.chapters = chapters
        #         break

        # if not level_found:
        #     self.chapters = get_chapters_from_level("h1")

        # if sum([len(chapter["content"]) for chapter in self.chapters]) < 500:
        #     self.chapters = [{
        #         "title": "All",
        #         "content": str(self.soup)
        #     }]

        
        self.chapters = [{
            "title": "All",
            "content": str(self.soup)
        }]

        

        # def get_chapters_from_level(level):
        #     chapters = []
        #     htags = self.soup.find_all(level)
        #     for htag in htags:
        #         chapter = [str(htag)]
        #         elem = next_element(htag)
        #         while elem and elem.name != level:
        #             chapter.append(str(elem))
        #             elem = next_element(elem)
        #         chapters.append({"title": htag.text, "content": "\n".join(chapter)})
        #     return chapters

        # for level in ["h1", "h2", "h3"]:
        #     chapters = get_chapters_from_level(level)
        #     if len(chapters) > 3:
        #         self.chapters = chapters
        #         return

        # self.chapters = get_chapters_from_level("h1")



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
        print("SAVING EPUB")
        self.path_epub = self.epub.create_epub(output_directory=output_dir)

    def _convert_epub_to_kepub(self, book_store: Path):
        print("CONVERTING TO KEPUB", self.path_epub)
        kepub_path = self.path_epub + ".kepub"
        if not os.path.exists(kepub_path):
            subprocess.run(["/home/oliveryh/Documents/repo/notion-kobo-assistant/bin/kepubify-linux-64bit", self.path_epub], cwd=book_store)
            try:
                os.remove(self.path_epub)
            except FileNotFoundError as exc:
                pass
        else:
            print("SKIPPING KEPUB ALREADY CONVERTED")

    def generate_epub(self, book_store: Path):

        if self.url.strip() == "":
            print("Skipping empty URL")
        else:
            self._generate_soup()
            self._generate_chapter_segments()
            self._generate_title()
            self._convert_chapters_to_epub()
            self._save_epub(book_store)
            self._convert_epub_to_kepub(book_store)
