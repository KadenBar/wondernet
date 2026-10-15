from scripts.audit_offline_editions import BOOK_IDS, audit_page, audit

def test_all_fifty_imported_editions_have_structural_security_baseline():
    reports = audit()
    assert len(BOOK_IDS) == len(set(BOOK_IDS)) == len(reports) == 51
    assert not [(r["id"], r["errors"]) for r in reports if r["errors"]]

def test_audit_detects_active_content_and_broken_anchors():
    html = '<main><h1>Book</h1><a href="#missing">Go</a><script src="https://bad.test/x"></script></main>'
    report = audit_page("dracula", html)
    assert "active script or remote media" in report["errors"]
    assert "broken in-page navigation" in report["errors"]
    assert "missing content security policy" in report["errors"]

def test_audit_never_automatically_approves_rights_or_age_suitability():
    html = '<meta http-equiv="Content-Security-Policy"><main><h1>Book</h1><p>Project Gutenberg</p></main>'
    report = audit_page("dracula", html)
    assert not report["errors"]
    assert any("independent review" in f for f in report["review_flags"])
    assert any("older-reader" in f for f in report["review_flags"])
