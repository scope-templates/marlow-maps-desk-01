---
title: Service status and uptime
updated: 2026-02-09
---

# Service status and uptime

Live service health is published at `status.marlowmaps.com`, with one component per area: Geocoding, Batch geocoding,
Routing, Recalculation and Webhooks. Subscribe there for email or webhook notices of incidents and planned maintenance.

## Commitments

| Plan | Monthly uptime target | Service credits |
|---|---|---|
| Starter | 99.5% | No |
| Growth | 99.9% | Yes |
| Scale | 99.95% | Yes |

Uptime is measured as the share of minutes in which `POST /v2/geocode` and `POST /v2/routes` answered valid requests
without a 5xx. Planned maintenance announced 7 days ahead is excluded, and is scheduled between 01:00 and 04:00 UTC on
Sundays.

## How maintenance looks to your client

During maintenance some calls may get `503 service_unavailable` with a `Retry-After` header. Retry after the given
number of seconds; requests during a maintenance window never return partial results.

```python
import time
import requests

def call(session, url, payload, attempts=5):
    for _ in range(attempts):
        resp = session.post(url, json=payload, timeout=15)
        if resp.status_code != 503:
            return resp
        time.sleep(int(resp.headers.get("Retry-After", "30")))
    return resp
```

## A health check for your own monitoring

`GET /v2/health` needs no key and does not count toward any rate limit. It reports whether each area is accepting
traffic from your region:

```bash
curl https://api.marlowmaps.com/v2/health
```

```json
{"geocoding": "ok", "routing": "ok", "recalculation": "degraded", "webhooks": "ok"}
```

`degraded` means requests succeed but slower than usual, or recalculation webhooks are delayed. Webhooks that are
delayed during an incident are still delivered, and their retry schedule only starts once a delivery is attempted.

## Incident reports

For any incident affecting a component for more than 15 minutes, a written report follows on the status page within
five working days, with the timeline, the cause and what changed.
