---
title: Request ids and debugging
updated: 2025-11-03
---

# Request ids and debugging

Every response from `https://api.marlowmaps.com`, successful or not, carries an `X-Request-Id` header such as
`req_7c1e93a0`. Error bodies repeat it as `error.request_id`, and geocode responses include it as `request_id`.

With that id we can find the exact request in our logs: what you sent, which reference data version answered it, and
how long each step took. Without it, "a geocode last Tuesday came back wrong" is very hard to trace.

## Log it

```python
import logging
import os
import requests

log = logging.getLogger("marlow")

resp = requests.post(
    "https://api.marlowmaps.com/v2/geocode",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"address": address},
    timeout=10,
)
log.info("geocode status=%s request_id=%s", resp.status_code, resp.headers.get("X-Request-Id"))
```

```bash
curl -s -D - -o /dev/null -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" -H "Content-Type: application/json" \
  -d '{"address": "14 Wharf Road, London N1 7GR"}' | grep -i x-request-id
```

Store the id next to anything you keep from the response, such as the coordinates on an order. When a driver reports a
wrong pin weeks later, the id takes you straight to the original lookup.

## Sending your own correlation id

If you send `X-Correlation-Id` (up to 64 printable characters), Marlow logs it alongside the request id and echoes it
in the response. Use your own trace or order id so both sides can be matched up. It has no effect on behaviour.

## Reporting a problem

Email api@marlowmaps.com with:

- the `X-Request-Id` values (up to ten);
- what you expected and what you got;
- for a wrong geocode, the correct address or coordinates if you know them.

Request logs are kept for 30 days, so report problems promptly. Geocode corrections are usually live in the next weekly
data release.

## Webhook deliveries

Webhook deliveries have their own ids in `X-Marlow-Delivery` (`dlv_...`). Use those, not request ids, when asking
about a webhook; the [delivery log](webhook-delivery-log.md) shows every attempt.
