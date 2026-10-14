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
