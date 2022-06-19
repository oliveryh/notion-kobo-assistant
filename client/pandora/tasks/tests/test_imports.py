import os
import tempfile
import zipfile

import html2epub
from bs4 import BeautifulSoup


class TestEpubGeneration:
    def test_epub_contains_stylesheet(self):

        title = "Webpage Title"
        domain_name = "website.com"
        url = "https://www.website.com/blog/entry"
        soup = BeautifulSoup(
            """
            <html>
                <head>
                </head>
                <body>
                    <h1>Title</h1>
                </body>
            </html>
            """
        )
        chapters = [{"title": "All", "content": str(soup)}]

        epub = html2epub.Epub(title, creator=domain_name)
        for chapter in chapters:
            chapter_epub = html2epub.create_chapter_from_string(
                chapter["content"], url, chapter["title"]
            )
            epub.add_chapter(chapter_epub)

        tempdir = tempfile.mkdtemp()
        epub.create_epub(output_directory=tempdir)

        zip_file = os.path.join(tempdir, "Webpage Title.epub")
        with zipfile.ZipFile(zip_file, "r") as zip_ref:
            assert "OEBPS/styles/stylesheet.css" in zip_ref.namelist()
