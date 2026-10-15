# SPDX-License-Identifier: AGPL-3.0-only
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_is_read_only_and_minimal():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "release": "alpha-0.1"}
    assert response.headers["cache-control"] == "no-store"

def test_catalog_is_valid_and_read_only():
    response = client.get("/api/catalog")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "sample-only"
    assert len(payload["tracks"]) >= 3
    assert client.post("/api/catalog", json={}).status_code == 405

def test_home_is_accessible_and_local():
    response = client.get("/")
    assert response.status_code == 200
    assert '<main id="main-content"' in response.text
    assert 'Skip to main content' in response.text
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "script-src 'self'" in response.headers["content-security-policy"]
    assert "WonderNet" in response.text

def test_assets_served_locally():
    response = client.get("/assets/styles.css")
    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert client.get("/assets/main.js").status_code == 200


def test_frontend_uses_only_local_runtime_assets():
    html = client.get("/").text.lower()
    css = client.get("/assets/styles.css").text.lower()
    assert '<script src="http' not in html
    assert '<link rel="stylesheet" href="http' not in html
    assert "@import url(" not in css
    assert "https://" not in css


def test_unimplemented_sensitive_endpoints_are_not_exposed():
    for path in ("/api/upload", "/api/execute", "/api/users", "/admin"):
        assert client.get(path).status_code == 404
        assert client.post(path).status_code == 404

def test_all_six_sections_have_real_pages():
    from backend.app.main import SECTIONS
    homepage = client.get("/").text
    for slug in SECTIONS:
        url = f"/explore/{slug}"
        assert f'href="{url}"' in homepage
        response = client.get(url)
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/html")
        assert '<main id="main-content"' in response.text
        assert "ALPHA 0.1" in response.text
        assert 'href="/assets/section-pages.css"' in response.text


def test_section_routes_are_allowlisted():
    for url in ("/explore/not-real", "/play/not-real", "/explore/admin", "/play/execute"):
        assert client.get(url).status_code == 404


def test_tiny_activities_are_served_locally_without_accounts():
    for activity in ("letter-match", "patterns"):
        response = client.get(f"/play/{activity}")
        assert response.status_code == 200
        assert f'data-activity="{activity}"' in response.text
        assert 'src="/assets/activities.js"' in response.text
        assert "No account" in response.text
        assert "script-src 'self'" in response.headers["content-security-policy"]
    script = client.get("/assets/activities.js")
    assert script.status_code == 200
    assert "questionSets" in script.text
    assert "localStorage" not in script.text
    assert "fetch(" not in script.text
    assert client.get("/assets/activities.css").status_code == 200
    assert client.get("/assets/section-pages.css").status_code == 200


def test_section_pages_do_not_load_third_party_assets():
    for url in ("/explore/early-learning", "/explore/wonderparty", "/play/letter-match"):
        html = client.get(url).text
        assert 'src="https://' not in html
        assert 'href="https://' not in html or "github.com/KadenBar/wondernet" in html
        assert "<script " not in html or 'src="/assets/activities.js"' in html
