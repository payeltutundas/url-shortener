"""Loopback rule: when the app runs on a loopback address, every loopback name
on the app's own port is the app itself and must be rejected (422).
A different port is a different service and must be accepted (201).
The tests adapt to BASE_URL from the app settings."""
from urllib.parse import urlparse

import pytest

LOOPBACK_NAMES = ["localhost", "127.0.0.1", "::1", "0.0.0.0"]


def _fmt(host):
    return f"[{host}]" if ":" in host else host


def _own(base_url):
    p = urlparse(base_url)
    port = p.port or (443 if p.scheme == "https" else 80)
    return (p.hostname or "").lower(), port, p.scheme


def _post(client, url):
    return client.post("/api/links", json={"url": url})


def _skip_unless_loopback(base_url):
    host, _, _ = _own(base_url)
    if host not in LOOPBACK_NAMES:
        pytest.skip(f"BASE_URL host {host!r} is not a loopback name")


@pytest.mark.parametrize("name", LOOPBACK_NAMES)
def test_loopback_name_on_own_port_rejected(client, base_url, name):
    _skip_unless_loopback(base_url)
    _, port, _ = _own(base_url)
    r = _post(client, f"http://{_fmt(name)}:{port}/x")
    assert r.status_code == 422, r.text


@pytest.mark.parametrize("name", LOOPBACK_NAMES)
def test_loopback_name_on_other_port_accepted(client, base_url, name):
    _skip_unless_loopback(base_url)
    _, port, _ = _own(base_url)
    other = 9000 if port != 9000 else 9001
    r = _post(client, f"http://{_fmt(name)}:{other}/x")
    assert r.status_code == 201, r.text


@pytest.mark.parametrize("name", LOOPBACK_NAMES)
def test_loopback_name_https_on_own_port_rejected(client, base_url, name):
    _skip_unless_loopback(base_url)
    _, port, _ = _own(base_url)
    r = _post(client, f"https://{_fmt(name)}:{port}/x")
    assert r.status_code == 422, r.text
