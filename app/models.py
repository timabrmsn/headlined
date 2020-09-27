from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Headlines(Base):
    __tablename__ = "headlines"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    link = Column(String)
    published_text = Column(String)
    published_parsed = Column(DateTime)
    summary = Column(String)
    icon = Column(String)
    site = Column(String)
    source = Column(String)


class Authors(Base):
    __tablename__ = "authors"
    
    author_id = Column(Integer, primary_key=True)
    name = Column(String)


class Tags(Base):
    __tablename__ = "tags"
    
    tag_id = Column(Integer, primary_key=True)
    name = Column(String)


class HeadlineTags(Base):
    __tablename__ = "headline_tags"
    
    headline_tag_id = Column(Integer, primary_key=True)
    tag_id = Column(Integer)
    headline_id = Column(Integer)



class HeadlineAuthors(Base):
    __tablename__ = "headline_authors"

    headline_author_id = Column(Integer, primary_key=True)
    author_id = Column(Integer)
    headline_id = Column(Integer)