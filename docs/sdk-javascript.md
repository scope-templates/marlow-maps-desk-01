---
title: JavaScript SDK
updated: 2026-05-27
---

# JavaScript SDK

`@marlowmaps/js` is the official client for Node.js 18 and later, Deno and Bun. It is for server-side code only; the
constructor throws if it detects a browser, because an `X-Marlow-Key` in a web page is a key anyone can use.

```bash
npm install @marlowmaps/js@^2.3
```

## Usage

```js
import { MarlowClient } from "@marlowmaps/js";

const marlow = new MarlowClient({ apiKey: process.env.MARLOW_KEY, maxRetries: 3 });

const hit = await marlow.geocode({ address: "Keizersgracht 221, 1016 DV Amsterdam", country: "NL" });
console.log(hit.precision); // "rooftop"

const results = await marlow.geocodeBatch(addresses); // sent 500 at a time
const route = await marlow.routes.create({ profile: "van", stops, recalculate: true });
```

Method names follow the endpoints: `geocode` is `POST /v2/geocode`, `geocodeBatch` is `POST /v2/geocode/batch`,
`routes.create` is `POST /v2/routes`, and so on.

## Errors

Failed calls reject with a `MarlowError` carrying `status`, `code`, `message` and `requestId`:

```js
try {
  await marlow.routes.create({ profile: "van", stops: tooManyStops });
} catch (err) {
  if (err.code === "too_many_stops") splitRoute(tooManyStops);
  else throw err;
}
```

`429` and `5xx` responses are retried automatically, honouring `Retry-After`.

## Webhooks

```js
import { verifySignature } from "@marlowmaps/js/webhooks";

app.post("/marlow/webhooks", express.raw({ type: "application/json" }), (req, res) => {
  if (!verifySignature(req.body, req.get("X-Marlow-Signature"), process.env.MARLOW_WEBHOOK_SECRET)) {
    return res.sendStatus(401);
  }
  queue.push(JSON.parse(req.body));
  res.sendStatus(204);
});
```

Use `express.raw`, not `express.json`: the signature is computed over the raw body.

## Checking a call from Python or a shell

When the SDK and your expectations disagree, repeat the call without it:

```python
import os
import requests

r = requests.post("https://api.marlowmaps.com/v2/geocode",
                  headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
                  json={"address": "Keizersgracht 221, 1016 DV Amsterdam", "country": "NL"},
                  timeout=10)
print(r.status_code, r.headers["X-Request-Id"], r.json())
```

```bash
curl -si -X POST https://api.marlowmaps.com/v2/geocode -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" -d '{"address": "Keizersgracht 221, 1016 DV Amsterdam"}'
```

Versions 1.x of the package used the retired v1 geocoding endpoint and fail with `410 endpoint_retired`.
