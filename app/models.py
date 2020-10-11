from datetime import datetime
from time import mktime
import re
import pytz
import tldextract
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker, scoped_session

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

class SessionBase:
    query = scoped_session(SessionLocal).query_property()

Base = declarative_base(cls=SessionBase)

tag_association_table = Table("tag_association", Base.metadata,
    Column("headline_id", Integer, ForeignKey("headlines.headline_id")),
    Column("tag_id", Integer, ForeignKey("tags.tag_id"))
)

author_association_table = Table("author_association", Base.metadata,
    Column("headline_id", Integer, ForeignKey("headlines.headline_id")),
    Column("author_id", Integer, ForeignKey("authors.author_id"))
)

class Headlines(Base):
    __tablename__ = "headlines"

    headline_id = Column(Integer, primary_key=True, nullable=False)
    rss_id = Column(String, unique=True)
    source = Column(String)
    title = Column(String)
    link = Column(String)
    icon = Column(String)
    domain = Column(String)
    published = Column(String)
    published_parsed = Column(DateTime)
    summary = Column(String)
    authors = relationship("Authors", secondary=author_association_table)
    tags = relationship("Tags", secondary=tag_association_table)

    def __init__(self, rss, db):
        self.rss_id = rss.id
        self.source = rss.source
        self.title = rss.title
        self.link = rss.link
        self.domain = tldextract.extract(rss.link).registered_domain
        self.icon = f"https://www.google.com/s2/favicons?sz=128&domain={self.domain}"
        self.published = rss.published
        self.published_parsed = datetime.fromtimestamp(mktime(rss.published_parsed), tz=pytz.UTC)
        self.summary = getattr(rss, "summary", None)
        if authors := getattr(rss, "author", None):
            authors = authors.replace(" and ", ",").replace("By ", "").split(",")
            author_list = []
            for author in authors:
                if a := db.query(Authors).filter(Authors.name==author).first():
                    pass
                else:
                    a = Authors(name=author)
                author_list.append(a)
            self.authors = author_list
        if tags := getattr(rss, "tags", None):
            tag_list = []
            for tag in tags:
                if t := db.query(Tags).filter(Tags.term==tag["term"]).first():
                    pass
                else:
                    t = Tags(term=tag["term"])
                tag_list.append(t)
            self.tags = tag_list
        try:
            db.add(self)
            db.commit()
            print(f"added: {self.rss_id}, {self.source}")
        except IntegrityError as e:
            print(f"dupe: {self.rss_id}, {self.source}")
        except Exception as e:
            print(f"unknown exception: {e}: {self.rss_id}, {self.source}")
        finally:
            db.rollback()


class Authors(Base):
    __tablename__ = "authors"

    author_id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, unique=True)

class Tags(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, nullable=False)
    term = Column(String, unique=True)

class Author(BaseModel):
    name: str

    class Config:
        orm_mode = True

class Tag(BaseModel):
    term: str

    class Config:
        orm_mode = True

class Entry(BaseModel):
    title: str
    link: str
    icon: str
    domain: str
    published: str
    published_parsed: datetime
    summary: Optional[str] = None
    tags: Optional[List[Tag]] = []
    authors: Optional[List[Author]] = []
    source: str

    class Config:
        orm_mode = True
