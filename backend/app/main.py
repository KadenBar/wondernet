# SPDX-License-Identifier: AGPL-3.0-only
# Copyright (c) 2026 WonderNet contributors
"""WonderNet local development server. No accounts, uploads, or user code execution."""
from pathlib import Path
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[2]
FRONTEND = ROOT / "frontend"
CATALOG = ROOT / "curriculum" / "catalog.json"
SECTIONS = frozenset({"early-learning", "academy", "special-interests", "arcade", "library", "wonderparty"})
ACTIVITIES = {"letter-match", "patterns", "circuit-garden", "word-workshop"}
READABLE_BOOKS = {
    "lantern": "book-lantern.html",
    "mara-garden": "book-mara-garden.html",
    "peter-rabbit": "book-peter-rabbit.html",
    "benjamin-bunny": "book-benjamin-bunny.html",
    "tom-kitten": "book-tom-kitten.html",
    "jemima-puddle-duck": "book-jemima-puddle-duck.html",
    "jeremy-fisher": "book-jeremy-fisher.html",
}

app = FastAPI(title="WonderNet Prototype", version="0.1.0", docs_url=None, redoc_url=None, openapi_url=None)

@app.middleware("http")
async def basic_security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=(), payment=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; "
        "connect-src 'self'; font-src 'self'; form-action 'self'; object-src 'none'; "
        "base-uri 'none'; frame-ancestors 'none'"
    )
    if request.url.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response

@app.get("/api/health")
def health():
    return {"status": "ok", "release": "alpha-0.1"}

@app.get("/api/catalog")
def catalog():
    return json.loads(CATALOG.read_text(encoding="utf-8"))

app.mount("/assets", StaticFiles(directory=FRONTEND / "assets"), name="assets")

@app.get("/", include_in_schema=False)
def home():
    return FileResponse(FRONTEND / "index.html", media_type="text/html")

@app.get("/explore/{section}", include_in_schema=False)
def section_page(section: str):
    if section not in SECTIONS:
        raise HTTPException(status_code=404)
    return FileResponse(FRONTEND / "pages" / f"{section}.html", media_type="text/html")

@app.get("/read/{book}", include_in_schema=False)
def read_book(book: str):
    if book not in READABLE_BOOKS:
        raise HTTPException(status_code=404)
    return FileResponse(FRONTEND / "pages" / READABLE_BOOKS[book], media_type="text/html")

@app.get("/play/{activity}", include_in_schema=False)
def activity_page(activity: str):
    if activity not in ACTIVITIES:
        raise HTTPException(status_code=404)
    return FileResponse(FRONTEND / "pages" / f"{activity}.html", media_type="text/html")
