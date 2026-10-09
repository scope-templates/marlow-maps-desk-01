---
title: Precision values
updated: 2025-09-29
---

# Precision values

Every geocode result, whether from `POST /v2/geocode`, a batch item or a reverse geocode, carries a `precision` field.
It tells you what kind of place the coordinates point at. `precision` is one of `rooftop`, `street`, `locality`.

| Value | The coordinates are | Good enough for |
|---|---|---|
| `rooftop` | On the building or its entrance | Doorstep delivery, technician arrival |
| `street` | On the right street, interpolated between known house numbers | Route planning, rough ETAs |
| `locality` | At the centre of a town, village or postcode district | Zone assignment, pricing by area |

There are no other values. The v1 values `exact` and `approx` were replaced on 2025-03-03 when v2 launched, and they
are never returned by v2. If your code still compares against `"exact"`, every result will look imprecise.

## Using precision in a checkout

A common pattern is to accept `rooftop` silently, ask the customer to confirm a pin for `street`, and ask for a better
address for `locality`:

```python
import os
import requests

resp = requests.post(
    "https://api.marlowmaps.com/v2/geocode",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    json={"address": form["address"], "country": form["country"]},
    timeout=10,
)
result = resp.json()["results"][0]

if result["precision"] == "rooftop":
    accept(result)
elif result["precision"] == "street":
    ask_customer_to_place_pin(result)
else:
    ask_for_house_number()
```

Test it from a shell with an address that only resolves to a town:

```bash
curl -s -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address": "Lyon", "country": "FR"}'
```

That returns `"precision": "locality"` with coordinates near 45.7640, 4.8357.

## Precision and confidence

`confidence` (0 to 1) is a separate signal: how sure the match is, not how specific. A `rooftop` result with
`confidence` 0.55 means "a specific building, but possibly the wrong one", typically when two streets share a name.
Treat anything under 0.7 as needing confirmation, whatever its precision.

## Migrating stored values

If your database holds v1 values, map `exact` to `rooftop`. `approx` cannot be mapped reliably because it covered both
street and town matches; re-geocode those rows with [batch geocoding](geocode-batch.md).
