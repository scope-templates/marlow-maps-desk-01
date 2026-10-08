from datetime import date

from desk.faq import FAQ, pick


def test_eight_entries_with_unique_ids():
    assert len(FAQ) == 8
    assert len({entry["id"] for entry in FAQ}) == 8


def test_every_last_reviewed_is_an_iso_date():
    for entry in FAQ:
        date.fromisoformat(entry["last_reviewed"])


def test_every_entry_has_a_question_and_an_answer():
    for entry in FAQ:
        assert entry["question"].endswith("?"), entry["id"]
        assert len(entry["answer"].split(". ")) >= 2, entry["id"]


def test_batch_question_picks_the_batch_entry():
    assert pick("how many addresses can I send in one batch")["id"] == "batch-geocode"


def test_punctuation_and_case_do_not_change_the_pick():
    assert pick("How many ADDRESSES can I send in one batch?")["id"] == "batch-geocode"


def test_rate_limit_question_picks_the_rate_limit_entry():
    assert pick("we keep getting 429 responses, what is the rate limit per minute?")["id"] == "rate-limit"


def test_no_shared_words_picks_nothing():
    assert pick("asdf") is None


def test_only_common_words_shared_picks_nothing():
    assert pick("how do I cancel my account") is None


def test_one_shared_word_is_not_enough():
    assert pick("can our van drivers see the batch?") is None


def test_two_shared_words_are_enough():
    assert pick("what is your rate limit")["id"] == "rate-limit"
