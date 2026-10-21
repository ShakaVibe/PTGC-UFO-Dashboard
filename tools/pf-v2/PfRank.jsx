    /* ===== HOLDER RANK WINDOW (2026-10-21, design/portfolio/mock-rank-window-v1.html, "perfect!") =====
       Opens from any rank badge. Reads data/rank-index/<TOKEN>/meta.json + the wallet's shard (<first three hex>.json): for every
       wallet that ever held, [firstDayIndex, [rank delta per day]] over the token's life (rank 0 = not holding). Today's point is the
       LIVE rank from holder-ranks.json (pfRank), so the chart ends where the badge says. Periods LIFE · 1Y · 90D · 30D · 7D. Buy /
       sell dots = Recent Transactions' rows (t, addr, tok, type). Several wallets → "as one" is not in the index (it is a sum), so
       the window opens on the FIRST counted wallet with a picker. */
    const PFR_RAW='https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/rank-index/';
    const pfrCache={};
    const pfrGet=url=>pfrCache[url]||(pfrCache[url]=fetch(url,{cache:'no-cache'}).then(r=>r.ok?r.json():null).catch(()=>null).then(j=>{if(!j)delete pfrCache[url];return j;}));
    /* → {day0, days, series:[rank|0 per day index], holders:[count per day]} for one wallet, or null */
    const pfrLoad=async(tok,addr)=>{
      const a=addr.toLowerCase();
      const[meta,shard]=await Promise.all([pfrGet(`${PFR_RAW}${tok}/meta.json`),pfrGet(`${PFR_RAW}${tok}/${a.slice(2,5)}.json`)]);
      if(!meta||meta.schema!==2)return null;
      const series=new Array(meta.days).fill(0);
      const rec=shard&&shard[a];
      if(rec){let i=rec[0],r=0;for(const d of rec[1]){r+=d;if(i<series.length)series[i]=r;i++;}}   // schema 2: [firstDay, [rank delta per day]]
      return{day0:meta.day0,days:meta.days,series,holders:meta.holders||[],generatedAt:meta.generatedAt,known:!!rec};
    };
    const usePfRankHist=(tok,addr)=>{const[d,setD]=useState({state:'loading'});
      useEffect(()=>{let live=true;setD({state:'loading'});pfrLoad(tok,addr).then(h=>{if(!live)return;setD(h?{state:'ok',...h}:{state:'failed'});});return()=>{live=false;};},[tok,addr]);return d;};
    const PFR_PERIODS=[['LIFE',Infinity],['1Y',365],['90D',90],['30D',30],['7D',7]];
    const pfrDate=(day0,i)=>new Date(Date.parse(day0+'T00:00:00Z')+i*86400e3);
    const pfrFmt=(d,long)=>long?d.toLocaleDateString('en-US',{month:'short',day:'numeric',year:'numeric',timeZone:'UTC'}):d.toLocaleDateString('en-US',{month:'short',day:'numeric',timeZone:'UTC'});
    const pfrFmtY=d=>d.toLocaleDateString('en-US',{month:'short',year:'2-digit',timeZone:'UTC'});
    /* small gold line icons for the tiles and section titles */
    const PfIco=({k})=>{const P={trophy:'M6 3h12v3a5 5 0 0 1-3 4.6V13h3v2H6v-2h3v-2.4A5 5 0 0 1 6 6V3zm-3 2h3v2a3 3 0 0 1-3-2zm18 0h-3v2a3 3 0 0 0 3-2z',down:'M5 8l7 8 7-8z',bars:'M4 20V12h3v8zm6.5 0V5h3v15zm6.5 0v-9h3v9z',cal:'M5 5h14v15H5zM5 9h14M8 3v4m8-4v4',chart:'M4 18 9 12l3 3 7-8M19 7h-4m4 0v4',bolt:'M13 2 4 14h6l-1 8 9-12h-6z'};
      return <svg className={`pf2-ico${k==='down'?' dn':''}`} viewBox="0 0 24 24" aria-hidden="true"><path d={P[k]} fill={k==='bolt'||k==='down'||k==='bars'||k==='trophy'?'currentColor':'none'} stroke="currentColor" strokeWidth={k==='bolt'||k==='trophy'?0:1.8} strokeLinecap="round" strokeLinejoin="round"/></svg>;};
    /* the chart: rank over time, higher = better (y flipped), the period's own scale, buy / sell dots, the best point marked */
    const PfRankChart=({pts,day0,i0,col,evs,tok})=>{
      /* phones: a narrower, taller drawing with bigger type (the 820-wide one shrinks to unreadable at 390 px) */
      const narrow=typeof window!=='undefined'&&window.innerWidth<=700;
      const W=narrow?360:820,H=narrow?230:260,L=narrow?40:48,R=narrow?10:14,T=18,B=narrow?26:30,FS=narrow?12:11;
      const held=pts.map((r,i)=>[i,r]).filter(x=>x[1]>0);
      if(held.length<2)return <div className="pf2-hwait" style={{height:200}}><div>Not enough days with this wallet holding {tok} to draw yet.</div></div>;
      const lo=Math.min(...held.map(x=>x[1])),hi=Math.max(...held.map(x=>x[1]));
      /* 2026-10-21 (Shaka, a whale that dumped: #12 all year then #8,469 — "it's just a straight line … something must be off on the
         scale"): on a 1 → 9,500 linear scale #12 and #1 are the same pixel. When the period spans more than 8× in rank the scale is
         LOG, so #12 sits a quarter of the way down and the drop still shows; the top gridline is the period's best, the bottom its
         worst. A narrow range stays linear with whole-rank gridlines. */
      const logS=hi/lo>=8;
      const lo2=logS?Math.max(1,lo/1.12):Math.max(1,lo-Math.max(1,(hi-lo)*.12)),hi2=logS?hi*1.12:hi+Math.max(1,(hi-lo)*.12);
      const sc=v=>logS?Math.log(v):v;
      const n=pts.length;const X=i=>L+(W-L-R)*i/Math.max(1,n-1),Y=v=>T+(H-T-B)*(sc(v)-sc(lo2))/(sc(hi2)-sc(lo2));
      /* gaps (rank 0 = not holding) break the line */
      const segs=[];let cur=[];pts.forEach((r,i)=>{if(r>0)cur.push(`${X(i).toFixed(1)},${Y(r).toFixed(1)}`);else if(cur.length){segs.push(cur);cur=[];}});if(cur.length)segs.push(cur);
      const area=segs.map(s=>{const f=s[0].split(','),l=s[s.length-1].split(',');return `M${f[0]},${H-B} L${s.join(' L')} L${l[0]},${H-B} Z`;}).join(' ');
      /* gridlines on whole ranks only — a #1–#2 range used to print "#2, #2, #3, #3" */
      const nice=v=>{const m=Math.pow(10,Math.floor(Math.log10(v))-1);return Math.max(1,Math.round(v/m)*m);};   // 2 significant digits
      const gv=logS?[...new Set([lo,...[1,2,3].map(k=>nice(Math.exp(Math.log(lo)+(Math.log(hi)-Math.log(lo))*k/4))),hi])].filter(v=>v>=1)
        :[...new Set([0,1,2,3,4].map(k=>Math.round(lo2+(hi2-lo2)*k/4)))].filter(v=>v>=1);
      const grid=gv.map(v=>{const y=Y(v),k=v;return <g key={k}><line x1={L} x2={W-R} y1={y} y2={y} stroke="rgba(255,255,255,.07)"/><text x={L-6} y={y+4} textAnchor="end" fontSize={FS} fill="rgba(255,255,255,.5)" fontFamily="Rajdhani" fontWeight="600">#{Math.round(v).toLocaleString('en-US')}</text></g>;});
      const XL=narrow?[0,2,4]:[0,1,2,3,4];const xl=XL.map(k=>{const i=Math.round((n-1)*k/4),d=pfrDate(day0,i0+i);return <text key={k} x={X(i)} y={H-8} textAnchor="middle" fontSize={FS} fill="rgba(255,255,255,.5)" fontFamily="Rajdhani" fontWeight="600">{n<=120?pfrFmt(d):pfrFmtY(d)}</text>;});
      const bi=held.reduce((m,x)=>x[1]<m[1]?x:m,held[0]);
      const gid='pfrg'+(col==='#F2D35B'?'p':'u');
      return <svg viewBox={`0 0 ${W} ${H}`} className="pf2-rkc" role="img" aria-label={`${tok} holder rank over time, best #${bi[1]}`}>
        <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity=".85"/><stop offset=".55" stopColor={col} stopOpacity=".45"/><stop offset="1" stopColor={col} stopOpacity=".12"/></linearGradient>
          <pattern id={gid+'d'} width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r=".8" fill="rgba(255,255,255,.13)"/></pattern></defs>
        <rect x={L} y={T} width={W-L-R} height={H-T-B} fill={`url(#${gid}d)`}/>
        {grid}<path d={area} fill={`url(#${gid})`}/>{segs.map((s,k)=><polyline key={k} points={s.join(' ')} fill="none" stroke={col} strokeWidth="2.6" strokeLinejoin="round" style={{filter:`drop-shadow(0 0 6px ${col})`}}/>)}
        {evs.map((e,k)=>pts[e.i]>0&&<circle key={k} cx={X(e.i)} cy={Y(pts[e.i])+(evs.some(o=>o.i===e.i&&o.inn!==e.inn)?(e.inn?-5:5):0)} r={evs.length>40?3:4} fill={e.inn?'#39E15A':'#FF4B55'} stroke="#0b0d12" strokeWidth="1.5"><title>{e.what} · {pfrFmt(pfrDate(day0,i0+e.i),true)}</title></circle>)}
        {(()=>{/* the BEST marker is skipped only when it would sit ON today's label: today IS the best (the end label says BEST), or best is within 6% of the end AND at nearly the same height (a whale that was #12 last week and dumped to #8,469 today keeps its BEST #12) */const nearEnd=X(n-1)-X(bi[0])<(W-L-R)*.06;if(bi[0]===n-1||(nearEnd&&Math.abs(Y(bi[1])-Y(pts[n-1]))<22))return null;const right=X(bi[0])>W-R-110;return <>
          <circle cx={X(bi[0])} cy={Y(bi[1])} r="5" fill="#0b0d12" stroke={col} strokeWidth="2"/>
          <text x={right?X(bi[0])-9:X(bi[0])+9} y={Y(bi[1])<T+16?Y(bi[1])+16:Y(bi[1])-9} textAnchor={right?'end':'start'} fontSize="11" fill={col} fontFamily="Orbitron" fontWeight="900" style={{paintOrder:'stroke',stroke:'#05060a',strokeWidth:4}}>BEST #{bi[1].toLocaleString('en-US')}</text>
        </>;})()}
        <circle cx={X(n-1)} cy={Y(pts[n-1])} r="6" fill="#0b0d12" stroke={col} strokeWidth="2.5"/><circle cx={X(n-1)} cy={Y(pts[n-1])} r="2.5" fill={col}/>
        <text x={X(n-1)-12} y={Y(pts[n-1])<T+16?Y(pts[n-1])+5:Y(pts[n-1])-10} textAnchor="end" fontSize="12" fill={col} fontFamily="Orbitron" fontWeight="900" style={{paintOrder:'stroke',stroke:'#05060a',strokeWidth:4}}>{bi[1]===pts[n-1]?'BEST ':''}#{pts[n-1].toLocaleString('en-US')}</text>{xl}</svg>;
    };
    const PfRankModal=({tok:tok0,wallets,data,ranks,txs,prices,close})=>{
      const[tok,setTok]=useState(tok0);
      const[sel,setSel]=useState(()=>wallets[0]&&wallets[0].address.toLowerCase());
      const[per,setPer]=useState(()=>{try{return localStorage.getItem('grays_pf_rank_per')||'1Y';}catch(e){return '1Y';}});
      /* Shaka: "default the chart to NOT show buys and sells.. if they want to see them they can check a box.. and then they get a
         loading while it loads" + "should always default to off.. even on refresh" — off every time the window opens, never remembered */
      const[showTx,setShowTx]=useState(false);
      const[want,setWant]=useState('');   // the calculator's typed rank (his add, 2026-10-21 evening: mock-rank-calc-v2, pick C)
      const isU=tok==='UFO',col=isU?'#8DFF3A':'#F2D35B',logo=isU?TOKENS.UFO.logo:TOKENS.PTGC.logo;
      const w=wallets.find(x=>x.address.toLowerCase()===sel)||wallets[0];
      const d=w&&data[w.address.toLowerCase()];
      const bal=d&&!d.error?(isU?(d.ufo.balance||0):(d.ptgc.totalHolding||0)):0;
      const live=pfRank(ranks,tok,bal);
      const h=usePfRankHist(tok,w?w.address:'0x');
      const nowT=usePfTick();
      /* the series + today's live point */
      const full=h.state==='ok'?[...h.series]:null;
      if(full){const today=Math.floor((Date.now()-Date.parse(h.day0+'T00:00:00Z'))/86400e3);while(full.length<=today)full.push(0);full[today]=live?live.r:0;}
      const nDays=PFR_PERIODS.find(p=>p[0]===per)[1];
      const i0=full?Math.max(0,full.length-Math.min(full.length,nDays)):0;
      const pts=full?full.slice(i0):[];
      const held=pts.filter(r=>r>0);
      const first=pts.find(r=>r>0)||null,best=held.length?Math.min(...held):null,worst=held.length?Math.max(...held):null;
      const bestI=best!=null?pts.indexOf(best):-1,worstI=worst!=null?pts.lastIndexOf(worst):-1;
      const chg=live&&first?live.r-first:null;
      const tracked=full?full.filter(r=>r>0).length:0;
      /* DAYS IN TOP N (Shaka, 2026-10-21 pm): the first of 100 / 500 / 1,000 / 2,500 / 5,000 / 10,000 the wallet has ever been inside */
      const topN=full?[100,500,1000,2500,5000,10000].map(n=>[n,full.filter(r=>r>0&&r<=n).length]).find(([n,c])=>c>0)||[10000,0]:[100,0];
      /* days tokens moved IN or OUT of this wallet, from Recent Transactions (r.t is in MILLISECONDS — the first build multiplied by
         1,000 and no dot ever landed inside the chart). Shaka: "should sends be added, because they can send tokens out of the
         wallet, which would lower their rank" → yes: every row that changed the balance counts — buys, receives, claims and LP
         removes are IN (green); sells, sends and LP adds are OUT (red); a move between two of his wallets is OUT of one and IN to
         the other (the list keeps one row per move, so the counterparty side is read from cp). Unstakes are left out — staked
         PTGC is still in the wallet's balance, so an unstake changes nothing. One dot per day per direction. */
      const wa=w&&w.address.toLowerCase();
      const evs=(()=>{const seen=new Set(),out=[];(txs&&txs.rows||[]).forEach(r=>{if(r.tok!==tok||r.type==='Unstake')return;let dir;if(r.addr===wa)dir=r.dir;else if(r.type==='Move'&&r.cp===wa)dir=-r.dir;else return;const i=Math.floor((r.t-Date.parse(h.day0+'T00:00:00Z'))/86400e3)-i0;if(i<0||i>=pts.length)return;const k=i+(dir>0?'i':'o');if(seen.has(k))return;seen.add(k);out.push({i,inn:dir>0,what:r.type==='Move'?(dir>0?'Move in':'Move out'):r.type});});return out;})();
      /* is THIS wallet + token read back to the start of the period? (LIFE = a year, as far as the list goes). cov = the time the
         list is complete back to (0 = its whole history); jd = that job finished (no more pages / the cap / a year). While not:
         a percentage of the period covered, so the spinner moves. */
      const txK=wa+'|'+tok,now=Date.now();
      const perStart=Math.max(h.day0?Date.parse(h.day0+'T00:00:00Z')+i0*86400e3:0,now-365*864e5);
      const txCov=txs&&txs.cov?txs.cov[txK]:undefined,txJd=!!(txs&&txs.jd&&txs.jd[txK]);
      const txDone=!!txs&&(txCov===0||(txCov!==undefined&&txCov<=perStart)||txJd||!txs.busy);
      const txBusy=!txDone;
      const txPct=!txs||txCov===undefined?0:Math.min(99,Math.max(1,Math.round((now-txCov)/Math.max(1,now-perStart)*100)));
      useEffect(()=>{if(showTx&&txs&&txs.prioritize&&wa)txs.prioritize(wa,tok);},[showTx,wa,tok,!!(txs&&txs.prioritize)]);
      /* what it takes: milestones from today's list */
      const list=ranks&&ranks.tokens&&ranks.tokens[tok]&&ranks.tokens[tok].b||[];
      const ms=live?[live.r-1,10,5,1].filter((r,i,a)=>r>=1&&r<live.r&&a.indexOf(r)===i):[];
      const px=isU?prices.ufo:prices.ptgc;
      return(
        <PfModal className="z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80" onClose={close} label={`${tok} holder rank`}>
          <div className={`pf2-erw pf2-rkw${isU?' u':''}`} onClick={ev=>ev.stopPropagation()}>
            <div aria-hidden="true" className={`pf2-rkw-sky${isU?' ufo':''}`}></div>
            <div className="ehd"><img src={logo} alt=""/><div className="tt"><h2><span className="tk">{tok}</span> HOLDER RANK</h2><div className="sub"><span>{w?(w.name||pfAddr(w.address)):'—'}{w&&w.name?<> {'·'} {pfAddr(w.address)}</>:null} {'·'} {pfAbbr(bal)} {tok}</span>
                {/* 2026-10-21 (his pick B of mock-rank-league-v1): the wallet's league on BOTH tokens — the sea creature the League box
                   uses, the window's token lit, the other one quiet; a token it does not hold gets no chip */}
                {d&&!d.error&&['PTGC','UFO'].map(T=>{const b=T==='UFO'?(d.ufo.balance||0):(d.ptgc.totalHolding||0),L=pfLeague(b,PF_SUPPLY[T]);if(!L||!L.cur)return null;
                  return <span key={T} className={`lgc${T==='UFO'?' u':''}${T===tok?' on':''}`} title={L.next?`${L.pct.toFixed(1)}% to ${L.next.name} · need ${pfAbbr(L.need)} ${T}`:`Top league — ${L.cur.name}`}><img src={pfSea(L.cur.emoji)} alt=""/>{T} {L.cur.name}</span>;})}</div></div>
              <div className="tw"><div className="tabs">{['PTGC','UFO'].map(t=><button key={t} className={tok===t?'on':''} aria-pressed={tok===t} onClick={()=>setTok(t)}><img src={t==='UFO'?TOKENS.UFO.logo:TOKENS.PTGC.logo} alt=""/>{t}</button>)}</div></div>
              <button className="x" onClick={close} aria-label="Close">{'×'}</button></div>
            {wallets.length>1&&<div className="pf2-edsel"><div className="ws">{wallets.map(x=>{const a=x.address.toLowerCase();return <button key={a} className={sel===a?'on':''} aria-pressed={sel===a} onClick={()=>setSel(a)}>{x.name||pfAddr(x.address)}</button>;})}</div></div>}
            <div className="hero">
              <div className="big"><small>TODAY</small><span className="wr"><b>{live?'#'+live.r.toLocaleString('en-US'):'—'}</b></span>
                {chg==null?<span className="flat">{live?'—':'not holding '+tok}</span>:chg===0?<span className="flat">{'—'} no change</span>:<span className={chg<0?'up':'dn'}>{chg<0?'▲':'▼'} {Math.abs(chg).toLocaleString('en-US')} place{Math.abs(chg)===1?'':'s'}</span>}
                <em>{per==='LIFE'?'since the first day held':`vs ${nDays} days ago`}</em></div>
              <div className="tiles">
                <div className="tl"><div className="l"><PfIco k="trophy"/>BEST EVER</div><div className="v">{best!=null?'#'+best.toLocaleString('en-US'):'—'}</div><div className="s">{bestI>=0?pfrFmt(pfrDate(h.day0,i0+bestI),true):''}</div></div>
                <div className="tl"><div className="l"><PfIco k="down"/>LOWEST</div><div className="v">{worst!=null?'#'+worst.toLocaleString('en-US'):'—'}</div><div className="s">{worstI>=0?pfrFmt(pfrDate(h.day0,i0+worstI),true):''}</div></div>
                <div className="tl"><div className="l"><PfIco k="bars"/>{live&&live.pass!=null?`TO PASS #${(live.r-1).toLocaleString('en-US')}`:'TO PASS'}</div><div className="v">{live?live.pass==null?'—':pfPassAmt(live.pass):'—'}</div><div className="s">{live?live.pass==null?'nobody above you':tok+' more':''}</div></div>
                <div className="tl"><div className="l"><PfIco k="cal"/>DAYS IN TOP {topN[0].toLocaleString('en-US')}</div><div className="v">{full?topN[1].toLocaleString('en-US'):'—'}</div><div className="s">{full?`of ${tracked.toLocaleString('en-US')} held`:''}</div></div>
              </div>
            </div>
            <div className="ch"><div className="chh"><span><PfIco k="chart"/>RANK OVER TIME</span><div className="pp" role="group" aria-label="Period">{PFR_PERIODS.map(([k])=><button key={k} className={per===k?'on':''} aria-pressed={per===k} onClick={()=>{setPer(k);try{localStorage.setItem('grays_pf_rank_per',k);}catch(e){}}}>{k}</button>)}</div></div>
              {h.state==='loading'&&<div className="pf2-hwait" style={{height:200}}><div>Reading the rank history{'…'}</div></div>}
              {h.state==='failed'&&<div className="pf2-hwait" style={{height:200}}><div>The rank history isn{'’'}t available right now.</div></div>}
              {full&&<PfRankChart pts={pts} day0={h.day0} i0={i0} col={col} evs={showTx?evs:[]} tok={tok}/>}
              <div className="lg"><span><i style={{background:col}}></i>your rank {'·'} higher is better</span><label className="tx"><input type="checkbox" checked={showTx} onChange={e=>setShowTx(e.target.checked)}/><span className="bx" aria-hidden="true"></span>show buys {'&'} sells</label>{showTx&&<span><i style={{background:'#39E15A'}}></i>tokens in</span>}{showTx&&<span><i style={{background:'#FF4B55'}}></i>tokens out</span>}{showTx&&txBusy&&<span className="ld"><i className="sp"></i>reading your transactions{'…'} <b>{txPct}%</b></span>}{showTx&&!txBusy&&!evs.length&&<span className="ld" style={{opacity:.6}}>none in this period</span>}<span className="r">one point per UTC day {'·'} today{'’'}s point is live</span></div></div>
            {live&&ms.length>0&&<div className="wt"><div className="chh"><span><PfIco k="bolt"/>WHAT IT TAKES</span><span className="r">from today{'’'}s holder list</span></div><div className="lad">
              {ms.map(r=>{const need=Math.max(0,(list[r-1]||0)-pfRankKey(bal)+1);const pct=list[r-1]>0?Math.min(100,pfRankKey(bal)/list[r-1]*100):0;const c=usd(need,px);
                return <div className="st" key={r}><span className="rk">#{r.toLocaleString('en-US')}</span><span className="bar"><i style={{width:pct+'%'}}></i></span><span className="nd">+ {pfPassAmt(need)} {tok}{c!=null&&<small className="usd"> {'≈'} {fmtDollar(c,0)}</small>}</span></div>;})}
            </div>
              {/* the calculator (mock-rank-calc-v2, his pick C): type any rank → tokens to buy, cost at today's price, the league it makes you.
                 The ⓘ: cost is a snapshot — slippage and the price moving as you buy are not in it. */}
              {(()=>{const n=parseInt(String(want).replace(/[^0-9]/g,''),10);const ok=n>=1&&n<=list.length;const mine=live.r;
                const need=ok&&n<mine?Math.max(0,(list[n-1]||0)-pfRankKey(bal)+1):0;const c=usd(need,px);
                const L=ok&&n<mine?pfLeague(bal+need,PF_SUPPLY[tok]):null;const L0=pfLeague(bal,PF_SUPPLY[tok]);
                const msg=!want?null:!ok?(n>list.length?`the list ends at #${list.length.toLocaleString('en-US')}`:'type a rank'):n>=mine?(n===mine?`that’s you — #${mine.toLocaleString('en-US')} today`:`you’re already above #${n.toLocaleString('en-US')}`):null;
                return <div className="ctl">
                  <div className="ask"><div className="l">I WANT TO BE RANK <span className="ii" tabIndex="0" aria-label="About the cost">i<span className="tip" role="tooltip"><b>Cost is a snapshot.</b> It’s the tokens you’d need at today’s price. A real buy moves the price as it fills — slippage and the price rising while you buy aren’t included, so expect the real cost to be higher.</span></span></div>
                    <label className="inp"><span>#</span><input inputMode="numeric" pattern="[0-9]*" placeholder={mine>1?String(Math.max(1,Math.ceil(mine/2))):'1'} value={want} onChange={e=>setWant(e.target.value.replace(/[^0-9]/g,'').slice(0,6))} aria-label="The rank you want"/></label>
                    <div className="s">{msg||<>any rank above your #{mine.toLocaleString('en-US')} {'·'} from today{'’'}s holder list</>}</div></div>
                  <div className="tl"><div className="l">TOKENS TO BUY</div><div className="v">{ok&&n<mine?pfPassAmt(need):'—'}</div><div className="s">{tok} more than you hold</div></div>
                  <div className="tl"><div className="l">COST TODAY</div><div className={`v${ok&&n<mine&&c!=null?' usd':''}`}>{ok&&n<mine&&c!=null?fmtDollar(c,0):'—'}</div><div className="s">at {fmtPriceNode(px)} per {tok}</div></div>
                  <div className="tl"><div className="l">YOU’D BE A</div><div className="v">{L&&L.cur?<><img src={pfSea(L.cur.emoji)} alt=""/>{L.cur.name}</>:'—'}</div><div className="s">{L&&L.cur?(L.next?`${L.pct.toFixed(1)}% of the way to ${L.next.name}`:'the top league'):L0&&L0.cur?`you’re a ${L0.cur.name} now`:''}</div></div>
                </div>;})()}
            </div>}
            <div className="ft">Ranked among every wallet holding {tok}, except liquidity pools and other contracts, the burn addresses, the token contracts and the DAO{isU?' and UFO OA':''} wallets {'·'} history rebuilt from the chain, one point per UTC day{h.state==='ok'?<> {'·'} history to {pfrFmt(pfrDate(h.day0,h.days-1),true)}</>:null}</div>
          </div>
        </PfModal>
      );
    };
