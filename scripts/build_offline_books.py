#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Build static, offline chapter readers from reviewed, pinned local text files.

Maintainer-only. No network calls, no remote HTML, and no learner uploads.
The source is a UTF-8 text file under library/import-sources/ with chapters
separated by a line consisting of three equals signs (===).
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
from pathlib import Path

from scripts.validate_book_imports import validate

ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "library" / "import-sources"
OUTPUT_ROOT = ROOT / "frontend" / "pages"
MAX_SOURCE_BYTES = 3_000_000
MAX_CHAPTERS = 150
MAX_CHAPTER_LENGTH = 100_000


def parse_chapters(raw: bytes) -> list[tuple[str, list[str]]]:
    if not raw or len(raw) > MAX_SOURCE_BYTES:
        raise ValueError("Source text empty or oversized")
    source = raw.decode("utf-8")
    if "\x00" in source:
        raise ValueError("NUL in source text")
    chapters = []
    for part in re.split(r"(?m)^===[ \t]*$", source.replace("\r\n", "\n")):
        part = part.strip()
        if not part:
            raise ValueError("Empty chapter")
        if len(part) > MAX_CHAPTER_LENGTH:
            raise ValueError("Chapter too long")
        lines = part.splitlines()
        title = lines[0].strip()
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", "\n".join(lines[1:])) if p.strip()]
        if not title or not paragraphs:
            raise ValueError("Each chapter needs a title and paragraphs")
        chapters.append((title, paragraphs))
    if len(chapters) > MAX_CHAPTERS:
        raise ValueError("Too many chapters")
    return chapters


def render(item: dict, chapters: list[tuple[str, list[str]]]) -> str:
    esc = lambda value: html.escape(value, quote=True)
    title = esc(item["title"])
    creator = esc(item["creator"])
    sections = []
    links = []
    for number, (chapter_title, paragraphs) in enumerate(chapters, 1):
        links.append(f'<li><a href="#chapter-{number}">{number}. {esc(chapter_title)}</a></li>')
        body = "\n".join(f"<p>{esc(p)}</p>" for p in paragraphs)
        sections.append(f'<section id="chapter-{number}" aria-labelledby="chapter-heading-{number}">'
                        f'<h2 id="chapter-heading-{number}">{esc(chapter_title)}</h2>\n{body}</section>')
    toc = "\n".join(links)
    content = "\n".join(sections)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">
<title>{title} | WonderNet Library</title>
<link rel="stylesheet" href="/assets/styles.css">
<link rel="stylesheet" href="/assets/book-reader.css">
</head><body class="reader-page"><a class="skip-link" href="#main">Skip to book</a>
<header><a href="/library">Back to Library</a></header>
<main id="main"><h1>{title}</h1><p>By {creator}</p>
<nav aria-label="Table of contents"><h2>Chapters</h2><ol>{toc}</ol></nav>
{content}</main></body></html>
"""


def build(manifest: dict, *, source_root: Path = SOURCE_ROOT, output_root: Path = OUTPUT_ROOT,
          write: bool = False) -> list[Path]:
    errors = validate(manifest, [])
    if errors:
        raise ValueError("; ".join(errors))
    rendered: list[tuple[Path, str]] = []
    for item in manifest["items"]:
        if item["import_status"] != "reviewed":
            continue
        if any(item["gate"][key] != "approved" for key in (
            "rights_review", "content_review", "accessibility_review", "package_review"
        )):
            raise ValueError("Review gates not approved")
        source = source_root / (item["id"] + ".txt")
        if source.is_symlink() or not source.is_file():
            raise ValueError(f"Missing or symlinked source: {item['id']}")
        if source.stat().st_size > MAX_SOURCE_BYTES:
            raise ValueError("Oversized source")
        raw = source.read_bytes()
        if hashlib.sha256(raw).hexdigest() != item["sha256"]:
            raise ValueError(f"Checksum mismatch: {item['id']}")
        chapters = parse_chapters(raw)
        rendered.append((output_root / ("book-" + item["id"] + ".html"), render(item, chapters)))
    if write:
        output_root.mkdir(parents=True, exist_ok=True)
        for path, content in rendered:
            if path.is_symlink():
                raise ValueError(f"Refusing symlink output: {path}")
            path.write_text(content, encoding="utf-8")
    return [path for path, _ in rendered]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--write", action="store_true", help="Write static pages after validating all inputs")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    paths = build(manifest, write=args.write)
    print(f"{'Generated' if args.write else 'Validated'} {len(paths)} offline book pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
