---
title: Routes
updated: 2026-07-02
---

# Routes

`POST /v2/routes` plans a route through an ordered list of stops and returns distance, duration, per-leg detail and a
polyline for drawing it. The stop order you send is the order driven; to have Marlow choose the order, call
[`POST /v2/optimize`](optimize.md) first.

## Request

| Field | Type | Required | Notes |
|---|---|---|---|
| `profile` | string | yes | `car`, `van`, `bicycle` or `walk`; see [Route profiles](route-profiles.md) |
| `stops` | array | yes | 2 to 100 stops; each is `{"lat", "lng"}` or `{"address"}` |
| `depart_at` | string | no | ISO 8601 time; defaults to now |
| `recalculate` | boolean | no | Watch the route for traffic and send webhooks; default `false` |
| `vehicle` | object | no | Van dimensions; see [Vehicle restrictions](vehicle-restrictions.md) |

Stops given as `address` are geocoded for you and count toward your geocode quota.

```bash
curl -X POST https://api.marlowmaps.com/v2/routes \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "van",
    "recalculate": true,
    "stops": [
      {"lat": 51.5322, "lng": -0.0962},
      {"address": "221 Kingsland Road, London E2 8AN"},
      {"lat": 51.5450, "lng": -0.0553}
    ]
  }'
```

```python
import os
import requests

route = requests.post(
    "https://api.marlowmaps.com/v2/routes",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"profile": "van", "recalculate": True, "stops": stops},
    timeout=15,
).json()
```

## Response

```json
{
  "route_id": "rte_9Kx2mQ4",
  "status": "active",
  "profile": "van",
  "distance_m": 8420,
  "duration_s": 1710,
  "legs": [
    {"from": 0, "to": 1, "distance_m": 3105, "duration_s": 640},
    {"from": 1, "to": 2, "distance_m": 5315, "duration_s": 1070}
  ],
  "polyline": "_p~iF~ps|U_ulLnnqC_mqNvxq`@",
  "recalculate": true,
  "created_at": "2026-04-02T07:58:11Z"
}
```

Fetch it again later with `GET /v2/routes/rte_9Kx2mQ4`. Routes made with live keys are kept 30 days, with test keys
7 days.

## Errors

| Status | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | Fewer than 2 stops, unknown `profile`, bad coordinates |
| 404 | `no_match` | An `address` stop could not be geocoded; `message` names its position |
| 422 | `too_many_stops` | More than 100 stops |
| 422 | `region_unsupported` | A stop or the path between stops leaves the supported regions |
| 422 | `no_route` | No legal path for this profile, for example a bridge too low for the van |
| 429 | `rate_limited` | Over 600 requests per minute |

When `recalculate` is `true`, Marlow keeps the route current for 12 hours and tells you about changes through
[route recalculation webhooks](route-recalculation-webhooks.md).
