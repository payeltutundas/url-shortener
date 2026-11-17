URL = "https://example.com/target?a=b"


def test_redirect_returns_307_to_original_url(client):
    code = client.post("/api/links", json={"url": URL}).json()["code"]
    r = client.get(f"/{code}")
    assert r.status_code == 307
    assert r.headers["location"] == URL


def test_click_count_increases_by_exactly_one_each_visit(client, get_clicks):
    code = client.post("/api/links", json={"url": URL}).json()["code"]
    for expected in (1, 2, 3):
        assert client.get(f"/{code}").status_code == 307
        assert get_clicks(code) == expected
    listed = [i for i in client.get("/api/links").json() if i["code"] == code][0]
    assert listed["clicks"] == 3


def test_unknown_code_returns_404(client):
    assert client.get("/doesnotexist").status_code == 404


def test_redirect_with_custom_alias(client):
    client.post("/api/links", json={"url": URL, "alias": "promo_1"})
    r = client.get("/promo_1")
    assert r.status_code == 307
    assert r.headers["location"] == URL


def test_alias_is_case_sensitive(client):
    client.post("/api/links", json={"url": URL, "alias": "Promo"})
    assert client.get("/promo").status_code == 404
    assert client.get("/Promo").status_code == 307
