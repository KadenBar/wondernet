#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Pin, sanitize and bundle TWO classic public-domain US illustrated editions.

Maintainer-only build operation; does not run when a user opens the library.
Raw third-party HTML is parsed into safe plain-text paragraphs and inert local
JPEG <img> tags. No arbitrary source URLs, HTML, scripts, or CSS survive.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_FILE = ROOT / "library/illustrated-classics.json"
SOURCE_HOST = "raw.githubusercontent.com"
MAX_FILE = 300_000
VALID_NAME = re.compile(r"^[a-z][a-z0-9-]+$")
VALID_MEDIA = re.compile(r"^[A-Za-z0-9_-]+\.jpg$")
ROMAN = {"I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"}


def blob_hash(contents: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(contents)).encode("ascii") + b"\0" + contents).hexdigest()


def get_source(book: dict, path: str, sha: str, size: int) -> bytes:
    owner, repo = book["sourceRepo"].split("/")
    if (owner, repo) != ("GITenberg", {"winnie-the-pooh": "Winnie-the-Pooh_67098",
                                       "velveteen-rabbit": "The-Velveteen-Rabbit_11757"}[book["id"]]):
        raise ValueError("Unexpected upstream repository")
    if any(not re.fullmatch(r"[0-9a-f]{40}", x) for x in (book["commit"], sha)):
        raise ValueError("Missing pinned Git commit/blob hashes")
    allow = {book["html"], *(m["source_path"] for m in book["images"])}
    if path not in allow or ".." in path or not re.fullmatch(r"[a-zA-Z0-9_./-]+", path):
        raise ValueError(f"Unapproved source path: {path}")
    address = f"https://{SOURCE_HOST}/{owner}/{repo}/{book['commit']}/{path}"
    request = Request(address, headers={"User-Agent": "WonderNet-PublicDomain-Importer/1.0"})
    with urlopen(request, timeout=60) as response:
        if urlparse(response.geturl()).hostname != SOURCE_HOST:
            raise ValueError("Source redirected to an unexpected host")
        data = response.read(MAX_FILE + 1)
    if not data or len(data) > MAX_FILE or len(data) != size:
        raise ValueError(f"Unexpected original image/source size: {path}")
    if blob_hash(data) != sha:
        raise ValueError(f"Upstream source Git blob SHA mismatch: {path}")
    return data


def as_text(tag) -> str:
    return " ".join(tag.stripped_strings)


def figure_tag(book: dict, name: str, alt: str = "") -> str:
    if name not in {m["name"] for m in book["images"]} or not VALID_MEDIA.fullmatch(name):
        raise ValueError(f"Unexpected source illustration: {name}")
    url = f"/assets/books/classics/{book['id']}/{name}"
    return f'<figure class="classic-figure"><img src="{url}" loading="lazy" alt="{html.escape(alt, quote=True)}"></figure>'


def original_images(tag) -> list[str]:
    return [img.get("src", "").replace("images/", "") for img in tag.find_all("img")
            if img.get("src", "").startswith("images/")]


def parse_pooh(source: bytes, book: dict) -> tuple[list[dict], set[str]]:
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(source.decode("utf-8-sig"), "html.parser")
    contents = list(soup.body.children)
    chapters: list[dict] = []
    active = None
    used = {"illus1.jpg", "illus2.jpg", "map.jpg"}
    for item in contents:
        if not isinstance(item, Tag):
            continue
        contents_text = as_text(item)
        if "*** END OF THE PROJECT GUTENBERG EBOOK" in contents_text:
            break
        if item.name == "p" and "Printed in Canada" in contents_text:
            break
        if item.name == "h2":
            label = contents_text.upper()
            if label == "INTRODUCTION":
                active = {"title": "Introduction", "elements": [figure_tag(book, "illus1.jpg", "Original E. H. Shepard frontispiece illustration")]}
                chapters.append(active)
                continue
            if label == "CONTENTS":
                active = None
                continue
            anchor = item.find("a", id=re.compile(r"^CHAPTER_(?:I|V|X)"))
            if anchor or re.fullmatch(r"CHAPTER (?:I|II|III|IV|V|VI|VII|VIII|IX|X)", label):
                active = {"title": contents_text.title(), "elements": []}
                if label == "CHAPTER I":
                    active["elements"].insert(0, figure_tag(book, "map.jpg", "Original Hundred Acre Wood map"))
                    active["elements"].insert(1, figure_tag(book, "illus2.jpg", "Original opening Shepard illustration"))
                chapters.append(active)
                continue
            if active is not None:
                active = None
        if active is None:
            continue
        if item.name == "h3":
            # Original chapter subtitles, normalized as section titles.
            active["title"] += " — " + as_text(item).capitalize()
            continue
        if item.name == "p":
            words = as_text(item)
            if words:
                active["elements"].append(f"<p>{html.escape(words)}</p>")
        elif item.name == "div":
            if "figcenter" in item.get("class", []):
                for image in original_images(item):
                    used.add(image)
                    active["elements"].append(figure_tag(book, image))
            elif "poetry" in item.get("class", []):
                lines = [as_text(x) for x in item.find_all(class_=re.compile(r"(?:verse|stanza)")) if
                         "verse" in x.get("class", [])]
                if not lines:
                    lines = [as_text(item)]
                if any(lines):
                    active["elements"].append('<p class="classic-verse">' +
                        "<br>".join(html.escape(s) for s in lines if s) + "</p>")
    if len(chapters) != 11 or not all(c["elements"] for c in chapters):
        raise ValueError(f"Expected the introduction plus ten full Pooh chapters, got {len(chapters)}")
    # All book illustrations should be referenced, with the extra frontispiece
    # and map added to their appropriate opening scenes.
    expected = {m["name"] for m in book["images"]}
    if used != expected - {"cover.jpg"}:
        raise ValueError(f"Pooh source artwork mismatch: missing={expected-used-{"cover.jpg"}}, extra={used-expected}")
    return chapters, used


def parse_velveteen(source: bytes, book: dict) -> tuple[list[dict], set[str]]:
    from bs4 import BeautifulSoup, Tag
    soup = BeautifulSoup(source.decode("ascii", errors="strict"), "html.parser")
    inside = False
    chunks: list[dict] = []
    current: list[str] = []
    count = 0
    used: set[str] = set()

    def flush():
        nonlocal current, count
        if current:
            chunks.append({"title": f"Story page {len(chunks)+1}", "elements": current})
            current = []
            count = 0

    for item in list(soup.body.children):
        if not isinstance(item, Tag) or item.name != "p":
            continue
        if not inside:
            if item.find("img", src=re.compile(r"^images/detail\.jpg$")):
                inside = True
            else:
                continue
        if "***ENDOFTHEPROJECTGUTENBERGEBOOK" in as_text(item).upper().replace(" ", ""):
            break
        images = original_images(item)
        plain = as_text(item)
        words = len(plain.split())
        if count > 180 and (count + words > 250 or images):
            flush()
        if images:
            for name in images:
                used.add(name)
                # Historical captions are separately present in the source.
                caption = item.find("i")
                description = as_text(caption) if caption else ""
                current.append(figure_tag(book, name, description))
        # Preserve story prose and actual illustration captions; do not embed
        # unsafe Gutenberg HTML or hyperlinks.
        if plain and not (plain == "\xa0"):
            current.append("<p>" + html.escape(plain) + "</p>")
        count += words
    flush()
    expected = {m["name"] for m in book["images"]}
    if not inside or used != expected or len(chunks) < 10 or len(chunks) > 35:
        raise ValueError(f"Velveteen full story parse failed: pages={len(chunks)}, images={used}")
    return chunks, used


def build_reader(book: dict, chapters: list[dict]) -> str:
    esc = html.escape
    total = len(chapters)
    title = esc(book["title"])
    description = esc(book["description"])
    page_html = []
    toc = []
    for n, page in enumerate(chapters, 1):
        heading = esc(page["title"])
        toc.append('<li><button type="button" data-open-chapter="' + str(n) + '"' +
                   (' aria-current="true"' if n == 1 else '') +
                   f'><span>{n:02}</span> {heading}</button></li>')
        page_html.append(f'<section class="reader-chapter classic-chapter" id="chapter-{n}" data-chapter="{n}" aria-labelledby="chapter-title-{n}"' +
            (' hidden' if n > 1 else '') +
            f'><p class="reader-chapter-number">{"CHAPTER" if book["id"] == "winnie-the-pooh" else "STORY PAGE"} {n} OF {total}</p>'
            f'<h2 id="chapter-title-{n}" tabindex="-1">{heading}</h2>' +
            "\n".join(page["elements"]) + "</section>")
    cover_name = book["cover"]
    cover_path = f"/assets/books/classics/{book['id']}/{cover_name}"
    notable = ("All 10 chapters and introduction · Original E. H. Shepard illustrations"
               if book["id"] == "winnie-the-pooh" else
               "Complete picture-book story · Original William Nicholson illustrations")
    source_url = f"https://www.gutenberg.org/ebooks/{book['pg']}"
    return f"""<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} | WonderNet Library</title>
<meta name="description" content="{description} Complete US-public-domain original illustrated edition.">
<link rel="stylesheet" href="/assets/styles.css"><link rel="stylesheet" href="/assets/section-pages.css"><link rel="stylesheet" href="/assets/interiors.css"><link rel="stylesheet" href="/assets/book-reader.css"><link rel="stylesheet" href="/assets/illustrated-classics.css">
<script defer src="/assets/book-reader.js?v=classic1"></script></head>
<body class="interior-page reader-page illustrated-classic" data-reader-theme="paper" data-reader-unit="{'Chapter' if book["id"] == "winnie-the-pooh" else "Page"}">
<a class="skip-link" href="#main-content">Skip to story</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="WonderNet home"><span class="brand-mark" aria-hidden="true">✳</span><span>Wonder<span class="brand-emphasis">Net</span></span><span class="alpha">ALPHA 0.1</span></a>
<nav class="site-nav" aria-label="Main navigation"><a href="/">Home</a><a href="/explore/library">Library</a></nav></div></header>
<main class="reader-main" id="main-content"><nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="/">Home</a><span aria-hidden="true">/</span><a href="/explore/library">Library</a><span aria-hidden="true">/</span><span aria-current="page">{title}</span></nav>
<section class="reader-cover" aria-labelledby="book-title"><div class="reader-cover-copy">
<p class="reader-kicker">✦ THE ORIGINAL ILLUSTRATED CLASSIC</p><h1 id="book-title">{title}</h1>
<p class="reader-byline">Written by {esc(book["author"])} · Illustrated by {esc(book["illustrator"])} · {book["year"]}</p>
<p class="reader-summary">{description}</p><span class="reader-sample">{notable} · US public domain</span></div>
<div class="reader-cover-art classic-cover"><img src="{cover_path}" alt="Historical illustration from the original {title} edition." width="650" height="650"></div></section>
<div class="reader-layout"><aside class="reader-sidebar" aria-label="Reading controls">
<section class="reader-toolbox" aria-labelledby="reader-tools-heading">
<p class="reader-eyebrow">MAKE IT YOURS</p><h2 id="reader-tools-heading">Reading tools</h2>
<div class="reader-settings-row"><span class="reader-setting-name" id="reader-size-label">Text size</span>
<div class="reader-size-buttons" role="group" aria-labelledby="reader-size-label">
<button type="button" id="reader-smaller" aria-label="Decrease text size">A−</button>
<output id="reader-size" aria-live="polite" aria-label="Text size">100%</output>
<button type="button" id="reader-larger" aria-label="Increase text size">A+</button></div></div>
<fieldset class="reader-themes"><legend>Page colors</legend>
<label><input type="radio" name="reading-theme" value="paper" checked><span class="reader-swatch reader-swatch-paper" aria-hidden="true"></span> Paper</label>
<label><input type="radio" name="reading-theme" value="night"><span class="reader-swatch reader-swatch-night" aria-hidden="true"></span> Night</label>
<label><input type="radio" name="reading-theme" value="contrast"><span class="reader-swatch reader-swatch-contrast" aria-hidden="true"></span> High contrast</label></fieldset>
<p class="reader-tool-note">No account or tracking. Your reading page and settings reset if you close the site.</p></section>
<nav class="reader-chapter-nav" aria-label="Table of contents"><p class="reader-eyebrow">READ AT YOUR OWN PACE</p>
<h2>Contents</h2><ol id="reader-toc">{''.join(toc)}</ol></nav></aside>
<div class="reader-book"><div class="reader-book-top"><div><p class="reader-eyebrow">YOUR CURRENT PAGE</p>
<p class="reader-progress-copy" id="reader-progress-copy" role="status" aria-live="polite">1 of {total}</p></div>
<progress id="reader-progress" max="{total}" value="1" aria-label="Reading sections reached">1 of {total}</progress></div>
<article class="reader-paper" aria-label="Complete {title} story"><div class="reader-paper-decoration" aria-hidden="true">✦ ✧ ✦</div>{''.join(page_html)}</article>
<div class="reader-pager" aria-label="Page navigation"><button type="button" id="reader-previous" disabled>← Previous</button>
<span id="reader-page-label" aria-live="polite">1 / {total}</span><button type="button" id="reader-next">Next →</button></div>
<p class="reader-keyboard-tip">Read the original text alongside historical artwork. Use left/right arrow keys outside controls, or select a chapter directly.</p>
<aside class="reader-note"><strong>Source, rights and reading guidance</strong>
<p>Written by {esc(book["author"])}; original illustrations by {esc(book["illustrator"])}. Original-era edition, {book["year"]}. Source: Project Gutenberg ebook {book["pg"]} (maintainer link in library documentation: {source_url}). Both original text and period illustrations are treated as public domain in the <strong>United States</strong>; rights may differ elsewhere. Newer commercial illustrations, Disney adaptations and branded artwork are <strong>not</strong> included.</p>
<p>WonderNet adaptation: book prose is presented in screen-reader-friendly paragraphs and chapter/page divisions, illustrations are copied as local JPEGs in narrative order, and source printer/imprint front matter and Project Gutenberg trademark/license blocks are excluded. Exact origin commit and artwork hashes are recorded in repository documentation. Image description accessibility review remains incomplete.</p>
<p><strong>Adult developer preview only:</strong> content suitability, educational reading level and manual accessibility reviews are pending. {esc(book["review_note"])}</p></aside></div></div>
<nav class="reader-bottom-nav" aria-label="Return to library"><a href="/explore/library">← Back to the Library</a></nav>
</main><footer><p>WonderNet early developer preview, not yet approved for unsupervised child use.</p></footer></body></html>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    if {b["id"] for b in manifest["books"]} != {"winnie-the-pooh", "velveteen-rabbit"}:
        raise ValueError("Only two pre-reviewed source edition routes permitted")
    hashes: dict[str, str] = {}
    pages: dict[str, dict] = {}
    for book in manifest["books"]:
        ident = book["id"]
        if not VALID_NAME.fullmatch(ident):
            raise ValueError("Unsafe edition slug")
        expected = ({"cover.jpg", "map.jpg"} | {f"illus{n}.jpg" for n in range(1, 114)}
                    if ident == "winnie-the-pooh" else
                    {"detail.jpg", "christmas.jpg", "horse.jpg", "spring.jpg",
                     "summer.jpg", "anxious.jpg", "fairy.jpg", "last.jpg"})
        if {img["name"] for img in book["images"]} != expected:
            raise ValueError("Edition image set differs from pinned allowlist")
        dest = ROOT / "frontend/pages" / f"book-{ident}.html"
        if args.verify_only:
            if not dest.is_file():
                raise ValueError(f"Missing complete static edition {dest}")
            page = dest.read_text(encoding="utf-8")
            expected_count = 11 if ident == "winnie-the-pooh" else None
            count = page.count('class="reader-chapter classic-chapter"')
            if count != expected_count and (expected_count is not None or not 10 <= count <= 35):
                raise ValueError(f"Missing story sections: {ident} has {count}")
            if not all(f"/assets/books/classics/{ident}/{img['name']}" in page for img in book["images"]):
                raise ValueError(f"Original illustration missing from complete page {ident}")
            if any(s in page for s in ('src="https://', '<iframe', '<script>', 'Project Gutenberg eBook of')):
                raise ValueError("External content or original PG license leaked into book")
            pages[ident] = {"pages": count, "image_count": len(book["images"])}
        else:
            source = get_source(book, book["html"], book["source_sha"], book["source_size"])
            sections, seen = (parse_pooh(source, book) if ident == "winnie-the-pooh"
                              else parse_velveteen(source, book))
            if seen != expected - ({"cover.jpg"} if ident == "winnie-the-pooh" else set()):
                raise ValueError("A pinned historical illustration is missing")
            text = build_reader(book, sections)
            dest.write_text(text, encoding="utf-8")
            pages[ident] = {"pages": len(sections), "image_count": len(book["images"])}
        for image in book["images"]:
            local = image["local"]
            intended = f"frontend/assets/books/classics/{ident}/{image['name']}"
            if local != intended or image["source_path"] != f"{book['source_image_prefix']}{image['name']}":
                raise ValueError("Source/local image path tampering")
            target = ROOT / local
            if args.verify_only:
                data = target.read_bytes()
            else:
                data = get_source(book, image["source_path"], image["git_sha"], image["bytes"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(data)
            if len(data) != image["bytes"] or blob_hash(data) != image["git_sha"]:
                raise ValueError(f"Original artwork corrupted: {local}")
            if not data.startswith(b"\xff\xd8\xff") or not data.endswith(b"\xff\xd9"):
                raise ValueError(f"Original image does not look like complete JPEG: {local}")
            hashes[local] = hashlib.sha256(data).hexdigest()
    digests = ROOT / "library/illustrated-classics-assets.sha256.json"
    if args.verify_only:
        if json.loads(digests.read_text(encoding="utf-8")) != hashes:
            raise ValueError("Local illustrated-classics SHA-256 inventory mismatch")
    else:
        digests.write_text(json.dumps(hashes, indent=2, sort_keys=True)+"\n", encoding="utf-8")
        (ROOT / "library/illustrated-classics-pages.json").write_text(
            json.dumps(pages, indent=2, sort_keys=True)+"\n", encoding="utf-8")
    print("Verified two full US public-domain illustrated classics:", pages, len(hashes), "local JPEGs")


if __name__ == "__main__":
    main()
