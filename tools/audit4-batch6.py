#!/usr/bin/env python3
"""Audit IV batch 6 (2026-10-23): the medium items e32–e41 (Shaka: "do them all"). Idempotent, from the repo root:
    python3 tools/audit4-batch6.py        (twice: the second run must print "0 edit(s)")
then `cd tools/harness && npm run css` if tw.css changed. See handover/HANDOVER.md "Current state" for what each part does.
"""
import sys; sys.exit('audit4-batch6.py: applied 2026-10-23, then superseded by later edits. Re-running it would write a partial edit to tools/pf-v2/PortfolioV2.jsx and then fail. Kept for its history only (tools/README.md).')   # Audit VI item 5 (2026-10-28)
import hashlib, re, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new and new in s: return
    if not new and old not in s: return   # a deletion already done
    if s.count(old) != count:
        alt = ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in old)
        if s.count(alt) == count: old = alt
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
def cut(path, start, end, repl):
    """replace [start .. end) (end not included) with repl, once; skipped when start is gone"""
    global n
    s = open(path, encoding='utf-8').read()
    a = s.find(start)
    if a < 0: return
    b = s.index(end, a)
    open(path, 'w', encoding='utf-8').write(s[:a] + repl + s[b:]); n += 1

IX, PF, CA, CH, LE = 'index.html', 'portfolio.html', 'calculators.html', 'charts.html', 'ledger.html'
PV, PL, PR = 'tools/pf-v2/PortfolioV2.jsx', 'tools/pf-v2/PfLeagues.jsx', 'tools/pf-v2/PfRank.jsx'

# ============================== 6A — safety + correctness ==============================
# ---- e32: a portfolio code / the add box hold at most 50 wallets; labels 40 characters, groups 24 ----
edit(PF, '''    const sanitizeWallets=(list)=>{
      if(!Array.isArray(list))return{wallets:[],dropped:0};
      const seen=new Set();const wallets=[];let dropped=0;
      list.forEach(w=>{
        const address=w&&(typeof w==='object')?(w.address||w.a):null;
        if(!isValidAddr(address)||seen.has(address.toLowerCase())){dropped++;return;}
        seen.add(address.toLowerCase());
        wallets.push({address,name:typeof w.name==='string'?w.name:(typeof w.n==='string'?w.n:''),group:(typeof w.group==='string'&&w.group)||(typeof w.g==='string'&&w.g)||'Default'});
      });
      return{wallets,dropped};
    };''', '''    /* Audit IV e32 (2026-10-23): a pasted code (or the add box) holds at most PF_MAX_WALLETS — a crafted 2,000-wallet GRAY- code
       fired ~20,000 eth_calls on every visit (here, on calculators and in the Top 100 window) until the list was cleared.
       Labels 40 characters, groups 24. The SAVED list is never cut (nobody loses wallets they already have). */
    const PF_MAX_WALLETS=50,PF_NAME_MAX=40,PF_GROUP_MAX=24;
    const sanitizeWallets=(list,cap=false)=>{
      if(!Array.isArray(list))return{wallets:[],dropped:0,over:0};
      const seen=new Set();const wallets=[];let dropped=0,over=0;
      list.forEach(w=>{
        const address=w&&(typeof w==='object')?(w.address||w.a):null;
        if(!isValidAddr(address)||seen.has(address.toLowerCase())){dropped++;return;}
        seen.add(address.toLowerCase());
        if(cap&&wallets.length>=PF_MAX_WALLETS){over++;return;}
        const name=typeof w.name==='string'?w.name:(typeof w.n==='string'?w.n:''),group=(typeof w.group==='string'&&w.group)||(typeof w.g==='string'&&w.g)||'Default';
        wallets.push({address,name:cap?name.slice(0,PF_NAME_MAX):name,group:cap?group.slice(0,PF_GROUP_MAX):group});
      });
      return{wallets,dropped,over};
    };''')
edit(PF, '''        const data=JSON.parse(pfB64Dec(code.slice(5)));   // e7: UTF-8 first, old Latin-1 codes still read
        return sanitizeWallets(data);''', '''        const data=JSON.parse(pfB64Dec(code.slice(5)));   // e7: UTF-8 first, old Latin-1 codes still read
        return sanitizeWallets(data,true);   // e32: the first 50, labels cut to 40''')
edit(PF, '''        if(decoded.dropped)console.warn(`Load Code: ${decoded.dropped} entr${decoded.dropped===1?'y':'ies'} without a valid address skipped`);''',
         '''        if(decoded.dropped)console.warn(`Load Code: ${decoded.dropped} entr${decoded.dropped===1?'y':'ies'} without a valid address skipped`);
        /* e32: a code with more than 50 wallets says so once (amber) before it loads the first 50 */
        if(decoded.over&&codeError.indexOf('holds')<0){setCodeError(`This code holds ${decoded.wallets.length+decoded.over} wallets. A portfolio keeps up to ${PF_MAX_WALLETS} — press Load again to load the first ${PF_MAX_WALLETS}.`);return}''')
edit(PF, '''      const handleLoadCode=()=>{
        setCodeError('');''', '''      const handleLoadCode=()=>{
        if(codeError.indexOf('holds')<0)setCodeError('');   // e32: keep the "holds N wallets" note for the second press''')
edit(PF, '''{codeError&&<div className="text-red-400 text-base mb-3">{codeError}</div>}''',
         '''{codeError&&<div className={`${codeError.indexOf('holds')>=0?'text-amber-300':'text-red-400'} text-base mb-3`}>{codeError}</div>}''')
edit(PF, '''<input value={codeInput} onChange={e=>{setCodeInput(e.target.value);setLoadArmed(0)}}''', '''<input value={codeInput} onChange={e=>{setCodeInput(e.target.value);setLoadArmed(0);setCodeError('')}}''')
edit(PF, '''      const addWallet=()=>{
        const addr=inputAddr.trim();
        if(!addr||!/^0x[0-9a-fA-F]{40}$/.test(addr))return;
        if(wallets.find(w=>w.address.toLowerCase()===addr.toLowerCase()))return;
        const newWallet={address:addr,name:inputName.trim()||'',group:inputGroup||'Default'};''', '''      const addWallet=()=>{
        const addr=inputAddr.trim();
        if(!addr||!/^0x[0-9a-fA-F]{40}$/.test(addr))return;
        if(wallets.find(w=>w.address.toLowerCase()===addr.toLowerCase()))return;
        if(wallets.length>=PF_MAX_WALLETS)return;   // e32 (the add box says why)
        const newWallet={address:addr,name:inputName.trim().slice(0,PF_NAME_MAX)||'',group:inputGroup||'Default'};''')
edit(PV, '''        if(wallets.find(w=>w.address.toLowerCase()===a.toLowerCase())){setAddMsg('That wallet is already in your portfolio.');return;}''',
         '''        if(wallets.find(w=>w.address.toLowerCase()===a.toLowerCase())){setAddMsg('That wallet is already in your portfolio.');return;}
        if(wallets.length>=PF_MAX_WALLETS){setAddMsg(`A portfolio keeps up to ${PF_MAX_WALLETS} wallets — remove one first.`);return;}   // Audit IV e32''')
edit(PV, '''<input value={p.inputName} onChange={e=>p.setInputName(e.target.value)} placeholder="My Wallet" aria-label="Label (optional)"''',
         '''<input value={p.inputName} onChange={e=>p.setInputName(e.target.value)} maxLength={PF_NAME_MAX} placeholder="My Wallet" aria-label="Label (optional)"''')

# ---- e35: calculators + ledger get an error boundary (a render throw was a black page with no way back) ----
BOUNDARY = '''    /* Audit IV e35 (2026-10-23): an error boundary — React 18 unmounts the whole page on an uncaught render error; this keeps a
       card with Reload and the way back instead of a black page. (= portfolio's PortfolioBoundary, without its wallet reset) */
    class PageBoundary extends React.Component{
      constructor(p){super(p);this.state={error:null};}
      static getDerivedStateFromError(error){return{error};}
      componentDidCatch(error,info){console.error('Page render error:',error,info&&info.componentStack);}
      render(){
        if(!this.state.error)return this.props.children;
        const msg=String(this.state.error&&this.state.error.message||this.state.error);
        return(
          <div className="min-h-screen flex items-center justify-center p-6">
            <div role="alert" className="max-w-md w-full text-center bg-[#111]/80 border border-white/10 rounded-2xl p-8">
              <div className="text-lg text-[#D9CA5D] font-bold mb-2">Something went wrong</div>
              <p className="text-white/60 text-sm mb-1">This page hit an error while drawing.</p>
              <p className="text-white/35 text-xs font-mono break-all mb-6">{msg}</p>
              <div className="flex flex-wrap justify-center gap-3">
                <button onClick={()=>window.location.reload()} className="px-5 py-2 rounded-xl border border-[#D9CA5D]/40 text-[#D9CA5D] font-semibold hover:bg-white/5">Reload</button>
                <a href="./index.html" className="px-5 py-2 rounded-xl border border-white/15 text-white/70 hover:bg-white/5">Back to the dashboard</a>
              </div>
            </div>
          </div>
        );
      }
    }
'''
edit(CA, "    ReactDOM.createRoot(document.getElementById('root')).render(<CalculatorsPage/>);",
         BOUNDARY + "    ReactDOM.createRoot(document.getElementById('root')).render(<PageBoundary><CalculatorsPage/></PageBoundary>);")
edit(LE, "    ReactDOM.createRoot(document.getElementById('root')).render(<App />);",
         BOUNDARY + "    ReactDOM.createRoot(document.getElementById('root')).render(<PageBoundary><App /></PageBoundary>);")

# ---- e36: helper drift on the sibling pages ----
FMT_ABBR_NEW = "    const fmtAbbr=n=>{if(n==null||isNaN(n))return'\\u2014';const num=Number(n);if(!isFinite(num))return'\\u2014';if(num<0)return'-'+fmtAbbr(-num);if(num>=999.995e9)return(num/1e12).toFixed(2)+'T';if(num>=999.995e6)return(num/1e9).toFixed(2)+'B';if(num>=999.995e3)return(num/1e6).toFixed(2)+'M';if(num>=999.995)return(num/1e3).toFixed(2)+'K';return Math.floor(num).toLocaleString('en-US')};   // Audit IV e36: index's a67 bands (999,999 → 1.00M, never 1000.00K); negatives / Infinity"
FMT_ABBR_OLD = "    const fmtAbbr=n=>{if(n==null||isNaN(n))return'\\u2014';const num=Number(n);if(num>=1e12)return(num/1e12).toFixed(2)+'T';if(num>=1e9)return(num/1e9).toFixed(2)+'B';if(num>=1e6)return(num/1e6).toFixed(2)+'M';if(num>=1e3)return(num/1e3).toFixed(2)+'K';return Math.floor(num).toLocaleString('en-US')};"
edit(CA, FMT_ABBR_OLD, FMT_ABBR_NEW)
edit(PF, FMT_ABBR_OLD, FMT_ABBR_NEW)
edit(LE, '''      const num=Number(n);
      if(num>=1e12)return(num/1e12).toFixed(2)+'T';
      if(num>=1e9)return(num/1e9).toFixed(2)+'B';
      if(num>=1e6)return(num/1e6).toFixed(2)+'M';
      if(num>=1e3)return(num/1e3).toFixed(2)+'K';''', '''      const num=Number(n);
      if(!isFinite(num))return'\\u2014';
      if(num<0)return '-'+fmtAbbr(-num);   // Audit IV e36: negatives keep their unit
      /* Audit IV e36: index's a67 bands — the unit is picked AFTER the 2-dp rounding (999,999,999 → 1.00B, never 1000.00M) */
      if(num>=999.995e9)return(num/1e12).toFixed(2)+'T';
      if(num>=999.995e6)return(num/1e9).toFixed(2)+'B';
      if(num>=999.995e3)return(num/1e6).toFixed(2)+'M';
      if(num>=999.995)return(num/1e3).toFixed(2)+'K';''')
edit(CA, "    const getBurnC=(pct,min='Shell')=>{const r=[];let rem=pct;const minI=BURN_C.findIndex(c=>c.n===min);for(let i=0;i<BURN_C.length;i++){if(minI>=0&&i>minI)continue;const c=BURN_C[i];if(c.p>0&&rem>=c.p){const cnt=Math.floor(rem/c.p);if(cnt>0){r.push({...c,cnt});rem-=cnt*c.p}}}return r};",
         '''    /* Audit IV e36 = index's a42 creatureCount: 0.3/0.1 is 2.9999999999999996, so Math.floor gave one Shark too few and a tail
       of ×9s at every exact tenth. A quotient within a relative 1e-9 of a whole number IS that number. */
    const creatureCount=(value,unit)=>{
      if(!(unit>0)||!(value>0))return 0;
      const q=value/unit,r=Math.round(q);
      return Math.abs(q-r)<=1e-9*Math.max(1,Math.abs(r))?r:Math.floor(q);
    };
    const getBurnC=(pct,min='Shell')=>{const r=[];let rem=pct;const minI=BURN_C.findIndex(c=>c.n===min);for(let i=0;i<BURN_C.length;i++){if(minI>=0&&i>minI)continue;const c=BURN_C[i];if(c.p>0){const cnt=creatureCount(rem,c.p);if(cnt>0){r.push({...c,cnt});rem-=cnt*c.p}}}return r};''')
# a missing 24 h change is unknown ("—"), never +0.00 % (gotcha 20)
edit(CH, "    const chg = p.priceChange?.h24 ? parseFloat(p.priceChange.h24) : 0;",
         "    const chg = (p.priceChange && p.priceChange.h24 != null && !isNaN(parseFloat(p.priceChange.h24))) ? parseFloat(p.priceChange.h24) : null;   // Audit IV e36: missing = unknown (\"—\"), never +0.00 %")
edit(CH, '''  const up = chg >= 0;''', '''  const chgKnown = chg != null && !isNaN(chg), up = chgKnown && chg >= 0;   // e36''')
edit(CH, '''  chgEl.textContent = (up ? '\\u2191' : '\\u2193') + ' ' + Math.abs(chg).toFixed(2) + '%';
  chgEl.className = `mt-2 text-xs sm:text-sm lg:text-base font-bold tabular-nums ${up ? 'text-emerald-400' : 'text-rose-400'}`;''',
         '''  chgEl.textContent = chgKnown ? (up ? '\\u2191' : '\\u2193') + ' ' + Math.abs(chg).toFixed(2) + '%' : '\\u2014';
  chgEl.className = `mt-2 text-xs sm:text-sm lg:text-base font-bold tabular-nums ${!chgKnown ? 'text-white/30' : up ? 'text-emerald-400' : 'text-rose-400'}`;''')
edit(CA, "            change: pp.priceChange?.h24 || 0,", "            change: (pp.priceChange && pp.priceChange.h24 != null && !isNaN(parseFloat(pp.priceChange.h24))) ? parseFloat(pp.priceChange.h24) : null,   // e36: unknown, never 0")
# the UFO tile's reflections line after PulseScan failed
edit(PV, ":r7.state==='ok'?'waiting for your transactions\\u2026':'reading\\u2026'}",
         ":r7.state==='ok'?(txs&&txs.failed>0&&!(txs.flows&&txs.flows.length)?'PulseScan unreachable \\u2014 see Recent transactions':'waiting for your transactions\\u2026'):'reading\\u2026'}")   # e36
# the ledger's router strings were not the routers the treasury trades with (dead path today; the next classifier's trap)
for f in (LE, 'scripts/fetch-treasury-transactions.js'):
    edit(f, "'0x165c3410fc91b0e65d87e89d8bcadd85c9e6dbf1': 'PulseX V1 Router',", "'0x165c3410fc91ef562c50559f7d2289febed552d9': 'PulseX V1 Router',   // Audit IV e36: the real address (= ADDR.PULSEX_ROUTER)")
    edit(f, "'0x98bf93ebf5c380c0e6ae8e192a7e2ae08edacc3a': 'PulseX V2 Router',", "'0x98bf93ebf5c380c0e6ae8e192a7e2ae08edacc02': 'PulseX V2 Router',   // Audit IV e36: the real address")
edit(LE, "      '0x456548a9b56efbbd89ca0309edd17a9e20b04018': { symbol: 'UFO', name: 'UFO', decimals: 18 },",
         "      '0x456548a9b56efbbd89ca0309edd17a9e20b04018': { symbol: 'UFO', name: 'UFO (old contract)', decimals: 18 },\n      '0x49ed499433bee42dd34c169470fef2c8f9fae6e6': { symbol: 'UFO', name: 'UFO', decimals: 18 },   // Audit IV e36: the live contract")
# calculators' chain-read WETH pool is a constructor pool, not an RH core (index's flag)
s = open(CA, encoding='utf-8').read()
m = re.search(r"\{ address: [^}]*quoteSymbol: 'WETH'[^}]*isRHCore: true[^}]*\}", s)
if m:
    s = s[:m.start()] + m.group(0).replace('isRHCore: true', 'isRHCore: false') + ' /* Audit IV e36: index.html — WETH is a pool, not an RH core */' + s[m.end():]
    open(CA, 'w', encoding='utf-8').write(s); n += 1
# eight sequential calls to the RETIRED UFO LP-staking contract on every UFO load (props nothing reads) — gone
cut(CA, "          // Fetch total UFO share rate from LP staking contract\n          if(token==='UFO'){\n            try{\n              const ufoStakedRes=",
    "          await cgP;   // e14",
    "          /* Audit IV e36: the 1 + 7 sequential reads of the RETIRED UFO LP-staking contract (totalUFOShareRate / stakingPairs — nothing\n             reads either) are gone; on a hanging node they held the Rewards 7/30/90-day averages for up to 8 × 24 s. */\n          \n")

# ---- e40: rank / feed edges ----
edit(PL, "pfRanksP=fetch(PF_RANKS_URL,{cache:'no-cache'}).then(r=>r.ok?r.json():null).then(j=>j&&j.schema===1&&j.tokens&&j.tokens.PTGC&&j.tokens.UFO?j:null).catch(()=>null)\n        .then(j=>{if(!j)pfRanksP=null;return j;});return pfRanksP;};",
         "pfRanksP=fetch(PF_RANKS_URL,{cache:'no-cache'}).then(r=>r.ok?r.json():null).then(j=>j&&j.schema===1&&j.tokens&&j.tokens.PTGC&&j.tokens.UFO?j:null).catch(()=>null)\n        .then(j=>{if(!j){pfRanksP=null;return{failed:true};}return j;});return pfRanksP;};   // Audit IV e40: a failed read says so (it used to look like \"still loading\" for ever)")
edit(PL, "      useEffect(()=>{let live=true;const go=()=>pfRanksLoad().then(j=>{if(live&&j)setD(j);});go();",
         "      useEffect(()=>{let live=true;const go=()=>pfRanksLoad().then(j=>{if(live&&j)setD(prev=>j.failed&&prev&&!prev.failed?prev:j);});go();")   # e40: a failed 30-min re-read never replaces a good list
edit(PL, "      return d?{...d,stale,staleTok,readAt:{PTGC:rdAt('PTGC'),UFO:rdAt('UFO')}}:null;};",
         "      if(d&&d.failed)return{failed:true,stale:true,staleTok:{PTGC:true,UFO:true},tokens:{}};   // e40\n      return d?{...d,stale,staleTok,readAt:{PTGC:rdAt('PTGC'),UFO:rdAt('UFO')}}:null;};")
edit(PL, "    const PfRankRow=({tok,x,label,open})=>!x?null:",
         "    /* Audit IV e40: with no usable list the League box says why instead of the rank line vanishing (the Top 100 window's wording) */\n    const PfRankRow=({tok,x,label,open,note})=>!x?(note?<div className=\"pf2-rk3 na\" style={{fontSize:12,color:'rgba(255,255,255,.5)',padding:'6px 2px'}}>HOLDER RANK {'\\u2014'} {note}</div>:null):")
edit(PV, "      const rkOne=counted.length===1;", "      const rkOne=counted.length===1;\n      const rkNote=(tok,bal)=>!ranks||!(bal>0)?null:ranks.failed?'couldn\\u2019t load the holder list right now':(ranks.stale||(ranks.staleTok&&ranks.staleTok[tok]))?'the holder list is out of date, so ranks are hidden until the next refresh':null;   // Audit IV e40")
edit(PV, "rankRow={rkOne&&<PfRankRow tok=\"PTGC\" x={pfRank(ranks,'PTGC',pt.totalHolding,counted[0]&&counted[0].address)} open={()=>setRkWin('PTGC')}/>}",
         "rankRow={rkOne&&<PfRankRow tok=\"PTGC\" x={pfRank(ranks,'PTGC',pt.totalHolding,counted[0]&&counted[0].address)} note={rkNote('PTGC',pt.totalHolding)} open={()=>setRkWin('PTGC')}/>}")
s = open(PV, encoding='utf-8').read()
m = re.search(r"rankRow=\{rkOne&&<PfRankRow tok=\"UFO\" x=\{pfRank\(ranks,'UFO',uf\.balance[^}]*\)\}", s)
if m and 'note={rkNote(\'UFO\'' not in s:
    s = s[:m.end()] + " note={rkNote('UFO',uf.balance)}" + s[m.end():]
    open(PV, 'w', encoding='utf-8').write(s); n += 1
edit(PV, ":<div className=\"pf2-rkfoot\">Holder ranks are hidden: the holder list is out of date",
         ":ranks.failed?<div className=\"pf2-rkfoot\">Holder ranks are hidden: the holder list could not be loaded right now. They come back on the next try.</div>:<div className=\"pf2-rkfoot\">Holder ranks are hidden: the holder list is out of date")   # e40
# the rank window's COST TODAY / WHAT IT TAKES at the LIVE price, never the Moon Math one
s = open(PV, encoding='utf-8').read()
i = s.find('{rkWin&&<PfRankModal ')
if i >= 0:
    j = s.index('/>', i)
    seg = s[i:j]
    if 'prices={dp}' in seg:
        s = s[:i] + seg.replace('prices={dp}', 'prices={prices}') + s[j:]
        open(PV, 'w', encoding='utf-8').write(s); n += 1   # e40 (M-15)
# a stalled rank-history step: the days the index has not reached are UNKNOWN (-1), not "not holding" (0)
edit(PR, "if(full){const today=Math.floor((Date.now()-Date.parse(h.day0+'T00:00:00Z'))/86400e3);while(full.length<=today)full.push(0);full[today]=live?live.r:0;}",
         "if(full){const today=Math.floor((Date.now()-Date.parse(h.day0+'T00:00:00Z'))/86400e3);while(full.length<=today)full.push(-1);full[today]=live?live.r:0;}   // Audit IV e40: -1 = a day the history has not reached yet (a gap in the line, never \"not holding\")")
edit(PR, "history to {pfrFmt(pfrDate(h.day0,h.days-1),true)}</>:null}</div>",
         "<span style={h.days<Math.floor((Date.now()-Date.parse(h.day0+'T00:00:00Z'))/86400e3)-1?{color:'#E8C044'}:undefined}>history to {pfrFmt(pfrDate(h.day0,h.days-1),true)}</span></>:null}</div>")   # e40: amber when the daily rebuild is behind
# the feed's prices are the hour's price, not each trade's fill (HOW IT WORKS promised the latter)
edit(PV, "with the price each trade got.", "each valued at that hour{'\\u2019'}s price (not the exact fill price).")

# ---- e41: the dead header-preview gate and its SHA-256 of a human-chosen word ----
cut(IX, "    /* ===================== HEADER PREVIEW SWITCH (2026-09-30) =====================",
    "    /* ===================== DASHBOARD PANELS v2 — helpers (2026-09-30) =====================",
    "    /* (Audit IV e41, 2026-10-23: the header-preview switch — a secret URL word + password checked against single-round\n       SHA-256 hashes shipped in this public file — was deleted; v2 has been live for everyone since 2026-10-03. Treat that word\n       as burned: never reuse it anywhere.) */\n\n")
edit(IX, '''      const[hdrGate,setHdrGate]=useState(false);
      useEffect(()=>{let live=true;hdrPreviewRequested().then(y=>{if(live&&y)setHdrGate(true);});return()=>{live=false;};},[]);
''', '')
edit(IX, "{hdrGate&&<HeaderPreviewGate on={headerDesign==='v2'} onChange={setHeaderDesign} onClose={()=>setHdrGate(false)}/>}", "")


# ============================== 6B — phones + speed ==============================
# ---- e37: 320-px phones stop scrolling sideways; small tap targets get the 32-px hit box ----
edit(IX, '''              <div className="flex gap-2 items-center">
                <div className="bg-white/[0.03] border border-white/[0.07] rounded-lg px-2 flex items-center gap-1.5">''', '''              <div className="flex gap-2 items-center flex-wrap">{/* Audit IV e37: wraps on 320-px phones (the sort group ran to x=336 — the whole page scrolled sideways) */}
                <div className="bg-white/[0.03] border border-white/[0.07] rounded-lg px-2 flex items-center gap-1.5">''')
for f in (IX, 'h2-header.jsx'):
    edit(f, "hsp:Math.max(.9,Math.min(1.3,w/390))", "hsp:Math.max(.78,Math.min(1.3,w/390))")   # e37: floor = 305/390, so the KPI tiles fit a 320 phone (badges no longer on the label, the 📷 buttons no longer clipped)
edit(CH, "  .range-bar{display:flex;gap:3px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:3px}",
         "  .range-bar{display:flex;gap:3px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:10px;padding:3px}\n  @media(max-width:380px){.range-bar{flex-wrap:wrap}.range-btn{padding:7px 9px!important}#presetBtns{flex-wrap:wrap}.token-bar{flex-wrap:wrap}}   /* Audit IV e37: the range / preset rows were 386 px wide on a 320 phone */")
edit(CA, "      .cp-btn img{width:34px;height:34px}.cp-btn .ch{font-size:18px}\n    }\n",
         "      .cp-btn img{width:34px;height:34px}.cp-btn .ch{font-size:18px}\n    }\n    @media(max-width:360px){.cp-t{font-size:25px}}   /* Audit IV e37: \"Calculators\" ran 6 px past a 320 screen */\n")
edit(IX, "    .hc-dash:hover{background:var(--hc-c);color:#0b0b06;",
         "    @media(max-width:360px){.hc-dash{width:36px;padding:0;justify-content:center;gap:0}.hc-dash span{display:none}.hc-t2{font-size:1.9rem}}   /* Audit IV e37: on a 320 phone the BUY / SELL pill sat on the token name (now the ⇄ icon alone; its aria-label stays) and DASHBOARD lost a letter each side */\n    @media(max-width:360px){h3.font-orbitron.uppercase{letter-spacing:.04em!important;gap:6px!important}}   /* Audit IV e37: the panel titles pushed their 📷 share buttons out of the panel on a 320 phone (and the Token Allocation title row scrolled the page) */\n    .hc-dash:hover{background:var(--hc-c);color:#0b0b06;")
edit(IX, "    @media(min-width:901px) and (max-width:1199px){.sh-hd{gap:10px}",
         "    @media(max-width:360px){.sh-hd{gap:8px}.sh-hd>div{min-width:0}.sh-hd .lg{width:64px;height:64px}.sh-hd .lg2{width:70px;height:60px;transform:scale(1.25)}}   /* Audit IV e37: the Socials columns were 386 px in a 320 screen */\n    @media(min-width:901px) and (max-width:1199px){.sh-hd{gap:10px}")

# tap targets (V-8 / U-10): the 32-px invisible hit box (the .hit idea) on the controls that were still 12–26 px
edit('h2.css', ".h2-tb>button::before,.h2-tile .h2-tb>a::before{content:\"\";position:absolute;left:50%;top:50%;width:calc(100% + 6px);",
               ".h2-tb>button::before,.h2-tile .h2-tb>a::before{content:\"\";position:absolute;left:50%;top:50%;width:max(calc(100% + 6px),32px);")   # Audit IV e37: the tile badges were 14–27 px wide
edit('tools/pf-v2/pf2.css', ".pf2-ed{flex:none;border:0;background:transparent;color:rgba(255,255,255,.45);font-size:13px;line-height:1;padding:0;width:24px;height:24px;border-radius:7px}",
     ".pf2-ed{flex:none;border:0;background:transparent;color:rgba(255,255,255,.45);font-size:13px;line-height:1;padding:0;width:24px;height:24px;border-radius:7px}\n"
     "    .pf2-ed,.acts>button,.pf2-erw .x{position:relative}.pf2-ed::before,.acts>button::before,.pf2-erw .x::before,.pf2-ew .x::before{content:\"\";position:absolute;left:50%;top:50%;width:max(100%,32px);height:max(100%,32px);transform:translate(-50%,-50%)}   /* Audit IV e37: 32-px hit boxes on Edit / Remove and the windows' × (24 / 22 px before), layout unchanged */")
edit('tools/top100/t1.css', ".t1cp{border:0;background:none;padding:2px;color:rgba(255,255,255,.38);display:inline-flex}",
     ".t1cp{border:0;background:none;padding:2px;color:rgba(255,255,255,.38);display:inline-flex;position:relative}.t1cp::before{content:\"\";position:absolute;left:50%;top:50%;width:32px;height:32px;transform:translate(-50%,-50%)}   /* Audit IV e37: the copy button was 17×17 */")
# charts: the range / preset rows say which one is pressed (screen readers heard seven equal buttons)
edit(CH, '''`<button class="range-btn${range && r.days === range.days ? ' active' : ''}" data-d="${r.days}">${r.label}</button>`''',
         '''`<button class="range-btn${range && r.days === range.days ? ' active' : ''}" data-d="${r.days}" aria-pressed="${range && r.days === range.days ? 'true' : 'false'}">${r.label}</button>`''')   # e37
edit(CH, "    b.classList.toggle('active', match);\n  });\n}", "    b.classList.toggle('active', match);\n    b.setAttribute('aria-pressed', match ? 'true' : 'false');   // Audit IV e37\n  });\n}")
# ledger: the month pills say which is selected; the six category tiles are keyboard-reachable toggles
edit(LE, '''                  onClick={() => { setSelectedMonth(m.value); setFilter('all'); }}''', '''                  onClick={() => { setSelectedMonth(m.value); setFilter('all'); }}
                  aria-pressed={selectedMonth === m.value}''')
s = open(LE, encoding='utf-8').read()
k0 = 0
for key in ('ptgc_buy', 'burn', 'swap', 'lp_add', 'lp_remove', 'transfer'):
    old = f"""                <div 
                  onClick={{() => setFilter(filter === '{key}' ? 'all' : '{key}')}}"""
    new = f"""                <div role="button" tabIndex={{0}} aria-pressed={{filter === '{key}'}}
                  onKeyDown={{e => {{ if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); setFilter(filter === '{key}' ? 'all' : '{key}'); }} }}}}
                  onClick={{() => setFilter(filter === '{key}' ? 'all' : '{key}')}}"""
    if old in s: s = s.replace(old, new); k0 += 1
if k0: open(LE, 'w', encoding='utf-8').write(s); n += 1; print(f'  ledger: {k0} category tiles keyboard-reachable')
# Affiliates at 640–900: the Commission Log's last columns (Status) sit behind a sideways scroll with no cue → a right-edge fade
edit(IX, '''                <div className="hidden sm:block overflow-x-auto">
                  <table className="af-tbl w-full text-sm table-fixed min-w-[820px]">''', '''                <div className="hidden sm:block overflow-x-auto af-tblwrap">{/* Audit IV e37: the fade says "more to the right" on a portrait tablet */}
                  <table className="af-tbl w-full text-sm table-fixed min-w-[820px]">''')
edit(IX, "    @media(max-width:360px){.hc-dash{width:36px;", "    @media(min-width:640px) and (max-width:900px){.af-tblwrap{-webkit-mask-image:linear-gradient(90deg,#000 calc(100% - 56px),transparent);mask-image:linear-gradient(90deg,#000 calc(100% - 56px),transparent)}}   /* Audit IV e37 */\n    @media(max-width:360px){.hc-dash{width:36px;")


# ---- e38: performance / compatibility leftovers ----
import os, base64
# (P-7) real icon files: iOS ignores a data: apple-touch-icon (the home-screen icon became a screenshot); ledger had its own icon.
#        favicon.png = the 64 px icon the pages inlined; apple-touch-icon.png = 180 px from 07_Two_Color_Alien_Transparent.png
#        (committed with this batch — deploy.yml already copies *.png to the site).
assert os.path.exists('favicon.png') and os.path.exists('apple-touch-icon.png'), 'favicon.png / apple-touch-icon.png missing (committed with batch 6)'
for f in (IX, PF, CA, CH, LE):
    s = open(f, encoding='utf-8').read()
    s2 = re.sub(r'<link rel="icon" type="image/png" href="data:image/png;base64,[^"]+">', '<link rel="icon" type="image/png" href="favicon.png">', s)
    s2 = re.sub(r'<link rel="apple-touch-icon" href="data:image/png;base64,[^"]+">', '<link rel="apple-touch-icon" href="apple-touch-icon.png">   <!-- Audit IV e38: real files (iOS ignores a data: URI) -->', s2)
    if s2 != s: open(f, 'w', encoding='utf-8').write(s2); n += 1
edit('sitemap.xml', '''    <loc>https://ptgc-ufo.com/portfolio.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.5</priority>
  </url>''', '''    <loc>https://ptgc-ufo.com/portfolio.html</loc>
    <changefreq>weekly</changefreq>
    <priority>0.5</priority>
  </url>
  <url>
    <loc>https://ptgc-ufo.com/ledger.html</loc>
    <changefreq>daily</changefreq>
    <priority>0.4</priority>
  </url>''')
# (P-6) preconnect on the sibling pages + a <noscript> line on all five
PRE = ('  <link rel="preconnect" href="https://unpkg.com" crossorigin>   <!-- Audit IV e38: the CDN handshakes start with the HTML (index has had these) -->\n'
       '  <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>\n'
       '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
       '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n')
for f in (PF, CA, LE):
    edit(f, '  <link rel="stylesheet" href="tw.css?v=', PRE + '  <link rel="stylesheet" href="tw.css?v=')
edit(CH, '<link rel="stylesheet" href="tw.css?v=', PRE.replace('https://unpkg.com', 'https://cdnjs.cloudflare.com') + '<link rel="stylesheet" href="tw.css?v=')
NOSCRIPT = '<noscript><p style="margin:40px auto;max-width:30em;padding:0 16px;text-align:center;color:#E8C044;font:16px/1.5 system-ui,sans-serif">The Grays Dashboard needs JavaScript to read the chain. Please turn it on and reload.</p></noscript>   <!-- Audit IV e38 -->'
for f in (IX, PF, CA, CH, LE):
    s = open(f, encoding='utf-8').read()
    if '<noscript>' not in s:
        s = re.sub(r'(<body[^>]*>)', r'\1\n  ' + NOSCRIPT.replace('\\', '\\\\'), s, count=1)
        open(f, 'w', encoding='utf-8').write(s); n += 1
# (P-5) charts.html: html2canvas only when a share image is made (it was 46 KB gz on every visit)
s = open(CH, encoding='utf-8').read()
m = re.search(r'<script src="https://cdnjs\.cloudflare\.com/ajax/libs/html2canvas/1\.4\.1/html2canvas\.min\.js" integrity="(sha384-[^"]+)" crossorigin="anonymous"></script>\n', s)
if m:
    sri = m.group(1)
    s = s[:m.start()] + '<!-- Audit IV e38: html2canvas is loaded on demand by downloadShare() (loadH2C), not on every visit -->\n' + s[m.end():]
    s = s.replace('/* Download share image using html2canvas */\nasync function downloadShare(captureId) {',
                  "/* Audit IV e38: html2canvas on demand — same file, same SRI as the old <script> tag */\n"
                  "let _h2cP = null;\n"
                  "function loadH2C() {\n"
                  "  if (window.html2canvas) return Promise.resolve(window.html2canvas);\n"
                  "  if (_h2cP) return _h2cP;\n"
                  "  _h2cP = new Promise((res, rej) => { const el = document.createElement('script'); el.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';\n"
                  f"    el.integrity = '{sri}'; el.crossOrigin = 'anonymous'; el.async = true;\n"
                  "    el.onload = () => window.html2canvas ? res(window.html2canvas) : rej(new Error('html2canvas did not initialise'));\n"
                  "    el.onerror = () => { _h2cP = null; rej(new Error('could not load html2canvas')); }; document.head.appendChild(el); });\n"
                  "  return _h2cP;\n}\n"
                  "/* Download share image using html2canvas */\nasync function downloadShare(captureId) {", 1)
    s = s.replace('    const canvas = await html2canvas(el, {', '    const canvas = await (await loadH2C())(el, {', 1)
    open(CH, 'w', encoding='utf-8').write(s); n += 1
# (P-8) the KPI card's and the Top 100 window's phone layouts are container queries only — iOS ≤ 15.6 drew the desktop grid in a
#       390-px window. The same rules again for browsers WITHOUT container queries, on phone-width screens (where the containers
#       are the screen's width anyway).
def cq_fallback(path, head, width):
    global n
    s = open(path, encoding='utf-8').read()
    tag = f'/* Audit IV e38: no-container-query fallback for the @container (max-width:{width}px) block above */'
    if tag in s: return
    a = s.index(head); i = s.index('{', a) + 1; d = 1
    while d:
        if s[i] == '{': d += 1
        elif s[i] == '}': d -= 1
        i += 1
    body = s[s.index('{', a) + 1:i - 1]
    s = s[:i] + f'\n    {tag}\n    @supports not (container-type:inline-size){{@media (max-width:{width + 60}px){{{body}}}}}' + s[i:]
    open(path, 'w', encoding='utf-8').write(s); n += 1
cq_fallback(IX, '@container (max-width:540px){', 540)
cq_fallback('tools/top100/t1.css', '@container (max-width:560px){', 560)
# (P-9) WebKit: -webkit-backdrop-filter beside every unprefixed backdrop-filter in a CSS rule, and a vh fallback for 100dvh panels
def webkit_bf(path):
    global n
    s = open(path, encoding='utf-8').read()
    def rule(m):
        body = m.group(0)
        if '-webkit-backdrop-filter' in body or 'backdrop-filter:' not in body: return body
        return re.sub(r'(?<![-\w])backdrop-filter:([^;}]+)', r'-webkit-backdrop-filter:\1;backdrop-filter:\1', body)
    s2 = re.sub(r'\{[^{}]*\}', rule, s)
    if s2 != s: open(path, 'w', encoding='utf-8').write(s2); n += 1
for f in (IX, CA, CH, 'h2.css', 'tools/pf-v2/pf2.css'):
    webkit_bf(f)
edit(IX, "    .hc-dash svg{flex-shrink:0}", "    .hc-dash svg{flex-shrink:0}\n    @supports not (height:100dvh){.h-\\[100dvh\\]{height:100vh}}   /* Audit IV e38: iOS 15.0–15.3 have no dvh — the phone windows fall back to 100vh */")
# (P-10) two components declared inside render bodies (a fresh component type every render) — moved to module scope
s = open(IX, encoding='utf-8').read()
if 'const HvbSide=' not in s:
    a = s.index('      const Side=({cls,tag,pct,vol,n,gen,note,art})=>(')
    b = s.index('        </div>);\n', a) + len('        </div>);\n')
    side = s[a:b]
    s = s[:a] + s[b:]
    side = '\n'.join(l[2:] if l.startswith('  ') else l for l in side.split('\n')).replace('const Side=', 'const HvbSide=', 1)
    s = s.replace('    const HvbShareCard=({mode,file,P,feeRates})=>{', '    /* Audit IV e38: at module scope (it was declared inside HvbShareCard\'s render — gotcha 14) */\n' + side + '    const HvbShareCard=({mode,file,P,feeRates})=>{', 1)
    s = s.replace('<Side cls=', '<HvbSide cls=')
    a = s.index('      const Fold=({open,onToggle,title,count,color,children})=>(')
    b = s.index('      );\n', a) + len('      );\n')
    fold = s[a:b]
    s = s[:a] + s[b:]
    fold = '\n'.join(l[2:] if l.startswith('  ') else l for l in fold.split('\n')).replace('const Fold=', 'const VsFold=', 1)
    s = s.replace('    const VolumeSplitModal=({token:initial,feeRates,pairs,otherPairs,onClose})=>{', '    /* Audit IV e38: at module scope (it was declared inside the Humans vs Bots window\'s render — gotcha 14) */\n' + fold + '    const VolumeSplitModal=({token:initial,feeRates,pairs,otherPairs,onClose})=>{', 1)
    s = s.replace('<Fold open=', '<VsFold open=').replace('</Fold>', '</VsFold>')
    open(IX, 'w', encoding='utf-8').write(s); n += 1

# ---- e34: the client's call budget ----
# (R-9) the Live Feed stops polling while its tab is hidden (≈1,300 RPC calls an hour per open deck) and catches up on return
edit(IX, '''            const tick=async()=>{
              if(stop)return;
              try{
                const hr=await rpcFetch({jsonrpc:'2.0',method:'eth_blockNumber',params:[],id:1});''', '''            const tick=async()=>{
              if(stop)return;
              if(document.hidden){timer=setTimeout(tick,DECK_POLL_MS*5);return;}   // Audit IV e34: a background tab does not poll the chain (wakeDeck catches up)
              try{
                const hr=await rpcFetch({jsonrpc:'2.0',method:'eth_blockNumber',params:[],id:1});''')
edit(IX, '''            timer=setTimeout(tick,DECK_POLL_MS);
          }catch(e){console.warn('deck feed:',e);setStatus('chain read failed');}
        };
        run();
        return()=>{stop=true;if(timer)clearTimeout(timer);replayTimers.forEach(clearTimeout);};''', '''            timer=setTimeout(tick,DECK_POLL_MS);
            wakeDeck=()=>{if(!stop&&!document.hidden&&timer){clearTimeout(timer);timer=setTimeout(tick,300);}};   // e34: back in view → read now
          }catch(e){console.warn('deck feed:',e);setStatus('chain read failed');}
        };
        let wakeDeck=null;const onDeckVis=()=>{if(wakeDeck)wakeDeck();};
        document.addEventListener('visibilitychange',onDeckVis);
        run();
        return()=>{stop=true;if(timer)clearTimeout(timer);replayTimers.forEach(clearTimeout);document.removeEventListener('visibilitychange',onDeckVis);};''')
# (R-7) the six UFO fee getters are not read a second time 0.45 s after the boot read them
edit(IX, '''      if(fees){
        ufo.feeRate=fees.feeRate;
        ufo.feeBreakdown=fees.breakdown;''', '''      if(fees){
        ufo.feeRate=fees.feeRate;
        ufo.feeBreakdown=fees.breakdown;
        ufo.feesAt=Date.now();   // Audit IV e34: load() skips its own read for 5 min after this''')
edit(IX, '''            fetchUfoFees(cfg.address).then(f=>{
              if(f){cfg.feeRate=f.feeRate;cfg.feeBreakdown=f.breakdown;if(!loadCancelled)setFeeVersion(v=>v+1);}
            }).catch(()=>{});''', '''            if(!(cfg.feesAt&&Date.now()-cfg.feesAt<5*60e3))fetchUfoFees(cfg.address).then(f=>{   // e34: not again right after the boot read them
              if(f){cfg.feeRate=f.feeRate;cfg.feeBreakdown=f.breakdown;cfg.feesAt=Date.now();if(!loadCancelled)setFeeVersion(v=>v+1);}
            }).catch(()=>{});''')
# (R-8) portfolio: the saved wallets load three at a time (all at once was ≥140 parallel POSTs for 20 wallets), history batches of 40
edit(PF, '''        if(initialLoad||wallets.length===0)return;
        wallets.forEach(w=>{
          if(!portfolioData[w.address.toLowerCase()]){
            fetchWalletData(w.address);
          }
        });''', '''        if(initialLoad||wallets.length===0)return;
        /* Audit IV e34: three wallets at a time — a 20-wallet list fired ≥140 parallel POSTs at one public node on mount, the burst
           pattern that gets rate-limited (and then shows "Read failed"). */
        const todo=wallets.filter(w=>!portfolioData[w.address.toLowerCase()]).map(w=>w.address);
        let qi=0;const worker=async()=>{while(qi<todo.length){const a=todo[qi++];try{await fetchWalletData(a);}catch(e){}}};
        for(let k=0;k<Math.min(3,todo.length);k++)worker();''')
edit('tools/pf-v2/PfHistory.jsx', "PFH_RPC_TIMEOUT=20000,PFH_BATCH=80;", "PFH_RPC_TIMEOUT=20000,PFH_BATCH=40;   // Audit IV e34: 40 (the owner measured: batches of 100 failed, 40 worked; 80 sat between)")


# ============================== 6C — data pipeline ==============================
# ---- e33 (D-5): top-stakers reads balanceOf only for the 110 it publishes (it read 3,429 — 59 % of the step's calls) ----
TS = 'scripts/build-top-stakers.mjs'
edit(TS, '''    if (amt <= 0n) return;
    const bal = BigInt(await rpc('eth_call', [{ to: PTGC, data: SEL_BALANCE + pad(a) }, 'latest']));
    rows.push([a, amt, w(5), bal]);''', '''    if (amt <= 0n) return;
    rows.push([a, amt, w(5), null]);   // Audit IV e33: the wallet balance is read below for the published TOP_N only''')
edit(TS, '''rows.sort((x, y) => (y[1] > x[1] ? 1 : y[1] < x[1] ? -1 : (x[0] < y[0] ? -1 : 1)));
''', '''rows.sort((x, y) => (y[1] > x[1] ? 1 : y[1] < x[1] ? -1 : (x[0] < y[0] ? -1 : 1)));
/* Audit IV e33 (2026-10-23): `top` is the only place a wallet balance is published — read it for those TOP_N rows (110 calls,
   not one per staker). Same rule as before: an unread balance fails the step (the previous file stays). */
let balMiss = 0;
await pool(20, rows.slice(0, TOP_N), async r => {
  try { r[3] = BigInt(await rpc('eth_call', [{ to: PTGC, data: SEL_BALANCE + pad(r[0]) }, 'latest'])); } catch (e) { balMiss++; }
});
if (balMiss) { console.error(`top-stakers: ${balMiss} of the top ${TOP_N} wallet balances unread — previous file kept`); process.exit(1); }
''')
# ---- e33 (D-7): swap-volume re-prices the last 6 h of rows with this run's prices (they were priced from the previous run's
#      intraday file — charts-intraday lands later, in the other lane — and kept that USD for ever) ----
SV = 'scripts/build-swap-volume.mjs'
edit(SV, '''    .sort((x, y) => x[0] - y[0]);
  // round trips: a tx that buys a token in one pool and sells it in another (the arbitrage itself)''', '''    .sort((x, y) => x[0] - y[0]);
  /* Audit IV e33 (2026-10-23): re-price the rows of the last 6 h with this run's price file — the newest hours were priced from
     the PREVIOUS run's charts-intraday.json (it is rebuilt later in the other lane) and never revisited. Amounts are untouched. */
  { const cut = Date.now() - 6 * HOUR; let rp = 0;
    for (const r of rows) { if (r[0] < cut) continue;
      const pp = prices.PTGC ? prices.PTGC(r[0]) : null, pu = prices.UFO ? prices.UFO(r[0]) : null;
      if (r[6] != null && pp > 0) { const v = Number((r[6] * pp).toPrecision(6)); if (v !== r[7]) { r[7] = v; rp++; } }
      if (r[8] != null && pu > 0) { const v = Number((r[8] * pu).toPrecision(6)); if (v !== r[9]) { r[9] = v; rp++; } } }
    if (rp) console.log(`re-priced ${rp} value(s) from the last 6 h with this run's prices`); }
  // round trips: a tx that buys a token in one pool and sells it in another (the arbitrage itself)''')
# ---- e33 (D-9): rank-history runs once a day, right after 00:15 UTC, and writes nothing on a no-op run ----
RH = 'scripts/build-rank-history.mjs'
edit(RH, '''  st.cur = Object.fromEntries([...cur.entries()].map(([a, v]) => [a, v.toString()]));
  st.contracts = [...contracts]; st.eoa = [...eoa]; st.cursorDay = Object.keys(st.days).sort().pop(); st.generatedAt = new Date().toISOString();''', '''  /* Audit IV e33 (2026-10-23): a run that extended nothing writes nothing (it used to re-stamp and rewrite the 19 MB archive and
     ~4,000 index files), and the stamp is the CLOSE of the last archived day, not the run time — with the 24.5 h gate the step
     runs on the first hourly run after 00:15 UTC and extends exactly one day (the run-time stamp drifted 4 h earlier per cycle). */
  if (n === 0) { console.log(`${sym}: archive already current → ${lastDone} — nothing written`); return { unchanged: true }; }
  st.cur = Object.fromEntries([...cur.entries()].map(([a, v]) => [a, v.toString()]));
  st.contracts = [...contracts]; st.eoa = [...eoa]; st.cursorDay = Object.keys(st.days).sort().pop(); st.generatedAt = new Date((utc0(st.cursorDay) + 86400) * 1000).toISOString();''')
edit(RH, "  try { const st = await extend(sym); if (st) { index(sym, st); ok++; } }", "  try { const st = await extend(sym); if (st) { if (!st.unchanged) index(sym, st); ok++; } }   // e33: no index rebuild on a no-op")
edit('scripts/pipeline-run.mjs', "  'rank-history':    { run: 'scripts/build-rank-history.mjs',       gate: ['data/rank-index/PTGC/meta.json', 20] },",
     "  'rank-history':    { run: 'scripts/build-rank-history.mjs',       gate: ['data/rank-index/PTGC/meta.json', 24.5] },   // Audit IV e33: meta.generatedAt = the close of the last archived day → runs once a day after 00:15 UTC")

# ---- e39 (N-10): token-allocation's `staked` was the staking contract's own PTGC — the REWARD POOL (3.33 B), not what is staked
#      (187.46 B by totalStaked(); stakers keep their PTGC in their wallets). No page reads the field; renamed so nobody does. ----
TA = 'scripts/build-token-allocation.mjs'
edit(TA, "      staked: { amount: toTok(staked), pct: pct(staked) },", "      rewardPool: { amount: toTok(staked), pct: pct(staked) },   // Audit IV e39: balanceOf(staking contract) = the REWARD POOL; staked PTGC stays in the stakers' wallets (totalStaked() ≈ 187 B) — it was published as `staked`")

# the watchdog reads the step gates with a regex — a decimal gate (rank-history's 24.5) must parse, or the step would count as hourly
edit('scripts/pipeline-watchdog.mjs', r"""(?:,\s*gate:\s*\[\s*'[^']+',\s*(\d+)\s*\])?/g)) gates[m[1]] = m[2] ? +m[2] : 1;""",
     r"""(?:,\s*gate:\s*\[\s*'[^']+',\s*(\d+(?:\.\d+)?)\s*\])?/g)) gates[m[1]] = m[2] ? +m[2] : 1;   // Audit IV e33: decimal gates (24.5)""")

# tw.css drops the two utilities only the deleted header-preview gate used → `npm run css`, and the cache key moves on
for p in (IX, PF, CA, CH, LE):
    edit(p, 'href="tw.css?v=5"', 'href="tw.css?v=6"')
# h2.css (tile-badge hit boxes, -webkit-backdrop-filter) and h2-header.jsx (the phone scale floor) changed → their cache keys too
for p in (IX, PF, CA, CH):
    s = open(p, encoding='utf-8').read()
    if 'h2.css?v=3' in s: edit(p, 'h2.css?v=3', 'h2.css?v=4')
for p in (PF, CA):
    edit(p, 'h2-header.jsx?v=3', 'h2-header.jsx?v=4')
for cmd in ('tools/pf-v2.py', 'tools/top100.py'):
    out = subprocess.run([sys.executable, cmd], capture_output=True, text=True)
    if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
    print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-batch6: {n} edit(s), index {sha(IX)}, portfolio {sha(PF)}, calculators {sha(CA)}, charts {sha(CH)}, ledger {sha(LE)}')
