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
        assert 'href="https://' not in html
        assert "<script " not in html or 'src="/assets/activities.js"' in html


def test_homepage_puts_real_demos_before_future_features():
    html = client.get("/").text
    assert 'href="/play/letter-match"' in html
    assert 'href="/play/patterns"' in html
    assert 'href="/assets/home.css"' in html
    assert "safer offline internet for kids" in html
    assert "Free code. Open doors." in html
    assert "Pi Wi-Fi network is planned" in html
    assert 'id="next-up"' in html


def test_learner_homepage_has_no_outbound_links_or_remote_assets():
    html = client.get("/").text
    assert 'href="https://' not in html
    assert 'src="https://' not in html
    assert "github.com/KadenBar/wondernet" in html  # text only for local deployments
    assert "Developer preview" not in html  # banner belongs to the public export


def test_all_interior_pages_use_the_handmade_design_and_local_assets():
    from backend.app.main import SECTIONS
    for section in SECTIONS:
        html = client.get(f"/explore/{section}").text
        assert f'class="interior-page section--{section}"' in html
        assert 'href="/assets/interiors.css"' in html
        assert 'class="detail-scene"' in html
        if section == "arcade":
            assert "CIRCUIT GARDEN" in html
        else:
            assert "CONCEPT ART" in html
        assert 'href="https://' not in html
        assert 'src="https://' not in html
    for game in ("letter-match", "patterns"):
        html = client.get(f"/play/{game}").text
        assert f'class="interior-page game--{game}"' in html
        assert 'href="/assets/interiors.css"' in html
        assert 'id="activity-meter"' in html
        assert 'max="5" value="0"' in html
        assert "No account" in html
        assert 'href="https://' not in html
        assert 'src="https://' not in html
    assert client.get("/assets/interiors.css").status_code == 200


def test_game_progress_remains_in_browser_memory_only():
    script = client.get("/assets/activities.js").text
    assert 'document.getElementById("activity-meter")' in script
    assert "meter.value = index + 1" in script
    assert "meter.value = questions.length" in script
    assert "localStorage" not in script
    assert "sessionStorage" not in script
    assert "fetch(" not in script


def test_circuit_garden_is_a_complete_locally_served_game():
    html = client.get("/play/circuit-garden").text
    assert '<main id="main-content"' in html
    assert 'class="interior-page circuit-page"' in html
    assert 'id="cg-board"' in html
    assert 'id="cg-level-list"' in html
    assert 'id="cg-reset"' in html
    assert 'id="cg-hint"' in html
    assert 'src="/assets/circuit-engine.js"' in html
    assert 'src="/assets/circuit-garden.js"' in html
    assert 'href="/assets/circuit-garden.css"' in html
    assert "No timer" in html
    assert "not ready for unsupervised child use" in html
    assert "script-src 'self'" in client.get("/play/circuit-garden").headers["content-security-policy"]
    for url in ("/assets/circuit-engine.js", "/assets/circuit-garden.js", "/assets/circuit-garden.css"):
        response = client.get(url)
        assert response.status_code == 200
        assert "https://" not in response.text
        assert "localStorage" not in response.text
        assert "sessionStorage" not in response.text
        assert "fetch(" not in response.text
    assert 'href="https://' not in html
    assert 'src="https://' not in html


def test_circuit_garden_is_discoverable_without_disguising_practice_as_games():
    home = client.get("/").text
    arcade = client.get("/explore/arcade").text
    assert 'href="/play/circuit-garden"' in home
    assert 'href="/play/circuit-garden"' in arcade
    assert "practice activities" in home
    assert "PRACTICE" in arcade


def test_word_workshop_is_accessible_through_allowlisted_local_routes():
    html = client.get("/play/word-workshop").text
    assert 'id="ww-tray"' in html
    assert 'id="ww-slots"' in html
    assert 'id="ww-check"' in html
    assert 'id="ww-hint"' in html
    assert 'id="ww-world-list"' in html
    assert 'src="/assets/word-workshop-engine.js"' in html
    assert 'src="/assets/word-workshop.js"' in html
    assert 'href="/assets/word-workshop.css"' in html
    assert "not ready for unsupervised child use" in html
    assert 'href="https://' not in html
    assert 'src="https://' not in html
    assert "script-src 'self'" in client.get("/play/word-workshop").headers["content-security-policy"]
    for path in ("word-workshop-engine.js", "word-workshop.js", "word-workshop.css"):
        response = client.get("/assets/" + path)
        assert response.status_code == 200
        assert "https://" not in response.text
        assert "localStorage" not in response.text
        assert "sessionStorage" not in response.text
        assert "fetch(" not in response.text


def test_word_workshop_is_visible_in_early_learning_and_on_homepage():
    home = client.get("/").text
    early = client.get("/explore/early-learning").text
    assert 'href="/play/word-workshop"' in home
    assert 'href="/play/word-workshop"' in early
    assert "Word Workshop" in home
    assert "Word Workshop" in early
    assert "not a validated phonics curriculum" in early
    assert client.get("/play/unknown-workshop").status_code == 404
