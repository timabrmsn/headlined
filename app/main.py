import os
import re
from datetime import datetime, timedelta
from collections import namedtuple
from typing import List, Optional

from fastapi import Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from copy import copy

DATABASE_URL = "postgresql://headlined:c1o8mglpfn2fjdjm@db-postgresql-nyc1-headlines-do-user-4175084-0.a.db.ondigitalocean.com:25060/defaultdb?sslmode=require"
#os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class RSSEntry(Base):
    __tablename__ = "homepage_rssentry"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String)
    published = Column(String)
    published_parsed = Column(DateTime)
    summary = Column(String)
    tags = Column("tags", postgresql.ARRAY(String))
    author = Column(String)
    source = Column(String)


class Entry(BaseModel):
    id: int
    title: str
    link: str
    icon: str
    pub: str
    published: str
    published_parsed: datetime
    summary: Optional[str] = None
    tags: Optional[List[str]] = []
    author: List[str]
    source: str

    class Config:
        orm_mode = True


def _get_latest(db: Session):
    return (
        db.query(RSSEntry)
        .filter(RSSEntry.published_parsed >= datetime.now() - timedelta(days=10))
        .limit(25).all()
    )

db = SessionLocal()
class cache:
    time = datetime.now()
    data = _get_latest(db)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=List[Entry])
def get_latest(db: Session = Depends(get_db)):
    # if diff := (datetime.now() - cache.time) > timedelta(seconds=60):
    #     cache.data = _get_latest(db)
    #     cache.time = datetime.now()
    #     print(diff)
    cache.data = _get_latest(db)
    updated_entries = []
    for entry_orig in cache.data:
        entry = copy(entry_orig)
        try:
            domain = re.search(r"https?://([^\/]+)", entry.link).groups()[0]
            entry.pub = domain.split(".")[-2].upper()
            entry.icon = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
        except ValueError:
            entry.pub = entry.source
            entry.icon = "X"
        if match := re.match(r"[^|]+", entry.author):
            entry.author = match.group().replace(" and ", ",").replace("By ", "").split(",")
        else:
            entry.author = [entry.author]
        updated_entries.append(entry)
    return updated_entries
