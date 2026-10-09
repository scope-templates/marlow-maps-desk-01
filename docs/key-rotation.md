---
title: Rotating API keys
updated: 2026-01-12
---

# Rotating API keys

Rotate a key when someone who had it leaves, when it may have been logged or committed, or on a fixed schedule. Marlow
keys never expire on their own, so rotation is always a deliberate step.

The safe order is create, deploy, verify, revoke. Because an account can hold up to 10 active keys, the old and new key
can work side by side while you roll out.

## Step 1: create the replacement

In the dashboard open **Settings**, then **API keys**, and create a key in the same mode. If the old key was
`mm_live_9d31f0a7c2e84b16`, the new one also starts `mm_live_`.

## Step 2: deploy it

Update your secret store and redeploy every service that used the old key. Services that read the key at start-up
need a restart.

## Step 3: verify that traffic has moved

The **API keys** screen shows a "last used" time per key. You can also confirm from a deployed host that the new key
is the one in use:

```bash
curl -s https://api.marlowmaps.com/v2/account \
  -H "X-Marlow-Key: $MARLOW_KEY" | python -m json.tool
```

```python
import os
import requests

me = requests.get(
    "https://api.marlowmaps.com/v2/account",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
).json()
assert me["key"]["last4"] == os.environ["EXPECTED_KEY_LAST4"]
```

Wait until the old key's "last used" time stops moving. For batch jobs that run nightly, that can mean waiting a day.

## Step 4: revoke the old key

Revoke it from the same screen. Within about a minute every request still using it fails with `403 key_revoked`. Watch
your error tracking for that code for the next day; anything that appears is a service you missed.

## If a key has leaked

Revoke first and rotate second. A leaked live key can spend your quota at 600 requests per minute, and the requests
are billed. Revocation is immediate enough that a short outage is usually cheaper than leaving the key active.

Webhook signing secrets are separate from API keys and rotate on their own schedule; see
[Webhook signatures](webhook-signatures.md).
