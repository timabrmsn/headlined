import os
import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import feedparser
import tldextract
import json
from datetime import datetime
from pathlib import Path
from time import mktime, sleep
from pytz import timezone

from models import db, Base, Headlines
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


def fetch_rss_entries(file="urls.json"):
    with open(file, "r") as json_file:
        feeds = json.load(json_file)
    for site in feeds:
        page = feedparser.parse(site["url"])
        if page.status < 400:
            for entry in page.entries:
                entry.source = page.href
                yield entry


if __name__ == "__main__":
    for entry in fetch_rss_entries():
        h = Headlines(entry, db)

