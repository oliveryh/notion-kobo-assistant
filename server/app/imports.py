# %%
import os
import subprocess
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import html2epub
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from notion_client import Client

from app import db
from app.models import Author, Book

load_dotenv()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
BOOK_COLLECTION_ID = os.environ['BOOK_COLLECTION_ID']
BOOK_STORE = os.path.abspath('../store')

notion = Client(auth=NOTION_TOKEN)


# %%
# get data from notion id

database = notion.databases.query(database_id=BOOK_COLLECTION_ID)


# get URLS from database
def get_urls_from_database(database):
    return [row['properties']['URL']['url'] for row in database['results']]


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

    epub = html2epub.Epub(title, creator=domain_name)
    for chapter in chapters:
        chapter_epub = html2epub.create_chapter_from_string(
            chapter["content"], url, chapter["title"]
        )
        epub.add_chapter(chapter_epub)
    return epub


def save_epub_to_file(epub):
    return epub.create_epub(output_directory=BOOK_STORE)


def convert_epub_to_kepub(path_epub):
    kepub_path = path_epub.replace(".epub", ".kepub")
    if not os.path.exists(kepub_path):
        subprocess.run(
            [
                "/home/oliveryh/Documents/repo/notion-kobo-assistant/bin/kepubify-linux-64bit",
                path_epub,
                "--output",
                kepub_path,
            ],
            cwd=BOOK_STORE,
        )
        try:
            os.remove(path_epub)
        except FileNotFoundError:
            pass
        return kepub_path
    else:
        return None


def convert_urls_to_kepubs():
    urls = get_urls_from_database(database)
    for url in urls:
        epub = get_epub_from_url(url)
        print(epub.title)
        epub_path = save_epub_to_file(epub)
        kepub_path = convert_epub_to_kepub(epub_path)
        if kepub_path:
            print(f'✔️ {kepub_path}')
        else:
            print(f'〰️ {epub_path}')
        add_kepub_to_db(epub.creator, epub.title, kepub_path)


def add_kepub_to_db(author_name, title, filename):

    author_exists = db.session.query(Author).filter(Author.name == author_name).first()
    # check if author already exists in db
    if author_exists:
        author_id = author_exists.author_id
        book_exists = author_exists = (
            db.session.query(Book).filter(Book.title == title).first()
        )
        if not book_exists:
            book = Book(author_id=author_id, title=title, filename=filename)
            db.session.add(book)
            db.session.commit()
    else:
        author = Author(name=author_name)
        db.session.add(author)
        db.session.commit()
        book_exists = author_exists = (
            db.session.query(Book).filter(Book.title == title).first()
        )
        if not book_exists:
            book = Book(author_id=author.author_id, title=title, filename=filename)
            db.session.add(book)
            db.session.commit()


# %%
convert_urls_to_kepubs()
