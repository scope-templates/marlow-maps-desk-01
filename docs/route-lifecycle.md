---
title: Route lifecycle
updated: 2026-03-23
---

# Route lifecycle

Every route has a `status` that moves in one direction:

```
active  ->  completed
active  ->  expired
active  ->  cancelled
```

| Status | Meaning | Recalculates? |
|---|---|---|
| `active` | Planned and, if `recalculate` is on, watched | Yes |
| `completed` | The last stop was marked arrived | No |
| `expired` | 12 hours passed since `depart_at` without completion | No |
| `cancelled` | You cancelled it | No |

Recalculation, positions and stop changes are only accepted while the route is `active`. Afterwards they fail with
`409 route_not_active`.

## Cancelling

```bash
curl -X POST https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4/cancel \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

requests.post(
    "https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4/cancel",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
).raise_for_status()
```

Cancel routes that will not be driven. An `active` route with recalculation on keeps generating `route.recalculated`
webhooks for up to 12 hours, which is noise for your endpoint and for your logs.

## Listing routes

`GET /v2/routes` lists routes newest first, filtered by `status` if you pass it:

```bash
curl "https://api.marlowmaps.com/v2/routes?status=active&limit=50" \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

The list uses `limit` (up to 100) and `cursor`, as described in [Pagination](pagination.md).

## Retention

Routes created with live keys are kept for 30 days after creation, test routes for 7 days. After that
`GET /v2/routes/{route_id}` returns `404 route_not_found`. If you need routes for longer, for proof of delivery or
disputes, copy the response into your own storage when the route completes; the `route.completed` webhook is a good
moment to do it.

## Events

Each status change sends a webhook to subscribed endpoints: `route.completed`, `route.expired` and `route.cancelled`.
Recalculations while `active` send `route.recalculated`. The full list is in [Webhook events](webhook-events.md).
