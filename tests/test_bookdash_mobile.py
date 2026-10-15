# SPDX-License-Identifier: AGPL-3.0-only
"""Mobile regression for five Book Dash cards after a phone image/text overlap."""
from pathlib import Path
from fastapi.testclient import TestClient
from backend.app.main import app

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(app)


def test_five_books_still_use_separate_cover_and_description_elements():
    page = client.get("/explore/library")
    assert page.status_code == 200
    html = page.text
    assert html.count('class="lb-dash-card"') == 5
    assert html.count('class="lb-dash-cover"') == 5
    assert html.count('class="lb-dash-meta"') == 5
    assert html.count('class="lb-dash-read"') == 5
    assert html.count('data-bookdash="') == 5
    assert 'href="/assets/library-shelf.css?v=mobile1"' in html


def test_mobile_book_cards_stack_cover_above_the_text_instead_of_overlapping():
    css = (ROOT / "frontend/assets/library-shelf.css").read_text(encoding="utf-8")
    assert "@media(max-width:680px)" in css
    mobile = css.split("@media(max-width:680px)", 1)[1]
    # No child cover may stretch to 100% of a text-height-driven grid row:
    # that interaction formerly expanded its intrinsic square aspect-ratio
    # and caused the cover to render underneath its sibling's text.
    assert ".lb-dash-grid{grid-template-columns:minmax(0,1fr)" in mobile
    assert ".lb-dash-card{display:flex;flex-direction:column" in mobile
    assert ".lb-dash-cover{box-sizing:border-box;display:block;width:100%" in mobile
    assert "height:auto;aspect-ratio:4/3" in mobile
    assert "border-bottom:2px solid #7da08c" in mobile
    assert ".lb-dash-meta{box-sizing:border-box;width:100%;min-width:0" in mobile
    assert "height:100%;border-right:" not in mobile
    assert "grid-template-columns:120px" not in mobile
    assert ".lb-dash-read{min-height:44px" in mobile


def test_desktop_book_grid_still_has_three_columns():
    css = (ROOT / "frontend/assets/library-shelf.css").read_text(encoding="utf-8")
    assert ".lb-dash-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr))" in css
    assert "@media(max-width:900px){.lb-dash-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}" in css


def test_new_mobile_layout_stylesheet_is_loaded_after_legacy_styles_and_exported():
    html = client.get("/explore/library").text
    assert 'href="/assets/library-shelf.css?v=mobile1"' in html
    assert 'href="/assets/bookdash-layout-v2.css"' in html
    assert html.index('/assets/library-shelf.css?v=mobile1') < html.index('/assets/bookdash-layout-v2.css')
    response = client.get("/assets/bookdash-layout-v2.css")
    assert response.status_code == 200
    assert "height:auto" in response.text
    assert "aspect-ratio:auto" in response.text
    assert "(pointer:coarse)" in response.text
    assert "flex:0 0 auto" in response.text
    # This is additive rather than modifying desktop cards or the older books.
    assert html.count('data-bookdash="') == 5
