#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka: "audit this page … also make all the small text a little bigger"):
  - every small text in the window ~1 px bigger (toggles, card names / thresholds / burn label, pills, legend, hover, axis labels,
    footer), on desktop and phone — ONE override block at the end of tools/league-history/lh.css, so the earlier rules stay as they were;
  - fix: the y-axis rounding of the big chart was swallowed by a `//` comment in d81faff1 (the axis started at odd values such as
    89 / 94 / 99 / 104 and the top line was not a round number) — the rounding is on its own line again.
Idempotent, from the repo root:   python3 tools/lh-text-axis.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
J, C = 'tools/league-history/lh.jsx', 'tools/league-history/lh.css'

edit(J, "   // counts: whole steps onlymn=Math.floor(mn/step)*step;",
        "   // counts: whole steps only\n      mn=Math.floor(mn/step)*step;")

TEXT = """
    /* 2026-10-24 (Shaka: "make all the small text a little bigger"): the small text ~1 px up — overrides, so the rules above stay as built */
    .lh-cam{font-size:12px}.lh-tg button{font-size:11.5px}.lh-mode button{font-size:11px}
    .lh-cd .nm{font-size:12px}.lh-cd .th{font-size:13.5px}.lh-cd .bwl{font-size:11.5px}
    .lh-bh h3{font-size:14px}.lh-bh .s2{font-size:14.5px}.lh-pill .k{font-size:10.5px}
    .lh-lg{font-size:13.5px}.lh-tip{font-size:14.5px}.lh-tip .t2{font-size:13px}
    .lh-ch svg text{font-size:13px}   /* the axis + high / low labels (CSS beats the SVG attribute) */
    .lh-foot{font-size:14px}.lh-wait button{font-size:12px}.lh-strip .lh-go{font-size:10px}
    @media(max-width:700px){.lh-tg button{font-size:10.5px}.lh-cd .th{font-size:12.5px}.lh-cd .hd2{font-size:14px}.lh-cd .jl{font-size:13.5px}.lh-foot{font-size:13.5px}}
    @media(max-width:359.98px){.lh-tg button{font-size:10px}}
"""
s = open(C, encoding='utf-8').read()
if 'make all the small text a little bigger' not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + TEXT.lstrip('\n')); n += 1

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-text-axis: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
