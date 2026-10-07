# Volume window — the Volume tile's ⓘ (2026-10-07)

Shaka (his screenshot of the old "Volume Analytics" modal): "It is still a dated look, and we need to upgrade to get in line with
a lot of the cosmetic changes we have made. Mock it up for me to see first."

The old window: `showVolumeModal` in index.html (~line 14295) — a `max-w-lg` card, four 2×2 volume boxes, a Daily Averages box,
a Today vs Averages list of three arrows. Numbers: `data.vol` (DexScreener 24h) + `volumeByPeriod` (7D / 30D / 90D from
`coingecko-data.json`, gated — gotcha a19: null → "—").

## Mock v1 — `mock-volume-v1.html` → `renders/volume-v1-ptgc.png`, `volume-v1-ufo.png` (7D), `volume-v1-phone.png` (90D, 390)
`?token=UFO`, `?period=7D|30D|90D`; the pills work in the mock. Real numbers: the four figures are the live window's (PTGC) and the
dashboard's (UFO); the chart days and the pools are `data/swap-volume.json` as of 2026-10-07 13:15 UTC.

Decisions, top to bottom:
- **The Humans vs Bots shell** (same window it shares the tile with): `max-w-4xl`, the token-colour edge and halo, the hairline.
- **Plate = the dashboard's own banner** (`logos/header/dash-bg.jpg`) — the gold half for PTGC, the green half for UFO (one image,
  two crops; no new art needed, and the window reads as the tile's). His own art welcome instead (ask).
- The lit coin (`LgCoin`), the title "PTGC **Volume**" (token word in the token colour, Orbitron), one-line subtitle, then the glass
  pills **7D / 30D / 90D** (they drive the chart and the pool table only — the four figures always show) and "as of".
- **Four period tiles** (the Leagues window's framed tiles in the token colour): 24H lit (it is the live number, the tile's), 7D / 30D /
  90D quieter with their **per-day average** on the sub-line — the old Daily Averages box folded into the tiles. The 24H tile's
  sub-line is the dashboard tile's "vs 7d avg" change. The bars icon = `lp-bars-gold/green.webp`.
- **Today vs averages as bars**, not just arrows: each row = the window's daily average under the label, a bar of today's volume
  with a white "avg" tick at the midpoint (the bar reaches the tick when today equals the average; the scale is 0–2× so a big day
  overshoots visibly), the % in red / green at the right.
- **Daily volume chart** — NEW: real bars per day over the chosen window (7 / 30 / 90) with a dashed line at the window's average and
  the peak labelled. Data = `swap-volume.json` `hours` (humans + bots per hour, summed per day — on-chain, 90 d kept). On his wave
  plate for PTGC (`logos/hvb/wave.jpg`), the Value Generated plate for UFO (`bg-vg.jpg`), under the HvB chart veil.
- **By pool** — NEW: the top 6 pools of the window (rank ring, trades, volume, share + mini-bar) and "and N more pools — show all"
  (a fold). Data = `swap-volume.json` `periods[win].pools` (DexScreener's pool names).
- The honesty line at the foot: the four figures are DexScreener's (the tile's numbers); the chart + pools are on-chain and will not
  match to the dollar.
- Phone (≤ 640): full-screen like HvB, tiles 2×2, the Trades column leaves the pool table, the chart 150 px.

Not in v1 (ask if wanted): a USD / TOK toggle; a 📷 share card; a 24H line in the pills (hourly bars — the file has them).

## Built (same day) — Shaka: "that looks great, lets make the logo Bigger. and then make it live."
`tools/volume-window.py` on index.html (idempotent; md5 after `10d5c9119d0b7f01c3c6d7d046364ab9`): the `vw-*` CSS after the `vs-*` block,
`VW_PERIODS` / `VW_ICON` / `vwDays` / `VwChart` / `VolumeModal` at module scope just above `VolumeSplitModal`, and the Dashboard's 84-line
inline "Volume Details Modal" replaced by `<VolumeModal token data volumeByPeriod onClose/>` (the ⓘ on both the v2 tile and the classic
tile still calls `setShowVolumeModal`). **The coin is `--u:.72px` (140 px; the HvB window's is .5 / 97 px), .56 on phones.**
The chart measures its own width (`ResizeObserver`) — no stretched type on phones; today's partial UTC day is the last bar at 45 %
("Today so far" in the key) and is left out of the window average; the pool share is of the file's own period total (the shares sum to
100 %); "show all" rolls the table out. Honest states: the four figures and every line under them print "—" when `data.vol` /
`volumeByPeriod` are null (DS_DOWN); the chart card shows "Couldn't load the hourly file — Retry" when `fetchSwapVolume` gives null
(file moved away), the pool table stays hidden. Harness: `probes/vw-state.js`; renders `renders/build-v1-ptgc.png` (1440, 30D),
`build-v1-ufo.png` (UFO, 7D, all 22 pools rolled out), `build-v1-phone.png` (390, 90D), `build-v1-fail.png` (DS_DOWN + no file).
