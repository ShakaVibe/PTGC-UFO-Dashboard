#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka, on the big chart's header: "why the discrepancy of holders.. 18206 on the front page.. 17081 here",
"make that text larger … from the 98-96 and the line under it", "make the joined left and share bigger boxes and bigger text", "make
the text that has the date and 96 sharks etc larger"):
  - the holders line names what it counts: "17,081 holder wallets · people only — pools and contracts not counted" (the dashboard's
    HOLDERS tile counts every address holding the token, ~1,100 of them contracts: LP pairs, routers, bots, contract wallets); the
    WALLETS-view pill reads HOLDER WALLETS.
  - bigger: the big chart's title lines (wallets / holders / hold), the JOINED / LEFT / SHARE boxes and their text, the readout row.
    One override block at the end of lh.css.
Idempotent, from the repo root:   python3 tools/lh-bigger.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
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

edit(J, "{(tm||bm)&&<div className=\"s s3\"><b>{lhFmt(total)}</b> holders of {tok} in all</div>}",
        "{(tm||bm)&&<div className=\"s s3\"><b>{lhFmt(total)}</b> holder wallets {'\\u00B7'} people only {'\\u2014'} pools and contracts not counted</div>}")
edit(J, "<div className=\"lh-pill\"><div className=\"k\">ALL HOLDERS</div>",
        "<div className=\"lh-pill\" title=\"People only: pools and contracts are not counted (the dashboard's HOLDERS counts every address)\"><div className=\"k\">HOLDER WALLETS</div>")

CSS = """
    /* 2026-10-24 (Shaka): bigger big-chart title lines, JOINED / LEFT / SHARE boxes and the readout row */
    .lh-bh .s{font-size:18px;margin-top:4px}.lh-bh .s2{font-size:17px}.lh-bh .s3{font-size:16px}
    @media(min-width:700.02px){.lh-bh{flex-wrap:nowrap;align-items:center}.lh-bh .l{flex:1 1 auto}.lh-bh .r{flex:none}}   /* the boxes stay at the right; the title lines wrap instead */
    .lh-bh .r{gap:12px}.lh-pill{padding:11px 18px;min-width:118px;border-radius:14px}
    .lh-pill .k{font-size:12px}.lh-pill .n{font-size:26px;margin-top:5px}
    .lh-rd{font-size:19.5px;min-height:30px}.lh-rd small{font-size:16px}.lh-rd .t2{font-size:17.5px}
    @media(max-width:700px){.lh-bh .s{font-size:16px}.lh-bh .s2{font-size:15px}.lh-bh .s3{font-size:14px}
      .lh-bh .r{gap:8px}.lh-pill{padding:9px 10px;min-width:0}.lh-pill .k{font-size:11px;letter-spacing:.1em}.lh-pill .n{font-size:21px}
      .lh-rd{font-size:17px}.lh-rd small{font-size:14.5px}.lh-rd .t2{font-size:15.5px}}
"""
s = open(C, encoding='utf-8').read()
if 'bigger big-chart title lines' not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-bigger: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
