import os
from asyncio import sleep
from datetime import datetime, timedelta
from typing import List

import render
from fastapi import Depends
from fastapi import FastAPI
from fastapi import Request
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from models import Headlines
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


def get_latest(db: Session, delta: timedelta):
    return db.query(Headlines) \
        .filter(Headlines.published_parsed >= datetime.utcnow() - delta) \
        .order_by(Headlines.published_parsed.desc()) \
        .limit(25).all()


class cache:
    def __init__(self):
        self.time = datetime.now()
        self.data = []


home_cache = cache()
home_cache.data = get_latest(SessionLocal(), timedelta(days=10))

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_model=List[Entry])
async def home(request: Request, db: Session = Depends(get_db)):
    if (datetime.now() - home_cache.time) > timedelta(seconds=60):
        home_cache.data = get_latest(db, timedelta(days=10))
        home_cache.time = datetime.now()
    return templates.TemplateResponse(
        "index.html",
        {"data": [render.headline(entry) for entry in home_cache.data],
         "request": request}
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    connection_cache = cache()
    connection_cache.data = home_cache.data
    while True:
        await sleep(5)
        latest = get_latest(db, timedelta(days=10))
        new = []
        for entry in latest:
            if entry not in connection_cache.data:
                new.append(entry)
        if new:
            headlines = "\n".join(
                [render.headline(entry)
                 for entry in latest]
            )
            await websocket.send_text(
                f"""<turbo-stream action="prepend" target="headlines">
                        <template>
                            {headlines}
                        </template>
                    </turbo-stream>
            """)
        connection_cache.data = latest
