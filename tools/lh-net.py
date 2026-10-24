#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka's mock-up: "here is where to add the NET box.. make the other three smaller if need to"):
a NET box between LEFT and SHARE OF SUPPLY, in the same row beside the title (joined − left over the period, coloured, a gold frame);
the four boxes a little smaller (labels centred) so the title keeps its width. Phone: the four in one row, smaller still.
Idempotent, from the repo root:   python3 tools/lh-net.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
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
LEFT = "<div className=\"lh-pill\"><div className=\"k\">LEFT</div><div className=\"n lh-dn\">{fl?'−'+lhFmt(fl[1][sel]):'—'}</div></div>"
edit(J, LEFT, LEFT + "\n                        {(()=>{const nt=fl?fl[0][sel]-fl[1][sel]:b-a;return<div className=\"lh-pill net\"><div className=\"k\">NET</div>"
        "<div className={`n ${nt>0?'lh-up':nt<0?'lh-dn':''}`}>{nt>0?'+':nt<0?'\\u2212':''}{lhFmt(Math.abs(nt))}</div></div>;})()}")
CSS = """
    /* 2026-10-24 (Shaka's mock-up): NET between LEFT and SHARE, four smaller boxes in the title row */
    .lh-bh .r{gap:8px}.lh-pill{padding:8px 11px;min-width:76px;text-align:center}.lh-pill .k{font-size:10.5px;letter-spacing:.1em}.lh-pill .n{font-size:22px;margin-top:4px}
    .lh-bh .l{padding-left:98px}.lh-bh h3{letter-spacing:.12em}   /* the title keeps one line beside the four boxes */
    .lh-pill.net{border-color:rgba(var(--rgb),.85);box-shadow:0 0 14px rgba(var(--rgb),.3),inset 0 0 16px rgba(var(--rgb),.12)}
    @media(max-width:700px){.lh-bh .r{gap:6px}.lh-pill{padding:8px 4px;min-width:0}.lh-pill .k{font-size:10px;letter-spacing:.08em}.lh-pill .n{font-size:18px}}
"""
s = open(C, encoding='utf-8').read()
if "NET between LEFT and SHARE" not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1
out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-net: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
