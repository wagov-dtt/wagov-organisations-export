# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests",
# ]
# ///
# agencies.py
import os
import json
import requests

ELASTIC_URL = os.getenv("ELASTIC_URL")
ELASTIC_INDEX = os.getenv("ELASTIC_INDEX")
ELASTIC_USER = os.getenv("ELASTIC_USER")
ELASTIC_PASS = os.getenv("ELASTIC_PASS")

response = requests.post(
    f"{ELASTIC_URL}/{ELASTIC_INDEX}/_search",
    auth=(ELASTIC_USER, ELASTIC_PASS),
    headers={"Content-Type": "application/json"},
    json={
        "query": {"match": {"content_type": "government_organisation"}},
        "_source": ["content_type", "nid", "title", "url", "field_url"],
        "sort": ["url"],
        "size": 10000,
    },
)

agencies = [
    {key: hit["_source"][key][0] for key in ("title", "nid", "url")}
    for hit in response.json()["hits"]["hits"]
]

print(json.dumps(agencies, indent=2))
