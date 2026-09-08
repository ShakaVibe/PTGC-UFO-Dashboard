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

## Current state (end of 2026-09-08)

Roadmap: 32 of 58 items closed. Everything below marked "in repo" is committed to the local
clone on Shaka's Mac; check `git status` there and push if anything is still pending.

| Area | Status |
|---|---|
| Phase 0 — wrong numbers / crashes (17 items) | **Done, live** |
| Phase 1 — dead code (b3), html2canvas removal (b4) | **Done, live** |
| Phase 1 — Vite build (b1, b2), icons/manifest (b5), fonts (b6), CI/CSP (b7), tests (b8), operator script (b9) | Not started — build deliberately parked by Shaka |
| Phase 2 — all data items (d1–d12) | **Done** (d10 and d12 closed as won't-do, see gotchas). d1/d4 are live; d5/d7/d8/d9/d11 are in the repo awaiting the next push |
| Phase 3 — share cards (u2) | **Done, live** |
| Phase 3 — everything else (u1, u3–u14) | Not started. Suggested order: u7+u8 (clarity + mobile), u12 (keep shell while loading), u10 (rename Socials Hub), u1 (Modal wrapper), u9 (a11y), u4/u5/u6, u3 (decomposition — better after the build) |
| Phase 4 — product ideas (g1–g6) | Not started |

### How a session goes
1. Shaka opens the task in the Claude desktop app with `~/Desktop/PTGC-UFO` linked (Add folder).
2. Claude edits in place (or writes via the device bridge), verifies with the headless harness
   described under Testing, and updates `handover/` + the roadmap ticks.
3. Shaka pushes: `git add -A && git commit -m "…" && git pull --rebase && git push`. The
   `pull --rebase` is needed because the Actions bots commit `data/*.json` every few minutes.
4. If a pipeline script changed, run its workflow once by hand (Actions → Run workflow).

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

00. **Addresses live in `ADDR`, supplies in `SUPPLY`** (top of the script, just before `TOKENS`).
   The older names (`WPLS_ADDRESS`, `UFO_WETH`, `LP_ADDRESSES`, `HARDCODED_UFO_PAIRS`, …) are
   aliases of it. Add new addresses there, not as literals.

0. **UFO's ATH is the ORIGINAL contract's on purpose.** The migration is the same token, so
   "X's to ATH" measures against `ATH_PRICES.UFO = 0.000113` (the pre-migration high) and the
   CoinGecko file carries no UFO ATH to override it. Do not "fix" this (roadmap d10 is closed).

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

1. **Push the pending commit** (Phase 2 leftovers d5/d7/d8/d9/d11 + handover). No Action run needed.
2. **First-timer clarity (u7 + u8)** — ~half a day: tier labels under the creature emojis, tappable
   ⓘ explainers for "Value Generated" / "RH Cores" / "Day N" / "X's to ATH" (title tooltips don't
   exist on touch), mobile nav overflow cue, orphan 7th KPI tile, tap targets ≥32 px.
3. **Keep the shell visible while loading (u12)** — replace the full-page spinner with header +
   nav + per-panel skeletons; fix Home's 128 px skeletons (shorter than the real cards).
4. **Modal wrapper (u1) + a11y pass (u9)** — give the non-share modals what `ShareCardModal`
   already has (Escape, focus, scroll lock, role=dialog); aria-labels on icon buttons; focus
   rings; reduced-motion.
5. **Vite build (Phase 1)** when Shaka says go. Hosting is GitHub Pages (`deploy.yml`), so the
   decision is Pages-from-`dist` vs a `gh-pages` branch. Do b3-style cleanup first; everything
   in Phase 3 gets easier after it.
6. **October 6, 2026** — UFO day 90. Check the UFO dashboard and the "PTGC Burned by UFO" panel
   that day (both of the fixed 90-day bugs get their first real test; the `exactTo` bug found
   in dry-run would have shown up here too).

## Session log

- `sessions/2026-09-08.md` — review, roadmap, Phase 0, dead code, data quick wins, generator repoint.
