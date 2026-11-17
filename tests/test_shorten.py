import re
import time
from datetime import datetime, timedelta, timezone

from conftest import future

URL = "https://example.com/some/long/path?x=1"


def test_shorten_valid_url_returns_201_with_code_and_short_url(client, base_url):
    r = client.post("/api/links", json={"url": URL})
    assert r.status_code == 201
    d = r.json()
    assert re.fullmatch(r"[A-Za-z0-9]{7}", d["code"])
    assert d["short_url"] == f"{base_url}/{d['code']}"
    assert d["original_url"] == URL
    assert d["clicks"] == 0
    assert d["expires_at"] is None
    assert d["created_at"]


def test_shorten_with_custom_alias_and_expiry(client, base_url):
    r = client.post("/api/links", json={"url": URL, "alias": "my-offer", "expires_at": future(2)})
    assert r.status_code == 201
    d = r.json()
    assert d["code"] == "my-offer"
    assert d["short_url"] == f"{base_url}/my-offer"
    assert d["expires_at"] is not None


def test_shorten_naive_expiry_is_treated_as_utc(client):
    r = client.post("/api/links", json={"url": URL, "expires_at": "2999-01-01T00:00:00"})
    assert r.status_code == 201
    assert r.json()["expires_at"].startswith("2999-01-01T00:00:00")


def test_two_links_get_different_codes(client):
    a = client.post("/api/links", json={"url": URL}).json()["code"]
    b = client.post("/api/links", json={"url": URL}).json()["code"]
    assert a != b


def test_health_endpoint(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_list_links_newest_first_with_status(client):
    for alias in ("first", "second", "third"):
        client.post("/api/links", json={"url": URL, "alias": alias})
        time.sleep(0.05)
    r = client.get("/api/links")
    assert r.status_code == 200
    items = r.json()
    assert [i["code"] for i in items] == ["third", "second", "first"]
    assert all(i["status"] == "active" for i in items)
    assert all("clicks" in i for i in items)


def test_list_links_shows_expired_status(client, make_link):
    make_link(code="gone", expires_at=datetime.now(timezone.utc) - timedelta(hours=1))
    client.post("/api/links", json={"url": URL, "alias": "alive"})
    items = {i["code"]: i for i in client.get("/api/links").json()}
    assert items["gone"]["status"] == "expired"
    assert items["alive"]["status"] == "active"


def test_list_links_empty(client):
    assert client.get("/api/links").json() == []
