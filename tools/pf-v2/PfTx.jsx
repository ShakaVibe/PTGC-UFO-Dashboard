    /* ===== Portfolio v2 — RECENT TRANSACTIONS (round 9, rewritten through round 27) =====
       PulseScan's token-transfer list per counted wallet and token (PTGC, UFO) — /api/v2/addresses/{w}/token-transfers, CORS
       open, 50 per page, paged back up to a year (round 18), cached per wallet+token in localStorage (round 24). Transfers of
       one tx + token are netted for the wallet (a UFO sell is the pair leg + the fee leg → one "Sell"). Types (pftClassify):
       Claim (from the staking contract, named by function), Unstake, Buy / Sell (a contract counterparty AND another token
       moved in the tx), Add / Remove LP, Move (between two of YOUR wallets), Receive / Send. Value = amount × that hour's /
       day's price (the history's price files). Shown as an activity feed (round 17) and handed to the value chart's strip
       and the Details window (rows, flows, coverage). Expects from the other files: PF_ADDR, pfAddr, pfCopy (PfLeagues),
       PFH_TOK, pfhPrices, pfhPriceAt (PfHistory). */
    /* round 18 (Shaka: "a lot of dots are still missing on the chart"): ONE page (the latest 50 transfers) was all we read, and a
       busy wallet's 50 reach back only hours — so the chart had no trades for most of the week. Now each wallet + token is read
       page by page back a year (PFT_BACK) or PFT_PAGES pages, whichever comes first: page 1 for everyone first (the list paints
       fast), then the deeper pages in the background. A cached entry keeps {items, next (PulseScan's next_page_params), done};
       a refresh reads only the newest page(s) and merges them in until it meets what is already cached. */
    /* round 27 (audit E6): the one place that says whether a wallet+token's transaction list reaches back to time t.
       cov[addr|TOK]: undefined = not read yet · 0 = PulseScan ran out of pages (whole history) · a timestamp = complete back to it */
    const pftCovered=(txs,addr,tok,t)=>{const c=txs&&txs.cov?txs.cov[addr+'|'+tok]:undefined;return c!==undefined&&t>=c;};
    const PFT_LS='grays_pf_tx_v4:';   // v4 (round 24): one key per wallet+token (v3 was one blob)
    const PFT_API='https://api.scan.pulsechain.com/api/v2/addresses/';
    const PFT_STAKING=PF_ADDR.STAKING.toLowerCase();
    const PFT_TTL=5*60e3,PFT_BACK=365*864e5,PFT_PAGES=20;
    try{['grays_pf_tx_v1','grays_pf_tx_v2','grays_pf_tx_v3'].forEach(k=>localStorage.removeItem(k));}catch(e){}
    /* round 23 (audit A5): the cache used to be WIPED on a quota error (a 20-wallet portfolio is ~4 MB), so big portfolios never
       kept one and re-read everything every visit. Now: saves are debounced, and on quota the least recently read wallet+token
       entries are dropped one at a time until it fits. */
    /* round 24 (audit B3): one localStorage key per wallet+token (PFT_LS + key) — a landed page writes only its own entry
       instead of re-serialising the whole multi-MB cache; on quota the least recently read OTHER entries go first. */
    const pftCache=(()=>{const m={};let loaded=false,t=null;const dirty=new Set();
      const load=()=>{if(loaded)return;loaded=true;try{for(let i=localStorage.length-1;i>=0;i--){const k=localStorage.key(i);if(k&&k.startsWith(PFT_LS)){try{m[k.slice(PFT_LS.length)]=JSON.parse(localStorage.getItem(k));}catch(e){}}}}catch(e){}};
      const write=()=>{for(const k of [...dirty]){dirty.delete(k);const e=m[k];if(!e)continue;for(let i=0;i<40;i++){try{localStorage.setItem(PFT_LS+k,JSON.stringify(e));break;}
        catch(err){const ks=Object.keys(m).filter(x=>x!==k);if(!ks.length)break;const old=ks.sort((a,b)=>(m[a].at||0)-(m[b].at||0))[0];delete m[old];try{localStorage.removeItem(PFT_LS+old);}catch(e2){}}}}};
      return{get(){load();return m;},save(k){dirty.add(k);clearTimeout(t);t=setTimeout(write,400);},flush(){clearTimeout(t);write();}};})();
    const pftPage=async(addr,tok,next)=>{
      const ac=new AbortController();const to=setTimeout(()=>ac.abort(),25000);
      try{
        const q=next?'&'+Object.entries(next).map(([k,v])=>encodeURIComponent(k)+'='+encodeURIComponent(v)).join('&'):'';
        let r=await fetch(`${PFT_API}${addr}/token-transfers?type=ERC-20&token=${PFH_TOK[tok]}${q}`,{signal:ac.signal});
        if(r.status===429){await new Promise(res=>setTimeout(res,2500));r=await fetch(`${PFT_API}${addr}/token-transfers?type=ERC-20&token=${PFH_TOK[tok]}${q}`,{signal:ac.signal});}   // round 24 (audit B6): one polite retry when PulseScan rate-limits
        if(!r.ok)throw new Error('HTTP '+r.status);
        const j=await r.json();
        const items=(j.items||[]).map(x=>({h:x.tx_hash,t:Date.parse(x.timestamp),f:(x.from&&x.from.hash||'').toLowerCase(),to:(x.to&&x.to.hash||'').toLowerCase(),fc:!!(x.from&&x.from.is_contract),tc:!!(x.to&&x.to.is_contract),m:x.method||'',v:(()=>{try{return Number(BigInt(x.total.value))/Math.pow(10,+x.total.decimals||18);}catch(e){return 0;}})(),li:x.log_index}));
        return{items,next:j.next_page_params||null};
      }finally{clearTimeout(to);}
    };
    const pftKey=i=>i.h+'|'+(i.li!=null?i.li:i.f+i.to+i.v);
    const pftDone=(e)=>!e.next||e.pages>=PFT_PAGES||(e.items.length&&Date.now()-e.items[e.items.length-1].t>PFT_BACK);
    /* page 1 (fresh or merged into the cache) */
    const pftFetch=async(addr,tok,force)=>{
      const k=addr+'|'+tok,c=pftCache.get(),hit=c[k];
      if(!force&&hit&&Date.now()-hit.at<PFT_TTL)return hit;
      try{
        let pg=await pftPage(addr,tok,null),e;
        if(hit&&hit.items.length){
          const have=new Set(hit.items.map(pftKey));let fresh=pg.items.filter(i=>!have.has(pftKey(i))),n=1;
          /* the newest page didn't reach the cache yet → keep reading (a few pages at most) */
          while(fresh.length===pg.items.length&&pg.next&&n<5){pg=await pftPage(addr,tok,pg.next);n++;fresh=fresh.concat(pg.items.filter(i=>!have.has(pftKey(i))));}
          e=fresh.length===pg.items.length*n&&pg.next?{at:Date.now(),items:fresh,next:pg.next,pages:n}   // still a gap → start over from here
            :{...hit,at:Date.now(),items:fresh.concat(hit.items)};
        }else e={at:Date.now(),items:pg.items,next:pg.next,pages:1};
        e.done=pftDone(e);c[k]=e;pftCache.save(k);return e;
      }catch(err){if(hit)return hit;throw err;}
    };
    /* one more (older) page */
    const pftMore=async(addr,tok)=>{
      const k=addr+'|'+tok,c=pftCache.get(),e=c[k];if(!e||e.done)return e;
      const pg=await pftPage(addr,tok,e.next);
      const have=new Set(e.items.map(pftKey));
      const n={...e,items:e.items.concat(pg.items.filter(i=>!have.has(pftKey(i)))),next:pg.next,pages:(e.pages||1)+1};
      n.done=pftDone(n);c[k]=n;pftCache.save(k);return n;
    };
    /* round 13 (Shaka: "double check your types … those ones from 0bd0 show as Stake, but they were sells"). Checked live on
       PulseScan: EVERY PTGC transfer — sells, buys, plain sends — splits off fee legs to the token contract, the staking contract
       and the burn address, so "a leg went to the staking contract" meant nothing; and routers often show a bare selector
       (0xe25d4a18) instead of a "swap…" method name, so the method can't be trusted either. Now: fee legs are left out when
       finding who the wallet traded WITH (they still count in the amount — it is what left the wallet); the main counterparty is
       the biggest remaining leg. From the staking contract = Claim; one of your own wallets = Move; method add/removeLiquidity =
       Add LP / Remove LP; a CONTRACT (DEX pair, router, aggregator) = Buy (tokens in) / Sell (tokens out); a person = Receive / Send. */
    /* round 14 — lessons from pulsechain_monitor.py (the trade monitor we built earlier, every rule verified on chain there):
       · claims are named by the FUNCTION, not the contract (staking and locking share 0xc71f…): withdrawReward = staking
         rewards, withdrawRewardLock = lock rewards. (round 14b, Shaka: the DAO has nothing to do with a personal wallet —
         the monitor's DAO claim / DAO lock rules are left out.)
       · PTGC staking is balance-lock style: an UNSTAKE (withdraw(uint256) on the staking contract) moves no principal — only the
         reward out and the unstake fee in — so it is labelled Unstake and its principal is read from the call (see pftDetail).
       · the 1 % HOLDERS share of the fee (reflections) leaves the sender with NO Transfer event — it is paid by shrinking
         everyone's balance-rate, not by a transfer. PTGC fee 5 %: emitted = 2.5 % to the token contract (2 % DAO + 0.5 %
         liquidity), 1 % to the staking contract, 0.5 % to 0x…369 (burn); hidden = 1 % holders = the same size as the staking
         leg. UFO fee 6 %: emitted = 5 % to the UFO contract (burns + liquidity); hidden = 1 % holders = that leg ÷ 5.
         Checked on chain 2026-10-13: a PTGC sell (tx 0x91968a23…, block 27,789,557) logged 14,850 out, the wallet's balanceOf
         fell 15,000; three UFO sells fell by emitted + exactly the fee leg ÷ 5. Sell / Send amounts are grossed up by it.
       · LP adds made through a helper / zapper look like a Sell — the tell is LP tokens minted to the wallet in the same tx
         (pftDetail checks the tx's other transfers). */
    const PFT_FEE=new Set(['0x0000000000000000000000000000000000000000','0x0000000000000000000000000000000000000369','0x000000000000000000000000000000000000dead',PFT_STAKING]);
    const PFT_CLAIM_SUB={withdrawreward:'staking',withdrawrewardlock:'lock'};
    const pftClassify=(legs,addr,own,tok)=>{
      let net=0;legs.forEach(l=>{if(l.to===addr)net+=l.v;if(l.f===addr)net-=l.v;});
      const tokAddr=PFH_TOK[tok].toLowerCase();
      const m=(legs[0]&&legs[0].m||'').toLowerCase();
      const fromSt=legs.some(l=>l.f===PFT_STAKING&&l.to===addr);
      /* round 23 (audit A12, checked on PulseScan): the staking contract's withdraw(uint256) is NOT decoded there — real unstakes
         come back with method null and the bare selector 0x2e1a7d4d, so match the selector as well */
      if((m==='withdraw'||m==='0x2e1a7d4d')&&legs.some(l=>l.f===PFT_STAKING||l.to===PFT_STAKING))return{type:'Unstake',net};
      if(fromSt)return{type:'Claim',net,sub:PFT_CLAIM_SUB[m]||''};
      const main=legs.filter(l=>(l.to===addr||l.f===addr)).map(l=>l.to===addr?{a:l.f,c:l.fc,v:l.v}:{a:l.to,c:l.tc,v:l.v})
        .filter(x=>x.a&&x.a!==addr&&x.a!==tokAddr&&!PFT_FEE.has(x.a)).sort((x,y)=>y.v-x.v)[0];
      /* the hidden reflection slice of a send (see above) */
      if(net<0){if(tok==='PTGC'){const stLeg=legs.filter(l=>l.f===addr&&l.to===PFT_STAKING).reduce((a,l)=>a+l.v,0);net-=stLeg;}
        else{const fee=legs.filter(l=>l.f===addr&&l.to===tokAddr).reduce((a,l)=>a+l.v,0);const sp=window.ufoSplitAt?window.ufoSplitAt(legs[0].t,true):[100,500];net-=fee*sp[0]/sp[1];}}   // Audit V v31: the split in force then (÷ 5 at the launch rates)
      let type;
      if(main&&own.has(main.a))type='Move';
      else if(/addliquidity/.test(m))type='Add LP';
      else if(/removeliquidity/.test(m))type='Remove LP';
      else if(main&&main.c)type=net>=0?'Buy':'Sell';
      else type=net>=0?'Receive':'Send';
      return{type,net,cp:main&&main.a};
    };
    /* per-tx detail, fetched only for the rows on screen that need it, cached for good (past txs never change):
       Sell / Buy → was it really an LP add / remove through a helper (LP tokens minted to / returned by the wallet)?
       Unstake → the principal, decoded from withdraw(uint256)'s argument. */
    const PFT_DLS='grays_pf_txd_v2';   // v2 (round 23): + swap (another token moved in the tx)
    try{localStorage.removeItem('grays_pf_txd_v1');}catch(e){}
    const pftD=(()=>{let c=null;return{get(){if(c)return c;try{c=JSON.parse(localStorage.getItem(PFT_DLS)||'{}')||{};}catch(e){c={};}return c;},save(){try{localStorage.setItem(PFT_DLS,JSON.stringify(c));}catch(e){}}};})();
    const pftDetail=async(h,addr,tok)=>{
      const c=pftD.get(),k=h+'|'+addr+'|'+tok;if(c[k])return c[k];
      const g=async u=>{const ac=new AbortController();const to=setTimeout(()=>ac.abort(),20000);try{const r=await fetch(PFT_API.replace('addresses/','')+u,{signal:ac.signal});if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}finally{clearTimeout(to);}};
      const out={};
      const tx=await g('transactions/'+h);
      const raw=tx&&tx.raw_input||'';
      if(raw.startsWith('0x2e1a7d4d')&&raw.length>=74){try{out.principal=Number(BigInt('0x'+raw.slice(10,74)))/1e18;}catch(e){}}
      const tt=await g('transactions/'+h+'/token-transfers');
      /* round 23 (audit A13): a real buy / sell always moves ANOTHER token in the same tx (WPLS, DAI, the other side of the pair).
         A transfer to / from a contract with nothing else moving is a send / receive (a Safe, a bridge, a vesting contract…). */
      const mine=(PFH_TOK[tok]||'').toLowerCase();
      out.swap=(tt.items||[]).some(x=>((x.token&&x.token.address)||'').toLowerCase()!==mine&&!((x.token&&x.token.symbol)==='PLP'));
      (tt.items||[]).forEach(x=>{const sym=(x.token&&x.token.symbol||''),nm=(x.token&&x.token.name||'');if(!(sym==='PLP'||/\bLP\b/.test(nm)))return;
        const f=(x.from&&x.from.hash||'').toLowerCase(),t=(x.to&&x.to.hash||'').toLowerCase();
        if(t===addr&&/^0x0{40}$/.test(f))out.lp='add';else if(f===addr)out.lp='remove';});
      c[k]=out;pftD.save();return out;
    };
    /* round 28 (Shaka: "mouse over or click on the little daily bars and it pops a window showing the day's moves"): the feed
       row is a shared component now — Recent Transactions AND the Value History day window (PfDayModal, PfHistory.jsx) draw
       the same rows. pftNameOf(wallets) → a→label; pftWhoOf(nameOf,r) → "A → B" for moves. */
    const PFT_VERB={Buy:'Bought',Sell:'Sold',Claim:'Claimed','Add LP':'Added to LP','Remove LP':'Removed from LP',Move:'Moved',Receive:'Received',Send:'Sent',Unstake:'Unstaked'};
    const PFT_AMT={Sell:'neg',Send:'neg','Add LP':'neg',Buy:'pos',Receive:'pos',Claim:'pos','Remove LP':'pos'};
    const PFT_VAL={Sell:'received',Buy:'paid',Claim:'earned'};
    /* Audit V v10 (2026-10-25): the fee comes off the transfer, so a BUY that landed N tokens paid for N ÷ (1 − fee) (more when a
       router split it across pools), and a SELL of N tokens got PLS for N × (1 − fee). Every other type is valued at N × price. */
    const pftUsd=(type,amt,p,tok)=>{if(p==null)return null;const f=PF_BUY_FEE[tok]||0;return Math.abs(amt)*p*(type==='Buy'?1/(1-f):type==='Sell'?(1-f):1);};
    const pftTm=t=>new Date(t).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'});
    const pftNameOf=wallets=>{const m={};wallets.forEach(w=>{m[w.address.toLowerCase()]=w.name||pfAddr(w.address);});return a=>m[a]||(a?a.slice(0,6)+'…'+a.slice(-4):'');};
    const pftWhoOf=(nameOf,r)=>r.type==='Move'&&r.cp?(r.dir>=0?nameOf(r.cp)+' → '+nameOf(r.addr):nameOf(r.addr)+' → '+nameOf(r.cp)):nameOf(r.addr);
    /* round 35 (Shaka: "so much dead space between the text on the left and the dollar value on the right" — picked A of
       mock-feed-v2): a LEDGER row — icon · action (+ note) · wallet · price per token · time · value · link, column headers above
       (PfTxColh), a soft zebra by `z`. The phone and the day window drop the price column (pf2.css). */
    const PfTxRow=({r,who,cp,onCopy,z})=>{const[c,g]=PFT_TYPE[r.type]||['#fff','•'];
      const note=r.type==='Claim'&&r.sub?'from '+r.sub:r.unstake?'released from staking':r.type==='Move'?'between your wallets':'';
      const px=(r.type==='Buy'||r.type==='Sell')&&r.usd!=null&&Math.abs(r.amt)>0?r.usd/Math.abs(r.amt):null;
      return(<div className={`pf2-fr${z?' z':''}`}>
        <div className="ic" style={{color:c,borderColor:c+'88',background:c+'1f'}}>{g}<img src={r.tok==='PTGC'?TOKENS.PTGC.logo:TOKENS.UFO.logo} alt={r.tok}/></div>
        <div className="m"><div className="t1">{PFT_VERB[r.type]||r.type} <em className={PFT_AMT[r.type]||''}>{pfAbbr(Math.abs(r.amt))}</em> {r.tok}</div>
          <div className="t2">{note&&<span className="nt">{note}</span>}<span className="tmi">{note?' \u00B7 ':''}{pftTm(r.t)}</span></div></div>
        <div className="w"><span className={/^0x/i.test(who)?'wc mono':'wc'}>{who}</span><button className={`cp${cp?' ok':''}`} onClick={()=>onCopy(r)} title={`Copy ${r.addr}`} aria-label={`Copy wallet address ${r.addr}`}>{cp?'✓':'⧉'}</button><span className="tmw">{'\u00B7'} {pftTm(r.t)}</span></div>
        <div className="px">{px!=null?<>{fmtPriceNode(px)}<small>per {r.tok}</small></>:<span className="na">{'\u2014'}</span>}</div>
        <div className="tm">{pftTm(r.t)}</div>
        <div className="v">{fmtDollar(r.usd)}<small>{PFT_VAL[r.type]||'value'}</small></div>
        <a className="lk" href={`https://scan.pulsechain.com/tx/${r.h}`} target="_blank" rel="noopener noreferrer" title="Open on PulseScan" aria-label="Open this transaction on PulseScan">{'↗'}</a>
      </div>);};
    const PfTxColh=()=><div className="pf2-colh" aria-hidden="true"><span></span><span>ACTION</span><span>WALLET</span><span>PRICE</span><span>TIME</span><span className="r">VALUE</span><span></span></div>;
    /* the "copied ✓" flash shared by the feed and the day window: returns [copiedId, copy(r)] */
    const usePftCopy=()=>{const[cp,setCp]=useState(null);
      const copy=React.useCallback(r=>{pfCopy(r.addr).then(ok=>{if(!ok)return;setCp(r.id);setTimeout(()=>setCp(c=>c===r.id?null:c),1400);});},[]);
      return[cp,copy];};
    const PFT_TYPE={Buy:['#39E15A','▲'],Sell:['#FF6B73','▼'],Receive:['#39E15A','↙'],Send:['#FF6B73','↗'],Claim:['#5AB8FF','⬇'],'Add LP':['#F2D35B','\u2295'],Unstake:['#B9C4FF','\u21E7'],'Remove LP':['#F2D35B','\u2296'],Move:['#B26BFF','⇄']};
    const PfRecentTx=({wallets,prices,onRows,onProgress})=>{   // round 30: onProgress({done,total,pd,pt,ud,ut,failed}) during the first read (the chart's loader)
      const pxNow=React.useRef(prices);pxNow.current=prices;
      const[st,setSt]=useState({state:'idle',rows:[],failed:0,done:0,total:0});
      const[lim,setLim]=useState(10);      // round 17: rows shown (10, +30 per Show more)
      const[flt,setFlt]=useState('All');    // round 17: filter chip
      const[cp,copy]=usePftCopy();         // round 17: the row whose wallet address was just copied
      const tick=usePfTick();               // round 34: the "read N min ago" stamp
      const[nonce,setNonce]=useState(0);
      const force=React.useRef(false);   // round 24 (audit B2): Refresh re-reads page 1 ONCE (nonce>0 used to force it on every later toggle)
      const secRef=React.useRef(null);
      const key=wallets.map(w=>w.address.toLowerCase()).sort().join(',');
      useEffect(()=>{
        if(!wallets.length){setSt({state:'empty',rows:[],failed:0,done:0,total:0});return;}
        let live=true,tellT=null;const forceNow=force.current;force.current=false;
        (async()=>{
          const own=new Set(wallets.map(w=>w.address.toLowerCase()));
          const names={};wallets.forEach(w=>{names[w.address.toLowerCase()]=w.name||(w.address.slice(0,6)+'…'+w.address.slice(-4));});
          const jobs=[];wallets.forEach(w=>['PTGC','UFO'].forEach(tok=>jobs.push({addr:w.address.toLowerCase(),tok})));
          const prog=()=>{if(!onProgress||!live)return;const n=t=>jobs.filter(j=>j.tok===t).length,d=t=>got.filter(g=>g.tok===t).length;onProgress({done,total:jobs.length,pd:d('PTGC'),pt:n('PTGC'),ud:d('UFO'),ut:n('UFO'),failed});};
          setSt(s=>({...s,state:s.rows.length?'ok':'loading',done:0,total:jobs.length}));
          const got=[];let failed=0,done=0,q=0,q2=0;
          const px=await pfhPrices().catch(()=>null);
          if(window.ufoRateTimeline)await window.ufoRateTimeline().catch(()=>null);   // Audit V v31
          let flows=[];   // round 20: every tx's net per wallet + token (moves on BOTH sides) — the Earned details' UFO maths
          const build=()=>{
            const rows=[];flows=[];
            got.forEach(({addr,tok,items})=>{
              const by={};items.forEach(it=>{(by[it.h]=by[it.h]||[]).push(it);});
              Object.values(by).forEach(legs=>{const{type,net,cp:mcp,sub}=pftClassify(legs,addr,own,tok);flows.push({addr,tok,t:legs[0].t,net});if(Math.abs(net)<1e-9&&type!=='Move')return;
                const t=legs[0].t;let p=px?pfhPriceAt(px,tok,t):null;
                /* newer than the price files (they refresh hourly) → today's price */
                if(p==null){const ser=px&&px.hourly[tok];const last=ser&&ser.length?ser[ser.length-1][0]:null;const cur=pxNow.current&&pxNow.current[tok==='PTGC'?'ptgc':'ufo'];if(last!=null&&t>=last&&cur>0)p=cur;}   // round 23 (audit A3): never "today's price" for old rows when the price files failed
                const cp=mcp;
                rows.push({id:addr+legs[0].h+tok,t,addr,cp:type==='Move'?cp:null,dir:net>=0?1:-1,tok,type,sub,amt:net,p,usd:pftUsd(type,net,p,tok),h:legs[0].h});});   // round 25 (audit C3): the name is looked up at render, so a rename shows at once
            });
            /* a Move shows once (the receiving side), not twice */
            const seen=new Set();const out=[];
            rows.sort((a,b)=>b.t-a.t).forEach(r=>{if(r.type==='Move'){const k=r.h+r.tok;if(seen.has(k))return;seen.add(k);if(r.amt<0){r.amt=-r.amt;}}out.push(r);});
            return out;
          };
          /* round 18: chart coverage — a wallet + token is complete back to its oldest transfer unless it hit the page cap / a year */
          /* round 23 (audit A4): "complete" only when PulseScan ran out of pages; a list that stopped at the page cap or the
             one-year mark is complete back to its OLDEST item, not to the beginning of time */
          const cov=()=>{const o={};got.forEach(g=>{o[g.addr+'|'+g.tok]=g.full?0:(g.items.length?g.items[g.items.length-1].t:Date.now());});return o;};
          let busy=true,pages=0;   // round 22: the Details window waits on these (busy = older pages still coming; pages = how many read)
          /* round 24 (audit B1): build() ran twice per landed page and every one re-rendered the whole page (~1,500 times for 20
             wallets). Now one build per page, and the parent is told at most ~2× a second (always at the end). */
          let lastRows=null,lastTell=0;
          const tell=(final)=>{if(!onRows||!live)return;const now=Date.now();if(!final&&now-lastTell<500){clearTimeout(tellT);tellT=setTimeout(()=>tell(true),520-(now-lastTell));return;}
            clearTimeout(tellT);lastTell=now;const jd={};got.forEach(g=>{jd[g.addr+'|'+g.tok]=!!g.done;});onRows({rows:lastRows||(lastRows=build()),cov:cov(),jd,failed,flows,busy,pages,prioritize});};
          /* 2026-10-21 (the rank window's "show buys & sells" — Shaka: "anything we can do to make it faster"): the window asks for ITS
             wallet + token first — that job jumps the deep-page queue and the wait-for-scroll before phase 2 is skipped */
          let pri=null,deepRef=null,goNow=null;
          const prioritize=(addr,tok)=>{pri=addr+'|'+tok;if(deepRef){const i=deepRef.findIndex((g,k)=>k>=q2&&g.addr+'|'+g.tok===pri);if(i>q2){const[g]=deepRef.splice(i,1);deepRef.splice(q2,0,g);}}if(goNow)goNow();};
          const worker=async()=>{while(q<jobs.length){const j=jobs[q++];try{const e=await pftFetch(j.addr,j.tok,forceNow);got.push({...j,items:e.items,done:e.done,full:!e.next});}catch(e){failed++;}done++;if(live){lastRows=build();setSt({state:'ok',rows:lastRows,failed,done,total:jobs.length});prog();}}};
          prog();
          await Promise.all([worker(),worker(),worker()]);
          if(!live)return;
          tell(true);
          /* round 24 (audit B7): the deep (older) pages only start once the section has been scrolled into view — or after
             5 s anyway, so the chart's history and the Details window still fill in on a page left open */
          await new Promise(res=>{let done2=false;const go=()=>{if(!done2){done2=true;res();}};goNow=go;if(pri){go();return;}const el=secRef.current;
            if(!el||!('IntersectionObserver' in window)){setTimeout(go,1500);return;}
            const io=new IntersectionObserver(es=>{if(es.some(x=>x.isIntersecting)){io.disconnect();go();}},{rootMargin:'600px'});io.observe(el);setTimeout(()=>{io.disconnect();go();},5000);});
          if(!live)return;
          /* phase 2: the older pages, two at a time, the list and the chart updating as they land */
          const deep=got.filter(g=>!g.done).sort((a,b)=>(a.tok==='UFO'?0:1)-(b.tok==='UFO'?0:1));   // UFO first — the Details window's UFO days need it
          if(pri){const i=deep.findIndex(g=>g.addr+'|'+g.tok===pri);if(i>0){const[g]=deep.splice(i,1);deep.unshift(g);}}deepRef=deep;
          const w2=async()=>{while(q2<deep.length&&live){const g=deep[q2++];while(!g.done&&live){try{const e=await pftMore(g.addr,g.tok);if(!e)break;g.items=e.items;g.done=e.done;g.full=!e.next;pages++;}catch(err){break;}
            if(live){lastRows=build();setSt(s=>({...s,rows:lastRows}));tell(false);}}}};
          await Promise.all([w2(),w2()]);
          if(!live)return;
          const rows=lastRows=build();
          busy=false;tell(true);
          setSt({state:rows.length?'ok':failed===jobs.length?'failed':'none',rows,failed,done,total:jobs.length,at:Date.now()});
        })();
        /* round 23 (audit A6): if this run is cut short (wallet set changed, section unmounted) the Details window must not
           keep waiting on busy:true */
        return()=>{live=false;clearTimeout(tellT);pftCache.flush();if(onRows)onRows(t=>t?{...t,busy:false}:t);};
      },[key,nonce]);
      /* round 17 (Shaka picked option B of mock-tx-v1): an activity feed — one plain-words line per transaction ("Sold 8.91M PTGC"),
         a round type icon with the token's logo on its corner, the wallet (with a copy button) and time underneath, the dollar value
         on the right; grouped by day; filter chips with counts; "Show 30 more". The same layout on a phone. */
      const PFT_CHIP=[['Buys','#39E15A'],['Sells','#FF4B55'],['Claims','#4AA8FF'],['Unstakes','#B9C4FF'],['LP','#F2D35B'],['Transfers','#9AA4B2']];   // round 44: the bar's chips (first four with a count)
      const PFT_F={All:null,Buys:['Buy'],Sells:['Sell'],Claims:['Claim'],Unstakes:['Unstake'],LP:['Add LP','Remove LP'],Transfers:['Move','Receive','Send']};   // round 25 (audit C9): Unstakes have their own chip
      const nameOf=React.useMemo(()=>pftNameOf(wallets),[wallets]);
      const whoOf=r=>pftWhoOf(nameOf,r);
      /* round 25 (audit C1): dust — rows under $1 are hidden until "Show dust" is on (a bot wallet is full of $0.18 buys) */
      const[dust,setDust]=useState(false);
      const isDust=r=>r.usd!=null&&r.usd<1&&r.type!=='Move'&&r.type!=='Claim'&&r.type!=='Unstake';
      const[det,setDet]=useState({});
      /* LP / unstake detail first (it can turn a "Sell" into "Add LP"), so the chips count the corrected types */
      const fix=r=>{const d=det[r.h+'|'+r.addr];if(!d)return r;
        if(d.lp&&(r.type==='Sell'||r.type==='Buy')){const ty=d.lp==='add'?'Add LP':'Remove LP';return{...r,type:ty,usd:pftUsd(ty,r.amt,r.p,r.tok)};}
        if(d.swap===false&&(r.type==='Sell'||r.type==='Buy')){const ty=r.type==='Sell'?'Send':'Receive';return{...r,type:ty,usd:pftUsd(ty,r.amt,r.p,r.tok)};}
        if(r.type==='Unstake'&&d.principal>0)return{...r,net:r.amt,amt:d.principal,unstake:true,usd:r.p==null?null:d.principal*r.p};
        return r;};
      const all0=st.rows.map(fix);
      const nDust=all0.filter(isDust).length;
      const all=dust?all0:all0.filter(r=>!isDust(r));
      const cnt=k=>PFT_F[k]?all.filter(r=>PFT_F[k].includes(r.type)).length:all.length;
      const list=PFT_F[flt]?all.filter(r=>PFT_F[flt].includes(r.type)):all;
      const show=list.slice(0,lim);
      useEffect(()=>{let live=true;const need=show.filter(r=>(r.type==='Sell'||r.type==='Buy'||r.type==='Unstake')&&!det[r.h+'|'+r.addr]);if(!need.length)return;
        (async()=>{let q=0;const w=async()=>{while(q<need.length){const r=need[q++];try{const d=await pftDetail(r.h,r.addr,r.tok);if(live)setDet(x=>({...x,[r.h+'|'+r.addr]:d}));}catch(e){if(live)setDet(x=>({...x,[r.h+'|'+r.addr]:{}}));}}};await Promise.all([w(),w()]);})();
        return()=>{live=false;};},[show.map(r=>r.id).join()]);
      const dayKey=t=>{const d=new Date(t);return d.getFullYear()*10000+d.getMonth()*100+d.getDate();};
      const dayName=t=>{const d=new Date(t),n=new Date(),k=dayKey(t),y=new Date(n);y.setDate(n.getDate()-1);
        const md=d.toLocaleDateString('en-US',{month:'short',day:'numeric'});
        if(k===dayKey(n.getTime()))return['TODAY',md];if(k===dayKey(y.getTime()))return['YESTERDAY',md];
        if(n-d<6*864e5)return[d.toLocaleDateString('en-US',{weekday:'long'}).toUpperCase(),md];
        return[md.toUpperCase(),d.getFullYear()!==n.getFullYear()?String(d.getFullYear()):''];};
      const groups=[];show.forEach(r=>{const k=dayKey(r.t);const g=groups[groups.length-1];if(g&&g.k===k)g.rows.push(r);else groups.push({k,rows:[r]});});
      const row=(r,i)=><PfTxRow key={r.id} r={r} who={whoOf(r)} cp={cp===r.id} onCopy={copy} z={i%2===1}/>;
      /* round 35: the section rolls up into a bar like Per-wallet breakdown; the day window's link opens it */
      const[open,setOpen]=usePfFold('rt');useEffect(()=>{const h=()=>setOpen(true);window.addEventListener('pf2-open-feed',h);return()=>window.removeEventListener('pf2-open-feed',h);},[]);
      return(
        <section className="pf2-pn pf2-fold pf2-rt" ref={secRef}>
          {/* round 44 (his pick A of mock-folds-v1): an icon tile, title + meta line, live chips (the filter counts) and a solid gold SHOW button */}
          <button className="pf2-foldh" aria-expanded={open} onClick={()=>setOpen(!open)}>
            <span className="ic" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="#F6E98A" strokeWidth="2" strokeLinecap="round"><path d="M4 19h16"/><path d="M7 16V9"/><path d="M12 16V5"/><path d="M17 16v-6"/></svg></span>
            <span className="tt"><b className="oh">RECENT TRANSACTIONS</b><span className="mt">{st.state==='ok'?<>{all0.length} transaction{all0.length===1?'':'s'} {'\u00B7'} all wallets</>:st.state==='loading'?'reading PulseScan\u2026':'all wallets'}
              {st.state==='ok'&&st.done<st.total&&<span className="pf2-rtl"> {'\u00B7'} reading {st.done} / {st.total}{'…'}</span>}
              {st.state==='ok'&&st.done>=st.total&&st.at&&<span className="pf2-rtl" title={`Read at ${new Date(st.at).toLocaleString()} \u00B7 \u21BB Refresh reads again`}> {'\u00B7'} read {pfAgo(st.at,tick)}</span>}</span></span>
            {st.state==='ok'&&all.length>0&&<span className="chips" aria-hidden="true">{PFT_CHIP.filter(([k])=>cnt(k)>0).slice(0,4).map(([k,c])=><span key={k} className="chip"><i style={{background:c}}></i>{k}<b>{cnt(k)}</b></span>)}</span>}
            <span className="chev" aria-hidden="true"></span></button>
          {open&&<div className="pf2-foldb">
          <div className="pf2-sech">
            {st.state==='ok'&&st.rows.length>0&&<div className="pf2-chips" role="group" aria-label="Show">{Object.keys(PFT_F).map(k=>{const n=cnt(k);if(!n&&k!=='All')return null;return <button key={k} className={flt===k?'on':''} aria-pressed={flt===k} onClick={()=>{setFlt(k);setLim(10);}}>{k}<b>{n}</b></button>;})}
              {nDust>0&&<button className={`dust${dust?' on':''}`} aria-pressed={dust} onClick={()=>setDust(!dust)} title="Transactions worth under $1">{dust?'Hide':'Show'} dust<b>{nDust}</b></button>}</div>}
            <button className="pf2-lnk q" onClick={()=>{force.current=true;setNonce(n=>n+1);}}>{'↻'} Refresh</button></div>
          {st.state==='loading'&&<div className="pf2-soon">Reading your wallets{'’'} PTGC and UFO transfers from PulseScan{'…'}</div>}
          {st.state==='failed'&&<div className="pf2-soon">Couldn{'’'}t reach PulseScan right now. <button className="pf2-lnk" onClick={()=>setNonce(n=>n+1)}>Retry</button></div>}
          {st.state==='none'&&<div className="pf2-soon">{st.failed>0?<>{st.failed} of {st.total} PulseScan reads failed, so some history may be missing. <button className="pf2-lnk" onClick={()=>setNonce(n=>n+1)}>Retry</button></>:'No PTGC or UFO transfers in the counted wallets yet.'}</div>}
          {st.state==='ok'&&st.rows.length>0&&<>
            <PfTxColh/>
            <div className="pf2-feed">{groups.map(g=>{const[d,md]=dayName(g.rows[0].t);return(<React.Fragment key={g.k}>
              {/* round 34: the day's net (tokens in − tokens out, in dollars) on the header — what the day window works out */}
              <div className="pf2-fday">{d}<span>{md}{md?' · ':''}{g.rows.length} <i className="tw">transaction{g.rows.length===1?'':'s'}</i><i className="tx">tx</i></span>{(()=>{let i=0,o=0;g.rows.forEach(r=>{const s=PFT_AMT[r.type];if(s==='pos')i+=r.usd||0;else if(s==='neg')o+=r.usd||0;});const n=i-o;if(!i&&!o)return null;return <em className={n<0?'neg':'pos'} title={`in ${fmtDollar(i)} \u00B7 out ${fmtDollar(o)}`}>{n<0?'\u2212':'+'}{fmtDollar(Math.abs(n),0)} net</em>;})()}</div>{g.rows.map(row)}</React.Fragment>);})}</div>
            {list.length>lim&&<button className="pf2-more" onClick={()=>setLim(l=>l+30)}>Show {Math.min(30,list.length-lim)} more</button>}
            <div className="pf2-txf">{st.failed>0&&<span className="pf2-hnote">{st.failed} of {st.total} reads failed {'—'} <button onClick={()=>setNonce(n=>n+1)}>retry</button></span>}
              <span className="src">From PulseScan {'·'} up to a year back per wallet and token</span></div>
          </>}
          </div>}
        </section>
      );
    };
