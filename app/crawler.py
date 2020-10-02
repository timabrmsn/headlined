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

from models import Headlines
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


db = SessionLocal()


def fetch_rss_entries(file="urls.json"):
    with open(file, "r") as json_file:
        feeds = json.load(json_file)
    for site in feeds:
        page = feedparser.parse(site["url"])
        if page.status < 400:
            tld = tldextract.extract(page.href).registered_domain
            source = page.href
            for entry in page.entries:
                yield (entry, tld, source)


def process_entry(entry, tld, source):
    h = Headlines()
    h.rss = entry
    h.rss_id = entry.id
    h.source = source
    h.domain = tld
    try:
        db.add(h)
        db.flush()
        db.commit()
        print(f"added: {entry.id}, {source}")
    except IntegrityError as e:
        db.rollback()
    except Exception as e:
        print(f"exception: {type(e)}\nentry_id: {entry.id}, source: {source}")
        db.rollback()


if __name__ == "__main__":
    for entry in fetch_rss_entries():
        process_entry(*entry)

