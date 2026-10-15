# Public WonderNet preview on GitHub Pages

This is a **developer preview**, NOT a child-ready product or a hosted Pi installation. It exists for adults to review the design, follow development, and offer feedback.

## Enable the deployment

The repository includes `.github/workflows/pages-preview.yml`. It builds a static copy of the real frontend and automatically deploys it on relevant changes to `main`. A repository owner must enable GitHub Pages in Settings; the connected GitHub app cannot change this setting.

1. Open https://github.com/KadenBar/wondernet/settings/pages.
2. Under **Build and deployment → Source**, choose **GitHub Actions** (not "Deploy from a branch").
3. Merge the pull request adding the workflow. If deployment ran before Pages was enabled and failed, open **Actions → Publish WonderNet developer preview** and use **Run workflow** on main (or rerun the failed workflow).
4. Confirm the green "Deploy public preview" job and visit **https://kadenbar.github.io/wondernet/**. This is an *expected* address, not a confirmed live site until GitHub Pages deploys it.

GitHub may take a few minutes to complete the deployment.

## What's in the preview

- Responsive homepage and six interior pages. The Library page now includes one original story, five complete US public-domain story-text editions, and a separately marked research-only list of eleven other unapproved candidates.
- Letter Match and Pattern Playground: five browser-only practice questions each.
- Circuit Garden: ten handcrafted circuit puzzles with session-only level progression; no data stored.
- Word Workshop: sixteen word-building puzzles, four thematic collections and optional hints, with in-memory progress only.
- Original five-chapter short-story reader at `/read/lantern/` with locally bundled prose, themes and text sizing, not age-reviewed.
- Five original-text Beatrix Potter stories under `/read/` with full US public-domain narrative, newly authored basic decorations and no historical illustrations. Human editorial and accessibility review is still pending.
- A prominent early-development warning banner on every page.
- No analytics, logins, ads, user uploads, chat or persistent learner data.
- Static asset links rewritten to work under `/wondernet/`.
- `noindex` tags ask search engines not to index the preview; they do not make it private.

## What is NOT deployed

- The FastAPI backend, including `/api/health` and `/api/catalog`.
- Raspberry Pi configuration, private Wi-Fi, TLS and host isolation.
- General-purpose imported EPUB/PDF media, historical picture-book illustrations, bulk ebook viewers/importers, uploads, code labs, multiplayer, progress, accounts, or production security features.

GitHub Pages is publicly accessible over the internet. It does **not** demonstrate offline-first networking and is **not approved for children or unsupervised learner use**. Do not use it to gather children's data. Adult contributors can download and run the prototype bound to `127.0.0.1` if they need to test the API.

## Preview build commands

From the repository root with Python 3.11+:

```bash
python scripts/build_pages_preview.py --output _site --base-path /wondernet
python -m pytest -q
```

For a local preview hosted at the root rather than a repository subpath, use `--base-path ""` and serve the exported files with a local HTTP server. GitHub Pages uses the `/wondernet` prefix because this repository is a project site, not an account-root site.

## Ongoing updates

Changes to `frontend/**`, the preview builder or deployment workflow on `main` automatically rebuild the static preview. Backend changes do not deploy. If the repository name, Pages path or custom domain changes, adjust `--base-path`. The deployment job has narrowly scoped Pages permissions and depends on a successful build.

## Safety and accessibility follow-up

This preview only proves that the basic site renders. Manual mobile, keyboard, screen-reader and contrast testing is required before any child-facing use.
