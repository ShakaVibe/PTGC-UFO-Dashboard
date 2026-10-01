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
| LP Pairs | `mock-lp-v1.html` | **v1** (2026-10-01, from `reference/shaka-lp-pairs-mockup.png`) | Shaka's mock-up, one round: the section header bigger (50 px logo in a ring, LP PAIRS 22 px, Volume / Liquidity in gold 24 px, glass All / RH Cores + Sort pills), then a panel frame (gold border, top hairline, `bg-burn` at 18 %, the cosmic-Home ground strip as the ember band along the bottom — green side for UFO) holding ONE table: gold rank circles, glowing logos, pair name in the token colour with "PulseX V1/V2" under it, Volume 24h, a 7-day volume curve (gold / green when the second half of the week out-volumes the first, red otherwise), Liquidity, 24h ▲/▼, buys / sells, Vol/Liq, ⓘ (details drawer) · DexScreener · DEXTools. Declined earlier and now IN: rank numbers, one-line rows, per-pair curves. Still OUT: the Buy/Sell column, the eye icon. Phones keep the stacked cards. `assets/ptgc-pairs-2026-09-30.json` is the real pair list the mock renders. Live round 2: type larger throughout; round 3: the action squares were "too loud" — `mock-lp-actions-v1.html` (four options), **C picked** (28 px dark glass squares, one soft tint per glyph) with a **line-graph glyph for DEXTools** ("a wrench means settings"); the DexScreener bars stay. |
| PTGC Burned by UFO (UFO page) | `mock-ufoburn-v1.html` | **v1** | No mock-up from Shaka — derived from the Burn panel in sky blue on the treasury backdrop: three glass tiles (Burned / USD Value / % of PTGC in their colours), the flame bar in **UFO green** (`assets/flames-green.png`; Shaka: green, not blue), creatures, period boxes. |
| Panel toggles (USD / TOK, 24H–90D) | `mock-toggles-v1.html` | **open** (2026-10-01) | Shaka: today's gold-filled buttons "look so old school". Ten options A–J on the Value Generated backdrop, gold and UFO-green accents, at the real 36 px size: A lit glass · B underline · C segmented (frosted thumb) · D outline · E dot · F metallic pill (today's idea done properly) · G metallic text · H chips · I backlit key · J accent bar. Render `renders/toggles-v1.png`. The build is the `.p2 [role="group"]` block in index.html, markup unchanged. |

## Shared language (keep it when building)
- Backdrop = `assets/bg-*.jpg` (all made by `assets/tint.py` from `logos/home/cosmic-bg.jpg` and `logos/header/dash-bg.jpg` — his art, hue-shifted per box) at 50–72 % under a veil that darkens towards the bottom, so the tiles sit on near-black. Move the assets into `logos/panels/` for the build (served).
- Title row: 34 px glowing square with the icon, Orbitron title, logo 30 px with a faint gold glow, camera 📷 at full brightness, toggles/buttons at the right.
- Headline figure: 40–44 px, metallic gold (`#FFF1C4 → #FFD66B → #F0A83A → #D2811E`).
- Tiles: 12 px radius, box-tinted glass gradient, 1 px border in the box colour at .22–.24, values in `#FFD98A` (gold) 24 px.
- Panel frame: 18 px radius, 1.5 px border in the box colour at .55, outer glow `0 0 28px -8px`, the old top hairline kept.
- LP Pairs: built 2026-10-01 as the table above (Shaka changed his mind on rank numbers / one-line rows / curves once he drew it himself; Buy/Sell column stays out).

## Build notes
The UFO page's Burn / Value Generated (six different tiles) / Allocation (no staking slices) follow the same designs with the
green accent where PTGC uses gold. Everything renders from the same variables and setters as today (gotcha 36 spirit) and only
under `hdrV2`.
