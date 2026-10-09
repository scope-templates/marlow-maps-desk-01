---
title: Vehicle restrictions
updated: 2026-01-07
---

# Vehicle restrictions

Vans meet low bridges, weight limits and narrow lanes that cars never notice. The `van` profile avoids them when you
tell it how big the vehicle is.

## The `vehicle` object

| Field | Type | Range | Default |
|---|---|---|---|
| `height_cm` | integer | 150 to 400 | 260 |
| `weight_kg` | integer | 1,000 to 3,500 | 3,500 |
| `width_cm` | integer | 150 to 255 | 220 |
| `avoid` | array | `tolls`, `ferries`, `low_emission_zones` | `[]` |

Only the `van` profile reads `height_cm`, `weight_kg` and `width_cm`. `avoid` works with `car` and `van`.

```bash
curl -X POST https://api.marlowmaps.com/v2/routes \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": "van",
    "vehicle": {"height_cm": 290, "weight_kg": 3500, "avoid": ["low_emission_zones"]},
    "stops": [{"lat": 48.8566, "lng": 2.3522}, {"lat": 48.9362, "lng": 2.3574}]
  }'
```

```python
import os
import requests

LUTON_VAN = {"height_cm": 290, "weight_kg": 3500, "width_cm": 230}

resp = requests.post(
    "https://api.marlowmaps.com/v2/routes",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"profile": "van", "vehicle": LUTON_VAN, "stops": stops},
    timeout=15,
)
if resp.status_code == 422 and resp.json()["error"]["code"] == "no_route":
    flag_for_dispatcher(stops)
```

## Low emission zones

With `low_emission_zones` in `avoid`, the route stays out of the London ULEZ, Dutch milieuzones, German Umweltzonen and
French ZFE areas. If a stop is inside a zone, the route enters it by the shortest path and the response sets
`"enters_restricted_zone": true` on that leg rather than failing.

## Errors

| Status | `error.code` | When |
|---|---|---|
| 400 | `invalid_request` | A dimension out of range, or `vehicle` sent with `bicycle` or `walk` |
| 422 | `no_route` | No path respects the dimensions, for example every way in passes under a 2.7 m bridge |

Vehicle restrictions do not change the rate limit or quota cost of a route. Matrices and optimisation accept the same
`vehicle` object.
