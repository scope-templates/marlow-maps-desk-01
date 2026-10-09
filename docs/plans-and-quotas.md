---
title: Plans and monthly quotas
updated: 2026-03-05
---

# Plans and monthly quotas

Two limits apply to every account. The per-key rate limit (600 requests per minute) protects the service from bursts;
it is the same on every plan and is described in [Rate limits](rate-limits.md). The monthly quota decides how much
work you can do in a billing month and depends on your plan.

| Plan | Geocoded addresses / month | Routes / month | Webhook endpoints |
|---|---|---|---|
| Starter | 25,000 | 5,000 | 2 |
| Growth | 250,000 | 50,000 | 5 |
| Scale | 2,500,000 | 500,000 | 5 |

A batch geocode counts each address in the batch, so one `POST /v2/geocode/batch` with 500 addresses uses 500 of your
geocode quota but only one request of your rate limit. Reverse geocodes count as geocodes. A route recalculation does
not count as a new route.

Test keys (`mm_test_`) never draw on the quota.

## Checking usage

The dashboard shows month-to-date usage on the **Usage** screen. The same numbers are available from the API:

```bash
curl https://api.marlowmaps.com/v2/account/usage -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import os
import requests

usage = requests.get(
    "https://api.marlowmaps.com/v2/account/usage",
    headers={"X-Marlow-Key": os.environ["MARLOW_KEY"]},
    timeout=10,
).json()
print(f'{usage["geocodes"]["used"]} of {usage["geocodes"]["included"]} geocodes used')
```

## Going over

On Growth and Scale, usage past the quota is billed per thousand at the rate on your order form, and requests keep
working. On Starter, requests past the quota fail with `402 quota_exceeded` until the next billing month starts at
00:00 UTC on the first. Owners receive an email at 80% and 100% of each quota.

If you expect a one-off spike, such as geocoding an entire customer file during a migration, ask your account manager
for a temporary quota increase before you start.
