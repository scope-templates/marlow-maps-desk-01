import re
from pathlib import Path

import markdown
from flask import Flask, abort, render_template_string, request

from .text import WORD, words

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs"

HEAD = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>{{ title }} - Marlow Maps developer docs</title></head>
<body>
<header>
<p><a href="/docs">Marlow Maps developer docs</a></p>
<form action="/docs/search" method="get">
<input type="text" name="q" value="{{ q }}">
<button type="submit">Search</button>
</form>
</header>
<main>
"""
FOOT = """
</main>
<footer><p>Still stuck? Open a ticket with the support desk (POST /tickets).</p></footer>
</body>
</html>
"""
CONTENTS = HEAD + """<h1>Contents</h1>
<ul>
{% for slug, page in pages %}<li><a href="/docs/{{ slug }}">{{ page.title }}</a></li>
{% endfor %}</ul>""" + FOOT
PAGE = HEAD + """<h1>{{ title }}</h1>
<p>Updated {{ updated }}</p>
{{ html|safe }}""" + FOOT
RESULTS = HEAD + """<h1>Search results</h1>
{% if results %}<ol>
{% for slug, page, snippet in results %}<li><a href="/docs/{{ slug }}">{{ page.title }}</a>{% if snippet %}<p>{{ snippet }}</p>{% endif %}</li>
{% endfor %}</ol>{% else %}<p>No pages match.</p>{% endif %}""" + FOOT


def add_docs_site(app: Flask) -> None:
    pages = {}
    for path in DOCS_DIR.glob("*.md"):
        _, front_matter, body = path.read_text(encoding="utf-8").split("---\n", 2)
        fields = dict(line.split(": ", 1) for line in front_matter.splitlines())
        body = body.lstrip("\n").removeprefix(f"# {fields['title']}\n").strip()
        html = markdown.markdown(body, extensions=["tables", "fenced_code"])
        pages[path.stem] = {
            **fields,
            "body": body,
            "html": re.sub(r'href="(?:\./)?([\w-]+)\.md(#[^"]*)?"', r'href="/docs/\1\2"', html),
            "title_words": words(fields["title"]),
            "words": words(f"{fields['title']}\n{body}"),
        }

    @app.get("/docs")
    def docs_contents():
        listed = sorted(pages.items(), key=lambda item: item[1]["title"].lower())
        return render_template_string(CONTENTS, title="Contents", pages=listed)

    @app.get("/docs/<slug>")
    def docs_page(slug: str):
        if slug not in pages:
            abort(404)
        page = pages[slug]
        return render_template_string(PAGE, title=page["title"], updated=page["updated"], html=page["html"])

    @app.get("/docs/search")
    def docs_search():
        q = request.args.get("q", "")
        asked = words(q)
        matches = sorted(
            ((slug, page) for slug, page in pages.items() if asked & page["words"]),
            key=lambda match: (
                -len(asked & match[1]["words"]), -len(asked & match[1]["title_words"]), match[1]["title"].lower(),
            ),
        )
        results = []
        for slug, page in matches:
            hit = next((word.start() for word in WORD.finditer(page["body"].lower()) if word.group() in asked), None)
            line = "" if hit is None else page["body"][page["body"].rfind("\n", 0, hit) + 1:].split("\n", 1)[0]
            results.append((slug, page, line))
        return render_template_string(RESULTS, title="Search results", q=q, results=results)
