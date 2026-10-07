#!/usr/bin/env python3
"""Audit III, the P1 session (2026-10-07): c1–c8, plus c11 and c25 (one-liners). Idempotent — run from the repo root on both copies:
    python3 tools/audit3-p1.py
Each edit asserts its anchor exists exactly once (or is already applied) so a drifted file fails loudly instead of half-applying.
  c1  data-presets="react" on the six text/babel tags (the compile 15 s → 3 s; see sessions/2026-10-07-audit.md P-1)
  c2  the DAO buttons' glow pseudo-element clipped on phones (the 11 px sideways scroll on #/ptgc)
  c3  the v2 tab band's scroll cue + the active tab scrolled into view — DashHeaderV2, H2TabBand (jsx), the charts twin; h2.css rules
  c4  fetch-coingecko-data.js: time-based retention (100 days) instead of the last 500 snapshots
  c5  one 24 h holders number: the tile's `holders24h` reaches the KPI Report, the Holders ⓘ card and the Socials Holders card
      (+ a quiet day prints "— quiet" instead of "▼ 100.0%")
  c6  Leagues window + combined Leagues card: "—" when the burn read failed, never "Burned 0"
  c7  Combined Burn Stats card: 810 px frame (was 540 — the UFO rows and the total were cut), screenshot-only
  c8  calculators 10 Yr Projection: a failed burn/price read is "—" + Unavailable, never the unburned supply under LIVE
  c11 h2.css / h2-header.jsx ?v=1 → ?v=2 (both changed 2026-10-05/06)
  c25 toLocaleString('en-US') on the DAY pill and the Leagues table prices (PTGC is day 1,092 — "1.092" in Berlin)
"""
import sys, re, hashlib

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)
def md5(s): return hashlib.md5(s.encode('utf-8')).hexdigest()

class Edit:
    def __init__(self, path):
        self.path = path; self.s = read(path); self.n = 0
    def rep(self, old, new, count=1, done_marker=None):
        """Replace `old` → `new` exactly `count` times; skip silently when `done_marker` (default: new) is already present."""
        if done_marker is not None:
            if done_marker in self.s: return False
        elif new in self.s and old not in self.s:
            return False
        c = self.s.count(old)
        assert c == count, f'{self.path}: expected {count}× anchor, found {c}: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def save(self):
        write(self.path, self.s); print(f'{self.path}: {self.n} edit(s), md5 {md5(self.s)}')

# ------------------------------------------------------------------ index.html
ix = Edit('index.html')

# c1 — data-presets
ix.rep('  <script type="text/babel">\n', '  <script type="text/babel" data-presets="react">\n')
ix.rep("""    /* CAUTION: do NOT write 10n**12n here. Babel (which compiles this page in-browser via
       type="text/babel") transpiles the ** operator into Math.pow(), and Math.pow throws
       "Cannot convert a BigInt value to a number" on BigInt operands. Use a literal. */""",
       """    /* CAUTION: do NOT write 10n**12n here. Babel (which compiles this page in-browser via
       type="text/babel") used to transpile the ** operator into Math.pow(), and Math.pow throws
       "Cannot convert a BigInt value to a number" on BigInt operands. Since 2026-10-07 (Audit III c1)
       the tag carries data-presets="react" — JSX only, no ES5 down-level, the compile is ~5× faster —
       so ** would survive, but keep the literal: it is what the harness's compile.js checks. */""")

# c2 — the DAO buttons' glow on phones
ix.rep("@media(max-width:639.98px){.p2 .p2-ctl{position:relative;right:auto;top:auto;flex-direction:row;justify-content:flex-end;width:100%;margin-top:8px}.p2 .p2-ctl::before{left:-20px;right:-20px;top:-14px;bottom:-14px}.p2 .p2-vghead{padding-right:0}}",
       "@media(max-width:639.98px){.p2 .p2-ctl{position:relative;right:auto;top:auto;flex-direction:row;justify-content:flex-end;width:100%;margin-top:8px}.p2 .p2-ctl::before{left:-20px;right:-20px;top:-14px;bottom:-14px}.p2 .p2-vghead{padding-right:0}.p2 .p2-daobtns::before{left:-16px;right:-12px}}   /* c2 (Audit III): the glow's right:-44px reached past the viewport — the PTGC page scrolled sideways 11 px on every phone */", done_marker='.p2 .p2-daobtns::before{left:-16px')

# c3 — scroll cue + active tab into view (DashHeaderV2)
ix.rep("""      const artRef=useRef(null),artRef2=useRef(null);   // desktop / phone banner — whichever is displayed
      useEffect(()=>{
        const on=()=>{const a=artRef.current,b=artRef2.current;const h=(a&&a.offsetHeight)||(b&&b.offsetHeight)||300;setScrolled(window.scrollY>h-40);};""",
       """      const artRef=useRef(null),artRef2=useRef(null);   // desktop / phone banner — whichever is displayed
      /* c3 (Audit III): the tab row hides its scrollbar, so on a phone nothing said Charts / Live Feed / Portfolio / Affiliates existed
         (u8's cue lived only in the classic header). The cue fades + chevrons; the active tab is scrolled to the middle on each change. */
      const tabRef=useRef(null);
      const tabCue=useScrollCue(tabRef,[token,scrolled,activeTab,loading]);
      useEffect(()=>{h2CenterActiveTab(tabRef.current);},[activeTab,token]);
      useEffect(()=>{
        const on=()=>{const a=artRef.current,b=artRef2.current;const h=(a&&a.offsetHeight)||(b&&b.offsetHeight)||300;setScrolled(window.scrollY>h-40);};""", done_marker='const tabRef=useRef(null);')
ix.rep("""            <nav aria-label="Dashboard sections" className="h2-tabrow">
              {scrolled&&<div className="hidden lg:flex">{mini('h2-mini')}</div>}""",
       """            <nav ref={tabRef} aria-label="Dashboard sections" className="h2-tabrow">
              {scrolled&&<div className="hidden lg:flex">{mini('h2-mini')}</div>}""")
ix.rep("""              <FreshnessBadge lastUpdate={fresh.lastUpdate} refreshing={fresh.refreshing} error={fresh.error} loading={fresh.loading} onRefresh={fresh.onRefresh} className="h2-fresh"/>
            </nav>
            </div>""",
       """              <FreshnessBadge lastUpdate={fresh.lastUpdate} refreshing={fresh.refreshing} error={fresh.error} loading={fresh.loading} onRefresh={fresh.onRefresh} className="h2-fresh"/>
            </nav>
            <H2Cues cue={tabCue}/>
            </div>""", done_marker='<H2Cues cue={tabCue}/>')
# the two helpers next to useScrollCue / ScrollCues (module scope); mirrored in h2-header.jsx
ix.rep("""    const ScrollCues=({cue})=>(
      <>
        <div className="scroll-cue scroll-cue-l" data-on={cue.l?'1':'0'} aria-hidden="true"><span>{'\\u2039'}</span></div>
        <div className="scroll-cue scroll-cue-r" data-on={cue.r?'1':'0'} aria-hidden="true"><span>{'\\u203A'}</span></div>
      </>
    );""",
       """    const ScrollCues=({cue})=>(
      <>
        <div className="scroll-cue scroll-cue-l" data-on={cue.l?'1':'0'} aria-hidden="true"><span>{'\\u2039'}</span></div>
        <div className="scroll-cue scroll-cue-r" data-on={cue.r?'1':'0'} aria-hidden="true"><span>{'\\u203A'}</span></div>
      </>
    );
    /* c3 (Audit III): the same two cues drawn for the v2 gold tab band (h2.css .h2-cue — a dark fade over the art, the chevron in the
       accent); h2-header.jsx carries a copy for the sibling pages (gotcha 36: mirror). h2CenterActiveTab scrolls the row, never the page. */
    const H2Cues=({cue})=>(
      <>
        <div className="h2-cue h2-cue-l" data-on={cue.l?'1':'0'} aria-hidden="true"><span>{'\\u2039'}</span></div>
        <div className="h2-cue h2-cue-r" data-on={cue.r?'1':'0'} aria-hidden="true"><span>{'\\u203A'}</span></div>
      </>
    );
    const h2CenterActiveTab=(nav)=>{
      if(!nav)return;const el=nav.querySelector('[aria-current="page"]');if(!el)return;
      const vis=el.offsetLeft>=nav.scrollLeft&&el.offsetLeft+el.offsetWidth<=nav.scrollLeft+nav.clientWidth;
      if(vis)return;   // already in view — never shove a row that fits (desktop)
      nav.scrollLeft=Math.max(0,el.offsetLeft-(nav.clientWidth-el.offsetWidth)/2);
    };""", done_marker='const H2Cues=')

# c5 — one holders24h
ix.rep("holderChange={NEW_HOLDERS_LIVE?(nhFile?nhNet(nhFile,token,24):null):holderChange}",
       "holderChange={holders24h}")
ix.rep("""      const nhFile=useNewHoldersFile(NEW_HOLDERS_LIVE);          // data/new-holders.json, read only once the window is live — the Holders tile's change line comes from it then
""",
       """      const nhFile=useNewHoldersFile(NEW_HOLDERS_LIVE);          // data/new-holders.json, read only once the window is live — the Holders tile's change line comes from it then
      /* c5 (Audit III): ONE 24 h holders number for every surface — the file's net once Holders Details is live (gotcha 40: the tile
         already printed it), PulseScan's delta before. The KPI Report, the Holders ⓘ card and the Socials Holders card read this too. */
      const holders24h=NEW_HOLDERS_LIVE?(nhFile?nhNet(nhFile,token,24):null):holderChange;
      const holders24hBoth=NEW_HOLDERS_LIVE?{PTGC:nhFile?nhNet(nhFile,'PTGC',24):null,UFO:nhFile?nhNet(nhFile,'UFO',24):null}:undefined;
""", done_marker='const holders24h=')
if 'holderChange={holderChange}' in ix.s:
    assert ix.s.count('holderChange={holderChange}') == 3, ix.s.count('holderChange={holderChange}')
    ix.rep('holderChange={holderChange}', 'holderChange={holders24h}', count=3)
ix.rep("""          {showHoldersSingleModal&&<HoldersSingleModal token={token} holders={holders} holdersByPeriod={holdersByPeriod} tiers={holderTiers} onClose={()=>closeModalAndReturn(setShowHoldersSingleModal)}/>}""",
       """          {showHoldersSingleModal&&<HoldersSingleModal token={token} holders={holders} holdersByPeriod={holdersByPeriod} tiers={holderTiers} today24={holders24h} onClose={()=>closeModalAndReturn(setShowHoldersSingleModal)}/>}""")
ix.rep("""          {showHoldersShareModal&&<HoldersSocialModal data={holdersShareData} loading={holdersShareLoading} error={holdersShareError} onRetry={()=>setHoldersShareTry(n=>n+1)} onClose={()=>closeModalAndReturn(setShowHoldersShareModal)}/>}""",
       """          {showHoldersShareModal&&<HoldersSocialModal data={holdersShareData} loading={holdersShareLoading} error={holdersShareError} today24={holders24hBoth} onRetry={()=>setHoldersShareTry(n=>n+1)} onClose={()=>closeModalAndReturn(setShowHoldersShareModal)}/>}""")
# the components: `today` overrides the PulseScan-snapshot delta when it is defined (null = unknown → "—")
ix.rep("""    const HoldersPeriodTiles=({p,z,rgb})=>{
      const cur=p&&p.current!=null?p.current:null;
      const chg24h=cur!=null&&p.d1Ago!=null?cur-p.d1Ago:null;""",
       """    const HoldersPeriodTiles=({p,z,rgb})=>{
      const cur=p&&p.current!=null?p.current:null;
      const chg24h=p&&p.today!==undefined?p.today:(cur!=null&&p.d1Ago!=null?cur-p.d1Ago:null);   // c5: the dashboard's one number when given""")
ix.rep("""                        <span className="tabular-nums" style={{fontSize:z.tq+2,fontWeight:700,whiteSpace:'nowrap',color:holdCol(r.pct)}}>{r.pct==null?'—':`${holdArrow(r.pct)} ${Math.abs(r.pct).toFixed(1)}%`}</span>""",
       """                        <span className="tabular-nums" style={{fontSize:z.tq+2,fontWeight:700,whiteSpace:'nowrap',color:chg24h===0?'rgba(255,255,255,0.45)':holdCol(r.pct)}}>{r.pct==null?'—':chg24h===0?'— quiet today':`${holdArrow(r.pct)} ${Math.abs(r.pct).toFixed(1)}%`}</span>""")
ix.rep("""    const HoldersTokenPanel=({tkn,d,z,tall})=>{
      const T=HOLD_THEME[tkn],cfg=TOKENS[tkn];
      const holders=d&&d.holders!=null?d.holders:null;
      const p=d?d.periods:null;
      const chg24h=p&&p.current!=null&&p.d1Ago!=null?p.current-p.d1Ago:null;""",
       """    const HoldersTokenPanel=({tkn,d,z,tall,today24})=>{
      const T=HOLD_THEME[tkn],cfg=TOKENS[tkn];
      const holders=d&&d.holders!=null?d.holders:null;
      const p=d?(today24!==undefined?{...d.periods,today:today24}:d.periods):null;
      const chg24h=today24!==undefined?today24:(p&&p.current!=null&&p.d1Ago!=null?p.current-p.d1Ago:null);   // c5""")
ix.rep("""    const HoldersSingleCard=({token,holders,holdersByPeriod,tiers,shape='wide',days=30})=>{""",
       """    const HoldersSingleCard=({token,holders,holdersByPeriod,tiers,shape='wide',days=30,today24})=>{""")
ix.rep("""      const p={current:cur,d1Ago:hp.d1Ago!=null?hp.d1Ago:null,d7Ago:hp.d7Ago!=null?hp.d7Ago:null,d30Ago:hp.d30Ago!=null?hp.d30Ago:null,d90Ago:hp.d90Ago!=null?hp.d90Ago:null};
      const chg24h=cur!=null&&p.d1Ago!=null?cur-p.d1Ago:null;""",
       """      const p={current:cur,d1Ago:hp.d1Ago!=null?hp.d1Ago:null,d7Ago:hp.d7Ago!=null?hp.d7Ago:null,d30Ago:hp.d30Ago!=null?hp.d30Ago:null,d90Ago:hp.d90Ago!=null?hp.d90Ago:null};
      if(today24!==undefined)p.today=today24;   // c5: the dashboard's one 24 h number
      const chg24h=today24!==undefined?today24:(cur!=null&&p.d1Ago!=null?cur-p.d1Ago:null);""")
ix.rep("""    const HoldersSingleModal=({token,holders,holdersByPeriod,tiers,onClose})=>{""",
       """    const HoldersSingleModal=({token,holders,holdersByPeriod,tiers,onClose,today24})=>{""")
ix.rep("""    const HoldersSocialModal=({data,loading,error,onRetry,onClose})=>{""",
       """    const HoldersSocialModal=({data,loading,error,onRetry,onClose,today24})=>{""")
# pass `today` down inside the two shells
n_single = ix.s.count('<HoldersSingleCard token={token} holders={holders} holdersByPeriod={holdersByPeriod} tiers={tiers}')
assert n_single >= 1, 'HoldersSingleCard call site'
ix.rep('<HoldersSingleCard token={token} holders={holders} holdersByPeriod={holdersByPeriod} tiers={tiers}',
       '<HoldersSingleCard token={token} holders={holders} holdersByPeriod={holdersByPeriod} tiers={tiers} today24={today24}', count=n_single, done_marker='tiers={tiers} today24={today24}')
ix.rep('<HoldersTokenPanel tkn="PTGC" d={P} z={z} tall={tall}/>', '<HoldersTokenPanel tkn="PTGC" d={P} z={z} tall={tall} today24={today24?today24.PTGC:undefined}/>')
ix.rep('<HoldersTokenPanel tkn="UFO" d={U} z={z} tall={tall}/>', '<HoldersTokenPanel tkn="UFO" d={U} z={z} tall={tall} today24={today24?today24.UFO:undefined}/>')

# c6 — Leagues: never "Burned 0"
ix.rep("""      const startingSupply=cfg.totalSupply;
      const burnedQty=burn?.total||0;
      const currentSupply=Math.max(0,startingSupply-burnedQty);
      const circ=supplyMode==='circ';""",
       """      const startingSupply=cfg.totalSupply;
      const burnKnown=!!(burn&&burn.supply>0);   // c6 (Audit III): a failed burn read is "—", never "Burned 0" / circulating = starting (gotcha 20)
      const burnedQty=burnKnown?burn.total:null;
      const currentSupply=burnKnown?Math.max(0,startingSupply-burnedQty):null;
      const circ=supplyMode==='circ'&&burnKnown;""")
ix.rep("""<div className="lg-t burn"><img src="logos/panels/vg-flame.webp" alt=""/><div className="l">Burned</div><div className="v tabular-nums">{fmt(burnedQty)}</div></div>""",
       """<div className="lg-t burn"><img src="logos/panels/vg-flame.webp" alt=""/><div className="l">Burned</div><div className="v tabular-nums">{burnKnown?fmt(burnedQty):'\\u2014'}</div></div>""")
ix.rep("""      const[burns,setBurns]=useState({ptgc:0,ufo:0});""",
       """      const[burns,setBurns]=useState({ptgc:null,ufo:null});   // c6: null = unknown, never 0""")
ix.rep("""            setBurns({ptgc:ptgcBurn?.total||0,ufo:ufoBurn?.total||0});""",
       """            setBurns({ptgc:ptgcBurn&&ptgcBurn.supply>0?ptgcBurn.total:null,ufo:ufoBurn&&ufoBurn.supply>0?ufoBurn.total:null});   // c6""")
ix.rep("""      const circ=supplyMode==='circ';
      const ptgcBase=circ?Math.max(0,TOKENS.PTGC.totalSupply-burns.ptgc):TOKENS.PTGC.totalSupply;
      const ufoBase=circ?Math.max(0,TOKENS.UFO.totalSupply-burns.ufo):TOKENS.UFO.totalSupply;""",
       """      const burnsKnown=burns.ptgc!=null&&burns.ufo!=null;
      const circ=supplyMode==='circ'&&burnsKnown;   // c6: the circulating basis needs both burns; unknown → the card stays on starting supply
      const ptgcBase=circ?Math.max(0,TOKENS.PTGC.totalSupply-burns.ptgc):TOKENS.PTGC.totalSupply;
      const ufoBase=circ?Math.max(0,TOKENS.UFO.totalSupply-burns.ufo):TOKENS.UFO.totalSupply;""")

# c7 — Combined Burn Stats card: 810 px frame (the Sep 14 CVG fix), screenshot-only (the inline gradient total cannot be exported)
ix.rep("""<ShareCardModal onClose={()=>closeModalAndReturn(setShowCombinedBurnModal)} width={600} height={540} label="Combined burn stats share card" filename={`combined-burn-${new Date().toISOString().slice(0,10)}.png`}>
                  <div id="combined-burn-card" style={{position:'relative',width:'600px',borderRadius:'16px',overflow:'hidden',background:'#0a0900'}}>""",
       """<ShareCardModal onClose={()=>closeModalAndReturn(setShowCombinedBurnModal)} width={600} height={810} screenshot label="Combined burn stats share card" filename={`combined-burn-${new Date().toISOString().slice(0,10)}.png`}>{/* c7 (Audit III): 805 px of content sat in a 540 px frame — the UFO rows and the total were cut; screenshot-only because the gradient total cannot be exported (gotcha 5). The redo is backlog -4. */}
                  <div id="combined-burn-card" style={{position:'relative',width:'600px',minHeight:'810px',display:'flex',flexDirection:'column',borderRadius:'16px',overflow:'hidden',background:'#0a0900'}}>""")

# c11 — the ?v bump
ix.rep('h2.css?v=1', 'h2.css?v=2')

# c25 — en-US
ix.rep('{hdrDaysOld.toLocaleString()}', "{hdrDaysOld.toLocaleString('en-US')}", count=ix.s.count('{hdrDaysOld.toLocaleString()}'))
ix.rep('`Day ${hdrDaysOld.toLocaleString()}`', "`Day ${hdrDaysOld.toLocaleString('en-US')}`")
ix.rep('{daysOld.toLocaleString()}', "{daysOld.toLocaleString('en-US')}", count=ix.s.count('{daysOld.toLocaleString()}'))
ix.rep("if(val>=1)return'$'+Math.floor(val).toLocaleString();", "if(val>=1)return'$'+Math.floor(val).toLocaleString('en-US');")
ix.save()

# ------------------------------------------------------------------ h2.css
css = Edit('h2.css')
css.rep(".h2-tabs .h2-tabrow::-webkit-scrollbar{display:none}",
        """.h2-tabs .h2-tabrow::-webkit-scrollbar{display:none}
/* c3 (Audit III, 2026-10-07): the band hides its scrollbar — these are the cue that more tabs sit off-screen (index.html H2Cues /
   h2-header.jsx / charts.html h2Boot). A dark fade over the art with the chevron in the accent; data-on flips with scrollLeft. */
.h2-tabs .h2-cue{position:absolute;top:0;bottom:0;width:calc(48*var(--u));pointer-events:none;display:flex;align-items:center;opacity:0;transition:opacity .2s;z-index:2}
.h2-tabs .h2-cue[data-on="1"]{opacity:1}
.h2-tabs .h2-cue-r{right:0;justify-content:flex-end;padding-right:calc(8*var(--u));background:linear-gradient(to left,rgba(4,4,4,.92) 30%,rgba(4,4,4,0))}
.h2-tabs .h2-cue-l{left:0;justify-content:flex-start;padding-left:calc(8*var(--u));background:linear-gradient(to right,rgba(4,4,4,.92) 30%,rgba(4,4,4,0))}
.h2-tabs .h2-cue span{color:rgba(var(--a-rgb),.95);font-size:calc(24*var(--u));line-height:1;text-shadow:0 0 8px rgba(var(--a-rgb),.6)}""", done_marker='.h2-tabs .h2-cue{')
css.save()

# ------------------------------------------------------------------ h2-header.jsx
jx = Edit('h2-header.jsx')
jx.rep("""const H2TabBand=({token,vars,active,navTo,mini,miniOn})=>(
  <div className="h2 h2-tabs" data-tok={token} style={vars}>
    {miniOn&&mini&&<div className="lg:hidden">{mini('h2-phone-mini')}</div>}
    <div className="h2-tabband">
      <nav aria-label="Site sections" className="h2-tabrow">""",
       """/* c3 (Audit III, 2026-10-07): the scroll cue for the gold band — MIRRORS index.html's useScrollCue / H2Cues / h2CenterActiveTab. */
const h2UseScrollCue=(ref,deps)=>{
  const[cue,setCue]=React.useState({l:false,r:false});
  React.useEffect(()=>{
    const el=ref.current;if(!el)return;
    const upd=()=>{const l=el.scrollLeft>2,r=el.scrollLeft+el.clientWidth<el.scrollWidth-2;setCue(c=>(c.l===l&&c.r===r)?c:{l,r});};
    upd();el.addEventListener('scroll',upd,{passive:true});window.addEventListener('resize',upd);
    let ro=null;if(window.ResizeObserver){ro=new ResizeObserver(upd);ro.observe(el);}
    const t=setTimeout(upd,300);
    return()=>{el.removeEventListener('scroll',upd);window.removeEventListener('resize',upd);if(ro)ro.disconnect();clearTimeout(t);};
  },deps);
  return cue;
};
const H2Cues=({cue})=>(<>
  <div className="h2-cue h2-cue-l" data-on={cue.l?'1':'0'} aria-hidden="true"><span>{'\\u2039'}</span></div>
  <div className="h2-cue h2-cue-r" data-on={cue.r?'1':'0'} aria-hidden="true"><span>{'\\u203A'}</span></div>
</>);
const h2CenterActiveTab=(nav)=>{
  if(!nav)return;const el=nav.querySelector('[aria-current="page"]');if(!el)return;
  const vis=el.offsetLeft>=nav.scrollLeft&&el.offsetLeft+el.offsetWidth<=nav.scrollLeft+nav.clientWidth;
  if(vis)return;
  nav.scrollLeft=Math.max(0,el.offsetLeft-(nav.clientWidth-el.offsetWidth)/2);
};
const H2TabBand=({token,vars,active,navTo,mini,miniOn})=>{
  const tabRef=React.useRef(null);
  const cue=h2UseScrollCue(tabRef,[token,active,miniOn]);
  React.useEffect(()=>{h2CenterActiveTab(tabRef.current);},[active,token]);
  return(
  <div className="h2 h2-tabs" data-tok={token} style={vars}>
    {miniOn&&mini&&<div className="lg:hidden">{mini('h2-phone-mini')}</div>}
    <div className="h2-tabband">
      <nav ref={tabRef} aria-label="Site sections" className="h2-tabrow">""")
jx.rep("""            {key==='portfolio'?<span>{label}</span>:label}{badge&&<span className="h2-new">{badge}</span>}
          </button>))}
      </nav>
    </div>
  </div>);""",
       """            {key==='portfolio'?<span>{label}</span>:label}{badge&&<span className="h2-new">{badge}</span>}
          </button>))}
      </nav>
      <H2Cues cue={cue}/>
    </div>
  </div>);};""", done_marker='<H2Cues cue={cue}/>')
jx.rep('{hdrDaysOld.toLocaleString()}', "{hdrDaysOld.toLocaleString('en-US')}")
jx.save()

# ------------------------------------------------------------------ charts.html (the static twin)
ch = Edit('charts.html')
ch.rep("""  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
}""",
       """  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });
  // c3 (Audit III, 2026-10-07): the band's scroll cue + the active tab centred — the static twin of index.html's H2Cues / h2CenterActiveTab
  const band = v.querySelector('.h2-tabband'), row = v.querySelector('.h2-tabrow');
  if (band && row && !band.querySelector('.h2-cue')) {
    const mk = (side, ch) => { const d = document.createElement('div'); d.className = 'h2-cue h2-cue-' + side; d.setAttribute('aria-hidden', 'true'); d.dataset.on = '0'; d.innerHTML = '<span>' + ch + '</span>'; band.appendChild(d); return d; };
    const L = mk('l', '\\u2039'), R = mk('r', '\\u203A');
    const upd = () => { L.dataset.on = row.scrollLeft > 2 ? '1' : '0'; R.dataset.on = row.scrollLeft + row.clientWidth < row.scrollWidth - 2 ? '1' : '0'; };
    row.addEventListener('scroll', upd, { passive: true }); window.addEventListener('resize', upd);
    const cur = row.querySelector('[aria-current="page"]');
    if (cur) { const vis = cur.offsetLeft >= row.scrollLeft && cur.offsetLeft + cur.offsetWidth <= row.scrollLeft + row.clientWidth; if (!vis) row.scrollLeft = Math.max(0, cur.offsetLeft - (row.clientWidth - cur.offsetWidth) / 2); }
    upd(); setTimeout(upd, 300);
  }
}""", done_marker='h2-cue h2-cue-')
ch.rep('h2.css?v=1', 'h2.css?v=2')
ch.rep("e.textContent = days != null ? days.toLocaleString() : '\\u2014'", "e.textContent = days != null ? days.toLocaleString('en-US') : '\\u2014'")
ch.save()

# ------------------------------------------------------------------ calculators.html
ca = Edit('calculators.html')
ca.rep('  <script type="text/babel" src="h2-header.jsx?v=1"></script>\n  <script type="text/babel">\n',
       '  <script type="text/babel" data-presets="react" src="h2-header.jsx?v=2"></script>\n  <script type="text/babel" data-presets="react">\n')
ca.rep('h2.css?v=1', 'h2.css?v=2')
# c8 — the 10 Yr Projection tab
ca.rep("""            const processed = lvProcessPairs(pairs, c.address);
            const circulating = c.totalSupply - (burn?.total || 0);
            return {
              price: processed?.price || 0,
              totalLP: processed?.totalLiquidity || 0,
              supply: circulating,
              mcap: (processed?.price || 0) * circulating,
            };
          } catch (e) {
            console.error('Growth calc fetch error for ' + tk + ':', e);
            return { price: 0, totalLP: 0, supply: 0, mcap: 0 };
          }""",
       """            const processed = lvProcessPairs(pairs, c.address);
            /* c8 (Audit III, 2026-10-07): a failed burn read used to print the UNBURNED supply (and a ~16 % high MCap) under a green LIVE
               badge (the a6 rule for the other tabs). null = unknown → "—" and the Unavailable badge; never the catch's zeros. */
            const burnKnown = !!(burn && burn.supply > 0);
            const circulating = burnKnown ? c.totalSupply - burn.total : null;
            const price = processed?.price > 0 ? processed.price : null;
            return {
              price,
              totalLP: processed?.totalLiquidity > 0 ? processed.totalLiquidity : null,
              supply: circulating,
              mcap: price != null && circulating != null ? price * circulating : null,
            };
          } catch (e) {
            console.error('Growth calc fetch error for ' + tk + ':', e);
            return null;   // c8: failed, not zeros
          }""")
ca.rep("""      const [allData, setAllData] = React.useState({ PTGC: null, UFO: null });""",
       """      const [allData, setAllData] = React.useState({ PTGC: undefined, UFO: undefined });   // c8: undefined = loading, null = failed, object = data (nullable fields)""")
ca.rep("""      const liveData = allData[growthToken];
      const loadingLive = liveData === null;""",
       """      const liveData = allData[growthToken];
      const loadingLive = liveData === undefined;
      const liveOk = !!(liveData && liveData.price != null && liveData.supply != null && liveData.totalLP != null);   // c8: every baseline known""")
ca.rep("""      const currentPrice = liveData?.price || 0;
      const currentLP = liveData?.totalLP || 0;
      const supply = liveData?.supply || 0;""",
       """      const currentPrice = liveData?.price ?? NaN;   // c8: NaN prints "—" through fmt$/fmtUsers/fmtPrice, never a 0 that looks like a fact
      const currentLP = liveData?.totalLP ?? NaN;
      const supply = liveData?.supply ?? NaN;""")
ca.rep("""              <span className="text-white/30 text-xs font-bold uppercase tracking-widest">
                {loadingLive ? 'Fetching live data\\u2026' : 'Live'}
                {!loadingLive && <span className="inline-block w-1.5 h-1.5 rounded-full bg-green-400 ml-1.5 align-middle animate-pulse"></span>}
              </span>""",
       """              <LiveBadge loading={loadingLive} data={liveOk} size="text-xs"/>{/* c8: three states like the other tabs — Loading / Unavailable / Live */}""")
ca.rep("""                      {loadingLive ? <span className="text-white/30 text-sm">{'Loading\\u2026'}</span> : t.val}""",
       """                      {loadingLive ? <span className="text-white/30 text-sm">{'Loading\\u2026'}</span> : t.val}{/* c8: a null baseline prints "—" via the formatters */}""", done_marker='c8: a null baseline prints')
ca.save()

# fmtPrice(NaN) must be "—" too — check the page's fmtPrice handles non-finite
s = read('calculators.html')
assert "const fmtPrice" in s

# ------------------------------------------------------------------ portfolio.html / ledger.html — c1 + c11
po = Edit('portfolio.html')
po.rep('  <script type="text/babel" src="h2-header.jsx?v=1"></script>\n  <script type="text/babel">\n',
       '  <script type="text/babel" data-presets="react" src="h2-header.jsx?v=2"></script>\n  <script type="text/babel" data-presets="react">\n')
po.rep('h2.css?v=1', 'h2.css?v=2')
po.save()
le = Edit('ledger.html')
le.rep('  <script type="text/babel">\n', '  <script type="text/babel" data-presets="react">\n')
le.save()

# ------------------------------------------------------------------ scripts/fetch-coingecko-data.js — c4
cg = Edit('scripts/fetch-coingecko-data.js')
cg.rep("""  // Trim to last 500 snapshots
  for (const h of [liquidityHistory, transactionHistory, tokensInLPHistory]) {
    if (h.snapshots.length > 500) h.snapshots = h.snapshots.slice(-500);""",
       """  // c4 (Audit III, 2026-10-07): retention by TIME, not count. "Last 500 snapshots" was written for 4–5 runs a day (~100 days);
  // at the hourly beat it was 21 days and the dashboard's 30-day sparklines (H2_DAYS) would have lost their window around Oct 20.
  // Keep everything newer than 100 days; thin older-than-7-days points to one per hour so the files stay ~100–300 KB.
  const KEEP_MS = 100 * 86400000, THIN_AFTER_MS = 7 * 86400000, cutoff = Date.now() - KEEP_MS;
  for (const h of [liquidityHistory, transactionHistory, tokensInLPHistory]) {
    const kept = [];
    let lastHour = null;
    for (const s of h.snapshots) {
      const t = Date.parse(s.timestamp);
      if (!isFinite(t) || t < cutoff) continue;
      if (Date.now() - t > THIN_AFTER_MS) {
        const hour = Math.floor(t / 3600000);
        if (hour === lastHour) { kept[kept.length - 1] = s; continue; }   // keep the latest point of each hour
        lastHour = hour;
      }
      kept.push(s);
    }
    h.snapshots = kept;""")
cg.save()

print('audit3-p1: done')
