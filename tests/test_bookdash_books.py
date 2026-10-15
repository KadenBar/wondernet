# SPDX-License-Identifier: AGPL-3.0-only
"""Verified, fully local CC BY 4.0 Book Dash picture books."""
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)
MANIFEST = json.loads((ROOT / "library/bookdash-books.json").read_text(encoding="utf-8"))
HASHES = json.loads((ROOT / "library/bookdash-assets.sha256.json").read_text(encoding="utf-8"))
SLUGS = {"a-beautiful-day", "a-tiny-seed", "a-house-for-mouse", "come-back-cat", "walking-together"}


def git_sha1(contents):
    return hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()


def test_five_source_licensed_books_and_complete_local_media_are_pinned():
    assert MANIFEST["schema_version"] == 1
    assert MANIFEST["source_repo"] == "bookdash/bookdash-books"
    assert MANIFEST["source_ref"] == "54916310c5c06a5282e2d5d4add18d64f90e5fde"
    assert MANIFEST["license"] == "CC-BY-4.0"
    assert MANIFEST["status"] == "bundled-original-images-verified"
    assert len(MANIFEST["books"]) == 5
    assert {book["id"] for book in MANIFEST["books"]} == SLUGS
    assert len(HASHES) == 65
    for book in MANIFEST["books"]:
        assert book["author"] and book["illustrator"] and book["designer"]
        assert book["official_url"].startswith("https://bookdash.org/books/")
        assert book["source_md_sha"] and len(book["source_md_sha"]) == 40
        assert book["media_status"] == "locally-imported-verified"
        assert book["spread_count"] == 12
        assert book["review"]["child_use"] == "not-approved"
        assert book["review"]["editorial"] == "pending"
        assert book["review"]["accessibility"] == "pending"
        assert len(book["media"]) == 13
        assert {x["name"] for x in book["media"]} == {
            "cover.jpg", *(f"{i:02}.jpg" for i in range(1, 13))
        }
        for file in book["media"]:
            data = (ROOT / file["local_path"]).read_bytes()
            assert len(data) == file["bytes"]
            assert git_sha1(data) == file["git_blob_sha"]
            assert hashlib.sha256(data).hexdigest() == HASHES[file["local_path"]]
            assert data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9")
            assert len(data) < 240000


def test_each_complete_book_has_twelve_local_original_picture_spreads_and_credits():
    for book in MANIFEST["books"]:
        resp = client.get(book["local_route"])
        assert resp.status_code == 200
        assert "script-src 'self'" in resp.headers["content-security-policy"]
        html = resp.text
        assert f'<title>{book["title"]} | WonderNet Library</title>' in html
        assert 'href="/assets/bookdash-books.css"' in html
        assert 'src="/assets/book-reader.js?v=bookdash1"' in html
        assert f'Written by {book["author"]}' in html
        assert f'Illustrated by {book["illustrator"]}' in html
        assert f'Designed by {book["designer"]}' in html
        if book["editor"]:
            assert f'Edited by {book["editor"]}' in html
        assert "Creative Commons Attribution 4.0 International" in html
        assert "bookdash.org" in html
        assert 'data-reader-unit="Page"' in html
        assert html.count('class="reader-chapter dash-chapter"') == 12
        assert html.count('data-open-chapter="') == 12
        assert html.count('class="dash-spread"') == 12
        assert 'id="chapter-12"' in html
        assert f'src="/assets/books/bookdash/{book["id"]}/cover.jpg"' in html
        assert f'src="/assets/books/bookdash/{book["id"]}/01.jpg"' in html
        assert f'src="/assets/books/bookdash/{book["id"]}/12.jpg"' in html
        assert html.count("<p>") >= 10
        assert html.count('alt="') >= 13
        assert "THE END" in html
        assert "Not approved for unsupervised child use" in html
        assert 'href="https://' not in html
        assert 'src="https://' not in html
        assert "<iframe" not in html
        assert "<script>" not in html
        assert "site.image-set" not in html
        for name in ["cover.jpg", "01.jpg", "12.jpg"]:
            r = client.get(f"/assets/books/bookdash/{book['id']}/{name}")
            assert r.status_code == 200
            assert r.headers["content-type"].startswith("image/jpeg")
            assert len(r.content) > 1000
        assert client.post(book["local_route"]).status_code == 405


def test_library_displays_five_real_original_covers_and_keeps_candidate_rights_gates():
    html = client.get("/explore/library").text
    assert html.count('data-bookdash="') == 5
    assert html.count('data-readable="') == 5  # The previous Potter editions.
    assert html.count('data-book-id="') == 11   # Unapproved research queue.
    assert "Five beautiful picture books, ready to open." in html
    for book in MANIFEST["books"]:
        assert f'href="{book["local_route"]}"' in html
        assert f'/assets/books/bookdash/{book["id"]}/cover.jpg' in html
        assert book["illustrator"] in html
    assert 'href="/read/mara-garden"' in html  # Experimental SVG story demoted, not deleted.
    for blocked in ("/read/cloud-of-trash", "/read/alice-wonderland", "/api/library/upload"):
        assert client.get(blocked).status_code == 404
    assert client.post("/api/library/upload").status_code == 404


def test_media_import_pipeline_has_no_student_facing_remote_downloads():
    script = (ROOT / "scripts/import_bookdash.py").read_text(encoding="utf-8")
    assert '--verify-only' in script
    assert 'raw.githubusercontent.com' in script
    assert 'expected_sha' in script
    assert "MAX_BYTES" in script
    assert not (ROOT / ".github/workflows/import-bookdash-assets.yml").exists(), "one-time privileged workflow must be removed before merge"
    reader = client.get("/assets/book-reader.js")
    assert reader.status_code == 200
    assert "fetch(" not in reader.text
