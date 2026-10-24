#!/usr/bin/env python3
"""Portfolio: the holder rank of ALL counted wallets combined (2026-10-24, Shaka: "when multiple wallets are selected … show the
ranking as if all wallets were one … in the same place where we show the ranking details of a single wallet").
Idempotent, from the repo root:   python3 tools/pf-rank-combined.py   (twice: the second run must print "0 edit(s)")

  1. PfLeagues.jsx  pfRankAll — the counted wallets' balances added up and ranked against holder-ranks.json WITHOUT each of those
                    wallets' own entries (the e9 rule, per wallet: the list is up to 2 h old). PfRankRow's label joins its aria-label.
  2. PortfolioV2.jsx the League box's rank row: one wallet → as before; two or more → "ALL N WALLETS COMBINED  #r  ▲ x more to
                    pass #r-1", opening the rank window on the combined view.
  3. PfRank.jsx     the rank window: an "All N combined" pick first in the wallet picker. Combined = TODAY, COMBINED, BEST WALLET
                    ALONE, PLACES GAINED, TO PASS, WHAT IT TAKES + the calculator. No chart: the rank index is per address (a rank per
                    wallet per day, no balances), so a combined history cannot be built from it — the window says so.
  Two fixes found on the way (both live since Audit IV batch 5 / 6):
  4. pfRank's guard `if(!t||…||!(bal>0))return null;` sat behind batch 5's `// e27` comment on the same line → commented out: a
     stale token or a failed list read made pfRank throw, and a 0 balance got a rank.
  5. usePfRanks read d.tokens[tok] before the e40 "failed" check, so a failed holder-ranks.json read crashed the whole page
     ("Something went wrong … reading 'PTGC'").
Then tools/pf-v2.py splices the fragments into portfolio.html.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

PL, PR, PV = 'tools/pf-v2/PfLeagues.jsx', 'tools/pf-v2/PfRank.jsx', 'tools/pf-v2/PortfolioV2.jsx'

# ---------------- 4 + 5: the two fixes ----------------
edit(PL, "      const rdAt=tok=>Date.parse((d&&d.tokens[tok]&&d.tokens[tok].readAt)||(d&&d.generatedAt));",
         "      const rdAt=tok=>Date.parse((d&&d.tokens&&d.tokens[tok]&&d.tokens[tok].readAt)||(d&&d.generatedAt));   // 2026-10-24: a failed read has no tokens (it crashed the page)")
edit(PL, "&&ranks.tokens&&ranks.tokens[tok];   // e27: per-token stalenessif(!t||!Array.isArray(t.b)||!(bal>0))return null;",
         "&&ranks.tokens&&ranks.tokens[tok];   // e27: per-token staleness\n      if(!t||!Array.isArray(t.b)||!(bal>0))return null;   // 2026-10-24: this guard had ended up behind the comment above")

# ---------------- 1: pfRankAll + the row's label in its aria-label ----------------
edit(PL, "    const pfPassAmt=v=>v>=1?pfAbbr(v):String(+v.toFixed(6));",
'''    /* 2026-10-24 (Shaka: "show the ranking as if all wallets were one"): the counted wallets' balances added up and ranked against
       the list WITHOUT each of those wallets' own entries (e9, per wallet — the chain lists them apart, and an entry can be up to 2 h
       old, so a wallet that sold could otherwise sit above its own total). Wallets holding 0 are still looked up (a stale entry of
       a wallet that sold everything is dropped too). items = [{addr, bal}] for the counted wallets that read.
       → null (no usable list / nothing held) or {r, pass, list (the list it was ranked in), bal (the total)} */
    const pfRankAll=(ranks,tok,items)=>{const t=ranks&&!ranks.stale&&!(ranks.staleTok&&ranks.staleTok[tok])&&ranks.tokens&&ranks.tokens[tok];
      if(!t||!Array.isArray(t.b))return null;
      const its=(items||[]).filter(Boolean),bal=its.reduce((s,x)=>s+(x.bal>0?x.bal:0),0);if(!(bal>0))return null;
      const b=t.b,T=t.t,drop=new Set();
      if(typeof T==='string'&&T.length===b.length*6)its.forEach(({addr,bal:wb})=>{if(!addr)return;
        const tag=String(addr).toLowerCase().slice(2,8),js=[];let i=T.indexOf(tag);while(i>=0){if(i%6===0&&!drop.has(i/6))js.push(i/6);i=T.indexOf(tag,i+1);}
        if(!js.length)return;const k=pfRankKey(wb>0?wb:0);drop.add(js.reduce((p,q)=>Math.abs(b[q]-k)<Math.abs(b[p]-k)?q:p));});   // a shared tag: the entry nearest this wallet's balance
      const list=drop.size?b.filter((v,j)=>!drop.has(j)):b;
      const x=pfRankKey(bal);let lo=0,hi=list.length;while(lo<hi){const m=(lo+hi)>>1;if(list[m]>x)lo=m+1;else hi=m;}
      const d=lo>0?list[lo-1]-x:null;return{r:lo+1,pass:d==null?null:(x>=1&&list[lo-1]>=1?d+1:d+1e-6),list,bal};};
    const pfPassAmt=v=>v>=1?pfAbbr(v):String(+v.toFixed(6));''')
edit(PL, "aria-label={`${tok} holder rank #${x.r.toLocaleString('en-US')}, open the rank history`}><span className=\"st\">",
         "aria-label={`${label?label.toLowerCase()+': ':''}${tok} holder rank #${x.r.toLocaleString('en-US')}, open the rank history`}><span className=\"st\">")
edit(PL, "    /* H3: the row under the league bar — shown only when ONE wallet is counted (2026-10-21 pm: \"all N wallets as one\" dropped) */",
         "    /* H3: the row under the league bar — ONE wallet counted: its rank; two or more (2026-10-24, Shaka — he had dropped \"all N\n       wallets as one\" on 2026-10-21 pm and asked for it back): \"ALL N WALLETS COMBINED\" + pfRankAll */")

# ---------------- 2: the League box rows ----------------
edit(PV, "      const rkOne=counted.length===1;",
'''      const rkOne=counted.length===1;
      /* 2026-10-24: two or more counted → the League box ranks them as ONE wallet (pfRankAll) and the row opens the window combined */
      const rkItems=tok=>counted.map(w=>{const d=portfolioData[w.address.toLowerCase()];return d&&!d.error?{addr:w.address,bal:tok==='PTGC'?(d.ptgc.totalHolding||0):(d.ufo.balance||0)}:null;}).filter(Boolean);
      const rkLabel=`ALL ${counted.length} WALLETS COMBINED`;''')
for T, B in (('PTGC', 'pt.totalHolding'), ('UFO', 'uf.balance')):
    edit(PV, f"rankRow={{rkOne&&<PfRankRow tok=\"{T}\" ",
             f"rankRow={{counted.length>1?<PfRankRow tok=\"{T}\" label={{rkLabel}} x={{pfRankAll(ranks,'{T}',rkItems('{T}'))}} note={{rkNote('{T}',{B})}} open={{()=>setRkWin({{tok:'{T}',all:true}})}}/>:rkOne&&<PfRankRow tok=\"{T}\" ")
edit(PV, "data={portfolioData} ranks={ranks} txs={txs} prices={prices} close={()=>setRkWin(null)}/>}",
         "all={!!(rkWin&&rkWin.all)} data={portfolioData} ranks={ranks} txs={txs} prices={prices} close={()=>setRkWin(null)}/>}")

# ---------------- 3: the rank window ----------------
edit(PR, "    const usePfRankHist=(tok,addr)=>{const[d,setD]=useState({state:'loading'});\n      useEffect(()=>{let live=true;setD({state:'loading'});pfrLoad(",
         "    const usePfRankHist=(tok,addr)=>{const[d,setD]=useState({state:addr?'loading':'none'});   // no addr (the combined view) = no history to read\n      useEffect(()=>{let live=true;if(!addr){setD({state:'none'});return;}setD({state:'loading'});pfrLoad(")
edit(PR, "const P={trophy:", "const P={stack:'M4 6h16v4H4zm0 8h16v4H4z',trophy:")
edit(PR, "    const PfRankModal=({tok:tok0,wallets,data,ranks,txs,prices,close})=>{",
         "    const PfRankModal=({tok:tok0,wallets,all,data,ranks,txs,prices,close})=>{")
edit(PR, "      const[sel,setSel]=useState(()=>wallets[0]&&wallets[0].address.toLowerCase());",
         "      const[sel,setSel]=useState(()=>all&&wallets.length>1?'*':wallets[0]&&wallets[0].address.toLowerCase());   // '*' = all the counted wallets combined (2026-10-24)")
edit(PR, '''      const w=wallets.find(x=>x.address.toLowerCase()===sel)||wallets[0];
      const d=w&&data[w.address.toLowerCase()];
      const bal=d&&!d.error?(isU?(d.ufo.balance||0):(d.ptgc.totalHolding||0)):0;
      const live=pfRank(ranks,tok,bal,w&&w.address);   // e9: without the wallet's own (possibly stale) entry
      const h=usePfRankHist(tok,w?w.address:'0x');''', '''      /* 2026-10-24: the combined view — every counted wallet that read, added up (the same sum as the League box) and ranked as one
         (pfRankAll); `w` is null there. BEST WALLET ALONE / PLACES GAINED compare it with the best single wallet's own rank. */
      const comb=sel==='*'&&wallets.length>1;
      const rd=wallets.map(x=>({x,z:data[x.address.toLowerCase()]})).filter(o=>o.z&&!o.z.error);
      const w=comb?null:(wallets.find(x=>x.address.toLowerCase()===sel)||wallets[0]);
      const d=comb?(rd.length?{ptgc:{totalHolding:rd.reduce((s,o)=>s+(o.z.ptgc.totalHolding||0),0)},ufo:{balance:rd.reduce((s,o)=>s+(o.z.ufo.balance||0),0)}}:null):w&&data[w.address.toLowerCase()];
      const bal=d&&!d.error?(isU?(d.ufo.balance||0):(d.ptgc.totalHolding||0)):0;
      const balOf=z=>isU?(z.ufo.balance||0):(z.ptgc.totalHolding||0);
      const live=comb?pfRankAll(ranks,tok,rd.map(o=>({addr:o.x.address,bal:balOf(o.z)}))):pfRank(ranks,tok,bal,w&&w.address);   // e9: without the wallet's own (possibly stale) entry
      const solo=comb?rd.map(o=>{const r=pfRank(ranks,tok,balOf(o.z),o.x.address);return r?{w:o.x,r:r.r}:null;}).filter(Boolean).sort((p,q)=>p.r-q.r)[0]||null:null;
      const nHold=comb?rd.filter(o=>balOf(o.z)>0).length:0;
      const h=usePfRankHist(tok,comb?null:w?w.address:'0x');''')
edit(PR, "      const list=ranks&&ranks.tokens&&ranks.tokens[tok]&&ranks.tokens[tok].b||[];",
         "      const list=comb?(live?live.list:[]):ranks&&ranks.tokens&&ranks.tokens[tok]&&ranks.tokens[tok].b||[];   // combined: the list it was ranked in (own entries out)")
edit(PR, "<div className=\"sub\"><span>{w?(w.name||pfAddr(w.address)):'—'}{w&&w.name?<> {'·'} {pfAddr(w.address)}</>:null} {'·'} {pfAbbr(bal)} {tok}</span>",
         "<div className=\"sub\"><span>{comb?<>All {wallets.length} wallets combined</>:<>{w?(w.name||pfAddr(w.address)):'—'}{w&&w.name?<> {'·'} {pfAddr(w.address)}</>:null}</>} {'·'} {pfAbbr(bal)} {tok}</span>")
edit(PR, "{wallets.length>1&&<div className=\"pf2-edsel\"><div className=\"ws\">{wallets.map(",
         "{wallets.length>1&&<div className=\"pf2-edsel\"><div className=\"ws\"><button key=\"*\" className={comb?'on':''} aria-pressed={comb} onClick={()=>setSel('*')}>All {wallets.length} combined</button>{wallets.map(")
edit(PR, "                {chg==null?<span className=\"flat\">{live?'—':'not holding '+tok}</span>",
         "                {comb?<span className=\"flat\">{live?`if your ${wallets.length} wallets were one`:`none of these wallets hold ${tok}`}</span>:chg==null?<span className=\"flat\">{live?'—':'not holding '+tok}</span>")
edit(PR, "                <em>{per==='LIFE'?'since the first day held':`vs ${nDays} days ago`}</em></div>\n              <div className=\"tiles\">",
'''                <em>{comb?'from today’s holder list':per==='LIFE'?'since the first day held':`vs ${nDays} days ago`}</em></div>
              {comb?<div className="tiles">
                <div className="tl"><div className="l"><PfIco k="stack"/>COMBINED</div>{(()=>{const v=bal>0?pfAbbr(bal).replace(/\\.00(?=[KMBT]$)/,''):'—';return <div className="v" style={v.length>6?{fontSize:21}:undefined}>{v}</div>;})()}<div className="s">{tok} in {nHold} wallet{nHold===1?'':'s'}</div></div>
                <div className="tl"><div className="l"><PfIco k="trophy"/>BEST WALLET ALONE</div><div className="v">{solo?'#'+solo.r.toLocaleString('en-US'):'—'}</div><div className="s">{solo?(solo.w.name||pfAddr(solo.w.address)):''}</div></div>
                <div className="tl"><div className="l"><PfIco k="chart"/>PLACES GAINED</div><div className="v">{live&&solo?(solo.r-live.r).toLocaleString('en-US'):'—'}</div><div className="s">{live&&solo?'vs your best wallet alone':''}</div></div>
                <div className="tl"><div className="l"><PfIco k="bars"/>{live&&live.pass!=null?`TO PASS #${(live.r-1).toLocaleString('en-US')}`:'TO PASS'}</div><div className="v">{live?live.pass==null?'—':pfPassAmt(live.pass):'—'}</div><div className="s">{live?live.pass==null?'nobody above you':tok+' more':''}</div></div>
              </div>:<div className="tiles">''')
# the tiles' closing: the single-wallet grid ends right before </div> of .hero — close the ternary there
edit(PR, '''<div className="s">{full?`of ${tracked.toLocaleString('en-US')} held`:''}</div></div>
              </div>
            </div>''', '''<div className="s">{full?`of ${tracked.toLocaleString('en-US')} held`:''}</div></div>
              </div>}
            </div>''')
edit(PR, "            <div className=\"ch\"><div className=\"chh\"><span><PfIco k=\"chart\"/>RANK OVER TIME</span><div className=\"pp\"",
         "            {comb&&<div className=\"ch\"><div className=\"chh\"><span><PfIco k=\"chart\"/>RANK OVER TIME</span></div><div className=\"pf2-hwait\" style={{height:110}}><div>Rank history is kept per wallet {'—'} the chain lists your wallets separately, so there is no combined history. Pick a wallet above to see its chart.</div></div></div>}\n            {!comb&&<div className=\"ch\"><div className=\"chh\"><span><PfIco k=\"chart\"/>RANK OVER TIME</span><div className=\"pp\"")
edit(PR, "<span className=\"r\">one point per UTC day {'·'} today{'’'}s point is live</span></div></div>",
         "<span className=\"r\">one point per UTC day {'·'} today{'’'}s point is live</span></div></div>}")
edit(PR, "DAO{isU?' and UFO OA':''} wallets {'·'} history rebuilt",
         "DAO{isU?' and UFO OA':''} wallets{comb?<> {'·'} your {wallets.length} wallets added up and ranked as if they were one</>:null} {'·'} history rebuilt")

out = subprocess.run([sys.executable, 'tools/pf-v2.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'pf-rank-combined: {n} edit(s), portfolio.html {sha("portfolio.html")}')
