# SPDX-License-Identifier: AGPL-3.0-only
"""Static preview checks, including path safety and honest preview labeling."""
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_pages_preview import make_html, normalize_base_path, rewrite_url


def test_export_builds_nine_live_html_routes(tmp_path):
    result = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "build_pages_preview.py"),
            "--output", str(tmp_path), "--base-path", "/wondernet",
        ],
        check=True, capture_output=True, text=True, cwd=ROOT,
    )
    assert "Built 9 public preview pages" in result.stdout
    expected = [
        "index.html", "explore/early-learning/index.html",
        "explore/academy/index.html", "explore/special-interests/index.html",
        "explore/arcade/index.html", "explore/library/index.html",
        "explore/wonderparty/index.html",
        "play/letter-match/index.html", "play/patterns/index.html",
    ]
    for relative in expected:
        html = (tmp_path / relative).read_text(encoding="utf-8")
        assert "Developer preview" in html
        assert 'href="https://github.com/KadenBar/wondernet"' in html
        assert "Source code and feedback" in html
        assert "not a child-ready product" in html
        assert 'name="robots" content="noindex,nofollow"' in html
        assert 'href="/wondernet/assets/preview.css"' in html
        assert 'href="/assets/' not in html
        assert 'src="/assets/' not in html
        assert 'href="/explore/' not in html
        assert 'href="/play/' not in html
        assert "<main" in html
    homepage = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'href="/wondernet/explore/early-learning/"' in homepage
    assert 'href="/wondernet/play/letter-match/"' in homepage
    assert 'href="/wondernet/play/patterns/"' in homepage
    assert 'href="/wondernet/assets/home.css"' in homepage
    assert "Pi Wi-Fi network is planned" in homepage
    first_page = (tmp_path / "explore/early-learning/index.html").read_text(encoding="utf-8")
    assert 'href="/wondernet/play/letter-match/"' in first_page
    assert (tmp_path / "assets/activities.js").is_file()
    assert (tmp_path / "assets/main.js").is_file()
    assert (tmp_path / ".nojekyll").is_file()
    assert not (tmp_path / "api").exists()


def test_base_path_validation():
    assert normalize_base_path("/wondernet/") == "/wondernet"
    assert normalize_base_path("") == ""
    for invalid in ("wondernet", "//example.com", "/../x", "/bad path", "/a//b"):
        with pytest.raises(ValueError):
            normalize_base_path(invalid)


def test_rewrites_only_allowlisted_local_paths():
    assert rewrite_url("/#explore", "/wondernet") == "/wondernet/#explore"
    assert rewrite_url("/play/patterns", "/wondernet") == "/wondernet/play/patterns/"
    assert rewrite_url("/assets/main.js", "/wondernet") == "/wondernet/assets/main.js"
    with pytest.raises(ValueError):
        rewrite_url("/play/../../admin", "/wondernet")
    with pytest.raises(ValueError):
        rewrite_url("/api/health", "/wondernet")
    with pytest.raises(ValueError):
        rewrite_url("//example.com/script.js", "/wondernet")


def test_preview_security_meta_and_no_remote_code():
    html = make_html(
        '<!doctype html><html><head></head><body>'
        '<a href="/">Home</a><script src="/assets/main.js"></script></body></html>',
        "/wondernet",
    )
    assert "Content-Security-Policy" in html
    assert "connect-src &#39;none&#39;" in html
    assert 'src="/wondernet/assets/main.js"' in html
    assert 'href="/wondernet/"' in html
