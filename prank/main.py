from typing import Dict

from notion.block import HeaderBlock, SubheaderBlock, TextBlock
from notion.client import NotionClient
from notion.collection import CollectionRowBlock

from prank.ptypes import Medium
from prank.syncing import SyncGenerator
from prank.generators import *

from prank.config import config


class PRANKRow:
    def __init__(self, url, title, medium, date_completed):
        self.url: str = url
        self.title: str = title
        self.medium: Medium = medium
        self.date_completed = date_completed
        self.time_spent = None
        self.status = None
        self.highlights = None

    def __repr__(self):
        return f"<PRANKRow medium={self.medium} title={self.title}>"

    def enrich(self):
        self.title = (
            self.title
            if self.title
            else TitleGenerator().get_title(self.url, self.medium)
        )
        self.medium = (
            self.medium if self.medium else MediumGenerator().get_medium(self.url)
        )


class PRANKRowCollectionRowBlock(PRANKRow):
    def __init__(self, crb: CollectionRowBlock):

        url = crb.url
        title = crb.title if len(crb.title) != 0 else None
        medium = Medium[crb.medium] if crb.medium else None
        date_completed = crb.date_completed
        super().__init__(url, title, medium, date_completed)

    def push(self, crb: CollectionRowBlock):

        crb.title = self.title if self.title else None
        crb.medium = self.medium.name if self.medium else None
        crb.status = self.status.name if self.status else None
        crb.time_spent = self.time_spent
        crb.date_completed = self.date_completed

        if self.highlights:
            crb.children.add_new(HeaderBlock, title="Highlights")
            for highlight in self.highlights:
                if highlight["type"] == "chapter":
                    crb.children.add_new(SubheaderBlock, title=highlight["content"])
                if highlight["type"] == "highlight":
                    crb.children.add_new(TextBlock, title=highlight["content"])


class PRANKCollection:
    def __init__(self, id):
        self.id: str = id
        self.rows: Dict[PRANKRow] = {}

    def pull(self):
        """
        Pull the current list of URLs and other attributes from Notion
        """
        client = NotionClient(token_v2=config["notion"]["token"].get())
        collection = client.get_collection(self.id)
        for row in collection.get_rows():
            url = row.url
            self.rows[url] = PRANKRowCollectionRowBlock(row)

    def enrich(self):
        """
        Populate fields that can be derived from the URL after initially
        being added
        """
        for row in self.rows.values():
            row.enrich()

    def sync(self):

        SyncGenerator().sync(self.rows)

    def push(self):
        """
        Push the updated fields back to Notion after all enriching &
        syncing with other services is complete
        """
        client = NotionClient(token_v2=config["notion"]["token"].get())
        collection = client.get_collection(self.id)
        for row in collection.get_rows():
            self.rows[row.url].push(row)

    def run(self):

        self.pull()
        self.enrich()
        self.sync()
        self.push()


if __name__ == "__main__":
    collection = PRANKCollection(id=config["notion"]["collection"].get())
    collection.run()
