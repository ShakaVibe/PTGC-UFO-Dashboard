#!/usr/bin/env python3
"""2026-10-24 (Shaka: 'next to the 1 Poseidon, lets put "The Burn address"' + 'could we add an overlay line chart of the token
counts … use what you think makes it good'):
  - index.html: the Token Allocation creature strip names the burn wallet next to its league's count — "THE BURN ADDRESS" when it
    is the only wallet there (PTGC's 1 Poseidon), "INCL. THE BURN ADDRESS" when it shares the league (UFO's Whales today).
  - tools/league-history/lh.jsx + lh.css: the same label on the League History card; the big chart gets BOTH (now the default):
    the league's wallets as the bold line (left axis) over the tokens they hold as a sky-blue area (right axis, its ticks on the
    same grid lines), a legend, and a two-line hover (wallets · held, share of supply, tokens per wallet). WALLETS / TOKENS HELD
    stay as the single views.
  - the window opens on 1 year (was 6 months) with the Sharks chart; the cards' "hold" and "joined · left" lines are bigger.
Idempotent, from the repo root:   python3 tools/burn-label-overlay.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

IX, J, C = 'index.html', 'tools/league-history/lh.jsx', 'tools/league-history/lh.css'

# ---- the dashboard strip: the label next to the count
edit(IX, "<span className=\"x tabular-nums\">{tierCountLabel(tiers,k)}</span></span>))}\n      </div>);",
         "<span className=\"x tabular-nums\">{tierCountLabel(tiers,k)}</span>{tiers&&tiers.burnIn===k&&<span className=\"bwl\">{tiers[k]===1?'The Burn address':'incl. the Burn address'}</span>}</span>))}\n"
         "        {tiers&&tiers.burnIn&&<div className=\"bwn\">{'\\u{1F525}'} {tiers[tiers.burnIn]===1?`${tiers.burnIn} = the Burn address`:`${tiers.burnIn}s include the Burn address`}</div>}   {/* the phone's caption line */}\n      </div>);")
edit(IX, "    .p2 .p2-strip .e{position:relative}.p2 .p2-strip .bw{",
         "    .p2 .p2-strip .bwl{font-size:10px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;line-height:1.1;color:#FDBA74;max-width:66px;margin-left:-2px}   /* 2026-10-24: \"The Burn address\" */\n"
         "    .p2 .p2-strip .bwn{display:none}   /* the phone shows it as a caption line under the creatures instead (no room beside the count) */\n"
         "    .p2 .p2-strip .e{position:relative}.p2 .p2-strip .bw{")
edit(IX, ".p2 .p2-strip .x{font-size:13px}",
         ".p2 .p2-strip .x{font-size:13px}.p2 .p2-strip{flex-wrap:wrap}.p2 .p2-strip .bwl{display:none}.p2 .p2-strip .bwn{display:block;flex-basis:100%;text-align:center;margin-top:5px;font-size:10px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#FDBA74}")

# ---- League History: the card label
edit(J, "<div><div className=\"nm\">{n}</div><div className=\"th\">{th?`≥ ${th} of supply`:'below Shrimp'}</div></div></div>",
        "<div><div className=\"nm\">{n}</div><div className=\"th\">{th?`≥ ${th} of supply`:'below Shrimp'}</div>{t.burnIn&&t.burnIn[basis]===i&&<div className=\"bwl\">{b===1?'The Burn address':'incl. the Burn address'}</div>}</div></div>")
edit(C, "    .lh-cd .th{font-size:12.5px;color:rgba(255,255,255,.45);font-weight:600}",
        "    .lh-cd .th{font-size:12.5px;color:rgba(255,255,255,.45);font-weight:600}\n"
        "    .lh-cd .bwl{font-size:10.5px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#FDBA74;margin-top:1px}   /* \"The Burn address\" */")

# ---- League History: the overlay chart
OLD_HEAD = """    const LhChart=({vals,day0,i0,col,f=lhFmt,what="Count"})=>{"""
NEW_HEAD = """    /* v2 (2026-10-24, Shaka: "an overlay line chart of the token counts"): a second series on its own right-hand axis, drawn as a
       sky-blue area BEHIND the wallets line; its ticks sit on the same grid lines (a nice step × the same number of divisions).
       unit = the hover's word for the first series ("sharks"); tip2(k) = the hover's second line for day k of the slice. */
    const lhNice=r=>{const p=10**Math.floor(Math.log10(r||1));return[1,2,2.5,5,10].map(m=>m*p).find(s=>s>=r)||r||1;};
    const LhChart=({vals,day0,i0,col,f=lhFmt,what="Count",unit=null,v2=null,f2=fmtAbbr,col2='#7DD3FC',tip2=null})=>{"""
edit(J, OLD_HEAD, NEW_HEAD)
edit(J, "      const ph=w<560,H=ph?230:290,L=ph?40:48,R=12,T=16,B=28;",
        "      const ph=w<560,H=ph?230:290,L=ph?40:48,R=v2?(ph?44:56):12,T=16,B=28;")
edit(J, """      const pts=vals.map((v,k)=>`${X(k).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');""",
        """      const pts=vals.map((v,k)=>`${X(k).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
      let Y2=null,pts2='',r2=[];
      if(v2){const nd=ticks.length-1,a0=Math.min(...v2),b0=Math.max(...v2),pd2=(b0-a0)*.12||b0*.05||1,lo=Math.max(0,a0-pd2),hi2=b0+pd2;
        let st=lhNice((hi2-lo)/nd),m2=Math.floor(lo/st)*st;for(let g=0;g<12&&m2+st*nd<hi2;g++){st=lhNice(st*1.001);m2=Math.floor(lo/st)*st;}
        Y2=v=>T+(1-(v-m2)/(st*nd))*(H-T-B);pts2=v2.map((v,k)=>`${X(k).toFixed(1)},${Y2(v).toFixed(1)}`).join(' ');
        r2=ticks.map((v,j)=>[Y(v),m2+st*j]);}""")
edit(J, """            <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity=".32"/><stop offset="1" stopColor={col} stopOpacity="0"/></linearGradient></defs>""",
        """            <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity=".32"/><stop offset="1" stopColor={col} stopOpacity="0"/></linearGradient>
              {v2&&<linearGradient id={gid+'b'} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col2} stopOpacity=".26"/><stop offset="1" stopColor={col2} stopOpacity=".02"/></linearGradient>}</defs>""")
edit(J, """            <path d={`M${X(0)},${Y(mn)} L${pts.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid})`}/>""",
        """            {v2&&<>{r2.map(([y,v],j)=><text key={'r'+j} x={w-R+7} y={y+4} fill={col2} fillOpacity=".75" fontSize="12" fontFamily="Rajdhani" fontWeight="600">{f2(v)}</text>)}
              <path d={`M${X(0)},${Y(mn)} L${pts2.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid}b)`}/>
              <polyline points={pts2} fill="none" stroke={col2} strokeOpacity=".85" strokeWidth="1.8" strokeLinejoin="round"/>
              <circle cx={X(last)} cy={Y2(v2[last])} r="4.5" fill={col2} stroke="#05070c" strokeWidth="2"/></>}
            {!v2&&<path d={`M${X(0)},${Y(mn)} L${pts.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid})`}/>}""")
edit(J, """<circle cx={X(hv)} cy={Y(vals[hv])} r="5" fill={col} stroke="#05070c" strokeWidth="2"/></g>}""",
        """<circle cx={X(hv)} cy={Y(vals[hv])} r="5" fill={col} stroke="#05070c" strokeWidth="2"/>{v2&&<circle cx={X(hv)} cy={Y2(v2[hv])} r="4.5" fill={col2} stroke="#05070c" strokeWidth="2"/>}</g>}""")
edit(J, """<small>{lhDate(lhDay(day0,i0+hv),true)}</small>{f(vals[hv])}</div>}""",
        """<small>{lhDate(lhDay(day0,i0+hv),true)}</small>{f(vals[hv])}{unit?` ${unit}`:''}{v2&&<div className="t2">{tip2?tip2(hv):`hold ${f2(v2[hv])}`}</div>}</div>}""")
edit(J, """      const[mode,setMode]=useState('w');   // the big chart: 'w' = wallets, 't' = tokens held (2026-10-24, Shaka: "how many tokens do those 107 wallets hold")""",
        """      const[mode,setMode]=useState('b');   // the big chart: 'b' = both (the overlay, default), 'w' = wallets, 't' = tokens held (2026-10-24, Shaka: "how many tokens do those 107 wallets hold" → "an overlay line chart")""")
edit(J, "      const tm=mode==='t'&&!!held;",
        "      const tm=mode==='t'&&!!held,bm=mode==='b'&&!!held;\n"
        "      const per1=(v,c)=>c>0&&v>0?fmtAbbr(v/c):null;   // tokens per wallet, for the hover")
edit(J, """<h3>{n.toUpperCase()}S {tm?'\\u2014 TOKENS HELD':'OVER TIME'}</h3>""",
        """<h3>{n.toUpperCase()}S {tm?'\\u2014 TOKENS HELD':bm?'\\u2014 WALLETS + TOKENS HELD':'OVER TIME'}</h3>""")
edit(J, """                        :<div className="s"><b>{lhFmt(a)}</b> {'→'} <b>{lhFmt(b)}</b> <LhChange a={a} b={b}/> <span style={{color:'rgba(255,255,255,.45)'}}>{'·'} {span}</span></div>}</div></div>""",
        """                        :<div className="s"><b>{lhFmt(a)}</b> {'→'} <b>{lhFmt(b)}</b> <LhChange a={a} b={b}/> <span style={{color:'rgba(255,255,255,.45)'}}>{'·'} {span}</span></div>}
                      {bm&&<div className="s s2">hold <b>{fmtAbbr(held[i0][sel])}</b> {'→'} <b>{fmtAbbr(held[last][sel])}</b> <LhChange a={held[i0][sel]} b={held[last][sel]} f={fmtAbbr}/></div>}</div></div>""")
edit(J, """                        {tm?<div className="lh-pill"><div className="k">SHARE OF SUPPLY</div>""",
        """                        {tm||bm?<div className="lh-pill"><div className="k">SHARE OF SUPPLY</div>""")
edit(J, """                    {held&&<div className="lh-tg lh-mode" role="group" aria-label="Chart"><button type="button" aria-pressed={!tm} onClick={()=>setMode('w')}>WALLETS</button><button type="button" aria-pressed={tm} onClick={()=>setMode('t')}>TOKENS HELD</button></div>}
                    {tm?<LhChart key="t" vals={held.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} f={fmtAbbr} what="Tokens held"/>
                      :<LhChart key="w" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col}/>}""",
        """                    {held&&<div className="lh-mrow"><div className="lh-tg lh-mode" role="group" aria-label="Chart"><button type="button" aria-pressed={bm} onClick={()=>setMode('b')}>BOTH</button><button type="button" aria-pressed={!tm&&!bm} onClick={()=>setMode('w')}>WALLETS</button><button type="button" aria-pressed={tm} onClick={()=>setMode('t')}>TOKENS HELD</button></div>
                      {bm&&<div className="lh-lg" aria-hidden="true"><span><i style={{background:col}}></i>Wallets <em>left</em></span><span><i className="a"></i>Tokens held <em>right</em></span></div>}</div>}
                    {tm?<LhChart key="t" vals={held.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} f={fmtAbbr} what="Tokens held"/>
                      :bm?<LhChart key="b" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} unit={`${n.toLowerCase()}${rows[last][sel]===1&&rows[i0][sel]<=1?'':'s'}`} what={`${n}s (wallets) and the tokens they hold`}
                          v2={held.slice(i0).map(r=>r[sel])} tip2={k=>{const v=held[i0+k][sel],c=rows[i0+k][sel],sh=shareOf(v,i0+k),e=per1(v,c);return`hold ${fmtAbbr(v)}${sh!=null?` (${sh}%)`:''}${e&&c>1?` \\u00B7 ~${e} each`:''}`;}}/>
                      :<LhChart key="w" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col}/>}""")
edit(C, "    .lh-mode{margin-top:12px;height:32px}.lh-mode button{font-size:10px}",
        "    .lh-mode{margin-top:12px;height:32px}.lh-mode button{font-size:10px}\n"
        "    .lh-mrow{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:8px 14px}   /* the chart toggle + the overlay legend */\n"
        "    .lh-lg{display:flex;gap:14px;font-size:12.5px;font-weight:700;color:rgba(255,255,255,.75)}.lh-lg span{display:flex;align-items:center;gap:6px}\n"
        "    .lh-lg i{display:block;width:16px;height:3px;border-radius:2px}.lh-lg i.a{height:10px;background:linear-gradient(180deg,rgba(125,211,252,.55),rgba(125,211,252,.12));border-top:2px solid #7DD3FC;border-radius:1px}\n"
        "    .lh-lg em{font-style:normal;font-weight:600;color:rgba(255,255,255,.4)}\n"
        "    .lh-bh .s2{font-size:13.5px;color:#7DD3FC;margin-top:1px}.lh-bh .s2 b{color:#BAE6FD}\n"
        "    .lh-tip .t2{font-size:12px;font-weight:700;color:#7DD3FC;margin-top:1px}")

# ---- 2026-10-24 (Shaka: "lets default to 1 year and the shark selection. and lets make the hold joined and left text in each card larger"):
#      1Y on open (a new key, so the 6M remembered from the first look does not stick), Shark is already the default; bigger card lines
edit(J, "      const[per,setPer]=useState(()=>{const v=lsGet(LS.LH_PER);return LH_PERS.some(p=>p[0]===v)?v:'6M';});",
        "      const LH_PER_KEY='grays_lh_per_v2';   // v2 (2026-10-24): the default became 1Y — a new key so an earlier pick of 6M does not stick\n"
        "      const[per,setPer]=useState(()=>{const v=lsGet(LH_PER_KEY);return LH_PERS.some(p=>p[0]===v)?v:'1Y';});")
edit(J, "      const setP=k=>{setPer(k);lsSet(LS.LH_PER,k);};", "      const setP=k=>{setPer(k);lsSet(LH_PER_KEY,k);};")
edit(C, "    .lh-cd .hd2{margin-top:4px;font-size:12.5px;", "    .lh-cd .hd2{margin-top:5px;font-size:14.5px;")
edit(C, "    .lh-cd .jl{margin-top:3px;font-size:12.5px;", "    .lh-cd .jl{margin-top:4px;font-size:14px;")
edit(C, ".lh-cd .th{font-size:11.5px}", ".lh-cd .th{font-size:11.5px}.lh-cd .hd2{font-size:13px}.lh-cd .jl{font-size:12.5px}")

# ---- two small fixes seen in the checks: wallet-count axes never take a 2.5 step (it printed 93 / 95 / 98 / 100 — 97.5 rounded);
#      a league holding nothing shows "0%", not "<0.001%"
edit(J, "      const step=[1,2,2.5,5,10].map(m=>m*p10).find(s=>s>=r0)||r0||1;",
        "      const step=[1,2,2.5,5,10].map(m=>m*p10).filter(s=>f!==lhFmt||(s>=1&&Number.isInteger(s))).find(s=>s>=r0)||r0||1;   // counts: whole steps only")
edit(J, "const shareOf=(v,k)=>{const sp=supAt(k);if(!(sp>0)||v==null)return null;const p=v/sp*100;",
        "const shareOf=(v,k)=>{const sp=supAt(k);if(!(sp>0)||v==null)return null;if(v===0)return'0';const p=v/sp*100;")

edit(J, "      const nt=ph?4:6,xt=[];", "      const nt=ph?(vals.length>200?3:4):6,xt=[];/* phone + a long period (dates with the year): 3 labels, else they run into each other */")

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'burn-label-overlay: {n} edit(s); index.html {sha(IX)}, lh.jsx {sha(J)}, lh.css {sha(C)}')
