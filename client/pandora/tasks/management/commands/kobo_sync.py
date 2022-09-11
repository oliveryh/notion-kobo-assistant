import datetime
import os
import sqlite3
from urllib.request import Request, urlopen

from django.conf import settings
from django.core.management.base import BaseCommand, CommandParser
from markdownify import markdownify as md

from pandora.tasks.kobo import Library
from pandora.tasks.models import Article


def clean_db(db_abspath):

    """For some reason kobuddy doesn't like the binary blobs of
    EventType=3 in the Event table. This function cleans the database"""

    conn = sqlite3.connect(db_abspath)
    query = "DELETE FROM Event WHERE EventType = 3;"
    conn.execute(query)
    conn.commit()


def get_highlight_markdown(url, highlights):

    md_output = []

    headers = {"User-Agent": "Magic Browser"}
    req = Request(url=url, headers=headers)
    webpage = urlopen(req).read()
    wt = webpage.decode("utf-8")
    wt_clean = wt
    # wt_clean = clean(wt)

    link_mapping = {}

    def get_segment_md(wt: str, content: str) -> str:

        haystack_raw = md(wt)
        search = content

        alphabets = [(chr(ord('a') + i)) for i in range(26)]
        alphabets += [(chr(ord('A') + i)) for i in range(26)]

        def strip_letters(string):
            return "".join([x for x in string if x in alphabets])

        haystack = haystack_raw

        import regex as re

        pattern = re.compile(r'\[([^][]+)\](\(((?:[^()]+|(?2))+)\))')

        for match in pattern.finditer(haystack):
            description, _, url = match.groups()
            link_string = f"[{description}]({url})"
            link_mapping[description] = link_string
            haystack = haystack.replace(link_string, description)

        alpha_search = strip_letters(search)
        alpha_pop = strip_letters(haystack)

        alpha_index_start = 0
        alpha_index_end = 0

        expand = 1
        while expand < len(alpha_search):
            if alpha_pop.count(alpha_search[:expand]) == 1:
                alpha_index_start = alpha_pop.index(alpha_search[:expand])
                break
            expand += 1

        expand = 1
        alpha_pop_rev = alpha_pop[::-1]
        alpha_search_rev = alpha_search[::-1]

        while expand < len(alpha_search_rev):
            if alpha_pop_rev.count(alpha_search_rev[:expand]) == 1:
                alpha_index_end = len(alpha_pop) - alpha_pop_rev.index(
                    alpha_search_rev[:expand]
                )
                break
            expand += 1

        bools = [x in alphabets for x in haystack]

        def get_position_in_original(index):
            total = 0
            non_alpha = 0
            idx = 0
            while total < index:
                is_alpha = bools[idx]
                if is_alpha:
                    total += 1
                else:
                    non_alpha += 1
                idx += 1
            return index + non_alpha

        if (alpha_index_start == 0) and (alpha_index_end == 0):
            res = content
        else:
            index_start = get_position_in_original(alpha_index_start)
            index_end = get_position_in_original(alpha_index_end)

            res = haystack[index_start + 1 : index_end]

        return res

    if highlights:
        md_output.append("# Highlights")
    for highlight in highlights:

        if highlight["type"] == "chapter":
            md_output.append(f"## {highlight['content']}")
        if highlight["type"] == "highlight":
            md_output.append(get_segment_md(wt_clean, highlight["content"]))

    md_output = "\n".join(md_output)

    for k, v in link_mapping.items():
        md_output = md_output.replace(k, v)

    return md_output


class Command(BaseCommand):
    help = 'Sync Kobo articles'

    def add_arguments(self, parser: CommandParser) -> None:

        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Refresh all article highlights including ones already completed',
        )

        return super().add_arguments(parser)

    def handle(self, *args, **options):

        upload_dir = '../upload'
        db_filename = 'KoboReader.sqlite'
        db_abspath = os.path.abspath(os.path.join(upload_dir, db_filename))

        # log db_abspath
        clean_db(db_abspath)

        # try:
        library = Library(db_abspath)
        # except Exception as exc:
        # raise FileNotFoundError("The database may not exist in the given path")

        library.load_articles()

        articles = Article.objects.all()

        for article in articles:
            kobo_article = library.get_book_by_title(article.name)
            if kobo_article:
                if kobo_article.is_finished() or options['force_update']:
                    highlights = kobo_article.get_highlights()
                    markdown = get_highlight_markdown(article.url, highlights)
                    article.highlights = markdown
                    article.completed_at = datetime.datetime.now()
                    article.time_read_minutes = kobo_article.get_time_spent()
                    article.save()
