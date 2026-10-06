#!/usr/bin/env python3
"""The Volume Split window (2026-10-06, Shaka: "both ptgc and ufo heavily rely on the volume that it gets from the arb bots… a
nice window… volume broken down between Human Volume and ARB Bot volume… hide it down with a very small faint dot in the bottom
right"). Data = data/swap-volume.json (scripts/build-swap-volume.mjs, hourly). Hidden: VOL_SPLIT_LIVE=false → the faint dot
(`VsDot`, the Holders Details pattern) opens `VolumeSplitModal`; going live = that constant true (the dot goes; the Volume
tile's icon entrance is the next step, like Holders'). Everything the window shows: design/volume-split/README.md.
Run once: python3 tools/volume-split.py"""
import sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
p=root/'index.html'; s=p.read_text()
if 'VOL_SPLIT_LIVE' in s: sys.exit('already applied')
def rep(old,new):
    global s
    assert s.count(old)==1,(old[:70],s.count(old)); s=s.replace(old,new)

CSS = r'''    /* ---- Volume Split window (2026-10-06): vs-* — human vs arb-bot volume. --tg = the token accent, --bot = the bot accent ---- */
    .vs-stat{position:relative;overflow:hidden;border-radius:18px;border:1px solid rgba(255,255,255,.1);background:linear-gradient(180deg,rgba(255,255,255,.05),rgba(255,255,255,.015));padding:14px 16px 12px;min-height:96px;box-shadow:inset 0 1px 0 rgba(255,255,255,.07)}
    .vs-stat::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:rgb(var(--acc));opacity:.9;box-shadow:0 0 18px rgba(var(--acc),.7)}
    .vs-stat .l{font-size:11px;letter-spacing:.22em;text-transform:uppercase;font-weight:700;color:rgba(255,255,255,.55)}
    .vs-stat .v{font-family:'Orbitron',monospace;font-weight:700;font-size:26px;line-height:1.1;margin-top:6px;color:#fff;letter-spacing:-.01em}
    .vs-stat .s{font-size:12px;color:rgba(255,255,255,.55);margin-top:5px}
    .vs-stat .s b{color:rgb(var(--acc));font-weight:700}
    .vs-bar{height:14px;border-radius:999px;overflow:hidden;display:flex;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08)}
    .vs-bar>i{display:block;height:100%}
    .vs-bar>i.h{background:linear-gradient(180deg,rgba(var(--tg),1),rgba(var(--tg),.7))}
    .vs-bar>i.b{background:linear-gradient(180deg,rgba(var(--bot),1),rgba(var(--bot),.7))}
    .vs-key{display:inline-flex;align-items:center;gap:6px;font-size:12px;color:rgba(255,255,255,.7)}
    .vs-key i{width:10px;height:10px;border-radius:3px;display:inline-block}
    .vs-chart{display:block;width:100%;height:170px}
    .vs-chart text{font-family:'JetBrains Mono',monospace;font-size:10px;fill:rgba(255,255,255,.45)}
    .vs-th{font-size:11px;letter-spacing:.18em;text-transform:uppercase;font-weight:700;color:rgba(255,255,255,.5);padding:9px 8px;text-align:right;white-space:nowrap}
    .vs-th:first-child{text-align:left}
    .vs-td{padding:9px 8px;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;font-size:14px;color:rgba(255,255,255,.9)}
    .vs-td:first-child{text-align:left}
    .vs-mini{display:inline-flex;height:6px;width:72px;border-radius:999px;overflow:hidden;background:rgba(255,255,255,.08);vertical-align:middle;margin-left:8px}
    .vs-mini i{display:block;height:100%}
    .vs-note{font-size:12px;color:rgba(255,255,255,.55);line-height:1.5}
    @media(max-width:640px){.vs-stat{min-height:84px;padding:12px 14px 10px}.vs-stat .v{font-size:22px}.vs-chart{height:140px}.vs-td,.vs-th{padding:8px 6px}.vs-mini{width:46px}}
'''
rep("    .nh-sky{position:absolute;inset:0;background:url(logos/holders/nh-sky.jpg)", CSS+"    .nh-sky{position:absolute;inset:0;background:url(logos/holders/nh-sky.jpg)")

JS = r'''    /* ================= Volume Split (2026-10-06) — human vs arb-bot trading volume =================
       Shaka: "both ptgc and ufo heavily rely on the volume that it gets from the arb bots… a nice window that pops up… volume
       broken down between Human Volume and ARB Bot volume". Data: data/swap-volume.json (scripts/build-swap-volume.mjs, hourly):
       every pool's Swap events, classed by the contract that called the pool — a known router / aggregator is a person, any other
       contract is an arb bot — priced at the hourly close. Hidden behind the faint bottom-right dot until VOL_SPLIT_LIVE; then the
       entrance moves to the Volume tile (the Holders Details pattern). States per gotcha 3 / a18: undefined = loading, null = failed. */
    const VOL_SPLIT_LIVE=false;
    const SWAP_VOL_URL='https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/swap-volume.json';
    const VS_MAX_AGE=36*3600*1000,VS_TTL=5*60*1000,VS_AMBER_MS=3*3600*1000;
    const VS_BOT='79,209,255';   // the bots' colour (electric cyan) — never a token colour, so a bar reads at a glance
    const VS_PERIODS=[{k:'24H',p:'24h',h:24,label:'Past 24 hours'},{k:'7D',p:'7d',h:168,label:'Past 7 days'},{k:'30D',p:'30d',h:720,label:'Past 30 days'}];
    let _vsFile,_vsAt=0,_vsP=null;
    const fetchSwapVolume=(force=false)=>{
      if(!force&&_vsAt&&Date.now()-_vsAt<VS_TTL)return Promise.resolve(_vsFile);
      if(_vsP)return _vsP;
      _vsP=fetch(SWAP_VOL_URL+'?t='+Date.now()).then(r=>r.ok?r.json():null).then(j=>{
        _vsP=null;_vsAt=Date.now();
        _vsFile=(j&&j.schema===1&&j.tokens&&j.tokens.PTGC&&j.tokens.UFO&&Date.now()-Date.parse(j.generatedAt)<VS_MAX_AGE)?j:null;
        return _vsFile;
      }).catch(()=>{_vsP=null;_vsAt=Date.now();_vsFile=null;return null;});
      return _vsP;
    };
    const VsDot=({token,onOpen})=>(
      <button type="button" onClick={onOpen} aria-label="Volume split (preview)" title="" className="fixed bottom-1 right-1 z-30 w-7 h-7 flex items-center justify-center bg-transparent border-0 p-0">
        <span aria-hidden="true" className="block w-1.5 h-1.5 rounded-full" style={{background:(TOKENS[token]||TOKENS.PTGC).colorHex,opacity:0.16}}></span>
      </button>
    );
    /* Pure: one view of the file for a token (or BOTH) and a period. Sums are over the file's precomputed periods; the series
       is binned from the hourly rows (24H: hours, 7D: six-hour bins, 30D: days). */
    const vsView=(file,token,P)=>{
      const toks=token==='BOTH'?['PTGC','UFO']:[token];
      const zero=()=>({n:0,usd:0});
      const v={human:zero(),bot:zero(),pools:{},senders:{},routers:file.routers||{}};
      for(const tk of toks){
        const per=file.tokens[tk]&&file.tokens[tk].periods&&file.tokens[tk].periods[P.p];if(!per)continue;
        for(const k of['human','bot']){v[k].n+=per[k].n;v[k].usd+=per[k].usd;}
        for(const[a,pl]of Object.entries(per.pools||{})){const o=v.pools[a]||(v.pools[a]={name:pl.name,token:tk,human:zero(),bot:zero()});for(const k of['human','bot']){o[k].n+=pl[k].n;o[k].usd+=pl[k].usd;}if(o.token!==tk)o.token='BOTH';}
        for(const sd of per.senders||[]){const o=v.senders[sd.addr]||(v.senders[sd.addr]={addr:sd.addr,kind:sd.kind,label:sd.label,n:0,usd:0});o.n+=sd.n;o.usd+=sd.usd;}
      }
      v.total={n:v.human.n+v.bot.n,usd:v.human.usd+v.bot.usd};
      v.botShare=v.total.usd>0?v.bot.usd/v.total.usd:null;
      v.pools=Object.values(v.pools).map(o=>({...o,total:o.human.usd+o.bot.usd})).sort((a,b)=>b.total-a.total);
      v.bots=Object.values(v.senders).filter(s=>s.kind==='bot').sort((a,b)=>b.usd-a.usd||b.n-a.n).slice(0,8);
      v.humans=Object.values(v.senders).filter(s=>s.kind==='human').sort((a,b)=>b.usd-a.usd);
      // series
      const now=Date.now(),since=now-P.h*3600000,binMs=P.h<=24?3600000:P.h<=168?6*3600000:86400000,bins=Math.ceil(P.h*3600000/binMs);
      const start=Math.floor(since/binMs)*binMs;
      v.series=Array.from({length:bins},(_,i)=>({t:start+i*binMs,h:0,b:0}));
      for(const tk of toks)for(const r of(file.tokens[tk]&&file.tokens[tk].hours)||[]){if(r[0]<start)continue;const i=Math.min(bins-1,Math.floor((r[0]-start)/binMs));v.series[i].h+=r[2];v.series[i].b+=r[4];}
      v.binMs=binMs;
      return v;
    };
    const vsPct=x=>x==null?'—':(x*100).toFixed(x*100>=10?0:1)+'%';
    const vsShort=a=>a.slice(0,6)+'…'+a.slice(-4);
    const VsStat=({label,value,sub,acc})=>(
      <div className="vs-stat" style={{'--acc':acc}}>
        <div className="l">{label}</div>
        <div className="v tabular-nums">{value}</div>
        {sub&&<div className="s">{sub}</div>}
      </div>
    );
    /* Stacked bars: bots at the foot (the floor the humans stand on), humans on top; one label per few bins. */
    const VsChart=({series,binMs,rgb})=>{
      const W=720,H=170,padL=8,padR=8,padT=10,padB=22;
      const max=Math.max(1,...series.map(s=>s.h+s.b));
      const n=series.length,bw=(W-padL-padR)/n,gap=Math.min(4,bw*0.25);
      const y=v=>padT+(H-padT-padB)*(1-v/max);
      const fmtT=t=>{const d=new Date(t);return binMs<86400000&&binMs<6*3600000?d.toLocaleTimeString([],{hour:'numeric'}):d.toLocaleDateString('en-US',{month:'short',day:'numeric'});};
      const every=n<=24?4:n<=28?4:5;
      return(
        <svg className="vs-chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" role="img" aria-label="Volume over time, humans over bots">
          {[0.25,0.5,0.75].map(f=><line key={f} x1={padL} x2={W-padR} y1={y(max*f)} y2={y(max*f)} stroke="rgba(255,255,255,.07)"/>)}
          {series.map((s,i)=>{const x=padL+i*bw+gap/2,w=Math.max(1,bw-gap);const yb=y(s.b),yh=y(s.b+s.h);return(
            <g key={s.t}>
              <title>{`${fmtT(s.t)} — humans ${fmtUSD(s.h)} · bots ${fmtUSD(s.b)}`}</title>
              <rect x={x} y={yb} width={w} height={Math.max(0,y(0)-yb)} fill={`rgba(${VS_BOT},.85)`}/>
              <rect x={x} y={yh} width={w} height={Math.max(0,yb-yh)} fill={`rgba(${rgb},.9)`}/>
            </g>);})}
          {series.map((s,i)=>i%every===0?<text key={'t'+s.t} x={padL+i*bw+bw/2} y={H-6} textAnchor="middle">{fmtT(s.t)}</text>:null)}
          <text x={W-padR} y={padT+8} textAnchor="end">{fmtUSD(max)}</text>
        </svg>
      );
    };
    const VolumeSplitModal=({token:initial,feeRates,onClose})=>{
      const[token,setToken]=useState(initial==='UFO'?'UFO':'PTGC');
      const[win,setWin]=useState('7D');
      const[file,setFile]=useState(undefined);
      const[showHow,setShowHow]=useState(false);
      const[showHumans,setShowHumans]=useState(false);
      const load=(force)=>{setFile(undefined);fetchSwapVolume(force).then(setFile);};
      useEffect(()=>{let live=true;fetchSwapVolume().then(j=>{if(live)setFile(j);});return()=>{live=false;};},[]);
      const P=VS_PERIODS.find(w=>w.k===win)||VS_PERIODS[1];
      const T=NH_THEME[token==='BOTH'?'PTGC':token],hex=token==='BOTH'?'#F5F0D8':T.hex,rgb=token==='BOTH'?'232,192,68':T.rgb;
      const view=React.useMemo(()=>file?vsView(file,token,P):null,[file,token,win]);
      const ageMs=file?Date.now()-Date.parse(file.generatedAt):null;
      const amber=ageMs!=null&&ageMs>VS_AMBER_MS;
      const phone=typeof window!=='undefined'&&window.innerWidth<640;
      const fee=token==='BOTH'?null:(feeRates&&feeRates[token])||0;
      const vg=view&&fee>0?{h:view.human.usd*fee,b:view.bot.usd*fee}:view&&token==='BOTH'&&feeRates?{h:(file.tokens.PTGC.periods[P.p].human.usd*(feeRates.PTGC||0))+(file.tokens.UFO.periods[P.p].human.usd*(feeRates.UFO||0)),b:(file.tokens.PTGC.periods[P.p].bot.usd*(feeRates.PTGC||0))+(file.tokens.UFO.periods[P.p].bot.usd*(feeRates.UFO||0))}:null;
      const logo=token==='BOTH'?null:TOKENS[token].logo;
      return(
        <Modal onClose={onClose} label={`${token} volume split`} className="z-50 flex items-center justify-center p-0 sm:p-4 modal-overlay bg-black/85">
          <div onClick={e=>e.stopPropagation()} className="relative w-full h-[100dvh] sm:h-auto sm:max-h-[calc(100dvh-2rem)] sm:max-w-4xl flex flex-col rounded-none sm:rounded-3xl border bg-[#070707] overflow-y-auto overflow-x-hidden overscroll-contain" style={{borderColor:`${hex}55`,boxShadow:`0 0 80px -20px ${hex}66, 0 30px 80px -20px rgba(0,0,0,.9)`}}>
            <div aria-hidden="true" className="pointer-events-none absolute -top-32 left-1/2 -translate-x-1/2 w-[640px] h-[300px] rounded-full blur-3xl opacity-20" style={{background:`radial-gradient(circle, ${hex} 0%, transparent 65%)`}}></div>
            <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-px" style={{background:`linear-gradient(90deg, transparent, ${hex}cc, transparent)`}}></div>
            {/* Header — the Holders window's plate for now (his art for this window is owed) */}
            <div className="relative shrink-0 px-4 sm:px-6 pt-4 sm:pt-6 pb-3 overflow-hidden" style={{minHeight:phone?150:190}}>
              <div aria-hidden="true" className={`nh-sky${token==='UFO'?' ufo':''}`}></div>
              <div aria-hidden="true" className="nh-sky-fade"></div>
              <div className="relative flex items-start gap-3 sm:gap-4">
                <div className="relative shrink-0 flex items-center">
                  {token==='BOTH'?(<><img src={TOKENS.PTGC.logo} alt="" className="relative w-12 h-12 sm:w-20 sm:h-20 -mr-3" style={{filter:'drop-shadow(0 4px 12px rgba(0,0,0,.9))'}}/><img src={TOKENS.UFO.logo} alt="" className="relative w-12 h-12 sm:w-20 sm:h-20" style={{filter:'drop-shadow(0 4px 12px rgba(0,0,0,.9))'}}/></>)
                  :(<><div aria-hidden="true" className="absolute inset-0 rounded-full blur-xl opacity-50 scale-110" style={{background:`radial-gradient(circle, ${hex} 0%, transparent 60%)`}}></div><img src={logo} alt="" className="relative w-16 h-16 sm:w-24 sm:h-24" style={{filter:'drop-shadow(0 4px 12px rgba(0,0,0,.9))'}}/></>)}
                </div>
                <div className="flex-1 min-w-0" style={{textShadow:'0 2px 10px rgba(0,0,0,.95), 0 0 24px rgba(0,0,0,.8)'}}>
                  <h2 className="font-orbitron text-2xl sm:text-4xl font-bold tracking-wide leading-tight" style={{color:hex}}>Volume Split</h2>
                  <div className="text-white/85 text-[12px] sm:text-sm mt-1">{P.label} {'·'} {token==='BOTH'?'PTGC + UFO':token} trading volume {'—'} people vs arbitrage bots</div>
                </div>
                <button type="button" onClick={onClose} aria-label="Close" className="tap-h shrink-0 w-9 h-9 rounded-full border border-white/25 bg-black/50 text-white/80 hover:text-white hover:border-white/60 flex items-center justify-center text-lg leading-none">{'✕'}</button>
              </div>
              <div className="relative mt-5 sm:mt-7 flex flex-wrap items-center gap-2 sm:gap-3">
                <NhPills items={[{k:'PTGC'},{k:'UFO'},{k:'BOTH'}]} value={token} onChange={setToken} label="Token" rgb={rgb}/>
                <NhPills items={VS_PERIODS} value={win} onChange={setWin} label="Period" rgb={rgb}/>
                <div className="ml-auto text-[11px] text-white/60 tabular-nums" style={{textShadow:'0 1px 6px rgba(0,0,0,.9)'}}>
                  {file===undefined?'Loading…':file?<span className={amber?'text-amber-300/90':''}>as of {fmtSnapshotAge(ageMs)}{amber?' — the hourly update is late':''}</span>:null}
                </div>
              </div>
            </div>
            {/* Body */}
            <div className="relative px-4 sm:px-6 pb-5 sm:pb-6 flex-1 min-h-0">
              {file===null?(
                <div className="rounded-2xl border border-white/10 bg-black/40 p-6 text-center">
                  <div className="text-white/80 font-semibold">Couldn't load the volume file</div>
                  <div className="text-white/45 text-sm mt-1">The hourly file didn't answer, or it is more than {VS_MAX_AGE/3600000} hours old.</div>
                  <button type="button" onClick={()=>load(true)} className="tap-h mt-4 px-4 rounded-full border text-xs font-bold uppercase tracking-[0.14em]" style={{borderColor:`${hex}88`,color:hex}}>Retry</button>
                </div>
              ):file===undefined?(
                <div aria-busy="true" className="space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">{[0,1,2].map(i=><div key={i} className="h-[96px] rounded-2xl bg-white/[0.05] animate-pulse"></div>)}</div>
                  <div className="h-[170px] rounded-2xl bg-white/[0.04] animate-pulse"></div>
                </div>
              ):(
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 sm:gap-3">
                    <VsStat label="Total volume" value={fmtUSD(view.total.usd)} sub={<>{fmt(view.total.n)} trades</>} acc="255,255,255"/>
                    <VsStat label="Human volume" value={fmtUSD(view.human.usd)} sub={<><b>{vsPct(view.total.usd>0?view.human.usd/view.total.usd:null)}</b> {'·'} {fmt(view.human.n)} trades through routers</>} acc={rgb}/>
                    <VsStat label="ARB bot volume" value={fmtUSD(view.bot.usd)} sub={<><b>{vsPct(view.botShare)}</b> {'·'} {fmt(view.bot.n)} trades from {fmt(Object.values(view.senders).filter(s=>s.kind==='bot').length)} bot contract{Object.values(view.senders).filter(s=>s.kind==='bot').length===1?'':'s'}</>} acc={VS_BOT}/>
                  </div>
                  <div className="mt-3 rounded-2xl border border-white/10 bg-black/40 p-3 sm:p-4" style={{'--tg':rgb,'--bot':VS_BOT}}>
                    <div className="flex items-center justify-between gap-3 flex-wrap">
                      <span className="vs-key"><i style={{background:`rgb(${rgb})`}}></i>Humans {vsPct(view.total.usd>0?view.human.usd/view.total.usd:null)}</span>
                      <span className="vs-key"><i style={{background:`rgb(${VS_BOT})`}}></i>Arb bots {vsPct(view.botShare)}</span>
                    </div>
                    <div className="vs-bar mt-2" role="img" aria-label={`Humans ${vsPct(view.total.usd>0?view.human.usd/view.total.usd:null)}, bots ${vsPct(view.botShare)}`}>
                      <i className="h" style={{width:`${view.total.usd>0?view.human.usd/view.total.usd*100:0}%`}}></i><i className="b" style={{width:`${view.total.usd>0?view.bot.usd/view.total.usd*100:0}%`}}></i>
                    </div>
                    <div className="mt-3"><VsChart series={view.series} binMs={view.binMs} rgb={rgb}/></div>
                    {vg&&<div className="mt-2 vs-note">Value generated at {token==='BOTH'?'each token’s':''} {fee>0?`${+(fee*100).toFixed(2)}% `:''}fee: <b className="text-white">{fmtUSD(vg.h)}</b> from people {'·'} <b className="text-white">{fmtUSD(vg.b)}</b> from bots</div>}
                  </div>
                  {/* Pools */}
                  <div className="mt-4 text-[12px] sm:text-[13px] font-semibold uppercase tracking-[0.22em]" style={{color:hex}}>By pool</div>
                  <div className="mt-2 rounded-2xl border border-white/10 bg-black/40 overflow-hidden">
                    <table className="w-full">
                      <thead><tr><th className="vs-th">Pool</th><th className="vs-th">Volume</th>{!phone&&<th className="vs-th">Humans</th>}{!phone&&<th className="vs-th">Bots</th>}<th className="vs-th">Bot share</th></tr></thead>
                      <tbody>{view.pools.filter(pl=>pl.total>0||pl.human.n+pl.bot.n>0).slice(0,phone?10:20).map(pl=>{const bs=pl.total>0?pl.bot.usd/pl.total:null;return(
                        <tr key={pl.name+pl.token} className="border-t border-white/[0.06]">
                          <td className="vs-td font-semibold">{pl.name}{token==='BOTH'&&<span className="text-white/40 font-normal text-[12px]"> {pl.token}</span>}</td>
                          <td className="vs-td">{fmtUSD(pl.total)}</td>
                          {!phone&&<td className="vs-td">{fmtUSD(pl.human.usd)} <span className="text-white/40 text-[12px]">{fmt(pl.human.n)}</span></td>}
                          {!phone&&<td className="vs-td">{fmtUSD(pl.bot.usd)} <span className="text-white/40 text-[12px]">{fmt(pl.bot.n)}</span></td>}
                          <td className="vs-td">{vsPct(bs)}<span className="vs-mini"><i style={{width:`${bs!=null?bs*100:0}%`,background:`rgb(${VS_BOT})`}}></i></span></td>
                        </tr>);})}</tbody>
                    </table>
                  </div>
                  {/* Bots */}
                  <div className="mt-4 text-[12px] sm:text-[13px] font-semibold uppercase tracking-[0.22em]" style={{color:`rgb(${VS_BOT})`}}>Top bot contracts</div>
                  {view.bots.length===0?<div className="mt-2 rounded-2xl border border-white/10 bg-black/40 p-5 text-center text-white/55 text-sm">No bot trades in the {P.label.toLowerCase()}.</div>:(
                    <div className="mt-2 rounded-2xl border border-white/10 bg-black/40 overflow-hidden">
                      <table className="w-full">
                        <thead><tr><th className="vs-th">Contract</th><th className="vs-th">Trades</th><th className="vs-th">Volume</th>{!phone&&<th className="vs-th">Of bot volume</th>}</tr></thead>
                        <tbody>{view.bots.map(b=>(
                          <tr key={b.addr} className="border-t border-white/[0.06]">
                            <td className="vs-td"><a href={`https://scan.pulsechain.com/address/${b.addr}`} target="_blank" rel="noopener noreferrer" className="font-mono text-white/90 hover:text-white hover:underline" title={b.addr}>{vsShort(b.addr)}</a>{b.label&&<span className="text-white/40 text-[12px]"> {b.label}</span>}</td>
                            <td className="vs-td">{fmt(b.n)}</td>
                            <td className="vs-td">{fmtUSD(b.usd)}</td>
                            {!phone&&<td className="vs-td">{vsPct(view.bot.usd>0?b.usd/view.bot.usd:null)}</td>}
                          </tr>))}</tbody>
                      </table>
                    </div>)}
                  {/* Humans' routes + method */}
                  <div className="mt-3 flex flex-wrap gap-2">
                    <button type="button" onClick={()=>setShowHumans(s=>!s)} aria-expanded={showHumans} className="tap-h rounded-xl border border-white/10 bg-black/30 px-3 text-left text-[12px] font-semibold uppercase tracking-[0.18em] text-white/55">Human routes {'·'} {view.humans.length} {showHumans?'▲':'▼'}</button>
                    <button type="button" onClick={()=>setShowHow(s=>!s)} aria-expanded={showHow} className="tap-h rounded-xl border border-white/10 bg-black/30 px-3 text-left text-[12px] font-semibold uppercase tracking-[0.18em] text-white/55">How we tell {showHow?'▲':'▼'}</button>
                  </div>
                  {showHumans&&<div className="mt-2 rounded-2xl border border-white/10 bg-black/30 p-3 vs-note">{view.humans.length?view.humans.map(h=><div key={h.addr} className="flex justify-between gap-3 py-0.5"><span><span className="text-white/85">{h.label||'router'}</span> <a href={`https://scan.pulsechain.com/address/${h.addr}`} target="_blank" rel="noopener noreferrer" className="font-mono text-white/45 hover:text-white/80">{vsShort(h.addr)}</a></span><span className="tabular-nums">{fmt(h.n)} trades {'·'} {fmtUSD(h.usd)}</span></div>):'No router trades in this window.'}</div>}
                  {showHow&&<div className="mt-2 rounded-2xl border border-white/10 bg-black/30 p-3 vs-note">Every trade on a PulseX pool is a Swap event that names the contract which called the pool. A person's wallet can only reach a pool through a router or aggregator (PulseX, Piteas, …), so trades sent by those are counted as human — a multi-hop swap included. Arbitrage bots call the pools from their own contracts, so every other sender is counted as a bot; a sender PulseScan names as a verified router or aggregator is moved to the human side automatically. Each trade is valued at the token's price for that hour, on the pools this dashboard tracks — so the totals will not match DexScreener's to the dollar. Updated hourly; the list covers 30 days.</div>}
                </>
              )}
            </div>
          </div>
        </Modal>
      );
    };
'''
rep("    const NhDot=({token,onOpen})=>(", JS+"    const NhDot=({token,onOpen})=>(")

# dashboard wiring: state + render (next to Holders Details)
rep("""      const[showNewHolders,setShowNewHolders]=useState(false);   // Holders Details (2026-10-02): the faint dot while hidden, the button beside the ⓘ once NEW_HOLDERS_LIVE""",
"""      const[showNewHolders,setShowNewHolders]=useState(false);   // Holders Details (2026-10-02): the faint dot while hidden, the button beside the ⓘ once NEW_HOLDERS_LIVE
      const[showVolSplit,setShowVolSplit]=useState(false);       // Volume Split (2026-10-06): human vs arb-bot volume — the faint dot while hidden (VOL_SPLIT_LIVE)""")
rep("""          {!NEW_HOLDERS_LIVE&&activeTab==='dashboard'&&<NhDot token={token} onOpen={()=>setShowNewHolders(true)}/>}""",
"""          {!NEW_HOLDERS_LIVE&&activeTab==='dashboard'&&<NhDot token={token} onOpen={()=>setShowNewHolders(true)}/>}
          {/* Volume Split (2026-10-06): people vs arb bots. Hidden behind the faint bottom-right dot until VOL_SPLIT_LIVE. */}
          {showVolSplit&&<VolumeSplitModal token={token} feeRates={{PTGC:TOKENS.PTGC.feeRate||0.05,UFO:TOKENS.UFO.feeRate||0.06,[token]:cfg.feeRate||TOKENS[token].feeRate||(token==='UFO'?0.06:0.05)}} onClose={()=>setShowVolSplit(false)}/>}
          {!VOL_SPLIT_LIVE&&activeTab==='dashboard'&&<VsDot token={token} onOpen={()=>setShowVolSplit(true)}/>}""")
p.write_text(s); print('edited index.html')
