/* h2-header.jsx — the v2 site header for the pages beside index.html (2026-10-03, go-live prep).
   calculators.html and portfolio.html load it as <script type="text/babel" src="h2-header.jsx"> right
   BEFORE their own text/babel block (Babel runs the two in order; top-level consts here are visible to
   the page's block). charts.html is plain JS and carries a static copy of the same markup. Styles are
   h2.css, shared with index.html.
   index.html keeps its own DashHeaderV2 (it needs InfoTips, the KPI sparklines, the Live Feed deck):
   H2Coin / H2Btns / the tab band here MIRROR the ones there — when the look changes, change both.
   Nothing here renders unless the page's HEADER_DESIGN is 'v2' or this device holds the preview flag
   (h2PreviewOn, the same localStorage flag index.html's HeaderPreviewGate sets). */
const h2PreviewOn=()=>{try{return JSON.parse(localStorage.getItem('grays_hdr_preview_v1'))===1;}catch(e){return false;}};
/* --u is one reference pixel (gotcha 36): desktop = width/2166 (floor .47), phone = width/390 (.9–1.3). */
const h2Scale=(w)=>({hsd:Math.max(.47,Math.min(1,w/2166)),hsp:Math.max(.9,Math.min(1.3,w/390))});
const h2DocW=()=>(document.documentElement&&document.documentElement.clientWidth)||window.innerWidth||1440;
const useH2Scale=()=>{
  const[sc,setSc]=React.useState(()=>h2Scale(h2DocW()));
  React.useLayoutEffect(()=>{
    const m=()=>setSc(s=>{const n=h2Scale(h2DocW());return(n.hsd===s.hsd&&n.hsp===s.hsp)?s:n;});
    m();window.addEventListener('resize',m);
    return()=>window.removeEventListener('resize',m);
  },[]);
  return sc;
};
const H2_ASSETS={band:'logos/header/dash-bg.jpg',head:'logos/header/alien-head.webp',corona:{PTGC:'logos/header/coin-corona.webp',UFO:'logos/header/coin-corona-green.webp'}};
/* uid: the phone banner's copy needs its own gradient ids — a gradient defined inside the hidden desktop SVG does not paint */
const H2Tri=({down=false,uid=''})=>(<svg viewBox="0 0 30 26" aria-hidden="true"><defs><linearGradient id={'h2ua'+uid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#6BF7A8"/><stop offset="1" stopColor="#00C865"/></linearGradient><linearGradient id={'h2da'+uid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#FF8AA6"/><stop offset="1" stopColor="#E0284F"/></linearGradient></defs><path d="M15 1 L29 25 L1 25 Z" fill={down?`url(#h2da${uid})`:`url(#h2ua${uid})`}/></svg>);
const H2Cal=()=>(<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true" style={{color:'var(--a)'}}><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>);
const H2Copy=()=>(<svg width="1em" height="1em" viewBox="0 0 24 26" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><rect x="5" y="5" width="14" height="18" rx="2"/><path d="M9 3h6v4H9z" fill="currentColor"/><path d="M8 12h8M8 16h8"/></svg>);
const H2Sk=({w,h,className=''})=><span className={'inline-block rounded bg-white/10 animate-pulse '+className} style={{width:w,height:h}}></span>;
const H2Coin=({token,logo})=>(
  <div className="h2-coin">
    <div className="h2-halo" aria-hidden="true"></div>
    <img className="h2-corona" src={H2_ASSETS.corona[token]||H2_ASSETS.corona.PTGC} alt="" aria-hidden="true"/>
    <div className="h2-flare" aria-hidden="true"></div><div className="h2-flare-v" aria-hidden="true"></div><div className="h2-flare-h" aria-hidden="true"></div>
    <img className="h2-logo" src={logo} alt={token}/>
  </div>);
/* BUY / SELL here sends the visitor to the dashboard with the switch.win window already open
   (index.html?token=X&open=swap) — the widget lives only in index.html. */
const H2Btns=({token,logo,otherLogo,onBuy,onSwitch})=>{
  const other=token==='PTGC'?'UFO':'PTGC';
  return(<>
    <button type="button" onClick={onBuy} aria-label={`Buy or sell ${token}`} className="h2-buy">
      <img src={logo} alt=""/>
      <span className="orb h2-bt"><span>BUY</span><span className="h2-hr" aria-hidden="true"></span><span>SELL</span></span>
    </button>
    <button type="button" onClick={()=>onSwitch(other)} aria-label={`Switch to ${other}`} className="h2-sw">
      <img src={otherLogo} alt=""/>
      <span className="orb">SWITCH</span>
    </button>
  </>);
};
const H2Stat=({label,value,loading,skW})=>(
  <div className="h2-stat">
    <div className="h2-statl">{label}</div>
    {loading?<div className="h2-statv"><H2Sk w={skW} h="1em" className="opacity-60"/></div>:<div className="h2-tref2 tn h2-statv h2-sh">{value}</div>}
  </div>);
/* The tabs, in the dashboard's order. Live Feed opens the deck on the dashboard (open=feed). */
const H2_PAGES=[['dashboard','Dashboard'],['kpi','KPI Report'],['social','Socials'],['calculators','Calculators'],['charts','Charts'],['feed','Live Feed','NEW'],['portfolio','Portfolio'],['affiliates','Affiliates']];
/* The sticky tab row: a black wrapper around the gold band (h2.css .h2-tabs). `mini` = the token · price
   line, shown when `miniOn` (the dashboard shows it once its banner has scrolled away; same here). */
const H2TabBand=({token,vars,active,navTo,mini,miniOn})=>(
  <div className="h2 h2-tabs" data-tok={token} style={vars}>
    {miniOn&&mini&&<div className="lg:hidden">{mini('h2-phone-mini')}</div>}
    <div className="h2-tabband">
      <nav aria-label="Site sections" className="h2-tabrow">
        {miniOn&&mini&&<div className="hidden lg:flex">{mini('h2-mini')}</div>}
        {H2_PAGES.map(([key,label,badge])=>(
          <button type="button" key={key} aria-current={active===key?'page':undefined} onClick={active===key?undefined:()=>navTo(key)} className={'h2-tab'+(key==='portfolio'?' h2-pf':key==='affiliates'?' h2-aff':'')}>
            {key==='portfolio'?<span>{label}</span>:label}{badge&&<span className="h2-new">{badge}</span>}
          </button>))}
      </nav>
    </div>
  </div>);
/* The one-token page header (calculators.html, charts.html's twin): the dashboard's banner — coin,
   name, address, Day pill, price + 24h change, the three stats, BUY / SELL + SWITCH — then the band.
   Every figure is the page's own (same variables the classic header prints); `renderPrice(p,cls)` is
   the page's Price component so sub-micro prices keep their notation. */
const SiteHeaderV2=(p)=>{
  const{token,logo,otherLogo,address,data,loading,hdrDaysOld,copied,copyAddress,plsRatio,xToATH,xToPenny,fmtX,renderPrice,onBack,onSwitch,onBuy,navTo,active}=p;
  const sc=useH2Scale();
  const[scrolled,setScrolled]=React.useState(false);
  const artRef=React.useRef(null),artRef2=React.useRef(null);
  React.useEffect(()=>{
    const on=()=>{const a=artRef.current,b=artRef2.current;const h=(a&&a.offsetHeight)||(b&&b.offsetHeight)||300;setScrolled(window.scrollY>h-40);};
    on();window.addEventListener('scroll',on,{passive:true});
    return()=>window.removeEventListener('scroll',on);
  },[]);
  const changeKnown=data?.change!=null&&!isNaN(data.change);
  const priceUp=changeKnown&&data.change>=0;
  const chgCls=changeKnown?(priceUp?'up':'dn'):'na';
  const chgTxt=changeKnown?`${priceUp?'+':'−'}${Math.abs(data.change).toFixed(2)}%`:'—';
  const addr=`${address.slice(0,6)}...${address.slice(-4)}`;
  const dayPill=hdrDaysOld!=null
    ?<span className="h2-daypill"><H2Cal/><span className="h2-dayl">DAY</span><span className="orb h2-tref2 h2-dayn tn">{hdrDaysOld.toLocaleString()}</span></span>
    :(loading?<H2Sk w="calc(205*var(--u))" h="calc(45*var(--u))" className="rounded-full opacity-60"/>:null);
  const addrRow=(
    <div className="h2-addr tn">{addr}<button type="button" onClick={copyAddress} aria-label={copied?'Copied':'Copy contract address'} className="-my-2 -mx-1" style={{fontSize:'.85em'}}>{copied?'✓':<H2Copy/>}</button></div>);
  const stats=(<>
    <H2Stat label="PLS Ratio" value={plsRatio} loading={loading} skW="3em"/>
    <H2Stat label="X's to ATH" value={fmtX(xToATH)} loading={loading} skW="3em"/>
    <H2Stat label="X's to a Penny" value={fmtX(xToPenny)} loading={loading} skW="3em"/>
  </>);
  const priceBlock=(cls)=>(loading?<H2Sk w="70%" h="1em" className={cls+' mx-auto opacity-60'}/>:renderPrice(data?.price,`h2-tprice tn h2-sh ${cls}`));
  const chgRow=(inline)=>(
    <div className={`h2-chg tn ${chgCls}`}>{loading?<H2Sk w="4em" h=".9em" className="opacity-60"/>:<>{changeKnown&&<H2Tri down={!priceUp} uid={inline?'p':''}/>}{chgTxt}{inline&&<span className="h2-chgl">24h</span>}</>}</div>);
  const mini=(cls)=>(
    <div className={cls}>
      <img src={logo} alt=""/><span className="h2-mname h2-tref">{token}</span>
      <span className="h2-mright">{loading?<H2Sk w={72} h={14}/>:<>{renderPrice(data?.price,'h2-mprice h2-tprice tn')}<span className={`h2-mchg tn ${chgCls}`}>{chgTxt}</span></>}</span>
    </div>);
  const vars={'--hsd':sc.hsd,'--hsp':sc.hsp};
  const btns=<H2Btns token={token} logo={logo} otherLogo={otherLogo} onBuy={onBuy} onSwitch={onSwitch}/>;
  return(<>
    <div className="h2" data-tok={token} style={vars}>
      {/* ---- desktop banner ---- */}
      <div className="h2-desk hidden lg:block" ref={artRef}>
        <div className="h2-art" aria-hidden="true">
          <img className="h2-band" src={H2_ASSETS.band} alt=""/>
          <img className="h2-band2" src={H2_ASSETS.band} alt=""/>
          <img className="h2-head" src={H2_ASSETS.head} alt=""/>
          <div className="h2-shade"></div><div className="h2-shade-r"></div><div className="h2-fade"></div>
        </div>
        <button type="button" onClick={onBack} aria-label="Back to the dashboard" className="h2-back">{'←'}</button>
        <div className="h2-row">
          <H2Coin token={token} logo={logo}/>
          <div className="h2-id">
            <div className="orb h2-tref h2-name">{token}</div>
            {addrRow}
            <div className="h2-day">{dayPill}</div>
          </div>
          <div className="h2-vl" aria-hidden="true"></div>
          <div className="h2-price">
            {priceBlock('h2-pricev')}
            {chgRow(false)}
            <div className="h2-chgl">24h change</div>
          </div>
          <div className="h2-vl" aria-hidden="true"></div>
          <div className="h2-stats">{stats}</div>
          <div className="h2-btns">{btns}</div>
        </div>
      </div>
      {/* ---- phone / tablet banner ---- */}
      <div className="h2-phone lg:hidden" ref={artRef2}>
        <div className="h2-art" aria-hidden="true">
          <img className="h2-band" src={H2_ASSETS.band} alt=""/>
          <img className="h2-head" src={H2_ASSETS.head} alt=""/>
          <div className="h2-shade"></div><div className="h2-shade2"></div>
        </div>
        <button type="button" onClick={onBack} aria-label="Back to the dashboard" className="h2-back">{'←'}</button>
        <div className="h2-top">
          <H2Coin token={token} logo={logo}/>
          <div className="h2-id">
            <div className="orb h2-tref h2-name">{token}</div>
            {addrRow}
            <div className="h2-day">{dayPill}</div>
          </div>
        </div>
        <div className="h2-price">
          {priceBlock('h2-pricev')}
          {chgRow(true)}
        </div>
        <div className="h2-stats">{stats}</div>
        <div className="h2-btns">{btns}</div>
      </div>
    </div>
    {/* the tab row is a SIBLING of the banner wrapper — position:sticky ends with its parent (gotcha 36) */}
    <H2TabBand token={token} vars={vars} active={active} navTo={navTo} mini={mini} miniOn={scrolled}/>
  </>);
};
