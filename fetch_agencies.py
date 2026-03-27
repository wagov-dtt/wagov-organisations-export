#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path
from urllib.parse import quote

import urllib3


FIELDS = ("title", "nid", "url")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def first_value(source: dict, key: str):
    value = source[key]
    return value[0] if isinstance(value, list) else value


def fetch_agencies() -> list[dict]:
    base_url = require_env("ELASTIC_URL").rstrip("/")
    index = quote(require_env("ELASTIC_INDEX"), safe=",*")
    auth = f"{require_env('ELASTIC_USER')}:{require_env('ELASTIC_PASS')}"

    body = {
        "query": {"match": {"content_type": "government_organisation"}},
        "_source": list(FIELDS),
        "sort": "url",
        "size": 10000,
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        **urllib3.make_headers(basic_auth=auth),
    }

    response = urllib3.PoolManager(
        timeout=urllib3.Timeout(connect=10.0, read=60.0)
    ).request(
        "POST",
        f"{base_url}/{index}/_search",
        body=json.dumps(body).encode(),
        headers=headers,
    )

    if response.status >= 400:
        raise SystemExit(
            f"Elasticsearch search failed: HTTP {response.status} "
            f"{response.data.decode('utf-8', 'replace')}"
        )

    payload = json.loads(response.data)
    return [
        {key: first_value(hit["_source"], key) for key in FIELDS}
        for hit in payload["hits"]["hits"]
    ]


def main() -> None:
    output = json.dumps(fetch_agencies(), indent=2)

    if len(sys.argv) > 1:
        Path(sys.argv[1]).write_text(output)
        print(f"Wrote agencies to {sys.argv[1]}")
    else:
        print(output)


if __name__ == "__main__":
    main()
