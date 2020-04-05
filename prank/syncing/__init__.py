from notion.block import TextBlock, SubheaderBlock, HeaderBlock

from prank.ptypes import Medium, Status
from prank.syncing.article import Library
from prank.converters.epub import EpubConverter
import datetime
from prank.config import config

class SyncGenerator:

    def sync(self, rows) -> bool:
        for medium in Medium:
            if (medium == Medium.VIDEO) or (medium == Medium.OTHER):
                continue
            filtered_rows = {k: v for k, v in rows.items() if v.medium == medium}
            syncer = self._get_syncer(medium)
            syncer(filtered_rows)
        return True

    def _get_syncer(self, medium: Medium):
        if medium == Medium.ARTICLE:
            return self._sync_kobo

    def _sync_kobo(self, rows):
        print(config)
        library = Library(config["kobo"]["db"].get())
        library.load_articles()
        for row in rows.values():
            article = library.get_book_by_title(row.title)
            if article:
                row.status = Status.COMPLETE if article.is_finished() else Status.TODO
                row.time_spent = article.get_time_spent()
                if row.status == Status.COMPLETE:
                    if row.date_completed is None:
                        row.date_completed = datetime.date.today()
                        row.highlights = article.get_highlights()

            else:
                ec = EpubConverter(row.url)
                ec.generate_epub(config["kobo"]["book_store"].get())
                row.status = Status.TODO
                row.time_spent = 0
