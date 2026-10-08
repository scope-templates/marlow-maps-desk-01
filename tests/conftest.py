import pytest


@pytest.fixture
def db_path(tmp_path):
    return tmp_path / "desk.sqlite"


@pytest.fixture
def client(db_path, monkeypatch):
    monkeypatch.delenv("MARLOW_MODEL", raising=False)
    from desk.server import create_app

    return create_app(db_path, seed_path=None).test_client()


@pytest.fixture
def seeded_client(db_path, monkeypatch):
    monkeypatch.delenv("MARLOW_MODEL", raising=False)
    from desk.server import create_app

    return create_app(db_path).test_client()
