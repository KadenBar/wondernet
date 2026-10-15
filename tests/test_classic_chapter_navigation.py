"""Regression tests for semantic offline classic chapter navigation."""
from html.parser import HTMLParser
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "frontend" / "pages"

class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.headings = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href", "").startswith("#chapter-"):
            self.links.append(attrs["href"][1:])
        if tag == "a" and attrs.get("href", "").startswith("#part-"):
            self.links.append(attrs["href"][1:])
        if tag in ("h2", "h3"):
            self.headings.append(tag)

def test_dracula_has_27_real_chapter_targets():
    html = (PAGES / "book-dracula.html").read_text(encoding="utf-8")
    structure = Structure()
    structure.feed(html)
    assert len(structure.links) == 27
    assert len(set(structure.links)) == 27
    assert set(structure.links) <= structure.ids
    assert all(f'<h2 id="chapter-{n}">' in html for n in range(1, 28))

def test_study_in_scarlet_has_two_parts_and_fourteen_chapters():
    html = (PAGES / "book-study-in-scarlet.html").read_text(encoding="utf-8")
    structure = Structure()
    structure.feed(html)
    assert '<h2 id="part-1">' in html
    assert '<h2 id="part-2">' in html
    assert len(structure.links) == 14
    assert len(set(structure.links)) == 14
    assert set(structure.links) <= structure.ids
    assert all(f'<h3 id="part-{part}-chapter-{n}">' in html for part in (1, 2) for n in range(1, 8))
