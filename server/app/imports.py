# %%
import binascii
import datetime
import os
import subprocess
from urllib.error import HTTPError
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

# get URLS from database
def get_urls_from_database():
    database = notion.databases.query(database_id=BOOK_COLLECTION_ID)

    return [
        row['properties']['URL']['url']
        for row in database['results']
        if not row['properties']['Date Added']['date']
    ]


def enrich_database(database):
    for row in database['results']:
        try:
            enrich_entry(row)
        except HTTPError:
            pass


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


def save_epub_to_file(epub):
    return epub.create_epub(output_directory=BOOK_STORE)


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


def convert_urls_to_kepubs():
    urls = get_urls_from_database()
    for url in urls:
        try:
            epub = get_epub_from_url(url)
            if epub:
                epub_path = save_epub_to_file(epub)
                kepub_path = convert_epub_to_kepub(epub_path)
                if kepub_path:
                    print(f'✔️ {kepub_path}')
                else:
                    print(f'〰️ {epub_path}')
                add_kepub_to_db(epub.creator, epub.title, kepub_path, url)
            else:
                print(f'❌ Skipping URL: {url}')
        except HTTPError:
            print(f'❌ Skipping URL: {url}')


def enrich_entry(row):

    url = row['properties']['URL']['url']
    id = row['id']

    properties = row['properties']

    title_existing = (
        properties['Name']['title'][0]['plain_text']
        if properties['Name']['title'] != []
        else None
    )
    date_added_existing = (
        properties['Date Added']['date']['start']
        if properties['Date Added']['date']
        else None
    )

    if not title_existing or not date_added_existing:

        headers = {"User-Agent": "Magic Browser"}
        req = Request(url=url, headers=headers)
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, "html.parser")

        try:
            title = soup.title.string
        except AttributeError:
            title = "Unknown Title"

        update_payload = {}

        if not title_existing and title:
            update_payload.update(
                {
                    "Name": {
                        "type": "title",
                        "title": [{"type": "text", "text": {"content": title}}],
                    },
                }
            )

        if not date_added_existing:
            update_payload.update(
                {
                    "Date Added": {
                        "type": "date",
                        "date": {
                            "start": datetime.datetime.strftime(
                                datetime.date.today(), '%Y-%m-%d'
                            ),
                            "end": None,
                            "time_zone": None,
                        },
                    }
                }
            )

        if update_payload:
            notion.pages.update(id, properties=update_payload)


def add_kepub_to_db(author_name, title, filename, url):

    author_exists = db.session.query(Author).filter(Author.name == author_name).first()
    # check if author already exists in db
    if author_exists:
        author_id = author_exists.author_id
        book_exists = author_exists = (
            db.session.query(Book).filter(Book.title == title).first()
        )
        if not book_exists:
            book = Book(
                author_id=author_id,
                title=title,
                filename=filename,
                url=url,
            )
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
            book = Book(
                author_id=author.author_id,
                title=title,
                filename=filename,
                url=url,
            )
            db.session.add(book)
            db.session.commit()


# %%
def refresh():
    convert_urls_to_kepubs()
    database = notion.databases.query(database_id=BOOK_COLLECTION_ID)
    enrich_database(database)
