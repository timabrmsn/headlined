import logging
import os
from datetime import datetime, timedelta
from typing import List

from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from models import Headlines
from models import Authors
from models import Tags
from models import Entry
from models import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

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
    return db.query(Headlines)\
        .filter(Headlines.published_parsed >= datetime.utcnow() - timedelta(days=10))\
        .limit(25).all()

class cache:
    time = datetime.now()
    data = _get_latest(SessionLocal())

logger = logging.getLogger(__name__)

app = FastAPI()
app.logger = logger

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/", response_model=List[Entry])
def get_latest(request: Request, db: Session = Depends(get_db)):
    if diff := (datetime.now() - cache.time) > timedelta(seconds=60):
        cache.data = _get_latest(db)
        cache.time = datetime.now()
    request.app.logger.info(cache.data)
    return cache.data
