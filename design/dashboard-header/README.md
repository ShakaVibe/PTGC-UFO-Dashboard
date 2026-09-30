# Dashboard header redesign — PTGC + UFO

Started 2026-09-29 with Shaka. Goal: the top of the dashboard (hero banner + tab row + KPI tiles) rebuilt to match
Shaka's reference mock-up (`reference/shaka-reference-mockup.png`). **2026-09-30: BUILT into `index.html`**
(`DashHeaderV2` / `KpiTilesV2`, CSS block `h2-*`, assets in `logos/header/`) behind `HEADER_DESIGN` + the hidden
preview switch — see `handover/sessions/2026-09-30.md` and gotcha 36. The mock-ups below are the record of what was
agreed. This folder is outside the deployed site (deploy.yml copies only root `*.html`/`*.png`, `logos/`,
`data/*.json`), so it is safe in the repo.

## Open it
Open `mockup-ptgc-v11.html` in a browser (1:1 at 2166×636 — the reference's size). It is self-contained: every image and
font it uses is in `assets/`. `renders/v11-final.png` is the same thing as a picture.

## What's in here
| Path | What |
|---|---|
| `mockup-ptgc-v11.html` | The current design, standalone (relative paths). |
| `renders/v11-final.png` | Screenshot of it. `v1-first-try.png` = where we started. `coin-compare.png`, `price-compare.png` = reference (left) vs ours (right). |
| `reference/` | Shaka's inputs: the reference mock-up, its left crop, the banner with the alien baked in, the raw background band (white border, cropped into `assets/dash-bg.png` at x 2–2170, y 185–535), the raw transparent alien head. |
| `assets/dash-bg.png` | Background band, 2168×350 (Shaka's art, no alien). |
| `assets/alien-head.png` | Alien head, transparent, 1330×1182 (Shaka's art). |
| `assets/coin-corona.png` | Generated fire light behind the coin (`source/make-corona.py`). |
| `assets/*.png` (coins), `assets/fonts/` | PTGC / UFO coins; Orbitron 700/900, Rajdhani 500/600/700. |
| `source/gen11.py` | The generator that wrote the mock-up (imports `gen10.py` → `gen2.py` for CSS, sparkline + icons). Paths inside are the cloud workspace's (`/home/claude/ptgc/...`) — to re-run, point `R` at the repo and the fonts at `assets/fonts/`. It reads `data/charts-data.json` + `data/holder-history.json` for the sparklines. |

## Decisions Shaka made (keep them)
- **No global top bar**: no "THE GRAYS" nav line, no search box. The page starts with the banner (← back arrow top-left, as today).
- **Buttons are ours, not the reference's**: solid shiny gold **BUY / SELL** (PTGC coin, dark text, hairline between) and a
  dark-green-glass **SWITCH** with a bright green edge + glow and the UFO coin. (The site's current translucent `.buy-btn`
  was tried in v7/v8 and was too hard to see on the art — Shaka: "your buttons were better".)
- **Art** = Shaka's background band full width **plus** his separate alien head, placed like the reference
  (head scale 0.385 → 512 px wide, left 1395, top −135; fades out at the shoulders; soft green edge light right, gold left;
  brightness .78). The band's **right part is a second copy, enlarged** (left −262, top −26, 2428×392) and blended in
  from x≈1300–1420, so the centre planet's **bright green rim shows just left of the alien** as in the reference; the left
  part is unscaled so the gold planet rim sits above the price.
- **Dark shading behind all text** (radial black patches behind name, price — including above it — the three stats,
  extra under X'S TO A PENNY next to the alien, and behind the buttons). Text must read clearly.
- **Coin**: no second ring. Just the logo with **fire light behind it** (the generated corona, tight and cloudy, stronger
  left + upper right, embers) and a small star flare at top-right. Shaka's words: "just a cool light behind it".
- **Gold text**: PTGC name uses `.t-ref` (sampled from the reference: #FEF7C0 → #FFD066 → #A87226); **price** uses
  `.t-price` (cream → warm gold: #FFF6D6 → #F6C866 → #D69C40); stats/day use `.t-ref2`.
- **Price block**: price 66 px at y 118; change 40 px bright green #12E28A with a **gradient green triangle** (not ▲ text),
  close under the price; "24h change" 21 px, 70 % white. The price keeps the site's subscript zeros ($0.0₄4080).
- Layout coordinates were measured on the reference at 2166 px wide — see `banner()` in `gen11.py` (coin 85,88 @195 px;
  name 308,98 @80 px; price column 645–977; stats at 1017 / 1207 / 1400; buttons 1840, 250×72 at y 106 and 198;
  banner 336 px tall; tab row 60 px; tiles top 424, 186 px tall).

## UFO version (2026-09-29, first look)
`mockup-ufo-v1.html` (same art) and `mockup-ufo-v1b-all-green.html` (background hue-shifted green, alien kept gold) —
renders in `renders/ufo-*.png`. Same layout and rules as PTGC, in UFO green: green coin corona
(`assets/coin-corona-green.png`, a channel-swap of the gold one), green name/price/stat golds (`.t-gref`, `.t-gprice`,
`.t-gref2`), **green solid BUY/SELL with the UFO coin**, **gold-edged SWITCH with the PTGC coin**, green tab underline,
tiles and sparklines (UFO price + holder series). Live UFO numbers from 2026-09-29. Generators `source/gen12.py`,
`gen12b.py` (they patch gen11's text). **Shaka picked A: the background art stays the same on UFO — no hue shift** (B's teal was rejected; `mockup-ufo-v1b-all-green.html` kept only as a record).

## How it goes live (Shaka, 2026-09-29): a hidden preview switch
Build the new header into `index.html` behind a switch; everyone else keeps today's header. Shaka turns it on for his own
devices with a secret link **plus a password**: `ptgc-ufo.com/?<secret word>` opens a small password box; the right
password turns the new header on for that device (remembered in localStorage); a matching "off" link turns it back off.
Nothing on the page hints the switch exists (no button, no text, no console log).
- Store only a **SHA-256 hash** of the password in the code, never the password itself; Shaka chooses it and never types
  it into a file, commit or chat that lands in the repo (gotcha 33 spirit — the repo is public).
- Be honest with Shaka: GitHub Pages is static and the repo is public, so this hides it from visitors, not from someone
  reading the code on GitHub. Real secrecy would need a server-side gate (e.g. the ptgcapi worker serving the assets).
- "Flip the switch" = make the new header the default (one line) + push. Roll back the same way.

## Built 2026-09-30 — what differs from the mock-ups
- Sparklines are real 7-day data on all seven tiles (Shaka's pick): Market Cap from GeckoTerminal hourly candles,
  Volume + Liquidity from `data/lv-snapshots.json`, Liq/MCap derived, Holders / Tokens in LP / Txns from the history
  files. A missing series is a dashed flat line, not a placeholder shape.
- Sizes scale with the window: the mock-up's pixels × (width / 2166), 1:1 at 2166 px, .665 at 1440, floor .47 at
  1024; under 1024 px the phone layout (× width/390, cap 1.3 on tablets).
- All tabs white (as the mock-up) — the classic header's Portfolio gradient / Affiliates purple are not carried over.
- The tab row is sticky and grows a logo · token · price line once the banner scrolls away.

## Still open
1. Shaka's live look with the switch on (Mac, iPhone, iPad) and his tweaks.
2. Flip: `HEADER_DESIGN='v2'`.
