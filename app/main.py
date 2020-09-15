import os
import re
from datetime import datetime, timedelta
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

DATABASE_URL = os.environ["DATABASE_URL"]

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
    entries = _get_latest(db)
    for entry in entries:
        try:
            domain = re.search("https?://([^\/]+)", entry.link).groups()[0]
            entry.pub = domain.split(".")[-2].upper()
            entry.icon = f"https://www.google.com/s2/favicons?sz=128&domain={domain}"
        except ValueError:
            entry.pub = entry.source
            entry.icon = "X"
        match = re.match(r"[^|]+", entry.author)
        if match:
            entry.author = match.group().replace(" and ", ",").replace("By ", "").split(",")
        else:
            entry.author = [entry.author]
    return entries
