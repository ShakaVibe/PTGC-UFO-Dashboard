#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka: "make sure that it defaults back to 1 year every time they come to the page", "this text a
little larger" [the cards' hold / per-wallet / joined-left], "darken the background of the chart section more", "use the logo at
the top that we use on the dashboard" [the lit coin], "update the card to have the new look"):
  - the period is NOT remembered any more: every opening starts on 1Y (the localStorage read / write are gone);
  - the cards' three lines ~2 px bigger; the chart panel's veil darker;
  - the header coin = the dashboard's lit coin (LgCoin: halo, corona, flares — the Leagues window's) at the old 112 px (phone 84);
  - the share card (Wide 1200 × 675) redrawn in the window's new look: the lit coin, the ownership beam, the eight leagues with the
    big creatures, count + change on one line, "hold … · …%", league-coloured sparklines, the holder-wallets total.
Idempotent, from the repo root:   python3 tools/lh-card-v2.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
def block(path, start, end, new):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    a = s.index(start); b = s.index(end, a)
    open(path, 'w', encoding='utf-8').write(s[:a] + new + s[b:]); n += 1
J, C = 'tools/league-history/lh.jsx', 'tools/league-history/lh.css'

# 1. always 1Y on opening
edit(J, "      const LH_PER_KEY='grays_lh_per_v2';   // v2 (2026-10-24): the default became 1Y — a new key so an earlier pick of 6M does not stick\n"
        "      const[per,setPer]=useState(()=>{const v=lsGet(LH_PER_KEY);return LH_PERS.some(p=>p[0]===v)?v:'1Y';});",
        "      const[per,setPer]=useState('1Y');   // every opening starts on 1Y (Shaka, 2026-10-24) — the pick is not remembered")
edit(J, "      const setP=k=>{setPer(k);lsSet(LH_PER_KEY,k);};", "      const setP=k=>setPer(k);")

# 4. the lit coin in the header
edit(J, "<div className=\"lh-hc\"><img className=\"lh-coin\" src={TOKENS[tok].logo} alt=\"\"/>",
        "<div className=\"lh-hc\"><div className=\"lh-coinw\"><LgCoin token={tok}/></div>")

# 5. the share card, new look
CARD = """    /* the share card — Wide 1200 × 675 (screenshot-only, like the other v2 cards). v2 (2026-10-24, Shaka: "update the card to have the
       new look"): the lit coin, the ownership beam, the eight leagues with the big creatures, count + change on one line, the tokens
       held, league-coloured sparklines. */
    const LhShareCard=({tok,t,per,basis,i0,shareOf})=>{const isU=tok==='UFO',rows=t[basis],last=rows.length-1,pd=LH_PERS.find(p=>p[0]===per);
      const held=t.held&&t.held[basis],total=rows[last].reduce((s,v)=>s+v,0);
      return(
        <div className={`lh-card v2${isU?' u':''}`}><div className="sky"></div><div className="veil"></div><div className="in">
          <div className="tt"><div className="cw"><LgCoin token={tok}/></div><div className="tx"><div className="h"><span className="t">{tok}</span> LEAGUE HISTORY</div>
            <div className="pd">{(i0===0&&pd[1]!=null&&pd[1]>last)||pd[0]==='ALL'?'Since launch':`Last ${pd[2]}`} {'\\u00B7'} {lhDate(lhDay(t.day0,i0),true)} {'\\u2192'} {lhDate(lhDay(t.day0,last),true)}</div></div>
            <div className="tot"><b>{lhFmt(total)}</b><span>holder wallets</span></div></div>
          {held&&<div className="bmw"><LhBeam t={t} tok={tok} basis={basis} last={last} onSel={()=>{}} shareOf={shareOf}/></div>}
          <div className="g">{LH_TIERS.map(([n,img],i)=>{const a=rows[i0][i],b=rows[last][i],sh=held?shareOf(held[last][i],last):null;return(
            <div className="c" key={n}><div className="r1"><img src={lhSea(img)} alt=""/><div className="nm">{n.toUpperCase()}</div></div>
              <div className="vr"><span className="ft">{lhFmt(b)}</span><span className="ch"><LhChange a={a} b={b}/></span></div>
              {held&&<div className="hd">hold <b>{fmtAbbr(held[last][i])}</b>{sh!=null&&<> {'\\u00B7'} {sh}%</>}</div>}
              <LhSpark vals={rows.slice(i0).map(r=>r[i])} w={240} h={40} col={LH_BEAM_C[i][1]}/></div>);})}</div></div>
          <div className="bt"><span>People only + the {'\\u{1F525}'} burn wallet {'\\u00B7'} {basis==='circ'?'circulating':'starting'} supply {'\\u00B7'} rebuilt from the chain</span><b>PTGC-UFO.COM</b></div>
        </div>);
    };
"""
block(J, "    /* the share card: Wide 1200 × 675, the eight leagues then → now with sparklines", "    const LeagueHistoryModal=", CARD)
edit(J, "<LhShareCard tok={tok} t={t} per={per} basis={basis} i0={i0}/>", "<LhShareCard tok={tok} t={t} per={per} basis={basis} i0={i0} shareOf={shareOf}/>")

CSS = """
    /* 2026-10-24 (Shaka): bigger card lines, a darker chart panel, the lit coin, the share card v2 */
    .lh-cd .hd2{font-size:18.5px}.lh-cd .av{font-size:17px}.lh-cd .jl{font-size:18px}
    .lh-big{background:linear-gradient(180deg,rgba(5,7,12,.7) 0%,rgba(5,7,12,.78) 45%,rgba(5,7,12,.9) 100%),url(logos/leagues/lh-chart-bg.webp) 50% 45%/cover no-repeat}
    .lh-hd{padding-top:30px}
    .lh-coinw{position:relative;width:112px;height:112px}
    .lh-coinw .lg-coin{--u:.574px;--halo:255,120,20;--ring:255,190,80}.lh-win.u .lh-coinw .lg-coin{--halo:110,255,40;--ring:140,255,60}
    .lh-hc h2{position:relative;z-index:1}
    @media(max-width:700px){.lh-cd .hd2{font-size:15.5px}.lh-cd .av{font-size:14.5px}.lh-cd .jl{font-size:15.5px}
      .lh-hd{padding-top:24px}.lh-coinw{width:84px;height:84px}.lh-coinw .lg-coin{--u:.431px}}
    .lh-card.v2 .in{padding:30px 44px 0}
    .lh-card.v2 .tt{display:flex;align-items:center;gap:26px}
    .lh-card.v2 .cw{position:relative;width:86px;height:86px;flex:none;margin-left:6px}
    .lh-card.v2 .cw .lg-coin{--u:.441px;--halo:255,120,20;--ring:255,190,80}.lh-card.v2.u .cw .lg-coin{--halo:110,255,40;--ring:140,255,60}
    .lh-card.v2 .tx{position:relative;z-index:1;flex:1;min-width:0}.lh-card.v2 .h{font-size:38px}
    .lh-card.v2 .tot{position:relative;z-index:1;text-align:right}.lh-card.v2 .tot b{display:block;font:700 34px 'Orbitron',sans-serif;color:#fff}.lh-card.v2 .tot span{font-size:18px;color:rgba(255,255,255,.65);font-weight:600}
    .lh-card.v2 .bmw{margin:22px 0 0}.lh-card.v2 .bmw .lh-bm{margin:0 4px}
    .lh-card.v2 .g{margin-top:22px;gap:14px}
    .lh-card.v2 .c{padding:12px 16px 10px;background:rgba(0,0,0,.6)}
    .lh-card.v2 .c img{width:58px;height:58px;object-fit:contain}.lh-card.v2 .c .nm{font-size:14px}
    .lh-card.v2 .vr{display:flex;align-items:baseline;gap:10px;margin-top:6px;white-space:nowrap}
    .lh-card.v2 .vr .ft{font:700 30px 'Orbitron',sans-serif}.lh-card.v2 .vr .ch{font-size:18px;font-weight:700}
    .lh-card.v2 .hd{font-size:18px;color:rgba(255,255,255,.62);font-weight:600;margin-top:3px}.lh-card.v2 .hd b{color:#fff}
    .lh-card.v2 .c svg{height:40px;margin-top:6px}
"""
s = open(C, encoding='utf-8').read()
if 'the lit coin, the share card v2' not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-card-v2: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
