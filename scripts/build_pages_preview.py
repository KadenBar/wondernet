# SPDX-License-Identifier: AGPL-3.0-only
"""Build the public, static developer preview from the WonderNet frontend.

GitHub Pages cannot run FastAPI. Export only public HTML/CSS/JS, no backend,
API, library imports or future learner data.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
FRONTEND = ROOT / "frontend"
SECTIONS = (
    "early-learning", "academy", "special-interests",
    "arcade", "library", "wonderparty",
)
ACTIVITIES = ("letter-match", "patterns", "circuit-garden", "word-workshop")
READERS = {
    "lantern": "book-lantern.html",
    "winnie-the-pooh": "book-winnie-the-pooh.html",
    "velveteen-rabbit": "book-velveteen-rabbit.html",
    "a-beautiful-day": "book-a-beautiful-day.html",
    "a-tiny-seed": "book-a-tiny-seed.html",
    "a-house-for-mouse": "book-a-house-for-mouse.html",
    "come-back-cat": "book-come-back-cat.html",
    "walking-together": "book-walking-together.html",
    "mara-garden": "book-mara-garden.html",
    "peter-rabbit": "book-peter-rabbit.html",
    "benjamin-bunny": "book-benjamin-bunny.html",
    "tom-kitten": "book-tom-kitten.html",
    "jemima-puddle-duck": "book-jemima-puddle-duck.html",
    "jeremy-fisher": "book-jeremy-fisher.html",
    "wonderful-wizard-oz": "book-wonderful-wizard-oz.html",
    "secret-garden": "book-secret-garden.html",
    "anne-green-gables": "book-anne-green-gables.html",
    "peter-and-wendy": "book-peter-and-wendy.html",
}
ROUTES = {
    **{f"/explore/{slug}": f"/explore/{slug}/" for slug in SECTIONS},
    **{f"/play/{slug}": f"/play/{slug}/" for slug in ACTIVITIES},
    **{f"/read/{slug}": f"/read/{slug}/" for slug in READERS},
}
ATTRIBUTE = re.compile(
    r"""(?P<name>\b(?:href|src))(?P<equals>\s*=\s*)(?P<quote>["'])(?P<value>/[^"']*)(?P=quote)""",
    re.IGNORECASE,
)
WARNING = (
    '<div class="public-preview-notice" role="note">'
    '<strong>Developer preview · not a child-ready product.</strong> '
    'This site demonstrates early webpages, two practice activities, Circuit Garden, Word Workshop, a sample book reader, and five public-domain full-text stories (original historical illustrations not included). '
    'Full lessons, safety validation, offline Wi-Fi and multiplayer are not available yet. '
    '<a href="https://github.com/KadenBar/wondernet" rel="noopener noreferrer">Source code and feedback</a>.'
    "</div>"
)
SECURITY_META = (
    '<meta http-equiv="Content-Security-Policy" '
    'content="default-src &#39;self&#39;; script-src &#39;self&#39;; '
    'style-src &#39;self&#39;; img-src &#39;self&#39; data:; '
    'font-src &#39;self&#39;; connect-src &#39;none&#39;; '
    'object-src &#39;none&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">'
)
ROBOTS_META = '<meta name="robots" content="noindex,nofollow">'
BODY_TAG = re.compile(r"<body(?:\s[^>]*)?>", re.IGNORECASE)


def normalize_base_path(value: str) -> str:
    value = value.rstrip("/")
    if value == "":
        return ""
    if not value.startswith("/") or value.startswith("//"):
        raise ValueError("base path must start with a single '/'")
    if not re.fullmatch(r"/[A-Za-z0-9_-]+(?:/[A-Za-z0-9_-]+)*", value):
        raise ValueError("invalid base path")
    return value


def rewrite_url(url: str, base: str) -> str:
    """Convert root-relative local application routes to Pages directory URLs."""
    parsed = urlsplit(url)
    if parsed.scheme or parsed.netloc:
        raise ValueError(f"unexpected protocol-relative URL: {url}")
    path = parsed.path
    if path == "/":
        new_path = "/"
    elif path in ROUTES:
        new_path = ROUTES[path]
    elif path.startswith("/assets/"):
        if not (FRONTEND / path.lstrip("/")).is_file():
            raise ValueError(f"missing local asset: {url}")
        new_path = path
    else:
        raise ValueError(f"unknown local frontend link: {url}")
    return urlunsplit(("", "", f"{base}{new_path}", parsed.query, parsed.fragment))


def make_html(html: str, base: str) -> str:
    """Keep the actual app HTML while rewriting known local frontend URLs."""
    def rewrite(match: re.Match[str]) -> str:
        quote = match.group("quote")
        return (
            match.group("name") + match.group("equals") + quote
            + rewrite_url(match.group("value"), base) + quote
        )

    html = ATTRIBUTE.sub(rewrite, html)
    if "<head>" not in html or not BODY_TAG.search(html):
        raise ValueError("source HTML must contain <head> and a body tag")
    stylesheet = f'<link rel="stylesheet" href="{base}/assets/preview.css">'
    html = html.replace("<head>", "<head>" + ROBOTS_META + SECURITY_META + stylesheet, 1)
    return BODY_TAG.sub(lambda match: match.group(0) + WARNING, html, count=1)


def build(destination: Path, base_path: str) -> None:
    base = normalize_base_path(base_path)
    destination = destination.resolve()
    if destination == ROOT or destination == FRONTEND or FRONTEND in destination.parents:
        raise ValueError("output must not replace the source or repository")
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FRONTEND / "assets", destination / "assets", dirs_exist_ok=True)
    shutil.copyfile(ROOT / "scripts" / "preview.css", destination / "assets" / "preview.css")
    pages = [(FRONTEND / "index.html", destination / "index.html")]
    pages.extend(
        (FRONTEND / "pages" / f"{slug}.html",
         destination / "explore" / slug / "index.html")
        for slug in SECTIONS
    )
    pages.extend(
        (FRONTEND / "pages" / f"{slug}.html",
         destination / "play" / slug / "index.html")
        for slug in ACTIVITIES
    )
    pages.extend(
        (FRONTEND / "pages" / filename,
         destination / "read" / slug / "index.html")
        for slug, filename in READERS.items()
    )
    for source, output in pages:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(make_html(source.read_text(encoding="utf-8"), base), encoding="utf-8")
    (destination / ".nojekyll").write_text("", encoding="utf-8")
    print(f"Built {len(pages)} public preview pages at {destination} (prefix {base or '/'})")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("_site"))
    parser.add_argument("--base-path", type=str, default="/wondernet")
    args = parser.parse_args()
    build(args.output, args.base_path)


if __name__ == "__main__":
    main()
