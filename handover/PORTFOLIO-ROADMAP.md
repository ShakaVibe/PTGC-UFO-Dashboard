# Portfolio v2 — audit & roadmap (2026-10-14, after round 22)

How this was put together: (1) a full read of `tools/pf-v2/*` (PortfolioV2.jsx, PfTx.jsx, PfHistory.jsx, PfLeagues.jsx,
pf2.css) plus the classic page's fetch code; (2) a live walk-through of ptgc-ufo.com (round 21 live) with two real wallets —
one normal staker, one bot-like trader with 929 transactions this year — on desktop and at phone width, timing every network
call; (3) the harness a11y / overflow / tap-target sweep. Test wallets and caches were removed afterwards.

Effort: **S** = under an hour · **M** = half a day · **L** = a day or more. "Live" = seen on the real site; "Code" = found by
reading, not yet reproduced.

---

## What the live check measured (2 wallets, cold cache, desktop)

| | |
|---|---|
| Page paints, totals + value chart up | ~10 s |
| Recent Transactions first rows | ~15 s |
| Background history paging finished | ~45 s · 69 PulseScan calls (avg 1.9 s each) |
| Chain reads (archive eth_call) | 31 calls, avg 0.5 s, all done by 4 s |
| Price files from GitHub | **10 fetches for 2 files** (duplicate callers — see B2) |
| Transactions cache after one visit | **421 KB for 2 wallets** (~4 MB for 20 — see A5) |
| Details window, cold open | 2.0 s, 9 RPC calls |
| Console errors | none |
| Phone width 375 | no horizontal overflow; page is 5,070 px tall |
| a11y sweep (phone) | 0 unnamed buttons, 0 images without alt, **39 texts under 12 px, 30 tap targets under 24 px** |

The one thing that jumped out on screen: with a busy wallet the **value chart is buried under 69 dots** (30D) — the line is
unreadable. See A1.

---

## Phase A — fix before go-live (correctness + the obvious)

| # | What | Why it matters | Where | Effort |
|---|---|---|---|---|
| A1 | **Chart dot overload** (Live). A wallet with many trades paints a dot on nearly every point; on 7D/30D with a bot wallet the line vanishes. | The chart's whole point is the line. | PfHistory `PfHistChart` ev[] | M — cap dots per point: when a step has > N transactions, draw ONE dot coloured by the net (in/out), size it by count, list them in the tooltip; add a "Dots: on / off / trades only" toggle; hide dust (< $1). |
| A2 | **"Clear" (deselect all) shows "Reading your wallets from the chain…" forever** (Code, trivial to reproduce). | Looks broken. | PortfolioV2 ~183/305 `anyData` | S — branch on `counted.length===0` → "No wallets counted — switch one on". |
| A3 | **Price-file failure silently prices everything at today's price** (Code). If the two GitHub price files fail, the empty result is cached 30 min and every historical row / day gets amount × today's price with no warning; the chart's Retry can't recover for 30 min. | Silent wrong money. | PfHistory `pfhPrices` 68–75; PfTx 144; PfHistory `priceOf` | S — don't cache a failed load; only use the live price when the series is non-empty and the row is newer than it. |
| A4 | **Page cap reported as "complete"** (Code). Paging stops at 20 pages (1,000 transfers) but coverage says "whole history" → UFO reflections in Details can count an old buy as earned, and the chart drops no dots / no "complete from" note. | Wrong UFO numbers for busy wallets. | PfTx `pftDone` / `cov()` | S — when paging ended for the cap, report the oldest fetched time as the coverage edge. |
| A5 | **Transactions cache will blow the browser quota for big portfolios** (Live: 421 KB / 2 wallets). On quota the whole cache is wiped, deep paging stops silently, and every visit repeats it. `grays_pf_tx_v1` is never cleaned up either. | 15–20-wallet users never get a cache; the page re-reads ~700 pages every 5 min. | PfTx `pftCache.save` | M — slim the stored shape, cap items per wallet+token (a year or 600, whichever first), evict oldest by `at` instead of wiping, one key per wallet+token, delete the old v1 key. |
| A6 | **Details loader can spin forever** (Code). `txs.busy` stays true if the feed unmounts mid-run (e.g. Clear all), so the Both/UFO tabs wait on stale state. | Stuck "Crunching…". | PfTx effect cleanup / PortfolioV2 `txs` | S — send a final `{busy:false}` on cleanup, or key `txs` by the wallet set. |
| A7 | Loader copy says "**12 more pages**" but it's pages already read (counts up). | Confusing. | PfHistory loader | S — "12 pages read". |
| A8 | **Remove wallet is one tap, no confirm** (card ✕ is 18×21 px; also in the Edit window). | A mis-tap on a phone deletes a wallet and its cached history. | PortfolioV2 card, PfEditWallet | S — confirm, or an "Undo" toast for 6 s. |
| A9 | PulseScan partial failure with zero rows shows "No PTGC or UFO transfers … yet" — the "x of y reads failed" line only renders when there ARE rows. | Users think they have no history. | PfTx `none` state | S. |
| A10 | "**+ New group**" chosen but Create not clicked → wallet saved in a group literally named `__new`, which then shows as a chip. | Visible junk. | PortfolioV2 `add()` | S — use the typed name, or block with a message. |
| A11 | Old-UFO-contract file failure is silent since round 16 (the Reflections box just shows a smaller number). | Numbers quietly drop by the old-contract share. | PortfolioV2 `reflBox` / `v1.state` | S — "old contract not included · retry" line. |
| A12 | Verify **Unstake** on one real unstake tx on PulseScan (only the harness stub has been seen). If PulseScan doesn't name the method, an unstake shows as a Claim with only the reward. | Label accuracy — the thing he cares most about. | PfTx `pftClassify` | S (check) · S (fix: match the bare selector `0x2e1a7d4d` too). |
| A13 | Contract-held wallets (Gnosis Safe, bridges, vesting, CEX hot wallets that are contracts) get **Bought/Sold** labels; only pairs/routers should. | Wrong type on non-DEX transfers. | PfTx `main.c` rule | M — require a counter-leg in another token in the same tx (we already fetch tx detail for LP), else Receive/Send. |

**Go-live checklist** after A: hard-refresh test on Chrome / Safari / iPhone; a 10-wallet portfolio cold load; set `PF_V2_LIVE=true`;
remove the dot; keep the classic body one more round as a fallback; update HANDOVER.md "Portfolio" section.

---

## Phase B — performance (before it has many users)

| # | What | Effect today | Effort |
|---|---|---|---|
| B1 | **`build()` runs twice per landed page and re-renders the whole page each time** (every older page → `setSt(build())` AND `tell()`→`build()`→`setTxs` → full PortfolioV2 re-render incl. chart path + dot bucketing). With 20 wallets that's ~1,500 full rebuilds in the background. | Phone jank for the first minute. | M — build once per page, throttle `tell()` (every 500 ms / 5 pages), memoise PfHistChart + the token cards. |
| B2 | **Duplicate first-paint fetches**: price files fetched up to 5× (seen: 10 calls for 2 files), anchors 3×; `usePf24h` re-reads on every wallet toggle; after one Refresh, `nonce>0` is sticky so every later toggle bypasses the 5-min cache. | Wasted seconds + RPC load. | S — in-flight dedupe for `pfhPrices` / `pfhGetAnchors`; key 24h by minute; reset nonce after a run. |
| B3 | `pftCache.save()` stringifies the whole multi-MB cache after **every** page on the main thread. | 10–50 ms hitches × hundreds. | S — debounce like `pfhSave`; per-key storage (ties into A5). |
| B4 | Details `days` memo rescans ALL flows for every wallet × 30 days on every `txs` tick (24M iterations per tick with 20 busy wallets). | Modal stutters while paging. | S — bucket flows by wallet+token+UTC day once per `txs`. |
| B5 | **1Y points never line up day to day** (`step 4 d, unit 1 d`) → ~70 new archive reads per wallet+token every day, and `grays_pf_hist_v1` grows without pruning; 7D adds 4 points/day forever. | Slow 1Y, cache bloat. | S — align 1Y to 4-day UTC boundaries; prune > 400 days and 6-h points > 14 days on load. |
| B6 | No timeout on `pftDetail` and the old-UFO shard fetches; no back-off on PulseScan 429. | A hung call parks a worker / leaves "loading… old UFO contract" forever. | S — AbortController + 20 s like the others; one `pool()` helper with the same abort/retry for every path. |
| B7 | Deep PulseScan paging (up to 38 calls per wallet) runs on every 5-min-expired visit even if the user never scrolls to the chart. | Needless load. | S — start deep paging only when the chart or Details is in view, or after idle. |
| B8 | **Faster UFO load** (his open question from yesterday) — cache each wallet's UFO log scan and only read new blocks. Classic code, so it goes live for everyone. | UFO reflections take 10–20 s per wallet today. | M — he said hold; still the biggest single load-time win. |

---

## Phase C — UX polish (the next "polish" rounds)

| # | What | Effort |
|---|---|---|
| C1 | **Dust filter** in Recent Transactions: hide rows under $1 by default (the bot wallet shows "Bought 8.19K PTGC · $0.18" rows), with a "show dust" chip. | S |
| C2 | **Days: UTC vs local.** The feed groups by the phone's local day; Details and the chart use UTC midnight; the chart tooltip prints a UTC point with a local date (shows "Oct 13" for the Oct 14 00:00 UTC point west of UTC). Pick one — UTC everywhere with "(UTC)" once, or local everywhere. | S |
| C3 | Renaming a wallet leaves the **old name in the feed** until Refresh (names are baked into rows). | S |
| C4 | **Loading flicker**: toggling a wallet or changing the period blanks the chart and the three sparklines even when every point is cached. Keep the old chart with an "updating…" tag (the Details window already does this). | S |
| C5 | **Chart tooltip clipping** on phones (nowrap, up to 4 trade lines, flips left at > 62 % and gets cut by overflow:hidden). | S |
| C6 | Money formats mixed in one panel ($12,345.67 next to $12K; tooltip vs axis). Pick one per panel. | S |
| C7 | "**Moon Math is on — every dollar figure below…**" isn't true for Value History, the card price and the feed (all live by design). Reword, or tag those panels "live". | S |
| C8 | "17 counted · $X" counts wallets whose read failed but the $ excludes them → add "· 2 unreadable". | S |
| C9 | "Claims" chip silently includes Unstakes; Unstake row says "value". Own chip or "Claims & unstakes". | S |
| C10 | Details button on a wallet set with no UFO spends 217 calls per wallet to show zeros → disable / grey the UFO tab when `uf.balance===0 && ufoEarned===0`. | S |
| C11 | Creatures row stops at Turtle (6 tiers) while the league goes to Shrimp/Shell (8) → a Shrimp-sized bag shows "League: Shrimp" with an empty creature row. | S |
| C12 | Low-contrast text: footer, "From PulseScan…", chip counts, "dots complete from…" at 35–42 % white (≈2.5–3 : 1, fails AA). Lift to 55–60 %. | S |
| C13 | Address truncation styles differ ("0x1234...abcd" vs "0x1234…abcd"); unnamed wallets show the address twice in the breakdown. | S |
| C14 | Moon Math: typing "0." or clearing to "0" makes every $ figure $0.00 while typing → treat `!(x>0)` as "keep live". Also `type="number"` rejects comma decimals on some phones → `inputMode="decimal"` text input. | S |
| C15 | Per-wallet Details (open the 30-day window for ONE wallet from its card / breakdown row). | M |
| C16 | Details periods: 7D / 30D / 90D (the reads scale linearly; 90D ≈ 650 calls per wallet, so cache-first). | M |
| C17 | Group totals row in the breakdown when groups exist; sort wallets by value / name. | S |

---

## Phase D — accessibility (keyboard + screen reader + touch)

| # | What | Effort |
|---|---|---|
| D1 | **No focus trap in any modal** (Tab walks out behind the overlay); How-it-works isn't even a PfModal (no Esc, no focus move, no scroll lock). | M — one trap in PfModal; make How-it-works use it. |
| D2 | **Edit window steals focus** from the Name input (`autoFocus` then the overlay focuses itself) and on close focus falls to `<body>` instead of the ✎. | S |
| D3 | Hover-only data: value chart and daily bars expose values only to a mouse/finger. Add arrow-key stepping (`tabIndex=0` + onKeyDown) and an `aria-live` text for the tooltip; the Details window has its table as a fallback, the value chart has none. | M |
| D4 | **Tap targets under 24 px** (30 found): card ✕ 18×21, ✎ 20×20, the 30×17 switch, copy buttons 24, Back 22. WCAG 2.2 minimum is 24×24 — pad the hit area, not the glyph. | S |
| D5 | Status dot on wallet cards is colour-only (title only) → visually-hidden text / aria-label. | S |
| D6 | Search input has `outline:none` with no `:focus-visible` replacement. | S |
| D7 | `role="tab"` / `role="radio"` groups (Both/PTGC/UFO, supply toggle, Moon Math) have no arrow-key behaviour or `aria-controls` → use `aria-pressed` buttons like the period control already does, or implement roving tabindex. | S |
| D8 | Text under 12 px (39 found): tile labels 10.5, period buttons 10.5, HOW IT WORKS 10, ✕ 11. Keep ≥ 12 px for anything that carries meaning. | S |
| D9 | iOS: `body{overflow:hidden}` doesn't lock background scroll (long Details modal scrolls the page beneath); `clipboard.writeText` rejections aren't caught (✓ shows even when the copy failed). | S |

---

## Phase E — code health (so the next person — or next session — doesn't get bitten)

| # | What | Effort |
|---|---|---|
| E1 | **Dead code**: `PfYield` + its CSS, `ptYield/ufoYield/fmtY/ptgcEarned`, the PLS-multiplier maths, round-8 dot branches in PfHistChart, unused props passed from portfolio.html, and the CSS of every retired round (table feed, old Moon Math strip, `.pf2-src3.two`, `.pf2-tbl`, …). **Roughly a third of pf2.css is unreachable.** | M |
| E2 | Four copies of the same addresses / supply across files (`PFT_STAKING` lowercase vs `PFE_ST` checksum vs `PTGC_STAKING_ADDR`; `PFH_TOK` vs `PF_TOKEN_ADDR`; the literal `999999999051` next to `PF_SUPPLY.UFO`). One `PF_ADDR` / `PF_SUPPLY` block. | S |
| E3 | Three different localStorage quota strategies (wipe all / drop a third / wipe all) → one `pfStore(key,{maxBytes,evict})`. | S (with A5) |
| E4 | Cross-file globals depend on the concatenation order in `pf-v2.py` (PfLeagues → PfHistory → PfTx → PortfolioV2); a module-scope use in the wrong file would TDZ-crash the page. Header comment per file listing what it expects; or one small `pfShared` object. | S |
| E5 | `window.pfUfoRecv` side channel from the classic scan → return `received` on `portfolioData[addr].ufo` like PTGC does. | S |
| E6 | `txs` is a grab-bag (`rows, cov, failed, flows, busy, pages`) with three readers assuming different meanings of `cov` → a small shape + `coverageAt(addr,tok)` helper (prevents A4 recurring). | S |
| E7 | Comment rot (swapped comments at PV2 166/169, a "UI note" that no longer exists, duplicated comment in PfHistory, the PfTx header still says "latest 50 per call"). Magic numbers (`10300` block ms, `80` batch, `1e-9`, loader weights) → named. | S |
| E8 | Hand-rolled worker pools ×5 → one `pool(jobs, n, fn, {abort, timeout})`. | S |
| E9 | Precompile the JSX (the console warns "You are using the in-browser Babel transformer" 3×): Babel-standalone parses ~250 KB of JSX on every visit. A build step would cut first paint by ~0.5–1 s and is the one change that affects every page. | L (site-wide decision) |

---

## Phase F — bigger ideas (worth a mock-up each)

| # | Idea | Why |
|---|---|---|
| F1 | **Cost basis & P&L**: paid vs current value per token (we already have every buy with its $ at the time). Needs care — gifts / moves in have no cost — so show "based on N buys worth $X". | The question every holder asks. |
| F2 | **CSV / PDF export** of the breakdown, the 30-day rewards and the transaction feed (tax time). | Cheap, often requested. |
| F3 | **"Since your last visit"** strip: rewards earned, price move, trades — from the caches we already keep. | Makes the page a daily habit. |
| F4 | **Shareable read-only link** (GET CODE exists; a `?code=` URL that opens the same portfolio without saving it). | Share with a partner / in Telegram. |
| F5 | **Goals**: "need X more for Whale" is there; add a target (league or $) with a progress bar and ETA at the current reward rate. | Fun + on brand (leagues). |
| F6 | **Lock calendar**: a small timeline of unlock dates with the amounts (the data is in `locks`). | Lock positions is just a list today. |
| F7 | **Alerts** (local, no server): notify when a claim is ready above $X or a lock becomes unlockable, via the browser's Notifications API while the tab is open. | Zero backend. |

---

## Suggested order

1. **Round 23 — Phase A** (A1 dots, A2–A11 fixes, A12 check). Mostly S items; one M (A1, A5). Then the go-live checklist.
2. **Round 24 — Phase B** (B1–B7). This is the "feels fast on a phone" round; B8 when he says.
3. **Rounds 25–26 — Phase C + D** in two passes (polish, then keyboard/touch).
4. **Round 27 — Phase E** cleanup (best done once the UI has settled).
5. **Phase F** one at a time, mock-up first, as he picks.

### Done after the phases (his own asks)

- **Round 28** (2026-10-14): strip bars hover / click → tooltip + day window (`PfDayModal`); the deck shrunk to 7-across mini
  tiles with a sort (his pick: A of `design/portfolio/mock-wallets-v2.html`). Still hidden. Next: the go-live checklist above
  when he says, B8 when he says, Phase F one at a time with a mock-up.
