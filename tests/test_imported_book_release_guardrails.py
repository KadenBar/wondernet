# SPDX-License-Identifier: AGPL-3.0-only
"""Release guardrails for imported offline editions awaiting human approval."""
from pathlib import Path

from scripts.audit_offline_editions import BOOK_IDS, PAGES, audit

LIBRARY = PAGES / "library.html"


def test_all_imported_editions_keep_visible_review_pending_notice():
    for slug in BOOK_IDS:
        html = (PAGES / f"book-{slug}.html").read_text(encoding="utf-8")
        assert "review pending" in html.lower(), slug


def test_library_marks_imported_editions_as_preview_and_review_pending():
    html = LIBRARY.read_text(encoding="utf-8")
    assert "New complete offline books · Preview" in html
    assert "Editorial and accessibility reviews remain pending." in html
    for slug in BOOK_IDS:
        assert f'/read/{slug}"' in html, slug


def test_audit_does_not_equate_structural_pass_with_release_approval():
    reports = audit()
    assert len(reports) == len(BOOK_IDS)
    assert all(not report["errors"] for report in reports)
    assert all(
        any("independent review" in flag for flag in report["review_flags"])
        for report in reports
    )


def test_illustration_dependent_editions_are_explicitly_flagged():
    by_id = {report["id"]: report for report in audit()}
    for slug in ("flopsy-bunnies", "squirrel-nutkin", "timmy-tiptoes", "book-of-dragons"):
        assert any(
            "illustration-dependent edition" in flag
            for flag in by_id[slug]["review_flags"]
        ), slug
