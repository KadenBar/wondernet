# SPDX-License-Identifier: AGPL-3.0-only
"""Static preview checks, including path safety and honest preview labeling."""
import subprocess
import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_pages_preview import make_html, normalize_base_path, rewrite_url


def test_export_builds_seventeen_live_html_routes(tmp_path):
    result = subprocess.run(
        [
            sys.executable, str(ROOT / "scripts" / "build_pages_preview.py"),
            "--output", str(tmp_path), "--base-path", "/wondernet",
        ],
        check=True, capture_output=True, text=True, cwd=ROOT,
    )
    assert "Built 17 public preview pages" in result.stdout
    expected = [
        "index.html", "explore/early-learning/index.html",
        "explore/academy/index.html", "explore/special-interests/index.html",
        "explore/arcade/index.html", "explore/library/index.html",
        "explore/wonderparty/index.html",
        "play/letter-match/index.html", "play/patterns/index.html",
        "play/circuit-garden/index.html", "play/word-workshop/index.html",
        "read/lantern/index.html",
        "read/peter-rabbit/index.html", "read/benjamin-bunny/index.html",
        "read/tom-kitten/index.html", "read/jemima-puddle-duck/index.html",
        "read/jeremy-fisher/index.html",
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
        assert 'href="/read/' not in html
        assert "<main" in html
    homepage = (tmp_path / "index.html").read_text(encoding="utf-8")
    assert 'href="/wondernet/explore/early-learning/"' in homepage
    assert 'href="/wondernet/play/letter-match/"' in homepage
    assert 'href="/wondernet/play/patterns/"' in homepage
    assert 'href="/wondernet/play/circuit-garden/"' in homepage
    assert 'href="/wondernet/play/word-workshop/"' in homepage
    assert 'href="/wondernet/assets/home.css"' in homepage
    assert "Pi Wi-Fi network is planned" in homepage
    first_page = (tmp_path / "explore/early-learning/index.html").read_text(encoding="utf-8")
    assert 'href="/wondernet/play/letter-match/"' in first_page
    assert (tmp_path / "assets/activities.js").is_file()
    assert (tmp_path / "assets/circuit-engine.js").is_file()
    assert (tmp_path / "assets/circuit-garden.js").is_file()
    assert (tmp_path / "assets/circuit-garden.css").is_file()
    assert (tmp_path / "assets/word-workshop-engine.js").is_file()
    assert (tmp_path / "assets/word-workshop.js").is_file()
    assert (tmp_path / "assets/word-workshop.css").is_file()
    workshop = (tmp_path / "play/word-workshop/index.html").read_text(encoding="utf-8")
    assert 'src="/wondernet/assets/word-workshop-engine.js"' in workshop
    assert 'src="/wondernet/assets/word-workshop.js?v=touch2"' in workshop
    assert 'href="/wondernet/assets/word-workshop.css?v=touch2"' in workshop
    garden = (tmp_path / "play/circuit-garden/index.html").read_text(encoding="utf-8")
    assert 'src="/wondernet/assets/circuit-engine.js"' in garden
    assert 'src="/wondernet/assets/circuit-garden.js"' in garden
    assert 'href="/wondernet/assets/circuit-garden.css"' in garden
    assert (tmp_path / "assets/book-reader.js").is_file()
    assert (tmp_path / "assets/book-reader.css").is_file()
    reader = (tmp_path / "read/lantern/index.html").read_text(encoding="utf-8")
    assert 'src="/wondernet/assets/book-reader.js"' in reader
    assert 'href="/wondernet/assets/book-reader.css"' in reader
    assert 'href="/wondernet/explore/library/"' in reader
    assert 'id="chapter-5"' in reader
    assert 'href="/wondernet/read/lantern/"' in (tmp_path / "explore/library/index.html").read_text(encoding="utf-8")
    for name in ("peter-rabbit", "benjamin-bunny", "tom-kitten",
                 "jemima-puddle-duck", "jeremy-fisher"):
        book = (tmp_path / "read" / name / "index.html").read_text(encoding="utf-8")
        assert 'data-reader-unit="Page"' in book
        assert 'src="/wondernet/assets/book-reader.js?v=editions1"' in book
        assert 'href="/wondernet/explore/library/"' in book
        assert "<svg " in book
        assert "End of Project Gutenberg" not in book
        assert 'href="https://' not in book.replace('href="https://github.com/KadenBar/wondernet"', '')
        assert (tmp_path / "read" / name / "index.html").is_file()
    assert (tmp_path / "assets/interiors.css").is_file()
    for relative in expected[1:]:
        html = (tmp_path / relative).read_text(encoding="utf-8")
        assert 'href="/wondernet/assets/interiors.css"' in html
    for game in ("letter-match", "patterns"):
        html = (tmp_path / "play" / game / "index.html").read_text(encoding="utf-8")
        assert 'id="activity-meter"' in html
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
    assert rewrite_url("/play/circuit-garden", "/wondernet") == "/wondernet/play/circuit-garden/"
    assert rewrite_url("/play/word-workshop", "/wondernet") == "/wondernet/play/word-workshop/"
    assert rewrite_url("/read/lantern", "/wondernet") == "/wondernet/read/lantern/"
    assert rewrite_url("/read/peter-rabbit", "/wondernet") == "/wondernet/read/peter-rabbit/"
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


def test_preview_banner_handles_body_classes():
    html = make_html(
        '<html><head></head><body class="home-page"><main>Hi</main></body></html>',
        "/wondernet",
    )
    assert '<body class="home-page"><div class="public-preview-notice"' in html
    assert "Source code and feedback" in html
