#!/usr/bin/env python3
"""Holders SINGLE share cards v2 (Socials → PTGC / UFO → Holders, and the Holders box's ⓘ), 2026-10-26.
Shaka approved design/holders-card/mock-single-v1.html (single-*.png). Run AFTER tools/holders-card-v2.py.

- The token's half of his Atlantis art (logos/leagues/lg-atl-ptgc|ufo.webp), border in the token colour, "PTGC HOLDERS" title,
  "Past N days" pill, the lit coin + wallets holding + today chip + "+N in N days · %", the N-day trend panel (Hc2Spark),
  7D/30D/90D with "then" and per day, all eight leagues (Wide: one row of 8, Tall: 4 x 2 grid). The 7D/30D/90D switch stays.
- League counts: ONE helper for both cards now — hc2RanksFile() (holder-ranks.json, fetched once per 30 min) + hc2Leagues()
  (people by holdingTier on the starting supply + 1 for the burn wallet's league, unmarked). The combined card's loader uses them.
- The old single card's pieces that nothing uses any more are removed (HoldersSpark, HoldersPeriodTiles, HoldersAliens,
  HoldersLogo, HOLD_TIERS, holdersTierCounts) — checked by count before removal.

Idempotent (done-markers); a second run prints "0 edit(s)". Run from the repo root.
"""
import sys, re, pathlib

P = pathlib.Path('index.html')
s = P.read_text()
edits = 0

def rep(old, new, marker, count=1):
    global s, edits
    if marker in s:
        return
    n = s.count(old)
    if n != count:
        sys.exit(f'anchor found {n}x (want {count}): {old[:100]!r}')
    s = s.replace(old, new)
    edits += 1

if 'const Hc2Spark=' not in s:
    sys.exit('run tools/holders-card-v2.py first')

# ---- 1. shapes for the single card -----------------------------------------------------------------------------------
a = s.find('    const HOLD1_SHAPES={'); b = s.find('    const HOLD_THEME={')
if 'hc2s:1' not in s:
    s = s[:a] + """    const HOLD1_SHAPES={   // hc2s:1 — single Holders card v2 (2026-10-26, design/holders-card/mock-single-v1.html)
      wide:{W:1200,H:675,pad:44,top:34,bottom:30,kick:14,title:46,cu:.62,big:84,lb:13,chip:16,sh:150,sf:10,pp:8,pk:11,pv:22,pa:12,lh:12,gg:7,r8p:'10px 6px 8px',r8i:50,r8c:21,gt:10.5,g:12,cw:600},
      tall:{W:1080,H:1350,pad:56,top:46,bottom:42,kick:15,title:60,cu:.82,big:104,lb:16,chip:20,sh:166,sf:13,pp:12,pk:14,pv:30,pa:15,lh:15,gg:12,gi:14,gpad:'12px 14px',ia:64,gc:32,gt:13,g:16}
    };
""" + s[b:]
    edits += 1

# ---- 2. Hc2Periods: optional "then"; Hc2Leagues: `row` picks the one-row layout -------------------------------------
rep("const Hc2Periods=({p,z})=>{", "const Hc2Periods=({p,z,showThen})=>{", "const Hc2Periods=({p,z,showThen})=>{")
rep("""<div className="a tabular-nums" style={{fontSize:z.pa,marginTop:4}}>{net==null?(cur!=null?'gathering…':'not available'):`${net>=0?'+':''}${(net/days).toFixed(1)}/day`}</div>""",
    """<div className="a tabular-nums" style={{fontSize:z.pa,marginTop:4}}>{net==null?(cur!=null?'gathering…':'not available'):`${showThen?`${fmt(then)} then · `:''}${net>=0?'+':''}${(net/days).toFixed(1)}/day`}</div>""",
    "${showThen?`${fmt(then)} then · `:''}")
rep("""    /* lg = {counts:[8], people, burnIn:index|null} or null. Wide = 4 x 2 tiles, tall = one row of 8. */
    const Hc2Leagues=({lg,rgb,z,tall})=>{""",
    """    /* lg = {counts:[8], people, burnIn:index|null} or null. row = one row of 8 (combined Tall, single Wide), else 4 x 2 tiles. */
    const Hc2Leagues=({lg,rgb,z,row})=>{""", "const Hc2Leagues=({lg,rgb,z,row})=>{")
rep("      if(tall)return(\n        <div>{head}\n          <div className=\"hc2-row8\"",
    "      if(row)return(\n        <div>{head}\n          <div className=\"hc2-row8\"", "      if(row)return(\n        <div>{head}\n          <div className=\"hc2-row8\"")
rep("<Hc2Leagues lg={d?d.leagues:null} rgb={T.rgb} z={z} tall={tall}/>", "<Hc2Leagues lg={d?d.leagues:null} rgb={T.rgb} z={z} row={tall}/>", "z={z} row={tall}/>")

# ---- 3. shared league helpers (module scope, just above Hc2Spark) ---------------------------------------------------
rep("    const HC2_FS='hc2-fs';\n",
    """    /* The eight league counts for the Holders cards: PEOPLE from data/holder-ranks.json (`b` = every person's balance in whole
       tokens, <= 48 h old) placed by holdingTier (% of the STARTING supply — the dashboard strip's basis), + 1 for the burn wallet
       in the league token-allocation.json names (`burnIn`), unmarked (Shaka: no 🔥). Unknown → null → "—". */
    let _hc2Ranks=null;
    const hc2RanksFile=()=>{
      const now=Date.now();
      if(_hc2Ranks&&now-_hc2Ranks.at<30*60*1000)return _hc2Ranks.p;
      const p=fetch('https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/holder-ranks.json?t='+Math.floor(now/3600000)).then(r=>r.ok?r.json():null).catch(()=>null);
      _hc2Ranks={at:now,p};p.then(j=>{if(!j)_hc2Ranks=null;});
      return p;
    };
    const hc2Leagues=(ranksFile,tkn,burnInName)=>{
      const e=ranksFile&&ranksFile.tokens&&ranksFile.tokens[tkn];
      const at=e&&Date.parse(e.readAt);
      if(!e||!Array.isArray(e.b)||!e.b.length||!isFinite(at)||Date.now()-at>=48*3600*1000)return null;
      const counts=BURN_C.map(()=>0);
      for(const v of e.b){const c=holdingTier(Number(v),tkn);if(c)counts[BURN_C.indexOf(c)]++;}
      const bi=burnInName?BURN_C.findIndex(c=>c.n===burnInName):-1;
      if(bi>=0)counts[bi]++;
      return{counts,people:Number.isFinite(e.holders)?e.holders:e.b.length,burnIn:bi>=0?bi:null};
    };
""", "const hc2RanksFile=()=>{")

# the combined loader uses them
a = s.find("            /* hc2 (2026-10-26): all eight leagues for the card")
b = s.find("            setHoldersShareData({\n              PTGC:{holders:ptgcHolders")
if a >= 0 and b > a:
    s = s[:a] + "            const ranksFile=await hc2RanksFile();   // hc2: the eight leagues (hc2Leagues)\n" + s[b:]
    edits += 1
rep("leagues:holdersLeagues('PTGC',ptgcTierObj)}", "leagues:hc2Leagues(ranksFile,'PTGC',ptgcTierObj&&ptgcTierObj.burnIn)}", "hc2Leagues(ranksFile,'PTGC'")
rep("leagues:holdersLeagues('UFO',ufoTierObj)}", "leagues:hc2Leagues(ranksFile,'UFO',ufoTierObj&&ufoTierObj.burnIn)}", "hc2Leagues(ranksFile,'UFO'")

# ---- 4. the single card -------------------------------------------------------------------------------------------------
a = s.find("    /* ⓘ Holder Analytics → 📷: one token, in its colour.")
b = s.find("    /* The ⓘ on the Holders box (both dashboards).")
NEW_SINGLE = r"""    /* ⓘ Holder Analytics → 📷: one token, in its colour (v2 2026-10-26, design/holders-card/mock-single-v1.html). Reads the same
       state the modal prints (holdersByPeriod, holders, holderTiers.burnIn); `leagues` comes from HoldersSingleModal (hc2Leagues). */
    const HoldersSingleCard=({token,holders,holdersByPeriod,leagues,shape='wide',days=30,today24})=>{
      const z=HOLD1_SHAPES[shape]||HOLD1_SHAPES.wide,tall=shape==='tall';
      const T=HOLD_THEME[token]||HOLD_THEME.PTGC;
      const today=new Date().toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});
      const hp=holdersByPeriod||{};
      const cur=hp.current!=null?hp.current:(holders!=null?holders:null);
      const p={current:cur,d1Ago:hp.d1Ago!=null?hp.d1Ago:null,d7Ago:hp.d7Ago!=null?hp.d7Ago:null,d30Ago:hp.d30Ago!=null?hp.d30Ago:null,d90Ago:hp.d90Ago!=null?hp.d90Ago:null};
      const chg24h=today24!==undefined?today24:(cur!=null&&p.d1Ago!=null?cur-p.d1Ago:null);   // c5: the dashboard's one 24 h number
      const thenWin=days===7?p.d7Ago:days===90?p.d90Ago:p.d30Ago;   // the window's own "then" for the headline line
      const nW=cur!=null&&thenWin!=null?cur-thenWin:null;
      const pctW=nW!=null&&thenWin>0?nW/thenWin*100:null;
      const series=holdersSeries(token,cur,days);
      const kick=<div className="hc2-kick" style={{fontSize:z.kick}}>The Grays {'·'} Holder Analytics</div>;
      const ttl=<div className="hc2-ttl" style={{fontSize:z.title,marginTop:tall?12:8}}><span className={T.cls}>{token}</span> <span style={{color:'#fff'}}>Holders</span></div>;
      const pill=<span className="hc2-pill" style={tall?{fontSize:16,padding:'10px 22px'}:{fontSize:12,padding:'8px 16px'}}><span style={{color:T.hex}}>Past {days} days</span></span>;
      const amount=(
        <div style={{textAlign:tall?'center':'left'}}>
          <div className="hc2-lbl" style={{fontSize:z.lb}}>Wallets holding</div>
          <div className="hc2-big tabular-nums" style={{fontSize:z.big,marginTop:6,textAlign:tall?'center':'left'}}>{fmt(cur)}</div>
          <div style={{display:'flex',alignItems:'center',gap:12,marginTop:10,justifyContent:tall?'center':'flex-start'}}>
            <HoldersTodayChip d={chg24h} z={z}/>
            <span className="tabular-nums" style={{fontSize:z.chip,fontWeight:600,color:'rgba(255,255,255,0.7)',whiteSpace:'nowrap'}}>{nW==null?`— in ${days} days`:<>{holdSgn(nW)} in {days} days {'·'} <span style={{color:holdCol(nW)}}>{pctW!=null?pctW.toFixed(2)+'%':'—'}</span></>}</span>
          </div>
        </div>);
      const coin=<div className={`hc2-coin${token==='UFO'?' g':''}`} style={{'--u':`${z.cu}px`}}><LgCoin token={token}/></div>;
      const chartBox=w=>(
        <div className="hc2-tp" style={{'--c':T.rgb,padding:tall?'16px 18px 12px':'12px 14px 10px'}}>
          <div className="hc2-lgh" style={{fontSize:z.lh,marginBottom:8}}><span style={{color:`rgba(${T.rgb},0.95)`}}>{days}-day holder trend</span></div>
          <Hc2Spark pts={series.pts} from={series.from} w={w} h={z.sh} rgb={T.rgb} hex={T.hex} fs={z.sf}/>
        </div>);
      const foot=<div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginTop:tall?16:12}}><span className={`font-orbitron ${T.cls}`} style={{fontSize:tall?30:24,fontWeight:700}}>ptgc-ufo.com</span><span className="hc2-meta" style={{fontSize:tall?12:10.5}}>{today} {'·'} Holders = every address {'·'} Leagues = people</span></div>;
      const iw=z.W-2*z.pad;
      return(
        <div className="hc2 relative overflow-hidden text-white" style={{width:z.W,height:z.H,background:'#04070a',fontFamily:"'Rajdhani',sans-serif"}}>
          <div aria-hidden="true" className="hc2-sky" style={{backgroundImage:`url(logos/leagues/lg-atl-${token==='UFO'?'ufo':'ptgc'}.webp?v=${LG_ART_V})`,backgroundPosition:'50% 35%'}}></div>
          <div aria-hidden="true" className="hc2-shade"></div>
          <div aria-hidden="true" className="hc2-glow" style={{boxShadow:`0 0 70px -10px rgba(${T.rgb},0.55)`}}></div>
          <div aria-hidden="true" className="hc2-edge" style={{background:`linear-gradient(#0000,#0000) padding-box,linear-gradient(135deg,${T.edge[0]} 0%,${T.edge[1]} 50%,${T.edge[2]} 100%) border-box`}}></div>
          <div style={{position:'absolute',left:z.pad,right:z.pad,top:z.top,bottom:z.bottom,display:'flex',flexDirection:'column'}}>
            {tall?(
              <>
                <div style={{textAlign:'center'}}>{kick}{ttl}<div style={{marginTop:14}}>{pill}</div></div>
                <div style={{display:'flex',justifyContent:'center',marginTop:38}}>{coin}</div>
                <div style={{marginTop:28}}>{amount}</div>
                <div style={{flex:1,minHeight:0}}></div>
                {chartBox(iw-36)}
                <div style={{marginTop:z.g}}><Hc2Periods p={p} z={z} showThen/></div>
                <div style={{marginTop:z.g+4}}><Hc2Leagues lg={leagues} rgb={T.rgb} z={z} row={false}/></div>
                {foot}
              </>
            ):(
              <>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start'}}><div>{kick}{ttl}</div><div style={{paddingTop:4}}>{pill}</div></div>
                <div style={{flex:1,minHeight:0}}></div>
                <div style={{display:'flex',gap:22,alignItems:'center'}}>
                  <div style={{display:'flex',alignItems:'center',gap:26,flex:1,minWidth:0,paddingLeft:18}}>{coin}{amount}</div>
                  <div style={{width:z.cw,flexShrink:0}}>{chartBox(z.cw-28)}</div>
                </div>
                <div style={{marginTop:z.g}}><Hc2Periods p={p} z={z} showThen/></div>
                <div style={{marginTop:z.g+2}}><Hc2Leagues lg={leagues} rgb={T.rgb} z={z} row/></div>
                {foot}
              </>
            )}
          </div>
        </div>
      );
    };
"""
if 'leagues,shape=\'wide\',days=30,today24})=>{' not in s:
    if a < 0 or b < 0 or b < a:
        sys.exit('single card anchors not found')
    s = s[:a] + NEW_SINGLE + s[b:]
    edits += 1

# ---- 5. the modal loads the ranks file and passes leagues ------------------------------------------------------------
rep("""      const[days,setDays]=useState(30);
      const z=HOLD1_SHAPES[shape];""",
    """      const[days,setDays]=useState(30);
      const[ranks,setRanks]=useState(undefined);   // hc2s: holder-ranks.json for the eight leagues (undefined = loading → "—")
      useEffect(()=>{let on=true;hc2RanksFile().then(j=>{if(on)setRanks(j||null);});return()=>{on=false;};},[]);
      const leagues=ranks?hc2Leagues(ranks,token,tiers&&tiers.burnIn):null;
      const z=HOLD1_SHAPES[shape];""", "const[ranks,setRanks]=useState(undefined);   // hc2s")
rep("<HoldersSingleCard token={token} holders={holders} holdersByPeriod={holdersByPeriod} tiers={tiers} today24={today24} shape={shape} days={days}/>",
    "<HoldersSingleCard token={token} holders={holders} holdersByPeriod={holdersByPeriod} leagues={leagues} today24={today24} shape={shape} days={days}/>",
    "leagues={leagues} today24={today24} shape={shape} days={days}/>")

# ---- 6. remove the pieces nothing uses any more ----------------------------------------------------------------------
def drop_const(name, start_pat, end_pat, use_pat=None):
    """Remove `const name=…` (from start_pat up to end_pat, exclusive) when name has no other use."""
    global s, edits
    a = s.find(start_pat)
    if a < 0:
        return
    b = s.find(end_pat, a + len(start_pat))
    if b < 0:
        sys.exit(f'end anchor for {name} not found')
    rest = s[:a] + s[b:]
    if re.search(use_pat or (r'\b' + re.escape(name) + r'\b'), rest):
        print(f'  keep {name}: still used')
        return
    s = rest
    edits += 1

for name, start, end, *_ in [
    ('HoldersPeriodTiles', '    /* The three period tiles + the "today vs daily growth rate" caption.', '    /* ===== Holders card v2 (hc2'),
    ('HoldersSpark', '    const HoldersSpark=(', '    const HoldersAliens=('),
    ('HoldersAliens', '    const HoldersAliens=(', '    const HoldersLogo=('),
    ('HoldersLogo', '    const HoldersLogo=(', '    const HoldersTodayChip=('),
    ('holdersRate', '    /* Same maths as HolderAnalyticsModal', '    /* Trend series from the holder-history file', r'holdersRate\('),
    ('holdersTierCounts', '    /* The seeded / failed tier object is all-zero;', '    /* Trend series from the holder-history file'),
    ('HOLD_TIERS', '    const HOLD_TIERS=[', '    const HOLD_SHAPES={'),
    ('HOLD_ALIENS', '    const HOLD_ALIENS=', '\n'),
]:
    drop_const(name, start, end) if len(_) == 0 else drop_const(name, start, end, _[0])

P.write_text(s)
print(f'{edits} edit(s)')
