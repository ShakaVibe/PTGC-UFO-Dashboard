#!/usr/bin/env python3
"""Humans vs Bots — a COUNT switch: ALL SWAPS / EACH TX (2026-10-27).

Shaka: "the 30 day in the Volume window does not match the 30 day for the arb bots one … we probably need to match
dexscreener … ya, we probably need a selector switch".

Why they differed: the Volume window (and DexScreener) count every swap in every pool, so a bot loop (a buy in one pool +
a sell in another, ONE transaction) is two swaps; Humans vs Bots counted each transaction once (Audit V v22). People's
volume is the same either way — the whole gap is bot loops (PTGC 30D $1.49M vs $1.28M, UFO $428K vs $288K).

- New switch in the window's control row: ALL SWAPS (default — the DexScreener way, = the Volume window's 7D / 30D / 90D
  to the dollar) / EACH TX (each transaction once, UFO's own swapback apart — the old view). Shown only when the file has
  the `measured` block.
- It drives the totals strip, both boxes (volume, %, count — "swaps" / "transactions"), the bar, the chart (`hours` vs
  `measuredHours`) and the share card (📷 has the same switch; Socials' card opens on ALL SWAPS).
- Fees paid are the chain's in both modes (unchanged). The note under the boxes always shows the other count, so the
  honest bot share is one glance away.
- By pool / Top bot contracts are per pool, i.e. per swap, in both modes (unchanged).

Idempotent (done-markers); a second run prints "0 edit(s)". Run from the repo root.
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
        sys.exit(f'anchor found {n}x (want {count}): {old[:100]!r}')
    s = s.replace(old, new)
    edits += 1

# ---- 1. vsView: the chart series follow the count -------------------------------------------------------------------
rep("const vsView=(file,token,P,pairMap)=>{",
    "const vsView=(file,token,P,pairMap,count='swaps')=>{   // count (2026-10-27): 'swaps' = every swap, as DexScreener / the Volume window; 'txs' = each transaction once",
    "const vsView=(file,token,P,pairMap,count='swaps')")
rep("const useM=v.m&&toks.every(tk=>file.tokens[tk]&&Array.isArray(file.tokens[tk].measuredHours));   // Audit V v22: each tx once",
    "const useM=count==='txs'&&v.m&&toks.every(tk=>file.tokens[tk]&&Array.isArray(file.tokens[tk].measuredHours));   // Audit V v22: each tx once (EACH TX only, 2026-10-27)",
    "const useM=count==='txs'&&v.m")

# ---- 2. vsShow: volume / counts by the switch, fees from the chain either way ------------------------------------------
rep("""    const vsShow=(view,vg)=>{
      if(view.m){const m=view.m,f=m.fees;return{measured:true,hUsd:m.human.usd,bUsd:m.bot.usd,hN:m.human.txs,bN:m.bot.txs,unit:'transaction',""",
    """    /* The COUNT switch (2026-10-27, Shaka: "we probably need to match dexscreener … a selector switch"). ALL SWAPS = every swap in
       every pool (DexScreener's way, = the Volume window to the dollar: a bot loop is two swaps); EACH TX = each transaction once. */
    const VS_COUNT=[{k:'ALL SWAPS',label:'Count every swap, like DexScreener'},{k:'EACH TX',label:'Count each transaction once'}];
    const vsCountK=c=>c==='txs'?'EACH TX':'ALL SWAPS',vsCountOf=k=>k==='EACH TX'?'txs':'swaps';
    const vsShow=(view,vg,count='swaps')=>{
      if(view.m){const m=view.m,f=m.fees,sw=count!=='txs',txUsd=m.human.usd+m.bot.usd;return{measured:true,count:sw?'swaps':'txs',
        hUsd:sw?view.human.usd:m.human.usd,bUsd:sw?view.bot.usd:m.bot.usd,hN:sw?view.human.n:m.human.txs,bN:sw?view.bot.n:m.bot.txs,unit:sw?'swap':'transaction',
        swapUsd:view.total.usd,swapBotShare:view.total.usd>0?view.bot.usd/view.total.usd:null,txUsd,txBotShare:txUsd>0?m.bot.usd/txUsd:null,""",
    "const VS_COUNT=[")

# ---- 3. share card + its modal + the Socials entry ------------------------------------------------------------------
rep("const HvbShareCard=({mode,file,P,feeRates})=>{",
    "const HvbShareCard=({mode,file,P,feeRates,count='swaps'})=>{",
    "const HvbShareCard=({mode,file,P,feeRates,count='swaps'})")
rep("const view=React.useMemo(()=>file?vsView(file,mode,P,{}):null,[file,mode,P]);",
    "const view=React.useMemo(()=>file?vsView(file,mode,P,{},count):null,[file,mode,P,count]);",
    "vsView(file,mode,P,{},count)")
rep("const D=vsShow(view,hvsVg(file,mode,P,feeRates));   // Audit V: measured when the file has it (each tx once, fees from the chain)",
    "const D=vsShow(view,hvsVg(file,mode,P,feeRates),count);   // Audit V: fees from the chain; volume by the COUNT switch (2026-10-27)",
    "vsShow(view,hvsVg(file,mode,P,feeRates),count)")
rep("nL=D.measured?'Transactions':'Trades',gL=",
    "nL=D.unit==='swap'?'Swaps':D.measured?'Transactions':'Trades',gL=",
    "nL=D.unit==='swap'?'Swaps'")
rep("<span className=\"hvs-period\">{both?'PTGC + UFO':mode} VOLUME {'\\u00b7'} {P.label.toUpperCase()}</span>",
    "<span className=\"hvs-period\">{both?'PTGC + UFO':mode} VOLUME {'\\u00b7'} {P.label.toUpperCase()}{D.count==='txs'?<> {'\\u00b7'} EACH TX ONCE</>:null}</span>",
    "EACH TX ONCE</>:null}</span>")
rep("const HvbShareModal=({token:initial,file,win,setWin,feeRates,loading=false,error=false,onRetry,onClose})=>{",
    "const HvbShareModal=({token:initial,file,win,setWin,count='swaps',setCount,feeRates,loading=false,error=false,onRetry,onClose})=>{",
    "const HvbShareModal=({token:initial,file,win,setWin,count='swaps',setCount,")
rep("{setWin&&<NhPills items={VS_PERIODS} value={win} onChange={setWin} label=\"Period\" rgb={T.rgb}/>}",
    "{setWin&&<NhPills items={VS_PERIODS} value={win} onChange={setWin} label=\"Period\" rgb={T.rgb}/>}\n"
    "        {setCount&&<NhPills items={VS_COUNT} value={vsCountK(count)} onChange={k=>setCount(vsCountOf(k))} label=\"Count\" rgb={T.rgb}/>}",
    "{setCount&&<NhPills items={VS_COUNT}")
rep("<HvbShareCard mode={mode} file={file} P={P} feeRates={feeRates}/>",
    "<HvbShareCard mode={mode} file={file} P={P} feeRates={feeRates} count={count}/>",
    "feeRates={feeRates} count={count}/>")
rep("""const HvbShareSocial=({mode,feeRates,onClose})=>{
      const[win,setWin]=useState('30D');""",
    """const HvbShareSocial=({mode,feeRates,onClose})=>{
      const[win,setWin]=useState('30D');
      const[count,setCount]=useState('swaps');   // 2026-10-27: the COUNT switch, ALL SWAPS first""",
    "const[count,setCount]=useState('swaps');   // 2026-10-27: the COUNT switch, ALL SWAPS first")
rep("return <HvbShareModal token={mode} file={file||null} win={win} setWin={setWin} feeRates={feeRates}",
    "return <HvbShareModal token={mode} file={file||null} win={win} setWin={setWin} count={count} setCount={setCount} feeRates={feeRates}",
    "file={file||null} win={win} setWin={setWin} count={count}")

# ---- 4. the window ---------------------------------------------------------------------------------------------------
rep("const[win,setWin]=useState('30D');   // round 7: opens on 30 days (Shaka)",
    "const[win,setWin]=useState('30D');   // round 7: opens on 30 days (Shaka)\n"
    "      const[count,setCount]=useState('swaps');   // 2026-10-27 (Shaka): ALL SWAPS (= DexScreener / the Volume window) first, EACH TX the other",
    "const[count,setCount]=useState('swaps');   // 2026-10-27 (Shaka)")
rep("const view=React.useMemo(()=>file?vsView(file,token,P,pairMap):null,[file,token,win,pairMap]);",
    "const view=React.useMemo(()=>file?vsView(file,token,P,pairMap,count):null,[file,token,win,pairMap,count]);",
    "vsView(file,token,P,pairMap,count)")
rep("const D=view?vsShow(view,vg):null;   // Audit V v21 / v22: measured when the file has it",
    "const D=view?vsShow(view,vg,count):null;   // Audit V v21 / v22: fees from the chain; volume by the COUNT switch (2026-10-27)",
    "vsShow(view,vg,count)")
rep("<NhPills items={VS_PERIODS} value={win} onChange={setWin} label=\"Period\" rgb={rgb}/>",
    "<NhPills items={VS_PERIODS} value={win} onChange={setWin} label=\"Period\" rgb={rgb}/>\n"
    "                {view&&view.m&&<NhPills items={VS_COUNT} value={vsCountK(count)} onChange={k=>setCount(vsCountOf(k))} label=\"Count\" rgb={rgb}/>}",
    "{view&&view.m&&<NhPills items={VS_COUNT}")
rep("<span className=\"k\">{D.measured?'Transactions':'Trades'}</span>",
    "<span className=\"k\">{D.unit==='swap'?'Swaps':D.measured?'Transactions':'Trades'}</span>",
    "<span className=\"k\">{D.unit==='swap'?'Swaps'")
rep("{shareCard&&file&&<HvbShareModal token={token} file={file} win={win} setWin={setWin} feeRates={feeRates}",
    "{shareCard&&file&&<HvbShareModal token={token} file={file} win={win} setWin={setWin} count={count} setCount={setCount} feeRates={feeRates}",
    "<HvbShareModal token={token} file={file} win={win} setWin={setWin} count={count}")

# the note under the boxes: the other count always one glance away; UFO's swapback only "not counted" in EACH TX
OLD_REST = ("{D.measured&&(D.feeT>0||D.protoUsd>0)&&<div className=\"vs-rest\">{D.feeT>0&&<>+ <b>{fmtUSD(D.feeT)}</b> in fees from sends "
            "between wallets and staking moves ({vsPct(D.feeTot>0?D.feeT/D.feeTot:null)})</>}{D.feeT>0&&D.protoUsd>0&&<> {'\\u00b7'} </>}"
            "{D.protoUsd>0&&<>UFO{'\\u2019'}s own buy-and-burn swaps ({fmtUSD(D.protoUsd)}) are not counted as anyone{'\\u2019'}s</>}</div>}")
NEW_REST = ("{D.measured&&<div className=\"vs-rest\">\n"
            "                    <div>{D.count==='swaps'\n"
            "                      ?<>Counted like DexScreener: every swap in every pool, so a bot{'\\u2019'}s loop {'\\u2014'} a buy in one pool and a sell in another, one transaction {'\\u2014'} counts twice. Each transaction once: <b>{fmtUSD(D.txUsd)}</b>, bots <b>{vsPct(D.txBotShare)}</b>.</>\n"
            "                      :<>Each transaction counted once. Counting every swap like DexScreener: <b>{fmtUSD(D.swapUsd)}</b>, bots <b>{vsPct(D.swapBotShare)}</b>.{D.protoUsd>0&&<> UFO{'\\u2019'}s own buy-and-burn swaps ({fmtUSD(D.protoUsd)}) are not counted as anyone{'\\u2019'}s.</>}</>}</div>\n"
            "                    {D.feeT>0&&<div className=\"mt-1\">+ <b>{fmtUSD(D.feeT)}</b> in fees from sends between wallets and staking moves ({vsPct(D.feeTot>0?D.feeT/D.feeTot:null)})</div>}\n"
            "                  </div>}")
rep(OLD_REST, NEW_REST, "Counted like DexScreener: every swap in every pool")

rep("The sums count each transaction once and the fees are read from the chain, so a bot{'\\u2019'}s loop (two swaps, one fee) is no longer counted twice.",
    "{D.count==='swaps'?<>The volume counts every swap, the way DexScreener does (EACH TX counts a bot{'\\u2019'}s loop {'\\u2014'} two swaps, one fee {'\\u2014'} once), and the fees are read from the chain.</>"
    ":<>The sums count each transaction once and the fees are read from the chain, so a bot{'\\u2019'}s loop (two swaps, one fee) is not counted twice.</>}",
    "The volume counts every swap, the way DexScreener does")

P.write_text(s)
print(f'{edits} edit(s)')
