#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
"""Render the real exported Library in Chromium and assert cards never overlap.

This catches visual geometry bugs that CSS-string assertions and route smoke
tests cannot catch, including Android-style virtual desktop-width touch views.
Developer/CI regression only: serves a localhost export, never student data.
"""
from __future__ import annotations

import functools
import http.server
import subprocess
import sys
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
LIBRARY_ROUTE = "/explore/library/"
MEASURE_JS = """() => {
 const cards = [...document.querySelectorAll('.lb-dash-card')];
 const rect = el => {const r = el.getBoundingClientRect();
   return {left:r.left, right:r.right, top:r.top, bottom:r.bottom,
           width:r.width, height:r.height};};
 return {
  innerWidth: window.innerWidth,
  width: document.documentElement.scrollWidth,
  isCoarse: matchMedia('(pointer:coarse)').matches,
  gridColumns: getComputedStyle(document.querySelector('.lb-dash-grid')).gridTemplateColumns,
  loadedLayoutCss: [...document.styleSheets].some(sheet => sheet.href?.includes('bookdash-layout-v2.css')),
  cards: cards.map(card => ({
    card:rect(card),
    cover:rect(card.querySelector('.lb-dash-cover')),
    image:rect(card.querySelector('.lb-dash-cover img')),
    meta:rect(card.querySelector('.lb-dash-meta')),
    button:rect(card.querySelector('.lb-dash-read')),
    imageLoaded:card.querySelector('.lb-dash-cover img').naturalWidth>0
  })),
  classics: [...document.querySelectorAll('.lb-favorite-card')].map(card => ({
    card:rect(card),
    cover:rect(card.querySelector('.lb-favorite-cover')),
    image:rect(card.querySelector('.lb-favorite-cover img')),
    meta:rect(card.querySelector('.lb-favorite-copy')),
    button:rect(card.querySelector('.lb-favorite-read')),
    imageLoaded:card.querySelector('.lb-favorite-cover img').naturalWidth>0
  }))
 };
}"""


def check_page(browser, url: str, width: int, touch: bool, scale: float = 1.0) -> None:
    context = browser.new_context(
        viewport={"width": width, "height": 900},
        device_scale_factor=3 if touch else 1,
        is_mobile=touch,
        has_touch=touch,
        reduced_motion="reduce",
    )
    page = context.new_page()
    try:
        response = page.goto(url, wait_until="networkidle", timeout=30000)
        assert response and response.status == 200, "Library failed to load"
        if scale > 1:
            page.evaluate("(value) => { document.documentElement.style.fontSize = value; }", f"{100*scale:.0f}%")
        for card in page.locator(".lb-dash-card, .lb-favorite-card").all():
            card.scroll_into_view_if_needed()
            card.locator("img").evaluate("(img) => img.decode()")
        sizes = page.evaluate(MEASURE_JS)
        assert sizes["loadedLayoutCss"], f"New layout stylesheet absent: {sizes}"
        assert len(sizes["cards"]) == 5, f"Expected five Book Dash cards: {sizes}"
        assert len(sizes["classics"]) == 2, f"Expected two historic illustrated classics: {sizes}"
        assert sizes["width"] <= sizes["innerWidth"] + 3, f"Page has horizontal overflow: {sizes}"
        if touch or width <= 740:
            columns = sizes["gridColumns"].split()
            assert len(columns) == 1, f"Expected one column at {width}px (touch={touch}): {sizes}"
        elif width >= 1160:
            assert len(sizes["gridColumns"].split()) == 3, f"Desktop grid changed: {sizes}"
        for n, geometry in enumerate(sizes["cards"], start=1):
            card, cover, image, meta, button = (
                geometry["card"], geometry["cover"], geometry["image"], geometry["meta"], geometry["button"]
            )
            def fail(reason: str):
                raise AssertionError(
                    f"At {width}px touch={touch} scale={scale}, card #{n}: {reason}: {geometry}"
                )
            if not geometry["imageLoaded"]:
                fail("Cover image did not load locally")
            if cover["width"] > card["width"] + 1:
                fail("Cover wider than its card")
            if image["width"] > cover["width"] + 1:
                fail("Cover image wider than cover")
            if meta["top"] < cover["bottom"] - 1.5:
                fail("TEXT OVERLAPS IMAGE")
            if card["bottom"] < meta["bottom"] - 2:
                fail("Text extends beyond card")
            if button["top"] < meta["top"] - 1 or button["bottom"] > meta["bottom"] + 1.5:
                fail("Read button outside text region")
            if card["left"] < -1 or card["right"] > sizes["innerWidth"] + 2:
                fail("Card extends offscreen")
        for n, geometry in enumerate(sizes["classics"], start=1):
            card, cover, image, meta, button = (
                geometry["card"], geometry["cover"], geometry["image"], geometry["meta"], geometry["button"]
            )
            assert geometry["imageLoaded"], f"Classic book cover #{n} failed to load"
            assert cover["width"] <= card["width"] + 1, f"Classic cover #{n} exceeds its card"
            assert image["width"] <= cover["width"] + 1, f"Classic image #{n} exceeds cover"
            assert meta["top"] >= cover["bottom"] - 1.5, f"Classic #{n} image/text overlap at {width}px"
            assert card["bottom"] >= meta["bottom"] - 2, f"Classic #{n} text outside card"
            assert button["bottom"] <= meta["bottom"] + 2, f"Classic #{n} button outside details"
            assert card["left"] >= -1 and card["right"] <= sizes["innerWidth"] + 2, f"Classic #{n} offscreen"
        print(f"PASS browser geometry width={width} touch={touch} text-scale={scale} BookDash={len(sizes['cards'])} classics={len(sizes['classics'])}")
    finally:
        context.close()


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="wondernet-mobile-check-") as directory:
        destination = Path(directory)
        subprocess.run([
            sys.executable, str(ROOT / "scripts/build_pages_preview.py"),
            "--output", str(destination), "--base-path", "",
        ], check=True, cwd=ROOT)
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=directory)
        server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            url = f"http://127.0.0.1:{server.server_port}{LIBRARY_ROUTE}"
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(channel="chrome", headless=True, args=["--no-sandbox"])
                try:
                    for width in (320, 360, 390, 430, 709, 980):
                        check_page(browser, url, width=width, touch=True)
                    for width in (768, 1024, 1280):
                        check_page(browser, url, width=width, touch=False)
                    check_page(browser, url, width=390, touch=True, scale=2.0)
                finally:
                    browser.close()
        finally:
            server.shutdown()
            worker.join(timeout=4)
            server.server_close()


if __name__ == "__main__":
    main()
