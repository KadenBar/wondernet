# Website pages and first mini activities

WonderNet's early site has six direct section routes and four playable browser activities, including two standalone games. Navigation is deliberately website-style; no explorable hub, account or progress barrier.

| URL | State |
| --- | --- |
| `/` | Homepage with featured Circuit Garden and Word Workshop, plus two practice activities, six sections, and local filtering |
| `/explore/early-learning` | Playable Word Workshop plus Letter Match practice |
| `/explore/academy` | Planned subjects and pathways |
| `/explore/special-interests` | Planned coding, defensive cyber and trades |
| `/explore/arcade` | Links to Circuit Garden plus a small pattern practice activity |
| `/explore/library` | Planned content library and import review |
| `/explore/wonderparty` | Planned private local party games |
| `/play/letter-match` | Five-round uppercase/lowercase recognition activity |
| `/play/patterns` | Five-round shape/pattern reasoning practice |
| `/play/circuit-garden` | Ten-level circuit-rotation puzzle game; mouse, touch and keyboard support |
| `/play/word-workshop` | Sixteen hands-on spelling/letter-building puzzles across four themed worlds |

## Interior design refresh

All six section pages now share a lightweight, locally hosted style sheet (`frontend/assets/interiors.css`) while giving each section its own colors and illustrative concept artwork. The two mini activities use the same visual language and show a semantic five-round progress indicator. That progress is maintained only in the current browser page's memory, never written to accounts, local storage or the server.

The individual section illustrations depict **concepts**, not live applications. Features marked `PLANNED` remain unimplemented. Learner pages still link only to allowed local WonderNet routes; the public developer-preview banner is the exception for adult contributors.

Mobile/keyboard/assistive-tech manual review remains necessary. A passing build does not establish child-ready safety or curriculum validity.

## Important limits

The Letter Match and Pattern Playground activities are intentionally tiny prototype exercises, not evidence-based literacy curricula or validated child-ready games. We have not yet validated phonics outcomes, accessibility with assistive technologies, or suitability for independent child use. No new server-side state, accounts, analytics, cookies, uploads, multiplayer or code execution are introduced.

Practice questions and choices are hard-coded in `frontend/assets/activities.js`. The activities keep state only in browser memory until refresh; they make no fetch requests. Circuit Garden uses a separate puzzle engine, `frontend/assets/circuit-engine.js`, with handcrafted and automated-tested levels. Its unlocks, moves and star ratings live only in browser memory, and reset on reload. Word Workshop uses its own tested tile engine (`frontend/assets/word-workshop-engine.js`), and holds letter placements, hints, mistakes, stars and unlocks in memory only. It includes an optional desktop drag-and-drop gesture and accessible tap/click/keyboard button alternatives; no voices or external dictionaries.

All CSS/JS remains local. No remote content or external hyperlinks are embedded in learner pages; GitHub links remain in repository documentation, not in the browser-facing learning experience.

The GitHub Pages export adds an explicit **adult developer-preview banner** with a contributor link to GitHub. That link does not exist in the actual learner-facing homepage served by FastAPI, which displays the repository address as text only. This keeps its clickable navigation local while still letting adult reviewers find the source in the public preview.

All `/explore/{section}` and `/play/{activity}` routes are hard-coded allowlists in `backend/app/main.py`. No arbitrary file paths, route names or dynamic user-provided assets are accepted.

Word Workshop is informal English spelling/word-building practice using visual and text clues. It is **not** a validated phonics or reading curriculum, and needs an educator review as well as manual accessibility testing before child use.

## Next improvements

1. Manually test keyboard, screen reader and mobile behaviors (including reduced motion and text zoom) before broad distribution.
2. Get educator input before expanding print recognition into phonics. Don't substitute TTS pronunciation for validated sound recordings.
3. Build local reviewed-library metadata and imports only after permission/sandbox/threat-model work.
4. Introduce richer games without adding user tracking or unsafe host-side execution.
