import os
import sqlite3
from typing import List, Optional

import kobuddy
from kobuddy import FinishedEvent
import pandas as pd

class Article:

    def __init__(self, book, highlights):
        self.book = book
        self.highlights = highlights

    def is_finished(self) -> bool:
        return self.book.finished

    def get_time_spent(self) -> int:
        for event in self.book.events:
            if (
                isinstance(event, FinishedEvent)
                and event.time_spent_s is not None
            ):
                return int(event.time_spent_s // 60)
        return 0

    def get_title(self) -> str:
        return self.book.book.title

    def get_highlights(self):
        return self.highlights



class Library:

    def __init__(self, db):
        self.db = db
        self.connection = kobuddy.set_databases(db)
        self.articles: List[Article] = []
        self.highlight_df = None

    def _load_highlight_df(self):

        try:
            cnx = sqlite3.connect(os.path.join(self.db, "KoboReader.sqlite"))
            query = "select Bookmark.ContentID,Bookmark.Text,Bookmark.Hidden,Bookmark.Annotation,Bookmark.ExtraAnnotationData,Bookmark.DateCreated,Bookmark.DateModified,content.BookTitle,content.Title,content.VolumeIndex,ChapterProgress from Bookmark, content WHERE Bookmark.ContentID = content.ContentID;"
            df = pd.read_sql_query(query, cnx)
        except:
            print("Unable to process sqlite file")
            exit(1)

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
        self.highlight_df = df.copy()

    def _get_book_highlights(self, title: str) -> dict:

        highlights = []

        df = self.highlight_df.copy()
        df = df[df["BookTitle"] == title]
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

    def load_articles(self):
        """
        Load the library with Article instances that contain
        titles, reading events, and highlights
        """
        self._load_highlight_df()

        for book in kobuddy.get_books_with_events():
            book_highlights = self._get_book_highlights(book.book.title)
            self.articles.append(Article(book, book_highlights))

    def get_book_by_title(self, title: str) -> Optional[Article]:
        for article in self.articles:
            if article.get_title() == title:
                return article
        return None
