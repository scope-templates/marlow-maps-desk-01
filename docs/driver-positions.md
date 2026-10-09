---
title: Sending driver positions
updated: 2026-01-26
---

# Sending driver positions

For a route created with `"recalculate": true`, you can stream the driver's GPS position to Marlow. Positions let Marlow
spot when the driver has left the planned path and replan from where they actually are.

## Endpoint

```
POST https://api.marlowmaps.com/v2/routes/{route_id}/positions
```

The body holds one or more fixes, oldest first:

```json
{
  "positions": [
    {"lat": 51.5331, "lng": -0.0921, "at": "2026-04-02T08:10:04Z"},
    {"lat": 51.5338, "lng": -0.0897, "at": "2026-04-02T08:10:19Z"}
  ]
}
```

Up to 20 positions per request. Send them every 15 to 30 seconds while the driver is moving; one request per fix is
wasteful and eats into the 600 requests per minute that the whole key shares.

```bash
curl -X POST https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4/positions \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"positions": [{"lat": 51.5338, "lng": -0.0897, "at": "2026-04-02T08:10:19Z"}]}'
```

```python
import os
import requests

def send_fixes(route_id, fixes):
    resp = requests.post(
        f"https://api.marlowmaps.com/v2/routes/{route_id}/positions",
        headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
        json={"positions": fixes[-20:]},
        timeout=5,
    )
    return resp.json()["on_route"]
```

## Response

```json
{"accepted": 2, "on_route": true, "distance_from_route_m": 12}
```

When `distance_from_route_m` goes above 75 for the latest fix, `on_route` turns `false` and a recalculation starts. Your
webhook endpoint then receives `route.recalculated` with `"reason": "driver_off_route"`.

## Errors

| Status | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | More than 20 positions, or a fix without `at` |
| 404 | `route_not_found` | Unknown route, or a route from the other key mode |
| 409 | `route_not_active` | Route completed or past its 12-hour window |
| 409 | `recalculation_disabled` | Route was created without `"recalculate": true` |

Positions older than ten minutes are accepted but ignored for the off-route check.

## Privacy

Positions are used for recalculation and kept for 24 hours, then deleted. They are not shown in the dashboard.
