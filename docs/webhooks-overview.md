---
title: Webhooks overview
updated: 2026-06-30
---

# Webhooks overview

Marlow Maps sends webhooks when something happens to a route that your app did not directly cause: traffic changed the
ETA, a driver went off route, a route expired. Each webhook is an HTTPS `POST` of a JSON event to an endpoint you
register.

## The moving parts

1. **Endpoint.** A URL on your server, registered with `POST /v2/webhooks` or in the dashboard under
   **Settings**, then **Webhooks**. Each endpoint has its own signing secret. See [Webhook endpoints](webhook-endpoints.md).
2. **Event.** A JSON body with `id`, `type`, `created_at`, `mode` and `data`. The types are listed in
   [Webhook events](webhook-events.md).
3. **Delivery.** One attempt to send one event to one endpoint. Deliveries carry four headers:

| Header | Example | Purpose |
|---|---|---|
| `X-Marlow-Signature` | `9f2c...e1` | HMAC-SHA256 of the raw body, hex; see [Webhook signatures](webhook-signatures.md) |
| `X-Marlow-Event` | `route.recalculated` | The event type, so you can route before parsing |
| `X-Marlow-Delivery` | `dlv_2207ab` | Unique per event and endpoint; the same on every retry |
| `X-Marlow-Attempt` | `1` | 1 for the first try, up to 6 |

## A minimal receiver

```python
from flask import Flask, request, abort
import hashlib
import hmac
import os

app = Flask(__name__)
SECRET = os.environ["MARLOW_WEBHOOK_SECRET"].encode()

@app.post("/marlow/webhooks")
def receive():
    expected = hmac.new(SECRET, request.get_data(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, request.headers.get("X-Marlow-Signature", "")):
        abort(401)
    enqueue(request.get_json())
    return "", 204
```

Answer with any 2xx within 10 seconds and do the real work afterwards. Slow or failing answers are retried; the
schedule for route recalculation events is 5 retries over 30 minutes with backoff, described in
[Route recalculation webhooks](route-recalculation-webhooks.md).

## Sending yourself a test event

```bash
curl -X POST https://api.marlowmaps.com/v2/webhooks/we_31fb8a/test \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type": "route.recalculated"}'
```

More on local testing in [Testing webhooks](webhook-testing.md).

## Limits

Up to 5 endpoints per account (2 on Starter). Payloads are at most 64 KB. Events are delivered at least once and may
arrive out of order; use `X-Marlow-Delivery` to drop duplicates and `data.version` to ignore stale route updates.
