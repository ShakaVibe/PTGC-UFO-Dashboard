#!/usr/bin/env python3
"""Holders share card v2 (Socials -> Combined -> Holders), 2026-10-26, Shaka picked mock A
(design/holders-card/mock-v1.html, mock-A-wide.png / mock-A-tall.png).

- His Atlantis split art (logos/leagues/lg-atl-split.webp) behind the card, the gold -> green edge, "HOLDERS" in Orbitron.
- Each token panel: the dashboard's lit coin (LgCoin), holders (every address, same as the dashboard box), today chip,
  30-day trend (Hc2Spark), 7D / 30D / 90D net + per-day, and ALL EIGHT leagues with his sea-creature art (Wide: 4 x 2 grid,
  Tall: one row of 8). The old card showed five emoji groups with Squid -> Shell lumped behind one squid.
- League counts = PEOPLE (data/holder-ranks.json `b`, <= 48 h old, % of the starting supply - the same rule as holdingTier
  and the dashboard strip) + 1 for the burn wallet in the league token-allocation.json names (`tiers.burnIn`), unmarked (Shaka: no 🔥).
  Missing / stale ranks file -> every league "—" (never zeros).

Idempotent: every edit has a done-marker; a second run prints "0 edit(s)". Run from the repo root.
"""
import sys, pathlib

P = pathlib.Path('index.html')
s = P.read_text()
edits = 0

def rep(old, new, marker, count=1):
    global s, edits
    if marker in s:
        return
    n = s.count(old)
    if n != count:
        sys.exit(f'anchor found {n}x (want {count}): {old[:90]!r}')
    s = s.replace(old, new)
    edits += 1

# ---- 1. shapes -------------------------------------------------------------------------------------------------
OLD_SHAPES = s[s.find('    const HOLD_SHAPES={'):s.find('    const HOLD1_SHAPES={')] if 'hc2:1' not in s else ''
NEW_SHAPES = """    const HOLD_SHAPES={   // hc2:1 — Holders card v2 (2026-10-26, mock A)
      wide:{W:1200,H:675,pad:44,top:34,bottom:30,cu:.4,nm:32,big:58,lb:12,chip:15,idg:16,pad2:20,g:10,sh:64,sf:10,pp:7,pk:11,pv:22,pa:12,lh:12,gg:7,gi:8,gpad:'5px 8px',ia:38,gc:21,gt:10.5,title:56,kick:15},
      tall:{W:1080,H:1350,pad:56,top:42,bottom:42,cu:.44,nm:42,big:70,lb:15,chip:19,idg:22,pad2:22,g:10,sh:50,sf:12,pp:8,pk:13,pv:24,pa:13,lh:15,gg:10,r8p:'10px 6px 8px',r8i:60,r8c:25,gt:13,title:66,kick:15}
    };
"""
if OLD_SHAPES:
    rep(OLD_SHAPES, NEW_SHAPES, 'hc2:1')

# ---- 2. the combined card ------------------------------------------------------------------------------------------
a = s.find('    /* Creature row — the emojis as they are (gotcha 9)')
b = s.find("    /* Socials → Holders. data / loading / error are the Dashboard's holdersShareData state")
NEW_CARD = r"""    /* ===== Holders card v2 (hc2, 2026-10-26 — Shaka picked mock A, design/holders-card/mock-v1.html) =====
       Combined card only (HoldersSingleCard keeps its own look). Leagues = people from holder-ranks.json + the burn wallet
       (holdersLeagues in the loader); null = unknown → "—". Screenshot-only card: masks / background-clip are fine. */
    const HC2_FS='hc2-fs';
    const Hc2Spark=({pts,from,w,h,rgb,hex,fs})=>{
      const uid=React.useId().replace(/[^a-zA-Z0-9]/g,'');
      if(!pts||pts.length<2)return<div style={{width:w,height:h,display:'flex',alignItems:'center',justifyContent:'center',fontSize:fs+5,fontStyle:'italic',color:'rgba(255,255,255,0.4)'}}>{pts&&pts.length===1?'Trend appears as days accumulate':'History unavailable'}</div>;
      const p=6,base=h-fs-4,mn=Math.min(...pts),mx=Math.max(...pts),r=(mx-mn)||1;
      const P=pts.map((v,i)=>[p+i*(w-2*p)/(pts.length-1),p+(1-(v-mn)/r)*(base-p-4)]);
      const d=P.map((x,i)=>(i?'L':'M')+x[0].toFixed(1)+' '+x[1].toFixed(1)).join(' '),last=P[P.length-1];
      return(
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{display:'block',overflow:'visible'}} aria-hidden="true">
          <defs><linearGradient id={`hc2g${uid}`} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={`rgba(${rgb},0.45)`}/><stop offset="1" stopColor={`rgba(${rgb},0)`}/></linearGradient>
            <filter id={`hc2f${uid}`} x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3"/></filter></defs>
          <path d={`${d} L${last[0].toFixed(1)} ${base} L${p} ${base} Z`} fill={`url(#hc2g${uid})`}/>
          <path d={d} fill="none" stroke={hex} strokeWidth="5" strokeLinejoin="round" opacity="0.5" filter={`url(#hc2f${uid})`}/>
          <path d={d} fill="none" stroke={hex} strokeWidth="2.6" strokeLinejoin="round" strokeLinecap="round"/>
          <circle cx={last[0]} cy={last[1]} r="5" fill={hex} stroke="#fff" strokeWidth="1.5"/>
          <text x={p} y={h-2} fontFamily="Orbitron" fontWeight="700" fontSize={fs} letterSpacing="2" fill="rgba(255,255,255,0.45)">{from} {'·'} {fmt(pts[0])}</text>
          <text x={w-p} y={h-2} textAnchor="end" fontFamily="Orbitron" fontWeight="700" fontSize={fs} letterSpacing="2" fill="rgba(255,255,255,0.45)">TODAY {'·'} {fmt(pts[pts.length-1])}</text>
        </svg>);
    };
    const Hc2Periods=({p,z})=>{
      const cur=p&&p.current!=null?p.current:null;
      return(
        <div className="hc2-per" style={{padding:`${z.pp}px 0`}}>
          {[['7D',p?p.d7Ago:null,7],['30D',p?p.d30Ago:null,30],['90D',p?p.d90Ago:null,90]].map(([k,then,days])=>{
            const net=cur!=null&&then!=null?cur-then:null;
            return(
              <div key={k}>
                <div className="k" style={{fontSize:z.pk}}>{k}</div>
                <div className="v tabular-nums" style={{fontSize:z.pv,marginTop:5,color:holdCol(net)}}>{net==null?'—':`${holdArrow(net)} ${holdSgn(net)}`}</div>
                <div className="a tabular-nums" style={{fontSize:z.pa,marginTop:4}}>{net==null?(cur!=null?'gathering…':'not available'):`${net>=0?'+':''}${(net/days).toFixed(1)}/day`}</div>
              </div>);})}
        </div>);
    };
    /* lg = {counts:[8], people, burnIn:index|null} or null. Wide = 4 x 2 tiles, tall = one row of 8. */
    const Hc2Leagues=({lg,rgb,z,tall})=>{
      const head=(
        <div className="hc2-lgh" style={{fontSize:z.lh}}>
          <span style={{color:`rgba(${rgb},0.95)`}}>The Leagues</span>
          <span className="tabular-nums" style={{color:'rgba(255,255,255,0.5)'}}>{lg?`${fmt(lg.people)} people`:'people only'}</span>
        </div>);
      const cell=i=>{const c=lg?lg.counts[i]:null;return{c,dim:!c};};
      if(tall)return(
        <div>{head}
          <div className="hc2-row8" style={{marginTop:z.gg+2,padding:z.r8p}}>
            {LH_TIERS.map(([n,k],i)=>{const{c,dim}=cell(i);return(
              <div key={n}>
                <img src={lhSea(k)} alt="" style={{width:z.r8i,height:z.r8i}}/>
                <div className="c tabular-nums" style={{fontSize:z.r8c,marginTop:4,color:dim?'rgba(255,255,255,0.35)':'#fff'}}>{c==null?'—':fmt(c)}</div>
                <div className="t" style={{fontSize:z.gt,marginTop:3}}>{n}</div>
              </div>);})}
          </div>
        </div>);
      return(
        <div>{head}
          <div className="hc2-lgg" style={{gap:z.gg,marginTop:z.gg+2}}>
            {LH_TIERS.map(([n,k],i)=>{const{c,dim}=cell(i);return(
              <div key={n} className={`hc2-lgt${dim?' z':''}`} style={{gap:z.gi,padding:z.gpad}}>
                <img src={lhSea(k)} alt="" style={{width:z.ia,height:z.ia}}/>
                <div><div className="c tabular-nums" style={{fontSize:z.gc}}>{c==null?'—':fmt(c)}</div><div className="t" style={{fontSize:z.gt,marginTop:3}}>{n}</div></div>
              </div>);})}
          </div>
        </div>);
    };
    /* One token's panel. d = holdersShareData[tkn] = {holders,tiers,periods,leagues} or null. */
    const HoldersTokenPanel=({tkn,d,z,tall,w,today24})=>{
      const T=HOLD_THEME[tkn],ufo=tkn==='UFO';
      const holders=d&&d.holders!=null?d.holders:null;
      const p=d?d.periods:null;
      const chg24h=today24!==undefined?today24:(p&&p.current!=null&&p.d1Ago!=null?p.current-p.d1Ago:null);   // c5
      const series=holdersSeries(tkn,holders,30);
      const inner=w-2*z.pad2;
      return(
        <div className="hc2-tp" style={{'--c':T.rgb,padding:z.pad2}}>
          <div style={{display:'flex',alignItems:'center',justifyContent:'space-between'}}>
            <div style={{display:'flex',alignItems:'center',gap:z.idg}}>
              <div className={`hc2-coin${ufo?' g':''}`} style={{'--u':`${z.cu}px`}}><LgCoin token={tkn}/></div>
              <div className={`font-orbitron ${T.cls}`} style={{fontSize:z.nm,fontWeight:900,lineHeight:1}}>{tkn}</div>
            </div>
            <div>
              <div className="hc2-big tabular-nums" style={{fontSize:z.big}}>{fmt(holders)}</div>
              <div style={{display:'flex',alignItems:'center',justifyContent:'flex-end',gap:10,marginTop:6}}>
                <span className="hc2-lbl" style={{fontSize:z.lb}}>Holders</span>
                <HoldersTodayChip d={chg24h} z={z}/>
              </div>
            </div>
          </div>
          <div style={{marginTop:z.g}}><Hc2Spark pts={series.pts} from={series.from} w={inner} h={z.sh} rgb={T.rgb} hex={T.hex} fs={z.sf}/></div>
          <div style={{marginTop:z.g}}><Hc2Periods p={p} z={z}/></div>
          <div style={{marginTop:z.g+2}}><Hc2Leagues lg={d?d.leagues:null} rgb={T.rgb} z={z} tall={tall}/></div>
        </div>);
    };
    const HoldersSocialCard=({data,shape='wide',today24})=>{   // c5 prop (missing → ReferenceError, fixed 2026-10-26)
      const z=HOLD_SHAPES[shape]||HOLD_SHAPES.wide,tall=shape==='tall';
      const today=new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
      const P=data?data.PTGC:null,U=data?data.UFO:null;
      const both=P&&U&&P.holders!=null&&U.holders!=null?P.holders+U.holders:null;
      const net=(d,k)=>d&&d.periods&&d.periods.current!=null&&d.periods[k]!=null?d.periods.current-d.periods[k]:null;
      const sum=(a,b)=>a!=null&&b!=null?a+b:null;
      const b7=sum(net(P,'d7Ago'),net(U,'d7Ago')),b30=sum(net(P,'d30Ago'),net(U,'d30Ago'));
      const pw=tall?z.W-2*z.pad:(z.W-2*z.pad-20)/2;
      const pill=(
        <span className="hc2-pill tabular-nums" style={tall?{fontSize:17,padding:'11px 26px'}:{fontSize:13,padding:'9px 18px'}}>
          <span>PTGC + UFO</span><span className="gold-green-text" style={{fontSize:tall?24:19}}>{fmt(both)}</span>
          <span style={{color:holdCol(b7)}}>{holdSgn(b7)} <span style={{color:'rgba(255,255,255,0.5)'}}>7D</span></span>
          <span style={{color:holdCol(b30)}}>{holdSgn(b30)} <span style={{color:'rgba(255,255,255,0.5)'}}>30D</span></span>
        </span>);
      const kick=<div className="hc2-kick" style={{fontSize:z.kick}}>The Grays {'·'} Holder Analytics</div>;
      const ttl=<div className="hc2-ttl gold-green-text" style={{fontSize:z.title,marginTop:tall?12:10}}>Holders</div>;
      const head=tall
        ?<div style={{textAlign:'center'}}>{kick}{ttl}<div style={{marginTop:16}}>{pill}</div></div>
        :<div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}><div>{kick}{ttl}</div>
           <div style={{textAlign:'right',paddingTop:2}}>{pill}<div className="hc2-meta" style={{fontSize:11,marginTop:12}}>{today} {'·'} Past 30 days</div></div></div>;
      const foot=tall
        ?<div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:14}}><span className="font-orbitron gold-green-text" style={{fontSize:30,fontWeight:700}}>ptgc-ufo.com</span><span className="hc2-meta" style={{fontSize:13}}>{today}</span></div>
        :<div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:12}}><span className="font-orbitron gold-green-text" style={{fontSize:24,fontWeight:700}}>ptgc-ufo.com</span><span className="hc2-meta" style={{fontSize:10.5}}>Holders = every address {'·'} Leagues = people</span></div>;
      return(
        <div className="hc2 relative overflow-hidden text-white" style={{width:z.W,height:z.H,background:'#04070a',fontFamily:"'Rajdhani',sans-serif"}}>
          <div aria-hidden="true" className="hc2-sky" style={tall?{backgroundPosition:'50% 0',backgroundSize:'auto 46%'}:undefined}></div>
          <div aria-hidden="true" className="hc2-shade"></div>
          <div aria-hidden="true" className="hc2-glow"></div>
          <div aria-hidden="true" className="hc2-edge"></div>
          <div style={{position:'absolute',left:z.pad,right:z.pad,top:z.top,bottom:z.bottom,display:'flex',flexDirection:'column'}}>
            {head}
            <div style={{flex:1,minHeight:0}}></div>
            <div style={{display:'flex',flexDirection:tall?'column':'row',gap:tall?16:20}}>
              <HoldersTokenPanel tkn="PTGC" d={P} z={z} tall={tall} w={pw} today24={today24?today24.PTGC:undefined}/>
              <HoldersTokenPanel tkn="UFO" d={U} z={z} tall={tall} w={pw} today24={today24?today24.UFO:undefined}/>
            </div>
            {foot}
          </div>
        </div>
      );
    };
"""
if 'const Hc2Spark=' not in s:
    if a < 0 or b < 0 or b < a:
        sys.exit('card block anchors not found')
    s = s[:a] + NEW_CARD + s[b:]
    edits += 1

# ---- 3. CSS ----------------------------------------------------------------------------------------------------------
CSS_ANCHOR = "    .lg-hd .lg-coin{--u:.574px;position:absolute;left:50%;top:60px;transform:translateX(-50%)}\n"
CSS = CSS_ANCHOR + """    /* hc2 — Holders share card v2 (2026-10-26, design/holders-card/mock-v1.html) */
    .hc2-sky{position:absolute;inset:0;background:url(logos/leagues/lg-atl-split.webp?v=1) 50% 30%/cover no-repeat}
    .hc2-shade{position:absolute;inset:0;background:radial-gradient(ellipse 60% 45% at 50% 18%,rgba(2,5,12,.15),rgba(2,5,12,0) 70%),linear-gradient(180deg,rgba(3,8,20,.25) 0%,rgba(3,8,20,.45) 30%,rgba(4,6,10,.82) 62%,rgba(4,6,10,.94) 100%)}
    .hc2-edge{position:absolute;inset:14px;border-radius:26px;border:2px solid transparent;background:linear-gradient(#0000,#0000) padding-box,linear-gradient(90deg,#E8C044 0%,#5DB8FF 50%,#7CFC00 100%) border-box;-webkit-mask:linear-gradient(#000 0 0) padding-box,linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude}
    .hc2-glow{position:absolute;inset:14px;border-radius:26px;box-shadow:0 0 70px -10px rgba(232,192,68,.5),0 0 70px -10px rgba(124,252,0,.4)}
    .hc2-kick{font-family:'Orbitron',monospace;font-weight:700;letter-spacing:.32em;color:rgba(235,242,255,.82);text-transform:uppercase;text-shadow:0 2px 8px #000}
    .hc2-ttl{font-family:'Orbitron',monospace;font-weight:900;letter-spacing:.06em;line-height:1;text-transform:uppercase;filter:drop-shadow(0 3px 14px rgba(0,0,0,.85))}
    .hc2-pill{display:inline-flex;align-items:center;gap:14px;border-radius:999px;border:1px solid rgba(255,255,255,.22);background:rgba(4,6,10,.62);font-family:'Orbitron',monospace;font-weight:700;letter-spacing:.2em;text-transform:uppercase;color:#fff}
    .hc2-meta{font-family:'Orbitron',monospace;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:rgba(255,255,255,.55)}
    .hc2-tp{position:relative;flex:1 1 0;min-width:0;border-radius:22px;background:linear-gradient(180deg,rgba(8,12,18,.78),rgba(4,6,10,.9));border:1.5px solid rgba(var(--c),.55);box-shadow:inset 0 1px 0 rgba(255,255,255,.08),0 0 40px -10px rgba(var(--c),.6);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px)}
    .hc2-coin .lg-coin{--halo:255,120,20;--ring:255,190,80}.hc2-coin.g .lg-coin{--halo:110,255,40;--ring:140,255,60}
    .hc2-big{font-weight:700;line-height:.9;text-align:right;color:#fff}
    .hc2-lbl{font-family:'Orbitron',monospace;font-weight:700;letter-spacing:.24em;text-transform:uppercase;color:rgba(255,255,255,.6)}
    .hc2-per{display:flex;border-radius:14px;background:rgba(0,0,0,.42);border:1px solid rgba(255,255,255,.08)}
    .hc2-per>div{flex:1;text-align:center;border-left:1px solid rgba(255,255,255,.08)}.hc2-per>div:first-child{border-left:0}
    .hc2-per .k{font-family:'Orbitron',monospace;font-weight:700;letter-spacing:.2em;color:rgba(255,255,255,.55)}
    .hc2-per .v{font-weight:700;line-height:1}.hc2-per .a{color:rgba(255,255,255,.5);font-weight:600}
    .hc2-lgh{display:flex;justify-content:space-between;align-items:baseline;font-family:'Orbitron',monospace;font-weight:700;letter-spacing:.2em;text-transform:uppercase}
    .hc2-lgg{display:grid;grid-template-columns:repeat(4,1fr)}
    .hc2-lgt{position:relative;display:flex;align-items:center;border-radius:12px;background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.08)}
    .hc2-lgt img,.hc2-row8 img{flex:none;max-width:none;filter:drop-shadow(0 3px 6px rgba(0,0,0,.8))}
    .hc2-lgt .c,.hc2-row8 .c{font-weight:700;line-height:1;color:#fff}.hc2-lgt.z .c{color:rgba(255,255,255,.35)}
    .hc2-lgt .t,.hc2-row8 .t{font-weight:600;color:rgba(255,255,255,.55);letter-spacing:.06em;text-transform:uppercase;line-height:1}
    .hc2-row8{display:flex;justify-content:space-between;border-radius:16px;background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.08)}
    .hc2-row8>div{position:relative;display:flex;flex-direction:column;align-items:center;flex:1}
"""
rep(CSS_ANCHOR, CSS, '/* hc2 — Holders share card v2')

# ---- 4. the loader: burnIn from the allocation file + the eight leagues from holder-ranks.json ----------------------
rep("""                if(pt&&typeof pt.Whale==='number')ptgcTierObj={Poseidon:pt.Poseidon||0,Whale:pt.Whale||0,Shark:pt.Shark||0,Dolphin:pt.Dolphin||0,SquidAndBelow:pt.SquidAndBelow||0};
                if(ut&&typeof ut.Whale==='number')ufoTierObj={Poseidon:ut.Poseidon||0,Whale:ut.Whale||0,Shark:ut.Shark||0,Dolphin:ut.Dolphin||0,SquidAndBelow:ut.SquidAndBelow||0};""",
    """                if(pt&&typeof pt.Whale==='number')ptgcTierObj={Poseidon:pt.Poseidon||0,Whale:pt.Whale||0,Shark:pt.Shark||0,Dolphin:pt.Dolphin||0,SquidAndBelow:pt.SquidAndBelow||0,burnIn:pt.burnIn||null};   // hc2: burnIn
                if(ut&&typeof ut.Whale==='number')ufoTierObj={Poseidon:ut.Poseidon||0,Whale:ut.Whale||0,Shark:ut.Shark||0,Dolphin:ut.Dolphin||0,SquidAndBelow:ut.SquidAndBelow||0,burnIn:ut.burnIn||null};""",
    "burnIn:pt.burnIn||null};   // hc2: burnIn")

rep("""            setHoldersShareData({
              PTGC:{holders:ptgcHolders,tiers:ptgcTierObj,periods:calcPeriods('PTGC',ptgcHolders)},
              UFO:{holders:ufoHolders,tiers:ufoTierObj,periods:calcPeriods('UFO',ufoHolders)}
            });""",
    """            /* hc2 (2026-10-26): all eight leagues for the card — PEOPLE from data/holder-ranks.json (`b` = every person's balance in
               whole tokens, <= 48 h old), each placed by % of the STARTING supply (holdingTier's rule, the dashboard strip's basis),
               plus the burn wallet in the league token-allocation.json names (its `burnIn`) — counted like the dashboard strip, NOT marked (Shaka: no 🔥). No file → null → "—". */
            let ranksFile=null;
            try{const r=await fetch('https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/holder-ranks.json?t='+Math.floor(Date.now()/3600000));if(r.ok)ranksFile=await r.json();}catch(e){}
            const holdersLeagues=(tkn,tierObj)=>{
              const e=ranksFile&&ranksFile.tokens&&ranksFile.tokens[tkn];
              const at=e&&Date.parse(e.readAt);
              if(!e||!Array.isArray(e.b)||!e.b.length||!isFinite(at)||Date.now()-at>=48*3600*1000)return null;
              const counts=BURN_C.map(()=>0);
              for(const v of e.b){const c=holdingTier(Number(v),tkn);if(c)counts[BURN_C.indexOf(c)]++;}
              const bi=tierObj&&tierObj.burnIn?BURN_C.findIndex(c=>c.n===tierObj.burnIn):-1;
              if(bi>=0)counts[bi]++;
              return{counts,people:Number.isFinite(e.holders)?e.holders:e.b.length,burnIn:bi>=0?bi:null};
            };
            setHoldersShareData({
              PTGC:{holders:ptgcHolders,tiers:ptgcTierObj,periods:calcPeriods('PTGC',ptgcHolders),leagues:holdersLeagues('PTGC',ptgcTierObj)},
              UFO:{holders:ufoHolders,tiers:ufoTierObj,periods:calcPeriods('UFO',ufoHolders),leagues:holdersLeagues('UFO',ufoTierObj)}
            });""",
    "const holdersLeagues=(tkn,tierObj)=>{")

P.write_text(s)
print(f'{edits} edit(s)')
