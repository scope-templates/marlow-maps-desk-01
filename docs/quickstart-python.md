---
title: Quickstart for Python
updated: 2026-05-27
---

# Quickstart for Python

This walkthrough geocodes two addresses and plans a van route between them using nothing but the `requests`
package. It takes about ten minutes. If you prefer a client library, the [Python SDK](sdk-python.md) wraps the same
calls.

## 1. Get a test key

In the dashboard open **Settings**, then **API keys**, and create a key. Test keys start `mm_test_`; they behave like
live keys but are not billed. Export it so the examples can read it:

```bash
export MARLOW_KEY=mm_test_2b7c91e0d4a6f835
pip install requests
```

## 2. Geocode the pickup and the drop-off

```python
import os
import requests

BASE = "https://api.marlowmaps.com"
session = requests.Session()
session.headers["X-Marlow-Key"] = os.environ["MARLOW_KEY"]


def geocode(address):
    resp = session.post(f"{BASE}/v2/geocode", json={"address": address}, timeout=10)
    resp.raise_for_status()
    return resp.json()["results"][0]


pickup = geocode("14 Wharf Road, London N1 7GR")
dropoff = geocode("221 Kingsland Road, London E2 8AN")
print(pickup["precision"], dropoff["precision"])
```

`precision` comes back as `rooftop`, `street` or `locality`. For a doorstep delivery you usually want `rooftop`;
see [Precision](precision.md) for how to handle the other two.

## 3. Plan the route

```python
route = session.post(
    f"{BASE}/v2/routes",
    json={
        "profile": "van",
        "stops": [
            {"lat": pickup["lat"], "lng": pickup["lng"]},
            {"lat": dropoff["lat"], "lng": dropoff["lng"]},
        ],
    },
    timeout=15,
).json()
print(route["route_id"], route["duration_s"], "seconds")
```

## 4. Handle the errors you will meet first

| Status | `error.code` | What to do |
|---|---|---|
| 401 | `missing_key` / `invalid_key` | Check the `X-Marlow-Key` header |
| 404 | `no_match` | Ask the user to check the address |
| 422 | `region_unsupported` | The address is outside the five supported countries |
| 429 | `rate_limited` | Wait for the `Retry-After` seconds, then retry |

Next, register a webhook so your app hears about [route recalculations](route-recalculation-webhooks.md).
