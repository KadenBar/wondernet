# WonderNet 🌐

**WonderNet** is an offline-first, accessible educational and entertainment platform designed to run on a Raspberry Pi 4B and serve connected phones, tablets, and computers.

> **Status: early prototype (Alpha 0.1).** This repository is NOT ready for child accounts, public Wi-Fi deployment, arbitrary code execution, or untrusted uploads. The first build provides the foundational app, documentation, and tests only.

## Our vision

- **Learn:** Early literacy (including systematic phonics), K–12, adult education, programming, cybersecurity, skilled trades, and life skills.
- **Play:** A standalone arcade of puzzles, simulations, cozy games, mysteries, and party games—not activities gated behind lessons.
- **Connect locally:** Private, in-person multiplayer games, including an original kid-friendly Jackbox-style experience.
- **Explore offline:** A searchable library of books, audio, videos, lessons and appropriately licensed resources, with safe, administrator-controlled imports later.
- **Learn your way:** Accessible navigation and activities, with multiple presentation modes and adjustable accommodations.

We intentionally use a **traditional website interface** rather than a character-controlled world. Users should return to lessons and games with one click.

## What works today

- A responsive, keyboard-friendly prototype homepage with live section filtering.
- A read-only FastAPI backend exposing `/api/health` and `/api/catalog`.
- Baseline security response headers and loopback-only development instructions.
- Project structure, architecture documentation, security policy, and automated smoke tests.

**Not yet implemented:** authentication, content uploading, learning progression, code execution, multiplayer, Wi-Fi hotspot, server-side games, account data, or cybersecurity labs. The homepage is a preview, not a production service.

## Run on your computer (no Raspberry Pi required)

Requirements: Python **3.11+** and Git (for version control). The setup command installs Python dependencies and therefore needs internet on your development computer **once**; after installation, this prototype works without external services.

### Windows (PowerShell)

```powershell
cd wondernet
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

### macOS / Linux

```bash
cd wondernet
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Open **http://127.0.0.1:8000**. Stop with `Ctrl+C`.

To run tests:

```bash
python -m pytest -q
```

**Security note:** Keep development bound to `127.0.0.1`. Do **not** use `--host 0.0.0.0`, expose port 8000, or place this prototype on a child-accessible Wi-Fi network. Deployment hardening, TLS, accounts, and upload safety are not yet in place.

## Repository map

```text
wondernet/
├── backend/           # FastAPI service (currently read-only)
├── frontend/          # Accessible website prototype and local assets
├── curriculum/        # Versioned lesson/module manifests; no executable imports
├── games/             # Future first-party games and party-game manifests
├── security/          # Threat model and security design requirements
├── docs/              # Architecture, accessibility, roadmap, license decision
├── tests/             # App smoke tests
└── .github/           # CI checks and future community issue templates
```

## Project guardrails

1. **Safety/security first:** User-submitted code must never run as an OS process on the production Pi. Browser-based editors will use restricted execution contexts; advanced security labs will be separately isolated.
2. **Offline by default:** No required cloud login, tracking SDKs, ads, or external CDN dependencies.
3. **Accessibility by design:** Target WCAG 2.2 AA where applicable. Provide keyboard access, readable content, clear focus indicators, captions/transcripts, reduced motion, and alternative ways to use games.
4. **Age-appropriate without gatekeeping:** Different curricular levels for early learning through adulthood, with flexible progress and age-respectful UI.
5. **Privacy:** Collect as little learner data as possible, and don't ship real student data or secrets in Git.
6. **Respect third-party rights:** Educational media, game assets, books, and community contributions must have redistribution-compatible licenses or remain user-supplied.

## Licensing

The **initial code license is MIT**, documented in [`LICENSE`](LICENSE) and [`docs/license-decision.md`](docs/license-decision.md). This is a *provisional project decision to review before publication*. Third-party educational content and game assets are not automatically covered by this license. The name **WonderNet** is a working name, not a cleared trademark.

## Contributing and security

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for contribution practices and [`SECURITY.md`](SECURITY.md) for private vulnerability reporting. Please do not create public issues containing exploit details or personal information.

## Milestone

Our first milestone is a locally running, tested homepage. Later milestones include Pi networking, the safe library, phonics, an accessible puzzle, and an original private-room WonderParty prototype. See [`docs/roadmap.md`](docs/roadmap.md).
