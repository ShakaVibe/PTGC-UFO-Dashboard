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
- **Portfolio v2 — LIVE since 2026-10-16 (`bc8e60b8b`), the ONLY body since 2026-10-20 (cleanup, `tools/pf-cleanup.py`):**
  `PortfolioV2` (`.pf2-*`) rendered by `PortfolioPage` in portfolio.html, which owns the state and the shared windows (Get / Load
  Code, Edit wallet, Leagues). Source `tools/pf-v2/PfLeagues.jsx → PfHistory.jsx → PfTx.jsx → PortfolioV2.jsx` + `pf2.css`, synced
  into the page by `tools/pf-v2.py` (run it twice: must print `0 edit(s)`). Mock-ups + every decision `design/portfolio/README.md`,
  the audit + roadmap `handover/PORTFOLIO-ROADMAP.md`. Next: Phase F, one at a time, MOCK-UP FIRST (F4 share link first).
- **Volume window (2026-10-07):** the Volume tile's ⓘ in the Humans vs Bots look — `VolumeModal` (`.vw-*`), build `tools/volume-window.py`,
  mock-ups + every decision `design/volume-analytics/README.md`; its chart + pool table read `data/swap-volume.json` like HvB.
- **RH Cores window (2026-10-07):** the Liquidity tile's RH button in the same look — `RhCoresModal` (`.rc-*`, reuses `vw-tile` / `vw-card`),
  build `tools/rh-cores.py` (run AFTER volume-window.py), decisions `design/rh-cores/README.md`.
- **Audit III (2026-10-07):** `sessions/2026-10-07-audit.md` — 65 merged items (c1–c65) with evidence; top of that file = the list.
  On the roadmap artifact as the "AUDIT III" phase. **The P1 batch (c1–c8 + c11 + c25) is built by `tools/audit3-p1.py`** (idempotent,
  on the repo root; "0 edit(s)" = already applied) — c1 `data-presets="react"` = the compile 15 s → 3 s.
- **Audit IV (2026-10-22 night, Claude, NO code changed):** `sessions/2026-10-22-audit4.md` — the whole repo re-read at
  `223de3f58` by eight sweeps (security, index numbers, sibling-page numbers, pipeline, client RPC, perf/SEO/compat, a11y/UX/tests,
  responsive) with ~200 harness runs + a live check from the Mac. **47 merged items e1–e47 (8 × P0, 23 × P1), TOP 10, the
  four finding sections, quick wins, ideas, "do not change".** NOT yet on the roadmap artifact (add an "AUDIT IV" phase with e1–e47).
- **Charts page (2026-10-05 / 10-06):** the Calculators treatment (same plate, "Grays Charts") — `tools/charts-v2.py`, `cp-*` CSS in charts.html; then
  `charts-gt.py` (GeckoTerminal back-off), `charts-v3.py` (no sub-tab box, the Share badge at the right, UFO-green titles) and **`charts-fast.py` +
  `scripts/build-charts-intraday.js` → `data/charts-intraday.json` (hourly pipeline step `charts-intraday`): 24H / 7D / 14D paint from the prebuilt
  file at once, live GeckoTerminal only tops up; a new load supersedes the one in flight.** Every page's metallic "Grays …" / "Socials Hub" title turns
  UFO green via `html[data-tok]` (stamped by the headers).
- **Calculators page (2026-10-05):** his art as the plate + "Grays Calculators" title + his icon buttons + framed disclaimers — `tools/calc-v2.py` (`cp-*` CSS in calculators.html), assets `logos/calculators/`, decisions `design/calculators/README.md`.
- **KPI Report tab (2026-10-05):** `KpiCardV2` (`.kp-*`, container queries) — assets `logos/kpi/`, build script `tools/kpi-v2.py`, mock-up + every decision `design/kpi/README.md`. The old 📷 share image (`TwitterCard`) is unreachable since 2026-10-08 — the Socials Combined row opens the new cards too.
- **Leagues (2026-10-04):** the holder-tiers modal (`TierInfoModal`, `.lg-*`) and the Socials combined card (`LeaguesCombinedCard`, `.lgc`) — assets `logos/leagues/`, mock-ups + every decision `design/leagues/README.md`.
- Repo layout: `index.html` is the whole app (React 18 + Babel-standalone + Tailwind play
  CDN, compiled in the browser). `scripts/` + `.github/workflows/data-pipeline.yml` are the
  hourly data pipeline that writes `data/*.json` (ONE workflow since 2026-09-17, a29; `deploy.yml`
  is the only other workflow). `calculators.html`, `charts.html`, `portfolio.html`,
  `ledger.html` are separate pages. `data/new-holders.json` + `scripts/build-new-holders.mjs` = the Holders Details window's
  data (2026-10-02, hourly `new-holders` step). **Since 2026-10-03 the v2 header's CSS is `h2.css` (root, linked by index +
  the three sibling pages) and the sibling pages' v2 header components are `h2-header.jsx` (root, Babel `src`).** The Socials tab's
  art is `logos/socials/hub-sky.jpg` + `logos/socials/hub/*.png` (2026-10-03, `tools/socials-hub.py` = the build).

## Current state (2026-10-22)

**2026-10-24 (night): "THE BURN ADDRESS" label + the OVERLAY chart + 1Y default — BUILT, NOT pushed.** (Shaka: 'next to the 1 Poseidon,
lets put "The Burn address"' / 'could we add an overlay line chart of the token counts … use what you think makes it good' / 'lets
default to 1 year and the shark selection. and lets make the hold joined and left text in each card larger'.)
`python3 tools/burn-label-overlay.py` (idempotent; from `92a8ae65` → index.html 9176dde4, lh.jsx 34861884, lh.css d5fe4dc1):
the strip says THE BURN ADDRESS beside the count when the burn wallet is alone in its league (PTGC's 1 Poseidon), INCL. THE BURN
ADDRESS when it shares it (UFO's Whales); on a phone that becomes one caption line under the creatures ("🔥 Poseidon = the Burn
address"). League History: the same label on the card; the big chart's new default BOTH = the wallets line (left axis) over the
tokens held as a sky-blue area (right axis, ticks on the same grid lines), a legend, hover "102 sharks / hold 81.82B (24.5%) · ~802M
each"; WALLETS / TOKENS HELD stay as single views. Opens on 1Y (new localStorage key grays_lh_per_v2) with Sharks; bigger "hold" and
"joined · left" lines. Fixes: count axes take whole steps only (was 93/95/98), a league holding 0 shows 0%, phone + long period = 3
date labels. Probes strip.js, lh-big.js. Still hidden (LEAGUE_HISTORY_LIVE=false).

**2026-10-24 (late evening): the BURN WALLET is a sea creature again + TOKENS HELD per league + a bigger League History logo — BUILT, NOT
pushed.** (Shaka: "what happened to the poseidon???? Why is it gone... it was the burn wallet" → picked "Count it as Poseidon"; then
"make the logo at the top bigger … how many tokens do those 107 wallets hold".) e13 (people only) had dropped 0x…0369 — PTGC's only
Poseidon. Now: people only EXCEPT the burn wallet, which counts in the league its balance puts it in, marked 🔥 (`burnIn`).
*Files:* `tools/burn-poseidon.py` (idempotent; edits scripts/build-token-allocation.mjs + index.html — strip 🔥 + hover, live fallback
scan keeps 0x…0369 — and re-splices League History); `scripts/build-league-history.mjs` SCHEMA 3 (burn wallet in every day's counts,
`burnIn {start,circ}`, `held {start,circ}` = tokens held per league per day) and `tools/league-history/lh.jsx` / `lh.css` edited
directly (card icon 🔥, "hold 76.69B · 23.0%" line on each card, chart toggle WALLETS / TOKENS HELD, share card shows hold, footer
"People only + the 🔥 burn wallet", logo 112 px / phone 84 px). Data rebuilt: token-allocation PTGC 1/12/96/693 (burnIn Poseidon),
UFO 0/17/99/498 (burnIn Whale — 96.06 B = 9.6 %, a Whale until it passes 10 %); league-history.json schema 3, 319 KB.
Shas: index.html 6252a0d9, build-token-allocation 71e84430, build-league-history 6ebce599, lh.jsx 886becb9, lh.css 4910dedd,
league-history.json 2a6400ec, token-allocation.json d976e7a5. League History still HIDDEN (LEAGUE_HISTORY_LIVE=false).

**2026-10-24 (evening): LEAGUE HISTORY window — BUILT, HIDDEN behind the faint bottom-right dot, NOT pushed.** (Shaka, after the mock:
"Thats awesome... Lets build it, but I dont want to make it live yet.. hide this behind a small faint dot in the bottom right corner of
the dashboard … then when I am ready I can tell you to go live and you can move it to where they can click the sea creature bar.")
Build = `python3 tools/league-history.py` (idempotent; from `36377545b` index.html sha256 6a3329a9, re-runs "0 edit(s)"; it also wires
the pipeline step). New: `scripts/build-league-history.mjs`, `tools/league-history/lh.css` + `lh.jsx` (the fragments — edit those, never
the spliced copy), `data/league-history.json` (104 KB, built here so the window works right after the push), probes lh-state.js /
lh-hover.js. Design + data notes: `design/creatures/README.md`.
*Data:* the rank-history archive walked day by day (people only = the strip's population), counts of all 8 leagues per UTC day on
the starting AND circulating basis; circulating = starting − balanceOf(0x369) at each day's last block (cached per archive day in the
file; one read per new day); joined / left for 7D … ALL (a wallet's league on the period's first day vs the last; joined − left = the
change — checked for every league, period and basis: 0 mismatches). The history starts on the first day with a holder (PTGC
2023-10-11, UFO 2026-07-09). Oct 23 PTGC 0 / 12 / 96 / 696 / 2,226 / 2,930 / 1,844 / 9,276 (= the mock; circulating 286,997,740,190
from balanceOf = the same as the burn-archive sum). Pipeline: step `league-history` in the holder-ranks lane after rank-history (no
gate; writes only when the archive has a new day — a no-op run takes ~1 s), commit list + `only` description updated.
*Window (LeagueHistoryModal, index.html, Modal shell → Escape / Back close it):* the mock as built — PTGC / UFO, 7D … ALL (remembered:
LS.LH_PER), Starting / Circulating, eight cards (count, ▲▼ change %, joined / left, sparkline), the big chart of the tapped league
(high / low, today's dot, hover / touch readout of any day), JOINED / LEFT / ALL HOLDERS, the foot (people only, basis, "history to
the close of Oct 23 (UTC)", amber past 2 days), 📷 = a Wide 1200 × 675 screenshot card. Loading = skeleton cards; a failed read =
"Couldn't load … RETRY". `LhDot` (the VsDot pattern) opens it on the dashboard tab while `LEAGUE_HISTORY_LIVE=false`.
*Evidence (harness, real data):* the dot opens it; 6M Sharks 103 → 96 ▼ 7, +21 / −28; 1Y circulating Whales 16 → 13, +1 / −4; hover
"Aug 9, 2026 98"; share card renders; Escape closes the card first, then Back closes the window and stays on #/ptgc; 390 px UFO
cards two across, no sideways scroll; missing file → Retry; dashboard DOM = before + the dot only; a LIVE copy: no dot, the strip is
a button with a "HISTORY ›" tag and opens the window (1280 / 390, no overflow); compile + ci-mount 7/7; tw.css unchanged.

**2026-10-24 (afternoon): ROADMAP + D-4 + D-6 + AUDIT IV P3s + P-5 / P-11 / M-13 — BUILT on the Mac, NOT pushed.** (Shaka, on
the "what's next" list: "1 no [share link], 2 yes, 3 yes, 4 yes, 5 yes, 6 yes"; then picked "256 bigger files" for D-6, "Chart
counts it too" for M-13, "Later" for e43's names / gold mock-up.) Build, in this order (all idempotent, re-runs "0 edit(s)"; a clean
run from `aa7eebd75` = these shas): `python3 tools/pipeline-rpc-pool.py` → `tools/rank-index-256.py` → `tools/audit4-batch7.py` →
`tools/dao-buys-token-paid.py` → `tools/audit4-polish.py`, then `cd tools/harness && npm run css` (tw.css 52dd311b → `?v=7`; h2.css
2ae97342 → `?v=5`). index.html bd04ec8c, portfolio bfb42701, calculators c74b2d4c, charts fe40aba4. New file `scripts/rpc-pool.js`.
*Roadmap artifact:* "AUDIT IV" phase added (e1–e47 from the audit file; phone overflow of the page fixed); ticked: every e-item but
e5 / e6 (Worker v8, parked) and e43 (names / gold — his "later").
*D-4 (e33) — one RPC pool for the pipeline:* `scripts/rpc-pool.js` (CommonJS; the .mjs import it as default) — rpc.pulsechain.com
first, then rpc-pulsechain.g4mm4.io and pulsechain-rpc.publicnode.com (`RPC_URLS` overrides, a script's own `RPC=` pins one).
The primary is always tried first, so nothing changes while it is healthy; a transport error / timeout / HTTP 429-5xx / JSON-RPC
rate limit cools it 30 s and the next one answers. HEAD CHECK: a call naming a block (getLogs toBlock, eth_call at a block,
getBlockByNumber) only goes to a node whose eth_blockNumber has reached it (re-probed when short), and 'latest' calls skip a node
> 30 blocks behind — so a lagging fallback can never return an empty getLogs and make a scan skip blocks. Wired into
fetch-burn-history (→ fetch-ufo-ptgc-burns too), value-generated, dao-buys, new-holders, swap-volume, rank-history,
token-allocation, top-stakers; each keeps its own retries / halving; per-try budget passed as `attemptMs`. A script that used a
fallback prints one "rpc pool:" line at exit. Tested: 12 fake-node cases (healthy, 503, -32005, hang, all down, lagging B → C,
nobody has the block → error not []), and real runs of dao-buys, burn-history (reconcile ✓ both tokens), swap-volume, rank-history.
*D-6 — 256 rank-index shards:* `meta.json` gains `shard: 2`; files are `<first two hex>.json` (~110 KB PTGC, 35 KB gz; 512 files a
day instead of ~6,900). The builder reshards on its next run even with nothing to extend (`INDEX_ONLY=1` does it locally, no RPC);
PfRank reads meta + the 2-char shard together and falls back to the other layout. Verified: resharded index = the old one wallet
for wallet (19,270 / 5,106), meta identical but `shard`; the rank window renders the same on both layouts.
*e42:* sr-only h1 per dashboard ("PTGC dashboard — overview / KPI Report / Socials") + "Skip to content" (h2.css `.g-skip`, focus →
`#g-main`); KPI tab h2, Live Feed title h2; the five panel h3s named by their title (aria-label); Calculators / Charts titles h1.
*e44:* Back closes the open window — index's `useDialog` (every Modal / share card) and portfolio's `PfModal` push one same-URL
history entry; Back pops it → the top window closes; ×/Escape take it back off; hash router untouched. Harness `back=` action.
*e45:* a refused wallet-list save drops the two history caches and retries, else "This browser didn't let the page save your
wallet list … Use GET CODE to keep a copy."  *e46:* league bar ≤ 99.9 % while below the line + "need 1.3 ≈ < $1"; fmtX keeps
"x" above 1,000 (UFO "4.1Kx"); getWhaleProgress with the a42 epsilon (5.00 % = 5 whales, 0.0 %); KPI compare card's other-token
Volume badge computed (vol24h vs vol7dFromCache/7); Live Feed SELL on a known pool grossed up by 1/(1−fee) ($0.32 → $0.34 in
the stub); footer px-4; Leagues / disclaimer / Affiliates / Logos windows in dvh (+ @supports vh fallback); "About the cost" ⓘ
(Top 100 + rank window) is a tap-toggle button (hover only with a mouse); Volume / Holders tiles at 1024–1199 get a 7 px gap.
*P-5:* index loads Chart.js on demand (`loadChartJs` / `useChartJs`, same SRI) — #/ptgc boots with no chart script; the DAO Buys
window loads it and draws (line + bar, share card too). Calculators keep `defer` (six charts with long shared deps).
*P-11:* Home "ENTER DASHBOARD" + classic BUY: the box-shadow pulse → static glow + an inset glow on ::before animating OPACITY
(getAnimations: boxShadow → opacity); looks the same.
*M-13:* build-dao-buys counts token-paid buys by the Ledger's rule; priced at the block's PTGC market price, `pls` = PLS-equivalent,
`paidWith {symbol, amount, token}`, `tokenPaidBuys` in the file; the window prints the token ("5.56B Burn") on those buys. Real
rebuild: July 5 / 168.1 M → 6 / 183.0 M (= the Ledger), Jun / Aug / Sep unchanged, plus 2024-12-19 (3,000 EHEX → 0.03 M) and
2025-03-16 (15 B "808" → 33.1 M, ≈ $12.5K): 321 → 324 buys, $1.912 M → $1.925 M.
*e47:* numbers only (Actions minutes free while the repo is public; Pages / CoinGecko / PulseScan budgets far from a limit).
*Harness:* `T1_BY_ADDR`, `back=`, the jsDelivr chart.umd.js route; probes back-state.js, anims.js, chart-lazy.js; ci-mount 7/7.

**2026-10-24 (day): COMBINED HOLDER RANK + READY TO CLAIM AT 0 + TWO RANK CRASH FIXES — BUILT on the Mac, NOT pushed.**
(Shaka: "when multiple wallets are selected … show the ranking as if all wallets were one … in the same place where we show the
ranking details of a single wallet" — he had dropped "all N wallets as one" on 10-21 pm and asked for it back; then "if a wallet has
no stakes or locks, its just this big blank space … show just they have 0 to claim".) Build = `python3 tools/pf-rank-combined.py`
then `python3 tools/pf-claim-zero.py` (both idempotent, re-splice via tools/pf-v2.py; from `ecc9d1fe` → portfolio.html sha256
e81d22b6, re-runs "0 edit(s)"; tw.css unchanged).
*Combined rank:* two or more counted wallets → the League box row reads "ALL N WALLETS COMBINED · HOLDER RANK #r · ▲ x more to pass
#r-1" (`pfRankAll`: the counted balances added up — the same sum as the box — ranked against holder-ranks.json with EACH counted
wallet's own entry dropped by its tag, e9 per wallet, zero-balance wallets included so a sold wallet's stale entry goes too). One
wallet → exactly as before. The row opens the rank window on a new first picker entry "All N combined": TODAY + "if your N wallets were
one", tiles COMBINED / BEST WALLET ALONE / PLACES GAINED / TO PASS, WHAT IT TAKES + the calculator against the same list; no chart
("Rank history is kept per wallet …" — the rank index has ranks per address per day, no balances, so a combined history cannot be
built). The breakdown badges still open on their wallet, with the combined pick available.
*Ready to claim:* once any wallet has read, the PTGC spotlight always shows — 0 PTGC, an empty Staking / Locks bar, "Nothing to claim
— no PTGC staked or locked in this wallet / these wallets" (the old "rewards build up while you stake" line stays when something is
staked or locked).
*Fixes (live bugs):* (1) Audit IV batch 5's `// e27` comment had swallowed pfRank's guard on the same line — a stale token's list or a
failed read made pfRank throw, a 0 balance got a rank; (2) usePfRanks read `d.tokens[tok]` before e40's failed check, so a failed
holder-ranks.json read crashed the WHOLE Portfolio page ("Something went wrong … reading 'PTGC'") — reproduced in the harness at HEAD.
*Evidence (cloud harness, real holder-ranks.json, new `T1_BY_ADDR=1` switch = T1_BAL × the address's last hex digit):* 3 wallets
50M / 100M / 150M → combined 300M = PTGC #117 (▲ 2.87M to #116), UFO #256 (▲ 2.20M) = a Python count over the list; a wallet tagged
like the real #100 entry (412.5M, i.e. "sold") → #116 (its entry dropped); window: BEST WALLET ALONE #223 (C), PLACES GAINED 106;
2 wallets → 150M = #223, A alone #617, B #356; single wallet: page text + rank rows identical to HEAD; list missing (1 and 2 wallets)
→ "HOLDER RANK — couldn't load …", no crash (HEAD: crash); UFO list stale → PTGC combined ranks, UFO says out of date; no sideways
scroll at 1280 / 600 / 390; compile ok. Probe `probes/pf2-rank-all.js`.

**2026-10-24 (late, 2): "PTGC BURNED BY UFO" COUNTS pTGC's 0.5 % FEE BURN ON BOTH CONTRACTS — PUSHED `ecc9d1fe` (data runs not yet seen — see Next up -36).** (Shaka: asked
which way → "what do you suggest" → Claude: count it on both (it exists only because UFO bought; no ratio fingerprint) → "do it".)
`python3 tools/ufo-fee-legs.py` (idempotent, 11 edits): scripts/build-value-generated.mjs AND its twin in index.html no longer drop
the leg that is 0.005/0.95 of the delivered leg (window scan + pre-window lifetime slice); the file checkpoint
`delivered.ptgcPreWindow` is reused only with `method:'all-legs'`; the browser checkpoint key → grays_ptgc_by_ufo_pre_v2 (v1
swept). index.html sha256 391de7b0, build-value-generated.mjs 3fe13acf. Ran the old and new builder side by side against the
chain: v2 lifetime 316,468,990 → 318,127,174 (+0.524 % = 0.005/0.95 ✓); 24H 2.325 → 2.338 M, 7D 33.63 → 33.80 M, 30D 147.41 →
148.18 M, 90D 238.57 → 239.82 M — the new windows equal fetch-ufo-ptgc-burns v4's v2 windows to the token (two independent
methods agree). Site "PTGC burned by UFO" after both pushes ≈ 4,366.9 (v1) + 318.1 (v2) = 4,685.0 M (was 4,904.8 M).

**2026-10-24 (late): LOGOS THUMBNAILS (P-4) + "PTGC BURNED BY UFO" v4 — PUSHED `7815732b`.** (Shaka: "1 yes … 3. yes"; the token:
"ptgcapi pipeline dispatch" has NO expiration — checked by him; "saucer-claude" (expires Nov 4) is not used by this site.)
*Logos:* `python3 tools/logos-thumbs.py` (idempotent; run on the Mac) → logos/{ptgc,ufo,combined}/thumbs/*.webp (18 files, 480 px
longest side, 300 KB total vs 5.8 MB of originals), the three windows' <img> use them with loading="lazy" decoding="async";
links/download still the originals. index.html sha256 7fa5823e.
*fetch-ufo-ptgc-burns.js v4:* found a real over-count — v3 read a tx's receipt once PER UFO-burn log in it, so a tx with 2 UFO
burns stored its pTGC burns twice (3 → 9 rows): 126 txs, v1 lifetime 4,588.37 M → 4,366.92 M (−221.45 M), v2 file total
334.98 M → 316.79 M (the site's v2 figure comes from value-generated.json, 316.47 M, unaffected). Now: rows keyed by block + log
index, one receipt per tx, real block times (shared code from fetch-burn-history.js, whose scanBurns rows now also carry `tx` —
not written to the archive), re-read from cache `scannedTo` − 1800 to head − 96. First v4 run migrates: re-reads all 4,721
receipts (all-or-nothing, ~75 s here) and rebuilds every row. Simulated: migration ✓, second run no-op ✓; UFO burned
(reference) v1 149,591,279,767.087 = its burn-address balance, v2 96,059,530,539 = its balance. Site headline "PTGC burned by
UFO" ≈ 4,904.8 M → 4,683.4 M; 7D 34.73 → 34.46 M, 30D 150.15 → 149.36 M, 90D 246.67 → 244.63 M. Optional, NOT done (his call):
v1 still counts pTGC's own 0.5 % fee-burn legs, which the v2 chain scan drops (~ −23 M if aligned). The step is gated 6 h, so
the migration lands on the first ufo-ptgc-burns run ≤ 6 h after the push (or Run workflow → only=ufo-ptgc-burns).

**2026-10-24: BURN ARCHIVE v2 — the PTGC burn windows fixed (Shaka: "lets fix it.. we need it to be right") + HOME CARDS ROUND 5
— PUSHED `f2d25262`, VERIFIED: the 21:16 UTC pipeline run applied the rebuild (deleted the 8 rebuild files), burn-history step 20 s,
`PTGC.archive.reconcile.ok: true` (diff −0.0009 token at block 27873830), UFO v1 ok; raw burn-summary 7D 190.84 M / 30D 559.9 M / 90D
1,428.5 M; landing cards live (round 5 CSS, no axis labels). Shaka checked UFO: the UFO total (new contract, 96.06 B) already carries
the old contract's history — the 93.06 B burn of 2026-07-09 = old UFO burned to 2026-07-07; leave it.**
*Cause:* fetch-burn-history.js guessed each burn's time (head time − blocks × 10 s; PulseChain is ~3 % slower) and dropped re-read
burns by "same sender, amount ±1, time ±10 min"; once two runs' guesses drifted > 10 min apart the burn was saved again. Exact match
to the burn-address balance through 2025-09; from 2025-10 the archive over-counted (Aug 2026 570.7 M vs 366.5 M real; Aug 20 12–16 UTC
1,670 rows / 108.16 M vs 712 logs / 36.26 M on chain). Total +762 M; windows 7D +12 %, 30D +6 %, 90D +21 %. UFO v1 (retired contract,
ufo-burns.json, not shown on the site) 268.4 B logged vs 149.6 B real.
*Fix (scripts/fetch-burn-history.js, block "BURN ARCHIVE v2"):* a burn = (block `b`, log index `i`); real block times (batched
eth_getBlockByNumber); each run re-reads from `burn-summary.json` `<token>.archive.scannedTo` − 1800 to head − 96 (past finality) and
merges by key; every run reconciles the archive sum with balanceOf(0x369) at that block (`archive.reconcile`, ::warning:: on a
miss) and a miss makes the next run re-read from the last matching block with the fresh read replacing stored rows (doubling, ≤ 7 days);
files are written via .tmp + rename; a UFO load error is fatal now; windows end at the archive's last block (`periodsAsOf`).
*Rebuild:* `node tools/rebuild-burn-archive.js PTGC 2025-07-01` (798,769 burns, blocks 23866673–27873398) and `… UFO 2024-05-01`
(4,687) → data/ptgc-burns-rebuild-{ptgc,ufo}-*.json (8 files, 87 MB). Both checks passed to < 0.001 token: rebuilt sum = balance
change over the same blocks; kept pre-2025-07 rows + rebuilt = balance (46,332,002,587.47). The first pipeline run swaps them in
(rewrites 2025-h2 / 2026-h1 / 2026-h2 with b/i, ufo-burns.json), continues from block 27873398 and deletes them. Simulated here:
first run ✓ reconcile, later runs ✓, a planted phantom + missing row healed in 2 runs, leftover rebuild file removed. Independent
review: nothing serious; its 6 robustness points applied. Expected windows after (2026-10-23 ~20:00 UTC): 24H 4.18 M, 7D 190.7 M
(was 213.9), 30D 560.1 M (595.2), 90D 1,428.1 M (1,729.9); total 46.33 B = the balance. Nothing on the site reads the period files;
index.html reads burn-summary.json only (same fields). CHECK after the push: the Data Pipeline run's burn-history step log says
"Rebuild applied" and "= burn address balance … ✓"; burn-summary.json `PTGC.archive.reconcile.ok: true`.
*Home cards round 5* (Shaka: "make the two backgrounds … darker" + "get rid of the numbers to the right of the graph"): veil
.64/.70/.80/.78/.68 (radial .86/.6), PTGC art brightness .85, UFO .58; `.hc-yax` hidden. index.html sha256 4d5470a5 (from `18433ac2`
and from `f6f3cc7e`; re-runs "0 edit(s)").

**2026-10-24: HOME CARDS ROUND 4 (Shaka: "dont show the up down percentage for the 7D" + "make the ufo background a little darker";
"i dont need a mock up") — PUSHED `18433ac2`.** Appended to `tools/home-cards-atlantis.py` (the round-3 header edit has a `done=` marker;
from `9e1aa6f8` and from `f6f3cc7e` index.html sha256 f38e0d01; re-runs "0 edit(s)"). The chart label is "7D" alone (chg7 still feeds
the aria-label up/down only); UFO art brightness .78 → .66. Heights unchanged.

**2026-10-24: HOME CARDS ROUND 3 (Shaka: "make both backgrounds a little darker... and maybe we shold do the graph at 7 days not
24 hrs?"; worked example shown first, then "make it live") — PUSHED `9e1aa6f8`.** Appended to `tools/home-cards-atlantis.py` (round-1
edits that round 3 moves on carry `done=` markers; from `743dd044` index.html sha256 d6a2acbc; from `f6f3cc7e` the same file; re-runs
"0 edit(s)"). Chart = GeckoTerminal HOURLY candles, last 7 days (`/ohlcv/hour?aggregate=1&limit=170&token=`, `HOME_SPARK_WIN`),
one line per day, volume bars on a square-root scale. Fallback = `homeSparkRepo` (data/charts-intraday.json hourly, only if its
newest close is < 3 h old; no bars); the 24 h five-point fallback is deleted (it could not be labelled 7D). Label "7D ▼ x%" =
card price ÷ first close inside the window − 1 (worked example 2026-10-23 18:49 UTC: PTGC 0.0₄2241 → 0.0₄1904 = −15.06 %, UFO
0.0₅2984 → 0.0₅2462 = −17.49 %). The 24 h chip by the price is unchanged (Shaka chose no "24H" tag). Both veils darker
(.42/.52/.70/.68/.50 → .54/.62/.76/.74/.60; radial .78/.45 → .82/.52). Phone axis keeps both labels when there are only two.
Heights unchanged (453 at 1440×900, 365 at 390).

**2026-10-24: HOME CARDS ROUND 2 (Shaka: "the boxes are taller than than used to be. Can you shorter up the boxes" + "make the
backgrounds in the ufo box a little darker") — PUSHED `743dd044`.** Appended to `tools/home-cards-atlantis.py` (one R2_CSS block after
`.hc-status>div`, i.e. after every round-1 rule, never inside a round-1 insert; index.html sha256 5d266a60, re-runs "0 edit(s)").
Card heights (harness, GT_CANDLES=1): 1440×900 613 → 453 px (before the redesign 457), 1280×800 555 → 419 (430), 1920×1080
707 → 537 (511), 390 450 → 365 (357). Smaller logo / name / price, tighter gaps, slimmer tiles, a one-line 24H label, chart 62 px on
phones / clamp(78, max(5.4vw, 8vh), 120) desktop (every other axis label hidden under 640 px), button 48 / clamp(52, 4.2vw, 66).
UFO art `filter:saturate(.85) brightness(.78)` (PTGC unchanged).

**2026-10-24: HOME CARDS → THE ATLANTIS LOOK (Shaka sent a mockup + two background artworks: "make it look as close to the mock up as
you can"; after the mockup: "can you darken the backgrounds more", then "make it live") — PUSHED `5cf4491a`.** `python3 tools/home-cards-atlantis.py`
(idempotent; from `f6f3cc7e` it gives index.html sha256 9a8266f0, a re-run prints "0 edit(s)"). New art: `logos/home/hc-art-ptgc.webp`
(gold ruins) and `hc-art-ufo.webp` (green ruins + saucer), 1200×873. CosmicCard: art + a navy veil INSIDE the frame (`.hc-art` /
`.hc-veil`, darkest behind logo/name/price), "NATIVE TOKEN" line, price + chip on one row, address + DAY on one row, icon stat tiles,
the 24H chart in a panel with a price axis (`hcTicks`, ≤4 round prices in fmtPrice format), 15-min volume bars (column 5 of the SAME
GeckoTerminal candles — no new request; the 5-point fallback has no bars) and an end dot; ENTER DASHBOARD is dark glass with waves.
BUY / SELL: compact pill on phones, the ⇄ icon alone under 380 px (was 360). Skeleton mirrors the new geometry (gotcha 11). No number,
source or formula changed. Harness: 1440 / 390 / 360 / 320, GT_CANDLES=1, fallback and SLOW skeleton — no sideways scroll, nothing
outside the card, the pill clears the name at every width.

**2026-10-24: Leagues card round 2 (Shaka: "I dont like how the image goes out past the frame … make both tokens larger and move them
and their prices up a little") — PUSHED `f6f3cc7e`, live.** `python3 tools/leagues-atlantis.py` (round 2 appended; idempotent,
`done=` markers let round 1 skip what round 2 moved on). The Socials combined card's art + veil now sit in `.clipin` (inset 16 px,
radius 24 — inside the gold → green frame); outside the frame is plain #04070e. Coins `--u` .8 → .98 (156 → 191 px), the coin row
290 → 232 px, padding 150 → 130, name 24 → 27 px, price 36 → 42 px. index.html sha256 d98caccb. Batch 6 itself is PUSHED (`2193fa055`).

**2026-10-24 (overnight): AUDIT IV BATCH 6 — the medium items e32–e41 (Shaka: "do them all") + the LEAGUES ATLANTIS ART — PUSHED
`2193fa055`, LIVE-VERIFIED (tw.css v6, the gate gone, /apple-touch-icon.png 200, #/ptgc at 320 px: no sideways scroll — it was 364).** Build = `python3 tools/audit4-batch6.py` then `python3 tools/leagues-atlantis.py` (both idempotent; from
`3925eac36` the two give index.html 8db28c1c, portfolio f432811e, calculators 98b90af6, charts ee41c4e0, ledger bd5ad150; re-runs
"0 edit(s)") + `cd tools/harness && npm run css` (tw.css loses two dead utilities → `?v=6`; h2.css / h2-header.jsx `?v=4`).
**Leagues art (his kit, `design/leagues/atlantis/CLAUDE_INSTRUCTIONS.md`):** `logos/leagues/lg-atl-split.webp` (the Socials combined
card, 1560 px wide at the top, gold left → blue → green right, no tints), `lg-atl-ptgc.webp` / `lg-atl-ufo.webp` (the Leagues window
header + foot, index TierInfoModal AND portfolio PfTierInfoModal; phones crop to the token's coloured side). The whale / shark hero
images are gone from both (the creatures stay in the rows; lg-whale/lg-shark.webp left in the repo, unused). ~35 % navy over the art,
much darker behind each coin + price (his ask). Before / after PNGs were sent to him in chat. No number touched.
**e32** a Load Code / the add box keep at most 50 wallets (`PF_MAX_WALLETS`), labels 40 chars (input `maxLength`), groups 24; a code
with more says "holds N … press Load again to load the first 50" (amber) — the SAVED list is never cut. **e35** `PageBoundary` (Reload +
"Back to the dashboard") around calculators + ledger. **e36** `fmtAbbr` = index's a67 bands on calculators / ledger / portfolio (+
negatives, Infinity "—"); calculators `creatureCount` (a42); charts' header "—" (not "+0.00 %") for a missing 24 h change, calculators
`change` null; the UFO tile says "PulseScan unreachable — see Recent transactions" when every read failed; the ledger / treasury
script router strings corrected and the live UFO contract in the ledger's KNOWN_TOKENS; calculators' chain-read WETH pool
isRHCore false; the 1 + 7 calls to the RETIRED UFO LP-staking contract on every calculators UFO load deleted. **e40** usePfRanks
says `failed` (and keeps a good list over a failed 30-min re-read); the League box prints "HOLDER RANK — couldn't load … / out of
date …" instead of vanishing; the rank window's COST TODAY uses live prices (not Moon Math); days the rank index has not reached are
-1 (a gap), not "not holding", and "history to …" turns amber when the daily rebuild is behind; HOW IT WORKS says the feed is
"valued at that hour's price (not the exact fill price)". Not done (owner's call): the Ledger "PTGC Buys" vs DAO Buys chart
(M-13). **e41** the dead header-preview gate + its SHA-256 hashes deleted (treat the word as burned). The iframe sandbox and the
Worker items stay parked. **e37** 320 px: the LP sort row wraps, h2Scale floor .78, the panel titles' tracking tightens under 360
(the 📷 buttons stay inside), charts' range / preset rows wrap, "Calculators" 25 px, Home's BUY / SELL = the ⇄ icon alone under
360, Socials headers shrink; 640–900 px Affiliates Commission Log gets a right-edge fade; 32-px hit boxes on the tile badges, Edit /
Remove, the windows' ×, Top 100 copy; charts range / preset `aria-pressed`; ledger month pills `aria-pressed`, the six category
tiles keyboard toggles. **e38** favicon.png + apple-touch-icon.png (180 px from 07_Two_Color_Alien) replace the inline data: icons
on all five pages (ledger's odd icon too); ledger.html in the sitemap; preconnect on the four sibling pages; `<noscript>`;
charts.html loads html2canvas on demand (same SRI); `@supports not (container-type…)` copies of the KPI card + Top 100 phone rules;
`-webkit-backdrop-filter` everywhere; a 100vh fallback for `h-[100dvh]`; `HvbSide` / `VsFold` at module scope. Not done: the Logos
windows' thumbnails (P-4 — needs 30-odd new image files; next), lazy Chart.js (P-5 — defer already covers first paint), the Home
BUY glow animation (P-11 — design). **e34** the Live Feed does not poll while its tab is hidden (wakes on return); the UFO fees are
not re-read right after the boot read them; portfolio loads saved wallets 3 at a time; history batches 40. **e33** top-stakers reads
balanceOf only for the 110 it publishes; swap-volume re-prices the last 6 h each run; rank-history stamps the close of its last day
+ gate 24.5 h (once a day after 00:15 UTC) and writes nothing on a no-op; the watchdog parses decimal gates. Not done: one shared
RPC pool for the pipeline (D-4 — a fallback node that lags the head would make an incremental getLogs step skip blocks for good;
needs a per-script head check first) and the rank-index shard count / data branch (D-6 — c21). **e39** settled with live chain reads:
(1) `totalStaked()` = 187.46 B — the donut is right; token-allocation.json's `staked` (3.33 B, the staking contract's own balance =
the REWARD POOL) is renamed `rewardPool`. (2) burn: the archive matches `balanceOf(0x369)` exactly per day for 2023-h2 … 2025-h1 and
for Oct 13–16 2026, but OVERCOUNTS in 2026: Apr–Jun +343 M, Jul +94 M, Aug +204 M (570.7 M logged vs 366.5 M real), Sep +68 M,
Oct 1–13 +4 M — the 762 M total gap. The 7D / 30D / 90D burn windows use those rows (today 7D +12 %, 30D +6 %, 90D +21 % vs the
balance change); exact-duplicate rows explain only ~5 %. NOT changed — a formula / source decision for him (see Next up -34).
Evidence: harness — a 60-wallet code → the amber note, then 50 saved; overflow probe 320 px = no sideways scroll on Home, #/ufo,
calculators, charts, portfolio, ledger (#/ptgc's only overflow is the stub's quadrillion-dollar DAO figure); compile + ci-mount 7/7;
the Leagues renders as sent; a clean run of both scripts from HEAD = the same files.

**2026-10-23 (late night, 3): AUDIT IV BATCH 5 — the last six P1s: e26, e27, e28, e29, e30, e31 — PUSHED, LIVE-VERIFIED**
(Site check #4 + Deploy #7583 green; live: five pages `tw.css?v=5`; #/ptgc TXNS "803 B203 / S600 ↑31.2 %" = 803 vs burn-summary's Oct 22 reading 612; charts 1Y "UFO −35.33 % SINCE JUL 10"; Portfolio LOAD CODE opens as a dialog with focus in the code box, Escape closes it). Build = `python3 tools/audit4-batch5.py` (idempotent; a clean run from `fd1d5391b` = 49 edits, re-run "0 edit(s)"; it
re-splices tools/pf-v2.py + tools/top100.py) then `cd tools/harness && npm run css` (tw.css gains min-w-[40px] / min-h-[40px]
→ `?v=5` on the five pages). index.html sha256 47d1825e, portfolio c2b36baf, calculators 42db1db3, charts 290ecf08.
**e29** (his pick "Yes, DexScreener"): the TXNS 24H arrow = the live DexScreener count vs the pipeline's last DexScreener reading of
yesterday (burn-summary.json `snapshots`, UTC date) — CoinGecko's transaction-history only when that snapshot is missing. Real
data today: PTGC ↑96.6 % (CoinGecko 820 vs 417) → ↑43.6 % (DexScreener 879 vs 612); UFO ↑19.8 % → ↓12.0 %. fetchDex's price
fallback + the two hard-coded-pair price seeds use `dsPricePair` (base side only, gotcha 35). `HOLDER_SNAP_MAX_AGE_MS` = 36 h: an
older holder-history point is not "now" (fetchHolders goes live; the 7D / 30D / 90D go "—"); `nhView` gains `endOk` (the file
reaches within 3 h / a tenth of the window of now) and the Holders tile's 24 h new-holders line needs both ends. **e28** (his
pick "Flag UFO"): `seriesSinceLabel` — a token whose series starts more than max(3 h, 5 % of the range) after the range start is
labelled "since Jul 10": summary card badge, Leaderboard + Scorecard cards, the full-report card, the bars (`UFO*` + a footnote)
and the status line. 3M unaffected (UFO's data covers it); 6M / 1Y: "UFO −35.33 % SINCE JUL 10", "Live · 5/5 tokens · UFO since
Jul 10". No number changed. **e27** the Portfolio 24H pills say "24H PRICE" when the 24 h-ago holdings read is missing (the
fallback is the price change applied to today's balance); holder ranks: staleness per token from `tokens[tok].readAt` (a
carried token keeps its old readAt) — a stale token ranks nothing, the column hides only when both are; the footer prints
"PTGC list read …, UFO …". **e26** Affiliates: 25 controls keyboard-reachable — 13 sort headers (`tabIndex`, Enter / Space,
`aria-sort`), referrer rows / names / phone cards, the "▶ n" expanders (`aria-expanded`), receipt day headers, the show-more
rows (`afKey` helper); Portfolio GET CODE / LOAD CODE are `PfModal` dialogs (Escape, Tab trap, scroll lock, focus back; the
Load input autofocuses; × has a label and a 40 px target); the dead Edit Wallet window and the unused DisclaimerModal copy are
deleted. **e30** inputs ≥ 16 px under 640 px (portfolio add / search / new group / Moon Math, the Top 100 search) — iOS focus
zoom. **e31** `BsN`: a visible B / S letter + "buys" / "sells" for screen readers on the TXNS tiles (v2 + classic) and the deck
pool cards; the LP v2 rows get the words for screen readers and the Txns header "buys | sells"; `DashWhy` = the dash + an ⓘ that
opens the reason on tap (TXNS unavailable ×2, a failed burn window, an unread allocation row). **Evidence (harness):** TXNS tile
"200 B120 / S80 ↓67.3 %" (stub 200 vs the file's 612) and UFO ↑19.8 % (200 vs 167); charts 1Y cards / bars / status as above, 3M
unflagged; Portfolio Load Code → role=dialog "Load a portfolio code", focus in the input, Escape closes and focus returns to the
button; inputs 16 px at 390, 14 / 15.5 px at 1280; Top 100 search 16 px at 390; Affiliates: a name span + Enter → "Referrer
details", a sort header Enter → none → ascending → descending, an expander Enter → aria-expanded true; #/ptgc and #/ufo body text
before / after differ only by the B / S letters, the screen-reader words, the Txns header and the TXNS arrow; compile + ci-mount 7/7.

**2026-10-23 (late night, 2): AUDIT IV BATCH 4 — e14 (no page hangs on a stalled fetch), e15 (the stale-file UFO scan on
the three mint pools only), e16 (the a41 RPC pool on portfolio + calculators) — PUSHED, LIVE-VERIFIED** (Site check #3 + Deploy #7582 green; live: index 13 `dataFetch` reads + `UFO_MINT_POOL_SYMBOLS`, portfolio / calculators carry `RPC_COOLDOWN_MS`, portfolio `pfDsTokens` + `pricesLoading`; #/ptgc paints with the burn periods filled from the files (24H / 7D / 30D / 90D), calculators and a saved portfolio wallet load normally, no console errors). Build =
`python3 tools/audit4-batch4.py` (idempotent; a clean run from `693883eaf` = 21 edits, re-run "0 edit(s)"; it re-splices the Top 100
fragment via tools/top100.py). index.html sha256 21a784a2, portfolio 9f51fa14, calculators d645d568. No formula touched.
**e14** (a) portfolio: `pfDsTokens` = DexScreener with an 8 s abort for `quoteOf` / `usdOf`; `initialLoad` clears at once so the
wallet reads start before the prices land (the header's skeleton follows the new `pricesLoading`). (b) index: `dataFetch(url)` =
`fetch(url,DATA_FETCH)` + a 20 s abort covering the body — all 13 repo data reads (t1.jsx's too); PTGC's first paint no longer
awaits the six history files (`setBurnPeriods(undefined)` then seeded from `cachesP.then`, the UFO way). (c) calculators: fetchDex /
lvFetchTokenPairs / Moon Math cores through the page's `dsJson`; the coingecko read has a 15 s abort and is awaited only before the
volume windows. **e15** `UFO_MINT_POOL_SYMBOLS` = WPLS / PLSX / WETH; the browser's value-generated fallback passes only those pools
(`?debug=1` keeps all seven for its swap reconciliation). **e16** index's pool block (cooldown, -32005 rotation, `transport`) copied
verbatim into portfolio + calculators; portfolio's getLogsRange returns null on `r.transport` instead of halving. **Evidence**
(scratch harness with a request log — `DS_SLOW` / `DATA_SLOW` / `LOGS_503` / `VG_OLD` switches, not committed): portfolio with
DexScreener stalled 40 s, 12 s after load: 5 RPC posts and no wallet reads → 34 posts, both wallets read + their log scans;
`#/ptgc` with the data files stalled 30 s, at 9 s: skeleton, no price → "$0.000142 +3.21%" painted; calculators with DexScreener
stalled 60 s, at 36 s: "Loading Calculators…" → the page up with "—" prices; `#/ufo` with value-generated 5 h old: 991 RPC posts /
864 eth_getLogs / 546 Mint scans on 7 pools → 671 / 552 / 234 on 3 (data/value-generated.json: every mint is on WPLS / PLSX /
WETH); portfolio with every eth_getLogs 503: 168 log posts → 16. Normal runs: the body text of #/ptgc, calculators and
portfolio (one wallet) IDENTICAL before / after; compile + ci-mount 7/7.

**2026-10-23 (late night): AUDIT IV e13 — Token Allocation tier counts PEOPLE ONLY (Shaka chose "People only") — PUSHED, data rebuilt by his manual run
(only=token-allocation, force), LIVE-VERIFIED: the file says `tiersSource` "holder-ranks (people only)"; the live strips read PTGC
0 / 12 / 96 / 692 → 16,317 and UFO 0 / 16 / 98 / 500 → 4,373.** Build = `python3 tools/audit4-e13.py` (idempotent, 11 edits, re-run 0; index.html sha256 a58e6b82,
build-token-allocation.mjs 367a2cad). Same thresholds (% of the starting supply); only WHO is counted changes. **Builder:** the tiers
are counted over `data/holder-ranks.json` `b` (the Top 100 / Portfolio-rank people list: burn addresses, DAO wallets, every
contract, the UFO OA wallet out, PulseScan page repeats dropped); Squid & below = people − the four tiers; the file gains
`tiersSource` + `tiersAsOf`; holder-ranks missing / carried / > 12 h → the previous tiers are kept with a `::warning::`. This step
no longer pages PulseScan. **Real data (old → new):** PTGC 1 / 13 / 104 / 714 / 17,361 → 0 / 12 / 96 / 692 / 16,317; UFO
0 / 18 / 104 / 510 / 4,684 → 0 / 16 / 98 / 500 / 4,373 (the builder run against the real file wrote exactly these; a 3-day-old
holder-ranks entry → warning + kept). **Page:** the live fallback `fetchHolderTiers` (only when token-allocation.json is missing or
> 24 h old) de-dupes, skips `TIER_NOT_PEOPLE` + every `is_contract`, and takes Squid & below from holder-ranks.json's people count
(≤ 48 h; else "—", never PulseScan's address total); tier cache key `grays_tiers_v3_` (v2 retired). The tier block's hover title
says "People only…". Harness `TIER_HOLDERS=1` (burn, DAO wallet, a contract, three people, a page repeat) → "0 1 1 1 → 17,114"
(= 17,117 − 3); compile + ci-mount 7/7. **The numbers on the site change at the token-allocation step's next run (gate 6 h)** —
or Actions → Data Pipeline → Run workflow, only = `token-allocation`, force = true.

**2026-10-23 (night): AUDIT IV BATCH 3 — phone first screen (e17, e24, e25), calculators UFO share (e12), deferred CDN scripts
(e18), deploy safety net (e20–e23) — PUSHED `be68af66b`, LIVE-VERIFIED** (Site check #1 green 1m 49s; Deploy #7580 = `check` 24 s → `deploy` 32 s; Pipeline watchdog #1 run by hand, green 11 s; live: all five pages `tw.css?v=4`, boot shell + boot-fail text + `defer` on the four React pages, charts untouched; calculators on UFO at 390 read eligible 728.78B from the chain, no page-wide overflow). Build = `python3 tools/audit4-batch3.py` (idempotent;
a clean run from `db1bd3aca` = 57 edits, re-run "0 edit(s)"; it re-splices portfolio via tools/pf-v2.py) + `python3 tools/audit4-ci.py`
ON the Mac (the workflow files; 3 edits, re-run 0) + `cd tools/harness && npm run css` (tw.css 79,795 B — the calculators' `sm:` utilities —
so `?v=4` on the five pages). index.html sha256 ab0a51da, portfolio e3f4dc7b, calculators aa71e0b7, ledger cb21fa09, charts 86ce54cc.
**e17** the disclaimer window: text scrolls inside the panel, the Accept / Decline footer is pinned (max 90dvh) — Accept on screen at
390×844 (681–733), 320×647 (458–510), 768, 1380; wording unchanged, no DISCLAIMER_VERSION bump. **e24** calculators at phone width: the
two token cards stack, the amount row stacks (input full width), the Moon Math bag row wraps — before, the fee box overprinted "PTGC" and
the Split button ran 2 px past the clip at 390; after, cards 366 px, nothing past the edge at 390 / 320. (The 320-only title overflow
`span.cp-t.w` 326/320 is e37, not done.) **e25** the Leagues People / Circulating toggle is absolutely centred on the header (each label
133 px, fits at 390), and the Socials column headers at 901–1199 shrink the logos + name (`.sh-hd` media block) so "Combined" is whole at
901 and the chevron never overruns. **e12** (formula — worked example shown to him): calculators' UFO reward share used circulating − the
DexScreener LP estimate; it now uses the Portfolio's eligible supply — totalSupply − burn − the UFO contract − the excluded wallet − the 13
excluded pools (`CALC_UFO_EXCL` = portfolio's `PF_UFO_EXCL`), one batched RPC call, 10-min memory cache, its own localStorage key
`grays_calc_ufo_elig_v1`, falls back to portfolio's `grays_pf_ufo_elig` (≤ 24 h) and then to the old estimate. Live numbers: 807.23B →
728.78B eligible; a 1B bag 0.1239 % → 0.1372 % of the UFO rewards (+11 %). **e18** `defer` on the React / ReactDOM / Babel / Chart.js tags
of index, portfolio, calculators, ledger (charts.html left alone — its inline script runs at parse time). First paint on `#/ptgc` at 390
over a 1.6 Mbps throttle: 27.5 s → 3.5 s (the boot shell paints while the 3 MB of scripts download; the app itself is no faster). **e21**
every React page has a static boot shell (`data-boot`, "LOADING…") and an inline watchdog: a Babel SyntaxError, or the shell still up 20 s
after `load`, swaps the text for "This is taking longer than it should. Please reload the page — if it keeps happening, try again in a few
minutes." (amber) — instead of a black page. **e20** `tools/harness/compile.js` compiles EVERY page's inline babel + syntax-checks plain
inline scripts (exit 1); `deploy.yml` gains a `check` job (compile only, ~15 s) and `deploy` `needs: check` — a page that does not compile
is never deployed, the site stays on the last good version; `.github/workflows/site-check.yml` (push to main touching pages/harness/fragments
+ manual): compile, tw.css drift check, `ci-mount.js` mounts 7 routes in the Playwright 1.47 container (`probes/ci-mounted.js`: no
`[data-boot]`, >40 nodes, >200 chars; errors outside an ALLOW list fail). Proven: a broken portfolio copy → compile exit 1 "Unexpected
token" and the boot-fail text in the browser; the real tree → "all pages compile", ci-mount 7/7 ok. **e22**
`.github/workflows/pipeline-watchdog.yml` every 3 h (`23 */3 * * *`) runs `scripts/pipeline-watchdog.mjs` on the PUBLISHED status file:
red (→ GitHub's failure e-mail) if the last pipeline run is > 3 h old or any step has not succeeded within 2 × its gate + 3 h; a carried
step is a `::warning::`. Tested on real data (pass) and a doctored file (fail). **e23** the pipeline's silent fallbacks now print
`::warning::` (charts-data ×4, charts-intraday, pair-volume, coingecko ×3, value-generated without burn periods), and an EXISTING but
unreadable state file is fatal instead of "start from empty" (lv-snapshot, burn-history periods + holder-history, ufo-ptgc-burns) — a
corrupt file can no longer silently reset a history; the 365-row holder-history trim is gone (it threw away the oldest days). run.js:
CDN regexes accept `defer`, the mount wait needs no `[data-boot]`, and it prints an `ERRORS_JSON` line.
**After his push:** Actions shows "Site check" green on the push, the Deploy run has a `check` job before `deploy`, Pipeline watchdog →
Run workflow once → green; live: the disclaimer on a phone (clear site data or a private tab), calculators at 390, the Rewards tab's UFO
share. The first Site check run may need one look (container image pull, ~1 min).

**2026-10-23 (evening): HOLDER RANK TRIO e9 + e10 + e11 — PUSHED `db1bd3aca`, data rebuilt by his manual run (only=holder-ranks,rank-history, force; 14:43 UTC, both ok), LIVE-VERIFIED:** holder-ranks.json now `repeats` 126 / 44, 17,117 / 4,987 people, tags present; Top 100 "PEOPLE HOLDING 17,117"; real wallets, live balance ranked by the deployed pfRank vs the new index's last day: #20 / #150 / #700 / #2,000 step 0, #5,000 −6, #8,000 −1, #11,000 −4 (real overnight moves; before: +19 at #2,000, +64 at #8,000). Build =
`python3 tools/audit4-rank.py` (idempotent, 17 edits, re-run "0 edit(s)"; it edits the two builders + the pf-v2 / top100 fragments and
re-splices with tools/pf-v2.py + tools/top100.py). **e10 — the real cause, found today:** PulseScan's holder paging REPEATS the last
row of some pages as the first row of the next (its next_page_params balance is a rounded float): a fresh full read had 18,328 PTGC
rows for 18,202 unique addresses (= PulseScan's own count) — 126 repeats, UFO 44 — and `build-holder-ranks.mjs` ranked every repeat as
a person, spread evenly down the list. So every live rank below ~#150 was too low (#2,000 shown as #2,019; #8,000 as #8,065; the
1-token block +95), "PEOPLE HOLDING" was 17,255 instead of 17,117, and the rank window's live point sat that far below its own
history (chain-built, no repeats) — Audit IV's "+64 at 5k–10k" was this, not a population rule (the address diff found only 40 dust
EOAs and 0 contracts of difference). Now: de-duplicated by address (log line "N page repeats dropped", `repeats` in the file), the
98 % check counts unique addresses; and `build-rank-history.mjs` index() ranks ties the badge's way (1 + how many hold strictly
more, on the same rounded key) instead of by address. **e9:** the builder writes `t` (first 6 hex chars of every listed address, 6 per
entry, aligned with `b`; tags shared by only 6 PTGC entries, resolved by the nearest balance — 99.988 % right in a simulation of real
sellers); `pfRank(ranks,tok,bal,addr)` and the Top 100 checker leave the wallet's OWN entry out. File: 69 KB → 146 KB gz. Old file
without `t` → ranks exactly as before. **e11:** BEST EVER / LOWEST = the whole life (the chart keeps the period). **Evidence:** the new
builder against a local replay of this morning's real PulseScan pages (repeats included): 126 / 44 dropped, 17,117 / 4,987 ranked,
all 110 `top` wallets found by tag at their own balance. Real wallets, `pfRank` old file+code → new: the #50 wallet after selling 1
token #51 "pass 2" → #50 "pass 619,501"; #2,000: #2,020 "pass 2" → #2,000 "pass 22,539"; #8,000: #8,066 "pass 2" → #8,000 "pass
119". Rank-window step (history's last day → today, same balance): #2,000 +19 → 0, #8,000 +64 → −1, 1-token block +30 → +10 (real
overnight churn + 40 dust wallets). New index on the real archive: 3,709 of 17,077 last-day ranks change, all inside tie blocks.
Harness: Top 100 checker for the real #2,000 wallet at −1 token: "RANK #2,022 · PEOPLE HOLDING 17,255" → "#2,000 · 17,117"; the
Portfolio rank window LOWEST (1Y) #2,623 → life #2,909 (Mar 26, 2025) = the index's own life low. index.html sha256 08305dd1,
portfolio.html aa88ca9d. **The DATA changes only when the pipeline runs the two builders** (holder-ranks gate 2 h, rank-history
gate 20 h) — after his push: Actions → Data Pipeline (hourly) → Run workflow → only = `holder-ranks,rank-history`, force = true; or
wait. Until then the pages rank exactly as before. **Same PulseScan repeat bug, NOT fixed here (follow-up, his call — changes the
tier counts people see):** `build-token-allocation.mjs` and index.html's live `fetchHolderTiers` page the same endpoint, so the Token
Allocation tier counts (Shark / Dolphin …) include repeats too (folds into e13). Scratch: the real PulseScan pull is in the git-ignored
`Claude outputs/rank-check/` (two JSON files, safe to delete).
**2026-10-23 (afternoon): AUDIT IV BATCH P0b — e7 + e8 + e3 + e4 + e19 — PUSHED `b071ba060`, LIVE-VERIFIED** (deployed files carry every fix; live `tw.css?v=3` = the 79,763 B build with `text-purple-500/40`; the DAO panel on real data reads $100,200 total, no note, no "≥" — identical to before; a browser holding the old HTML for Pages' 10 min still asks for `?v=2`, harmless). Build =
`python3 tools/audit4-p0b.py` (idempotent; a clean run from `d6a7b13c6` = 49 edits, re-run "0 edit(s)") then `cd tools/harness && npm run
css` (committed `tw.css`, `?v=3` on the five pages). **e7** portfolio GET / LOAD CODE: UTF-8-safe base64 (`pfB64Enc` / `pfB64Dec`) — an
ASCII-only list gives the byte-identical code as before, old Latin-1 codes still load, emoji / en-dash / "✦" labels round-trip (harness:
"Cold 🚀" + "Ledger – cold" / group "Vault ✦" → a code, Copy → "✓ Copied!", node round-trip exact; a 3,000-wallet list encodes in chunks);
a code that still cannot be built says so (no empty box), Copy waits for the clipboard ("Copy failed — select the code" on a reject);
LOAD CODE over a non-empty list asks once ("This replaces your 2 saved wallets with the 1 in this code" → button "Replace 2 wallets
with 1") and drops the old queued scans. **e8** the UFO `balanceOf` is read in the PTGC batch and must pass `okWord` (and both per-lock
reads too): a failed UFO read = "1 unreadable", total "—", Retry — was a green wallet with "UFO VALUE $0.00 · 0 UFO" (harness switch
FAIL_UFO_BAL in a scratch copy of run.js, before vs after). **e3** DAO Treasury: no PLS price or no management balance → `null` ("—"
everywhere, the a16 path); lockedAmount unreadable → Available / Pending "—", total EXACT (contract balance); a failed token balance /
price or PTGC leg → listed in a visible amber note under the hero and the totals print "≥ $X" (panel, breakdown popup, share card;
the card drops its split bar). Normal path: identical figures (harness). Live DexScreener check: HEX / PLSX / INC / PTGC all have
base-side priced pools, so a healthy read never shows "≥". **e4** referrer window: rows carry the entry's `meetsThreshold` → a
below-minimum month shows "Below", "—" in Comm., and the header Comm. leaves it out (a54 fixture, bob: was "Comm: 1.60K · 1,600 ·
Unpaid" → "Comm: 0 · — · Below"; alice unchanged at 20.00K). **e19** fresh `tw.css` (79,763 B; has `text-purple-500/40` again, which
the live Affiliates receipts lacked, plus the new classes). Compile: every babel block of index / portfolio / calculators / ledger
compiles (compile.js itself still only reads the first tag — e20). Harness: portfolio 2-wallet recipe text identical before / after
except one clock-driven 30D figure; #/ptgc 390 no overflow. index.html sha256 164c833f, portfolio.html 966e614e, tw.css 7e158f9c.
**e1 + e2 LIVE-VERIFIED** (built-in browser, `d6a7b13c6`): the deployed pages carry both fixes; the real #100 PTGC wallet (0xae4d…)
in the Top 100 checker → "HOLDS 412.51M · YOU'RE IN #100 · YOUR CUSHION 7.17M" (= 412.51M − the #101's 405.34M; the old code
said ~20.5M); the portfolio's incremental UFO scan (REFRESH on the profile's one saved wallet, fetch wrapped to log) read
0x1a94836 → 0x1a94837 = head in both directions, zero `latest`, balanceOf at 0x1a94837. **NEXT: his push → Claude's live check of
p0b (DAO panel normal = no note; a portfolio with an emoji label → GET CODE; the affiliates receipts icon colour; ?v=3 live) →
Worker v8 (e5 + e6, drafted by Claude, deployed by him) → e20–e23 (deploy gate) → the rank trio e9–e11.**
**2026-10-23: AUDIT IV e1 + e2 BUILT ("fix 1 and 2") — PUSHED `d6a7b13c6`, LIVE-VERIFIED 2026-10-23 (see above).** `python3 tools/audit4-e1e2.py` (idempotent;
run twice → "0 edit(s)"; it edits `tools/top100/t1.jsx` and re-splices index.html via `tools/top100.py`, then edits portfolio.html's data
layer directly — that layer is NOT in the pf-v2 fragments, `tools/pf-v2.py` leaves it alone). **e1** `cush = k − list[99]` (was
`list[100]`): harness `T1_BAL=412485544` (= the real #100's balance, a wallet not in `top`) → "YOU'RE IN #100 · YOUR CUSHION 0",
412485545 → cushion 1, 708163209 → #50 cushion 295.68M; no overflow, no errors. **e2** portfolio.html: `getLogsChunked` /
`_getLogsChunked` take `exactTo` (index's gotcha-4 flag) and `computeUfoReflectionsWei` passes `true`, so the last slice is
`toBlock:<head>`, never `'latest'` — what the B8 cache stores as `{to:head}` is exactly what was read; and the wallet's `balanceOf`
is re-read AT block `head` (one `eth_call` with a block tag; a failed at-head read keeps the mount-time balance) so balance and the
two sums come from one block. Harness (request log): 8 `eth_getLogs`, every `toBlock` = 0x19d8360 = HEAD_BLOCK, zero `latest`; two
`balanceOf … @0x19d8360`; the cache row `{v:1,to:27100000,…}`; `#root` before vs after identical on the 2-wallet recipe (rpc 32 → 34);
`LOGS_DOWN=1` → "Reflections unavailable — the chain read failed", no cache row (a12 holds). index.html sha256 b5e78e24,
portfolio.html e80bfb78. Live check after his push: a real UFO wallet's Lifetime earned equals its pre-push value (first visit =
full scan; a reload = incremental), and in DevTools → Network the last `eth_getLogs` of the scan carries a hex `toBlock`.
**2026-10-23 (small hours): AUDIT IV DONE — `sessions/2026-10-22-audit4.md`, written to the Mac, NOT pushed; no code touched.**
His ask: "a COMPLETE audit of this entire website/application … do NOT start changing code yet … create a prioritized TODO / handoff
document". Eight parallel sweeps on a clean clone of `223de3f58` (code identical to the Mac), every number re-run against the real
`data/*.json`, ~200 harness runs (six widths, every route + window, RPC / DexScreener / PulseScan down or slow), live checks from the
built-in browser (site 200, stale `tw.css` live, `/apple-touch-icon.png` + `/ptgc` 404, Worker `no-store`, pipeline dispatched 00:15
UTC, 0 console errors) and one RPC read (`totalStaked()` 187.48B / `totalLocked()` 124.36B — the donut reads the right thing).
**SEVERE: e1 the Top 100 "Your cushion" subtracts `list[100]` where `list[99]` is the overall #101 — overstated for every top-100
wallet (the #100 wallet: prints 20.52M, truth 7.15M; one-token fix in `tools/top100/t1.jsx:161`); e2 portfolio's UFO reflections scan
sends the last slice to `latest` but caches `to:head` (no `exactTo` — gotcha 4 never reached portfolio.html) → a transfer in the gap is
double-counted for ever; e6 the Worker's `/read`/`/write` `path` walks out of ToolBox (`../../PTGC-UFO-Dashboard/contents/index.html`)
and the public read is an uncached two-GitHub-calls-per-GET fan-out on the owner's PAT; e3 DAO Treasury prints a quiet $0 / short
total when one of ~15 reads fails; e4/e5 the referrer window ignores the month's threshold verdict and the Worker compares
`thresholdType` case-sensitively + `||2` on a 0 % month; e7 GET CODE is EMPTY for an emoji label (`btoa`, third time); e8 a failed
UFO `balanceOf` is a silent 0 with a green dot.** P1 headliners: e9 holder rank ranks a seller against its own stale entry ("to pass
#50" = itself), e10 the rank window's "today" is ranked on a different population than its history (median +64 places at
5k–10k), e11 BEST EVER is period-scoped, e12 calculators' UFO share 9 % below the Portfolio's, e13 the tier counts call the burn
address PTGC's only Poseidon, e14 three pages hang on a stalled fetch with no timeout, e15 a stale value-generated.json = ~950 RPC
calls per UFO visit, e16 the sibling pages' RPC pool pre-dates a41, e17 the disclaimer's Accept button is below the fold on every
phone, e18 `defer` on the CDN tags = FCP 9.0 s → 0.8 s at 1.6 Mbps, e19 **the committed `tw.css` is stale (live-verified: the new
Affiliates receipts' `text-purple-500/40` has no rule) — `npm run css` was not committed after the Affiliates redo**, e20
`compile.js` compiles 0 bytes of portfolio/calculators (first babel tag is the `src=` one) + no CI, e22 nothing alerts when the
pipeline is never started and the `DISPATCH_TOKEN` expiry is unrecorded (30-day default → ~Nov 5), e23 five builders carry forward
without `::warning::` (status says `carried: 0`). Full list, evidence, fixes, TOP 10, quick wins, ideas and "do not change" in the
file. **NEXT: (1) show him the SEVERE list + TOP 10; (2) his picks → one idempotent `tools/audit4-p0.py` batch for the P0 tier
(e1–e8; the Worker items are a v8 by hand), harness, push, live check; (3) add the "AUDIT IV" phase (e1–e47) to the roadmap
artifact; (4) then the queue as before (Leaderboard + Receipts windows mock, F4 share link mock, the Top 100 Telegram post).**
**SIGN-OFF 2026-10-22 (night): THE AFFILIATE PROGRAM'S NEW LOOK IS LIVE — his push `ecd5621c7`, LIVE-VERIFIED (built-in browser, real
data: the hero, the bands 74 / 1,525 / 7.98B, the October podium @ptgcofficialonboard · 88Xcuto4 · DeFiMission, no overflow, no console
errors), tree clean except these notes. NEXT: (1) the Leaderboard + Payment Receipts windows in the same look, MOCK FIRST; (2) Phase F,
F4 share link, mock-up first; (3) he posts the Top 100 Telegram announcement (sessions/2026-10-22.md) if not yet.**
**2026-10-22 night: THE AFFILIATE PROGRAM PAGE'S NEW LOOK — BUILT ("make it live").** His ask: "this page is
still the old and ugly look. Can you mock up a new look?" → `design/affiliate/` (README has every decision): v1 two looks (A the Calculators
treatment / B "hall of fame") → "I like affil-v1-b-1380" + "recent activity full width, the Registry under it" → v2 + "use the logo that has
the glowing light around it like we use on the dashboard" (the h2.css corona coin) → his AI mock (`reference/shaka-ai-mock.png`) → "keep
ours as is except add some of that background artwork" → v3 (3a the gold mountain hero / 3b the Holders beam-UFO hero) → "make it live"
(no pick → 3a, the hero he had already approved). **Build = `python3 tools/affiliate-v2.py` from `tools/affiliate/af.css` (run twice →
"0 edit(s)"; the render blocks sit between `{/* AFFIL2:X */}…{/* /AFFIL2:X */}` markers so the script's fragments can be edited and re-run;
EDIT THE SCRIPT / af.css, never index.html).** What changed in `AffiliatesPage`: the hero (rank-plate sky + the dashboard's corona coin +
"PTGC AFFILIATE PROGRAM"), terms as chips, Leaderboard / Payment Receipts as the Calculators icon buttons, ALL-TIME / month as framed bands of
tiles (sea art via SeaIcon, "PAID OUT" = commissions paid; the month select stays on the green plate), NEW the month's podium (`AfPodium`, top 3
by PTGC bought on his medals, tap = the referrer card), Recent Activity / Registry fold / Commission Log as framed cards (the lists' own cells
kept; the log's rank = a CSS counter; the log's User column 20 %), the footer; his Calculators space art under the whole page (`.af-art`,
72 % veil; absolute over the top 1000 px on phones). The header is no longer sticky. `probes/affil-registry.js` matches the uppercased heads
case-insensitively (only probe change). Harness `AFFIL_DATA=real` 1400 / 1024 / 390: no overflow, no errors; a54 / card / registry probes
unchanged in substance. index.html sha256 8fafd7c2. The Leaderboard + Payment Receipts windows still wear the old look — NEXT ROUND, MOCK
FIRST. Pushed `ecd5621c7`, live-verified (above).
(`_to_delete/harness-stage.tgz` = a 16 MB assets bundle staged for the cloud harness; git-ignored, he can delete it.)

**SIGN-OFF 2026-10-22 (~17:30 UTC): TOP 100 IS LIVE AND DONE — last push `1246ec775`, tree clean except these notes.** The Token
Allocation panel's TOP 100 button (PTGC + UFO) opens `Top100Modal`: top holders (people only) and, on PTGC, top stakers; the wallet
checker (rank, tokens + $ to break in, cushion, stake-more); his beam-UFO medals on a tinted podium; STAKED (whole stake) / LOCKED
columns. Build = `python3 tools/top100.py` from `tools/top100/t1.css` + `t1.jsx` (edit the fragments, never index.html). Data =
`holder-ranks` (`top` addresses) + NEW step `top-stakers` (first CI run 16:15 UTC ok, 32 s). Live-verified after every push today.
Session file `sessions/2026-10-22.md`. **NEXT: (1) he posts the Telegram announcement (in that file); (2) Phase F, F4 share link
first, MOCK-UP FIRST.**
**Deploy lesson (2026-10-22, GitHub Actions incident 15:28 UTC on):** a queued Pages deploy sat 40+ min; an EMPTY commit pushed behind
it (`git commit --allow-empty -m "Redeploy: …"`) went through in 2.5 min while the queued one was still waiting — the deploy.yml
concurrency did NOT cancel the waiting run. When a deploy is stuck in "Queued" for a long time, an empty redeploy commit is worth a
try (Claude told him it would not help — it did).
The column change itself: PUSHED `7f7837f` as "staked, not locked", then CORRECTED on his word ("staked will
be the bigger number because to be locked you also have to be staked … a staked column, and then a locked column") — STAKED = the wallet's whole stake (locked included), LOCKED = the locked part; the bar column has no number now
(legend "■ unlocked ▨ locked"); the phone's third column reads "STAKED" (`.t1po`). index sha256 cc3acf88 — PUSHED `2bd410f` + redeploy `1246ec775`, LIVE-VERIFIED (#1 18.97B staked / 18.21B locked). The superseded note: "we show locked, but
not staked": the stakers list is # · Wallet · TOTAL STAKED (bar: gold = staked, pink stripes = locked) · STAKED (total − locked, gold
`.un2`) · LOCKED · SHARE · VALUE; grid 48 / 1.1fr / 1.55fr / 90 / 90 / 66 / 96; the phone hides the four small columns as before.
1380 / 1024 / 390 no overflow. index sha256 a7a43d6b.

**2026-10-22 evening: TOP 100 GO LIVE ("make it live!") — PUSHED `6ed7e0d12`, LIVE-VERIFIED 16:20 UTC** (fresh visitor: button, no dot, old flag gone; PTGC window 101 rows + 3 medals, a PulseScan link checked → #118, +124.40M ≈ $2,311 to break in; UFO window 101 rows, no switch; the first CI `top-stakers` run 16:15 UTC = success in 32 s). `TOP100_LIVE=true`
in tools/top100/t1.jsx (+ a one-line removal of the old `grays_t100_preview_v1` flag on load), `python3 tools/top100.py` → index sha256
9cfc7d6c. Harness: the Top 100 button shows for a plain visitor on PTGC and UFO, no dot, the window opens with the list and the
checker. Telegram announcement written in chat (post after the live check). NEXT: his push → Claude's live check (button for a fresh
visitor, window, a real wallet) → the 16:40 UTC check of the first CI top-stakers run.

**2026-10-22 evening: TOP 100 podium backgrounds — written to the Mac, NOT pushed.** "drop the background behind first place … a
background in each of the three boxes that fills the boxes … tint that matches the trophy, very faint … darken the area behind the
text": the rk-hero laurel art is gone from #1; every podium card now has his UFO-beam sky (`logos/holders/nh-sky.webp`, cover) in grey
at .32 (::before), tinted to its medal by a mix-blend colour layer (::after; gold 242,190,60 / the 2nd medal's blue beam 80,160,255 /
copper 235,120,50), and the address · amount · $ · share sit on a dark pad (`.t1pt`, radial rgba(3,4,7,.86 → .35)). Same on UFO and
the phone. index sha256 05261d98.

**2026-10-22 evening: TOP 100 AUDIT + fixes (his picks 1–5, 8–12; 6 = watch the first CI top-stakers run; 7 = go-live cleanup,
LATER — "i will let you know when to go live"; 13–17 no) — written to the Mac, NOT pushed.** Verified first: our staker sum 187.4634B =
the contract's totalStaked() 187.4645B (the list is complete). Fixed in tools/top100/t1.jsx: A1 the checker refuses the builders'
known addresses (T1_EXCL) and any contract (eth_getCode, holders view) with a plain message; A2 a checked wallet that is in `top`
has its OWN old entry taken out of the list before ranking (`t1Without`) — a sold wallet no longer counts its old self above it
(the line to beat becomes the old #101); A3 rows + podium are module-level `T1Row` / `T1Pod` and the list is one useMemo — typing no
longer remounts 100 rows (probe: the first row's DOM node survives typing); A4 `t1Copy` (clipboard → execCommand fallback), ✓ only
on success, ✕ + "Copy failed" otherwise; A5 list age: amber `.t1old` past 12 h, past 48 h a red note + ranks / tiles / list hidden
("too old to rank against"); A8 Holders ↔ Stakers re-checks the last wallet; A9 the count tile is "PEOPLE HOLDING · pools &
contracts left out"; A10 the staker cushion says how much of the stake is unlocked (locked PTGC can't drop you out); A11 equal
amounts share a rank in the list (`t1Ranks`); A12 the box takes a PulseScan link (first 0x + 40 hex not followed by more hex — a tx
hash is not mistaken for an address). Harness: run.js answers eth_getCode ('0x' unless T1_CONTRACT names the address); probe
`t1-audit.js` (window.__t1 = {addr, mode:'s', typeTest}). All scenarios green: #118 out; staking contract → left out; a contract
link → contract; link + switch to stakers re-checks; #50 at 100M → #353 with the line 405.28M; 20 h amber; 60 h hidden; copy ✓;
390 px clean. index sha256 see the build's print.

**2026-10-22 evening: TOP 100 round 4 — written to the Mac, NOT pushed.** Round 3 checked LIVE first (built-in browser, real data:
101 rows #1–#101, podium 19.18B / 14.86B / 8.91B; checker on 0xB1c0…9769 = #118 Dolphin, +124.41M ≈ $2,238 to break in; stakers view
= #95 of 3,428, +2.62M to pass #94). Then his asks: (1) NEW medals — beam-UFO 1st / 2nd / 3rd (his PNG had the transparency
checkerboard BAKED IN → keyed out by flood-filling the light, unsaturated pixels from the edges + colour-to-alpha against the nearest
checker colour in a 7 px band; split into three by empty columns; 240 px webp under the same names, T1_ART_V=2), shown at 118 px
(#1 138; phone 70 / 84); (2) "the scroll bar cuts into the corners" → the frame (`.t1m`) no longer scrolls: an inner `.t1sc` does, with
a thin token-coloured webkit scrollbar whose track has 20 px margins (Firefox: scrollbar-width thin); the ✕ stays put above it;
(3) "increase the logo size … no overlapping" → coin 125 px (--u .64, top 66), title top 212, header 300 (phone: 98 px, --u .5,
top 58, title 170, header 246) — probe `t1-hero.js` reports the switch / coin / title boxes and their gaps (14 / 21 px desktop,
11 / 14 phone, no overlaps at 1380 · 1024 · 390, PTGC + UFO). index sha256 9a4125a9.

**2026-10-22 evening: TOP 100 round 3 — written to the Mac, NOT pushed.** (1) "the leagues logo … half of it look darker": the
panel title's dark plate (`.p2 h3::before`, reaches 48 px past the title, h3 is positioned so it paints OVER static siblings) covered
the left half of LEAGUES once the pair sat close → `.t1btns` position:relative + z-index:1, and both buttons get an opaque base
(#0d0718 under the purple tint) so nothing behind shades one half; (2) Portfolio chips showed only 6 → every saved wallet;
(3) HIS 1st / 2nd / 3rd UFO medals (PTGC_UFO_Rank_Icons_Transparent.zip → `logos/top100/t1-1st|2nd|3rd.webp`, 200 px, T1_ART_V=1) replace
the round medals — 96 px (#1 112), phone 58 / 68; (4) the sea creature in the podium corners is gone. The #1 card's laurel art
mask now transparent to 12 % / solid 26–72 % / gone by 86 % (a frame line still showed); on the phone the art is height-sized
(auto 128 %) so the narrow card shows no band. index sha256 126f999c.

**2026-10-22 evening: TOP 100 round 2 (his first live look, pushed `6055c0c68`) — written to the Mac, NOT pushed.** (1) the
TOP HOLDERS / TOP STAKERS switch touched the coin → header 270 px, coin top 70, title 182 (phone 224 / 62 / 146); (2) "the list never
loaded" — the live holder-ranks.json is still from the OLD builder (no `top`) until the next holder-ranks run (gate 2 h after
14:13 UTC → ~16:15 UTC, or Actions → Data Pipeline → Run workflow → only=holder-ranks); TOP 100 HOLD now sums the first 100 of `b`
so it no longer shows "—" meanwhile; (3) the #1 card showed the laurel art's own gold frame lines → the card has its own 1.5 px gold
border + glow and the art is masked (transparent 0–6 %, solid 20–74 %, gone by 88 %); (4) "why does the stakers start at 4" — the
list now runs #1–#100 under the podium (both views). index sha256 a5ee12c8.

**2026-10-22 (later): TOP 100 BUILT — his picks B1 + Look B, HIDDEN behind the faint bottom-right dot (`TOP100_LIVE=false`), written to
the Mac, NOT pushed.** "Button B1, look B … I dont want the button live … until i say … behind a small faint dot". Build =
`python3 tools/top100.py` (run twice → "0 edit(s)"; splices `tools/top100/t1.css` + `t1.jsx` between `/* T100:CSS|JSX:BEGIN/END */`
markers — EDIT THE FRAGMENTS, not index.html; plus LS.T100_PREVIEW, the Dashboard state, the button, the mount, the dot). The dot
(`T1Dot`, same place / look as the old NhDot / VsDot) toggles the Top 100 button on THIS device (remembered in
`grays_t100_preview_v1`); the button sits right of Leagues in a `.t1btns` pair (both tighten to 8px 9px / .08em so the pair fits
beside the title at 1280–1440 — 1 px to spare at 1280; narrower it wraps as a pair, right-aligned, like Leagues alone did).
`Top100Modal` (`.t1m`, container query for the phone): rank-plate header + LgCoin + "PTGC TOP 100", TOP HOLDERS / TOP STAKERS switch
(PTGC), four tiles, CHECK A WALLET (live balanceOf / mapUserInfo → rank by binary search on the list; out: holds · rank + league · to
break in · cost today with the ⓘ snapshot card · % of the way; in: you're in · to pass #N-1 · cushion above #101; Portfolio wallets as
chips), podium (#1 in rk-hero laurels, ::before hue-rotated on UFO), list #4–#100 + THE TOP 100 LINE + the checked wallet's row.
Gotcha: the page has a GLOBAL `.sh{}` rule (Socials hub) — the podium's share line is `.t1sh`. **Data:** `build-holder-ranks.mjs` now
also writes `top` = first 110 people [addr, key] per token (the live file gets it on the next holder-ranks run, ≤ 2 h after the push —
until then the window says "the top-100 list arrives with the next data update"; the checker works off `b` already). NEW step
`top-stakers` (`scripts/build-top-stakers.mjs` → `data/top-stakers.json` + `data/top-stakers-cache.json` = known stakers + last block;
holder-ranks lane, gate 2 h, ~30 s; wired by `tools/top100-pipeline.py`, which also keeps the cache off the site in deploy.yml) — both
files seeded in this push (3,428 stakers, #100 = 271.94M). Harness: `T1_BAL=<tokens>` makes every balanceOf answer that (the "out"
state); probes `t1-check.js` (types `window.__addr`, reports tiles / result / rows / overflow) and `t1-btn.js` (header geometry).
Checked: hidden by default, dot → button → remembered across reload → dot again hides it; PTGC holders #118 state = the mock's
numbers; stakers in/out; UFO; 390 px; no overflow. Index sha256 6517ce57. **NEXT: his push → live check (dot, window, a real wallet,
the first top-stakers + holder-ranks runs) → his look → TOP100_LIVE=true when he says.**

**2026-10-22: the pipeline's first `rank-history` run LANDED** (12:16 UTC, ok; UFO meta 105 → 106 days). **NEW: the TOP 100 window — MOCKED UP, waiting on his picks.**
His ask: a "Top 100" button right of LEAGUES in the Token Allocation panel (PTGC + UFO) → a window listing the top 100 wallets, a bar to
check any address (what it holds, tokens + $ to break into the top 100), and on PTGC a toggle to TOP 100 STAKERS (how much to have
staked). Mock **`design/top100/mock-top100-v1.html`** (+ `mock-top100.js`, `mock-data.js` = REAL data read 2026-10-22,
render `mock-top100-v1.png`): button B1 (purple twin) / B2 (gold trophy, green on UFO); Look A "the deep" (Leagues sea header +
whale/shark) vs Look B "hall of fame" (rank plate, #1 in rk-hero laurels); tiles (#100 holds = the line to beat · top-100 share · #1 ·
count), CHECK A WALLET (holds · rank + league · to break in · cost today with the ⓘ snapshot disclaimer · % of the way), podium
#2/#1/#3, list #4→#100 with THE TOP 100 LINE, the "you're in" state (cushion above #101), empty state (his Portfolio wallets as chips),
stakers view (staked + locked stripes, "stake your unstaked + buy the rest"), UFO, phone 390. ASK: B1/B2, Look A/B.
**Data facts for the build:** holders need ADDRESSES — `holder-ranks.json` stores balances only, so the build needs a top-N-with-addresses
file (PulseScan holders, same exclusions). Stakers: the staking contract's `Deposit(address user,uint256)` (user NOT indexed, topic
0xe1fffcc4…109c) since block 18,543,401 → 5,137 addresses ever, 3,428 with `mapUserInfo.amount` > 0 now; #100 staked 271.94M; sum
187.46B, locked 124.33B. RPC getLogs in 25K-block chunks ×12 parallel = ~4 min; mapUserInfo single eth_calls ×40 = 30 s (JSON-RPC
batches of 100 failed on rpc.pulsechain.com; 40 worked). Prototype scripts were cloud-only (not in the repo).

## Current state (2026-10-21)

**2026-10-21 afternoon → evening: THE HOLDER RANK WINDOW + RANK HISTORY — built, written to the Mac, NOT pushed (he had to run:
"keep working on this").** His ask: click the rank badge → "a really nice window with stats on the ranking, a nice looking chart,
and period selectors" — LIFE · 1Y · 90D · 30D · 7D; the history prefilled from the chain, then recorded daily. Mock
`design/portfolio/mock-rank-window-v1.html` → "perfect!". **Data:** every real holder's balance at every UTC day end, exact.
Method (after a slow first try at 49 s/day and a replay-only try that drifted): `design/portfolio/ranks-mock/backfill-fast.mjs`
streams all Transfer events once (PTGC: 9.1M in 14 min), classifies each address once, reads ONLY the movers at each day end
(256 concurrent eth_calls, ~390/s), and carries everyone else forward by the day's REFLECTION FACTOR measured on 6 reference
holders that did not move (reflections scale every untouched balance alike — verified: 30 of 30 random wallet-days match the
chain's balanceOf exactly for UFO). `to-deltas.mjs` turns that into the archive `data/rank-history/<TOKEN>.json` (schema 2,
CHANGES only: per day {b, f, m:{addr: key|0}} — UFO 28 MB → 1 MB; a full per-day list would be ~670 MB for PTGC).
`scripts/build-rank-history.mjs` (pipeline step `rank-history`, gate 20 h, in the holder-ranks lane after holder-ranks —
`tools/rank-history-pipeline.py`) EXTENDS the archive a day at a time by the same method and REBUILDS the index
`data/rank-index/<TOKEN>/<xx>.json` (256 shards by address prefix, [firstDay, [[rank, run], …]], rank 0 = not holding) +
`meta.json`. Ties sort by address so a rank is reproducible. **Page:** `tools/pf-v2/PfRank.jsx` (new, loaded after PfTx.jsx) —
`usePfRankHist` (meta + the wallet's shard), `PfRankChart` (SVG, y flipped, gaps where not holding, buy / sell dots from Recent
Transactions, BEST marked; a narrower taller drawing under 700 px), `PfRankModal` (the Earned frame: big rank + change over the
period, BEST EVER / LOWEST / TO PASS / DAYS IN TOP 100 tiles, the chart + pills (remembered in `grays_pf_rank_per`), WHAT IT
TAKES to #N-1 / #10 / #5 / #1 with ≈ $, the foot; PTGC / UFO tabs; a wallet picker when several are counted — opens on the
badge's wallet). Every rank badge and the League-box number are buttons that open it. CSS `.pf2-rkw` at the end of pf2.css.
Harness: opens from the UFO League box with a real whale (105 real days drawn), LIFE pill, 390 px clean. **DONE while he was away:** PTGC's
whole life rebuilt (1,107 days, 9.1M transfers streamed in 14 min, 334,642 balance reads in 4 min, 18.6 min in all; 30 of 30 random
wallet-days match the chain exactly — same for UFO); the archive is written as deltas straight from the backfill (PTGC 19 MB,
UFO 1 MB); the index is schema 2 (4,096 shards by three hex chars, [firstDay, [rank delta per day]] — PTGC's biggest shard 30 KB,
was 540 KB with run-lengths); the daily step was proven by trimming UFO's last day and letting it rebuild it (same block, same
factor to all digits, same holders). All of it is on the Mac (`data/rank-history/`, `data/rank-index/` = 6,969 files, the page,
the step, the pipeline wiring). Harness: the window opens from the League box and from the breakdown badges at 1380 / 1024 / 390,
the PTGC whale's LIFE chart draws 1,107 real days (#15 → #1 in Oct 2023), no overflow. His first live look: "the window gets cut off when it pops up" — the modal lacked the other windows' centring
classes (`z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80` on PfModal) → fixed; gridlines on whole ranks only.
Then "all 5 wallets as one is useless info … if more than one wallet is selected, we shouldn't show anything on the main
dashboard, just on the per wallet breakdown" → the League-box rank line only with ONE counted wallet (`rkOne`); the "As one wallet"
pair in the breakdown's ALL WALLETS row gone too (table + phone cards). Then his AI mock of the window ("best is cut off … try and get ours to look like this one") → dressed to it: the Holders
window's gold panorama as the plate (`.pf2-rkw-sky`, UFO hue-rotated) under a dark veil, the TODAY hero gold-framed + glowing with
SVG laurels (`PfLaurel`) either side of the number, gold line icons (`PfIco`: trophy / down / bars / calendar / chart / bolt) on
the tiles and section titles, the token name gold in the title, the chart's fill solid gold → faded with a dotted grid and a glow
on the line, the end point labelled "#N" (and "· BEST" when today is the best — the old BEST label ran off the right edge; it
also flips left when near the edge), WHAT IT TAKES gold-framed with glowing bars. His second look ("best #24 … messed up", the Today box "ugly, use this background",
"a background for the overall card", tiles "so tall … empty space"): HIS TWO ART FILES in `logos/portfolio/` — `rk-hero.webp`
(gold laurel wreath + frame, the Today tile's background, number between the leaves, `center/118%`) and `rk-plate.webp` (gold-framed
mountain sky, the window's plate, `cover` at `inset:-3%` so its frame sits on the window's edge; UFO = hue-rotated); the CSS /
SVG laurels and the Holders sky are gone; ONE end-point label ("BEST #N" when today is the best, else "#N", drops below the
point at the top edge, dark stroke); the tiles no longer stretch to the hero (`align-items:start`, hero `min-height:132px`).
His third look ("two bright bars … the bottom one even covers some text", "dollar figures green in what it takes", "best is on top of
current on the chart … you can only see the 125") + "if they have 0 days in top 100 show days in top 500 … 1000 … 2500 … 5000 … 10000":
the bars were the plate art's own gold frame — cropped OUT of `rk-plate.webp` (lines at y 36 / 821, x 27 / 1746, 18 px margin,
1,600 wide, 59 KB; `cover` at `inset:0`, opacity .9, the window's own 2 px gold border is the frame now); `.lad .nd small.usd`
green #39E15A; the BEST marker is skipped when it sits within 6 % of the chart width of today's point (the end label says
"BEST #N" when today IS the best, so nothing is lost); `topN` = the first of 100 / 500 / 1,000 / 2,500 / 5,000 / 10,000 with
any days, tile "DAYS IN TOP N" (a #121 → #125 wallet shows BEST #121 and #125 as two clean labels — harness `dress6`).
He pushed that (`f2ad9e87d`) and the bars were STILL there — the recropped plate had only reached the cloud clone, never the Mac,
so the framed image went live. Now: the frame-free image is `logos/portfolio/rk-plate-nf.webp` (NEW name, so no browser cache can
serve the framed one; the old `rk-plate.webp` is left in place, unreferenced) and `.pf2-rkw-sky::after` fades the top and bottom
14 % to the window's black so nothing of the art can read as a bar. And his "there has to be some sells in there": the buy / sell
dots NEVER drew — `r.t` from Recent Transactions is already milliseconds and the window multiplied by 1,000, so every dot fell
off the chart → fixed, one dot per day per kind (harness: 30 buys + 30 sells drawn on the bot wallet's 90D). The dots cover what
Recent Transactions has loaded (a year or 20 pages back, buys / sells only — a send to a person or a move between his wallets
is not a dot, same as the list's typing). He pushed; the dots were live (checked in the browser: 88 on 0xe4bb…e4e6's 1Y) but
"took a long time" (the list reads up to 20 pages per wallet per token) → his call: "default the chart to NOT show buys and
sells.. a box they can check.. and a loading while it loads" → DONE: a `show buys & sells` tick in the chart legend (off EVERY time
the window opens — his "always default to off.. even on refresh" — nothing remembered); ticked → the in / out swatches, a gold spinner "reading your transactions…" while
Recent Transactions is still reading pages (`txs.busy`), "none in this period" when done and empty. And his "should sends be
added, because they can send tokens out, which would lower their rank" → yes: a dot is any row that changed the balance —
IN (green): buy, receive, claim, move in; OUT (red): sell, send, move out; unstakes left out (staked PTGC is already in the
balance); a move between two of his wallets is read from the row's `cp` for the other side; one dot per day per direction,
nudged apart when a day has both; the tooltip names the type. Harness: 7D on the bot wallet ticks → Claim / Move out /
Receive + Sell (same day, two dots) / Sell; 390 no overflow. Also his "the logos are not next to the names" in the breakdown's table header: the page's base CSS makes every img
display:block, so each token logo sat on its own line above the label → the header cells are a flex row (`th .h`: logo, then the
name, right-aligned; PENDING TO CLAIM on two lines). Then "a percentage complete on the reading your transactions … anything
to make it faster without breaking anything?" → the spinner shows **N%** = how much of the chart's period the list has read back
to for THIS wallet + token (`txs.cov[addr|tok]`, the time the list is complete back to; LIFE = a year, as far as the list goes),
and it stops as soon as the period is covered — a 7D chart is done after page 1, it no longer waits for all 20 pages of every
wallet. Faster: `txs.prioritize(addr,tok)` (PfTx: `tell()` now also carries `jd` per-job done flags + the hook) — ticking the box
moves that wallet + token to the front of the deep-page queue and skips the wait-for-scroll before phase 2. PulseScan's page
reads stay 2-wide (it rate-limits). Harness with SLOW_SCAN=6000: "reading your transactions… 13%" on 30D after page 1, gone
once page 2 landed, no errors. The tick is OFF every time the window opens (his "always default to off.. even on refresh";
nothing remembered). Then "to the right of the address, show all the sea creatures of what that wallet is" → `mock-rank-league-v1`
(A one chip for the window's token / B both tokens' leagues / C the whole ladder) → **B**: two chips in the header's `.sub` — the
wallet's PTGC league and its UFO league with the League box's sea art (`pfLeague` + `pfSea` from PortfolioV2.jsx), the window's
token lit (`.lgc.on`, UFO green), the other quiet, a token not held gets no chip; hover = % to the next league + need. Harness
1200 PTGC / UFO tabs + 390 clean. Evening: his screenshot of Duhawks (0xd376…762d: #12 all year, dumped 3.6B → 11.6K on Oct 18,
now #8,469) — "it's just a straight line … something must be off on the scale": the data was right, the scale was not — on a
1 → 9,500 linear axis #12 and #1 are the same pixel. Now the chart is LOG when the period spans ≥ 8× in rank (`logS` in
PfRankChart; gridlines = the period's best, three 2-significant-digit steps, the worst — "#12 #62 #320 #1,600 #8,469"), linear
with whole-rank gridlines otherwise; and the BEST marker is skipped only when today IS the best or best sits within 6% of the end
at nearly the same height (Duhawks keeps its BEST #12 beside the #8,469 end label). Harness: Duhawks 1Y / 30D / LIFE, a normal
wallet's 90D unchanged. Later that evening his add: "a bit of a calculator in WHAT IT TAKES — put in any rank, it tells you how
many tokens you need and the price" → `mock-rank-calc-v1` (A a ladder row / B a sentence strip / C a block with tiles) → C, then
`-v2` ("I WANT TO BE RANK" + an ⓘ hover disclaimer, the rank box centred under its label) → BUILT: `.ctl` under the ladder in
PfRank.jsx — the box (`want` state, digits only, placeholder = half your rank), tiles TOKENS TO BUY (`list[n-1] − pfRankKey(bal) + 1`,
same maths as the ladder), COST TODAY (× price, green), YOU'D BE A (`pfLeague(bal+need)` → sea art + name + % to the next); messages
for a rank at/below yours ("that's you" / "you're already above #N"), past the list ("the list ends at #17,253"); the ⓘ's card on
hover / focus: "Cost is a snapshot … slippage and the price rising while you buy aren't included". CSS `.pf2-rkw .ctl`, `.ii`;
2 columns under 860, 1 under 480. (Gotcha again: the base CSS makes img display:block — the sea art in the tile needed
inline-block.) Harness 1200 + 390 clean. portfolio.html sha256 d8501938…
**ALL OF IT IS LIVE — his last push today is `8976af399` (the calculator; working tree clean at sign-off). Live check of the calculator on 0xe4bb…e4e6: #50 → 358.09M PTGC, $6,496, Shark 12.5% to Whale. Claude's live check in the browser
after it: the window opens from the League box on 0xe4bb…e4e6, header "PTGC SHARK · UFO SHARK", the tick off, the frame-free
plate, no errors (a first load showed the previous build — his browser / the CDN cache; a cache-busting reload showed the new one,
so if he reports something "still there" after a push, check the live file with `fetch(…,{cache:'no-store'})` before touching code).
NEXT when he is back: (1) confirm the pipeline's first `rank-history` run landed (gate 20 h → ~2026-10-22 ~05 UTC; `only=rank-history`
forces it; look for a commit touching data/rank-history + data/rank-index, then the window's foot "history to <yesterday>");
(2) he posts the two Telegram pieces (the launch post + the breakdown-screenshot caption, both in sessions/2026-10-21.md);
(3) Phase F (F4 share link, mock-up first).** Known limits: the window needs a wallet in the index (a wallet that first
held AFTER the last archive day shows "Not enough days" until the next daily run); "as one wallet" has no history (the window
opens on the first counted wallet with a picker); the buy / sell dots reach as far as Recent Transactions does (a year or 20
pages per wallet + token).**Afternoon 2026-10-21: HOLDER RANK LIVE (`270f1a5d9`), then trimmed on his word — written to the Mac, NOT pushed.** His live look
("why does it say out of 12,244 … there are over 18k holders"; then "lets not show the Of the part.. Just their ranks, and more
needed to pass … dont exclude dust wallets"; then "remove the top 1000 and top 100 badges"): (1) **dust counts** — the 1-token floor
is gone; `build-holder-ranks.mjs` keeps every balance above zero, stored as whole tokens from 1 up and to 6 decimals below 1
(`key()`; the page's `pfRankKey` rounds the same way); re-run 13:38 UTC: PTGC 17,253 ranked, UFO 5,025, 156 KB, on the Mac;
(2) **no "of N", no "top x%", no TOP 10 / 100 / 1,000 badges** anywhere — badge = token + #rank + "▲ N more to pass #N-1", H3 row =
label + #rank + the same; rank #1 says "Nobody above you"; a dust gap prints decimals (`pfPassAmt`); the foot line no longer counts
holders ("Ranks count every wallet holding PTGC or UFO, except …"); the `.pf2-md` CSS removed. Harness 1380 / 1024 / 390 clean.
portfolio.html sha256 `0dd6a29c`. **PUSHED and LIVE-VERIFIED** (built-in browser, three real wallets): the column, chips,
sorts, H3 "ALL 3 WALLETS AS ONE #9 ▲ 233.34M more to pass #8", foot line; a hand count from PulseScan's live holder list (people
only) matches 5 of 6 ranks exactly — PTGC #14 / #17, UFO #43 / #105 — and the sixth (#137 vs #136) is a holder just above who
moved after the list was read (the wallet's own stale entry was below its live balance, checked). Known limit: a wallet that SOLD
since the list was read can sit one place low (its own old entry still counts above it) until the next 2-hour refresh — fixing it
needs addresses in the file. **Then the badge look (his ask: "more of a badge … something that looks cooler" → five loud ones `mock-rank-badge-v1`
("no too loud.. b3 is the closest") → four quiet plaques `-v2` + "I like the Holder Rank word… like in B4" → `-v3`): HE PICKED P2 for
the League box line — no pill, "HOLDER / RANK" stacked in tiny caps beside a big gold / green number (`.pf2-rk3 .p2`, 24 px
Orbitron); with one wallet the line has no other label, with several "ALL N WALLETS AS ONE" sits in front. The breakdown + phone
badges keep the live pill but are labelled "PTGC RANK" / "UFO RANK" (`mock-ranks-bd-p2.html`, "do it"). Built, harness clean at
1380 (1 and 2 wallets) and 390, portfolio.html sha256 `0bde650f` — written to the Mac, NOT pushed. NEXT: his push → live glance →
Phase F, F4 share link mock-up first.

**2026-10-21 (Wednesday): HOLDER RANK — decisions made, the data side BUILT, the page side waiting on his OK of the phone mock.**
Morning: his 2026-10-20 push (`2b63c386f`) live-checked (v2 only, no dot / classic footer, two real wallets read, Load Code /
Leagues / Edit wallet open, the old `grays_pf_v2_preview` key removed on load, no errors). "go for it" on Claude's picks: **G2
one-line badges** in the breakdown column, **H3 with 2+ wallets = "ALL N WALLETS AS ONE · #N"**, **people only** (every contract,
the burn, the token contracts, the DAO wallets + DAO contract, the UFO OA wallet left out), **floor 1 whole token**. Staking check
DONE: the eight biggest stakers' `balanceOf` ≥ their `mapUserInfo` amount (e.g. 19,178M balance / 18,966M staked) — staked and
locked PTGC stays in the wallet, so ranking by balance is right; the staking contract's 3.31B is the reward pool. **Built:**
`scripts/build-holder-ranks.mjs` → `data/holder-ranks.json` (schema 1: per token `holders`, `listed`, `left{known,contracts,dust}`,
`readAt`, `b` = whole-token balances high → low; a failed token carries the previous list with ::warning::, both failing = exit 1);
first real run 13:10 UTC: PTGC 18,344 rows → 12,244 ranked in 205 s, UFO 5,364 → 4,942 in 57 s, 111 KB (the file is on the Mac so
the page has data at go-live). `tools/holder-ranks-pipeline.py` put it in the pipeline: step `holder-ranks`, gate 2 h, its OWN lane
(4th), the yml's `only` list + Commit list. Phone mock `design/portfolio/mock-ranks-phone-v1.html` (breakdown cards: the two badges
between the share bar and the amounts, "more to pass" wraps under; "as one wallet" under ALL WALLETS; the H3 line wraps) — his OK
("i think so"). **THE PAGE SIDE BUILT — written to the Mac, NOT pushed:** `PfLeagues.jsx` end = `usePfRanks` (reads
`data/holder-ranks.json`, re-reads every 30 min; a list > 48 h old is `stale` → no ranks), `pfRank` (binary search on the LIVE
balance, whole tokens), `PfRankBadge` (G2), `PfRankRow` (H3); `PortfolioV2.jsx`: `PfLeague` takes `rankRow`, the cards pass
"HOLDER RANK" / "ALL N WALLETS AS ONE"; the breakdown gets the HOLDER RANK column (`.pf2-bdt.rk`, fixed widths 13/41/11/11/10/14),
best-rank header chips, PTGC rank / UFO rank sorts, "As one wallet" in ALL WALLETS, the badges in the phone cards (`.pf2-rkm`), the
foot line (`.pf2-rkfoot`; "hidden: the list is out of date" when stale); `pf2.css` end = the rank CSS + **below 1,150 px the
breakdown is the wallet cards two across (one under 700)** — the table with the rank column spilled at 900–1,100 px. Harness
(2 / 1 wallet, stub balances): squeeze scan clean at 1380 · 1280 · 1180 · 1150 · 1100 · 1024 · 900 · 700 · 480 · 390, no sideways
scroll, no errors; stale file → no column + the note; missing file → the page exactly as before. portfolio.html sha256 `515fdfbb`.
**NEXT: his push → the pipeline's first `holder-ranks` run (gate 2 h; the committed file is from 13:10 UTC) → Claude's live check
with real wallets (ranks match a hand count from PulseScan; tablet / phone).**

## Before that (2026-10-20)

**NOT PUSHED at the end of 2026-10-20: the Portfolio cleanup round (below) + the holder-rank mock-ups + these notes.** One push
covers it all (the line is at the end of `sessions/2026-10-20.md`); then Claude's live check of portfolio.html.

**HOLDER RANK PER WALLET — MOCKED UP, HIS LAYOUT CHOSEN, BUILD TOMORROW (2026-10-21) ("save that to the handover and we will
work on making it live tomorrow").** People asked "where does my wallet rank among holders (not counting LP wallets)". He wants it
PER WALLET (people have several), PTGC and UFO each, in the **Per-wallet breakdown**. Three mock rounds
(`design/portfolio/mock-ranks-v1/v2/v3.html`, renders `renders/ranks-v*-1380.png`): v1 A/B/C → "I like C" (rank + top % + TOP 10 /
100 / 1,000 badge + "▲ N more to pass #N-1" + PTGC rank / UFO rank sort buttons + the ALL WALLETS row ranked "as one wallet" + the
header chips "Best PTGC rank / Best UFO rank") but "the layout needs to change"; v2 D strip / E in-column / F cards → "I don't like
those either"; **v3 = his idea: the HOLDER RANK badges in their OWN COLUMN right after the wallet — Wallet · Holder Rank · PTGC ·
Pending · UFO · Total.** G1 (two-line badges) vs G2 (one-line, "more to pass" at the right end, rows near today's height) NOT yet
picked — Claude recommends G2; ASK FIRST THING. Plus the CARDS: H3, the rank row in the League box (below). Also owed before
building: the PHONE mock of both (he wants a mock-up before every build).
**Tomorrow's order:** (0) his push of 2026-10-20 + Claude's live check of portfolio.html; (1) ask G1 / G2 and the 2+-wallets
question for H3; (2) the staking check (below); (3) the pipeline step + `data/holder-ranks.json`, run once by hand; (4) phone
mocks of the breakdown column + the H3 row → his OK; (5) build both (`tools/pf-v2/*` + `python3 tools/pf-v2.py` twice), harness
(1380 → 390 squeeze scan, ranks against a stub list), push, live check with real wallets.
**Build plan:** (1) a pipeline step `scripts/build-holder-ranks.mjs` → `data/holder-ranks.json`: page PulseScan
`/api/v2/tokens/<t>/holders` for both tokens (measured: UFO 5,324 rows ~95 s, PTGC 18,195 rows ~7 min — fine hourly, or every 2–3 h
in its own lane), drop burn (0x0 / 0x…369 / 0x…dead), the token contracts, LP POOLS (production rule: any contract answering
`token0()`; ~1,080 PTGC + 334 UFO holders are contracts, many are pools not in our lists — the mock dropped every contract), the UFO OA
wallet (`PF_UFO_EXCL.wallets`); keep balances ≥ 1 token (12,114 PTGC / 4,906 UFO today); store the sorted balances (whole tokens,
compact) + counts + generatedAt. (2) the page: rank = 1 + count of listed balances strictly above the wallet's LIVE balance (binary
search) — live for the visitor, the list up to an hour old; "more to pass" = the balance just above − yours + 1; as-one-wallet = the
same on the sum. (3) **CHECK FIRST: is all staked / locked PTGC still in the wallet's balance?** The classic code says so
(`walletFree = balance − uiAmount`, `totalHolding = balance`) but the staking contract 0xC71f…39EF holds 3.31B PTGC — if any staked
PTGC sits there, stakers rank too low and their stake must be added back (and the staking contract is then not a "holder").
(4) the foot line: "Rank among N PTGC and N UFO holders (wallets holding at least 1 token). Left out: liquidity pools, the burn
addresses, the token contracts, the UFO OA wallet. Your balance is read live; the holder list is refreshed hourly · list read N ago."
**Also mocked (his ask, same evening): the badge on the PTGC / UFO
CARDS when ONE wallet is counted** — `design/portfolio/mock-ranks-single-v1.html` (built from his screenshot's numbers, 3.88B PTGC =
#12, 18.04B UFO = #7): H1 a HOLDER RANK pill under the price · H2 a third tile beside Total holdings / Lifetime earned · H3 a rank
row inside the LEAGUE box with "more to pass" · H4 a spotlight inside Earned by source (fills PTGC's empty space; under the
"Paid to your wallet" panel on UFO) with a mini ladder #11 / YOU / #13. **HE PICKED H3** ("H3.... add that to the notes … for
when we make it live"): under the league bar in each card's LEAGUE box (`.pf2-lgb`, after `.pf2-lgbf`), a row split by a hairline —
left "HOLDER RANK" caps label + the rank in Orbitron (gold on PTGC, green on UFO) + "of 12,114 · top 0.10%" + the TOP 10 / 100 /
1,000 badge; right "▲ 4.49M more to pass #11". Mock CSS = `.rk3` in `mock-ranks-single-v1.html`. Still open: with 2+ wallets
counted, hide the row or show "ALL N WALLETS AS ONE · #28" — ASK. Prototype scripts: `design/portfolio/ranks-mock/` (README there; `mock_single.py` + the card
markup `cards.html` for this one). Open questions he has not answered: DAO treasury / bridges / CEX
wallets in or out (mock: in, unless a contract); the ≥ 1 token dust floor.

**Later 2026-10-20: THE PORTFOLIO CLEANUP ROUND — written to the Mac, NOT pushed.** "yes please" → `tools/pf-cleanup.py`
(idempotent) took the classic body (~570 lines), the pfV2 state + toggle, `PfV2Dot`, `PF_V2_LIVE` / `LS_PF_V2` / `pfV2Saved`, the
dot's CSS, the classic footer and seven classic-only leftovers out (portfolio.html 4,331 → 3,722 lines; a device still holding
`grays_pf_v2_preview` has it removed once); `tools/pf-v2.py` rewritten to just the sync (135 → 57 lines, the dead wrap / dot /
guard steps gone). Proof: from a clean main the two scripts rebuild the identical file (sha256 `deebd5b6`); the harness `#root`
markup before vs after differs only in clock-driven figures at 1380 and 390 px; Load Code / Leagues / Edit wallet windows open the
same; no errors, no sideways scroll. **NEXT: his push → Claude's live check of portfolio.html (v2 renders, no dot, the three
windows) → the HOLDER RANK build (above: G1 / G2, phone mock, then build) → Phase F, F4 share link mock-up first.**

**2026-10-20 (Tuesday): the Volume window's 7D / 30D / 90D "—" FIXED — `tools/vol-windows-fresh.py`, written to the Mac, NOT
pushed by Shaka as `b2d76a06d`, LIVE-VERIFIED.** His screenshot: 24H filled, the three windows and the Today-vs-averages bars "—". The page read `coingecko-data.json`
once per page life and gates it at 12 h, so a tab open overnight blanked them on its next load() and never recovered. Now the
file is re-read every 15 min and the 5-min refresh re-gates the windows (`cgVolWindows`). Harness-proven (stale → recovers;
missing → "—"). Live: the ⓘ shows all four figures on PTGC + UFO, a forced re-read + Refresh keeps them. Portfolio v2 live check DONE (3 real
wallets: cold ~17 s, no console errors, no failed requests, no "Live price unavailable", 1Y chart continuous, no sideways scroll
at the pane's 446 px). `sessions/2026-10-20.md`. **NEXT: the rest of the 2026-10-16 plan below — the CLEANUP round (classic
body out of portfolio.html) when he says, then Phase F mock-ups starting with F4.**

## Before that (2026-10-16)

**2026-10-16 (Friday): PORTFOLIO v2 IS LIVE — `bc8e60b8b` "Portfolio v2 GO LIVE + B8".** `PF_V2_LIVE=true` (set in
`tools/pf-v2/PortfolioV2.jsx`, synced into portfolio.html by `pf-v2.py`, which now REFUSES to run if the two disagree), the dot is
gone, every visitor gets v2; B8 (UFO reflections scan cached per wallet in `grays_ufo_refl_v1:<addr>`, incremental after the
first visit) shipped in the same push. Live-verified from the built-in browser with two random current-UFO holders: cold
full scan = cached incremental (635.74M lifetime earned), no console errors, no dot. Announcement copy + six screenshot
captions written in chat (random PulseScan wallets in the shots). `sessions/2026-10-16.md`.

**NEXT (agreed with Shaka at the end of 2026-10-16, in this order):** (1) let the page breathe a day or two and fix what real
wallets surface — watch for PulseScan slowness on the first cold read, the "Live price unavailable" note (DexScreener), 1Y chart
gaps; (2) the CLEANUP round: strip the classic body, `PfV2Dot` and the preview flag out of portfolio.html and simplify
`tools/pf-v2.py` (steps 3–5 and the guard become dead) — no mock-up needed, nothing visible changes, but a big diff, so after
the quiet period; (3) Phase F one at a time, MOCK-UP FIRST — he approves every visual before it is built — in this order:
F4 share link (`?code=`), F3 since-last-visit, F1 cost basis & P&L (from the buys in Recent Transactions; wants a few days of real
data first), F2 CSV export, then F5 goals / F6 lock calendar / F7 local alerts. The held `Claude outputs/pf-golive-friday.tgz`
is history; `Claude outputs/_to_delete_portfolio.r43.html` can go.

## Before that (2026-10-15)

**2026-10-15 (Thursday): PORTFOLIO v2 rounds 29–47 — polish day, all pushed by him (last `e05c99caf`), STILL HIDDEN behind the dot.**
Morning: B8 explained and parked ("we will wait on that"). Then polish, every visual from a mock-up he picked: the wallets panel +
"YOUR HOLDINGS" heading (29, his C), the Details loader over the chart while PulseScan reads + the ledger dressed like the page
(30), the UFO share audited on chain — the reward-eligible supply excludes burn, the token contract, the UFO OA wallet and 13
PulseX pools (`PF_UFO_EXCL`, `pfUfoEligible`, `tools/ufo-reward-excluded.py`; 23.2 % → ≈31.6 %) — and the READY TO CLAIM spotlight
under Earned by source (31, his C), the UFO spotlight to match + the period-change loader + day headers in the feed + lock header
+ "read N ago" stamps + the 30D change on the Total tile (32–34), Recent Transactions rolled into a bar like the breakdown (35),
"Reflections last 7 days" row instead of the excluded-address list (36–37, "I like the reflections last 7 days"), fonts up (38),
the mid-width squeeze fixes with a new `probes/pf2-squeeze.js` scan at ten widths (39), Audit II (`PORTFOLIO-ROADMAP.md` "Audit II"
P/R/S tables; 40–42 knocked out, R2–R4 closed by a live measurement: 103 PulseScan reads, 1.26 MB localStorage, 1Y chart no gaps,
~50 s cold for 22 wallets), the DAY BY DAY buttons (42), the Day-by-day loader on a period change (43), the two fold bars dressed
up — icon tile, live chips, gold SHOW (44, his A with B's button). Late: "Clear" → "Deselect all" in the wallets toolbar (45); the Total tile's 24H / 30D changes as two tinted pills (46, his A of mock-total-v1); the three value tiles with bigger art + number, a facts line, a share bar and a footer (47, his A of mock-tiles-v1). Harness recipe for every round in `tools/harness/README.md`;
decisions in `design/portfolio/README.md` rounds 29–44. **Classic body unchanged all day** (round 44's classic hash equals round
43's). **He said: "I am not going to go live until tomorrow, Friday."**

**NEXT (Friday 2026-10-17, only when he says go):** (1) his hard-refresh look on Chrome / Safari / iPhone with the dot on; (2) unpack
`Claude outputs/pf-golive-friday.tgz` on the Mac (the same tar loop as a round, then `python3 tools/pf-v2.py` twice — it holds
round 47 + B8 + `PF_V2_LIVE=true`, already rebuilt on the last round — if anything else ships first, rebuild it again, recipe in `sessions/2026-10-15.md`), commit "Portfolio v2 GO LIVE + B8"; (3) live check with the test wallets
`0x5f203BD7c8453eF8B812635fc3cDAcecae7b9ed5` and `0xEC1904931777ff32f30f939D6D278cb28F30a03e` — UFO reflections equal before /
after (B8 must not move the number), no dot, v2 for a plain visitor, `grays_ufo_refl_v1:*` written; (4) update this file. If any
hidden round ships before that, REBUILD the package on it (`sessions/2026-10-15.md`, corrected splice recipe). After go-live:
keep the classic body one round, then Phase F ideas one at a time, MOCK-UP FIRST. `sessions/2026-10-15.md`.

## Before that (2026-10-14)

**2026-10-14 (Wednesday): PORTFOLIO v2 rounds 17–28 — all built, pushed by him (last `0f39d5c5c`), STILL HIDDEN behind the dot.**
Morning: Recent Transactions as an activity feed (his pick B of `mock-tx-v1`), bigger fonts, the chart's trade dots → an activity
strip, UFO old+new contract as one Reflections box, the per-wallet breakdown rebuilt, a 30-day "Details" window for Earned by
source (mock approved: "awesome. lets build it"; scroll bar, BOTH tab default, avg/day beside DAILY, big loader, dressed tiles).
Then a **full audit + roadmap** (`handover/PORTFOLIO-ROADMAP.md`) and its phases in order: A fixes (round 23), B performance
(24), C polish (25), D accessibility (26), E cleanup (27 — shared constants in PfLeagues.jsx, dead code out, the build script's
`JSX_A1` marker so it is idempotent again). Evening, round 28: the strip bars are hover / click targets — tooltip + a DAY
WINDOW (`PfDayModal`, rows shared with the feed via `PfTxRow`), bar labels fixed to the trades' own day; the wallet deck shrunk
to 7-across mini tiles with a Value / Name / Added sort (his pick A of `mock-wallets-v2`). Classic body hash unchanged all day
(`probes/pf2-classic-hash.js` → 215506704 with no PF_STAKE, no preview flag). Live checks on ptgc-ufo.com with the two test
wallets (`sessions/2026-10-14.md` has the numbers). He asked "anything left besides making it live?" — answer: nothing required;
**NEXT, only when he says: (1) the go-live checklist in PORTFOLIO-ROADMAP.md (hard-refresh test Chrome / Safari / iPhone,
10-wallet cold load, `PF_V2_LIVE=true`, remove the dot, keep the classic body one round, update this file); (2) B8 faster UFO
load — best in the same push as go-live since both touch classic; (3) Phase F ideas (F1 cost basis & P&L, F2 CSV/PDF export,
F3 since-last-visit, F4 `?code=` share link, F5 goals, F6 lock calendar, F7 local alerts) one at a time, MOCK-UP FIRST — he
approves every visual before it is built.** `sessions/2026-10-14.md`, `design/portfolio/README.md` rounds 14–28.

## Before that (2026-10-13)

**2026-10-13 (Tuesday): THE PORTFOLIO PAGE REDESIGNED — step 1 BUILT and HIDDEN, written to the Mac, NOT pushed.** His mock-up →
mock v1–v4 + a three-option sheet for the wallets area (he picked A, wallet cards) → "Lets BUILD BUT … hide it behind a small faint
dot". `tools/pf-v2.py` (idempotent, sha256 `b1442380…`): the new body (`PortfolioV2`) renders from the classic body's own state;
the faint dot flips a device to v2 and back (remembered); classic byte-identical with no flag (`probes/pf2-classic-hash.js`).
Value History + Recent Transactions are "Coming next" panels. **NEXT: his push + his look (click the dot at the bottom-right of
the Portfolio page, Mac then phone); then step 2 — the value history from real balances read from the chain (option C — he
chose it after learning option A would hide sells), the 24 h change + tile sparklines from it, Recent Transactions; PLS
balances still unanswered. Go-live = `PF_V2_LIVE=true` when he says.** `sessions/2026-10-13.md`.

## Before that (2026-10-08)

**2026-10-08 (Thursday): the Socials → Combined → "Combined KPI Report" row showed the new `KpiCardV2` pair and then flipped to the
2025 `TwitterCard` share image once UFO's data landed (`startInTwitterMode`, the 2026-10-05 "share image only from the Socials row"
decision). Fixed: the row opens the two new cards side by side like the menu's KPI Report + ADD UFO; nothing opens the TwitterCard
any more (its code stays, unreachable — clean up or rebuild in the new look if he asks). Harness probe `probes/kpi-combined.js`
(README line). `sessions/2026-10-08.md`. Written to the Mac, NOT pushed, NOT seen live.**

## Before that (end of 2026-10-07)

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
`tools/audit3-p5b.py` swapping the references — PUSHED `1201aa916`, live-verified (no broken images, 27 WebP requests, logo at 512).
**DexScreener's public API went down ~20:05 UTC** (pairs:null everywhere; dexscreener.com itself fine) — the dashboard printed "—"
per a14; Shaka asked twice, the distinction explained. **The 20:07 run on the batch-4 runner:** `data/pipeline-status.json` live — 9 ok,
3 skipped, 1 failed (pair-volume: the outage, named), value-generated last; `PTGC.ath` 0.00132623 written. THEN BATCH 6 ("keep
working"): c30 + the Liquidity "chain · core pools only" note + the calculators "$0" cap — **includes the URGENT fix for the Leagues
window not scrolling on phones since c13 (M-11)** — PUSHED `7cfa416d8` 20:29 UTC, live-verified. **DAY CLOSED by Shaka ~20:35 UTC**
("so should we wrap up?") with DexScreener's API still empty (he reproduced it: `search?q=SOL` → `pairs:[]`); the dashboard
repopulates by itself when it returns. 28 of 65 audit items shipped in six pushes; only the handover notes are uncommitted. Live looks: ALL DONE by Claude in the browser (see below). The UFO day-90 real test: the first
value-generated run after 18:39 UTC (the launch burn was 18:38:55 UTC, so the 17:13 run still printed the old d90).** Shaka's live look at
Humans vs Bots: "loks good i think"; the Telegram wording handed to him to post. His screenshot of the old "Volume Analytics" modal
("still a dated look… Mock it up for me to see first") → mock v1 (`design/volume-analytics/`) → "that looks great, lets make the logo
Bigger. and then make it live." → built by `tools/volume-window.py`: the Humans vs Bots shell with the dashboard's own banner as the
plate (gold half PTGC / green half UFO), the lit coin at 140 px, "PTGC Volume", 7D / 30D / 90D pills, four framed period tiles (24H
lit, per-day averages on the windows), Today vs averages as bars with an "avg" tick, a daily volume chart and a By pool table from
`swap-volume.json` (same `fetchSwapVolume` as HvB), the honesty line. Honest states verified (DS_DOWN → "—", file missing → Retry).
Commit line + harness detail: `sessions/2026-10-07.md`. **The TXNS 24H item is CLOSED — nothing to fix** (the tile reads 40 = the
chain's 39; yesterday's 10,761 was DexScreener's bad h24 count on one pair, passed). **NEXT (a fresh session): confirm DexScreener came back (numbers on the tiles, pair-volume green on the next hourly run); then
c16 (the small kpi-history file — also lets lv-snapshot go hourly), c21 (the orphan data branch), c10 (needs his wallet test), the
look list c32–c37 with mock-ups, and the product ideas c50–c65 for him to pick from;
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
   the page; bump `tw.css?v=` on the five pages when it changes (Pages caches 10 min). And: tw.css is
   linked BEFORE each page's inline `<style>`, so an inline rule of equal specificity now beats a Tailwind
   utility on the same element (the play CDN used to append its CSS last and win) — the Leagues window's
   `.lg-m{overflow:hidden}` vs `overflow-y-auto` was the one case the audit had flagged (M-11, fixed in
   batch 6); write the behaviour you want into the inline rule, never rely on a utility to override it.**
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

- **The pipeline's RPC goes through `scripts/rpc-pool.js` (2026-10-24, D-4).** Never `fetch('https://rpc.pulsechain.com', …)` in a
  new script — `rpcPool.poolFetch({attemptMs, body})` (CommonJS: `require('./rpc-pool.js')`; ESM: `import rpcPool from
  './rpc-pool.js'`). The pool's head check is what makes a fallback safe for incremental scans: name the block (hex `toBlock`,
  the block tag on eth_call) — a call on 'latest' cannot be checked. Rank-index shards are 2 hex chars since D-6 (meta.shard).
- **Windows are history entries (2026-10-24, e44).** index's `useDialog` and portfolio's `PfModal` push a same-URL history entry;
  a window that closes itself while it is the current entry calls `history.back()`. A new overlay that does not use `Modal` /
  `useDialog` / `PfModal` gets no Back behaviour — use them.

## Next up (in order)

-42. **BURN ADDRESS label + overlay chart + 1Y default (2026-10-24 night) — BUILT, NOT pushed.** His push → Claude's check: the live
   strip reads "1 THE BURN ADDRESS" (PTGC) / "17 INCL. THE BURN ADDRESS" (UFO); the dot's window opens on 1Y, Sharks, BOTH.
-41. **DONE — pushed `92a8ae65` (one data-file conflict with the hourly run, kept ours).** Was: **BURN WALLET as Poseidon + TOKENS HELD + bigger logo (2026-10-24 late evening) — BUILT, NOT pushed.** His push → Claude's check:
   the strip on ptgc-ufo.com shows Poseidon 1 with a 🔥 (UFO: the 🔥 on Whale); the next token-allocation run keeps `burnIn`; the
   League History dot → cards show "hold …", TOKENS HELD toggle works; the `league-history` step stays ok (schema 3).
-40. **LEAGUE HISTORY — BUILT hidden (2026-10-24 evening), NOT pushed.** His push → Claude's check: the dot on ptgc-ufo.com opens the
   window with the file's numbers; the next pipeline runs show `league-history` ok (a no-op until ~00:15 UTC, then it adds Oct 24).
   GO LIVE when he says: `LEAGUE_HISTORY_LIVE=true` in tools/league-history/lh.jsx → `python3 tools/league-history.py` → push (the dot
   goes, the Token Allocation creature strip becomes the button with "HISTORY ›"). Optional later: a Tall card shape.
-39. **DONE — mock-up v1 approved ("Thats awesome... Lets build it"), see -40.** Was: **LEAGUE HISTORY window — mock-up v1 shown 2026-10-24, waiting for his notes** (`design/creatures/README.md`, renders in
   `design/creatures/renders/`). His picks so far: all 8 leagues, cards + one big chart, joined / left, Starting / Circulating,
   share card, PTGC + UFO. Data = the rank-history archive walked day by day (real, people only, matches the strip). Build after
   his OK: a `data/league-history.json` output in the rank-history step, the window (module scope, PfModal-style dialog), the strip
   as its button, the card (screenshot-only, Wide + Tall?).
-38. **DONE — pushed `36377545`, live-verified (lazy Chart.js, h1, skip link, panel names); pipeline + rank reshard checks still owed.** Was: **Roadmap + D-4 + D-6 + e42/e44/e45/e46 + P-5/P-11/M-13 (2026-10-24 afternoon) — BUILT, NOT pushed.** His push → Claude's
   checks: (1) the next Data Pipeline run is green and no step slower (a "rpc pool:" line only if the primary failed); (2) after
   ~00:15 UTC Oct 25 data/rank-index/PTGC has 256 files + meta `shard: 2` (or Run workflow only=rank-history force=true now);
   the rank window still draws; (3) dao-buys.json `tokenPaidBuys: 3`, July = 6 buys; (4) live: #/ptgc boots with no chart.umd.js
   request, DAO Buys window draws; Back closes a window on a phone; the skip link on Tab. Left: e43 (names / one gold — his "later",
   mock-up first), e5 / e6 (Worker v8, parked), the share link F4 (he said no for now).
-37. **DONE — pushed `aa7eebd75`** (combined holder rank, Ready to claim at 0, rank crash fixes). Was:
   **Combined holder rank + Ready to claim at 0 + the two rank crash fixes (2026-10-24 day) — BUILT, NOT pushed.** His push →
   Claude's live look: Portfolio with 2+ wallets (the League rows, the window's "All N combined"), one wallet unchanged, a wallet with
   nothing staked (the 0 box). Wording "ALL N WALLETS COMBINED" is a one-line swap (`rkLabel` in PortfolioV2.jsx) if he prefers his
   "If all wallets were combined". Then the -36 list's "next work".
-36. **DONE 2026-10-24 day — VERIFIED:** cache schema 4, v1 PTGCbyUFO 4,366.92 M, value-generated ptgcBurnedAll 318.13 M
   method all-legs (its 30D 148.18 M = the v2 file's 30D), burn-summary reconcile ok PTGC + UFO (13:52 UTC), the 14:15 run 0 failed,
   live #/ufo "PTGC BURNED BY UFO" 4.69B, index.html 391de7b0 with grays_ptgc_by_ufo_pre_v2. (PTGC 7D 164.5 M — the window moved.) Was:
   **START OF NEXT SESSION — verify the 2026-10-24 burn pushes landed in the data (Shaka: "You can check tomorrow").**
   Pushed today: `f2d25262` (burn archive v2 + cards round 5, VERIFIED), `7815732b` (Logos thumbnails, live; PTGC-burned-by-UFO
   v4), `ecc9d1fe` (fee legs counted). Check on origin/main: (1) data/ufo-ptgc-burns-cache.json `schema: 4` and
   ufo-ptgc-burns.json byContract.v1.PTGCbyUFO.totalBurned ≈ 4,366.9 M (+ a little new) — the v4 migration runs on the first
   gated (6 h) ufo-ptgc-burns run after 21:16 UTC Oct 23; if pipeline-status shows it failed, read lastError (an unreadable
   receipt makes the migration retry — all-or-nothing). (2) data/value-generated.json delivered.ptgcBurnedAll ≈ 318.1 M+ and
   delivered.ptgcPreWindow.method = 'all-legs'. (3) burn-summary.json PTGC.archive.reconcile.ok true (and UFO). (4) live
   ptgc-ufo.com: index has grays_ptgc_by_ufo_pre_v2; #/ufo "PTGC burned by UFO" headline ≈ 4,685 M; #/ptgc burn 7D ≈ 190 M.
   Then the next work: D-4 (shared RPC pool with a head check), D-6 / c21 (rank-index shard count / data branch), P3s e42–e47,
   P-5 lazy Chart.js, P-11 BUY glow, M-13 Ledger vs DAO Buys. Tokens: "ptgcapi pipeline dispatch" has NO expiry (Shaka checked
   2026-10-24) — the ~Nov 5 worry is closed; "saucer-claude" (expires Nov 4) is not used by this site. Worker v8 (e5/e6) still
   parked by him.
-35. **Burn archive v2 + home cards round 5 (2026-10-24) — PUSHED `f2d25262`, VERIFIED (see Current state).** His push (promptly — the first run
   re-reads from the rebuild's last block) → check the pipeline's burn-history log + `PTGC.archive.reconcile.ok` → live look at the
   #/ptgc burn windows (7D ≈ 190 M) and the cards. e39 burn: DONE by this. Then: P-4 thumbnails, D-4 pool with a head check, D-6 / c21,
   (DISPATCH_TOKEN: no expiry — closed. fetch-ufo-ptgc-burns.js: fixed in v4, see -36.)
-34. **AUDIT IV batch 6 + Leagues Atlantis art (2026-10-24) — BUILT, on the Mac, NOT pushed.** His push → Claude's live look (the
   Leagues window + Socials card, 320 px pages, the favicon on iOS). **Decision for him (e39 burn):** the archive overcounts PTGC burns
   in 2026 (see Current state) — options: (a) find and drop the extra rows (needs tx hashes in the archive — a rebuild of 2026 with
   `h`), or (b) compute the 24H / 7D / 30D / 90D windows as balanceOf(0x369) now − at the window start (archive eth_call, 4 calls an
   hour in the pipeline). Show him the numbers first. Then: P-4 thumbnails, D-4 pool with a head check, D-6 / c21.
-33. **AUDIT IV batch 5 (2026-10-23 late night) — e26–e31 — PUSHED, LIVE-VERIFIED.** His push → Claude's live look (TXNS
   arrow vs burn-summary, charts 1Y "since Jul 10", Portfolio Load Code Escape, the B / S letters). That closes every P1. Left:
   e5 / e6 (Worker v8, parked), then the P2s (e32–e41) and P3s (e42–e47).
-32. **AUDIT IV batch 4 (2026-10-23 late night) — e14, e15, e16 — PUSHED, LIVE-VERIFIED.** His push → Claude's live look
   (portfolio paints wallets with prices arriving after; #/ptgc / calculators / portfolio unchanged on a normal load). Next by
   tier: e26+ (P1/P2 — see the audit file's list); e5 / e6 (Worker v8) still parked.
-31. **AUDIT IV e13 (2026-10-23 late night) — tier counts people only — PUSHED, data rebuilt, LIVE-VERIFIED.** His push → Run workflow
   only=`token-allocation` force=true (or wait ≤ 6 h) → Claude's live check (token-allocation.json `tiersSource` "holder-ranks
   (people only)", PTGC strip 0 / 12 / 96 / 692 / ~16.3K). Left: e5 / e6 (Worker v8, parked), then e14+ by tier (e14 stalled
   fetches with no timeout, e15 the stale value-generated RPC burst, e16 the sibling pages' old RPC pool).
-30. **AUDIT IV batch 3 (2026-10-23 night) — e17, e24, e25, e12, e18, e20, e21, e22, e23 — PUSHED `be68af66b`, LIVE-VERIFIED.** His
   push → the checks in Current state (Site check green, deploy's `check` job, run Pipeline watchdog once) → Claude's live look. Left
   from the P0/P1 list: e13 (tier counts — his call: people only vs every address), e5 / e6 (Worker v8, parked), then e14+ by tier.
   The DISPATCH_TOKEN expiry (~Nov 5) is now caught within 3 h by the watchdog — but renew it before then anyway.
-29. **AUDIT IV rank trio e9 + e10 + e11 (2026-10-23) — PUSHED `db1bd3aca`, data rebuilt, LIVE-VERIFIED.** His push → Run workflow
   only=`holder-ranks,rank-history` force=true (or wait ≤ 20 h) → Claude's live check (holder-ranks.json has `t` + `repeats`, PEOPLE
   HOLDING ≈ 17.1K, a real wallet's badge = its rank-window history's last day). Follow-up: the same de-dupe for the tier counts (e13).
-28. **AUDIT IV batch P0b (2026-10-23) — e7, e8, e3, e4, e19 — PUSHED `b071ba060`, LIVE-VERIFIED.**
   **Worker v8 (e5 + e6) PARKED by Shaka 2026-10-23 ("I dont want to mess with new keys right now").** When picked up: ask first whether
   ToolBox reads / saves anything outside `data/` (v8 whitelists `data/*.json`); no third "public read" token — GitHub's 5,000/h is per
   user, the 60 s Worker cache is the fix. Still worth one look without changing anything: the DISPATCH_TOKEN expiry date (30-day
   default → ~Nov 5). His push → Claude's live check → Worker v8 (e5 + e6) → e20–e23 → e9–e11. Open P0: e5, e6 (the Worker).
-27. **AUDIT IV e1 + e2 (2026-10-23) — BUILT by `tools/audit4-e1e2.py`, PUSHED `d6a7b13c6`, LIVE-VERIFIED.** His push → Claude's live check
   (above) → the next P0 picks (e3–e8).
-26. **AUDIT IV (2026-10-22 night) — `sessions/2026-10-22-audit4.md`, written to the Mac, NOT pushed; nothing built.** e1–e47
   (8 × P0: Top 100 cushion, UFO reflections `exactTo`, DAO Treasury silent $0, referrer-window verdict, Worker rate/threshold
   edges, Worker path traversal + uncached public read, GET CODE empty on emoji, silent 0 UFO balance). Order of work: the P0 batch
   (`tools/audit4-p0.py`, idempotent) → the deploy gate (e19 `npm run css`, e20 compile.js + CI, e21, e22 watchdog + token expiry)
   → the rank trio (e9–e11) → the rest by tier. Each item names its raw finding; formula changes (e1, e2, e9–e13) carry an old → new
   worked example — show him before building.
-25. **AUDIT III batch 6 (2026-10-07) — PUSHED `7cfa416d8`, live-verified (the Leagues window scrolls at 375).** c30 (M-4, M-8, M-9,
   M-10, M-11, M-12 colours, M-13, M-16) + the Liquidity tile's "chain · core pools only" line when DexScreener is out + the
   calculators Market Cap "—". **M-11 is urgent: the Leagues window stopped scrolling on phones when c13 put tw.css ahead of the
   inline styles.** tw.css `?v=2`. Not done from c30: the deck label sizes (M-12's 8–9 px — his layout), M-14 / M-15 (product).
-24. **AUDIT III batch 5b (2026-10-07) — PUSHED `1201aa916`, live-verified.** c15: the 16 plates
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
   phase).** Batches 1–6 shipped on the day (see -19 … -25). Remaining: c10 (needs a wallet test), c16, c21 → the look list
   c32–c37 → platform c38–c43 → product c50–c65.
   Done: c1–c8, c11, c25 (-19); c23, c24, c26, c27 (-20); c9, c28, c29, c31 (-21); c17, c18, c19, c20, c22 (-22); c12, c13, c14 (-23);
   c15 (-24); c30 (-25). Left: c10 (needs a wallet test), c16, c21, the look list c32–c37, platform c38–c43, product c50–c65.
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
- `sessions/2026-10-23.md` — Audit IV fixes: e1 + e2, batch P0b e7 / e8 / e3 / e4 / e19, the rank trio e9–e11 (all pushed, live-verified); batch 3 e17 / e24 / e25 / e12 / e18 / e20–e23 (built).
- `sessions/2026-10-22-audit4.md` — Audit IV: the merged e1–e47 list (P0–P3, TOP 10, security / mobile / performance / data sections, quick wins, ideas, do-not-change) and the eight raw sweeps (S, N, M, D, R, P, U, V) with evidence. No code changed.
- `sessions/2026-10-22.md` — TOP 100: mock-ups, the build (holders + stakers, the checker), four look rounds, the audit, go-live, the stakers columns, the Telegram post.

- `sessions/2026-10-16.md` — Portfolio v2 GO LIVE + B8 (`bc8e60b8b`): the flip, the live check with two random UFO holders
  (cold = cached), the announcement copy.
- `sessions/2026-10-15.md` — Portfolio v2 rounds 29–47 (polish day): wallets panel, loaders, UFO share audited on chain, the
  spotlights, the Recent Transactions bar, Reflections last 7 days, squeeze fixes, Audit II, DAY BY DAY, the fold bars. The held
  Friday go-live package (round 44 + B8) and its corrected splice recipe. Still hidden; go-live Friday on his word.
- `sessions/2026-10-14.md` — Portfolio v2 rounds 17–28: the activity feed, strip, Details window, the audit + roadmap and its
  five phases, round 28's day window + mini tiles. Still hidden; go-live / B8 / Phase F wait for his word.
- `sessions/2026-10-13.md` — Portfolio v2 step 1 (mock v1–v4, the wallet cards, hidden behind the dot) and step 2 (value history
  from chain balances, Recent Transactions, rounds up to 16).
- `sessions/2026-10-07.md` — the Volume window (mock v1 → built, `tools/volume-window.py`, pushed `43fb8af46`) and the RH Cores window
  (mock v1 → built, `tools/rh-cores.py`, pushed `1119ec37f`), the hub's RH rows (`tools/rh-socials.py`, pushed `2c3d15d4c`); Audit III (→ `2026-10-07-audit.md`, pushed `822e2a78e`, roadmap AUDIT III phase); the P1 batch c1–c8 + c11 + c25 (`tools/audit3-p1.py`, pushed `d60b83082`); batch 2 c23 + c24 + c26 + c27 (`tools/audit3-p2.py`, pushed `d8b1c6a2f`); batch 3 c9 + c31 + c28 + c29 (`tools/audit3-p3.py`, pushed `742b07829`, live-verified in the browser); batch 4 the pipeline c17 + c18 + c20 + c19 + c22 (`tools/audit3-p4.py`, pushed `468c308a5`); batch 5a c13 + c12 + c14 (`tools/audit3-p5.py`, tw.css, pushed `685bad0b4`, live-verified); batch 5b c15 (21 WebP files, `tools/audit3-p5b.py`, pushed `1201aa916`); the DexScreener outage + the first run on the new runner; batch 6 c30 + the liquidity note (`tools/audit3-p6.py`, commit line); the TXNS 24H item closed; HvB live look ok.
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

