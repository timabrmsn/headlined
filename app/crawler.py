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

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

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
                h = Headlines()
                h.rss = entry
                h.rss_id = entry.id
                h.source = source
                h.domain = tld
                try:
                    db.add(h)
                    db.commit()
                except Exception as e:
                    print(e)



if __name__ == "__main__":
    fetch_rss_entries()
