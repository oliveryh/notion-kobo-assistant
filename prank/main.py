import datetime
import tempfile
from typing import Dict, Optional

from notion.client import NotionClient
from md2notion.upload import upload
from prank.ptypes import Medium, Status
from prank.syncing import SyncGenerator
from prank.generators import *
from markdownify import markdownify as md

from notion_client import Client

from prank.config import config

class PRANKRow:
    def __init__(self, id, notion_url, url, title, medium, date_added, date_completed):
        self.id: str = id
        self.notion_url: str = notion_url
        self.url: str = url
        self.title: str = title
        self.medium: Optional[Medium] = Medium[medium] if medium else None
        self.date_added = datetime.datetime.strptime(date_added, '%Y-%m-%d') if date_added else None
        self.date_completed = datetime.datetime.strptime(date_completed, '%Y-%m-%d') if date_completed else None
        self.time_spent = None
        self.status = None
        self.highlights = None

    def __repr__(self):
        return f"<PRANKRow medium={self.medium} title={self.title}>"

    def enrich(self):
        if self.title is None:
            self.title = TitleGenerator().get_title(self.url, self.medium)
        if self.medium is None:
            self.medium = MediumGenerator().get_medium(self.url)
        if self.date_added is None:
            self.date_added = datetime.date.today()
        if self.status is None:
            self.status = Status.TODO


class PRANKRowCollectionRowBlock(PRANKRow):
    def __init__(self, result):
        id = result['id']
        notion_url = result['url']
        properties = result['properties']
        url = properties['URL']['url']
        title = properties['Name']['title'][0]['plain_text'] if properties['Name']['title'] != [] else None
        medium = properties['Medium']['select']['name'] if properties['Medium']['select'] else None
        date_added = properties['Date Added']['date']['start'] if properties['Date Added']['date'] else None
        date_completed = properties['Date Completed']['date']['start'] if properties['Date Completed']['date'] else None
        super().__init__(id, notion_url, url, title, medium, date_added, date_completed)

    def push(self, crb):

        update_payload = {}

        if self.title:
            update_payload.update({
                "Name": {
                    "type": "title",
                    "title": [{ "type": "text", "text": { "content": self.title } }]
                },
            })

        if self.medium:
            update_payload.update({
                "Medium": {
                    "type": "select",
                    "select": {
                        "name": self.medium.name
                    },
                },
            })

        update_payload.update({
            "Time Spent": {
                "type": "number",
                "number": self.time_spent
            }
        })

        update_payload.update({
            "Date Added": {
                "type": "date",
                "date": {
                    "start": self.date_added.strftime('%Y-%m-%d'),
                    "end": None,
                    "time_zone": None
                }
            }
        })
        
        curr_props = crb['properties']
        current_status = curr_props['Status']['select']['name'] if curr_props['Status']['select'] else None
        if current_status != "COMPLETE":
            if self.status and self.status.name == "COMPLETE":
                update_payload.update({
                    "Status": {
                        "type": "select",
                        "select": {
                            "name": self.status.name
                        },
                    },
                })
                update_payload.update({
                    "Date Completed": {
                        "type": "date",
                        "date": {
                            "start": self.date_completed.strftime('%Y-%m-%d'),
                            "end": None,
                            "time_zone": None
                        }
                    }
                })
            if self.highlights:

                md_output = []

                url = self.url
                headers = {"User-Agent": "Magic Browser"}
                req = Request(url=url, headers=headers)
                webpage = urlopen(req).read()
                wt = webpage.decode("utf-8")
                wt_clean = wt
                # wt_clean = clean(wt)

                def get_segment_md(wt:str, content:str) -> str:
                    haystack = md(wt)
                    search = content
                    
                    alphabets=[(chr(ord('a')+i)) for i in range(26)]
                    alphabets += [(chr(ord('A')+i)) for i in range(26)]

                    def strip_letters(string):
                        return "".join([x for x in string if x in alphabets])
                    
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
                        print(alpha_pop_rev.count(alpha_search_rev[:expand]))
                        if alpha_pop_rev.count(alpha_search_rev[:expand]) == 1:
                            alpha_index_end = len(alpha_pop) - alpha_pop_rev.index(alpha_search_rev[:expand])
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
                        
                        res = haystack[index_start+1: index_end]
                    
                    return res

                md_output.append("# Highlights")
                for highlight in self.highlights:

                    if highlight["type"] == "chapter":
                        md_output.append(f"## {highlight['content']}")
                    if highlight["type"] == "highlight":
                        md_output.append(get_segment_md(wt_clean, highlight["content"]))

                md_output = "\n".join(md_output)
                tp = tempfile.NamedTemporaryFile()
                tp.write(bytes(md_output, encoding="utf-8"))
                tp.flush()
                old_client = NotionClient(token_v2=config["notion"]["token_old"].get())
                page = old_client.get_block(self.notion_url)
                with open(tp.name, 'r', encoding="utf-8") as mdFile:
                    upload(mdFile, page)
        
        client = Client(auth=config["notion"]["token"].get())
        client.pages.update(self.id, properties=update_payload)


class PRANKCollection:
    def __init__(self, id):
        self.id: str = id
        self.rows: Dict[PRANKRow] = {}

    def pull(self):
        """
        Pull the current list of URLs and other attributes from Notion
        """

        client = Client(auth=config["notion"]["token"].get())
        collection = client.databases.query(database_id=self.id)
        for row in collection['results']:
            page_id = row['id']
            self.rows[page_id] = PRANKRowCollectionRowBlock(row)

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
        client = Client(auth=config["notion"]["token"].get())
        collection = client.databases.query(database_id=self.id)
        for row in collection['results']:
            page_id = row['id']
            self.rows[page_id].push(row)

    def run(self):

        self.pull()
        self.enrich()
        self.sync()
        self.push()


if __name__ == "__main__":
    collection = PRANKCollection(id=config["notion"]["collection"].get())
    collection.run()
