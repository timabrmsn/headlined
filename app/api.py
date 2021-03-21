from os import environ

from fastapi import FastAPI
from elasticsearch import Elasticsearch

from models import Headline
from models import Query

app = FastAPI()

es = Elasticsearch(
        cloud_id=environ["ES_CLOUD_ID"],
        api_key=(environ["ES_API_ID"], environ["ES_API_KEY"])
    )


@app.post("/", response_model=List[Headline])
def home(query: Query):
    body = {"query": {"match": {query.term: {"query": query.query }}}}
    return [Headline.parse_obj(obj["_source"]) for obj in es.search(body=body)["hits"]["hits"]]
