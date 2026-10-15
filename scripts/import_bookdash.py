#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Import precisely pinned, CC BY 4.0 Book Dash texts and JPEG assets.

Maintainer-only, build-time import. Never run on a learner request or Pi server.
Source file paths, commit hashes, blob hashes and expected byte sizes are fixed
in library/bookdash-books.json. No arbitrary URLs or redirects to unknown hosts.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "library/bookdash-books.json"
UPSTREAM = "https://raw.githubusercontent.com/bookdash/bookdash-books"
IMAGE_NAME = re.compile(r"^(?:cover|(?:0[1-9]|1[0-2]))\.jpg$")
SOURCE_SLUG = re.compile(r"^[a-z]+(?:-[a-z]+)*$")
MARKER = re.compile(r"!\[([^\]]+)\]\(\{\{ site\.image-set \}\}/((?:0[1-9]|1[0-2])\.jpg)\)")
MAX_BYTES = 240_000
STYLE = ["styles.css", "section-pages.css", "interiors.css", "book-reader.css", "bookdash-books.css"]


def git_blob_sha(payload: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(payload)).encode("ascii") + b"\\0" + payload).hexdigest()


def read_pinned(ref: str, source_path: str, expected_sha: str, expected_size: int | None = None) -> bytes:
    if not re.fullmatch(r"[0-9a-f]{40}", ref):
        raise ValueError("Source commit is not pinned")
    if not re.fullmatch(r"[0-9a-f]{40}", expected_sha):
        raise ValueError("Missing source blob hash")
    if not re.fullmatch(r"[a-z0-9-]+/en/(?:index\.md|images/(?:cover|[0-9]{2})\.jpg)", source_path):
        raise ValueError("Source path not on the verified allowlist")
    url = f"{UPSTREAM}/{ref}/{source_path}"
    request = Request(url, headers={"User-Agent": "WonderNet-BookDash-Offline-Importer/1.0"})
    with urlopen(request, timeout=45) as response:
        # The download must never be redirected to an arbitrary server.
        if urlparse(response.geturl()).hostname != "raw.githubusercontent.com":
            raise ValueError("Unexpected source redirect host")
        payload = response.read(MAX_BYTES + 1)
    if not payload or len(payload) > MAX_BYTES:
        raise ValueError(f"Empty or excessive source file: {source_path}")
    if expected_size is not None and len(payload) != expected_size:
        raise ValueError(f"Unexpected byte length: {source_path}")
    if git_blob_sha(payload) != expected_sha:
        raise ValueError(f"Source blob SHA mismatch: {source_path}")
    return payload


def parse_book_markdown(data: bytes) -> list[dict]:
    source = data.decode("utf-8").replace("\r\n", "\n")
    body = re.sub(r"^---\n[\s\S]*?\n---\s*", "", source, count=1).strip()
    if not body.startswith("# "):
        raise ValueError("Missing book heading")
    body = body.split("\n", 1)[1].strip()
    found = list(MARKER.finditer(body))
    if len(found) != 12 or body[:found[0].start()].strip():
        raise ValueError("Expected exactly twelve illustrated book spreads")
    result = []
    for index, match in enumerate(found):
        expected_name = f"{index+1:02}.jpg"
        if match.group(2) != expected_name:
            raise ValueError("Spread images must be ordered 01.jpg through 12.jpg")
        until = found[index+1].start() if index + 1 < len(found) else len(body)
        segment = body[match.end():until].strip()
        paragraphs = [re.sub(r"\s+", " ", p).strip()
                      for p in re.split(r"\n\s*\n", segment) if p.strip()]
        # No user-provided HTML or markdown embeds are permitted in book pages.
        if any("<" in p or ">" in p or "![" in p or "{{" in p for p in paragraphs):
            raise ValueError("Unexpected book markup")
        result.append({"image": expected_name, "alt": match.group(1).strip(), "paragraphs": paragraphs})
    if not any(p["paragraphs"] for p in result) or any(not p["alt"] for p in result):
        raise ValueError("Story text or accessible picture descriptions missing")
    return result


def escape(value: str) -> str:
    return html.escape(str(value), quote=True)


def build_html(book: dict, spreads: list[dict]) -> str:
    title = escape(book["title"])
    name = escape(book["id"])
    credits = [
        "Written by " + escape(book["author"]),
        "Illustrated by " + escape(book["illustrator"]),
        "Designed by " + escape(book["designer"]),
    ]
    if book["editor"]:
        credits.append("Edited by " + escape(book["editor"]))
    credit_string = "; ".join(credits)
    pages = []
    menu = []
    for n, spread in enumerate(spreads, 1):
        menu.append(f'<li><button type="button" data-open-chapter="{n}"' +
                    (' aria-current="true"' if n == 1 else "") +
                    f'><span>{n:02}</span> Spread {n}</button></li>')
        paragraphs = "\n".join("<p>" + escape(p) + "</p>" for p in spread["paragraphs"])
        pages.append(
            f'<section class="reader-chapter dash-chapter" id="chapter-{n}" data-chapter="{n}" '
            f'aria-labelledby="chapter-title-{n}"' + (' hidden' if n > 1 else '') + '>\n'
            f'<p class="reader-chapter-number">SPREAD {n} OF 12</p>'
            f'<h2 id="chapter-title-{n}" tabindex="-1">{title} · {n}</h2>'
            f'<figure class="dash-spread"><img src="/assets/books/bookdash/{name}/{spread["image"]}" '
            f'width="1000" height="700" loading="{"eager" if n == 1 else "lazy"}" '
            f'alt="{escape(spread["alt"])}"></figure>\n{paragraphs}'
            + ('<p class="reader-the-end">THE END ✳</p>' if n == 12 else '') + '</section>')
    css = "".join(f'<link rel="stylesheet" href="/assets/{style}">' for style in STYLE)
    toc = "\n".join(menu)
    sections = "\n".join(pages)
    text = f"""<!-- SPDX-License-Identifier: AGPL-3.0-only -->
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="{title}: original Book Dash pictures and full story, locally hosted under CC BY 4.0.">
<title>{title} | WonderNet Library</title>{css}
<script defer src="/assets/book-reader.js?v=bookdash1"></script></head>
<body class="interior-page reader-page dash-book" data-reader-theme="paper" data-reader-unit="Page">
<a class="skip-link" href="#main-content">Skip to reading</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="/" aria-label="WonderNet home"><span class="brand-mark" aria-hidden="true">✳</span><span>Wonder<span class="brand-emphasis">Net</span></span><span class="alpha">ALPHA 0.1</span></a><nav class="site-nav" aria-label="Main navigation"><a href="/">Home</a><a href="/explore/library">Library</a></nav></div></header>
<main class="reader-main" id="main-content"><nav class="breadcrumbs" aria-label="Breadcrumb">
<a href="/">Home</a><span aria-hidden="true">/</span><a href="/explore/library">Library</a>
<span aria-hidden="true">/</span><span aria-current="page">{title}</span></nav>
<section class="reader-cover" aria-labelledby="book-title">
<div class="reader-cover-copy"><p class="reader-kicker">✦ BOOK DASH · OPENLY LICENSED STORY</p>
<h1 id="book-title">{title}</h1><p class="reader-byline">{credit_string}</p>
<p class="reader-summary">{escape(book["blurb"])}</p>
<span class="reader-sample">Original published artwork · English · CC BY 4.0 · Child-use review pending</span></div>
<div class="reader-cover-art dash-cover"><img src="/assets/books/bookdash/{name}/cover.jpg"
width="700" height="700" alt="Original Book Dash cover of {title}."></div></section>
<div class="reader-layout"><aside class="reader-sidebar" aria-label="Reading controls and table of contents">
<section class="reader-toolbox" aria-labelledby="reader-tools-heading"><p class="reader-eyebrow">READ IT YOUR WAY</p>
<h2 id="reader-tools-heading">Reading tools</h2>
<div class="reader-settings-row"><span class="reader-setting-name" id="reader-size-label">Text size</span>
<div class="reader-size-buttons" role="group" aria-labelledby="reader-size-label">
<button type="button" id="reader-smaller" aria-label="Decrease text size">A−</button>
<output id="reader-size" aria-live="polite" aria-label="Text size">100%</output>
<button type="button" id="reader-larger" aria-label="Increase text size">A+</button></div></div>
<fieldset class="reader-themes"><legend>Page colors</legend>
<label><input type="radio" name="reading-theme" value="paper" checked><span class="reader-swatch reader-swatch-paper" aria-hidden="true"></span> Paper</label>
<label><input type="radio" name="reading-theme" value="night"><span class="reader-swatch reader-swatch-night" aria-hidden="true"></span> Night</label>
<label><input type="radio" name="reading-theme" value="contrast"><span class="reader-swatch reader-swatch-contrast" aria-hidden="true"></span> High contrast</label></fieldset>
<p class="reader-tool-note">All story images and text are hosted by WonderNet. No external book requests, accounts or saved reading history.</p>
</section>
<nav class="reader-chapter-nav" aria-label="Table of contents"><p class="reader-eyebrow">TWELVE ILLUSTRATED SPREADS</p>
<h2>Jump to a spread</h2><ol id="reader-toc">{toc}</ol></nav></aside>
<div class="reader-book"><div class="reader-book-top"><div><p class="reader-eyebrow">YOUR CURRENT SPREAD</p>
<p class="reader-progress-copy" id="reader-progress-copy" role="status" aria-live="polite">Page 1 of 12 · {title} · 1</p></div>
<progress id="reader-progress" max="12" value="1" aria-label="Spreads reached">1 of 12</progress></div>
<article class="reader-paper" aria-label="Illustrated complete story">
<div class="reader-paper-decoration" aria-hidden="true">✦ ✧ ✦</div>{sections}</article>
<div class="reader-pager" aria-label="Spread navigation">
<button type="button" id="reader-previous" disabled>← Previous page</button>
<span id="reader-page-label" aria-live="polite">1 / 12</span>
<button type="button" id="reader-next">Next page →</button></div>
<p class="reader-keyboard-tip">Use left and right arrow keys when not focused on another control.
Pictures and words come from the original Book Dash edition, rearranged into reading screens.</p>
<aside class="reader-note"><strong>Book Dash creators and open license</strong>
<p>{credit_string}. Published by Book Dash ({book["year"]}), ISBN {escape(book["isbn"])}.
Creative Commons Attribution 4.0 International (CC BY 4.0).</p>
<p>Original publisher: bookdash.org · Source: {escape(book["official_url"])}
· License: creativecommons.org/licenses/by/4.0/.
Adaptation: formatted for WonderNet's local page reader; line spacing normalized and original picture spreads retained.
Edition and file hashes are documented in the WonderNet repository.</p>
<p><strong>Developer preview only:</strong> educator, age suitability, accessibility and content review are pending.
Not approved for unsupervised child use.</p></aside></div></div>
<nav class="reader-bottom-nav" aria-label="Return to library"><a href="/explore/library">← Back to Library</a></nav></main>
<footer><p>WonderNet early developer preview. Book Dash originals: CC BY 4.0.</p></footer></body></html>
"""
    # No remote links, scripts, embeds or programmatically accessed user content.
    if 'src="https://' in text or 'href="https://' in text or "<iframe" in text or "<script>" in text:
        raise ValueError("Generated content contains forbidden resource or executable markup")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true",
                        help="Check already imported assets without downloading or modifying")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["source_repo"] != "bookdash/bookdash-books":
        raise ValueError("Only the pinned official Book Dash mirror is supported")
    ref = manifest["source_ref"]
    if len(manifest["books"]) != 5 or len({b["id"] for b in manifest["books"]}) != 5:
        raise ValueError("Expected exactly five named Book Dash titles")
    fingerprints: dict[str, str] = {}
    for book in manifest["books"]:
        slug = book["id"]
        if not SOURCE_SLUG.fullmatch(slug):
            raise ValueError("Invalid fixed source identifier")
        image_names = {f"{i:02}.jpg" for i in range(1, 13)} | {"cover.jpg"}
        if {m["name"] for m in book["media"]} != image_names:
            raise ValueError("Expected twelve illustrations and one cover")
        expected_md = f"{slug}/en/index.md"
        if book["source_markdown"] != expected_md:
            raise ValueError("Unexpected edition source")
        page = ROOT / "frontend/pages" / f"book-{slug}.html"
        if args.verify_only:
            if not page.is_file():
                raise ValueError(f"Missing generated book page: {page}")
        else:
            md = read_pinned(ref, expected_md, book["source_md_sha"])
            spreads = parse_book_markdown(md)
            page.write_text(build_html(book, spreads), encoding="utf-8")
        for file in book["media"]:
            name = file["name"]
            source_path = f"{slug}/en/images/{name}"
            local_path = f"frontend/assets/books/bookdash/{slug}/{name}"
            if not IMAGE_NAME.fullmatch(name) or source_path != file["source_path"] or local_path != file["local_path"]:
                raise ValueError("Unapproved image name or path")
            target = ROOT / local_path
            if args.verify_only:
                blob = target.read_bytes()
                if len(blob) != file["bytes"] or git_blob_sha(blob) != file["git_blob_sha"]:
                    raise ValueError(f"Invalid stored media: {target}")
            else:
                blob = read_pinned(ref, source_path, file["git_blob_sha"], file["bytes"])
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(blob)
            if not (blob.startswith(b"\\xff\\xd8\\xff") and blob.endswith(b"\\xff\\xd9")):
                raise ValueError(f"File is not a valid JPEG stream: {target}")
            fingerprints[local_path] = hashlib.sha256(blob).hexdigest()
        print(f"Verified {book['title']}: 12 original picture spreads + cover")
    sha_path = ROOT / "library/bookdash-assets.sha256.json"
    if args.verify_only:
        expected = json.loads(sha_path.read_text(encoding="utf-8"))
        if expected != fingerprints:
            raise ValueError("Local media SHA-256 inventory does not match")
    else:
        sha_path.write_text(json.dumps(fingerprints, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"{'Verified' if args.verify_only else 'Imported'} {len(fingerprints)} pinned Book Dash images")


if __name__ == "__main__":
    main()
