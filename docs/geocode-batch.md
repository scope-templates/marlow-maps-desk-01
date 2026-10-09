---
title: Batch geocoding
updated: 2026-06-23
---

# Batch geocoding

You can send up to 500 addresses per `POST /v2/geocode/batch` request. The whole batch counts as a single request
against the 600 requests per minute rate limit, although each address counts toward your monthly geocode quota.

The limit was raised from 100 to 500 on 2025-04-14. Requests with more than 500 addresses are rejected as a whole with
`413 batch_too_large`; nothing in them is geocoded.

## Request

```json
{
  "addresses": [
    "14 Wharf Road, London N1 7GR",
    {"address": "Keizersgracht 221, 1016 DV Amsterdam", "ref": "order-1182"},
    {"address": "Via Roma 10, 20121 Milano", "ref": "order-1183"}
  ],
  "country": null
}
```

Each item is either a string or an object with `address` and an optional `ref` of up to 64 characters. The `ref`
comes back untouched so you can match results to your own records. An optional top-level `country` applies to every
item.

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode/batch \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d @addresses.json
```

```python
import os
import requests

def geocode_many(addresses):
    resp = requests.post(
        "https://api.marlowmaps.com/v2/geocode/batch",
        headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
        json={"addresses": addresses[:500]},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["results"]
```

## Response

Results come back in the same order as the input, one per address. A bad address does not fail the batch; it gets its
own `status`.

```json
{
  "results": [
    {"status": "ok", "lat": 51.5322, "lng": -0.0962, "precision": "rooftop", "ref": null},
    {"status": "ok", "lat": 52.3745, "lng": 4.8844, "precision": "rooftop", "ref": "order-1182"},
    {"status": "region_unsupported", "ref": "order-1183"}
  ],
  "counts": {"ok": 2, "no_match": 0, "region_unsupported": 1, "invalid_address": 0},
  "request_id": "req_a51d0c77"
}
```

| Item `status` | Meaning |
|---|---|
| `ok` | Geocoded; `precision` is `rooftop`, `street` or `locality` |
| `no_match` | No match in the supported regions |
| `region_unsupported` | Outside the UK, Ireland, the Netherlands, Germany and France |
| `invalid_address` | Empty, or longer than 300 characters |

## Request-level errors

| Status | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | `addresses` missing or empty |
| 413 | `batch_too_large` | More than 500 addresses |
| 429 | `rate_limited` | Over 600 requests per minute |

Allow up to 30 seconds for a full batch of 500. Tips for files with thousands of rows are in
[Batch geocoding at scale](batch-best-practices.md).
