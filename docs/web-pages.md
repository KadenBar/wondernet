# Website pages and first mini activities

WonderNet's early site has six direct section routes and four playable browser activities, including two standalone games. Navigation is deliberately website-style; no explorable hub, account or progress barrier. One original five-chapter short story and five complete public-domain US story texts are locally readable through the Library.

| URL | State |
| --- | --- |
| `/` | Homepage with featured Circuit Garden and Word Workshop, plus two practice activities, six sections, and local filtering |
| `/explore/early-learning` | Playable Word Workshop plus Letter Match practice |
| `/explore/academy` | Planned subjects and pathways |
| `/explore/special-interests` | Planned coding, defensive cyber and trades |
| `/explore/arcade` | Links to Circuit Garden plus a small pattern practice activity |
| `/explore/library` | Six locally readable stories (one original, five complete US public-domain texts) plus a separate 11-title unapproved research queue |
| `/explore/wonderparty` | Planned private local party games |
| `/play/letter-match` | Five-round uppercase/lowercase recognition activity |
| `/play/patterns` | Five-round shape/pattern reasoning practice |
| `/play/circuit-garden` | Ten-level circuit-rotation puzzle game; mouse, touch and keyboard support |
| `/play/word-workshop` | Sixteen hands-on spelling/letter-building puzzles across four themed worlds |
| `/read/lantern` | Original five-chapter story with local reading themes, text sizing and chapter navigation |
| `/read/peter-rabbit`, `/read/benjamin-bunny`, `/read/tom-kitten`, `/read/jemima-puddle-duck`, `/read/jeremy-fisher` | Full US public-domain story texts by Beatrix Potter with page navigation; historical illustrations not included |

## Original offline story reader

**The Lantern That Kept the Stars** is original, embedded in `frontend/pages/book-lantern.html`, and exported to `/read/lantern/`. Its CSS and JavaScript are local, with no external resources, trackers, accounts or persistence. Chapter navigation, text scaling and paper/night/high-contrast reading themes operate in memory; a chapter URL fragment is shareable. `library/reader-demos.json` tracks sample rights and pending review. The sample is not an approved children's book or an arbitrary third-party ebook viewer.

## Five complete US public-domain stories

The first imported story texts are the complete narrative of **The Tale of Peter Rabbit**, **The Tale of Benjamin Bunny**, **The Tale of Tom Kitten**, **The Tale of Jemima Puddle-Duck** and **The Tale of Mr. Jeremy Fisher**, authored by Beatrix Potter and originally published 1902–1908. Each uses a strictly allowlisted read-only static page, a local browser reader, and original WonderNet-made decorative SVG. The historical book illustrations were **not imported** due to image transfer restrictions and must never be presented as included. The original narrative has been transcribed from public-domain US editions using a mirror of Project Gutenberg, with page breaks added and whitespace normalized; `library/complete-text-editions.json` records exact source ebook numbers and source blob SHAs. No general-purpose importer, upload API, untrusted HTML rendering, or externally hosted images were introduced. **Copyright status is US-specific** and editorial, accessibility and child-suitability checks remain pending. Adults can preview the texts; do not describe this as an approved child library.

## First Library research shelf

The Library section exposes an offline-capable **metadata-only** preview of eleven potential titles, each clearly labeled *under review*. The source-of-truth curation queue is `library/catalog.json`; the local page contains only safe display metadata, not outside provider links or downloadable books. These eleven other candidate items all have uncompleted rights, content, accessibility and package review gates. They must not be served to learners until each specific edition is approved and separately imported into secure offline storage.

## Interior design refresh

All six section pages now share a lightweight, locally hosted style sheet (`frontend/assets/interiors.css`) while giving each section its own colors and illustrative concept artwork. The two mini activities use the same visual language and show a semantic five-round progress indicator. That progress is maintained only in the current browser page's memory, never written to accounts, local storage or the server.

The individual section illustrations depict **concepts**, not live applications. Features marked `PLANNED` remain unimplemented. Learner pages still link only to allowed local WonderNet routes; the public developer-preview banner is the exception for adult contributors.

Mobile/keyboard/assistive-tech manual review remains necessary. A passing build does not establish child-ready safety or curriculum validity.

## Important limits

The Letter Match and Pattern Playground activities are intentionally tiny prototype exercises, not evidence-based literacy curricula or validated child-ready games. We have not yet validated phonics outcomes, accessibility with assistive technologies, or suitability for independent child use. No new server-side state, accounts, analytics, cookies, uploads, multiplayer or code execution are introduced.

Practice questions and choices are hard-coded in `frontend/assets/activities.js`. The activities keep state only in browser memory until refresh; they make no fetch requests. Circuit Garden uses a separate puzzle engine, `frontend/assets/circuit-engine.js`, with handcrafted and automated-tested levels. Its unlocks, moves and star ratings live only in browser memory, and reset on reload. Word Workshop uses its own tested tile engine (`frontend/assets/word-workshop-engine.js`), and holds letter placements, hints, mistakes, stars and unlocks in memory only. It uses Pointer Events for mouse and touchscreen tile dragging, with tap/click/keyboard button alternatives. The dragged tile follows the pointer and highlights valid word spaces; no voices or external dictionaries. The original native HTML drag-and-drop was unreliable on mobile and is no longer used. Touch Events with non-passive touchstart/touchmove listeners now prevent the browser from scrolling when dragging starts on a letter. A user-controlled precise placement mode allows selecting a letter and then selecting the destination space without dragging. For a deploy, the Word Workshop page versions its CSS/JS asset links so mobile browsers request updated files.

All CSS/JS remains local. No remote content or external hyperlinks are embedded in learner pages; GitHub links remain in repository documentation, not in the browser-facing learning experience.

The GitHub Pages export adds an explicit **adult developer-preview banner** with a contributor link to GitHub. That link does not exist in the actual learner-facing homepage served by FastAPI, which displays the repository address as text only. This keeps its clickable navigation local while still letting adult reviewers find the source in the public preview.

All `/explore/{section}`, `/play/{activity}` and `/read/{book}` routes are hard-coded allowlists in `backend/app/main.py`. No arbitrary file paths, route names or dynamic user-provided assets are accepted.

Word Workshop is informal English spelling/word-building practice using visual and text clues. It is **not** a validated phonics or reading curriculum, and needs an educator review as well as manual accessibility testing before child use.

## Next improvements

1. Manually test keyboard, screen reader and mobile behaviors (including reduced motion and text zoom) before broad distribution.
2. Get educator input before expanding print recognition into phonics. Don't substitute TTS pronunciation for validated sound recordings.
3. Build local reviewed-library metadata and imports only after permission/sandbox/threat-model work.
4. Introduce richer games without adding user tracking or unsafe host-side execution.
