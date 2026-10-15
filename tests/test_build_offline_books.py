import hashlib
from pathlib import Path

import pytest

from scripts.build_offline_books import build, parse_chapters, render


def item(payload: bytes):
    return {
        "id": "safe-example", "title": "<Safe & Story>", "creator": "A. Writer",
        "source_url": "https://example.org/source",
        "rights": {"classification": "PD-US", "territory": "US", "license_url": "https://example.org/rights"},
        "gate": {k: "approved" for k in ("rights_review", "content_review", "accessibility_review", "package_review")},
        "import_status": "reviewed", "sha256": hashlib.sha256(payload).hexdigest(),
    }


def test_parse_multiple_chapters():
    assert len(parse_chapters(b"One\n\nHello.\n===\nTwo\n\nWorld.")) == 2


def test_escape_all_imported_text():
    markup = render({"title": "<script>", "creator": "A & B"}, [("<img>", ["<script>alert(1)</script>"])])
    assert "<script>" not in markup
    assert "&lt;script&gt;" in markup
    assert "A &amp; B" in markup


def test_checksum_and_no_writes_on_dry_run(tmp_path: Path):
    source, output = tmp_path / "sources", tmp_path / "pages"
    source.mkdir()
    payload = b"Chapter 1\n\nHello, world."
    (source / "safe-example.txt").write_bytes(payload)
    manifest = {"schema_version": 1, "items": [item(payload)]}
    assert len(build(manifest, source_root=source, output_root=output)) == 1
    assert not output.exists()
    assert len(build(manifest, source_root=source, output_root=output, write=True)) == 1
    assert "Hello, world." in (output / "book-safe-example.html").read_text()


def test_tampered_source_is_rejected(tmp_path: Path):
    source = tmp_path / "sources"
    source.mkdir()
    (source / "safe-example.txt").write_text("Wrong")
    with pytest.raises(ValueError, match="Checksum mismatch"):
        build({"schema_version": 1, "items": [item(b"Correct")]}, source_root=source)


def test_unreviewed_items_not_published(tmp_path: Path):
    candidate = item(b"unused")
    candidate["import_status"] = "not-imported"
    candidate.pop("sha256")
    assert build({"schema_version": 1, "items": [candidate]}, source_root=tmp_path) == []


def test_symlink_source_rejected(tmp_path: Path):
    source = tmp_path / "sources"
    source.mkdir()
    outside = tmp_path / "outside"
    outside.write_text("Chapter\n\nContent")
    (source / "safe-example.txt").symlink_to(outside)
    with pytest.raises(ValueError, match="symlinked"):
        build({"schema_version": 1, "items": [item(outside.read_bytes())]}, source_root=source)


def test_invalid_chapter_rejected():
    with pytest.raises(ValueError, match="paragraphs"):
        parse_chapters(b"Only a title")
