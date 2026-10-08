# Marlow Maps support desk

Marlow Maps sells a geocoding and routing API to delivery, courier and field-service apps, and this is the desk our support staff work tickets from: developers at our customers write in about integrating the API, the desk drafts a reply from our FAQ, and Priya (days) or Tom (evenings) edits the draft, replies to the developer and records the reply on the ticket. The developer docs at https://github.com/scope-templates/marlow-birchwell-docs-01/tree/main/marlow are the source of truth for the API itself.

## Running

```
py -3.12 -m pip install -r requirements.txt
py -3.12 -m desk.server
```

The desk listens on port 8080 (set `PORT` to change it) and keeps tickets in `data/desk.sqlite`, which is created on first run. The first start also loads the recent tickets from `data/tickets.json`.

Drafts are written by a LangChain chain in `desk/chain.py`. With `MARLOW_MODEL` unset the desk runs in dry-run mode: the matching FAQ answer is used as the draft word for word, so no network or account is needed. To draft with a hosted chat model, set `MARLOW_MODEL` to a `provider:model` string that LangChain's `init_chat_model` accepts and install that provider's LangChain package.

## Endpoints

All requests and responses are JSON.

| Method | Path | Body | Returns |
|---|---|---|---|
| POST | `/tickets` | `{"customer": "...", "question": "..."}` | `201` with `{"ticket_id": "T-4200", "draft": "...", "faq_id": "...", "status": "open"}` |
| GET | `/tickets` | | the fifty most recent tickets, newest first |
| GET | `/tickets/<id>` | | one ticket with its draft and any reply sent |
| POST | `/tickets/<id>/reply` | `{"reply": "..."}` | the ticket with the reply staff sent; `409` if it already has one |
| GET | `/stats` | | for tickets opened in the 30 days before the newest one: `{"tickets", "drafted", "no_draft", "draft_sent_unchanged", "open"}` |
| GET | `/faq` | | the eight FAQ entries with their `last_reviewed` dates |
| GET | `/health` | | `{"status": "ok", "model": "dry-run"}` or the configured model |

Ticket ids count up from `T-4200`. A missing or empty field is a `400`; an unknown ticket is a `404`.

## FAQ

The desk matches a ticket to one of the eight entries in `desk/faq.py` by the words it shares with the entry's question, and drafts from that entry's answer. The FAQ entries live in `desk/faq.py`, each with the date support last reviewed it. A ticket the FAQ does not cover arrives with no draft, and staff answer it from the developer docs.

## Docs

The developer docs at https://github.com/scope-templates/marlow-birchwell-docs-01/tree/main/marlow are the source of truth for every integration question; the FAQ is the desk's shorthand.

## Tests

```
py -3.12 -m pytest -q
```
