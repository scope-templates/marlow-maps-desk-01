---
title: Team members and roles
updated: 2025-09-16
---

# Team members and roles

A Marlow Maps account can have any number of team members. Each member signs in to the dashboard with their own email
and has one of three roles. Roles control the dashboard only; API calls are authorised by keys, not by people.

| Role | Can see usage | Can manage API keys | Can manage webhooks | Can change billing |
|---|---|---|---|---|
| Owner | Yes | Yes | Yes | Yes |
| Admin | Yes | Yes | Yes | No |
| Developer | Yes | No | Yes | No |

Every account has exactly one owner. Ownership can be transferred from **Settings**, then **Team**.

## Why developers cannot create keys

Keys carry the full rate limit of 600 requests per minute and are billed. Keeping key creation with owners and admins
means a new key always has someone accountable for it. Developers can still register webhook endpoints and read
delivery logs, which is most of what day-to-day integration work needs.

## Listing members through the API

Admins can list members with a live or test key. This is mostly useful for audits:

```bash
curl https://api.marlowmaps.com/v2/account/members \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

resp = requests.get(
    "https://api.marlowmaps.com/v2/account/members",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    params={"limit": 50},
    timeout=10,
)
for m in resp.json()["data"]:
    print(m["email"], m["role"], m["last_sign_in"])
```

The list is paginated with `limit` (up to 100) and `cursor`; see [Pagination](pagination.md). Members cannot be
invited through the API; invitations are sent from the dashboard so the invitee's email is confirmed.

## Removing someone

Removing a member signs them out of the dashboard at once. It does not touch API keys, because keys do not belong to
people. If the person had copied a key, rotate it as described in [Rotating API keys](key-rotation.md).
