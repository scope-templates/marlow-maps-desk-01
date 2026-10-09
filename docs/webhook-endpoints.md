---
title: Webhook endpoints
updated: 2025-12-22
---

# Webhook endpoints

An endpoint is a URL plus the list of event types it wants. You can manage endpoints in the dashboard (**Settings**,
then **Webhooks**) or with the API below. Endpoints belong to a mode: one created with a `mm_test_` key only receives
test events.

## Create

```bash
curl -X POST https://api.marlowmaps.com/v2/webhooks \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://dispatch.example.com/marlow/webhooks", "events": ["route.recalculated", "route.recalculation_failed"]}'
```

```json
{
  "id": "we_31fb8a",
  "url": "https://dispatch.example.com/marlow/webhooks",
  "events": ["route.recalculated", "route.recalculation_failed"],
  "secret": "mmws_5b9e02f47c1d8a36e0b4",
  "enabled": true,
  "mode": "live"
}
```

The `secret` is only returned in this response and on rotation. Store it straight away.

## Rules

- `url` must be HTTPS on port 443 with a publicly valid certificate. Plain HTTP and IP addresses are refused with
  `400 invalid_webhook_url`.
- `events` must list at least one type, or `["*"]` for all of them.
- Up to 5 endpoints per account (2 on Starter); a sixth returns `409 webhook_limit_reached`.

## Update, list, delete

```python
import os
import requests

BASE = "https://api.marlowmaps.com/v2/webhooks"
H = {"X-Marlow-Key": os.environ["MARLOW_KEY"]}

requests.patch(f"{BASE}/we_31fb8a", headers=H, json={"events": ["*"]}, timeout=10)
endpoints = requests.get(BASE, headers=H, timeout=10).json()["data"]
requests.delete(f"{BASE}/we_31fb8a", headers=H, timeout=10)
```

Changing `events` applies to events created after the change; deliveries already queued still go out.

## Automatic disabling

If every delivery to an endpoint has failed for 3 days in a row, the endpoint is set to `"enabled": false` and the
account owner gets an email. Re-enable it with `PATCH` and `{"enabled": true}` once it is fixed; failed deliveries from
the last 14 days can then be replayed.

## Errors

| Status | `error.code` | When |
|---|---|---|
| 400 | `invalid_webhook_url` | Not HTTPS, not port 443, or not a public host |
| 400 | `invalid_request` | Unknown event type in `events` |
| 404 | `webhook_not_found` | Unknown endpoint id, or one from the other mode |
| 409 | `webhook_limit_reached` | Already at the endpoint limit |
