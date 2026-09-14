# The Grays Dashboard — Handover

Living status file for work on this repo. One entry per working session lives in
`handover/sessions/`. This file is the summary: what's true now, what's done, what's next.
Update it at the end of every session.

- Live site: https://ptgc-ufo.com (GitHub Pages from `main`, `deploy.yml`)
- Roadmap + tick-off backlog (Claude artifact, shared state): "Grays Dashboard Roadmap"
  in Shaka's Claude artifact gallery — 59 items across five phases (u10 dropped 2026-09-09,
  g7 Buy/Sell via switch.win added + ticked 2026-09-13, g8 DAO Buys chart added + ticked
  2026-09-13 night — built but hidden, see below).
- Repo layout: `index.html` is the whole app (React 18 + Babel-standalone + Tailwind play
  CDN, compiled in the browser). `scripts/` + `.github/workflows/` are the hourly data
  pipeline that writes `data/*.json`. `calculators.html`, `charts.html`, `portfolio.html`,
  `ledger.html` are separate pages.

## Current state (end of 2026-09-14)

Roadmap: 41 of 59 items closed. u1 + u9 pushed as `5c2d3cf93` (2026-09-09); a header
tweak (`96afb0ed8`, PLS ratio / X's stats inline from 1024px) landed after the last
handover. 2026-09-13: **Buy/Sell button + switch.win widget modal built and live**; evening
u4 + u13; night **DAO Buys chart built, HIDDEN behind `DAO_BUYS_LIVE=false`** — entrance is
the faint gold dot top-right of the PTGC dashboard header (see `sessions/2026-09-13.md`).
2026-09-14: **Grays creature line in the "PTGC bought" tile + a Recent-buys ledger box** under
the chart (`DaoCreatures`, `sessions/2026-09-14.md`) — uncommitted when the session ended unless
the log below says otherwise. Check `git --no-optional-locks status` before starting.

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
| Phase 3 — u5, u6, u11, u14, u3 | Not started. Suggested order: u5/u6, u11/u14, u3 (decomposition — better after the build) |
| Phase 4 — product ideas (g1–g6) | Not started |
| Phase 4 — g7 Buy/Sell via switch.win | **Done, live** (2026-09-13; three commits, ticked on the artifact) |
| Phase 4 — g8 DAO Buys chart | **Built, hidden** (2026-09-13 night; creatures + ledger 2026-09-14). `DaoBuysModal` + `data/dao-buys.json` (hourly). Flip `DAO_BUYS_LIVE` to show the Buys button |

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
- **DAO Buys (PTGC)**: `data/dao-buys.json` (hourly, second step of `fetch-treasury.yml`,
  generator `scripts/build-dao-buys.mjs`). Buys = wallet-sent, PLS-paid txs that delivered PTGC
  to `TOKENS.PTGC.daoTreasury`; priced from pair reserves at the buy's block (PLS/USD via
  `PAIR_WPLS_DAI`, PTGC via `PAIR_PTGC_WPLS`). Price line = same reserves on a block grid.
  No third-party API anywhere in it.
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
   **html2canvas is not the browser** (2026-09-14): it cannot do `background-clip:text` (every
   `metallic-gold` word became a solid gold bar) and draws text inside `white-space:nowrap` /
   `truncate` elements half a line too low, then clips it. `shareCardPng`'s `onclone` now flattens
   `.metallic-gold` to `#E8C044` and turns nowrap/truncate off inside `[data-share-wrap]` — so in a
   card, never rely on nowrap to hold a layout, and don't put a bordered pill around text (the box
   lands ~12 px above the text; the DAO Buys card shows its "4.6d ago" as plain text for that
   reason). Check every card change with `H2C=1` + `probes/share-png-real.js` (harness README).
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
15. **DAO Buys chart is hidden on purpose** (`DAO_BUYS_LIVE=false`, next to `DAO_BUYS_URL`).
   The faint dot top-right of the PTGC header opens it (deliberately no hover/title — Shaka
   does not want it found); the "Buys" button next to Ledger appears when the flag flips.
   Dots sit ON the market line (`DAO_BUYS_DOT_AT='market'`); the price PAID is 3–14% higher
   (tax + slippage) and lives in the hover card and the stats. Modal + share card share
   `computeDaoBuysView` / `buildDaoBuysChartConfig` — change the chart there, not in JSX.
   `fetchFreshDaoBuys` scans the chain for buys newer than the snapshot on open. The generator
   caches priced buys by hash and extends the price grid; if a buy's PLS/PTGC ever changes in
   the treasury files it is re-priced automatically. To rebuild from scratch, delete
   `data/dao-buys.json` and run the script (26 s). `removeLiquidityETH…` calls deliver PTGC to
   the wallet too — they are excluded (`excluded.lpRemovals`), never count them as buys.
   Creature rows (tile + ledger) come from `DaoCreatures` → `getBurnC` (top three tiers,
   starting supply); the ledger lists `view.buysAll` (lifetime), not the selected range.
11. **Loading is a shell, not a spinner.** `loading` in `Dashboard` only covers the first
   DexScreener/RPC round-trip. While it is true the header/nav render with `Sk` bars and the tab
   body is `DashboardSkeleton`; Home uses `HomeCardSkeleton`. Both skeletons copy the real
   containers' classes so nothing moves when data lands — if you change a tile's padding or line
   height, change the skeleton too (measure with `SLOW=9000` in the harness).

## Next up (in order)

0. **DAO Buys chart (g8) — built 2026-09-13 night, hidden.** Shaka reviews it via the header
   dot on the live site, then: (a) says "make it live" → set `DAO_BUYS_LIVE=true` (and decide
   if the dot stays); (b) optional share card; (c) after the first hourly `fetch-treasury` run
   check `data/dao-buys.json` `generatedAt` moved and the buy count is still 211+ (the Action
   step is `continue-on-error`, so a failure only shows in the workflow log).
1. **Buy/Sell (switch.win)** — done and live (2026-09-13, g7 ticked). Shaka connected a wallet
   and bought in-frame; the Switch founder has been told about the embed. Optional follow-up
   left: a compact Buy/Sell in the phone sticky bar (`sessions/2026-09-13.md`).
2. **Live check of u1 + u9** (30 seconds): on the phone open any ⓘ modal, the page behind must
   not scroll; on desktop, Tab through the header and Escape out of a modal — focus should land
   back on the button that opened it.
3. **Phase 3 leftovers** — u5/u6 next (see roadmap), then u11/u14. u3 (decomposition)
   waits for the build.
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
- `sessions/2026-09-14.md` — g8 follow-up: `DaoCreatures` (Grays tiers via `getBurnC`) in the
  "PTGC bought" tile, Recent-buys ledger box (last 10, +10, table on sm+, stacked list on
  phones). Harness ran in the cloud workspace (no Chromium on the local VM).
