---
title: Changelog
updated: 2026-09-08
---

# Changelog

Changes to the Marlow Maps API, newest first. Additive changes ship without a version bump; anything that could break
an integration is announced at least 90 days ahead (see [Versioning](versioning.md)).

## 2026-09-08

- `GET /v2/account/usage` returns a `days` array with per-day geocode and route counts for the current month.

## 2026-06-02

- The webhook delivery log keeps 14 days of deliveries, up from 7. Any delivery in the log can be replayed, not only
  failed ones.

## 2026-04-14

- New webhook event `route.cancelled`, sent when you cancel a route.

## 2026-03-16

- Eircode-only addresses in Ireland now resolve to `rooftop` precision where the Eircode identifies a single building.

## 2026-01-26

- `POST /v2/routes/{route_id}/positions` accepts up to 20 positions per request, up from 5.

## 2025-11-10

- New route profile `bicycle`.

## 2025-06-30

- **Retired:** `GET /v1/geocode` and `GET /v1/reverse-geocode`. Both now return `410 endpoint_retired`. Use
  `POST /v2/geocode` with a JSON body `{"address": "..."}` and `POST /v2/reverse-geocode`.

## 2025-05-19

- Route recalculation webhooks are now retried 5 times over 30 minutes with backoff (1, 3, 8, 15 and 30 minutes after
  the original attempt). Previously they were retried 3 times over 10 minutes.
- Every webhook delivery is signed: `X-Marlow-Signature` carries the HMAC-SHA256 of the raw body, keyed with the
  endpoint's signing secret. See [Webhook signatures](webhook-signatures.md).
- New delivery header `X-Marlow-Attempt`.

## 2025-04-14

- `POST /v2/geocode/batch` accepts up to 500 addresses per request, up from 100. Larger batches return
  `413 batch_too_large`.

## 2025-03-03

- **New:** `POST /v2/geocode` takes `{"address": "..."}` as JSON. `precision` is now one of `rooftop`, `street` or
  `locality`, replacing `exact` and `approx`.
- **Deprecated:** `GET /v1/geocode` and `GET /v1/reverse-geocode`, with retirement set for 2025-06-30.

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" -H "Content-Type: application/json" \
  -d '{"address": "14 Wharf Road, London N1 7GR"}'
```

```python
requests.post("https://api.marlowmaps.com/v2/geocode",
              headers={"X-Marlow-Key": key}, json={"address": "14 Wharf Road, London N1 7GR"}, timeout=10)
```
