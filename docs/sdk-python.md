---
title: Python SDK
updated: 2026-05-27
---

# Python SDK

The `marlowmaps` package is a thin client over the HTTP API. It adds the `X-Marlow-Key` header, splits large batches,
waits out `429` responses and turns error bodies into exceptions. Everything it does can also be done with `requests`,
and the examples in these docs use `requests` so you can see the wire format.

```bash
pip install "marlowmaps>=2.3,<3"
```

Python 3.9 or later. Versions before 2.0 called `GET /v1/geocode` and have not worked since that endpoint was retired
on 2025-06-30; upgrade if you see `endpoint_retired` in your logs.

## Basics

```python
import os
from marlowmaps import Client

client = Client(api_key=os.environ["MARLOW_KEY"], timeout=10, max_retries=3)

hit = client.geocode("14 Wharf Road, London N1 7GR", country="GB")
print(hit["precision"])          # rooftop

results = client.geocode_batch(addresses)    # any length; sent 500 at a time
route = client.routes.create(profile="van", stops=stops, recalculate=True)
client.routes.recalculate(route["route_id"])
```

`geocode` returns the first result dict; pass `limit=3` to get a list. `geocode_batch` returns results in input order.

## What the client does on errors

| Situation | Behaviour |
|---|---|
| `429 rate_limited` | Sleeps for `Retry-After` seconds and retries, up to `max_retries` |
| `500`, `503`, connection reset | Retries with backoff, up to `max_retries` |
| Any other 4xx | Raises `marlowmaps.ApiError` at once |

```python
from marlowmaps import ApiError

try:
    client.geocode("Via Roma 10, 20121 Milano")
except ApiError as err:
    print(err.status, err.code, err.request_id)   # 422 region_unsupported req_...
```

## Verifying webhooks

```python
from marlowmaps.webhooks import verify

ok = verify(raw_body=request.get_data(),
            signature=request.headers["X-Marlow-Signature"],
            secret=os.environ["MARLOW_WEBHOOK_SECRET"])
```

`verify` computes the HMAC-SHA256 of the raw body and compares in constant time.

## The same call without the SDK

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" -H "Content-Type: application/json" \
  -d '{"address": "14 Wharf Road, London N1 7GR", "country": "GB"}'
```

The SDK is MIT licensed. Its release notes track the API [changelog](changelog.md).
