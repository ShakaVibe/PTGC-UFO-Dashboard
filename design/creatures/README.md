# League History window — the Token Allocation creature strip, over time

Shaka (2026-10-24): "click on this full bar of sea creatures, and then it opens a big window.. see the Sea creatures, select time
periods, and see the up down percentage over time.. like how many sharks did we have 6 months ago vs now.. cool line charts of each
sea creature". Discussed first; his picks: **all 8 leagues separately**, **cards + one big chart**, and every extra:
**joined / left per league**, **starting / circulating supply toggle**, **a share card**, **PTGC + UFO switch**.

## Data (real, not estimated)
`data/rank-history/<TOKEN>.json` (the rank window's archive) holds every PEOPLE holder's balance for every UTC day since launch —
the same population as the Token Allocation strip since Audit IV e13 (contracts, pools, burn, token contracts, DAO / UFO OA left
out). Walking it forward gives each day's count per league. Checked against the live strip: Oct 23 PTGC 0 / 12 / 96 / 696 / 16,276
(strip now 0 / 12 / 96 / 693 / 16,320), UFO 0 / 16 / 99 / 499 (strip 0 / 16 / 98 / 500) — the strip is "now", the archive is the
close of Oct 23. Circulating = starting − burned that day (PTGC: the burn archive; UFO: the v2 burn rows, incl. the 93 B migration
burn of 2026-07-09). Joined / left = a wallet's league on the period's first day vs the last day; joined − left = the change.
`build-mock-data.py` (18 s) → `mock-data.js` (118 KB). For the build: a pipeline output `data/league-history.json` written by the
rank-history step (it already walks every day), ~1,110 days × 8 × 2 bases + the six periods' joined / left.

## Mock v1 — `mock-creatures-v1.html` (`?tok=PTGC|UFO&per=7D|30D|90D|6M|1Y|ALL&sel=0-7&basis=start|circ&view=win|card|entry`)
- Header: the Leagues window's Atlantis art for the token, coin, "PTGC LEAGUE HISTORY", PTGC / UFO, the six periods, Starting /
  Circulating; 📷 SHARE and × top right.
- Eight cards (4 × 2; 2 × 4 on a phone): sea art, league + its line (≥ 0.1 % of supply), the count now, ▲ / ▼ change and % over
  the period, "+21 joined · −28 left", a sparkline. The selected card lights up.
- The big chart for the selected league: the line + area, its high and low marked, today's dot; JOINED / LEFT / ALL HOLDERS.
- Share card (Wide 1200 × 675): eight cells "103 → 96 ▼ 7 (6.8 %)" with sparklines, period + dates, basis, PTGC-UFO.COM.
- The entry: the strip in the Token Allocation panel becomes a button with a small "HISTORY ›" tag.
Renders in `renders/`. Open questions for him: the title ("League History"?), the entry tag, Tall card shape too, chart hover.
