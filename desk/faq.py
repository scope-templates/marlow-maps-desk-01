import re

COMMON_WORDS = frozenset(
    "how do i my the a an is can in to of we our it what with for on and you your be get when does there".split()
)

FAQ = [
    {
        "id": "auth-header",
        "question": "How do I authenticate requests to the API?",
        "answer": (
            "Send your key in the X-Marlow-Key header on every request, like this: X-Marlow-Key: <key>. "
            "The same header works for geocoding, batch geocoding and routing calls. "
            "Keep the key on your own server rather than inside a driver app or a web page."
        ),
        "last_reviewed": "2025-02-11",
    },
    {
        "id": "geocode-endpoint",
        "question": "Which endpoint do I call to geocode an address?",
        "answer": (
            "Call GET /v1/geocode?address=... on https://api.marlowmaps.com with the address URL-encoded "
            "in the query string. "
            "The response gives you the coordinates and a precision value for the match. "
            "It is a plain GET, so you can try it from curl with nothing more than your key header."
        ),
        "last_reviewed": "2024-08-19",
    },
    {
        "id": "batch-geocode",
        "question": "How many addresses can I geocode in one batch request?",
        "answer": (
            "A batch geocode request takes up to 100 addresses. "
            "For a longer list, split it into requests of 100 or fewer and send them one after another. "
            "Each address comes back with its own coordinates and precision, in the order you sent them."
        ),
        "last_reviewed": "2024-11-03",
    },
    {
        "id": "rate-limit",
        "question": "What is the rate limit, and what happens if I go over it?",
        "answer": (
            "Each key can make 600 requests per minute. "
            "Go over that and you get a 429 response with a Retry-After header saying how many seconds to wait. "
            "Wait at least that long before you try again rather than retrying straight away."
        ),
        "last_reviewed": "2025-01-27",
    },
    {
        "id": "route-webhooks",
        "question": "How do route recalculation webhooks retry if my endpoint is down?",
        "answer": (
            "If your endpoint does not answer with a 2xx, we retry the route recalculation webhook 3 times "
            "over 10 minutes. "
            "After the third failed attempt we stop trying, so the event is not delivered again. "
            "Answer quickly with a 200 and do any slow work after you have replied."
        ),
        "last_reviewed": "2024-06-14",
    },
    {
        "id": "precision-values",
        "question": "What do the precision values in a geocode response mean?",
        "answer": (
            "Every geocode result has a precision field, and it is either exact or approx. "
            "exact means we matched the address to a single building; approx means we placed it on the "
            "right street or in the right area. "
            "If your drivers need a door to stop at, treat approx results with care."
        ),
        "last_reviewed": "2024-07-02",
    },
    {
        "id": "getting-a-key",
        "question": "Where do I get an API key?",
        "answer": (
            "Sign in to the dashboard and open Settings, then API keys. "
            "Live keys start with mm_live_ and test keys start with mm_test_, so use a test key while you build. "
            "You can create a new key and revoke an old one from the same page."
        ),
        "last_reviewed": "2025-02-11",
    },
    {
        "id": "regions",
        "question": "Which countries and regions do you cover?",
        "answer": (
            "We cover the UK, Ireland, the Netherlands, Germany and France. "
            "An address anywhere else comes back with the error region_unsupported. "
            "Check for that code before you show a result to a driver."
        ),
        "last_reviewed": "2024-12-09",
    },
]


def pick(question: str) -> dict | None:
    asked = set(re.findall(r"[a-z0-9_]+", question.lower())) - COMMON_WORDS
    shared, entry = max(
        ((len(asked & set(re.findall(r"[a-z0-9_]+", candidate["question"].lower()))), candidate) for candidate in FAQ),
        key=lambda pair: pair[0],
    )
    return entry if shared >= 2 else None
