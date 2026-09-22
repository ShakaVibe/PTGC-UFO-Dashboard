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
- Repo layout: `index.html` is the whole app (React 18 + Babel-standalone + Tailwind play
  CDN, compiled in the browser). `scripts/` + `.github/workflows/data-pipeline.yml` are the
  hourly data pipeline that writes `data/*.json` (ONE workflow since 2026-09-17, a29; `deploy.yml`
  is the only other workflow). `calculators.html`, `charts.html`, `portfolio.html`,
  `ledger.html` are separate pages.

## Current state (end of 2026-09-22)

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

**Deployed and verified live** (`73580760b`, Pages 14:24:40 UTC): the affiliates page renders the
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
u1 + u9 pushed as `5c2d3cf93` (2026-09-09); a header
tweak (`96afb0ed8`, PLS ratio / X's stats inline from 1024px) landed after the last
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
| Phase 3 — share cards (u2) | **Done, live** |
| Phase 3 — clarity + mobile (u7, u8) | **Done, live.** Tier labels under the creature emojis deliberately NOT done (Shaka) |
| Phase 3 — loading shell (u12) | **Done, live** |
| Phase 3 — Modal wrapper (u1), a11y (u9) | **Done, live** (`5c2d3cf93`, 2026-09-09) |
| Phase 3 — u10 (rename Socials Hub) | **Dropped** — Shaka wants the tab name kept |
| Phase 3 — u4 (hoisted render-defined components), u13 (chart late-data) | **Done** (2026-09-13 evening) |
| Phase 3 — u5 (one Value Generated model), u6 (share-card parity) | **Done** (2026-09-14 night; `computeValueGen`, see gotcha 16) |
| Phase 3 — u11 (Live Feed render cost), u14 (versioned localStorage) | **Done** (2026-09-16; `DeckRow`/`DeckScanline`/`DeckPods`, `LS` table — gotcha 18) |
| Phase 3 — u3 (decomposition) | Not started — waits for the build |
| Phase 4 — product ideas (g1–g6) | Not started |
| Phase 4 — g7 Buy/Sell via switch.win | **Done, live** (2026-09-13; three commits, ticked on the artifact) |
| **Affiliates API (`ptgcapi` worker, outside this repo)** | **Was 500ing site-wide, fixed 2026-09-20 (worker v4).** GitHub's contents API stops inlining a file over 1 MB (`200 OK`, `"content": ""`), and `data/affiliate-commissions.json` in `ShakaVibe/ToolBox` grew past it — `atob("")` → `JSON.parse("")` → "Unexpected end of JSON input" → 500, which also killed the worker's own cron sync silently. v4 reads via `Accept: application/vnd.github.raw` (no ceiling) and writes compact JSON. Source: `handover/ptgcapi-worker-v4.js` — the ONLY copy outside the Cloudflare editor; deploy is dash.cloudflare.com → Compute (Workers) → ptgcapi → Edit code. Still latent: `btoa()` dies on a non-Latin1 username, and nothing prunes that file. **Cron: `0 8 * * *`, daily 08:00 UTC** (dashboard → Settings → Trigger events; index.html mirrors it in `AFFILIATE_SYNC_UTC_HOURS` — change both together). **Two things to know before trusting its timestamps (2026-09-21):** the sync writes to GitHub only `if (newTxCount > 0)`, so `monthlyLogs[m].lastSyncDate` is when the data last CHANGED, never when it was last checked — a quiet week leaves it a week old with nothing wrong; and `getPublicCommissions` builds `publicData` from `referrers`/`monthlyLogs`/`receipts` only, so the `lastAutoSync` the sync writes never reaches the page. A real "last checked" needs a heartbeat that does not re-upload the 692 KB file (KV, or a tiny separate file) — see `sessions/2026-09-21.md`. **2026-09-22: `jsonResponse` sends NO cache headers** — no `Cache-Control`, no `ETag`, no `Last-Modified`, verified live — so any proxy between a viewer and the worker may hold one copy of that body indefinitely with nothing able to revalidate it. One line (`'Cache-Control': 'no-store'`) fixes it for every consumer; needs a manual paste in the Cloudflare editor, NOT done. Also still on `*.workers.dev`, a shared hostname this project does not control; a Workers custom domain (`api.ptgc-ufo.com`) would put the numbers on the same domain as the page. |
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
   stage it from a NEW path under outputs/ — re-using the first path re-sent the first snapshot.)
4. If a pipeline script changed, run it once by hand: Actions → "Data Pipeline (hourly)" → Run
   workflow → `only=<step>` (step names are in the workflow's `only` description; `force=true`
   ignores the file-age gates).

## Sources of truth for numbers

- **Prices / liquidity / volume**: DexScreener, with on-chain reserves as fallback.
- **Burn totals**: `balanceOf(0x369)` on chain.
- **Pipeline cadence (measured 2026-09-18)**: GitHub delivers the hourly cron ~5×/day (gaps 2–5 h), every run
  green. The site's thresholds assume that: value-generated live-scan fallback after 6 h, burn-summary amber
  after 8 h. Expect ~5 "data: hourly pipeline" commits a day, not 24.
- **PTGC burn windows (24H/7D/30D/90D)**: `data/burn-summary.json` (hourly, the burn-history step of `data-pipeline.yml`).
  The burn archive behind it is `data/ptgc-burns-<year>-h1|h2.json`, half-years derived from the date (a30) —
  never add a period to a list; a file past 80 MB logs a warning, GitHub refuses 100 MB.
  Shown with an amber "as of" label after 8 h, as "—" after 7 days.
- **UFO burn windows**: `data/value-generated.json` → `burnPeriods.UFO` when <6 h old, otherwise a
  live chain scan. `burn-summary.json`'s UFO section still describes the OLD contract
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
   (loading-state) runs. Rebuild
   `tw.out.css` (`npm run css`) after editing `index.html` or new Tailwind classes won't exist.
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
11. **Loading is a shell, not a spinner.** `loading` in `Dashboard` only covers the first
   DexScreener/RPC round-trip. While it is true the header/nav render with `Sk` bars and the tab
   body is `DashboardSkeleton`; Home uses `HomeCardSkeleton`. Both skeletons copy the real
   containers' classes so nothing moves when data lands — if you change a tile's padding or line
   height, change the skeleton too (measure with `SLOW=9000` in the harness).

## Next up (in order)

-2. **Affiliates, waiting on a reply (2026-09-22).** The page fix is live and verified; nothing more
   is worth building until one affected referrer answers two questions: does his own username appear
   in the raw endpoint text, and what does `#/affiliates` show him on the new build - real numbers
   (resolved), the error screen (a page-context block; an onboarding line, not a DNS migration), or
   still `0.00` (the interesting one - impossible from a missing payload on this build, so it would
   mean a different bug or a different site; get a screenshot). Cheap and unblocked meanwhile: the
   one-line `'Cache-Control': 'no-store'` in the worker's `jsonResponse`, by hand in the Cloudflare
   editor. Full reasoning: `sessions/2026-09-22.md`.

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
0b. **Account hardening, unfinished** — GitHub 2FA is SMS-only. Next: passkey added, SMS removed,
   recovery codes saved, collaborators/tokens reviewed, `main` ruleset, registrar 2FA
   (`security-buy-sell-2026-09-14.md`, "Do" list). Ask Shaka where he got to.
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
- `sessions/2026-09-14.md` — g8 follow-up: `DaoCreatures` (Grays tiers via `getBurnC`) in the
  "PTGC bought" tile, Recent-buys ledger box (last 10, +10, table on sm+, stacked list on
  phones). Harness ran in the cloud workspace (no Chromium on the local VM).
