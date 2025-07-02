#!/usr/bin/env python3
import os, json, sys
from elasticsearch import Elasticsearch

# Setup Elasticsearch client
es = Elasticsearch(
    hosts=[os.getenv("ELASTIC_URL")],
    basic_auth=(os.getenv("ELASTIC_USER"), os.getenv("ELASTIC_PASS")),
)

# Search for nodes of government_organisation content_type in drupal index
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

# Format as pretty JSON to make diffs nice
output = json.dumps(agencies, indent=2)

# Write to file if provided, otherwise print to stdout
if len(sys.argv) > 1:
    with open(sys.argv[1], "w") as f:
        f.write(output)
    print(f"Wrote {len(agencies)} agencies to {sys.argv[1]}")
else:
    print(output)
