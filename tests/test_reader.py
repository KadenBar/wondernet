# SPDX-License-Identifier: AGPL-3.0-only
"""Local, allowlisted, non-uploadable reader for one original prototype story."""
import json
import re
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_exactly_one_declared_original_demo_is_locally_readable():
    manifest = json.loads((ROOT / "library/reader-demos.json").read_text(encoding="utf-8"))
    assert manifest["schema_version"] == 1
    assert manifest["collection"] == "original-reader-demos"
    assert len(manifest["books"]) == 1
    book = manifest["books"][0]
    assert book["id"] == "lantern"
    assert book["chapters"] == 5
    assert book["source_file"] == "frontend/pages/book-lantern.html"
    assert book["local_route"] == "/read/lantern"
    assert book["rights"]["classification"] == "AGPL-3.0-only"
    assert book["rights"]["third_party_media"] is False
    assert book["review"]["child_use"] == "not-approved"
    assert book["review"]["editorial"] == "prototype-not-reviewed"
    assert book["network_required_by_story"] is False
    assert book["account_required"] is False


def test_story_and_all_five_chapters_are_in_local_html_without_scripts_from_elsewhere():
    response = client.get("/read/lantern")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "script-src 'self'" in response.headers["content-security-policy"]
    html = response.text
    assert '<main class="reader-main" id="main-content">' in html
    assert '<h1 id="book-title">' in html
    assert 'href="/explore/library"' in html
    assert 'src="/assets/book-reader.js"' in html
    assert 'href="/assets/book-reader.css"' in html
    assert '<progress id="reader-progress" max="5" value="1"' in html
    assert 'id="reader-larger"' in html
    assert 'id="reader-smaller"' in html
    assert 'id="reader-next"' in html
    assert 'id="reader-previous"' in html
    assert html.count('name="reading-theme"') == 3
    assert html.count('class="reader-chapter"') == 5
    assert sorted(int(n) for n in re.findall(r'id="chapter-([1-5])"', html)) == [1, 2, 3, 4, 5]
    assert html.count('data-open-chapter="') == 5
    for word in ("Pip", "Moss", "Hush", "THE END"):
        assert word in html
    assert "not a reviewed children's book" not in html or "Not an age-reviewed book" in html
    assert "not approved for unsupervised child use" in html
    assert 'href="https://' not in html
    assert 'src="https://' not in html
    assert "<iframe" not in html
    assert "<form" not in html
    assert "<script>" not in html


def test_reader_has_no_unapproved_book_access_or_external_dependencies():
    for path in ("/read/alice-wonderland", "/read/../../admin", "/read/secret-garden",
                 "/read/unknown", "/read/lantern/anything", "/api/library/upload"):
        assert client.get(path).status_code == 404
    assert client.post("/read/lantern").status_code == 405
    for asset in ("book-reader.css", "book-reader.js"):
        response = client.get("/assets/" + asset)
        assert response.status_code == 200
        content = response.text
        assert "https://" not in content
        assert "fetch(" not in content
        assert "localStorage" not in content
        assert "sessionStorage" not in content
        assert "eval(" not in content


def test_library_distinguishes_original_demo_from_unapproved_candidates():
    html = client.get("/explore/library").text
    assert 'href="/read/lantern"' in html
    assert "The Lantern That Kept the Stars" in html
    assert "Original WonderNet demo" in html
    assert html.count('data-book-id="') == 11
    assert "11 books we're looking into" in html
    assert "not approved" not in html or "not a child-ready collection" in html
