    /* ===== Portfolio v2 — RECENT TRANSACTIONS (2026-10-13, round 9) =====
       PulseScan's token-transfer list per counted wallet and token (PTGC, UFO) — /api/v2/addresses/{w}/token-transfers, CORS
       open, the latest 50 per call (tested live: ~1–10 s a call). Up to 3 calls in flight; answers cached 5 min in
       localStorage (PFT_LS) so a reload paints at once. Transfers of one tx + token are netted for the wallet (a UFO sell is
       the pair leg + the fee leg to the token contract → one "Sell"). Types: Claim (from the PTGC staking contract — staking
       or lock reward), Stake (to it), Buy / Sell (the tx called a swap), Move (between two of YOUR wallets),
       Receive / Send (anything else). Value = amount × that hour's / day's price (the history's price files). */
    /* round 18 (Shaka: "a lot of dots are still missing on the chart"): ONE page (the latest 50 transfers) was all we read, and a
       busy wallet's 50 reach back only hours — so the chart had no trades for most of the week. Now each wallet + token is read
       page by page back a year (PFT_BACK) or PFT_PAGES pages, whichever comes first: page 1 for everyone first (the list paints
       fast), then the deeper pages in the background. A cached entry keeps {items, next (PulseScan's next_page_params), done};
       a refresh reads only the newest page(s) and merges them in until it meets what is already cached. */
    const PFT_LS='grays_pf_tx_v3';   // v3 (round 18): entries carry next / done (paging)
    const PFT_API='https://api.scan.pulsechain.com/api/v2/addresses/';
    const PFT_STAKING='0xc71f597a2ac39e47f07102e849d18489c96f39ef';
    const PFT_TTL=5*60e3,PFT_BACK=365*864e5,PFT_PAGES=20;
    try{localStorage.removeItem('grays_pf_tx_v2');}catch(e){}
    const pftCache=(()=>{let c=null;return{get(){if(c)return c;try{c=JSON.parse(localStorage.getItem(PFT_LS)||'{}')||{};}catch(e){c={};}return c;},save(){try{localStorage.setItem(PFT_LS,JSON.stringify(c));}catch(e){try{c={};localStorage.removeItem(PFT_LS);}catch(e2){}}}};})();
    const pftPage=async(addr,tok,next)=>{
      const ac=new AbortController();const to=setTimeout(()=>ac.abort(),25000);
      try{
        const q=next?'&'+Object.entries(next).map(([k,v])=>encodeURIComponent(k)+'='+encodeURIComponent(v)).join('&'):'';
        const r=await fetch(`${PFT_API}${addr}/token-transfers?type=ERC-20&token=${PFH_TOK[tok]}${q}`,{signal:ac.signal});
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
        e.done=pftDone(e);c[k]=e;pftCache.save();return e;
      }catch(err){if(hit)return hit;throw err;}
    };
    /* one more (older) page */
    const pftMore=async(addr,tok)=>{
      const k=addr+'|'+tok,c=pftCache.get(),e=c[k];if(!e||e.done)return e;
      const pg=await pftPage(addr,tok,e.next);
      const have=new Set(e.items.map(pftKey));
      const n={...e,items:e.items.concat(pg.items.filter(i=>!have.has(pftKey(i)))),next:pg.next,pages:(e.pages||1)+1};
      n.done=pftDone(n);c[k]=n;pftCache.save();return n;
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
      if(m==='withdraw'&&legs.some(l=>l.f===PFT_STAKING||l.to===PFT_STAKING))return{type:'Unstake',net};
      if(fromSt)return{type:'Claim',net,sub:PFT_CLAIM_SUB[m]||''};
      const main=legs.filter(l=>(l.to===addr||l.f===addr)).map(l=>l.to===addr?{a:l.f,c:l.fc,v:l.v}:{a:l.to,c:l.tc,v:l.v})
        .filter(x=>x.a&&x.a!==addr&&x.a!==tokAddr&&!PFT_FEE.has(x.a)).sort((x,y)=>y.v-x.v)[0];
      /* the hidden reflection slice of a send (see above) */
      if(net<0){if(tok==='PTGC'){const stLeg=legs.filter(l=>l.f===addr&&l.to===PFT_STAKING).reduce((a,l)=>a+l.v,0);net-=stLeg;}
        else{const fee=legs.filter(l=>l.f===addr&&l.to===tokAddr).reduce((a,l)=>a+l.v,0);net-=fee/5;}}
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
    const PFT_DLS='grays_pf_txd_v1';
    const pftD=(()=>{let c=null;return{get(){if(c)return c;try{c=JSON.parse(localStorage.getItem(PFT_DLS)||'{}')||{};}catch(e){c={};}return c;},save(){try{localStorage.setItem(PFT_DLS,JSON.stringify(c));}catch(e){}}};})();
    const pftDetail=async(h,addr)=>{
      const c=pftD.get(),k=h+'|'+addr;if(c[k])return c[k];
      const g=async u=>{const r=await fetch(PFT_API.replace('addresses/','')+u);if(!r.ok)throw new Error('HTTP '+r.status);return r.json();};
      const out={};
      const tx=await g('transactions/'+h);
      const raw=tx&&tx.raw_input||'';
      if(raw.startsWith('0x2e1a7d4d')&&raw.length>=74){try{out.principal=Number(BigInt('0x'+raw.slice(10,74)))/1e18;}catch(e){}}
      const tt=await g('transactions/'+h+'/token-transfers');
      (tt.items||[]).forEach(x=>{const sym=(x.token&&x.token.symbol||''),nm=(x.token&&x.token.name||'');if(!(sym==='PLP'||/LP/.test(nm)))return;
        const f=(x.from&&x.from.hash||'').toLowerCase(),t=(x.to&&x.to.hash||'').toLowerCase();
        if(t===addr&&/^0x0{40}$/.test(f))out.lp='add';else if(f===addr)out.lp='remove';});
      c[k]=out;pftD.save();return out;
    };
    const PFT_TYPE={Buy:['#39E15A','▲'],Sell:['#FF6B73','▼'],Receive:['#39E15A','↙'],Send:['#FF6B73','↗'],Claim:['#5AB8FF','⬇'],'Add LP':['#F2D35B','\u2295'],Unstake:['#B9C4FF','\u21E7'],'Remove LP':['#F2D35B','\u2296'],Move:['#B26BFF','⇄']};
    const PfRecentTx=({wallets,prices,onRows})=>{
      const pxNow=React.useRef(prices);pxNow.current=prices;
      const[st,setSt]=useState({state:'idle',rows:[],failed:0,done:0,total:0});
      const[lim,setLim]=useState(10);      // round 17: rows shown (10, +30 per Show more)
      const[flt,setFlt]=useState('All');    // round 17: filter chip
      const[cp,setCp]=useState(null);       // round 17: the row whose wallet address was just copied
      const[nonce,setNonce]=useState(0);
      const key=wallets.map(w=>w.address.toLowerCase()).sort().join(',');
      useEffect(()=>{
        if(!wallets.length){setSt({state:'empty',rows:[],failed:0,done:0,total:0});return;}
        let live=true;
        (async()=>{
          const own=new Set(wallets.map(w=>w.address.toLowerCase()));
          const names={};wallets.forEach(w=>{names[w.address.toLowerCase()]=w.name||(w.address.slice(0,6)+'…'+w.address.slice(-4));});
          const jobs=[];wallets.forEach(w=>['PTGC','UFO'].forEach(tok=>jobs.push({addr:w.address.toLowerCase(),tok})));
          setSt(s=>({...s,state:s.rows.length?'ok':'loading',done:0,total:jobs.length}));
          const got=[];let failed=0,done=0,q=0;
          const px=await pfhPrices().catch(()=>null);
          const build=()=>{
            const rows=[];
            got.forEach(({addr,tok,items})=>{
              const by={};items.forEach(it=>{(by[it.h]=by[it.h]||[]).push(it);});
              Object.values(by).forEach(legs=>{const{type,net,cp:mcp,sub}=pftClassify(legs,addr,own,tok);if(Math.abs(net)<1e-9&&type!=='Move')return;
                const t=legs[0].t;let p=px?pfhPriceAt(px,tok,t):null;
                /* newer than the price files (they refresh hourly) → today's price */
                if(p==null){const last=px&&px.hourly[tok]&&px.hourly[tok].length?px.hourly[tok][px.hourly[tok].length-1][0]:0;const cur=pxNow.current&&pxNow.current[tok==='PTGC'?'ptgc':'ufo'];if(t>=last&&cur>0)p=cur;}
                const cp=mcp;
                rows.push({id:addr+legs[0].h+tok,t,addr,who:type==='Move'&&cp?(net>=0?(names[cp]||cp.slice(0,6))+' \u2192 '+names[addr]:names[addr]+' \u2192 '+(names[cp]||cp.slice(0,6))):names[addr],tok,type,sub,amt:net,p,usd:p==null?null:Math.abs(net)*p,h:legs[0].h});});
            });
            /* a Move shows once (the receiving side), not twice */
            const seen=new Set();const out=[];
            rows.sort((a,b)=>b.t-a.t).forEach(r=>{if(r.type==='Move'){const k=r.h+r.tok;if(seen.has(k))return;seen.add(k);if(r.amt<0){r.amt=-r.amt;}}out.push(r);});
            return out;
          };
          /* round 18: chart coverage — a wallet + token is complete back to its oldest transfer unless it hit the page cap / a year */
          const cov=()=>{const o={};got.forEach(g=>{o[g.addr+'|'+g.tok]=g.done?0:(g.items.length?g.items[g.items.length-1].t:Date.now());});return o;};
          const tell=()=>{if(onRows&&live)onRows({rows:build(),cov:cov(),failed});};
          const worker=async()=>{while(q<jobs.length){const j=jobs[q++];try{const e=await pftFetch(j.addr,j.tok,nonce>0);got.push({...j,items:e.items,done:e.done});}catch(e){failed++;}done++;if(live)setSt({state:'ok',rows:build(),failed,done,total:jobs.length});}};
          await Promise.all([worker(),worker(),worker()]);
          if(!live)return;
          tell();
          /* phase 2: the older pages, two at a time, the list and the chart updating as they land */
          let q2=0;const deep=got.filter(g=>!g.done);
          const w2=async()=>{while(q2<deep.length&&live){const g=deep[q2++];while(!g.done&&live){try{const e=await pftMore(g.addr,g.tok);if(!e)break;g.items=e.items;g.done=e.done;}catch(err){break;}
            if(live){setSt(s=>({...s,rows:build()}));tell();}}}};
          await Promise.all([w2(),w2()]);
          if(!live)return;
          const rows=build();
          tell();
          setSt({state:rows.length?'ok':failed===jobs.length?'failed':'none',rows,failed,done,total:jobs.length});
        })();
        return()=>{live=false;};
      },[key,nonce]);
      /* round 17 (Shaka picked option B of mock-tx-v1): an activity feed — one plain-words line per transaction ("Sold 8.91M PTGC"),
         a round type icon with the token's logo on its corner, the wallet (with a copy button) and time underneath, the dollar value
         on the right; grouped by day; filter chips with counts; "Show 30 more". The same layout on a phone. */
      const PFT_F={All:null,Buys:['Buy'],Sells:['Sell'],Claims:['Claim','Unstake'],LP:['Add LP','Remove LP'],Transfers:['Move','Receive','Send']};
      const[det,setDet]=useState({});
      /* LP / unstake detail first (it can turn a "Sell" into "Add LP"), so the chips count the corrected types */
      const fix=r=>{const d=det[r.h+'|'+r.addr];if(!d)return r;
        if(d.lp&&(r.type==='Sell'||r.type==='Buy'))return{...r,type:d.lp==='add'?'Add LP':'Remove LP'};
        if(r.type==='Unstake'&&d.principal>0)return{...r,net:r.amt,amt:d.principal,unstake:true,usd:r.p==null?null:d.principal*r.p};
        return r;};
      const all=st.rows.map(fix);
      const cnt=k=>PFT_F[k]?all.filter(r=>PFT_F[k].includes(r.type)).length:all.length;
      const list=PFT_F[flt]?all.filter(r=>PFT_F[flt].includes(r.type)):all;
      const show=list.slice(0,lim);
      useEffect(()=>{let live=true;const need=show.filter(r=>(r.type==='Sell'||r.type==='Buy'||r.type==='Unstake')&&!det[r.h+'|'+r.addr]);if(!need.length)return;
        (async()=>{let q=0;const w=async()=>{while(q<need.length){const r=need[q++];try{const d=await pftDetail(r.h,r.addr);if(live)setDet(x=>({...x,[r.h+'|'+r.addr]:d}));}catch(e){if(live)setDet(x=>({...x,[r.h+'|'+r.addr]:{}}));}}};await Promise.all([w(),w()]);})();
        return()=>{live=false;};},[show.map(r=>r.id).join()]);
      const dayKey=t=>{const d=new Date(t);return d.getFullYear()*10000+d.getMonth()*100+d.getDate();};
      const dayName=t=>{const d=new Date(t),n=new Date(),k=dayKey(t),y=new Date(n);y.setDate(n.getDate()-1);
        const md=d.toLocaleDateString('en-US',{month:'short',day:'numeric'});
        if(k===dayKey(n.getTime()))return['TODAY',md];if(k===dayKey(y.getTime()))return['YESTERDAY',md];
        if(n-d<6*864e5)return[d.toLocaleDateString('en-US',{weekday:'long'}).toUpperCase(),md];
        return[md.toUpperCase(),d.getFullYear()!==n.getFullYear()?String(d.getFullYear()):''];};
      const groups=[];show.forEach(r=>{const k=dayKey(r.t);const g=groups[groups.length-1];if(g&&g.k===k)g.rows.push(r);else groups.push({k,rows:[r]});});
      const fmtTm=t=>new Date(t).toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'});
      const VERB={Buy:'Bought',Sell:'Sold',Claim:'Claimed','Add LP':'Added to LP','Remove LP':'Removed from LP',Move:'Moved',Receive:'Received',Send:'Sent',Unstake:'Unstaked'};
      const AMT={Sell:'neg',Send:'neg','Add LP':'neg',Buy:'pos',Receive:'pos',Claim:'pos','Remove LP':'pos'};
      const VAL={Sell:'received',Buy:'paid',Claim:'earned'};
      const copy=(r)=>{try{navigator.clipboard.writeText(r.addr);}catch(e){}setCp(r.id);setTimeout(()=>setCp(c=>c===r.id?null:c),1400);};
      const row=r=>{const[c,g]=PFT_TYPE[r.type]||['#fff','•'];
        const extra=r.type==='Claim'&&r.sub?' · from '+r.sub:r.unstake?' · released from staking':'';
        return(<div key={r.id} className="pf2-fr">
          <div className="ic" style={{color:c,borderColor:c+'88',background:c+'1f'}}>{g}<img src={r.tok==='PTGC'?TOKENS.PTGC.logo:TOKENS.UFO.logo} alt={r.tok}/></div>
          <div className="m"><div className="t1">{VERB[r.type]||r.type} <em className={AMT[r.type]||''}>{pfAbbr(Math.abs(r.amt))}</em> {r.tok}</div>
            <div className="t2"><span className="w">{r.who}</span><button className={`cp${cp===r.id?' ok':''}`} onClick={()=>copy(r)} title={`Copy ${r.addr}`} aria-label={`Copy wallet address ${r.addr}`}>{cp===r.id?'✓':'⧉'}</button><span className="tm">{'·'} {fmtTm(r.t)}{extra}</span></div></div>
          <div className="v">{fmtDollar(r.usd)}<small>{VAL[r.type]||'value'}</small></div>
          <a className="lk" href={`https://scan.pulsechain.com/tx/${r.h}`} target="_blank" rel="noopener noreferrer" title="Open on PulseScan" aria-label="Open this transaction on PulseScan">{'↗'}</a>
        </div>);};
      return(
        <section className="pf2-pn pf2-sec pf2-rt">
          <div className="pf2-sech"><h2 className="oh">RECENT TRANSACTIONS <span>(ALL WALLETS)</span></h2>
            {st.state==='ok'&&st.done<st.total&&<span className="pf2-rtl">reading {st.done} / {st.total}{'…'}</span>}
            {st.state==='ok'&&st.rows.length>0&&<div className="pf2-chips" role="group" aria-label="Show">{Object.keys(PFT_F).map(k=>{const n=cnt(k);if(!n&&k!=='All')return null;return <button key={k} className={flt===k?'on':''} aria-pressed={flt===k} onClick={()=>{setFlt(k);setLim(10);}}>{k}<b>{n}</b></button>;})}</div>}
            <button className="pf2-lnk q" onClick={()=>setNonce(n=>n+1)}>{'↻'} Refresh</button></div>
          {st.state==='loading'&&<div className="pf2-soon">Reading your wallets{'’'} PTGC and UFO transfers from PulseScan{'…'}</div>}
          {st.state==='failed'&&<div className="pf2-soon">Couldn{'’'}t reach PulseScan right now. <button className="pf2-lnk" onClick={()=>setNonce(n=>n+1)}>Retry</button></div>}
          {st.state==='none'&&<div className="pf2-soon">No PTGC or UFO transfers in the counted wallets yet.</div>}
          {st.state==='ok'&&st.rows.length>0&&<>
            <div className="pf2-feed">{groups.map(g=>{const[d,md]=dayName(g.rows[0].t);return(<React.Fragment key={g.k}>
              <div className="pf2-fday">{d}<span>{md}{md?' · ':''}{g.rows.length} transaction{g.rows.length===1?'':'s'}</span></div>{g.rows.map(row)}</React.Fragment>);})}</div>
            {list.length>lim&&<button className="pf2-more" onClick={()=>setLim(l=>l+30)}>Show {Math.min(30,list.length-lim)} more</button>}
            <div className="pf2-txf">{st.failed>0&&<span className="pf2-hnote">{st.failed} of {st.total} reads failed {'—'} <button onClick={()=>setNonce(n=>n+1)}>retry</button></span>}
              <span className="src">From PulseScan {'·'} up to a year back per wallet and token</span></div>
          </>}
        </section>
      );
    };
