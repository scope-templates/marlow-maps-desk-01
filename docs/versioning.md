---
title: Versioning and deprecations
updated: 2025-09-04
---

# Versioning and deprecations

The version is part of the path: `https://api.marlowmaps.com/v2/...`. v2 is the current and only supported version.

## What can change within v2

Without a new version, we may:

- add endpoints, optional request fields and response fields;
- add event types and enum values that you did not ask for, such as a new `reason` on `route.recalculated`;
- raise limits, as with the batch size rising from 100 to 500 on 2025-04-14.

We will not, within v2, remove or rename a field, change a field's type, make an optional field required, or narrow
an existing enum. The three `precision` values (`rooftop`, `street`, `locality`) are fixed for the life of v2.

## Deprecation policy

When an endpoint or version is to be retired we give at least 90 days' notice through the [changelog](changelog.md),
an email to account owners, and a `Deprecation` header on every response from the affected endpoint:

```
Deprecation: true
Sunset: Mon, 30 Jun 2025 00:00:00 GMT
Link: <https://api.marlowmaps.com/v2/geocode>; rel="successor-version"
```

After the sunset date the endpoint returns `410 endpoint_retired`.

## The v1 retirement

v2 geocoding launched on 2025-03-03. `GET /v1/geocode` and `GET /v1/reverse-geocode` were deprecated the same day and
retired on 2025-06-30, 119 days later. Calls to them now fail permanently:

```bash
curl -i "https://api.marlowmaps.com/v1/geocode?address=14+Wharf+Road" -H "X-Marlow-Key: $MARLOW_KEY"
# HTTP/1.1 410 Gone
```

```python
import requests

r = requests.get("https://api.marlowmaps.com/v1/geocode",
                 params={"address": "14 Wharf Road"},
                 headers={"X-Marlow-Key": key}, timeout=10)
assert r.json()["error"]["code"] == "endpoint_retired"
```

[Migrating from v1](migrating-from-v1.md) covers the move.

## Watching for deprecations

Alert on any response with a `Deprecation` header in your HTTP client middleware. It costs nothing and gives you the
full notice period instead of finding out from a 410.
