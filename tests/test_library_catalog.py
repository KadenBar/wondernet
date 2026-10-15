# SPDX-License-Identifier: AGPL-3.0-only
"""The library is a strictly gated research catalog, not a book downloader."""
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from fastapi.testclient import TestClient
from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "library" / "catalog.json"
FRONTEND = ROOT / "frontend"
client = TestClient(app)
ALLOWED_SOURCES = {"standardebooks.org", "storyweaver.org.in"}
ALL_GATES = {"rights_review", "content_review", "accessibility_review", "package_review"}


def test_first_library_catalog_is_traceable_and_explicitly_unapproved():
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    assert catalog["schema_version"] == 1
    assert catalog["status"] == "curation-only"
    assert len(catalog["items"]) == 11
    assert len({book["id"] for book in catalog["items"]}) == 11
    assert len({book["source_url"] for book in catalog["items"]}) == 11
    assert {"Standard Ebooks", "StoryWeaver"} == {book["source"] for book in catalog["items"]}
    for book in catalog["items"]:
        assert re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", book["id"])
        assert all(book[field] for field in ("title", "creator", "source", "source_url",
            "audience", "language", "collection", "review_note"))
        assert book["subjects"] and all(isinstance(s, str) and s for s in book["subjects"])
        source = urlparse(book["source_url"])
        assert source.scheme == "https"
        assert source.hostname in ALLOWED_SOURCES
        assert source.username is None and source.password is None
        assert set(book["gate"]) == ALL_GATES
        assert set(book["gate"].values()) == {"pending"}
        assert book["import_status"] == "not-imported"
        assert book["local_file"] is None
        assert book["sha256"] is None
        rights = book["rights"]
        assert all(rights[k] for k in ("classification", "territory", "edition_contributions", "license_url"))
        assert rights["license_url"].startswith("https://creativecommons.org/")
        if book["source"] == "Standard Ebooks":
            assert rights["classification"] == "PD-US"
            assert "United States" in rights["territory"]
        else:
            assert rights["classification"] == "CC-BY-4.0"
            assert "audio/readalongs excluded" in rights["territory"]


def test_library_preview_is_fully_local_and_unambiguously_research_only():
    books = json.loads(CATALOG.read_text(encoding="utf-8"))["items"]
    response = client.get("/explore/library")
    assert response.status_code == 200
    html = response.text
    assert 'id="research-shelf"' in html
    assert 'id="lb-query"' in html
    assert 'id="lb-kind"' in html
    assert 'href="/assets/library-shelf.css"' in html
    assert 'src="/assets/library-shelf.js"' in html
    assert "Nothing here is downloadable or readable on WonderNet yet." in html
    assert "not a child-ready collection" in html
    assert html.count('data-book-id="') == len(books)
    for book in books:
        assert f'data-book-id="{book["id"]}"' in html
        assert book["title"].replace("’", "’").replace("&", "&amp;") in html
    assert 'src="https://' not in html
    assert 'href="https://' not in html
    assert "standardebooks.org" not in html
    assert "storyweaver.org.in" not in html
    for asset in ("library-shelf.css", "library-shelf.js"):
        response = client.get("/assets/" + asset)
        assert response.status_code == 200
        assert "https://" not in response.text
        assert "fetch(" not in response.text
        assert "localStorage" not in response.text
        assert "sessionStorage" not in response.text


def test_research_only_has_no_file_import_or_open_download_endpoint():
    for path in ("/api/library/import", "/api/library/download", "/library/catalog.json",
                 "/library/book", "/api/library/books"):
        assert client.get(path).status_code == 404
        assert client.post(path).status_code == 404
