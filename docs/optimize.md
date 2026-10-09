---
title: Stop order optimisation
updated: 2026-04-20
---

# Stop order optimisation

`POST /v2/optimize` takes a start point, an optional end point and up to 100 stops, and returns the order that
minimises total driving time. It does not create a route; pass the ordered stops to `POST /v2/routes` afterwards.

## Request

```json
{
  "profile": "van",
  "start": {"lat": 52.3600, "lng": 4.9000},
  "end": {"lat": 52.3600, "lng": 4.9000},
  "stops": [
    {"id": "drop-1", "lat": 52.3745, "lng": 4.8844, "window": ["09:00", "11:00"]},
    {"id": "drop-2", "lat": 52.3512, "lng": 4.8661, "service_s": 300},
    {"id": "drop-3", "address": "Keizersgracht 221, 1016 DV Amsterdam"}
  ]
}
```

| Stop field | Notes |
|---|---|
| `id` | Your reference, returned in the answer |
| `window` | Optional local-time arrival window |
| `service_s` | Optional time spent at the stop, default 120 seconds |

```bash
curl -X POST https://api.marlowmaps.com/v2/optimize \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d @day-plan.json
```

```python
import os
import requests

plan = requests.post(
    "https://api.marlowmaps.com/v2/optimize",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json=day_plan,
    timeout=60,
).json()

ordered = [stops_by_id[i] for i in plan["order"]]
```

## Response

```json
{
  "order": ["drop-2", "drop-3", "drop-1"],
  "duration_s": 3920,
  "distance_m": 14210,
  "late_stops": [],
  "request_id": "req_6d0f3a12"
}
```

`late_stops` lists stops whose window cannot be met by any order. They are still placed in `order`, as early as
possible.

## Limits and errors

| Status | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | Missing `start`, malformed `window` |
| 422 | `too_many_stops` | More than 100 stops |
| 422 | `region_unsupported` | A point outside the five supported countries |
| 429 | `rate_limited` | Over 600 requests per minute |

Optimisation of 100 stops can take up to 40 seconds, so set a generous client timeout. Each call counts as one route
toward your monthly quota.
