    /* ===== Portfolio v2 — shared bits (loaded FIRST by pf-v2.py) =====
       Everything here is used by the other three files: PF_ADDR / PF_SUPPLY (addresses, supplies), pfAbbr, pfAddr, pfCopy,
       pfLsSet, PfModal (focus-trapping window), the leagues modal. Only module-scope constants and functions live here. */
    /* Portfolio v2, round 2 (2026-10-13): the Leagues window = the dashboard's TierInfoModal look (index.html, 2026-10-04
       redesign: his sea + whale + shark header, the lit coin, Starting / Burned / Circulating tiles, eight sea-art rows, Close).
       Ported here because portfolio.html does not load index.html's code; its lg-* CSS is copied in by tools/pf-v2.py
       straight from index.html, so the two stay one design. The burn is read live (balance of 0x…369 + totalSupply), the same
       read as index.html's fetchBurn; a failed read prints "—" and keeps the starting basis (gotcha 20). */
    const PF_BURN_C=[{n:'Poseidon',e:'\u{1F531}',p:10},{n:'Whale',e:'\u{1F40B}',p:1},{n:'Shark',e:'\u{1F988}',p:0.1},{n:'Dolphin',e:'\u{1F42C}',p:0.01},{n:'Squid',e:'\u{1F991}',p:0.001},{n:'Turtle',e:'\u{1F422}',p:0.0001},{n:'Shrimp',e:'\u{1F990}',p:0.00001},{n:'Shell',e:'\u{1F41A}',p:0}];
    const pfTierFraction=c=>c.p>0?Number((c.p/100).toPrecision(15)):0.00000001;   // = index.html tierFraction (SHELL_CARD_PCT)
    /* round 27 (audit E2): ONE place for the addresses and supplies every v2 file uses (there were four copies) */
    const PF_ADDR={PTGC:'0x94534EeEe131840b1c0F61847c572228bdfDDE93',UFO:'0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6',STAKING:'0xC71f597a2AC39E47F07102E849d18489C96f39EF',BURN:'0x0000000000000000000000000000000000000369'};
    const PF_SUPPLY={PTGC:333333333333,UFO:999999999051};
    /* round 31 (Shaka: "audit this number… tokens that have been burned are not getting rewards… a percentage of circulating supply"):
       the UFO holder reward (the hidden 1 % of every fee-paying transfer) is shared by balance among the holders that are NOT
       excluded from rewards. The contract is unverified and has no isExcludedFromReward getter, so the excluded set was MEASURED
       on 2026-10-15 (tools: design/portfolio/README.md round 31): an address is excluded when its balance moves ONLY by its own
       transfers (+ the hidden 1 % on its fee-paying sends) over 12,000 blocks, while ordinary holders grow ~0.07 %. Excluded:
       the burn address (95.8 B), the token contract, the wallet 0x92DD…574D (71.8 B, an EOA excluded by the owner) and 13 PulseX
       pools (same bytecode). Cross-check: four untouched holders' reflections ÷ their balance × the window's total reflected fee
       all give 735.87 B eligible; supply − these balances gives 734.1 B (the 0.24 % gap = pools under 1 B). The share shown is
       balance ÷ (supply − excluded balances), read live and cached 10 min (localStorage fallback when the RPC is down). */
    const PF_UFO_EXCL={wallets:['0x92DD8E86fDb206fA41E451398A9f03fbd36d574D'],
      pools:['0x9aBD84EAE174c6cf7FBf67cBb550930845866e05','0x145BC3a8a5EC0C84061511a5DB6023360caDF654','0xE221e6fC30e5787F0d551f980B4da1055D832A03','0x1693b411Ca2dF63C15292ad1fCcF8Ff06a643b25','0xF7d75A0BbE1EF90CDA220DEa7450105a956Abf19','0x3fE128f60797E371aAF43c038955bb37356d1e8a','0xe61AA9A9B7a13cEEdEaa8D26BFf5222003A40634','0xc4434600F1f263Ee38c38dfe32c8DEf8c0047C0b','0x6e60E4fA05e1f2a4Ab5706B17b52ddd8EA92372D','0x1a813F71324C02a57e02a0b79460Bb2dD675ae02','0x50771B2B774541937D657144e034D7e2215542AD','0x865bEbb526a61d5aA75A379Ea84fa8d710eA25be','0x9Dc651b1435eAD1cC2dDf8745e9BaB7A3C94f1ca']};
    /* round 34: "read 2 min ago" stamps — a 30 s tick so they stay honest, and the words */
    const usePfTick=(ms=30000)=>{const[t,setT]=useState(Date.now());useEffect(()=>{const i=setInterval(()=>setT(Date.now()),ms);return()=>clearInterval(i);},[ms]);return t;};
    const pfAgo=(at,now)=>{const s=Math.max(0,Math.round(((now||Date.now())-at)/1000));if(s<45)return'just now';const m=Math.round(s/60);if(m<60)return m+' min ago';const h=Math.round(m/60);if(h<24)return h+' h ago';return Math.round(h/24)+' d ago';};
    const pfIn=sec=>{const s=Math.max(0,sec);if(s<3600)return Math.max(1,Math.round(s/60))+' min';if(s<86400)return Math.round(s/3600)+' h';const d=Math.round(s/86400);if(d<60)return d+' d';if(d<365)return Math.round(d/30)+' mo';return (d/365).toFixed(1).replace(/\.0$/,'')+' y';};
    /* round 40 (audit II S1): the fold bars remember open / closed per device — grays_pf_folds {rt,bd,lk,x} */
    const PF_FOLDS_LS='grays_pf_folds';
    const usePfFold=(key,def=false)=>{const[v,setV]=useState(()=>{try{const o=JSON.parse(localStorage.getItem(PF_FOLDS_LS)||'{}');return typeof o[key]==='boolean'?o[key]:def;}catch(e){return def;}});
      const set=React.useCallback(x=>{setV(prev=>{const n=typeof x==='function'?x(prev):x;try{const o=JSON.parse(localStorage.getItem(PF_FOLDS_LS)||'{}');o[key]=n;localStorage.setItem(PF_FOLDS_LS,JSON.stringify(o));}catch(e){}return n;});},[key]);
      return[v,set];};
    const PF_UFO_ELIG_LS='grays_pf_ufo_elig';let pfUfoEligP=null,pfUfoEligMem=null;
    const pfUfoEligible=()=>{
      if(pfUfoEligMem&&Date.now()-pfUfoEligMem.at<10*60e3)return Promise.resolve(pfUfoEligMem);
      if(pfUfoEligP)return pfUfoEligP;
      const addrs=[PF_ADDR.BURN,PF_ADDR.UFO,...PF_UFO_EXCL.wallets,...PF_UFO_EXCL.pools];
      const call=(id,data)=>({jsonrpc:'2.0',id,method:'eth_call',params:[{to:PF_ADDR.UFO,data},'latest']});
      const body=[call(0,'0x18160ddd'),...addrs.map((a,i)=>call(i+1,'0x70a08231'+a.slice(2).toLowerCase().padStart(64,'0')))];
      pfUfoEligP=pfhRpc(body).then(res=>{const by={};res.forEach(r=>{by[r.id]=r&&r.result&&r.result!=='0x'?Number(BigInt(r.result))/1e18:null;});
        const supply=by[0];if(!(supply>0))throw new Error('no supply');let excl=0,burn=0,wallets=0,pools=0;
        addrs.forEach((a,i)=>{const v=by[i+1];if(v==null)throw new Error('no balance');excl+=v;if(i===0)burn=v;else if(i<=1+PF_UFO_EXCL.wallets.length)wallets+=v;else pools+=v;});
        const list=addrs.map((a,i)=>({a,v:by[i+1],k:i===0?'burn':i===1?'contract':i<=1+PF_UFO_EXCL.wallets.length?'wallet':'pool'}));
        const o={supply,elig:supply-excl,burn,wallets,pools,list,at:Date.now()};pfUfoEligMem=o;try{localStorage.setItem(PF_UFO_ELIG_LS,JSON.stringify(o));}catch(e){}return o;})
        .catch(()=>{try{const s=localStorage.getItem(PF_UFO_ELIG_LS);if(s){const o=JSON.parse(s);if(o&&o.elig>0)return o;}}catch(e){}return null;})
        .finally(()=>{pfUfoEligP=null;});
      return pfUfoEligP;};
    const usePfUfoEligible=()=>{const[e,setE]=useState(()=>{try{const s=localStorage.getItem(PF_UFO_ELIG_LS);const o=s?JSON.parse(s):null;return o&&o.elig>0?o:null;}catch(x){return null;}});
      useEffect(()=>{let live=true;pfUfoEligible().then(o=>{if(live&&o)setE(o);});return()=>{live=false;};},[]);return e;};
    const PF_BURN_ADDR=PF_ADDR.BURN;
    const PF_TOKEN_ADDR={PTGC:PF_ADDR.PTGC,UFO:PF_ADDR.UFO};
    const pfFetchBurn=async token=>{try{const to=PF_TOKEN_ADDR[token];const[b,s]=await Promise.all([rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to,data:'0x70a08231000000000000000000000000'+PF_BURN_ADDR.slice(2)},'latest'],id:1}),rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to,data:'0x18160ddd'},'latest'],id:2})]);if(!b||!s||b.result==null||s.result==null)return null;const burned=Number(BigInt(b.result))/1e18,supply=Number(BigInt(s.result))/1e18;return supply>0?{total:burned,supply}:null;}catch(e){return null;}};
    /* = index.html fmtAbbr (a67: the unit is picked AFTER rounding — never "1000.00M"); the classic page keeps its own */
    /* round 26 (audit D9): clipboard writes REJECT (not throw) when they fail on iOS — the ✓ only shows on success */
    /* round 27 (audit E3): one localStorage write with one quota strategy — keep calling `shrink(obj)` (which must drop
       something and return true) until the write fits; give up quietly when nothing is left to drop */
    const pfLsSet=(key,obj,shrink)=>{for(let i=0;i<40;i++){try{localStorage.setItem(key,JSON.stringify(obj));return true;}catch(e){if(!shrink||!shrink(obj))break;}}return false;};
    const pfCopy=text=>{try{if(navigator.clipboard&&navigator.clipboard.writeText)return navigator.clipboard.writeText(text).then(()=>true,()=>false);}catch(e){}
      try{const ta=document.createElement('textarea');ta.value=text;ta.setAttribute('readonly','');ta.style.position='fixed';ta.style.opacity='0';document.body.appendChild(ta);ta.select();const ok=document.execCommand('copy');document.body.removeChild(ta);return Promise.resolve(!!ok);}catch(e){return Promise.resolve(false);}};
    const pfAddr=a=>a?a.slice(0,6)+'\u2026'+a.slice(-4):'';   // round 25 (audit C13): one address style everywhere (the classic page's truncAddr uses three dots)
    const pfAbbr=n=>{if(n==null||isNaN(n))return'\u2014';const num=Number(n);if(num>=999.995e9)return(num/1e12).toFixed(2)+'T';if(num>=999.995e6)return(num/1e9).toFixed(2)+'B';if(num>=999.995e3)return(num/1e6).toFixed(2)+'M';if(num>=999.995)return(num/1e3).toFixed(2)+'K';return Math.floor(num).toLocaleString('en-US')};
    const pfFmtInt=n=>n==null||isNaN(n)?'—':Math.floor(Number(n)).toLocaleString('en-US');
    /* round 26 (audit D1 / D2 / D9): every window traps Tab inside itself, gives focus back to the button that opened it,
       leaves an autoFocus'd field alone, and locks the page behind on iOS too (position:fixed — overflow:hidden isn't enough there) */
    const PF_FOCUSABLE='a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
    const PfModal=({onClose,label,className='',children})=>{
      const ref=React.useRef(null);const cl=React.useRef(onClose);cl.current=onClose;
      const prevRef=React.useRef(typeof document!=='undefined'?document.activeElement:null);   // captured at render, before anything inside autofocuses
      useEffect(()=>{const prev=prevRef.current,b=document.body,saved={ov:b.style.overflow,pos:b.style.position,top:b.style.top,w:b.style.width},y=window.scrollY;
        b.style.overflow='hidden';b.style.position='fixed';b.style.top=(-y)+'px';b.style.width='100%';
        const key=e=>{if(e.key==='Escape'&&cl.current){e.preventDefault();cl.current();return;}
          if(e.key==='Tab'&&ref.current){const f=[...ref.current.querySelectorAll(PF_FOCUSABLE)].filter(x=>x.offsetParent!==null);if(!f.length){e.preventDefault();return;}
            const i=f.indexOf(document.activeElement);if(e.shiftKey&&(i<=0)){e.preventDefault();f[f.length-1].focus();}else if(!e.shiftKey&&(i===-1||i===f.length-1)){e.preventDefault();f[0].focus();}}};
        document.addEventListener('keydown',key);
        try{if(ref.current&&!ref.current.contains(document.activeElement))ref.current.focus({preventScroll:true});}catch(e){}
        return()=>{document.removeEventListener('keydown',key);b.style.overflow=saved.ov;b.style.position=saved.pos;b.style.top=saved.top;b.style.width=saved.w;window.scrollTo(0,y);try{prev&&prev.focus&&prev.focus({preventScroll:true});}catch(e){}};},[]);
      return ReactDOM.createPortal(<div ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={label} className={`fixed inset-0 outline-none ${className}`} onClick={e=>{e.stopPropagation();cl.current&&cl.current();}}>{children}</div>,document.body);
    };
    const PfSupplyToggle=({mode,setMode,color,color2})=>{   // = index.html SupplyBasisToggle (size md)
      const opts=[{k:'start',label:'Starting Supply'},{k:'circ',label:'Circulating Supply'}];const idx=mode==='circ'?1:0;
      return(
        <div role="group" aria-label="Supply basis" className="relative inline-grid grid-cols-2 rounded-full p-1 select-none" style={{background:'rgba(255,255,255,0.06)',border:'1px solid rgba(255,255,255,0.14)',boxShadow:'inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 18px rgba(0,0,0,0.35)'}}>
          <div className="absolute top-1 bottom-1 rounded-full transition-transform duration-300 ease-out" style={{left:'4px',width:'calc(50% - 4px)',transform:`translateX(${idx*100}%)`,background:`linear-gradient(180deg, ${color} 0%, ${color2||(color+'cc')} 100%)`,boxShadow:`0 0 14px ${color}66, 0 1px 0 rgba(255,255,255,0.35) inset`}}/>
          {opts.map(o=>{const active=(mode==='circ'?'circ':'start')===o.k;return(
            <button key={o.k} aria-pressed={active} onClick={()=>setMode(o.k)} className={`relative z-10 rounded-full font-semibold tracking-wider uppercase whitespace-nowrap transition-colors duration-200 px-3.5 py-1.5 text-[11px] sm:text-xs ${active?'text-black':'text-white/55 hover:text-white'}`}>{o.label}</button>);})}
        </div>);
    };
    const PfLgCoin=({token})=>(
      <div className="lg-coin"><div className="halo" aria-hidden="true"></div><img className="corona" src={H2_ASSETS.corona[token]||H2_ASSETS.corona.PTGC} alt="" aria-hidden="true"/><div className="fl" aria-hidden="true"></div><div className="flv" aria-hidden="true"></div><div className="flh" aria-hidden="true"></div><img className="lg" src={TOKENS[token].logo} alt={token}/></div>);
    const PF_LG_ART_V=1;   // = index.html LG_ART_V
    const PfTierInfoModal=({token,price,close})=>{
      const[mode,setMode]=useState('start');
      const[burn,setBurn]=useState(undefined);   // undefined = reading, null = failed
      useEffect(()=>{let live=true;pfFetchBurn(token).then(b=>{if(live)setBurn(b);});return()=>{live=false;};},[token]);
      const now=new Date();const date=`${now.getMonth()+1}-${now.getDate()}-${String(now.getFullYear()).slice(-2)}`;
      const start=PF_SUPPLY[token];
      const burnKnown=!!(burn&&burn.supply>0);
      const burned=burnKnown?burn.total:null;
      const circSupply=burnKnown?Math.max(0,start-burned):null;
      const circ=mode==='circ'&&burnKnown;
      const basis=circ?circSupply:start;
      const tiers=PF_BURN_C.map(c=>({name:c.n,emoji:c.e,threshold:basis*pfTierFraction(c)}));
      const isPTGC=token==='PTGC';
      const usdCell=v=>!v||isNaN(v)?'—':v>=1?'$'+Math.floor(v).toLocaleString('en-US'):'$'+v.toFixed(2);
      return(
        <PfModal className="z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80" onClose={close} label={`${token} leagues`}>
          <div className={`lg-m max-w-[560px] w-full max-h-[92vh] overflow-y-auto overscroll-contain${isPTGC?'':' ufo'}`} onClick={e=>e.stopPropagation()}>
            <div className="lg-hd">
              <div className="sky" aria-hidden="true"></div><img className="whale" src={`logos/leagues/lg-whale.webp?v=${PF_LG_ART_V}`} alt="" aria-hidden="true"/><img className="shark" src={`logos/leagues/lg-shark.webp?v=${PF_LG_ART_V}`} alt="" aria-hidden="true"/>
              <div className="tg"><PfSupplyToggle mode={mode} setMode={m=>setMode(m==='circ'&&!burnKnown?'start':m)} color={isPTGC?'#FFE27A':'#B4FF86'} color2={isPTGC?'#E3B52A':'#5BE632'}/></div>
              <PfLgCoin token={token}/>
              <div className="lg-pl"><div className="d">Price {date}</div><div className="p">{fmtPriceNode(price)}</div></div>
            </div>
            <div className="lg-tiles" role="group" aria-label="Supply basis">
              <button type="button" onClick={()=>setMode('start')} aria-pressed={!circ} className={`lg-t${circ?' dim':' sel'}`}><img src={`logos/leagues/lg-ic-coins.webp?v=${PF_LG_ART_V}`} alt=""/><div className="l">Starting supply</div><div className="v tabular-nums">{pfFmtInt(start)}</div></button>
              <div className="lg-t burn"><img src="logos/panels/vg-flame.webp" alt=""/><div className="l">Burned</div><div className="v tabular-nums">{burn===undefined?'…':burnKnown?pfFmtInt(burned):'—'}</div></div>
              <button type="button" onClick={()=>burnKnown&&setMode('circ')} aria-pressed={circ} disabled={!burnKnown} className={`lg-t circ${circ?' sel':' dim'}`}><img src={`logos/leagues/lg-ic-circ.webp?v=${PF_LG_ART_V}`} alt=""/><div className="l">Circulating supply</div><div className="v tabular-nums">{burnKnown?pfFmtInt(circSupply):burn===undefined?'…':'—'}</div></button>
            </div>
            <div className="lg-tb">
              <div className="lg-cap">Tiers based on {circ?'circulating':'starting'} supply</div>
              <div className="lg-th" aria-hidden="true"><b></b><b>Tier</b><b>Tokens</b><b>Price USD</b></div>
              <div role="table" aria-label={`${token} holder tiers`}>
                {tiers.map((t,i)=>(
                  <div key={i} role="row" className={`lg-r${i===0?' top':''}`}>
                    <span role="cell"><img className="sea-ic" src={pfSea(t.emoji)} alt="" style={{width:46,height:46}}/></span>
                    <span role="cell" className="nm">{t.name}</span>
                    <span role="cell" className="tk">{pfAbbr(t.threshold)}</span>
                    <span role="cell" className="pr">{usdCell(t.threshold*price)}</span>
                  </div>))}
              </div>
            </div>
            <button type="button" onClick={close} className="lg-cl">Close</button>
            <div className="lg-ft" aria-hidden="true"></div>
          </div>
        </PfModal>
      );
    };
