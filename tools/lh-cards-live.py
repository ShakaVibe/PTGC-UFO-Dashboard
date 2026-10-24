#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka's six): (1) the selected card is obvious — lifted, a soft gold / blue inner glow and an
"IN THE CHART" tab on its bottom edge; (2) every card reacts on hover — the creature grows ~10 %, the border lights in the
creature's own colour, the sparkline brightens (click = the big chart, as before); (3) a "High · Low" line on each card (over the
chosen period, like its sparkline); (4) the plot area behind the lines ~15 % darker and the two lines glow, so they dominate;
(5) the big chart's creature is the panel's mascot — larger, overlapping its upper-left edge; (6) NET CHANGE first among the boxes
(joined − left, coloured), JOINED / LEFT / SHARE kept.
Idempotent, from the repo root:   python3 tools/lh-cards-live.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
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

# (1) + (2): the creature's colour on each card (hover border / glow), the IN THE CHART tab on the selected one
edit(J, "<button type=\"button\" key={n} className=\"lh-cd\" aria-pressed={sel===i} onClick={()=>setSel(i)}",
        "<button type=\"button\" key={n} className=\"lh-cd\" style={{'--cc':LH_BEAM_C[i][1],'--cg':LH_BEAM_C[i][3]}} aria-pressed={sel===i} onClick={()=>setSel(i)}")
# (3) High · Low over the period, above the sparkline; the tab after it
edit(J, "                    <LhSpark vals={rows.slice(i0).map(r=>r[i])} col={LH_BEAM_C[i][1]}/>   {/* the league's colour (the beam's) */}",
        "                    {(()=>{const v=rows.slice(i0).map(r=>r[i]);return<div className=\"hl\">High <b>{lhFmt(Math.max(...v))}</b> {'\\u00B7'} Low <b>{lhFmt(Math.min(...v))}</b></div>;})()}\n"
        "                    <LhSpark vals={rows.slice(i0).map(r=>r[i])} col={LH_BEAM_C[i][1]}/>   {/* the league's colour (the beam's) */}\n"
        "                    {sel===i&&<span className=\"lh-on\" aria-hidden=\"true\">{'\\u25BC'} IN THE CHART</span>}")
# (4) the lines glow
edit(J, "<polyline points={pts} fill=\"none\" stroke={col} strokeWidth=\"2.6\" strokeLinejoin=\"round\"/>",
        "<polyline points={pts} fill=\"none\" stroke={col} strokeWidth=\"2.8\" strokeLinejoin=\"round\" style={{filter:`drop-shadow(0 0 5px ${col})`}}/>")
edit(J, "<polyline points={pts2} fill=\"none\" stroke={col2} strokeOpacity=\".85\" strokeWidth=\"1.8\" strokeLinejoin=\"round\"/>",
        "<polyline points={pts2} fill=\"none\" stroke={col2} strokeOpacity=\".95\" strokeWidth=\"2.2\" strokeLinejoin=\"round\" style={{filter:`drop-shadow(0 0 4px ${col2})`}}/>")
# the right-hand axis labels ("270.00B" at 13 px) were clipped on phones: more room on that side
edit(J, "R=v2?(ph?44:56):12", "R=v2?(ph?54:60):12")
# (6) NET CHANGE first
edit(J, "<div className=\"r\"><div className=\"lh-pill\"><div className=\"k\">JOINED</div>",
        "<div className=\"r\">{(()=>{const nt=fl?fl[0][sel]-fl[1][sel]:b-a;return<div className=\"lh-pill net\"><div className=\"k\"><span className=\"lg\">NET CHANGE</span><span className=\"sm\">NET</span></div>"
        "<div className={`n ${nt>0?'lh-up':nt<0?'lh-dn':''}`}>{nt>0?'+':nt<0?'\\u2212':''}{lhFmt(Math.abs(nt))}</div></div>;})()}"
        "<div className=\"lh-pill\"><div className=\"k\">JOINED</div>")

CSS = """
    /* 2026-10-24 (Shaka's six): the selected card, live hover, High · Low, darker plot + glowing lines, the mascot, NET CHANGE */
    .lh-cd{transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
    .lh-cd .top img{transition:transform .18s ease,filter .18s ease}.lh-cd svg{transition:filter .18s ease}
    .lh-cd:not([aria-pressed=true]):hover{border-color:var(--cc);box-shadow:0 0 18px rgba(var(--cg),.38),inset 0 0 14px rgba(var(--cg),.1)}
    .lh-cd:hover .top img{transform:scale(1.1);filter:drop-shadow(0 0 10px rgba(var(--cg),.55))}
    .lh-cd:hover svg{filter:brightness(1.45) drop-shadow(0 0 4px rgba(var(--cg),.8))}
    .lh-cd[aria-pressed=true]{transform:translateY(-5px);border-width:1.5px;
      box-shadow:0 14px 30px rgba(0,0,0,.6),0 0 26px rgba(var(--rgb),.4),inset 0 0 26px rgba(var(--rgb),.16),inset 0 -18px 34px rgba(56,189,248,.08)}
    .lh-cd[aria-pressed=true] svg{filter:brightness(1.3) drop-shadow(0 0 3px rgba(var(--cg),.7))}
    .lh-on{position:absolute;left:50%;bottom:-11px;transform:translateX(-50%);z-index:2;white-space:nowrap;padding:3px 10px;border-radius:99px;
      font:700 9.5px 'Orbitron',sans-serif;letter-spacing:.14em;color:#0a0b10;background:linear-gradient(180deg,var(--a2),var(--a));box-shadow:0 0 12px rgba(var(--rgb),.6)}
    .lh-cd .hl{margin-top:5px;font-size:14.5px;color:rgba(255,255,255,.5);font-weight:600}.lh-cd .hl b{color:rgba(255,255,255,.85);font-weight:700}
    .lh-ch{border-radius:12px;background:radial-gradient(ellipse 62% 70% at 50% 58%,rgba(2,4,9,.62),rgba(2,4,9,.38) 70%,rgba(2,4,9,.2) 100%)}
    .lh-big{margin-top:46px}
    .lh-bh .l{position:relative;padding-left:104px;min-height:84px}
    .lh-bh .l img{position:absolute;left:-26px;top:-48px;width:128px;height:128px;z-index:3;filter:drop-shadow(0 8px 14px rgba(0,0,0,.75)) drop-shadow(0 0 16px rgba(var(--rgb),.25))}
    .lh-bh{flex-wrap:wrap!important}.lh-bh .l{flex:1 1 100%}.lh-bh .r{width:100%;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:14px}.lh-bh .r .lh-pill{min-width:0}   /* four boxes: their own row */
    .lh-pill.net{border-color:rgba(var(--rgb),.55);box-shadow:inset 0 0 18px rgba(var(--rgb),.1)}.lh-pill.net .n{font-size:30px}
    @media(max-width:700px){.lh-cd .hl{font-size:13px}.lh-on{font-size:8.5px;bottom:-9px;padding:2px 8px}
      .lh-big{margin-top:36px}.lh-bh .l{padding-left:72px;min-height:60px}.lh-bh .l img{left:-14px;top:-36px;width:88px;height:88px}
      .lh-bh .r{display:grid;grid-template-columns:1fr 1fr;width:100%}.lh-pill.net .n{font-size:24px}}
    @media(hover:none){.lh-cd:hover .top img{transform:none}}
    @media(prefers-reduced-motion:reduce){.lh-cd,.lh-cd .top img{transition:none}.lh-cd[aria-pressed=true]{transform:none}}
"""
s = open(C, encoding='utf-8').read()
if "Shaka's six): the selected card" not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-cards-live: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
