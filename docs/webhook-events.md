---
title: Webhook events
updated: 2026-04-14
---

# Webhook events

Every event has the same envelope:

```json
{
  "id": "evt_5a0c19e2",
  "type": "route.recalculated",
  "created_at": "2026-04-02T08:21:40Z",
  "mode": "live",
  "data": {}
}
```

`id` is unique per event. If an event goes to two endpoints, both see the same `id` but each delivery has its own
`X-Marlow-Delivery` id.

## Event types

| Type | Sent when | `data` fields |
|---|---|---|
| `route.recalculated` | A watched route was recalculated | `route_id`, `version`, `reason`, `previous_duration_s`, `duration_s`, `stops` |
| `route.recalculation_failed` | A recalculation found no legal path | `route_id`, `version`, `reason`, `error_code` |
| `route.completed` | The last stop was marked arrived | `route_id`, `completed_at`, `distance_m`, `duration_s` |
| `route.expired` | 12 hours passed without completion | `route_id`, `expired_at` |
| `route.cancelled` | You cancelled the route | `route_id`, `cancelled_at` |

`route.recalculated` deliveries are retried 5 times over 30 minutes with backoff when your endpoint does not answer
with a 2xx; the other route events follow the same schedule.

## Subscribing to a subset

```bash
curl -X PATCH https://api.marlowmaps.com/v2/webhooks/we_31fb8a \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"events": ["route.recalculated", "route.completed"]}'
```

## Handling unknown types

New event types may be added within v2. Ignore types you do not recognise, but still answer `2xx`, otherwise the
delivery is retried for 30 minutes and counts toward automatic disabling:

```python
HANDLERS = {
    "route.recalculated": on_recalculated,
    "route.completed": on_completed,
}

def handle(event):
    handler = HANDLERS.get(event["type"])
    if handler:
        handler(event["data"])
```

## Ordering and duplicates

Events are delivered at least once and not necessarily in order. Two rules cover nearly every case:

1. Remember `X-Marlow-Delivery` ids for a day and drop repeats.
2. For route events, ignore any whose `data.version` is lower than the one you have stored.

Fetching a past event by id is possible for 14 days with `GET /v2/events/{event_id}`.
