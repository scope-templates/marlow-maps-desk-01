---
title: Address formats by country
updated: 2025-10-08
---

# Address formats by country

`POST /v2/geocode` takes free text, so you do not have to split addresses into fields. Match quality still depends on
what you send. These are the forms that produce `rooftop` results most often in each supported region.

| Region | Recommended order | Example |
|---|---|---|
| UK | number, street, town, postcode | `14 Wharf Road, London N1 7GR` |
| Ireland | unit, street or estate, town, Eircode | `Unit 4, Ballymount Industrial Estate, Dublin 12, D12 X2F7` |
| Netherlands | street, number, postcode, city | `Keizersgracht 221, 1016 DV Amsterdam` |
| Germany | street, number, postcode, city | `Torstraße 109, 10119 Berlin` |
| France | number, street, postcode, city | `12 rue de la République, 69002 Lyon` |

## Postcodes carry most of the weight

In the UK, Ireland and the Netherlands the postcode alone narrows an address to a handful of buildings. If a customer
types a postcode that disagrees with the street, Marlow trusts the street and town and lowers `confidence`. An Eircode
on its own is usually enough for a `rooftop` result.

## Characters and length

Send UTF-8. Accented and special characters (`ß`, `é`, `ij`) are fine and should not be transliterated; `Torstrasse`
matches but `Torstraße` matches with higher confidence. The maximum is 300 characters; longer values fail with
`400 invalid_request` on a single geocode or `invalid_address` on a batch item.

## Things to strip before sending

- Delivery notes such as "leave with neighbour" or "gate code 4411".
- Company names on their own line, unless the address is a named building.
- Phone numbers, which can be mistaken for house numbers.

```python
import re

NOTE = re.compile(r"\b(leave|gate code|ring|call)\b.*", re.IGNORECASE)

def clean(address: str) -> str:
    return NOTE.sub("", address).strip(" ,")

payload = {"address": clean("14 Wharf Road, London N1 7GR, ring twice"), "country": "GB"}
```

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address": "12 rue de la République, 69002 Lyon", "country": "FR"}'
```

When the country is known from your order form, always pass it as `country`. It removes cross-border mix-ups such as
the many "Station Road" and "Bahnhofstraße" entries across the five regions.
