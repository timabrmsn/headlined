import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

import feedparser
import tldextract
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from time import mktime, sleep
from pytz import timezone

from models import Headlines, Authors, Tags, HeadlineAuthors, HeadlineTags
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://headlined:c1o8mglpfn2fjdjm@db-postgresql-nyc1-headlines-do-user-4175084-0.a.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
# os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

db = SessionLocal()


def fetch_rss_entries(file="urls.json"):
    with open(file, "r") as json_file:
        feeds = json.load(json_file)
    for site in feeds:
        page = feedparser.parse(site["url"])
        yield page


def extract_headline_row(entry: feedparser.FeedParserDict):
    h = Headlines()
    h.title = entry.title
    h.link = entry.link
    h.published_text = getattr(entry, 'published', None)
    h.published_parsed = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone('UTC')) if getattr(entry,
                                                                                                               "published_parsed",
                                                                                                               None) else None
    h.source = getattr(getattr(entry, "title_detail", None), "base", None)
    h.summary = getattr(entry, 'summary', None)
    domain = tldextract.extract(entry.link)
    h.pub = domain.registered_domain
    h.icon = f"https://www.google.com/s2/favicons?sz=128&domain={domain.registered_domain}"
    return h


def extract_authors_rows(entry: feedparser.FeedParserDict):
    authors = getattr(entry, 'author')
    if authors is not None:
        if match := re.match(r"[^|]+", authors):
            authors = match.group().replace(" and ", ",").replace("By ", "").split(",")
            return authors
        else:
            return [authors]
    else:
        return ["N/A"]


if __name__ == "__main__":
    for site in fetch_rss_entries():
        for entry in site.entries:
            row = extract_headline_row(entry)
            db.add(row)
            db.flush()
            db.commit()
            authors = extract_authors_rows(entry)
