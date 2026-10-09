---
title: Authentication
updated: 2026-02-18
---

# Authentication

Every request to `https://api.marlowmaps.com` must carry an API key in the `X-Marlow-Key` header:

```
X-Marlow-Key: <key>
```

The key is the whole value. There is no `Bearer` prefix, no query-string parameter and no basic auth. A key sent any
other way is ignored and the request fails as if no key were present.

## Example

```bash
curl -X POST https://api.marlowmaps.com/v2/reverse-geocode \
  -H "X-Marlow-Key: mm_live_9d31f0a7c2e84b16" \
  -H "Content-Type: application/json" \
  -d '{"lat": 53.3105, "lng": -6.3622}'
```

```python
import requests

resp = requests.post(
    "https://api.marlowmaps.com/v2/reverse-geocode",
    headers={"X-Marlow-Key": "mm_live_9d31f0a7c2e84b16"},
    json={"lat": 53.3105, "lng": -6.3622},
    timeout=10,
)
```

In real code load the key from an environment variable or a secrets manager; never commit it.

## Live and test keys

Keys start `mm_live_` or `mm_test_`. Both authenticate the same way and see the same address data. Test keys are not
billed and their webhooks are signed with the test endpoint's secret. See [Test and live keys](test-and-live-keys.md).

## Failures

| Status | `error.code` | Cause |
|---|---|---|
| 401 | `missing_key` | No `X-Marlow-Key` header on the request |
| 401 | `invalid_key` | The value is not a key we recognise (often a stray space or a truncated paste) |
| 403 | `key_revoked` | The key was revoked in the dashboard |

A failed authentication still counts toward the key's 600 requests per minute if the key itself is valid, so a
revoked key in a retry loop can push a busy integration into `429` as well.

## Browser and mobile apps

Do not embed a key in a browser bundle or a mobile binary. Proxy calls through your own backend, which adds the
header. Keys cannot be scoped to a domain or an app id, so anyone holding a key can spend your quota.

Creating, naming and revoking keys is covered in [API keys](api-keys.md).
