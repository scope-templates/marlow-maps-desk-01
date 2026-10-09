---
title: Glossary
updated: 2025-09-12
---

# Glossary

Terms used throughout the Marlow Maps docs, with the field or endpoint each one maps to.

**Batch geocode.** A single `POST /v2/geocode/batch` request carrying up to 500 addresses. Counts as one request for
rate limiting and one geocode per address for quota.

**Confidence.** A number from 0 to 1 on every geocode result saying how sure the match is. Independent of precision.

**Delivery.** One event sent to one webhook endpoint, including all its retries. Identified by `X-Marlow-Delivery`.

**Key mode.** Whether a key is live (`mm_live_`) or test (`mm_test_`). Objects created in one mode are invisible in
the other.

**Leg.** The part of a route between two consecutive stops. Each leg has its own `distance_m`, `duration_s` and
polyline.

**Precision.** What the coordinates point at: `rooftop`, `street` or `locality`.

**Profile.** The kind of traveller a route is planned for: `car`, `van`, `bicycle` or `walk`.

**Recalculation.** Replanning an active route because of traffic, a driver going off route, a stop change or a manual
request. Announced with a `route.recalculated` webhook.

**Region.** One of the five supported countries: UK, Ireland, Netherlands, Germany, France. Anything else is
`region_unsupported`.

**Signing secret.** The per-endpoint secret (`mmws_...`) used to compute `X-Marlow-Signature`.

**Version (route).** A counter on each route that goes up by one on every recalculation. Use it to ignore stale
webhooks.

## Ids at a glance

| Prefix | Object | Example |
|---|---|---|
| `mm_live_`, `mm_test_` | API key | `mm_live_9d31f0a7c2e84b16` |
| `rte_` | Route | `rte_9Kx2mQ4` |
| `we_` | Webhook endpoint | `we_31fb8a` |
| `evt_` | Event | `evt_5a0c19e2` |
| `dlv_` | Webhook delivery | `dlv_2207ab` |
| `req_` | Request | `req_7c1e93a0` |
| `acc_` | Account | `acc_51c09e` |

Ids are case sensitive. Treat them as opaque strings of up to 32 characters; do not parse them.

```python
import re

ROUTE_ID = re.compile(r"^rte_[A-Za-z0-9]{1,28}$")
assert ROUTE_ID.match("rte_9Kx2mQ4")
```

```bash
curl https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4 -H "X-Marlow-Key: $MARLOW_KEY"
```
