    /* Portfolio v2, round 2 (2026-10-13): the Leagues window = the dashboard's TierInfoModal look (index.html, 2026-10-04
       redesign: his sea + whale + shark header, the lit coin, Starting / Burned / Circulating tiles, eight sea-art rows, Close).
       Ported here because portfolio.html does not load index.html's code; its lg-* CSS is copied in by tools/pf-v2.py
       straight from index.html, so the two stay one design. The burn is read live (balance of 0x…369 + totalSupply), the same
       read as index.html's fetchBurn; a failed read prints "—" and keeps the starting basis (gotcha 20). */
    const PF_BURN_C=[{n:'Poseidon',e:'\u{1F531}',p:10},{n:'Whale',e:'\u{1F40B}',p:1},{n:'Shark',e:'\u{1F988}',p:0.1},{n:'Dolphin',e:'\u{1F42C}',p:0.01},{n:'Squid',e:'\u{1F991}',p:0.001},{n:'Turtle',e:'\u{1F422}',p:0.0001},{n:'Shrimp',e:'\u{1F990}',p:0.00001},{n:'Shell',e:'\u{1F41A}',p:0}];
    const pfTierFraction=c=>c.p>0?Number((c.p/100).toPrecision(15)):0.00000001;   // = index.html tierFraction (SHELL_CARD_PCT)
    const PF_BURN_ADDR='0x0000000000000000000000000000000000000369';
    const PF_TOKEN_ADDR={PTGC:'0x94534EeEe131840b1c0F61847c572228bdfDDE93',UFO:'0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6'};
    const pfFetchBurn=async token=>{try{const to=PF_TOKEN_ADDR[token];const[b,s]=await Promise.all([rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to,data:'0x70a08231000000000000000000000000'+PF_BURN_ADDR.slice(2)},'latest'],id:1}),rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to,data:'0x18160ddd'},'latest'],id:2})]);if(!b||!s||b.result==null||s.result==null)return null;const burned=Number(BigInt(b.result))/1e18,supply=Number(BigInt(s.result))/1e18;return supply>0?{total:burned,supply}:null;}catch(e){return null;}};
    /* = index.html fmtAbbr (a67: the unit is picked AFTER rounding — never "1000.00M"); the classic page keeps its own */
    const pfAbbr=n=>{if(n==null||isNaN(n))return'\u2014';const num=Number(n);if(num>=999.995e9)return(num/1e12).toFixed(2)+'T';if(num>=999.995e6)return(num/1e9).toFixed(2)+'B';if(num>=999.995e3)return(num/1e6).toFixed(2)+'M';if(num>=999.995)return(num/1e3).toFixed(2)+'K';return Math.floor(num).toLocaleString('en-US')};
    const pfFmtInt=n=>n==null||isNaN(n)?'—':Math.floor(Number(n)).toLocaleString('en-US');
    const PfModal=({onClose,label,className='',children})=>{
      const ref=React.useRef(null);const cl=React.useRef(onClose);cl.current=onClose;
      useEffect(()=>{const prev=document.activeElement,ov=document.body.style.overflow;document.body.style.overflow='hidden';
        const key=e=>{if(e.key==='Escape'&&cl.current){e.preventDefault();cl.current();}};document.addEventListener('keydown',key);
        try{ref.current&&ref.current.focus({preventScroll:true});}catch(e){}
        return()=>{document.removeEventListener('keydown',key);document.body.style.overflow=ov;try{prev&&prev.focus&&prev.focus({preventScroll:true});}catch(e){}};},[]);
      return ReactDOM.createPortal(<div ref={ref} tabIndex={-1} role="dialog" aria-modal="true" aria-label={label} className={`fixed inset-0 outline-none ${className}`} onClick={e=>{e.stopPropagation();cl.current&&cl.current();}}>{children}</div>,document.body);
    };
    const PfSupplyToggle=({mode,setMode,color,color2})=>{   // = index.html SupplyBasisToggle (size md)
      const opts=[{k:'start',label:'Starting Supply'},{k:'circ',label:'Circulating Supply'}];const idx=mode==='circ'?1:0;
      return(
        <div role="tablist" aria-label="Supply basis" className="relative inline-grid grid-cols-2 rounded-full p-1 select-none" style={{background:'rgba(255,255,255,0.06)',border:'1px solid rgba(255,255,255,0.14)',boxShadow:'inset 0 1px 0 rgba(255,255,255,0.05), 0 4px 18px rgba(0,0,0,0.35)'}}>
          <div className="absolute top-1 bottom-1 rounded-full transition-transform duration-300 ease-out" style={{left:'4px',width:'calc(50% - 4px)',transform:`translateX(${idx*100}%)`,background:`linear-gradient(180deg, ${color} 0%, ${color2||(color+'cc')} 100%)`,boxShadow:`0 0 14px ${color}66, 0 1px 0 rgba(255,255,255,0.35) inset`}}/>
          {opts.map(o=>{const active=(mode==='circ'?'circ':'start')===o.k;return(
            <button key={o.k} role="tab" aria-selected={active} onClick={()=>setMode(o.k)} className={`relative z-10 rounded-full font-semibold tracking-wider uppercase whitespace-nowrap transition-colors duration-200 px-3.5 py-1.5 text-[11px] sm:text-xs ${active?'text-black':'text-white/55 hover:text-white'}`}>{o.label}</button>);})}
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
