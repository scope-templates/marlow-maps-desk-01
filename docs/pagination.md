---
title: Pagination
updated: 2025-09-23
---

# Pagination

List endpoints return results a page at a time using an opaque cursor. The same two parameters work everywhere:

| Parameter | Default | Max | Notes |
|---|---|---|---|
| `limit` | 20 | 100 | Items per page |
| `cursor` | none | | The `next_cursor` from the previous page |

Paginated endpoints:

- `GET /v2/routes`
- `GET /v2/webhooks`
- `GET /v2/webhooks/{id}/deliveries`
- `GET /v2/account/members`

Each response has `data` (the page) and `next_cursor`. When `next_cursor` is `null`, you have reached the end.

```json
{
  "data": [{"route_id": "rte_9Kx2mQ4", "status": "active"}],
  "next_cursor": "c_eyJ0IjoxNzc1MTE3NDYwfQ"
}
```

Items are ordered newest first and the order is stable while you page: a route created after you fetched the first page
will not shift later pages.

## Walking every page

```python
import os
import requests

def all_routes(status="active"):
    params = {"status": status, "limit": 100}
    headers = {"X-Marlow-Key": os.environ["MARLOW_KEY"]}
    while True:
        page = requests.get(
            "https://api.marlowmaps.com/v2/routes",
            headers=headers,
            params=params,
            timeout=10,
        ).json()
        yield from page["data"]
        if not page["next_cursor"]:
            return
        params["cursor"] = page["next_cursor"]
```

```bash
curl "https://api.marlowmaps.com/v2/routes?limit=100&cursor=c_eyJ0IjoxNzc1MTE3NDYwfQ" \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

## Rules

- Cursors expire after 15 minutes. An expired or edited cursor returns `400 invalid_request` with
  `"message": "cursor expired"`; start again from the first page.
- Cursors are bound to the filters they were made with. Changing `status` while reusing a cursor is an error.
- Each page is one request against the 600 requests per minute limit. Use `limit=100` for bulk exports.
- A `limit` above 100 is rejected rather than silently capped.
