---
title: Webhook signatures
updated: 2026-02-24
---

# Webhook signatures

Anyone who learns your endpoint URL can post to it. The `X-Marlow-Signature` header lets you prove a request came from
Marlow Maps and was not altered.

## How the signature is made

```
X-Marlow-Signature = hex( HMAC-SHA256( key = endpoint signing secret, message = raw request body ) )
```

- The message is the **raw body bytes** exactly as sent. No timestamp, no headers, no re-serialised JSON.
- The key is the endpoint's signing secret, which starts `mmws_` and is shown when you create the endpoint.
- The output is 64 lowercase hex characters, with no prefix.

Signatures have been sent on every delivery since 2025-05-19.

## Verifying in Python

```python
import hashlib
import hmac
import os

SECRET = os.environ["MARLOW_WEBHOOK_SECRET"].encode()

def verify(raw_body: bytes, header_value: str) -> bool:
    expected = hmac.new(SECRET, raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header_value or "")
```

Read the body with your framework's raw accessor: `request.get_data()` in Flask, `await request.body()` in FastAPI,
`request.body` in Django. Parsing and dumping the JSON first changes whitespace and key order, and the signature will
not match.

## Checking by hand

Save a body to a file and compute the signature with `openssl` to compare with the header:

```bash
openssl dgst -sha256 -hmac "$MARLOW_WEBHOOK_SECRET" -hex < body.json
```

## Rotating the secret

```bash
curl -X POST https://api.marlowmaps.com/v2/webhooks/we_31fb8a/rotate-secret \
  -H "X-Marlow-Key: $MARLOW_KEY"
```

```python
import requests

new = requests.post(
    "https://api.marlowmaps.com/v2/webhooks/we_31fb8a/rotate-secret",
    headers={"X-Marlow-Key": key},
    timeout=10,
).json()["secret"]
```

For 24 hours after rotation, deliveries carry a second header, `X-Marlow-Signature-Previous`, signed with the old
secret. Accept either during the switch, then drop the old one.

## Failures

If verification fails, answer `401` and do not process the event. Marlow treats it as a failed delivery and retries on
the normal schedule, which gives you time to fix a misconfigured secret. Repeated signature failures across many
deliveries usually mean the body was modified by a proxy or decompressed and re-encoded on the way in.
