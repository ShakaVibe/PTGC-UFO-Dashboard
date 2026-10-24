#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka: "let's drop the high and low from the 8 tiles — that info is in the chart area already; that
will help make the tiles shorter"): the cards' "High · Low" line is removed (the big chart keeps its High / Low pills).
Idempotent, from the repo root:   python3 tools/lh-no-hilo.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
J = 'tools/league-history/lh.jsx'
OLD = "\n                    {(()=>{const v=rows.slice(i0).map(r=>r[i]);return<div className=\"hl\">High <b>{lhFmt(Math.max(...v))}</b> {'\\u00B7'} Low <b>{lhFmt(Math.min(...v))}</b></div>;})()}"
s = open(J, encoding='utf-8').read()
if OLD in s:
    open(J, 'w', encoding='utf-8').write(s.replace(OLD, '', 1)); n += 1
out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-no-hilo: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}')
