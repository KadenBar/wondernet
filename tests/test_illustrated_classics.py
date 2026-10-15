# SPDX-License-Identifier: AGPL-3.0-only
"""Both complete US-public-domain classics retain their original-era artwork."""
import hashlib
import json
from pathlib import Path

from fastapi.testclient import TestClient
from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)
MANIFEST = json.loads((ROOT / "library/illustrated-classics.json").read_text())
ASSET_HASHES = json.loads((ROOT / "library/illustrated-classics-assets.sha256.json").read_text())
PAGES = json.loads((ROOT / "library/illustrated-classics-pages.json").read_text())
SLUGS = {"winnie-the-pooh", "velveteen-rabbit"}
EXPECTED = {"winnie-the-pooh": (11, 115), "velveteen-rabbit": (15, 8)}


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def test_exactly_two_source_pinned_us_public_domain_editions():
    assert MANIFEST["schema_version"] == 1
    assert MANIFEST["territory"].startswith("United States")
    assert MANIFEST["content_review"] == "not approved for unsupervised use with children"
    assert len(MANIFEST["books"]) == 2
    assert {b["id"] for b in MANIFEST["books"]} == SLUGS
    assert len(ASSET_HASHES) == 123
    assert PAGES == {
        "velveteen-rabbit": {"pages": 15, "image_count": 8},
        "winnie-the-pooh": {"pages": 11, "image_count": 115},
    }
    for book in MANIFEST["books"]:
        slug = book["id"]
        assert book["author"] and book["illustrator"]
        assert book["sourceRepo"].startswith("GITenberg/")
        assert len(book["commit"]) == 40
        assert len(book["source_sha"]) == 40
        assert book["review"]["child_use"] == "not-approved"
        assert book["review"]["editorial"] == "pending"
        assert book["review"]["accessibility"] == "pending"
        assert book["year"] in (1922, 1926)
        assert len(book["images"]) == EXPECTED[slug][1]
        for media in book["images"]:
            file = ROOT / media["local"]
            data = file.read_bytes()
            assert len(data) == media["bytes"]
            assert git_blob_sha(data) == media["git_sha"]
            assert hashlib.sha256(data).hexdigest() == ASSET_HASHES[media["local"]]
            assert data.startswith(b"\xff\xd8\xff") and data.endswith(b"\xff\xd9")


def test_books_are_complete_local_read_only_with_original_illustrations():
    for book in MANIFEST["books"]:
        slug = book["id"]
        count, illustrations = EXPECTED[slug]
        response = client.get(book["route"])
        assert response.status_code == 200
        assert "script-src 'self'" in response.headers["content-security-policy"]
        markup = response.text
        assert f"<title>{book['title']} | WonderNet Library</title>" in markup
        assert 'src="/assets/book-reader.js?v=classic1"' in markup
        assert 'href="/assets/illustrated-classics.css"' in markup
        assert markup.count('class="reader-chapter classic-chapter"') == count
        assert markup.count('data-open-chapter="') == count
        assert markup.count('<figure class="classic-figure">') == (114 if slug == "winnie-the-pooh" else 8)
        assert f'id="chapter-{count}"' in markup
        assert book["author"] in markup and book["illustrator"] in markup
        assert "Original-era edition" in markup
        assert "not</strong> included" in markup
        assert "Adult developer preview" in markup
        assert 'src="https://' not in markup
        assert 'href="https://' not in markup
        assert '<script>' not in markup
        assert '<iframe' not in markup
        assert '*** END OF THE PROJECT GUTENBERG' not in markup
        assert client.post(book["route"]).status_code == 405
        for media in book["images"]:
            assert f'/assets/books/classics/{slug}/{media["name"]}' in markup
        jpg = book["images"][-1]
        r = client.get(f'/assets/books/classics/{slug}/{jpg["name"]}')
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/jpeg")
    pooh = client.get("/read/winnie-the-pooh").text
    assert "Here is Edward Bear" in pooh
    assert "CHAPTER X" in pooh
    assert "INTRODUCTION" not in pooh or "Introduction" in pooh
    assert 'data-reader-unit="Chapter"' in pooh
    rabbit = client.get("/read/velveteen-rabbit").text
    assert "THERE was once a velveteen rabbit" in rabbit
    assert "his own Bunny, come back to look at the child" in rabbit
    assert 'data-reader-unit="Page"' in rabbit


def test_library_features_recognizable_edition_covers_but_gates_old_candidates():
    html = client.get("/explore/library").text
    assert "14 readable stories + 11 research titles" in html
    assert 'class="lb-favorite-grid"' in html
    assert html.count('class="lb-favorite-card"') == 2
    for slug in SLUGS:
        assert f'href="/read/{slug}"' in html
        assert f'/assets/books/classics/{slug}/' in html
    assert html.count('data-bookdash="') == 5
    assert html.count('data-readable="') == 5
    assert html.count('data-book-id="') == 11
    assert client.get("/read/alice-wonderland").status_code == 404
    assert client.get("/api/library/upload").status_code == 404


def test_importer_never_becomes_runtime_downloader():
    script = (ROOT / "scripts/import_illustrated_classics.py").read_text()
    assert '--verify-only' in script
    assert 'blob_hash(data)' in script
    assert "raw.githubusercontent.com" in script
    assert "BeautifulSoup" in script
    assert not (ROOT / ".github/workflows/one-time-illustrated-classics.yml").exists(), "Remove elevated import workflow before PR merge"
    assert "fetch(" not in client.get("/assets/book-reader.js").text
