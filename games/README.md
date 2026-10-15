# WonderNet Arcade and WonderParty

## Circuit Garden: first standalone game (playable alpha)

Circuit Garden is a single-player local browser puzzle with **10 handcrafted levels**.
Rotate circuit tiles to carry power from a fixed battery to every flower. Connected
pipes glow; powered flowers bloom. Later levels have branches and multiple flowers.
There are no timers. Levels unlock only in the current page session, and star
ratings, moves and hints are held in memory only.

- Start the FastAPI developer server at `127.0.0.1:8000` and open `/play/circuit-garden`.
- Or build the public GitHub Pages developer preview and open `/play/circuit-garden/`.
- Play with mouse/touch or keyboard (Tab, arrow keys, Enter/Space or R).
- Restart any unlocked puzzle, or request a hint that turns one tile.

All CSS and JavaScript files are hosted locally, and the game makes no network
calls. Once served from a local WonderNet installation, the game itself has no
internet dependency. **The Raspberry Pi offline Wi-Fi hotspot is not ready yet.**

The engine is in `frontend/assets/circuit-engine.js`. Tests run with
`node --test tests/circuit-garden.test.cjs`, including full puzzle solvability.

Circuit Garden is a development demo, **not validated for unsupervised child
use or accessibility with assistive technology**. Educator, parent and
accessibility reviews are welcome.

## Earlier prototype practice activities

Letter Match and Pattern Playground are small five-round practice activities,
not stand-alone Arcade games. Neither stores answers or progress.

## Planned

WonderParty local multiplayer, simulations and bigger adventures remain
unimplemented. Future multiplayer must use local server authorization and
appropriate moderation and security controls. No unreviewed packages execute
on the main WonderNet host.
