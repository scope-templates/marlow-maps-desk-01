---
title: Geocode an address
updated: 2026-06-23
---

# Geocode an address

`POST /v2/geocode` turns one free-text address into coordinates.

```
POST https://api.marlowmaps.com/v2/geocode
X-Marlow-Key: <key>
Content-Type: application/json

{"address": "..."}
```

The address goes in a JSON body, not in the query string. `GET /v1/geocode` was retired on 2025-06-30 and now returns
`410 endpoint_retired`; if you are still moving off it, read [Migrating from v1](migrating-from-v1.md).

## Request body

| Field | Type | Required | Notes |
|---|---|---|---|
| `address` | string | yes | 1 to 300 characters, any of the five supported countries |
| `country` | string | no | `GB`, `IE`, `NL`, `DE` or `FR`; narrows ambiguous addresses |
| `limit` | integer | no | 1 to 5 candidates, default 1 |

## Example

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
resp.raise_for_status()
best = resp.json()["results"][0]
```

```json
{
  "results": [
    {
      "formatted_address": "14 Wharf Road, London N1 7GR, United Kingdom",
      "lat": 51.5322,
      "lng": -0.0962,
      "precision": "rooftop",
      "confidence": 0.97,
      "country": "GB",
      "postcode": "N1 7GR"
    }
  ],
  "request_id": "req_7c1e93a0"
}
```

`precision` is one of `rooftop`, `street` or `locality`. Every field is described in
[Geocode response fields](geocode-response.md).

## Errors

| Status | `error.code` | When |
|---|---|---|
| 400 | `address_required` | `address` missing or blank |
| 400 | `invalid_request` | Body is not JSON, or `limit` is out of range |
| 404 | `no_match` | Nothing in the supported regions matches |
| 410 | `endpoint_retired` | You called `GET /v1/geocode` |
| 422 | `region_unsupported` | The address is outside the UK, Ireland, the Netherlands, Germany and France |
| 429 | `rate_limited` | Over 600 requests per minute; wait `Retry-After` seconds |

## Many addresses?

Sending addresses one at a time burns through the rate limit quickly. For more than a handful, use
[batch geocoding](geocode-batch.md), which takes up to 500 addresses per request.
