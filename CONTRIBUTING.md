# Contributing to WonderNet

Welcome! WonderNet aims to make **offline learning and play accessible on affordable hardware**. We welcome help from educators, developers, designers, disabled users, security researchers, parents and hobbyists.

> **Alpha caution:** WonderNet is a proof of concept, not a child-ready service. Please do not use real learner information for testing.

## Good first contributions

- Improve documentation and beginner-friendly setup instructions.
- Add or clarify accessible interaction patterns (keyboard, screen reader, reduced motion).
- Propose simple, offline-first puzzles or curriculum outlines.
- Extend tests and threat modeling for currently implemented functionality.
- Suggest and validate evidence-informed foundational literacy lessons.

See [the roadmap](docs/roadmap.md) and [the issues page](https://github.com/KadenBar/wondernet/issues). Please open an issue before large rewrites or new dependencies.

## Local workflow

1. Fork/clone the repository and create a descriptive branch.
2. Set up Python 3.11+ following the [README](README.md#run-the-prototype).
3. Make the smallest reasonable change and add tests.
4. Run `python -m pytest -q`; check keyboard navigation and mobile layout for UI changes.
5. Open a pull request using our template. Explain changes, testing, accessibility and security impact.

## Definition of done

- **Offline-first:** No CDN, tracking scripts, mandatory cloud dependencies or remote asset loads at runtime.
- **Accessible:** Semantic HTML, visible focus, WCAG 2.2 AA targets where applicable, no inaccessible drag-only gameplay.
- **Safe:** No arbitrary student code on host, unreviewed active uploads, privileged file access or secrets in git.
- **Age-appropriate:** No personal information, unsafe challenges, public matchmaking or child-directed ads.
- **Licensable:** Code and contributed media are yours to contribute and appropriately licensed. Include provenance/attribution for third-party material.
- **Honest:** Clearly distinguish prototypes from planned or supported functionality.

## Code organization

- `backend/` API and application logic
- `frontend/` interface and local assets
- `curriculum/` lesson definitions/metadata
- `games/` game definitions and eventual first-party games
- `library/` planned catalog/import
- `security/` threat models
- `tests/` automated tests

## Source-code license

WonderNet code contributions accepted into this repository are intended to be licensed under **GNU AGPL-3.0-only** (see [LICENSE](LICENSE)). By submitting a contribution, confirm you have the right to license it under those terms and that any included code or assets have compatible licenses. You retain copyright in your original contributions. If your employer or another party owns your code, get permission before contributing.

Educational media, books, artwork and other content may have different licenses; do not assume they are covered by the software license. See [the licensing policy](docs/license-decision.md).

## Security & conduct

**Never report a vulnerability in a public issue.** Follow [SECURITY.md](SECURITY.md). Never include tokens, secrets, child data, private correspondence or exploit instructions that endanger real users.

Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). We aim for a constructive, patient learning community.

Maintainers may request changes or decline code that would increase risk or maintenance burden.
