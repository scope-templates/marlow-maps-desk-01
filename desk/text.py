import re


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
