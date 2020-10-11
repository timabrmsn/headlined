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
from sqlalchemy.types import DateTime
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from models import Headlines, Authors, Tags, Entry, Base

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def _get_latest(db: Session):
    updated = []
    entries = (
        db.query(Headlines, Authors, Tags)
        .filter(Headlines.published_parsed >= datetime.utcnow() - timedelta(days=10))
        .limit(25).all()
    )


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
