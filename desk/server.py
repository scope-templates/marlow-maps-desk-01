import os
from pathlib import Path

from flask import Flask, jsonify, request

from .chain import build_chain
from .faq import FAQ, pick
from .text import required_text
from .tickets import TicketStore

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DATA_DIR / "desk.sqlite"
SEED_PATH = DATA_DIR / "tickets.json"


def create_app(db_path: Path | str = DB_PATH, seed_path: Path | None = SEED_PATH) -> Flask:
    app = Flask(__name__)
    store = TicketStore(db_path, seed_path)
    chain = build_chain()
    model_name = os.environ.get("MARLOW_MODEL", "").strip() or "dry-run"

    @app.post("/tickets")
    def open_ticket():
        payload = request.get_json(silent=True)
        try:
            customer = required_text(payload, "customer")
            question = required_text(payload, "question")
        except ValueError as err:
            return jsonify(error=str(err)), 400
        entry = pick(question)
        faq_id = draft = None
        if entry:
            faq_id = entry["id"]
            draft = chain.invoke({"question": question, "faq_question": entry["question"], "answer": entry["answer"]})
        ticket = store.open(customer, question, faq_id, draft)
        return jsonify({key: ticket[key] for key in ("ticket_id", "draft", "faq_id", "status")}), 201

    @app.get("/tickets")
    def list_tickets():
        return jsonify(store.list())

    @app.get("/tickets/<ticket_id>")
    def get_ticket(ticket_id: str):
        try:
            return jsonify(store.get(ticket_id))
        except KeyError:
            return jsonify(error=f"no ticket {ticket_id}"), 404

    @app.post("/tickets/<ticket_id>/reply")
    def reply(ticket_id: str):
        try:
            text = required_text(request.get_json(silent=True), "reply")
        except ValueError as err:
            return jsonify(error=str(err)), 400
        try:
            return jsonify(store.record_reply(ticket_id, text))
        except KeyError:
            return jsonify(error=f"no ticket {ticket_id}"), 404
        except ValueError as err:
            return jsonify(error=str(err)), 409

    @app.get("/stats")
    def stats():
        return jsonify(store.stats())

    @app.get("/faq")
    def faq():
        return jsonify(FAQ)

    @app.get("/health")
    def health():
        return jsonify(status="ok", model=model_name)

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))
