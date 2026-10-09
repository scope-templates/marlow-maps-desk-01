---
title: Timeouts and retries
updated: 2026-01-19
---

# Timeouts and retries

The SDKs handle retries for you. If you call the HTTP API directly, this page gives the rules they follow so your own
client behaves the same way.

## Client timeouts

| Endpoint | Typical | Set your timeout to |
|---|---|---|
| `POST /v2/geocode`, `POST /v2/reverse-geocode` | under 150 ms | 10 s (3 s at checkout) |
| `POST /v2/geocode/batch` (500 addresses) | 5 to 15 s | 60 s |
| `POST /v2/routes` | under 1 s | 15 s |
| `POST /v2/matrix` (25 × 25) | 2 to 6 s | 20 s |
| `POST /v2/optimize` (100 stops) | up to 40 s | 60 s |

The server gives up on any request after 60 seconds and answers `504 upstream_timeout`.

## What to retry

| Response | Retry? | How |
|---|---|---|
| `429 rate_limited` | Yes | After `Retry-After` seconds |
| `429 recalculation_too_frequent` | Yes | After `Retry-After` seconds |
| `500 internal_error`, `503 service_unavailable`, `504 upstream_timeout` | Yes | Exponential backoff from 1 s, at most 3 tries |
| Connection error or client timeout | Yes, for reads and geocodes | As for 5xx |
| Any other 4xx | No | Fix the request |

Geocodes, reverse geocodes, matrices and optimisations have no side effects, so retrying them is always safe. Creating a
route is not: a retried `POST /v2/routes` after a client timeout can create two routes. Send an `Idempotency-Key`
header on route creation and Marlow returns the first route for any repeat with the same key within 24 hours.

## A retrying session for `requests`

```python
import os
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 503, 504],
    allowed_methods=["GET", "POST"],
    respect_retry_after_header=True,
)
session = requests.Session()
session.mount("https://", HTTPAdapter(max_retries=retry))
session.headers["X-Marlow-Key"] = os.environ["MARLOW_KEY"]
```

## From a shell

```bash
curl --retry 3 --retry-delay 2 --max-time 15 \
  -X POST https://api.marlowmaps.com/v2/routes \
  -H "X-Marlow-Key: $MARLOW_KEY" -H "Idempotency-Key: plan-2026-04-02-van7" \
  -H "Content-Type: application/json" -d @route.json
```

Never retry `410 endpoint_retired` or `401 invalid_key`; they will not change.
