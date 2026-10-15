#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Validate a maintainer-curated offline book import staging manifest.

No network access, file writes, or learner-facing upload functionality.
"""
from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_GATES = ("rights_review", "content_review", "accessibility_review", "package_review")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).casefold()
    return " ".join(re.findall(r"[a-z0-9]+", value))


def valid_https(value: str) -> bool:
    try:
        url = urlsplit(value)
        return (url.scheme == "https" and bool(url.hostname) and
                url.username is None and url.password is None and
                not any(ch.isspace() for ch in value) and "\\" not in value)
    except ValueError:
        return False


def validate(manifest: dict, existing: list[dict]) -> list[str]:
    errors: list[str] = []
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("items"), list):
        return ["Expected schema_version=1 and an items array"]
    known = {(normalized(x.get("title", "")), normalized(x.get("creator", x.get("author", ""))))
             for x in existing if isinstance(x, dict)}
    ids: set[str] = set()
    for index, item in enumerate(manifest["items"]):
        tag = f"items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{tag}: expected object")
            continue
        slug, title, creator = (item.get(k) for k in ("id", "title", "creator"))
        if not isinstance(slug, str) or not SLUG.fullmatch(slug):
            errors.append(f"{tag}: invalid id")
        elif slug in ids:
            errors.append(f"{tag}: duplicate id")
        else:
            ids.add(slug)
        if not isinstance(title, str) or not title.strip() or not isinstance(creator, str) or not creator.strip():
            errors.append(f"{tag}: missing title or creator")
        else:
            key = (normalized(title), normalized(creator))
            if key in known:
                errors.append(f"{tag}: duplicate title/creator already cataloged")
            known.add(key)
        source = item.get("source_url")
        if not isinstance(source, str) or not valid_https(source):
            errors.append(f"{tag}: source_url must be HTTPS")
        rights = item.get("rights")
        if not isinstance(rights, dict) or not all(isinstance(rights.get(k), str) and rights[k].strip()
                                                    for k in ("classification", "territory", "license_url")):
            errors.append(f"{tag}: missing rights metadata")
        gates = item.get("gate")
        if not isinstance(gates, dict) or any(gates.get(k) not in ("pending", "approved", "rejected") for k in REQUIRED_GATES):
            errors.append(f"{tag}: invalid review gates")
        status = item.get("import_status")
        if status not in ("not-imported", "staged", "reviewed"):
            errors.append(f"{tag}: invalid import_status")
        if status == "reviewed" and (not isinstance(gates, dict) or any(gates.get(k) != "approved" for k in REQUIRED_GATES)):
            errors.append(f"{tag}: reviewed status requires all gates approved")
        if status in ("staged", "reviewed") and not (isinstance(item.get("sha256"), str) and SHA256.fullmatch(item["sha256"])):
            errors.append(f"{tag}: staged item requires SHA-256")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="Staging JSON file")
    parser.add_argument("--existing", type=Path, action="append", default=None, help="Existing catalog/edition JSON; repeatable; defaults to all local library inventories")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    existing = []
    paths = args.existing if args.existing is not None else [
        ROOT / "library" / name for name in (
            "catalog.json", "complete-text-editions.json", "illustrated-classics.json",
            "bookdash-books.json", "picture-books.json", "reader-demos.json"
        )
    ]
    for path in paths:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            for key in ("items", "books", "stories"):
                entries = data.get(key, [])
                if isinstance(entries, list):
                    existing.extend(entries)
    errors = validate(manifest, existing)
    for error in errors:
        print(error)
    if errors:
        return 1
    print(f"Validated {len(manifest['items'])} staging entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
