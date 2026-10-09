---
title: Route profiles
updated: 2025-11-10
---

# Route profiles

The `profile` field on `POST /v2/routes`, `POST /v2/matrix` and `POST /v2/optimize` chooses which roads may be used and
how fast the traveller moves. There are four.

| Profile | Uses | Speeds from | Notes |
|---|---|---|---|
| `car` | All public roads | Live and historic traffic | Avoids roads closed to cars, such as bus gates |
| `van` | Roads open to vans up to 3.5 t | Live and historic traffic, van speed caps | Honours `vehicle` height and weight |
| `bicycle` | Cycle lanes, quiet streets, permitted paths | Fixed 16 km/h, slower uphill | Added 2025-11-10 |
| `walk` | Pavements, footpaths, pedestrian zones | Fixed 4.8 km/h | Ignores one-way streets |

Only `car` and `van` routes use traffic, and only they can be recalculated for traffic. `bicycle` and `walk` routes
accept `"recalculate": true` but only recalculate when a stop is added or removed.

## Choosing between car and van

For couriers in small vans, `van` gives more realistic ETAs in city centres: it keeps out of car-only zones and applies
the lower speed limits for goods vehicles in France and Germany. On a typical London route the difference is a few
minutes per hour of driving.

```bash
curl -X POST https://api.marlowmaps.com/v2/routes \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"profile": "bicycle", "stops": [{"lat": 52.3745, "lng": 4.8844}, {"lat": 52.3600, "lng": 4.8852}]}'
```

```python
import os
import requests

def compare(stops):
    out = {}
    for profile in ("car", "van", "bicycle"):
        r = requests.post(
            "https://api.marlowmaps.com/v2/routes",
            headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
            json={"profile": profile, "stops": stops},
            timeout=15,
        ).json()
        out[profile] = r["duration_s"]
    return out
```

## Errors

An unknown profile returns `400 invalid_request` with `message` listing the four valid values. A profile that has no
legal path between two stops (a `car` route into a pedestrian-only street, for example) returns `422 no_route`.

Every profile counts the same toward the rate limit and the monthly route quota.
