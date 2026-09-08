# Headless harness

The verification method from the handover, in the repo. Two steps:

1. **Compile** the `text/babel` block with the exact `@babel/standalone@7.26.4` the page pins:
   `npm run compile` — fails loudly on a syntax error, in ~2 s, without a browser.
2. **Mount** the page in headless Chromium with the CDN scripts served from the pinned npm
   packages (versions in `package.json` match the `<script>` tags in `index.html`), the Tailwind
   play CDN replaced by a CLI build of the same classes, and the data APIs stubbed: RPC
   (`eth_*` returns canned values), DexScreener (four PTGC pairs), PulseScan counters/holders,
   `raw.githubusercontent.com/.../data/*.json` (served from the local `data/`), fonts, html2canvas.

```
cd tools/harness
npm install                      # once; playwright-core needs a Chromium — set CHROME=/path/to/chromium
npm run css                      # rebuild tw.out.css after editing index.html
node run.js "#/ptgc" 375 812 out/ptgc-m "shot=top;scroll=520;shot=panels"
node run.js "#/ufo"  1440 900 out/ufo-d
RPC_DOWN=1 node run.js "#/ptgc" 375 812 out/rpcdown      # every RPC returns 503
DS_DOWN=1  node run.js "#/ufo"  375 812 out/dsdown       # DexScreener returns 503
HTML=index.orig.html node run.js "#/ptgc" 375 812 out/before   # compare against another copy
```

Actions (semicolon-separated, in order): `shot=<name>` viewport screenshot, `scroll=<y>`,
`click=<playwright selector>` (add `:visible` — several controls exist twice for phone/desktop),
`key=<Key>`, `wait=<ms>`, `eval=<js>` (no semicolons), `evalfile=<path>`. A full-page screenshot is
always written to `<outPrefix>.png` at the end, and the run prints the first 400 chars of body text,
the RPC request count, and console errors (the Babel "deoptimised" note is expected).

The disclaimer is pre-accepted via localStorage. The stub numbers are nonsense (a 33T market cap
on the DexScreener-down run is the fake reserves, not a bug) — the harness checks that the page
mounts, walks its tabs and degrades without throwing, not that the figures are right.

Not wired to CI (roadmap b7/b8). To turn a run into a test, assert on `errors` being empty
and on `evalfile` probes, e.g. that every `button[aria-label^="What is"]` measures ≥32×32.
