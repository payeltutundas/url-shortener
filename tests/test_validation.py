from urllib.parse import urlparse

import pytest

LONG_OK = "https://example.com/" + "a" * (2048 - len("https://example.com/"))


def _post(client, url):
    return client.post("/api/links", json={"url": url})


@pytest.mark.parametrize(
    "url",
    [
        "",
        "   ",
        "javascript:alert(1)",
        "ftp://x.com",
        "data:text/html,<script>alert(1)</script>",
        "file:///etc/passwd",
        "http://",
        "https://",
        "https:///path-only",
        "not a url",
        "example.com",
        "//example.com",
    ],
)
def test_invalid_url_rejected_with_422(client, url):
    assert _post(client, url).status_code == 422


def test_too_long_url_rejected(client):
    assert _post(client, LONG_OK + "b").status_code == 422


def test_max_length_url_accepted(client):
    assert len(LONG_OK) == 2048
    assert _post(client, LONG_OK).status_code == 201


def test_own_short_domain_rejected(client, base_url):
    assert _post(client, base_url + "/abc1234").status_code == 422
    assert _post(client, base_url).status_code == 422


def test_own_domain_uppercase_host_rejected(client, base_url):
    p = urlparse(base_url)
    netloc = p.hostname.upper() + (f":{p.port}" if p.port else "")
    assert _post(client, f"{p.scheme}://{netloc}/x").status_code == 422


def test_same_host_different_port_allowed(client):
    assert _post(client, "http://localhost:9999/x").status_code == 201


def test_http_and_https_accepted(client):
    assert _post(client, "http://example.com").status_code == 201
    assert _post(client, "https://example.com/p?q=1#f").status_code == 201


def test_missing_url_field_rejected(client):
    assert client.post("/api/links", json={}).status_code == 422


def test_non_string_url_rejected(client):
    assert client.post("/api/links", json={"url": 123}).status_code == 422
