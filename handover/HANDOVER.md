# The Grays Dashboard — Handover

Living status file for work on this repo. One entry per working session lives in
`handover/sessions/`. This file is the summary: what's true now, what's done, what's next.
Update it at the end of every session.

- Live site: https://ptgc-ufo.com (GitHub Pages from `main`, `deploy.yml`)
- Roadmap + tick-off backlog (Claude artifact, shared state): "Grays Dashboard Roadmap"
  in Shaka's Claude artifact gallery — 126 items: 59 from the Sep 8 review across five phases
  (u10 dropped 2026-09-09, g7 + g8 added and live) plus **67 from Audit II (2026-09-16, ids
  `a1`–`a67`, group "AUDIT II")**. Full evidence for the a-items: `sessions/2026-09-16-audit.md`.
- Repo layout: `index.html` is the whole app (React 18 + Babel-standalone + Tailwind play
  CDN, compiled in the browser). `scripts/` + `.github/workflows/data-pipeline.yml` are the
  hourly data pipeline that writes `data/*.json` (ONE workflow since 2026-09-17, a29; `deploy.yml`
  is the only other workflow). `calculators.html`, `charts.html`, `portfolio.html`,
  `ledger.html` are separate pages.

## Current state (end of 2026-09-17)

Roadmap: 65 of 126 items closed — 45 of the original 59 (u11 + u14 done 2026-09-16), 20 of the 67
Audit II items (a1–a4, a13; a10, a11, a25; a16, a22, a24, a48 — 2026-09-16; **a14, a15, a17, a18,
a19, a20, a21, a23 — 2026-09-17, the honest-failure pass; **a29** the same evening — nine
scheduled workflows collapsed into `data-pipeline.yml` — first run green 14:40 UTC; night: **a28**
PulseScan paging, **a31** fatal log chunks, **a30** half-year burn files, **a34** Ledger reads raw
GitHub — `sessions/2026-09-17.md`**). **Next: measure the pipeline cadence on Sep 18, then a33 / a32,
then the calculators a5–a9.** u1 + u9 pushed as `5c2d3cf93` (2026-09-09); a header
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
| Wording — no "tax" anywhere on the site (Shaka, 2026-09-14) | **Done.** `taxRate`/`taxBreakdown` are now `feeRate`/`feeBreakdown`; the u7 "x% tax on every trade" line under Value Generated is gone. Keep it that way: write "fee" |
| Phase 4 — g8 DAO Buys chart | **Done, live** (2026-09-14). `DaoBuysModal` + `data/dao-buys.json` (hourly); "PTGC Buys" button in the DAO Treasury panel |
| **Audit II (a1–a67)** — Charts/Ledger wrong numbers, sibling-page hardening, index.html silent zeros, pipeline cadence + failure handling, a11y/mobile, cleanup | **26 of 67 done.** 2026-09-17 night, pipeline: a29 one hourly workflow, a28 PulseScan paging, a31 fatal log chunks, a30 half-year burn files, a34 Ledger reads raw GitHub, a33 token-allocation builder null-on-failure + staking under PTGC. 2026-09-16: a1 Charts 24H window, a2 + a4 Ledger amounts, a3 coingecko d90, a13 SRI on all four sibling pages, a10 + a11 portfolio, a25 phone Live Feed header, a16 DAO panel dashes, a22 deck-reopen flag gone, a24 Holder Analytics null guards, a48 sub-price sr-only text. **2026-09-17 — the honest-failure pass, index.html only:** a14 DexScreener-outage fallback (null vol/txns/change, chain liquidity from reserves), a15 burn USD + allocation donut, a17 PTGC-burned-by-UFO pending/failed/oldMissing, a18 five share cards (`CardLoadState` overlay + Retry), a19 KPI compare card, a20 quickRefresh token guard (`tokenRef`), a21 partner-price null through the Value Generated model (`missing`), a23 deck windows from `computeValueGen`. **Not started:** a5–a9 calculators, a12, a26, a27, a32, a35–a47, a49–a67 |

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
- **PTGC burn windows (24H/7D/30D/90D)**: `data/burn-summary.json` (hourly, the burn-history step of `data-pipeline.yml`).
  The burn archive behind it is `data/ptgc-burns-<year>-h1|h2.json`, half-years derived from the date (a30) —
  never add a period to a list; a file past 80 MB logs a warning, GitHub refuses 100 MB.
  Shown with an amber "as of" label after 6 h, as "—" after 7 days.
- **UFO burn windows**: `data/value-generated.json` → `burnPeriods.UFO` when <3 h old, otherwise a
  live chain scan. `burn-summary.json`'s UFO section still describes the OLD contract
  (`fetch-burn-history.js` line 31) — never use it for UFO.
- **UFO Value Generated**: `data/value-generated.json` (hourly, the value-generated step of `data-pipeline.yml`); the
  browser falls back to a live scan when the file is >3 h old.
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
   committed once per run as "data: hourly pipeline …"; expect ~24 a day — if it drops to ~5 again,
   GitHub is throttling even one workflow and the site's stale thresholds should move instead.
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
11. **Loading is a shell, not a spinner.** `loading` in `Dashboard` only covers the first
   DexScreener/RPC round-trip. While it is true the header/nav render with `Sk` bars and the tab
   body is `DashboardSkeleton`; Home uses `HomeCardSkeleton`. Both skeletons copy the real
   containers' classes so nothing moves when data lands — if you change a tile's padding or line
   height, change the skeleton too (measure with `SLOW=9000` in the harness).

## Next up (in order)

-1. **Audit II, top of the list:** the pipeline ran green by hand on 2026-09-17 (14:40 UTC). On
   Sep 18 count `git log --format="%ad %s" --date=format:"%m-%d %H:%M" | grep "hourly pipeline"`
   — want ~24/day at :10–:30; ~5 means GitHub throttles even one workflow → raise the site's stale
   thresholds instead (end of `sessions/2026-09-17.md`). Also check that commit's file list once:
   `ptgc-burns-2026.json` gone, `2026-h1` + `2026-h2` present (a30 migration). Then a32 (slim
   ufo-ptgc-burns.json), a38 (move handover/ out of the deploy), then the calculators a5–a9. Ordered list on the artifact's "Next up". Done 2026-09-16: a1–a4, a13, a10, a11, a25, a16,
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
  builder: null on failure, previous entry kept, staking contract under PTGC).
- `sessions/2026-09-14.md` — g8 follow-up: `DaoCreatures` (Grays tiers via `getBurnC`) in the
  "PTGC bought" tile, Recent-buys ledger box (last 10, +10, table on sm+, stacked list on
  phones). Harness ran in the cloud workspace (no Chromium on the local VM).
