# Website pages and first mini activities

WonderNet's early site now has six direct section routes. Navigation is deliberately website-style; no explorable hub, account or progress barrier.

| URL | State |
| --- | --- |
| `/` | Homepage and live section filter |
| `/explore/early-learning` | Section preview, links to Letter Match |
| `/explore/academy` | Planned subjects and pathways |
| `/explore/special-interests` | Planned coding, defensive cyber and trades |
| `/explore/arcade` | Section preview, links to Pattern Playground |
| `/explore/library` | Planned content library and import review |
| `/explore/wonderparty` | Planned private local party games |
| `/play/letter-match` | Five-round uppercase/lowercase recognition activity |
| `/play/patterns` | Five-round shape/pattern reasoning activity |

## Important limits

The two activities are intentionally tiny prototype exercises, not evidence-based literacy curricula or validated child-ready games. We have not yet validated phonics outcomes, accessibility with assistive technologies, or suitability for independent child use. No new server-side state, accounts, analytics, cookies, uploads, multiplayer or code execution are introduced.

Questions and choices are hard-coded in `frontend/assets/activities.js`. The activities keep state only in browser memory until refresh; they make no fetch requests. All CSS/JS remains local. No remote content or external hyperlinks are embedded in learner pages; GitHub links remain in repository documentation, not in the browser-facing learning experience.

All `/explore/{section}` and `/play/{activity}` routes are hard-coded allowlists in `backend/app/main.py`. No arbitrary file paths, route names or dynamic user-provided assets are accepted.

## Next improvements

1. Manually test keyboard, screen reader and mobile behaviors (including reduced motion and text zoom) before broad distribution.
2. Get educator input before expanding print recognition into phonics. Don't substitute TTS pronunciation for validated sound recordings.
3. Build local reviewed-library metadata and imports only after permission/sandbox/threat-model work.
4. Introduce richer games without adding user tracking or unsafe host-side execution.
