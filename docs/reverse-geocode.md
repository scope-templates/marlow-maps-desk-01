---
title: Reverse geocoding
updated: 2025-11-25
---

# Reverse geocoding

`POST /v2/reverse-geocode` goes the other way: you send coordinates and get back the nearest address. Driver apps use it
to show "you are at 4 Ballymount Road" on proof-of-delivery screens, and field-service apps use it to label a
technician's check-in.

## Request

| Field | Type | Required | Notes |
|---|---|---|---|
| `lat` | number | yes | WGS84 latitude, -90 to 90 |
| `lng` | number | yes | WGS84 longitude, -180 to 180 |
| `radius_m` | integer | no | How far to look, 10 to 500 metres, default 100 |

```bash
curl -X POST https://api.marlowmaps.com/v2/reverse-geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"lat": 53.3105, "lng": -6.3622}'
```

```python
import os
import requests

resp = requests.post(
    "https://api.marlowmaps.com/v2/reverse-geocode",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"lat": 53.3105, "lng": -6.3622, "radius_m": 50},
    timeout=10,
)
place = resp.json()["result"]
print(place["formatted_address"], place["distance_m"])
```

## Response

```json
{
  "result": {
    "formatted_address": "Unit 4, Ballymount Industrial Estate, Dublin 12, D12 X2F7, Ireland",
    "lat": 53.3106,
    "lng": -6.3620,
    "precision": "street",
    "distance_m": 18,
    "country": "IE",
    "postcode": "D12 X2F7"
  },
  "request_id": "req_0e4b88d2"
}
```

Reverse geocodes use the same `precision` values as forward geocodes. A `rooftop` result means a building was found
inside the radius; `street` means the nearest match is a street segment; `locality` means only a town or district was
within reach.

## Errors and limits

| Status | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | `lat` or `lng` missing or out of range |
| 404 | `no_match` | Nothing within `radius_m` |
| 422 | `region_unsupported` | The point is outside the five supported countries |
| 429 | `rate_limited` | Over 600 requests per minute |

Each reverse geocode counts as one geocode toward your monthly quota. There is no batch reverse endpoint; if you need
to label a whole GPS trace, sample one point every 30 seconds or so rather than every fix.

The retired `GET /v1/reverse-geocode` endpoint returns `410 endpoint_retired` since 2025-06-30.
