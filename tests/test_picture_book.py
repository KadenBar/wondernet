# SPDX-License-Identifier: AGPL-3.0-only
"""One original, eight-spread illustrated bilingual book, still pending review."""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from fastapi.testclient import TestClient
from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "frontend/assets"
MANIFEST = json.loads((ROOT / "library/picture-books.json").read_text(encoding="utf-8"))
client = TestClient(app)

ENGLISH_LINES = [
    "In the courtyard behind Mara",
    "Mara found a red wagon",
    "They filled the wagon with soil",
    "Mara rolled the garden into the courtyard",
    "Under the stairs it was too dark",
    "Near the bench, the path was wide and smooth",
    "A week later, bean vines climbed",
    "Mara tied a sign to the wagon",
]
SPANISH_LINES = [
    "En el patio detrás del edificio de Mara",
    "Mara encontró un carrito rojo",
    "Llenaron el carrito con tierra",
    "Mara llevó el jardín al patio",
    "Debajo de las escaleras había demasiada sombra",
    "Cerca del banco, el camino era ancho y liso",
    "Una semana después, los frijoles treparon",
    "Mara ató un letrero al carrito",
]


def test_original_book_rights_and_review_status_are_explicit_and_separate():
    assert MANIFEST["schema_version"] == 1
    assert MANIFEST["collection"] == "original-illustrated-bilingual-picture-books"
    assert MANIFEST["status"] == "developer-preview-only-not-child-approved"
    assert len(MANIFEST["books"]) == 1
    book = MANIFEST["books"][0]
    assert book["id"] == "mara-garden"
    assert book["route"] == "/read/mara-garden"
    assert book["rights"]["content_license"] == "CC-BY-4.0"
    assert "CC BY 4.0" in (ROOT / "library/PICTURE-BOOK-LICENSE.md").read_text()
    assert "AGPL-3.0-only" in (ROOT / "library/PICTURE-BOOK-LICENSE.md").read_text()
    assert {lang["code"] for lang in book["languages"]} == {"en", "es"}
    assert book["review"]["spanish_translation"] == "pending"
    assert book["review"]["screen_reader"] == "pending"
    assert book["review"]["editorial"] == "pending"
    assert book["review"]["child_use"] == "not-approved"
    assert not book["network_required"]
    assert not book["analytics"]
    assert not book["files_uploaded"]
    assert len(book["illustrations"]) == 8


def test_all_eight_local_original_svg_illustrations_are_safe_and_accessible():
    book = MANIFEST["books"][0]
    for index, file in enumerate(book["illustrations"], 1):
        assert file == f"frontend/assets/books/mara-garden/page-{index}.svg"
        data = (ROOT / file).read_text(encoding="utf-8")
        svg = ET.fromstring(data)
        assert svg.tag == "{http://www.w3.org/2000/svg}svg"
        assert svg.attrib["viewBox"] == "0 0 900 550"
        assert len(list(svg)) >= 5
        assert svg.find("{http://www.w3.org/2000/svg}title") is not None
        assert svg.find("{http://www.w3.org/2000/svg}desc") is not None
        lowered = data.lower()
        for forbidden in ("<script", "foreignobject", "<iframe", "http://", "https://",
                          "javascript:", "onload=", "onerror=", "<image", "<use ", "@import"):
            assert forbidden not in lowered, (file, forbidden)
        response = client.get(f"/assets/books/mara-garden/page-{index}.svg")
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("image/svg+xml")
        assert response.text == data


def test_eight_complete_bilingual_spreads_with_local_images_and_accessible_titles():
    res = client.get("/read/mara-garden")
    assert res.status_code == 200
    assert "script-src 'self'" in res.headers["content-security-policy"]
    assert "img-src 'self' data:" in res.headers["content-security-policy"]
    html = res.text
    assert html.count('class="reader-chapter story-spread"') == 8
    assert html.count('data-open-chapter="') == 8
    assert html.count('class="story-illustration"') == 8
    assert html.count('class="story-language-group" data-story-lang="en" lang="en"') == 8
    assert html.count('class="story-language-group" data-story-lang="es" lang="es" hidden') == 8
    assert html.count('data-alt-en=') == 8
    assert html.count('data-alt-es=') == 8
    assert '<select id="reader-language"' in html
    assert '<option value="en" selected>' in html
    assert '<option value="es" lang="es">' in html
    assert 'href="/assets/picture-books.css"' in html
    assert 'src="/assets/book-reader.js?v=bilingual1"' in html
    assert 'data-reader-unit="Page"' in html
    for i in range(1, 9):
        assert f'id="chapter-{i}"' in html
        assert f'/assets/books/mara-garden/page-{i}.svg' in html
    for line in ENGLISH_LINES + SPANISH_LINES:
        assert line in html
    assert "THIS GARDEN BELONGS TO EVERYONE" in html
    assert "ESTE JARDÍN ES DE TODOS" in html
    assert 'href="https://' not in html
    assert 'src="https://' not in html
    assert "<script>" not in html
    assert "<iframe" not in html
    assert "not approved for unsupervised child use" in html
    for asset in ("picture-books.css", "book-reader.js"):
        resp = client.get("/assets/" + asset)
        assert resp.status_code == 200
        assert "fetch(" not in resp.text
        assert "localStorage" not in resp.text
        assert "sessionStorage" not in resp.text


def test_library_has_new_feature_but_keeps_unapproved_research_queue_separate():
    html = client.get("/explore/library").text
    assert 'href="/read/mara-garden"' in html
    assert 'src="/assets/books/mara-garden/page-7.svg"' in html
    assert "Mara's Moving Garden" in html
    assert "El jardín viajero de Mara" in html
    assert 'href="/read/lantern"' in html
    assert html.count('data-readable="') == 5
    assert html.count('data-book-id="') == 11
    assert "11 books we're looking into." in html
    assert client.get("/read/cloud-of-trash").status_code == 404
    assert client.get("/read/mara-garden/edit").status_code == 404
    assert client.post("/read/mara-garden").status_code == 405
    assert client.post("/api/library/upload").status_code == 404
