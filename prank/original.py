from dataclasses import dataclass

import html2epub
import click
import sqlite3
import pandas as pd

@dataclass
class Article:

    title: str
    url: str

    def generate_epub(self):

        epub = html2epub.Epub(self.title)
        chapter = html2epub.create_chapter_from_url("https://neilkakkar.com/things-I-learnt-from-a-senior-dev.html")
        epub.add_chapter(chapter)
        epub.create_epub("/tmp")

    def get_highlights(self):

        try:
            cnx = sqlite3.connect("/tmp/KoboReader.sqlite")
            query = "select Bookmark.ContentID,Bookmark.Text,Bookmark.Hidden,Bookmark.Annotation,Bookmark.ExtraAnnotationData,Bookmark.DateCreated,Bookmark.DateModified,content.BookTitle,content.Title,content.VolumeIndex,ChapterProgress from Bookmark, content WHERE Bookmark.ContentID = content.ContentID;"
            df = pd.read_sql_query(query, cnx)
        except:
            print("Unable to process sqlite file")
            exit(1)

        df = df[df["BookTitle"] == "How Not To Die"]
        df = df[df["Hidden"] == "false"]
        df = df[["ContentID", "BookTitle", "ChapterProgress", "Text", "VolumeIndex", "Hidden", "Title"]]
        df = df.sort_values(by=["VolumeIndex", "ChapterProgress"])
        df = df.reset_index()

        current_chapter = None
        for i in range(len(df)):
            chapter_title: str = df["Title"][i]
            highlight_text: str = df["Text"][i]

            if current_chapter != chapter_title:
                print("# " + chapter_title)
                current_chapter = chapter_title
            print("* " + highlight_text)

        current_chapter = None
        print(df)



@click.command()
@click.option("--title")
@click.option("--url")
@click.pass_context
def cli(ctx, title, url):
    ctx.obj["ARTICLE"] = Article(title, url)
    ctx.obj["ARTICLE"].get_highlights()

if __name__ == "__main__":
    cli(obj={})