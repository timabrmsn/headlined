#!/usr/bin/env python3
import sys
from os import environ
from itertools import count
from pathlib import Path
from time import sleep
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConflictError
import feedparser
import json
import tldextract
from datetime import datetime, timezone
from time import mktime
import shelve

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))


def fetch_rss_entries(file="urls.json"):
    with open(file, "r") as json_file:
        feeds = json.load(json_file)
    with shelve.open("processed_entries", writeback=True) as db:
        processed = db.get("processed", set())
        for site in feeds:
            page = feedparser.parse(site["url"])
            if page.status < 400:
                for entry in page.entries:
                    if entry.id in processed:
                        print(f"{entry.id} already processed.")
                        continue
                    processed.add(entry.id)
                    entry.source_link = page.href
                    if tags := getattr(entry, "tags", None):
                        entry.tags = [t["term"] for t in tags]
                    if authors := getattr(entry, "authors", None):
                        entry.authors = [a["name"] for a in authors if "name" in a]
                    yield {"site": site["site"],
                           "source_link": page.href,
                           "title": entry.title,
                           "link": entry.link,
                           "domain": tldextract.extract(entry.link).registered_domain,
                           "authors": getattr(entry, "authors", None),
                           "publisher": getattr(entry, "publisher", None),
                           "published": datetime.fromtimestamp(mktime(entry.published_parsed)).replace(tzinfo=timezone.utc),
                           "summary": getattr(entry, "summary", None),
                           "tags": getattr(entry, "tags", None),
                           }


if __name__ == "__main__":
    es = Elasticsearch(
        cloud_id=environ["ES_CLOUD_ID"],
        api_key=(environ["ES_API_ID"], environ["ES_API_KEY"])
    )
    while True:
        for i in count(1):
            for entry in fetch_rss_entries():
                try:
                    es.create("headlined", entry["link"], entry)
                except ConflictError:
                    pass
            print(f"Run {i} complete.")
            sleep(60)

