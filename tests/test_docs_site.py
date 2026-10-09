import re

from desk.docs_site import DOCS_DIR
from desk.server import create_app


def result_slugs(html):
    return re.findall(r'<li><a href="/docs/([\w-]+)">', html)


def test_contents_lists_every_page_by_title_alphabetically(client):
    html = client.get("/docs").get_data(as_text=True)
    titles = {}
    for path in DOCS_DIR.glob("*.md"):
        titles[path.stem] = re.search(r"^title: (.*)$", path.read_text(encoding="utf-8"), re.M).group(1)
        assert f'<a href="/docs/{path.stem}">{titles[path.stem]}</a>' in html, path.stem
    assert result_slugs(html) == sorted(titles, key=lambda slug: titles[slug].lower())


def test_page_renders_its_heading_date_and_rewritten_links(client):
    response = client.get("/docs/geocode")
    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "<h1>Geocode an address</h1>" in html
    assert html.count("<h1>") == 1
    assert "Updated 2026-06-23" in html
    assert 'href="/docs/migrating-from-v1"' in html
    assert ".md" not in html


def test_every_relative_link_form_is_rewritten(tmp_path, db_path, monkeypatch):
    monkeypatch.delenv("MARLOW_MODEL", raising=False)
    monkeypatch.setattr("desk.docs_site.DOCS_DIR", tmp_path)
    (tmp_path / "start.md").write_text(
        "---\ntitle: Start\nupdated: 2026-01-05\n---\n\n# Start\n\n"
        "[a](./keys.md) [b](keys.md#rotation) [c](./keys.md#rotation) [d](https://api.marlowmaps.com)\n",
        encoding="utf-8",
    )
    html = create_app(db_path, seed_path=None).test_client().get("/docs/start").get_data(as_text=True)
    assert re.findall(r'href="([^"]*)"', html) == [
        "/docs", "/docs/keys", "/docs/keys#rotation", "/docs/keys#rotation", "https://api.marlowmaps.com",
    ]


def test_unknown_page_is_404(client):
    assert client.get("/docs/no-such-page").status_code == 404


def test_search_puts_the_one_page_with_the_word_in_its_title_first(client):
    html = client.get("/docs/search?q=precision").get_data(as_text=True)
    slugs = result_slugs(html)
    assert slugs[0] == "precision"
    assert len(slugs) > 1
    assert "precision" in html.split("<li>")[1].split("<p>")[1].lower()


def test_search_without_a_hit_says_no_pages_match(client):
    for query in ("zzzz", "", "how do i"):
        html = client.get("/docs/search", query_string={"q": query}).get_data(as_text=True)
        assert "No pages match." in html
        assert result_slugs(html) == []


def test_search_query_is_escaped(client):
    html = client.get("/docs/search", query_string={"q": "<script>"}).get_data(as_text=True)
    assert "<script>" not in html
    assert 'value="&lt;script&gt;"' in html


def test_search_form_and_footer_are_on_a_rendered_page(client):
    html = client.get("/docs/routes").get_data(as_text=True)
    assert '<form action="/docs/search" method="get">' in html
    assert '<input type="text" name="q"' in html
    assert ">Search</button>" in html
    assert "Still stuck? Open a ticket with the support desk (POST /tickets)." in html
