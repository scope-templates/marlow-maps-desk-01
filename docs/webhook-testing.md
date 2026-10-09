---
title: Testing webhooks
updated: 2025-10-14
---

# Testing webhooks

You do not need a real route and a traffic jam to exercise your receiver. Marlow can send synthetic events to any
endpoint, and test keys give you a safe place to try the full flow.

## Send a synthetic event

`POST /v2/webhooks/{id}/test` queues one event of the type you name, with a realistic but fake `data` body:

```bash
curl -X POST https://api.marlowmaps.com/v2/webhooks/we_31fb8a/test \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "route.recalculation_failed"}'
```

```python
import os
import requests

resp = requests.post(
    "https://api.marlowmaps.com/v2/webhooks/we_31fb8a/test",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"type": "route.recalculated"},
    timeout=10,
)
print(resp.json()["delivery_id"])
```

Test events are signed with the endpoint's real secret and carry `"test": true` at the top level. They follow the
normal retry schedule, so you can watch retries happen by returning `500` on purpose.

## Receiving on a laptop

Endpoints must be public HTTPS on port 443, so `localhost` cannot be registered. Use a tunnelling tool that gives you a
public HTTPS address forwarding to your local port, register that address with a test key, and remove the endpoint
when you are done so it does not count toward your limit of 5.

## Driving a real recalculation in test mode

1. Create a route with a `mm_test_` key and `"recalculate": true`.
2. Call `POST /v2/routes/{route_id}/recalculate`.
3. A `route.recalculated` event with `"reason": "manual"` arrives within a few seconds.

## Checklist before going live

- The receiver verifies `X-Marlow-Signature` against the raw body and rejects mismatches with `401`.
- It answers within 10 seconds, even when your queue is slow.
- It drops repeated `X-Marlow-Delivery` ids.
- It answers `2xx` to event types it does not handle.
- A separate live endpoint, with its own secret, is registered with a `mm_live_` key.

Errors from the test call itself: `404 webhook_not_found` for an unknown endpoint, `400 invalid_request` for an unknown
`type`, and `409 webhook_disabled` if the endpoint is disabled.
