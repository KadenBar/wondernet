# 🌐 WonderNet

### A little internet. A lot of possibility.

**Building a safer offline internet for kids: educational, free and open source. Designed to run on accessible hardware like the Raspberry Pi 4B.**

[![Status: Alpha 0.1](https://img.shields.io/badge/status-alpha%200.1-52627c)](docs/roadmap.md)
[![License: AGPLv3](https://img.shields.io/badge/license-AGPLv3-137c72)](LICENSE)
[![CI checks](https://github.com/KadenBar/wondernet/actions/workflows/checks.yml/badge.svg)](https://github.com/KadenBar/wondernet/actions/workflows/checks.yml)

> [!IMPORTANT]
> **Early development preview — not ready for children or public deployment.** The working app currently shows a prototype homepage, six navigable section pages, two tiny practice activities, a ten-level Circuit Garden puzzle game, live section filtering and two read-only API endpoints. Full courses, advanced games, uploads, multiplayer, accounts and the Pi Wi-Fi hotspot are **planned**, not released.

**[Vision](docs/vision.md) · [Roadmap](docs/roadmap.md) · [Run locally](#run-the-prototype) · [Contribute](CONTRIBUTING.md) · [Security](SECURITY.md) · [Public launch checklist](docs/public-launch-checklist.md)**

---

## Why WonderNet?

What if a kid could connect a tablet to a tiny offline network and find **phonics games, science experiments, coding lessons, a library and party games with friends**—all without cloud accounts, subscription fees, trackers or public internet?

WonderNet is an attempt to build that. But it's not only for kids: the long-term vision includes career skills, trades, and adult education.

We're deliberately building a **fast, accessible website**, not a virtual town that you have to walk through to get to a lesson.

## Six destinations, one little internet

| Destination | What we're planning |
|:---|:---|
| 🔤 **Early Learning** | Evidence-informed phonics, reading and foundational math, with offline audio and accessible alternatives |
| 📚 **Academy** | Elementary → middle → high school → adult learning pathways, without rigid age locks |
| 💻 **Special Interests** | Programming, cybersecurity, networking, digital forensics, engineering and skilled trades |
| 🎮 **Arcade** | *Just-for-fun* puzzles, cozy simulations, creative sandbox games, mysteries and RPGs |
| 📖 **Library** | Searchable offline books, audio, videos and educational resources; safe admin-approved imports |
| 🎉 **WonderParty** | Original kid-friendly room-code games: drawing, trivia and cooperative mysteries, entirely on the local network |

**The Arcade is not a reward for finishing lessons.** Learning and entertainment are equally valid reasons to open WonderNet.

## What exists today?

| Ready to explore | Still to be built |
|:---|:---|
| Responsive six-section homepage and interior pages | Full curriculum and phonics games |
| Search/filter for homepage sections | Searchable library and reviewed uploads |\n| Circuit Garden (10 puzzles) and two practice demos | Larger games, adaptive lessons and learner progress |
| Local-only FastAPI prototype | Student profiles and progress |
| Read-only health/catalog API | Secure multiplayer rooms and game engines |
| Security/accessibility planning docs | Pi hotspot, local TLS and segmented networking |
| Smoke tests and automated CI | Browser code sandbox and isolated cyber labs |

See the [roadmap](docs/roadmap.md) for phased milestones. We will never describe an unreleased feature as working.

## Build principles

- **Offline means offline.** No cloud sign-in, mandatory internet access, advertising, analytics trackers or remote frontend CDNs.
- **Accessibility is foundational.** Target WCAG 2.2 AA where applicable; design for keyboard and assistive technology use, flexible reading levels, reduced motion, captions, and accessible game controls.
- **Curiosity deserves a safe sandbox.** Student browsers, uploaded content and programming exercises are untrusted. Do not execute student code on the production Pi.
- **Minimize children's data.** Future profiles and uploads require an explicit privacy and authorization design before implementation.
- **Keep learning age-flexible.** Age-appropriate pathways exist, but access to foundational skills should not be embarrassing or blocked for older learners.
- **Make contribution approachable.** Modular content, simple technology, documented standards and reviewed community contributions.

[Architecture](docs/architecture.md) · [Accessibility](docs/accessibility.md) · [Threat model](security/THREAT_MODEL.md)

## Public website preview

The **[GitHub Pages developer preview](https://kadenbar.github.io/wondernet/)** lets adults explore our early homepage, six section pages, two practice activities and the Circuit Garden puzzle game. It is publicly hosted and updates from `main` after a successful Pages deployment. See the [preview guide](docs/pages-preview.md).

**Important:** This is a public internet-hosted static UI preview, not an offline Raspberry Pi deployment, a complete curriculum, or a child-safe release. The FastAPI backend is deliberately not published to Pages.

## Run the prototype

You **do not need a Raspberry Pi** to run this first build.

Requirements: Python **3.11+** and Git. Install dependencies on an internet-connected development computer; the **running prototype itself** needs no cloud services.

**Windows PowerShell**

```powershell
git clone https://github.com/KadenBar/wondernet.git
cd wondernet
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

**macOS / Linux**

```bash
git clone https://github.com/KadenBar/wondernet.git
cd wondernet
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

Visit **http://127.0.0.1:8000** to explore. Open any of the six section cards, or try **Letter Match** at **/play/letter-match** and **Pattern Playground** at **/play/patterns**, or **Circuit Garden** at **/play/circuit-garden**. See [web pages and activities](docs/web-pages.md). Stop with `Ctrl+C`. Run tests with:

```bash
python -m pytest -q
```

**Security:** Keep the development server on `127.0.0.1`. It has no user authentication or hardened deployment environment. Do **not** expose it to children, a shared Wi-Fi network or the public internet.

## Inside the repo

```text
backend/          FastAPI service (read-only prototype)
frontend/         Website and locally served assets
curriculum/       Course manifest examples and future lesson modules
games/            Arcade game catalog and WonderParty plans
library/          Offline library design placeholder
security/         Threat model and security engineering decisions
docs/             Roadmap, architecture, accessibility, launch checklists
tests/            Automated smoke tests
.github/          CI, issue templates, pull-request templates
```

## Follow the build / get involved

Curious? **Star** this project to bookmark it, **Watch** for updates, or look through the [roadmap](docs/roadmap.md) and [issues](https://github.com/KadenBar/wondernet/issues). Educators, accessibility advocates, parents, game creators and security folks are welcome.

For ideas or bugs, use the provided issue templates. For code contributions, see [CONTRIBUTING.md](CONTRIBUTING.md). **Do not publish vulnerability details in issues**; see [SECURITY.md](SECURITY.md).

> **License and content:** WonderNet source code uses the [GNU Affero General Public License v3 (AGPL-3.0-only)](LICENSE). Modified covered versions distributed or operated for users over a network have applicable source-code disclosure obligations; contributors do not have to submit those changes back to this repository. Books, game assets, media and user-supplied resources require separate redistribution rights. **WonderNet** is a working name pending trademark clearance. No official affiliation with KidNet or any other product is claimed.

*Little hardware. Big curiosity. Built openly, carefully, and one step at a time.*
