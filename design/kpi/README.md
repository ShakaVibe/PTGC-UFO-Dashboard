# KPI Report tab — facelift, 2026-10-05

Shaka's mock-up: `reference/shaka-kpi-mockup.png` (the whole page at 1312 px: v2 header, tab band, the UFO and PTGC
cards side by side). His two card backgrounds: `reference/shaka-kpi-backgrounds.png` (green | gold, side by side) —
cut into `kpi-bg-green.jpg` and `kpi-bg-gold.jpg` (656 × 1199 each, **provisional: cut from the side-by-side image;
he has a zip with the full-size pair — swap file-for-file when it lands**). The art is composed for the card: UFO +
planets at the top (the header), dark through the middle (the tiles), the planet's horizon glowing at the bottom
(behind the burn block).

The target is `KPIContent` / `renderKPICard` in index.html (the KPI Report tab; also the Socials rows "KPI Report"
and "Combined KPI Report", and the 📷 `TwitterCard` share image). Same numbers, same honest-null rules (a19, u5/u6):
this is a skin.

## Mock v1 — `mock-kpi-v1.html` → `renders/kpi-v1.jpg` (1312, the pair) + `renders/kpi-v1-phone.jpg` (390)
His layout, with the site's art where he asked ("use the new emojis we have added recently where you can — the sea
creatures, the burn bar, etc"):

- **Card** 600 px, 24 px radius, a 2 px token-colour frame with a soft glow; his background as the card's plate
  (`cover`, top-aligned) under a light veil (darker through the tile band, lighter at the top and bottom so the planets
  and the horizon show). A soft dark pool behind the title block so the name / KPI REPORT / address read over the art.
- **Header**: the dashboard's lit coin (`h2-coin`: halo + `coin-corona(-green).webp` + flares, u = 0.6) with the token
  logo; name in Orbitron 44 in the token colour; KPI REPORT (Orbitron 16, letter-spaced, white 78 %); the full contract
  address; date top-right and a solid 24H pill in the token colour.
- **Price box**: his coin-stack icon = `dao-coins.webp` (the Treasury's gold coins — real alpha; the Leagues' `lg-ic-coins`
  is still on a checkerboard); PRICE as a dark chip; the price 48 px in the token colour with the sub-digit; a red / green
  change box with its own sparkline (red when down — his mock; the only place a sparkline is not in the token colour);
  a PLS RATIO box.
- **Six tiles** (2 × 3): icon · label chip · change badge or ⓘ, then the figure (29 px white) with a sparkline in the
  token colour (drawn like the KPI tiles' `H2Spark`: crisp line, soft bloom, faint fill). Icons from the site:
  MARKET CAP = `lp-bars-gold` / `lp-bars-green` (the LP header's bars, per token); LIQUIDITY = `vg-droplet`;
  LIQ/MC RATIO = `pbu-pie` (the blue/gold pie); VOLUME = `nh-ic-net` (the gold rising chart); HOLDERS = `nh-ic-new`
  (the green people, as on the Holders tile); VALUE GEN = `vg-moneybag` (his mock has a lightning bolt — we have no
  bolt; the money bag or `vg-diamond` are the candidates). Badges as in his mock: Market Cap and Volume carry the 24 h
  change, Holders the net count, Value Gen its change (UFO) or the 7D tag (PTGC), Liquidity and Liq/MC an ⓘ.
- **Burn block**: orange frame on a dark pool; `vg-flame.webp` leads TOTAL BURNED and 7D BURN; the lifetime figure 33 px
  amber with the token after it, USD + % under it; the creature row in **our sea-creature art** (`sea-*.webp`, 38 px,
  × counts 19 px — the v2 Burn panel's row); then **the v2 fire bar** (`.p2-bar`, verbatim CSS: flames texture, lit tip,
  bright end) with the % and the whale at its end (the panel's "progress to Whale"). Right column: 7D BURN amount /
  token / USD in green, the window's creature below (`sea-dolphin`).
- **Sparkline data** in the mock is a seeded walk — placeholders for the shape; the build reads the real series
  (`useH2Series` for the tiles that have one; the 7-day holder / volume history for the rest).
- **Phone (390)**: the cards stack; the tiles stay 2-up with the badge pinned bottom-right and the sparkline under the
  figure; the PLS RATIO box drops under the price; the burn block's 7D column becomes a row under the bar.

Open for Shaka on v1: the Value Gen icon (money bag vs diamond vs a new bolt from him), the Holders icon on PTGC
(green people on a gold card — the Holders tile greys it; here it stays green), whether the price sparkline should
follow the token colour instead of red / green, and the full-size backgrounds.
