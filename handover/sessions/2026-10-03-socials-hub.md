# 2026-10-03 (second session, Saturday) — the Socials Hub redesign

Shaka opened with the handover and the next item on the list (the Holders Details share card), then put Holders Details on the
back burner ("maybe next session") and brought a full-page mock-up of the Socials tab plus `socials_hub_icon_pack.zip`: "it is
time to update the artwork of the socials page… let me see your mock up before you make anything live."

## The material

- **The zip was mis-cut.** Its 20 icon PNGs were rectangles taken off their marks from a bigger labelled sheet — `burn_stats.png`
  was the green saucer, `targets.png` the gold columns captioned "dao_treasury", `holders_ptgc.png` had "value_generated" printed
  across it — and its background carried a strip of that icon column down its left edge. Unusable; told him so.
- **The icons used** are therefore cut from his mock-up image itself (`ce33c932`… → 70 × 56 px, difference-keyed against the
  card tint, soft edge). Good enough to judge and to ship as a first cut; **he still owes the full-size sheet** — swap
  `logos/socials/hub/<col>-<key>.png` one for one when it arrives (same names, any size; they draw at 70 × 56). Three rows do not
  use cuts: PTGC Logos / UFO Logos are the token logos themselves (Shaka), RH Core Liquidity is the dashboard's
  `logos/panels/vg-droplet.webp` (Shaka: "the water drop that we use on the dashboard"), The Grays & The Cores is a new gold globe
  he sent (1312 × 1199 RGBA → `hub/combined-grays-cores.png`, 256 px).
- **The background**: his first file (the one in the zip, 886 × 805) had the icon strip; my first mock mirrored it left-right to
  reach page width → "ours has too many big planets". He then sent the proper wide scene (1312 × 1199) → `logos/socials/hub-sky.jpg`
  (311 KB), used ONCE, `object-fit: cover`, anchored top, so the mountain ridge sits under the title and the planet horizon along
  the foot, as in his mock-up. Phones: the hub is many screens tall, so the top of the scene is under the title and a second copy's
  planet sits at the foot (`img.ft`), dark between.

## Rounds (all on `design/socials-hub/mock-hub-v1.html`, renders in `renders/`)

1. v1 from his mock-up: metallic "Socials Hub" title (Orbitron 900, gold / silver gradients), three framed columns (gold / green /
   blue) with logo + name + "PulseChain · The Grays" and a circled chevron, his icon per row, title in the row's colour.
2. The background, once (his wide file) — `hub-v1-*.png`.
3. His five asks: a dark radial pool behind the title block; UFO Logos = the UFO token; the droplet; Grays & Cores options
   (A alien head / B roundel / C two coins); a black gap under the tab band + the sky fading in from black so it never runs up
   into the bar. Then: PTGC Logos = the PTGC token too — `hub-v2-*.png`.
4. His globe for The Grays & The Cores (drawn 60 px with a gold glow — it is detailed); darker pools behind all three column
   headers (he asked for PTGC and Combined; one rule for three).
5. **Row order** ("make sure the order of all the buttons make sense… use your judgement"): rows 1–5 = the five cards every
   column has — Logos, Burn Stats, Value Generated, KPI Report, Holders — level across the page; rows 6–7 = the two the token
   columns share (Token Allocation, Targets), level between PTGC and UFO, while Combined fills them with RH Core Liquidity and
   Leagues; the rest is each column's own at the foot (PTGC: DAO Treasury, DAO Buys, Affiliates Report; UFO: PTGC Burned by
   UFO; Combined: The Grays & The Cores). 10 / 8 / 8 as before — `hub-v3-*.png`. He pushed the mock-up rounds as `9d3f434f0`.
6. "the old one is still displaying" — he was looking at the live site; nothing had been built yet. **Approved → built.**

## Built — `tools/socials-hub.py` (idempotent, exact-string edits; run on the cloud clone AND the Mac, sha256 equal:
`c76bdf7b…f1ade`)

Three edits to `index.html`: (1) the `sh-*` CSS block appended to the end of the p2 block (just before that `</style>`);
(2) `ShRow` / `ShCol` + `shIcon` at module scope above `DashboardSkeleton` (pure presentation — u4); (3) the Socials tab's JSX,
start marker `{/* Social Tab Content */}` to the legacy KPI modal comment. **Every row's onClick is the previous hub's handler,
lifted verbatim by the script** (it finds the old column's button by its bold label and copies what sat in `onClick={…}`), so what a
row DOES is unchanged — same modals, same `setSocialReturn`, same loaders (a18). Only the frame, the art and the order are new.
The "Back to Dashboard" button is `gotoTab('dashboard')` as before. The section is full-bleed (the sky needs the width); the
columns sit in a 1200 px `.sh-in`. Grid → one column under 900 px (phones + small tablets), max 520 px wide.

## Harness (cloud clone; `CHROME=/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell` — the plain
chromium-1194 binary no longer launches under playwright-core 1.47's old headless mode)

```
node run.js "#/ptgc" 1440 1000 out/sh "wait=4000;click=button:has-text('Socials'):visible;wait=1500;shot=hub;evalfile=probes/sh-rows.js;click=.sh-row:has-text('Burn Stats') >> nth=0;wait=2500;shot=burn"
node run.js "#/ufo"  1440 1000 out/shu "wait=4000;click=button:has-text('Socials'):visible;wait=1500;scroll=900;wait=300;shot=bottom;evalfile=probes/overflow.js"
node run.js "#/ptgc" 390 844 out/shm "wait=4000;scrollnav=1;click=button:has-text('Socials'):visible;wait=1500;shot=top;scroll=700;wait=300;shot=mid;evalfile=probes/overflow.js;evalfile=probes/sh-rows.js"
```

`probes/sh-rows.js` (new) prints each column's row titles in order, any `.sh img` that failed to load, the sky's natural size and
the hub's width vs the document's. Results: the three orders exactly as designed; broken imgs none; sky 1312 × 1199; scrollW = vw
at 1440 and 390 (`overflow.js`); the Burn Stats row opens the Burn share card (same modal as before); the UFO page's hub at the
foot shows the planet under the Back button. Compile clean (Babel's size note only); the three 404s in the console are the
harness's usual (favicon / manifest).

## End of session (Shaka: "lets wrap it up. good work")

Pushed by Shaka: the mock-up rounds (`9d3f434f0`) and the build (`6786b4af0`). Tree clean. Not seen live by anyone yet —
that is the first thing next session.

## Not done / owed

- **Shaka's live look** on the Mac (ptgc-ufo.com → Socials), then iPhone + iPad (the one-column hub).
- **The full-size icon sheet** — the 18 cut icons are 70 × 56 px and will look soft on a Retina Mac; swap them file-for-file.
- A `_to_delete/hub-sky-top.jpg` in the repo root (my mirrored sky, before his wide file arrived) — the bridge cannot delete; he
  bins it or it ships in `_site` (harmless, 90 KB).
- The chevron circle in each column header is decorative (aria-hidden); the mock-up had it, nothing is behind it.
- Holders Details share card (-8 in HANDOVER) stays where it was: next session, his call.
