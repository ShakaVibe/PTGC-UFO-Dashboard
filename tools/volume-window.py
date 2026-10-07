#!/usr/bin/env python3
"""The Volume window (2026-10-07) — the Volume tile's ⓘ rebuilt to design/volume-analytics/mock-volume-v1.html.

Idempotent: python3 tools/volume-window.py [index.html]. Three edits:
  1. the `vw-*` CSS block after the Humans vs Bots `vs-*` block;
  2. `VolumeModal` (+ `vwDays`, `VwChart`) at module scope, just above `VolumeSplitModal`;
  3. the old inline "Volume Details Modal" JSX in Dashboard → `<VolumeModal …/>`.
Shaka (his screenshot of the old window): "It is still a dated look, and we need to upgrade to get in line with a lot of the
cosmetic changes we have made" → mock v1 ("that looks great, lets make the logo Bigger. and then make it live").
"""
import re, sys, hashlib

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()
if 'const VolumeModal=' in src:
    print('already applied'); sys.exit(0)

# ---------- 1. CSS ----------
CSS = r"""    /* ---- Volume window (2026-10-07): vw-* — the Volume tile's ⓘ, rebuilt to design/volume-analytics/mock-volume-v1.html. The Humans vs
       Bots shell; plate = the dashboard's own banner (gold half PTGC, green half UFO — one image, two crops); --tg = the token accent. ---- */
    .vw-sky{position:absolute;inset:0;background:url(logos/header/dash-bg.jpg) 14% 40%/auto 150% no-repeat}
    .vw-sky.ufo{background-position:90% 40%}
    .vw-veil{position:absolute;inset:0;background:radial-gradient(ellipse 46% 120% at 50% 42%,rgba(0,0,0,.42) 0%,rgba(0,0,0,.22) 55%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,.52) 58%,rgba(7,7,7,.88) 88%,#070707 100%)}
    .vw-coins{display:flex;align-items:center;justify-content:center;height:150px}   /* "make the logo Bigger" — .72 vs the HvB window's .5 */
    .vw-coins .lg-coin{--u:.72px;--halo:255,120,20;--ring:255,190,80}
    .vw-coins.g .lg-coin{--halo:110,255,40;--ring:140,255,60}
    .vw-k{font-size:12px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.55)}
    .vw-tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}
    .vw-tile{position:relative;border-radius:14px;border:1.5px solid rgba(var(--tg),.45);background:linear-gradient(180deg,rgba(var(--tg),.10),rgba(6,7,10,.9) 55%);box-shadow:inset 0 1px 0 rgba(255,255,255,.08);padding:12px 14px 11px;min-width:0}
    .vw-tile.live{border-color:rgba(var(--tg),.85);background:linear-gradient(180deg,rgba(var(--tg),.2),rgba(6,7,10,.9) 55%);box-shadow:inset 0 1px 0 rgba(255,255,255,.12),0 0 22px -6px rgba(var(--tg),.6)}
    .vw-tile .l{display:flex;align-items:center;justify-content:space-between;gap:6px}
    .vw-tile .l .p{font-family:'Orbitron',monospace;font-weight:700;font-size:11px;letter-spacing:.2em;color:rgb(var(--tg))}
    .vw-tile .l .ic{width:22px;height:22px;object-fit:contain;opacity:.9;max-width:none}
    .vw-tile .v{font-family:'Rajdhani',sans-serif;font-size:32px;font-weight:700;line-height:1;margin-top:9px;color:#fff;font-variant-numeric:tabular-nums;white-space:nowrap}
    .vw-tile .s{font-size:13.5px;font-weight:500;color:rgba(255,255,255,.6);margin-top:6px;white-space:nowrap}
    .vw-tile .s b{color:#fff;font-weight:600}
    .vw-dn{color:#FF2E3B}.vw-up{color:#4ADE80}
    .vw-card{margin-top:12px;border-radius:16px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.4);padding:14px 18px 14px}
    .vw-hdr{display:flex;align-items:baseline;justify-content:space-between;gap:10px;flex-wrap:wrap}
    .vw-hdr .t{font-family:'Orbitron',monospace;font-weight:700;font-size:13px;letter-spacing:.22em;text-transform:uppercase;color:rgb(var(--tg))}
    .vw-hdr .c{font-size:13px;color:rgba(255,255,255,.5);font-weight:600}
    .vw-cmp{display:grid;grid-template-columns:150px 1fr 96px;align-items:center;gap:14px;margin-top:12px}
    .vw-cmp .n{font-size:16px;font-weight:600;color:rgba(255,255,255,.85)}
    .vw-cmp .n small{display:block;font-size:12.5px;font-weight:500;color:rgba(255,255,255,.5)}
    .vw-cmp .tr{position:relative;height:12px;border-radius:999px;background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.08)}
    .vw-cmp .tr i{position:absolute;left:0;top:0;bottom:0;border-radius:999px;background:linear-gradient(90deg,rgba(var(--tg),.55),rgb(var(--tg)));box-shadow:0 0 12px rgba(var(--tg),.45)}
    .vw-cmp .tr b{position:absolute;top:-5px;bottom:-5px;width:2px;background:#fff;box-shadow:0 0 6px rgba(255,255,255,.8);left:50%}
    .vw-cmp .tr b::after{content:'avg';position:absolute;left:50%;top:-16px;transform:translateX(-50%);font-family:'Rajdhani',sans-serif;font-weight:600;font-size:10px;letter-spacing:.14em;text-transform:uppercase;color:rgba(255,255,255,.5)}
    .vw-cmp .pc{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
    .vw-cmp .pc .tri{font-size:14px;margin-right:4px}
    .vw-chartcard{position:relative;overflow:hidden;background:#06080d url(logos/hvb/wave.jpg) center 60%/cover no-repeat}
    .vw-chartcard.ufo{background-image:url(logos/panels/bg-vg.jpg);background-position:center 70%}
    .vw-chartcard::before{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,6,10,.78),rgba(4,6,10,.62) 40%,rgba(4,6,10,.72) 100%);pointer-events:none}
    .vw-chartcard>*{position:relative}
    .vw-chart{display:block;width:100%;height:190px;margin-top:8px}
    .vw-chart text{font-family:'Rajdhani',sans-serif;font-size:12px;font-weight:600;fill:rgba(255,255,255,.5)}
    .vw-key{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:4px}
    .vw-key span{display:inline-flex;align-items:center;gap:7px;font-size:14px;font-weight:600;color:rgba(255,255,255,.75);white-space:nowrap}
    .vw-key i{width:11px;height:11px;border-radius:3px;display:inline-block;background:rgb(var(--tg))}
    .vw-key i.avg{width:14px;height:0;border-top:2px dashed rgba(255,255,255,.75);border-radius:0;background:none}
    .vw-key i.today{opacity:.45}
    .vw-tbl{width:100%;border-collapse:collapse;margin-top:4px}
    .vw-th{font-size:12px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.55);padding:9px 8px;text-align:right;white-space:nowrap}
    .vw-td{padding:9px 8px;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;font-size:16px;font-weight:600;color:rgba(255,255,255,.9);border-top:1px solid rgba(255,255,255,.06)}
    .vw-th:first-child,.vw-td:first-child{text-align:left}
    .vw-rk{display:inline-flex;width:24px;height:24px;border-radius:50%;align-items:center;justify-content:center;font-family:'Orbitron',monospace;font-weight:700;font-size:10px;color:rgb(var(--tg));border:1px solid rgba(var(--tg),.6);margin-right:10px;vertical-align:middle;background:rgba(var(--tg),.08)}
    .vw-mini{display:inline-flex;height:6px;width:90px;border-radius:999px;overflow:hidden;background:rgba(255,255,255,.08);vertical-align:middle;margin-left:10px}
    .vw-mini i{display:block;height:100%;background:rgb(var(--tg))}
    .vw-more{display:block;width:100%;text-align:center;font-size:13px;font-weight:600;color:rgba(255,255,255,.5);padding-top:10px;background:none;border:0;cursor:pointer}
    .vw-more b{color:rgb(var(--tg));font-weight:700}
    .vw-more:hover{color:rgba(255,255,255,.8)}
    .vw-conf{margin:14px 4px 2px;font-size:12.5px;line-height:1.55;color:rgba(255,255,255,.42);text-align:center}
    .vw-conf::before{content:"";display:block;width:120px;height:1px;margin:0 auto 12px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.25),transparent)}
    .vw-wait{height:190px;border-radius:12px;background:rgba(255,255,255,.05);animation:pulse 2s cubic-bezier(.4,0,.6,1) infinite;margin-top:8px}
    @media(max-width:640px){.vw-coins{height:118px}.vw-coins .lg-coin{--u:.56px}.vw-tiles{grid-template-columns:1fr 1fr;gap:10px}.vw-tile .v{font-size:27px}.vw-tile .s{font-size:12.5px}
      .vw-cmp{grid-template-columns:96px 1fr 78px;gap:10px}.vw-cmp .n{font-size:14px}.vw-cmp .pc{font-size:19px}.vw-chart{height:150px}.vw-wait{height:150px}.vw-th,.vw-td{padding:8px 6px;font-size:15px}.vw-mini{width:48px}.vw-nophone{display:none}.vw-key{gap:4px 12px}.vw-key span{font-size:12.5px}}
"""
anchor_css = "    @media(max-width:640px){.vs-card{padding:14px 14px 12px}"
i = src.index(anchor_css)
j = src.index('\n', i) + 1
src = src[:j] + CSS + src[j:]

# ---------- 2. the component ----------
JSX = r"""    /* ---- VOLUME WINDOW (2026-10-07) — the Volume tile's ⓘ, rebuilt to design/volume-analytics/mock-volume-v1.html (README = the
       decisions; build tools/volume-window.py). The four figures are the tile's own (DexScreener 24h + volumeByPeriod's 7D / 30D / 90D,
       a19: null → "—"); the daily chart and the pool table are the Humans vs Bots hourly file (fetchSwapVolume — humans + bots summed,
       on-chain, 90 d), so they never match DexScreener to the dollar and the foot says so. States per gotcha 3 / a18. ---- */
    const VW_PERIODS=[{k:'7D',p:'7d',d:7},{k:'30D',p:'30d',d:30},{k:'90D',p:'90d',d:90}];
    const VW_ICON={PTGC:'logos/panels/lp-bars-gold.webp',UFO:'logos/panels/lp-bars-green.webp'};
    /* Pure: the file's hourly rows → one bar per UTC day, the last n full days plus today so far (`part`), oldest first. null = no rows. */
    const vwDays=(file,token,n)=>{
      const rows=file&&file.tokens&&file.tokens[token]&&file.tokens[token].hours;
      if(!rows||!rows.length)return null;
      const by={};rows.forEach(r=>{const k=Math.floor(r[0]/86400000);by[k]=(by[k]||0)+(r[2]||0)+(r[4]||0);});
      const today=Math.floor(Date.now()/86400000),out=[];
      for(let k=today-n;k<=today;k++)out.push({t:k*86400000,v:by[k]||0,part:k===today});
      return out;
    };
    const VwChart=({days,rgb,label})=>{
      const ref=React.useRef(null);const[W,setW]=useState(0);
      useEffect(()=>{const el=ref.current;if(!el)return;const m=()=>setW(el.clientWidth||0);m();
        if(typeof ResizeObserver!=='undefined'){const ro=new ResizeObserver(m);ro.observe(el);return()=>ro.disconnect();}
        window.addEventListener('resize',m);return()=>window.removeEventListener('resize',m);},[]);
      const H=(typeof window!=='undefined'&&window.innerWidth<640)?150:190,padT=16,padB=22;
      const full=days.filter(d=>!d.part),n=days.length;
      const avg=full.length?full.reduce((s,d)=>s+d.v,0)/full.length:0;
      const max=Math.max(1,...days.map(d=>d.v));
      const gap=n>40?1.5:n>10?4:10,bw=W?Math.min(64,(W-gap*(n-1))/n):0,x0=W?(W-(bw*n+gap*(n-1)))/2:0;
      const y=v=>padT+(H-padT-padB)*(1-v/max);
      const fmtD=t=>new Date(t).toLocaleDateString('en-US',{month:'short',day:'numeric',timeZone:'UTC'});
      const step=n>40?15:n>10?5:1,pk=days.findIndex(d=>d.v===max);
      return(
        <svg ref={ref} className="vw-chart" viewBox={W?`0 0 ${W} ${H}`:undefined} role="img" aria-label={label}>
          {W>0&&days.map((d,i)=>{const h=Math.max(0,y(0)-y(d.v)),x=x0+i*(bw+gap);return(
            <rect key={d.t} x={x} y={y(d.v)} width={bw} height={h} rx={Math.min(3,bw/3)} fill={`rgba(${rgb},${d.v===max?1:.78})`} opacity={d.part?.45:1}><title>{`${fmtD(d.t)}${d.part?' (today so far)':''} — ${fmtUSD(d.v)}`}</title></rect>);})}
          {W>0&&avg>0&&<line x1="0" x2={W} y1={y(avg)} y2={y(avg)} stroke="rgba(255,255,255,.75)" strokeWidth="1.5" strokeDasharray="5 5"/>}
          {W>0&&pk>=0&&<text x={Math.max(34,Math.min(x0+pk*(bw+gap)+bw/2,W-60))} y={padT-4} textAnchor="middle">{fmtUSD(max)}</text>}
          {W>0&&days.map((d,i)=>i%step===0?<text key={'t'+d.t} x={Math.min(W-18,Math.max(18,x0+i*(bw+gap)+bw/2))} y={H-5} textAnchor="middle">{fmtD(d.t)}</text>:null)}
        </svg>);
    };
    const VolumeModal=({token,data,volumeByPeriod,onClose})=>{
      const[win,setWin]=useState('30D');
      const[file,setFile]=useState(undefined);
      const[allPools,setAllPools]=useState(false);
      const load=(force)=>{setFile(undefined);fetchSwapVolume(force).then(setFile);};
      useEffect(()=>{let live=true;fetchSwapVolume().then(j=>{if(live)setFile(j);});return()=>{live=false;};},[]);
      useEffect(()=>{setAllPools(false);},[win]);
      const tk=token==='UFO'?'UFO':'PTGC',T=NH_THEME[tk],hex=T.hex,rgb=T.rgb,P=VW_PERIODS.find(w=>w.k===win)||VW_PERIODS[1];
      const v24=(data&&data.vol!=null&&isFinite(data.vol))?data.vol:null;   // a14: null → "—", never $0
      const vb=volumeByPeriod||{};
      const vol={'24H':v24,'7D':vb.vol7d==null?null:vb.vol7d,'30D':vb.vol30d==null?null:vb.vol30d,'90D':vb.vol90d==null?null:vb.vol90d};
      const avg=p=>vol[p]==null?null:vol[p]/{'7D':7,'30D':30,'90D':90}[p];
      const pctEl=(a,b)=>{if(a==null||b==null||!(b>0))return <span className="text-white/40">{'—'}</span>;const d=(a-b)/b*100;return <span className={d<0?'vw-dn':'vw-up'}><span className="tri">{d<0?'▼':'▲'}</span>{Math.abs(d).toFixed(1)}%</span>;};
      const days=React.useMemo(()=>file?vwDays(file,tk,P.d):null,[file,tk,win]);
      const per=file&&file.tokens[tk]&&file.tokens[tk].periods&&file.tokens[tk].periods[P.p];
      const pools=React.useMemo(()=>{if(!per||!per.pools)return null;return Object.values(per.pools).map(x=>({name:x.name||'pool',n:(x.human.n||0)+(x.bot.n||0),usd:(x.human.usd||0)+(x.bot.usd||0)})).filter(x=>x.usd>0).sort((a,b)=>b.usd-a.usd);},[per]);
      const poolTot=pools?pools.reduce((s,p)=>s+p.usd,0):0;
      const chartAvg=days?(()=>{const f=days.filter(d=>!d.part);return f.length?f.reduce((s,d)=>s+d.v,0)/f.length:null;})():null;
      const ageMs=file?Date.now()-Date.parse(file.generatedAt):null,amber=ageMs!=null&&ageMs>VS_AMBER_MS;
      const shown=pools?(allPools?pools:pools.slice(0,6)):[];
      return(
        <Modal onClose={onClose} label={`${tk} volume`} className="z-50 flex items-center justify-center p-0 sm:p-4 modal-overlay bg-black/85">
          <div onClick={e=>e.stopPropagation()} className="relative w-full h-[100dvh] sm:h-auto sm:max-h-[calc(100dvh-2rem)] sm:max-w-4xl flex flex-col rounded-none sm:rounded-3xl border bg-[#070707] overflow-y-auto overflow-x-hidden overscroll-contain" style={{borderColor:`${hex}55`,boxShadow:`0 0 80px -20px ${hex}66, 0 30px 80px rgba(0,0,0,.8)`,'--tg':rgb}}>
            <div aria-hidden="true" className="pointer-events-none absolute -top-32 left-1/2 -translate-x-1/2 w-[640px] h-[300px] rounded-full blur-3xl opacity-20" style={{background:`radial-gradient(circle, ${hex} 0%, transparent 65%)`}}></div>
            <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-px" style={{background:`linear-gradient(90deg, transparent, ${hex}cc, transparent)`}}></div>
            {/* Header — the dashboard's banner, gold half / green half */}
            <div className="relative shrink-0 px-4 sm:px-6 pt-4 sm:pt-5 pb-3 overflow-hidden">
              <div aria-hidden="true" className={`vw-sky${tk==='UFO'?' ufo':''}`}></div>
              <div aria-hidden="true" className="vw-veil"></div>
              <button type="button" onClick={onClose} aria-label="Close" className="tap-h absolute right-4 top-4 sm:right-6 sm:top-6 z-10 w-9 h-9 rounded-full border border-white/25 bg-black/50 text-white/80 hover:text-white hover:border-white/60 flex items-center justify-center text-lg leading-none">{'✕'}</button>
              <div className="relative flex flex-col items-center text-center" style={{textShadow:'0 2px 10px rgba(0,0,0,.95), 0 0 24px rgba(0,0,0,.8)'}}>
                <div className={`vw-coins${tk==='UFO'?' g':''}`}><LgCoin token={tk}/></div>
                <h2 className="font-orbitron text-2xl sm:text-4xl font-bold tracking-wide leading-tight whitespace-nowrap mt-2"><span style={{color:hex}}>{tk}</span><span className="text-white ml-3">Volume</span></h2>
                <div className="text-white/85 text-[13px] sm:text-base mt-1 font-medium">Trading volume across every {tk} pool on PulseChain</div>
              </div>
              <div className="relative mt-5 sm:mt-7 flex flex-wrap items-center gap-2 sm:gap-3">
                <NhPills items={VW_PERIODS} value={win} onChange={setWin} label="Chart window" rgb={rgb}/>
                <div className="ml-auto text-[11px] text-white/60 tabular-nums" style={{textShadow:'0 1px 6px rgba(0,0,0,.9)'}}>
                  {file===undefined?'Loading the hourly file…':file?<span className={amber?'text-amber-300/90':''}>chart as of {fmtSnapshotAge(ageMs)}{amber?' — the hourly update is late':''}</span>:null}
                </div>
              </div>
            </div>
            {/* Body */}
            <div className="relative px-4 sm:px-6 pb-5 sm:pb-6 flex-1 min-h-0">
              <div className="vw-tiles">
                {['24H','7D','30D','90D'].map(p=>(
                  <div key={p} className={`vw-tile${p==='24H'?' live':''}`}>
                    <div className="l"><span className="p">{p}</span><img className="ic" src={VW_ICON[tk]} alt="" aria-hidden="true"/></div>
                    <div className="v">{vol[p]==null?'—':fmtUSD(vol[p])}</div>
                    <div className="s">{p==='24H'?<>{pctEl(v24,avg('7D'))} vs 7D avg</>:(avg(p)==null?<span className="text-white/40">{'—'}</span>:<><b>{fmtUSD(avg(p))}</b> / day</>)}</div>
                  </div>))}
              </div>
              <div className="vw-card">
                <div className="vw-hdr"><span className="t">Today vs averages</span><span className="c">24H volume against each window's daily average</span></div>
                {['7D','30D','90D'].map(p=>{const a=avg(p),r=(v24!=null&&a>0)?v24/a:null,w=r==null?0:Math.min(r,2)/2*100;return(
                  <div key={p} className="vw-cmp">
                    <div className="n">vs {p} average<small>{a==null?'—':`${fmtUSD(a)} / day`}</small></div>
                    <div className="tr" role="img" aria-label={r==null?'unavailable':`${Math.round(r*100)}% of the ${p} average`}><i style={{width:`${w}%`}}></i><b aria-hidden="true"></b></div>
                    <div className="pc">{pctEl(v24,a)}</div>
                  </div>);})}
              </div>
              <div className={`vw-card vw-chartcard${tk==='UFO'?' ufo':''}`}>
                <div className="vw-hdr"><span className="t">Daily volume {'·'} past {P.d} days</span><span className="c">{chartAvg!=null?`avg ${fmtUSD(chartAvg)} / day · on-chain`:''}</span></div>
                {file===null?(
                  <div className="text-center py-8">
                    <div className="text-white/80 font-semibold">Couldn't load the hourly file</div>
                    <div className="text-white/45 text-sm mt-1">It didn't answer, or it is more than {VS_MAX_AGE/3600000} hours old.</div>
                    <button type="button" onClick={()=>load(true)} className="tap-h mt-4 px-4 rounded-full border text-xs font-bold uppercase tracking-[0.14em]" style={{borderColor:`${hex}88`,color:hex}}>Retry</button>
                  </div>
                ):file===undefined||!days?(
                  <div aria-busy="true" className="vw-wait"></div>
                ):(
                  <>
                    <VwChart days={days} rgb={rgb} label={`${tk} volume per day, past ${P.d} days`}/>
                    <div className="vw-key"><span><i></i>Volume per day</span><span><i className="today"></i>Today so far</span><span><i className="avg"></i>Window average</span></div>
                  </>
                )}
              </div>
              {file&&pools&&pools.length>0&&(
                <div className="vw-card">
                  <div className="vw-hdr"><span className="t">By pool</span><span className="c">past {P.d} days {'·'} {pools.length} pool{pools.length===1?'':'s'}</span></div>
                  <table className="vw-tbl"><thead><tr><th className="vw-th">Pool</th><th className="vw-th vw-nophone">Trades</th><th className="vw-th">Volume</th><th className="vw-th">Share</th></tr></thead>
                    <tbody>{shown.map((p,i)=>(
                      <tr key={p.name+i}><td className="vw-td"><span className="vw-rk">{i+1}</span>{p.name}</td><td className="vw-td vw-nophone">{fmt(p.n)}</td><td className="vw-td">{fmtUSD(p.usd)}</td><td className="vw-td">{poolTot>0?(p.usd/poolTot*100).toFixed(1)+'%':'—'}<span className="vw-mini" aria-hidden="true"><i style={{width:`${p.usd/pools[0].usd*100}%`}}></i></span></td></tr>))}
                    </tbody></table>
                  {pools.length>6&&<button type="button" className="vw-more" onClick={()=>setAllPools(a=>!a)} aria-expanded={allPools}>{allPools?<>show the top 6</>:<>and <b>{pools.length-6} more pool{pools.length-6===1?'':'s'}</b> {'—'} show all</>}</button>}
                </div>
              )}
              <div className="vw-conf">The four figures are DexScreener's, summed over every pair {'—'} the same numbers as the Volume tile. The daily chart and the pool table are on-chain swap volume from the hourly file (the Humans vs Bots data), so they will not match DexScreener to the dollar.</div>
            </div>
          </div>
        </Modal>
      );
    };
"""
anchor_jsx = "    const VolumeSplitModal=({token:initial,feeRates,pairs,otherPairs,onClose})=>{"
i = src.index(anchor_jsx)
src = src[:i] + JSX + src[i:]

# ---------- 3. the Dashboard's old inline modal → the component ----------
start_marker = "          {/* Volume Details Modal */}\n          {showVolumeModal&&(\n"
i = src.index(start_marker)
end_marker = "            </Modal>\n          )}\n"
j = src.index(end_marker, i) + len(end_marker)
old = src[i:j]
assert 'Volume Analytics' in old and 'Today vs Averages' in old, 'the old Volume modal block was not where expected'
NEW = "          {/* Volume window (2026-10-07) — VolumeModal at module scope; the old inline card is in git history */}\n          {showVolumeModal&&<VolumeModal token={token} data={data} volumeByPeriod={volumeByPeriod} onClose={()=>setShowVolumeModal(false)}/>}\n"
src = src[:i] + NEW + src[j:]

open(path, 'w', encoding='utf-8').write(src)
print('applied', path, 'md5', hashlib.md5(src.encode('utf-8')).hexdigest(), 'removed', old.count('\n'), 'lines of the old modal')
