from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()


class Headlines(Base):
    __tablename__ = "headlines"

    id = Column(Integer, primary_key=True)
    rss_id = Column(String, unique=True)
    rss = Column(JSONB)
    source = Column(String)
    domain = Column(String)
