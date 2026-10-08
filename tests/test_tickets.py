import json

import pytest

from desk.faq import FAQ, pick
from desk.server import SEED_PATH
from desk.tickets import TicketStore


def open_one(store, question="Where do I get an API key?"):
    return store.open("dispatch@northwind-couriers.example", question, "getting-a-key", "draft text")


def test_ticket_numbers_start_at_4200(db_path):
    store = TicketStore(db_path)
    assert open_one(store)["ticket_id"] == "T-4200"
    assert open_one(store)["ticket_id"] == "T-4201"


def test_open_ticket_has_no_reply_yet(db_path):
    ticket = open_one(TicketStore(db_path))
    assert ticket["status"] == "open"
    assert ticket["draft"] == "draft text"
    assert ticket["faq_id"] == "getting-a-key"
    assert ticket["reply"] is None
    assert ticket["replied_at"] is None


def test_get_returns_the_stored_ticket(db_path):
    store = TicketStore(db_path)
    opened = open_one(store, "Which countries do you cover?")
    assert store.get(opened["ticket_id"]) == opened


@pytest.mark.parametrize("ticket_id", ["T-9999", "T-abc", "4200", "X-4200", "", "T-04200"])
def test_get_unknown_raises_key_error(db_path, ticket_id):
    store = TicketStore(db_path)
    open_one(store)
    with pytest.raises(KeyError):
        store.get(ticket_id)


def test_record_reply_marks_the_ticket_replied(db_path):
    store = TicketStore(db_path)
    ticket_id = open_one(store)["ticket_id"]
    replied = store.record_reply(ticket_id, "Settings, then API keys.")
    assert replied["status"] == "replied"
    assert replied["reply"] == "Settings, then API keys."
    assert replied["replied_at"] is not None
    assert store.get(ticket_id) == replied


def test_record_reply_twice_raises_value_error(db_path):
    store = TicketStore(db_path)
    ticket_id = open_one(store)["ticket_id"]
    store.record_reply(ticket_id, "first")
    with pytest.raises(ValueError):
        store.record_reply(ticket_id, "second")
    assert store.get(ticket_id)["reply"] == "first"


def test_record_reply_on_unknown_ticket_raises_key_error(db_path):
    with pytest.raises(KeyError):
        TicketStore(db_path).record_reply("T-4200", "hello")


def test_list_is_newest_first_and_capped_at_fifty(db_path):
    store = TicketStore(db_path)
    for n in range(55):
        open_one(store, f"question {n}")
    listed = store.list()
    assert len(listed) == 50
    assert listed[0]["ticket_id"] == "T-4254"
    assert listed[-1]["ticket_id"] == "T-4205"


def test_tickets_survive_a_new_store_on_the_same_file(db_path):
    ticket_id = open_one(TicketStore(db_path))["ticket_id"]
    assert TicketStore(db_path).get(ticket_id)["ticket_id"] == ticket_id


def test_ticket_without_a_faq_match_has_no_draft(db_path):
    ticket = TicketStore(db_path).open("dispatch@northwind-couriers.example", "Can I cancel a route?", None, None)
    assert ticket["faq_id"] is None
    assert ticket["draft"] is None
    assert ticket["status"] == "open"


def test_first_start_loads_the_seed_and_numbering_continues(db_path):
    store = TicketStore(db_path, SEED_PATH)
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    assert store.get("T-4200")["question"] == seed[0]["question"]
    assert store.list()[0]["ticket_id"] == "T-4239"
    assert open_one(store)["ticket_id"] == "T-4240"


def test_seed_is_not_loaded_twice(db_path):
    open_one(TicketStore(db_path, SEED_PATH))
    store = TicketStore(db_path, SEED_PATH)
    assert open_one(store)["ticket_id"] == "T-4241"


def test_seed_is_not_loaded_into_a_store_that_already_has_tickets(db_path):
    open_one(TicketStore(db_path))
    assert open_one(TicketStore(db_path, SEED_PATH))["ticket_id"] == "T-4201"


def test_seeded_tickets_have_status_from_their_reply(db_path):
    tickets = TicketStore(db_path, SEED_PATH).list()
    assert len(tickets) == 40
    assert sum(ticket["status"] == "replied" for ticket in tickets) == 36
    for ticket in tickets:
        assert (ticket["status"] == "open") == (ticket["reply"] is None) == (ticket["replied_at"] is None)


def test_seed_matches_what_the_desk_would_have_drafted():
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    assert [ticket["ticket_id"] for ticket in seed] == [f"T-{4200 + n}" for n in range(40)]
    assert [ticket["opened_at"] for ticket in seed] == sorted(ticket["opened_at"] for ticket in seed)
    assert seed[0]["opened_at"].startswith("2026-09-01")
    assert seed[-1]["opened_at"].startswith("2026-10-07")
    answers = {entry["id"]: entry["answer"] for entry in FAQ}
    for ticket in seed:
        entry = pick(ticket["question"])
        assert ticket["faq_id"] == (entry["id"] if entry else None), ticket["ticket_id"]
        assert ticket["draft"] == answers.get(ticket["faq_id"]), ticket["ticket_id"]
        if ticket["replied_at"]:
            assert ticket["replied_at"] > ticket["opened_at"], ticket["ticket_id"]
    assert sum(ticket["faq_id"] is None for ticket in seed) == 30
    assert len({ticket["faq_id"] for ticket in seed}) == 9


def test_seed_replies_to_stale_faq_answers_give_the_current_values():
    seed = json.loads(SEED_PATH.read_text(encoding="utf-8"))
    current = {
        "geocode-endpoint": "POST /v2/geocode",
        "batch-geocode": "500 addresses",
        "route-webhooks": "X-Marlow-Signature",
        "precision-values": "rooftop",
    }
    corrected = [ticket for ticket in seed if ticket["faq_id"] in current]
    assert len(corrected) == 4
    for ticket in corrected:
        assert current[ticket["faq_id"]] in ticket["reply"], ticket["ticket_id"]


def test_stats_on_an_empty_store_are_zero(db_path):
    assert TicketStore(db_path).stats() == {
        "tickets": 0, "drafted": 0, "no_draft": 0, "draft_sent_unchanged": 0, "open": 0,
    }

