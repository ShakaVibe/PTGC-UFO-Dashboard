    /* ===== Portfolio v2 — RECENT TRANSACTIONS (2026-10-13, round 9) =====
       PulseScan's token-transfer list per counted wallet and token (PTGC, UFO) — /api/v2/addresses/{w}/token-transfers, CORS
       open, the latest 50 per call (tested live: ~1–10 s a call). Up to 3 calls in flight; answers cached 5 min in
       localStorage (PFT_LS) so a reload paints at once. Transfers of one tx + token are netted for the wallet (a UFO sell is
       the pair leg + the fee leg to the token contract → one "Sell"). Types: Claim (from the PTGC staking contract — staking
       or lock reward), Stake (to it), Buy / Sell (the tx called a swap), Move (between two of YOUR wallets),
       Receive / Send (anything else). Value = amount × that hour's / day's price (the history's price files). */
    const PFT_LS='grays_pf_tx_v1';
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
        const items=(j.items||[]).map(x=>({h:x.tx_hash,t:Date.parse(x.timestamp),f:(x.from&&x.from.hash||'').toLowerCase(),to:(x.to&&x.to.hash||'').toLowerCase(),m:x.method||'',v:(()=>{try{return Number(BigInt(x.total.value))/Math.pow(10,+x.total.decimals||18);}catch(e){return 0;}})()}));
        c[k]={at:Date.now(),items};pftCache.save();return items;
      }catch(e){if(hit)return hit.items;throw e;}finally{clearTimeout(to);}
    };
    const pftClassify=(legs,addr,own,tok)=>{
      let net=0;legs.forEach(l=>{if(l.to===addr)net+=l.v;if(l.f===addr)net-=l.v;});
      const tokAddr=PFH_TOK[tok].toLowerCase();
      const others=legs.map(l=>l.to===addr?l.f:l.to).filter(a=>a&&a!==addr&&a!==tokAddr);
      const m=(legs[0]&&legs[0].m||'').toLowerCase();
      let type;
      if(legs.some(l=>l.f===PFT_STAKING))type='Claim';   // staked PTGC never leaves the wallet, so anything paid out by the staking contract is a reward
      else if(legs.some(l=>l.to===PFT_STAKING))type='Stake';
      else if(/swap|multicall|execute|zap/.test(m))type=net>=0?'Buy':'Sell';
      else if(others.length&&others.every(a=>own.has(a)))type='Move';
      else type=net>=0?'Receive':'Send';
      return{type,net};
    };
    const PFT_TYPE={Buy:['#39E15A','▲'],Sell:['#FF6B73','▼'],Receive:['#39E15A','↙'],Send:['#FF6B73','↗'],Claim:['#5AB8FF','⬇'],Stake:['#F2D35B','⦿'],Unstake:['#F2D35B','↺'],Move:['#B26BFF','⇄']};
    const PfRecentTx=({wallets,prices})=>{
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
              Object.values(by).forEach(legs=>{const{type,net}=pftClassify(legs,addr,own,tok);if(Math.abs(net)<1e-9&&type!=='Move')return;
                const t=legs[0].t;let p=px?pfhPriceAt(px,tok,t):null;
                /* newer than the price files (they refresh hourly) → today's price */
                if(p==null){const last=px&&px.hourly[tok]&&px.hourly[tok].length?px.hourly[tok][px.hourly[tok].length-1][0]:0;const cur=pxNow.current&&pxNow.current[tok==='PTGC'?'ptgc':'ufo'];if(t>=last&&cur>0)p=cur;}
                const cp=legs.map(l=>l.to===addr?l.f:l.to).find(a=>a&&a!==addr);
                rows.push({id:addr+legs[0].h+tok,t,addr,who:type==='Move'&&cp?(net>=0?(names[cp]||cp.slice(0,6))+' \u2192 '+names[addr]:names[addr]+' \u2192 '+(names[cp]||cp.slice(0,6))):names[addr],tok,type,amt:net,usd:p==null?null:Math.abs(net)*p,h:legs[0].h});});
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
          setSt({state:rows.length?'ok':failed===jobs.length?'failed':'none',rows,failed,done,total:jobs.length});
        })();
        return()=>{live=false;};
      },[key,nonce]);
      const show=st.rows.slice(0,more?40:10);
      const fmtT=t=>{const d=new Date(t);return d.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'})+' '+d.toLocaleTimeString('en-US',{hour:'numeric',minute:'2-digit'});};
      const ty=t=>{const[c,g]=PFT_TYPE[t]||['#fff','•'];return <span className="pf2-ty" style={{color:c}}><i>{g}</i>{t}</span>;};
      const amt=r=><span className={r.type==='Move'?'':r.amt>=0?'pos':'neg'}>{r.type==='Move'?'':r.amt>=0?'+':'−'}{pfAbbr(Math.abs(r.amt))}</span>;
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
              <tbody>{show.map(r=><tr key={r.id}><td>{fmtT(r.t)}</td><td className="w">{r.who}</td><td>{ty(r.type)}</td><td className={r.tok==='PTGC'?'tp':'tu'}>{r.tok}</td><td className="r">{amt(r)}</td><td className="r">{fmtDollar(r.usd)}</td><td>{tx(r.h)}</td></tr>)}</tbody></table>
            <div className="pf2-txm">{show.map(r=><div key={r.id}><span>{ty(r.type)} <b className={r.tok==='PTGC'?'tp':'tu'}>{r.tok}</b></span><span className="a">{amt(r)}</span><span className="d">{fmtT(r.t)} {'·'} {r.who}</span><span className="d r">{fmtDollar(r.usd)} {tx(r.h)}</span></div>)}</div>
            <div className="pf2-txf">{st.rows.length>10&&<button className="pf2-lnk" onClick={()=>setMore(!more)}>{more?'Show fewer':`Show more (${Math.min(40,st.rows.length)})`}</button>}
              {st.failed>0&&<span className="pf2-hnote">{st.failed} of {st.total} reads failed {'—'} <button onClick={()=>setNonce(n=>n+1)}>retry</button></span>}
              <span className="src">From PulseScan {'·'} the latest 50 transfers per wallet and token</span></div>
          </>}
        </section>
      );
    };
