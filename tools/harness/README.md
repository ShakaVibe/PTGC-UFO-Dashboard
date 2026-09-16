# Headless harness

The verification method from the handover, in the repo. Two steps:

1. **Compile** the `text/babel` block with the exact `@babel/standalone@7.26.4` the page pins:
   `npm run compile` — fails loudly on a syntax error, in ~2 s, without a browser.
2. **Mount** the page in headless Chromium with the CDN scripts served from the pinned npm
   packages (versions in `package.json` match the `<script>` tags in `index.html`), the Tailwind
   play CDN replaced by a CLI build of the same classes, and the data APIs stubbed: RPC
   (`eth_*` returns canned values), DexScreener (four PTGC pairs), PulseScan counters/holders,
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
node run.js "#/ptgc" 1440 900 out/buys "click=button[aria-label^='PTGC Buys'];wait=2500;shot=modal;hoverfile=probes/dao-buys-dot.js;shot=tip"
HTML=index.orig.html node run.js "#/ptgc" 375 812 out/before   # compare against another copy
H2C=1 node run.js "#/ptgc" 1400 900 out/png "click=button[aria-label^='PTGC Buys'];wait=3000;click=button[aria-label='Share the DAO Buys chart as an image'];wait=2500;evalfile=probes/share-png-real.js;wait=500;shot=png"
```

`H2C=1` serves the real html2canvas 1.4.1 (devDependency, `npm install` once) instead of the
`window.html2canvas=null` stub, and `probes/share-png-real.js` presses the card's own Download
button, intercepts the blob and puts the PNG on the page at 1× so `shot=` shows exactly what the
user would download. Run it for any share-card change — html2canvas ≠ the browser (gotcha 5).

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
