if __name__ == "__main__":
    from notion.client import NotionClient
    from prank.collection import NotionCollection

    client = NotionClient(
        token_v2="0fb0689c4ffe6add436d896c427a6313949da6565f9109c969fd32b4840cc2530c965deb5365e18ee2928af66601f482e1e8f54deb6de0305b37aecd4ee12c5724664b02eca29668a442be45ed3f"
    )
    collection = client.get_collection("2c75694c-eeee-42a3-98e2-2bd19e67a4c7")
    prank = NotionCollection(collection)
    prank.enrich_rows()
    prank.save_to_epubs()
    prank.save_highlights()
    prank.save_status()
    prank.save_timespent()
