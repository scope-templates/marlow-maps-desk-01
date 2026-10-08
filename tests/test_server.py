from langchain_core.runnables import RunnableLambda

from desk.faq import FAQ
from desk.server import create_app

BATCH_TICKET = {
    "customer": "dev@harbourline-delivery.example",
    "question": "How many addresses can I send in one batch?",
}


def open_ticket(client, body=BATCH_TICKET):
    response = client.post("/tickets", json=body)
    assert response.status_code == 201
    return response.get_json()


def test_open_ticket_returns_a_plain_draft(client):
    body = open_ticket(client)
    assert set(body) == {"ticket_id", "draft", "faq_id", "status"}
    assert body["ticket_id"] == "T-4200"
    assert body["faq_id"] == "batch-geocode"
    assert body["status"] == "open"
    assert "up to 100 addresses" in body["draft"]


def test_open_ticket_needs_customer_and_question(client):
    assert client.post("/tickets", json={"customer": "dev@harbourline-delivery.example"}).status_code == 400
    assert client.post("/tickets", json={"customer": " ", "question": "Where is my key?"}).status_code == 400
    assert client.post("/tickets", data="not json").status_code == 400
    assert client.get("/tickets").get_json() == []


def test_ticket_detail_has_draft_and_sent_reply(client):
    ticket_id = open_ticket(client)["ticket_id"]
    client.post(f"/tickets/{ticket_id}/reply", json={"reply": "Up to 100 per request."})
    detail = client.get(f"/tickets/{ticket_id}").get_json()
    assert detail["question"] == BATCH_TICKET["question"]
    assert detail["customer"] == BATCH_TICKET["customer"]
    assert detail["reply"] == "Up to 100 per request."
    assert detail["status"] == "replied"
    assert "up to 100 addresses" in detail["draft"]
    assert set(detail) == {
        "ticket_id", "customer", "question", "faq_id", "draft", "status", "opened_at", "reply", "replied_at",
    }


def test_unknown_ticket_is_404(client):
    assert client.get("/tickets/T-9999").status_code == 404
    assert client.get("/tickets/nonsense").status_code == 404
    assert client.post("/tickets/T-9999/reply", json={"reply": "hello"}).status_code == 404


def test_second_reply_is_409(client):
    ticket_id = open_ticket(client)["ticket_id"]
    first = client.post(f"/tickets/{ticket_id}/reply", json={"reply": "first"})
    assert first.status_code == 200
    assert first.get_json()["reply"] == "first"
    assert client.post(f"/tickets/{ticket_id}/reply", json={"reply": "second"}).status_code == 409
    assert client.get(f"/tickets/{ticket_id}").get_json()["reply"] == "first"


def test_empty_reply_is_400(client):
    ticket_id = open_ticket(client)["ticket_id"]
    assert client.post(f"/tickets/{ticket_id}/reply", json={"reply": ""}).status_code == 400
    assert client.get(f"/tickets/{ticket_id}").get_json()["status"] == "open"


def test_ticket_list_is_newest_first(client):
    open_ticket(client)
    open_ticket(client, {"customer": "ops@kestrel-field.example", "question": "Which countries do you cover?"})
    listed = client.get("/tickets").get_json()
    assert [ticket["ticket_id"] for ticket in listed] == ["T-4201", "T-4200"]


def test_faq_lists_all_eight_entries_with_review_dates(client):
    entries = client.get("/faq").get_json()
    assert len(entries) == 8
    assert entries == FAQ
    assert all("last_reviewed" in entry for entry in entries)


def test_health_reports_dry_run(client):
    assert client.get("/health").get_json() == {"status": "ok", "model": "dry-run"}


def test_ticket_the_faq_does_not_cover_gets_no_draft(db_path, monkeypatch):
    drafted = []
    fake_chain = RunnableLambda(lambda inputs: drafted.append(inputs) or "drafted")
    monkeypatch.setattr("desk.server.build_chain", lambda: fake_chain)
    client = create_app(db_path, seed_path=None).test_client()

    response = client.post(
        "/tickets", json={"customer": "ops@kestrel-field.example", "question": "how do I cancel my account"}
    )
    assert response.status_code == 201
    assert response.get_json() == {"ticket_id": "T-4200", "draft": None, "faq_id": None, "status": "open"}
    assert drafted == []

    assert open_ticket(client)["draft"] == "drafted"
    assert len(drafted) == 1


def test_first_start_shows_the_seeded_tickets(seeded_client):
    listed = seeded_client.get("/tickets").get_json()
    assert len(listed) == 40
    assert listed[0]["ticket_id"] == "T-4239"
    assert open_ticket(seeded_client)["ticket_id"] == "T-4240"


def test_stats_on_the_seed(seeded_client):
    assert seeded_client.get("/stats").get_json() == {
        "tickets": 33, "drafted": 8, "no_draft": 25, "draft_sent_unchanged": 2, "open": 4,
    }


def test_stats_count_new_tickets(client):
    open_ticket(client)
    client.post("/tickets", json={"customer": "ops@kestrel-field.example", "question": "how do I cancel my account"})
    ticket_id = open_ticket(client)["ticket_id"]
    draft = client.get(f"/tickets/{ticket_id}").get_json()["draft"]
    client.post(f"/tickets/{ticket_id}/reply", json={"reply": draft})
    assert client.get("/stats").get_json() == {
        "tickets": 3, "drafted": 2, "no_draft": 1, "draft_sent_unchanged": 1, "open": 2,
    }
