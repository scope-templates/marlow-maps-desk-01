---
title: API keys
updated: 2025-12-03
---

# API keys

API keys are created and revoked in the dashboard: open **Settings**, then **API keys**. Only account owners and
admins see that screen (see [Team members](team-members.md)).

## Key format

Every key starts with one of two prefixes:

- `mm_live_` for production traffic, billed against your plan.
- `mm_test_` for development and CI, not billed.

The prefix is followed by sixteen lowercase hex characters, for example `mm_live_9d31f0a7c2e84b16`. If a value in your
config does not start with one of these prefixes, it is not a Marlow key; the API rejects it with `401 invalid_key`.

## Creating a key

1. Open **Settings**, then **API keys**, and choose **Create key**.
2. Pick live or test and give the key a name you will recognise later, such as `dispatch-worker-prod`.
3. Copy the key. It is shown once; after you close the dialog only the last four characters remain visible.

An account can hold up to 10 active keys. Use one key per service so a leak or a rate-limit problem stays contained.

## Checking a key from the command line

`GET /v2/account` is a cheap call that confirms a key works and shows which account it belongs to:

```bash
curl https://api.marlowmaps.com/v2/account -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

info = requests.get(
    "https://api.marlowmaps.com/v2/account",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
).json()
print(info["account_id"], info["key"]["mode"], info["key"]["name"])
```

```json
{
  "account_id": "acc_51c09e",
  "key": {"name": "dispatch-worker-prod", "mode": "live", "last4": "4b16"},
  "rate_limit_per_minute": 600
}
```

## Revoking a key

Choose **Revoke** next to the key. Revocation takes effect within a minute; after that, requests with the key fail
with `403 key_revoked`. Revoked keys cannot be restored, so rotate first if the key is still in use. The
[key rotation](key-rotation.md) guide gives a zero-downtime order of steps.
