from datetime import datetime, timedelta, timezone

from conftest import future, past

URL = "https://example.com/e"


def test_expired_link_returns_410(client, make_link):
    make_link(code="oldlink", expires_at=datetime.now(timezone.utc) - timedelta(minutes=5))
    r = client.get("/oldlink")
    assert r.status_code == 410
    assert "location" not in r.headers


def test_expired_link_does_not_count_clicks(client, make_link, get_clicks):
    make_link(
        code="oldlink", expires_at=datetime.now(timezone.utc) - timedelta(minutes=5), clicks=4
    )
    for _ in range(3):
        assert client.get("/oldlink").status_code == 410
    assert get_clicks("oldlink") == 4


def test_link_with_future_expiry_still_redirects(client):
    client.post("/api/links", json={"url": URL, "alias": "soon", "expires_at": future(1)})
    assert client.get("/soon").status_code == 307


def test_expiry_in_past_rejected(client):
    assert client.post("/api/links", json={"url": URL, "expires_at": past(1)}).status_code == 422


def test_naive_past_expiry_rejected(client):
    r = client.post("/api/links", json={"url": URL, "expires_at": "2000-01-01T00:00:00"})
    assert r.status_code == 422


def test_invalid_expiry_format_rejected(client):
    r = client.post("/api/links", json={"url": URL, "expires_at": "not-a-date"})
    assert r.status_code == 422


def test_expiry_with_timezone_offset_converted_to_utc(client):
    exp = (datetime.now(timezone.utc) + timedelta(days=1)).astimezone(
        timezone(timedelta(hours=5, minutes=30))
    )
    r = client.post("/api/links", json={"url": URL, "expires_at": exp.isoformat()})
    assert r.status_code == 201
    got = datetime.fromisoformat(r.json()["expires_at"].replace("Z", "+00:00"))
    assert got.utcoffset() == timedelta(0)
    assert abs((got - exp).total_seconds()) < 1
