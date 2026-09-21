# Headless harness

The verification method from the handover, in the repo. Two steps:

1. **Compile** the `text/babel` block with the exact `@babel/standalone@7.26.4` the page pins:
   `npm run compile` — fails loudly on a syntax error, in ~2 s, without a browser.
2. **Mount** the page in headless Chromium with the CDN scripts served from the pinned npm
   packages (versions in `package.json` match the `<script>` tags in `index.html`), the Tailwind
   play CDN replaced by a CLI build of the same classes, and the data APIs stubbed: RPC
   (`eth_*` returns canned values; `eth_getBalance` = 125M PLS so the DAO panel has an anchor read), DexScreener (four PTGC pairs), PulseScan counters/holders,
   `raw.githubusercontent.com/.../data/*.json` (served from the local `data/`), html2canvas. Orbitron and
   Rajdhani are served for real from `@fontsource` (devDependencies), so screenshots show the page's type.

```
cd tools/harness
npm install                      # once; playwright-core needs a Chromium — set CHROME=/path/to/chromium
npm run css                      # rebuild tw.out.css after editing index.html
node run.js "#/ptgc" 375 812 out/ptgc-m "shot=top;scroll=520;shot=panels"
node run.js "#/ufo"  1440 900 out/ufo-d
RPC_DOWN=1 node run.js "#/ptgc" 375 812 out/rpcdown      # every RPC returns 503
DS_DOWN=1  node run.js "#/ufo"  375 812 out/dsdown       # DexScreener returns 503
SLOW=9000  node run.js "#/ptgc" 375 812 out/loading      # every data reply waits 9 s → screenshot the loading shell
SLOW_HISTORY=6000 node run.js "#/ptgc" 1280 900 out/hist  # only data/*history*.json wait → modals opened before history lands (u13)
DECK_LOGS=8 node run.js "#/ptgc" 1440 900 out/deck "click=button:has-text('Live Feed'):visible;wait=9000;shot=deck"   # 8 synthetic Swap events → the Live Feed has rows, lifts, count-ups (u11)
REDUCED=1 DECK_LOGS=8 node run.js "#/ufo" 1280 900 out/deck-rm "click=button:has-text('Live Feed'):visible;wait=4000"   # prefers-reduced-motion for the run
NO_ACCEPT=1 node run.js "#/ptgc" 1280 900 out/disc      # do NOT pre-accept the disclaimer (u14: the modal must show)
HTML=ledger.html node run.js "" 1280 900 out/ledger     # any sibling page: since 2026-09-16 their CDN tags match index's, so the rewrite applies (data/ served locally)
SLOW=9000 SLOW_DATA=1 HTML=ledger.html node run.js "" 1280 900 out/ledger-slow "wait=4000;evalfile=probes/ledger-summary.js"   # a35: SLOW alone delays RPC/DexScreener/PulseScan; SLOW_DATA=1 delays the repo's data/*.json too → the summary must read "—" at 4 s
for TZ in UTC Australia/Sydney America/Los_Angeles; do TZ=$TZ HTML=ledger.html node run.js "" 1280 900 out/led-$TZ "wait=8000;evalfile=probes/ledger-digest.js"; done   # a60: per-month tile counts + the set of tx hashes; the three digests must be IDENTICAL (months are cut at UTC midnight). Age data/treasury-recent.json's lastUpdated by 9 h for the amber banner, 200 h for the red one and "—" tiles
HTML=ledger.html node run.js "" 1280 900 out/ledger-rows "wait=6000;evalfile=probes/ledger-rows.js"   # a36: which treasury files the page fetched (want ONLY treasury-recent.json) + every month's summary and rows; run once more with data/treasury-recent.json moved away and diff the two — the rows must be identical (only the footer time differs). `node scripts/fetch-treasury-transactions.js --recent-only` rebuilds the slim file from the full ones
W='[{"address":"0x1111111111111111111111111111111111111111","name":"A","group":"Default"},{"address":"0x2222222222222222222222222222222222222222","name":"B","group":"Default"}]'
HEAD_BLOCK=27100000 SLOW=2000 HTML=portfolio.html node run.js "" 1280 900 out/pf "wait=1500;eval=localStorage.setItem('ptgc_ufo_portfolio',JSON.stringify($W));reload=1000;evalfile=probes/portfolio-state.js;wait=4000;evalfile=probes/portfolio-state.js;wait=12000;evalfile=probes/portfolio-state.js"   # a12: seed two wallets, raise the stub head past UFO's launch block so the reflections scan has a window; chips yellow → green, the UFO lifetime bar reads "scanning the chain…" while the ONE-AT-A-TIME queue drains, then the number
HEAD_BLOCK=27100000 LOGS_DOWN=1 HTML=portfolio.html node run.js "" 1280 900 out/pf-fail "wait=1500;eval=localStorage.setItem('ptgc_ufo_portfolio',JSON.stringify($W));reload=12000;evalfile=probes/portfolio-state.js;click=button[aria-label^='Retry the UFO reflections'];wait=8000;evalfile=probes/portfolio-state.js"   # a12: eth_getLogs answers a JSON-RPC error → tile "unavailable" + Retry, bar "unavailable — the chain read failed for 2 wallets"; never a 0
HTML=charts.html node run.js "" 1280 900 out/charts "wait=10000;evalfile=probes/charts-status.js"   # a37: charts.html (no #root — the harness no longer waits for one) → status line "Live · 5/5 tokens / data to <time>"
TZ=America/Los_Angeles HTML=charts.html node run.js "?from=UFO" 1280 900 out/ch-ufo "wait=12000;evalfile=probes/charts-token.js"   # a59: the page must open as UFO (?from= / ?token= / ptgc_last_token), and on a 1M+ range every x label is the candle’s UTC day — run the same line under TZ=UTC and the tick labels must match
HTML=calculators.html node run.js "" 1280 900 out/calc "wait=3000;click=button:has-text('Rewards'):visible;wait=1500;evalfile=probes/calc-sanity.js"   # calculators.html; the probe lists any NaN / Infinity / undefined on the page (a5–a9 — run it with RPC_DOWN=1 and DS_DOWN=1 too: "MCap: —", "Circ. Supply: —", never 333B)
DS_UFO_PRICE=0.00005 SLOW_UFO=2500 HTML=calculators.html node run.js "" 1280 900 out/race "wait=3000;click=button:has-text('Switch'):visible;wait=300;click=button:has-text('Switch'):visible;wait=9000;evalfile=probes/calc-header.js"   # a7: two quick Switch taps — the header must say PTGC with PTGC's $0.000142, not UFO's price (DS_UFO_PRICE gives UFO calls their own price; SLOW_UFO makes the UFO load land last)
HTML=calculators.html node run.js "" 1280 900 out/keep "wait=3000;click=button:has-text('Rewards'):visible;wait=800;evalfile=probes/calc-type.js;wait=600;reload=4000;evalfile=probes/calc-header.js;click=button:has-text('Switch'):visible;wait=6000;evalfile=probes/calc-header.js"   # a8/a9: the typed holding survives a reload (saved on typing), a switch keeps the page mounted (amber "Loading UFO data… your inputs are kept" banner) and the bag is per token (UFO starts empty, PTGC's is still in localStorage). probes/calc-type.js types into `window.__typeSel` (default: the Rewards holding box) — set it with `eval=window.__typeSel='input[type=number][step=any]'` for the X-factor box

DECK_LOGS=4 node run.js "#/ptgc" 375 812 out/deck-m "scrollnav=1;click=button:has-text('Live Feed'):visible;wait=4000;evalfile=probes/deck-header.js"   # deck header geometry at phone width (a25)
SLOW_RPC=6000 node run.js "#/" 1280 900 out/fp "evalfile=probes/first-paint.js"   # a62: the chain answers slowly (RPC_DOWN cannot show this - a 503 returns instantly). The PTGC card must paint ~5 s before the UFO one, which alone waits for bootReady
DS_DOWN=1 RPC_DOWN=1 node run.js "#/" 1280 900 out/ladder "evalfile=probes/ladder-watch.js"   # a51: BOTH sources must be down or the chain-reserve fallback supplies a price and the ladder correctly never starts. Two rungs must appear in 22 s (4s then 10s), not one
PS_DOWN=1 node run.js "#/ptgc" 1280 900 out/psdown      # PulseScan returns 503 (holders → null unless the history file has a snapshot)
AFFIL_DATA=1 node run.js "#/ptgc" 1400 950 out/a54 "wait=6000;click=button:has-text('Affiliates'):visible;wait=4000;evalfile=probes/affil-a54.js"   # a54: three referrers against a $100 monthly minimum (alice clears it, bob does not, carol has her own 5% rate) and thresholdType deliberately "USD" in the wrong case. ALL-TIME Commissions must read 40.00K PTGC, not 41.60K, and bob's row must be BELOW MIN
AFFIL_DATA=1 node run.js "#/ptgc" 1400 950 out/a54card "wait=6000;click=button:has-text('Affiliates'):visible;wait=4000;eval=window.__who='bob';evalfile=probes/affil-card.js"   # a54: bob's progress card must read "$60.00 to go", "$40.00 / $100.00", 0 PTGC pending and "Min: $100 monthly total" — never "Threshold Met"
PS_COUNTERS_DOWN=1 node run.js "#/ptgc" 1280 900 out/counters "wait=12000;eval=(document.body.innerText.match(/🦑→🐚[\\s\\S]{0,20}/u)||[''])[0]"   # a53: only /counters fails, holder pages answer → "🦑→🐚 —", never 0 (age the allocation file past ALLOC_DEAD_MS first, or the prebuilt file answers instead)
DS_PRICE=4.542e-5 node run.js "#/ptgc" 1280 900 out/subprice "evalfile=probes/price-copy.js"   # a sub-micro price → the $0.0₄… notation; the probe reads what a copy yields (a48)
node run.js "#/ptgc" 1440 900 out/buys "click=button[aria-label^='PTGC Buys'];wait=2500;shot=modal;hoverfile=probes/dao-buys-dot.js;shot=tip"
node run.js "#/ptgc" 1440 900 out/cards "wait=3000;click=button:has-text('Socials'):visible;wait=1000;evalfile=probes/fetch-fail-all.js;click=button:has-text('Combined Burn Stats');wait=4000;shot=burnerr"   # a18: after the page is up, DexScreener + affiliate API + RPC POSTs reject → every second-fetch card must show "Couldn't load … — Retry", never $0 (fetch-fail.js keeps RPC alive)
HTML=index.orig.html node run.js "#/ptgc" 375 812 out/before   # compare against another copy
H2C=1 node run.js "#/ptgc" 1400 900 out/png "click=button[aria-label^='PTGC Buys'];wait=3000;click=button[aria-label='Share the DAO Buys chart as an image'];wait=2500;evalfile=probes/share-png-real.js;wait=500;shot=png"
```

`H2C=1` serves the real html2canvas 1.4.1 (devDependency, `npm install` once) instead of the
`window.html2canvas=null` stub, and `probes/share-png-real.js` presses the card's own Download
button, intercepts the blob and puts the PNG on the page at 1× so `shot=` shows exactly what the
user would download. Run it for any share-card change — html2canvas ≠ the browser (gotcha 5).

`HEAD_BLOCK=n` raises the stub chain head (default 24,000,000 — below UFO's launch block, so portfolio's
log scan is a no-op unless you raise it); `LOGS_DOWN=1` makes every `eth_getLogs` a JSON-RPC error while
`eth_call` keeps working (a12). To test the ErrorBoundary (a26) make a copy of index.html with a
`throw` at the top of `Dashboard` gated on `window.__boom===token`, run it with `HTML=`, set `__boom`
with `eval=`, click a tab, then `eval=location.hash='#/ptgc'` — `probes/eb-state.js` reports the card.
`SLOW_UFO=ms` delays only the UFO token's DexScreener calls and `DS_UFO_PRICE=n` gives them a
different price (base symbol UFO) — together they make a token-switch race visible (a7).

Actions (semicolon-separated, in order): `shot=<name>` viewport screenshot, `scroll=<y>`,
`click=<playwright selector>` (add `:visible` — several controls exist twice for phone/desktop),
`key=<Key>`, `wait=<ms>`, `reload=<ms>` (reload in place — localStorage survives — then wait), `eval=<js>` (no semicolons), `evalfile=<path>`, `hoverfile=<path>` (a
JS file that returns `{x,y}` in viewport px — the mouse moves there, for tooltips; see
`probes/dao-buys-dot.js`, which finds the biggest DAO-buy dot). A full-page screenshot is
always written to `<outPrefix>.png` at the end, and the run prints the first 400 chars of body text,
the RPC request count, and console errors (the Babel "deoptimised" note is expected).

The disclaimer is pre-accepted via localStorage (`grays_disclaimer_v1` = the current `DISCLAIMER_VERSION`; `NO_ACCEPT=1` skips that). RPC `eth_getLogs` answers `[]` unless `DECK_LOGS=n` (Swap events on the stub pair only). The stub numbers are nonsense (a 33T market cap
on the DexScreener-down run is the fake reserves, not a bug) — the harness checks that the page
mounts, walks its tabs and degrades without throwing, not that the figures are right.

Not wired to CI (roadmap b7/b8). To turn a run into a test, assert on `errors` being empty
and on `evalfile` probes, e.g. that every `button[aria-label^="What is"]` measures ≥32×32.

### Reproducing the a51 skeleton loop

A throw anywhere in `load()` AFTER first paint used to make every quick refresh re-run the whole
load, so the page flipped to `DashboardSkeleton` on every 5-minute tick, every tab refocus and
every badge tap — while the error screen stayed invisible (it is gated on `loadError && !data`).
To see it, copy index.html and put a `throw` immediately after the first-paint line
(`setData(d);…setLoading(false);`), then:

```
HTML=boom.html node run.js "#/ptgc" 1280 900 out/boom "wait=4000;evalfile=probes/skeleton-watch.js"
```

`sawSkeletonAfterRefresh` must be **false**. It was true before a51.
