---
title: Marlow Maps API overview
updated: 2026-07-14
---

# Marlow Maps API overview

The Marlow Maps API turns addresses into coordinates and coordinates into drivable routes. It is built for
delivery, courier and field-service software: the order screen that checks a drop-off address, the dispatch board that
plans a van's day, and the driver app that needs a fresh ETA when traffic changes.

All requests go to one base URL:

```
https://api.marlowmaps.com
```

Every call is HTTPS, sends and receives JSON, and is authenticated with the `X-Marlow-Key` header. There are no
cookies and no OAuth flow; a key belongs to an account, not a user.

## What the API covers

| Area | Main endpoints | Page |
|---|---|---|
| Geocoding | `POST /v2/geocode`, `POST /v2/geocode/batch`, `POST /v2/reverse-geocode` | [Geocode an address](geocode.md) |
| Routing | `POST /v2/routes`, `POST /v2/matrix`, `POST /v2/optimize` | [Routes](routes.md) |
| Webhooks | `POST /v2/webhooks` | [Webhooks overview](webhooks-overview.md) |

Coverage is limited to the UK, Ireland, the Netherlands, Germany and France. Requests for anywhere else return
`region_unsupported`; see [Regions](regions.md).

## A first request

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address": "14 Wharf Road, London N1 7GR"}'
```

```python
import os
import requests

resp = requests.post(
    "https://api.marlowmaps.com/v2/geocode",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"address": "14 Wharf Road, London N1 7GR"},
    timeout=10,
)
print(resp.status_code, resp.json()["results"][0]["precision"])
```

## Limits at a glance

- 600 requests per minute per key, across all endpoints.
- Up to 500 addresses per batch geocode request.
- Up to 100 stops per route.

The [Python quickstart](quickstart-python.md) walks through a full geocode-then-route flow in about ten minutes.
