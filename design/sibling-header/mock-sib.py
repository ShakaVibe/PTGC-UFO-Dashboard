#!/usr/bin/env python3
"""Build calculators.mock.html = calculators.html + the v2 header in three variants (?v=A|B|C).
Throwaway mock-up builder for design/sibling-header/ (2026-10-03). Not part of the site."""
import re, sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
idx = (root/'index.html').read_text().split('\n')
calc = (root/'calculators.html').read_text()

# 1. the h2-* CSS block from index.html (lines 275..496, 1-based)
css = '\n'.join(idx[274:496])
assert css.lstrip().startswith('/* ===== DASHBOARD HEADER v2'), css[:80]
assert '.h2-tabs,.h2-tiles{--u:' in idx[495]
extra_css = r"""
    /* --- sibling-page extras (mock) --- */
    .h2-tabs .h2-mini.always{margin-right:calc(10*var(--u))}
    .h2-tabs .h2-tabrow .h2-back{flex:none;margin-right:calc(6*var(--u));font-size:max(calc(26*var(--u)),1rem);color:rgba(255,255,255,.55);padding:0 calc(10*var(--u));line-height:1}
    .h2-tabs .h2-tabrow .h2-back:hover{color:#fff}
    .h2-tabs .h2-acts{margin-left:auto;flex:none;display:flex;align-items:center;gap:calc(10*var(--u));padding-left:calc(16*var(--u))}
    .h2-tabs .h2-msw,.h2-tabs .h2-mbuy{display:inline-flex;align-items:center;gap:calc(8*var(--u));height:calc(40*var(--u));padding:0 calc(16*var(--u)) 0 calc(8*var(--u));border-radius:calc(10*var(--u));font-family:'Orbitron',monospace;font-weight:700;font-size:max(calc(14*var(--u)),.6rem);letter-spacing:.14em;white-space:nowrap;line-height:1}
    .h2-tabs .h2-msw{color:#fff;background:rgba(0,0,0,.5);border:1px solid rgba(var(--sw-edge),.7);box-shadow:0 0 10px -2px rgba(var(--sw-rgb),.5),inset 0 1px 0 rgba(255,255,255,.08)}
    .h2-tabs .h2-msw img,.h2-tabs .h2-mbuy img{width:calc(26*var(--u));height:calc(26*var(--u));border-radius:50%}
    .h2-tabs .h2-mbuy{color:var(--buy-ink);background:var(--buy-bg);border:1px solid rgba(255,235,170,.6);box-shadow:0 0 12px -2px rgba(var(--buy-glow),.7),inset 0 1px 0 rgba(255,255,255,.35)}
    .h2-sub{--u:calc(var(--hsd,.665)*.0625rem);display:flex;align-items:center;gap:calc(34*var(--u));padding:calc(12*var(--u)) calc(40*var(--u));background:#04070a;border-bottom:1px solid rgba(255,255,255,.08);color:#fff;font-family:'Rajdhani',sans-serif;overflow-x:auto;scrollbar-width:none}
    .h2-sub .h2-ss{display:flex;align-items:baseline;gap:calc(10*var(--u));white-space:nowrap}
    .h2-sub .h2-ssl{font-size:max(calc(13*var(--u)),.6rem);font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:rgba(255,255,255,.62)}
    .h2-sub .h2-ssv{font-size:max(calc(24*var(--u)),.9rem);font-weight:700;line-height:1}
    .h2-sub .h2-addr{font-size:max(calc(14*var(--u)),.7rem);color:rgba(255,255,255,.7);display:flex;align-items:center;gap:calc(8*var(--u))}
    .h2-sub .h2-vl{width:1px;height:calc(28*var(--u));background:rgba(255,255,255,.14)}
    .h2-sub .h2-daypill{height:calc(34*var(--u));gap:calc(9*var(--u));padding:0 calc(16*var(--u)) 0 calc(12*var(--u))}
    .h2-sub .h2-daypill svg{width:calc(16*var(--u));height:calc(16*var(--u))}
    .h2-sub .h2-daypill .h2-dayl{font-size:max(calc(12*var(--u)),.6rem)}
    .h2-sub .h2-daypill .h2-dayn{font-size:max(calc(16*var(--u)),.75rem)}
    @media(max-width:1023.98px){.h2-sub{--u:calc(var(--hsp,1)*.0625rem);gap:calc(14*var(--u));padding:calc(8*var(--u)) calc(12*var(--u))}.h2-sub .h2-ssv{font-size:max(calc(15*var(--u)),.85rem)}.h2-sub .h2-ssl{font-size:max(calc(9*var(--u)),.55rem)}.h2-tabs .h2-acts{padding-left:calc(8*var(--u))}.h2-tabs .h2-msw,.h2-tabs .h2-mbuy{height:calc(30*var(--u));font-size:max(calc(10*var(--u)),.55rem);padding:0 calc(10*var(--u)) 0 calc(6*var(--u))}.h2-tabs .h2-msw img,.h2-tabs .h2-mbuy img{width:calc(20*var(--u));height:calc(20*var(--u))}}
"""
calc = calc.replace('  </style>\n</head>', css + extra_css + '\n  </style>\n</head>', 1)

# 2. components: scale hook + icons + coin + buttons (verbatim from index.html) + a page header
def block(a, b):
    s = '\n'.join(idx[a-1:b]); return s
comp = block(8939, 8950)            # h2Scale, h2DocW, useH2Scale
comp += '\n' + "const H2_ASSETS={band:'logos/header/dash-bg.jpg',head:'logos/header/alien-head.webp',corona:{PTGC:'logos/header/coin-corona.webp',UFO:'logos/header/coin-corona-green.webp'}};"
comp += '\n' + block(9139, 9162)    # H2Tri, H2Cal, H2Copy, H2Info, H2Coin, H2Btns
assert 'const H2Btns' in comp and 'const useH2Scale' in comp
comp += r"""
    const Sk=({w,h,className=''})=><span className={'inline-block rounded bg-white/10 animate-pulse '+className} style={{width:w,height:h}}></span>;
    const H2Stat=({label,value,loading,skW})=>(
      <div className="h2-stat">
        <div className="h2-statl">{label}</div>
        {loading?<div className="h2-statv"><Sk w={skW} h="1em" className="opacity-60"/></div>:<div className="h2-tref2 tn h2-statv h2-sh">{value}</div>}
      </div>);
    const MOCK_V=(new URLSearchParams(location.search).get('v')||'A').toUpperCase();
    /* The sibling-page header under v2 (mock): A = the dashboard's banner + band; B = band + slim stat strip; C = band only. */
    const SibHeaderV2=(p)=>{
      const{token,cfg,data,loading,hdrDaysOld,copied,copyAddress,changeKnown,priceUp,plsRatio,xToATH,xToPenny,fmtX,onBack,onSwitch,onBuy,navTo,active,variant}=p;
      const sc=useH2Scale();
      const[scrolled,setScrolled]=useState(false);
      const artRef=useRef(null),artRef2=useRef(null);
      useEffect(()=>{
        if(variant!=='A'){setScrolled(true);return;}
        const on=()=>{const a=artRef.current,b=artRef2.current;const h=(a&&a.offsetHeight)||(b&&b.offsetHeight)||300;setScrolled(window.scrollY>h-40);};
        on();window.addEventListener('scroll',on,{passive:true});
        return()=>window.removeEventListener('scroll',on);
      },[variant]);
      const chgCls=changeKnown?(priceUp?'up':'dn'):'na';
      const chgTxt=changeKnown?`${priceUp?'+':'−'}${Math.abs(data.change).toFixed(2)}%`:'—';
      const addr=`${cfg.address.slice(0,6)}...${cfg.address.slice(-4)}`;
      const other=token==='PTGC'?'UFO':'PTGC';
      const dayPill=hdrDaysOld!=null?<span className="h2-daypill"><H2Cal/><span className="h2-dayl">DAY</span><span className="orb h2-tref2 h2-dayn tn">{hdrDaysOld.toLocaleString()}</span></span>:null;
      const addrRow=(<div className="h2-addr tn">{addr}<button type="button" onClick={copyAddress} aria-label={copied?'Copied':'Copy contract address'} className="-my-2 -mx-1" style={{fontSize:'.85em'}}>{copied?'✓':<H2Copy/>}</button></div>);
      const stats=(<>
        <H2Stat label="PLS Ratio" value={plsRatio} loading={loading} skW="3em"/>
        <H2Stat label="X's to ATH" value={fmtX(xToATH)} loading={loading} skW="3em"/>
        <H2Stat label="X's to a Penny" value={fmtX(xToPenny)} loading={loading} skW="3em"/>
      </>);
      const priceBlock=(cls)=>(loading?<Sk w="70%" h="1em" className={cls+' mx-auto opacity-60'}/>:<Price p={data?.price} c={`h2-tprice tn h2-sh ${cls}`}/>);
      const chgRow=(inline)=>(<div className={`h2-chg tn ${chgCls}`}>{loading?<Sk w="4em" h=".9em" className="opacity-60"/>:<>{changeKnown&&<H2Tri down={!priceUp}/>}{chgTxt}{inline&&<span className="h2-chgl">24h</span>}</>}</div>);
      const mini=(cls)=>(
        <div className={cls}>
          <img src={cfg.logo} alt=""/><span className="h2-mname h2-tref">{token}</span>
          <span className="h2-mright">{loading?<Sk w={72} h={14}/>:<><Price p={data?.price} c="h2-mprice h2-tprice tn"/><span className={`h2-mchg tn ${chgCls}`}>{chgTxt}</span></>}</span>
        </div>);
      const tab=(key,label,href)=>href
        ?<a key={key} href={href} aria-current={active===key?'page':undefined} className="h2-tab">{label}</a>
        :<button type="button" key={key} aria-current={active===key?'page':undefined} onClick={()=>navTo(key)} className="h2-tab">{label}</button>;
      const vars={'--hsd':sc.hsd,'--hsp':sc.hsp};
      const acts=(<div className="h2-acts">
        {variant==='B'&&token==='PTGC'&&<button type="button" onClick={onBuy} className="h2-mbuy"><img src={cfg.logo} alt=""/>BUY / SELL</button>}
        <button type="button" onClick={onSwitch} aria-label={`Switch to ${other}`} className="h2-msw"><img src={TOKENS[other].logo} alt=""/>SWITCH</button>
      </div>);
      return(<>
        {variant==='A'&&(
        <div className="h2" data-tok={token} style={vars}>
          <div className="h2-desk hidden lg:block" ref={artRef}>
            <div className="h2-art" aria-hidden="true">
              <img className="h2-band" src={H2_ASSETS.band} alt=""/>
              <img className="h2-band2" src={H2_ASSETS.band} alt=""/>
              <img className="h2-head" src={H2_ASSETS.head} alt=""/>
              <div className="h2-shade"></div><div className="h2-shade-r"></div><div className="h2-fade"></div>
            </div>
            <button type="button" onClick={onBack} aria-label="Back to the dashboard" className="h2-back tap">{'←'}</button>
            <div className="h2-row">
              <H2Coin token={token} cfg={cfg}/>
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
              <div className="h2-btns"><H2Btns token={token} cfg={cfg} openSwap={onBuy} onSwitch={onSwitch}/></div>
            </div>
          </div>
          <div className="h2-phone lg:hidden" ref={artRef2}>
            <div className="h2-art" aria-hidden="true">
              <img className="h2-band" src={H2_ASSETS.band} alt=""/>
              <img className="h2-head" src={H2_ASSETS.head} alt=""/>
              <div className="h2-shade"></div><div className="h2-shade2"></div>
            </div>
            <button type="button" onClick={onBack} aria-label="Back to the dashboard" className="h2-back tap">{'←'}</button>
            <div className="h2-top">
              <H2Coin token={token} cfg={cfg}/>
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
            <div className="h2-btns"><H2Btns token={token} cfg={cfg} openSwap={onBuy} onSwitch={onSwitch}/></div>
          </div>
        </div>)}
        <div className="h2 h2-tabs" data-tok={token} style={vars}>
            {scrolled&&<div className="lg:hidden">{mini('h2-phone-mini')}</div>}
            <div className="h2-tabband">
            <nav aria-label="Site sections" className="h2-tabrow">
              {variant!=='A'&&<button type="button" onClick={onBack} aria-label="Back to the dashboard" className="h2-back">{'←'}</button>}
              {scrolled&&<div className="hidden lg:flex">{mini('h2-mini'+(variant!=='A'?' always':''))}</div>}
              {tab('dashboard','Dashboard')}
              {tab('kpi','KPI Report')}
              {tab('social','Socials')}
              {tab('calculators','Calculators',`./calculators.html?from=${token}`)}
              {tab('charts','Charts',`./charts.html?from=${token}`)}
              {tab('portfolio','Portfolio',`./portfolio.html?from=${token}`)}
              {tab('affiliates','Affiliates')}
              {variant!=='A'&&acts}
            </nav>
            </div>
        </div>
        {variant==='B'&&(
        <div className="h2-sub" data-tok={token} style={vars}>
          {dayPill}
          <div className="h2-vl"></div>
          <div className="h2-ss"><span className="h2-ssl">PLS Ratio</span><span className="h2-ssv h2-tref2 tn">{plsRatio}</span></div>
          <div className="h2-ss"><span className="h2-ssl">X's to ATH</span><span className="h2-ssv h2-tref2 tn">{fmtX(xToATH)}</span></div>
          <div className="h2-ss"><span className="h2-ssl">X's to a Penny</span><span className="h2-ssv h2-tref2 tn">{fmtX(xToPenny)}</span></div>
          <div className="h2-vl"></div>
          {addrRow}
        </div>)}
      </>);
    };
"""
# the .h2-sub needs the tref2 gradient: it is defined under `.h2 .h2-tref2`, so give the strip the h2 class too
comp = comp.replace('<div className="h2-sub" data-tok={token}', '<div className="h2 h2-sub" data-tok={token}')
calc = calc.replace('    const CalculatorsPage=()=>{', comp + '\n    const CalculatorsPage=()=>{', 1)
calc = calc.replace('const {useState,useEffect,useMemo}=React;', 'const {useState,useEffect,useMemo,useRef,useLayoutEffect}=React;', 1)

# 3. fork the header
m = re.search(r'(\n          <header className="sticky top-0 z-50 bg-\[#0a0a0a\]/95 backdrop-blur-md border-b border-white/10">.*?\n          </header>\n)', calc, re.S)
assert m
classic = m.group(1)
fork = ('\n          {MOCK_V===\'0\'?(' + classic.rstrip('\n') + '\n          ):(<SibHeaderV2 token={token} cfg={cfg} data={data} loading={loading} hdrDaysOld={hdrDaysOld} copied={copied} copyAddress={copyAddress} changeKnown={data?.change!=null} priceUp={priceUp} plsRatio={plsRatio} xToATH={xToATH} xToPenny={xToPenny} fmtX={hdrFmtX} onBack={goBack} onSwitch={switchToken} onBuy={()=>window.open(\'https://goptgc.com/#/ptgc-onboarding\')} navTo={navTo} active="calculators" variant={MOCK_V}/>)}\n')
calc = calc.replace(classic, fork, 1)
(root/'calculators.mock.html').write_text(calc)
print('wrote calculators.mock.html', len(calc))
