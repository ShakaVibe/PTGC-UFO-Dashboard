# Dashboard panels redesign — mock-ups (2026-09-30)

Second half of the header-v2 day. Shaka brought a mock-up of the four panels under the KPI tiles (Burn /
Value Generated / Token Allocation / DAO Treasury) and the LP Pairs table; he liked the feel — art inside each
box in the box's colour, bigger figures, glass tiles — but wants the real logos, his own art (subtle, not busy)
and no Buy/Sell column on the pairs table. Routine he chose: **mock-ups first, one panel at a time**, then the
build behind the same v2 preview switch as the header.

## Approved (each file is standalone; renders in `renders/`)
| Panel | File | Approved as | Notes |
|---|---|---|---|
| Total Supply Burned | `mock-burn-v1.html` | **v1c** | Fire-tinted crop of the cosmic art (left nebula + mountains, no alien). Bar copied from his mock-up: flames inside the fill (`assets/flames.png`, a strip of the fire-tinted mountain glow screened over a red→white gradient), white-hot tip, white-cored end dot with a three-layer halo, faint embers in the empty track. Logo 30 px, camera at full brightness. |
| Value Generated | `mock-vg-v1.html` | **v1c** | The green side of the header band (two planet rims, nebula, mountains), as painted, lighter veil ("I want to see more green"). Period switch sits beside the headline — the title row can't hold both toggles at panel width. |
| Token Allocation | `mock-alloc-v1.html` | **v1e** | Band centre shifted gold → purple. The donut, after studying his reference pixel by pixel: **flat, fully saturated slices, no gloss/shading**, hairline seams, a thin bright line on both rims, a faint darkening at the inner edge, the hole a dark glossy sphere behind the real logo, **no glow outside the ring** (v1d had one — removed). Built as a CSS `conic-gradient` masked to a ring + an SVG overlay. Legend dots are glass beads. Creature strip with counts (his tick) replaces the 2-row grid with 🦑→🐚. |
| DAO Treasury | `mock-dao-v1.html` | **v1b** | Band left shifted gold → blue, saturated ("a little more blue"). Total DAO Value as the headline (his tick), four tiles with a big icon each in a lit blue square. The fourth tile still repeats the total, as in his mock — open. |
| PTGC Burned by UFO (UFO page) | `mock-ufoburn-v1.html` | **v1** | No mock-up from Shaka — derived from the Burn panel in sky blue on the treasury backdrop: three glass tiles (Burned / USD Value / % of PTGC in their colours), the flame bar in **UFO green** (`assets/flames-green.png`; Shaka: green, not blue), creatures, period boxes. |

## Shared language (keep it when building)
- Backdrop = `assets/bg-*.jpg` (all made by `assets/tint.py` from `logos/home/cosmic-bg.jpg` and `logos/header/dash-bg.jpg` — his art, hue-shifted per box) at 50–72 % under a veil that darkens towards the bottom, so the tiles sit on near-black. Move the assets into `logos/panels/` for the build (served).
- Title row: 34 px glowing square with the icon, Orbitron title, logo 30 px with a faint gold glow, camera 📷 at full brightness, toggles/buttons at the right.
- Headline figure: 40–44 px, metallic gold (`#FFF1C4 → #FFD66B → #F0A83A → #D2811E`).
- Tiles: 12 px radius, box-tinted glass gradient, 1 px border in the box colour at .22–.24, values in `#FFD98A` (gold) 24 px.
- Panel frame: 18 px radius, 1.5 px border in the box colour at .55, outer glow `0 0 28px -8px`, the old top hairline kept.
- LP Pairs: today's row layout, restyled to match (rank numbers / compact rows / mini-curves all declined; Buy/Sell column out).

## Build notes
The UFO page's Burn / Value Generated (six different tiles) / Allocation (no staking slices) follow the same designs with the
green accent where PTGC uses gold. Everything renders from the same variables and setters as today (gotcha 36 spirit) and only
under `hdrV2`.
