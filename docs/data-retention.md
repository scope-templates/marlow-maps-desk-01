---
title: Data retention
updated: 2026-04-28
---

# Data retention

This page lists what Marlow Maps keeps from your API traffic, and for how long. Everything is stored in the EU.

| Data | Kept for | Notes |
|---|---|---|
| Geocode request logs (address, result, request id) | 30 days | Used for debugging and abuse prevention |
| Routes created with live keys | 30 days | Then `GET /v2/routes/{id}` returns `404 route_not_found` |
| Routes created with test keys | 7 days | |
| Driver positions | 24 hours | Used only for off-route detection |
| Webhook events (`GET /v2/events/{id}`) | 14 days | |
| Webhook delivery log | 14 days | Includes the first 2 KB of your responses |
| Account usage counts | 25 months | Needed for billing disputes |

Batch geocode inputs are treated like single geocodes and logged for 30 days.

## Deleting data early

You can delete a route and its positions before the retention period ends:

```bash
curl -X DELETE https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4 \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

resp = requests.delete(
    "https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
)
assert resp.status_code == 204
```

Deleting an `active` route also stops its recalculation; no `route.cancelled` event is sent for deletions. A deleted
route returns `404 route_not_found` immediately.

To have geocode logs for specific addresses erased, for example after a data subject request, email
privacy@marlowmaps.com with the request ids or the addresses. Erasure is completed within 30 days, which is also the
point at which logs would expire anyway.

## What we do not keep

- We do not keep the response bodies your webhook endpoint returns beyond the first 2 KB, nor anything beyond 14 days.
- We do not keep the content of `ref` values from batch requests after the response is sent.
- We do not build profiles of recipients from the addresses you send.

Your own copies of results are governed by [Storing and reusing geocodes](storing-results.md).
