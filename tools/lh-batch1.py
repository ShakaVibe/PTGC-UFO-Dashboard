#!/usr/bin/env python3
"""League History — roadmap batch 1 (2026-10-24, Shaka picked "Fixes", "Easier to read", "Speed": lh2–lh7, lh9–lh11, lh13, lh15).
  lh2 + lh11  the hover box is gone: a READOUT ROW above the big chart always shows a day — the latest one, or the one under the
              mouse / finger (no clipping at the phone edges, nothing covering the top of the chart); on a phone the day stays
              after the finger lifts, with a LATEST button to go back.
  lh3         the subtitle's start date comes from the file (PTGC Oct 11, 2023 · UFO Jul 9, 2026), not hard-coded text.
  lh4         the file is re-read when the window opens and the copy in the tab is over an hour old.
  lh5         a card that did not move is read as "no change" (was "up 0").
  lh6         the third pill says "SHARE" on phones (SHARE OF SUPPLY wrapped to three lines; "% OF SUPPLY" still wrapped at 360 px).
  lh7         data/league-history.json schema 4: counts and tokens held DELTA-encoded per day (the first day whole), tokens held in
              units of 10,000 tokens, the burn line in whole tokens — 319 KB → ~155 KB (gzipped 137 → ~60 KB). The window decodes it
              once on load. The builder reuses the old file's burn readings across the schema change (no 1,100 RPC re-reads).
  lh9         the big chart's geometry is built once per data / width (useMemo); a mouse move only moves the cursor and the readout.
  lh10        the total holders is on the big chart's title line whenever the ALL HOLDERS pill is not showing (BOTH, TOKENS HELD).
  lh13        each card: "~799M per shark" (tokens per wallet).
  lh15        the footer says the history runs to yesterday's close while the dashboard strip is hourly (a count can differ by one).
Idempotent, from the repo root:   python3 tools/lh-batch1.py   (twice: "0 edit(s)"); then  node scripts/build-league-history.mjs
(the file goes to schema 4 on the first run). Re-splices via tools/league-history.py.
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
    """replace the text from `start` up to (not incl.) `end` with `new` — once (skipped when `new` is already there)"""
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    a = s.index(start); b = s.index(end, a)
    assert s.count(start) == 1, f'{path}: block start x{s.count(start)}'
    open(path, 'w', encoding='utf-8').write(s[:a] + new + s[b:]); n += 1

J, C, B = 'tools/league-history/lh.jsx', 'tools/league-history/lh.css', 'scripts/build-league-history.mjs'

# ======================= the builder: schema 4 (lh7)
edit(B, "const SCHEMA = 3;   // 2 (2026-10-24): the burn wallet counts in its league (`burnIn`); 3: + `held` — the tokens each league holds per day",
        "const SCHEMA = 4;   // 2 (2026-10-24): the burn wallet counts in its league (`burnIn`); 3: + `held` — the tokens each league holds per day;\n"
        "                    // 4 (lh7): start / circ / held DELTA-encoded per day (row 0 whole), held in units of HELD_UNIT tokens, burned in whole tokens\n"
        "const HELD_UNIT = 1e4;   // 10,000 tokens — the window prints 2 decimals of M / B, so nothing it shows changes\n"
        "const delta = rows => rows.map((r, k) => k ? r.map((v, i) => v - rows[k - 1][i]) : r.slice());")
edit(B, "  if (prev && prev.archiveDay0 === days[0] && prev.lastDay === lastDay && !process.env.FORCE_LH) {",
        "  if (prev && prevFile.schema === SCHEMA && prev.archiveDay0 === days[0] && prev.lastDay === lastDay && !process.env.FORCE_LH) {")
edit(B, "start: start.slice(k0), circ: circ.slice(k0), held: { start: hS.slice(k0), circ: hC.slice(k0) }, flows, burnIn,",
        "start: delta(start.slice(k0)), circ: delta(circ.slice(k0)),\n"
        "    held: { start: delta(hS.slice(k0).map(r => r.map(v => Math.round(v / HELD_UNIT)))), circ: delta(hC.slice(k0).map(r => r.map(v => Math.round(v / HELD_UNIT)))) }, flows, burnIn,")
edit(B, "    archiveDay0: days[0], burned: burned.map(v => Math.round(v * 1e6) / 1e6) };",
        "    archiveDay0: days[0], burned: burned.map(v => v == null ? null : Math.round(v)) };")
edit(B, "return j && j.schema === SCHEMA ? j : null; } catch (e) {",
        "return j && j.schema >= 2 ? j : null; } catch (e) {   // any schema ≥ 2: its burn readings are reused (a schema change rebuilds the rest)")
edit(B, "const out = { schema: SCHEMA, generatedAt: null, tiers: TIERS.map(t => t[0]), thresholds: TIERS.map(t => t[1]),",
        "const out = { schema: SCHEMA, generatedAt: null, enc: { rows: 'delta', heldUnit: HELD_UNIT }, tiers: TIERS.map(t => t[0]), thresholds: TIERS.map(t => t[1]),")

# ======================= the window
# lh4 + lh7: re-read after an hour; decode schema 4
edit(J, """    let lhP=null;
    const lhLoad=()=>lhP||(lhP=dataFetch(LH_URL).then(r=>r.ok?r.json():null).catch(()=>null)
      .then(j=>{const ok=j&&j.schema>=1&&j.tokens&&j.tokens.PTGC;if(!ok)lhP=null;return ok?j:null;}));""",
"""    /* lh7 (schema 4): start / circ / held are DELTA-encoded per day (row 0 whole) and held is in units of enc.heldUnit tokens —
       decoded once here, so everything below reads plain per-day rows (schema 1–3 files pass through as they are) */
    const lhUndelta=(rows,m=1)=>{const o=[];let p=null;for(const r of rows||[]){const c=p?r.map((v,i)=>v+p[i]):r.slice();o.push(c);p=c;}return m===1?o:o.map(r=>r.map(v=>v*m));};
    const lhDecode=j=>{if(!(j.schema>=4))return j;const u=(j.enc&&j.enc.heldUnit)||1;
      for(const k in j.tokens){const t=j.tokens[k];t.start=lhUndelta(t.start);t.circ=lhUndelta(t.circ);if(t.held)t.held={start:lhUndelta(t.held.start,u),circ:lhUndelta(t.held.circ,u)};}return j;};
    /* lh4: the read is kept for an hour, then the next opening re-reads it (no-cache = a 304 when the file did not change) */
    let lhP=null,lhAt=0;
    const lhLoad=()=>{if(lhP&&Date.now()-lhAt<36e5)return lhP;lhAt=Date.now();
      return lhP=dataFetch(LH_URL).then(r=>r.ok?r.json():null).catch(()=>null)
        .then(j=>{const ok=j&&j.schema>=1&&j.tokens&&j.tokens.PTGC;if(!ok){lhP=null;return null;}try{return lhDecode(j);}catch(e){lhP=null;return null;}});};""")

# lh2 + lh9 + lh11: the chart
NEW_CHART = """    /* lh9 (2026-10-24): the geometry is built once per data / width (useMemo) — a mouse move only moves the cursor and the readout.
       lh2 + lh11: no floating hover box — the READOUT row above the plot always shows a day: the latest, or the one under the mouse /
       finger (never clipped at a phone edge, never over the lines); on a phone the day stays after the finger lifts (LATEST = back).
       rd(k) → [main text, second text | null] for day k of the slice. */
    const lhNice=r=>{const p=10**Math.floor(Math.log10(r||1));return[1,2,2.5,5,10].map(m=>m*p).find(s=>s>=r)||r||1;};
    const LhChart=({vals,day0,i0,col,f=lhFmt,what="Count",v2=null,f2=fmtAbbr,col2='#7DD3FC',rd=null})=>{
      const box=useRef(null);const[w,setW]=useState(900);const[hv,setHv]=useState(null);const[pin,setPin]=useState(false);
      useEffect(()=>{const el=box.current;if(!el)return;const on=()=>setW(Math.max(260,Math.round(el.clientWidth)));on();
        const ro=typeof ResizeObserver!=='undefined'?new ResizeObserver(on):null;if(ro)ro.observe(el);else window.addEventListener('resize',on);
        return()=>{if(ro)ro.disconnect();else window.removeEventListener('resize',on);};},[]);
      useEffect(()=>{setHv(null);setPin(false);},[vals.length,i0,day0]);   // another period / token: back to the latest day
      const g=useMemo(()=>{
        const ph=w<560,H=ph?230:290,L=ph?40:48,R=v2?(ph?44:56):12,T=16,B=28;
        const mn0=Math.min(...vals),mx0=Math.max(...vals),pad=Math.max(1,Math.round((mx0-mn0)*.12));   // f: lhFmt (wallets) or fmtAbbr (tokens held)
        let mn=Math.max(0,mn0-pad),mx=mx0+pad;const r0=(mx-mn)/4,p10=10**Math.floor(Math.log10(r0||1));
        const step=[1,2,2.5,5,10].map(m=>m*p10).filter(s=>f!==lhFmt||(s>=1&&Number.isInteger(s))).find(s=>s>=r0)||r0||1;   // counts: whole steps only
        mn=Math.floor(mn/step)*step;mx=Math.ceil(mx/step)*step;if(mx===mn)mx=mn+step;
        const X=k=>L+k/(vals.length-1||1)*(w-L-R),Y=v=>T+(1-(v-mn)/(mx-mn))*(H-T-B);
        const ticks=[];for(let v=mn;v<=mx+1e-9;v+=step)ticks.push(v);
        const long=vals.length>200,nt=ph?(long?3:4):6,xt=[];/* phone + a long period (dates with the year): 3 labels */for(let t=0;t<nt;t++)xt.push(Math.round(t/(nt-1)*(vals.length-1)));
        const pts=vals.map((v,k)=>`${X(k).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
        let Y2=null,pts2='',r2=[];
        if(v2){const nd=ticks.length-1,a0=Math.min(...v2),b0=Math.max(...v2),pd2=(b0-a0)*.12||b0*.05||1,lo=Math.max(0,a0-pd2),hi2=b0+pd2;
          let st=lhNice((hi2-lo)/nd),m2=Math.floor(lo/st)*st;for(let q=0;q<12&&m2+st*nd<hi2;q++){st=lhNice(st*1.001);m2=Math.floor(lo/st)*st;}
          Y2=v=>T+(1-(v-m2)/(st*nd))*(H-T-B);pts2=v2.map((v,k)=>`${X(k).toFixed(1)},${Y2(v).toFixed(1)}`).join(' ');
          r2=ticks.map((v,j)=>[Y(v),m2+st*j]);}
        const last=vals.length-1;
        return{ph,H,L,R,T,B,mn,mx,mn0,mx0,X,Y,Y2,ticks,xt,nt,long,pts,pts2,r2,last,hi:vals.indexOf(mx0),lo:vals.lastIndexOf(mn0)};
      },[vals,v2,w,f]);
      const{H,L,R,T,B,mn,mn0,mx0,X,Y,Y2,ticks,xt,nt,long,pts,pts2,r2,last,hi,lo}=g;
      const gid=`lhg${col.slice(1)}`;
      /* pointer events: a finger / pen PINS the day (it stays after lifting — LATEST goes back); the mouse follows and leaves */
      const at=e=>{const el=box.current;if(!el)return;const rc=el.getBoundingClientRect();const x=e.clientX-rc.left;
        const k=Math.round((x-L)/(rc.width-L-R)*(vals.length-1));setHv(Math.max(0,Math.min(last,k)));setPin(e.pointerType!=='mouse');};
      const k=hv!=null&&hv<=last?hv:null,kk=k!=null?k:last;
      const[r1,r2t]=rd?rd(kk):[f(vals[kk]),v2?`hold ${f2(v2[kk])}`:null];
      return(
        <div className="lh-ch" ref={box}>
          <div className="lh-rd"><small>{lhDate(lhDay(day0,i0+kk),true)}{k==null?' \\u00B7 latest':''}</small><b>{r1}</b>{r2t&&<span className="t2">{r2t}</span>}
            {pin&&k!=null&&<button type="button" className="lh-rdx" onClick={()=>{setHv(null);setPin(false);}}>LATEST</button>}</div>
          <svg viewBox={`0 0 ${w} ${H}`} role="img" aria-label={`${what} over the period: ${f(vals[0])} to ${f(vals[last])}, high ${f(mx0)}, low ${f(mn0)}`}
            onPointerDown={at} onPointerMove={at} onPointerLeave={e=>{if(e.pointerType==='mouse')setHv(null);}}>
            <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity=".32"/><stop offset="1" stopColor={col} stopOpacity="0"/></linearGradient>
              {v2&&<linearGradient id={gid+'b'} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col2} stopOpacity=".26"/><stop offset="1" stopColor={col2} stopOpacity=".02"/></linearGradient>}</defs>
            {ticks.map(v=><g key={v}><line x1={L} x2={w-R} y1={Y(v)} y2={Y(v)} stroke="rgba(255,255,255,.07)"/><text x={L-8} y={Y(v)+4} fill="rgba(255,255,255,.5)" fontSize="12" fontFamily="Rajdhani" fontWeight="600" textAnchor="end">{f(v)}</text></g>)}
            {xt.map((q,t)=><text key={t} x={X(q)} y={H-8} fill="rgba(255,255,255,.5)" fontSize="12" fontFamily="Rajdhani" fontWeight="600" textAnchor={t===0?'start':t===nt-1?'end':'middle'}>{lhDate(lhDay(day0,i0+q),long)}</text>)}
            {v2&&<>{r2.map(([y,v],j)=><text key={'r'+j} x={w-R+7} y={y+4} fill={col2} fillOpacity=".75" fontSize="12" fontFamily="Rajdhani" fontWeight="600">{f2(v)}</text>)}
              <path d={`M${X(0)},${Y(mn)} L${pts2.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid}b)`}/>
              <polyline points={pts2} fill="none" stroke={col2} strokeOpacity=".85" strokeWidth="1.8" strokeLinejoin="round"/>
              <circle cx={X(last)} cy={Y2(v2[last])} r="4.5" fill={col2} stroke="#05070c" strokeWidth="2"/></>}
            {!v2&&<path d={`M${X(0)},${Y(mn)} L${pts.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid})`}/>}
            <polyline points={pts} fill="none" stroke={col} strokeWidth="2.6" strokeLinejoin="round"/>
            {hi!==last&&hi!==0&&mx0!==mn0&&<g><circle cx={X(hi)} cy={Y(mx0)} r="4.5" fill="#05070c" stroke={col} strokeWidth="2.5"/><text x={Math.min(w-R-24,Math.max(L+24,X(hi)))} y={Y(mx0)-12} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">high {f(mx0)}</text></g>}
            {lo!==last&&lo!==0&&lo!==hi&&mx0!==mn0&&<g><circle cx={X(lo)} cy={Y(mn0)} r="4.5" fill="#05070c" stroke={col} strokeWidth="2.5"/><text x={Math.min(w-R-24,Math.max(L+24,X(lo)))} y={Y(mn0)+21} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">low {f(mn0)}</text></g>}
            <circle cx={X(last)} cy={Y(vals[last])} r="6" fill={col} stroke="#05070c" strokeWidth="2"/>
            {k!=null&&<g><line x1={X(k)} x2={X(k)} y1={T} y2={H-B} stroke="rgba(255,255,255,.35)" strokeDasharray="3 4"/><circle cx={X(k)} cy={Y(vals[k])} r="5" fill={col} stroke="#05070c" strokeWidth="2"/>{v2&&<circle cx={X(k)} cy={Y2(v2[k])} r="4.5" fill={col2} stroke="#05070c" strokeWidth="2"/>}</g>}
          </svg>
        </div>);
    };
"""
block(J, "    /* v2 (2026-10-24, Shaka: \"an overlay line chart of the token counts\")", "    /* the share card:", NEW_CHART)

# the chart calls: rd per view
NEW_CALLS = """                    {(()=>{const nm=n.toLowerCase(),un=c=>`${lhFmt(c)} ${c===1?nm:nm+'s'}`;   // lh2: what the readout row says for day q of the slice
                      const hl=q=>{const v=held[i0+q][sel],sh=shareOf(v,i0+q);return`${sh!=null?`${sh}% of supply`:''}`;};
                      return tm?<LhChart key="t" vals={held.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} f={fmtAbbr} what="Tokens held"
                          rd={q=>[`${fmtAbbr(held[i0+q][sel])} held`,hl(q)||null]}/>
                        :bm?<LhChart key="b" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} what={`${n}s (wallets) and the tokens they hold`}
                          v2={held.slice(i0).map(r=>r[sel])} rd={q=>{const v=held[i0+q][sel],c=rows[i0+q][sel],sh=shareOf(v,i0+q),e=per1(v,c);return[un(c),`hold ${fmtAbbr(v)}${sh!=null?` (${sh}%)`:''}${e&&c>1?` \\u00B7 ~${e} each`:''}`];}}/>
                        :<LhChart key="w" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} rd={q=>[un(rows[i0+q][sel]),null]}/>;})()}
"""
block(J, "                    {tm?<LhChart key=\"t\"", "                  </div>);})()}", NEW_CALLS)

# lh3: the start date from the file
edit(J, "<div className=\"lh-sub\">How many of each sea creature hold {tok} {'—'} every day since {isU?'Jul 8, 2026':'launch, Oct 2023'}</div>",
        "<div className=\"lh-sub\">How many of each sea creature hold {tok} {'—'} every day since {t?lhDate(lhDay(t.day0,0),true):'launch'}</div>")
# lh5: "no change"
edit(J, "aria-label={`${n}: ${lhFmt(b)} now, ${b-a>=0?'up':'down'} ${lhFmt(Math.abs(b-a))} over ${pd[2]} — show the chart`}",
        "aria-label={`${n}: ${lhFmt(b)} now, ${b===a?'no change':`${b>a?'up':'down'} ${lhFmt(Math.abs(b-a))}`} over ${pd[2]} — show the chart`}")
# lh6: the pill's short label on phones
edit(J, "<div className=\"lh-pill\"><div className=\"k\">SHARE OF SUPPLY</div>",
        "<div className=\"lh-pill\"><div className=\"k\"><span className=\"lg\">SHARE OF SUPPLY</span><span className=\"sm\">SHARE</span></div>")
# lh10: total holders on the title line when the pill is not showing
edit(J, "                      {bm&&<div className=\"s s2\">hold <b>{fmtAbbr(held[i0][sel])}</b>",
        "                      {(tm||bm)&&<div className=\"s s3\"><b>{lhFmt(total)}</b> holders of {tok} in all</div>}\n"
        "                      {bm&&<div className=\"s s2\">hold <b>{fmtAbbr(held[i0][sel])}</b>")
# lh13: tokens per wallet on each card
edit(J, "                    {held&&<div className=\"hd2\">hold <b>{fmtAbbr(held[last][i])}</b> {'\\u00B7'} {shareOf(held[last][i],last)}%</div>}",
        "                    {held&&<div className=\"hd2\">hold <b>{fmtAbbr(held[last][i])}</b> {'\\u00B7'} {shareOf(held[last][i],last)}%</div>}\n"
        "                    {held&&<div className=\"av\">{b>1?<>~<b>{per1(held[last][i],b)}</b> per {n.toLowerCase()}</>:b===1?'one wallet':'no wallets'}</div>}")
# lh15: the footer note
edit(J, "joined {'−'} left = the change.</div>",
        "joined {'−'} left = the change. The history runs to yesterday{'’'}s close (UTC); the creature strip on the dashboard is updated every hour, so a count there can differ by one or two.</div>")

# CSS
CSS = """
    /* roadmap batch 1 (2026-10-24): the readout row (lh2 / lh11), the phone pill label (lh6), holders line (lh10), per-wallet line (lh13) */
    .lh-rd{display:flex;flex-wrap:wrap;align-items:baseline;gap:2px 10px;min-height:26px;margin-top:12px;font-size:16px;font-weight:700;color:#fff}
    .lh-rd small{font-size:13.5px;font-weight:600;color:rgba(255,255,255,.55)}.lh-rd .t2{font-size:14.5px;color:#7DD3FC}
    .lh-rdx{margin-left:auto;font:700 10.5px 'Orbitron',sans-serif;letter-spacing:.12em;padding:4px 9px;border-radius:8px;border:1px solid rgba(var(--rgb),.55);background:rgba(var(--rgb),.12);color:var(--a2);cursor:pointer}
    .lh-ch{margin-top:4px}.lh-ch svg{touch-action:pan-y}
    .lh-pill .k .sm{display:none}
    .lh-bh .s3{font-size:13.5px;color:rgba(255,255,255,.55);margin-top:1px}.lh-bh .s3 b{color:rgba(255,255,255,.85)}
    .lh-cd .av{margin-top:3px;font-size:13.5px;color:rgba(255,255,255,.5);font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.lh-cd .av b{color:rgba(255,255,255,.82);font-weight:700}
    @media(max-width:700px){.lh-pill .k .lg{display:none}.lh-pill .k .sm{display:inline}.lh-rd{font-size:15px}.lh-rd .t2{font-size:13.5px}.lh-cd .av{font-size:12.5px}}
"""
s = open(C, encoding='utf-8').read()
if 'roadmap batch 1 (2026-10-24)' not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1

# ---- the harness: LOCAL_DATA=1 answers the repo's raw data/*.json reads from this checkout (tests a data file before it is pushed)
H = 'tools/harness/run.js'
edit(H, "    if(slowHist&&/data\\/[a-z-]*history[a-z-]*\\.json/.test(u))await sleep(slowHist);",
        "    if(slowHist&&/data\\/[a-z-]*history[a-z-]*\\.json/.test(u))await sleep(slowHist);\n"
        "    if(process.env.LOCAL_DATA){const m=u.match(/raw\\.githubusercontent\\.com\\/[^/]+\\/[^/]+\\/main\\/(data\\/[\\w./-]+\\.json)/);const fp=m&&path.join(REPO,m[1]);"
        "if(fp&&fs.existsSync(fp))return r.fulfill({status:200,contentType:'application/json',headers:{'access-control-allow-origin':'*'},body:fs.readFileSync(fp)});}   // LOCAL_DATA=1: this checkout's data/*.json")

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-batch1: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}, builder {sha(B)}')
