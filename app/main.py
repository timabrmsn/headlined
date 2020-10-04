import os
import re
from datetime import datetime, timedelta
from collections import namedtuple
from typing import List, Optional

from fastapi import Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from models import Headlines

from copy import copy

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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
    updated = []
    entries = (
        db.query(Headlines)
        .filter(Headlines.published_parsed >= datetime.now() - timedelta(days=10))
        .limit(25).all()
    )
    for entry in entries:
        e = Entry(**entry.rss)
        e.pub = entry.domain
        e.source = entry.source
        e.icon = f"https://www.google.com/s2/favicons?sz=128&domain={entry.domain}"
        updated.append(e)
    return updated


class cache:
    time = datetime.now()
    data = _get_latest(SessionLocal())

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
    if diff := (datetime.now() - cache.time) > timedelta(seconds=60):
        cache.data = _get_latest(db)
        cache.time = datetime.now()
    return cache.data
