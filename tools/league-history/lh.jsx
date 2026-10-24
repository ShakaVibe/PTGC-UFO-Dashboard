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
    /* lh7 (schema 4): start / circ / held are DELTA-encoded per day (row 0 whole) and held is in units of enc.heldUnit tokens —
       decoded once here, so everything below reads plain per-day rows (schema 1–3 files pass through as they are) */
    const lhUndelta=(rows,m=1)=>{const o=[];let p=null;for(const r of rows||[]){const c=p?r.map((v,i)=>v+p[i]):r.slice();o.push(c);p=c;}return m===1?o:o.map(r=>r.map(v=>v*m));};
    const lhDecode=j=>{if(!(j.schema>=4))return j;const u=(j.enc&&j.enc.heldUnit)||1;
      for(const k in j.tokens){const t=j.tokens[k];t.start=lhUndelta(t.start);t.circ=lhUndelta(t.circ);if(t.held)t.held={start:lhUndelta(t.held.start,u),circ:lhUndelta(t.held.circ,u)};}return j;};
    /* lh4: the read is kept for an hour, then the next opening re-reads it (no-cache = a 304 when the file did not change) */
    let lhP=null,lhAt=0;
    const lhLoad=()=>{if(lhP&&Date.now()-lhAt<36e5)return lhP;lhAt=Date.now();
      return lhP=dataFetch(LH_URL).then(r=>r.ok?r.json():null).catch(()=>null)
        .then(j=>{const ok=j&&j.schema>=1&&j.tokens&&j.tokens.PTGC;if(!ok){lhP=null;return null;}try{return lhDecode(j);}catch(e){lhP=null;return null;}});};
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
    /* lh9 (2026-10-24): the geometry is built once per data / width (useMemo) — a mouse move only moves the cursor and the readout.
       lh2 + lh11: no floating hover box — the READOUT row above the plot always shows a day: the latest, or the one under the mouse /
       finger (never clipped at a phone edge, never over the lines); on a phone the day stays after the finger lifts (LATEST = back).
       rd(k) → [main text, second text | null] for day k of the slice. */
    const lhNice=r=>{const p=10**Math.floor(Math.log10(r||1));return[1,2,2.5,5,10].map(m=>m*p).find(s=>s>=r)||r||1;};
    const lhUnit=v=>v>=1e9?'B':v>=1e6?'M':v>=1e3?'K':'';   // the tokens axis title's unit
    const LhChart=({vals,day0,i0,col,f=lhFmt,what="Count",v2=null,f2=fmtAbbr,col2='#7DD3FC',rd=null,tl=null,tr=null})=>{
      const box=useRef(null);const[w,setW]=useState(900);const[hv,setHv]=useState(null);const[pin,setPin]=useState(false);
      useEffect(()=>{const el=box.current;if(!el)return;const on=()=>setW(Math.max(260,Math.round(el.clientWidth)));on();
        const ro=typeof ResizeObserver!=='undefined'?new ResizeObserver(on):null;if(ro)ro.observe(el);else window.addEventListener('resize',on);
        return()=>{if(ro)ro.disconnect();else window.removeEventListener('resize',on);};},[]);
      useEffect(()=>{setHv(null);setPin(false);},[vals.length,i0,day0]);   // another period / token: back to the latest day
      const g=useMemo(()=>{
        const ph=w<560,tt=tl||tr?20:0,H=(ph?230:290)+tt,L=ph?40:48,R=v2?(ph?54:60):12,T=16+tt,B=28;
        const mn0=Math.min(...vals),mx0=Math.max(...vals),pad=Math.max(1,Math.round((mx0-mn0)*.12));   // f: lhFmt (wallets) or fmtAbbr (tokens held)
        let mn=Math.max(0,mn0-pad),mx=mx0+pad;const r0=(mx-mn)/4,p10=10**Math.floor(Math.log10(r0||1));
        const step=[1,2,2.5,5,10].map(m=>m*p10).filter(s=>f!==lhFmt||(s>=1&&Number.isInteger(s))).find(s=>s>=r0)||r0||1;   // counts: whole steps only
        mn=Math.floor(mn/step)*step;mx=Math.ceil(mx/step)*step;if(mx===mn)mx=mn+step;
        const X=k=>L+k/(vals.length-1||1)*(w-L-R),Y=v=>T+(1-(v-mn)/(mx-mn))*(H-T-B);
        const ticks=[];for(let v=mn;v<=mx+1e-9;v+=step)ticks.push(v);
        const long=vals.length>200,nt=ph?(long?3:4):6,xt=[];/* phone + a long period (dates with the year): 3 labels */for(let t=0;t<nt;t++)xt.push(Math.round(t/(nt-1)*(vals.length-1)));
        const pts=vals.map((v,k)=>`${X(k).toFixed(1)},${Y(v).toFixed(1)}`).join(' ');
        let Y2=null,pts2='',r2=[];
        if(v2){const nd=ticks.length-1,a0=Math.min(...v2),b0=Math.max(...v2),pd2=(b0-a0)*.12||b0*.05||1,lo=Math.max(0,a0-pd2),hi2=b0+pd2;
          let st=lhNice((hi2-lo)/nd),m2=Math.floor(lo/st)*st;for(let q=0;q<12&&m2+st*nd<hi2;q++){st=lhNice(st*1.001);m2=Math.floor(lo/st)*st;}
          Y2=v=>T+(1-(v-m2)/(st*nd))*(H-T-B);pts2=v2.map((v,k)=>`${X(k).toFixed(1)},${Y2(v).toFixed(1)}`).join(' ');
          r2=ticks.map((v,j)=>[Y(v),m2+st*j]);}
        const last=vals.length-1;
        return{ph,H,L,R,T,B,mn,mx,mn0,mx0,X,Y,Y2,ticks,xt,nt,long,pts,pts2,r2,last,hi:vals.indexOf(mx0),lo:vals.lastIndexOf(mn0)};
      },[vals,v2,w,f,tl,tr]);
      const{H,L,R,T,B,mn,mn0,mx0,X,Y,Y2,ticks,xt,nt,long,pts,pts2,r2,last,hi,lo}=g;
      const gid=`lhg${col.slice(1)}`;
      /* pointer events: a finger / pen PINS the day (it stays after lifting — LATEST goes back); the mouse follows and leaves */
      const at=e=>{const el=box.current;if(!el)return;const rc=el.getBoundingClientRect();const x=e.clientX-rc.left;
        const k=Math.round((x-L)/(rc.width-L-R)*(vals.length-1));setHv(Math.max(0,Math.min(last,k)));setPin(e.pointerType!=='mouse');};
      const k=hv!=null&&hv<=last?hv:null,kk=k!=null?k:last;
      const[r1,r2t]=rd?rd(kk):[f(vals[kk]),v2?`hold ${f2(v2[kk])}`:null];
      return(
        <div className="lh-ch" ref={box}>
          <div className="lh-rd"><small>{lhDate(lhDay(day0,i0+kk),true)}{k==null?' \u00B7 latest':''}</small><b>{r1}</b>{r2t&&<span className="t2">{r2t}</span>}
            {pin&&k!=null&&<button type="button" className="lh-rdx" onClick={()=>{setHv(null);setPin(false);}}>LATEST</button>}</div>
          <svg viewBox={`0 0 ${w} ${H}`} role="img" aria-label={`${what} over the period: ${f(vals[0])} to ${f(vals[last])}, high ${f(mx0)}, low ${f(mn0)}`}
            onPointerDown={at} onPointerMove={at} onPointerLeave={e=>{if(e.pointerType==='mouse')setHv(null);}}>
            <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity=".32"/><stop offset="1" stopColor={col} stopOpacity="0"/></linearGradient>
              {v2&&<linearGradient id={gid+'b'} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col2} stopOpacity=".26"/><stop offset="1" stopColor={col2} stopOpacity=".02"/></linearGradient>}</defs>
            {tl&&<text className="ttl" x={2} y={14} fill={col} fontFamily="Orbitron" fontWeight="700" letterSpacing="1.4">{tl}</text>}
            {tr&&<text className="ttl" x={w-2} y={14} fill={col2} fontFamily="Orbitron" fontWeight="700" letterSpacing="1.4" textAnchor="end">{tr}</text>}
            {ticks.map(v=><g key={v}><line x1={L} x2={w-R} y1={Y(v)} y2={Y(v)} stroke="rgba(255,255,255,.07)"/><text x={L-8} y={Y(v)+4} fill="rgba(255,255,255,.5)" fontSize="12" fontFamily="Rajdhani" fontWeight="600" textAnchor="end">{f(v)}</text></g>)}
            {xt.map((q,t)=><text key={t} x={X(q)} y={H-8} fill="rgba(255,255,255,.5)" fontSize="12" fontFamily="Rajdhani" fontWeight="600" textAnchor={t===0?'start':t===nt-1?'end':'middle'}>{lhDate(lhDay(day0,i0+q),long)}</text>)}
            {v2&&<>{r2.map(([y,v],j)=><text key={'r'+j} x={w-R+7} y={y+4} fill={col2} fillOpacity=".75" fontSize="12" fontFamily="Rajdhani" fontWeight="600">{f2(v)}</text>)}
              <path d={`M${X(0)},${Y(mn)} L${pts2.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid}b)`}/>
              <polyline points={pts2} fill="none" stroke={col2} strokeOpacity=".95" strokeWidth="2.2" strokeLinejoin="round" style={{filter:`drop-shadow(0 0 4px ${col2})`}}/>
              <circle cx={X(last)} cy={Y2(v2[last])} r="4.5" fill={col2} stroke="#05070c" strokeWidth="2"/></>}
            {!v2&&<path d={`M${X(0)},${Y(mn)} L${pts.split(' ').join(' L')} L${X(last)},${Y(mn)} Z`} fill={`url(#${gid})`}/>}
            <polyline points={pts} fill="none" stroke={col} strokeWidth="2.8" strokeLinejoin="round" style={{filter:`drop-shadow(0 0 5px ${col})`}}/>
            {hi!==last&&hi!==0&&mx0!==mn0&&<g><circle cx={X(hi)} cy={Y(mx0)} r="4.5" fill="#05070c" stroke={col} strokeWidth="2.5"/>{(()=>{const tx=`High ${f(mx0)}`,pw=tx.length*7.4+16,cx=Math.min(w-R-pw/2,Math.max(L+pw/2,X(hi))),cy=Y(mx0)-17;return<g><rect x={cx-pw/2} y={cy-10.5} width={pw} height={21} rx={10.5} fill="rgba(5,7,12,.85)" stroke={col} strokeOpacity=".7"/><text x={cx} y={cy+4.5} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">{tx}</text></g>;})()}</g>}
            {lo!==last&&lo!==0&&lo!==hi&&mx0!==mn0&&<g><circle cx={X(lo)} cy={Y(mn0)} r="4.5" fill="#05070c" stroke={col} strokeWidth="2.5"/>{(()=>{const tx=`Low ${f(mn0)}`,pw=tx.length*7.4+16,cx=Math.min(w-R-pw/2,Math.max(L+pw/2,X(lo))),cy=Math.min(H-B-12,Y(mn0)+18);return<g><rect x={cx-pw/2} y={cy-10.5} width={pw} height={21} rx={10.5} fill="rgba(5,7,12,.85)" stroke={col} strokeOpacity=".7"/><text x={cx} y={cy+4.5} fill="#fff" fontSize="13" fontFamily="Rajdhani" fontWeight="700" textAnchor="middle">{tx}</text></g>;})()}</g>}
            <circle cx={X(last)} cy={Y(vals[last])} r="6" fill={col} stroke="#05070c" strokeWidth="2"/>
            {k!=null&&<g><line x1={X(k)} x2={X(k)} y1={T} y2={H-B} stroke="rgba(255,255,255,.35)" strokeDasharray="3 4"/><circle cx={X(k)} cy={Y(vals[k])} r="5" fill={col} stroke="#05070c" strokeWidth="2"/>{v2&&<circle cx={X(k)} cy={Y2(v2[k])} r="4.5" fill={col2} stroke="#05070c" strokeWidth="2"/>}</g>}
          </svg>
        </div>);
    };
    /* the ownership BEAM (2026-10-24, Shaka's mock-up v3 "B"): one glowing section per league, its length = the league's share of the
       tokens in holders' wallets on the last day (pools / contracts / the DAO are not on it, so the leagues fill the beam). No labels —
       hover (mouse) or tap (finger) shows the creature, wallets, share of the supply (shareOf: the basis supply) and tokens; a click /
       tap also selects the league. The tip is clamped inside the beam's width (never off a phone's edge). */
    const LH_BEAM_C=[['#6B4A06','#E8B828','#FFF0A0','255,200,60'],['#0A2A7A','#2F7BFF','#BFDDFF','60,130,255'],['#2E3646','#8D99AC','#F2F5FA','190,200,220'],['#05506E','#1FB6EE','#C8F6FF','40,190,245'],
      ['#5E0A12','#E8434B','#FFC2C4','240,70,80'],['#0C4E18','#3FC24A','#D2FFC0','70,210,80'],['#6A2A06','#FF8A3D','#FFDDB8','255,140,60'],['#6E463C','#EDB7A6','#FFF4EE','240,190,175']];   // [dark, core, hot end, glow] per league
    const LhBeam=({t,tok,basis,last,onSel,shareOf})=>{
      const box=useRef(null),tipRef=useRef(null);const[hv,setHv]=useState(null);const[pin,setPin]=useState(false);
      const held=t&&t.held&&t.held[basis],row=held?held[last]:null,cnt=t&&t[basis]?t[basis][last]:null;
      const tot=row?row.reduce((s,v)=>s+v,0):0;
      useEffect(()=>{setHv(null);setPin(false);},[tok,basis]);
      useEffect(()=>{if(!pin)return;const f=e=>{if(box.current&&!box.current.contains(e.target)){setHv(null);setPin(false);}};
        document.addEventListener('pointerdown',f);return()=>document.removeEventListener('pointerdown',f);},[pin]);
      useLayoutEffect(()=>{const b=box.current,tp=tipRef.current;if(!b||!tp||hv==null)return;const sg=b.querySelector(`[data-i="${hv}"]`);if(!sg)return;
        const W=b.clientWidth,tw=tp.offsetWidth,c=sg.offsetLeft+sg.offsetWidth/2,x=Math.max(0,Math.min(W-tw,c-tw/2));
        tp.style.left=`${x}px`;tp.style.setProperty('--ax',`${Math.max(14,Math.min(tw-14,c-x))}px`);},[hv,tok,basis,last]);
      if(!row||!cnt||!(tot>0))return null;
      const lastI=row.reduce((k,v,i)=>v>0?i:k,-1);
      const tap=i=>{const off=hv===i&&pin;setHv(off?null:i);setPin(!off);};
      const h=hv!=null&&row[hv]>0?hv:null;
      return(
        <div className="lh-bm" ref={box}>
          <div className="lh-bm-tr" role="group" aria-label={`Who holds ${tok}: the leagues' share of the tokens in holders' wallets`}
            onPointerLeave={e=>{if(e.pointerType==='mouse'&&!pin)setHv(null);}}>
            {LH_TIERS.map(([nm],i)=>{if(!(row[i]>0))return null;const[k,m,l,g]=LH_BEAM_C[i],sh=shareOf(row[i],last);return(
              <button type="button" key={nm} data-i={i} className={`lh-bm-s${h===i?' hv':''}`} style={{flex:`${(row[i]/tot*100).toFixed(5)} 1 0`,'--k':k,'--m':m,'--l':l,'--g':g}}
                aria-label={`${nm}: ${lhFmt(cnt[i])} wallet${cnt[i]===1?'':'s'} hold ${fmtAbbr(row[i])} ${tok}${sh!=null?`, ${sh}% of the supply`:''} — show the chart`}
                onPointerEnter={e=>{if(e.pointerType==='mouse'&&!pin)setHv(i);}} onPointerDown={e=>{if(e.pointerType!=='mouse')tap(i);}}
                onFocus={()=>setHv(i)} onBlur={()=>{if(!pin)setHv(null);}} onClick={()=>onSel(i)}>{i!==lastI&&<i aria-hidden="true"></i>}</button>);})}
          </div>
          {h!=null&&(()=>{const[nm,img]=LH_TIERS[h],c=cnt[h],sh=shareOf(row[h],last),bw=t.burnIn&&t.burnIn[basis]===h;return(
            <div className="lh-bm-tip" ref={tipRef} style={{'--g':LH_BEAM_C[h][3]}} aria-hidden="true">
              <img src={lhSea(img)} alt=""/><div><div className="n">{nm.toUpperCase()} {'\u00B7'} {lhFmt(c)} WALLET{c===1?'':'S'}</div>
                <div className="v">{sh!=null?`${sh}%`:'\u2014'}<small>{fmtAbbr(row[h])} {tok}</small></div>
                {bw&&<div className="bn">{c===1?'the Burn address':'incl. the Burn address'}</div>}</div></div>);})()}
        </div>);
    };
    /* the share card — Wide 1200 × 675 (screenshot-only, like the other v2 cards). v2 (2026-10-24, Shaka: "update the card to have the
       new look"): the lit coin, the ownership beam, the eight leagues with the big creatures, count + change on one line, the tokens
       held, league-coloured sparklines. */
    const LhShareCard=({tok,t,per,basis,i0,shareOf})=>{const isU=tok==='UFO',rows=t[basis],last=rows.length-1,pd=LH_PERS.find(p=>p[0]===per);
      const held=t.held&&t.held[basis],total=rows[last].reduce((s,v)=>s+v,0);
      return(
        <div className={`lh-card v2${isU?' u':''}`}><div className="sky"></div><div className="veil"></div><div className="in">
          <div className="tt"><div className="cw"><LgCoin token={tok}/></div><div className="tx"><div className="h"><span className="t">{tok}</span> LEAGUE HISTORY</div>
            <div className="pd">{(i0===0&&pd[1]!=null&&pd[1]>last)||pd[0]==='ALL'?'Since launch':`Last ${pd[2]}`} {'\u00B7'} {lhDate(lhDay(t.day0,i0),true)} {'\u2192'} {lhDate(lhDay(t.day0,last),true)}</div></div>
            <div className="tot"><b>{lhFmt(total)}</b><span>holder wallets</span></div></div>
          {held&&<div className="bmw"><LhBeam t={t} tok={tok} basis={basis} last={last} onSel={()=>{}} shareOf={shareOf}/></div>}
          <div className="g">{LH_TIERS.map(([n,img],i)=>{const a=rows[i0][i],b=rows[last][i],sh=held?shareOf(held[last][i],last):null;return(
            <div className="c" key={n}><div className="r1"><img src={lhSea(img)} alt=""/><div className="nm">{n.toUpperCase()}</div></div>
              <div className="vr"><span className="ft">{lhFmt(b)}</span><span className="ch"><LhChange a={a} b={b}/></span></div>
              {held&&<div className="hd">hold <b>{fmtAbbr(held[last][i])}</b>{sh!=null&&<> {'\u00B7'} {sh}%</>}</div>}
              <LhSpark vals={rows.slice(i0).map(r=>r[i])} w={240} h={40} col={LH_BEAM_C[i][1]}/></div>);})}</div></div>
          <div className="bt"><span>People only + the burn wallet {'\u00B7'} {basis==='circ'?'circulating':'starting'} supply {'\u00B7'} rebuilt from the chain</span><b>PTGC-UFO.COM</b></div>
        </div>);
    };
    const LeagueHistoryModal=({token,onClose})=>{
      const[tok,setTok]=useState(token==='UFO'?'UFO':'PTGC');
      const[per,setPer]=useState('1Y');   // every opening starts on 1Y (Shaka, 2026-10-24) — the pick is not remembered
      const[basis,setBasis]=useState('start');
      const[sel,setSel]=useState(2);   // Shark — the one he asked about
      const[file,setFile]=useState(undefined);   // undefined = loading, null = failed
      const[share,setShare]=useState(false);
      const[mode,setMode]=useState('b');   // the big chart: 'b' = both (the overlay, default), 'w' = wallets, 't' = tokens held (2026-10-24, Shaka: "how many tokens do those 107 wallets hold" → "an overlay line chart")
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
      const setP=k=>setPer(k);
      const total=rows?rows[last].reduce((s,v)=>s+v,0):null;
      /* tokens held per league (schema 3): `held[basis]` per day; the share is of the basis supply THAT day (circulating = starting − the
         burn wallet's balance, the `burned` line, which is per ARCHIVE day — offset by the days trimmed before the first holder) */
      const held=t&&t.held&&t.held[basis];
      const off=t&&t.archiveDay0?Math.round((Date.parse(t.day0)-Date.parse(t.archiveDay0))/864e5):0;
      const supAt=k=>!t?null:basis==='circ'?(Array.isArray(t.burned)&&t.burned[off+k]!=null?t.supply-t.burned[off+k]:null):t.supply;
      const shareOf=(v,k)=>{const sp=supAt(k);if(!(sp>0)||v==null)return null;if(v===0)return'0';const p=v/sp*100;return p>=10?p.toFixed(1):p>=0.1?p.toFixed(2):p>=0.001?p.toFixed(3):'<0.001';};
      const tm=mode==='t'&&!!held,bm=mode==='b'&&!!held;
      const per1=(v,c)=>c>0&&v>0?fmtAbbr(v/c):null;   // tokens per wallet, for the hover
      return(
        <Modal onClose={onClose} label={`${tok} league history`} className="z-50 overflow-y-auto overscroll-contain bg-black/85 sm:p-4">
          <div className={`lh-win${isU?' u':''}`} onClick={e=>e.stopPropagation()}>
            <div className="lh-hd"><div className="sky" aria-hidden="true"></div><div className="veil" aria-hidden="true"></div>
              {rows&&<button type="button" className="lh-cam" onClick={()=>setShare(true)} aria-label="Share the league history as an image">{'\u{1F4F7}'}<span>SHARE</span></button>}
              <button type="button" className="lh-x" onClick={onClose} aria-label="Close">{'×'}</button>
              <div className="lh-hc"><div className="lh-coinw"><LgCoin token={tok}/></div>
                <h2><span className="t">{tok}</span><span className="w">LEAGUE HISTORY</span></h2>
                <div className="lh-sub">How many of each sea creature hold {tok} {'—'} every day since {t?lhDate(lhDay(t.day0,0),true):'launch'}</div>
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
                <LhBeam t={t} tok={tok} basis={basis} last={last} onSel={setSel} shareOf={shareOf}/>
                <div className="lh-cards">{LH_TIERS.map(([n,img,th],i)=>{const a=rows[i0][i],b=rows[last][i];return(
                  <button type="button" key={n} className="lh-cd" style={{'--cc':LH_BEAM_C[i][1],'--cg':LH_BEAM_C[i][3]}} aria-pressed={sel===i} onClick={()=>setSel(i)} aria-label={`${n}: ${lhFmt(b)} now, ${b===a?'no change':`${b>a?'up':'down'} ${lhFmt(Math.abs(b-a))}`} over ${pd[2]} — show the chart`}>
                    <div className="top"><span className="ic"><img src={lhSea(img)} alt=""/></span><div><div className="nm">{n}</div><div className="th">{th?`≥ ${th} of supply`:'below Shrimp'}</div>{t.burnIn&&t.burnIn[basis]===i&&<div className="bwl">{b===1?'The Burn address':'incl. the Burn address'}</div>}</div></div>
                    <div className="vr"><div className="v">{lhFmt(b)}</div><div className="ch"><LhChange a={a} b={b}/></div></div>
                    {held&&<div className="hd2">hold <b>{fmtAbbr(held[last][i])}</b> {'\u00B7'} {shareOf(held[last][i],last)}%</div>}
                    {held&&<div className="av">{b>1?<>~<b>{per1(held[last][i],b)}</b> per {n.toLowerCase()}</>:b===1?'one wallet':'no wallets'}</div>}
                    <div className="jl">{fl?<><b className="lh-up">+{lhFmt(fl[0][i])}</b> joined {'·'} <b className="lh-dn">{'−'}{lhFmt(fl[1][i])}</b> left</>:' '}</div>
                    {(()=>{const v=rows.slice(i0).map(r=>r[i]);return<div className="hl">High <b>{lhFmt(Math.max(...v))}</b> {'\u00B7'} Low <b>{lhFmt(Math.min(...v))}</b></div>;})()}
                    <LhSpark vals={rows.slice(i0).map(r=>r[i])} col={LH_BEAM_C[i][1]}/>   {/* the league's colour (the beam's) */}
                  </button>);})}</div>
                {(()=>{const[n,img]=LH_TIERS[sel],a=rows[i0][sel],b=rows[last][sel];return(
                  <div className="lh-big">
                    <div className="lh-bh"><div className="l"><img src={lhSea(img)} alt=""/><div><h3>{n.toUpperCase()}S {tm?'\u2014 TOKENS HELD':bm?'\u2014 WALLETS + TOKENS HELD':'OVER TIME'}</h3>
                      {tm?<div className="s"><b>{fmtAbbr(held[i0][sel])}</b> {'→'} <b>{fmtAbbr(held[last][sel])}</b> <LhChange a={held[i0][sel]} b={held[last][sel]} f={fmtAbbr}/> <span style={{color:'rgba(255,255,255,.45)'}}>{'·'} {span}</span></div>
                        :<div className="s"><b>{lhFmt(a)}</b> {'→'} <b>{lhFmt(b)}</b> <LhChange a={a} b={b}/> <span style={{color:'rgba(255,255,255,.45)'}}>{'·'} {span}</span></div>}
                      {(tm||bm)&&<div className="s s3"><b>{lhFmt(total)}</b> holder wallets {'\u00B7'} people only</div>}
                      {bm&&<div className="s s2">hold <b>{fmtAbbr(held[i0][sel])}</b> {'→'} <b>{fmtAbbr(held[last][sel])}</b> <LhChange a={held[i0][sel]} b={held[last][sel]} f={fmtAbbr}/></div>}</div></div>
                      <div className="r"><div className="lh-pill"><div className="k">JOINED</div><div className="n lh-up">{fl?'+'+lhFmt(fl[0][sel]):'—'}</div></div>
                        <div className="lh-pill"><div className="k">LEFT</div><div className="n lh-dn">{fl?'−'+lhFmt(fl[1][sel]):'—'}</div></div>
                        {(()=>{const nt=fl?fl[0][sel]-fl[1][sel]:b-a;return<div className="lh-pill net"><div className="k">NET</div><div className={`n ${nt>0?'lh-up':nt<0?'lh-dn':''}`}>{nt>0?'+':nt<0?'\u2212':''}{lhFmt(Math.abs(nt))}</div></div>;})()}
                        {tm||bm?<div className="lh-pill"><div className="k"><span className="lg">SHARE OF SUPPLY</span><span className="sm">SHARE</span></div><div className="n">{shareOf(held[last][sel],last)}%</div></div>
                          :<div className="lh-pill" title="People only: pools and contracts are not counted (the dashboard's HOLDERS counts every address)"><div className="k">HOLDER WALLETS</div><div className="n">{lhFmt(total)}</div></div>}</div></div>
                    {held&&<div className="lh-mrow"><div className="lh-tg lh-mode" role="group" aria-label="Chart"><button type="button" aria-pressed={bm} onClick={()=>setMode('b')}>BOTH</button><button type="button" aria-pressed={!tm&&!bm} onClick={()=>setMode('w')}>WALLETS</button><button type="button" aria-pressed={tm} onClick={()=>setMode('t')}>TOKENS HELD</button></div>
                      {bm&&<div className="lh-lg" aria-hidden="true"><span><i style={{background:col,boxShadow:`0 0 9px ${col}`}}></i>Wallets <em>(left)</em></span><span><i className="a"></i>Tokens held <em>(right)</em></span></div>}</div>}
                    {(()=>{const nm=n.toLowerCase(),un=c=>`${lhFmt(c)} ${c===1?nm:nm+'s'}`;   // lh2: what the readout row says for day q of the slice
                      const hl=q=>{const v=held[i0+q][sel],sh=shareOf(v,i0+q);return`${sh!=null?`${sh}% of supply`:''}`;};
                      return tm?<LhChart key="t" vals={held.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} f={fmtAbbr} what="Tokens held" tl={`TOKENS HELD (${lhUnit(Math.max(...held.slice(i0).map(r=>r[sel])))})`}
                          rd={q=>[`${fmtAbbr(held[i0+q][sel])} held`,hl(q)||null]}/>
                        :bm?<LhChart key="b" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} tl="WALLETS" tr={`TOKENS HELD (${lhUnit(Math.max(...held.slice(i0).map(r=>r[sel])))})`} what={`${n}s (wallets) and the tokens they hold`}
                          v2={held.slice(i0).map(r=>r[sel])} rd={q=>{const v=held[i0+q][sel],c=rows[i0+q][sel],sh=shareOf(v,i0+q),e=per1(v,c);return[un(c),`hold ${fmtAbbr(v)}${sh!=null?` (${sh}%)`:''}${e&&c>1?` \u00B7 ~${e} each`:''}`];}}/>
                        :<LhChart key="w" vals={rows.slice(i0).map(r=>r[sel])} day0={t.day0} i0={i0} col={col} tl="WALLETS" rd={q=>[un(rows[i0+q][sel]),null]}/>;})()}
                  </div>);})()}
                <div className="lh-foot"><b>People only, plus the burn wallet</b> {'—'} wallets holding {tok}; pools, contracts, the token contracts and the DAO{isU?' and UFO OA':''} wallets are left out; the burn wallet counts in the league its balance puts it in (the same count as the Token Allocation strip). Leagues are a share of the <b>{basis==='circ'?'circulating supply that day (starting − burned)':'starting supply'}</b>. One point per UTC day, rebuilt from the chain {'·'} <span className={ageDays>2?'old':undefined}>history to the close of {lhDate(lhDay(t.day0,last),true)} (UTC)</span>. <b>Hold</b> = the tokens that league{'\u2019'}s wallets hold that day, and their share of the {basis==='circ'?'circulating':'starting'} supply. <b>Joined / left</b> = wallets that moved into or out of a league over the period (by buying, selling, or {basis==='circ'?'a burn moving the line':'moving tokens'}); joined {'−'} left = the change. The history runs to yesterday{'’'}s close (UTC); the creature strip on the dashboard is updated every hour, so a count there can differ by one or two.</div>
              </>}
            </div>
          </div>
          {share&&rows&&<ShareCardModal onClose={()=>setShare(false)} width={1200} height={675} zIndex={60} screenshot label={`${tok} league history share card`} filename={`${tok.toLowerCase()}-leagues-${per.toLowerCase()}-${new Date().toISOString().slice(0,10)}.png`}>
            <LhShareCard tok={tok} t={t} per={per} basis={basis} i0={i0} shareOf={shareOf}/>
          </ShareCardModal>}
        </Modal>);
    };
    /* the faint bottom-right dot while !LEAGUE_HISTORY_LIVE (the VsDot / NhDot pattern) */
    const LhDot=({token,onOpen})=>(
      <button type="button" onClick={onOpen} aria-label="League history (preview)" title="" className="fixed bottom-1 right-1 z-30 w-7 h-7 flex items-center justify-center bg-transparent border-0 p-0">
        <span aria-hidden="true" className="block w-1.5 h-1.5 rounded-full" style={{background:(TOKENS[token]||TOKENS.PTGC).colorHex,opacity:0.16}}></span>
      </button>
    );
