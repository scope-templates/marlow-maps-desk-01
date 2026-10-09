import re

WORD = re.compile(r"[a-z0-9_]+")
COMMON_WORDS = frozenset(
    "how do i my the a an is can in to of we our it what with for on and you your be get when does there".split()
)


def words(text: str) -> set[str]:
    return set(WORD.findall(text.lower())) - COMMON_WORDS


def ticket_id(number: int) -> str:
    return f"T-{number}"


def ticket_number(ticket_id: str) -> int:
    if not re.fullmatch(r"T-[1-9][0-9]*", ticket_id):
        raise KeyError(ticket_id)
    return int(ticket_id[2:])


def required_text(payload: object, field: str) -> str:
    value = payload.get(field) if isinstance(payload, dict) else None
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")
    return value.strip()
