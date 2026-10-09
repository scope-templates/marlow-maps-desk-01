---
title: Test and live keys
updated: 2025-10-21
---

# Test and live keys

Marlow Maps has two kinds of key and no separate sandbox host. Both talk to `https://api.marlowmaps.com`; the prefix of
the key decides the mode.

| | `mm_test_` keys | `mm_live_` keys |
|---|---|---|
| Billing | Free | Counted against your plan |
| Address data | Same as live | Same as test |
| Rate limit | 600 requests per minute per key | 600 requests per minute per key |
| Routes | Kept 7 days | Kept 30 days |
| Webhooks | Sent to endpoints created in test mode | Sent to endpoints created in live mode |

Because the data is the same, a geocode made with a test key returns the same coordinates and `precision` as one made
with a live key. That makes test keys suitable for CI suites that assert on real results.

## Telling the modes apart in code

`GET /v2/account` reports the mode as `key.mode`, and every response carries an `X-Marlow-Mode` header set to `test`
or `live`:

```bash
curl -si -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address": "Torstraße 109, 10119 Berlin"}' | grep -i x-marlow-mode
```

```python
resp = session.post(f"{BASE}/v2/geocode", json={"address": "Torstraße 109, 10119 Berlin"}, timeout=10)
assert resp.headers["X-Marlow-Mode"] == "test", "CI must never run with a live key"
```

## Objects do not cross modes

A route created with a test key cannot be read or recalculated with a live key, and the reverse. The API answers
`404 route_not_found` rather than revealing that the route exists in the other mode. Webhook endpoints are also
per mode: register your staging receiver with a test key and your production receiver with a live key.

## Common mistakes

- **A test key in production.** Everything works, nothing is billed, and routes vanish after 7 days. Check the
  `X-Marlow-Mode` header in your health check.
- **Mixing keys between services.** A dispatch service using a live key and a driver app using a test key will see
  `route_not_found` for each other's routes.
