#!/usr/bin/env python3
"""Audit IV batch 7 (2026-10-24, Shaka: "4 yes"): the P3s e42, e44, e45, e46 (e43 = his naming / gold call, later; e47 = the
platform budget numbers, nothing to build). Idempotent, from the repo root:
    python3 tools/audit4-batch7.py        (twice: the second run must print "0 edit(s)")
then  cd tools/harness && npm run css   (tw.css gains the max-h-[..dvh] utilities → ?v=7).
  e42 headings: an h1 on the dashboards (screen-reader only — the v2 title is art) and a "Skip to content" link; Calculators' and
      Charts' titles are h1; the KPI tab and the Live Feed get an h2; the five panel h3s are named by their title alone
      (they read "Total Supply Burned PTGC 📷").
  e44 Back closes the open window (index.html's Modal shell = every window there, and portfolio's PfModal) instead of
      leaving the page; the hash router is untouched.
  e45 a wallet list the browser refuses to save says so ("use GET CODE to keep a copy") instead of vanishing on reload; the
      history caches are dropped once to make room first.
  e46 the league bar never says "100.0% … need 1 ≈ $0"; fmtX keeps its "x" above 1,000; getWhaleProgress uses the a42
      epsilon; the KPI compare card's other-token Volume badge is computed (it read a field nothing writes); a Live Feed
      SELL on a known pool is valued gross of the fee like the receipt path; the dashboard footer has a gutter; the Leagues /
      disclaimer / Affiliates / Logos windows use dvh (+ a vh fallback); the "About the cost" ⓘ (Top 100, rank window)
      opens on a tap; the Volume tile's two badges stop touching "24H" at 1024–1199.
"""
import hashlib, re, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
def sub_all(path, old, new):
    global n
    s = open(path, encoding='utf-8').read()
    if old in s: open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

IX, PF, CA, CH, LD = 'index.html', 'portfolio.html', 'calculators.html', 'charts.html', 'ledger.html'
PL, PR, PV = 'tools/pf-v2/PfLeagues.jsx', 'tools/pf-v2/PfRank.jsx', 'tools/pf-v2/PortfolioV2.jsx'
T1J, T1C, H2 = 'tools/top100/t1.jsx', 'tools/top100/t1.css', 'h2.css'

# ============================ e42 — headings ============================
edit(H2, "@media(prefers-reduced-motion:reduce){.h2 .h2-buy::after",
     "/* Audit IV e42 (2026-10-24): screen-reader-only text and the skip link (all pages that load h2.css) */\n"
     ".g-sr{position:absolute!important;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}\n"
     ".g-skip{position:fixed;left:10px;top:-80px;z-index:10000;padding:9px 16px;border-radius:10px;background:#0b0d12;color:#F6E98A;border:1px solid rgba(242,211,91,.65);font:700 15px 'Rajdhani',sans-serif;letter-spacing:.04em;text-decoration:none}\n"
     ".g-skip:focus{top:10px;outline:2px solid #F6E98A;outline-offset:2px}\n"
     "@media(prefers-reduced-motion:reduce){.h2 .h2-buy::after")
edit(IX, """        <div className="min-h-screen">
""" + " "*10 + """
          {/* ===== HEADER v2 (2026-09-30)""", """        <div className="min-h-screen">
          {/* Audit IV e42: the page's h1 (the v2 title is art) and a skip link past the header + tab band to the content */}
          <a href="#" className="g-skip" onClick={e=>{e.preventDefault();const m=document.getElementById('g-main');if(m){try{m.focus({preventScroll:true});m.scrollIntoView({block:'start'});}catch(err){}}}}>Skip to content</a>
          <h1 className="g-sr">{token} dashboard {'\\u2014'} {activeTab==='kpi'?'KPI Report':activeTab==='social'?'Socials':'overview'}</h1>
""" + " "*10 + """
          {/* ===== HEADER v2 (2026-09-30)""")
edit(IX, "          {/* Dashboard Tab Content */}\n",
         "          {/* Dashboard Tab Content */}\n          <div id=\"g-main\" tabIndex={-1} className=\"outline-none\" style={{scrollMarginTop:72}}></div>   {/* e42: the skip link's target */}\n")
edit(IX, "          {activeTab==='kpi'&&loading&&<DashboardSkeleton token={token}/>}",
         "          {activeTab==='kpi'&&<h2 className=\"g-sr\">KPI Report</h2>}   {/* e42 */}\n          {activeTab==='kpi'&&loading&&<DashboardSkeleton token={token}/>}")
edit(IX, "              <div className={`font-orbitron text-base sm:text-xl font-black tracking-[0.14em] ${metal}`}>LIVE FEED</div>",
         "              <h2 className={`font-orbitron text-base sm:text-xl font-black tracking-[0.14em] ${metal}`}>LIVE FEED</h2>   {/* e42: was a div */}")
# the five panel titles: name each h3 by its title (aria-label), so "📷" / the logo's alt are not part of the heading
s = open(IX, encoding='utf-8').read()
H3 = '<h3 className="font-orbitron text-xs sm:text-sm uppercase tracking-[0.18em] text-white/85 flex items-center gap-2'
for title in ('Total Supply Burned', 'Value Generated', 'Token Allocation', 'DAO Treasury', 'PTGC Burned by UFO'):
    j = s.find(title, s.find('{/* Dashboard Tab Content */}'))
    while j >= 0:
        i = s.rfind(H3, 0, j)
        if i >= 0 and j - i < 700 and s.rfind('</h3>', i, j) < 0:
            break
        j = s.find(title, j + 1)
    assert j >= 0, title
    tag_end = s.index('>', i)
    if 'aria-label=' not in s[i:tag_end]:
        s = s[:tag_end] + f' aria-label="{title}"' + s[tag_end:]; n += 1
open(IX, 'w', encoding='utf-8').write(s)
for P in (CA, CH):
    edit(P, "  .cp-ttl h2{margin:0;line-height:1}" if P == CH else "    .cp-ttl h2{margin:0;line-height:1}",
            ("  " if P == CH else "    ") + ".cp-ttl h1,.cp-ttl h2{margin:0;line-height:1}")
edit(CA, '            <h2><span className="cp-t g">Grays</span><span className="cp-t w">Calculators</span></h2>',
         '            <h1><span className="cp-t g">Grays</span><span className="cp-t w">Calculators</span></h1>')
edit(CH, '      <h2><span class="cp-t g">Grays</span><span class="cp-t w">Charts</span></h2>',
         '      <h1><span class="cp-t g">Grays</span><span class="cp-t w">Charts</span></h1>')

# ============================ e44 — Back closes the window ============================
BACK_IX = """    /* Audit IV e44 (2026-10-24): the browser / phone Back closes the open window instead of leaving the page. Each window with
       an onClose pushes one same-URL history entry (state.grayModal); Back pops it → popstate → the TOP window closes. A window
       closed any other way (×, Escape, the backdrop) takes its own entry back off — only while that entry is still the current
       one (a window closed BY a navigation leaves it, and Back then just steps over it). The entries share the URL, so the hash
       router sees no hashchange. */
    const MODAL_HIST=[];let _histSkip=0;
    if(typeof window!=='undefined')window.addEventListener('popstate',()=>{if(_histSkip>0){_histSkip--;return;}const h=MODAL_HIST[MODAL_HIST.length-1];if(h){h.fromBack=true;h.close();}});
    const useBackCloses=(closeRef)=>{useEffect(()=>{if(!closeRef.current)return;const h={id:'gm'+Date.now().toString(36)+Math.random().toString(36).slice(2,6),fromBack:false,close:()=>{if(closeRef.current)closeRef.current();}};
      try{history.pushState(Object.assign({},history.state||{},{grayModal:h.id}),'');}catch(e){return;}
      MODAL_HIST.push(h);
      return()=>{const i=MODAL_HIST.indexOf(h);if(i>=0)MODAL_HIST.splice(i,1);if(!h.fromBack&&history.state&&history.state.grayModal===h.id){_histSkip++;history.back();}};},[]);};
"""
edit(IX, "    const FOCUSABLE='a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex=\"-1\"])';\n    const useDialog=(dlgRef,onClose)=>{\n      const closeRef=useRef(onClose);closeRef.current=onClose;\n",
         BACK_IX + "    const FOCUSABLE='a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex=\"-1\"])';\n    const useDialog=(dlgRef,onClose)=>{\n      const closeRef=useRef(onClose);closeRef.current=onClose;\n      useBackCloses(closeRef);   // e44\n")
BACK_PF = BACK_IX.replace("index.html's", "portfolio's").replace("const MODAL_HIST=[];let _histSkip=0;", "const PF_MODAL_HIST=[];let _pfHistSkip=0;") \
    .replace("MODAL_HIST", "PF_MODAL_HIST").replace("PF_PF_", "PF_").replace("_histSkip", "_pfHistSkip").replace("useBackCloses", "pfUseBackCloses").replace("'gm'", "'pm'")
edit(PL, "    const PfModal=({onClose,label,className='',children})=>{\n      const ref=React.useRef(null);const cl=React.useRef(onClose);cl.current=onClose;\n",
         BACK_PF + "    const PfModal=({onClose,label,className='',children})=>{\n      const ref=React.useRef(null);const cl=React.useRef(onClose);cl.current=onClose;\n      pfUseBackCloses(cl);   // e44 (runs before the scroll lock below, so the entry keeps the real scroll position)\n")

# ============================ e45 — a refused wallet-list save says so ============================
edit(PF, """      // Save to localStorage whenever wallets change
      useEffect(()=>{
        try{localStorage.setItem(PORTFOLIO_STORAGE_KEY,JSON.stringify(wallets));}catch{}
      },[wallets]);""", """      // Save to localStorage whenever wallets change
      /* Audit IV e45 (2026-10-24): a refused save (storage full / blocked / private mode) used to be silent and the wallets were
         gone after a reload. Now: drop the two history caches once (they rebuild from the chain) and try again; if it still
         fails the page says so and points at GET CODE. */
      const[walletSaveFailed,setWalletSaveFailed]=useState(false);
      useEffect(()=>{
        const put=()=>localStorage.setItem(PORTFOLIO_STORAGE_KEY,JSON.stringify(wallets));
        let ok=false;
        try{put();ok=true;}catch(e){try{localStorage.removeItem(PFH_LS);localStorage.removeItem(PFE_LS);put();ok=true;}catch(e2){}}
        setWalletSaveFailed(!ok&&wallets.length>0);
      },[wallets]);""")
edit(PF, "<PortfolioV2 updateWallet={updateWalletV2} wallets={wallets} ", "<PortfolioV2 updateWallet={updateWalletV2} walletSaveFailed={walletSaveFailed} wallets={wallets} ")
edit(PV, "          {addMsg&&<div className=\"pf2-addmsg\" role=\"alert\">{addMsg}</div>}",
         "          {addMsg&&<div className=\"pf2-addmsg\" role=\"alert\">{addMsg}</div>}\n"
         "          {p.walletSaveFailed&&<div className=\"pf2-addmsg\" role=\"alert\">This browser didn{'\\u2019'}t let the page save your wallet list (its storage is full or blocked), so it will be gone after a reload. Use GET CODE to keep a copy.</div>}   {/* Audit IV e45 */}")

# ============================ e46 — number / layout nits ============================
# (a) the league bar: never "100.0 %" while still below the line, never "≈ $0"
edit(PV, "      return{cur,next,pct:Math.max(0,Math.min(100,(balance-floor)/(ceil-floor)*100)),need:Math.max(0,ceil-balance)};",
         "      const need=Math.max(0,ceil-balance);   // e46: below the line = at most 99.9 % (it printed \"100.0% … need 1 ≈ $0\")\n"
         "      return{cur,next,pct:Math.max(0,Math.min(need>0?99.9:100,(balance-floor)/(ceil-floor)*100)),need};")
edit(PV, "<span>need <b>{pfAbbr(L.need)}</b>{cost!=null&&<> {'≈'} {fmtDollar(cost,0)}</>}</span>",
         "<span>need <b>{pfPassAmt(L.need)}</b>{cost!=null&&<> {'≈'} {cost<1?'< $1':fmtDollar(cost,0)}</>}</span>")
# (b) fmtX keeps the x above 1,000 (UFO's X'S TO A PENNY read "4.1K")
edit(IX, "if(n>=1e6)return(n/1e6).toFixed(1)+'M';if(n>=1e4)return(n/1e3).toFixed(0)+'K';if(n>=1e3)return(n/1e3).toFixed(1)+'K';return n>=100?",
         "if(n>=1e6)return(n/1e6).toFixed(1)+'Mx';if(n>=1e4)return(n/1e3).toFixed(0)+'Kx';if(n>=1e3)return(n/1e3).toFixed(1)+'Kx';return n>=100?")
edit(IX, "const fmtX=(x)=>{if(!x)return null;if(x>=1e5)return Math.round(x/1000)+'K';if(x>=1e3)return(x/1e3).toFixed(1)+'K';",
         "const fmtX=(x)=>{if(!x)return null;if(x>=1e5)return Math.round(x/1000)+'Kx';if(x>=1e3)return(x/1e3).toFixed(1)+'Kx';")
# (c) getWhaleProgress with the a42 epsilon
edit(IX, "    const getWhaleProgress=pct=>({whales:Math.floor(pct),progress:(pct-Math.floor(pct))*100});",
         "    const getWhaleProgress=pct=>{const w=creatureCount(pct,1);return{whales:w,progress:Math.max(0,(pct-w)*100)};};   // e46: the a42 epsilon (4.9999999 % is 5 whales)")
# (d) KPI compare card: the other token's Volume badge, computed as on the main card
edit(IX, "        :(burnHistoryCache?.[t]?.changes?.volume24h??null);",
         "        :(()=>{const v24=d?.vol||0;const avg=(vol7dFromCache(t)||0)/7;return(v24>0&&avg>0)?((v24-avg)/avg)*100:null;})();   // e46: was changes.volume24h, a field no file writes")
# (e) Live Feed: a SELL on a known pool, gross of the transfer fee (the pool receives amount × (1 − fee))
edit(IX, "          const amt=tokIn+tokOut;if(!(amt>0))return null;\n          const side=tokOut>=tokIn?'BUY':'SELL';    // token leaving the pool = someone bought it",
         "          const side=tokOut>=tokIn?'BUY':'SELL';    // token leaving the pool = someone bought it\n"
         "          const amt=side==='SELL'&&st.fee>0&&st.fee<1?tokIn/(1-st.fee)+tokOut:tokIn+tokOut;if(!(amt>0))return null;   // e46: a sell is what the seller SENT (the pool gets it net of the fee) — as resolveViaReceipt")
# (f) the dashboard footer gets the page's gutter
edit(IX, '          <footer className="text-center py-4 border-t border-white/10 mt-8"><p className="text-white/30 text-xs">',
         '          <footer className="text-center py-4 px-4 border-t border-white/10 mt-8"><p className="text-white/30 text-xs">')
# (g) windows in dvh, with the vh fallback for iOS 15.0–15.3
for a, b in (('max-h-[90vh]', 'max-h-[90dvh]'), ('max-h-[92vh]', 'max-h-[92dvh]'), ('max-h-[80vh]', 'max-h-[80dvh]')):
    sub_all(IX, a, b); sub_all(PL, a, b)
edit(IX, "    @supports not (height:100dvh){.h-\\[100dvh\\]{height:100vh}}",
         "    @supports not (height:100dvh){.h-\\[100dvh\\]{height:100vh}.max-h-\\[92dvh\\]{max-height:92vh}.max-h-\\[90dvh\\]{max-height:90vh}.max-h-\\[80dvh\\]{max-height:80vh}}   /* + e46: the Leagues / disclaimer / Affiliates / Logos windows */")
PF2C = 'tools/pf-v2/pf2.css'
s = open(PF2C, encoding='utf-8').read()
if 'max-h-\\[92dvh\\]{max-height:92vh}' not in s:
    open(PF2C, 'w', encoding='utf-8').write(s.rstrip('\n') + "\n    @supports not (height:100dvh){.max-h-\\[92dvh\\]{max-height:92vh}}   /* Audit IV e46: the Leagues window on iOS 15.0–15.3 */\n"); n += 1
# (h) the "About the cost" ⓘ opens on a tap (Top 100 + the rank window), like InfoTip
edit(T1J, 'const T1Cost=()=>(<span className="t1ii" tabIndex={0} aria-label="About the cost">i<span className="tip" role="tooltip">',
          'const T1Cost=()=>{const[o,setO]=useState(false);return(<button type="button" className={`t1ii${o?\' open\':\'\'}`} aria-label="About the cost" aria-expanded={o} onClick={e=>{e.stopPropagation();setO(v=>!v);}} onBlur={()=>setO(false)}>i<span className="tip" role="tooltip">')
edit(T1J, "higher.</span></span>);", "higher.</span></button>);};   {/* e46: a button that toggles (was hover / focus only) */}".replace("   {/* e46: a button that toggles (was hover / focus only) */}", "   // e46: a tap toggles it (was hover / focus only)"))
edit(T1C, "    .t1ii:hover .tip,.t1ii:focus .tip{display:block}",
          "    @media(hover:hover){.t1ii:hover .tip{display:block}}\n    .t1ii.open .tip{display:block}\n    button.t1ii{background:transparent;padding:0;margin:0}   /* e46: a button now — a tap toggles it; hover only with a mouse (a sticky :hover / kept focus held it open on phones) */")
edit(PR, "      const[want,setWant]=useState('');", "      const[want,setWant]=useState('');\n      const[iiOpen,setIiOpen]=useState(false);   // e46: the cost ⓘ opens on a tap")
edit(PR, '<span className="ii" tabIndex="0" aria-label="About the cost">i<span className="tip" role="tooltip">',
         '<button type="button" className={`ii${iiOpen?\' open\':\'\'}`} aria-label="About the cost" aria-expanded={iiOpen} onClick={e=>{e.stopPropagation();setIiOpen(o=>!o);}} onBlur={()=>setIiOpen(false)}>i<span className="tip" role="tooltip">')
edit(PR, "higher.</span></span></div>", "higher.</span></button></div>")
edit(PF2C, ".pf2-rkw .ii:hover .tip,.pf2-rkw .ii:focus .tip,.pf2-rkw .ii:focus-within .tip{display:block}",
           "@media(hover:hover){.pf2-rkw .ii:hover .tip{display:block}}.pf2-rkw .ii.open .tip{display:block}.pf2-rkw button.ii{padding:0;margin:0}")
# (i) the Volume tile's two badges (ⓘ + bot) touched "24H" at 1024–1199
edit(H2, "@media(min-width:1024px){.h2-tabs{--u:calc(var(--hsd,.665)*.0625rem)}",
     "/* Audit IV e46 / V-12 (2026-10-24): a tile with TWO badges (Volume: ⓘ + bot) — at 1024–1199 the label's 12 px floor ran into them */\n"
     "@media(min-width:1024px) and (max-width:1199.98px){.h2-tile:has(.h2-tb .h2-hd) .h2-tl{font-size:max(calc(22*var(--u)),.7rem);letter-spacing:0}}\n"
     "@media(min-width:1024px){.h2-tabs{--u:calc(var(--hsd,.665)*.0625rem)}")

# ============================ splice + cache keys ============================
for cmd in ('tools/pf-v2.py', 'tools/top100.py'):
    out = subprocess.run([sys.executable, cmd], capture_output=True, text=True)
    if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
    print('  ' + out.stdout.strip().splitlines()[-1])
for p in (IX, CA, CH, PF):
    edit(p, 'href="h2.css?v=4"', 'href="h2.css?v=5"')
# tw.css gains the max-h-[..dvh] utilities (`cd tools/harness && npm run css`) → its cache key moves on
for p in (IX, CA, CH, PF, LD):
    edit(p, 'href="tw.css?v=6"', 'href="tw.css?v=7"')

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-batch7: {n} edit(s), index {sha(IX)}, portfolio {sha(PF)}, calculators {sha(CA)}, charts {sha(CH)}, h2.css {sha(H2)}')
