# The Grays Dashboard — Handover

Living status file for work on this repo. One entry per working session lives in
`handover/sessions/`. This file is the summary: what's true now, what's done, what's next.
Update it at the end of every session.

- Live site: https://ptgc-ufo.com (GitHub Pages from `main`, `deploy.yml`)
- Roadmap + tick-off backlog (Claude artifact, shared state): "Grays Dashboard Roadmap"
  in Shaka's Claude artifact gallery — 58 items across five phases.
- Repo layout: `index.html` is the whole app (React 18 + Babel-standalone + Tailwind play
  CDN, compiled in the browser). `scripts/` + `.github/workflows/` are the hourly data
  pipeline that writes `data/*.json`. `calculators.html`, `charts.html`, `portfolio.html`,
  `ledger.html` are separate pages.

## Current state (2026-09-08)

| Area | Status |
|---|---|
| Phase 0 — wrong numbers / crashes | **Done, deployed** (17 items) |
| Phase 1 — build step (Vite) | Not started (deliberately deferred) |
| Phase 1 — dead code (b3) | **Done, deployed** (641 lines) |
| Phase 2 — data quick wins (d2, d3, d6) | **Done, deployed** |
| Phase 2 — burn-summary staleness label (d4, browser half) | **Done, deployed** |
| Phase 2 — `ufo-ptgc-burns` generator repoint (d4, pipeline half) | **Done in repo, awaiting push + first Action run** |
| Phase 2 — precompute UFO scans (d1) | **Done in repo, awaiting push + first Action run.** `build-value-generated.mjs` now also writes `burnPeriods.UFO` and `delivered.ptgcBurnedAll` (+ a `ptgcPreWindow` checkpoint). With a fresh file a UFO visit makes ~30 RPC calls and 0 `eth_getLogs` (was ~150/63 fresh, ~1,100/1,010 stale). |
| Phase 3 — share cards (u2) | **Done in repo, awaiting push.** One `ShareCardModal` shell; 13 cards on it; real PNG download (2×) + Web Share; portrait-phone fit; Escape/focus/scroll-lock. |
| Phase 3 — rest (Modal wrapper u1, jargon u7, mobile u8, a11y u9, …) | Not started |

## Sources of truth for numbers

- **Prices / liquidity / volume**: DexScreener, with on-chain reserves as fallback.
- **Burn totals**: `balanceOf(0x369)` on chain.
- **PTGC burn windows (24H/7D/30D/90D)**: `data/burn-summary.json` (hourly, `update-burn-history.yml`).
  Shown with an amber "as of" label after 6 h, as "—" after 7 days.
- **UFO burn windows**: `data/value-generated.json` → `burnPeriods.UFO` when <3 h old, otherwise a
  live chain scan. `burn-summary.json`'s UFO section still describes the OLD contract
  (`fetch-burn-history.js` line 31) — never use it for UFO.
- **UFO Value Generated**: `data/value-generated.json` (hourly, `build-value-generated.yml`); the
  browser falls back to a live scan when the file is >3 h old.
- **PTGC burned by UFO** — always OLD + NEW contract, headline and period boxes alike (Shaka's
  explicit intent). Three sources, combined in `computePtgcBurnedByUfo` in `index.html`:
  v1 (retired contract) lifetime from `data/ufo-ptgc-burns.json` → `byContract.v1`;
  v2 (live) from the on-chain delivered scan + a checkpointed pre-window scan, with the file's
  `byContract.v2` as fallback.

## Gotchas — read before editing

1. **SRI hashes.** The `<script>` tags for React, ReactDOM, Babel and Chart.js carry
   `integrity` hashes. Change a version → regenerate the hash or the page goes blank:
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
6. **`ufo-ptgc-burns.json` schema 2**: `PTGCbyUFO` is now the COMBINED total across both UFO
   contracts; `byContract.v1` / `byContract.v2` split it. The deployed `index.html` reads
   `byContract.v1` as the historical base. Do not deploy the new generator with an older
   `index.html`, or the headline double-counts v2.
7. **`Dashboard` is not keyed by token on purpose.** The Socials tab switches token and then
   opens a share modal on the same instance; a remount would drop the modal. The token-switch
   race is handled inside `load()` with `loadCancelled` guards instead.
8. **Testing.** There is no test suite in the repo yet (roadmap b8). The working method so far:
   compile the `text/babel` block with the exact `@babel/standalone@7.26.4` in Node, then mount
   the page in headless Chromium with the CDN scripts served from the pinned npm packages and
   the data APIs stubbed (RPC, DexScreener, PulseScan; real `data/*.json`). Walk Home → PTGC →
   UFO → Live Feed → KPI, plus RPC-down and DexScreener-down runs. That harness lives in the
   Claude session, not the repo — porting it into `tools/` is on the list.

## Next up (in order)

1. Push and run "Build Value Generated" manually once (Actions → workflow_dispatch). The log's
   last line should say `lifetime pTGC by UFO v2: … (exact) | UFO burn periods: fresh`.
   Then the live UFO dashboard's burn tiles should appear instantly (no "Loading") with a small
   "as of Xm ago" label once the file is >1 h old.
2. (Done 2026-09-08) "Fetch UFO PTGC Burns" ran: v1 4.59B, v2 148.9M, combined 4.73B ✓.
3. Phase 2 leftovers, all small: d5 (return scan errors instead of `lastLogError` global),
   d7 (one constants block), d8 (dead mcap rescale), d9 (vol windows nulled on spikes),
   d10 (UFO ATH is the old contract's), d11 (holder-tier scan cancellation), d12 (affiliates coverFee).
4. Phase 1 build step (b1/b2) when ready — biggest payoff on the list; decide hosting first
   (currently GitHub Pages, so `vite build` → `dist/` → Pages from `dist` or from a `gh-pages` branch).
5. Phase 3 polish: first-timer clarity (u7 tier labels + ⓘ explainers; u8 mobile nav overflow,
   tap targets), then the general Modal wrapper (u1) for the non-share modals, then a11y (u9).

## Session log

- `sessions/2026-09-08.md` — review, roadmap, Phase 0, dead code, data quick wins, generator repoint.
