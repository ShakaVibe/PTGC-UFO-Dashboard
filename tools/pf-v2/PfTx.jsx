    /* ===== Portfolio v2 — RECENT TRANSACTIONS (2026-10-13, round 9) =====
       PulseScan's token-transfer list per counted wallet and token (PTGC, UFO) — /api/v2/addresses/{w}/token-transfers, CORS
       open, the latest 50 per call (tested live: ~1–10 s a call). Up to 3 calls in flight; answers cached 5 min in
       localStorage (PFT_LS) so a reload paints at once. Transfers of one tx + token are netted for the wallet (a UFO sell is
       the pair leg + the fee leg to the token contract → one "Sell"). Types: Claim (from the PTGC staking contract — staking
       or lock reward), Stake (to it), Buy / Sell (the tx called a swap), Move (between two of YOUR wallets),
       Receive / Send (anything else). Value = amount × that hour's / day's price (the history's price files). */
    const PFT_LS='grays_pf_tx_v2';   // v2 (round 13): rows also carry whether each side is a contract
    const PFT_API='https://api.scan.pulsechain.com/api/v2/addresses/';
    const PFT_STAKING='0xc71f597a2ac39e47f07102e849d18489c96f39ef';
    const PFT_TTL=5*60e3;
    const pftCache=(()=>{let c=null;return{get(){if(c)return c;try{c=JSON.parse(localStorage.getItem(PFT_LS)||'{}')||{};}catch(e){c={};}return c;},save(){try{localStorage.setItem(PFT_LS,JSON.stringify(c));}catch(e){try{c={};localStorage.removeItem(PFT_LS);}catch(e2){}}}};})();
    const pftFetch=async(addr,tok,force)=>{
      const k=addr+'|'+tok,c=pftCache.get(),hit=c[k];
      if(!force&&hit&&Date.now()-hit.at<PFT_TTL)return hit.items;
      const ac=new AbortController();const to=setTimeout(()=>ac.abort(),25000);
      try{
        const r=await fetch(`${PFT_API}${addr}/token-transfers?type=ERC-20&token=${PFH_TOK[tok]}`,{signal:ac.signal});
        if(!r.ok)throw new Error('HTTP '+r.status);
        const j=await r.json();
        const items=(j.items||[]).map(x=>({h:x.tx_hash,t:Date.parse(x.timestamp),f:(x.from&&x.from.hash||'').toLowerCase(),to:(x.to&&x.to.hash||'').toLowerCase(),fc:!!(x.from&&x.from.is_contract),tc:!!(x.to&&x.to.is_contract),m:x.method||'',v:(()=>{try{return Number(BigInt(x.total.value))/Math.pow(10,+x.total.decimals||18);}catch(e){return 0;}})()}));
        c[k]={at:Date.now(),items};pftCache.save();return items;
      }catch(e){if(hit)return hit.items;throw e;}finally{clearTimeout(to);}
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
      const[more,setMore]=useState(false);
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
          const worker=async()=>{while(q<jobs.length){const j=jobs[q++];try{const items=await pftFetch(j.addr,j.tok,nonce>0);got.push({...j,items});}catch(e){failed++;}done++;if(live)setSt({state:'ok',rows:build(),failed,done,total:jobs.length});}};
          await Promise.all([worker(),worker(),worker()]);
          if(!live)return;
          const rows=build();
          /* round 14: hand the trades to the value chart (its buy / sell dots). A wallet+token that filled a whole page (50) is
             only complete back to its oldest item — older than that, the chart keeps its balance-change dots. */
          if(onRows){let since=0;got.forEach(g=>{if(g.items.length>=50){const o=Math.min(...g.items.map(i=>i.t));if(o>since)since=o;}});if(failed)since=Date.now();onRows({rows,since});}
          setSt({state:rows.length?'ok':failed===jobs.length?'failed':'none',rows,failed,done,total:jobs.length});
        })();
        return()=>{live=false;};
      },[key,nonce]);
      const[det,setDet]=useState({});
      const show0=st.rows.slice(0,more?40:10);
      useEffect(()=>{let live=true;const need=show0.filter(r=>(r.type==='Sell'||r.type==='Buy'||r.type==='Unstake')&&!det[r.h+'|'+r.addr]);if(!need.length)return;
        (async()=>{let q=0;const w=async()=>{while(q<need.length){const r=need[q++];try{const d=await pftDetail(r.h,r.addr);if(live)setDet(x=>({...x,[r.h+'|'+r.addr]:d}));}catch(e){if(live)setDet(x=>({...x,[r.h+'|'+r.addr]:{}}));}}};await Promise.all([w(),w()]);})();
        return()=>{live=false;};},[st.rows.map(r=>r.id).slice(0,more?40:10).join(),more]);
      const show=show0.map(r=>{const d=det[r.h+'|'+r.addr];if(!d)return r;
        if(d.lp&&(r.type==='Sell'||r.type==='Buy'))return{...r,type:d.lp==='add'?'Add LP':'Remove LP'};
        if(r.type==='Unstake'&&d.principal>0)return{...r,net:r.amt,amt:d.principal,unstake:true,usd:r.p==null?null:d.principal*r.p};
        return r;});
      const fmtT=t=>{const d=new Date(t);return d.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})+' '+d.toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'});};
      const ty=(t,sub)=>{const[c,g]=PFT_TYPE[t]||['#fff','•'];return <span className="pf2-ty" style={{color:c}}><i>{g}</i>{t}{sub&&<small>{sub}</small>}</span>;};
      /* an Unstake shows the principal that came free (it never moves — the stake is a lock on the balance), not a +/− */
      const amt=r=>r.unstake?<span title="Principal released from staking (it never left the wallet)">{pfAbbr(r.amt)}</span>:<span className={r.type==='Move'?'':r.amt>=0?'pos':'neg'}>{r.type==='Move'?'':r.amt>=0?'+':'−'}{pfAbbr(Math.abs(r.amt))}</span>;
      const tx=h=><a className="pf2-txl" href={`https://scan.pulsechain.com/tx/${h}`} target="_blank" rel="noopener noreferrer">{h.slice(0,6)}{'…'}{h.slice(-4)} {'↗'}</a>;
      return(
        <section className="pf2-pn pf2-sec pf2-rt">
          <div className="pf2-sech"><h2 className="oh">RECENT TRANSACTIONS <span>(ALL WALLETS)</span></h2>
            {st.state==='ok'&&st.done<st.total&&<span className="pf2-rtl">reading {st.done} / {st.total}{'…'}</span>}
            <button className="pf2-lnk q" onClick={()=>setNonce(n=>n+1)}>{'↻'} Refresh</button></div>
          {st.state==='loading'&&<div className="pf2-soon">Reading your wallets{'’'} PTGC and UFO transfers from PulseScan{'…'}</div>}
          {st.state==='failed'&&<div className="pf2-soon">Couldn{'’'}t reach PulseScan right now. <button className="pf2-lnk" onClick={()=>setNonce(n=>n+1)}>Retry</button></div>}
          {st.state==='none'&&<div className="pf2-soon">No PTGC or UFO transfers in the counted wallets yet.</div>}
          {st.state==='ok'&&st.rows.length>0&&<>
            <table className="pf2-txt"><thead><tr><th>TIME</th><th>WALLET</th><th>TYPE</th><th>TOKEN</th><th className="r">AMOUNT</th><th className="r">VALUE</th><th>TX</th></tr></thead>
              <tbody>{show.map(r=><tr key={r.id}><td>{fmtT(r.t)}</td><td className="w">{r.who}</td><td>{ty(r.type,r.sub)}</td><td className={r.tok==='PTGC'?'tp':'tu'}>{r.tok}</td><td className="r">{amt(r)}</td><td className="r">{fmtDollar(r.usd)}</td><td>{tx(r.h)}</td></tr>)}</tbody></table>
            <div className="pf2-txm">{show.map(r=><div key={r.id}><span>{ty(r.type,r.sub)} <b className={r.tok==='PTGC'?'tp':'tu'}>{r.tok}</b></span><span className="a">{amt(r)}</span><span className="d">{fmtT(r.t)} {'·'} {r.who}</span><span className="d r">{fmtDollar(r.usd)} {tx(r.h)}</span></div>)}</div>
            <div className="pf2-txf">{st.rows.length>10&&<button className="pf2-lnk" onClick={()=>setMore(!more)}>{more?'Show fewer':`Show more (${Math.min(40,st.rows.length)})`}</button>}
              {st.failed>0&&<span className="pf2-hnote">{st.failed} of {st.total} reads failed {'—'} <button onClick={()=>setNonce(n=>n+1)}>retry</button></span>}
              <span className="src">From PulseScan {'·'} the latest 50 transfers per wallet and token</span></div>
          </>}
        </section>
      );
    };
