#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["elasticsearch<9"]
# ///
import os, json, sys
from elasticsearch import Elasticsearch

es = Elasticsearch(
    hosts=[os.getenv("ELASTIC_URL")],
    basic_auth=(os.getenv("ELASTIC_USER"), os.getenv("ELASTIC_PASS")),
)

agencies = [
    {k: hit["_source"][k][0] for k in ("title", "nid", "url")}
    for hit in es.search(
        index=os.getenv("ELASTIC_INDEX"),
        query={"match": {"content_type": "government_organisation"}},
        _source=["title", "nid", "url"],
        sort="url",
        size=10000,
    )["hits"]["hits"]
]

output = json.dumps(agencies, indent=2)

if len(sys.argv) > 1:
    with open(sys.argv[1], "w") as f:
        f.write(output)
    print(f"Wrote {len(agencies)} agencies to {sys.argv[1]}")
else:
    print(output)
