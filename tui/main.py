import datetime
import select

from textual import events
from textual.app import App
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Footer, Header, Input, Static, DataTable

from tui.api.models import Article, Highlight, add_article, create_tables
from tui.components.table import Table
from tui.components.notification import Notification
from tui.components.stopwatch import Stopwatch
from tui.components.markdown import MyMarkdown
from tui.exceptions import ValidationError
from tui.icons import NerdIcon

from tui.components.markdown import MyMarkdown
class ArticleList(Table):

    filter = {}

    def fetch_data(self):
        articles = Article.select()
        return articles

    def populate_table(self, table):
        for column in [f"{NerdIcon.CHECK}", f"{NerdIcon.CLOCK}", "Author", "Title"]:
            table.add_column(column)
        table.zebra_stripes = True

        for datum in self.filtered_data:
            table.add_row(
                f"{NerdIcon.CHECK}" if datum.completed_at else "",
                str(datetime.timedelta(seconds=datum.time_secs)),
                datum.author,
                datum.title,
            )
        return table


class HighlightColumn(Static):

    def compose(self) -> ComposeResult:
        yield Static("🟦\n🟦", id='highlighting')

    def render(self, *args, **kwargs):
        my_markdown = self.screen.query_one('#content', Static).renderable
        highlight_string = my_markdown.get_highlight_mapping()
        highlighting = self.query_one('#highlighting', Static)
        highlighting.update(highlight_string)
        return super().render(*args, **kwargs)


class ArticleContent(Static):

    def __init__(self, markdown='', article=None, *args, **kwargs):
        self.markdown = markdown
        self.article = None
        super().__init__(*args, **kwargs)

    def refresh_content(self):
        self.query_one('#content', Static).update(self.markdown)

    def compose(self) -> ComposeResult:
        yield Static(MyMarkdown(self.markdown, self.article), id='content', classes='-active')

    def on_click(self, event: events.Click) -> None:
        my_markdown = self.query_one('#content', Static).renderable
        index, element = my_markdown.get_element_at_line(event.y + 1)
        existing_highlight = Highlight.filter(article=self.article, segment=index)
        if existing_highlight:
            query = Highlight.delete().where(Highlight.article == self.article, Highlight.segment == index)
            query.execute()
        else:
            Highlight.create(
                article=self.article,
                segment=index,
            )
        highlight_margin = self.screen.query_one(HighlightColumn)
        highlight_margin.render()
        meta = self.get_style_at(event.x, event.y).meta
        if meta:
            event.stop()


class BasicApp(App):
    """A Textual app to manage stopwatches."""

    CSS_PATH = 'main.css'

    BINDINGS = [
        ("enter", "view_article", "View article contents"),
        ("c", "mark_complete", "Mark as complete"),
        ("f", "stop_reading", "Stop reading current article"),
    ]

    article_being_viewed = None

    def compose(self) -> ComposeResult:
        yield Header(classes='')
        yield Footer()
        yield Input(placeholder='Enter a URL')
        yield Notification(id='notification')
        yield ArticleList()
        yield Stopwatch()
        yield Horizontal(
            HighlightColumn(),
            ArticleContent(),
        )

    def on_my_markdown_finished_render(self, message: MyMarkdown.FinishedRender) -> None:
        self.screen.styles.animate("background", message.color, duration=0.5)

    def on_input_submitted(self, message: Input.Submitted) -> None:
        """A coroutine to handle a text submitted message."""
        if message.value:
            try:
                article = self.create_article(message.value)
                input = self.query_one(Input)
                input.value = ''
            except ValidationError as exc:
                self._notify(f'{exc.field}: {exc.message}', 'warning')

    def _get_table_row_data(self):
        proc_list = self.query_one(ArticleList)
        tickets = proc_list.filtered_data
        cursor_row = self.query_one(DataTable).cursor_row
        return tickets[cursor_row]

    def action_view_article(self):
        if self.article_being_viewed:
            stopwatch = self.query_one(Stopwatch)
            elapsed_time = stopwatch.reset_timer()
            if elapsed_time > 0:
                self.article_being_viewed.time_secs = int(elapsed_time)
                self.article_being_viewed.save()
                article_list = self.query_one(ArticleList)
                article_list.refresh_table()
        selected_article = self._get_table_row_data()
        markdown = selected_article.markdown
        title = selected_article.title
        content = self.query_one(ArticleContent)
        content.markdown = MyMarkdown(markdown, selected_article)
        content.article = selected_article
        content.refresh_content()
        self.article_being_viewed = selected_article
        stopwatch = self.query_one(Stopwatch)
        stopwatch.start_timer()
        stopwatch.set_total(self.article_being_viewed.time_secs)
        self._notify(f'Viewing article {title}', 'success')

    def action_stop_reading(self):
        content = self.query_one(ArticleContent)
        content.markdown = ''
        content.refresh_content()
        stopwatch = self.query_one(Stopwatch)
        elapsed_time = stopwatch.reset_timer()
        if elapsed_time > 0:
            self.article_being_viewed.time_secs = int(elapsed_time)
            self.article_being_viewed.save()
            article_list = self.query_one(ArticleList)
            article_list.refresh_table()

    def action_mark_complete(self):
        selected_article = self._get_table_row_data()
        title = selected_article.title
        selected_article.completed_at = datetime.datetime.now()
        selected_article.save()
        article_list = self.query_one(ArticleList)
        article_list.refresh_table()
        self._notify(f'Marked {title} as complete', 'success')

    def _notify(self, message, type):
        notification = self.query_one(Notification)
        notification.notify(message, type)

    def create_article(self, url: str) -> None:
        """Looks up a word."""
        add_article(url=url)
        article_list = self.query_one(ArticleList)
        article_list.refresh_table()

if __name__ == "__main__":
    create_tables()
    app = BasicApp()
    app.run()
