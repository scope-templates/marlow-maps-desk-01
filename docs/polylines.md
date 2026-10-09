---
title: Decoding route polylines
updated: 2025-09-18
---

# Decoding route polylines

Route responses carry the path as an encoded polyline string in `polyline`. It uses the widely used precision-5
encoding: coordinates are rounded to five decimal places, delta-encoded and packed into printable ASCII. A route of a
few hundred points fits in a couple of kilobytes.

If your map library reads encoded polylines, pass the string straight through. Otherwise decode it yourself.

## Decoding in Python

The `polyline` package on PyPI decodes it in one call:

```python
import os
import polyline
import requests

route = requests.get(
    "https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
).json()

points = polyline.decode(route["polyline"], 5)
print(len(points), points[0])
```

Note the order: the decoder returns `(lat, lng)` pairs. GeoJSON wants `[lng, lat]`, so swap them before building a
`LineString`.

## Asking for GeoJSON instead

Add `?geometry=geojson` to `GET /v2/routes/{route_id}` and the response carries a `geometry` object in place of
`polyline`:

```bash
curl "https://api.marlowmaps.com/v2/routes/rte_9Kx2mQ4?geometry=geojson" \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```json
{
  "route_id": "rte_9Kx2mQ4",
  "geometry": {
    "type": "LineString",
    "coordinates": [[-0.0962, 51.5322], [-0.0955, 51.5326], [-0.0553, 51.545]]
  }
}
```

The `geometry` option only exists on the GET; `POST /v2/routes` always returns the encoded form because it is smaller.

## Per-leg geometry

Each item in `legs` has its own `polyline` as well, which is useful for colouring completed and remaining legs
differently. The full-route string is simply the legs joined.

## Errors

An unknown value for `geometry` returns `400 invalid_request`. After a recalculation the polyline changes; webhooks
for `route.recalculated` do not include it, to keep payloads small, so fetch the route when you need the new path.
