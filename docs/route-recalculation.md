---
title: Route recalculation
updated: 2026-05-06
---

# Route recalculation

A route planned at 07:00 is often wrong by 08:30. Marlow can keep a route current for you: when traffic changes, when a
driver leaves the planned path, or when you change the stops. Each time the route is recalculated, your webhook
endpoint receives a `route.recalculated` event with the new duration and ETAs.

## Turning it on

Create the route with `"recalculate": true`. Marlow then watches it for 12 hours from `depart_at` (or creation). After
that window, or once the route is marked complete, it stops.

## What triggers a recalculation

| `reason` in the webhook | Trigger |
|---|---|
| `traffic` | Live traffic changes the remaining duration by more than 3 minutes or 10% |
| `driver_off_route` | A position sent to `/positions` is more than 75 metres from the planned path |
| `stop_added` / `stop_removed` | You changed the stop list with `PATCH /v2/routes/{route_id}` |
| `manual` | You called `POST /v2/routes/{route_id}/recalculate` |

## Forcing a recalculation

```bash
curl -X POST https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4/recalculate \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

resp = requests.post(
    "https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4/recalculate",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=15,
)
print(resp.status_code)  # 202
```

The call returns `202 Accepted` straight away. The new route arrives through the webhook, normally within five seconds;
`GET /v2/routes/rte_9Kx2mQ4` also shows it once it is ready.

## Limits

- One manual recalculation per route every 30 seconds. Faster calls get `429 recalculation_too_frequent` with a
  `Retry-After` header; this is separate from the 600 requests per minute key limit.
- Recalculation is available for routes with up to 100 stops, like every route.
- A completed or expired route returns `409 route_not_active`.

## Without webhooks

If you cannot receive webhooks, poll `GET /v2/routes/{route_id}` and compare `version`, which increases by one on every
recalculation. Polling every 60 seconds is plenty; the webhook is still the better choice because it arrives as soon as
the change is known and is retried if your server is down. Delivery rules are on
[route recalculation webhooks](route-recalculation-webhooks.md).
