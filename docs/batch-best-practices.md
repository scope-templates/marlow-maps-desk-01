---
title: Batch geocoding at scale
updated: 2026-02-02
---

# Batch geocoding at scale

Importing a customer file, cleaning a CRM export or re-geocoding old v1 results usually means tens of thousands of
addresses. This page covers how to push them through `POST /v2/geocode/batch` quickly without tripping limits.

## Split into groups of 500

The batch endpoint takes up to 500 addresses. Anything larger fails with `413 batch_too_large`, so split on your
side:

```python
import os
import time
import requests

URL = "https://api.marlowmaps.com/v2/geocode/batch"
HEADERS = {"X-Marlow-Key": os.environ["MARLOW_KEY"]}

def batches(rows, size=500):
    for start in range(0, len(rows), size):
        yield rows[start:start + size]

def geocode_file(rows):
    out = []
    for group in batches(rows):
        while True:
            resp = requests.post(URL, headers=HEADERS, json={"addresses": group}, timeout=60)
            if resp.status_code == 429:
                time.sleep(int(resp.headers["Retry-After"]))
                continue
            resp.raise_for_status()
            out.extend(resp.json()["results"])
            break
    return out
```

## Deduplicate first

Customer files repeat addresses. Normalise case and whitespace, drop exact duplicates, and fan results back out
afterwards. On a typical delivery-history export this removes a third of the rows and the same share of quota.

## Use `ref`

Send each row's primary key as `ref` so you never depend on array position when writing results back:

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode/batch \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"addresses": [{"address": "Torstraße 109, 10119 Berlin", "ref": "cust-20931"}]}'
```

## Throughput

One worker sending one batch at a time typically finishes 500 addresses in 5 to 15 seconds, which is well under the
600 requests per minute ceiling. Up to four workers sharing one key is safe; past that, watch
`X-RateLimit-Remaining` and back off when it drops below 20.

## Handle per-item failures

A batch returns `200` even when some items fail. Count the item statuses in `counts` and route `no_match` and
`invalid_address` rows to a manual review queue. `region_unsupported` rows will not succeed on retry; flag them instead.

## Quota

Each address uses one geocode from your monthly quota, including addresses that come back `no_match`. Run a 500-row
sample with a test key (`mm_test_`) before a large live job to check your cleaning step.
