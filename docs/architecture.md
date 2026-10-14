# WonderNet Architecture — proposed

Connected phone/tablet/laptop → future isolated Wi-Fi → future reverse proxy/TLS → FastAPI → future SQLite and reviewed local content packages.

The Pi 4B serves the site and stores approved data; browser clients render games wherever possible.

**Current:** Static local frontend, two read-only API endpoints, no account data, no uploads, no external runtime dependencies.

**Planned:** Accounts, progress, offline indexed library, accessible games, private multiplayer, administrator content import, signed offline updates.

**Boundaries:** Clients are untrusted, lessons are data rather than executable imports, student code must not reach the Pi host, administration is separately protected.

Do not deploy development Uvicorn with --reload to users. See security/THREAT_MODEL.md.
