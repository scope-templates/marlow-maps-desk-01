---
title: Distance matrix
updated: 2025-12-09
---

# Distance matrix

`POST /v2/matrix` returns travel time and distance between every origin and every destination you send. Dispatch
systems use it to answer "which driver is closest to this job?" without planning a full route for each pair.

## Limits

- Up to 25 origins and 25 destinations, so at most 625 cells.
- One matrix counts as one request against the 600 requests per minute limit and as one route against your monthly
  route quota.
- `profile` is required and takes the same four values as routes: `car`, `van`, `bicycle`, `walk`.

Larger requests fail with `422 matrix_too_large`.

## Example

```bash
curl -X POST https://api.marlowmaps.com/v2/matrix \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "van",
    "origins": [{"lat": 53.3498, "lng": -6.2603}, {"lat": 53.2707, "lng": -6.2050}],
    "destinations": [{"lat": 53.3105, "lng": -6.3622}]
  }'
```

```python
import os
import requests

drivers = [{"lat": 53.3498, "lng": -6.2603}, {"lat": 53.2707, "lng": -6.2050}]
job = [{"lat": 53.3105, "lng": -6.3622}]

m = requests.post(
    "https://api.marlowmaps.com/v2/matrix",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"profile": "van", "origins": drivers, "destinations": job},
    timeout=20,
).json()

closest = min(range(len(drivers)), key=lambda i: m["durations_s"][i][0])
```

## Response

```json
{
  "durations_s": [[1140], [1385]],
  "distances_m": [[9870], [11420]],
  "request_id": "req_44e1b9c0"
}
```

`durations_s[i][j]` is the time from origin `i` to destination `j`. A cell with no legal path is `null` rather than an
error, so one unreachable pair does not spoil the rest.

## Things to know

Matrices use traffic for `car` and `van`, based on `depart_at` if you send it and the current time if you do not.
Matrices are not stored and cannot be recalculated or watched; call again when you need fresh numbers. If any point
lies outside the UK, Ireland, the Netherlands, Germany or France, the whole request fails with
`422 region_unsupported`.
