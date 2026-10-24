#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka's card-text mock-up — "a typography / information-hierarchy improvement, not a rebuild"):
inside each of the eight cards, numbers strong, words quiet —
  "76.69B PTGC held · 23.0% supply" (amount white, the share cyan, the words small grey),
  "~798.83M avg per shark" (one wallet / no wallets unchanged),
  "+28 joined · −37 left · −9 NET" (NET = joined − left over the period; each number green / red / grey by its sign).
Card size, art, selected glow, colours, sparklines, data and clicks unchanged.
Idempotent, from the repo root:   python3 tools/lh-card-text.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
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
edit(J, "{held&&<div className=\"hd2\">hold <b>{fmtAbbr(held[last][i])}</b> {'\\u00B7'} {shareOf(held[last][i],last)}%</div>}",
        "{held&&(()=>{const sh=shareOf(held[last][i],last);return<div className=\"hd2\"><span className=\"g\"><b>{fmtAbbr(held[last][i])}</b> <span className=\"w\">{tok} held</span></span>"
        "{sh!=null&&<> <span className=\"w d\">{'\\u00B7'}</span> <span className=\"g\"><b className=\"sp\">{sh}%</b> <span className=\"w\">supply</span></span></>}</div>;})()}")
edit(J, "{held&&<div className=\"av\">{b>1?<>~<b>{per1(held[last][i],b)}</b> per {n.toLowerCase()}</>:b===1?'one wallet':'no wallets'}</div>}",
        "{held&&<div className=\"av\">{b>1?<><b>~{per1(held[last][i],b)}</b> <span className=\"w\">avg per {n.toLowerCase()}</span></>:b===1?'one wallet':'no wallets'}</div>}")
edit(J, "<div className=\"jl\">{fl?<><b className=\"lh-up\">+{lhFmt(fl[0][i])}</b> joined {'·'} <b className=\"lh-dn\">{'−'}{lhFmt(fl[1][i])}</b> left</>:'\u00a0'}</div>",
        "<div className=\"jl\">{fl?(()=>{const jn=fl[0][i],lf=fl[1][i],nt=jn-lf,sg=v=>v>0?'lh-up':v<0?'lh-dn':'z';return<>"
        "<span className=\"g\"><b className={jn>0?'lh-up':'z'}>+{lhFmt(jn)}</b> <span className=\"w\">joined</span></span> <span className=\"w d\">{'\\u00B7'}</span> "
        "<span className=\"g\"><b className={lf>0?'lh-dn':'z'}>{'\\u2212'}{lhFmt(lf)}</b> <span className=\"w\">left</span></span> <span className=\"w d\">{'\\u00B7'}</span> "
        "<span className=\"g\"><b className={sg(nt)}>{nt>0?'+':nt<0?'\\u2212':''}{lhFmt(Math.abs(nt))}</b> <span className=\"w\">NET</span></span></>;})():'\u00a0'}</div>")
CSS = """
    /* 2026-10-24 (Shaka's card-text mock-up): numbers strong, words quiet */
    .lh-cd .hd2,.lh-cd .av,.lh-cd .jl{white-space:normal;overflow:visible;line-height:1.3}.lh-cd .g{white-space:nowrap}.lh-cd .w.d{margin:0 -2px}   /* a line wraps only between groups (never \"supply\" alone); tight dots keep Shrimp / Shell on one line */
    .lh-cd .hd2{font-size:18px;margin-top:9px;letter-spacing:-.01em}.lh-cd .hd2 b{color:#fff;font-weight:700}
    .lh-cd .hd2 b.sp{color:#5CC8FF;font-size:16.5px}
    .lh-cd .av{font-size:17px;margin-top:4px;color:rgba(255,255,255,.82)}.lh-cd .av b{color:#fff;font-weight:700}
    .lh-cd .jl{font-size:16px;margin-top:6px;letter-spacing:-.01em}.lh-cd .jl b{font-weight:700}.lh-cd .jl b.z{color:rgba(255,255,255,.75)}
    .lh-cd .w{font-size:14px;font-weight:600;color:rgba(255,255,255,.5)}@media(min-width:700.02px){.lh-cd{padding-left:11px;padding-right:9px}}
    @media(max-width:700px){.lh-cd .hd2{font-size:15.5px}.lh-cd .hd2 b.sp{font-size:14.5px}.lh-cd .av{font-size:14.5px}.lh-cd .jl{font-size:14.5px}.lh-cd .w{font-size:12.5px}}
"""
s = open(C, encoding='utf-8').read()
if "card-text mock-up): numbers strong" not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1
out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-card-text: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
