#!/usr/bin/env python3
"""Audit III, batch 5a (2026-10-07): speed — c13, c12, c14 (the image work, c15, is batch 5b). Idempotent — run from the repo root:
    python3 tools/audit3-p5.py
Each edit asserts its anchor exists exactly once (or is already applied) so a drifted file fails loudly instead of half-applying.
  c13 the Tailwind play CDN (~390 KB script, no SRI, re-scans the DOM on every mutation) → the built `tw.css` (16 KB gz) that the
      harness has rendered every page with since a36. `npm run css` in tools/harness now ALSO writes the site file (minified);
      the five pages link `tw.css?v=1`; the harness swaps that link for its fresh build the way it swapped the CDN tag.
      RULE (gotcha 8, now for real): after editing any page's classes, `cd tools/harness && npm run css` and commit tw.css —
      a class with no rule in tw.css does nothing on the site.
  c12 `?t=Date.now()` on the raw.githubusercontent reads only defeated the BROWSER cache (the CDN ignores the query and serves
      ≤ 300 s stale regardless): the dashboard re-downloaded ~264 KB gz of data every reload and ~1.1 MB gz/hour in an open tab.
      Now `fetch(url, DATA_FETCH)` with `{cache:'no-cache'}` — the browser revalidates (If-None-Match) and gets a 304 unless the
      file changed. Bucketed `?t=<hour>` reads stay (they are cache-friendly already). The Holders Details 5-min re-read pauses
      while the tab is hidden.
  c14 a static boot shell inside #root (brand, one-sentence summary, links — React's render replaces it; a crawler or a
      blocked-CDN visitor no longer sees an empty page) and `<link rel="preload" as="image">` for the dashboard header art,
      added by the plain head script only when the URL is a dashboard route (Home does not use that art). NOT done: parking the
      boot fetches in the head script (the loaders' cache keys would need the same bucket logic — a session of its own) and the
      CDN onerror fallback (untestable here; the SRI hashes would have to be verified byte-for-byte on jsDelivr first).
"""
import sys, re, hashlib

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)
def md5(s): return hashlib.md5(s.encode('utf-8')).hexdigest()

class Edit:
    def __init__(self, path):
        self.path = path; self.s = read(path); self.n = 0
    def rep(self, old, new, count=1, done_marker=None):
        """Replace `old` → `new` exactly `count` times; skip silently when `done_marker` (default: new) is already present."""
        if done_marker is not None:
            if done_marker in self.s: return False
        elif new in self.s and old not in self.s:
            return False
        c = self.s.count(old)
        assert c == count, f'{self.path}: expected {count}× anchor, found {c}: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def rep_all(self, old, new, done_marker):
        if done_marker in self.s: return False
        assert old in self.s, f'{self.path}: anchor missing: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def save(self):
        write(self.path, self.s); print(f'{self.path}: {self.n} edit(s), md5 {md5(self.s)}')

TW_LINK = '<link rel="stylesheet" href="tw.css?v=1">   <!-- c13 (Audit III, 2026-10-07): the built Tailwind CSS (tools/harness: npm run css) in place of the play CDN -->'

# ================================================================= index.html
ix = Edit('index.html')
# c13
ix.rep("""  <link rel="preconnect" href="https://cdn.tailwindcss.com">\n""", "")
ix.rep("""  <script src="https://cdn.tailwindcss.com/3.4.16"></script>""", '  ' + TW_LINK)
# c14 — preload the dashboard header art on dashboard routes only (the plain head script runs before any CDN script)
ix.rep("""    (function(){try{if(!/[?&]debug=1\\b/.test(location.search)){var n=function(){};console.log=n;console.info=n;console.debug=n;}}catch(e){}})();
  </script>""",
       """    (function(){try{if(!/[?&]debug=1\\b/.test(location.search)){var n=function(){};console.log=n;console.info=n;console.debug=n;}}catch(e){}})();
    /* c14 (Audit III, 2026-10-07): the dashboard's header art used to be requested only after the ~3 s compile. Preload it when
       the URL is a dashboard (#/ptgc, #/ufo, ?token=) — Home has its own art and must not pay for this. Keep in step with
       H2_ASSETS / h2.css. */
    (function(){try{var q=location.search,h=location.hash;if(/[?&]token=(PTGC|UFO)\\b/.test(q)||/^#\\/(ptgc|ufo)\\b/i.test(h)){
      ['logos/header/dash-bg.jpg','logos/header/alien-head.webp','logos/header/tabs-bg.jpg'].forEach(function(u){var l=document.createElement('link');l.rel='preload';l.as='image';l.href=u;document.head.appendChild(l);});}}catch(e){}})();
  </script>""", done_marker="c14 (Audit III, 2026-10-07): the dashboard's header art")
# c14 — the boot shell
ix.rep("""  <div id="root"></div>
  <script type="text/babel" data-presets="react">""",
       """  <div id="root"><!-- c14 (Audit III): a static shell until React mounts — the compile takes ~3 s; a crawler or a visitor whose network
       blocks unpkg / jsDelivr used to get an empty page. React's render replaces this whole subtree. -->
    <div style="min-height:100vh;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:14px;background:#000;color:#fff;font-family:system-ui,-apple-system,sans-serif;text-align:center;padding:24px;box-sizing:border-box">
      <div style="font-size:22px;font-weight:800;letter-spacing:.1em;color:#E8C044">THE GRAYS DASHBOARD</div>
      <p style="margin:0;max-width:36em;font-size:14px;line-height:1.5;color:rgba(255,255,255,.62)">Live PulseChain stats for PTGC and UFO — price, liquidity, volume, holders, burns and value generated — with calculators, charts, a portfolio tracker and the DAO ledger.</p>
      <p style="margin:0;font-size:13px"><a href="#/ptgc" style="color:#E8C044;text-decoration:none">PTGC dashboard</a> &nbsp;·&nbsp; <a href="#/ufo" style="color:#7CFC00;text-decoration:none">UFO dashboard</a> &nbsp;·&nbsp; <a href="calculators.html" style="color:rgba(255,255,255,.7);text-decoration:none">Calculators</a> &nbsp;·&nbsp; <a href="charts.html" style="color:rgba(255,255,255,.7);text-decoration:none">Charts</a> &nbsp;·&nbsp; <a href="portfolio.html" style="color:rgba(255,255,255,.7);text-decoration:none">Portfolio</a> &nbsp;·&nbsp; <a href="ledger.html" style="color:rgba(255,255,255,.7);text-decoration:none">Ledger</a></p>
      <p style="margin:6px 0 0;font-size:12px;letter-spacing:.14em;color:rgba(255,255,255,.35)">LOADING…</p>
    </div>
  </div>
  <script type="text/babel" data-presets="react">""")
# c12 — one fetch option for the repo's data files
ix.rep("""    const cacheBucket=()=>Math.floor(Date.now()/(5*60*1000));""",
       """    const cacheBucket=()=>Math.floor(Date.now()/(5*60*1000));
    /* c12 (Audit III, 2026-10-07): raw.githubusercontent's CDN ignores the query string, so `?t=Date.now()` never bought freshness —
       it only stopped the BROWSER from caching (every reload re-downloaded ~264 KB gz of data; an open tab ~1.1 MB gz/hour).
       `no-cache` = always revalidate with If-None-Match: a 304 when the file is unchanged, the new file when it is. */
    const DATA_FETCH={cache:'no-cache'};""", done_marker="const DATA_FETCH={cache:'no-cache'};")
for old, new in [
    ("fetch(BURN_HISTORY_URL+'?t='+Date.now())", "fetch(BURN_HISTORY_URL,DATA_FETCH)"),
    ("fetch(UFO_PTGC_BURNS_URL+'?t='+Date.now())", "fetch(UFO_PTGC_BURNS_URL,DATA_FETCH)"),
    ("fetch(COINGECKO_DATA_URL + '?t=' + Date.now())", "fetch(COINGECKO_DATA_URL, DATA_FETCH)"),
    ("fetch(LIQUIDITY_HISTORY_URL + '?t=' + Date.now())", "fetch(LIQUIDITY_HISTORY_URL, DATA_FETCH)"),
    ("fetch(TRANSACTION_HISTORY_URL + '?t=' + Date.now())", "fetch(TRANSACTION_HISTORY_URL, DATA_FETCH)"),
    ("fetch(HOLDER_HISTORY_URL_NEW + '?t=' + Date.now())", "fetch(HOLDER_HISTORY_URL_NEW, DATA_FETCH)"),
    ("fetch(TOKENSINLP_HISTORY_URL + '?t=' + Date.now())", "fetch(TOKENSINLP_HISTORY_URL, DATA_FETCH)"),
    ("fetch(LV_SNAPSHOTS_URL+'?t='+Date.now())", "fetch(LV_SNAPSHOTS_URL,DATA_FETCH)"),
    ("fetch(PAIR_VOL_URL+'?t='+Date.now())", "fetch(PAIR_VOL_URL,DATA_FETCH)"),
    ("fetch(NEW_HOLDERS_URL+'?t='+Date.now())", "fetch(NEW_HOLDERS_URL,DATA_FETCH)"),
    ("fetch(SWAP_VOL_URL+'?t='+Date.now())", "fetch(SWAP_VOL_URL,DATA_FETCH)"),
    ("fetch('https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/charts-data.json?t='+Date.now())", "fetch('https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/charts-data.json',DATA_FETCH)"),
]:
    ix.rep(old, new)
# the Holders Details re-read pauses while the tab is hidden
ix.rep("""        go();const id=setInterval(go,NH_TTL);""",
       """        go();const id=setInterval(()=>{if(!document.hidden)go();},NH_TTL);   // c12: no 5-min re-read while the tab is hidden""")
ix.save()

# ================================================================= calculators.html
ca = Edit('calculators.html')
ca.rep("""  <script src="https://cdn.tailwindcss.com/3.4.16"></script>""", '  ' + TW_LINK)
ca.rep("""        const r = await fetch(COINGECKO_DATA_URL + '?t=' + Date.now());""",
       """        const r = await fetch(COINGECKO_DATA_URL, {cache:'no-cache'});   // c12 (Audit III): revalidate, never a cache-buster (the CDN ignores it)""")
ca.rep("""          const res = await fetch(LV_HISTORY_URL + '?t=' + Date.now());""",
       """          const res = await fetch(LV_HISTORY_URL, {cache:'no-cache'});   // c12""")
ca.rep("""        const res = await fetch(LV_HISTORY_URL + '?t=' + Date.now());""",
       """        const res = await fetch(LV_HISTORY_URL, {cache:'no-cache'});   // c12""")
ca.save()

# ================================================================= charts.html / portfolio.html — c13 only
ch = Edit('charts.html')
ch.rep("""<script src="https://cdn.tailwindcss.com/3.4.16"></script>""", TW_LINK)
ch.save()
pf = Edit('portfolio.html')
pf.rep("""  <script src="https://cdn.tailwindcss.com/3.4.16"></script>""", '  ' + TW_LINK)
pf.save()

# ================================================================= ledger.html — c13, c12
le = Edit('ledger.html')
le.rep("""  <script src="https://cdn.tailwindcss.com/3.4.16"></script>""", '  ' + TW_LINK)
le.rep("""       file's own lastUpdated. The cache-buster keeps raw.githubusercontent's CDN from serving an
       hour-old copy. Local harness runs rewrite this host to the local data/ (tools/harness/run.js). */
    const DATA_BASE_URL = 'https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/';
    const DATA_BUST = '?t=' + Date.now();""",
       """       file's own lastUpdated. c12 (Audit III, 2026-10-07): the old `?t=` cache-buster never reached the CDN (it ignores the
       query and serves ≤ 300 s stale regardless) — it only stopped the browser caching; `{cache:'no-cache'}` revalidates
       instead (a 304 when unchanged). Local harness runs rewrite this host to the local data/ (tools/harness/run.js). */
    const DATA_BASE_URL = 'https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/';
    const DATA_BUST = '';
    const DATA_FETCH = { cache: 'no-cache' };""")
le.rep("""fetch(`${DATA_BASE_URL}treasury-recent.json${DATA_BUST}`)""", """fetch(`${DATA_BASE_URL}treasury-recent.json${DATA_BUST}`, DATA_FETCH)""")
for f in ['treasury-wallet1-txns', 'treasury-wallet2-txns', 'treasury-wallet1-tokens', 'treasury-wallet2-tokens', 'treasury-summary']:
    le.rep(f"fetch(`${{DATA_BASE_URL}}{f}.json${{DATA_BUST}}`)", f"fetch(`${{DATA_BASE_URL}}{f}.json${{DATA_BUST}}`, DATA_FETCH)")
le.save()

# ================================================================= tools/harness — the build writes the site file; run.js swaps the link
pk = Edit('tools/harness/package.json')
pk.rep('''    "css": "tailwindcss -c tailwind.config.js -i tw.in.css -o tw.out.css",''',
       '''    "css": "tailwindcss -c tailwind.config.js -i tw.in.css -o tw.out.css && tailwindcss -c tailwind.config.js -i tw.in.css -o ../../tw.css --minify",''')
pk.save()
rj = Edit('tools/harness/run.js')
rj.rep("""  .replace(/<script src="https:\\/\\/cdn\\.tailwindcss\\.com\\/3\\.4\\.16"><\\/script>/,'<link rel="stylesheet" href="/__tw.css">')""",
       """  .replace(/<script src="https:\\/\\/cdn\\.tailwindcss\\.com\\/3\\.4\\.16"><\\/script>/,'<link rel="stylesheet" href="/__tw.css">')
  .replace(/<link rel="stylesheet" href="tw\\.css\\?v=\\d+">/,'<link rel="stylesheet" href="/__tw.css">')   // c13: the pages link the committed tw.css; the harness renders with its fresh build""", done_marker='c13: the pages link the committed tw.css')
rj.save()
print('audit3-p5: done')
