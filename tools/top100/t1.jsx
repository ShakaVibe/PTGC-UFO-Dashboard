    /* ================= TOP 100 (2026-10-22) — the Token Allocation panel's "Top 100" window =================
       Shaka: "a new button to the right of the Leagues button … Top 100 … list the Top 100 wallets … a bar where you can enter an
       address … how much ptgc or UFO you would need to buy, the value of that … On PTGC … Top 100 STAKERS". Mock-up
       design/topw → design/top100/mock-top100-v1.html; his picks: button B1 (the Leagues button's twin), look B (hall of fame).
       Data (both prebuilt by the pipeline, read from raw GitHub like every data file):
         · holders — data/holder-ranks.json (step holder-ranks, 2 h): `top` = the first 110 people WITH addresses, `b` = every
           person's balance high → low (the same list and the same people-only rule as the Portfolio HOLDER RANK)
         · stakers — data/top-stakers.json (step top-stakers, 2 h): `top` = [addr, staked, locked, wallet balance] × 110, `s` = every
           staker's amount high → low, from the staking contract's Deposit logs + mapUserInfo
       The checker reads the typed wallet LIVE (balanceOf, and mapUserInfo for stakers) and ranks it against the list: rank = 1 + how
       many listed amounts are strictly above (ties share a rank — pfRank's rule). Hidden until TOP100_LIVE: the button shows only on a
       device that tapped the faint bottom-right dot (T1Dot, remembered in LS.T100_PREVIEW). Honest states (gotcha 20): undefined =
       loading, null = failed → "Couldn't load — Retry", never a zero. */
    const TOP100_LIVE=true;   // LIVE 2026-10-22 (Shaka: "make it live!"). false = the button shows only on a device that tapped the faint bottom-right dot
    if(TOP100_LIVE){try{localStorage.removeItem('grays_t100_preview_v1');}catch(e){}}   // the preview dot's device flag means nothing once live
    const T1_RAW='https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/';
    const T1_ART_V=2;   // bump when logos/top100/* change under the same names (gotcha 38) — 2: his beam-UFO medals (bigger numbers)
    const T1_TTL=10*60*1000,T1_STALE=48*3600*1000;
    const T1_SEL={balanceOf:'0x70a08231',mapUserInfo:'0x15612933'};
    const _t1={};   // file name → {at, v, p}
    const t1Fetch=(f,force)=>{
      const c=_t1[f]||(_t1[f]={at:0,v:undefined,p:null});
      if(!force&&c.at&&Date.now()-c.at<T1_TTL)return Promise.resolve(c.v);
      if(c.p)return c.p;
      c.p=dataFetch(T1_RAW+f).then(r=>r.ok?r.json():null).catch(()=>null).then(j=>{c.p=null;c.at=Date.now();c.v=j&&j.schema>=1?j:null;return c.v;});
      return c.p;
    };
    /* whole tokens from 1 up, 6 decimals below 1 — the builders' key() (holder-ranks / top-stakers), so equal balances compare equal */
    const t1Key=w=>{const W=10n**18n;if(w<=0n)return 0;if(w>=W)return Number(w/W);const m=w/(10n**12n);return Math.max(1,Number(m))/1e6;};
    const t1Rank=(list,v)=>{let lo=0,hi=list.length;while(lo<hi){const m=(lo+hi)>>1;if(list[m]>v)lo=m+1;else hi=m;}return lo+1;};   // list high → low
    const t1Px=p=>p.toFixed(Math.min(12,Math.max(2,Math.ceil(-Math.log10(p))+3))).replace(/(\.\d*?[1-9])0+$/,'$1');   // 0.00001827 / 0.000002538, never 1.8e-5
    const t1Short=a=>a?a.slice(0,6)+'…'+a.slice(-4):'';
    const t1Usd=n=>n==null||!isFinite(n)?'—':n>=100?fmtUSD(n):'$'+n.toFixed(2);
    const t1League=(bal,sup)=>{if(!(bal>0))return null;const c=BURN_C.find(c=>bal>=sup*tierFraction(c))||BURN_C[BURN_C.length-1];return c;};
    const t1Wallets=()=>{try{const w=JSON.parse(localStorage.getItem('ptgc_ufo_portfolio')||'[]');return Array.isArray(w)?w.filter(x=>x&&/^0x[0-9a-fA-F]{40}$/.test(x.address||'')):[];}catch(e){return[];}};   // every saved wallet (Shaka: "not all the wallets in the portfolio are showing")
    const T1I={
      ticket:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"><path d="M3 8a2 2 0 0 0 0 4 2 2 0 0 0 0 4v2h18v-2a2 2 0 0 1 0-4 2 2 0 0 1 0-4V6H3z"/><path d="M13 6v12" strokeDasharray="2 2"/></svg>,
      pie:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 3v9h9a9 9 0 1 1-9-9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z" fill="currentColor"/></svg>,
      crown:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinejoin="round"><path d="M3 7l4.5 4L12 4l4.5 7L21 7l-2 11H5z"/></svg>,
      users:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6 6 0 0 1 3.5 6"/></svg>,
      search:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>,
      bolt:<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>,
      trophy:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3v2a4 4 0 0 1-4 4M7 5H4v2a4 4 0 0 0 4 4"/></svg>,
      copy:<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/></svg>,
    };
    const T1Tile=({l,ic,v,f,cls=''})=>(<div className={`t1t ${cls}`}><div className="l">{ic&&T1I[ic]}{l}</div><div className="v">{v}</div>{f!=null&&<div className="f">{f}</div>}</div>);
    const T1Amt=({v,tok})=>(<>{fmtAbbr(v)}<small>{tok}</small></>);
    const T1Cost=()=>(<span className="t1ii" tabIndex={0} aria-label="About the cost">i<span className="tip" role="tooltip"><b>Cost is a snapshot.</b> It's the tokens you'd need at today's price. A real buy moves the price as it fills — slippage and the price rising while you buy aren't included, so expect the real cost to be higher.</span></span>);
    const T1Dot=({token,on,onToggle})=>(
      <button type="button" onClick={onToggle} aria-label="Top 100 (preview)" aria-pressed={on} title="" className="fixed bottom-1 right-1 z-30 w-7 h-7 flex items-center justify-center bg-transparent border-0 p-0">
        <span aria-hidden="true" className="block w-1.5 h-1.5 rounded-full" style={{background:(TOKENS[token]||TOKENS.PTGC).colorHex,opacity:on?0.4:0.16}}></span>
      </button>
    );
    /* audit A4 (2026-10-22): the ✓ only when the copy really happened — the async clipboard can refuse (permissions, an
       insecure frame); the old execCommand path is the fallback */
    const t1Copy=a=>{
      const legacy=()=>{try{const t=document.createElement('textarea');t.value=a;t.setAttribute('readonly','');t.style.position='fixed';t.style.opacity='0';document.body.appendChild(t);t.select();const ok=document.execCommand('copy');t.remove();return ok;}catch(e){return false;}};
      try{if(navigator.clipboard&&navigator.clipboard.writeText)return navigator.clipboard.writeText(a).then(()=>true,()=>legacy());}catch(e){}
      return Promise.resolve(legacy());
    };
    const T1Addr=({a,me})=>{
      const[ok,setOk]=useState(null);   // null | true | false (failed)
      useEffect(()=>{if(ok===null)return;const t=setTimeout(()=>setOk(null),1400);return()=>clearTimeout(t);},[ok]);
      return(<div className="ad"><a href={`https://scan.pulsechain.com/address/${a}`} target="_blank" rel="noopener noreferrer" title={a}>{t1Short(a)}</a>
        <button type="button" className="t1cp" aria-label={`Copy ${a}`} title={ok===true?'Copied':ok===false?'Copy failed — select the address on PulseScan':'Copy address'} onClick={()=>{t1Copy(a).then(r=>setOk(!!r));}}>{ok===true?<span style={{fontSize:11}}>✓</span>:ok===false?<span style={{fontSize:11,color:'#FCA5A5'}}>✕</span>:T1I.copy}</button>
        {me&&<span className="t1tag">CHECKED</span>}</div>);
    };
    /* audit A3: rows and podium cards are module-level components, and the list is memoised — they used to be declared inside the
       window, so React remounted all 100 rows (and their images) on every keystroke in the address box */
    const T1Row=({x,rank,cls,isMe,stk,P,SUP,tot,mx})=>{
      const w=Math.max(2,Math.min(100,Math.sqrt(x.v)/mx*100));
      if(stk)return(<div role="row" className={`t1r ${cls||''}${isMe?' me':''}`}><span role="cell" className="rk">{rank}</span><span role="cell"><T1Addr a={x.a} me={isMe}/></span>
        <span role="cell" className="bal"><span className="bb"><i style={{width:w+'%'}}></i>{x.l>0&&<i className="lk" style={{width:w*Math.min(1,x.l/x.v)+'%'}}></i>}</span><span className="n">{fmtAbbr(x.v)}{P&&<span className="u2">{t1Usd(x.v*P)}</span>}</span></span>
        <span role="cell" className="un2 hp">{fmtAbbr(x.v)}</span><span role="cell" className="lk2 hp">{x.l>0?fmtAbbr(x.l):'—'}</span><span role="cell" className="pc2 hp">{(x.v/tot*100).toFixed(2)}%</span><span role="cell" className="uv hp">{P?t1Usd(x.v*P):'—'}</span></div>);
      const lg=t1League(x.v,SUP);
      return(<div role="row" className={`t1r ${cls||''}${isMe?' me':''}`}><span role="cell" className="rk">{rank}</span><span role="cell"><T1Addr a={x.a} me={isMe}/></span>
        <span role="cell">{lg&&<SeaIcon e={lg.e} size={32}/>}</span>
        <span role="cell" className="bal"><span className="bb"><i style={{width:w+'%'}}></i></span><span className="n">{fmtAbbr(x.v)}{P&&<span className="u2">{t1Usd(x.v*P)}</span>}</span></span>
        <span role="cell" className="pc2 hp">{(x.v/SUP*100).toFixed(2)}%</span><span role="cell" className="uv hp">{P?t1Usd(x.v*P):'—'}</span></div>);
    };
    const T1Pod=({x,i,cls,isMe,stk,P,tok,tot})=>!x?<div/>:(
      <div className={`t1pc ${cls}${isMe?' me':''}`}><img className="md" src={`logos/top100/t1-${['1st','2nd','3rd'][i]}.webp?v=${T1_ART_V}`} alt={`#${i+1}`}/>
        <div className="t1pt"><div className="ad"><a href={`https://scan.pulsechain.com/address/${x.a}`} target="_blank" rel="noopener noreferrer" title={x.a}>{t1Short(x.a)}</a></div>
        <div className="bl"><T1Amt v={x.v} tok={tok}/></div><div className="uv">{P?t1Usd(x.v*P):'—'}</div><div className="t1sh">{(x.v/tot*100).toFixed(2)}% {stk?'of staked':'of supply'}</div></div></div>);
    /* audit A1: never rank what the lists leave out — the builders' known addresses (burn, DAO wallets + contract, the UFO OA wallet,
       staking, router, the token contracts); any other contract is caught by eth_getCode in the holders view */
    const T1_EXCL=new Set(['0x0000000000000000000000000000000000000369','0x0000000000000000000000000000000000000000','0x000000000000000000000000000000000000dead',
      '0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1','0x440773b5104a102c00ef26979a5c897155336a34','0x305acfab82103c2b82b19543919d1c93b44e55db',
      '0x92dd8e86fdb206fa41e451398a9f03fbd36d574d','0xc71f597a2ac39e47f07102e849d18489c96f39ef','0x165c3410fc91ef562c50559f7d2289febed552d9',
      '0x94534eeee131840b1c0f61847c572228bdfdde93','0x49ed499433bee42dd34c169470fef2c8f9fae6e6','0x456548a9b56efbbd89ca0309edd17a9e20b04018']);
    const T1_AMBER=12*3600*1000;   // audit A5: past 12 h an amber "may be off" note; past T1_STALE (48 h) the ranks are hidden
    /* audit A11: equal amounts share a rank, in the list exactly as in the checker */
    const t1Ranks=list=>{const r=[];for(let i=0;i<list.length;i++)r.push(i>0&&list[i].v===list[i-1].v?r[i-1]:i+1);return r;};
    /* audit A2: the list is up to 2 h old and still holds the checked wallet's OLD amount — a wallet that sold since would count its own
       old self above it. For the top 110 we know the addresses, so that one old entry is taken out before ranking. */
    const t1Without=(all,v)=>{let lo=0,hi=all.length;while(lo<hi){const m=(lo+hi)>>1;if(all[m]>v)lo=m+1;else hi=m;}return lo<all.length&&all[lo]===v?all.slice(0,lo).concat(all.slice(lo+1)):all;};
    const Top100Modal=({token,price,onClose})=>{
      const tok=token==='UFO'?'UFO':'PTGC',cfg=TOKENS[tok],SUP=SUPPLY[tok];
      const[mode,setMode]=useState('h');
      const stk=tok==='PTGC'&&mode==='s';
      const[ranks,setRanks]=useState(undefined),[stakers,setStakers]=useState(undefined);
      const[q,setQ]=useState(''),[chk,setChk]=useState(null);   // chk: {busy}|{bad}|{err}|{nope}|{a,v,b?,l?,mode}
      const seq=useRef(0),last=useRef(null);
      const load=(force)=>{
        if(force){setRanks(undefined);if(tok==='PTGC')setStakers(undefined);}
        t1Fetch('holder-ranks.json',force).then(setRanks);
        if(tok==='PTGC')t1Fetch('top-stakers.json',force).then(setStakers);
      };
      useEffect(()=>{load(false);},[tok]);
      const P=price>0?price:null;
      /* the view's list: top = [{a,v,l?,b?}], all = every amount high → low */
      const view=useMemo(()=>{
        if(stk){
          if(stakers===undefined)return undefined;if(!stakers||!Array.isArray(stakers.top)||!Array.isArray(stakers.s))return null;
          return{top:stakers.top.map(r=>({a:String(r[0]).toLowerCase(),v:r[1],l:r[2],b:r[3]})),all:stakers.s,count:stakers.count,tot:stakers.total,at:Date.parse(stakers.generatedAt)};
        }
        if(ranks===undefined)return undefined;const t=ranks&&ranks.tokens&&ranks.tokens[tok];
        if(!t||!Array.isArray(t.b))return null;
        return{top:Array.isArray(t.top)?t.top.map(r=>({a:String(r[0]).toLowerCase(),v:r[1]})):null,all:t.b,tg:typeof t.t==='string'&&t.t.length===t.b.length*6?t.t:null,count:t.holders,tot:SUP,at:Date.parse(t.readAt)};
      },[stk,stakers,ranks,tok,SUP]);
      const age=view&&isFinite(view.at)?Date.now()-view.at:null;
      const stale=age!=null&&age>T1_STALE,amber=age!=null&&age>T1_AMBER&&!stale;
      const T=view&&view.all.length>=100?view.all[99]:null;
      const wallets=useMemo(t1Wallets,[]);
      const check=async(addr)=>{
        const raw=String(addr||q).trim();
        const m=raw.match(/0x[0-9a-fA-F]{40}(?![0-9a-fA-F])/);   // audit A12: a bare address or any link that carries one (PulseScan, Otter…)
        if(!m){setChk({bad:true});return;}
        const a=m[0];setQ(a);last.current=a;
        const my=++seq.current;setChk({busy:true});
        try{
          const p=encodeAddress(a),al=a.toLowerCase();
          if(!stk&&T1_EXCL.has(al)){if(my===seq.current)setChk({nope:'known'});return;}
          if(!stk){
            const code=await rpcFetch({jsonrpc:'2.0',method:'eth_getCode',params:[a,'latest'],id:1});
            if(!code||typeof code.result!=='string')throw new Error('code');
            if(code.result.length>2){if(my===seq.current)setChk({nope:'contract'});return;}
          }
          const bal=await ethCallRead(cfg.address,T1_SEL.balanceOf+p);
          if(bal==null)throw new Error('balance');
          let r={a,mode:stk?'s':'h',b:t1Key(BigInt(bal))};
          if(stk){
            const ui=await ethCallRead(cfg.stakingContract,T1_SEL.mapUserInfo+p);
            if(ui==null||ui.length<2+64*6)throw new Error('stake');
            const w=n=>BigInt('0x'+ui.slice(2+64*n,2+64*(n+1)));
            r.v=t1Key(w(0));r.l=t1Key(w(5));
          }else r.v=r.b;
          if(my===seq.current)setChk(r);
        }catch(e){if(my===seq.current)setChk({err:true});}
      };
      /* audit A8: switching Holders ↔ Stakers re-checks the same wallet in the other list */
      const firstMode=useRef(true);
      useEffect(()=>{if(firstMode.current){firstMode.current=false;return;}if(last.current)check(last.current);else setChk(null);},[mode]);
      const res=chk&&chk.a&&view&&T!=null&&!stale?(()=>{
        const k=chk.v,al=chk.a.toLowerCase();
        /* Audit IV e9: `top` has addresses for the first 110 only; holder-ranks.json's `t` tags every entry (first 6 hex chars,
           aligned with the list), so a checked wallet below #110 also has its own old entry left out (the nearest balance on a
           shared tag). */
        const own=(view.top&&view.top.find(x=>x.a===al))||(()=>{if(!view.tg)return null;const tag=al.slice(2,8),js=[];let i=view.tg.indexOf(tag);
          while(i>=0){if(i%6===0)js.push(i/6);i=view.tg.indexOf(tag,i+1);}if(!js.length)return null;
          const j=js.reduce((p,q)=>Math.abs(view.all[q]-k)<Math.abs(view.all[p]-k)?q:p);return{a:al,v:view.all[j]};})();
        const list=own?t1Without(view.all,own.v):view.all;   // A2
        const T2=list.length>=100?list[99]:T;
        const rank=k>0?t1Rank(list,k):null,inTop=rank!=null&&rank<=100;
        const pct=Math.min(100,k/T2*100);
        /* Audit IV e1 (2026-10-23): `list` has the checked wallet removed, so list[99] IS the overall #101 — the line the wallet
           drops under. list[100] was #102 and made every cushion too generous by list[99]−list[100]. */
        const cush=Math.max(0,k-(list[99]||0));
        if(chk.mode==='s'){
          const need=Math.max(0,T2-k+1),free=Math.max(0,(chk.b||0)-k),buy=Math.max(0,need-free);
          if(inTop){const up=rank>1?list[rank-2]:null,unl=Math.max(0,k-(chk.l||0));return{rank,inTop,tiles:[
            <T1Tile key="1" l="Staked" v={<T1Amt v={k} tok="PTGC"/>} f={chk.l>0?`${fmtAbbr(chk.l)} of it locked`:'none of it locked'}/>,
            <T1Tile key="2" l="You're in" ic="trophy" cls="in" v={`#${rank.toLocaleString('en-US')}`} f={`of ${view.count.toLocaleString('en-US')} stakers`}/>,
            up!=null?<T1Tile key="3" l={`To pass #${rank-1}`} ic="bolt" cls="hot" v={<>+<T1Amt v={up-k+1} tok="PTGC"/></>} f={<>stake that much more{P?<> · ≈ <span className="usd">{t1Usd((up-k+1)*P)}</span></>:null}</>}/>:<T1Tile key="3" l="Top staker" ic="crown" cls="hot" v="#1" f="nobody above you"/>,
            /* A10: locked PTGC can't be unstaked — say how much of the cushion is free */
            <T1Tile key="4" l="Your cushion" v={<T1Amt v={cush} tok="PTGC"/>} f={!(chk.l>0)?'above #101 — unstake more than this and you drop out':unl<cush?`above #101 — your ${fmtAbbr(unl)} unlocked can't drop you out (${fmtAbbr(chk.l)} is locked)`:`above #101 — ${fmtAbbr(unl)} of your stake is unlocked; unstake more than this and you drop out`}/>]};}
          return{rank,inTop,pct,tiles:[
            <T1Tile key="1" l="Staked" v={<T1Amt v={k} tok="PTGC"/>} f={k>0?(chk.l>0?`${fmtAbbr(chk.l)} of it locked`:'none of it locked'):'nothing staked'}/>,
            <T1Tile key="2" l="Staker rank" v={rank?`#${rank.toLocaleString('en-US')}`:'—'} f={rank?`of ${view.count.toLocaleString('en-US')} stakers`:'not staking'}/>,
            <T1Tile key="3" l="Stake more" ic="bolt" cls="hot" v={<>+<T1Amt v={need} tok="PTGC"/></>} f={`to pass #100 (${fmtAbbr(T2)} staked)`}/>,
            <T1Tile key="4" l={<>Cost today <T1Cost/></>} v={<span className="usd">{buy===0?'$0':P?t1Usd(buy*P):'—'}</span>} f={free>0?(buy>0?`stake your ${fmtAbbr(free)} unstaked + buy ${fmtAbbr(buy)}`:`stake ${fmtAbbr(need)} of your ${fmtAbbr(free)} unstaked`):`buy ${fmtAbbr(need)} PTGC and stake it`}/>]};
        }
        const lg=t1League(k,SUP);
        const lgEl=lg?<span className="t1lgc"><SeaIcon e={lg.e} size={22}/>{lg.n}</span>:'not holding';
        if(inTop){const up=rank>1?list[rank-2]:null;return{rank,inTop,tiles:[
          <T1Tile key="1" l="Holds" v={<T1Amt v={k} tok={tok}/>} f={P?<>≈ <span className="usd">{t1Usd(k*P)}</span></>:null}/>,
          <T1Tile key="2" l="You're in" ic="trophy" cls="in" v={`#${rank}`} f={<>{lgEl} · in the top 100</>}/>,
          up!=null?<T1Tile key="3" l={`To pass #${rank-1}`} ic="bolt" cls="hot" v={<>+<T1Amt v={up-k+1} tok={tok}/></>} f={P?<>≈ <span className="usd">{t1Usd((up-k+1)*P)}</span> today</>:null}/>:<T1Tile key="3" l="Top holder" ic="crown" cls="hot" v="#1" f="nobody above you"/>,
          <T1Tile key="4" l="Your cushion" v={<T1Amt v={cush} tok={tok}/>} f="above #101 — sell more than this and you drop out"/>]};}
        const need=Math.max(0,T2-k+1);
        return{rank,inTop,pct,tiles:[
          <T1Tile key="1" l="Holds" v={<T1Amt v={k} tok={tok}/>} f={P?<>≈ <span className="usd">{t1Usd(k*P)}</span></>:null}/>,
          <T1Tile key="2" l="Rank" v={rank?`#${rank.toLocaleString('en-US')}`:'—'} f={lgEl}/>,
          <T1Tile key="3" l="To break in" ic="bolt" cls="hot" v={<>+<T1Amt v={need} tok={tok}/></>} f={`to pass #100 (${fmtAbbr(T2)})`}/>,
          <T1Tile key="4" l={<>Cost today <T1Cost/></>} v={<span className="usd">{P?t1Usd(need*P):'—'}</span>} f={P?`at $${t1Px(P)} per ${tok}`:'price unavailable'}/>]};
      })():null;
      const top=view&&view.top,tot=view&&view.tot;
      const me=chk&&chk.a?chk.a.toLowerCase():null;
      const sum100=view&&view.all.length>=100?view.all.slice(0,100).reduce((s,x)=>s+x,0):null;   // from the full list, so it shows before `top` exists
      /* A3: the podium + 100 rows only re-render when the data, the view, the price or the checked wallet change — not on typing */
      const extra=res&&!res.inTop&&res.rank?{x:{a:chk.a.toLowerCase(),v:chk.v,l:chk.l},rank:res.rank}:null;
      const listEl=useMemo(()=>{
        if(!top||top.length<100||stale)return null;
        const mx=Math.sqrt(top[0].v),rk=t1Ranks(top),pp={stk,P,SUP,tot,mx};
        return(<>
          <div className="t1pod">{[[1,'s'],[0,'g'],[2,'b']].map(([i,c])=><T1Pod key={i} x={top[i]} i={i} cls={c} isMe={me===(top[i]&&top[i].a)} stk={stk} P={P} tok={tok} tot={tot}/>)}</div>
          <div className={`t1lst${stk?' stk':''}`} role="table" aria-label={`${tok} top 100 ${stk?'stakers':'holders'}`}>
            {stk?<div className="t1th" role="row"><b>#</b><b>Wallet</b><b><span className="unl hp">■ unlocked</span> <span className="lkl hp">▨ locked</span><span className="t1po">Staked</span></b><b className="hp">Staked</b><b className="hp">Locked</b><b className="hp">Share</b><b className="hp">Value</b></div>
                :<div className="t1th" role="row"><b>#</b><b>Wallet</b><b></b><b>Balance</b><b className="hp">Supply</b><b className="hp">Value</b></div>}
            {top.slice(0,100).map((x,i)=><T1Row key={x.a} x={x} rank={rk[i]} cls={i===99?'cut':''} isMe={me===x.a} {...pp}/>)}
            <div className="t1line" role="row">THE TOP 100 LINE</div>
            {extra?<T1Row x={extra.x} rank={extra.rank} isMe={true} {...pp}/>:top[100]?<T1Row x={top[100]} rank={rk[100]} isMe={me===top[100].a} {...pp}/>:null}
          </div>
        </>);
      },[top,stale,stk,P,SUP,tot,tok,me,extra&&extra.rank,extra&&extra.x.v]);
      return(
        <Modal className="z-50 flex items-center justify-center p-2 sm:p-4 modal-overlay bg-black/80" onClose={onClose} label={`${tok} top 100`}>
          <div className={`t1m${tok==='UFO'?' ufo':''}`} onClick={e=>e.stopPropagation()}>
            <button type="button" className="t1x" onClick={onClose} aria-label="Close">✕</button>
            <div className="t1sc">{/* the scroller sits INSIDE the frame, so its bar never cuts the rounded corners (Shaka 2026-10-22) */}
            <div className="t1hd">
              <div className="t1sky" aria-hidden="true"></div><div className="t1fade" aria-hidden="true"></div>
              {tok==='PTGC'&&<div className="t1sw" role="group" aria-label="List">
                <button type="button" aria-pressed={!stk} onClick={()=>setMode('h')}>Top holders</button>
                <button type="button" aria-pressed={stk} onClick={()=>setMode('s')}>Top stakers</button></div>}
              <LgCoin token={tok}/>
              <div className="t1ttl"><h2>{tok} <em>TOP 100</em></h2><p>{stk?'The 100 biggest PTGC stakers — staked + locked, read from the staking contract':`The 100 biggest ${tok} wallets — people only`}</p></div>
            </div>
            {view===undefined?<div className="t1wait"><span className="t1spin" aria-hidden="true"></span>Reading the list…</div>
            :view===null?<div className="t1wait">Couldn't load the list — if this is new, it is built by the next data update (every 2 h).<button type="button" onClick={()=>load(true)}>Retry</button></div>
            :<>
              {(amber||stale)&&<div className={`t1old${stale?' dead':''}`} role="status">{stale?<>This list was read {fmtSnapshotAge(age)} — too old to rank against, so ranks are hidden until the next data update.</>:<>This list was read {fmtSnapshotAge(age)} (it normally refreshes every 2 h) — ranks may be a little off.</>}</div>}
              <div className="t1st4">
                <T1Tile cls="lead" ic="ticket" l={stk?'#100 has staked':'#100 holds'} v={T!=null&&!stale?<T1Amt v={T} tok={tok}/>:'—'} f={T!=null&&P&&!stale?<>≈ <span className="usd">{t1Usd(T*P)}</span> — the line to beat</>:'the line to beat'}/>
                <T1Tile ic="pie" l={stk?'Top 100 stake':'Top 100 hold'} v={sum100!=null&&!stale?(sum100/tot*100).toFixed(1)+'%':'—'} f={stk?`of all ${fmtAbbr(tot)} staked PTGC`:`of the ${fmtAbbr(SUP)} starting supply`}/>
                <T1Tile ic="crown" l={stk?'#1 has staked':'#1 holds'} v={view.all.length&&!stale?<T1Amt v={view.all[0]} tok={tok}/>:'—'} f={view.all.length&&P&&!stale?<>≈ <span className="usd">{t1Usd(view.all[0]*P)}</span></>:null}/>
                {/* A9: people only — the dashboard's Holders tile counts pools and contracts too */}
                <T1Tile ic="users" l={stk?'Stakers':'People holding'} v={(view.count||view.all.length).toLocaleString('en-US')} f={stk?'wallets with PTGC staked now':'pools & contracts left out'}/>
              </div>
              <div className="t1chk">
                <div className="hh"><span>{T1I.search}{stk?'Check a wallet — how much to stake':'Check a wallet'}</span><span className="r">rank, tokens to break in, cost today</span></div>
                <form className="t1bar" onSubmit={e=>{e.preventDefault();check();}}>
                  <label className="t1inp">{T1I.search}<input value={q} onChange={e=>setQ(e.target.value)} placeholder="Paste a wallet address or a PulseScan link" spellCheck={false} autoComplete="off" aria-label="Wallet address"/></label>
                  <button type="submit" className="t1go" disabled={chk&&chk.busy}>{chk&&chk.busy?'…':'CHECK'}</button>
                </form>
                {!chk&&wallets.length>0&&<div className="t1mine">Your wallets from Portfolio: {wallets.map(w=><button type="button" key={w.address} onClick={()=>check(w.address)} title={w.address}>{w.name||t1Short(w.address)}</button>)}</div>}
                {chk&&chk.bad&&<div className="t1msg bad">That isn't a wallet address — paste one that starts with 0x (42 characters), or a PulseScan link to it.</div>}
                {chk&&chk.nope==='contract'&&<div className="t1msg bad">That's a contract (a pool, a router or another contract) — only people's wallets are ranked.</div>}
                {chk&&chk.nope==='known'&&<div className="t1msg bad">That address is left out of the ranking (a burn address, a DAO wallet, the staking contract or a token contract).</div>}
                {chk&&chk.err&&<div className="t1msg bad">Couldn't read that wallet from the chain just now — try again.</div>}
                {chk&&chk.busy&&<div className="t1msg"><span className="t1spin" aria-hidden="true"></span>Reading the wallet from the chain…</div>}
                {chk&&chk.a&&stale&&<div className="t1msg">The list is too old to rank against right now — try again after the next data update.</div>}
                {res&&<><div className="t1res">{res.tiles}</div>
                  {!res.inTop&&<div className="t1prog"><span>{res.pct.toFixed(1)}% of the way</span><span className="tr"><i style={{width:res.pct+'%'}}></i></span><b>#100</b></div>}</>}
              </div>
              {stale?null:listEl||<div className="t1wait">The top-100 list arrives with the next data update — the checker above already works.</div>}
              <div className="t1ft">{stk?'Read from the PTGC staking contract (every wallet that ever staked, its staked amount now; locked included)':`From PulseScan’s holder list · people only — left out: liquidity pools, every contract, the burn addresses, the DAO wallets${tok==='UFO'?', the UFO OA wallet':''}`} · refreshed every 2 h{age!=null&&<> · <span className={stale||amber?'old':''}>read {fmtSnapshotAge(age)}</span></>}. The checked wallet is read live.</div>
            </>}
            <button type="button" className="t1cl" onClick={onClose}>Close</button>
            </div>
          </div>
        </Modal>
      );
    };

