    /* ===== LEAGUE HISTORY (2026-10-24, design/creatures/README.md + mock-creatures-v1.html; Shaka: "Thats awesome... Lets build it,
       but I dont want to make it live yet") =====
       How many of each sea creature hold PTGC / UFO, every UTC day since launch: data/league-history.json (scripts/build-league-history.mjs,
       holder-ranks lane after rank-history — the rank window's archive walked day by day, PEOPLE only = the Token Allocation strip's
       population). Eight cards (count now, change over the period, joined / left, sparkline) → the big chart of the tapped league
       (hover / touch = that day's count), PTGC / UFO, 7D … ALL, starting / circulating supply, a Wide share card.
       Hidden until LEAGUE_HISTORY_LIVE: the faint bottom-right dot of the dashboard opens it (LhDot). Going live = flip the flag:
       the dot goes, the creature strip in the Token Allocation panel becomes the button (with a small HISTORY tag).
       Honest states (gotcha 20): loading = skeleton cards; a failed read = "couldn't load" + Retry; a file older than 2 days says so. */
    const LEAGUE_HISTORY_LIVE=false;
    const LH_URL='https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/league-history.json';
    const LH_TIERS=[['Poseidon','trident','10%'],['Whale','whale','1%'],['Shark','shark','0.1%'],['Dolphin','dolphin','0.01%'],['Squid','squid','0.001%'],['Turtle','turtle','0.0001%'],['Shrimp','shrimp','0.00001%'],['Shell','shell',null]];
    const LH_PERS=[['7D',7,'7 days'],['30D',30,'30 days'],['90D',90,'90 days'],['6M',182,'6 months'],['1Y',365,'1 year'],['ALL',null,'all time']];
    let lhP=null;
    const lhLoad=()=>lhP||(lhP=dataFetch(LH_URL).then(r=>r.ok?r.json():null).catch(()=>null)
      .then(j=>{const ok=j&&j.schema>=1&&j.tokens&&j.tokens.PTGC;if(!ok)lhP=null;return ok?j:null;}));
    const lhSea=k=>`logos/panels/sea-${k}.webp?v=${SEA_ART_V}`;
    const lhFmt=n=>n==null||!isFinite(n)?'—':Math.round(n).toLocaleString('en-US');
    const lhDay=(day0,k)=>new Date(Date.parse(day0+'T00:00:00Z')+k*86400e3);
    const lhDate=(d,long)=>d.toLocaleDateString('en-US',{month:'short',day:'numeric',year:long?'numeric':undefined,timeZone:'UTC'});
    const LhChange=({a,b,f=lhFmt})=>{const d=b-a;if(d===0)return <span className="lh-fl">{'—'} no change</span>;const p=a>0?Math.abs(d/a*100):null;
      return <span className={d>0?'lh-up':'lh-dn'}>{d>0?'▲':'▼'} {f(Math.abs(d))}{p!=null&&<> ({p.toFixed(1)}%)</>}</span>;};
    /* a sparkline: the period's own scale, flat when the count never moved */
    const LhSpark=({vals,w=120,h=34,col})=>{const mn=Math.min(...vals),mx=Math.max(...vals),r=mx-mn;
      const pts=vals.map((v,i)=>`${(i/(vals.length-1||1)*w).toFixed(1)},${(r?h-3-(v-mn)/r*(h-6):h/2).toFixed(1)}`).join(' ');
      return <svg viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true"><polyline points={pts} fill="none" stroke={col} strokeWidth="2" vectorEffect="non-scaling-stroke" strokeLinejoin="round"/></svg>;};
    /* the big chart: the selected league over the period — y on round steps, high / low marked, today's dot, hover / touch readout */
    const LhChart=({vals,day0,i0,col,f=lhFmt,what="Count"})=>{
      const box=useRef(null);const[w,setW]=useState(900);const[hv,setHv]=useState(null);
      useEffect(()=>{const el=box.current;if(!el)return;const on=()=>setW(Math.max(260,Math.round(el.clientWidth)));on();
        const ro=typeof ResizeObserver!=='undefined'?new ResizeObserver(on):null;if(ro)ro.observe(el);else window.addEventListener('resize',on);
        return()=>{if(ro)ro.disconnect();else window.removeEventListener('resize',on);};},[]);
      const ph=w<560,H=ph?230:290,L=ph?40:48,R=12,T=16,B=28;
      const mn0=Math.min(...vals),mx0=Math.max(...vals),pad=Math.max(1,Math.round((mx0-mn0)*.12));   // f: lhFmt (wallets) or fmtAbbr (tokens held)
      let mn=Math.max(0,mn0-pad),mx=mx0+pad;const r0=(mx-mn)/4,p10=10**Math.floor(Math.log10(r0||1));
      const step=[1,2,2.5,5,10].map(m=>m*p10).find(s=>s>=r0)||r0||1;mn=Math.floor(mn/step)*step;mx=Math.ceil(mx/step)*step;if(mx===mn)mx=mn+step;
      const X=k=>L+k/(vals.length-1||1)*(w-L-R),Y=v=>T+(1-(v-mn)/(mx-mn))*(H-T-B);
      const ticks=[];for(let v=mn;v<=mx+1e-9;v+=step)ticks.push(v);
      const nt=ph?4:6,xt=[];for(let t=0;t<nt;t++)xt.push(Math.round(t/(nt-1)*(vals.length-1)));
      const pts=vals.map((v,k)=>`${X(k).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
      const last=vals.length-1,hi=vals.indexOf(mx0),lo=vals.lastIndexOf(mn0),long=vals.length>200;
      const gid=`lhg${col.slice(1)}`;
      const move=e=>{const el=box.current;if(!el)return;const rc=el.getBoundingClientRect();const x=(e.touches?e.touches[0].clientX:e.clientX)-rc.left;
        const k=Math.round((x-L)/(rc.width-L-R)*(vals.length-1));setHv(Math.max(0,Math.min(last,k)));};
      return(
        <div className="lh-ch" ref={box} onMouseMove={move} onMouseLeave={()=>setHv(null)} onTouchStart={move} onTouchMove={move} onTouchEnd={()=>setHv(null)}>
          <svg viewBox={`0 0 ${w} ${H}`} role="img" aria-label={`${what} over the period: ${f(vals[0])} to ${f(vals[last])}, high ${f(mx0)}, low ${f(mn0)}`}>
            <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity=".32"/><stop offset="1" stopColor={col} stopOpacity="0"/></linearGradient></defs>
            {ticks.map(v=><g key={v}><line x1={L} x2={w-R} y1={Y(v)} y2={Y(v)} stroke="rgba(255,255,255,.07)"/><text x={L-8} y={Y(v)+4} fill="rgba(255,255,255,.5)" fontSize="12" fontFamily="Rajdhani" fontWeight="600" textAnchor="end">{f(v)}</text></g>)}
            {xt.map((k,t)=><text key={t} x={X(k)} y={H-8} fill="rgba(255,255,255,.5)" fontSize="12" fontFamily="Rajdhani" fontWeight="600" textAnchor={t===0?'start':t===nt-1?'end':'middle'}>{lhDate(lhDay(day0,i0+k),long)}</text>)}
            <path d={`M${X(0)},${Y(mn)} L${pts.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid})`}/>
            <polyline points={pts} fill="none" stroke={col} strokeWidth="2.6" strokeLinejoin="round"/>
            {hi!==last&&hi!==0&&mx0!==mn0&&<g><circle cx={X(hi)} cy={Y(mx0)} r="4.5" fill="#05070c" stroke={col} strokeWidth="2.5"/><text x={Math.min(w-R-24,Math.max(L+24,X(hi)))} y={Y(mx0)-12} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">high {f(mx0)}</text></g>}
            {lo!==last&&lo!==0&&lo!==hi&&mx0!==mn0&&<g><circle cx={X(lo)} cy={Y(mn0)} r="4.5" fill="#05070c" stroke={col} strokeWidth="2.5"/><text x={Math.min(w-R-24,Math.max(L+24,X(lo)))} y={Y(mn0)+21} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">low {f(mn0)}</text></g>}
            <circle cx={X(last)} cy={Y(vals[last])} r="6" fill={col} stroke="#05070c" strokeWidth="2"/>
            {hv!=null&&<g><line x1={X(hv)} x2={X(hv)} y1={T} y2={H-B} stroke="rgba(255,255,255,.35)" strokeDasharray="3 4"/><circle cx={X(hv)} cy={Y(vals[hv])} r="5" fill={col} stroke="#05070c" strokeWidth="2"/></g>}
          </svg>
          {hv!=null&&<div className="lh-tip" style={{left:`${Math.min(88,Math.max(12,X(hv)/w*100))}%`}}><small>{lhDate(lhDay(day0,i0+hv),true)}</small>{f(vals[hv])}</div>}
        </div>);
    };
    /* the share card: Wide 1200 × 675, the eight leagues then → now with sparklines (screenshot-only, like the other v2 cards) */
    const LhShareCard=({tok,t,per,basis,i0})=>{const isU=tok==='UFO',col=isU?'#8DFF3A':'#F2D35B',rows=t[basis],last=rows.length-1,pd=LH_PERS.find(p=>p[0]===per);
      return(
        <div className={`lh-card${isU?' u':''}`}><div className="sky"></div><div className="veil"></div><div className="in">
          <div className="tt"><img src={TOKENS[tok].logo} alt=""/><div><div className="h"><span className="t">{tok}</span> LEAGUES</div>
            <div className="pd">{i0===0&&pd[1]!=null?`Since ${lhDate(lhDay(t.day0,0),true)}`:pd[0]==='ALL'?'Since launch':pd[2].replace(/^./,c=>c.toUpperCase())} {'·'} {lhDate(lhDay(t.day0,i0),true)} {'→'} {lhDate(lhDay(t.day0,last),true)}</div></div></div>
          <div className="g">{LH_TIERS.map(([n,img],i)=>{const a=rows[i0][i],b=rows[last][i];return(
            <div className="c" key={n}><div className="r1"><img src={lhSea(img)} alt=""/><div className="nm">{n.toUpperCase()}</div></div>
              <div className="ft"><small>{lhFmt(a)} {'→'}</small>{lhFmt(b)}</div><div className="ch"><LhChange a={a} b={b}/>{t.held&&t.held[basis]&&<span className="hd"> {'\u00B7'} hold {fmtAbbr(t.held[basis][last][i])}</span>}</div>
              <LhSpark vals={rows.slice(i0).map(r=>r[i])} w={240} h={44} col={col}/></div>);})}</div></div>
          <div className="bt"><span>People only + the {'\u{1F525}'} burn wallet {'·'} {basis==='circ'?'circulating':'starting'} supply {'·'} rebuilt from the chain</span><b>PTGC-UFO.COM</b></div>
        </div>);
    };
    const LeagueHistoryModal=({token,onClose})=>{
      const[tok,setTok]=useState(token==='UFO'?'UFO':'PTGC');
      const[per,setPer]=useState(()=>{const v=lsGet(LS.LH_PER);return LH_PERS.some(p=>p[0]===v)?v:'6M';});
      const[basis,setBasis]=useState('start');
      const[sel,setSel]=useState(2);   // Shark — the one he asked about
      const[file,setFile]=useState(undefined);   // undefined = loading, null = failed
      const[share,setShare]=useState(false);
      const[mode,setMode]=useState('w');   // the big chart: 'w' = wallets, 't' = tokens held (2026-10-24, Shaka: "how many tokens do those 107 wallets hold")
      const load=()=>{setFile(undefined);lhLoad().then(j=>setFile(j||null));};
      useEffect(load,[]);
      const isU=tok==='UFO',col=isU?'#8DFF3A':'#F2D35B';
      const t=file&&file.tokens&&file.tokens[tok];
      const rows=t&&t[basis];
      const pd=LH_PERS.find(p=>p[0]===per);
      const last=rows?rows.length-1:0,i0=rows?(pd[1]==null||pd[1]>last?0:last-pd[1]):0;
      const fl=t&&t.flows&&t.flows[per]&&t.flows[per][basis];
      const ageDays=t?Math.floor((Date.now()-lhDay(t.day0,last).getTime())/86400e3):0;
      const span=rows?(i0===0&&pd[1]!=null&&pd[1]>last?`since ${lhDate(lhDay(t.day0,0),true)}`:`${lhDate(lhDay(t.day0,i0),true)} → ${lhDate(lhDay(t.day0,last),true)}`):'';
      const setP=k=>{setPer(k);lsSet(LS.LH_PER,k);};
      const total=rows?rows[last].reduce((s,v)=>s+v,0):null;
      /* tokens held per league (schema 3): `held[basis]` per day; the share is of the basis supply THAT day (circulating = starting − the
         burn wallet's balance, the `burned` line, which is per ARCHIVE day — offset by the days trimmed before the first holder) */
      const held=t&&t.held&&t.held[basis];
      const off=t&&t.archiveDay0?Math.round((Date.parse(t.day0)-Date.parse(t.archiveDay0))/864e5):0;
      const supAt=k=>!t?null:basis==='circ'?(Array.isArray(t.burned)&&t.burned[off+k]!=null?t.supply-t.burned[off+k]:null):t.supply;
      const shareOf=(v,k)=>{const sp=supAt(k);if(!(sp>0)||v==null)return null;const p=v/sp*100;return p>=10?p.toFixed(1):p>=0.1?p.toFixed(2):p>=0.001?p.toFixed(3):'<0.001';};
      const tm=mode==='t'&&!!held;
      return(
        <Modal onClose={onClose} label={`${tok} league history`} className="z-50 overflow-y-auto overscroll-contain bg-black/85 sm:p-4">
          <div className={`lh-win${isU?' u':''}`} onClick={e=>e.stopPropagation()}>
            <div className="lh-hd"><div className="sky" aria-hidden="true"></div><div className="veil" aria-hidden="true"></div>
              {rows&&<button type="button" className="lh-cam" onClick={()=>setShare(true)} aria-label="Share the league history as an image">{'\u{1F4F7}'}<span>SHARE</span></button>}
              <button type="button" className="lh-x" onClick={onClose} aria-label="Close">{'×'}</button>
              <div className="lh-hc"><img className="lh-coin" src={TOKENS[tok].logo} alt=""/>
                <h2><span className="t">{tok}</span><span className="w">LEAGUE HISTORY</span></h2>
                <div className="lh-sub">How many of each sea creature hold {tok} {'—'} every day since {isU?'Jul 8, 2026':'launch, Oct 2023'}</div>
                <div className="lh-ctl">
                  <div className="lh-tg" role="group" aria-label="Token">{['PTGC','UFO'].map(k=><button type="button" key={k} aria-pressed={tok===k} onClick={()=>setTok(k)}><img src={TOKENS[k].logo} alt=""/>{k}</button>)}</div>
                  <div className="lh-tg" role="group" aria-label="Period">{LH_PERS.map(([k,,lab])=><button type="button" key={k} aria-pressed={per===k} aria-label={lab} onClick={()=>setP(k)}>{k}</button>)}</div>
                  <div className="lh-tg" role="group" aria-label="Supply basis"><button type="button" aria-pressed={basis==='start'} onClick={()=>setBasis('start')}>STARTING SUPPLY</button><button type="button" aria-pressed={basis==='circ'} onClick={()=>setBasis('circ')}>CIRCULATING</button></div>
                </div></div></div>
            <div className="lh-body">
              {file===undefined&&<div className="lh-cards">{LH_TIERS.map(([n])=><div key={n} className="lh-sk"></div>)}</div>}
              {file===null&&<div className="lh-wait">Couldn{'’'}t load the league history right now.<button type="button" onClick={load}>RETRY</button></div>}
              {file&&!rows&&<div className="lh-wait">No league history for {tok} yet.</div>}
              {rows&&<>
                <div className="lh-cards">{LH_TIERS.map(([n,img,th],i)=>{const a=rows[i0][i],b=rows[last][i];return(
                  <button type="button" key={n} className="lh-cd" aria-pressed={sel===i} onClick={()=>setSel(i)} aria-label={`${n}: ${lhFmt(b)} now, ${b-a>=0?'up':'down'} ${lhFmt(Math.abs(b-a))} over ${pd[2]} — show the chart`}>
                    <div className="top"><span className="ic"><img src={lhSea(img)} alt=""/>{t.burnIn&&t.burnIn[basis]===i&&<span className="bw" title="Includes the burn wallet (0x…0369)" aria-label="includes the burn wallet">{'\u{1F525}'}</span>}</span><div><div className="nm">{n}</div><div className="th">{th?`≥ ${th} of supply`:'below Shrimp'}</div></div></div>
                    <div className="v">{lhFmt(b)}</div><div className="ch"><LhChange a={a} b={b}/></div>
                    {held&&<div className="hd2">hold <b>{fmtAbbr(held[last][i])}</b> {'\u00B7'} {shareOf(held[last][i],last)}%</div>}
                    <div className="jl">{fl?<><b className="lh-up">+{lhFmt(fl[0][i])}</b> joined {'·'} <b className="lh-dn">{'−'}{lhFmt(fl[1][i])}</b> left</>:' '}</div>
                    <LhSpark vals={rows.slice(i0).map(r=>r[i])} col={col}/>
                  </button>);})}</div>
                {(()=>{const[n,img]=LH_TIERS[sel],a=rows[i0][sel],b=rows[last][sel];return(
                  <div className="lh-big">
                    <div className="lh-bh"><div className="l"><img src={lhSea(img)} alt=""/><div><h3>{n.toUpperCase()}S {tm?'\u2014 TOKENS HELD':'OVER TIME'}</h3>
                      {tm?<div className="s"><b>{fmtAbbr(held[i0][sel])}</b> {'→'} <b>{fmtAbbr(held[last][sel])}</b> <LhChange a={held[i0][sel]} b={held[last][sel]} f={fmtAbbr}/> <span style={{color:'rgba(255,255,255,.45)'}}>{'·'} {span}</span></div>
                        :<div className="s"><b>{lhFmt(a)}</b> {'→'} <b>{lhFmt(b)}</b> <LhChange a={a} b={b}/> <span style={{color:'rgba(255,255,255,.45)'}}>{'·'} {span}</span></div>}</div></div>
                      <div className="r"><div className="lh-pill"><div className="k">JOINED</div><div className="n lh-up">{fl?'+'+lhFmt(fl[0][sel]):'—'}</div></div>
                        <div className="lh-pill"><div className="k">LEFT</div><div className="n lh-dn">{fl?'−'+lhFmt(fl[1][sel]):'—'}</div></div>
                        {tm?<div className="lh-pill"><div className="k">SHARE OF SUPPLY</div><div className="n">{shareOf(held[last][sel],last)}%</div></div>
                          :<div className="lh-pill"><div className="k">ALL HOLDERS</div><div className="n">{lhFmt(total)}</div></div>}</div></div>
                    {held&&<div className="lh-tg lh-mode" role="group" aria-label="Chart"><button type="button" aria-pressed={!tm} onClick={()=>setMode('w')}>WALLETS</button><button type="button" aria-pressed={tm} onClick={()=>setMode('t')}>TOKENS HELD</button></div>}
                    {tm?<LhChart key="t" vals={held.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} f={fmtAbbr} what="Tokens held"/>
                      :<LhChart key="w" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col}/>}
                  </div>);})()}
                <div className="lh-foot"><b>People only, plus the {'\u{1F525}'} burn wallet</b> {'—'} wallets holding {tok}; pools, contracts, the token contracts and the DAO{isU?' and UFO OA':''} wallets are left out; the burn wallet counts in the league its balance puts it in (the same count as the Token Allocation strip). Leagues are a share of the <b>{basis==='circ'?'circulating supply that day (starting − burned)':'starting supply'}</b>. One point per UTC day, rebuilt from the chain {'·'} <span className={ageDays>2?'old':undefined}>history to the close of {lhDate(lhDay(t.day0,last),true)} (UTC)</span>. <b>Hold</b> = the tokens that league{'\u2019'}s wallets hold that day, and their share of the {basis==='circ'?'circulating':'starting'} supply. <b>Joined / left</b> = wallets that moved into or out of a league over the period (by buying, selling, or {basis==='circ'?'a burn moving the line':'moving tokens'}); joined {'−'} left = the change.</div>
              </>}
            </div>
          </div>
          {share&&rows&&<ShareCardModal onClose={()=>setShare(false)} width={1200} height={675} zIndex={60} screenshot label={`${tok} league history share card`} filename={`${tok.toLowerCase()}-leagues-${per.toLowerCase()}-${new Date().toISOString().slice(0,10)}.png`}>
            <LhShareCard tok={tok} t={t} per={per} basis={basis} i0={i0}/>
          </ShareCardModal>}
        </Modal>);
    };
    /* the faint bottom-right dot while !LEAGUE_HISTORY_LIVE (the VsDot / NhDot pattern) */
    const LhDot=({token,onOpen})=>(
      <button type="button" onClick={onOpen} aria-label="League history (preview)" title="" className="fixed bottom-1 right-1 z-30 w-7 h-7 flex items-center justify-center bg-transparent border-0 p-0">
        <span aria-hidden="true" className="block w-1.5 h-1.5 rounded-full" style={{background:(TOKENS[token]||TOKENS.PTGC).colorHex,opacity:0.16}}></span>
      </button>
    );
