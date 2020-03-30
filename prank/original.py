from dataclasses import dataclass

import html2epub
import click
import sqlite3
import pandas as pd
import kobuddy


@dataclass
class Article:

    title: str
    url: str

    def generate_epub(self):

        epub = html2epub.Epub(self.title)
        chapter = html2epub.create_chapter_from_url(
            "https://neilkakkar.com/things-I-learnt-from-a-senior-dev.html"
        )
        epub.add_chapter(chapter)
        epub.create_epub("/tmp")

    def is_complete(self, title) -> bool:

        kobuddy.set_databases("/tmp/kobo_databases/")
        for book in kobuddy.get_books_with_events():
            if title == book.book.title:
                return book.finished
        return False

    def get_time_read(self, title) -> int:

        kobuddy.set_databases("/tmp/kobo_databases/")
        from kobuddy import FinishedEvent

        for book in kobuddy.get_books_with_events():
            if title == book.book.title:
                for event in book.events:
                    if (
                        isinstance(event, FinishedEvent)
                        and event.time_spent_s is not None
                    ):
                        return int(event.time_spent_s // 60)
        return 0

    def get_highlights(self, title) -> str:

        highlights = []

        try:
            cnx = sqlite3.connect("/tmp/kobo_databases/KoboReader.sqlite")
            query = "select Bookmark.ContentID,Bookmark.Text,Bookmark.Hidden,Bookmark.Annotation,Bookmark.ExtraAnnotationData,Bookmark.DateCreated,Bookmark.DateModified,content.BookTitle,content.Title,content.VolumeIndex,ChapterProgress from Bookmark, content WHERE Bookmark.ContentID = content.ContentID;"
            df = pd.read_sql_query(query, cnx)
        except:
            print("Unable to process sqlite file")
            exit(1)

        df = df[df["BookTitle"] == title]
        df = df[df["Hidden"] == "false"]
        df = df[
            [
                "ContentID",
                "BookTitle",
                "ChapterProgress",
                "Text",
                "VolumeIndex",
                "Hidden",
                "Title",
            ]
        ]
        df = df.sort_values(by=["VolumeIndex", "ChapterProgress"])
        df = df.reset_index()

        current_chapter = None
        for i in range(len(df)):
            chapter_title: str = df["Title"][i]
            highlight_text: str = df["Text"][i]

            if current_chapter != chapter_title:
                highlights.append({"type": "chapter", "content": chapter_title})
                current_chapter = chapter_title
            highlights.append({"type": "highlight", "content": highlight_text})

        return highlights


@click.command()
@click.option("--title")
@click.option("--url")
@click.pass_context
def cli(ctx, title, url):
    ctx.obj["ARTICLE"] = Article(title, url)
    highlights = ctx.obj["ARTICLE"].get_highlights(title)
    print(highlights)


if __name__ == "__main__":
    cli(obj={})
