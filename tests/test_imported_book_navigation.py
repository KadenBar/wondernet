"""Protect chapter and story navigation across imported offline editions."""
from html.parser import HTMLParser
from pathlib import Path

PAGES = Path(__file__).resolve().parents[1] / "frontend" / "pages"
EXPECTED = {
    "sherlock-adventures": 6,
    "oliver-twist": 53,
    "hound-baskervilles": 15,
    "great-expectations": 59,
    "kidnapped": 30,
    "sign-of-four": 12,
    "first-men-moon": 26,
    "pollyanna": 32,
    "pinocchio": 36,
    "children-new-forest": 27,
    "enchanted-castle": 12,
    "magic-city": 12,
    "white-company": 38,
    "scarlet-pimpernel": 31,
    "prisoner-of-zenda": 22,
    "last-man": 30,
    "scarlet-letter": 24,
    "dorian-gray": 20,
    "food-of-the-gods": 12,
    "man-iron-mask": 58,
    "lost-world": 16,
    "phantom-of-the-opera": 26,
    "return-sherlock": 13,
    "island-doctor-moreau": 22,
    "rebecca-sunnybrook": 31,
    "book-of-dragons": 8,
    "tale-two-cities": 45,
}


class Navigation(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicates = set()
        self.targets = []
        self.heading_ids = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        identifier = a.get("id")
        if identifier:
            if identifier in self.ids:
                self.duplicates.add(identifier)
            self.ids.add(identifier)
            if tag in ("h2", "h3"):
                self.heading_ids.add(identifier)
        if tag == "a" and a.get("href", "").startswith(("#chapter-", "#story-")):
            self.targets.append(a["href"][1:])


def test_imported_book_chapter_links_are_unique_and_point_to_headings():
    for slug, expected in EXPECTED.items():
        parser = Navigation()
        parser.feed((PAGES / f"book-{slug}.html").read_text(encoding="utf-8"))
        assert not parser.duplicates, (slug, parser.duplicates)
        assert len(parser.targets) == expected, (slug, len(parser.targets), expected)
        assert len(set(parser.targets)) == expected, slug
        assert set(parser.targets) <= parser.heading_ids, slug
