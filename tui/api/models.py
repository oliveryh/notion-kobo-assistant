import datetime

from urllib.request import urlopen, Request

from bs4 import BeautifulSoup
from markdownify import markdownify
from peewee import *
from readabilipy import simple_json_from_html_string

from tui.exceptions import ValidationError

DATABASE = 'pandora.db'

database = SqliteDatabase(DATABASE)

class BaseModel(Model):

    class Meta:
        database = database

class Article(BaseModel):

    url = CharField()
    title = CharField()
    author = CharField(null=True)
    html = TextField()
    markdown = TextField()
    time_secs = IntegerField(default=0)
    created_at = DateTimeField(default=datetime.datetime.now)
    completed_at = DateTimeField(null=True)


class Highlight(BaseModel):

    article = ForeignKeyField(Article, backref='highlights')
    segment = IntegerField()


def _get_soup_from_url(url) -> BeautifulSoup:
    headers = {"User-Agent": "Magic Browser"}
    req = Request(url=url, headers=headers)
    webpage = urlopen(req).read()
    return BeautifulSoup(webpage, "html.parser")

def add_article(url: str):
    try:
        soup = _get_soup_from_url(url)
    except ValueError as exc:
        raise ValidationError(field='url', message='That URL couldn\'t be processed') from exc
    html = str(soup)
    readable_json = simple_json_from_html_string(html, use_readability=True)
    html_simplified = readable_json['content']
    title = readable_json['title']
    author = readable_json['byline']
    markdown = markdownify(html_simplified)

    Article.create(
        url=url,
        title=title,
        author=author,
        html=html_simplified,
        markdown=markdown,
    )

def create_tables():
    with database:
        database.create_tables([Article, Highlight])