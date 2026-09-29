# Dashboard header redesign — PTGC (work in progress, NOT live)

Started 2026-09-29 with Shaka. Goal: the top of the PTGC dashboard (hero banner + tab row + KPI tiles) rebuilt to match
Shaka's reference mock-up (`reference/shaka-reference-mockup.png`). **Approved so far as a mock-up only — nothing in
`index.html` has changed.** This folder is outside the deployed site (deploy.yml copies only root `*.html`/`*.png`,
`logos/`, `data/*.json`), so it is safe in the repo.

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

## Still open (next session)
1. Shaka may still tweak — ask what else differs from the reference before building.
2. **Sparklines**: only Market Cap (price series) and Holders are real data. Volume, Liquidity, Liq/MCap, Tokens in LP,
   Txns are placeholders. `data/metrics-history.json` has daily/hourly volume/liquidity/tokensInLP but its hourly series
   stopped at 2026-09-02 — fix that pipeline first, or show sparklines only where data exists. Ask Shaka.
3. Mock-ups still owed before building: the **UFO** version (green) and **phone / tablet** layouts.
4. Then build into `index.html` (the Dashboard header block; the Buy/Sell button opens `SwapModal`, Switch calls
   `onSwitch`), assets into `logos/home/` (served), honest-null "—" for anything not loaded, harness check at 1440 /
   1024 / 390, then Shaka pushes.
