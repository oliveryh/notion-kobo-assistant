# %%
import binascii
import os
import subprocess
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import html2epub
from bs4 import BeautifulSoup

BOOK_STORE = os.path.abspath('../store')


def get_soup(url):
    headers = {"User-Agent": "Magic Browser"}
    req = Request(url=url, headers=headers)
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, "html.parser")


def get_article_from_url(url):
    soup = get_soup(url)
    domain_name = urlparse(url).netloc
    filename = convert_url_to_keypub(url)
    return {
        'name': soup.title.string,
        'author': domain_name,
        'filename': filename,
    }


def get_epub_from_url(url):
    headers = {"User-Agent": "Magic Browser"}
    req = Request(url=url, headers=headers)
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "html.parser")
    chapters = [{"title": "All", "content": str(soup)}]
    domain_name = urlparse(url).netloc

    try:
        title = soup.title.string
    except AttributeError:
        title = "Unknown Title"

    try:
        epub = html2epub.Epub(title, creator=domain_name)
        for chapter in chapters:
            chapter_epub = html2epub.create_chapter_from_string(
                chapter["content"], url, chapter["title"]
            )
            epub.add_chapter(chapter_epub)
    except AttributeError:
        return None
    except binascii.Error:
        return None
    return epub


def convert_epub_to_kepub(path_epub):
    kepub_path = path_epub.replace(".epub", ".kepub.epub")
    if not os.path.exists(kepub_path):
        result = subprocess.run(
            [
                "kepubify-linux-64bit",
                path_epub,
                "--output",
                kepub_path,
            ],
            cwd=BOOK_STORE,
        )
        if result.returncode != 0:
            return None
        try:
            os.remove(path_epub)
        except FileNotFoundError:
            pass
    kepub_filename = os.path.basename(kepub_path)
    return kepub_filename


def save_epub_to_file(epub):
    return epub.create_epub(output_directory=BOOK_STORE)


def convert_url_to_keypub(url):
    try:
        epub = get_epub_from_url(url)
        if epub:
            epub_path = save_epub_to_file(epub)
            kepub_path = convert_epub_to_kepub(epub_path)
            if kepub_path:
                print(f'✔️ {kepub_path}')
            else:
                print(f'〰️ {epub_path}')
            return kepub_path
        else:
            print(f'❌ Skipping URL: {url}')
    except HTTPError:
        print(f'❌ Skipping URL: {url}')
