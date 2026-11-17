import pytest

URL = "https://example.com/a"


def test_duplicate_alias_returns_409(client):
    assert client.post("/api/links", json={"url": URL, "alias": "taken"}).status_code == 201
    r = client.post("/api/links", json={"url": URL, "alias": "taken"})
    assert r.status_code == 409
    assert "taken" in r.json()["detail"].lower()


def test_alias_differing_only_in_case_is_a_different_alias(client):
    assert client.post("/api/links", json={"url": URL, "alias": "Taken"}).status_code == 201
    assert client.post("/api/links", json={"url": URL, "alias": "taken"}).status_code == 201


@pytest.mark.parametrize(
    "alias", ["has space", "bad!char", "sl/ash", "dot.dot", "ünï", "a%20b", "x@y"]
)
def test_alias_with_bad_characters_rejected(client, alias):
    assert client.post("/api/links", json={"url": URL, "alias": alias}).status_code == 422


@pytest.mark.parametrize("alias", ["a", "ab"])
def test_alias_too_short_rejected(client, alias):
    assert client.post("/api/links", json={"url": URL, "alias": alias}).status_code == 422


def test_alias_too_long_rejected(client):
    assert client.post("/api/links", json={"url": URL, "alias": "a" * 33}).status_code == 422


def test_alias_length_boundaries_accepted(client):
    assert client.post("/api/links", json={"url": URL, "alias": "abc"}).status_code == 201
    assert client.post("/api/links", json={"url": URL, "alias": "a" * 32}).status_code == 201


@pytest.mark.parametrize(
    "alias", ["api", "docs", "redoc", "health", "static", "assets", "API", "Docs"]
)
def test_reserved_alias_rejected(client, alias):
    assert client.post("/api/links", json={"url": URL, "alias": alias}).status_code == 422


@pytest.mark.parametrize("alias", ["openapi.json", "favicon.ico"])
def test_reserved_alias_with_dot_rejected(client, alias):
    # rejected either as reserved or as an invalid character
    assert client.post("/api/links", json={"url": URL, "alias": alias}).status_code == 422


def test_allowed_alias_characters(client):
    assert client.post("/api/links", json={"url": URL, "alias": "Az09_-x"}).status_code == 201


def test_empty_alias_gets_random_code(client):
    r = client.post("/api/links", json={"url": URL, "alias": ""})
    assert r.status_code == 201
    assert len(r.json()["code"]) == 7
