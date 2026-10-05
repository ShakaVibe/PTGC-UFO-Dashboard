#!/usr/bin/env python3
"""KPI Report v2 (2026-10-05, rounds 1–2): splice KpiCardV2 + the kp-* CSS into index.html, swap renderKPICard to it, widen the tab,
restore the Combined KPI modal (deleted by accident in 42f244912, 2026-09-29), add four explainers.
Run from the repo root on a clean index.html: python3 tools/kpi-v2.py  (idempotent — refuses to run twice)."""
import re,sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
p=root/'index.html'; s=p.read_text()
if 'const KpiCardV2=' in s: sys.exit('already applied')
css=(root/'tools/kpi-v2.css').read_text(); jsx=(root/'tools/kpi-v2.jsx').read_text()
def rep(old,new,count=1):
    global s
    n=s.count(old)
    assert n==count,(old[:70],n)
    s=s.replace(old,new)

# 1. CSS block before the LEAGUES block
rep('    /* LEAGUES (2026-10-04) — the holder-tiers modal',css+'    /* LEAGUES (2026-10-04) — the holder-tiers modal')
# 2. the v2 fire bar's selectors also match inside a KPI card
lines=s.split('\n'); n=0
for i,l in enumerate(lines):
    m=re.match(r'^(    )\.p2 \.p2-bar((?![a-z])[^,{]*)\{',l)
    if m:
        lines[i]=l.replace('.p2 .p2-bar'+m.group(2)+'{','.p2 .p2-bar'+m.group(2)+',.kp .p2-bar'+m.group(2)+'{',1); n+=1
assert n==8,n
s='\n'.join(lines)
# 3. the component above KPIContent
rep('    const KPIContent=({token,cfg,data,burn,burnPeriods,holders,holderChange,pls,burnHistoryCache,onClose,startWithBoth=false,startInTwitterMode=false,volumeByPeriod,valueGen7d})=>{',
    jsx+'    const KPIContent=({token,cfg,data,burn,burnPeriods,holders,holderChange,pls,burnHistoryCache,onClose,startWithBoth=false,startInTwitterMode=false,volumeByPeriod,valueGen7d})=>{')
# 4. renderKPICard → KpiCardV2 (the old markup goes; its maths live in the component)
a=s.index('      // Render a single KPI card\n      const renderKPICard=(t,c,d,b,bp,h,hChange,isMain=true)=>{')
b=s.index('      // Get other token\'s burn periods from the shared cache',a)
old=s[a:b]
assert old.rstrip().endswith('};') and old.count('const renderKPICard')==1
s=s[:a]+('      /* The card — KpiCardV2 (2026-10-05, Shaka\'s mock-up); the maths that used to live here moved into it unchanged. */\n'
         '      const renderKPICard=(t,c,d,b,bp,h,hChange,isMain=true)=><KpiCardV2 t={t} c={c} d={d} b={b} bp={bp} h={h} hChange={hChange} pls={pls} token={token} volumeByPeriod={volumeByPeriod} valueGen7d={valueGen7d} burnHistoryCache={burnHistoryCache}/>;\n      \n')+s[b:]
# 5. the side-by-side from lg (two 600 px cards need ~1224), the placeholders at the card's size
rep("<div className={`flex ${showBoth?'flex-col md:flex-row gap-6 justify-center items-start':'flex-col items-center'}`}>",
    "<div className={`w-full flex ${showBoth?'flex-col lg:flex-row gap-6 justify-center items-center lg:items-stretch':'flex-col items-center'}`}>")
rep('<div className="w-full max-w-md flex-shrink-0 h-[700px] rounded-2xl flex items-center justify-center" style={{background:\'#0d0d0d\',border:`2px solid ${token===\'PTGC\'?\'#7CFC00\':\'#D4AF37\'}40`}}>',
    '<div className="w-full max-w-[600px] flex-shrink-0 h-[700px] rounded-3xl flex items-center justify-center" style={{background:\'#0d0d0d\',border:`2px solid ${token===\'PTGC\'?\'#7CFC00\':\'#D4AF37\'}40`}}>')
rep('<div className="w-full max-w-md flex-shrink-0 h-[700px] rounded-2xl flex items-center justify-center" style={{background:\'#0d0d0d\',border:`2px solid ${token===\'PTGC\'?\'#7CFC00\':\'#D4AF37\'}40`}} role="status">',
    '<div className="w-full max-w-[600px] flex-shrink-0 h-[700px] rounded-3xl flex items-center justify-center" style={{background:\'#0d0d0d\',border:`2px solid ${token===\'PTGC\'?\'#7CFC00\':\'#D4AF37\'}40`}} role="status">')
# the tab's container and the Socials modal's
rep('            <div className="max-w-4xl mx-auto px-3 sm:px-6 py-2">\n              <KPIContent token={token}',
    '            <div className="max-w-[1264px] mx-auto px-3 sm:px-6 py-2">\n              <KPIContent token={token}')
rep('              <div className="relative z-10 w-full max-w-4xl flex flex-col items-center gap-3" onClick={e=>e.stopPropagation()}>\n                <KPIContent token={token}',
    '              <div className="relative z-10 w-full max-w-[1264px] flex flex-col items-center gap-3" onClick={e=>e.stopPropagation()}>\n                <KPIContent token={token}')
# 6. the Combined KPI modal (Socials → Combined → Combined KPI Report) — gone since 42f244912; back, as it was
combined='''          {/* Combined KPI Report (Socials → Combined): both tokens, straight into the share image. Deleted by accident in
              42f244912 (2026-09-29) — the row set showCombinedKPI and nothing read it; restored 2026-10-05. */}
          {showCombinedKPI&&(
            <Modal className="z-50 flex items-center justify-center p-4 overflow-auto" onClose={()=>{setShowCombinedKPI(false);if(socialReturn){gotoTab('social');setSocialReturn(false)}}} label="Combined KPI report">
              <div className="absolute inset-0 bg-black/85 backdrop-blur-md"></div>
              <button aria-label="Close"
                onClick={()=>{setShowCombinedKPI(false);if(socialReturn){gotoTab('social');setSocialReturn(false)}}}
                className="fixed top-8 right-20 w-10 h-10 rounded-full bg-gray-800/90 hover:bg-gray-700 flex items-center justify-center text-white text-xl font-bold transition-colors z-[60] border border-gray-600"
              >
                ✕
              </button>
              <div className="relative z-10 w-full max-w-[1264px] flex flex-col items-center gap-3" onClick={e=>e.stopPropagation()}>
                <KPIContent token={token} cfg={cfg} data={data} burn={burn} burnPeriods={burnPeriods} holders={holdersByPeriod?.current??holders} holderChange={holderChange} pls={pls} burnHistoryCache={burnHistoryCache} onClose={()=>{setShowCombinedKPI(false);if(socialReturn){gotoTab('social');setSocialReturn(false)}}} startWithBoth={true} startInTwitterMode={true} volumeByPeriod={volumeByPeriod} valueGen7d={valueGen7d}/>
              </div>
            </Modal>
          )}

          {/* KPI Report Modal (legacy - kept for direct link) */}'''
rep('          {/* KPI Report Modal (legacy - kept for direct link) */}',combined)
# 7. explainers for the card's ⓘs
expl='''      plsRatio:(token)=>(
        <p>The {token} price expressed in PLS: how many PLS one {token} is worth right now.</p>
      ),
      liquidity:(token)=>(
        <p>The USD value of every {token} liquidity pool added together — the depth behind the price. Deeper liquidity means a trade moves the price less.</p>
      ),
      liqMcap:(token)=>(
        <p>Liquidity as a share of market cap. A higher ratio means more of {token}'s value is backed by pool depth; a very low one means a small trade can move the price a lot.</p>
      ),
      volume24h:(token)=>(
        <p>USD traded across every {token} pool in the past 24 hours. The badge, when shown, compares it with the average day of the past week.</p>
      ),
      totalBurned:(token)=>(
        <p>{token} sent to the burn address since launch — gone from the supply for good — as tokens, as USD at today's price, and as a share of the starting supply. The creatures count that share in league tiers; the bar is the progress to the next whole Whale (1 %).</p>
      )
    };'''
rep('''      plsRatio:(token)=>(
        <p>The {token} price expressed in PLS: how many PLS one {token} is worth right now.</p>
      )
    };''',expl)
# 8. the camera goes (Shaka, 2026-10-05: "they can screen shot the images"); the controls in one centred row; ADD / REMOVE as
#    the SWITCH-style glass button
a=s.index('          {/* Twitter Screenshot Button - show when in dual view */}'); b=s.index('          {!showBoth?(',a)
s=s[:a]+('          {/* the controls, one centred row over the cards (2026-10-05) */}\n'
         '          <div className="flex justify-center items-center gap-3 mb-4">\n'
         '          {/* no 📷 here since 2026-10-05 (Shaka: "they can screen shot the images"); the 1200×675 share image is still what the Socials → Combined KPI Report row opens */}\n')+s[b:]
rep('''            <button onClick={()=>{loadOtherToken();setShowBoth(true);}} className="mb-3 px-5 py-2.5 rounded-lg font-bold text-sm flex items-center gap-2 hover:opacity-80 transition-opacity" style={{background:token==='PTGC'?'#7CFC00':'#D4AF37',color:'#000'}}>
              <span className="text-lg">+</span> Add {otherToken}
            </button>''',
'''            <button type="button" onClick={()=>{loadOtherToken();setShowBoth(true);}} aria-label={`Add the ${otherToken} card`} className={`kp-btn tap-h ${otherToken==='PTGC'?'gold':''}`}>
              <img src={otherCfg.logo} alt=""/><span>ADD {otherToken}</span>
            </button>''')
rep('''            <button onClick={()=>setShowBoth(false)} className="mb-3 px-5 py-2.5 rounded-lg font-bold text-sm flex items-center gap-2 hover:opacity-80 transition-opacity bg-gray-700 text-white">
              <span className="text-lg">−</span> Remove {otherToken}
            </button>
          )}
          
          {/* Side by side on desktop, stacked on mobile */}''',
'''            <button type="button" onClick={()=>setShowBoth(false)} aria-label={`Remove the ${otherToken} card`} className={`kp-btn off tap-h ${otherToken==='PTGC'?'gold':''}`}>
              <img src={otherCfg.logo} alt=""/><span>REMOVE {otherToken}</span>
            </button>
          )}
          </div>
          
          {/* Side by side on desktop, stacked on mobile */}''')
# 9. round 2 (same day): the compare card's UFO Value Generated from the hourly snapshot (no "7D EST" when the file is fresh),
#    the page's price map handed in, the pair stretched to one height
rep('    const KPIContent=({token,cfg,data,burn,burnPeriods,holders,holderChange,pls,burnHistoryCache,onClose,startWithBoth=false,startInTwitterMode=false,volumeByPeriod,valueGen7d})=>{',
    '    const KPIContent=({token,cfg,data,burn,burnPeriods,holders,holderChange,pls,burnHistoryCache,onClose,startWithBoth=false,startInTwitterMode=false,volumeByPeriod,valueGen7d,vgPrices})=>{')
rep('''      const[otherLoading,setOtherLoading]=useState(startWithBoth);
      ''','''      const[otherLoading,setOtherLoading]=useState(startWithBoth);
      const[otherVg,setOtherVg]=useState(null);   // UFO as the other token: {ufoSnap,plsxPx,wethPx} — the hourly delivered snapshot + the LP partner prices (2026-10-05)
      ''')
a=s.index("          if(otherToken==='UFO'){\n            const _fp=dexData?.pairs?.reduce("); b=s.index('          }',a)+len('          }')
s=s[:a]+'''          if(otherToken==='UFO'){
            /* the UFO card's Value Generated = the UFO dashboard's delivered figure (the hourly snapshot its panel reads) +
               the PLSX / WETH prices its LP buckets need — the Combined Value Generated card's 2026-09-29 route, not volume × fee.
               2026-10-05 round 3: the same snapshot's burnPeriods.UFO paints the burn box AT ONCE (the UFO panel's own route) —
               the first live look sat on "—" for the whole ~55-call chain scan; the scan now runs only when the file is not
               fresh (or failed), and replaces the snapshot's windows when it lands. */
            const _fp=dexData?.pairs?.reduce((m,pr)=>(pr.pairCreatedAt&&pr.pairCreatedAt<m)?pr.pairCreatedAt:m,Infinity);
            const scan=()=>fetchBurnPeriodsOnChain(otherCfg.address,otherCfg.decimals,(_fp&&isFinite(_fp))?_fp:UFO_LAUNCH_FALLBACK_MS).then(bp=>{if(bp)setOtherBurnPeriodsChain(bp);}).catch(()=>{});
            Promise.all([fetchValueGenSnapshot().catch(()=>null),Promise.all([PLSX_ADDRESS,UFO_WETH].map(a=>dsPairsFor(a).then(ps=>dsPriceOf(ps,a)).catch(()=>null)))])
              .then(([snap,lpPx])=>{
                const ufoSnap=snap&&snap.valid&&snap.ageMs<VALUE_GEN_INTERIM_MS?{delivered:snap.json.delivered,realizedFees:snap.json.realizedFees,at:Date.now()-snap.ageMs}:null;
                setOtherVg({ufoSnap,plsxPx:lpPx[0],wethPx:lpPx[1]});
                const bp=snap&&snap.valid&&snap.ageMs<BURN_HISTORY_MAX_AGE_MS&&snap.json.burnPeriods&&snap.json.burnPeriods.UFO;
                let painted=false;
                if(bp&&!bp.carriedForward&&typeof bp.h24==='number'&&typeof bp.d90==='number'){
                  setOtherBurnPeriodsChain(p=>p||{h12:bp.h12||0,h24:bp.h24,d7:bp.d7,d30:bp.d30,d90:bp.d90,sinceLaunch:!!bp.sinceLaunch,burnTxs:bp.burnTxs});   // never over a chain read that already landed
                  painted=true;
                }
                if(!(painted&&snap.ageMs<VALUE_GEN_STALE_MS))scan();
              }).catch(()=>{scan();});
          }'''+s[b:]
rep('volumeByPeriod={volumeByPeriod} valueGen7d={valueGen7d}/>','volumeByPeriod={volumeByPeriod} valueGen7d={valueGen7d} vgPrices={vgPricesNow}/>',3)
rep('      const renderKPICard=(t,c,d,b,bp,h,hChange,isMain=true)=><KpiCardV2 t={t} c={c} d={d} b={b} bp={bp} h={h} hChange={hChange} pls={pls} token={token} volumeByPeriod={volumeByPeriod} valueGen7d={valueGen7d} burnHistoryCache={burnHistoryCache}/>;',
    '      const renderKPICard=(t,c,d,b,bp,h,hChange,isMain=true)=><KpiCardV2 t={t} c={c} d={d} b={b} bp={bp} h={h} hChange={hChange} pls={pls} token={token} volumeByPeriod={volumeByPeriod} valueGen7d={valueGen7d} burnHistoryCache={burnHistoryCache} vgPrices={vgPrices} otherVg={otherVg}/>;')
p.write_text(s)
print('applied', len(s))
