# SPDX-License-Identifier: AGPL-3.0-only
"""Complete public-domain story text is bundled locally, with honest review gates."""
import json
import re
from html import unescape
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)
MANIFEST = json.loads((ROOT / "library/complete-text-editions.json").read_text(encoding="utf-8"))
OPENINGS = {
    "peter-rabbit": "Once upon a time there were four little Rabbits",
    "benjamin-bunny": "One morning a little rabbit sat on a bank.",
    "tom-kitten": "Once upon a time there were three little kittens",
    "jemima-puddle-duck": "What a funny sight it is to see a brood of ducklings",
    "jeremy-fisher": "Once upon a time there was a frog called Mr. Jeremy Fisher",
}
CLOSINGS = {
    "peter-rabbit": "bread and milk and blackberries for supper.",
    "benjamin-bunny": "the bunches of herbs and the rabbit-tobacco.",
    "tom-kitten": "have been looking for them ever since.",
    "jemima-puddle-duck": "but she had always been a bad sitter.",
    "jeremy-fisher": "THE END",
}


def test_catalog_tracks_five_distinct_complete_story_texts_with_specific_sources():
    items = MANIFEST["items"]
    assert MANIFEST["schema_version"] == 1
    assert MANIFEST["collection"] == "complete-public-domain-story-text-demos"
    assert len(items) == 5
    assert {i["id"] for i in items} == set(OPENINGS)
    assert len({i["source_ebook_number"] for i in items}) == 5
    for item in items:
        assert item["creator"] == "Beatrix Potter"
        assert item["local_text_status"] == "complete-story-text"
        assert item["source_landing"] == f'https://www.gutenberg.org/ebooks/{item["source_ebook_number"]}'
        assert re.fullmatch(r'[0-9a-f]{40}', item["source_blob_sha"])
        assert item["copyright"]["classification"] == "public-domain-US"
        assert item["copyright"]["territory"].startswith("United States")
        assert item["illustrations"]["original_source_illustrations_included"] is False
        assert "WonderNet" in item["illustrations"]["decoration"]
        assert item["review"]["child_use"] == "not-approved"
        assert item["review"]["editorial"] == "pending"
        assert item["review"]["accessibility"] == "pending"
        assert item["external_links_in_reader"] is False
        assert (ROOT / item["local_file"]).is_file()


def test_five_complete_stories_appear_on_read_only_pages_with_local_assets_and_endings():
    for item in MANIFEST["items"]:
        res = client.get(item["route"])
        assert res.status_code == 200
        assert res.headers["content-type"].startswith("text/html")
        assert res.headers["x-content-type-options"] == "nosniff"
        assert "script-src 'self'" in res.headers["content-security-policy"]
        html = res.text
        assert 'data-reader-unit="Page"' in html
        assert 'src="/assets/book-reader.js?v=editions1"' in html
        assert 'href="/assets/book-reader.css"' in html
        assert 'href="/explore/library"' in html
        assert f'<title>{item["title"]} | WonderNet Library</title>' in html
        assert html.count('class="reader-chapter"') == item["reading_pages"]
        assert html.count('data-open-chapter="') == item["reading_pages"]
        assert f'id="chapter-{item["reading_pages"]}"' in html
        assert OPENINGS[item["id"]] in unescape(html)
        assert CLOSINGS[item["id"]] in unescape(html)
        assert "original Beatrix Potter illustrations" not in html or "not included" in html
        assert "original period illustrations are" in html
        assert "United States" in html
        assert "not yet approved for unsupervised child use" in html
        assert 'src="https://' not in html
        assert 'href="https://' not in html
        assert "<iframe" not in html
        assert "<script>" not in html
        assert "Project Gutenberg EBook" not in html
        assert "www.gutenberg" not in html.lower()
        assert "End of Project Gutenberg" not in html
        assert "<svg " in html
        assert '<img ' not in html  # Historical image files were not imported.
        assert client.post(item["route"]).status_code == 405


def test_complete_story_text_is_not_just_a_preview_excerpt():
    for item in MANIFEST["items"]:
        html = client.get(item["route"]).text
        sections = re.findall(r'<section class="reader-chapter".*?</section>', html, flags=re.S)
        assert len(sections) == item["reading_pages"]
        narrative = []
        for section in sections:
            body = re.findall(r'<p>(.*?)</p>', section, flags=re.S)
            narrative += [unescape(re.sub(r'<[^>]+>', ' ', p)) for p in body]
        words = len(' '.join(narrative).split())
        assert words >= 650, (item["id"], words)
        assert abs(words - item["rough_word_count"]) < 35, (item["id"], words)
        assert len(narrative) >= 25, item["id"]


def test_existing_review_queue_remains_blocked_and_no_import_api_exists():
    library = client.get("/explore/library").text
    assert library.count('data-book-id="') == 11
    assert library.count('data-readable="') == 5
    assert 'id="lb-ready-query"' in library
    assert "11 books we're looking into." in library
    assert "not the original Beatrix Potter illustrations" in library
    assert 'href="/read/lantern"' in library
    for item in MANIFEST["items"]:
        assert f'href="{item["route"]}"' in library
    for rejected in ("/read/alice-wonderland", "/read/cloud-of-trash",
                     "/read/secret-garden", "/api/library/import", "/api/library/books"):
        assert client.get(rejected).status_code == 404
        assert client.post(rejected).status_code == 404
