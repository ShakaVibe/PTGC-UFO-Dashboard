#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka's chart mock-up: axis titles, his underwater-ruins art behind the chart, larger creatures, a
one-line holders note):
  - the holders line: "17,081 holder wallets · people only" (one line);
  - the big chart: axis titles in the plot — WALLETS (left, the token colour) and TOKENS HELD (B / M / K) (right, sky blue) in BOTH;
    the single views title their one axis; high / low in a small dark pill; the legend as glowing dots "Wallets (left)" /
    "Tokens held (right)";
  - the chart panel's background = Shaka's art (logos/leagues/lh-chart-bg.webp, 1600 × 640, from his 1983 × 793 PNG) under a dark veil;
  - a stronger glowing border around the chart panel (2 px, the token colour);
  - the sea creatures larger again: cards 60 → 76 px (phone 46 → 56), the big chart's 70 → 92 px (phone 56 → 66).
Idempotent, from the repo root:   python3 tools/lh-chart-art.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
Needs logos/leagues/lh-chart-bg.webp (committed with it).
"""
import hashlib, os, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
J, C = 'tools/league-history/lh.jsx', 'tools/league-history/lh.css'
if not os.path.exists('logos/leagues/lh-chart-bg.webp'): sys.exit('logos/leagues/lh-chart-bg.webp is missing — it ships with this script')

# 1. the holders line
edit(J, "<b>{lhFmt(total)}</b> holder wallets {'\\u00B7'} people only {'\\u2014'} pools and contracts not counted</div>}",
        "<b>{lhFmt(total)}</b> holder wallets {'\\u00B7'} people only</div>}")

# 2. axis titles (tl / tr) — 18 px more room at the top of the plot when there is a title
edit(J, "const LhChart=({vals,day0,i0,col,f=lhFmt,what=\"Count\",v2=null,f2=fmtAbbr,col2='#7DD3FC',rd=null})=>{",
        "const lhUnit=v=>v>=1e9?'B':v>=1e6?'M':v>=1e3?'K':'';   // the tokens axis title's unit\n"
        "    const LhChart=({vals,day0,i0,col,f=lhFmt,what=\"Count\",v2=null,f2=fmtAbbr,col2='#7DD3FC',rd=null,tl=null,tr=null})=>{")
edit(J, "        const ph=w<560,H=ph?230:290,L=ph?40:48,R=v2?(ph?44:56):12,T=16,B=28;",
        "        const ph=w<560,tt=tl||tr?20:0,H=(ph?230:290)+tt,L=ph?40:48,R=v2?(ph?44:56):12,T=16+tt,B=28;")
edit(J, "      },[vals,v2,w,f]);", "      },[vals,v2,w,f,tl,tr]);")
edit(J, "            {ticks.map(v=><g key={v}><line x1={L}",
        "            {tl&&<text className=\"ttl\" x={2} y={14} fill={col} fontFamily=\"Orbitron\" fontWeight=\"700\" letterSpacing=\"1.4\">{tl}</text>}\n"
        "            {tr&&<text className=\"ttl\" x={w-2} y={14} fill={col2} fontFamily=\"Orbitron\" fontWeight=\"700\" letterSpacing=\"1.4\" textAnchor=\"end\">{tr}</text>}\n"
        "            {ticks.map(v=><g key={v}><line x1={L}")
# high / low in a pill
edit(J, """<text x={Math.min(w-R-24,Math.max(L+24,X(hi)))} y={Y(mx0)-12} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">high {f(mx0)}</text></g>}""",
        """{(()=>{const tx=`High ${f(mx0)}`,pw=tx.length*7.4+16,cx=Math.min(w-R-pw/2,Math.max(L+pw/2,X(hi))),cy=Y(mx0)-17;return<g><rect x={cx-pw/2} y={cy-10.5} width={pw} height={21} rx={10.5} fill="rgba(5,7,12,.85)" stroke={col} strokeOpacity=".7"/><text x={cx} y={cy+4.5} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">{tx}</text></g>;})()}</g>}""")
edit(J, """<text x={Math.min(w-R-24,Math.max(L+24,X(lo)))} y={Y(mn0)+21} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">low {f(mn0)}</text></g>}""",
        """{(()=>{const tx=`Low ${f(mn0)}`,pw=tx.length*7.4+16,cx=Math.min(w-R-pw/2,Math.max(L+pw/2,X(lo))),cy=Math.min(H-B-12,Y(mn0)+18);return<g><rect x={cx-pw/2} y={cy-10.5} width={pw} height={21} rx={10.5} fill="rgba(5,7,12,.85)" stroke={col} strokeOpacity=".7"/><text x={cx} y={cy+4.5} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">{tx}</text></g>;})()}</g>}""")
# the three calls name their axes
edit(J, """<LhChart key="t" vals={held.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} f={fmtAbbr} what="Tokens held\"""",
        """<LhChart key="t" vals={held.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} f={fmtAbbr} what="Tokens held" tl={`TOKENS HELD (${lhUnit(Math.max(...held.slice(i0).map(r=>r[sel])))})`}""")
edit(J, """<LhChart key="b" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} what=""",
        """<LhChart key="b" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} tl="WALLETS" tr={`TOKENS HELD (${lhUnit(Math.max(...held.slice(i0).map(r=>r[sel])))})`} what=""")
edit(J, """<LhChart key="w" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} rd=""",
        """<LhChart key="w" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} tl="WALLETS" rd=""")
# the legend: glowing dots, "(left)" / "(right)"
edit(J, "<span><i style={{background:col}}></i>Wallets <em>left</em></span><span><i className=\"a\"></i>Tokens held <em>right</em></span>",
        "<span><i style={{background:col,boxShadow:`0 0 9px ${col}`}}></i>Wallets <em>(left)</em></span><span><i className=\"a\"></i>Tokens held <em>(right)</em></span>")

CSS = """
    /* 2026-10-24 (Shaka's chart mock-up): the art behind the chart, axis titles, the dot legend, larger creatures */
    .lh-big{background:linear-gradient(180deg,rgba(5,7,12,.5) 0%,rgba(5,7,12,.62) 45%,rgba(5,7,12,.8) 100%),url(logos/leagues/lh-chart-bg.webp) 50% 45%/cover no-repeat}
    .lh-big{border:2px solid rgba(var(--rgb),.85);box-shadow:0 0 22px rgba(var(--rgb),.32),0 0 4px rgba(var(--rgb),.6),inset 0 0 26px rgba(var(--rgb),.07)}   /* + "a stronger border around the chart section" */
    .lh-ch svg text.ttl{font-size:11.5px}
    .lh-lg{font-size:15px;gap:18px}.lh-lg em{color:rgba(255,255,255,.55)}
    .lh-lg i{width:13px;height:13px;border-radius:50%;border:2px solid rgba(255,255,255,.85)}
    .lh-lg i.a{height:13px;background:#38BDF8;border:2px solid rgba(255,255,255,.85);border-radius:50%;box-shadow:0 0 9px #38BDF8}
    .lh-cd .top img{width:76px;height:76px}.lh-bh .l img{width:92px;height:92px}
    @media(max-width:700px){.lh-cd .top img{width:56px;height:56px}.lh-bh .l img{width:66px;height:66px}.lh-lg{font-size:13.5px;gap:12px}}
"""
s = open(C, encoding='utf-8').read()
if "Shaka's chart mock-up): the art behind" not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-chart-art: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}, bg {sha("logos/leagues/lh-chart-bg.webp")}')
