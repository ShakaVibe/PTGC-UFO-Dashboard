# Affiliate Program page — the new look (2026-10-22)

Shaka: "we have done a TON of nice visual updates to the site.. this page is still the old and ugly look. Can you mock up a new
look?" The page = `AffiliatesPage` in index.html (its own header with ← Back, the gold / green stat bars, Recent Activity, the
Referrers Registry fold, the Commission Log; Leaderboard + Payment Receipts windows behind two buttons). His screenshot of the
live page is the reference for every figure in the mock (`mock-data.js` — REAL numbers read 2026-10-22; the four Registry rows
in that file are sample numbers, the Registry is folded in both looks).

## Mock v1 — `mock-affiliate-v1.html` (+ `mock-data.js`) → `renders/affil-v1-{a,b}-{1380,390}.png`, drawn by `render.mjs`
Both looks keep EVERYTHING today's page shows, in the same order — nothing moved or removed; only the dress changes.

Shared by A and B:
- ← Back to PTGC as a pill top-left; the freshness stamp ("Updated 11h ago · next in 13h") as a pill top-right with a live dot.
- The PTGC coin on its gold halo (LgCoin's look) over the title; one sub-line ("Earn PTGC on every buy you refer · 2% commission,
  paid monthly in PTGC").
- The old header's month box + the Rate / Min Threshold / 5% Fee settings → a row of chips (MONTH · OCTOBER 2026 ▼ lit gold, RATE 2%,
  MIN THRESHOLD $250 green, 5% FEE Covered green).
- Leaderboard / Payment Receipts → his Calculators icon buttons (`cp-btn`): gold with the 1st-place beam-UFO medal, purple with the
  money art; each with a one-line hint under the label.
- The ALL-TIME (gold) and month (green) bars → two framed bands of Top-100-style tiles (label in Orbitron caps, big number),
  PTGC REFERRED lit as the lead tile, $ in green, the sea creatures drawn with the sea art (`SeaIcon`), not emoji; the band's
  left plate = icon + ALL-TIME / OCTOBER '26 ▼ + a sub-line. 7 tiles across on desktop; 2-up on the phone (the lead spans both).
- Recent Activity → a purple-framed card (its colour today): date chip, name + "referred a buy", amount gold, $ green, tx link.
- Referrers Registry → a fold bar like Portfolio's (icon tile, title, "74 referrers · 14 active this month", a 74 REFERRERS chip,
  the search box, gold SHOW).
- Commission Log → a framed card: icon tile + title + the month pill; the table with Orbitron column heads, a dim row number,
  name gold, wallet mono + copy, buys a blue pill, PTGC bought + sea creature ×n, $ white, commission gold, status a small
  Orbitron badge (UNPAID amber / PAID green / BELOW MIN red, the row dimmed).
- Phone (390): chips wrap, the two buttons side by side, tiles 2-up, the activity row = chip · name · amount · $, the log keeps
  User · PTGC bought · Commission with the status badge under the name (wallet / buys / $ fold away as today).

**Look A — "Grays Affiliates", the Calculators treatment.** His Calculators art as the plate under the 62 % veil (the same art and
veil as calculators.html), the metallic two-tone title (gold "Grays" + silver "Affiliates", the Calculators / Charts title),
the content down the art's black centre.

**Look B — "Hall of Fame".** The rank window's gold mountain sky (`rk-plate-nf.webp`, the Top 100 window's plate) as a 330 px
hero band, the title in that window's Orbitron (white with AFFILIATE in gold), the page black under it. Plus **the month's podium**:
the top three referrers by PTGC bought on his 1st / 2nd / 3rd beam-UFO medals, tinted like the Top 100 podium cards (his UFO-beam
sky in grey under a medal-coloured layer, the figures on a dark pad); Recent Activity beside the Registry in two columns so the
Commission Log sits higher. The podium can go into Look A too.

ASK: A or B (or A + the podium); anything to change before the build. Build plan once picked: a `tools/affiliate-v2.py` that
splices an `af-*` CSS block + the new header / bands / card markup into `AffiliatesPage` (idempotent, "0 edit(s)" when applied),
same recipe as calc-v2.py; the Leaderboard and Payment Receipts windows get the same dress in a second round (mock first).

## Mock v2 — `mock-affiliate-v2.html` → `renders/affil-v2-1380.png`, `affil-v2-390.png` (`render-v2.mjs`)
Shaka: "I like affil-v1-b-1380... but I would rather see the recent activity box span the full width, and the Referrers registry
to go under it" + "also use the logo that has the glowing light around it like we use on the dashboard". → Look B re-laid:
Recent Activity full width, the Registry fold bar under it (the Look A bar), then the Commission Log; the coin is now the
DASHBOARD HEADER's coin — h2.css `.h2-coin` reproduced at --u .605 (118 px coin, the fire corona `logos/header/coin-corona.webp`
at 520u mix-blend screen, the halo, the three flares, the ring shadow; phone --u .46, no flares). The hero is 340 px.

## Mock v3 — `mock-affiliate-v3.html` → `renders/affil-v3{a,b}-{1380,390}.png` (`render-v3.mjs`)
His AI mock-up (`reference/shaka-ai-mock.png`: left-aligned header, a starry UFO sky behind the whole page, plain-column bands,
avatars, the log nested in the Registry) → "actually keep ours as is except add some of that background artwork". v2 unchanged +
his Calculators space art under the whole page (72 % veil, fading in under the hero; cards / bands a touch more solid).
3a = the hero as in v2 (gold mountain plate) · 3b = the hero swapped to the Holders window's beam-UFO sky (`nh-sky.webp`).

## BUILT — `tools/affiliate-v2.py` (2026-10-22, "make it live" on v3; 3a = the hero as in v2)
Run from the repo root, twice (the second run prints "0 edit(s)"). The CSS is `tools/affiliate/af.css` (spliced between
`/* AFFIL2:CSS:BEGIN/END */` before the TOP 100 CSS); `AfSea` + `AfPodium` between `/* AFFIL2:JSX:BEGIN/END */` before
`AffiliatesPage`; the page's render blocks (hero, bands, recent, registry head, log head, footer) sit between
`{/* AFFIL2:X */} … {/* /AFFIL2:X */}` markers so the script can be edited and re-run. The lists' own cells are the page's
(the Registry tables, the log's phone cards + expanded transaction rows, the referrer card, the Leaderboard and Payment
Receipts windows — those two windows are the next round, mock first). Differences from the mock that the build settled:
the month chip is a label (the month SELECT stays on the green band, as today); the header is no longer sticky; the log's
rank number is a CSS counter (no text — `probes/affil-a54.js` reads the cell as the name); `probes/affil-registry.js` now
matches the Orbitron-uppercased heads case-insensitively; commissions stay purple in the log (the page's own colour); the
User column widened to 20 % (the 16 px names). Harness: `AFFIL_DATA=real` at 1400 / 1024 / 390 — no overflow, no errors; the
a54 / card / registry probes read the same figures as before. index.html sha256 8fafd7c2.
