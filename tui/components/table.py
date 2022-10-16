from abc import abstractmethod
from typing import List

from textual.widget import Widget
from textual.widgets import DataTable
from textual._cache import LRUCache

class Table(Widget):

    @abstractmethod
    def populate_table(self, table: DataTable) -> DataTable:
        """Add rows to the provided empty DataTable instantiation"""

    @abstractmethod
    def fetch_data(self) -> List[dict]:
        """A function that can be called to return a list of dictionaries"""

    @abstractmethod
    def apply_filter(self) -> List[dict]:
        """A function that filters data based on particular rules"""
        return self.data

    def build_table(self, table=None):
        if table is None:
            table = DataTable()
        return self.populate_table(table)

    def on_mount(self):
        self.collect_data()

    def collect_data(self):
        self.data = self.fetch_data()
        self.filtered_data = self.apply_filter()
        self.table = self.build_table()

    def _clear_table(self, table):
        table._clear_caches()
        table.columns = []
        table.rows = {}
        table.data = {}
        table.row_count = 0
        table._y_offsets = []
        table._row_render_cache = LRUCache(1000)
        table._cell_render_cache = LRUCache(10000)
        table._line_cache = LRUCache(1000)
        table._line_no = 0

    def refresh_table(self, fetch=True):
        table = self.query_one(DataTable)
        self._clear_table(table)
        if fetch:
            self.data = self.fetch_data()
        self.filtered_data = self.apply_filter()
        table = self.build_table(table)
        table.refresh()

    def compose(self) -> DataTable:
        yield self.table