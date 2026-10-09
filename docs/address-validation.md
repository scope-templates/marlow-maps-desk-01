---
title: Validating addresses at checkout
updated: 2026-08-11
---

# Validating addresses at checkout

Most failed deliveries start with an address that was never checked. Geocoding the address while the customer is still
on the checkout page lets you catch typos when they are cheap to fix.

## The flow

1. The customer submits an address and country.
2. Your backend calls `POST /v2/geocode` with both.
3. You decide from `precision` and `confidence` whether to accept, confirm or reject.

```python
import os
import requests

def check_address(address, country):
    resp = requests.post(
        "https://api.marlowmaps.com/v2/geocode",
        headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
        json={"address": address, "country": country},
        timeout=3,
    )
    if resp.status_code == 404:
        return "reject", None
    if resp.status_code == 422:
        return "outside_area", None
    resp.raise_for_status()
    hit = resp.json()["results"][0]
    if hit["precision"] == "rooftop" and hit["confidence"] >= 0.8:
        return "accept", hit
    return "confirm", hit
```

Use a short timeout. A checkout should not hang on a slow lookup; if the call times out, accept the address and
geocode it again later in the order pipeline.

## What to show the customer

| Outcome | Status and fields | Suggested message |
|---|---|---|
| accept | `200`, `rooftop`, confidence ≥ 0.8 | none |
| confirm | `200`, `street` or `locality`, or low confidence | "Did you mean …?" with `formatted_address` |
| reject | `404 no_match` | "We could not find that address" |
| outside area | `422 region_unsupported` | "We deliver to the UK, Ireland, the Netherlands, Germany and France" |

## Testing the edge cases

```bash
curl -s -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" -H "Content-Type: application/json" \
  -d '{"address": "1 Nowhere Lane, Atlantis", "country": "GB"}'
```

That returns `404 no_match`. Swap the country for `IT` and you get `422 region_unsupported` without a lookup.

## Rate limits on busy days

A checkout makes one geocode per order attempt, so 600 requests per minute covers roughly ten orders per second. If
your peak is higher, use a separate key for checkout so a nightly batch job on another key cannot starve it.
