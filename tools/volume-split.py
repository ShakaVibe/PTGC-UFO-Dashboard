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

CSS = r'''    /* ---- Humans vs Bots window (2026-10-06): vs-* — human vs arb-bot volume. --acc = a side's accent (rgb), --accbg = its gradient ---- */
    .vs-sky{position:absolute;inset:0;background:url(logos/hvb/banner.jpg) center 38%/cover no-repeat}   /* round 6: his humans-vs-bots panorama (logos/hvb/banner.jpg) */
    .vs-sky-veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.64) 0%,rgba(0,0,0,.64) 60%,rgba(7,7,7,.86) 88%,#070707 100%)}   /* round 7: ~64 % ("dim it a little more" than the 50 %) + the fade into the body */
    .vs-strip{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 22px;padding:10px 16px;border-radius:14px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03)}
    .vs-strip .k{font-size:12px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.5)}
    .vs-strip .v{font-family:'Rajdhani',sans-serif;font-weight:700;font-size:22px;color:#fff;margin-left:8px}
    /* round 6: Shaka's art — his gold / blue network frames as the card (logos/hvb/card-*.jpg, border + accent line gone) and his figures
       (the lit silhouette, the robot) standing at the right behind the type, faded to the left so the figures never fight the numbers */
    .vs-card{position:relative;overflow:hidden;border-radius:20px;background:#05070c;padding:16px 18px 14px;min-height:238px;box-shadow:0 12px 30px -16px rgba(0,0,0,.9)}
    .vs-card .bg,.vs-card .bg2{position:absolute;inset:0;background:center/cover no-repeat;pointer-events:none}
    .vs-card.hu .bg,.vs-card.hu .bg2{background-image:url(logos/hvb/card-gold.jpg)}
    .vs-card.bo .bg{background-image:url(logos/hvb/card-blue.jpg)}
    .vs-card.ufo .bg,.vs-card.ufo .fig{filter:hue-rotate(62deg) saturate(1.05)}   /* round 7: UFO's human card is GREEN — the gold frame and silhouette hue-shifted */
    .vs-card.both .bg2{filter:hue-rotate(62deg) saturate(1.05);-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 30%,#000 70%);mask-image:linear-gradient(90deg,rgba(0,0,0,0) 30%,#000 70%)}   /* BOTH: gold at the left fading to green at the right */
    .vs-card.both .fig{filter:hue-rotate(30deg)}
    .vs-card::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(4,6,10,.72) 0%,rgba(4,6,10,.5) 50%,rgba(4,6,10,.22) 100%),linear-gradient(180deg,rgba(4,6,10,.7),rgba(4,6,10,.25) 28%,rgba(4,6,10,0) 45%);pointer-events:none}   /* round 7: darker at the top — the frames' lit corners sat under the label and the percentage */
    .vs-card .hd .n,.vs-card .pct{background:rgba(3,5,9,.62);border-radius:10px;padding:3px 10px;box-shadow:0 0 0 1px rgba(255,255,255,.06)}   /* round 7: the label and the percentage on their own dark pills — "you can't read the percentage" */
    .vs-card .hd{margin:-3px -4px 0}
    .vs-card .fig{position:absolute;right:3%;top:5%;height:90%;width:auto;max-width:56%;object-fit:contain;object-position:right center;opacity:.6;pointer-events:none;z-index:1;-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 40%);mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 40%)}
    .vs-card>*:not(.fig):not(.bg):not(.bg2){position:relative;z-index:2;text-shadow:0 1px 3px rgba(0,0,0,.95),0 0 16px rgba(0,0,0,.8)}
    .vs-card .hd{display:flex;align-items:baseline;justify-content:space-between;gap:10px}
    .vs-card .hd .n{font-size:13px;letter-spacing:.24em;text-transform:uppercase;font-weight:700;color:rgb(var(--acc))}
    .vs-card .hd .n.gg{color:#C9D96A}   /* BOTH: the gold-green midpoint, solid — gradient text vanished on its dark pill (round 7) */
    .vs-card .pct{font-family:'Orbitron',monospace;font-weight:900;font-size:30px;line-height:1;color:rgb(var(--acc))}   /* round 4: no glow (Shaka: "makes it kinda fuzzy") */
    .vs-card .pct.gg{color:#C9D96A}
    .vs-card .k{font-size:12px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.55);margin-top:12px}
    .vs-card .v{font-family:'Rajdhani',sans-serif;font-weight:700;font-size:40px;line-height:1;color:#fff;margin-top:4px}   /* the dashboard tiles' figure (h2.css .h2-tv) */
    .vs-card .s{font-size:14px;color:rgba(255,255,255,.6);margin-top:5px;font-weight:500}
    .vs-card .vg{margin-top:12px;padding-top:10px;border-top:1px solid rgba(255,255,255,.14);display:flex;align-items:baseline;justify-content:space-between;gap:10px;flex-wrap:wrap}
    .vs-card .vg .k{margin-top:0}
    .vs-card .vg .v{font-size:28px;margin-top:0}
    .vs-card .vg .s{margin-top:0}
    .vs-bs{margin-top:10px}
    .vs-bsbar{height:7px;border-radius:999px;overflow:hidden;display:flex;background:rgba(255,255,255,.06)}
    .vs-bsbar i{display:block;height:100%}
    .vs-bsl{display:flex;justify-content:space-between;gap:10px;margin-top:5px;font-size:13px;font-weight:600;color:rgba(255,255,255,.75);flex-wrap:wrap}
    .vs-hod{margin-top:14px}
    .vs-hodr,.vs-hodx{display:grid;grid-template-columns:76px 1fr;align-items:center;gap:10px;margin-top:4px}
    .vs-hodr .k{font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.55)}
    .vs-hodr .cells{display:grid;grid-template-columns:repeat(24,1fr);gap:2px;height:16px}
    .vs-hodr .cells i{display:block;border-radius:3px}
    .vs-hodx .cells{display:grid;grid-template-columns:repeat(24,1fr);gap:2px;font-size:11px;font-weight:600;color:rgba(255,255,255,.4)}
    @media(max-width:640px){.vs-hodr,.vs-hodx{grid-template-columns:58px 1fr}.vs-hodr .k{font-size:10px}}
    .vs-bar{height:16px;border-radius:999px;overflow:hidden;display:flex;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.08)}
    .vs-bar>i{display:block;height:100%}
    .vs-bar>i.h{background:linear-gradient(180deg,rgba(var(--tg),1),rgba(var(--tg),.7))}
    .vs-bar>i.h.gg{background:linear-gradient(90deg,#E8C044,#A8FF4A 70%,#7CFC00)}
    .vs-bar>i.b{background:linear-gradient(180deg,rgba(var(--bot),1),rgba(var(--bot),.7))}
    .vs-key{display:inline-flex;align-items:center;gap:7px;font-size:14px;font-weight:600;color:rgba(255,255,255,.75)}
    .vs-key i{width:11px;height:11px;border-radius:3px;display:inline-block}
    .vs-chart{display:block;width:100%;height:170px}
    .vs-chart text{font-family:'Rajdhani',sans-serif;font-size:12px;font-weight:600;fill:rgba(255,255,255,.5)}
    .vs-fold{width:100%;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:12px 16px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.4);text-align:left;cursor:pointer}
    .vs-fold:hover{border-color:rgba(255,255,255,.22)}
    .vs-fold .t{font-size:13px;letter-spacing:.22em;text-transform:uppercase;font-weight:700}
    .vs-fold .c{font-size:13px;color:rgba(255,255,255,.5);font-weight:600}
    .vs-fold .ch{color:rgba(255,255,255,.45);font-size:12px;transition:transform .2s}
    .vs-fold[aria-expanded="true"] .ch{transform:rotate(180deg)}
    .vs-th{font-size:12px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.55);padding:9px 8px;text-align:right;white-space:nowrap}
    .vs-th:first-child{text-align:left}
    .vs-td{padding:9px 8px;text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap;font-size:16px;font-weight:600;color:rgba(255,255,255,.9)}
    .vs-td:first-child{text-align:left}
    .vs-mini{display:inline-flex;height:6px;width:72px;border-radius:999px;overflow:hidden;background:rgba(255,255,255,.08);vertical-align:middle;margin-left:8px}
    .vs-mini i{display:block;height:100%}
    .vs-note{font-size:14px;color:rgba(255,255,255,.6);line-height:1.5}
    @media(max-width:640px){.vs-card{padding:14px 14px 12px}.vs-card .v{font-size:32px}.vs-card .vg .v{font-size:24px}.vs-card .pct{font-size:26px}.vs-strip .v{font-size:19px}.vs-chart{height:140px}.vs-td,.vs-th{padding:8px 6px}.vs-mini{width:46px}}
    .nh-sky{position:absolute;inset:0;background:url(logos/holders/nh-sky.jpg)", CSS+"    .nh-sky{position:absolute;inset:0;background:url(logos/holders/nh-sky.jpg)")

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
    const VS_PERIODS=[{k:'24H',p:'24h',h:24,label:'Past 24 hours'},{k:'7D',p:'7d',h:168,label:'Past 7 days'},{k:'30D',p:'30d',h:720,label:'Past 30 days'},{k:'90D',p:'90d',h:2160,label:'Past 90 days'}];
    let _vsFile,_vsAt=0,_vsP=null;
    const fetchSwapVolume=(force=false)=>{
      if(!force&&_vsAt&&Date.now()-_vsAt<VS_TTL)return Promise.resolve(_vsFile);
      if(_vsP)return _vsP;
      _vsP=fetch(SWAP_VOL_URL+'?t='+Date.now()).then(r=>r.ok?r.json():null).then(j=>{
        _vsP=null;_vsAt=Date.now();
        _vsFile=(j&&j.schema>=1&&j.tokens&&j.tokens.PTGC&&j.tokens.UFO&&Date.now()-Date.parse(j.generatedAt)<VS_MAX_AGE)?j:null;
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
    const vsView=(file,token,P,pairMap)=>{
      const toks=token==='BOTH'?['PTGC','UFO']:[token];
      const zero=()=>({n:0,usd:0});
      const v={human:zero(),bot:zero(),pools:{},senders:{},routers:file.routers||{},buys:{human:zero(),bot:zero()},sells:{human:zero(),bot:zero()},hod:Array.from({length:24},()=>[0,0]),wallets:{human:0,humanTxs:0,humanTxsKnown:0},hasDir:false,arb:{n:0,usd:0,txs:0}};
      for(const tk of toks){
        const per=file.tokens[tk]&&file.tokens[tk].periods&&file.tokens[tk].periods[P.p];if(!per)continue;
        for(const k of['human','bot']){v[k].n+=per[k].n;v[k].usd+=per[k].usd;
          if(per.buys){v.buys[k].n+=per.buys[k].n;v.buys[k].usd+=per.buys[k].usd;v.sells[k].n+=per.sells[k].n;v.sells[k].usd+=per.sells[k].usd;v.hasDir=true;}}
        if(per.hod)per.hod.forEach((h,i)=>{v.hod[i][0]+=h[0];v.hod[i][1]+=h[1];});
        if(per.wallets){v.wallets.human+=per.wallets.human;v.wallets.humanTxs+=per.wallets.humanTxs;v.wallets.humanTxsKnown+=per.wallets.humanTxsKnown;}
        if(per.arb){v.arb.n+=per.arb.n;v.arb.usd+=per.arb.usd;v.arb.txs+=per.arb.txs;}
        for(const[a,pl]of Object.entries(per.pools||{})){const o=v.pools[a]||(v.pools[a]={addr:a,name:pl.name,token:tk,human:zero(),bot:zero(),partner:vsPartner(file,a,tk,pairMap)});for(const k of['human','bot']){o[k].n+=pl[k].n;o[k].usd+=pl[k].usd;}if(o.token!==tk)o.token='BOTH';}
        for(const sd of per.senders||[]){const o=v.senders[sd.addr]||(v.senders[sd.addr]={addr:sd.addr,kind:sd.kind,label:sd.label,n:0,usd:0,arb:0});o.n+=sd.n;o.usd+=sd.usd;o.arb+=(sd.arb||0);}
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
    /* The OTHER token of a pool (Shaka: "the logos to all the pools — just the other token, not the ptgc or ufo"): its address from
       the file's pools map (token0 / token1), its logo = DexScreener's token image, or our own file for the Grays' pair. */
    const VS_SYMBOL_ADDR={WPLS:ADDR.WPLS,PLSX:ADDR.PLSX,INC:ADDR.INC,HEX:ADDR.HEX,EHEX:ADDR.EHEX,PRVX:ADDR.PRVX,WETH:ADDR.WETH,WBTC:ADDR.WBTC,USDC:ADDR.USDC,DAI:ADDR.DAI};   // last resort: the pool's name
    const vsPartner=(file,addr,tk,pairMap)=>{
      const mine=(TOKENS[tk].address||'').toLowerCase();
      const pm=pairMap&&pairMap[addr];
      const pl=file.pools&&file.pools[addr];
      let other=pm?[pm.base,pm.quote].find(a=>a&&a!==mine):null;
      if(!other&&pl&&pl.token0)other=[pl.token0,pl.token1].map(a=>(a||'').toLowerCase()).find(a=>a&&a!==mine);
      if(!other&&pl&&pl.name){const sym=pl.name.split('/').map(x=>x.trim().toUpperCase()).find(x=>x!=='PTGC'&&x!=='UFO');const a=sym&&VS_SYMBOL_ADDR[sym];if(a)other=a.toLowerCase();}
      if(!other)return null;
      const grays=Object.keys(TOKENS).find(k=>(TOKENS[k].address||'').toLowerCase()===other);
      return{addr:other,logo:grays?TOKENS[grays].logo:getLogo(other)};
    };
    const VsPoolLogo=({p})=>p&&p.logo?<img src={p.logo} alt="" className="w-6 h-6 rounded-full object-contain bg-black/40 ring-1 ring-white/10 shrink-0" onError={e=>{e.currentTarget.style.visibility='hidden';}}/>:<span aria-hidden="true" className="w-6 h-6 rounded-full bg-white/[0.06] shrink-0 inline-block"></span>;
    const vsShort=a=>a.slice(0,6)+'…'+a.slice(-4);
    const VsStat=({label,value,sub,acc})=>(
      <div className="vs-stat" style={{'--acc':acc}}>
        <div className="l">{label}</div>
        <div className="v tabular-nums">{value}</div>
        {sub&&<div className="s">{sub}</div>}
      </div>
    );
    /* Stacked bars: bots at the foot (the floor the humans stand on), humans on top; one label per few bins. */
    const VsChart=({series,binMs,rgb,gg})=>{
      const W=720,H=170,padL=8,padR=8,padT=10,padB=22;
      const max=Math.max(1,...series.map(s=>s.h+s.b));
      const n=series.length,bw=(W-padL-padR)/n,gap=Math.min(4,bw*0.25);
      const y=v=>padT+(H-padT-padB)*(1-v/max);
      const fmtT=t=>{const d=new Date(t);return binMs<86400000&&binMs<6*3600000?d.toLocaleTimeString([],{hour:'numeric'}):d.toLocaleDateString('en-US',{month:'short',day:'numeric'});};
      const every=n<=24?4:n<=28?4:n<=31?5:15;
      return(
        <svg className="vs-chart" viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" role="img" aria-label="Volume over time, humans over bots">
          <defs><linearGradient id="vs-gg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#7CFC00"/><stop offset="1" stopColor="#E8C044"/></linearGradient></defs>
          {[0.25,0.5,0.75].map(f=><line key={f} x1={padL} x2={W-padR} y1={y(max*f)} y2={y(max*f)} stroke="rgba(255,255,255,.07)"/>)}
          {series.map((s,i)=>{const x=padL+i*bw+gap/2,w=Math.max(1,bw-gap);const yb=y(s.b),yh=y(s.b+s.h);return(
            <g key={s.t}>
              <title>{`${fmtT(s.t)} — humans ${fmtUSD(s.h)} · bots ${fmtUSD(s.b)}`}</title>
              <rect x={x} y={yb} width={w} height={Math.max(0,y(0)-yb)} fill={`rgba(${VS_BOT},.85)`}/>
              <rect x={x} y={yh} width={w} height={Math.max(0,yb-yh)} fill={gg?'url(#vs-gg)':`rgba(${rgb},.9)`} opacity={gg?.95:1}/>
            </g>);})}
          {series.map((s,i)=>i%every===0?<text key={'t'+s.t} x={padL+i*bw+bw/2} y={H-6} textAnchor="middle">{fmtT(s.t)}</text>:null)}
          <text x={W-padR} y={padT+8} textAnchor="end">{fmtUSD(max)}</text>
        </svg>
      );
    };
    /* Buys vs sells of the token for one side (round 5): a two-tone bar in the dashboard's up / down colours + the two figures. */
    const VsBuySell=({b,s})=>{const t=(b.usd||0)+(s.usd||0);if(!(t>0))return null;const pb=b.usd/t*100;return(
      <div className="vs-bs">
        <div className="vs-bsbar" role="img" aria-label={`Buys ${fmtUSD(b.usd)}, sells ${fmtUSD(s.usd)}`}><i style={{width:`${pb}%`,background:'#2BE07F'}}></i><i style={{width:`${100-pb}%`,background:'#FF5A78'}}></i></div>
        <div className="vs-bsl"><span><b style={{color:'#2BE07F'}}>Buys</b> {fmtUSD(b.usd)} <span className="text-white/40">{fmt(b.n)}</span></span><span><b style={{color:'#FF5A78'}}>Sells</b> {fmtUSD(s.usd)} <span className="text-white/40">{fmt(s.n)}</span></span></div>
      </div>);};
    /* When they trade (round 5): two rows of 24 cells, the viewer's local hours, each row lit by its own busiest hour. */
    const VsHod=({hod,rgb,gg})=>{
      const off=Math.round(-new Date().getTimezoneOffset()/60);   // UTC → local, whole hours
      const local=Array.from({length:24},(_,h)=>hod[((h-off)%24+24)%24]);
      const mh=Math.max(1,...local.map(x=>x[0])),mb=Math.max(1,...local.map(x=>x[1]));
      const lbl=h=>h===0?'12am':h<12?h+'am':h===12?'12pm':(h-12)+'pm';
      const row=(i,max,color)=>local.map((x,h)=>{const a=x[i]/max;return <i key={h} title={`${lbl(h)}: ${fmtUSD(x[i])}`} style={{background:color,opacity:0.08+a*0.92}}></i>;});
      return(
        <div className="vs-hod">
          <div className="vs-hodr"><span className="k">Humans</span><div className="cells">{row(0,mh,gg?'linear-gradient(180deg,#E8C044,#7CFC00)':`rgb(${rgb})`)}</div></div>
          <div className="vs-hodr"><span className="k">Arb bots</span><div className="cells">{row(1,mb,`rgb(${VS_BOT})`)}</div></div>
          <div className="vs-hodx"><span></span><div className="cells">{[0,6,12,18].map(h=><span key={h} style={{gridColumn:`${h+1} / span 6`}}>{lbl(h)}</span>)}</div></div>
          <div className="vs-note mt-1">When they trade {'\u00b7'} your local time {'\u00b7'} each row lit against its own busiest hour</div>
        </div>);
    };
    const VolumeSplitModal=({token:initial,feeRates,pairs,otherPairs,onClose})=>{
      const[token,setToken]=useState(initial==='UFO'?'UFO':'PTGC');
      const[win,setWin]=useState('30D');   // round 7: opens on 30 days (Shaka)
      const[file,setFile]=useState(undefined);
      const[showPools,setShowPools]=useState(false);    // round 4 (Shaka): By pool and Top bots roll down, closed by default
      const[showBots,setShowBots]=useState(false);
      const[showHow,setShowHow]=useState(false);
      const[showHumans,setShowHumans]=useState(false);
      const load=(force)=>{setFile(undefined);fetchSwapVolume(force).then(setFile);};
      useEffect(()=>{let live=true;fetchSwapVolume().then(j=>{if(live)setFile(j);});return()=>{live=false;};},[]);
      const P=VS_PERIODS.find(w=>w.k===win)||VS_PERIODS[1];
      const both=token==='BOTH';
      const T=NH_THEME[both?'PTGC':token],hex=both?'#E8C044':T.hex,rgb=both?'232,192,68':T.rgb;   // BOTH: gold→green on the human side (round 4; the cream read as grey)
      const gg=both?' gg':'';
      /* the pools' partner tokens: the dashboard's DexScreener pairs (both tokens) first, the file's token0 / token1 next */
      const pairMap=React.useMemo(()=>{const m={};[...(pairs||[]),...(otherPairs||[])].forEach(p=>{const a=(p.pairAddress||'').toLowerCase();if(a)m[a]={base:(p.baseToken&&p.baseToken.address||'').toLowerCase(),quote:(p.quoteToken&&p.quoteToken.address||'').toLowerCase()};});return m;},[pairs,otherPairs]);
      const view=React.useMemo(()=>file?vsView(file,token,P,pairMap):null,[file,token,win,pairMap]);
      const ageMs=file?Date.now()-Date.parse(file.generatedAt):null;
      const amber=ageMs!=null&&ageMs>VS_AMBER_MS;
      const phone=typeof window!=='undefined'&&window.innerWidth<640;
      const fee=both?null:(feeRates&&feeRates[token])||0;
      const perOf=tk=>file&&file.tokens[tk]&&file.tokens[tk].periods&&file.tokens[tk].periods[P.p];
      const vg=view&&(both
        ?(feeRates&&perOf('PTGC')&&perOf('UFO')?{h:perOf('PTGC').human.usd*(feeRates.PTGC||0)+perOf('UFO').human.usd*(feeRates.UFO||0),b:perOf('PTGC').bot.usd*(feeRates.PTGC||0)+perOf('UFO').bot.usd*(feeRates.UFO||0)}:null)
        :(fee>0?{h:view.human.usd*fee,b:view.bot.usd*fee}:null));
      const pct=r=>r>0?`${+(r*100).toFixed(2)}%`:'';
      const feeLabel=both?`${pct(feeRates&&feeRates.PTGC)} PTGC · ${pct(feeRates&&feeRates.UFO)} UFO fee`:`at the ${pct(fee)} fee`;
      const share=(a,b)=>a+b>0?a/(a+b):null;
      const botN=view?Object.values(view.senders).filter(s=>s.kind==='bot').length:0;
      const logo=both?null:TOKENS[token].logo;
      const Fold=({open,onToggle,title,count,color,children})=>(
        <div className="mt-3">
          <button type="button" onClick={onToggle} aria-expanded={open} className="vs-fold">
            <span className="t" style={{color}}>{title}</span>
            <span className="flex items-center gap-3"><span className="c">{count}</span><span aria-hidden="true" className="ch">{'▼'}</span></span>
          </button>
          {open&&children}
        </div>
      );
      return(
        <Modal onClose={onClose} label={`${token} humans vs bots`} className="z-50 flex items-center justify-center p-0 sm:p-4 modal-overlay bg-black/85">
          <div onClick={e=>e.stopPropagation()} className="relative w-full h-[100dvh] sm:h-auto sm:max-h-[calc(100dvh-2rem)] sm:max-w-4xl flex flex-col rounded-none sm:rounded-3xl border bg-[#070707] overflow-y-auto overflow-x-hidden overscroll-contain" style={{borderColor:`${hex}55`,boxShadow:`0 0 80px -20px ${hex}66, 0 30px 80px -20px rgba(0,0,0,.9)`}}>
            <div aria-hidden="true" className="pointer-events-none absolute -top-32 left-1/2 -translate-x-1/2 w-[640px] h-[300px] rounded-full blur-3xl opacity-20" style={{background:`radial-gradient(circle, ${hex} 0%, transparent 65%)`}}></div>
            <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-px" style={{background:`linear-gradient(90deg, transparent, ${hex}cc, transparent)`}}></div>
            {/* Header — the DAO panel's blue mountains (round 3); his art for this window is owed */}
            <div className="relative shrink-0 px-4 sm:px-6 pt-4 sm:pt-6 pb-3 overflow-hidden" style={{minHeight:phone?150:190}}>
              <div aria-hidden="true" className="vs-sky"></div>
              <div aria-hidden="true" className="vs-sky-veil"></div>
              <div className="relative flex items-start gap-3 sm:gap-4">
                <div className="relative shrink-0 flex items-center">
                  {both?(<><img src={TOKENS.PTGC.logo} alt="" className="relative w-12 h-12 sm:w-20 sm:h-20 -mr-3" style={{filter:'drop-shadow(0 4px 12px rgba(0,0,0,.9))'}}/><img src={TOKENS.UFO.logo} alt="" className="relative w-12 h-12 sm:w-20 sm:h-20" style={{filter:'drop-shadow(0 4px 12px rgba(0,0,0,.9))'}}/></>)
                  :(<><div aria-hidden="true" className="absolute inset-0 rounded-full blur-xl opacity-50 scale-110" style={{background:`radial-gradient(circle, ${hex} 0%, transparent 60%)`}}></div><img src={logo} alt="" className="relative w-16 h-16 sm:w-24 sm:h-24" style={{filter:'drop-shadow(0 4px 12px rgba(0,0,0,.9))'}}/></>)}
                </div>
                <div className="flex-1 min-w-0" style={{textShadow:both?'none':'0 2px 10px rgba(0,0,0,.95), 0 0 24px rgba(0,0,0,.8)'}}>
                  <h2 className={`font-orbitron text-2xl sm:text-4xl font-bold tracking-wide leading-tight${both?' gold-green-text':''}`} style={both?{filter:'drop-shadow(0 2px 6px rgba(0,0,0,.9))'}:{color:hex}}>Humans vs Bots</h2>
                  <div className="text-white/85 text-[13px] sm:text-base mt-1 font-medium" style={{textShadow:'0 2px 10px rgba(0,0,0,.95)'}}>{P.label} {'·'} who moves {both?'the Grays’':token+'’s'} volume {'—'} people, or the arbitrage bots</div>
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
            <div className="relative px-4 sm:px-6 pb-5 sm:pb-6 flex-1 min-h-0" style={{'--tg':rgb,'--bot':VS_BOT}}>
              {file===null?(
                <div className="rounded-2xl border border-white/10 bg-black/40 p-6 text-center">
                  <div className="text-white/80 font-semibold">Couldn't load the volume file</div>
                  <div className="text-white/45 text-sm mt-1">The hourly file didn't answer, or it is more than {VS_MAX_AGE/3600000} hours old.</div>
                  <button type="button" onClick={()=>load(true)} className="tap-h mt-4 px-4 rounded-full border text-xs font-bold uppercase tracking-[0.14em]" style={{borderColor:`${hex}88`,color:hex}}>Retry</button>
                </div>
              ):file===undefined?(
                <div aria-busy="true" className="space-y-3">
                  <div className="h-[46px] rounded-2xl bg-white/[0.05] animate-pulse"></div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">{[0,1].map(i=><div key={i} className="h-[210px] rounded-2xl bg-white/[0.05] animate-pulse"></div>)}</div>
                  <div className="h-[170px] rounded-2xl bg-white/[0.04] animate-pulse"></div>
                </div>
              ):(
                <>
                  {/* the whole — one strip */}
                  <div className="vs-strip">
                    <span><span className="k">Total volume</span><span className="v tabular-nums">{fmtUSD(view.total.usd)}</span></span>
                    <span><span className="k">Trades</span><span className="v tabular-nums">{fmt(view.total.n)}</span></span>
                    {vg&&<span><span className="k">Value generated</span><span className="v tabular-nums">{fmtUSD(vg.h+vg.b)}</span></span>}
                    <span className="ml-auto text-[13px] text-white/45 font-medium">{P.label.toLowerCase()} {'·'} {both?'PTGC + UFO':token}</span>
                  </div>
                  {/* the two sides — volume, then the value it generated (round 4: "tied to the volume boxes… this much human volume generated this much value") */}
                  <div className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 sm:gap-3">
                    <div className={`vs-card hu${token==='UFO'?' ufo':both?' both':''}`} style={{'--acc':rgb}}>
                      <div className="bg" aria-hidden="true"></div>{both&&<div className="bg2" aria-hidden="true"></div>}
                      <img className="fig" src="logos/hvb/human.webp" alt="" aria-hidden="true"/>
                      <div className="hd"><span className={`n${gg}`}>Humans</span><span className={`pct tabular-nums${gg}`}>{vsPct(share(view.human.usd,view.bot.usd))}</span></div>
                      <div className="k">Volume</div>
                      <div className="v tabular-nums">{fmtUSD(view.human.usd)}</div>
                      <div className="s">{fmt(view.human.n)} trades{view.wallets.humanTxs>0?(view.wallets.human>0?<> by <b className="text-white">{view.wallets.humanTxsKnown<view.wallets.humanTxs||both?'\u2265':''}{fmt(view.wallets.human)}</b> wallet{view.wallets.human===1?'':'s'}</>:<span className="text-white/40"> {'\u00b7'} wallets being counted</span>):null} through {view.humans.length} router{view.humans.length===1?'':'s'}</div>
                      {view.hasDir&&<VsBuySell b={view.buys.human} s={view.sells.human}/>}
                      {vg&&<div className="vg"><span><span className="k">Value generated</span><div className="v tabular-nums">{fmtUSD(vg.h)}</div></span><span className="s">{vsPct(share(vg.h,vg.b))} of it {'·'} {feeLabel}</span></div>}
                    </div>
                    <div className="vs-card bo" style={{'--acc':VS_BOT}}>
                      <div className="bg" aria-hidden="true"></div>
                      <img className="fig" src="logos/hvb/bot.webp" alt="" aria-hidden="true"/>
                      <div className="hd"><span className="n">Arb bots</span><span className="pct tabular-nums">{vsPct(share(view.bot.usd,view.human.usd))}</span></div>
                      <div className="k">Volume</div>
                      <div className="v tabular-nums">{fmtUSD(view.bot.usd)}</div>
                      <div className="s">{fmt(view.bot.n)} trades from {fmt(botN)} bot contract{botN===1?'':'s'}{view.arb.txs>0&&<> {'\u00b7'} <b className="text-white">{fmt(view.arb.txs)}</b> round trip{view.arb.txs===1?'':'s'}<InfoTip label="Round trips" className="-my-2 ml-1" glyphClass="text-[11px]" tone="text-white/50 hover:text-white/85">A round trip is one transaction that buys the token in one pool and sells it in another — the arbitrage itself. Only a bot does that, so these trades count as bots whoever sent them. {fmt(view.arb.n)} of the {fmt(view.bot.n)} bot trades ({fmtUSD(view.arb.usd)}) were part of one.</InfoTip></>}</div>
                      {view.hasDir&&<VsBuySell b={view.buys.bot} s={view.sells.bot}/>}
                      {vg&&<div className="vg"><span><span className="k">Value generated</span><div className="v tabular-nums">{fmtUSD(vg.b)}</div></span><span className="s">{vsPct(share(vg.b,vg.h))} of it {'·'} {feeLabel}</span></div>}
                    </div>
                  </div>
                  {/* the split over time */}
                  <div className="mt-3 rounded-2xl border border-white/10 bg-black/40 p-3 sm:p-4">
                    <div className="flex items-center justify-between gap-3">
                      <span className="vs-key"><i style={{background:both?'linear-gradient(90deg,#E8C044,#7CFC00)':`rgb(${rgb})`}}></i>Humans {vsPct(share(view.human.usd,view.bot.usd))}</span>
                      <span className="vs-key"><i style={{background:`rgb(${VS_BOT})`}}></i>Arb bots {vsPct(share(view.bot.usd,view.human.usd))}</span>
                    </div>
                    <div className="vs-bar mt-2" role="img" aria-label={`Humans ${vsPct(share(view.human.usd,view.bot.usd))}, bots ${vsPct(share(view.bot.usd,view.human.usd))}`}>
                      <i className={`h${gg}`} style={{width:`${view.total.usd>0?view.human.usd/view.total.usd*100:0}%`}}></i><i className="b" style={{width:`${view.total.usd>0?view.bot.usd/view.total.usd*100:0}%`}}></i>
                    </div>
                    <div className="mt-3"><VsChart series={view.series} binMs={view.binMs} rgb={rgb} gg={both}/></div>
                    {view.hod.some(h=>h[0]+h[1]>0)&&<VsHod hod={view.hod} rgb={rgb} gg={both}/>}
                  </div>
                  {/* roll-downs (round 4): closed by default — the bar with the title and the count, the data under it on a click */}
                  <Fold open={showPools} onToggle={()=>setShowPools(s=>!s)} title="By pool" count={`${view.pools.filter(pl=>pl.total>0||pl.human.n+pl.bot.n>0).length} pools`} color={hex}>
                    <div className="mt-2 rounded-2xl border border-white/10 bg-black/40 overflow-hidden">
                      <table className="w-full">
                        <thead><tr><th className="vs-th">Pool</th><th className="vs-th">Volume</th>{!phone&&<th className="vs-th">Humans</th>}{!phone&&<th className="vs-th">Bots</th>}<th className="vs-th">Bot share</th></tr></thead>
                        <tbody>{view.pools.filter(pl=>pl.total>0||pl.human.n+pl.bot.n>0).slice(0,phone?12:30).map(pl=>{const bs=pl.total>0?pl.bot.usd/pl.total:null;return(
                          <tr key={pl.addr} className="border-t border-white/[0.06]">
                            <td className="vs-td font-semibold"><span className="inline-flex items-center gap-2.5"><VsPoolLogo p={pl.partner}/>{pl.name}{both&&<span className="text-white/40 font-normal text-[12px]"> {pl.token}</span>}</span></td>
                            <td className="vs-td">{fmtUSD(pl.total)}</td>
                            {!phone&&<td className="vs-td">{fmtUSD(pl.human.usd)} <span className="text-white/40 text-[12px]">{fmt(pl.human.n)}</span></td>}
                            {!phone&&<td className="vs-td">{fmtUSD(pl.bot.usd)} <span className="text-white/40 text-[12px]">{fmt(pl.bot.n)}</span></td>}
                            <td className="vs-td">{vsPct(bs)}<span className="vs-mini"><i style={{width:`${bs!=null?bs*100:0}%`,background:`rgb(${VS_BOT})`}}></i></span></td>
                          </tr>);})}</tbody>
                      </table>
                    </div>
                  </Fold>
                  <Fold open={showBots} onToggle={()=>setShowBots(s=>!s)} title="Top bot contracts" count={`${fmt(botN)} contract${botN===1?'':'s'}`} color={`rgb(${VS_BOT})`}>
                    {view.bots.length===0?<div className="mt-2 rounded-2xl border border-white/10 bg-black/40 p-5 text-center text-white/55 text-sm">No bot trades in the {P.label.toLowerCase()}.</div>:(
                      <div className="mt-2 rounded-2xl border border-white/10 bg-black/40 overflow-hidden">
                        <table className="w-full">
                          <thead><tr><th className="vs-th">Contract</th><th className="vs-th">Trades</th><th className="vs-th">Volume</th>{!phone&&<th className="vs-th">Of bot volume</th>}<th className="vs-th">Round trips</th></tr></thead>
                          <tbody>{view.bots.map(b=>(
                            <tr key={b.addr} className="border-t border-white/[0.06]">
                              <td className="vs-td"><a href={`https://scan.pulsechain.com/address/${b.addr}`} target="_blank" rel="noopener noreferrer" className="font-mono text-white/90 hover:text-white hover:underline" title={b.addr}>{vsShort(b.addr)}</a>{b.label&&<span className="text-white/40 text-[12px]"> {b.label}</span>}</td>
                              <td className="vs-td">{fmt(b.n)}</td>
                              <td className="vs-td">{fmtUSD(b.usd)}</td>
                              {!phone&&<td className="vs-td">{vsPct(view.bot.usd>0?b.usd/view.bot.usd:null)}</td>}
                              <td className="vs-td" title={`${fmt(b.arb||0)} of its ${fmt(b.n)} trades were round trips`}>{b.n?vsPct((b.arb||0)/b.n):'\u2014'}</td>
                            </tr>))}</tbody>
                        </table>
                      </div>)}
                  </Fold>
                  <Fold open={showHumans} onToggle={()=>setShowHumans(s=>!s)} title="Human routes" count={`${view.humans.length} router${view.humans.length===1?'':'s'}`} color="rgba(255,255,255,.6)">
                    <div className="mt-2 rounded-2xl border border-white/10 bg-black/30 p-3 vs-note">{view.humans.length?view.humans.map(h=><div key={h.addr} className="flex justify-between gap-3 py-0.5"><span><span className="text-white/85">{h.label||'router'}</span> <a href={`https://scan.pulsechain.com/address/${h.addr}`} target="_blank" rel="noopener noreferrer" className="font-mono text-white/45 hover:text-white/80">{vsShort(h.addr)}</a></span><span className="tabular-nums">{fmt(h.n)} trades {'·'} {fmtUSD(h.usd)}</span></div>):'No router trades in this window.'}</div>
                  </Fold>
                  <Fold open={showHow} onToggle={()=>setShowHow(s=>!s)} title="How we tell" count="" color="rgba(255,255,255,.6)">
                    <div className="mt-2 rounded-2xl border border-white/10 bg-black/30 p-3 vs-note">Every trade on a PulseX pool is a Swap event that names the contract which called the pool. A person's wallet can only reach a pool through a router or aggregator (PulseX, Piteas, …), so trades sent by those are counted as human — a multi-hop swap included. A transaction that buys the token in one pool and sells it in another — a round trip — is the arbitrage itself and counts as a bot whoever sent it. Beyond that, arbitrage bots call the pools from their own contracts, so every other sender is counted as a bot, with two ways back to the human side: a sender PulseScan names as a verified router or aggregator, or one that delivers its output to many different wallets (what a router does; a bot sends the output to itself) with few round trips — that is how an unnamed aggregator such as switch.win is recognised. The Round trips column on the bot list shows how sure we are about each one. Each trade is valued at the token's price for that hour, on the pools this dashboard tracks — so the totals will not match DexScreener's to the dollar. Updated hourly; the list covers 90 days.</div>
                  </Fold>
                </>
              )}
            </div>
          </div>
        </Modal>
      );
    };
    const NhDot=({token,onOpen})=>(", JS+"    const NhDot=({token,onOpen})=>(")

# dashboard wiring: state + render (next to Holders Details)
rep("""      const[showNewHolders,setShowNewHolders]=useState(false);   // Holders Details (2026-10-02): the faint dot while hidden, the button beside the ⓘ once NEW_HOLDERS_LIVE""",
"""      const[showNewHolders,setShowNewHolders]=useState(false);   // Holders Details (2026-10-02): the faint dot while hidden, the button beside the ⓘ once NEW_HOLDERS_LIVE
      const[showVolSplit,setShowVolSplit]=useState(false);       // Volume Split (2026-10-06): human vs arb-bot volume — the faint dot while hidden (VOL_SPLIT_LIVE)""")
rep("""          {!NEW_HOLDERS_LIVE&&activeTab==='dashboard'&&<NhDot token={token} onOpen={()=>setShowNewHolders(true)}/>}""",
"""          {!NEW_HOLDERS_LIVE&&activeTab==='dashboard'&&<NhDot token={token} onOpen={()=>setShowNewHolders(true)}/>}
          {/* Volume Split (2026-10-06): people vs arb bots. Hidden behind the faint bottom-right dot until VOL_SPLIT_LIVE. */}
          {showVolSplit&&<VolumeSplitModal token={token} pairs={data?.pairs||[]} otherPairs={otherTokenPairs||[]} feeRates={{PTGC:TOKENS.PTGC.feeRate||0.05,UFO:TOKENS.UFO.feeRate||0.06,[token]:cfg.feeRate||TOKENS[token].feeRate||(token==='UFO'?0.06:0.05)}} onClose={()=>setShowVolSplit(false)}/>}
          {!VOL_SPLIT_LIVE&&activeTab==='dashboard'&&<VsDot token={token} onOpen={()=>setShowVolSplit(true)}/>}""")
p.write_text(s); print('edited index.html')
