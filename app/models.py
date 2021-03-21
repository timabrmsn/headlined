from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Headline(BaseModel):
    site: str
    source_link: str
    title: str
    link: str
    domain: str
    published: datetime
    publisher: Optional[str] = None
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    authors: Optional[List[str]] = None


class Query(BaseModel):
    term: str
    query: str 
