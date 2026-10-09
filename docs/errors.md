---
title: Errors
updated: 2026-08-25
---

# Errors

Failed requests return a non-2xx status and a JSON body of the same shape on every endpoint:

```json
{
  "error": {
    "code": "region_unsupported",
    "message": "Addresses in IT are not covered. Supported: GB, IE, NL, DE, FR.",
    "request_id": "req_3f0b6d21"
  }
}
```

Branch on `error.code`, not on `message`; messages are for people and may be reworded. `request_id` is also sent as the
`X-Request-Id` header.

## Codes

| Status | `code` | Meaning |
|---|---|---|
| 400 | `invalid_request` | Malformed JSON, missing or out-of-range field |
| 400 | `address_required` | `address` missing or blank on a geocode |
| 400 | `invalid_webhook_url` | Webhook URL not public HTTPS on port 443 |
| 401 | `missing_key` | No `X-Marlow-Key` header |
| 401 | `invalid_key` | Header present but not a valid key |
| 402 | `quota_exceeded` | Starter plan past its monthly quota |
| 403 | `key_revoked` | Key was revoked |
| 404 | `no_match` | Address or point did not match anything |
| 404 | `route_not_found` | Unknown route, expired from storage, or from the other key mode |
| 404 | `webhook_not_found` | Unknown webhook endpoint |
| 409 | `route_not_active` | Route is completed, expired or cancelled |
| 409 | `recalculation_disabled` | Route created without `"recalculate": true` |
| 409 | `webhook_limit_reached` | Endpoint limit reached |
| 409 | `webhook_disabled` | Endpoint is disabled |
| 410 | `endpoint_retired` | `GET /v1/geocode` or `GET /v1/reverse-geocode`, retired 2025-06-30 |
| 413 | `batch_too_large` | More than 500 addresses in a batch |
| 422 | `region_unsupported` | Outside the UK, Ireland, the Netherlands, Germany and France |
| 422 | `too_many_stops` | More than 100 stops |
| 422 | `matrix_too_large` | More than 25 origins or 25 destinations |
| 422 | `no_route` | No legal path for the profile and vehicle |
| 429 | `rate_limited` | Over 600 requests per minute for this key |
| 429 | `recalculation_too_frequent` | Manual recalculation within 30 s of the last |
| 500 | `internal_error` | Our fault; retry with backoff |
| 503 | `service_unavailable` | Planned maintenance or overload; honour `Retry-After` |
| 504 | `upstream_timeout` | The request took over 60 s |

## Handling them in Python

```python
import requests

resp = session.post("https://api.marlowmaps.com/v2/geocode", json={"address": text}, timeout=10)
if resp.ok:
    return resp.json()["results"][0]

err = resp.json()["error"]
if err["code"] in ("no_match", "region_unsupported"):
    return None
raise RuntimeError(f'{resp.status_code} {err["code"]} ({err["request_id"]})')
```

## Seeing one from a shell

```bash
curl -s -X POST https://api.marlowmaps.com/v2/geocode \
  -H "Content-Type: application/json" -d '{"address": "x"}'
```

Without a key, that returns `401` with `"code": "missing_key"`. Batch geocodes report per-address problems inside
`results` with `status` rather than as an error response; see [Batch geocoding](geocode-batch.md).
