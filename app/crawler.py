#!/usr/bin/env python3
import sys
from itertools import count
from pathlib import Path
from time import sleep

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import feedparser
import json

from models import db, Headlines

processed_ids = set()

def fetch_rss_entries(file="urls.json"):
    with open(file, "r") as json_file:
        feeds = json.load(json_file)
    for site in feeds:
        page = feedparser.parse(site["url"])
        if page.status < 400:
            for entry in page.entries:
                if entry.id in processed_ids:
                    print(f"{entry.id} already processed.")
                    continue
                processed_ids.add(entry.id)
                entry.source = page.href
                yield entry


if __name__ == "__main__":
    while True:
        for i in count(1):
            for entry in fetch_rss_entries():
                h = Headlines(entry, db)
            print(f"Run {i} complete.")
            sleep(60)

