---
title: Storing and reusing geocodes
updated: 2025-10-30
---

# Storing and reusing geocodes

You may store coordinates and `formatted_address` values returned by the API for as long as you have the
customer relationship that produced them. Many teams geocode once at order time and keep the result on the order row;
that is the intended use.

## When to re-geocode

Stored results go stale slowly but they do go stale. New-build estates get house numbers, streets are renamed, and the
reference data improves. Re-geocode when:

- the stored `precision` is `street` or `locality` and the address is used again;
- the stored result is older than twelve months;
- the stored result still carries a v1 value (`exact` or `approx`).

## A simple cache

```python
import hashlib
import os
import requests

def cache_key(address, country):
    return hashlib.sha256(f"{country}|{address.strip().lower()}".encode()).hexdigest()

def geocode_cached(db, address, country):
    key = cache_key(address, country)
    row = db.get(key)
    if row and row["precision"] == "rooftop":
        return row
    resp = requests.post(
        "https://api.marlowmaps.com/v2/geocode",
        headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
        json={"address": address, "country": country},
        timeout=10,
    )
    resp.raise_for_status()
    row = resp.json()["results"][0]
    db.put(key, row)
    return row
```

If you keep the cache in a SQL table, put a unique database index on the hash column so concurrent writers do not
create duplicate rows.

## Re-geocoding old rows in bulk

Select the rows that meet the rules above and send them through `POST /v2/geocode/batch`, 500 at a time:

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode/batch \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d @stale-rows.json
```

## What you may not do

Results may not be resold, or published as a standalone dataset of addresses and coordinates. Showing a stored pin on
your own map, routing to it, or printing it on a delivery label is fine. If you stop being a Marlow Maps customer,
results already attached to orders may stay with those orders.
