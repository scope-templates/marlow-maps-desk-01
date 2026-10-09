---
title: Migrating from v1 geocoding
updated: 2025-09-09
---

# Migrating from v1 geocoding

`GET /v1/geocode` was retired on 2025-06-30. Since then it returns `410 endpoint_retired` for every request, live or
test. This page maps each v1 habit to its v2 equivalent.

## The request changed shape

v1 took the address as a query parameter:

```
GET /v1/geocode?address=14+Wharf+Road%2C+London
```

v2 takes a JSON body on a POST:

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address": "14 Wharf Road, London N1 7GR"}'
```

```python
import os
import requests

# before: requests.get(".../v1/geocode", params={"address": addr}, headers=h)
resp = requests.post(
    "https://api.marlowmaps.com/v2/geocode",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"address": addr},
    timeout=10,
)
```

The `X-Marlow-Key` header is unchanged; existing keys work with v2.

## What else changed

| v1 | v2 |
|---|---|
| `GET /v1/geocode?address=...` | `POST /v2/geocode` with `{"address": "..."}` |
| `GET /v1/reverse-geocode?lat=..&lng=..` | `POST /v2/reverse-geocode` with `{"lat": .., "lng": ..}` |
| `precision`: `exact` or `approx` | `precision`: `rooftop`, `street` or `locality` |
| Top-level `lat`/`lng` | `results` array, best match first |
| 404 with an empty body on no match | `404` with `error.code` `no_match` |
| Batch of 100 addresses | Batch of up to 500 addresses on `POST /v2/geocode/batch` |

## Checklist

1. Switch every call site to POST with a JSON body. `grep -rn "/v1/" .` finds them.
2. Read `results[0]` instead of the top-level object.
3. Replace comparisons against `exact` and `approx` with the three new `precision` values. See
   [Precision values](precision.md).
4. Raise your batch size to 500 if you group addresses.
5. Make your error handling read `error.code` from the body.

## Recognising the retirement error

```json
{
  "error": {
    "code": "endpoint_retired",
    "message": "GET /v1/geocode was retired on 2025-06-30. Use POST /v2/geocode.",
    "request_id": "req_91aa03fe"
  }
}
```

If you see this in production logs, the call site was missed. The error is permanent; retrying will not help.
