---
title: Geocode response fields
updated: 2025-12-15
---

# Geocode response fields

This page is the reference for the objects returned by `POST /v2/geocode`, each `ok` item of
`POST /v2/geocode/batch` and `POST /v2/reverse-geocode`.

## Result object

| Field | Type | Always present | Description |
|---|---|---|---|
| `formatted_address` | string | yes | The matched address, written the way the local postal service writes it |
| `lat` | number | yes | Latitude, WGS84, five decimal places at most |
| `lng` | number | yes | Longitude, WGS84 |
| `precision` | string | yes | `rooftop`, `street` or `locality` |
| `confidence` | number | yes | 0 to 1; how certain the match is |
| `country` | string | yes | `GB`, `IE`, `NL`, `DE` or `FR` |
| `postcode` | string | no | Omitted for `locality` results without a single postcode |
| `components` | object | yes | `house_number`, `street`, `locality`, `postcode`, `country`; missing parts are `null` |
| `distance_m` | integer | reverse only | Metres from the point you sent |

## Envelope

Single geocodes return `results` (an array, length 1 to `limit`) and `request_id`. Batches return `results`, `counts`
and `request_id`. Reverse geocodes return a single `result`.

```json
{
  "results": [
    {
      "formatted_address": "Torstraße 109, 10119 Berlin, Germany",
      "lat": 52.529,
      "lng": 13.401,
      "precision": "rooftop",
      "confidence": 0.94,
      "country": "DE",
      "postcode": "10119",
      "components": {
        "house_number": "109",
        "street": "Torstraße",
        "locality": "Berlin",
        "postcode": "10119",
        "country": "DE"
      }
    }
  ],
  "request_id": "req_b2c40f19"
}
```

## Reading the components

```python
import os
import requests

r = requests.post(
    "https://api.marlowmaps.com/v2/geocode",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"address": "Torstraße 109, 10119 Berlin", "limit": 3},
    timeout=10,
).json()

for candidate in r["results"]:
    c = candidate["components"]
    print(c["street"], c["house_number"], candidate["precision"], candidate["confidence"])
```

```bash
curl -s -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" -H "Content-Type: application/json" \
  -d '{"address": "Torstraße 109, 10119 Berlin", "limit": 3}' | jq '.results[].components'
```

## Stability

Fields are only added, never renamed, within v2. Your parser should ignore fields it does not know. `request_id` is
also sent as the `X-Request-Id` response header; quote it when you contact us about a result.
