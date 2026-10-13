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
    const PF_SUPPLY={PTGC:333333333333,UFO:UFO_TOTAL_SUPPLY};
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
    const PfRing=({parts,size=132})=>{
      const r=46,c=2*Math.PI*r,tot=parts.reduce((s,p)=>s+(p[0]>0?p[0]:0),0);let off=0;
      return(
        <svg viewBox="0 0 120 120" style={{width:size,height:size}} aria-hidden="true">
          <circle cx="60" cy="60" r={r} fill="none" stroke="rgba(255,255,255,.06)" strokeWidth="22"/>
          {tot>0&&parts.filter(p=>p[0]>0).map(([v,col],i)=>{const L=v/tot*c;const el=<circle key={i} cx="60" cy="60" r={r} fill="none" stroke={col} strokeWidth="22" strokeDasharray={`${L} ${c-L}`} strokeDashoffset={-off} transform="rotate(-90 60 60)" style={{filter:`drop-shadow(0 0 6px ${col}66)`}}/>;off+=L;return el;})}
        </svg>
      );
    };
    const pfPct=(v,t)=>{if(!(t>0)||v==null)return'—';const p=v/t*100;return(p>0&&p<0.1?p.toFixed(2):p.toFixed(1))+'%';};
    const pfChg=c=>c==null||isNaN(c)?<span className="na">{'—'} (24h)</span>:<span className={c>=0?'pos':'neg'}>{c>=0?'+':'−'}{Math.abs(c).toFixed(2)}% (24h)</span>;
    const PfCreatures=({tokens,token})=>{
      const list=tokens>0?getHoldingCreatures(tokens,token):[];
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
      const g=grp==='__new'?newG.trim():grp;
      const ok=!(grp==='__new'&&!g);
      const go=()=>{if(ok)save({name:name.trim(),group:g||'Default'});};
      return(
        <PfModal className="z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80" onClose={close} label="Edit wallet">
          <div className="pf2-ew" onClick={e=>e.stopPropagation()}>
            <button className="x" onClick={close} aria-label="Close">{'\u00D7'}</button>
            <h2>EDIT WALLET</h2>
            <div className="lb">Address</div>
            <div className="adr"><span className="mono">{w.address}</span><button onClick={()=>{try{navigator.clipboard.writeText(w.address);setCopied(true);setTimeout(()=>setCopied(false),1500);}catch(e){}}}>{copied?'Copied':'Copy'}</button></div>
            <label className="lb" htmlFor="pf2-ew-n">Name</label>
            <input id="pf2-ew-n" className="in" value={name} onChange={e=>setName(e.target.value)} placeholder="Give this wallet a name…" autoFocus onKeyDown={e=>e.key==='Enter'&&go()}/>
            <label className="lb" htmlFor="pf2-ew-g">Group</label>
            <select id="pf2-ew-g" className="in" value={grp} onChange={e=>setGrp(e.target.value)}>
              {[...new Set(['Default',...groups,w.group||'Default'])].map(x=><option key={x} value={x}>{x}</option>)}
              <option value="__new">+ New group</option>
            </select>
            {grp==='__new'&&<input className="in" value={newG} onChange={e=>setNewG(e.target.value)} placeholder="New group name…" aria-label="New group name" onKeyDown={e=>e.key==='Enter'&&go()}/>}
            <div className="bt"><button className="rm" onClick={remove}>Remove wallet</button><span style={{flex:1}}></span><button className="q" onClick={close}>Cancel</button><button className="sv" onClick={go} disabled={!ok}>Save</button></div>
          </div>
        </PfModal>
      );
    };
    const PortfolioV2=(p)=>{
      const{wallets,portfolioData,loadingAddrs,agg,dp,prices,changes,groups,isWalletChecked,toggleWallet,selectAllWallets,deselectAllWallets,removeWallet,fetchWalletData,retryFailedReflScans,truncAddr,initialLoad,moonMathActive,setMoonMathActive,customPrices,setCustomPrices,ATH_PRICES}=p;
      const[q,setQ]=useState('');
      const[grp,setGrp]=useState('All');
      const[showAll,setShowAll]=useState(false);
      const[how,setHow]=useState(false);
      const[allLocks,setAllLocks]=useState(false);
      const[bdOpen,setBdOpen]=useState(false);
      const[addMsg,setAddMsg]=useState('');
      const[lgTok,setLgTok]=useState(null);
      const[edit,setEdit]=useState(null);   // round 2 (Shaka: "we need to be able to edit a saved wallet"): the wallet being edited   // round 2: the Leagues window (PfTierInfoModal, the dashboard's look)
      const simulated=moonMathActive&&(customPrices.ptgc!==''||customPrices.ufo!==''||customPrices.pls!=='');
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
      const prev=(v,c)=>v==null?null:c==null||isNaN(c)?null:v/(1+c/100);
      const pPrev=prev(ptgcUSD,changes.ptgc),uPrev=prev(ufoUSD,changes.ufo);
      const tChg=simulated||total==null||(ptgcUSD>0&&pPrev==null)||(ufoUSD>0&&uPrev==null)?null:(()=>{const pr=(pPrev||0)+(uPrev||0);return pr>0?(total-pr)/pr*100:null;})();
      const shown=wallets.filter(w=>(grp==='All'||(w.group||'Default')===grp)&&(!q.trim()||(w.name||'').toLowerCase().includes(q.trim().toLowerCase())||w.address.toLowerCase().includes(q.trim().toLowerCase())));
      const allOn=wallets.length>0&&wallets.every(w=>isWalletChecked(w.address));
      const noneOn=wallets.every(w=>!isWalletChecked(w.address));
      const add=()=>{
        const a=p.inputAddr.trim();
        if(!/^0x[0-9a-fA-F]{40}$/.test(a)){setAddMsg('That is not a wallet address — it should start with 0x and be 42 characters.');return;}
        if(wallets.find(w=>w.address.toLowerCase()===a.toLowerCase())){setAddMsg('That wallet is already in your portfolio.');return;}
        setAddMsg('');p.addWallet();
      };
      const pt=agg.ptgc,uf=agg.ufo;
      const ufoRefl=uf.reflState==='ok'?uf.reflections:null;
      const ufoPrin=ufoRefl==null?null:Math.max(0,uf.balance-ufoRefl);
      const ufoYield=ufoRefl==null||!(ufoPrin>0)?null:ufoRefl/ufoPrin*100;
      const ptgcEarned=pt.claimed+pt.lockClaimed+pt.reflections;
      const fmtLock=t=>{if(!t)return'—';const now=Date.now()/1000;if(t<=now)return'Unlockable';const d=Math.floor((t-now)/86400);if(d>365)return Math.floor(d/365)+'y '+Math.floor((d%365)/30)+'m';if(d>30)return Math.floor(d/30)+'m '+d%30+'d';if(d>0)return d+'d';const h=Math.floor((t-now)/3600);return h>0?h+'h':Math.max(1,Math.floor((t-now)/60))+'m';};
      const reflBox=()=>uf.reflState==='pending'?<><div className="v" style={{fontSize:16,color:'rgba(255,255,255,.5)'}}>scanning{'…'}</div><div className="s">{uf.reflPending} wallet{uf.reflPending>1?'s':''}</div></>
        :uf.reflState==='failed'?<><div className="v" style={{fontSize:16,color:'#FFD38A'}}>unavailable</div><div className="s"><button onClick={retryFailedReflScans}>Retry</button></div></>
        :<><div className="v">{pfAbbr(ufoRefl)}</div><div className="s">{fmtDollar(usd(ufoRefl,dp.ufo))}</div></>;
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
          <div className="pf2-tools">
            <b>MY WALLETS <span>({wallets.length})</span></b>
            {wallets.length>0&&<span className="sum">{'·'} <strong>{counted.length}</strong> counted {'·'} <strong>{fmtDollar(total)}</strong></span>}
            {wallets.length>0&&<><button className="pf2-lnk" onClick={selectAllWallets} disabled={allOn}>Select all</button><button className="pf2-lnk q" onClick={deselectAllWallets} disabled={noneOn}>Clear</button></>}
            <span className="sp"></span>
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
              const{a,st,v,pv}=wv(w);const on=isWalletChecked(w.address);const label=w.name||truncAddr(w.address);
              const ps=v>0?(pv||0)/v:null;
              return(
                <div key={a} className={`pf2-wc ${on?'on':'off'}${st==='bad'?' bad':''}`}>
                  <div className="r1"><button className="pf2-tg" role="switch" aria-checked={on} aria-label={`Count ${label} in the totals`} onClick={()=>toggleWallet(w.address)}></button><span className={w.name?'nm':'nm mono'} style={w.name?null:{fontSize:14}} title={w.address}>{label}</span><button className="pf2-ed" onClick={()=>setEdit(w.address.toLowerCase())} aria-label={`Edit ${label}`} title="Edit name / group">✎</button><span className={`pf2-dot ${st==='ok'?'':st}`} title={st==='ok'?'Loaded':st==='run'?'Loading…':st==='bad'?'The chain read failed':''}></span></div>
                  <div className="ad mono">{w.name?<>{truncAddr(w.address)} {'·'} {w.group||'Default'}</>:<>{(w.group||'Default').toUpperCase()}</>}</div>
                  {st==='bad'?<button className="retry" onClick={()=>fetchWalletData(w.address)}>Read failed {'·'} retry</button>
                  :v==null?<div className="v dim">{st==='run'?'loading…':'—'}</div>
                  :<>
                    <div className="v">{fmtDollar(v)}</div>
                    <div className="pf2-split" aria-hidden="true">{ps!=null&&<><i className="p" style={{width:ps*100+'%'}}></i><i className="u" style={{width:(1-ps)*100+'%'}}></i></>}</div>
                    <div className="r3"><span className="p">PTGC {ps==null?'—':Math.round(ps*100)+'%'}</span><span className="u">UFO {ps==null?'—':Math.round((1-ps)*100)+'%'}</span></div>
                  </>}
                  <div className="acts"><button onClick={()=>removeWallet(w.address)} aria-label={`Remove ${label}`} title="Remove this wallet">✕</button></div>
                </div>
              );
            })}
            {!showAll&&shown.length>6&&<button className="pf2-more" onClick={()=>setShowAll(true)}>Show all {shown.length} wallets {'▾'}</button>}
          </div>
          {simulated&&<div className="pf2-mm">{'\u{1F319}'} Moon Math is on {'—'} every dollar figure below uses your prices.</div>}

          {wallets.length>0&&!anyData&&(()=>{const run=wallets.some(w=>loadingAddrs[w.address.toLowerCase()]);const bad=wallets.filter(w=>{const d=portfolioData[w.address.toLowerCase()];return d&&d.error;});return(
            <section className="pf2-pn pf2-sec" style={{marginTop:20}}><div className="pf2-soon" role="status">{run||!bad.length?<><b>Reading your wallets from the chain{'\u2026'}</b></>:<><b>Couldn{'\u2019'}t read your wallets from the chain right now.</b> The PulseChain node did not answer {'\u2014'} nothing is wrong with your list.<div style={{marginTop:12}}><button className="pf2-lnk" onClick={()=>bad.forEach(w=>fetchWalletData(w.address))}>Retry all</button></div></>}</div></section>);})()}
          {wallets.length>0&&anyData&&<>
          {/* ---- three summary tiles ---- */}
          <div className="pf2-row3">
            <section className="pf2-pn pf2-st t"><div className="ic w"><img src="logos/portfolio/pf-wallet.webp" alt=""/></div>
              <div className="tx"><div className="lb">Total portfolio value</div><div className="v">{fmtDollar(total)}</div><div className="s">{simulated?<span className="na">Moon Math prices</span>:pfChg(tChg)}</div></div></section>
            <section className="pf2-pn pf2-st p"><div className="ic"><img src={TOKENS.PTGC.logo} alt=""/></div>
              <div className="tx"><div className="lb">PTGC value</div><div className="v">{fmtDollar(ptgcUSD)}</div><div className="s" style={{color:'#F2D35B'}}>{pfPct(ptgcUSD,total)}</div></div></section>
            <section className="pf2-pn pf2-st u"><div className="ic"><img src={TOKENS.UFO.logo} alt=""/></div>
              <div className="tx"><div className="lb">UFO value</div><div className="v">{fmtDollar(ufoUSD)}</div><div className="s" style={{color:'#8DFF3A'}}>{pfPct(ufoUSD,total)}</div></div></section>
          </div>

          {/* ---- the two token cards ---- */}
          <div className="pf2-tok2">
            <section className="pf2-tk p">
              <div className="pf2-tkh"><img className="lg" src={TOKENS.PTGC.logo} alt=""/>
                <div className="nm"><div className="t">PTGC</div><div className="sb">The Grays Currency</div><PfCreatures tokens={pt.totalHolding} token="PTGC"/></div>
                <div className="px"><div className="a">{fmtPriceNode(prices.ptgc)}</div><div className="c">{pfChg(changes.ptgc)}</div></div></div>
              <div className="pf2-t4 t5">
                <div className="pf2-bx gold"><div className="lb">Total holdings</div><div className="v">{pfAbbr(pt.totalHolding)}</div><div className="s">{fmtDollar(usd(pt.totalHolding,dp.ptgc))}</div></div>
                <div className="pf2-bx blu"><div className="lb">Liquid</div><div className="v">{pfAbbr(pt.walletFree)}</div><div className="s">{fmtDollar(usd(pt.walletFree,dp.ptgc))}</div></div>
                <div className="pf2-bx pur"><div className="lb">Staked</div><div className="v">{pfAbbr(pt.staked)}</div><div className="s">{fmtDollar(usd(pt.staked,dp.ptgc))}</div></div>
                <div className="pf2-bx pnk"><div className="lb">Locked &amp; staked</div><div className="v">{pfAbbr(pt.locked)}</div><div className="s">{fmtDollar(usd(pt.locked,dp.ptgc))}</div></div>
                <div className="pf2-bx rf"><div className="lb">Reflections</div><div className="v">{pfAbbr(pt.reflections)}</div><div className="s">{fmtDollar(usd(pt.reflections,dp.ptgc))}</div></div>
              </div>
              {pt.totalHolding>0?(()=>{const parts=[['Staked (not locked)',pt.stakedOnly,'#B26BFF'],['Locked & staked',pt.locked,'#EC4899'],['Liquid',pt.walletFree,'#F2D35B']].filter(x=>x[1]>0);return(
                <div className="pf2-dn"><PfRing parts={parts.map(x=>[x[1],x[2]])}/>
                  <div className="pf2-lgd">{parts.map(x=><div key={x[0]}><i style={{background:x[2]}}></i>{x[0]}<b>{pfAbbr(x[1])}</b><em>{pfPct(x[1],pt.totalHolding)}</em></div>)}</div></div>);})()
              :<div className="pf2-wait">No PTGC in the counted wallets</div>}
              <div className="pf2-lgw"><PfLeague balance={pt.totalHolding} token="PTGC" price={dp.ptgc} onTiers={()=>setLgTok('PTGC')}/></div>
              <div className="pf2-le"><span className="lb">Total lifetime earned</span><span className="n">{fmtComma(Math.floor(ptgcEarned),2)}</span><span className="k">PTGC</span><span className="d"></span><span className="usd">{fmtDollar(usd(ptgcEarned,dp.ptgc))}</span></div>
              <div className="pf2-extw"><div className="pf2-ext">
                <span>Earned: staking <b>{pfAbbr(pt.claimed)}</b> {'\u00B7'} locking <b>{pfAbbr(pt.lockClaimed)}</b> {'\u00B7'} reflections <b>{pfAbbr(pt.reflections)}</b></span>
              </div></div>
            </section>

            <section className="pf2-tk u">
              <div className="pf2-tkh"><img className="lg" src={TOKENS.UFO.logo} alt=""/>
                <div className="nm"><div className="t">UFO</div><div className="sb">UFO Token</div><PfCreatures tokens={uf.balance} token="UFO"/></div>
                <div className="px"><div className="a">{fmtPriceNode(prices.ufo)}</div><div className="c">{pfChg(changes.ufo)}</div></div></div>
              <div className="pf2-t4">
                <div className="pf2-bx grn"><div className="lb">Total holdings</div><div className="v">{pfAbbr(uf.balance)}</div><div className="s">{fmtDollar(usd(uf.balance,dp.ufo))}</div></div>
                <div className="pf2-bx"><div className="lb">Principal</div><div className="v">{ufoPrin==null?'—':pfAbbr(ufoPrin)}</div><div className="s">{ufoPrin==null?'after the scan':fmtDollar(usd(ufoPrin,dp.ufo))}</div></div>
                <div className="pf2-bx grn"><div className="lb">Reflections</div>{reflBox()}</div>
                <div className="pf2-bx grn"><div className="lb">Reflection yield</div><div className="v">{ufoYield==null?'—':(ufoYield>0&&ufoYield<0.01?'<0.01':ufoYield.toFixed(ufoYield<1?3:2))+(ufoYield==null?'':'%')}</div><div className="s">of principal</div></div>
              </div>
              {uf.balance>0&&ufoRefl!=null?(
                <div className="pf2-dn"><PfRing parts={[[ufoPrin,'#7CFC00'],[ufoRefl,'#22D3EE']]}/>
                  <div className="pf2-lgd"><div><i style={{background:'#7CFC00'}}></i>Principal<b>{pfAbbr(ufoPrin)}</b><em>{pfPct(ufoPrin,uf.balance)}</em></div><div><i style={{background:'#22D3EE'}}></i>Reflections<b>{pfAbbr(ufoRefl)}</b><em>{pfPct(ufoRefl,uf.balance)}</em></div></div></div>
              ):<div className="pf2-wait">{!(uf.balance>0)?'No UFO in the counted wallets':uf.reflState==='failed'?'Reflections unavailable — the chain read failed':'Reading the reflections from the chain…'}</div>}
              <div className="pf2-lgw"><PfLeague balance={uf.balance} token="UFO" price={dp.ufo} onTiers={()=>setLgTok('UFO')}/></div>
              <div className="pf2-le"><span className="lb">Total lifetime earned</span>{ufoRefl==null?<span className="msg">{uf.reflState==='failed'?'unavailable':'scanning…'}</span>:<><span className="n">{fmtComma(Math.floor(ufoRefl),2)}</span><span className="k">UFO</span><span className="d"></span><span className="usd">{fmtDollar(usd(ufoRefl,dp.ufo))}</span></>}</div>
              <div className="pf2-extw"><div className="pf2-ext"><span>Share of supply <b>{uf.balance>0?((s=>s>0&&s<0.01?'<0.01':s.toFixed(s<1?3:2))(uf.balance/UFO_TOTAL_SUPPLY*100))+'%':'—'}</b></span></div></div>
            </section>
          </div>

          {/* ---- round 3 (Shaka: "we lost the Claimable Rewards Breakdown … missing the locked and staked … and the details for
               locks"): PTGC rewards + every lock, open on the page, under the two cards ---- */}
          {(pt.staked>0||pt.totalPending>0||pt.locks.length>0)&&(()=>{
            const now=Date.now()/1000;
            const locks=[];counted.forEach(w=>{const d=portfolioData[w.address.toLowerCase()];if(d&&!d.error)d.ptgc.locks.forEach(l=>locks.push({...l,who:w.name||truncAddr(w.address)}));});
            locks.sort((a,b)=>a.endTime-b.endTime);
            const shownL=allLocks?locks:locks.slice(0,6);
            const fmtD=t=>{try{return new Date(t*1000).toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric'});}catch(e){return'';}};
            const ready=locks.filter(l=>l.endTime<=now).length;
            return(
            <section className="pf2-pn pf2-rl">
              <div className="pf2-sech"><h2 className="oh"><img src={TOKENS.PTGC.logo} alt=""/>PTGC REWARDS &amp; LOCKS</h2><a href="https://goptgc.com" target="_blank" rel="noopener noreferrer" className="pf2-rlv">Verify on goptgc.com before unlocking {'\u2197'}</a></div>
              <div className="pf2-rlg">
                <div className="pf2-rlc">
                  <div className="lb">Claimable rewards</div>
                  <div className="row"><span><i style={{background:'#B26BFF'}}></i>Staking rewards</span><b style={{color:'#C38BFF'}}>{pfAbbr(pt.pendingStake)}</b><em>{fmtDollar(usd(pt.pendingStake,dp.ptgc))}</em></div>
                  <div className="row"><span><i style={{background:'#EC4899'}}></i>Lock rewards</span><b style={{color:'#F472B6'}}>{pfAbbr(pt.pendingLocks)}</b><em>{fmtDollar(usd(pt.pendingLocks,dp.ptgc))}</em></div>
                  <div className="row tot"><span>Total claimable</span><b className="pos">{pfAbbr(pt.totalPending)}</b><em className="pos">{fmtDollar(usd(pt.totalPending,dp.ptgc))}</em></div>
                  <div className="lb" style={{marginTop:16}}>Staking</div>
                  <div className="row"><span><i style={{background:'#B26BFF'}}></i>Staked (not locked)</span><b>{pfAbbr(pt.stakedOnly)}</b><em>{fmtDollar(usd(pt.stakedOnly,dp.ptgc))}</em></div>
                  <div className="row"><span><i style={{background:'#EC4899'}}></i>Locked &amp; staked</span><b>{pfAbbr(pt.locked)}</b><em>{fmtDollar(usd(pt.locked,dp.ptgc))}</em></div>
                  <div className="row tot"><span>Total staked</span><b>{pfAbbr(pt.staked)}</b><em>{fmtDollar(usd(pt.staked,dp.ptgc))}</em></div>
                </div>
                <div className="pf2-rll">
                  <div className="lb">Lock positions <span>({locks.length}{ready?` \u00B7 ${ready} unlockable`:''})</span></div>
                  {locks.length===0?<div className="pf2-wait" style={{padding:'18px 4px'}}>No locks in the counted wallets</div>:shownL.map((l,i)=>{
                    const done=l.endTime<=now;const span=l.endTime-l.startTime;const pc=done?100:span>0?Math.max(0,Math.min(100,(now-l.startTime)/span*100)):0;
                    return(
                      <div key={i} className={`pf2-lk${done?' done':''}`}>
                        <div className="a"><b>{pfAbbr(l.amount)} PTGC</b><span>{fmtDollar(usd(l.amount,dp.ptgc))}</span>{counted.length>1&&<small>{l.who}</small>}</div>
                        <div className="t"><b>{done?'Unlockable':fmtLock(l.endTime)}</b><span>{done?'since ':'unlocks '}{fmtD(l.endTime)}</span><div className="pg" aria-hidden="true"><i style={{width:pc+'%'}}></i></div></div>
                        <div className="r"><b>+{pfAbbr(l.pending)}</b><span>pending</span></div>
                      </div>);
                  })}
                  {locks.length>6&&<button className="pf2-lnk q" style={{marginTop:10}} onClick={()=>setAllLocks(!allLocks)}>{allLocks?'Show fewer':`Show all ${locks.length} locks`}</button>}
                </div>
              </div>
            </section>);
          })()}

          {/* ---- step 2: value history (real chain balances) + recent transactions ---- */}
          <section className="pf2-pn pf2-sec">
            <div className="pf2-sech"><h2 className="oh">PORTFOLIO VALUE HISTORY</h2></div>
            <div className="pf2-soon"><b>Coming next.</b> Your real balances, read from the chain day by day {'—'} sells show as drops, buys as rises.</div>
          </section>
          <section className="pf2-pn pf2-sec">
            <div className="pf2-sech"><h2 className="oh">RECENT TRANSACTIONS <span>(ALL WALLETS)</span></h2></div>
            <div className="pf2-soon"><b>Coming next.</b> Receives, sends, swaps, stakes and claims across your wallets.</div>
          </section>

          {/* ---- the two folds ---- */}
          <div className="pf2-folds">
            <section className="pf2-pn pf2-fold">
              <button className="pf2-foldh" aria-expanded={bdOpen} onClick={()=>setBdOpen(!bdOpen)}><b className="oh">PER-WALLET BREAKDOWN</b><span>{counted.length} wallet{counted.length===1?'':'s'}</span><span className="chev">{'▾'}</span></button>
              {bdOpen&&<div className="pf2-foldb" style={{overflowX:'auto'}}>
                <table className="pf2-tbl"><thead><tr><th>WALLET</th><th>PTGC</th><th>PENDING</th><th>UFO</th><th>REFLECTIONS</th></tr></thead><tbody>
                  {counted.map(w=>{const a=w.address.toLowerCase(),d=portfolioData[a];if(!d||d.error)return null;const r=d.ufo.reflections;return(
                    <tr key={a}><td>{w.name||truncAddr(w.address)}</td><td className="p">{pfAbbr(d.ptgc.totalHolding)}</td><td className="pos">{pfAbbr(d.ptgc.totalPending)}</td><td className="u">{pfAbbr(d.ufo.balance)}</td><td className="u">{r===undefined?(p.scanningAddr===a?'scanning…':'queued'):r===null?<span style={{color:'#FFD38A'}}>unavailable</span>:pfAbbr(r)}</td></tr>);})}
                </tbody></table></div>}
            </section>
            <section className="pf2-pn pf2-fold">
              <button className="pf2-foldh" aria-expanded={moonMathActive} onClick={()=>setMoonMathActive(!moonMathActive)}><b className="oh mmt">MOON MATH</b><span className={`off${moonMathActive?' on':''}`}>{moonMathActive?'ON':'OFF'}</span><span>try your own prices</span><span className="chev">{'▾'}</span></button>
              {moonMathActive&&<div className="pf2-foldb">
                <div className="pf2-mmg">
                  <div><label style={{color:'#F2D35B'}}>PTGC PRICE</label><input type="number" step="any" value={customPrices.ptgc} onChange={e=>setCustomPrices(c=>({...c,ptgc:e.target.value}))} placeholder={prices.ptgc?prices.ptgc.toFixed(8):'0.00'}/></div>
                  <div><label style={{color:'#8DFF3A'}}>UFO PRICE</label><input type="number" step="any" value={customPrices.ufo} onChange={e=>setCustomPrices(c=>({...c,ufo:e.target.value}))} placeholder={prices.ufo?prices.ufo.toFixed(9):'0.00'}/></div>
                  <div><label style={{color:'#8FB8FF'}}>PLS PRICE</label><input type="number" step="any" value={customPrices.pls} onChange={e=>setCustomPrices(c=>({...c,pls:e.target.value}))} placeholder={prices.pls?prices.pls.toFixed(8):'0.00'}/></div>
                </div>
                <div className="pf2-mmb"><button onClick={()=>setCustomPrices({ptgc:String(ATH_PRICES.ptgc),ufo:String(ATH_PRICES.ufo),pls:String(ATH_PRICES.pls)})}>{'\u{1F680}'} All-time highs</button><button className="q" onClick={()=>setCustomPrices({ptgc:'',ufo:'',pls:''})}>Reset to live</button></div>
              </div>}
            </section>
          </div>
          </>}
          <div className="pf2-foot">Portfolio data is read directly from the PulseChain blockchain. Not financial advice.<br/>Your portfolio is saved locally in your browser.</div>
        </div>
        {edit&&(()=>{const w=wallets.find(x=>x.address.toLowerCase()===edit);return w?<PfEditWallet w={w} groups={gNames} save={patch=>{p.updateWallet(edit,patch);setEdit(null);}} remove={()=>{removeWallet(w.address);setEdit(null);}} close={()=>setEdit(null)}/>:null;})()}
        {lgTok&&<PfTierInfoModal token={lgTok} price={lgTok==='PTGC'?(dp.ptgc||prices.ptgc):(dp.ufo||prices.ufo)} close={()=>setLgTok(null)}/>}
        {how&&(
          <div className="pf2-modal" onClick={()=>setHow(false)} role="dialog" aria-modal="true" aria-label="How it works"><div onClick={e=>e.stopPropagation()}>
            <button className="x" onClick={()=>setHow(false)} aria-label="Close">{'×'}</button>
            <h2>HOW IT WORKS</h2>
            <p><b>Add any wallet</b> by pasting its address. Nothing to connect or sign {'—'} the page only reads public balances from the PulseChain blockchain.</p>
            <p><b>Switch a wallet off</b> to leave it out of the totals without removing it. Groups let you keep wallets together (LP, cold storage, friends) and filter the cards.</p>
            <p><b>PTGC</b> holdings are the wallet's full balance; the PTGC staking contract tells us how much of it is staked or locked, and what rewards are waiting to be claimed. <b>Reflections</b> (PTGC and UFO) are worked out from the chain: what the wallet holds now, plus everything it ever sent, minus everything it ever received.</p>
            <p><b>Leagues</b> show your bag in sea creatures {'—'} a whale is 1 % of the supply, a shark 0.1 %, and so on down.</p>
            <p><b>Your list is saved in this browser only.</b> Use <b>Get Code</b> in the header to back it up, and <b>Load Code</b> to restore it on another device.</p>
          </div></div>
        )}
        </div>
      );
    };
