#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka: "I see the low marked on the chart, I don't see the high"): the High pill was hidden whenever
the period's high fell on its FIRST day (PTGC Sharks 1Y: 105 on Oct 23, 2025) or on the last; now the high is the LAST day it was
reached and both pills show wherever they fall (a flat line still shows neither).
Idempotent, from the repo root:   python3 tools/lh-high.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
J = 'tools/league-history/lh.jsx'
def swap(old, new):
    global n
    s = open(J, encoding='utf-8').read()
    if old not in s: return
    open(J, 'w', encoding='utf-8').write(s.replace(old, new, 1)); n += 1
swap("hi:vals.indexOf(mx0),lo:vals.lastIndexOf(mn0)", "hi:vals.lastIndexOf(mx0),lo:vals.lastIndexOf(mn0)")
swap("{hi!==last&&hi!==0&&mx0!==mn0&&", "{mx0!==mn0&&")
swap("{lo!==last&&lo!==0&&lo!==hi&&mx0!==mn0&&", "{mx0!==mn0&&")
out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-high: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}')
