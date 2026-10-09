---
title: Rate limits
updated: 2026-07-21
---

# Rate limits

The limit is **600 requests per minute per key**. It applies to the key, not to the account or IP, and it covers every
endpoint together: geocodes, batches, routes, matrices, webhook management and account calls all draw from the same
600.

A batch geocode of 500 addresses is one request. That makes `POST /v2/geocode/batch` the right tool for bulk work;
the per-address cost shows up in your monthly quota instead (see [Plans and monthly quotas](plans-and-quotas.md)).

## Headers on every response

| Header | Example | Meaning |
|---|---|---|
| `X-RateLimit-Limit` | `600` | Requests allowed per minute for this key |
| `X-RateLimit-Remaining` | `412` | Requests left in the current window |
| `X-RateLimit-Reset` | `1775117460` | Unix time when the window resets |

The window is a sliding minute, so `Remaining` recovers gradually rather than all at once.

## When you go over

The API answers `429 Too Many Requests`, and the 429 carries `Retry-After` with the number of seconds to wait:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 7
X-RateLimit-Limit: 600
X-RateLimit-Remaining: 0

{"error": {"code": "rate_limited", "message": "600 requests per minute exceeded for this key.", "request_id": "req_c09d2e44"}}
```

```python
import time
import requests

def post_with_limit(session, url, payload):
    while True:
        resp = session.post(url, json=payload, timeout=15)
        if resp.status_code != 429:
            return resp
        time.sleep(int(resp.headers.get("Retry-After", "1")))
```

```bash
curl -s -o /dev/null -D - -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" -H "Content-Type: application/json" \
  -d '{"address": "Torstraße 109, 10119 Berlin"}' | grep -i -E "ratelimit|retry-after"
```

Requests rejected with 429 do not count toward the limit, so waiting the full `Retry-After` is enough; there is no
penalty window.

## Other limits

| Limit | Value | Error |
|---|---|---|
| Addresses per batch | 500 | `413 batch_too_large` |
| Stops per route or optimisation | 100 | `422 too_many_stops` |
| Matrix size | 25 × 25 | `422 matrix_too_large` |
| Manual recalculations | 1 per route per 30 s | `429 recalculation_too_frequent` |
| Positions per request | 20 | `400 invalid_request` |

The 600 per minute limit is the same for live and test keys and on every plan. If you need more throughput, spread
independent services across separate keys rather than asking for a higher limit on one.
