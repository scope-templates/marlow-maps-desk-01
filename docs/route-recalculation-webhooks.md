---
title: Route recalculation webhooks
updated: 2026-06-30
---

# Route recalculation webhooks

When a route created with `"recalculate": true` changes, Marlow sends a `route.recalculated` event to every endpoint
subscribed to it. If the recalculation itself fails, for example because a road closure leaves no legal path, the event
is `route.recalculation_failed`.

## Payload

```json
{
  "id": "evt_5a0c19e2",
  "type": "route.recalculated",
  "created_at": "2026-04-02T08:21:40Z",
  "mode": "live",
  "data": {
    "route_id": "rte_9Kx2mQ4",
    "version": 3,
    "reason": "traffic",
    "previous_duration_s": 1710,
    "duration_s": 2035,
    "stops": [
      {"position": 1, "eta": "2026-04-02T08:16:30Z"},
      {"position": 2, "eta": "2026-04-02T08:40:12Z"}
    ]
  }
}
```

`reason` is one of `traffic`, `driver_off_route`, `stop_added`, `stop_removed` or `manual`.

## Signature

Every delivery is signed. The `X-Marlow-Signature` header holds the HMAC-SHA256 of the raw body, keyed with the
endpoint's signing secret, as lowercase hex. Verify it against the bytes you received, before any JSON parsing:

```python
import hashlib
import hmac

def is_from_marlow(raw_body: bytes, signature: str, secret: str) -> bool:
    expected = hmac.new(secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)
```

Details and other languages are on [Webhook signatures](webhook-signatures.md).

## Delivery and retries

Your endpoint must answer with a 2xx status within 10 seconds. Anything else (a 4xx, a 5xx, a timeout, a refused
connection) counts as a failure, and the delivery is retried 5 times over 30 minutes with backoff:

| Attempt | Sent after the first attempt |
|---|---|
| 1 (original) | immediately |
| 2 | 1 minute |
| 3 | 3 minutes |
| 4 | 8 minutes |
| 5 | 15 minutes |
| 6 | 30 minutes |

After the sixth attempt fails, the delivery is marked `failed`. You can replay it from the delivery log for 14 days;
see [Webhook delivery log](webhook-delivery-log.md). Retries reuse the same `X-Marlow-Delivery` id and the same body,
and `X-Marlow-Attempt` counts up from 1 to 6.

A newer recalculation does not cancel retries of an older one. If attempt 4 of version 2 arrives after attempt 1 of
version 3, keep the higher `data.version`.

## Replaying by hand

```bash
curl -X POST https://api.marlowmaps.com/v2/webhooks/deliveries/dlv_2207ab/replay \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

requests.post(
    "https://api.marlowmaps.com/v2/webhooks/deliveries/dlv_2207ab/replay",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
).raise_for_status()
```

A replay is a fresh delivery with `X-Marlow-Attempt: 1` and its own retry schedule.
