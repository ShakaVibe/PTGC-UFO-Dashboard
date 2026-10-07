# The Grays Dashboard — Handover

Living status file for work on this repo. One entry per working session lives in
`handover/sessions/`. This file is the summary: what's true now, what's done, what's next.
Update it at the end of every session.

- Live site: https://ptgc-ufo.com (GitHub Pages from `main`, `deploy.yml` — since 2026-09-17 it
  publishes an allow-listed `_site/`, not the checkout: `handover/`, `tools/`, `scripts/` and the
  burn archive are on GitHub but not on the site, a38)
- Roadmap + tick-off backlog (Claude artifact, shared state): "Grays Dashboard Roadmap"
  in Shaka's Claude artifact gallery — 126 items: 59 from the Sep 8 review across five phases
  (u10 dropped 2026-09-09, g7 + g8 added and live) plus **67 from Audit II (2026-09-16, ids
  `a1`–`a67`, group "AUDIT II")**. Full evidence for the a-items: `sessions/2026-09-16-audit.md`.
- **Volume window (2026-10-07):** the Volume tile's ⓘ in the Humans vs Bots look — `VolumeModal` (`.vw-*`), build `tools/volume-window.py`,
  mock-ups + every decision `design/volume-analytics/README.md`; its chart + pool table read `data/swap-volume.json` like HvB.
- **RH Cores window (2026-10-07):** the Liquidity tile's RH button in the same look — `RhCoresModal` (`.rc-*`, reuses `vw-tile` / `vw-card`),
  build `tools/rh-cores.py` (run AFTER volume-window.py), decisions `design/rh-cores/README.md`.
- **Audit III (2026-10-07):** `sessions/2026-10-07-audit.md` — 65 merged items (c1–c65) with evidence; top of that file = the list.
  On the roadmap artifact as the "AUDIT III" phase. **The P1 batch (c1–c8 + c11 + c25) is built by `tools/audit3-p1.py`** (idempotent,
  on the repo root; "0 edit(s)" = already applied) — c1 `data-presets="react"` = the compile 15 s → 3 s.
- **Charts page (2026-10-05 / 10-06):** the Calculators treatment (same plate, "Grays Charts") — `tools/charts-v2.py`, `cp-*` CSS in charts.html; then
  `charts-gt.py` (GeckoTerminal back-off), `charts-v3.py` (no sub-tab box, the Share badge at the right, UFO-green titles) and **`charts-fast.py` +
  `scripts/build-charts-intraday.js` → `data/charts-intraday.json` (hourly pipeline step `charts-intraday`): 24H / 7D / 14D paint from the prebuilt
  file at once, live GeckoTerminal only tops up; a new load supersedes the one in flight.** Every page's metallic "Grays …" / "Socials Hub" title turns
  UFO green via `html[data-tok]` (stamped by the headers).
- **Calculators page (2026-10-05):** his art as the plate + "Grays Calculators" title + his icon buttons + framed disclaimers — `tools/calc-v2.py` (`cp-*` CSS in calculators.html), assets `logos/calculators/`, decisions `design/calculators/README.md`.
- **KPI Report tab (2026-10-05):** `KpiCardV2` (`.kp-*`, container queries) — assets `logos/kpi/`, build script `tools/kpi-v2.py`, mock-up + every decision `design/kpi/README.md`. The 📷 share image (`TwitterCard`) is still the old look.
- **Leagues (2026-10-04):** the holder-tiers modal (`TierInfoModal`, `.lg-*`) and the Socials combined card (`LeaguesCombinedCard`, `.lgc`) — assets `logos/leagues/`, mock-ups + every decision `design/leagues/README.md`.
- Repo layout: `index.html` is the whole app (React 18 + Babel-standalone + Tailwind play
  CDN, compiled in the browser). `scripts/` + `.github/workflows/data-pipeline.yml` are the
  hourly data pipeline that writes `data/*.json` (ONE workflow since 2026-09-17, a29; `deploy.yml`
  is the only other workflow). `calculators.html`, `charts.html`, `portfolio.html`,
  `ledger.html` are separate pages. `data/new-holders.json` + `scripts/build-new-holders.mjs` = the Holders Details window's
  data (2026-10-02, hourly `new-holders` step). **Since 2026-10-03 the v2 header's CSS is `h2.css` (root, linked by index +
  the three sibling pages) and the sibling pages' v2 header components are `h2-header.jsx` (root, Babel `src`).** The Socials tab's
  art is `logos/socials/hub-sky.jpg` + `logos/socials/hub/*.png` (2026-10-03, `tools/socials-hub.py` = the build).

## Current state (2026-10-07, in progress)

**2026-10-07 (Wednesday). THE VOLUME WINDOW REBUILT — PUSHED by Shaka as `43fb8af46`, his live look owed. THEN THE RH CORES WINDOW
REBUILT (his screenshot of the old "LP with RH Core Coins" modal → mock v1 → "make it live.") — `tools/rh-cores.py`, `RhCoresModal`,
Richard Heart on stage as the plate, the RH liquidity with its share of all liquidity, the cores' stacked bar, six framed pair rows —
PUSHED by Shaka as `1119ec37f`. THEN the Socials got "RH Core Liquidity" rows for PTGC and UFO (`tools/rh-socials.py`) — PUSHED
`2c3d15d4c`. THEN AUDIT III: seven sweeps, c1–c65 in `sessions/2026-10-07-audit.md` (+ two harness probes) — PUSHED `822e2a78e`; the roadmap
artifact got the AUDIT III phase (Version 8). THEN THE P1 BATCH ("go for it. Lets get some items knocked off the list"): c1–c8 + c11 + c25
built by `tools/audit3-p1.py` — PUSHED by Shaka `d60b83082`. THEN BATCH 2 ("do the next thing"): c23 + c24 + c26 + c27 by
`tools/audit3-p2.py` — PUSHED `d8b1c6a2f`. THEN BATCH 3 ("done"): c9 + c31 + c28 + c29 by `tools/audit3-p3.py` (seven files, index.html
`cd12900f…`, h2 `?v=3`) — PUSHED `742b07829`. **LIVE-VERIFIED by Claude in the built-in browser (19:30 UTC):** Calculators ← →
`#/ufo`; Charts → Affiliates → Back → `#/ufo`; phone 375: scrollWidth 375, foot → KPI Report → band stuck at top (scrollY 442);
Holders tile ↑ +1 = card "▲ +1 today"; the Volume ⓘ (UTC heading, three-source foot) and the RH window ("largest pool", $829,232
= 83.9 % of UFO liquidity) look right; UFO/INC (chain-read) prints "—" across its LP row; HvB chart in Los Angeles labels "Sep 7 …
Oct 2" (UTC bins); hub rows open the RH window and Close returns to Socials; UFO day 90: the 90D burn box reads 216.64M / $8,050
(was $491K), lifetime 4.79B unchanged. All the owed live looks are closed. One thing seen: the RH window's 24H VOLUME tile is "—"
when ONE core pair is chain-read (UFO/INC today) although five rows show numbers — honest, but "$1,067 · 5 of 6 pools" would say
more (not done; a candidate). THEN BATCH 4 ("go"): the pipeline — c17 + c18 + c20 + c19 + c22 by `tools/audit3-p4.py` (index.html
`1ec3b6cc…`, pipeline-run.mjs writes `data/pipeline-status.json`, the yml edited ON the Mac by the script because the bridge refuses
`.github/`) — PUSHED `468c308a5` 19:41 UTC; the 20:07 run's check is scheduled (Claude). THEN BATCH 5a ("keep going"): c13 + c12 +
c14 by `tools/audit3-p5.py` — **the Tailwind play CDN is replaced by the committed `tw.css`** (built by `npm run css`; see the rule
in gotcha 8 / -23), the data reads revalidate instead of `?t=`, a boot shell in #root + the header-art preload — PUSHED `685bad0b4`,
LIVE-VERIFIED by Claude on every page. THEN BATCH 5b: c15 — 21 WebP files under new names (4.9 → 2.1 MB; 512 px token logos) +
`tools/audit3-p5b.py` swapping the references — NOT pushed, commit line in `sessions/2026-10-07.md`. Live looks: ALL DONE by Claude in the browser (see below). The UFO day-90 real test: the first
value-generated run after 18:39 UTC (the launch burn was 18:38:55 UTC, so the 17:13 run still printed the old d90).** Shaka's live look at
Humans vs Bots: "loks good i think"; the Telegram wording handed to him to post. His screenshot of the old "Volume Analytics" modal
("still a dated look… Mock it up for me to see first") → mock v1 (`design/volume-analytics/`) → "that looks great, lets make the logo
Bigger. and then make it live." → built by `tools/volume-window.py`: the Humans vs Bots shell with the dashboard's own banner as the
plate (gold half PTGC / green half UFO), the lit coin at 140 px, "PTGC Volume", 7D / 30D / 90D pills, four framed period tiles (24H
lit, per-day averages on the windows), Today vs averages as bars with an "avg" tick, a daily volume chart and a By pool table from
`swap-volume.json` (same `fetchSwapVolume` as HvB), the honesty line. Honest states verified (DS_DOWN → "—", file missing → Retry).
Commit line + harness detail: `sessions/2026-10-07.md`. **The TXNS 24H item is CLOSED — nothing to fix** (the tile reads 40 = the
chain's 39; yesterday's 10,761 was DexScreener's bad h24 count on one pair, passed). **NEXT: his push of batch 5b + Claude's live look at the plates / trophies / logos + the 20:07 pipeline run's check;
batch 5 (speed: c12, c13, c14, c15 — needs a real-browser look); his live look at both windows (the Volume ⓘ and the Liquidity RH on PTGC and UFO, the hub rows, phone); the UFO day-90 real test after the first pipeline run past ~14:30 UTC (the UFO 90D burn box must drop from
$491K, the 4.79B headline must not move); then the live looks owed below.**

## Before that (end of 2026-10-06)

**2026-10-06 (Tuesday), closed by Shaka ("lets wrap it up and call it a day"). PUSHED by him — the day ended as
`5b955fa93` (Charts 13:21, Actions 13:40, round 11 `02323fe3f`, go-live `ae67befe3`, share card `6073ad2a5`, audit fix `5b955fa93`);
handover pushed as `d88034fbd`; the last handover notes (self-audit, cron fix) are the only thing uncommitted — one push, line in
the session file. Closed by Shaka 2026-10-07 00:15 UTC ("great lets update the handover and call it a session"). Nothing is half-done.**

**HUMANS VS BOTS IS LIVE (pushed 2026-10-06 evening; his live look NOT yet reported).** The Volume tile carries a bot icon (the "Classic" robot, `logos/hvb/ic-bot.svg`) right of
its ⓘ, the Holders pattern; `VOL_SPLIT_LIVE=true`, the preview dot is gone. The window (`VolumeSplitModal`, `.vs-*`) is the version
of rounds 1–14: his banner (green human side on UFO via `.vs-sky-tint`, 56 % veil), the lit coin over a centred title, the two cards
with his art, the split bar + daily chart, folds By pool · Top bot contracts · How we tell, then the confidence note (`.vs-conf`).
Removed on his word: the Round-trips column, the Human routes fold, every round-trip number (the concept stays in How we tell).
**The share card** (`tools/hvb-share.py`, `.hvs-*`, `HvbShareCard` / `HvbShareModal` / `HvbShareSocial`): 1200×675, screenshot-only,
from the 📷 beside the window's period pills (opens on the window's token + period; Card PTGC / UFO / BOTH + Period toolbar) and
from Socials — a "Humans vs Bots · Who moves the volume" row with his robot (`logos/hvb/sh-bot.webp`) in all three columns, opening
on 30 days. Mock-ups + decisions: `design/volume-split/mock-share-v1.html` (v3) and `renders/share-v3-*.png`, `hvb-share-live-ptgc.png`,
`hvb-socials-rows.png`. **Tile badges**: the clickable ones (bot, Holders people, RH) are drawn in the token colour — the two icons
are CSS masks (`.h2-hd` span, `--ic`) filled with `var(--a)`, RH is a `.h2-rh` badge the icons' size; the ⓘ circles and the LP %
(`.h2-pct`) stay grey. **Classification** (builder `scripts/build-swap-volume.mjs`, SCHEMA 3, 90 d): round trips are bots whoever sent
them, named/verified routers and many-recipient senders are human (switch.win recognised that way, its router + adapters now named),
a wallet trading ≥ 50×/day through a router is a bot; verified against DexScreener pool by pool; stated confidence: numbers ~98 %,
bot side ~90 %, human side ~85 %. The Telegram announcement is drafted (session file, "Announcement") — post it after the push +
a live look.

**AUDIT + FIX (after close) — PUSHED by Shaka as `5b955fa93`, pipeline ran on it 18:42 UTC, live file 18:50 UTC confirms it.** His
24 h card said 70 % bots; the per-transaction audit (`design/volume-split/audit-ptgc-24h-2026-10-06.html`) found one $3,787 human
sale split over four pools by PulseX's smart router counted as a bot (the wallet rule counted legs, not swaps), and that every
router-sent "round trip" in 90 d was really a split sale with a small buy leg (~$108K of UFO). Fixed in the builder
(`tools/swap-volume-audit-fix.py`: transactions per day; router round trips need balanced legs and a same-asset loop). Live after
the fix: PTGC 24h humans $13,308 / bots $3,470 (79 / 21); expected PTGC 30d bots ~22 %, UFO 7d ~50 %. His window still showed the
old file at 18:55 — raw.githubusercontent's 5-minute edge cache; it clears by itself (the window refetches every 5 min).

**90-DAY SELF-AUDIT (both tokens, after the fix, no changes):** the top bot transactions are two-leg loops with buy/sell balance 0.95
(the 5 % fee) from contracts — textbook; the mixed router + contract transactions are one operator's fixed 33,333,330-PTGC chunk sold
via PulseX v1 inside its own arb txs (EOA with 159K txs). Of 120 bot contracts ($1.28M), 35 never round-trip (together $8,616 = 0.7 %);
the largest, 0xdb2ff97c… ($5,611, split buys to a single wallet 0xc4c041e7…), is almost certainly one person's own buying contract —
the only judgement call left, ~0.4 %. Candidate rule in the session file if he wants the list spotless. Shaka: "thats good".

 (1) His live look at the Volume tile icon, the window, the 📷 card (PTGC / UFO / BOTH), the Socials rows, Mac +
phone — then the Telegram post (if the window says "Couldn't load": Actions → Data Pipeline → Run workflow → `only=swap-volume`). (2) **Worker v7's cron — FIXED 2026-10-07 00:07 UTC.** Cloudflare's scheduler had never bound the triggers (no scheduled events in 7 days, the daily cron included) while the handler and the dispatch worked by hand; deleting both cron rows in Settings → Triggers and adding them back did it — the 00:07 `workflow_dispatch` run started on its own. The pipeline is hourly for real now; the 08:00 sync cron was re-added too. (3) CLOSED 2026-10-07: the UFO TXNS 24H tile reads 40 = the chain's count; the ~10,000 was DexScreener's
bad h24 count on one pair, passed — nothing to fix. (4) The banner robot cannot be shrunk alone (one image) — a re-export if he wants him smaller. (5) UFO day-90
real test 2026-10-07 after ~07:30 PDT. (6) Live looks still owed from 2026-10-04 / 10-05 (Calculators, KPI phone, KPI backgrounds).
(7) Decision -13(c), the orphan `data` branch.

## Before that (end of 2026-10-05)

**2026-10-05 (Monday), closed by Shaka ("let's call it a day, wrap it up"): PUSHED by him as `318957448` — ONE commit for the whole
day (the KPI Report tab, the Calculators page, the Charts page + its GeckoTerminal fix), tree clean. Nothing half-done. Seen live by
him on the Mac: the KPI tab (two rounds of notes, all done), the Charts page (where he found the 14D bug). NOT yet seen live: the
Calculators page, the charts after the GeckoTerminal fix, any of it on a phone. NEXT SESSION STARTS WITH: his live look — Charts
14D on WPLS + HEX (hourly candles if GeckoTerminal answers, "daily candles" if it refuses — never two points), the Calculators
page (Mac + phone), the KPI tab on a phone; the full-size KPI backgrounds if he has them (`logos/kpi/`, gotcha 38); whatever he
brings (ask — screenshots); then the live look owed from 2026-10-04 (below). **2026-10-06 (Tuesday) = UFO day 90: check the UFO
dashboard + PTGC-burned-by-UFO.** Not done, if he asks: the KPI 📷 share image (`TwitterCard`) in the new look; a "30D" mark on
the KPI card's sparklines.**

**2026-10-05 (Monday), afternoon: THE CALCULATORS PAGE RESKINNED — his gold space art as a fixed page plate under a 62 % veil,
"Grays Calculators" in the Socials Hub's metallic title, his five calculator buttons with his icons (three gold, two blue), every
calculator's own disclaimer card framed at the foot ("this needs to stay on the bottom of all the calculator pages"). Three mock
rounds (`design/calculators/`), then `tools/calc-v2.py` on calculators.html; **then the Charts page got the same treatment (`tools/charts-v2.py`: the plate, "Grays Charts", the chart card more solid; the two "—" placeholder sub-tabs gone, the one button centred). **His live look of the charts: 14D drew TWO DAYS, slow, "limited data" — GeckoTerminal refused every call after the first (a 429 prints as a CORS error), `fetchRetry` retried outside the gate, the two-point DexScreener line was cached for 10 min. `tools/charts-gt.py`: refusals count across tokens (pause 4 s / 8 s, then a 45 s circuit), 7D / 14D fall to the prebuilt DAILY file (real daily closes, "daily candles" / DAILY badge) before the two-point line, a fallback is never "fresh" in the cache. Harness `GT_CANDLES=refuse` / `refuse:<n>`.** Pushed as `318957448` (end of day); the Calculators page and the charts fix not yet seen live.**

**2026-10-05 (Monday): THE KPI REPORT TAB REDESIGNED — built to Shaka's mock-up ("perfect, make it live"), written to the Mac,
NOT pushed, NOT seen live.** His page mock-up + two card backgrounds (`design/kpi/reference/`; **the zip with the full-size
backgrounds never arrived — `logos/kpi/kpi-bg-*.jpg` are cut from the side-by-side image, 656 px, swap file-for-file when it
lands, gotcha 38**). Mock v1 (`design/kpi/mock-kpi-v1.html`, README = every decision) approved as rendered, then the build:
`KpiCardV2` at module scope above `KPIContent` — his art as the plate, the lit coin, the panel icons (Treasury coins / LP bars /
droplet / pie / rising chart / green people / money bag / flame), **real 30-day sparklines from the KPI tiles' own
`useH2Series` + `H2Spark`** (the compare card's other token draws its own), the sea-creature row and the v2 fire bar (its
`.p2 .p2-bar` rules now also match `.kp .p2-bar`), figures through `H2Val`; the `kp-*` CSS is a **container-query** unit (under
540 px: sparkline under the figure, badge bottom-right — a phone, or two cards side by side at 1024). Same numbers as before
(the old `renderKPICard` maths moved in unchanged; `renderKPICard` is a one-liner now). Tab container 1264 px, side-by-side
from `lg`, controls in one centred row. **Found on the way: the Socials "Combined KPI Report" row had been DEAD since
`42f244912` (2026-09-29) — its modal was deleted by accident; restored.** Four explainers added (`liquidity`, `liqMcap`,
`volume24h`, `totalBurned`). Not touched: the 📷 share image (`TwitterCard`, 2025 look). **Round 2 (his first live look, Mac): the 📷 button
GONE from the tab ("they can screen shot the images" — the share image now only opens from the Socials Combined row); ADD /
REMOVE restyled as the header's SWITCH button (`.kp-btn`); the VALUE GEN change badge gone (it was the volume change
relabelled and overran the tile); the UFO compare card's Value Generated now from the hourly delivered snapshot (`vgPrices` +
`otherVg` → "7D", EST only when the file is missing / stale); the price change 26 px; the creature row a fixed 40 px that
scales (`NhsFit`) — a scrollbar had made the PTGC card taller than UFO's — and the pair `lg:items-stretch`. Round 3: the burn box is 30D BURN (`bp.d30`); the UFO compare card's burn windows paint from the hourly snapshot at once (the scan only when the file is stale — it had sat on "—" through the ~55-call scan); sparklines = 30 days, the tiles' series.** Harness: 1440
single + both, 1024 both, 390, DS_DOWN, the two Socials rows, the dashboard unchanged — `sessions/2026-10-05.md`. **NEXT SESSION STARTS WITH: his
push + live look (KPI tab both tokens, Add UFO / Add PTGC, Mac then phone; Socials → KPI Report and → Combined KPI Report), the
full-size backgrounds, then — if he wants — the share image in the new look; then the live look owed from 2026-10-04 (below).
2026-10-06 (Tuesday) = UFO day 90: check the UFO dashboard + PTGC-burned-by-UFO.**


**2026-10-04 (Sunday), closed by Shaka ("lets wrap it up and call it a day and update the handover"): HOLDERS DETAILS IS
LIVE with its share card and the three Socials rows, the tile's grey icon, the Home cards' buttons swapped, the BOTH card's fit
fix, and THE LEAGUES REDESIGN (the holder-tiers modal + the Socials combined card, rounds 7–8) — eleven pushes by him, last
`8d578bc74`, tree clean. Nothing half-done. Seen live by him: the Leagues modal on PTGC (Mac, before round 9). NOT yet seen live: round 9's sea plate with the whale + shark
and the clickable tiles, the New Holder Details cards, the live Holders tile, the Home buttons, the combined Leagues card, the
Leagues modal on UFO / a phone. **Round 5, after the wrap (his Home screenshot): the Home cards' two buttons SWAPPED — the big bottom button is ENTER DASHBOARD (logo + chevron → the dashboard), the top-right pill is BUY / SELL (swap arrows → SwapModal); classes `.hc-buy` / `.hc-dash` kept, aria-labels follow the actions. Pushed `78e75aaa5`. Round 6 (his first live look): on the BOTH card "109 NEW HOLDERS" crossed the PTGC panel — the two panels' count groups now scale together to fit (`NhShareCombo`, `.nn-fit`), icon kept. **Round 7: THE LEAGUES REDESIGN — `TierInfoModal` (the Burn panel's Leagues button) rebuilt to his mock-up (sky header, lit coin, three supply tiles with the chosen one glowing, sea-creature rows) and the Socials combined card rebuilt as `LeaguesCombinedCard` (Tall 1080×1350, screenshot-only, his cut-out whale + shark on his sea, gold / green rock tints, silver toggle). Assets `logos/leagues/`, decisions `design/leagues/README.md`. Pushed `4e2201b54`; round 8 (his first live look: tile icons centred, bigger figures) `9cdfb8016`; **round 9: the window's plate is his sea with the whale at the left (20° clockwise, `lg-sea-wide.jpg`), and his shark at the right facing it, and the Starting / Circulating tiles are clickable (same state as the toggle) — `8d578bc74`.** Owed: the coin-stack + cycle icons on real alpha (`logos/leagues/lg-ic-*.webp`, `LG_ART_V` bump on swap).** Written to the Mac, not pushed.** NEXT SESSION STARTS WITH: his live look — the combined Leagues card (Socials → Combined → PTGC & UFO Leagues, Starting + Circulating) and the Leagues modal on UFO + a phone, the Home (both buttons, Mac + phone), the Holders tile (the grey
people icon right of the ⓘ opens the window; the change line is now the file's 24 h net, not PulseScan's), Socials → New
Holder Details in all three columns (PTGC / UFO / BOTH, 24H / 7D / 30D), the 📷 inside the window, on the Mac then his
phone — whatever he brings from it (ask — screenshots); then the Socials Hub live look + the icon sheet (owed since
2026-10-03), then the v2 leftovers (-5). 2026-10-06 (Tuesday) = UFO day 90: check the UFO dashboard + PTGC-burned-by-UFO.**
The day, in order — THE HOLDERS DETAILS SHARE CARD first (pushed `a2382e474`). Shaka: "time to
finish working on the new holder report". The 📷 sits right of the 24H / 7D / 30D chooser in the window; `NhShareModal` (module
scope, above `NewHoldersModal`) on the 2026-09-23 pattern, `ShareCardModal screenshot`, **Wide 1200×675 only**, toolbar = PTGC /
UFO / BOTH (opens on the window's token), period = the window's. A2 for one token (`NhShareCard`: dark left, saucer right, logo
top-right, count 170 px, the "Between them they hold" band with the ladder of the sum), C for BOTH (`NhShareCombo`: saucer on
top, gold PTGC + green UFO panels). Content = the v2 mock-ups' exactly (new holders only, no wallets). Both tokens' views from
the one file; the other token's price via the window's `requestPrice`; `NhsFit` scales a crowded ladder down instead of
clipping. CSS = the `nhs-*` block after `nh-*`. Harness: PTGC / UFO / BOTH at 24H + 30D (1440), 390 UFO, no overflow.
Pushed by Shaka (`a2382e474`), "those look good" — A2 + C stand. **Round 2 (same day): HOLDERS DETAILS IS LIVE —
`NEW_HOLDERS_LIVE=true`** (the dot gone, the "+" beside the Holders tile's ⓘ, the tile's change line = the file's 24 h net,
gotcha 40 — one count on both surfaces), **and the three cards are on the Socials tab: a "New Holder Details" row under Holders
in all three columns** (green, the New Holders tile's green-people icon, "New holder analytics"; PTGC / UFO / BOTH), opening
the card on its own (`NhShareSocial`: 7D, a period chooser on the toolbar, the a18 overlay while the file is out; prices via
`useNhPrices`). Harness: the three rows, 30D, 390, the file-missing state. Pushed `447566fab`. **Round 3: the tile's entrance is the people icon to the RIGHT of the ⓘ — no "+" (`72f650351`); round 4: in GREY (`img.h2-hd`, h2.css, a grayscale filter on the green file; the Socials row and the card stay green) (`859e8ffd1`).** `sessions/2026-10-04.md` rounds 2–4.

**2026-10-03, second session (Saturday), closed by Shaka ("lets wrap it up. good work"): THE SOCIALS HUB REDESIGNED — built,
pushed by him as `6786b4af0` (mock-up rounds `9d3f434f0` before it), tree clean, NOT yet seen live by anyone. Nothing half-done.
NEXT SESSION STARTS WITH: his live look at ptgc-ufo.com → Socials (Mac, then iPhone + iPad — one column under 900 px), whatever
he brings from it (ask — screenshots), the full-size icon sheet if he has it (swap `logos/socials/hub/<col>-<key>.png` file-for-
file), then the list below (-9 … -8: the Holders Details share card).** Shaka put Holders Details on the back burner ("maybe next session") and brought a full-page mock-up + an icon
zip for the Socials tab. The zip was mis-cut (every icon off its mark, labels bleeding in) — the icons are cut from his mock-up
image instead (70 × 56, provisional; **he owes the full-size sheet**, swap `logos/socials/hub/<col>-<key>.png` file-for-file).
Six mock-up rounds in `design/socials-hub/` (README = every decision; approved state `renders/hub-v3-1240.png`): his wide sky
ONCE (`hub-sky.jpg`, never mirrored — "too many big planets"), metallic title over a dark pool, three framed columns with darker
headers, the token logos on the Logos rows, the dashboard droplet on RH Core Liquidity, his new gold globe on The Grays & The
Cores, a black gap under the tab band, and **the rows reordered: Logos / Burn / Value Generated / KPI / Holders level across all
three columns, then Token Allocation + Targets level between PTGC and UFO (Combined: RH Core Liquidity, Leagues), then each
column's own.** Built by `tools/socials-hub.py` (run on both copies, sha256 `c76bdf7b…`): `sh-*` CSS, `ShRow` / `ShCol` at module
scope, the tab's JSX — **every row's onClick is the old hub's handler, lifted verbatim by the script**; only frame, art and order
changed. Harness: both tokens at 1440, phone 390, no overflow, all 26 rows in the designed order, Burn Stats opens its card.
`sessions/2026-10-03-socials-hub.md`. **NEXT: his push + live look (Mac, then iPhone / iPad — the hub is one column under
900 px), the icon sheet, then back to the list below (Holders Details share card, -8).**

**2026-10-02, evening (date note: the two sessions labelled "2026-10-03" above and below were worked on Oct 2 Pacific — the commits
are dated 2026-10-02; the labels stay, the day-90 date is still 2026-10-06). HOLDERS DETAILS — built, HIDDEN, written to the Mac, NOT
pushed, NOT seen live.** Shaka's new idea, discussed first then built: a window listing who became a PTGC / UFO holder (balance
0 → above 0) and who left (→ 0) over 24H / 7D / 30D (default 7D), each arrival with wallet + copy + PulseScan link, when, what
it holds NOW (+ USD) and its league creature; the departures collapsed underneath with what they had. New − Left = Net, and
**once live the Holders box's change line reads that same count** (Shaka: "it needs to match what the dashboard says" — a "+5"
is PulseScan's NET, there is no list of five behind it; he chose one count on both surfaces). Data = `data/new-holders.json`
from the new hourly `new-holders` step (`scripts/build-new-holders.mjs`, exact balances at both ends of each scanned range,
contracts and the DAO wallets excluded, 30-day backfill done: PTGC 7D net +22 = the box's +22). **Hidden:** `NEW_HOLDERS_LIVE=false`
→ a very faint dot bottom-right of both dashboards opens it (`NhDot`); **go-live = that one constant true** → dot gone, a "+"
button beside the Holders ⓘ, the tile's line from the file. Gotcha 40. `sessions/2026-10-02.md` "evening". **Round 2 (same evening): his art on it** — the gold UFO panorama as the header plate
(`logos/holders/nh-sky.jpg`, green-rotated on UFO), his New / Left / Net icons + bar-chart art on the tiles (`.nh-stat`), the panels'
glass toggles (`.nh-tg`), and the league as the creature LADDER in his sea art (`NhLadder`: 🐬×1 🦑×8 🦐×4 — getBurnC on the
STARTING supply, no words). **Round 3:** his seven size / readability asks, USD column, opens on 24H; the script rebuilt on EXACT
per-block balances (schema 2 — a replay of Transfer values never reaches zero on these tokens, the fee leaves without a Transfer;
endpoints-only missed wallets that bounced inside the range); a one-token dust floor measured then DROPPED at Shaka's call
(`DUST = 1n`, above zero = holding, PulseScan's reading); the window reads per WALLET over the period with an "In and out"
section for bots that came and went (counted in neither). PTGC 30D now 130 / 52 / +78 vs PulseScan +94. Pushed by Shaka: the
build (`91405a01a`) and round 2 (`68722802d`); round 3 pushed (`6646199fe`, after a rebase conflict on the data file — the bot had written its own; his version won).
**Round 4:** clean shrimp (`SEA_ART_V=4`), solid-colour title, RETURNING pill, bigger everything, green USD, no tile
sub-lines, the `NhTotals` band (sum of the new holders' bags + its creature ladder). **Round 5:** bars inset again,
RETURNING hover + tap card, no line above the title, sortable columns (`NhTh`), no stacked ladders (3 tiers in rows, 4 in
totals). **Round 6:** headings centred over their columns in the token colour; a NEWEST / BIGGEST sort toggle on phones.
**Round 7:** his green-plus / red-minus people icons on the New / Holders Left tiles (`NH_ART_V=2`). **Round 8:** no "ago"
line under the dates, no "holdings as of" note; **the share card MOCKED UP, not built** — `design/holders-details/mock-share-v2.html`
(+ `renders/share-v2.png`): Wide only, single-token A2 and the COMBINED card C. Rounds 1–7 pushed by Shaka (last `90bf01990`);
round 8 + the mock-ups on the Mac, not pushed. **Closed by Shaka ("let's call it a day"). NEXT SESSION: build the share card from
the v2 mock-up** (camera right of the period chooser, `ShareCardModal screenshot`, Wide 1200×675 only, PTGC / UFO / BOTH on the
toolbar — the plan is at the end of `sessions/2026-10-02.md`), then his iPhone / iPad look at the window, then the go-live word;
the owed v2 items below stand.

**2026-10-03, closed by Shaka ("lets wrap it up for the day"): v2 IS LIVE (`93e7774e7`), post-deploy walk done and pushed
(`c5ca286b9`), tree clean. Nothing half-done. NEXT SESSION: whatever he brings from living with v2 (ask — screenshots), then
his own look on a real iPhone + iPad (owed), then the post-flip polish that used to be pre-flip (-5): the DAO Treasury's fourth
tile (keep or replace — ask), UFO's Value Gen tile at the live 6 % (now checkable live), the LP header's % lines over a few
days. 2026-10-06 = UFO day 90 (item 5): check the UFO dashboard + PTGC-burned-by-UFO that day. The classic branches stay
until he says he has lived with v2; then one clean-up session removes them and retires the byte-identity probes.**

**🚀 2026-10-03 — THE FLIP. Shaka: "Make it LIVE!!!!!!!" — `HEADER_DESIGN='v2'` in all four files (index.html line ~841,
calculators.html, charts.html, portfolio.html); the v2 dashboard header, KPI tiles, panels, LP Pairs table and the sibling
pages' headers are the default for everyone from this push. The preview switch (`?<word>`) still works but is moot. The classic
branches STAY in the code (the `!hdrV2` forks, the `h2PreviewOn` reads) until he has lived with v2 — deleting them is a later,
separate clean-up (then `probes/lp-dom.js`, `vg-classic.js`, `panels-classic.js`, `dom-hash.js` retire). Harness: v2 renders on
all four pages with NO preview flag (`.h2-desk` present, the classic `<header>` gone / display:none).
POST-DEPLOY CHECK DONE 2026-10-03 on ptgc-ufo.com from the desktop app's built-in browser, preview flag REMOVED (a plain visitor): PTGC dashboard v2 (banner, 7/7 sparklines drawn, 4 panels, LP table), Calculators PTGC / Charts UFO / Portfolio (real prices, Day pills, quotes), BUY-SELL from Calculators → the Switch window open on the dashboard, Live Feed from Charts → the deck, phone 375: UFO dashboard + Calculators (banner, triangle, no sideways scroll). Still owed: Shaka's own eyes on his iPhone / iPad. The list, for reference: PTGC + UFO dashboards (banner, tiles + sparklines, the
four panels, LP Pairs), Home → dashboard, Calculators / Charts / Portfolio headers + their BUY-SELL and Live Feed jumps, the Live
Feed, a phone. A visitor with the OLD page cached sees it for up to 10 min (Pages `max-age=600`).**

**2026-10-03 — go-live prep, item (2) of the plan DONE and HIDDEN: the sibling pages wear the v2 header behind the same
preview switch.** Shaka ("make sure those dont go live yet… we dont want to ruin the suprise") picked **A — the dashboard's full
banner + gold band on every page** from a three-option sheet (`design/sibling-header/renders/sibling-header-v1.png`), BUY / SELL
on those pages → the dashboard's switch.win window, Ledger left alone. Built: `h2.css` (the h2-* block moved OUT of index.html,
linked from the same spot by all four pages), `h2-header.jsx` (`SiteHeaderV2` + the shared pieces, loaded by calculators +
portfolio), a static twin in charts.html (`#hdrV2`, `h2Boot`), `PortfolioHeaderV2` (both coins, PTGC / UFO / PLS quotes, the
page's buttons as pills), `?open=swap|feed` on index.html (opens the Buy/Sell window / the deck on arrival), the phone
banner's missing change triangle fixed (gotcha 39), `deploy.yml` ships `*.css *.jsx`. Classic renders proven identical on all
four pages (`probes/dom-hash.js`), v2 rendered 1440 / 1024 / 768 / 390 both tokens with no overflow. **Written to the Mac, NOT
pushed, NOT seen live.** All edits = `tools/sibling-header.py` (run on both copies). **The flip is now FOUR constants in one
push** — `HEADER_DESIGN='v2'` in index.html, calculators.html, charts.html, portfolio.html. `sessions/2026-10-03.md`.
**Later the same day (his screenshot):** the Market Cap / Liq-MCap sparklines read "unavailable" (dashed) for the ~5 s the
GeckoTerminal candles take — now a solid breathing baseline while loading (`.h2-spwait`; dashed only after the last retry) and
the candles cached 30 min in `LS.H2_PX`, so a reload paints at once. v2 only; classic fingerprint unchanged.
NEXT: Shaka's live look with the switch on (the three pages, Mac + iPhone + iPad, both tokens, the two jumps), then the
pre-flip leftovers (-5), then the flip.

**2026-10-02, closed by Shaka ("let's wrap it up for now"): rounds 22–25, all pushed by him as they landed (last `268038fce`,
the phone + iPad pass). Nothing half-done. NEXT SESSION = "start preparing to make it live": (1) his live look at today's
rounds on the Mac, then a real iPhone + iPad, both tokens — none of today has been seen live yet; (2) the sibling pages'
headers (-6); (3) the pre-flip leftovers (-5: DAO Treasury's fourth tile — ask; UFO's Value Gen at the live 6 %); (4)
`HEADER_DESIGN='v2'` + push, header / panels / LP Pairs / sibling headers together. The ordered plan is at the end of
`sessions/2026-10-02.md`.**


**2026-10-02, round 22 — LP Pairs alignment (Shaka's screenshots: headings vs data "some left justified, some centered";
the band's tiles "need consistency").** Two option sheets rendered from the real build (`design/dashboard-panels/renders/
lp-align-table-v1.png`, `lp-align-tiles-v1.png`); **Shaka picked Table A + Tile 1**: every table heading and cell centred
under its heading (Pair left, Actions centred, a quiet "7D" heading over the curve column, the curve centred under it) and the
band's tiles with label + figure flush left on one x, icon / change at the right (`.p2-lphk` first column `1fr`, not
`auto`). CSS in the `p2-lp*` block + the v2 heading row only; classic byte-identical (`probes/lp-dom.js`). Written to the Mac,
NOT yet pushed or seen live. **Round 23 (same morning, his mock-up):** PTGC Burned by UFO's three boxes carry icons in dark
squares (the VG "Burn PTGC" flame + coin cluster, his money stack `pbu-money.webp`, his pie `pbu-pie.webp`), label over a
22 px gold / green / gold figure (`p2-pbt`); the creature counts in the Burn panel and the PTGC-by-UFO row are 20 / 18 px
(`p2-cnt`); the Value Generated tile names are 14 px through `P2Name` (nowrap + shrink-to-fit on the text node, so never a
second line — the base `.p2-vgn` size lost its `!important`). Classic identical both tokens (`probes/panels-classic.js`).
**Rounds 24–25:** no "as of" top-right on Burn / PTGC-by-UFO, period labels 14 px, Live Feed sky .72, Home tag line
"A COMMUNITY BUILT SITE FOR THE GRAYS ECOSYSTEM"; then **the phone + iPad pass for all of v2** (390 / 768 / 1024 both
tokens): Token Allocation stacks on phones, the creature strip fits, the PTGC-by-UFO title on one line, a v2 band for the
phone LP header (`p2-lphp` + `.p2-lphm` figures), the classic All/RH knob fixed (`left-0`, pre-flip item c — done), 1024-tier
VG names may wrap and period figures 19 px. **Owed: his look on a real iPhone + iPad.** `sessions/2026-10-02.md`.

## Before that (end of 2026-10-01 — three sessions)

**2026-10-01, evening session, closed by Shaka ("call it a day"): rounds 19–21, all pushed by him as they landed (last
`63f6e1ae4`, "v2 LP Pairs band: three tiles one width…"), each seen live on his Mac. Nothing half-done. NEXT SESSION STARTS
WITH: whatever he brings (ask — he usually has a screenshot or a mock-up), then the pre-flip list (-5), then the sibling
headers (-6).** The evening (`sessions/2026-10-01.md`, rounds 19–21) — (1) the Live Feed tab's NEW badge: seven mock-ups
(`design/dashboard-panels/mock-tabbadge-v1.html`, render `renders/tabbadge-v1.png`), **B picked "with a slight glow"** → a
1 px gold hairline pill, gold caps, soft glow, one rule for both tokens (`.h2-tabs .h2-new`, the UFO override line gone);
(2) **Value Generated's "from $X of volume" is back under v2, to the RIGHT of the total on its baseline** (`.p2-vgfrom`, a
`{hdrV2?…:…}` fork; UFO gets the line too), following the 24H / 7D / 30D / 90D switch — and the blanket rule that hid every
line under the figure is gone, so the amber price notes show again as one quiet line; **the "as of" under that figure is hidden again on his ask (round 19b,
`.p2-vghead>.p2-asof{display:none}`)**. Round 19 pushed by Shaka as `75cae8575` and seen live; 19b written to his Mac. Classic byte-identical on both tokens (`probes/vg-classic.js` vs HEAD).
**Round 20 (same evening): LP Pairs — the band's SORT toggle is gone, sorting is on the column headings (`LpTh`, stacked
▲▼, six sortable columns, same `sortBy`/`sortDir` state); a third glass tile "Value Gen 24h" (green, `lp-bars-green.webp`) =
volume × fee between Volume and Liquidity; a "Value Gen" column after the curve (vol × `cfg.feeRate` — PTGC 5 %, UFO the live
contract fee, "—" when unknown); the 24h % heading is "Price 24h" (Shaka had read the badge as the liquidity's move — it is
DexScreener's price change). Grid tiers re-cut (curve leaves under 1120, Value Gen under 950). Classic LP identical both tokens.
Pushed `f91cbb1fe`, seen live. **Round 21:** the band's three tiles one width (222 / 198 px), further from the title, labels
centred over their figures; the title-row tier for tablets moved 760 → 980 px — pushed `63f6e1ae4`, seen live.**
**Owed from the evening:** the band's 980–1110 and under-980 tiers and the sort arrows at 1120–1280 on a real tablet / narrow
window (only the Mac at full width has seen any of it); the Value Gen tile + column on UFO at the live 6 % fee (the harness
reads 0 bps → "—"); phone + iPad for everything v2 (unchanged owe).


**2026-10-01, afternoon session, closed by Shaka ("call it a day"): six rounds, all pushed by him as they landed (last:
`c34383fa2`, "sparkline colour = the volume change vs the day before"), each seen live on his Mac. Nothing half-done.
NEXT SESSION STARTS WITH: whatever he brings — the LP Pairs section is where he was working (header done, rows done; the
drawer, the "< $1K" button and the phone cards are untouched), then the rest of the pre-flip list (-5 below), then the
sibling pages' headers (-6, same push as the flip).** The afternoon, in order — detail in `sessions/2026-10-01.md`,
rounds 16–18:
1. **Value Generated tiles** rebuilt to his layout (mock-up A/B, "B, not that loud — no pill"): icon | thin divider |
   name / quiet % / figure, no bars, his three-diamond cluster (`vg-diamonds3-v2.webp`); then names 12.5 px (measured —
   never a second line at ≥ 1280) and figures 31 px through `H2Val`; then UFO's burn tiles stack the 36 px coin on the
   flame like the LP pair discs. `.p2-vgt` = a CSS grid over the classic markup; classic byte-identical.
2. **LP Pairs header** = his band (`LpHeaderV2`, a `{hdrV2?…:…}` fork, classic DOM hash equal): ring logo, LP PAIRS +
   count, Volume 24h / Liquidity glass tiles with his bar icons (`lp-bars-gold/blue.webp`) and a change line (volume = the
   KPI tile's "vs 7d avg", liquidity = vs the lv-snapshot 24 h ago; All only, both vanish under RH Cores), All / RH Cores
   + SORT as the panels' glass toggles, Ratio sort dropped (his mock). Squeeze in three tiers (one compact row to
   1110 px, then the controls drop, tiles never stretched) after his live look at ~1265 px.
3. **LP Pairs rows** = his mock-up + his sparkline brief: 30 px rank rings, the volume's change vs the day before under
   it (DexScreener 24 h vs the curve's previous 24 h; no line without a curve), the sparkline as layered light on a
   SQUARE-ROOT height (`LpSpark` — one outlier bin used to flatten the week; data untouched), 24h % as a badge in their
   red, Txns total over buys | sells; the curve's colour = that volume change (his pick over price; red `#FF2E3B`).
**Owed from the afternoon (all built in the harness, all seen live by Shaka except where noted):** the LP header's two
% lines on real data over a few days (if the liquidity one reads a few % off every day, compare snapshot-to-snapshot —
round 17 notes); the UFO page's LP rows and header (he looked at PTGC); phone + iPad for everything v2 (unchanged owe).

**Earlier the same day: fifteen rounds of v2 clean-ups, all pushed by Shaka through the morning (last: `494f6e1d8`, "dark
pools behind the creature row and the bar-end whale"), every one seen live on his Mac as it landed. Nothing half-done.**
The day, in order — the detail is `sessions/2026-10-01.md`, rounds 1–15:
header buttons centred + address right-justified + bigger tile figures (`H2Val` shrinks, never ellipses) · `PTGC IN LP` /
`UFO IN LP` · the sparklines rebuilt three times to his spec (thin crisp line, peak lighting by `h2Peaks`, 30-day window
`H2_DAYS`, "30D" tag, one colour per token) · panel toggles = option A glass (`mock-toggles-v1.html`), 28 px, Value
Generated's stacked up level with Burn's · tab row on his gold band (`logos/header/tabs-bg.jpg`, `.h2-tabband`) framed in
black, fire-light pill, no "Updated" badge · the Token Allocation donut in SVG with lighting (`AllocRingV2`) · his icons
everywhere on the panels (`dao-*.webp`, `vg-*.webp`, `alloc-pie.webp`, `sea-*.webp` + `SeaIcon`, `SEA_ART_V=3`) · dark
radial pools behind the type on Value Generated, DAO Treasury and Burn · UFO's burn windows paint the snapshot at once
(amber "as of" past 6 h) instead of a blank wait. Gotcha 38 (image swaps need a version query).

**2026-10-01: v2 clean-ups, round 1 — Shaka's first three asks, CSS only in the `h2-*` block:** BUY/SELL + SWITCH
labels centred between the logo and the button's right edge (desktop), the contract address + copy button
right-justified under the title (`align-self:flex-end`; visible on PTGC, a no-op on UFO where the address is the
widest line), and the tiles' change line 21 → 26 u with the tile 214 → 236 u so the sparkline keeps its room
(phone tiles 14 → 17 u). **Round 2:** the LP tile reads `PTGC IN LP` / `UFO IN LP` (which also ends the 1024 badge
overlap), and the tile sparklines are Shaka's spec now — one crisp 1.6 px vivid line (`#FFD24D` / `#8DFF3A`), a 2 px
half-alpha drop-shadow as the only glow, a .16 → 0 fill, each series on its own Y range in a taller box (70 u, tile
250 u), then **layered light on the same geometry**: .9 px pale core, 1 px near-white core + bloom + a clipped pool of
light under the 2–4 most prominent peaks only (`h2Peaks`) — after he called the old ones fuzzy (and a neon pass in
between fuzzier). **Round 3:** the window is **30 days** (`H2_DAYS`, 720 GeckoTerminal candles for Market Cap, ~150
pipeline samples for the rest — the cure for the angular lines), a "30D" tag on every tile, ONE line colour per token
(gold / green — green means UFO, never "up"), the figures 38 → 46 u with `H2Val` shrinking a figure that would overrun
(never an ellipsis on a number). **Round 4:** the panel toggles are option A of `design/dashboard-panels/mock-toggles-v1.html`
(dark glass, lit translucent pane, gold `--tg`) via `.p2 [role="group"]:not(.p2-pill)`, and Value Generated's two toggles are
stacked (`.p2-ctl` column up on the title row, level with Burn's; a row under the title on phones), 28 px tall; soft dark
radial pools behind the VG headline, the stack and the DAO Treasury's PTGC Buys + Ledger (`p2-daobtns`); the tab row's type 24 u. **Round 6:** the Token Allocation donut is pure SVG (`AllocRingV2`:
per-slice radial gradients, top-left light, bloom, underside, rims, `P2_TONES`; the `.p2-rg` conic div is gone) — same data,
order, size, logo. **Round 8–9:** the sticky tab row is a black wrapper around a gold-bordered band on Shaka's art
(`logos/header/tabs-bg.jpg`, `.h2-tabband`; dark where the tabs are, the planet bright at the right) with a glowing gold
pill for the active tab and no "Updated" dot/text (refresh button kept); VG's "from … vol" line hidden under v2 (both top panels 366 px); DAO buttons' pool darker; the DAO Treasury's emoji replaced by Shaka's gold icons
(`logos/panels/dao-*.webp`, `P2_DAO_ICONS`, v2 only) and Value Generated's by his (`vg-*.webp`, `P2_VG_ICONS` by tile name); flame on both burn titles + the creature row,
his purple pie on Token Allocation (`alloc-pie.webp`); **his sea-creature art replaces the creature emoji on the v2 panels**
(`logos/panels/sea-*.webp`, `SEA_ART` + `SeaIcon` — emoji stay the data and stay everywhere else); title icons 44 px. The remaining angularity is the
pipeline's ~5 samples/day, not the drawing. Harness at
1440 / 1024 / 390, both tokens; classic byte-identical (script block diff 0). `sessions/2026-10-01.md`.
**Owed: his live look, then the rest of his clean-up list, then phone + iPad, then the flip.**

**2026-09-30, night: the LP Pairs section is BUILT under v2 — the whole preview design is now complete — and its curves
come from the pipeline (`data/pair-volume-7d.json`, `scripts/build-pair-volume.mjs`, hourly `pair-volume` step; first run
#73 landed). Tomorrow: Shaka's small clean-ups on the page, then phone + iPad, then the flip.** Shaka
brought his own mock-up (saved: `design/dashboard-panels/reference/shaka-lp-pairs-mockup.png`) and reversed three of
his morning calls: rank numbers, one line per pair and a 7-day volume curve per pair are IN; the Buy/Sell column and
the eye icon are out. One mock-up round (`design/dashboard-panels/mock-lp-v1.html`, "okay. looks good."), then built:
`LpPanelV2` / `LpTableV2` / `LpRowV2` / `LpSpark` + `useLpVolSeries` / `fetchPoolVol7d` (module scope, above
`DashboardSkeleton`), the `p2-lp*` CSS block, hook classes on the section header; the curve is REAL per-pool hourly
volume from GeckoTerminal (queued, cached 30 min, dashed when a pool is not listed — never a seeded shape); table from
640 px up (curve column leaves under 1100, Txns + Vol/Liq under 950), the stacked cards stay on phones. Classic proven
byte-identical with the switch off (`probes/lp-dom.js`). Gotcha 37. **Shaka's first live look (Mac): GeckoTerminal
refused the burst — four curves then dashes — fixed the same night (round 2: ~1 call/s, a 429 pauses the queue and the
pool is retried, refused = "loading" not dashed, answers cached in localStorage `LS.LP_VOL` for 30 min); his other
asks done too: larger type throughout the table, a wrench for DEXTools, a bigger ⓘ drawer. Round 3: the curves were
STILL dashed for quiet pools — GeckoTerminal's candles are sparse (only hours that traded) and the parser wanted 12 of
them; now the week is binned with real zeros (`GT_SPARSE=1`); the Burn panel's USD/TOK toggle was being covered by the
"as of" label when the title row wrapped at ≤ 1250 px (label `pointer-events:none`, titles shrink under 1280); and the
action icons were "too loud" — option C built (dark glass squares, line-graph glyph for DEXTools). **Round 4: the
curves now come from the PIPELINE** — `scripts/build-pair-volume.mjs` → `data/pair-volume-7d.json` (hourly step
`pair-volume`), read first by `useLpVolSeries`; the live per-pool read is only the fallback (a pool the file lacks, or
a file > 36 h old). **The file exists (run #73, 2026-09-30 22:04 UTC: 47 pools read, 0 refused, 8.6 KB; the step takes ~9 min on
GitHub's runners because GeckoTerminal answers them slowly — the hourly job is ~23 min now, still well inside its
50-min timeout; gate it to every 3 h if cadence ever suffers). Verified live from the Mac: 20 of 20 rows drawn from
the file, zero per-pool calls.** Round 5: curve moved next to the Volume figure, the three right-hand columns centred, regular weights throughout; round 6: 50 px rows. Owed: phone + iPad** — the harness fakes
the DexScreener logos and the GeckoTerminal answers. Found on the way, classic, live today:
the phone All/RH Cores switch draws its knob at the "on" end while All is selected (one line if he wants it fixed).
`sessions/2026-09-30.md` "Night". **Flip = `HEADER_DESIGN='v2'` + push: header, panels and LP Pairs together.**

**2026-09-30: the dashboard header redesign is BUILT into `index.html` — behind the hidden preview switch, classic
still the default.** `HEADER_DESIGN='classic'` (next to `HOME_DESIGN`); `'v2'` = Shaka's mock-up: the art banner
(`DashHeaderV2` — desktop ≥ 1024 px and a phone/tablet layout), a sticky tab row that grows a token · price line once
the banner scrolls away, and the seven KPI tiles with **7-day sparklines from real data on every tile** (`KpiTilesV2`,
`useH2Series`: GeckoTerminal hourly candles for Market Cap, `lv-snapshots.json` for Volume / Liquidity — fetched only
when v2 is on —, holder / tokensInLP / transaction history for the rest; a missing series is a dashed flat line, never a
fake shape). Same numbers, same modals, same loaders as the classic header; the classic blocks are untouched and the
classic render is byte-identical with the switch off. Assets under `logos/header/` (jpg/webp, 480 KB for all four).
**The switch:** `ptgc-ufo.com/?<word>` → password box → v2 on for that device (`LS.HDR_PREVIEW`); the same link
shows "Turn off" afterwards. Only SHA-256 hashes go in the code (`HEADER_PREVIEW_GATE_HASH` for the word,
`HEADER_PREVIEW_PASS_HASH` for the password) — **Shaka's hashes are in (2026-09-30, one secret for both, his
call)**; an empty hash would mean the switch does not exist. Reminded Shaka: hides it from visitors, not from someone
reading the public repo. Header seen live by Shaka the same day (three tweak rounds: the art images un-squeezed — Tailwind's preflight —,
the alien head clear of the stats, stats centred, taller tiles). **Afternoon: the four panels under the tiles (Burn /
Value Generated / Token Allocation / DAO Treasury) and UFO's "PTGC Burned by UFO" redesigned too — five mock-ups
approved one by one (`design/dashboard-panels/README.md`), then built as a SKIN over the classic markup (`p2-*` CSS,
`P2Art` / `P2Icon` / `P2Bar` / `AllocRingV2` / `CreatureStripV2`, hook classes), assets in `logos/panels/`; same
switch, same numbers and modals as today. Seen live by Shaka through seven tweak rounds the same evening (pop-ups,
heights, titles, as-of labels, WETH mark, backdrop, and the Market Cap / Liq-MCap sparklines that stayed blank after
one GeckoTerminal miss — they retry and refresh now).** "Flip the switch" = `HEADER_DESIGN='v2'` + push, header and
panels together. **LP Pairs done the same night (above).** Gotcha 36. `sessions/2026-09-30.md`.
**Before that (2026-09-29):** the mock-ups — `design/dashboard-header/` (`mockup-ptgc-v11.html`, `mockup-ufo-v1.html`,
the phone pair; `README.md` = every decision: no top nav/search bar, our solid-gold BUY/SELL + green SWITCH, his
background band + alien head placed like his reference, dark shading behind all text, fire-light coin with no second
ring, sampled golds, green change with a triangle; UFO = same art, no hue shift).

**End of day 2026-09-29 — everything is pushed; Shaka checked it live.** Affiliates unfrozen (worker v6), the
affiliates page on iPhone/iPad, three Socials cards redone (Affiliates Report, Combined Value Generated + its data fix,
Grays & Cores + its pair fix), white titles on Holders (combined) and RH Core Liquidity, and one rule for which
DexScreener pair prices a token (gotcha 35). Shaka confirmed live: the affiliates page on phone/tablet, the Affiliates
Report and Combined Value Generated cards, the combined card's UFO half matching the UFO dashboard at 90D, and the
Grays & Cores card with real WPLS / eHEX moves. **Only open look:** the portfolio page after the price-pair push
(5075cb8a9) — PLS should read ~4 % lower than before, UFO should equal the UFO dashboard. **Next session:** the
Combined Burn Stats card (the last old-style card under Socials → Combined; mock-ups first) — see "Next up".

**2026-09-29: the affiliates page frozen at Sep 23 — the `ptgcapi` worker's WRITE path, not this repo.** Since
the v5 redeploy on 2026-09-23 every write to `data/affiliate-commissions.json` (the 08:00 UTC cron and ToolBox's
Sync button alike) answered `500 {"error":"btoa() can only operate on characters in the Latin1 (ISO/IEC 8859-1)
range."}` — four em-dashes have sat in the file's `voidReason`s since Sep 21, and the redeploy's newer
compatibility date made `btoa()` strict. The referral API had 31 newer buys the whole time; ToolBox said "Sync
Complete!" because it showed the modal before the (queued) write ran. **Worker v6** = `handover/ptgcapi-worker-v6.js`
(UTF-8-safe base64, `toBase64Utf8`), **not deployed yet — Shaka pastes it into the Cloudflare editor**, then Sync in
ToolBox, then check ptgc-ufo.com → Affiliates. ToolBox's Sync now waits for the real write (`saveDataImmediate`).
`sessions/2026-09-29.md`. **Deployed 13:26 UTC — verified: 171 September buys on the live endpoint, the retry queue landed
the 31 within a minute of the deploy.**

**2026-09-29, later still: one rule for which DexScreener pair prices a token** — gotcha 35. Live before the fix:
the portfolio priced PLS ~4 % high (WPLS/NananaX) and UFO ~6 % off the dashboard (UFO/HEX, not the UFO/WPLS main
pair); the DAO treasury priced eHEX ~4 % high (eHEX/NananaX); the combined cards' UFO price was UFO/HEX. Now
`dsPricePair` everywhere in index.html, `pricePair` in portfolio.html, and the same rule in
`scripts/fetch-burn-history.js`. Harness stub: `baseToken.address` is now the requested token's address. Pushed as
5075cb8a9. **Owed: the portfolio look** (PLS ~4 % lower, UFO = the UFO dashboard).

**2026-09-29, later: the Grays & Cores price card restyled** — `GraysCoresSocialModal` (module scope, Wide/Tall,
24H–90D). Shaka kept today's layout (cores left, PTGC + UFO right); dressed with the combined logo, glass-strip headers,
glowing coins, brand-tinted core rows and plain coloured moves (no pills, no art backdrop). Tall is new (Grays on top,
cores 2-up). Loader honest-null: "—", never $0. **Seen live by Shaka ✓.** `sessions/2026-09-29.md` "Later".

**2026-09-29, late evening: the Combined Value Generated card redone** — `CombinedVgSocialModal` (module scope, Wide/Tall,
24H–90D): white combined total + per day + volume, PTGC and UFO panels built from the stand-alone Value Generated tile, and a
"where it went" strip (DAO / holders & stakers / liquidity / burned across both tokens; a group is "—" unless every bucket is
known). **Night fix:** the UFO half now uses the UFO dashboard's delivered figure from the PTGC page too (it was volume × fee,
"est."), and the other token's 24H volume sums every pair. **Seen live by Shaka ✓.** `sessions/2026-09-29.md` "Late evening" + "Night".

**2026-09-29, evening: the Socials Affiliates Report card redone** — `AffiliateSocialModal` (module scope, Wide/Tall,
screenshot-only, month picker on top): the month's totals, its top 5 referrers with share bars, and a clean gold
All-Time bar (solid gold edge, 🏆 pill + creatures, emoji labels, white numbers — Shaka: "pop but clean"). Month
commission no longer bills below-minimum entries (39.14M → 39.12M for Sep). **Seen live by Shaka ✓.**
`sessions/2026-09-29.md` "Evening".

**2026-09-29, afternoon: the affiliates page rebuilt for iPhone and iPad.** Header no longer pinned under 640 px (it
was a third of the screen), Recent Activity rows are two lines on phones, the Referrers Registry and the Commission
Log are one card per referrer under 640 px (with a phone-only Sort select) and `min-w` tables that scroll sideways
on a tablet, the referrer card / Payment Receipts modals wrap instead of colliding; stats bars 4-up on tablets.
Desktop byte-identical. Harness `AFFIL_DATA=real`. **Seen live by Shaka ✓.**
`sessions/2026-09-29.md` "Afternoon".

### Before that (end of 2026-09-28)

**2026-09-28, afternoon: the Socials RH Core Liquidity card redone** — Richard Heart on stage as the plate
(`logos/socials/rh-heart-stage.jpg`, watermark removed), the original two-column layout (PTGC gold / UFO green, six
pair rows, no bars) in the dark left, combined figure in white top-right, flat token colours. `RhCoresSocialModal`
at module scope, Wide only (Shaka), screenshot-only. Six mock-up rounds. Owed: the live look on the Mac.
`sessions/2026-09-28.md` "Afternoon".

**2026-09-28: UFO/WETH removed from the RH Cores liquidity modal (the "RH" button in the Liquidity box) and
the RH-only switch on the pairs table.** The seeded WETH pool carried `isRHCore: true` and `resolveUfoPairs`
stamped `true` on every constructor pool, so a chain-read UFO/WETH row (DexScreener missing it — `$0` volume
is the tell) walked in through the `_rhCore` placeholder; the Socials card builds from `RH_CORES` and was
always right. Three lines in `index.html`; before/after proven in the harness (`probes/rh-modal.js`,
`probes/rh-toggle.js`). Owed: a 10-second live look — UFO → RH → no WETH row. `sessions/2026-09-28.md`.

### Before that (end of 2026-09-26)

**2026-09-26, afternoon: the Live Feed reskinned** — Shaka's painted ship-over-city art is the sky
(`logos/livefeed/deck-bg.jpg`; UFO is the same file hue-rotated to green), glass fee boxes with icons (LP boxes carry
the PLS / PLSX / WETH logos), metallic totals, a glass Generated pill, green amounts in the ledger, and a two-line
phone ledger instead of the sideways scroll. Every animation is the same code. Gotcha 34. Owed: the live look, desktop
and phone, PTGC and UFO. `sessions/2026-09-26.md` "Afternoon, part two".

**2026-09-26: the Holders cards redone — Socials → Holders (both tokens, gold→green) and the ⓘ on each
dashboard's Holders box opens the one-token card directly (PTGC gold / UFO green, 7D/30D/90D trend, Wide/Tall) —
the 2025 in-page modal is deleted. The Socials hub has a Holders button in all three columns, on one row.** Six rounds of mock-ups, then built
on the 2026-09-23 pattern (`HoldersSocialModal` / `HoldersSingleModal`, module scope just above
`DashboardSkeleton`, Wide/Tall, screenshot-only). The old html2canvas Holders card and its two Chart.js
canvases are gone; the trend is an inline SVG from `snapshotsFor`. Every number is the ⓘ modal's (current, 24H,
7D/30D/90D "then" + net, per-day avg, today-vs-avg %) plus the tier counts; a missing read is "—" /
"Gathering…", and the loader no longer turns a failed count into 0 or a failed tier set into five zeros.
Title icon = Shaka's two-colour alien, cropped to `logos/combined/14_Two_Color__Alien_2_head.png`, doubled.
Shaka's first live look found the tier tiles crossing the frame on his Mac (Apple emoji + real fonts run taller
than the harness) — sizes trimmed for 30–44 px of slack, measured by the new `probes/card-slack.js` (want ≥ 25).
One harness lie fixed in `run.js` (the stub's UFO pairs were 1062 days old, so UFO's 90D read the old contract in
the harness only). **Owed: a second live look — Socials → Holders both shapes, PTGC ⓘ and UFO ⓘ, Wide + Tall.** `sessions/2026-09-26.md`.

### Before that (end of 2026-09-25)

**2026-09-25, night: privacy scrub.** The owner's real name was in the git author field of 97 commits here and in X1-Validator-HQ's public handover; both histories were rewritten and force-pushed, so **commit IDs from 2026-09-08 on are new** (the ones in these notes were remapped). Rule: gotcha 33. **Later that night:** the Actions run records (public API, name frozen at trigger time + old SHA) were the leftover — 144 here, 896 in x1-prism, 4 in ToolBox, all deleted and re-scanned to 0 across all five repos. Details: `sessions/2026-09-25.md`, "Night" and "Night, part two".

**2026-09-25, close of day.** Everything below shipped and was pushed by Shaka through the day (last commit:
"PTGC Burned by UFO share card: supply line moved down a little"). Nothing is half-done. The only thing owed is
the usual live look on a phone: the cosmic Home (art fills the window, both charts jagged not smooth, DASHBOARD
pills, one BUY / SELL per card), then the four redone Socials cards with real numbers — Value Generated, Token
Allocation (both tokens) and PTGC Burned by UFO — in Wide and Tall. Full trail: `sessions/2026-09-25.md`.

**2026-09-25: new Home screen ("cosmic") — the classic one kept as a switchable backup.** Shaka's
gold/green alien art behind a metallic THE GRAYS / DASHBOARD title, two glowing token cards (price,
24 h change, contract + copy, Day counter, MCap, volume, PLS ratio, a real 24 h chart from
GeckoTerminal 15-minute candles) and ONE "BUY / SELL <token>" button per card (Shaka: not two) that
opens the existing switch.win `SwapModal` (**since 2026-10-04 the big button is ENTER DASHBOARD and BUY / SELL is the top-right pill**). Round 2 the same day: the art COVERS the window at any
shape (scaled, sides cropped, never stretched), 140px of faded headroom over the alien's crown that
only shows when the window is tall enough (`--oy`), buttons with the classic glow + light sweep, stat
tiles. **Also 2026-09-25: the Value Generated and Token Allocation share cards (both tokens) redone in the
Burn / Treasury build — `ValueGenSocialModal`, `AllocSocialModal`, shared `SocialNebulaBackdrop` +
`SocialShapeSwitch`; the 600x314 cards are gone; the UFO "PTGC burned by UFO" card too (`PtgcByUfoSocialModal`, fire build) — every
Socials card is on the 2026-09-23 pattern now.** **`HOME_DESIGN` (next to `UFO_MAINTENANCE`) = 'cosmic';
set it to 'classic' to go back** — or look at either on the live site with `?home=classic` /
`?home=cosmic`. Same loaders as before; only the view is new. Art in `logos/home/`. Details, checks
and the owed live look: `sessions/2026-09-25.md`. Gotcha 32.

### Before that (end of 2026-09-23, late)

**2026-09-23: DAO Buys share card in Socials (PTGC column, under DAO Treasury).** `DaoBuysSocialModal`
opens on the latest buy in the Latest-DAO-buy tile's look (gold frame, glow, metallic amount, Grays
creatures) with a gold switch above the card - Latest / 24H / 7D / 30D / 90D / All time (rolling
windows). A window with no buys says "No DAO buys in the past 24 hours" and points at the last buy.
Screenshot-only, like the PTGC Buys chart card (gotcha 30). Live since b525c0d77; round 2 live as 53e7c9407;
round 3 (opens on All time, Wide 16:9 / Tall 4:5 switch, local + UTC times, more room above the
card) pushed as 4650e95f5. **Evening: two more Socials cards redone, both live.** Burn Stats (PTGC + UFO) in a fire theme
(`BurnSocialModal`, 68cff6ee0, logos/label enlarged in 902b00ea7 + b0a46464d) and the PTGC DAO Treasury card in
a blue "vault" look (`DaoTreasuryModal`, bc7fb3376: Total DAO Value, breakdown bar, four tiles incl. Treasury
holdings = tokens over $50 with logos). Both Wide/Tall, screenshot-only, and both also open from their panel's
📷. The UFO "PTGC burned by UFO" card followed on 2026-09-25. Shaka checked all three on his phone, both
shapes, 2026-09-23: all good.

**2026-09-22: the affiliates page showed some viewers a dashboard of zeros — and it was never a
cache.** Shaka's viewers hard-refreshed, cleared caches and opened a months-unused browser, and
still saw 0.00, because nothing about it lived in their browsers. The page's HTML comes from this
domain; every NUMBER on it comes from one request to a second host (`ptgcapi...workers.dev`), so an
ad or content blocker, a filtering DNS, a VPN or a corporate proxy can answer that single request
with `200` and `{}` — which parsed, passed `res.ok`, and summed empty arrays into a complete,
healthy-looking `REFERRERS 0 / $0 / 0 PTGC` dashboard with no warning at all. A HARD failure
(blocked outright, or the 09-20 500) already reached the error screen; only the SOFT one lied.
The fetch is now `cache:'no-store'` + a per-load cache-buster, and the answer must have the shape
`getPublicCommissions` builds (`referrers` + `monthlyLogs`) or it throws — an empty PROGRAM still
renders its zero state, an empty ANSWER now says so, in words a viewer can act on. Deploy and data
were both verified healthy first (live page, live endpoint, DomDoos correct in every place).
**Part two, the actual cause of the zeros:** the morning's fix was real but was not their bug.
The Referrers Registry on the main page built three of its six numeric columns from the payload's
per-referrer summary block (`r.totalBuys||0` and friends) while computing the other three from the
monthly logs - two sources in one row. Live, 3 referrers read 0 with real buys, 41 more were wrong,
24 right. One `lifetimeByUser` map now feeds the Registry, the Leaderboard and the referrer card;
nothing reads that block any more (gotcha 29). The ALL-TIME tiles were always correct, which is
exactly why this hid. See `sessions/2026-09-22.md` Part two.

**Deployed and verified live** (`0251ed93a`, Pages 14:24:40 UTC): the affiliates page renders the
real payload exactly as before - Min Threshold $250, 71 referrers, 1,404 buys, $520,651, no `0.00`
anywhere - and the cache-busted request fires. **Open, waiting on one referrer's reply:** he was
asked to open the endpoint directly and answered "a ton of text", which does NOT clear the blocker
theory - content blockers filter what a PAGE fetches from another origin and leave a typed
top-level navigation alone, so both facts fit together. The two unanswered follow-ups and the
three-way decision tree they settle (real numbers / error screen / still 0.00 - only the third
needs work) are at the end of `sessions/2026-09-22.md`, along with the costed comparison of the
custom-domain move (needs a GoDaddy -> Cloudflare nameserver migration for the whole domain) versus
publishing the public projection into this repo and reading it from raw GitHub like every other
number. Details and the two screenshot tells: `sessions/2026-09-22.md`.

**2026-09-21: a60, a59, a61 and a53 — the wrong numbers on the pages other than index.html.**
The Ledger stops calling an inbound transfer a "buy" (80 such rows in the full files, incl. 265.1B
of Oct-2023 treasury funding; none inside today's 7-month picker), cuts its months at UTC midnight
(a Sydney viewer and Shaka disagreed about 5 of the 7 months on offer — proved with
`probes/ledger-digest.js`) and shows an amber banner past 8 h / "—" past 7 days when the treasury
feed stalls. Charts opens as the token you came from and labels daily candles in UTC (they were a
day early west of UTC). fetch-coingecko-data keeps the previous figure instead of publishing a
partial one and exits non-zero on a throw; lv-snapshot checks the status code and refuses to append
a zeroed row. token-allocation.json is age-gated (14 h label / 36 h ignore) and an unknown holder
count leaves "Squid & Below" as "—" instead of a cached 0. Harness: all five pages are scanned for
Tailwind classes now, charts.html's date adapter is served (its charts had been blank since a37),
`reload=` works on pages without `#root`, and `PS_COUNTERS_DOWN=1` exists. Details, evidence and the
owed live look: `sessions/2026-09-21.md`.

Roadmap: 97 of 126 items closed — 45 of the original 59 (u11 + u14 done 2026-09-16), 52 of the 67
Audit II items (a1–a4, a13; a10, a11, a25; a16, a22, a24, a48 — 2026-09-16; a14, a15, a17, a18,
a19, a20, a21, a23 — 2026-09-17, the honest-failure pass; a29, a28, a31, a30, a34, a33, a32, a38,
a35, a37 — 2026-09-17 evening/night, the pipeline week; a5, a6, a7, a8, a9 — 2026-09-18, the
calculators; a36 the same evening; a12 + a26 at night; a27 closed won't-do, a39, a42, a67, a40, a41
— 2026-09-20; **a60, a59, a61, a53, a54, a62, a51 and a52 — 2026-09-21, `sessions/2026-09-21.md`**). **2026-09-18 cadence check: GitHub runs the one hourly
workflow ~5×/day (gaps up to 5 h, all green) — stale thresholds raised instead (value-generated 6 h,
burn-summary amber 8 h). **2026-09-20: no code changed — the 09-18 deploys were verified on the LIVE
site (a5, a6, a8, a9 on calculators; a12 on portfolio; a36 on ledger; the 09-17 index.html pass's owed
look), all pass; a26 code-verified only, a7 not forceable live. One cleanup filed: `ptgc-ufo.com/data/*.json`
is published in `_site` but frozen at the last code deploy while every reader uses raw GitHub —
`sessions/2026-09-20.md`.** **Next: a43-a47, a49, a50, a55-a58, a63-a66 (15 left: a11y / mobile / cleanup /
calculators / Live Feed), in any order.**
u1 + u9 pushed as `b765a2f06` (2026-09-09); a header
tweak (`178a3a577`, PLS ratio / X's stats inline from 1024px) landed after the last
handover. 2026-09-13: **Buy/Sell button + switch.win widget modal built and live**; evening
u4 + u13; night **DAO Buys chart built, HIDDEN behind `DAO_BUYS_LIVE=false`** — entrance is
the faint gold dot top-right of the PTGC dashboard header (see `sessions/2026-09-13.md`).
2026-09-15: Buy/Sell modal width moved to rem — a viewer with a larger browser font size saw the
title clipped to "PTG" on a YouTube stream (gotcha 17, `sessions/2026-09-15.md`).
2026-09-16: **u14** — every localStorage key in the `LS` table (gotcha 18); **u11** — Live Feed rows
memoised, countdown/count-up in their own components, learned pools named; evening **Audit II** —
whole-repo deep dive, 67 items on the roadmap, no code changed (`sessions/2026-09-16.md`).
2026-09-14: **DAO Buys went LIVE** — "PTGC Buys" button left of Ledger in the DAO Treasury panel,
header dot and `DAO_BUYS_LIVE` gate removed; creature lines (`DaoCreatures`), Recent DAO Buys
ledger, screenshot-only share card, phone header Buy/Sell row (`sessions/2026-09-14.md`).
Check `git --no-optional-locks status` before starting.
2026-09-20: **live verification pass** — every 09-18 item confirmed on ptgc-ufo.com, so the a5–a9 /
a12 / a36 live looks are done; then **a27 closed as won't-do (owner: another site manages affiliate
commissions), a39 + a42 + a67, and a40 + a41 built and certified**; and **the Affiliates page was
found DOWN and fixed — the `ptgcapi` worker, not this repo** (`sessions/2026-09-20.md`).

| Area | Status |
|---|---|
| Phase 0 — wrong numbers / crashes (17 items) | **Done, live** |
| Phase 1 — dead code (b3), html2canvas removal (b4) | **Done, live** |
| Phase 1 — Vite build (b1, b2), icons/manifest (b5), fonts (b6), CI/CSP (b7), tests (b8), operator script (b9) | Not started — build deliberately parked by Shaka |
| Phase 2 — all data items (d1–d12) | **Done, live** (d10 and d12 closed as won't-do, see gotchas) |
| Phase 3 — share cards (u2) | **Done, live.** Socials cards on the 2026-09-23 pattern: DAO Buys, Burn, DAO Treasury (09-23), Value Generated, Token Allocation, PTGC burned by UFO (09-25), Holders + the Holders-box ⓘ (09-26), RH Core Liquidity (09-28, RH photo, Wide only), **Affiliates Report (09-29, leaderboard + clean All-Time bar), Combined Value Generated (09-29), Grays & Cores price (09-29, Wide/Tall)** |
| Phase 3 — clarity + mobile (u7, u8) | **Done, live.** Tier labels under the creature emojis deliberately NOT done (Shaka) |
| Phase 3 — loading shell (u12) | **Done, live** |
| Phase 3 — Modal wrapper (u1), a11y (u9) | **Done, live** (`b765a2f06`, 2026-09-09) |
| Phase 3 — u10 (rename Socials Hub) | **Dropped** — Shaka wants the tab name kept |
| Phase 3 — u4 (hoisted render-defined components), u13 (chart late-data) | **Done** (2026-09-13 evening) |
| Phase 3 — u5 (one Value Generated model), u6 (share-card parity) | **Done** (2026-09-14 night; `computeValueGen`, see gotcha 16) |
| Phase 3 — u11 (Live Feed render cost), u14 (versioned localStorage) | **Done** (2026-09-16; `DeckRow`/`DeckScanline`/`DeckPods`, `LS` table — gotcha 18) |
| Phase 3 — u3 (decomposition) | Not started — waits for the build |
| Phase 4 — product ideas (g1–g6) | Not started |
| Phase 4 — g7 Buy/Sell via switch.win | **Done, live** (2026-09-13; three commits, ticked on the artifact) |
| **Affiliates API (`ptgcapi` worker, outside this repo)** | **Was 500ing site-wide, fixed 2026-09-20 (worker v4).** GitHub's contents API stops inlining a file over 1 MB (`200 OK`, `"content": ""`), and `data/affiliate-commissions.json` in `ShakaVibe/ToolBox` grew past it — `atob("")` → `JSON.parse("")` → "Unexpected end of JSON input" → 500, which also killed the worker's own cron sync silently. v4 reads via `Accept: application/vnd.github.raw` (no ceiling) and writes compact JSON. Source: `handover/ptgcapi-worker-v4.js` — the ONLY copy outside the Cloudflare editor; deploy is dash.cloudflare.com → Compute (Workers) → ptgcapi → Edit code. Still latent: `btoa()` dies on a non-Latin1 username, and nothing prunes that file. **Cron: `0 8 * * *`, daily 08:00 UTC** (dashboard → Settings → Trigger events; index.html mirrors it in `AFFILIATE_SYNC_UTC_HOURS` — change both together). **Two things to know before trusting its timestamps (2026-09-21):** the sync writes to GitHub only `if (newTxCount > 0)`, so `monthlyLogs[m].lastSyncDate` is when the data last CHANGED, never when it was last checked — a quiet week leaves it a week old with nothing wrong; and `getPublicCommissions` builds `publicData` from `referrers`/`monthlyLogs`/`receipts` only, so the `lastAutoSync` the sync writes never reaches the page. A real "last checked" needs a heartbeat that does not re-upload the 692 KB file (KV, or a tiny separate file) — see `sessions/2026-09-21.md`. **2026-09-22: `jsonResponse` sends NO cache headers** — no `Cache-Control`, no `ETag`, no `Last-Modified`, verified live — so any proxy between a viewer and the worker may hold one copy of that body indefinitely with nothing able to revalidate it. Fixed 2026-09-23: worker v5 sends `Cache-Control: no-store` (verified live). Also still on `*.workers.dev`, a shared hostname this project does not control; a Workers custom domain (`api.ptgc-ufo.com`) would put the numbers on the same domain as the page. **2026-09-29: the write path was dead since the v5 redeploy** — `btoa()` on the em-dashes in four `voidReason`s (500 on `/write` and inside the cron); **v6** (`handover/ptgcapi-worker-v6.js`, `toBase64Utf8`) fixes it — deploy by hand, then Sync from ToolBox. The `btoa` "still latent" note above is that bug. |
| Wording — no "tax" anywhere on the site (Shaka, 2026-09-14) | **Done.** `taxRate`/`taxBreakdown` are now `feeRate`/`feeBreakdown`; the u7 "x% tax on every trade" line under Value Generated is gone. Keep it that way: write "fee" |
| Phase 4 — g8 DAO Buys chart | **Done, live** (2026-09-14). `DaoBuysModal` + `data/dao-buys.json` (hourly); "PTGC Buys" button in the DAO Treasury panel |
| **Audit II (a1–a67)** — Charts/Ledger wrong numbers, sibling-page hardening, index.html silent zeros, pipeline cadence + failure handling, a11y/mobile, cleanup | **52 of 67 done (a27 closed won't-do).** **2026-09-21: a52** — a long-open tab froze twice: the UFO "as of" labels stored the snapshot's age AT LOAD and printed it forever (they store `{at}` now and compute the age at render), and `volumeByPeriod` was written only in `load()`, so the Value Generated panel on 24H kept first-load volume while the header tile beside it climbed with every refresh (84,000 vs 378,000 in the harness). **2026-09-21 night: a62** Home fires its three fetches at once and only UFO's waits on `bootReady`, each card painting on its own data (`undefined` = loading, `null` = failed) — with a 6 s slow RPC the first card lands 3.7 s after mount instead of 8.7 s; only a UFO dashboard waits for `bootReady` now. **a51** the retry ladder's rung counter is state bumped after each attempt settles, so all four rungs fire (both ladders; it managed exactly one before), and a throw in `load()` past first paint no longer sets `loadError` — which `quickRefresh` read as "the first load failed" and answered with a full re-load, so every 5-minute tick flipped the page back to its skeleton, invisibly, forever. **2026-09-21 evening: a54** — the affiliates page's threshold is a WHOLE-MONTH total per referrer with the verdict on the entry (`runCommissionSync` STEP 4), and three places tested a per-buy `b.meetsThreshold` the worker never writes: the progress bar measures `entry.usdAmount / threshold` instead of unpaid-only, Pending Commission uses the entry's own rate, `thresholdType` is normalised once in `normSettings()`, `getEntryComm`/`getEntryCommUsd`/`isBelowThreshold`/`getEntryStatus` all defer to `meetsThreshold===false` (the ALL-TIME Commissions tile billed 41.60K where 40.00K is owed), the referral link is `encodeURIComponent`d, and every date on the page prints UTC with "(UTC)" on three headings. **2026-09-21: a60** Ledger — inbound PTGC with no outgoing DAO tx is a transfer, not a buy (it disagreed with the DAO Buys chart); month buckets and every printed time in UTC, heading marked "(UTC)"; amber banner past 8 h and "—" past 7 days from `lastUpdated`. **a59** charts.html seeds its token from `?from=`/`?token=`/`ptgc_last_token` (it always opened PTGC and bounced UFO visitors to the PTGC dashboard) and labels daily-tier dates in UTC; index.html links `./charts.html?from=${token}`. **a61** `fetch-coingecko-data.js` publishes the previous figure with a `carriedFrom` stamp rather than a partial one, appends no history point for an incomplete figure, and `process.exit(1)`s on a throw; `lv-snapshot.js` rejects a non-2xx and refuses to append a row with no pairs or no liquidity. **a53** `token-allocation.json` age-gated (label 14 h, ignored 36 h, stamped `asOfTs`) and `squidAndBelow` is null when the holder count is unknown. **2026-09-20 evening: a40** the four pair Swap scans run only under `DIAG` (`?debug=1` / `UFO_MAINTENANCE`) — 1,443 RPC calls instead of 2,055 on a stale-file UFO visit, same figures on screen; **a41** `rpcFetch` skips an endpoint for 30 s after it fails, rotates off a `-32005` rate limit, and marks pool exhaustion `transport:true` so `getLogsRange` fails at once instead of halving the range six times. **2026-09-20: a39** burn-summary's UFO section (the RETIRED contract) no longer reaches either fallback — `mcapFromPrice` prefers this session's on-chain `totalSupply − burned` (`liveBurnedCache`, filled by `fetchBurn`), then an `address`-stamped file section, then the starting supply; burn-summary's own `PTGCbyUFO` (PTGC's buy-and-burn leg) is cleared on load so a failed `ufo-ptgc-burns.json` reads as `oldMissing` instead of printing 4.30B unlabeled; **a42** one `creatureCount(value,unit)` (relative 1e-9) behind every tier counter — 0.3% is 3 sharks again; **a67** `fmtAbbr` picks its unit after rounding, `findBlockAtTime` widens on a failed low probe, the two share-card tier tables derive from `BURN_C` (`tierFraction`, `SHELL_CARD_PCT`), portfolio's Shell is the floor, calculators use index's UFO ATH rule (`ufoNewTokenAthCache` gone). **a27 closed** — another site manages commissions. **2026-09-18 night: a12** portfolio reflections scanned one wallet at a time on the RPC pool, pending / failed states, total only when every wallet resolved; **a26** ErrorBoundary `resetKey` + Try again. **2026-09-18 evening: a36** Ledger reads `data/treasury-recent.json` (859 KB, both wallets, 8 whole months, ledger fields only) with the four full files as fallback. **2026-09-18, calculators.html:** a6 RPC pool + `fetchBurn` null (circ. supply / every MCap "—", Rewards share never bag/1), a5 PLS price null + `dsOnePair` (no $0.00005 placeholder), a8 Rewards inputs saved on typing + per-token bags (no cross-token leak), a9 calculators stay mounted across a Switch (inputs kept, amber banner, `LiveBadge`), a7 token-switch race cancelled. 2026-09-17 night, pipeline: a29 one hourly workflow, a28 PulseScan paging, a31 fatal log chunks, a30 half-year burn files, a34 Ledger reads raw GitHub, a33 token-allocation builder null-on-failure + staking under PTGC, a32 ufo-ptgc-burns.json 3.1 MB → 295 KB (caches in ufo-ptgc-burns-cache.json), a38 Pages deploys `_site/` only (18 MB, no handover/tools), a35 Ledger summary dashes while loading, a37 Charts status describes the data's age. 2026-09-16: a1 Charts 24H window, a2 + a4 Ledger amounts, a3 coingecko d90, a13 SRI on all four sibling pages, a10 + a11 portfolio, a25 phone Live Feed header, a16 DAO panel dashes, a22 deck-reopen flag gone, a24 Holder Analytics null guards, a48 sub-price sr-only text. **2026-09-17 — the honest-failure pass, index.html only:** a14 DexScreener-outage fallback (null vol/txns/change, chain liquidity from reserves), a15 burn USD + allocation donut, a17 PTGC-burned-by-UFO pending/failed/oldMissing, a18 five share cards (`CardLoadState` overlay + Retry), a19 KPI compare card, a20 quickRefresh token guard (`tokenRef`), a21 partner-price null through the Value Generated model (`missing`), a23 deck windows from `computeValueGen`. **Not started:** a43–a47, a49, a50, a55–a58, a63–a66 |

### How a session goes
1. Shaka opens the task in the Claude desktop app with `~/Desktop/PTGC-UFO` linked (Add folder).
2. Claude edits in place (or writes via the device bridge), verifies with the headless harness
   described under Testing, and updates `handover/` + the roadmap ticks.
3. Shaka pushes: `cd ~/Desktop/PTGC-UFO && git add -A && git commit -m "…" && git pull --rebase && git push`.
   The `pull --rebase` is needed because the Actions bots commit `data/*.json` every few minutes.
   **Claude ends every round of work with that full commit line, message filled in** (Shaka,
   2026-09-14) — never "same as before".
   (Claude-side notes: run git in the linked folder with `git --no-optional-locks …` — a plain
   `git status` from the bridge leaves a `.git/index.lock` it cannot delete, and the next commit
   fails with "index.lock: File exists". Never run `rebase --continue` or anything that writes
   refs from the bridge either — it leaves `REBASE_HEAD.lock` / `packed-refs.lock` for Shaka to
   `rm`. If `pull --rebase` aborts with "local changes would be overwritten" right after a
   commit, it is the folder sync re-writing Claude's edits a beat late — wait a moment,
   `git status`, then `git rebase --continue`. When writing a file back a second time in one session,
   stage it from a NEW path under outputs/ — re-using the first path re-sent the first snapshot. The bridge REFUSES to write
   `.github/workflows/*` ("protected file") — edit those through a build script run on the Mac with `device_bash`, 2026-10-07.)
3b. **After his push, Claude checks the live site itself** (Shaka, 2026-10-07: "cant you check this stuff instead of asking me to").
   The built-in browser (the `Claude_Browser` tools) reaches ptgc-ufo.com from his Mac: Pages had deployed within ~3 min of
   `742b07829`. Verify the version tags (`h2.css?v=N`, `data-presets`), run the same checks the harness ran (JS in the page:
   tile = card numbers, window subtitles, Back targets, scrollWidth at the mobile preset, `gotoTab` scroll), screenshot the windows.
   Transitions do not advance while the pane is hidden (a cue with `data-on="1"` reads opacity 0 — force `transition:none` to read
   the true state). Only ask for his eyes on taste, never on "does it work".
4. If a pipeline script changed, run it once by hand: Actions → "Data Pipeline (hourly)" → Run
   workflow → `only=<step>` (step names are in the workflow's `only` description; `force=true`
   ignores the file-age gates). Since 2026-10-06 the steps run inside ONE workflow step
   (`scripts/pipeline-run.mjs`, three lanes) — a new script = a line in its `STEPS` + a place in a
   lane, and the file in the Commit step's list; the run page's job summary has the per-step table.

## Sources of truth for numbers

- **Prices / liquidity / volume**: DexScreener, with on-chain reserves as fallback.
- **Burn totals**: `balanceOf(0x369)` on chain.
- **Pipeline cadence (measured 2026-09-18, again 2026-10-06)**: GitHub delivers the hourly cron ~4–5×/day (gaps 2–9 h), every run
  green. The site's thresholds assume that: value-generated live-scan fallback after 6 h, burn-summary amber
  after 8 h. **Since 2026-10-06 the real hourly beat is meant to be the ptgcapi Worker's `7 * * * *` cron dispatching the
  workflow (worker v7 — deployed? see Next up -13); once it is, expect ~24 data commits a day.** The run itself is three parallel
  lanes (`scripts/pipeline-run.mjs`), ~6–7 min; the job summary table on the run page says what ran, skipped and failed.
- **PTGC burn windows (24H/7D/30D/90D)**: `data/burn-summary.json` (hourly, the burn-history step of `data-pipeline.yml`).
  The burn archive behind it is `data/ptgc-burns-<year>-h1|h2.json`, half-years derived from the date (a30) —
  never add a period to a list; a file past 80 MB logs a warning, GitHub refuses 100 MB.
  Shown with an amber "as of" label after 8 h, as "—" after 7 days.
- **UFO burn windows**: `data/value-generated.json` → `burnPeriods.UFO`, painted at once when under 7 d old
  ("as of" label, amber past 6 h); past 6 h a live chain scan runs behind them and replaces them (2026-10-01 —
  before that the file was used only under 6 h and the boxes sat blank through the ~55-call scan on most visits). `burn-summary.json`'s UFO section still describes the OLD contract
  (`fetch-burn-history.js` line 31) — never use it for UFO.
- **ufo-ptgc-burns.json** (a32): summaries + `byContract` + `rows` (v1 rows, last 91 days) — ~300 KB.
  The generator's full caches are `ufo-ptgc-burns-cache.json`; nothing on the site reads that.
- **UFO Value Generated**: `data/value-generated.json` (hourly, the value-generated step of `data-pipeline.yml`); the
  browser falls back to a live scan when the file is >6 h old.
- **Ledger rows**: `data/treasury-recent.json` (a36; hourly, written by the treasury step right after the four
  full `treasury-wallet*.json`) — both wallets, whole months back 8 months, only the fields ledger.html reads,
  `input` kept whole. The Ledger trusts it when `schema===1` and `since` covers the picker's oldest month,
  else falls back to the four full files (the source of truth), then PulseScan. New field on the Ledger →
  add it to `RECENT_TX_FIELDS` / `RECENT_TRANSFER_FIELDS` in the generator or the slim path won't carry it.
- **DAO Buys (PTGC)**: `data/dao-buys.json` (hourly, the dao-buys step of `data-pipeline.yml`, right after treasury;
  generator `scripts/build-dao-buys.mjs`, schema 2). Buys = wallet-sent, PLS-paid txs that
  delivered PTGC to one of the TWO DAO wallets (`WALLETS` in the script = `TOKENS.PTGC.daoTreasury`
  0xeeac…31e1 and `ADDR.DAO_WALLET2` 0x4407…6A34 — the second bought Oct 2023 → May 2025 and was
  added 2026-09-14; each buy carries `wallet`); priced from pair reserves at the buy's block
  (PLS/USD via `PAIR_WPLS_DAI`, PTGC via `PAIR_PTGC_WPLS`). Price line = same reserves on a
  block grid, extended backwards when an older wallet appears. No third-party API anywhere in it.
  Run the generator locally with `NODE_USE_ENV_PROXY=1` (Node's fetch ignores the VM proxy).
- **Charts page intraday (24H / 7D / 14D)**: `data/charts-intraday.json` (hourly, the charts-intraday step; generator
  `scripts/build-charts-intraday.js`, CoinGecko Pro — 14 d of hourly + 24 h of 15-min closes per token). The page paints from it
  and tops up live from GeckoTerminal (PulseChain) / public CoinGecko (majors); a file > 36 h old is ignored. Daily (1M–1Y) =
  `charts-data.json`, as before.
- **Human vs arb-bot volume**: `data/swap-volume.json` (hourly, step `swap-volume`; generator `scripts/build-swap-volume.mjs`): every
  PTGC / UFO pool's Swap events over 30 d, classed by the Swap's `sender` (known router / aggregator = human, other contract = bot),
  priced at the hourly close. Cache `swap-volume-cache.json` (compact trade rows + cursor) is not deployed.
- **LP Pairs 7-day volume curves**: `data/pair-volume-7d.json` (hourly, the pair-volume step; generator
  `scripts/build-pair-volume.mjs` — GeckoTerminal hourly candles per pool, 28 six-hour bins, `binStart` shared). A
  pool the file has no entry for is read live by the browser; a file older than 36 h is ignored. GeckoTerminal's
  candles are sparse (only hours that traded) — a bin nobody traded in is a real zero, never "unavailable".
- **PTGC burned by UFO** — always OLD + NEW contract, headline and period boxes alike (Shaka's
  explicit intent). Three sources, combined in `computePtgcBurnedByUfo` in `index.html`:
  v1 (retired contract) lifetime from `data/ufo-ptgc-burns.json` → `byContract.v1`;
  v2 (live) from the on-chain delivered scan + a checkpointed pre-window scan, with the file's
  `byContract.v2` as fallback.

## Gotchas — read before editing

00. **Addresses live in `ADDR`, supplies in `SUPPLY`** (top of the script, just before `TOKENS`).
   The older names (`WPLS_ADDRESS`, `UFO_WETH`, `LP_ADDRESSES`, `HARDCODED_UFO_PAIRS`, …) are
   aliases of it. Add new addresses there, not as literals.

0. **UFO's ATH is the ORIGINAL contract's on purpose.** The migration is the same token, so
   "X's to ATH" measures against `ATH_PRICES.UFO = 0.000113` (the pre-migration high) and the
   CoinGecko file carries no UFO ATH to override it. Do not "fix" this (roadmap d10 is closed).

1. **SRI hashes.** The `<script>` tags for React, ReactDOM, Babel and Chart.js carry
   `integrity` hashes — on ALL five pages since 2026-09-16 (charts also pins the date-fns adapter and
   html2canvas). Change a version → regenerate the hash on every page or the page goes blank:
   `openssl dgst -sha384 -binary file.js | openssl base64 -A`. Tailwind's play CDN cannot
   carry one.
2. **October 6, 2026 = UFO day 90.** Two things used to assume UFO was younger than 90 days
   (fee-timeline fallback, lifetime pTGC-burned). Both are fixed, but that date is the first
   real test of the fixes — check the UFO dashboard and the "PTGC Burned by UFO" panel that day.
3. **`burnPeriods` state semantics**: `undefined` = loading, `null` = failed, object = data.
   Never seed it with zeros; "$0" is a claim.
4. **`getLogsChunked(..., exactTo)`** — a scan whose end block is NOT the chain head must pass
   `exactTo=true`, or the last chunk is sent as `toBlock:'latest'` and silently extends to the
   present (found 2026-09-08 in the pre-window scan; would have double-counted after Oct 6).
   Same helper exists in both `index.html` and `build-value-generated.mjs` — keep them in sync.
5. **Share cards** all render through `ShareCardModal` (search for it). Card content is the
   child at its natural W×H; anything that must NOT be in the image goes in `controls`. The PNG
   is html2canvas (loaded on first click, SRI-pinned) rendering a clone with the scale transform
   removed — `data-share-wrap` is what the export looks for. Cross-origin logos (DexScreener CDN)
   can taint the canvas; the shell then shows a "take a screenshot" message instead of failing
   silently. The overlay is portalled to `<body>` so it can open from inside the KPI modal.
   **html2canvas is not the browser** (2026-09-14): it cannot do `background-clip:text` (every
   `metallic-gold` word became a solid gold bar) and draws text inside `white-space:nowrap` /
   `truncate` elements half a line too low, then clips it. `shareCardPng`'s `onclone` now flattens
   `.metallic-gold` to `#E8C044` and turns nowrap/truncate off inside `[data-share-wrap]` — so in a
   card, never rely on nowrap to hold a layout, and don't put a bordered pill around text (the box
   lands ~12 px above the text; the DAO Buys card shows its "4.6d ago" as plain text for that
   reason). Check every card change with `H2C=1` + `probes/share-png-real.js` (harness README). Sub-micro prices
   carry an `sr-only` full-decimal span (a48) that `onclone` strips inside `[data-share-wrap]` — keep
   that line if the export code is ever rewritten.
6. **`ufo-ptgc-burns.json` schema 2**: `PTGCbyUFO` is now the COMBINED total across both UFO
   contracts; `byContract.v1` / `byContract.v2` split it. The deployed `index.html` reads
   `byContract.v1` as the historical base. Do not deploy the new generator with an older
   `index.html`, or the headline double-counts v2.
7. **`Dashboard` is not keyed by token on purpose.** The Socials tab switches token and then
   opens a share modal on the same instance; a remount would drop the modal. The token-switch
   race is handled inside `load()` with `loadCancelled` guards instead.
8. **Testing.** There is no test suite yet (roadmap b8), but the harness is now in the repo:
   `tools/harness/` (README there). `npm run compile` compiles the `text/babel` block with the
   exact `@babel/standalone@7.26.4`; `node run.js <route> <w> <h> <out> [actions]` mounts the page
   in headless Chromium with the CDN scripts served from the pinned npm packages, Tailwind from a
   CLI build, and the data APIs stubbed (RPC, DexScreener, PulseScan; real `data/*.json`).
   Walk Home → PTGC → UFO → Live Feed → KPI, plus `RPC_DOWN=1`, `DS_DOWN=1` and `SLOW=9000`
   (loading-state) runs. **`npm run css` after editing ANY page's classes — since 2026-10-07 (c13) the
   SITE loads the committed `tw.css` (no Tailwind play CDN any more) and the same command writes it,
   minified, next to tw.out.css: a class with no rule in tw.css does nothing live. Commit tw.css with
   the page; bump `tw.css?v=` on the five pages when it changes (Pages caches 10 min).**
9. **Emojis are off limits.** The creature emojis (🔱🐋🦈🐬🦑🐚) and their layout are Shaka's; do not
   add text labels under them or restyle them (decided 2026-09-08 when scoping u7).
10. **Explainer copy lives in `EXPLAINERS`** (right after the `InfoTip` component). Add a new ⓘ by
   writing the copy there and dropping `<InfoTip label="…">{EXPLAINERS.x(token)}</InfoTip>` next to
   the term. `title=` tooltips are hover-only — don't add new ones for anything a phone user needs.
12. **Every overlay is a `<Modal>`** (MODAL SHELL block, just above the share-card shell). New
   pop-up → `<Modal onClose={…} label="…" className="z-50 flex items-center justify-center p-4 modal-overlay bg-black/80">`
   with the panel as the child (panel keeps `onClick={e=>e.stopPropagation()}`). Escape, focus,
   Tab-cycling, scroll lock, `role=dialog` and the body portal come with it — don't re-add them.
   Escape only closes the TOP layer (`MODAL_STACK`); `InfoTip` is on that stack too. Omit
   `onClose` for a modal the user must act on. `useDialog(ref,onClose)` is the hook if the
   overlay needs its own markup (only `ShareCardModal` does).
13. **Buy/Sell = the switch.win widget in an iframe** (`SwapModal`, URLs from `switchWidgetUrl`
   only; partner wallet in `ADDR.SWITCH_PARTNER`). Three things to keep in mind: (a) when the
   CSP (b7) lands it MUST allow `frame-src https://switch.win` and `connect-src
   https://api.dexscreener.com`, or the window goes silently black; (b) Escape does not close
   the window once the user has clicked inside the widget (cross-origin key events) — ✕ and
   backdrop do; (c) the widget URL params are from switch.win's builder, not their docs — if the
   widget ever opens un-themed / un-prefilled, they renamed a param. Claude's in-app browser
   pane paints third-party frames black; judge the widget in a real browser.
14. **Don't declare components inside a component** (u4). A `const X=()=>…` inside a render body
   is a new type every render → React remounts it (images re-request, state resets). Put it at
   module scope and pass what it needs as props. To check a hoist didn't lose a closure, run an
   acorn scope pass over `tools/harness/compiled.js` (the 2026-09-13 note has the script shape).
15. **DAO Buys chart** — live since 2026-09-14 via the "PTGC Buys" button (DAO Treasury panel
   header, left of Ledger; `aria-label^="PTGC Buys"` is the harness entrance). The preview dot
   and the `DAO_BUYS_LIVE` gate are gone. Its share card is screenshot-only (`ShareCardModal
   screenshot`) because html2canvas cannot paint metallic text.
   Dots sit ON the market line (`DAO_BUYS_DOT_AT='market'`); the price PAID is 3–14% higher
   (fee + slippage) and lives in the hover card and the stats. Modal + share card share
   `computeDaoBuysView` / `buildDaoBuysChartConfig` — change the chart there, not in JSX.
   `fetchFreshDaoBuys` scans the chain for buys newer than the snapshot on open — for every
   wallet in the file's `wallets` (topic[2] is an OR-list). The generator
   caches priced buys by hash and extends the price grid; if a buy's PLS/PTGC ever changes in
   the treasury files it is re-priced automatically. To rebuild from scratch, delete
   `data/dao-buys.json` and run the script (26 s). `removeLiquidityETH…` calls deliver PTGC to
   the wallet too — they are excluded (`excluded.lpRemovals`), never count them as buys.
   Creature rows (tile + ledger) come from `DaoCreatures` → `getBurnC` (top three tiers,
   starting supply); the ledger lists `view.buysAll` (lifetime), not the selected range.
16. **Value Generated has ONE model — `computeValueGen`** (module scope, after
   `computeValueGenBuckets`). The Dashboard builds `valueGenView` (selected window) and
   `valueGen7d` once per render and every surface prints those: panel headline + PTGC tiles,
   Value Generated share card, Combined card (`FeeBlock vg=`), KPI card (`valueGen7d` prop).
   `basis` = delivered | accrued | volume; `pending` = dash; `total:null` = "—". UFO is never
   volume × fee unless `estimate:true` (only the KPI compare card from the PTGC page, tagged
   "7D EST"). Per tile: `valueGenBucketUsd(vg,item)` (null → "—"). Don't add a fourth
   Value Generated calculation anywhere — extend the model. Tier counts on cards and panel:
   `tierCountLabel`. Card prices: `fmtPrice` via `Price`/`PriceEl`/`formatSubPrice`.
17. **Containers in rem, not px, when what is inside is rem.** Tailwind sizes text, gaps, logos in
   rem, so a viewer with a larger browser font size (Chrome "Large", macOS bigger text) scales all of
   it — a px-capped container then squeezes its columns. Found 2026-09-15: `SwapModal` at
   `max-w-[460px]` showed "PTG" on a stream; now `max-w-[28.75rem]`. Worse, `.metallic-gold` is
   `background-clip:text`, so an overflowing glyph is invisible, not overlapping — a metallic title
   that "loses a letter" is a width problem. Reproduce in the harness with
   `eval=document.documentElement.style.fontSize='20px'` before the click.
18. **Every localStorage key is in `LS`** (right after `SUPPLY`), versioned. New key → add it there
   with a `_vN` suffix, read it with `lsGet(key, shapeOk)` so a stale shape is ignored instead of
   rendered, and when the shape changes bump N and add the old name to `LS_RETIRED` (or a prefix to
   `LS_RETIRED_PREFIXES`) so `lsSweep()` removes it at boot. **Changing the disclaimer wording →
   bump `DISCLAIMER_VERSION`** or nobody is re-prompted. The `ptgc_last_token` / `ptgc_nav_tab` /
   `ptgc_nav_view` names are the handoff contract with calculators/charts/portfolio.html — don't
   rename them; read them with `lsTake` (read-and-clear). The harness pre-accepts the disclaimer by
   writing `grays_disclaimer_v1` — keep `run.js` in step if the version moves.
21. **The pipeline is ONE workflow** (`data-pipeline.yml`, a29, 2026-09-17). Nine crons asking for
   ~190 runs/day made GitHub delay every schedule event 4–5 h (Actions log: each "hourly" job ran
   five times a day, every run green). Don't add a new scheduled workflow — add a step to the
   pipeline, in data order, `continue-on-error: true`, its `id` in the "Report step failures"
   list, and its output file in the commit step's `git add` list. A step that should run less
   than hourly gets a `pipeline-gate.mjs` line (age of its file, not the clock). `data/*.json` is
   committed once per run as "data: hourly pipeline …". Measured 2026-09-18: GitHub delivers ~5 a
   day even for one workflow (gaps 2–5 h, all green) — the stale thresholds were moved to match
   (`VALUE_GEN_STALE_MS` 6 h, `BURN_HISTORY_STALE_MS` 8 h). The only way to real hourly runs is an
   outside cron hitting `workflow_dispatch` with a token (`sessions/2026-09-18.md`).
20. **Honest failure = null through, "—" out** (the a14–a24 pass, 2026-09-17). A read that failed or
   has not landed is `null` in state and in every helper's return — never 0, never `{total:0}`.
   `fmt` / `fmtUSD` / `fmtAbbr` print null as "—"; before multiplying by a price check `price>0`
   and print "—" otherwise. `fetchDex` marks an outage with `_fromChain:true` and null
   `vol`/`buys`/`sells`/`change`; `fetchStakingData` / `fetchBurn` / `fetchDAOData` return null.
   Value Generated: `computeValueGenBuckets` gives `byKey[k]=null` + `total:null` + `missing:[…]`
   when a price is absent — don't "fix" a null total by summing the known buckets. Cards whose
   numbers come from a second fetch use `CardLoadState` (loading / error + Retry, inside the card)
   and a loader function with an error flag, never a bare effect. Async work started for one token
   checks `tokenRef.current` before every setter (`Dashboard` is not remounted — gotcha 7).
   Test with `RPC_DOWN=1`, `DS_DOWN=1`, and `evalfile=probes/fetch-fail-all.js` after load.
19. **Live Feed pieces live at module scope** (`DeckRow`, `DeckScanline`, `DeckPods`, right after
   `DECK_POD_POS`). Rows are `React.memo` and never re-render, which is also why the dispatch
   animation can light `.deck-a.on` by DOM class — don't put anything that changes per render
   into a row's props, and don't move state that ticks (clocks, count-ups) back into the deck.
   `DECK_LOGS=n` gives the harness deck synthetic swaps; `REDUCED=1` tests reduced motion.
22. **calculators.html follows the same honest-failure rules as index.html** (a5–a9, 2026-09-18):
   `rpcFetch` is the three-endpoint pool, `rpcWord(r)` turns an `eth_call` into a hex word or null,
   `fetchBurn` / `fetchPLS` return `null`, `dsJson` + `dsOnePair` are the DexScreener readers (the
   `/pairs/` endpoint answers `pairs[]`, never read `.pair` directly). `burn===null` → `circulatingSupply`
   null → every MCap "—" and Rewards / Fresh Capital shares 0 — never `:1` or `||0` on a supply. The
   page stays mounted across a token Switch (`loadedOnce`; the full-screen gate is first-load only), so
   the token effect's `cancelled` flag must guard every setter you add to `load()`. Per-token inputs:
   save effects keyed on the value ONLY, load effect resets unsaved fields to '' — a `[value, token]`
   dep re-introduces the cross-token leak. Harness: `HTML=calculators.html` + `probes/calc-*.js`,
   `DS_UFO_PRICE` / `SLOW_UFO` for the race.
23. **portfolio.html reflections are a queue** (a12): `fetchPortfolioData` never scans; `fetchWalletData`
   queues the wallet on `reflQueue` (one scan at a time) with its `gen`. `ufo.reflections`: `undefined`
   pending, `null` failed (+`reflError`), number done — keep those three apart; the aggregate shows a total
   only when every checked wallet resolved. Anything that reloads or removes a wallet bumps `genRef` and
   calls `dropReflScans`. Harness needs `HEAD_BLOCK=27100000` for the scan to do anything.
24. **ledger.html is a UTC page** (a60, 2026-09-21). Month buckets, the picker, the default month,
   the `treasury-recent.json` window gate and every time printed on a row are UTC, and the summary
   heading says so — block timestamps are UTC seconds, and cutting at the viewer's local midnight
   made a Sydney viewer and Shaka disagree about 5 of the 7 months on offer. Don't reintroduce a
   local-time `new Date(y,m,d)` here. Staleness mirrors index.html's burn-summary rule because the
   same pipeline writes both: `LEDGER_STALE_MS` 8 h (amber banner above the summary),
   `LEDGER_DEAD_MS` 7 d (red banner and every tile "—"). And: a PTGC transfer INTO a DAO wallet whose
   hash has no outgoing DAO transaction is a `transfer` with a 📥 icon, never `ptgc_buy` — a buy is
   something the wallet paid for, which is what the DAO Buys chart counts. Folding them into
   Transfers was the cheap choice; a dedicated "Received" tile is a small edit if Shaka wants one.
25. **Pipeline scripts publish the previous figure, never a partial one** (a61, 2026-09-21).
   `fetch-coingecko-data.js` now marks each token's `complete:{volume,transactions,liquidity}`;
   anything not whole is written as the last run's value with a `carriedFrom` stamp, and the
   append-only history files get no point for it (one understated point is permanent — they are
   averaged per day). A fetcher that cannot answer returns `null`, never `[]`. `lv-snapshot.js`
   rejects a non-2xx and refuses to append a row with `pairCount === 0` or `totalLiquidity === 0`.
   Both `process.exit(1)` on failure, which the pipeline's "Report step failures" step turns red.
   The 20 zero-UFO rows already in `lv-snapshots.json` are 7–12 Jul 2026, from when the script
   pointed at the pre-migration contract — history, not failed fetches; left in the file, but both
   readers in `calculators.html` now share `lvRowUsable(s)` and skip a snapshot where either token's
   `totalLiquidity` is not > 0 before averaging per day (three of those days had been averaging to
   exactly $0 of UFO liquidity). **Open, and wider:** every UFO row before ~12 Jul 2026 is the
   pre-migration contract, healthy-looking ones included — reading UFO liquidity history further
   back than that is reading a different asset. Needs its own decision (see `sessions/2026-09-21.md`).
26. **The harness serves all five pages now** (2026-09-21). `tailwind.config.js` scans index.html
   *and* the four sibling pages — a class used only on a sibling page used to have no CSS here, so
   the screenshot lied about it. charts.html's `chartjs-adapter-date-fns@3.0.0` is served too; it
   never was, so every chart on that page was blank in the harness from a37 until now. `reload=`
   no longer waits for `#root` (charts.html has none). `PS_COUNTERS_DOWN=1` fails only PulseScan's
   `/counters` while the holder pages answer — the a53 case. Rebuild `tw.out.css` (`npm run css`)
   after touching ANY of the five pages, not just index.html.
27. **The affiliate threshold is a WHOLE-MONTH total per referrer, decided on the ENTRY** (a54,
   2026-09-21). `runCommissionSync` STEP 4: `entry.usdAmount` is the sum of every buy in that
   entry's month and `meetsThreshold = entry.usdAmount >= threshold`; the verdict is written to the
   entry and **never to a buy**. Any test of `b.meetsThreshold` is testing a field that does not
   exist — it reads as "true" and the guard around it never fires, which is how a below-minimum
   entry got billed for, badged UNPAID and told "Threshold Met". `getEntryComm`, `getEntryCommUsd`,
   `isBelowThreshold` and `getEntryStatus` all key off `e.meetsThreshold===false` now; keep it that
   way. Also: `e.commissionPtgc` is legitimately `0` for such an entry, so never `||` it.
   `thresholdType` is normalised to lower case once, in `normSettings()` — the API has sent "USD".
   Every date on that page is UTC (the data and the month keys are), and three headings say so.
29. **Nothing reads `referrers[x].totalBuys/totalPtgc/totalUsd`** (2026-09-22). The payload's
   per-referrer summary block is written unreliably by the worker - measured live, 3 of 68 active
   referrers had those fields MISSING (`r.totalBuys||0` then printed a clean 0 against a name with
   real buys, which is what viewers were reporting), 41 more were wrong and 24 right; the rot is an
   overwrite rather than an accumulate, so DomDoos' `totalPtgc` was exactly his February figure and
   his `totalUsd` exactly his March one against a real lifetime of 266 / 1.41B / $124,142.24. The
   Registry built three columns of every row from that block while computing the three beside them
   from the monthly logs. One `lifetimeByUser` map (memoised on `data`, just above `stats`) now sums
   `buysCount`/`ptgcAmount`/`usdAmount` per username, and the Registry, the Leaderboard and the
   referrer card all read it through `lifetimeOf(username)`. Only `wallet` and `addedDate` still
   come from `referrers[x]`. Do not add a second sum, and do not "fix" a zero by falling back to the
   summary block. The ALL-TIME tiles were always right because they sum the monthly logs - that is
   why the top of the page looked healthy while a row read zero. `Comm. Paid 0` (never paid) and
   `Pending 0` (fully paid) are CORRECT zeros; leave them. Probe: `probes/affil-registry.js` with
   `AFFIL_DATA=1`, whose fixture carries no `total*` and so reproduces the live shape for free.
28. **An empty ANSWER is not an empty PROGRAM** (2026-09-22). `AffiliatesPage` reads ONE endpoint
   on a host this repo does not control, and until now anything that parsed was rendered: `{}` from
   a blocker, a proxy or a filtering DNS became `REFERRERS 0 / $0 / 0 PTGC` with no warning, which
   is what three viewers were looking at while the site and the data were both perfectly healthy.
   The fetch carries `cache:'no-store'` + `?t=${Date.now()}` (the worker routes on `url.pathname`,
   so the param is ignored), the body is `JSON.parse`d inside a `try`, and the result must have
   `referrers` and `monthlyLogs` as objects or it throws to the error screen. `{}` and `{}` for
   those two IS a legitimate empty program and still renders the zero state — keep those two cases
   apart. Never relax the guard to "it parsed, so use it". Harness: `AFFIL_BAD=1` (or
   `AFFIL_BAD=<body>`) serves the malformed answer; the default stub is now a valid empty program,
   not `{"entries":[]}`. **The two tells in a viewer's screenshot of the old build: `Min Threshold
   $10` (normSettings' default, not the real 250) and `Last update unknown`.** Same question is
   unasked for every other third-party read on the sibling pages.
30. **The Socials DAO Buys card (`DaoBuysSocialModal`, 2026-09-23) is screenshot-only on purpose.**
   Checked with `H2C=1` + `probes/share-png-real.js`: html2canvas flattened the metallic gold, drew the
   frame's inset / negative-spread glow as hard boxes, and set every text line ~0.3-0.5em low, so the
   124 px amount landed on the creature row. The same low-text offset shows on the existing Burn Stats
   PNG in the harness (smaller type hides it). The view maths are `computeDaoSocialView` (pure; data =
   `fetchDaoBuys` + `fetchFreshDaoBuys`, same as the PTGC Buys chart); `DAO_SOCIAL_RANGES` holds the
   switch. Harness entrance: Socials -> `button:has-text('DAO Buys')`, ranges by `aria-label`
   ('Past 7 days', 'All time').
31. **The Socials share cards built 2026-09-23 share one pattern** - DAO Buys (`DaoBuysSocialModal`), Burn
   (`BurnSocialModal`), DAO Treasury (`DaoTreasuryModal`): module-scope components just above `DashboardSkeleton`, a
   `*_SHAPES` table for Wide 1200x675 / Tall 1080x1350, `ShareCardModal screenshot` with `toolbarClass="mb-6"`, and
   gradient text via `.metallic-gold` / `.burn-fire-text` / `.dao-blue-text`. They are screenshot-only because
   html2canvas cannot draw background-clip text, masks or SVG blur (gotcha 30). A card fed by the harness stub shows
   absurd numbers (a 33-sextillion treasury, every burn 5.00%); inject real-shaped data through a copy of index.html
   (`dao={window.__daoFake||daoData}` + `eval=`) to judge layout. Long figures: `money()` abbreviates past $10M and
   `fitFs` shrinks text to its box - keep both if a tile is added.
   2026-09-25: Value Generated (`ValueGenSocialModal`) and Token Allocation (`AllocSocialModal`) joined the pattern;
   `SocialNebulaBackdrop` (colour via `rgb` + `edge`) and `SocialShapeSwitch` are the shared pieces for the next one.
   2026-09-26: Holders joined it twice — `HoldersSocialModal` (both tokens, `HoldersDualBackdrop` gold/green) and
   `HoldersSingleModal` (one token, `SocialNebulaBackdrop` in `HOLD_THEME[token]`, what the Holders-box ⓘ opens; its
   toolbar has the 7D/30D/90D trend window). The trend is `HoldersSpark`, an inline SVG — no Chart.js canvas in a card any more; a
   canvas needed a mount-retry loop and never survived the shape switch. Tier counts print through
   `holdersTierCounts`: the seeded `{0,0,0,0,0}` is "unknown", never five zeros. A Mac renders these cards ~10 px
   taller than the harness (Apple Color Emoji, font metrics) — keep ≥ 25 px of slack per shape and check it with
   `probes/card-slack.js` after touching any *_SHAPES table.
32. **Home has two designs; `HOME_DESIGN` picks one** (2026-09-25). 'cosmic' (live) is `HomeCosmicView` /
   `CosmicCard` / `CosmicCardSkeleton` / `HomeSpark`, styled by the `hc-*` block at the end of the head
   `<style>`; 'classic' is the original JSX, still inside `Home` below the cosmic `return`, untouched.
   Both share `Home`'s state and loaders, so a data fix goes in ONE place and reaches both — never copy
   the loader into the cosmic view. `?home=classic|cosmic` overrides the constant per visit. Images must
   stay under `logos/` (the `_site` allow-list in `deploy.yml`, a38). The cosmic chart reads GeckoTerminal
   (`fetchHomeSpark`), refuses a series that ends >25% from the card's price, and falls back to the
   classic five-point sparkline — when the CSP (b7) lands it needs `connect-src https://api.geckoterminal.com`
   next to switch.win's `frame-src`. If a card's element sizes change, change `CosmicCardSkeleton` too
   (gotcha 11); it reuses the card's own classes so that is usually automatic. Harness: `GT_CANDLES=1`. Layout maths: `--bgw` (painted art width, `max(window width, height x 1.3196)`)
   and `--oy` (art shifted up by up to the 140px headroom band on short windows) — every vertical position
   in the `hc-*` block is `fraction * --bgw + --oy`; the art is 1536x1164 and the fractions assume it.

35. **Price a token with `dsPricePair`, never "the deepest pair" (2026-09-29).** DexScreener lists a token's pairs on
   BOTH sides — when the token is the quote (INC/UFO, pTGC/UFO) `priceUsd` is the OTHER token's price — and PulseChain
   has fake pools (WPLS/NananaX, WPLS/MULE, eHEX/NananaX, PLSX/MULE) claiming $1-2M "liquidity" with ~$0 volume, no
   `priceChange` and a stale price, which outrank the real pools. `dsPricePair(pairs, addr)` / `dsPriceOf` (next to
   `dsPairsFor`): base side only, pairs with real 24h volume (≥ $100 and ≥ 2 % of the busiest), deepest of those;
   PTGC / UFO take their dashboard main pair first, so every card shows the dashboard's price. `portfolio.html`
   (`pricePair`) and `scripts/fetch-burn-history.js` carry the same rule. Summing liquidity / volume over every pair
   is a different job and still sums them all.

41. **Build scripts are idempotent by `done_marker`, and prop names collide (2026-10-07).** `tools/audit3-p1.py` (and the pattern to
   copy): every `rep(old,new)` names a `done_marker` string that is present only after the edit; the script skips the edit when it finds
   it, so re-running on an edited tree prints "0 edit(s)" — the Mac check after every copy. Two things that bit while building it:
   (a) `HoldersSingleCard` already declares a local `today` (a date string) — a prop of the same name is a COMPILE ERROR ("Identifier
   'today' has already been declared"), hence `today24`; the 24 h holders number is `holders24h`, computed ONCE in `Dashboard` right after
   `const nhFile=useNewHoldersFile(...)` and threaded down — never recompute it in a card. (b) The harness action string splits on
   `;` — an inline `eval=` with a `;` in it breaks the parser; use `evalfile=probes/x.js`. Also: Babel's `data-presets="react"` is on
   every `text/babel` tag (c1) — a new page or a new `src=` tag without it compiles 5× slower (ES5 lowering of 17 k lines).

40. **Holders Details is one count on two surfaces (2026-10-02).** `data/new-holders.json` (hourly `new-holders` step,
   `scripts/build-new-holders.mjs`) lists every real wallet whose balance went 0 → above 0 (`in`) or back to 0 (`out`) over
   31 days, with block / time / tx, the current balance of every arrival (`balances`, read at `balAt`) and a departure's
   `had`. The script is incremental on `cursor.block` and classifies against EXACT `balanceOf` at the block before the range
   and at head — never by replaying transfers alone (reflections drift). Contracts (`eth_getCode`, cached in `contracts`)
   and the two DAO wallets are never holders here. A failed RPC read aborts the run (previous file stays): a half-scanned
   range would lose arrivals forever. In index.html everything is the HOLDERS DETAILS block above `DashboardSkeleton`:
   `fetchNewHolders` (null past 36 h), `nhView` / `nhNet`, `holdingTier` (top BURN_C tier reached, Shell floor),
   `NewHoldersModal`. **LIVE since 2026-10-04 (`NEW_HOLDERS_LIVE=true`).** `NEW_HOLDERS_LIVE=false` = the faint bottom-right dot (`NhDot`) is the only way in and the Holders
   tile keeps PulseScan's snapshot delta; `true` = no dot, the green-people icon (`img.h2-hd`) right of the tile's ⓘ (a "+" until 2026-10-04 round 3), and the tile's change line is the
   file's 24 h net (`nhNet`, "—" when the file is missing or stale). The window's NET must equal that line — they are the
   same function. **Schema 2 (round 3): exact balance at the block before the range and at every block a wallet traded in; a
   crossing of zero between consecutive states is the event — never replay Transfer values here (the fee leaves without a
   Transfer, a replay never hits zero). `DUST = 1n` = Shaka's "no floor"; `10n ** 18n` = the one-token floor he saw and
   declined. The window is per WALLET per period (`nhView`): first-event state vs last-event state; came-and-went = "In and
   out", listed, not counted. **Known and deliberate until go-live:** the box's PulseScan figure and the window disagree — on day one the
   box read "+5" while the window read 3 new / 0 left; every recipient in PulseScan's own snapshot window was checked on
   chain and exactly three wallets went 0 → >0, no pools, nobody left. PulseScan's counter is its indexer's number, not
   wallets. Shaka chose (2026-10-02) to leave the box on PulseScan until the flip rather than switch the line early. Don't make the box read PulseScan again once live, and don't list arrivals without departures: the
   numbers stop matching. Harness: `probes/nh-state.js` (README line); the file is served from `data/`.

39. **A gradient defined inside a hidden SVG does not paint** (2026-10-03). `H2Tri` (the change triangle) is rendered twice —
   desktop and phone banner — and both copies carried `<linearGradient id="h2ua">`; the desktop copy owned the id and is
   `display:none` under lg, so the phone triangle was invisible (the harness's 390 px dashboard render shows it; never seen
   live). Per-instance ids (`uid` prop; the phone row passes `'p'`) in index.html and h2-header.jsx; charts.html's static
   twin uses distinct ids by hand. Any new inline SVG with `<defs>` that appears in both layouts needs the same care.

38. **An image swapped under the SAME name needs a version query** (2026-10-01). GitHub Pages serves `logos/` with
   `Cache-Control: max-age=600`; Shaka overwrote the sea-creature art twice and kept seeing the old set. `SeaIcon` appends
   `?v=${SEA_ART_V}` — bump it when those files change; for any other art swap use a new file name (the `_site` allow-list
   serves `logos/**`, so a new name costs nothing) or add the same query. Never a silent overwrite.

36. **The dashboard header has two designs; `HEADER_DESIGN` picks one (2026-09-30).** 'classic' is the header +
   KPI strip JSX inside `Dashboard` (the `!hdrV2&&(<>…</>)` branches); 'v2' is `DashHeaderV2` + `KpiTilesV2` at module
   scope (above `DashboardSkeleton`), styled by the `h2-*` block at the end of the head `<style>`. Both read the SAME
   variables in Dashboard's render and call the SAME setters — a data fix goes in one place and reaches both; never
   copy a loader into the v2 components. Every v2 size is `calc(N*var(--u))`, N being the pixel measured on the
   2166-px-wide reference mock-up (`--u` = width/2166 rem-scaled, floor .47 at 1024 px; the phone layout under 1024 px
   uses width/390, cap 1.3) — change a size by changing N, not by adding a px value. The sticky tab row must stay a
   SIBLING of the banner wrapper (`position:sticky` ends with its parent). Sparklines are `H2Spark` on `useH2Series`
   (`H2_DAYS` = 30 days since 2026-10-01, one colour per token, peak lighting by `h2Peaks`; null → dashed flat line +
   "history unavailable" label — don't seed a shape; the figure is `H2Val`, which shrinks rather than ellipses). `lv-snapshots.json` (~370 KB)
   is read only under v2. The preview switch: `LS.HDR_PREVIEW`, `HeaderPreviewGate`, hashes only in the code, empty
   hashes = no switch; strip nothing else from the URL there (`?home=`, `?debug=1` must survive). Flip = one constant.
   `.h2 img{max-width:none}` stays: Tailwind's preflight caps every img at its box width, which squeezed the corona
   and the band copy (found live). **The panels under the tiles are a SKIN** (2026-09-30 afternoon): the classic
   `<section>`s stay and carry `p2` + `data-c` + hook classes only when `hdrV2`; `{hdrV2?<P2Bar/>:…}`-style swaps are
   the only markup forks. Style a v2 panel in the `p2-*` block, never by editing the classic Tailwind classes; a new
   number goes into the classic JSX once and reaches both. `AllocRingV2` must stay grey when any slice is null (a15).
   Harness: `eval=localStorage.setItem('grays_hdr_preview_v1','1');reload=5000` turns
   v2 on for a run; `probes/h2-imgs.js` measures the art images. **Since 2026-10-03 the h2-* CSS is `h2.css`** (root; index.html
   links it from the exact spot the inline block held, the `<style>` split around it — cascade unchanged) **and the sibling pages
   wear the same header**: `h2-header.jsx` (`SiteHeaderV2`, `H2TabBand`, `H2Coin`, `H2Btns`… loaded by calculators + portfolio as
   `<script type="text/babel" src>`; its pieces MIRROR index.html's `DashHeaderV2` — change both), a static twin in charts.html
   (`#hdrV2` + `h2Boot` / `h2ApplyTheme` / `h2ApplyValues`), `PortfolioHeaderV2` in portfolio.html. Each page has its own
   `HEADER_DESIGN` + the same preview flag. `?v=N` on the h2.css / jsx tags — bump when they change (Pages caches 10 min); `?v=3` since 2026-10-07 batch 3 (c28 / c29 moved `.tap` + the focus and reduced-motion rules into h2.css).
   The sibling pages' BUY / SELL and Live Feed go to `index.html?token=X&open=swap|feed` (App reads it into `takeBootOpen`,
   Dashboard opens the window on mount). Classic identity check for any page: `probes/dom-hash.js` on `<page>.orig.html` vs
   `<page>.html`. **Sparkline states (2026-10-03):** `undefined` = loading (solid pulsing baseline `.h2-spwait`), `null` = the
   dashed "unavailable" line — `useH2Series` only says null after its last retry; the candles are cached in `LS.H2_PX`
   (30 min). `probes/h2-spark-state.js` reads the seven states.

37. **LP Pairs under v2 is a TABLE with real per-pool curves (2026-09-30 night).** From 640 px up `LpTableV2`
   replaces the `LPRow` list (phones keep `LPRow` in the `p2-lprow` skin); classic is the untouched `else` branch and
   must stay byte-identical (`probes/lp-dom.js` on two builds, `cmp`). The section header is the classic markup with
   hook classes added as `${hdrV2?' p2-x':''}` — keep that form, a `${hdrV2?'p2-x':''}` with a space before it leaves a
   trailing space in the classic class string. Columns: to drop one under a breakpoint, hide the CELL and remove the
   column from `grid-template-columns` together — a hidden grid item takes no slot, so a `0` column shifts every cell
   after it one column left (found at 768). The curves come from `useLpVolSeries`: FIRST the pipeline's
   `data/pair-volume-7d.json` (`fetchPairVolFile`, `scripts/build-pair-volume.mjs`, hourly `pair-volume` step — one
   ~6 KB read draws every row at once; ignored past 36 h; a pool marked null there is dashed without a live try), and
   only for a pool the file lacks, `fetchPoolVol7d`: one GeckoTerminal hourly-candle call per pool through ONE queue at `LP_GAP_MS` (1.1 s — GeckoTerminal refused a 150 ms burst live:
   four rows, then 429s; 20 rows now fill in ~22 s, top first), cached 30 min per pool in `_lpVol` (module level) AND
   in localStorage (`LS.LP_VOL`), so a token switch or a reload draws every curve at once; 6-hour buckets, colour =
   second half of the week vs the first. `undefined` = loading dots, `null` = dashed "history unavailable" — a pool
   GeckoTerminal does not list (404) is null for the TTL — and GeckoTerminal's candles are SPARSE (only the hours
   that traded), so `_lpParse` bins the week itself with real zeros and never demands a minimum count (a week with no
   trade is the solid floor line, not dashed); a 429 / 5xx / timeout pauses the WHOLE queue (`_lpPauseUntil`)
   and the same pool is retried (`LP_MAX_TRIES`), staying "loading" until three 20 s hook rounds have failed. Never
   seed a shape, and never turn a refusal into a dash early — that is what Shaka saw. The rows print "—" for a missing read (a14); the ranks follow the
   sort and the under-$1K table continues them (`rankStart`). **The desktop section header is `LpHeaderV2` since
   2026-10-01 afternoon** — a `{hdrV2?<LpHeaderV2/>:(classic)}` fork, NOT hook classes any more (the band needed its own
   elements: figure tiles, icons, two-button All / RH Cores); the classic header and the phone header are the untouched
   markup. Its change lines are `lpVolChg` (the KPI tile's formula) and `useLpLiqChange` (lv-snapshots, 24 h), All only.
   `LpSpark` draws the 28 bins on a SQUARE-ROOT height (2026-10-01 afternoon — one outlier bin used to flatten the week;
   the data is untouched) as layered light; its colour is the row's volume change vs the day before (`up` prop; the week's halves only when that
   figure is missing), down = `#FF2E3B`. The volume change is DexScreener 24 h vs the curve's previous 24 h (two sources;
   null = no line).
   **Sorting is on the column headings since 2026-10-01 evening** (`LpTh`; the band's SORT toggle is gone) over the same
   `sortBy`/`sortDir` the classic header's buttons use; keys `valuegen` (= volume order) and `txns` exist only for v2. The
   **Value Gen** tile and column are volume × `cfg.feeRate` — UFO's fee is the live contract read (boot overwrites `cfg`), so
   "—" means the fee is unknown, never 0 %. The 24h % badge is DexScreener's PRICE change — heading "Price 24h", keep it so.
   Harness: `DS_PAIRS=burn` (real 30-pair list), `probes/lp-head.js` for the band,
   `GT_CANDLES=1` + `GT_POOLS=miss:<n>`, probes `lp-rows` / `lp-curves` / `lp-dom` / `lp-fit`. When the CSP (b7) lands,
   `connect-src https://api.geckoterminal.com` covers this too.

34. **The Live Feed is a skin over the deck (2026-09-26).** `AbductionDeckModal`'s animations find their targets by
   class and ref — `.deck-pod` (via `podRefs`), `.deck-ship`, `.deck-gen`, `.deck-cell[data-k] .deck-a`, `.deck-links`,
   `.deck-beamclip` — so restyle freely but keep those names and the `data-k`/`data-id` attributes. The sky is
   `.deck-sky` (430 px; `DECK_POD_POS` y-values are px inside it, x in %); the art is ONE jpg under `logos/livefeed/`
   (the `_site` allow-list) and UFO is a `hue-rotate` of it — don't add a green copy. Phone (≤640) rules live in the
   same `<style>` block: pods become a grid strip, rows become flex-wrap with `.deck-unit` hidden and `.deck-cell-n`
   shown. Test with `DECK_LOGS=n` at 1440 and 375, and `REDUCED=1`.

33. **Privacy: the owner's real name goes nowhere** (2026-09-25). This repo and `handover/` are PUBLIC on GitHub.
   Never write the owner's real name, email, Mac name or `/Users/...` paths into a file, a commit message, or a
   screenshot committed to the repo; he is "Shaka" / ShakaVibe. Git author must be `ShakaVibe
   <145924450+ShakaVibe@users.noreply.github.com>` (check `git log -1 --format='%an <%ae>'`). On 2026-09-25 97 commits
   (Sep 8-23) carried his real name as author; history was rewritten with git-filter-repo `--mailmap` and force-pushed,
   so every commit ID from 2026-09-08 on changed — the IDs quoted in these notes were remapped from
   `.git/filter-repo/commit-map`. X1-Validator-HQ got the same scrub.

11. **Loading is a shell, not a spinner.** `loading` in `Dashboard` only covers the first
   DexScreener/RPC round-trip. While it is true the header/nav render with `Sk` bars and the tab
   body is `DashboardSkeleton`; Home uses `HomeCardSkeleton`. Both skeletons copy the real
   containers' classes so nothing moves when data lands — if you change a tile's padding or line
   height, change the skeleton too (measure with `SLOW=9000` in the harness).

- **Cloudflare cron triggers can sit unbound (2026-10-06).** Both ptgcapi crons were listed in Settings → Triggers with "Next" times,
  yet Observability showed no scheduled events in 7 days and nothing fired — the daily sync included; the handler and the dispatch
  worked when triggered by hand (`/__scheduled?cron=7+*+*+*+*` from the editor's HTTP tab). A redeploy did NOT help. Deleting both
  cron rows and adding them back did: the next :07 fired. Tell-tale: a "Next" time already in the past on the Triggers page.

## Next up (in order)

-24. **AUDIT III batch 5b (2026-10-07) — ON THE MAC, NOT PUSHED; commit line in `sessions/2026-10-07.md`.** c15: the 16 plates
   + 3 trophies as WebP and `logos/ptgc|ufo/logo-512.webp` for `TOKENS.*.logo` on every page, references swapped by
   `tools/audit3-p5b.py` (the Logos windows' download entries keep the PNG/JPG originals). Still JPG: the header set (dash-bg,
   tabs-bg — preloaded), bg-burn, cosmic-ground; the Logos thumbnails (P-9). Live look after the push: the plates on each surface,
   the trophies, the logos on a phone.
-23. **AUDIT III batch 5a (2026-10-07) — PUSHED `685bad0b4`, live-verified by Claude on every page.** c13 the play CDN →
   `tw.css?v=1` on all five pages (RULE: `cd tools/harness && npm run css` after any class change, commit tw.css; bump `?v=` when
   it changes); c12 `{cache:'no-cache'}` on the repo data reads (index 12, calculators 3, ledger 6), the NH re-read paused while
   hidden; c14 the boot shell in `#root` + preload of the three header images on dashboard routes. Live check after the push:
   every page styled as before, no cdn.tailwindcss.com request, 304s on a second load, the shell for a beat. Open: boot-fetch
   parking, CDN onerror fallback; batch 5b = c15 (the WebP pass + 512 px logos).
-22. **AUDIT III batch 4 (2026-10-07) — PUSHED `468c308a5`; the 20:07 run's check pending (Claude).** The pipeline: thresholds
   for the hourly beat (c17; VALUE_GEN_STALE 3 h, the ambers 2.5 h, alloc 8 / 24 h, cgFresh 12 h), the fallback cron at :37 that stands
   down when the last run is < 45 min old (c18), `data/pipeline-status.json` + ⚠️ carried steps in the job summary (c20),
   value-generated last in its lane (c19), PTGC `ath` written + readers take the max, lastUpdated at save, atomic save (c22).
   `tools/audit3-p4.py` — run it ON the Mac for the yml. After the push: the :07 run's job summary, the status file on the site,
   `PTGC.ath` in coingecko-data.json. Open from this batch: the value-generated checkpoint cache, the atomic-write helper for the
   other 24 writers, lv-snapshot's gate (needs c16 first).
-21. **AUDIT III batch 3 (2026-10-07) — PUSHED `742b07829`, live-verified by Claude (Current state).** c9 (Calculators ← to the
   dashboard, Affiliates Back to the token it came from, Ledger Back stays on site), c31 (a tab switch scrolls back to the band),
   c28 (`.hit` 32 px boxes on the small controls; `.tap` / focus rules now in h2.css; the tile badges only +6 px wide — a real 32 needs
   wider spacing, his call), c29 (reduced motion on every page, focus rings on the calculators / portfolio inputs). h2.css +
   h2-header.jsx `?v=3`. `tools/audit3-p3.py`, probe `c-p3.js`. Open for Shaka's taste only: the tile badges' spacing (c28).
-20. **AUDIT III batch 2 (2026-10-07) — PUSHED by Shaka `d8b1c6a2f`; live-verified.** c23 (honesty pass II:
   LP rows + band "—" for chain pairs / outages, Socials RH card "—" per missing core, KPI 30D burn USD, fetchDex mcap null-through),
   c24 (Volume window foot: three sources named), c26 ("largest pool per core" wording — the sum is the alternative), c27 (UTC day
   labels on the HvB chart, "UTC days" on the Volume window). `tools/audit3-p2.py`, probe `c-p2.js`. Live look after the push: LP
   Pairs band + rows, the RH window's subtitle, the Volume ⓘ foot, the HvB chart dates.
-19. **AUDIT III P1 batch (2026-10-07) — PUSHED by Shaka `d60b83082`; live-verified.** c1–c8 + c11 + c25 via
   `tools/audit3-p1.py` (idempotent; re-run prints "0 edit(s)"). Verified in the harness: PTGC 390 scrollWidth 390; charts.html 390
   cues + centred tab; holders tile = KPI = card; Leagues RPC_DOWN "—"; Combined Burn card whole at 810; calculators RPC_DOWN
   "UNAVAILABLE"; normal calculators still LIVE. Probes `c-p1.js`, `c-holders.js`, `c-cb.js`. Ticked on the roadmap artifact. After his
   push: the live look (load speed, phone PTGC, tab band on a phone, the 24 h holders line on three surfaces, the Combined Burn card
   footer). If anything regresses: `git revert` that one commit — the script is the whole change.
-18. **AUDIT III (2026-10-07) — c1–c65 in `sessions/2026-10-07-audit.md`, PUSHED `822e2a78e`, on the roadmap artifact (AUDIT III
   phase).** Batches 1–5b shipped on the day (see -19 … -24). Remaining: c10 (needs a wallet test), c16, c21, c30 → the look list
   c32–c37 → platform c38–c43 → product c50–c65.
   Done: c1–c8, c11, c25 (-19); c23, c24, c26, c27 (-20); c9, c28, c29, c31 (-21); c17, c18, c19, c20, c22 (-22); c12, c13, c14 (-23);
   c15 (-24). Left: c10 (needs a wallet test), c16, c21, c30, the look list c32–c37, platform c38–c43, product c50–c65.
-17. **Socials → RH Core Liquidity rows for PTGC / UFO (2026-10-07) — PUSHED by Shaka (`2c3d15d4c`), live look owed.** `tools/rh-socials.py` after rh-cores.py;
   probe `probes/sh-rh.js`. Live look: Socials → PTGC column → RH Core Liquidity opens the window on PTGC, Close returns to the hub; same for UFO.
-16. **The RH Cores window (2026-10-07) — PUSHED by Shaka (`1119ec37f`), live look owed.** The live look: the Liquidity
   tile's RH on PTGC and UFO (the plate, the hero + share bar, the stacked bar, the six rows with real DexScreener logos, the links), a
   phone. Build = `tools/rh-cores.py` after `tools/volume-window.py`; design `design/rh-cores/README.md`; probe `probes/rc-state.js`.
   Not built (ask): a PTGC / UFO switch inside the window; the token amounts in each pool.
-15. **The Volume window (2026-10-07) — PUSHED by Shaka (`43fb8af46`), live look owed.** The live look: the Volume tile's ⓘ on
   PTGC and UFO (the big coin, the four tiles, the bars, the chart on 7D / 30D / 90D, By pool + "show all"), a phone. Build =
   `tools/volume-window.py` on a clean index.html; design `design/volume-analytics/README.md`; probe `probes/vw-state.js`. Not built
   (ask): a USD / TOK toggle, a 📷 share card, a 24H view with hourly bars.
-14. **HUMANS VS BOTS (2026-10-06) — LIVE, pushed `6073ad2a5`; his live look + the Telegram post are the next steps.** Volume tile bot
   icon → `VolumeSplitModal`; the 📷 share card + the Socials rows; tile badges in the token colour. Actions → Data
   Pipeline → Run workflow → `only=swap-volume` if the live file is still schema < 3 (the window accepts any schema ≥ 1, the
   builder's first schema-3 run rebuilds 90 d in ~100 s), then his live look + the Telegram post. Owed: the TXNS 24H tile fix (his
   yes), the banner robot re-export (optional), a phone look at the card. Design + method: `design/volume-split/README.md`,
   `mock-share-v1.html`; build scripts `tools/volume-split.py` (+ the round edit scripts in `_to_delete/hvb-round*.py`, applied),
   `tools/hvb-share.py`. The TXNS 24H tile: CLOSED 2026-10-07, nothing to fix (see Current state).
-13. **The Actions review (2026-10-06 afternoon) — PUSHED 13:40; worker v7 DEPLOYED 14:00 but its cron has NOT fired (see Current state); one decision open.**
   (a) **Deploy worker v7** (`handover/ptgcapi-worker-v7.js`) so the pipeline really runs hourly: GitHub → Settings → Developer
   settings → Personal access tokens → Fine-grained → Generate: owner ShakaVibe, "Only select repositories" = PTGC-UFO-Dashboard,
   Repository permissions → **Actions: Read and write** (Metadata comes with it), a long expiry; Cloudflare → Workers → ptgcapi →
   Settings → Variables and Secrets → add secret **`DISPATCH_TOKEN`**; paste v7 into the editor → Deploy; Settings → Triggers →
   Cron Triggers → add **`7 * * * *`** (keep the existing sync cron). Check: at the next :07 the Actions list shows a "Data Pipeline
   (hourly)" run with event `workflow_dispatch`; the Worker's log says "dispatch: Data Pipeline started". Until then GitHub's own
   schedule keeps delivering ~4 runs a day. (b) After the push, watch the first pipeline run: three lanes in one step, the job
   summary table at the bottom of the run page, ~6–7 min; pair-volume's file `source` should read "CoinGecko Pro on-chain".
   (c) **Decision**: move the bot's data commits to an orphan `data` branch (pages read `raw.githubusercontent.com/…/data/data/…`),
   which ends the `pull --rebase` collisions and keeps `main` code-only — say the word and it is a session. Optional after that:
   checkpoint value-generated's 90-day rescan. Review notes: `sessions/2026-10-06.md` "Afternoon".
-12. **Charts round 3 + speed (2026-10-06) — PUSHED by Shaka 13:21; his full pipeline run at 13:22 built the intraday file.** Owed: the live
   look (24H / 7D / 14D switching, HEX on 24H, the badge, UFO-green titles on Charts / Calculators / Socials, Mac + phone). Watch the
   `charts-intraday` step's first runs (~1 min, 26 CoinGecko calls); the page ignores a file > 36 h old. **2026-10-07 after ~07:30 PDT =
   the real UFO day-90 test** (`sessions/2026-10-06.md`, "UFO day 90"). Builds: `tools/charts-v3.py` then `tools/charts-fast.py` on a
   charts-gt.py'd charts.html.
-11. **Calculators + Charts pages (2026-10-05) — PUSHED (`318957448`), live look owed** (Mac + phone). Charts = `tools/charts-v2.py` then `tools/charts-gt.py` (the GeckoTerminal back-off + daily fallback). After the push: 14D on WPLS + HEX again — hourly candles if GT answers, "daily candles" if it refuses; never two points for a fortnight. Build = `tools/calc-v2.py`
   on a clean calculators.html; design `design/calculators/README.md`; icons `logos/calculators/ic-*.webp`, plate `calc-bg.jpg`.
-10. **KPI Report tab (2026-10-05) — PUSHED (`318957448`), seen live on the Mac (two rounds of notes done); owed: a phone; the full-size backgrounds
   (`logos/kpi/`, new names or `?v=`); the 📷 share image (`TwitterCard`) in the new look if he asks. Build = `tools/kpi-v2.py`
   on a clean index.html (`kpi-v2.css` + `kpi-v2.jsx` are its parts); design `design/kpi/README.md`.
-9. **Socials Hub redesign (2026-10-03, second session) — BUILT and PUSHED (`6786b4af0`), live look owed.** Now: ptgc-ufo.com → Socials
   on the Mac (sky, title, three columns, every row opens the same card as before), then iPhone + iPad (one column). Then the
   full-size icon sheet from Shaka → replace the 18 cut icons in `logos/socials/hub/` (same names). `_to_delete/hub-sky-top.jpg`
   in the repo root is mine to lose — he bins it. Design: `design/socials-hub/README.md`; build: `tools/socials-hub.py`.
-8. **Holders Details (2026-10-02, hidden behind the dot) — NEXT: build the share card from `design/holders-details/mock-share-v2.html`
   (Wide only; single-token A2 + combined C; camera right of the period chooser), then his phone look, then the go-live word.** Rounds 1–7 pushed;
   round 8 + mock-ups on the Mac. After his push: the first hourly run continues the file from its cursor (watch the `new-holders` step
   once in Actions; `only=new-holders` reruns it alone). Go-live = `NEW_HOLDERS_LIVE=true` in index.html (gotcha 40) — the
   "+" beside the Holders ⓘ is a plain glyph for now, he may want it drawn; the dot is 16 % in `NhDot`. Not built on
   purpose: a share card, a live top-up for the hours since the file.
-7. **DONE 2026-10-03 — FLIPPED (step 4). Left: the post-deploy check (above) and the pre-flip leftovers (-5) which are now post-flip polish.** Was: GO-LIVE (Shaka, 2026-10-02: "when we come back we need to start preparing to make it live") — the ordered plan is the
   end of `sessions/2026-10-02.md`: live look (Mac, iPhone, iPad) → sibling headers (-6) → pre-flip leftovers (-5) →
   `HEADER_DESIGN='v2'` in FOUR files (index, calculators, charts, portfolio) + push → post-deploy check (both dashboards,
   Home, sibling pages, Live Feed, phone, the BUY / SELL and Live Feed jumps from the sibling pages). The classic branches stay
   until he has lived with it. (2) is DONE 2026-10-03, hidden; its live look is owed.
-6. **DONE 2026-10-03 (built, hidden behind the preview switch, owed the live look) — was: the sibling pages still wear the OLD header (Shaka, 2026-10-01: "make sure you make a note").**
   Now: `h2.css` + `h2-header.jsx` + the forks in the three pages; the flip = `HEADER_DESIGN='v2'` in FOUR files
   (`grep -n "const HEADER_DESIGN" *.html`). Ledger keeps its own bar (Shaka). The original note, for the record:
   `calculators.html` and `charts.html` (and `portfolio.html`; `ledger.html` has its own bar) carry the classic sticky
   header + nav from before v2. When `HEADER_DESIGN='v2'` goes live, those pages must get the v2 look too — the art
   banner is index.html's, but at minimum the black-framed gold tab band (`.h2-tabband`, `logos/header/tabs-bg.jpg`,
   the fire-light pill on the active tab, no "Updated" badge) and the same token · price line — or a visitor steps from
   the new dashboard into the 2025 header on every Calculators / Charts click. Do it in the same push as the flip, or
   the flip waits. Not started; parked by Shaka until go-live.
-5. **DONE 2026-10-01 afternoon: the Value Generated tiles, the LP Pairs header and rows (rounds 16–18); evening: the Live Feed badge (B) + the volume line beside the Value Generated total (round 19).** Next session:
   whatever Shaka brings (he usually has a mock-up — ask), then the rest of this item, which is where
   2026-09-30 left it: the dashboard page under v2 (header, tiles, panels, LP Pairs) — clean-ups were the whole of
   2026-10-01 (`sessions/2026-10-01.md`), the LP Pairs table has not been touched since 09-30. Six live rounds on the LP Pairs
   table today ended "sweet"; the pipeline file feeds its curves. Then, before the flip: (a) phone + iPad for the
   panels AND the pairs (only the Mac has seen either), (b) the DAO Treasury's fourth tile repeats the
   headline total — keep or replace, (c) DONE 2026-10-02 (`left-0`), (d) when he says so `HEADER_DESIGN='v2'` + push = live for everyone; the classic branches can be deleted
   once he has lived with it. Optional: a slim `data/kpi-history.json` from the pipeline instead of the 370 KB
   `lv-snapshots.json` for two sparklines; a `data/pair-history.json` would let the LP curves paint at once instead of
   over ~5 s (Shaka chose the live GeckoTerminal read for now).
-4. **After that: the Combined Burn Stats card** — Socials → Combined → 🔥 Combined Burn Stats,
   the last old-style card there. Same routine as the other redos: mock-ups first (Shaka's taste this week: "pop but
   clean", no heavy glow, no art backdrops, no rays, white titles, plain coloured moves not pills, emojis welcome but
   not beside the token names), then module-scope modal, Wide/Tall, screenshot-only, honest-null loader, and its
   other-token price through `dsPricePair` (already wired). Before building, a 10-second look at the portfolio page
   (PLS ~4 % lower than before the 5075cb8a9 push, UFO = the UFO dashboard).
-3. **2026-10-06 — UFO day 90** (item 5 below): check the UFO dashboard and the combined cards' 90D once UFO has a
   full 90-day window.
-2. **Affiliates (2026-09-29): worker v6 deployed and verified live** (171 September buys, retry queue landed the 31). The phone/tablet layout pass was seen live by Shaka the same day ✓ (`sessions/2026-09-29.md` "Afternoon"). Before that, 2026-09-22: closed. The referrer will not answer; nothing more to chase. Worker **v5 deployed 2026-09-23** (`handover/ptgcapi-worker-v5.js`,
   v4 + `'Cache-Control': 'no-store'` in `jsonResponse`); verified live with `curl -sI … | grep -i cache-control`
   -> `cache-control: no-store`. v5 is now the only copy outside the Cloudflare editor.

-1. **Audit II, top of the list:** cadence measured and thresholds moved 2026-09-18 (done — ~5
   runs/day is the new normal; a30/a32 migrations verified in the first scheduled run). Calculators
   a5–a9 done the same day, a36 the same evening, a12 + a26 at night. **All of those live looks are now
   DONE — 2026-09-20, on ptgc-ufo.com, nothing to re-check** (`sessions/2026-09-20.md`): PLS ratio 0.59 /
   3.81, MCaps real, the amber "Loading PTGC data… your inputs are kept" line instead of the gate, a typed
   bag saved per token and surviving a reload, portfolio reflections "scanning" → 3.93M with no zero
   standing in for an unknown, the Ledger on one `treasury-recent.json` request for both September and the
   oldest month offered. Still unexercised live: a26 (code-verified only), a7 (the race), and every
   failure path — they stay harness-only until something actually breaks. **a39 / a42 / a67 built the
   same day (`sessions/2026-09-20.md`); after that deploy, a 30-second live look: UFO's "PTGC BURNED BY
   UFO" headline should still read ~4.74B / 1.42% (if it reads 157.76M with "Old-contract history
   unavailable", `ufo-ptgc-burns.json` is not loading on the live site), and the creature row under a
   burn figure should no longer end in a run of ×9s.** a40 + a41 followed the same evening. **2026-09-21 closed a60, a59, a61 and a53** — none of it seen
   live yet; the 60-second look it is owed is at the end of `sessions/2026-09-21.md`, and the two
   pipeline scripts want one manual run each (Actions → Data Pipeline → `only=coingecko`,
   `only=lv-snapshot`, `force=true`). **19 Audit II items left: a43–a47, a49–a52, a54–a58, a62–a66**
   — a11y / mobile / cleanup / calculators / affiliates, in any order. Optional: `charts.html` `STATUS_STALE_MS` 2 h → 6 h if the
   permanent amber "as of" on the Charts page grates. Ordered list on the artifact's "Next up". Done 2026-09-16: a1–a4, a13, a10, a11, a25, a16,
   a22, a24, a48; 2026-09-17: a14, a15, a17–a21, a23 (honest-failure pass — after deploy, a
   30-second live look: PTGC header change line, UFO Value Generated headline (should be a number,
   not "—" — if it dashes, a partner price lookup is failing on the live site, see the note in
   `sessions/2026-09-17.md`), and the Live Feed on UFO still seeds its pods). If the 09-16 deploy
   has not been eyeballed: charts.html 24H (PTGC and BTC series should both start ~24 h back) and
   run `fetch-coingecko-data` by hand so the corrected "90D" lands.
   Note a38: `handover/` (this file) is public and deployed — move it before adding anything sensitive.

0. **DAO Buys chart (g8) — LIVE 2026-09-14.** Still worth a look after a few hourly
   `fetch-treasury` runs: `data/dao-buys.json` `generatedAt` should keep moving and the buy
   count stay 211+ (the Action step is `continue-on-error`, so a failure only shows in the
   workflow log). Tick g8's follow-ups on the roadmap artifact if Shaka wants them tracked.
0b. **Account hardening** - dropped from the list by Shaka (2026-09-23).
1. **Buy/Sell (switch.win)** — done and live (2026-09-13, g7 ticked). Shaka connected a wallet
   and bought in-frame; the Switch founder has been told about the embed. Optional follow-up
   left: a compact Buy/Sell in the phone sticky bar (`sessions/2026-09-13.md`).
2. **Live check of u1 + u9** (30 seconds): on the phone open any ⓘ modal, the page behind must
   not scroll; on desktop, Tab through the header and Escape out of a modal — focus should land
   back on the button that opened it.
3. **Phase 3 leftovers** — only u3 (decomposition) left; it waits for the build. Live check of
   the 2026-09-16 Live Feed in a real browser: open it on PTGC, watch a lift land, confirm the
   pod cells light and the "next scan" countdown ticks; on a reduced-motion device the cells
   should be lit from the start.
4. **Vite build (Phase 1)** when Shaka says go. Hosting is GitHub Pages (`deploy.yml`), so the
   decision is Pages-from-`dist` vs a `gh-pages` branch. Do b3-style cleanup first; everything
   in Phase 3 gets easier after it.
5. **October 6, 2026** — UFO day 90. Check the UFO dashboard and the "PTGC Burned by UFO" panel
   that day (both of the fixed 90-day bugs get their first real test; the `exactTo` bug found
   in dry-run would have shown up here too).

## Session log

- `sessions/2026-10-07.md` — the Volume window (mock v1 → built, `tools/volume-window.py`, pushed `43fb8af46`) and the RH Cores window
  (mock v1 → built, `tools/rh-cores.py`, pushed `1119ec37f`), the hub's RH rows (`tools/rh-socials.py`, pushed `2c3d15d4c`); Audit III (→ `2026-10-07-audit.md`, pushed `822e2a78e`, roadmap AUDIT III phase); the P1 batch c1–c8 + c11 + c25 (`tools/audit3-p1.py`, pushed `d60b83082`); batch 2 c23 + c24 + c26 + c27 (`tools/audit3-p2.py`, pushed `d8b1c6a2f`); batch 3 c9 + c31 + c28 + c29 (`tools/audit3-p3.py`, pushed `742b07829`, live-verified in the browser); batch 4 the pipeline c17 + c18 + c20 + c19 + c22 (`tools/audit3-p4.py`, pushed `468c308a5`); batch 5a c13 + c12 + c14 (`tools/audit3-p5.py`, tw.css, pushed `685bad0b4`, live-verified); batch 5b c15 (21 WebP files, `tools/audit3-p5b.py`, commit line); the TXNS 24H item closed; HvB live look ok.
- `sessions/2026-10-07-audit.md` — Audit III: the merged c1–c65 list and the seven raw sweeps (L, M, P, D, C, S, E) with evidence.
- `sessions/2026-10-06.md` — the Charts page: the sub-tab box gone, the Share badge restyled right, UFO-green metallic titles on every
  page (`html[data-tok]`), and the load-speed deep dive: prebuilt `data/charts-intraday.json` (new hourly step), paint-then-top-up,
  loads that supersede each other, the GT gate skipping aborted calls; harness; the UFO day-90 live check (real test = Oct 7).
  Afternoon: the Actions review — cadence ~4 runs/day, 22-min serial runs, two dao-buys reds, the 1.2 GB history — and the fixes:
  worker v7 dispatching the pipeline hourly (Shaka deploys), `scripts/pipeline-run.mjs` three parallel lanes + job-summary report,
  pair-volume on CoinGecko Pro, dao-buys carrying forward. Evening: HUMANS VS BOTS — the window through 14 design rounds (his
  art, his mock-ups), the classification self-check (round trips, switch.win, the wallet rule; confidence stated), the DAO Buys
  creature-clipping fix, the RH cores pinned, go-live (Volume tile bot icon), tile badges in the token colour, the share card
  (3 mock rounds → built) + Socials rows, the Telegram announcement; all pushed by him (`ae67befe3`, `6073ad2a5`) before close.
- `sessions/2026-10-05.md` — afternoon: the Calculators page reskinned (his art, Hub-style title, icon buttons, framed disclaimers; `tools/calc-v2.py`). Morning: the KPI Report tab redesigned to Shaka's mock-up: mock v1 (approved), `KpiCardV2` + `kp-*`
  container-query CSS, real sparklines via `useH2Series`, the fire bar shared, the Combined KPI Report row restored (dead since
  09-29), four explainers; harness at 1440 / 1024 / 390, DS_DOWN, the Socials rows.
- `sessions/2026-09-08.md` — review, roadmap, Phase 0, dead code, data quick wins, generator repoint,
  share cards, Phase 2 leftovers, u7/u8 clarity + mobile pass, harness ported to `tools/`.
- `sessions/2026-09-09.md` — u1 Modal shell (16 overlays migrated, key stack shared with
  ShareCardModal + InfoTip), u9 a11y (labels, nav landmarks, focus ring, reduced motion), u10 dropped.
- `sessions/2026-09-11.md` — switch.win buy-button research: `/dapp?from&to` deep link (no
  fee share) vs `/widget?…&partnerAddress=` iframe (50% fee share); both verified live. Build Sunday.
- `sessions/2026-09-13.md` — Buy/Sell via switch.win, end to end: header button (option B),
  `SwapModal` (widget iframe, in-window Switch, header v2 with address copy + live price),
  audit fixes, Home-card rail/footer bar (option E, cards now `lg:max-w-4xl`), wallet connect
  + buy verified live by Shaka, g7 ticked on the roadmap. Evening: u4 (16 render-defined
  components hoisted) + u13 (holder chart redraws when history lands; `SLOW_HISTORY` harness env).
  Night: g8 DAO Buys chart (`DaoBuysModal`, `scripts/build-dao-buys.mjs`, `data/dao-buys.json`,
  `hoverfile` harness action) — hidden behind `DAO_BUYS_LIVE`.
- `sessions/2026-09-15.md` — Swap modal `max-w` px→rem (title clipped to "PTG" on a larger browser
  font), "Market then" vs "Price paid" explainer, pipeline freshness check.
- `sessions/2026-09-16.md` — u14 (`LS` key table, disclaimer version, tier-cache shape check,
  `?token=` keeps the query) + u11 (Live Feed: `DeckRow` memo, `DeckScanline` clock + ageing
  Contacts 24h, `DeckPods` count-up, no blend layer, >6 pods, learned-pool names); harness
  `DECK_LOGS` / `REDUCED` / `NO_ACCEPT` / `reload`. Evening: Audit II method, live-check finds, headlines.
- `sessions/2026-09-16-audit.md` — the 153 raw Audit II findings (nine sections, evidence + scenario +
  fix each) behind roadmap a1–a67.
- `sessions/2026-09-17.md` — Audit II honest-failure pass (a14, a15, a17, a18, a19, a20, a21, a23):
  null through / "—" out across fetchDex, allocation, PTGC-burned-by-UFO, five share cards, KPI
  compare, quickRefresh token guard, partner prices in the Value Generated model, deck windows;
  harness `probes/fetch-fail*.js`. Evening: **a29** — Actions-API diagnosis (runs not created, not
  failing), `data-pipeline.yml` replaces nine workflows, `pipeline-gate.mjs`, `lv-snapshot.js`; first
  run green. Night: **a28** (250-row PulseScan pages walked to the end + reach assertion), **a31**
  (fatal log chunks, verified with a mock RPC), **a30** (half-year burn files, 2026 migration,
  unchanged files not rewritten), **a34** (Ledger data from raw GitHub), **a33** (token-allocation
  builder: null on failure, previous entry kept, staking contract under PTGC), **a32** (served
  ufo-ptgc-burns.json slimmed to summaries + 91-day v1 rows; caches in their own file), **a38**
  (Pages artifact = `_site/` allow-list), **a35** (Ledger summary "—" while loading), **a37**
  (Charts status = data age, "Cached", carried-forward); harness `SLOW_DATA`, charts.html runnable.
- `sessions/2026-09-18.md` — pipeline cadence measured (GitHub throttles even one workflow to ~5
  runs/day; thresholds 6 h / 8 h; a30/a32 migrations verified). Audit II calculators **a5–a9**: RPC
  pool + null burn, PLS null + `dsOnePair`, Rewards save effects + per-token bags, calculators stay
  mounted across a Switch (`LiveBadge`, banner), token-switch race cancelled; harness `DS_UFO_PRICE`
  / `SLOW_UFO`, `probes/calc-header|type|sanity.js`. Evening: **a36** — `treasury-recent.json` (859 KB
  vs 3.7 MB), Ledger reads it first with the full files as fallback; `probes/ledger-rows.js` proved the
  seven months identical. Night: **a12** (portfolio: RPC pool, one-at-a-time reflections queue with
  `gen` guards, pending / failed / Retry, total only when complete; harness `HEAD_BLOCK`, `LOGS_DOWN`,
  `probes/portfolio-state.js`), **a26** (ErrorBoundary `resetKey` + Try again; `probes/eb-state.js`),
  a27 read against the live API and left open. Note: `.github/workflows/*` is protected from the
  bridge's file writer — edit those in place from the shell.
- `sessions/2026-09-20.md` — FOUR passes. Last: **the Affiliates outage** — `ptgcapi`'s `/public/commissions` 500ing because its GitHub data file passed 1 MB and the contents API answers `200` with empty content; worker v4 reads raw. Not this repo (reproduced from x1prism.com with no dashboard code loaded; worker last deployed 7 months ago). Evening: **a40** (Swap scans behind `DIAG` — 612 RPC calls saved per stale-file UFO visit, figures byte-identical) and **a41** (`_rpcFailedAt` cooldown, `-32005` rotation, `transport:true` so `getLogsRange` stops halving a dead range). Afternoon: **a27 closed won't-do** (owner: another site manages commissions) and **a39 / a42 / a67** built — the retired UFO contract's burn out of both fallbacks (`liveBurnedCache`, `address` stamps, `PTGCbyUFO` cleared on load), one epsilon-tolerant `creatureCount`, `fmtAbbr`'s magnitude step, `findBlockAtTime`'s low edge probe, the tier tables derived from `BURN_C`, portfolio's Shell floor, calculators' ATH rule. Certified in node against the old code (200k random percentages, all seven `mcapFromPrice` branches) and in the cloud harness (the missing-file case reproduced on the old build: 4.30B unlabeled → 157.76M labelled). Morning: live verification of the 09-18 deploys, no code changed: a5 (PLS ratio
  0.59 / 3.81), a6 (MCaps $6.00M / $12.39M, circ supply and reflection-eligible real), a8 (bag saved on
  typing, per-token, survives reload and a Switch), a9 (amber "Loading PTGC data… your inputs are kept",
  values dash then land in ~1 s, no full-screen gate), a12 (UFO reflections "scanning" → 3.93M, no zero
  for an unknown, test wallets removed after), a36 (one `treasury-recent.json` request; Sep 2026 and the
  oldest month, Mar 2026, both render with no fallback fetch), plus the owed index.html look (Value
  Generated $3,160 delivered, PTGC-burned-by-UFO lifetime + four windows). a26 code-verified only.
  The "as of 3.8h ago" vs an 8.9 h file was the probe's error, not the site's: the app reads raw GitHub,
  `_site`'s `data/` copies are deploy-frozen — filed as cleanup for a39+.
- `sessions/2026-09-21.md` — Audit II, the wrong numbers on the pages other than index.html, then the affiliates freshness badge, **a54**, **a62 + a51** (first paint, the retry ladder, the five-minute skeleton) and **a52** (a long-open tab's frozen labels and volume).
  **a60** Ledger: inbound PTGC with no outgoing DAO transaction is a transfer (📥 "Received"), not a
  buy — 80 such rows in the full treasury files, none from a router, two of them 265.1B of Oct-2023
  funding, none inside today's picker; UTC month buckets, picker, window gate and row times, with a
  "(UTC)" mark; `LEDGER_STALE_MS` 8 h amber banner / `LEDGER_DEAD_MS` 7 d "—". **a59** charts.html
  seeds `currentHdrToken` from `?from=`/`?token=`/`ptgc_last_token`, index.html links
  `./charts.html?from=${token}`, daily-tier dates formatted in UTC (the 2026-09-21 candle read
  "Sep 20" in Los Angeles). **a61** fetch-coingecko-data: `fetchOHLCV`/`fetchTrades` null on failure,
  per-figure `complete`, previous value carried with `carriedFrom`, no history point for an
  incomplete figure, `process.exit(1)` on a throw; lv-snapshot: status-code check and no zeroed row.
  **a53** token-allocation.json age-gated (14 h / 36 h, `asOfTs`), `squidAndBelow` null when the
  holder count is. Proofs: `probes/ledger-digest.js` across three time zones, stubbed `main()` runs
  for both scripts, `PS_COUNTERS_DOWN=1` before/after on UFO. Harness: Tailwind scans all five pages,
  charts.html's date adapter is served at last, `reload=` fixed for pages without `#root`.
- `sessions/2026-09-22.md` — the affiliates page showed some viewers zeros while the site and the
  data were healthy: deploy current (all a54/a52/badge markers live), endpoint correct (71 referrers,
  DomDoos 66 buys / $8,244.38 / 3.44M), live page clean across all 66 expanded rows, and no second
  copy of the page anywhere (goptgc.com / x1prism.com have none). Reproduced on the live site by
  answering the one `ptgcapi` request with `200 {}`: a full dashboard of zeros, no warning. Shape
  guard + `no-store` + cache-buster + a plain-language error; harness `AFFIL_BAD`, default stub now a
  valid empty program. Verified 14/14 on the shipped guard expression, live against the real worker,
  and four harness runs. Open: the worker still sends no cache headers, and the endpoint is still on
  `*.workers.dev`.
- `sessions/2026-10-03.md` — go-live prep: the sibling pages' v2 header (option A) hidden behind the preview switch —
  `h2.css` out of index.html, `h2-header.jsx`, charts' static twin, `PortfolioHeaderV2`, `?open=swap|feed`, the phone
  triangle (gotcha 39), `deploy.yml` allow-list, harness fonts for charts.html, `probes/dom-hash.js`; classic identical on
  all four pages. Nothing pushed, nothing seen live.
- `sessions/2026-10-02.md` — **evening: Holders Details** (the discussion — new = 0→>0, departures listed so the net matches
  the box, pipeline file; `build-new-holders.mjs`, the 30-day backfill and its cross-check, the window, the dot, the gate);
  rounds 22–25: LP Pairs alignment (option sheets A/B/C + tiles 1/2 → Table A + Tile 1); PTGC
  Burned by UFO boxes with icons, 20 px creature counts, 14 px Value Generated titles (`P2Name` fit); no "as of" top-right,
  14 px period labels, Live Feed sky .72, Home tag line; the phone + iPad pass (Token Allocation stacks, creature strip,
  phone LP band `p2-lphp`, All/RH knob `left-0`, 1024 tier). Ends with the go-live plan.
- `sessions/2026-10-01.md` — **evening (rounds 19–21): the Live Feed NEW badge redrawn (seven mock-ups, B hairline + glow); the
  "from $X of volume" line back beside the Value Generated total under v2, per window, UFO too (no "as of" under it); LP Pairs:
  sorting on the column headings (`LpTh`, SORT toggle gone), the Value Gen 24h tile + Value Gen column (volume × fee), "Price
  24h", the band's tiles one width with centred labels; classic proven identical throughout.** Morning: fifteen rounds of v2 clean-ups; **afternoon (rounds 16–18): the Value Generated tiles to
  Shaka's layout (`.p2-vgt`, `H2Val` figures, coin-on-flame), the LP Pairs header band (`LpHeaderV2`, change lines, glass
  toggles, three-tier squeeze), the LP Pairs rows (rank rings, volume change, illuminated sqrt-height `LpSpark` coloured by
  that change, 24h % badge, stacked Txns); round 20: column sorting (`LpTh`), the Value Gen tile + column, "Price 24h"** — morning: fifteen rounds of v2 clean-ups, all live: header buttons + address, bigger fitted figures
  (`H2Val`), `PTGC IN LP`, sparklines to Shaka's spec (`h2Peaks`, `H2_DAYS` 30, one colour per token), option-A toggles,
  the tab band on his art, the SVG donut (`AllocRingV2`), his icons on every panel (`SeaIcon`, `SEA_ART_V`), dark pools,
  UFO burn windows from the snapshot at once; the flip checklist (-6); harness 1440 / 1024 / 390, classic unchanged.
- `sessions/2026-09-30.md` — the dashboard header v2 built into index.html: `DashHeaderV2` / `KpiTilesV2` / `H2Spark` /
  `useH2Series` (7-day real-data sparklines on all seven tiles), the `--u` reference-pixel CSS, `logos/header/` assets,
  `HEADER_DESIGN` + the hidden preview switch (`HeaderPreviewGate`, hashes only, empty until Shaka's); harness at
  1440 / 1024 / 768 / 390 / 375, loading shell, DS down, the walk, classic proven unchanged. Afternoon: the four panels
  + PTGC Burned by UFO as a skin (seven tweak rounds). Night: the LP Pairs table (`LpTableV2`, real per-pool 7-day
  volume curves, `DS_PAIRS=burn` harness, classic byte-identical).
- `sessions/2026-09-29.md` — affiliates frozen at Sep 23: the worker's `btoa()` write path threw on four em-dashes
  after the v5 redeploy; worker v6 (`toBase64Utf8`) deployed + verified, ToolBox Sync made honest (`saveDataImmediate`).
  Afternoon: the affiliates page on iPhone / iPad — unpinned header, two-line Recent Activity, Registry + Commission
  Log as phone cards, tablet min-width tables, modals wrap; harness `AFFIL_DATA=real`.
  Evening: Socials Affiliates Report card redone (`AffiliateSocialModal`, mock-up B + clean gold All-Time bar).
  Late evening: Combined Value Generated card redone (`CombinedVgSocialModal`, twin panels + "where it went").
  Later: Grays & Cores price card restyled (`GraysCoresSocialModal`, today's layout, glass-strip headers, Wide/Tall).
  Then: WPLS/eHEX pair fix + grey 0.00%, white titles (Holders combined, RH Core Liquidity), and one price-pair
  rule for the whole site (`dsPricePair`, gotcha 35). All pushed and checked live except the portfolio look.
- `sessions/2026-09-28.md` — UFO/WETH out of the RH Cores modal + RH-only switch (seed flag + `resolveUfoPairs`); afternoon: the Socials RH Core Liquidity card redone on Richard Heart's stage photo (`RhCoresSocialModal`, Wide only).
- `sessions/2026-09-26.md` — Holders cards redone: six mock-up rounds (cyan → silver → gold/green; tiles without
  accent bars; growth-rate data restored; Shaka's two-colour alien as the icon), then `HoldersSocialModal` +
  `HoldersSingleModal` built, old html2canvas card + Chart.js canvases removed, loader honest-null; afternoon: the ⓘ
  opens the card directly (old modal deleted, 7D/30D/90D in the toolbar), Mac overflow fixed with measured slack
  (`probes/card-slack.js`), harness `run.js` UFO `pairCreatedAt` fix. Afternoon, part two: the Live Feed reskinned
  on Shaka's art (gotcha 34).
- `sessions/2026-09-25.md` — new Home screen ("cosmic"): Shaka's alien art, metallic title, two glowing cards
  with a real 24 h GeckoTerminal chart and one BUY / SELL button each; classic kept behind `HOME_DESIGN`.
- `sessions/2026-09-23.md` — Socials DAO Buys card (three rounds: period switch, All time default, Wide/Tall,
  local + UTC times), Burn Stats fire redesign (PTGC + UFO), DAO Treasury blue redesign; all screenshot-only.
- `sessions/2026-09-14.md` — g8 follow-up: `DaoCreatures` (Grays tiers via `getBurnC`) in the
  "PTGC bought" tile, Recent-buys ledger box (last 10, +10, table on sm+, stacked list on
  phones). Harness ran in the cloud workspace (no Chromium on the local VM).
- `sessions/2026-10-03-socials-hub.md` — the Socials Hub redesign: his mock-up + icons (the zip mis-cut, icons cut from the
  mock-up instead), six mock-up rounds, the row order, the build (`tools/socials-hub.py`, handlers lifted verbatim), harness.

