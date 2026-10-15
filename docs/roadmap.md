# Roadmap

This is a **living plan**, not a release promise. Each milestone has explicit acceptance criteria and safety gates. Feature descriptions in the [vision](vision.md) do not mean those features are implemented.

## ✅ Alpha 0.1 — Foundation (prototype)
- [x] Repository structure for backend, frontend, curriculum, games, library and security
- [x] Responsive six-section homepage and local section filtering
- [x] FastAPI read-only `/api/health` and `/api/catalog`
- [x] Core security headers, local-only development instructions, smoke tests and CI workflow
- [x] First threat model, accessibility guidelines and contribution documentation

## 🔧 Alpha 0.2 — Public project foundation
- [ ] Confirm AGPL-3.0-only code licensing, copyright rights and content licensing before visibility changes
- [ ] Review repository contents and full Git history for credentials and personal data
- [ ] Enable private vulnerability reporting and establish a maintainer contact process
- [ ] Confirm CI passes; set appropriate branch protections and dependency updates
- [ ] Run manual keyboard, mobile, high-contrast and screen-reader reviews
- [ ] Finalize content/game metadata schemas and trust boundaries
- [ ] Publish accurate screenshots and a release-notes template

## 🥧 Alpha 0.3 — Offline Pi networking
- [ ] Preserve existing Pi installation and inspect storage/RAM
- [ ] Standalone Wi-Fi hotspot + local name resolution
- [ ] Test client-to-client isolation and home-LAN denial
- [ ] Protected admin access and local HTTPS trust strategy
- [ ] Offline functional and recovery tests

## 📚 Alpha 0.4 — Library + first learning activity
- [x] Rights-scoped eleven-book research catalog with metadata and a local-only filtered preview (no files installed)
- [ ] Review and approve a small, varied set of exact licensed editions before distributing any media
- [ ] Secure administrator-only media import with size/type and archive checks
- [x] First original five-chapter static reader demo with adjustable type, colors and chapters (manual a11y review pending)
- [x] Five complete US public-domain story texts packaged as read-only developer previews, with simple new decoration (period illustrations omitted, content/a11y review pending)
- [ ] Generalized approved-content reader and offline indexed search
- [x] First informal spelling/word-building game: Word Workshop (16 puzzles, not a phonics curriculum)
- [ ] One evidence-informed early phonics activity and accessible alternatives
- [ ] Educator review and manual keyboard/touch/screen-reader tests for Word Workshop
- [ ] Content provenance/licensing metadata and export/import validation

## 🎮 Alpha 0.5 — Arcade + WonderParty
- [x] One ten-level, locally hosted Circuit Garden puzzle game (prototype only, awaiting manual accessibility validation)
- [ ] Verify full keyboard, touch, screen-reader and contrast accessibility of Circuit Garden
- [ ] Private room-code party game with server-authoritative membership
- [ ] Local multiplayer test across phones/tablets; host controls and abuse cases
- [ ] Accessibility and load tests for games

## 🌱 Later possibilities
- [ ] Student profiles, permissions and progress after security/privacy review
- [ ] Browser-isolated JavaScript/Python exercises with bounded resources
- [ ] Higher-assurance, separately isolated advanced cybersecurity labs
- [ ] Age-based programming/cybersecurity and trades learning pathways
- [ ] Complex simulations, mysteries and cooperative adventures
- [ ] Curated user-installable content packages with verified offline updates

## How to help

Open an issue using our templates. Small, well-tested contributions are especially welcome. See [CONTRIBUTING.md](../CONTRIBUTING.md).

**The release safety bar is higher than the development demo bar.** An alpha milestone does not imply suitability for production, classroom or unsupervised child use.
