---
title: Supported regions
updated: 2026-03-30
---

# Supported regions

Marlow Maps covers five countries: UK, Ireland, Netherlands, Germany, France.

| Region | ISO code | Postcode format checked |
|---|---|---|
| UK | `GB` | Yes, full and outward-only postcodes |
| Ireland | `IE` | Yes, Eircodes |
| Netherlands | `NL` | Yes, `1234 AB` |
| Germany | `DE` | Yes, five digits |
| France | `FR` | Yes, five digits |

Addresses, coordinates and route stops anywhere else return `region_unsupported`. That applies to every endpoint:
geocoding, batch geocoding, reverse geocoding, routing, matrices and optimisation.

## What the error looks like

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address": "Via Roma 10, 20121 Milano"}'
```

```json
{
  "error": {
    "code": "region_unsupported",
    "message": "Addresses in IT are not covered. Supported: GB, IE, NL, DE, FR.",
    "request_id": "req_3f0b6d21"
  }
}
```

The status is `422`. Single geocodes and route requests fail as a whole. In a batch, only the affected item carries
`"status": "region_unsupported"` and the rest of the batch succeeds.

## Hinting the country

Ambiguous addresses ("Station Road 4") resolve faster and more accurately with a country hint:

```python
import requests

resp = requests.post(
    "https://api.marlowmaps.com/v2/geocode",
    headers={"X-Marlow-Key": key},
    json={"address": "Station Road 4", "country": "IE"},
    timeout=10,
)
```

`country` accepts the five ISO codes above. Any other value returns `region_unsupported` straight away, without a
lookup, so you can use it as a cheap pre-check.

## Routes across borders

Routes may cross between supported countries, for example Rotterdam to Cologne. A route that passes through an
unsupported country on the way, such as Lille to Luxembourg, returns `region_unsupported` with the offending stop or leg
named in `message`.

## Coming later

Belgium and Luxembourg are planned. New regions are announced in the [changelog](changelog.md); there is no beta flag
to request.
