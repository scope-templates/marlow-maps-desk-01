---
title: Quickstart for JavaScript
updated: 2026-04-09
---

# Quickstart for JavaScript

This guide uses the built-in `fetch` in Node.js 18 or later. Call the API from your server, never from a browser:
an `X-Marlow-Key` shipped to a web page can be copied and used against your quota.

## Set up

```bash
mkdir marlow-demo && cd marlow-demo
npm init -y
export MARLOW_KEY=mm_test_2b7c91e0d4a6f835
```

Keys are created in the dashboard under **Settings**, then **API keys**. Use a key starting `mm_test_` while you
build.

## Geocode an address

```js
const BASE = "https://api.marlowmaps.com";

async function geocode(address) {
  const res = await fetch(`${BASE}/v2/geocode`, {
    method: "POST",
    headers: {
      "X-Marlow-Key": process.env.MARLOW_KEY,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ address }),
  });
  if (!res.ok) {
    const { error } = await res.json();
    throw new Error(`${res.status} ${error.code}: ${error.message}`);
  }
  return (await res.json()).results[0];
}

const hit = await geocode("Keizersgracht 221, 1016 DV Amsterdam");
console.log(hit.lat, hit.lng, hit.precision);
```

Save it as `geocode.mjs` and run `node geocode.mjs`.

The same request from a shell, which is handy when you want to compare output:

```bash
curl -X POST https://api.marlowmaps.com/v2/geocode \
  -H "X-Marlow-Key: $MARLOW_KEY" \
  -H "Content-Type: application/json" \
  -d '{"address": "Keizersgracht 221, 1016 DV Amsterdam"}'
```

## Respect the rate limit

Each key may make 600 requests per minute. When you exceed it the API answers `429` with a `Retry-After` header in
seconds:

```js
if (res.status === 429) {
  const wait = Number(res.headers.get("Retry-After") ?? "1");
  await new Promise((r) => setTimeout(r, wait * 1000));
}
```

If you are geocoding a list of addresses, send them to `POST /v2/geocode/batch` in groups of up to 500 instead of one
request each. The [JavaScript SDK](sdk-javascript.md) handles both the batching and the `Retry-After` wait for you.
