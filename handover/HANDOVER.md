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
| Phase 2 — precompute UFO scans (d1) | Partly covered by the generator change (lifetime pTGC-burned now comes from the file); the fee/burn-period scans are still browser-side |
| Phase 3 — decompose + polish | Not started |

## Sources of truth for numbers

- **Prices / liquidity / volume**: DexScreener, with on-chain reserves as fallback.
- **Burn totals**: `balanceOf(0x369)` on chain.
- **PTGC burn windows (24H/7D/30D/90D)**: `data/burn-summary.json` (hourly, `update-burn-history.yml`).
  Shown with an amber "as of" label after 6 h, as "—" after 7 days.
- **UFO burn windows**: read live from chain — `burn-summary.json`'s UFO section still describes the
  OLD contract (`fetch-burn-history.js` line 31). Don't use it for UFO.
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
4. **`ufo-ptgc-burns.json` schema 2**: `PTGCbyUFO` is now the COMBINED total across both UFO
   contracts; `byContract.v1` / `byContract.v2` split it. The deployed `index.html` reads
   `byContract.v1` as the historical base. Do not deploy the new generator with an older
   `index.html`, or the headline double-counts v2.
5. **`Dashboard` is not keyed by token on purpose.** The Socials tab switches token and then
   opens a share modal on the same instance; a remount would drop the modal. The token-switch
   race is handled inside `load()` with `loadCancelled` guards instead.
6. **Testing.** There is no test suite in the repo yet (roadmap b8). The working method so far:
   compile the `text/babel` block with the exact `@babel/standalone@7.26.4` in Node, then mount
   the page in headless Chromium with the CDN scripts served from the pinned npm packages and
   the data APIs stubbed (RPC, DexScreener, PulseScan; real `data/*.json`). Walk Home → PTGC →
   UFO → Live Feed → KPI, plus RPC-down and DexScreener-down runs. That harness lives in the
   Claude session, not the repo — porting it into `tools/` is on the list.

## Next up (in order)

1. Push this session's changes and run the "Fetch UFO PTGC Burns" workflow manually
   (Actions → workflow_dispatch). First run scans the v2 contract from 2026-07-08 (~270 log
   chunks + ~150 receipts). Check the summary in the job log: v1 lifetime should match today's
   4.59B; v2 lifetime should be in the low hundreds of millions.
2. Verify on the live site that "PTGC Burned by UFO" still reads ≈ v1 + v2 (≈ 4.73B on Sep 8).
3. Phase 2 remainder: move UFO's fee scan and burn-period scan into `build-value-generated.mjs`
   (d1) — that's what removes the ~1,000 `eth_getLogs` a cold UFO visit still makes.
4. Phase 1 build step (b1/b2) when ready — biggest payoff on the list; decide hosting first
   (currently GitHub Pages, so `vite build` → `dist/` → Pages from `dist` or from a `gh-pages` branch).
5. Phase 3 polish (Modal wrapper, ShareCard shell, jargon explainers, a11y).

## Session log

- `sessions/2026-09-08.md` — review, roadmap, Phase 0, dead code, data quick wins, generator repoint.
