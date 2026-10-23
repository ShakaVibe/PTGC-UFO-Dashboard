#!/usr/bin/env python3
"""Audit IV batch 4 (2026-10-23): e14 + e15 + e16. Idempotent, from the repo root:
    python3 tools/audit4-batch4.py        (twice: the second run must print "0 edit(s)")

e14  No page hangs on a stalled fetch any more.
     (a) portfolio.html: the header quotes (quoteOf / usdOf) get an 8 s timeout, and the wallet reads no longer wait for the
         prices — `initialLoad` clears at once, the header's skeleton follows its own `pricesLoading`.
     (b) index.html: every repo data read (`fetch(X,DATA_FETCH)`) goes through `dataFetch` (20 s abort), and PTGC's first paint
         no longer awaits the six history files — its burn periods are seeded when they land (UFO already worked that way).
     (c) calculators.html: the two DexScreener token endpoints in fetchDex / lvFetchTokenPairs and the Moon Math core read use
         the page's own dsJson (8 s, one retry); the coingecko file has a 15 s abort and is no longer awaited before the
         price round (only the PTGC volume windows read it, after first paint).
e15  index.html: the browser's value-generated fallback scans Mint logs only on the three pools the UFO contract mints into
     (WPLS / PLSX / WETH — every mint in data/value-generated.json is on those three), not all seven: ~864 → ~552 eth_getLogs
     per visit while the file is stale, identical numbers. ?debug=1 keeps all seven (its swap reconciliation reads them).
e16  portfolio.html + calculators.html: index.html's a41 RPC pool verbatim (30 s cooldown per failed endpoint, a -32005 /
     rate-limit answer rotates, `{result:null,transport:true}` when nothing answered) and portfolio's getLogsRange stops
     halving on a transport failure (it made 7× the calls against a dead node, ~21 min per wallet of "scanning the chain…").
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    if s.count(old) != count:
        alt = ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in old)
        if s.count(alt) == count: old = alt
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

IX, PF, CA = 'index.html', 'portfolio.html', 'calculators.html'

# ---------------- e16 — the a41 pool into portfolio + calculators ----------------
ix = open(IX, encoding='utf-8').read()
a = ix.index('    let _rpcIdx=0,_rpcSince=0;')
END = "      return{result:null,transport:true,message:(lastErr&&lastErr.message)||'all endpoints failed'};\n    };\n"
POOL = ix[a:ix.index(END, a) + len(END)]
for f in (PF, CA):
    s = open(f, encoding='utf-8').read()
    if 'RPC_COOLDOWN_MS' in s: continue
    a = s.index('    let _rpcIdx=0,_rpcSince=0;')
    OLD_END = '      return{result:null};\n    };\n'
    b = s.index(OLD_END, a) + len(OLD_END)
    s = s[:a] + '    /* Audit IV e16 (2026-10-23): index.html\'s a41 pool, verbatim — cooldown, -32005 rotation, `transport` flag. */\n' + POOL + s[b:]
    open(f, 'w', encoding='utf-8').write(s); n += 1
edit(PF, '''      const msg=(r&&r.error&&r.error.message)||'no result field';
      if(depth<6&&(b-a)>250){''', '''      const msg=(r&&r.transport&&('transport: '+r.message))||(r&&r.error&&r.error.message)||'no result field';
      /* Audit IV e16 (a41, ported): only a real RPC answer can mean "range too big". When the pool never got through, halving
         is 7× the calls against a dead or hanging node — fail now; the scan queue's Retry handles it. */
      if(r&&r.transport){lastLogError=`eth_getLogs failed (blocks ${a}-${b}): ${msg}`;console.warn(lastLogError);return null;}
      if(depth<6&&(b-a)>250){''')

# ---------------- e14 (a) — portfolio ----------------
edit(PF, '''    const quoteOf=async(addr)=>{
      try{
        const r=await fetch(`https://api.dexscreener.com/latest/dex/tokens/${addr}`);
        const d=await r.json();''', '''    /* Audit IV e14: an 8 s limit on the DexScreener quote — a stalled connection used to hold the page (and every wallet read)
       for as long as it stalled. */
    const pfDsTokens=async(addr)=>{
      const c=new AbortController();const t=setTimeout(()=>c.abort(),8000);
      try{const r=await fetch(`https://api.dexscreener.com/latest/dex/tokens/${addr}`,{signal:c.signal});if(!r.ok)throw new Error('HTTP '+r.status);return await r.json();}
      finally{clearTimeout(t);}
    };
    const quoteOf=async(addr)=>{
      try{
        const d=await pfDsTokens(addr);''')
edit(PF, '''    const usdOf=async(addr)=>{
      try{
        const r=await fetch(`https://api.dexscreener.com/latest/dex/tokens/${addr}`);
        const d=await r.json();''', '''    const usdOf=async(addr)=>{
      try{
        const d=await pfDsTokens(addr);   // e14''')
edit(PF, '''      const[initialLoad,setInitialLoad]=useState(true);''', '''      const[initialLoad,setInitialLoad]=useState(true);
      const[pricesLoading,setPricesLoading]=useState(true);   // e14: the header's quote skeleton — the wallet reads no longer wait for it''')
edit(PF, '''        const init=async()=>{
          // Prices via the robust /tokens/{addr} path; each is null on failure (renders "—", never a fake 0).
          const[pq,uq,wq]=await Promise.all([''', '''        const init=async()=>{
          /* Audit IV e14: the wallet reads start NOW — balances, staking and locks come from the chain; USD is only a multiplier
             the tiles already print as "—" until a price lands. */
          setInitialLoad(false);
          // Prices via the robust /tokens/{addr} path; each is null on failure (renders "—", never a fake 0).
          const[pq,uq,wq]=await Promise.all([''')
edit(PF, '''          // The new UFO contract has no LP-staking module, so there's nothing to discover here.
          setInitialLoad(false);''', '''          // The new UFO contract has no LP-staking module, so there's nothing to discover here.
          setPricesLoading(false);''')
edit(PF, "<PortfolioHeaderV2 prices={prices} changes={changes} loading={initialLoad} ", "<PortfolioHeaderV2 prices={prices} changes={changes} loading={pricesLoading} ")

# ---------------- e14 (b) + e15 — index ----------------
edit(IX, "    const DATA_FETCH={cache:'no-cache'};", """    const DATA_FETCH={cache:'no-cache'};
    /* Audit IV e14 (2026-10-23): every repo data read gets a 20 s limit (headers AND body) — a stalled raw.githubusercontent
       connection used to hold PTGC's first paint (and the history readouts) for as long as it stalled. An abort is a failed
       read: every caller already treats a rejection as "unknown". */
    const DATA_TIMEOUT_MS=20000;
    const dataFetch=(url,ms=DATA_TIMEOUT_MS)=>{
      if(typeof AbortController==='undefined')return fetch(url,DATA_FETCH);
      const c=new AbortController();setTimeout(()=>c.abort(),ms);   // never cleared: the limit covers the body read too; an abort after it finished is a no-op
      return fetch(url,{...DATA_FETCH,signal:c.signal});
    };""")
edit('tools/top100/t1.jsx', 'c.p=fetch(T1_RAW+f,DATA_FETCH)', 'c.p=dataFetch(T1_RAW+f)')   # the Top 100 fragment (tools/top100.py splices it)
import re
s = open(IX, encoding='utf-8').read()
s2, k = re.subn(r'\bfetch\(\s*(?!url\b)([A-Za-z_][A-Za-z0-9_+.\']*|\'https://raw\.githubusercontent\.com/[^\']+\')\s*,\s*DATA_FETCH\s*\)', r'dataFetch(\1)', s)   # not dataFetch's own fetch(url,…)
if k: open(IX, 'w', encoding='utf-8').write(s2); n += 1; print(f'  index: {k} data reads → dataFetch')
edit(IX, '''          if(token==='UFO'){
            setBurnPeriods(undefined);   // undefined = still loading (the on-chain scan below fills it); null = failed
          }else{
            await cachesP;
            if(loadCancelled)return;
            setBurnPeriods(getBurnPeriods(token));
          }''', '''          if(token==='UFO'){
            setBurnPeriods(undefined);   // undefined = still loading (the on-chain scan below fills it); null = failed
          }else{
            /* Audit IV e14: first paint no longer waits for the six history files (a stalled CDN left PTGC a skeleton with no
               error and no Retry). The burn periods are seeded the moment they land — undefined (= loading) until then. */
            setBurnPeriods(undefined);
            cachesP.then(()=>{if(!loadCancelled)setBurnPeriods(getBurnPeriods(token));});
          }''')
edit(IX, '''    const HARDCODED_UFO_PAIRS = [''', '''    /* Audit IV e15 (2026-10-23): the pools the UFO contract's auto-liquidity mints into (the constructor pools — resolveUfoPairs'
       filter). The browser's value-generated fallback scans Mint logs on these only: the other four can never hold a contract
       mint (every mint in data/value-generated.json is on these three), and scanning them cost ~312 eth_getLogs per visit. */
    const UFO_MINT_POOL_SYMBOLS=['WPLS','PLSX','WETH'];
    const HARDCODED_UFO_PAIRS = [''')
edit(IX, "            try{ d=await fetchDeliveredValue(TOKENS.UFO.address,TOKENS.PTGC.address,firstPoolMs,HARDCODED_UFO_PAIRS); }",
         "            try{ d=await fetchDeliveredValue(TOKENS.UFO.address,TOKENS.PTGC.address,firstPoolMs,DIAG?HARDCODED_UFO_PAIRS:HARDCODED_UFO_PAIRS.filter(p=>UFO_MINT_POOL_SYMBOLS.includes(p.quoteSymbol))); }   // e15: ?debug=1 keeps all seven (its swap reconciliation)")

# ---------------- e14 (c) — calculators ----------------
edit(CA, '''        const [tokensRes, pairsRes] = await Promise.all([
          fetch(`https://api.dexscreener.com/latest/dex/tokens/${addr}`),
          fetch(`https://api.dexscreener.com/token-pairs/v1/pulsechain/${addr}`)
        ]);
        
        const tokensData = await tokensRes.json();
        let pairsData = [];
        try {
          pairsData = await pairsRes.json();
        } catch(e) {
          pairsData = [];
        }''', '''        /* Audit IV e14: through dsJson (8 s, one retry, null on failure) — two bare fetches here held the full-screen
           "Loading Calculators…" for as long as DexScreener stalled. A failed tokens read still fails this call, as before. */
        const [tokensData, pairsData0] = await Promise.all([
          dsJson(`https://api.dexscreener.com/latest/dex/tokens/${addr}`),
          dsJson(`https://api.dexscreener.com/token-pairs/v1/pulsechain/${addr}`)
        ]);
        if (!tokensData) throw new Error('DexScreener tokens endpoint unavailable');
        const pairsData = Array.isArray(pairsData0) ? pairsData0 : [];''')
edit(CA, '''        const [tokensRes, pairsRes] = await Promise.all([
          fetch(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`),
          fetch(`https://api.dexscreener.com/token-pairs/v1/pulsechain/${tokenAddress}`)
        ]);
        const tokensData = await tokensRes.json();
        let pairsData = []; try { pairsData = await pairsRes.json(); } catch(e) {}''', '''        const [tokensData, pairsData0] = await Promise.all([   // e14: dsJson, not bare fetches
          dsJson(`https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`),
          dsJson(`https://api.dexscreener.com/token-pairs/v1/pulsechain/${tokenAddress}`)
        ]);
        if (!tokensData) throw new Error('DexScreener tokens endpoint unavailable');
        const pairsData = Array.isArray(pairsData0) ? pairsData0 : [];''')
edit(CA, '''              const resp=await fetch(`https://api.dexscreener.com/latest/dex/tokens/${pair.coreAddress}`);
              const coreData=await resp.json();''', '''              const coreData=await dsJson(`https://api.dexscreener.com/latest/dex/tokens/${pair.coreAddress}`);   // e14''')
edit(CA, '''        const r = await fetch(COINGECKO_DATA_URL, {cache:'no-cache'});   // c12 (Audit III): revalidate, never a cache-buster (the CDN ignores it)
        coingeckoDataCache = await r.json();''', '''        const c = new AbortController(); setTimeout(() => c.abort(), 15000);   // Audit IV e14: a stalled CDN read is a failed read, not a hang (covers the body too)
        const r = await fetch(COINGECKO_DATA_URL, {cache:'no-cache', signal:c.signal});   // c12 (Audit III): revalidate, never a cache-buster (the CDN ignores it)
        if (!r.ok) throw new Error('HTTP ' + r.status);
        coingeckoDataCache = await r.json();''')
edit(CA, '''        const load=async()=>{
          await fetchCoingeckoData();
          if(cancelled)return;
          const[d,b,p]=await Promise.all([''', '''        const load=async()=>{
          /* Audit IV e14: the coingecko file is no longer a gate on first paint — only the PTGC volume windows below read it. */
          const cgP=fetchCoingeckoData();
          const[d,b,p]=await Promise.all([''')
edit(CA, '''          if(token==='UFO'){
            /* MIGRATION: actuals only — the coingecko file tracks the old contract. */''', '''          await cgP;   // e14: the volume windows (and the ATH floor) read it from here on
          if(cancelled)return;
          if(token==='UFO'){
            /* MIGRATION: actuals only — the coingecko file tracks the old contract. */''')

out = subprocess.run([sys.executable, 'tools/top100.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-batch4: {n} edit(s), index {sha(IX)}, portfolio {sha(PF)}, calculators {sha(CA)}')
