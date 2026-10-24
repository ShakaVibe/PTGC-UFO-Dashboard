#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka: "make each sea creature icon larger... and brighten the image that's at the top a little more"):
the cards' creatures 42 → 60 px (phone 34 → 46), the big chart's 54 → 70 px (phone 56), the beam tip's 38 → 46 px; the header art
brighter (the image itself +30 %, the dark veil lighter; a soft dark pool stays behind the title so it reads); each card's
sparkline in its league's colour (the beam's).
Idempotent, from the repo root:   python3 tools/lh-icons-sky.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
C, J = 'tools/league-history/lh.css', 'tools/league-history/lh.jsx'
# + "make the spark lines for each tile match the color of the icon": each card's sparkline in its league's beam colour
edit(J, "                    <LhSpark vals={rows.slice(i0).map(r=>r[i])} col={col}/>",
        "                    <LhSpark vals={rows.slice(i0).map(r=>r[i])} col={LH_BEAM_C[i][1]}/>   {/* the league's colour (the beam's) */}")
CSS = """
    /* 2026-10-24 (Shaka): bigger sea creatures, a brighter header picture */
    .lh-cd .top img{width:60px;height:60px}.lh-bh .l img{width:70px;height:70px}.lh-bm-tip img{width:46px;height:46px}
    .lh-hd .sky{filter:brightness(1.3) saturate(1.1)}
    .lh-hd .veil{background:linear-gradient(180deg,rgba(5,7,12,.12) 0%,rgba(5,7,12,.3) 55%,#05070c 100%),radial-gradient(ellipse 45% 80% at 50% 45%,rgba(0,0,0,.42),rgba(0,0,0,0) 80%)}
    @media(max-width:700px){.lh-cd .top img{width:46px;height:46px}.lh-bh .l img{width:56px;height:56px}}
"""
s = open(C, encoding='utf-8').read()
if 'bigger sea creatures, a brighter header picture' not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1
out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-icons-sky: {n} edit(s); index.html {sha("index.html")}, lh.css {sha(C)}')
