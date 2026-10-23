#!/usr/bin/env python3
r"""Audit IV (handover/sessions/2026-10-22-audit4.md) — batch P0b, 2026-10-23: e7, e8, e3, e4 + e19's version bump.
Idempotent, run from the repo root:   python3 tools/audit4-p0b.py      (run it twice: the second run must print "0 edit(s)")
Then rebuild the CSS in the harness (`cd tools/harness && npm run css`) and commit tw.css — that is e19's other half.

e7  portfolio.html GET / LOAD CODE: the code is UTF-8-safe base64 (btoa threw on any emoji / en-dash / CJK label and the window
    showed an EMPTY code); an ASCII-only list encodes byte-for-byte as before, and decode reads old Latin-1 codes too. If a code
    still cannot be built the window says so instead of an empty box; Copy waits for the clipboard and says when it failed.
    LOAD CODE over a non-empty list asks first ("Replace N wallets with M?") and drops the old wallets' queued scans.
e8  portfolio.html fetchPortfolioData: the UFO balanceOf is read in the same batch as the six PTGC words and must pass the same
    a11 `okWord` test — a failed UFO read now marks the wallet failed (red dot + Retry, left out of the totals) instead of a
    silent 0 with a green dot. Same rule for the two per-lock reads (a failed one used to drop that lock from Locked / Pending).
e3  index.html fetchDAOData + the DAO panel + the DAO share card: no PLS price or no management-wallet balance → no DAO data
    ("—", the a16 path) instead of "$0"; an unreadable lockedAmount → Available / Pending "—" (the total is still exact: it uses
    the contract balance); a token whose balance or price failed is listed in a visible note and the totals it feeds print as
    "≥ $X" (a lower bound), never as a plain figure. The normal path's arithmetic is unchanged.
e4  index.html referrer window: each transaction row carries its month entry's `meetsThreshold` (gotcha 27: the verdict lives on
    the ENTRY), so a month below the minimum shows "Below" on its buys, "—" in Comm., and the month header's Comm. sum leaves it out.
e19 tw.css?v=2 → ?v=3 on the five pages (the rebuilt tw.css is committed alongside).
"""
import hashlib, re

n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    # the pages write these characters as JS escapes ('\\u2014'); match an anchor in either spelling
    esc = old
    for c in (0x2014, 0x2713, 0x00a0, 0x2265): esc = esc.replace(chr(c), '\\u%04x' % c)
    if s.count(old) != count and s.count(esc) == count: old = esc
    if s.count(old) != count and count == 1:   # blank lines in the pages carry their indent; the anchors here may not
        for cand in (old, esc):
            pat = '\n'.join('[ \t]*' if not ln.strip() else re.escape(ln) for ln in cand.split('\n'))
            m = list(re.finditer(pat, s))
            if len(m) == 1: old = m[0].group(0); break
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))
    n += 1

PF, IX = 'portfolio.html', 'index.html'

# ============================================================== e7 — GET / LOAD CODE ===============================
edit(PF, r"""    const encodePortfolio=(wallets)=>{
      try{
        const data=wallets.map(w=>({a:w.address.toLowerCase(),n:w.name||'',g:w.group||'Default'}));
        return'GRAY-'+btoa(JSON.stringify(data));
      }catch{return null}
    };""", r"""    /* Audit IV e7 (2026-10-23): btoa() only takes Latin-1, so ONE emoji / en-dash / CJK character in a wallet label made the
       whole code null and GET CODE showed an empty box. The JSON is now UTF-8 encoded first. An ASCII-only list produces exactly
       the same code as before; decode tries UTF-8 and falls back to the old Latin-1 reading, so every code ever issued loads. */
    const pfB64Enc=str=>{const u=new TextEncoder().encode(str);let b='';for(let i=0;i<u.length;i+=0x8000)b+=String.fromCharCode.apply(null,u.subarray(i,i+0x8000));return btoa(b);};
    const pfB64Dec=b64=>{const bin=atob(b64);try{return new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(bin,c=>c.charCodeAt(0)));}catch(e){return bin;}};
    const encodePortfolio=(wallets)=>{
      try{
        const data=wallets.map(w=>({a:w.address.toLowerCase(),n:w.name||'',g:w.group||'Default'}));
        return'GRAY-'+pfB64Enc(JSON.stringify(data));
      }catch{return null}
    };""")
edit(PF, r"""        const data=JSON.parse(atob(code.slice(5)));""",
         r"""        const data=JSON.parse(pfB64Dec(code.slice(5)));   // e7: UTF-8 first, old Latin-1 codes still read""")
edit(PF, r"""      const[codeError,setCodeError]=useState('');""",
         r"""      const[codeError,setCodeError]=useState('');
      const[loadArmed,setLoadArmed]=useState(0);   // e7: >0 = "replace N wallets?" asked once; the number of wallets in the code""")
edit(PF, r"""        const code=encodePortfolio(wallets);
        setGeneratedCode(code||'');""", r"""        const code=encodePortfolio(wallets);
        setGeneratedCode(code);   // e7: null = the code could not be built — the window says so (never an empty box)""")
edit(PF, r"""        if(decoded.dropped)console.warn(`Load Code: ${decoded.dropped} entr${decoded.dropped===1?'y':'ies'} without a valid address skipped`);
        setWallets(decoded.wallets);""", r"""        if(decoded.dropped)console.warn(`Load Code: ${decoded.dropped} entr${decoded.dropped===1?'y':'ies'} without a valid address skipped`);
        /* e7: replacing a non-empty list asks once (the button turns into "Replace N wallets with M") */
        if(wallets.length>0&&loadArmed!==decoded.wallets.length){setLoadArmed(decoded.wallets.length);return}
        setLoadArmed(0);
        dropReflScans(null);   // the old wallets' queued reflection scans belong to the list being replaced
        setWallets(decoded.wallets);""")
edit(PF, r"""        try{navigator.clipboard.writeText(generatedCode);setCodeCopied(true);setTimeout(()=>setCodeCopied(false),2000);}catch{}""",
         r"""        /* e7: wait for the clipboard — "Copied!" only on success; on failure say so (the code stays selectable) */
        if(!generatedCode)return;
        const done=v=>{setCodeCopied(v);setTimeout(()=>setCodeCopied(false),v===true?2000:4000);};
        try{const p=navigator.clipboard&&navigator.clipboard.writeText(generatedCode);if(p&&p.then)p.then(()=>done(true),()=>done('fail'));else done('fail');}catch{done('fail');}""")
edit(PF, r"""                  <code className="text-[#D9CA5D] text-sm font-mono break-all select-all">{generatedCode}</code>
                </div>
                <button onClick={copyCode} className={`w-full py-2.5 rounded-lg font-bold transition-all ${codeCopied?'bg-green-500 text-black':'bg-[#D9CA5D] text-black hover:opacity-90'}`}>
                  {codeCopied?'✓ Copied!':'Copy to Clipboard'}
                </button>""", r"""                  {generatedCode
                    ?<code className="text-[#D9CA5D] text-sm font-mono break-all select-all">{generatedCode}</code>
                    :<div role="alert" className="text-red-400 text-base">Couldn't build the code for this list. Rename any wallet whose label has unusual characters and try again.</div>}
                </div>
                <button onClick={copyCode} disabled={!generatedCode} className={`w-full py-2.5 rounded-lg font-bold transition-all disabled:opacity-40 ${codeCopied===true?'bg-green-500 text-black':codeCopied==='fail'?'bg-red-500/80 text-white':'bg-[#D9CA5D] text-black hover:opacity-90'}`}>
                  {codeCopied===true?'✓ Copied!':codeCopied==='fail'?'Copy failed — select the code and copy it':'Copy to Clipboard'}
                </button>""")
edit(PF, r"""<input value={codeInput} onChange={e=>setCodeInput(e.target.value)} placeholder="GRAY-""",
         r"""<input value={codeInput} onChange={e=>{setCodeInput(e.target.value);setLoadArmed(0)}} placeholder="GRAY-""")
edit(PF, r"""                {codeError&&<div className="text-red-400 text-base mb-3">{codeError}</div>}
                <button onClick={handleLoadCode} className="w-full py-3 rounded-lg font-bold text-lg bg-gradient-to-r from-[#D9CA5D] to-[#7CFC00] text-black hover:opacity-90 transition-all">Load Portfolio</button>""",
         r"""                {codeError&&<div className="text-red-400 text-base mb-3">{codeError}</div>}
                {loadArmed>0&&<div role="alert" className="text-amber-300 text-base mb-3">This replaces your {wallets.length} saved wallet{wallets.length===1?'':'s'} with the {loadArmed} in this code. Press again to replace them.</div>}
                <button onClick={handleLoadCode} className="w-full py-3 rounded-lg font-bold text-lg bg-gradient-to-r from-[#D9CA5D] to-[#7CFC00] text-black hover:opacity-90 transition-all">{loadArmed>0?`Replace ${wallets.length} wallet${wallets.length===1?'':'s'} with ${loadArmed}`:'Load Portfolio'}</button>""")
edit(PF, r"""setShowLoadModal(true);setCodeError('');setCodeInput('')}""",
         r"""setShowLoadModal(true);setCodeError('');setCodeInput('');setLoadArmed(0)}""", count=2)

# ============================================================== e8 — UFO balance in the a11 guard ===================
edit(PF, r"""      const[ptgcBal,ptgcSend,ptgcRecv,ptgcUserInfo,ptgcPendingStake,ptgcLockCountRes]=await Promise.all([
        callContract(PTGC_TOKEN_ADDR,SEL.balanceOf+addr),""", r"""      /* Audit IV e8 (2026-10-23): the UFO balance is read in the SAME batch and must pass the same okWord test. It used to be
         a separate call allowed to fail softly: balance null → the wallet stayed "ok" (green dot) while the totals, the
         breakdown ("0 UFO") and the rank badge ("not holding") all used 0. */
      const[ptgcBal,ptgcSend,ptgcRecv,ptgcUserInfo,ptgcPendingStake,ptgcLockCountRes,ufoBal]=await Promise.all([
        callContract(PTGC_TOKEN_ADDR,SEL.balanceOf+addr),""")
edit(PF, r"""        callContract(PTGC_STAKING_ADDR,SEL.lockCount+addr),
      ]);""", r"""        callContract(PTGC_STAKING_ADDR,SEL.lockCount+addr),
        callContract(UFO_TOKEN_ADDR,SEL.balanceOf+addr),
      ]);""")
edit(PF, r"""      if(![ptgcBal,ptgcSend,ptgcRecv,ptgcUserInfo,ptgcPendingStake,ptgcLockCountRes].every(okWord)){
        throw new Error('PTGC read failed (RPC returned no result)');
      }""", r"""      if(![ptgcBal,ptgcSend,ptgcRecv,ptgcUserInfo,ptgcPendingStake,ptgcLockCountRes].every(okWord)){
        throw new Error('PTGC read failed (RPC returned no result)');
      }
      if(!okWord(ufoBal))throw new Error('UFO read failed (RPC returned no result)');   // e8""")
edit(PF, r"""            ]).then(([info,pend])=>{
              const amt=toNum(parseWord(info,0));""", r"""            ]).then(([info,pend])=>{
              if(!okWord(info)||!okWord(pend))throw new Error('PTGC lock read failed (RPC returned no result)');   // e8: a failed lock read dropped the lock silently
              const amt=toNum(parseWord(info,0));""")
edit(PF, r"""      const ufoBal=await callContract(UFO_TOKEN_ADDR,SEL.balanceOf+addr);
      // Distinguish a failed/reverted call (null or '0x') from a genuine zero balance (a full 32-byte word),
      // so a read failure shows "—" instead of a fake 0.
      const ufoOk=(ufoBal&&ufoBal!=='0x'&&ufoBal.length>=66);""", r"""      // e8: ufoBal is read with the PTGC batch above and has passed okWord (a failed read threw), so ufoOk is always true
      // here; the null branches below stay as a second line of defence.
      const ufoOk=okWord(ufoBal);""")

# ============================================================== e3 — DAO Treasury =================================
edit(IX, r"""    const fetchDAOData=async(daoContract,managementWallet,plsPrice)=>{
      try{""", r"""    /* Audit IV e3 (2026-10-23): every read after the a16 guard used to become 0 on failure and the panel printed the totals as
       fact. Now: no PLS price / no management balance → null (the panel says "—"); an unreadable lockedAmount → Available and
       Pending null (the total stays exact — it uses the contract balance); a failed token balance or price is named in
       `failed`, and `mgmtPartial` / `lowerBound` make the totals print as "≥ $X". The normal path's arithmetic is unchanged. */
    const daoUsd=(v,lb)=>v==null||isNaN(v)?'—':(lb?'≥ ':'')+fmtUSD(v);
    const fetchDAOData=async(daoContract,managementWallet,plsPrice)=>{
      try{
        if(!(plsPrice>0)){console.warn('DAO data: no PLS price');return null;}   // e3: was "$0" on every PLS figure
        const failed=[];""")
edit(IX, r"""        let lockedAmountWei=0n;
        try{
          const lockResult=await rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to:daoContract,data:'0x6ab28bc8'},'latest'],id:2});
          console.log('lockedAmount raw result:',lockResult.result);
          if(lockResult.result&&lockResult.result.length>2){
            lockedAmountWei=BigInt(lockResult.result);
          }
        }catch(e){console.error('lockedAmount error:',e)}""", r"""        let lockedAmountWei=0n,lockOk=false;
        try{
          const lockResult=await rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to:daoContract,data:'0x6ab28bc8'},'latest'],id:2});
          console.log('lockedAmount raw result:',lockResult&&lockResult.result);
          if(lockResult&&lockResult.result&&lockResult.result.length>=66){
            lockedAmountWei=BigInt(lockResult.result);lockOk=true;
          }
        }catch(e){console.error('lockedAmount error:',e)}
        if(!lockOk)failed.push('the locked amount');   // e3: Available / Pending print "—"; the total still uses the contract balance""")
edit(IX, r"""        const mgmtBalanceResult=await rpcFetch({jsonrpc:'2.0',method:'eth_getBalance',params:[managementWallet,'latest'],id:3});
        const mgmtPLSWei=BigInt(mgmtBalanceResult.result||'0x0');""", r"""        const mgmtBalanceResult=await rpcFetch({jsonrpc:'2.0',method:'eth_getBalance',params:[managementWallet,'latest'],id:3});
        if(!mgmtBalanceResult||mgmtBalanceResult.result==null){console.warn('DAO data: management eth_getBalance returned no result');return null;}   // e3: was "0 PLS"
        const mgmtPLSWei=BigInt(mgmtBalanceResult.result);""")
edit(IX, r"""            const tokenResult=await rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to:token.address,data},'latest'],id:4});
            if(tokenResult.result&&tokenResult.result!=='0x'&&tokenResult.result!=='0x0'){
              const balanceWei=BigInt(tokenResult.result);
              const balance=Number(balanceWei)/Math.pow(10,token.decimals);
              if(balance>0.0001){
                // Use stablecoin price of 1, otherwise use dynamic price from DexScreener
                const price = token.stablecoin ? 1 : (priceMap[token.address.toLowerCase()] || 0);""", r"""            const tokenResult=await rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to:token.address,data},'latest'],id:4});
            if(!tokenResult||!tokenResult.result||tokenResult.result==='0x')return{failed:`${token.symbol} balance`};   // e3: was skipped silently
            if(tokenResult.result!=='0x0'){
              const balanceWei=BigInt(tokenResult.result);
              const balance=Number(balanceWei)/Math.pow(10,token.decimals);
              if(balance>0.0001){
                // Use stablecoin price of 1, otherwise use dynamic price from DexScreener
                const price = token.stablecoin ? 1 : (priceMap[token.address.toLowerCase()] || 0);
                if(!(price>0))return{failed:`${token.symbol} price`};   // e3: a held token with no price was dropped from the total silently""")
edit(IX, r"""          }catch(e){console.error(`Error fetching ${token.symbol}:`,e)}
          return null;
        });

        const tokenResults=await Promise.all(tokenPromises);
        tokenResults.forEach(t=>{
          if(t&&t.usdValue>0){""", r"""          }catch(e){console.error(`Error fetching ${token.symbol}:`,e);return{failed:`${token.symbol} balance`};}
          return null;
        });

        const tokenResults=await Promise.all(tokenPromises);
        tokenResults.forEach(t=>{
          if(t&&t.failed){failed.push(t.failed);return;}
          if(t&&t.usdValue>0){""")
edit(IX, r"""        let ptgcBalance=0,ptgcPrice=0,ptgcUSD=0;""",
         r"""        const mgmtPartial=failed.some(f=>f!=='the locked amount');   // e3: Ready to Deploy is a lower bound
        let ptgcBalance=0,ptgcPrice=0,ptgcUSD=0;""")
edit(IX, r"""          ptgcPrice=ptgcPriceRes||0;
          if(ptgcBalRes.result&&ptgcBalRes.result!=='0x'&&ptgcBalRes.result!=='0x0'){
            ptgcBalance=Number(BigInt(ptgcBalRes.result))/Math.pow(10,TOKENS.PTGC.decimals);
            ptgcUSD=ptgcBalance*ptgcPrice;
          }""", r"""          ptgcPrice=ptgcPriceRes||0;
          if(!ptgcBalRes||!ptgcBalRes.result||ptgcBalRes.result==='0x'){failed.push('PTGC balance');ptgcUSD=null;}   // e3
          else if(ptgcBalRes.result!=='0x0'){
            ptgcBalance=Number(BigInt(ptgcBalRes.result))/Math.pow(10,TOKENS.PTGC.decimals);
            if(ptgcBalance>0.0001&&!(ptgcPrice>0)){failed.push('PTGC price');ptgcUSD=null;}   // e3: was "$0" for ~2B PTGC
            else ptgcUSD=ptgcBalance*ptgcPrice;
          }""")
edit(IX, r"""        }catch(e){console.error('PTGC balance fetch error:',e)}""",
         r"""        }catch(e){console.error('PTGC balance fetch error:',e);failed.push('PTGC balance');ptgcUSD=null;}""")
edit(IX, r"""        const availableUSD=availablePLS*plsPrice;
        const pendingUSD=lockedAmountPLS*plsPrice;
        const totalValue=availableUSD+pendingUSD+managementTotalUSD+ptgcUSD;""", r"""        const availableUSD=lockOk?availablePLS*plsPrice:null;
        const pendingUSD=lockOk?lockedAmountPLS*plsPrice:null;
        // e3: the same sum as before when every read worked; without lockedAmount the contract's whole balance stands in for
        // Available + Pending (their sum), and a failed PTGC leg is left out — `lowerBound` makes that visible.
        const daoLegUSD=lockOk?availableUSD+pendingUSD:(Number(daoBalanceWei)/1e18)*plsPrice;
        const totalValue=daoLegUSD+managementTotalUSD+(ptgcUSD||0);
        const lowerBound=mgmtPartial||ptgcUSD==null;""")
edit(IX, r"""        return{
          availablePLS,
          availableUSD,
          pendingPLS:lockedAmountPLS,
          pendingUSD,""", r"""        return{
          availablePLS:lockOk?availablePLS:null,
          availableUSD,
          pendingPLS:lockOk?lockedAmountPLS:null,
          pendingUSD,
          failed:failed.length?failed:null,mgmtPartial,lowerBound,   // e3""")
# --- the panel
edit(IX, r"""{daoData?fmtUSD(daoData.totalValue||0):'—'}""", r"""{daoData?daoUsd(daoData.totalValue,daoData.lowerBound):'—'}""", count=2)
edit(IX, r"""{daoData?fmtUSD(daoData.availableUSD||0):'—'}</div>
                            <div className="text-white/45 text-xs tabular-nums mt-1 truncate">{daoData?`${fmtAbbr(daoData.availablePLS||0)} PLS`:' '}</div>""",
         r"""{daoData?daoUsd(daoData.availableUSD):'—'}</div>
                            <div className="text-white/45 text-xs tabular-nums mt-1 truncate">{daoData&&daoData.availablePLS!=null?`${fmtAbbr(daoData.availablePLS)} PLS`:' '}</div>""")
edit(IX, r"""{daoData?fmtUSD(daoData.pendingUSD||0):'—'}</div>
                            <div className="text-white/45 text-xs tabular-nums mt-1 truncate">{daoData?`${fmtAbbr(daoData.pendingPLS||0)} PLS`:' '}</div>""",
         r"""{daoData?daoUsd(daoData.pendingUSD):'—'}</div>
                            <div className="text-white/45 text-xs tabular-nums mt-1 truncate">{daoData&&daoData.pendingPLS!=null?`${fmtAbbr(daoData.pendingPLS)} PLS`:' '}</div>""")
edit(IX, r"""{daoData?fmtUSD(daoData.managementValue||0):'—'}""", r"""{daoData?daoUsd(daoData.managementValue,daoData.mgmtPartial):'—'}""")
edit(IX, r"""<span className="text-emerald-400 tabular-nums">{fmtUSD(daoData.availableUSD||0)}</span>""",
         r"""<span className="text-emerald-400 tabular-nums">{daoUsd(daoData.availableUSD)}</span>""")
edit(IX, r"""<span className="text-emerald-400 tabular-nums">{fmtUSD(daoData.pendingUSD||0)}</span>""",
         r"""<span className="text-emerald-400 tabular-nums">{daoUsd(daoData.pendingUSD)}</span>""")
edit(IX, r"""<span className="text-emerald-400 tabular-nums">{fmtUSD(daoData.managementValue||0)}</span>""",
         r"""<span className="text-emerald-400 tabular-nums">{daoUsd(daoData.managementValue,daoData.mgmtPartial)}</span>""")
edit(IX, r"""<span className="text-emerald-400 ml-2">{fmtUSD(daoData.ptgcUSD||0)}</span>""",
         r"""<span className="text-emerald-400 ml-2">{daoUsd(daoData.ptgcUSD)}</span>""")
edit(IX, r"""<span className="text-emerald-400 font-bold tabular-nums">{fmtUSD(daoData.totalValue||0)}</span>""",
         r"""<span className="text-emerald-400 font-bold tabular-nums">{daoUsd(daoData.totalValue,daoData.lowerBound)}</span>""")
# the visible note, right after the second tile row of the panel
edit(IX, r"""                                  <div className="flex justify-between gap-3 pt-2 mt-1 border-t border-white/10">
                                    <span className="font-bold text-white/80">Total</span>""", r"""                                  {daoData.lowerBound&&<div className="text-amber-300/90 text-xs">{'≥'} = a lower bound: {daoData.failed.join(', ')} could not be read.</div>}
                                  <div className="flex justify-between gap-3 pt-2 mt-1 border-t border-white/10">
                                    <span className="font-bold text-white/80">Total</span>""")
edit(IX, r"""{hdrV2&&<div className="p2-hero"><span className="p2-hl tabular-nums">{daoData?daoUsd(daoData.totalValue,daoData.lowerBound):'—'}</span><span className="l">Total DAO Value</span></div>}""",
         r"""{hdrV2&&<div className="p2-hero"><span className="p2-hl tabular-nums">{daoData?daoUsd(daoData.totalValue,daoData.lowerBound):'—'}</span><span className="l">Total DAO Value</span></div>}
                        {daoData&&daoData.failed&&<div role="status" className="text-amber-300/90 text-xs leading-snug">Couldn't read {daoData.failed.join(', ')} just now{daoData.lowerBound?<> — figures marked {'≥'} are lower bounds</>:<> — shown as {'—'}</>}. Reload to try again.</div>}""")
# --- the share card (DaoTreasuryCard): never a plain total, never a split bar, when a read failed
edit(IX, r"""      const segs=d&&d.totalValue>0?[""", r"""      const segs=d&&d.totalValue>0&&!d.failed?[   // e3: no split bar when a read failed""")
edit(IX, r"""{loading&&!d?'…':money(d&&d.totalValue)}""", r"""{loading&&!d?'…':(d&&d.lowerBound&&d.totalValue!=null?'≥ ':'')+money(d&&d.totalValue)}""")
edit(IX, r"""sub={d?fmtAbbr(d.availablePLS)+' PLS':''}""", r"""sub={d&&d.availablePLS!=null?fmtAbbr(d.availablePLS)+' PLS':''}""")
edit(IX, r"""sub={d?fmtAbbr(d.pendingPLS)+' PLS':''}""", r"""sub={d&&d.pendingPLS!=null?fmtAbbr(d.pendingPLS)+' PLS':''}""")
edit(IX, r"""{val(money(d&&d.managementValue))}""", r"""{val((d&&d.mgmtPartial&&d.managementValue!=null?'≥ ':'')+money(d&&d.managementValue))}""")

# ============================================================== e4 — referrer window verdict =========================
edit(IX, r"""                    allTx.push({...b,month,rate:entry.commissionRate||log.settings?.commissionRate||2});""",
         r"""                    allTx.push({...b,month,rate:entry.commissionRate||log.settings?.commissionRate||2,meetsThreshold:entry.meetsThreshold});   // Audit IV e4: the verdict lives on the ENTRY (gotcha 27)""")
edit(IX, r"""{fmtAbbr(monthTxs.reduce((s,t)=>s+((t.ptgcAmount||0)*(t.rate||2)/100),0))}""",
         r"""{fmtAbbr(monthTxs.reduce((s,t)=>s+(t.meetsThreshold===false?0:(t.ptgcAmount||0)*(t.rate||2)/100),0))}""")
edit(IX, r"""<td className="py-2 px-2 sm:px-3 text-right text-purple-400 whitespace-nowrap"><span className="sm:hidden">{fmtAbbr((tx.ptgcAmount||0)*(tx.rate/100))}</span><span className="hidden sm:inline">{fmtComma((tx.ptgcAmount||0)*(tx.rate/100),4)}</span></td>""",
         r"""<td className="py-2 px-2 sm:px-3 text-right text-purple-400 whitespace-nowrap">{tx.meetsThreshold===false?<span className="text-white/40">{'—'}</span>:<><span className="sm:hidden">{fmtAbbr((tx.ptgcAmount||0)*(tx.rate/100))}</span><span className="hidden sm:inline">{fmtComma((tx.ptgcAmount||0)*(tx.rate/100),4)}</span></>}</td>""")

# ============================================================== e19 — the CSS version ===============================
for p in ('index.html', 'portfolio.html', 'calculators.html', 'charts.html', 'ledger.html'):
    edit(p, 'href="tw.css?v=2"', 'href="tw.css?v=3"')

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-p0b: {n} edit(s), index.html {sha(IX)}, portfolio.html {sha(PF)}, tw.css {sha("tw.css")}'
      + ('' if n == 0 else '   → now: cd tools/harness && npm run css, and commit tw.css'))
