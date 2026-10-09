---
title: ETAs
updated: 2026-06-15
---

# ETAs

Every route response includes an `eta` for each stop, computed from `depart_at` (or the creation time), the leg
durations and any `service_s` you set. For routes created with `"recalculate": true`, ETAs move as the route is
recalculated.

## Reading ETAs from a route

```bash
curl https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4 \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

route = requests.get(
    "https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
).json()

for stop in route["stops"]:
    print(stop["position"], stop["eta"], stop["status"])
```

```json
{
  "route_id": "rte_9Kx2mQ4",
  "version": 3,
  "stops": [
    {"position": 0, "eta": "2026-04-02T07:58:11Z", "status": "departed"},
    {"position": 1, "eta": "2026-04-02T08:11:02Z", "status": "arrived"},
    {"position": 2, "eta": "2026-04-02T08:34:47Z", "status": "pending"}
  ]
}
```

ETAs are in UTC. Convert to local time in your app; Marlow does not localise them.

## Marking stops as done

When your driver app records an arrival, tell Marlow so later ETAs start from the real time rather than the plan:

```bash
curl -X POST https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4/stops/1/arrive \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

Arriving at the last stop marks the route `completed` and stops recalculation.

## How ETAs reach customers

The usual pattern is to store the latest ETA per stop and push it to the recipient's tracking page. Do not poll the
route to keep it fresh; subscribe to `route.recalculated` instead, which carries every stop's new `eta` in its
payload. See [Route recalculation webhooks](route-recalculation-webhooks.md).

## Accuracy

On `car` and `van` routes in cities, 80% of arrivals land within five minutes of the ETA given an hour earlier,
provided positions are sent. Without positions, accuracy falls after the first missed stop because Marlow cannot know
the driver is late.

Each `GET /v2/routes/{route_id}` counts toward the 600 requests per minute limit but not the monthly route quota.
