#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka): (1) the cards' NET stands apart — "+28 joined · −37 left | −9 NET" (a divider, the NET number
a touch bigger, the joined / left words a touch smaller); (2) the cards' quiet words ("PTGC held", "avg per shark") +1 px;
(3) a one-sentence STORY right under the big chart, before the footer — it follows the league, the period and the basis:
"1 YEAR IN SHARKS · Shark wallets fell from 105 → 96 (−8.6%), while their combined holdings fell from 88.80B → 76.69B PTGC (−13.6%)."
Idempotent, from the repo root:   python3 tools/lh-story.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
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

# (1) the divider before NET
edit(J, "<span className=\"w\">left</span></span> <span className=\"w d\">{'\\u00B7'}</span> ",
        "<span className=\"w\">left</span></span> <span className=\"w bar\">|</span> ")
edit(J, "<span className=\"w\">NET</span></span></>;})()",
        "<span className=\"w nl\">NET</span></span></>;})()")
edit(J, "<span className=\"g\"><b className={sg(nt)}>", "<span className=\"g nt\"><b className={sg(nt)}>")

# (3) the story
STORY = """                {(()=>{const[n]=LH_TIERS[sel],a=rows[i0][sel],b=rows[last][sel];   /* the one-sentence story under the chart (Shaka, 2026-10-24) */
                  const PL={'7D':'7 DAYS','30D':'30 DAYS','90D':'90 DAYS','6M':'6 MONTHS','1Y':'1 YEAR','ALL':'ALL TIME'};
                  const lab=pd[1]!=null&&pd[1]>last?'SINCE LAUNCH':PL[per]||per;
                  const pc=(x,y)=>x>0?` (${y>=x?'+':'\\u2212'}${Math.abs((y-x)/x*100).toFixed(1)}%)`:'';
                  const vb=(x,y,f,u)=>x===y?<>held steady at <b>{f(y)}</b>{u}</>:<>{y>x?'rose':'fell'} from <b>{f(x)}</b> {'\\u2192'} <b>{f(y)}</b>{u}{pc(x,y)}</>;
                  return<div className="lh-story"><span className="k">{lab} IN {n.toUpperCase()}S</span> {'\\u00B7'} {n} wallets {vb(a,b,lhFmt,'')}
                    {held&&<>, while their combined holdings {vb(held[i0][sel],held[last][sel],fmtAbbr,` ${tok}`)}</>}.</div>;})()}
"""
edit(J, "                <div className=\"lh-foot\">", STORY + "                <div className=\"lh-foot\">")

CSS = """
    /* 2026-10-24 (Shaka): NET apart on the cards, quiet words +1 px, the story line under the chart */
    .lh-cd .hd2 .w,.lh-cd .av .w{font-size:15px}.lh-cd .hd2{font-size:17.5px}.lh-cd .hd2 b.sp{font-size:16px}.lh-cd .jl{font-size:15.5px}   @media(min-width:700.02px){.lh-cd{padding-left:10px;padding-right:7px}}   /* numbers a hair smaller + 3 px more width so the longest lines (Shrimp, Shell) stay on one line */
    .lh-cd .jl .w{font-size:13px}.lh-cd .jl .w.bar{margin:0 2px 0 1px;color:rgba(255,255,255,.32)}
    .lh-cd .jl .nt b{font-size:17px}.lh-cd .jl .w.nl{font-size:14px;color:rgba(255,255,255,.62);font-weight:700}
    .lh-story{margin-top:16px;padding:12px 16px;border-radius:14px;background:linear-gradient(90deg,rgba(var(--rgb),.1),rgba(0,0,0,.35));border:1px solid rgba(var(--rgb),.28);
      font-size:17px;line-height:1.45;color:rgba(255,255,255,.78);font-weight:500}
    .lh-story b{color:#fff;font-weight:700}.lh-story .k{font:700 12.5px 'Orbitron',sans-serif;letter-spacing:.14em;color:var(--a2)}
    @media(max-width:700px){.lh-cd .hd2 .w,.lh-cd .av .w{font-size:13px}.lh-cd .jl .w{font-size:11.5px}.lh-cd .jl .nt b{font-size:15.5px}.lh-cd .jl .w.nl{font-size:12px}
      .lh-story{font-size:15px;padding:10px 12px}.lh-story .k{font-size:11px}}
"""
s = open(C, encoding='utf-8').read()
if "NET apart on the cards" not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-story: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
