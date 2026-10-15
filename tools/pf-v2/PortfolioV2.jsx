    /* Expects (all defined before this file runs): PfLeagues.jsx, PfHistory.jsx, PfTx.jsx, plus the classic page's globals
       (TOKENS, fmtDollar, usd, agg / dp / prices / portfolioData passed in as props, PF_V2_LIVE…). */
    /* ===== PORTFOLIO v2 (2026-10-13) — the page body of design/portfolio/mock-portfolio-v4.html, built by tools/pf-v2.py =====
       HIDDEN: PF_V2_LIVE=false → the classic body stays the default and a faint dot bottom-right (PfV2Dot) flips this device
       to v2 and back (localStorage LS_PF_V2). Go-live = PF_V2_LIVE=true (the dot goes, v2 for everyone).
       Same state, same loaders, same maths as the classic body (agg, dp, getHoldingCreatures, LEAGUE_TIERS) — only the look
       is new. Step 2 (not built yet): the value history from real chain balances and Recent Transactions (placeholders below). */
    const PF_V2_LIVE=false;
    const LS_PF_V2='grays_pf_v2_preview';
    const pfV2Saved=()=>{try{return localStorage.getItem(LS_PF_V2)==='1'}catch(e){return false}};
    const PF_SEA_V=4;   // = index.html SEA_ART_V (the sea art files are shared: logos/panels/sea-*.webp)
    const PF_SEA={'\u{1F531}':'trident','\u{1F40B}':'whale','\u{1F988}':'shark','\u{1F42C}':'dolphin','\u{1F991}':'squid','\u{1F422}':'turtle','\u{1F990}':'shrimp','\u{1F41A}':'shell'};
    const pfSea=e=>`logos/panels/sea-${PF_SEA[e]||'shell'}.webp?v=${PF_SEA_V}`;
    const PfV2Dot=({on,toggle})=>(
      <button className="pf2-dotbtn" onClick={toggle} aria-label={on?'Back to the current portfolio page':'Preview the new portfolio page'} title={on?'Back to the current page':'Preview'}></button>
    );
    /* current tier → next tier, the classic LeagueProgress maths */
    const pfLeague=(balance,supply)=>{
      if(!(balance>0))return null;
      const tiers=LEAGUE_TIERS.map(t=>({...t,min:supply*t.pct}));
      const i=tiers.findIndex(t=>balance>=t.min);
      if(i===0)return{cur:tiers[0],next:null,pct:100,need:0};
      const cur=i===-1?null:tiers[i],next=i===-1?tiers[tiers.length-1]:tiers[i-1];
      const floor=cur?cur.min:0,ceil=next.min;
      return{cur,next,pct:Math.max(0,Math.min(100,(balance-floor)/(ceil-floor)*100)),need:Math.max(0,ceil-balance)};
    };
    /* round 5 (Shaka: "fix the pie chart … where the yellow meets the purple"): each segment's own drop-shadow painted over
       its neighbour and the last arc overlapped the first at 12 o'clock. Now a 2-unit dark gap between arcs (the dataviz
       spacer rule) and ONE glow on the group. */
    const PfRing=({parts,size=132})=>{
      const r=46,c=2*Math.PI*r,list=parts.filter(p=>p[0]>0),tot=list.reduce((s,p)=>s+p[0],0),gap=list.length>1?2:0;let off=0;
      return(
        <svg viewBox="0 0 120 120" style={{width:size,height:size}} aria-hidden="true">
          <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,.06)" strokeWidth="22"/>
          <g style={{filter:'drop-shadow(0 0 5px rgba(255,255,255,.18))'}}>
          {tot>0&&list.map(([v,col],i)=>{const L=v/tot*c;const vis=Math.max(.6,L-gap);const el=<circle key={i} cx="60" cy="60" r={r} fill="none" stroke={col} strokeWidth="22" strokeDasharray={`${vis} ${c-vis}`} strokeDashoffset={-(off+gap/2)} transform="rotate(-90 60 60)"/>;off+=L;return el;})}
          </g>
        </svg>
      );
    };
    const pfPct=(v,t)=>{if(!(t>0)||v==null)return'—';const p=v/t*100;return(p>0&&p<0.1?p.toFixed(2):p.toFixed(1))+'%';};
    const pfChg=c=>c==null||isNaN(c)?<span className="na">{'—'} (24h)</span>:<span className={c>=0?'pos':'neg'}>{c>=0?'+':'−'}{Math.abs(c).toFixed(2)}% (24h)</span>;
    /* round 25 (audit C11): the creature row used the classic 6-tier list (stops at Turtle) while the League goes to Shrimp /
       Shell — a Shrimp-sized bag showed "League: Shrimp" over an empty row. Same 8 tiers as the League now. */
    const pfCreatures=(tokens,supply)=>{const out=[];let rem=tokens;for(const c of PF_BURN_C){if(c.p<=0)continue;const th=supply*c.p/100;const n=Math.floor(rem/th);if(n>0){out.push({emoji:c.e,count:n,name:c.n});rem=rem%th;}}
      if(!out.length&&tokens>0)out.push({emoji:'\u{1F41A}',count:1,name:'Shell'});return out;};
    const PfCreatures=({tokens,token})=>{
      const list=tokens>0?pfCreatures(tokens,PF_SUPPLY[token]):[];
      if(!list.length)return null;
      return <div className="pf2-crw">{list.map((c,i)=><span key={i} title={`${c.count} × ${c.name}`}><img src={pfSea(c.emoji)} alt={c.name}/>{'×'}{c.count}</span>)}</div>;
    };
    const PfLeague=({balance,token,price,onTiers})=>{
      const L=pfLeague(balance,PF_SUPPLY[token]);
      if(!L)return null;
      const cost=usd(L.need,price);
      return(
        <div className="pf2-lgb">
          <div className="pf2-lgbh"><span className="lb">League</span>
            {L.cur?<span className="cur"><img src={pfSea(L.cur.emoji)} alt=""/>{L.cur.name}</span>:<span className="cur" style={{color:'rgba(255,255,255,.55)'}}>below {L.next.name}</span>}
            <button className="lnk" onClick={onTiers}>Leagues</button></div>
          {L.next?(
            <>
              <div className="pf2-bar">{L.cur?<img src={pfSea(L.cur.emoji)} alt=""/>:<span style={{width:28}}/>}<div className="pf2-trk" role="progressbar" aria-valuenow={Math.round(L.pct)} aria-valuemin="0" aria-valuemax="100" aria-label={`Progress to ${L.next.name}`}><div className="pf2-fl" style={{width:L.pct+'%'}}></div><i className="pf2-tip" style={{left:L.pct+'%'}}></i></div><img className="nx" src={pfSea(L.next.emoji)} alt=""/></div>
              <div className="pf2-lgbf"><span><b>{L.pct.toFixed(1)}%</b> to <b className="c2">{L.next.name}</b></span><span>need <b>{pfAbbr(L.need)}</b>{cost!=null&&<> {'≈'} {fmtDollar(cost,0)}</>}</span></div>
            </>
          ):<div className="pf2-top c2">Top league reached {'—'} {L.cur.name}</div>}
        </div>
      );
    };
    /* round 2: edit a saved wallet — its label and its group (the classic page's Edit Wallet only renamed) */
    const PfEditWallet=({w,groups,save,remove,close})=>{
      const[name,setName]=useState(w.name||'');
      const[grp,setGrp]=useState(w.group||'Default');
      const[newG,setNewG]=useState('');
      const[copied,setCopied]=useState(false);
      const[rm,setRm]=useState(false);   // round 23 (audit A8): Remove asks first
      const g=grp==='__new'?newG.trim():grp;
      const ok=!(grp==='__new'&&!g);
      const go=()=>{if(ok)save({name:name.trim(),group:g||'Default'});};
      return(
        <PfModal className="z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80" onClose={close} label="Edit wallet">
          <div className="pf2-ew" onClick={e=>e.stopPropagation()}>
            <button className="x" onClick={close} aria-label="Close">{'\u00D7'}</button>
            <h2>EDIT WALLET</h2>
            <div className="lb">Address</div>
            <div className="adr"><span className="mono">{w.address}</span><button onClick={()=>{pfCopy(w.address).then(ok=>{if(ok){setCopied(true);setTimeout(()=>setCopied(false),1500);}});}}>{copied?'Copied':'Copy'}</button></div>
            <label className="lb" htmlFor="pf2-ew-n">Name</label>
            <input id="pf2-ew-n" className="in" value={name} onChange={e=>setName(e.target.value)} placeholder="Give this wallet a name…" autoFocus onKeyDown={e=>e.key==='Enter'&&go()}/>
            <label className="lb" htmlFor="pf2-ew-g">Group</label>
            <select id="pf2-ew-g" className="in" value={grp} onChange={e=>setGrp(e.target.value)}>
              {[...new Set(['Default',...groups,w.group||'Default'])].map(x=><option key={x} value={x}>{x}</option>)}
              <option value="__new">+ New group</option>
            </select>
            {grp==='__new'&&<input className="in" value={newG} onChange={e=>setNewG(e.target.value)} placeholder="New group name…" aria-label="New group name" onKeyDown={e=>e.key==='Enter'&&go()}/>}
            <div className="bt">{rm?<span className="pf2-rmask in"><span>Remove this wallet?</span><button className="y" onClick={remove}>Yes, remove</button><button className="n" onClick={()=>setRm(false)}>Keep</button></span>:<button className="rm" onClick={()=>setRm(true)}>Remove wallet</button>}<span style={{flex:1}}></span><button className="q" onClick={close}>Cancel</button><button className="sv" onClick={go} disabled={!ok}>Save</button></div>
          </div>
        </PfModal>
      );
    };
    /* round 8: Reward yield tile with a plain-English explainer (Shaka: "'on brought in' sounds weird … we need to explain it better") */
    const PF_IC_HOLD='logos/leagues/lg-ic-coins.webp?v=1';   // round 9: his gold coin stack (the Leagues "Starting supply" icon)
    const PF_IC_EARN='logos/portfolio/pf-lifetime4.webp';     // round 13: his lifetime-earned icon (clock + coins)
    /* round 12 (Shaka: "remove the PLS … add Live, Custom, All-time highs … can you get it all into the moon math tile? maybe if you
       select custom it opens a little window for you to put the prices"). The strip under the row is gone: the tile holds a
       three-way toggle; Custom opens a small window anchored to the tile for the PTGC and UFO prices. */
    const PfMoonTile=({on,setOn,customPrices,setCustomPrices,prices,ATH_PRICES})=>{
      const ath={ptgc:String(ATH_PRICES.ptgc),ufo:String(ATH_PRICES.ufo),pls:''};
      const mode=!on||(customPrices.ptgc===''&&customPrices.ufo==='')?(on?'custom':'live'):(customPrices.ptgc===ath.ptgc&&customPrices.ufo===ath.ufo?'ath':'custom');
      const[pop,setPop]=useState(false);
      const ref=React.useRef(null);
      useEffect(()=>{if(!pop)return;const away=e=>{if(ref.current&&!ref.current.contains(e.target))setPop(false);};const key=e=>{if(e.key==='Escape')setPop(false);};
        document.addEventListener('mousedown',away);document.addEventListener('touchstart',away);document.addEventListener('keydown',key);
        return()=>{document.removeEventListener('mousedown',away);document.removeEventListener('touchstart',away);document.removeEventListener('keydown',key);};},[pop]);
      const pick=m=>{
        if(m==='live'){setCustomPrices({ptgc:'',ufo:'',pls:''});setOn(false);setPop(false);}
        else if(m==='ath'){setCustomPrices(ath);setOn(true);setPop(false);}
        else{if(mode==='ath')setCustomPrices({ptgc:'',ufo:'',pls:''});setOn(true);setPop(true);}
      };
      const fld=(k,logo,cls,live,dec)=>(
        <label className={`pf2-mmf ${cls}`}><img src={logo} alt=""/><span className="nm">{k.toUpperCase()}</span>
          <input type="text" inputMode="decimal" autoComplete="off" value={customPrices[k]} onChange={e=>setCustomPrices(c=>({...c,[k]:e.target.value,pls:''}))} placeholder={live?live.toFixed(dec):'0.00'} aria-label={`${k.toUpperCase()} price in dollars`}/>
          <span className="now">now {fmtPriceNode(live)}</span></label>);
      return(
        <div className={`pf2-pn pf2-st mm${on?' on':''}`} ref={ref}>
          <div className="mt"><img className="mo" src="logos/portfolio/pf-moon.webp" alt=""/><b className="oh mmt">MOON MATH</b></div>
          <div className="pf2-mmt3" role="group" aria-label="Prices to use">
            {[['live','Live Prices'],['custom','Custom \u270E'],['ath','\u{1F680} All-Time Highs']].map(([k,l])=>
              <button key={k} aria-pressed={mode===k} className={mode===k?'on':''} onClick={()=>pick(k)}>{l}</button>)}
          </div>
          {pop&&(
            <div className="pf2-mmpop" role="dialog" aria-label="Your own prices">
              <div className="h">Your own prices</div>
              <p>Type the price you want to imagine for PTGC and / or UFO. Every dollar figure on the page {'\u2014'} totals, cards, wallets {'\u2014'} switches to it. Leave one empty to keep its live price.</p>
              {fld('ptgc',TOKENS.PTGC.logo,'p',prices.ptgc,8)}
              {fld('ufo',TOKENS.UFO.logo,'u',prices.ufo,9)}
              <div className="bt"><button className="q" onClick={()=>setCustomPrices({ptgc:'',ufo:'',pls:''})}>Clear</button><button className="ok" onClick={()=>setPop(false)}>Done</button></div>
            </div>)}
          {mode==='custom'&&!pop&&<button className="pf2-mmedit" onClick={()=>setPop(true)}>{customPrices.ptgc||customPrices.ufo?'edit your prices':'enter your prices'}</button>}
        </div>);
    };
    const PortfolioV2=(p)=>{
      const{wallets,portfolioData,loadingAddrs,agg,dp:dp0,prices,changes,groups,isWalletChecked,toggleWallet,selectAllWallets,deselectAllWallets,removeWallet,fetchWalletData,retryFailedReflScans,truncAddr,initialLoad,moonMathActive,setMoonMathActive,customPrices,setCustomPrices,ATH_PRICES}=p;
      /* round 11 (Shaka: "double check the PLS price math"): on the old page a Moon Math PLS price changed NOTHING — no figure
         uses PLS. PTGC and UFO trade against PLS, so "PLS goes to X" now means: same price in PLS, so each token's $ price moves
         by X ÷ today's PLS price. A PTGC or UFO price typed in yourself still wins for that token. */
      /* round 25 (audit C14): while a custom price is being typed ("0.", "", "0") every $ figure went to $0.00 — a custom
         price counts only once it is a number above zero; until then the live price stands */
      const cust=k=>{const v=parseFloat(String(customPrices[k]).replace(',','.'));return moonMathActive&&v>0?v:null;};
      const dp={ptgc:cust('ptgc')!=null?cust('ptgc'):(moonMathActive&&customPrices.ptgc!==''?(prices.ptgc!=null?prices.ptgc:dp0.ptgc):dp0.ptgc),
                ufo:cust('ufo')!=null?cust('ufo'):(moonMathActive&&customPrices.ufo!==''?(prices.ufo!=null?prices.ufo:dp0.ufo):dp0.ufo),pls:dp0.pls};   // round 27 (audit E1): the PLS multiplier maths is gone (v2 has no PLS input since round 12)
      const[q,setQ]=useState('');
      const[grp,setGrp]=useState('All');
      const[showAll,setShowAll]=useState(false);
      const[how,setHow]=useState(false);
      const[allLocks,setAllLocks]=useState(false);
      const[lkOpen,setLkOpen]=useState(false);
      const[xOpen,setXOpen]=useState(false);   // round 34: the UFO card's "Not earning rewards" fold
      const[hChg,setHChg]=useState(null);      // round 34: the value history's period change → the Total tile
      const[bdOpen,setBdOpen]=useState(false);
      const[bdCp,setBdCp]=useState(null);
      const[bdSort,setBdSort]=useState('value');   // round 25 (audit C17): value | name | added
      const[dkSort,setDkSort]=useState(()=>{try{return localStorage.getItem('grays_pf_deck_sort')||'value';}catch(e){return 'value';}});   // round 28: the deck's own sort
      const[edTok,setEdTok]=useState(null);   // round 20: the Earned details window (which token it opened on)
      const ufoElig=usePfUfoEligible();      // round 31: the reward-eligible UFO supply (supply − burned − pools − excluded wallets)
      const[addMsg,setAddMsg]=useState('');
      const[lgTok,setLgTok]=useState(null);
      const[edit,setEdit]=useState(null);   // round 2 (Shaka: "we need to be able to edit a saved wallet"): the wallet being edited
      const[rmAsk,setRmAsk]=useState(null);   // round 23 (audit A8): the card whose ✕ was just tapped — asks before removing
      useEffect(()=>{if(!rmAsk)return;const t=setTimeout(()=>setRmAsk(null),5000);return()=>clearTimeout(t);},[rmAsk]);
      const simulated=moonMathActive&&(customPrices.ptgc!==''||customPrices.ufo!=='');
      const gNames=Object.keys(groups);
      useEffect(()=>{if(grp!=='All'&&!groups[grp])setGrp('All');},[gNames.join('|')]);
      /* per wallet: value at the displayed prices, the PTGC share, its state */
      const wv=w=>{
        const a=w.address.toLowerCase(),d=portfolioData[a];
        const st=loadingAddrs[a]?'run':d&&d.error?'bad':d?'ok':'idle';
        if(!d||d.error)return{a,st,v:null,pv:null,uv:null};
        const pv=usd(d.ptgc.totalHolding,dp.ptgc),uv=usd(d.ufo.balance||0,dp.ufo);
        const v=pv==null&&uv==null?null:(pv||0)+(uv||0);
        return{a,st,v,pv,uv};
      };
      const counted=wallets.filter(w=>isWalletChecked(w.address));
      const anyData=counted.some(w=>{const d=portfolioData[w.address.toLowerCase()];return d&&!d.error;});
      const ptgcUSD=anyData?usd(agg.ptgc.totalHolding,dp.ptgc):null;
      const ufoUSD=anyData?usd(agg.ufo.balance,dp.ufo):null;
      const total=ptgcUSD==null&&ufoUSD==null?null:(ptgcUSD||0)+(ufoUSD||0);
      /* 24h: today's holdings at yesterday's prices (the price move, not trades) — step 2 swaps in real balances */
      /* step 2 (value history, option C): the counted wallets' real balances from the chain */
      const hAddrs=counted.map(w=>w.address.toLowerCase());
      const[hPeriod,setHPeriod]=useState('30D');
      const v1=usePfUfoV1(hAddrs);   // round 15: UFO reflections earned on the OLD contract (see usePfUfoV1)
      const[txs,setTxs]=useState(null);   // round 14: Recent Transactions → the value chart's buy / sell dots
      const[txP,setTxP]=useState(null);   // round 30: the first PulseScan read's progress → the chart's loader
      const liveP=anyData?usd(agg.ptgc.totalHolding,prices.ptgc):null,liveU=anyData?usd(agg.ufo.balance,prices.ufo):null;
      const liveV=liveP==null&&liveU==null?null:(liveP||0)+(liveU||0);
      const live={v:liveV,p:liveP||0,u:liveU||0,bp:anyData?agg.ptgc.totalHolding:null,bu:anyData?agg.ufo.balance:null};
      const s30=usePfSeries(hAddrs,'30D',anyData);
      const h24=usePf24h(anyData?hAddrs:[]);
      const spk=k=>s30.pts.length?[...s30.pts.map(x=>x.v==null?null:x[k]),live[k]]:null;   // round 25 (audit C4): sparklines keep showing while a toggle reloads
      const prev=(v,c)=>v==null?null:c==null||isNaN(c)?null:v/(1+c/100);
      const pPrev=prev(ptgcUSD,changes.ptgc),uPrev=prev(ufoUSD,changes.ufo);
      const tChg=h24&&liveV!=null&&h24.v>0?(liveV-h24.v)/h24.v*100:simulated||total==null||(ptgcUSD>0&&pPrev==null)||(ufoUSD>0&&uPrev==null)?null:(()=>{const pr=(pPrev||0)+(uPrev||0);return pr>0?(total-pr)/pr*100:null;})();
      const shown=wallets.filter(w=>(grp==='All'||(w.group||'Default')===grp)&&(!q.trim()||(w.name||'').toLowerCase().includes(q.trim().toLowerCase())||w.address.toLowerCase().includes(q.trim().toLowerCase())));
      if(dkSort==='value')shown.sort((x,y)=>(wv(y).v||0)-(wv(x).v||0));else if(dkSort==='name')shown.sort((x,y)=>(x.name||x.address).localeCompare(y.name||y.address));   // 'added' = the saved order
      const cutN=typeof window!=='undefined'&&window.matchMedia&&window.matchMedia('(max-width:700px)').matches?6:window.matchMedia&&window.matchMedia('(max-width:1100px)').matches?20:28;   // matches pf2.css .cut
      const allOn=wallets.length>0&&wallets.every(w=>isWalletChecked(w.address));
      const noneOn=wallets.every(w=>!isWalletChecked(w.address));
      const add=()=>{
        const a=p.inputAddr.trim();
        if(!/^0x[0-9a-fA-F]{40}$/.test(a)){setAddMsg('That is not a wallet address — it should start with 0x and be 42 characters.');return;}
        if(wallets.find(w=>w.address.toLowerCase()===a.toLowerCase())){setAddMsg('That wallet is already in your portfolio.');return;}
        if(p.inputGroup==='__new'){setAddMsg(p.newGroupName.trim()?'Press Create next to the new group name first (or pick a group).':'Name the new group and press Create first (or pick a group).');return;}   // round 23 (audit A10): used to save the group as "__new"
        setAddMsg('');p.addWallet();
      };
      const pt=agg.ptgc,uf=agg.ufo;
      const ufoRefl=uf.reflState==='ok'?uf.reflections:null;
      /* round 6 (Shaka: "make sure your math is right … what if they earned a lot of reflections early on, and they sold most of
         that … the yield would look super high because it's against the current total"). Reflections here are LIFETIME
         (balance + everything sent − everything received), so dividing by today's bag is wrong once anything was sold.
         Yield = lifetime reflections ÷ every token the wallets ever RECEIVED (bought / transferred in) — selling cannot move
         it. The UFO split of TODAY's bag is pro-rata: the share of all tokens ever obtained that came from reflections,
         R ÷ (received + R), applied to the current holdings (sells are assumed to take principal and reflections alike), so
         it can never show more reflections than were earned or a negative principal. */
      const okW=counted.map(w=>portfolioData[w.address.toLowerCase()]).filter(d=>d&&!d.error);
      const ufRecv=(()=>{if(!okW.length)return null;let t=0;for(const w of counted){const a=w.address.toLowerCase(),d=portfolioData[a];if(!d||d.error)continue;if(!(d.ufo.balance>0))continue;const r=(window.pfUfoRecv||{})[a];if(typeof r!=='number')return null;t+=r;}return t;})();
      /* round 15: + the OLD UFO contract's reflections (to the 2026-07-06 migration). They are lifetime, so every counted wallet adds
         its share, sold-out ones too (ufoOld). For the split of today's bag only wallets still holding UFO count (ufoOldHeld): the
         migration airdrop sits inside ufRecv, and the old reflections are the part of it that was earned — so
         share = (new + old reflections) ÷ (received + new reflections), never above 1. If the file can't be read the page shows the
         new contract alone with an "old contract not included · retry" note (round 23). */
      const v1Sum=held=>v1.state!=='ok'?null:counted.reduce((t,w)=>{const a=w.address.toLowerCase(),d=portfolioData[a];if(!d||d.error)return t;if(held&&!(d.ufo.balance>0))return t;return t+v1.of(a);},0);
      const ufoOld=v1Sum(false),ufoOldHeld=v1Sum(true);
      const ufoNew=ufoRefl;
      const ufoEarned=ufoNew==null?null:v1.state==='loading'?null:ufoNew+(ufoOld||0);
      /* round 7 (option A of mock-rewards-v1): REWARDS = staking + locking + reflections (UFO: reflections only).
         Reward yield = everything earned ÷ the tokens the wallets BROUGHT IN. Checked on chain 2026-10-13: a lock claim is a
         Transfer from the staking contract, PTGC's totalReceived rises by exactly the claim and lockClaimed by the same amount —
         so claims sit inside "received" (and outside reflections). Brought in = received − staking claims − lock claims. */
      const ptEarned=pt.claimed+pt.lockClaimed+pt.reflections;
      const ufoShare=ufoEarned==null||ufRecv==null||!((ufRecv+ufoNew)>0)?null:Math.min(1,(ufoNew+(ufoOldHeld||0))/(ufRecv+ufoNew));
      const ufoReflNow=ufoShare==null?null:uf.balance*ufoShare,ufoPrin=ufoShare==null?null:uf.balance-ufoReflNow;
      const fmtLock=t=>{if(!t)return'—';const now=Date.now()/1000;if(t<=now)return'Unlockable';const d=Math.floor((t-now)/86400);if(d>365)return Math.floor(d/365)+'y '+Math.floor((d%365)/30)+'m';if(d>30)return Math.floor(d/30)+'m '+d%30+'d';if(d>0)return d+'d';const h=Math.floor((t-now)/3600);return h>0?h+'h':Math.max(1,Math.floor((t-now)/60))+'m';};
      const reflBox=()=>uf.reflState==='pending'?<><div className="v" style={{fontSize:16,color:'rgba(255,255,255,.5)'}}>scanning{'…'}</div><div className="s">{uf.reflPending} wallet{uf.reflPending>1?'s':''}</div></>
        :uf.reflState==='failed'?<><div className="v" style={{fontSize:16,color:'#FFD38A'}}>unavailable</div><div className="s"><button onClick={retryFailedReflScans}>Retry</button></div></>
        :ufoEarned==null?<><div className="v" style={{fontSize:16,color:'rgba(255,255,255,.5)'}}>loading{'…'}</div><div className="s">old UFO contract</div></>
        :<><div className="v">{pfAbbr(ufoEarned)}</div><div className="s">{fmtDollar(usd(ufoEarned,dp.ufo))}</div>{v1.state==='failed'&&<div className="s warn">old UFO contract not included {'\u00B7'} <button onClick={v1.retry}>retry</button></div>}</>;
      return(
        <div className="pf2"><div className="pf2-in">
          {/* ---- title, add capsule, toolbar, the deck ---- */}
          <div className="pf2-ttl"><h1><span className="pf2-tt g">Grays</span><span className="pf2-tt w">Portfolio</span></h1><p>Track PTGC and UFO across all your wallets</p></div>
          <div className="pf2-add">
            <div className="f a1"><img src="logos/portfolio/pf-wallet.webp" alt=""/><input className="ad" value={p.inputAddr} onChange={e=>{p.setInputAddr(e.target.value);setAddMsg('');}} placeholder="Paste a wallet address (0x…)" aria-label="Wallet address" spellCheck="false" autoComplete="off" onKeyDown={e=>e.key==='Enter'&&add()}/></div>
            <div className="f l"><small>LABEL</small><input value={p.inputName} onChange={e=>p.setInputName(e.target.value)} placeholder="My Wallet" aria-label="Label (optional)" onKeyDown={e=>e.key==='Enter'&&add()}/></div>
            <div className="f g"><small>GROUP</small><select value={p.inputGroup} onChange={e=>p.setInputGroup(e.target.value)} aria-label="Group">
              <option value="Default">Default</option>
              {gNames.filter(g=>g!=='Default').map(g=><option key={g} value={g}>{g}</option>)}
              {p.inputGroup!=='Default'&&p.inputGroup!=='__new'&&!groups[p.inputGroup]&&<option value={p.inputGroup}>{p.inputGroup}</option>}
              <option value="__new">+ New group</option>
            </select></div>
            <button className="pf2-addb" onClick={add} disabled={!p.inputAddr.trim()}>+ ADD WALLET</button>
          </div>
          {p.inputGroup==='__new'&&(
            <div className="pf2-newg"><input value={p.newGroupName} onChange={e=>p.setNewGroupName(e.target.value)} placeholder="New group name…" aria-label="New group name" onKeyDown={e=>{if(e.key==='Enter'&&p.newGroupName.trim()){p.setInputGroup(p.newGroupName.trim());p.setNewGroupName('');}}}/><button className="pf2-lnk" onClick={()=>{if(p.newGroupName.trim()){p.setInputGroup(p.newGroupName.trim());p.setNewGroupName('');}}}>Create</button></div>
          )}
          {addMsg&&<div className="pf2-addmsg" role="alert">{addMsg}</div>}
          {/* round 29 (Shaka: "better visual separation from the wallets to the start of all the data" — picked C of mock-sep-v1):
              the toolbar + deck (+ the Moon Math banner) sit in their own bordered panel, then the YOUR HOLDINGS heading */}
          <section className="pf2-pn pf2-wpan" aria-label="My wallets">
          <div className="pf2-tools">
            <b>MY WALLETS <span>({wallets.length})</span></b>
            {wallets.length>0&&(()=>{const bad=counted.filter(w=>{const d=portfolioData[w.address.toLowerCase()];return d&&d.error;}).length;return <span className="sum">{'·'} <strong>{counted.length}</strong> counted {'·'} <strong>{fmtDollar(total)}</strong>{bad>0&&<span className="warn"> {'·'} {bad} unreadable</span>}</span>;})()}
            {wallets.length>0&&<><button className="pf2-lnk" onClick={selectAllWallets} disabled={allOn}>Select all</button><button className="pf2-lnk q" onClick={deselectAllWallets} disabled={noneOn}>Clear</button></>}
            <span className="sp"></span>
            {wallets.length>2&&<div className="pf2-bds" role="group" aria-label="Sort wallets"><span>Sort</span>{[['value','Value'],['name','Name'],['added','Added']].map(([k,l])=><button key={k} className={dkSort===k?'on':''} aria-pressed={dkSort===k} onClick={()=>{setDkSort(k);try{localStorage.setItem('grays_pf_deck_sort',k);}catch(e){}}}>{l}</button>)}</div>}
            {gNames.length>1&&<div className="pf2-seg" role="group" aria-label="Show group">{['All',...gNames].map(g=><button key={g} className={grp===g?'on':''} aria-pressed={grp===g} onClick={()=>setGrp(g)}>{g}</button>)}</div>}
            {wallets.length>4&&<div className="pf2-srch"><span aria-hidden="true">{'⌕'}</span><input value={q} onChange={e=>setQ(e.target.value)} placeholder="Search wallets…" aria-label="Search wallets"/></div>}
            <button className="pf2-how" onClick={()=>setHow(true)}>{'ⓘ'} HOW IT WORKS</button>
          </div>
          <div className={`pf2-deck${showAll?'':' cut'}`}>
            {initialLoad&&wallets.length===0?null:wallets.length===0?(
              <div className="pf2-empty"><b>No wallets yet</b>Paste a wallet address above to see its PTGC and UFO {'—'} or use <span style={{color:'#F6E98A'}}>Load Code</span> in the header to restore a saved portfolio.</div>
            ):shown.length===0?(
              <div className="pf2-empty">No wallet matches {q.trim()?<>{'“'}{q.trim()}{'”'}</>:'this group'}.</div>
            ):shown.map(w=>{
              const{a,st,v,pv}=wv(w);const on=isWalletChecked(w.address);const label=w.name||pfAddr(w.address);
              const ps=v>0?(pv||0)/v:null;
              return(
                <div key={a} className={`pf2-wc ${on?'on':'off'}${st==='bad'?' bad':''}`}>
                  <div className="r1"><button className="pf2-tg" role="switch" aria-checked={on} aria-label={`Count ${label} in the totals`} onClick={()=>toggleWallet(w.address)}></button><span className={w.name?'nm':'nm mono'} title={w.name?`${w.address} \u00B7 ${w.group||'Default'}`:(w.group||'Default')}>{label}</span><button className="pf2-ed" onClick={()=>setEdit(w.address.toLowerCase())} aria-label={`Edit ${label}`} title="Edit name / group">✎</button><span className={`pf2-dot ${st==='ok'?'':st}`} role="img" aria-label={st==='ok'?'Loaded':st==='run'?'Loading':st==='bad'?'Read failed':'Not loaded'} title={st==='ok'?'Loaded':st==='run'?'Loading…':st==='bad'?'The chain read failed':''}></span></div>
                  {st==='bad'?<button className="retry" onClick={()=>fetchWalletData(w.address)}>Read failed {'·'} retry</button>
                  :v==null?<div className="v dim">{st==='run'?'loading…':'—'}</div>
                  :<>
                    <div className="v">{fmtDollar(v)}</div>
                    <div className="pf2-split" aria-hidden="true">{ps!=null&&<><i className="p" style={{width:ps*100+'%'}}></i><i className="u" style={{width:(1-ps)*100+'%'}}></i></>}</div>
                    <div className="r3"><span className="p">PTGC {ps==null?'—':Math.round(ps*100)+'%'}</span><span className="u">UFO {ps==null?'—':Math.round((1-ps)*100)+'%'}</span></div>
                  </>}
                  <div className="acts">{rmAsk===a?<span className="pf2-rmask" role="alertdialog" aria-label={`Remove ${label}?`}>Remove? <button className="y" onClick={()=>{removeWallet(w.address);setRmAsk(null);}}>Yes</button><button className="n" onClick={()=>setRmAsk(null)}>No</button></span>
                    :<button onClick={()=>setRmAsk(a)} aria-label={`Remove ${label}`} title="Remove this wallet">✕</button>}</div>
                </div>
              );
            })}
            {!showAll&&shown.length>cutN&&<button className="pf2-more" onClick={()=>setShowAll(true)}>Show all {shown.length} wallets {'▾'}</button>}
          </div>
          {moonMathActive&&(()=>{const isAth=customPrices.ptgc===String(ATH_PRICES.ptgc)&&customPrices.ufo===String(ATH_PRICES.ufo);const none=customPrices.ptgc===''&&customPrices.ufo==='';return(
            <div className="pf2-mm"><img src="logos/portfolio/pf-moon.webp" alt=""/>Moon Math is on {'\u2014'} {isAth?'your holdings, rewards and totals are valued at the All-Time High prices.':none?'Custom is selected: type a PTGC and / or UFO price in the Moon Math window (live prices until you do).':'your holdings, rewards and totals are valued at your custom prices.'} <span className="mmn">(The value history and the transactions stay at real prices.)</span> <button className="pf2-mmoff" onClick={()=>{setCustomPrices({ptgc:'',ufo:'',pls:''});setMoonMathActive(false);}}>Back to Live Prices</button></div>);})()}
          </section>

          {/* round 23 (audit A2): with every wallet switched off this used to say "Reading your wallets…" forever */}
          {wallets.length>0&&!anyData&&(()=>{const run=counted.some(w=>loadingAddrs[w.address.toLowerCase()]);const bad=counted.filter(w=>{const d=portfolioData[w.address.toLowerCase()];return d&&d.error;});return(
            <section className="pf2-pn pf2-sec" style={{marginTop:20}}><div className="pf2-soon" role="status">{!counted.length?<><b>No wallets are counted.</b> Switch one on above (or <button className="pf2-lnk" onClick={selectAllWallets}>Select all</button>) to see the totals.</>:run||!bad.length?<><b>Reading your wallets from the chain{'\u2026'}</b></>:<><b>Couldn{'\u2019'}t read your wallets from the chain right now.</b> The PulseChain node did not answer {'\u2014'} nothing is wrong with your list.<div style={{marginTop:12}}><button className="pf2-lnk" onClick={()=>bad.forEach(w=>fetchWalletData(w.address))}>Retry all</button></div></>}</div></section>);})()}
          {wallets.length>0&&anyData&&<>
          <div className="pf2-hsec"><h2 className="oh">YOUR HOLDINGS <span>{counted.length} wallet{counted.length===1?'':'s'} counted</span></h2><i aria-hidden="true"></i></div>
          {/* ---- three summary tiles ---- */}
          <div className="pf2-row3 r4 hd">
            <section className="pf2-pn pf2-st t"><div className="ic w"><img src="logos/portfolio/pf-wallet.webp" alt=""/></div>
              <div className="tx"><div className="lb">Total portfolio value</div><div className="v">{fmtDollar(total)}</div><div className="s">{simulated?<span className="na">Moon Math prices</span>:pfChg(tChg)}</div>{!simulated&&hChg&&<div className={`s2 ${hChg.chg>=0?'pos':'neg'}`}>{hChg.chg>=0?'\u25B2 +':'\u25BC \u2212'}{Math.abs(hChg.chg).toFixed(2)}% ({hChg.period})</div>}</div><PfSpark vals={spk('v')} col={tChg!=null&&tChg<0?'#FF4B55':'#7CFC00'}/></section>
            <section className="pf2-pn pf2-st p"><div className="ic"><img src={TOKENS.PTGC.logo} alt=""/></div>
              <div className="tx"><div className="lb">PTGC value</div><div className="v">{fmtDollar(ptgcUSD)}</div><div className="s" style={{color:'#F2D35B'}}>{pfPct(ptgcUSD,total)}</div></div><PfSpark vals={spk('p')} col="#F2D35B"/></section>
            <section className="pf2-pn pf2-st u"><div className="ic"><img src={TOKENS.UFO.logo} alt=""/></div>
              <div className="tx"><div className="lb">UFO value</div><div className="v">{fmtDollar(ufoUSD)}</div><div className="s" style={{color:'#8DFF3A'}}>{pfPct(ufoUSD,total)}</div></div><PfSpark vals={spk('u')} col="#7CFC00"/></section>
            {/* round 10 (Shaka: "shrink the three boxes a hair so we can move the moon math box to the end there") */}
            <PfMoonTile on={moonMathActive} setOn={setMoonMathActive} customPrices={customPrices} setCustomPrices={setCustomPrices} prices={prices} ATH_PRICES={ATH_PRICES}/>
          </div>

          {/* ---- the two token cards ---- */}
          <div className="pf2-tok2">
            <section className="pf2-tk p">
              <div className="pf2-tkh"><img className="lg" src={TOKENS.PTGC.logo} alt=""/>
                <div className="nm"><div className="t">PTGC</div><div className="sb">The Grays Currency</div><PfCreatures tokens={pt.totalHolding} token="PTGC"/></div>
                <div className="px"><div className="a">{fmtPriceNode(prices.ptgc)}</div><div className="c">{pfChg(changes.ptgc)}</div></div></div>
              <div className="pf2-t4 t2">
                <div className="pf2-bx gold big"><img className="bic" src={PF_IC_HOLD} alt=""/><div><div className="lb">Total holdings</div><div className="v">{pfAbbr(pt.totalHolding)}</div><div className="s">{fmtDollar(usd(pt.totalHolding,dp.ptgc))}</div></div></div>
                <div className="pf2-bx rf big"><img className="bic" src={PF_IC_EARN} alt=""/><div><div className="lb">Lifetime earned</div><div className="v">{pfAbbr(ptEarned)}</div><div className="s">{fmtDollar(usd(ptEarned,dp.ptgc))}</div></div></div>
              </div>
              {pt.totalHolding>0?(()=>{const parts=[['Liquid',pt.walletFree,'#F2D35B'],['Staked (not locked)',pt.stakedOnly,'#B26BFF'],['Locked & staked',pt.locked,'#EC4899']].filter(x=>x[1]>0);return(
                <div className="pf2-dn"><PfRing parts={parts.map(x=>[x[1],x[2]])}/>
                  <div className="pf2-lg2">{parts.map(x=><div className="r" key={x[0]}><i style={{background:x[2]}}></i><span>{x[0]}</span><b>{pfAbbr(x[1])}</b><span className="usd">{fmtDollar(usd(x[1],dp.ptgc))}</span><em>{pfPct(x[1],pt.totalHolding)}</em></div>)}</div></div>);})()
              :<div className="pf2-wait">No PTGC in the counted wallets</div>}
              <div className="pf2-lgw"><PfLeague balance={pt.totalHolding} token="PTGC" price={dp.ptgc} onTiers={()=>setLgTok('PTGC')}/></div>
              <div className="pf2-ebs">
                <div className="h">Earned by source<button className="pf2-edb" onClick={()=>setEdTok('PTGC')} aria-label="PTGC rewards per day, last 30 days"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true"><path d="M2.5 13.5h11"/><path d="M4.5 11V7.5"/><path d="M8 11V4"/><path d="M11.5 11V6"/></svg>Details {'\u00B7'} 30D</button></div>
                <div className="pf2-src3">
                  {[['Staking','st',pt.claimed],['Locking','lk',pt.lockClaimed],['Reflections','rf',pt.reflections]].map(([n,c,v])=>(
                    <div key={n} className={`pf2-src ${c}`}><div className="l">{n}</div><div className="v">{pfAbbr(v)}</div><div className="s">{fmtDollar(usd(v,dp.ptgc))}</div><div className="p">{pfPct(v,ptEarned)} of earned</div></div>))}
                </div>
                {/* round 32 (Shaka: "this ready to claim section needs help… looks like a footer" — picked C of mock-claim-v1, kept
                    under the Earned-by-source tiles): a green-gold spotlight — the amount big, the dollars, a Staking / Locks bar */}
                {(pt.totalPending>0||pt.staked>0)&&(()=>{const tp=pt.totalPending||0,ps=pt.pendingStake||0,pl=pt.pendingLocks||0;return(
                  <div className="pf2-spot"><img src="logos/portfolio/pf-claim2.webp" alt=""/>
                    <div className="b"><div className="k"><i aria-hidden="true"></i>READY TO CLAIM</div>
                      <div className="v">{pfAbbr(tp)}<small>PTGC</small></div>
                      <div className="u">{tp>0?<>{fmtDollar(usd(tp,dp.ptgc))} waiting to be claimed</>:<>Nothing to claim yet {'\u2014'} rewards build up while you stake</>}</div>
                      {tp>0&&<><div className="bar" aria-hidden="true"><i style={{width:ps/tp*100+'%',background:'#B26BFF'}}></i><i style={{width:pl/tp*100+'%',background:'#EC4899'}}></i></div>
                        <div className="lg"><span><i style={{background:'#B26BFF'}}></i>Staking <b>{pfAbbr(ps)}</b> {'\u00B7'} {fmtDollar(usd(ps,dp.ptgc))}</span><span><i style={{background:'#EC4899'}}></i>Locks <b>{pfAbbr(pl)}</b> {'\u00B7'} {fmtDollar(usd(pl,dp.ptgc))}</span></div></>}
                    </div>
                  </div>);})()}
              </div>
              <div className="pf2-extw">
              {pt.locks.length>0&&(()=>{
                const now=Date.now()/1000;
                const locks=[];counted.forEach(w=>{const d=portfolioData[w.address.toLowerCase()];if(d&&!d.error)d.ptgc.locks.forEach(l=>locks.push({...l,who:w.name||pfAddr(w.address)}));});
                locks.sort((a,b)=>a.endTime-b.endTime);
                const shownL=allLocks?locks:locks.slice(0,6);
                const fmtD=t=>{try{return new Date(t*1000).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});}catch(e){return'';}};
                const ready=locks.filter(l=>l.endTime<=now).length;
                return(
                <div className={`pf2-lkd${lkOpen?' open':''}`}>
                  <button className="pf2-lkh" aria-expanded={lkOpen} onClick={()=>setLkOpen(!lkOpen)}><span className="t">{'\u{1F512}'} Lock positions</span><span className="n">{locks.length}{ready?<> {'\u00B7'} <b>{ready} unlockable</b></>:null}{(()=>{const nx=locks.find(l=>l.endTime>now);return nx?<> {'\u00B7'} next unlock in {pfIn(nx.endTime-now)}</>:null;})()}</span><span className="chev">{'\u25BE'}</span></button>
                  {lkOpen&&<div className="pf2-lkb">
                    <a className="pf2-rlv" href="https://goptgc.com" target="_blank" rel="noopener noreferrer">Verify on goptgc.com before unlocking {'\u2197'}</a>
                    {shownL.map((l,i)=>{
                      const done=l.endTime<=now;const span=l.endTime-l.startTime;const pc=done?100:span>0?Math.max(0,Math.min(100,(now-l.startTime)/span*100)):0;
                      return(
                        <div key={i} className={`pf2-lk${done?' done':''}`}>
                          <div className="a"><b>{pfAbbr(l.amount)} PTGC</b><span>{fmtDollar(usd(l.amount,dp.ptgc))}</span>{counted.length>1&&<small>{l.who}</small>}</div>
                          <div className="t"><b>{done?'Unlockable':fmtLock(l.endTime)}</b><span>{done?'since ':'unlocks '}{fmtD(l.endTime)}</span><div className="pg" aria-hidden="true"><i style={{width:pc+'%'}}></i></div></div>
                          <div className="r"><b>+{pfAbbr(l.pending)}</b><span>pending</span></div>
                        </div>);
                    })}
                    {locks.length>6&&<button className="pf2-lnk q" style={{marginTop:10}} onClick={()=>setAllLocks(!allLocks)}>{allLocks?'Show fewer':`Show all ${locks.length} locks`}</button>}
                  </div>}
                </div>);
              })()}
              </div>
            </section>

            <section className="pf2-tk u">
              <div className="pf2-tkh"><img className="lg" src={TOKENS.UFO.logo} alt=""/>
                <div className="nm"><div className="t">UFO</div><div className="sb">UFO Token</div><PfCreatures tokens={uf.balance} token="UFO"/></div>
                <div className="px"><div className="a">{fmtPriceNode(prices.ufo)}</div><div className="c">{pfChg(changes.ufo)}</div></div></div>
              <div className="pf2-t4 t2">
                <div className="pf2-bx grn big"><img className="bic" src={PF_IC_HOLD} alt=""/><div><div className="lb">Total holdings</div><div className="v">{pfAbbr(uf.balance)}</div><div className="s">{fmtDollar(usd(uf.balance,dp.ufo))}</div></div></div>
                <div className="pf2-bx grn big"><img className="bic" src={PF_IC_EARN} alt=""/><div><div className="lb">Lifetime earned</div>{reflBox()}</div></div>
              </div>
              {uf.balance>0&&ufoShare!=null?(
                <div className="pf2-dn"><PfRing parts={[[ufoPrin,'#7CFC00'],[ufoReflNow,'#22D3EE']]}/>
                  <div className="pf2-lg2">
                    <div className="r"><i style={{background:'#7CFC00'}}></i><span>Principal</span><b>{pfAbbr(ufoPrin)}</b><span className="usd">{fmtDollar(usd(ufoPrin,dp.ufo))}</span><em>{pfPct(ufoPrin,uf.balance)}</em></div>
                    <div className="r"><i style={{background:'#22D3EE'}}></i><span>From reflections</span><b>{pfAbbr(ufoReflNow)}</b><span className="usd">{fmtDollar(usd(ufoReflNow,dp.ufo))}</span><em>{pfPct(ufoReflNow,uf.balance)}</em></div>
                  </div></div>
              ):<div className="pf2-wait">{!(uf.balance>0)?'No UFO in the counted wallets':uf.reflState==='failed'?'Reflections unavailable — the chain read failed':'Reading the reflections from the chain…'}</div>}
              <div className="pf2-lgw"><PfLeague balance={uf.balance} token="UFO" price={dp.ufo} onTiers={()=>setLgTok('UFO')}/></div>
              <div className="pf2-ebs">
                <div className="h">Earned by source<button className="pf2-edb" onClick={()=>setEdTok('UFO')} aria-label="UFO rewards per day, last 30 days"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" aria-hidden="true"><path d="M2.5 13.5h11"/><path d="M4.5 11V7.5"/><path d="M8 11V4"/><path d="M11.5 11V6"/></svg>Details {'\u00B7'} 30D</button></div>
                {/* round 16 (Shaka: "treat it as just one UFO … one box with a total"): old + new contract reflections in one box */}
                <div className="pf2-src3 one"><div className="pf2-src rf"><div className="l">Reflections</div>{ufoEarned==null?<div className="v" style={{fontSize:16,color:'rgba(255,255,255,.55)'}}>{uf.reflState==='failed'?'unavailable':'scanning\u2026'}</div>:<><div className="v">{pfAbbr(ufoEarned)}</div><div className="s">{fmtDollar(usd(ufoEarned,dp.ufo))}</div><div className="p">{v1.state==='failed'?<span className="warn">old contract not included {'\u00B7'} <button onClick={v1.retry}>retry</button></span>:'100% of earned'}</div></>}</div></div>
                {/* round 19 (option B of mock-r18-v1): mirrors PTGC's Ready to claim — UFO pays automatically, nothing to claim. Share of every
                    holder reward = the counted UFO ÷ the REWARD-ELIGIBLE supply (round 31: supply − burned − pools − excluded wallets, PfLeagues.jsx). */}
                {/* round 33 (Shaka: "The UFO side needs to match the look of the ptgc side"): the same spotlight — the share big, a bar of
                    your slice of the reward-eligible supply (round 31), the excluded balances as the legend */}
                {uf.balance>0&&(()=>{const el=ufoElig;const den=el?el.elig:PF_SUPPLY.UFO;const sh=uf.balance/den*100;const shs=sh<0.01?'<0.01':sh.toFixed(sh<1?3:2);return(
                  <div className="pf2-spot u"><img src={TOKENS.UFO.logo} alt=""/>
                    <div className="b"><div className="k"><i aria-hidden="true"></i>PAID TO YOUR WALLET AUTOMATICALLY</div>
                      <div className="v">{'\u2248'} {shs}%<small>of every holder reward</small></div>
                      <div className="u">1% of every UFO buy, sell and transfer {'\u2014'} paid straight to your wallet, nothing to claim</div>
                      <div className="bar" aria-hidden="true"><i style={{width:Math.max(0.5,Math.min(100,sh))+'%',background:'#7CFC00'}}></i></div>
                      <div className="lg">{el?<><span><i style={{background:'#7CFC00'}}></i>Your <b>{pfAbbr(uf.balance)}</b> of the <b>{pfAbbr(el.elig)}</b> UFO that earns rewards</span></>
                        :<span><i style={{background:'#7CFC00'}}></i>Your <b>{pfAbbr(uf.balance)}</b> of the total supply {'\u00B7'} reading the reward-eligible supply{'\u2026'}</span>}</div>
                    </div>
                  </div>);})()}
              </div>
              {/* round 34 (Shaka: "I want them to look aligned always"): the UFO card's sixth row, opposite Lock positions — the
                  balances that earn no holder reward (the round-31 audit made visible) */}
              {uf.balance>0&&(()=>{const el=ufoElig;const list=el&&el.list?el.list.filter(x=>x.v>0).sort((a,b)=>b.v-a.v):[];const tot=list.reduce((t,x)=>t+x.v,0);
                const name=x=>x.k==='burn'?'Burn address':x.k==='contract'?'UFO token contract':x.k==='wallet'?'Excluded wallet':x.a.toLowerCase()===TOKENS.UFO.mainPair.toLowerCase()?'UFO / WPLS pool (main)':'PulseX liquidity pool';
                return(
                <div className={`pf2-lkd x${xOpen?' open':''}`}>
                  <button className="pf2-lkh" aria-expanded={xOpen} onClick={()=>setXOpen(!xOpen)}><span className="t">{'\u{1F6F8}'} Not earning rewards</span><span className="n">{el?<>{list.length} addresses {'\u00B7'} <b>{pfAbbr(tot)} UFO</b></>:'reading\u2026'}</span><span className="chev">{'\u25BE'}</span></button>
                  {xOpen&&<div className="pf2-lkb">
                    <div className="pf2-xn">These balances are excluded from the holder reward, so the 1% of every transfer is shared among the other {el?pfAbbr(el.elig):'\u2014'} UFO {'\u2014'} that is what your share above is measured against.</div>
                    {list.map(x=><div key={x.a} className={`pf2-lk x ${x.k}`}><div className="a"><b>{name(x)}</b><span className="mono">{pfAddr(x.a)}</span></div><div className="t"><b>{pfAbbr(x.v)} UFO</b><span>{el&&el.supply>0?(x.v/el.supply*100).toFixed(2):'\u2014'}% of supply</span></div><a className="r lk" href={`https://scan.pulsechain.com/address/${x.a}`} target="_blank" rel="noopener noreferrer" aria-label={`${name(x)} on PulseScan`}>{'\u2197'}</a></div>)}
                  </div>}
                </div>);})()}
            </section>
          </div>

          {/* ---- step 2: value history (real chain balances) + recent transactions ---- */}
          <PfValueHistory addrs={hAddrs} live={live} period={hPeriod} setPeriod={setHPeriod} txs={txs} txp={txP} wallets={wallets} onChg={setHChg}/>
          <PfRecentTx wallets={counted} prices={prices} onRows={setTxs} onProgress={setTxP}/>

          {/* ---- the two folds ---- */}
          <div className="pf2-folds one">
            <section className="pf2-pn pf2-fold">
              <button className="pf2-foldh" aria-expanded={bdOpen} onClick={()=>setBdOpen(!bdOpen)}><b className="oh">PER-WALLET BREAKDOWN</b><span>{counted.length} wallet{counted.length===1?'':'s'}</span><span className="chev">{'▾'}</span></button>
              {/* round 19 (option A of mock-r18-v1, cards on a phone): tokens with $ under each, Pending to claim in PTGC yellow, UFO as one
                  total, a Total column with each wallet's share (bar split PTGC yellow / UFO green), copy buttons, an All-wallets row. */}
              {bdOpen&&(()=>{const COL=['#B26BFF','#F2D35B','#22D3EE','#FF8A3D','#EC4899','#7CFC00','#6FA8FF','#FF6B73'];
                const rows=counted.map((w,i)=>{const a=w.address.toLowerCase(),d=portfolioData[a];if(!d||d.error)return null;
                  const pT=d.ptgc.totalHolding||0,pc=d.ptgc.totalPending||0,uT=d.ufo.balance||0,p$=usd(pT,dp.ptgc)||0,u$=usd(uT,dp.ufo)||0;
                  return{w,a,i,c:COL[i%COL.length],pT,pc,uT,p$,c$:usd(pc,dp.ptgc)||0,u$,t$:p$+u$,g:w.group||'Default'};}).filter(Boolean);
                if(bdSort==='value')rows.sort((x,y)=>y.t$-x.t$);else if(bdSort==='name')rows.sort((x,y)=>(x.w.name||x.a).localeCompare(y.w.name||y.a));
                const S=(k,rs=rows)=>rs.reduce((t,r)=>t+r[k],0),all=S('t$');
                /* group subtotals when more than one group is counted */
                const gs=[...new Set(rows.map(r=>r.g))];const grouped=gs.length>1;
                const order=grouped?gs.flatMap(g=>{const rs=rows.filter(r=>r.g===g);return rs.length>1?[...rs,{sub:g,rs}]:rs;}):rows;   // a subtotal only where a group has 2+ wallets
                const cpy=a=>{pfCopy(a).then(ok=>{if(!ok)return;setBdCp(a);setTimeout(()=>setBdCp(x=>x===a?null:x),1400);});};
                const who=r=><><div className="n"><i style={{background:r.c}}></i>{r.w.name||pfAddr(r.w.address)}</div>
                  <div className="ad">{r.w.name?pfAddr(r.w.address):<span className="g">{r.g}</span>}<button className={`cp${bdCp===r.a?' ok':''}`} onClick={()=>cpy(r.w.address)} title={`Copy ${r.w.address}`} aria-label={`Copy wallet address ${r.w.address}`}>{bdCp===r.a?'\u2713':'\u29C9'}</button></div></>;
                const cell=(v,$v,k)=><><span className={`tk ${k}`}>{pfAbbr(v)}</span><span className="us">{fmtDollar($v)}</span></>;
                const bar=r=><div className="bar"><span><b style={{width:(r.t$>0?r.p$/r.t$*100:0)+'%',background:'#F2D35B'}}></b><b style={{width:(r.t$>0?r.u$/r.t$*100:0)+'%',background:'#7CFC00'}}></b></span><small>{all>0?(r.t$/all*100).toFixed(1):'0.0'}%</small></div>;
                const subRow=g=><tr key={'g'+g.sub} className="sub"><td><div className="n">{g.sub}</div></td><td>{cell(S('pT',g.rs),S('p$',g.rs),'p')}</td><td>{cell(S('pc',g.rs),S('c$',g.rs),'p')}</td><td>{cell(S('uT',g.rs),S('u$',g.rs),'u')}</td><td><span className="tot">{fmtDollar(S('t$',g.rs))}</span><div className="bar"><small>{all>0?(S('t$',g.rs)/all*100).toFixed(1):'0.0'}%</small></div></td></tr>;
                return(<div className="pf2-foldb pf2-bd">
                  <div className="pf2-bds"><span>Sort</span>{[['value','Value'],['name','Name'],['added','Added']].map(([k,l])=><button key={k} className={bdSort===k?'on':''} aria-pressed={bdSort===k} onClick={()=>setBdSort(k)}>{l}</button>)}</div>
                  <table className="pf2-bdt"><thead><tr><th>WALLET</th><th><img src={TOKENS.PTGC.logo} alt=""/>PTGC</th><th><img src={TOKENS.PTGC.logo} alt=""/>PENDING TO CLAIM</th><th><img src={TOKENS.UFO.logo} alt=""/>UFO</th><th>TOTAL {'\u00B7'} SHARE</th></tr></thead><tbody>
                    {/* round 30 (his pick B-A of mock-r30-v1): the ledger dressed like the rest of the page — bigger type, zebra, the wallet colour as a left accent, logos in the headers, a gold ALL WALLETS band */}
                    {order.map(r=>r.sub?subRow(r):<tr key={r.a} style={{'--c':r.c}}><td>{who(r)}</td><td>{cell(r.pT,r.p$,'p')}</td><td>{cell(r.pc,r.c$,'p')}</td><td>{cell(r.uT,r.u$,'u')}</td><td><span className="tot">{fmtDollar(r.t$)}</span>{bar(r)}</td></tr>)}
                    {rows.length>1&&<tr className="sum"><td><div className="n">ALL WALLETS</div></td><td>{cell(S('pT'),S('p$'),'p')}</td><td>{cell(S('pc'),S('c$'),'p')}</td><td>{cell(S('uT'),S('u$'),'u')}</td><td><span className="tot">{fmtDollar(all)}</span><div className="bar"><span><b style={{width:(all>0?S('p$')/all*100:0)+'%',background:'#F2D35B'}}></b><b style={{width:(all>0?S('u$')/all*100:0)+'%',background:'#7CFC00'}}></b></span><small>100%</small></div></td></tr>}
                  </tbody></table>
                  <div className="pf2-bdc">{order.map(r=>r.sub?<div key={'g'+r.sub} className="wsum g"><span className="l">{r.sub}</span><b>{fmtDollar(S('t$',r.rs))}</b></div>:<div key={r.a} className="wc"><div className="top"><div className="who">{who(r)}</div><div className="tv">{fmtDollar(r.t$)}<small>{all>0?(r.t$/all*100).toFixed(1):'0.0'}% of portfolio</small></div></div>
                      <div className="sb"><b style={{width:(r.t$>0?r.p$/r.t$*100:0)+'%',background:'#F2D35B'}}></b><b style={{width:(r.t$>0?r.u$/r.t$*100:0)+'%',background:'#7CFC00'}}></b></div>
                      <div className="cols"><div className="cl"><div className="l">PTGC</div>{cell(r.pT,r.p$,'p')}</div><div className="cl"><div className="l">Pending to claim</div>{cell(r.pc,r.c$,'p')}</div><div className="cl"><div className="l">UFO</div>{cell(r.uT,r.u$,'u')}</div></div></div>)}
                    {rows.length>1&&<div className="wsum"><span className="l">ALL WALLETS</span><b>{fmtDollar(all)}</b></div>}</div>
                </div>);})()}
            </section>
          </div>
          </>}
          <div className="pf2-foot">Portfolio data is read directly from the PulseChain blockchain. Not financial advice.<br/>Your portfolio is saved locally in your browser.</div>
        </div>
        {edit&&(()=>{const w=wallets.find(x=>x.address.toLowerCase()===edit);return w?<PfEditWallet w={w} groups={gNames} save={patch=>{p.updateWallet(edit,patch);setEdit(null);}} remove={()=>{removeWallet(w.address);setEdit(null);}} close={()=>setEdit(null)}/>:null;})()}
        {edTok&&<PfEarnedModal tok={edTok} addrs={hAddrs} txs={txs} prices={prices} wallets={counted} hasUfo={uf.balance>0||(ufoEarned||0)>0} close={()=>setEdTok(null)}/>}
        {lgTok&&<PfTierInfoModal token={lgTok} price={lgTok==='PTGC'?(dp.ptgc||prices.ptgc):(dp.ufo||prices.ufo)} close={()=>setLgTok(null)}/>}
        {how&&(
          <PfModal className="pf2-modal" onClose={()=>setHow(false)} label="How it works"><div onClick={e=>e.stopPropagation()}>
            <button className="x" onClick={()=>setHow(false)} aria-label="Close">{'×'}</button>
            <h2>HOW IT WORKS</h2>
            <p><b>Add any wallet</b> by pasting its address. Nothing to connect or sign {'—'} the page only reads public balances from the PulseChain blockchain.</p>
            <p><b>Switch a wallet off</b> to leave it out of the totals without removing it. Groups let you keep wallets together (LP, cold storage, friends) and filter the cards.</p>
            <p><b>PTGC</b> holdings are the wallet's full balance; the PTGC staking contract tells us how much of it is staked or locked, and what rewards are waiting to be claimed. <b>Reflections</b> (PTGC and UFO) are worked out from the chain: what the wallet holds now, plus everything it ever sent, minus everything it ever received.</p>
            <p><b>Lifetime earned</b> is every reward: PTGC staking + locking + reflections (UFO pays reflections only). UFO{'\u2019'}s principal / reflections split of today{'\u2019'}s bag is pro rata to everything ever received and earned. UFO reflections cover UFO{'\u2019'}s whole life, including the time before the Jul 2026 contract migration.</p>
            <p><b>Leagues</b> show your bag in sea creatures {'—'} a whale is 1 % of the supply, a shark 0.1 %, and so on down.</p>
            <p><b>Your list is saved in this browser only.</b> Use <b>Get Code</b> in the header to back it up, and <b>Load Code</b> to restore it on another device.</p>
          </div></PfModal>
        )}
        </div>
      );
    };
