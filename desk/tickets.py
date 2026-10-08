import json
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .text import ticket_id, ticket_number

SCHEMA = """
CREATE TABLE IF NOT EXISTS tickets (
    number INTEGER PRIMARY KEY,
    customer TEXT NOT NULL,
    question TEXT NOT NULL,
    faq_id TEXT,
    draft TEXT,
    status TEXT NOT NULL CHECK (status IN ('open', 'replied')),
    opened_at TEXT NOT NULL,
    reply TEXT,
    replied_at TEXT
)
"""


class TicketStore:
    def __init__(self, path: Path | str, seed_path: Path | None = None):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db, db:
            db.execute(SCHEMA)
            if seed_path and db.execute("SELECT COUNT(*) FROM tickets").fetchone()[0] == 0:
                db.executemany(
                    "INSERT INTO tickets (number, customer, question, faq_id, draft, status, opened_at, reply, replied_at) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    [
                        (
                            ticket_number(seeded["ticket_id"]), seeded["customer"], seeded["question"], seeded["faq_id"],
                            seeded["draft"], "open" if seeded["reply"] is None else "replied", seeded["opened_at"],
                            seeded["reply"], seeded["replied_at"],
                        )
                        for seeded in json.loads(seed_path.read_text(encoding="utf-8"))
                    ],
                )

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path)
        db.row_factory = sqlite3.Row
        return db

    def _ticket(self, row: sqlite3.Row) -> dict:
        ticket = {"ticket_id": ticket_id(row["number"])}
        ticket.update({key: row[key] for key in row.keys() if key != "number"})
        return ticket

    def open(self, customer: str, question: str, faq_id: str | None, draft: str | None) -> dict:
        opened_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with closing(self._connect()) as db, db:
            number = db.execute(
                "INSERT INTO tickets (number, customer, question, faq_id, draft, status, opened_at) "
                "SELECT COALESCE(MAX(number) + 1, 4200), ?, ?, ?, ?, 'open', ? FROM tickets",
                (customer, question, faq_id, draft, opened_at),
            ).lastrowid
            row = db.execute("SELECT * FROM tickets WHERE number = ?", (number,)).fetchone()
        return self._ticket(row)

    def get(self, ticket_id: str) -> dict:
        with closing(self._connect()) as db:
            row = db.execute("SELECT * FROM tickets WHERE number = ?", (ticket_number(ticket_id),)).fetchone()
        if row is None:
            raise KeyError(ticket_id)
        return self._ticket(row)

    def record_reply(self, ticket_id: str, reply: str) -> dict:
        number = ticket_number(ticket_id)
        replied_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with closing(self._connect()) as db, db:
            updated = db.execute(
                "UPDATE tickets SET reply = ?, replied_at = ?, status = 'replied' WHERE number = ? AND reply IS NULL",
                (reply, replied_at, number),
            ).rowcount
            row = db.execute("SELECT * FROM tickets WHERE number = ?", (number,)).fetchone()
        if row is None:
            raise KeyError(ticket_id)
        if not updated:
            raise ValueError(f"{ticket_id} already has a reply")
        return self._ticket(row)

    def stats(self) -> dict:
        with closing(self._connect()) as db:
            newest = db.execute("SELECT MAX(opened_at) FROM tickets").fetchone()[0]
            since = (datetime.fromisoformat(newest) - timedelta(days=30)).isoformat(timespec="seconds") if newest else ""
            # opened_at is always written as UTC isoformat, so comparing the strings compares the times.
            row = db.execute(
                "SELECT COUNT(*) AS tickets, COUNT(draft) AS drafted, COUNT(*) - COUNT(draft) AS no_draft, "
                "COUNT(CASE WHEN reply = draft THEN 1 END) AS draft_sent_unchanged, "
                "COUNT(CASE WHEN status = 'open' THEN 1 END) AS open "
                "FROM tickets WHERE opened_at >= ?",
                (since,),
            ).fetchone()
        return dict(row)

    def list(self) -> list[dict]:
        with closing(self._connect()) as db:
            rows = db.execute("SELECT * FROM tickets ORDER BY number DESC LIMIT 50").fetchall()
        return [self._ticket(row) for row in rows]
