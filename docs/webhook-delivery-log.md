---
title: Webhook delivery log
updated: 2026-06-02
---

# Webhook delivery log

Every delivery attempt is recorded for 14 days: the request headers and body Marlow sent, your status code, the first
2 KB of your response body, and how long you took. The log is the first place to look when an endpoint "never got"
an event.

## In the dashboard

**Settings**, then **Webhooks**, then choose an endpoint. Each row is one delivery, with its attempts nested under it.
Filter by status (`succeeded`, `retrying`, `failed`) or by event type.

## Through the API

```bash
curl "https://api.marlowmaps.com/v2/webhooks/we_31fb8a/deliveries?status=failed&limit=20" \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

resp = requests.get(
    "https://api.marlowmaps.com/v2/webhooks/we_31fb8a/deliveries",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    params={"status": "failed", "limit": 20},
    timeout=10,
)
for d in resp.json()["data"]:
    last = d["attempts"][-1]
    print(d["id"], d["event_type"], last["status_code"], last["duration_ms"])
```

```json
{
  "data": [
    {
      "id": "dlv_2207ab",
      "event_id": "evt_5a0c19e2",
      "event_type": "route.recalculated",
      "status": "failed",
      "attempts": [
        {"attempt": 1, "status_code": 502, "duration_ms": 311},
        {"attempt": 6, "status_code": null, "error": "timeout", "duration_ms": 10000}
      ]
    }
  ],
  "next_cursor": null
}
```

The example is trimmed; a failed delivery has all six attempts listed, since route events are retried 5 times over 30
minutes after the original attempt.

## Replay

Any delivery in the log can be replayed with `POST /v2/webhooks/deliveries/{delivery_id}/replay`, whatever its
status. A replay is a new delivery with a new id, the original body, and a fresh retry schedule. Up to 100 replays per
endpoint per hour.

## Reading common failures

| What the log shows | Usual cause |
|---|---|
| `status_code: 401` on every attempt | Wrong signing secret, or the body was re-serialised before verification |
| `error: timeout` | Your handler does the work before answering; queue it and answer first |
| `error: tls_handshake` | Expired or self-signed certificate |
| `status_code: 404` | The URL path changed in a deploy |
