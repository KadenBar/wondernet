# SPDX-License-Identifier: AGPL-3.0-only
"""Audit the 51 imported offline editions without granting editorial approval.

Run: python scripts/audit_offline_editions.py
Prints JSON for review; nonzero exit only for structural/security failures.
"""
from __future__ import annotations
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "frontend" / "pages"
BOOK_IDS = """wonderful-wizard-oz secret-garden anne-green-gables peter-and-wendy wind-in-the-willows jungle-book heidi tom-sawyer call-of-the-wild railway-children five-children-and-it princess-and-the-goblin war-of-the-worlds yellow-fairy-book violet-fairy-book pink-fairy-book brown-fairy-book crimson-fairy-book sherlock-adventures hound-baskervilles study-in-scarlet island-doctor-moreau lost-world kidnapped sign-of-four return-sherlock first-men-moon pollyanna pinocchio rebecca-sunnybrook children-new-forest book-of-dragons enchanted-castle magic-city white-company squirrel-nutkin timmy-tiptoes flopsy-bunnies scarlet-pimpernel prisoner-of-zenda scarlet-letter oliver-twist great-expectations tale-two-cities man-iron-mask last-man sleepy-hollow dorian-gray dracula food-of-the-gods phantom-of-the-opera""".split()
OLDER_READER = set("""dracula dorian-gray island-doctor-moreau war-of-the-worlds scarlet-letter last-man phantom-of-the-opera food-of-the-gods sleepy-hollow""".split())

class ReaderParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = {}
        self.links = []
        self.ids = set()
        self.scripts = 0
        self.remote_media = []
    def handle_starttag(self, tag, attrs):
        self.tags[tag] = self.tags.get(tag, 0) + 1
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "script":
            self.scripts += 1
        if tag == "a" and a.get("href", "").startswith("#"):
            self.links.append(a["href"][1:])
        if tag in ("img", "script", "iframe", "audio", "video", "source"):
            if a.get("src", "").startswith(("http:", "https:", "//")):
                self.remote_media.append(a["src"])

def audit_page(slug, html):
    parser = ReaderParser()
    parser.feed(html)
    findings = []
    if parser.tags.get("main", 0) != 1 or not parser.tags.get("h1"):
        findings.append("missing main landmark or book heading")
    if parser.scripts or parser.remote_media:
        findings.append("active script or remote media")
    if any(target not in parser.ids for target in parser.links):
        findings.append("broken in-page navigation")
    if not re.search(r"Content-Security-Policy", html, re.I):
        findings.append("missing content security policy")
    if not re.search(r"Project Gutenberg|GITenberg", html, re.I):
        findings.append("missing source attribution")
    advisory = []
    if not parser.tags.get("nav") or not parser.tags.get("h2"):
        advisory.append("chapter navigation or semantic headings missing")
    if "[Illustration" in html:
        advisory.append("source illustration placeholders remain; artwork not reproduced")
        if slug in {"flopsy-bunnies", "squirrel-nutkin", "timmy-tiptoes", "book-of-dragons"}:
            advisory.append("illustration-dependent edition: do not treat text-only rendering as a complete illustrated reading experience")
    if re.search(r"(?m)<p>\s*(?:CHAPTER\s+[IVXLCDM0-9]+|ADVENTURE\s+[IVXLCDM0-9]+)", html):
        advisory.append("chapter markers remain plain paragraphs")
    if slug in OLDER_READER:
        advisory.append("older-reader content: manual suitability review required")
    advisory.append("rights, edition fidelity, and accessibility require independent review")
    return {"id": slug, "errors": findings, "review_flags": advisory}

def audit(root=PAGES):
    return [audit_page(slug, (root / ("book-" + slug + ".html")).read_text(encoding="utf-8"))
            for slug in BOOK_IDS]

def main():
    reports = audit()
    print(json.dumps({"books": len(reports), "structural_failures": sum(bool(x["errors"]) for x in reports),
                      "reports": reports}, indent=2))
    raise SystemExit(1 if any(x["errors"] for x in reports) else 0)

if __name__ == "__main__":
    main()
