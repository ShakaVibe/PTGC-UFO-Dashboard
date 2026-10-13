    /* ===== Portfolio v2 — VALUE HISTORY (2026-10-13, Shaka's option C: "real balances read from the chain") =====
       For every counted wallet, the PTGC and UFO balanceOf AT PAST BLOCKS (archive eth_call, batched), times that moment's
       price (data/charts-data.json daily ≤ 365 d, data/charts-intraday.json hourly ≤ 14 d — the Charts page's prebuilt files),
       summed. Sells show as drops, buys as rises. PTGC staked / locked stay in balanceOf (the staking contract never moves
       them), so the PTGC line is the whole bag. UFO before its contract existed reads 0x → 0.
       Past points never change, so every balance is cached per wallet + token + timestamp in localStorage (PFH_LS); a reload
       only reads what is new. Points are aligned to UTC (6 h steps on 7D, days on 30D / 90D, 4 days on 1Y) so they repeat.
       A point with any wallet unread is a GAP, never a guess. Only the archive nodes (rpc.pulsechain.com, g4mm4) are used —
       publicnode answers "missing trie node" for old blocks (tested 2026-10-13). */
    const PFH_RPC=['https://rpc.pulsechain.com','https://rpc-pulsechain.g4mm4.io'];
    const PFH_LS='grays_pf_hist_v1';
    const PFH_TOK={PTGC:'0x94534EeEe131840b1c0F61847c572228bdfDDE93',UFO:'0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6'};
    const PFH_RAW='https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/';
    const PFH_H=3600e3,PFH_D=86400e3;
    const PFH_PERIODS={'7D':{step:6*PFH_H,n:28,unit:6*PFH_H},'30D':{step:PFH_D,n:30,unit:PFH_D},'90D':{step:PFH_D,n:90,unit:PFH_D},'1Y':{step:4*PFH_D,n:92,unit:PFH_D}};
    let pfhCache=null;   // {v:{'addr|TOK':{ts:bal}}}
    const pfhLoad=()=>{if(pfhCache)return pfhCache;try{const s=localStorage.getItem(PFH_LS);pfhCache=s?JSON.parse(s):{v:{}};if(!pfhCache.v)pfhCache={v:{}};}catch(e){pfhCache={v:{}};}return pfhCache;};
    let pfhSaveT=null;
    const pfhSave=()=>{clearTimeout(pfhSaveT);pfhSaveT=setTimeout(()=>{try{localStorage.setItem(PFH_LS,JSON.stringify(pfhCache));}catch(e){/* full: drop the oldest wallet entries */try{const ks=Object.keys(pfhCache.v);ks.slice(0,Math.ceil(ks.length/3)).forEach(k=>delete pfhCache.v[k]);localStorage.setItem(PFH_LS,JSON.stringify(pfhCache));}catch(e2){}}},800);};
    let pfhEp=0;
    const pfhRpc=async(body,tries=3)=>{
      for(let t=0;t<tries;t++){
        const ep=PFH_RPC[(pfhEp+t)%PFH_RPC.length];
        try{const ac=new AbortController();const to=setTimeout(()=>ac.abort(),20000);
          const r=await fetch(ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:ac.signal});clearTimeout(to);
          if(!r.ok)throw new Error('HTTP '+r.status);const j=await r.json();
          if(Array.isArray(body)&&!Array.isArray(j))throw new Error('no batch');
          pfhEp=(pfhEp+t)%PFH_RPC.length;return j;
        }catch(e){if(t===tries-1)throw e;}
      }
    };
    /* timestamp → block: anchors at the head and ~7 / 30 / 90 / 180 / 365 / 420 days back, linear between them */
    let pfhAnchors=null,pfhAnchorsAt=0;
    const pfhGetAnchors=async()=>{
      if(pfhAnchors&&Date.now()-pfhAnchorsAt<10*60e3)return pfhAnchors;
      const head=await pfhRpc({jsonrpc:'2.0',id:1,method:'eth_getBlockByNumber',params:['latest',false]});
      const hn=parseInt(head.result.number,16),ht=parseInt(head.result.timestamp,16)*1000;
      const nums=[7,30,90,180,365,420].map(d=>Math.max(1,hn-Math.round(d*PFH_D/10300)));
      const res=await pfhRpc(nums.map((n,i)=>({jsonrpc:'2.0',id:i,method:'eth_getBlockByNumber',params:['0x'+n.toString(16),false]})));
      const a=[[hn,ht]];res.forEach(r=>{if(r&&r.result)a.push([parseInt(r.result.number,16),parseInt(r.result.timestamp,16)*1000]);});
      a.sort((x,y)=>x[1]-y[1]);pfhAnchors=a;pfhAnchorsAt=Date.now();return a;
    };
    const pfhBlockAt=(a,ts)=>{
      if(ts>=a[a.length-1][1])return a[a.length-1][0];
      let i=a.findIndex(p=>p[1]>=ts);if(i<=0)i=1;
      const[b0,t0]=a[i-1],[b1,t1]=a[i];
      return Math.max(1,Math.round(b0+(b1-b0)*(ts-t0)/Math.max(1,t1-t0)));
    };
    /* round 15 (Shaka: "there was an old UFO contract and a new one … hopefully it includes the old one"): reflections earned on
       the OLD UFO contract up to the migration snapshot (block 26,963,880, 2026-07-06). The new-contract scan counts the migration
       airdrop as tokens RECEIVED, and that airdrop was each wallet's old balance — old reflections included — so without this
       they were principal. Prebuilt once by tools/ufo-v1-earned.py (the old contract is frozen; the method and every on-chain
       check are in that file); sharded by the address's first hex digit so a visit loads only the 1–16 small files it needs.
       Returns {state:'loading'|'ok'|'failed', of(addr) → whole tokens (0 if the wallet earned none there)}. */
    const pfV1Shard={};
    const usePfUfoV1=addrs=>{
      const key=addrs.map(a=>a.toLowerCase()).sort().join(',');
      const[st,setSt]=useState({state:'loading',m:{}});
      useEffect(()=>{let live=true;const cs=[...new Set(addrs.map(a=>a.toLowerCase()[2]))];
        if(!cs.length){setSt({state:'ok',m:{}});return;}
        Promise.all(cs.map(c=>pfV1Shard[c]||(pfV1Shard[c]=fetch(PFH_RAW+'ufo-v1-earned/'+c+'.json').then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).catch(e=>{delete pfV1Shard[c];throw e;}))))
          .then(ms=>{if(live)setSt({state:'ok',m:Object.assign({},...ms)});}).catch(()=>{if(live)setSt({state:'failed',m:{}});});
        return()=>{live=false;};},[key]);
      return{state:st.state,of:a=>st.m[a.toLowerCase().slice(2)]||0};
    };
    /* prices: the Charts page's prebuilt files (refetched every 30 min) */
    let pfhPx=null,pfhPxAt=0;
    const pfhPrices=async()=>{
      if(pfhPx&&Date.now()-pfhPxAt<30*60e3)return pfhPx;
      const g=async f=>{try{const r=await fetch(PFH_RAW+f,{cache:'no-cache'});return r.ok?await r.json():null;}catch(e){return null;}};
      const[d,h]=await Promise.all([g('charts-data.json'),g('charts-intraday.json')]);
      const ser=(o,k,tier)=>{try{const s=tier?o.tokens[k][tier].series:o.tokens[k].series;return(s||[]).filter(p=>p&&p[1]>0).sort((x,y)=>x[0]-y[0]);}catch(e){return[];}};
      pfhPx={daily:{PTGC:ser(d,'PTGC'),UFO:ser(d,'UFO')},hourly:{PTGC:ser(h,'PTGC','hourly'),UFO:ser(h,'UFO','hourly')}};pfhPxAt=Date.now();
      return pfhPx;
    };
    const pfhNear=(s,ts,maxGap)=>{if(!s||!s.length||ts<s[0][0]-maxGap)return null;let lo=0,hi=s.length-1;while(lo<hi){const m=(lo+hi+1)>>1;if(s[m][0]<=ts)lo=m;else hi=m-1;}
      let best=s[lo];if(lo+1<s.length&&Math.abs(s[lo+1][0]-ts)<Math.abs(best[0]-ts))best=s[lo+1];return Math.abs(best[0]-ts)<=maxGap?best[1]:null;};
    const pfhPriceAt=(px,tok,ts)=>{const h=pfhNear(px.hourly[tok],ts,3*PFH_H);return h!=null?h:pfhNear(px.daily[tok],ts,2*PFH_D);};
    /* read the balances not in the cache; in-flight reads are shared between the chart and the tiles */
    const pfhInflight=new Map();
    const pfhRead=async(jobs,onProgress)=>{
      const c=pfhLoad();const need=[];const waits=[];
      jobs.forEach(j=>{const k=j.addr+'|'+j.tok;const hit=c.v[k]&&c.v[k][j.ts]!=null;if(hit)return;const ik=k+'|'+j.ts;if(pfhInflight.has(ik)){waits.push(pfhInflight.get(ik));return;}need.push(j);});
      let done=0;const total=need.length;onProgress&&onProgress(total?0:1);
      const B=80,batches=[];for(let i=0;i<need.length;i+=B)batches.push(need.slice(i,i+B));
      const run=async batch=>{
        let res=null;try{res=await pfhRpc(batch.map((j,i)=>({jsonrpc:'2.0',id:i,method:'eth_call',params:[{to:PFH_TOK[j.tok],data:'0x70a08231'+j.addr.slice(2).padStart(64,'0')},'0x'+j.block.toString(16)]})));}catch(e){res=null;}
        const byId={};(res||[]).forEach(r=>{if(r)byId[r.id]=r;});
        batch.forEach((j,i)=>{const r=byId[i];if(!r||r.error||r.result==null)return;const k=j.addr+'|'+j.tok;let v=0;try{v=r.result==='0x'?0:Number(BigInt(r.result))/1e18;}catch(e){return;}(c.v[k]=c.v[k]||{})[j.ts]=Math.round(v*100)/100;});
        done+=batch.length;onProgress&&onProgress(total?done/total:1);
      };
      const ps=[];let q=0;const worker=async()=>{while(q<batches.length){const b=batches[q++];await run(b);}};
      const p=Promise.all([worker(),worker()]).then(()=>pfhSave());
      need.forEach(j=>pfhInflight.set(j.addr+'|'+j.tok+'|'+j.ts,p));
      p.finally(()=>need.forEach(j=>pfhInflight.delete(j.addr+'|'+j.tok+'|'+j.ts)));
      await Promise.all([p,...waits]);
    };
    const pfhTimes=period=>{const P=PFH_PERIODS[period];const now=Date.now();const last=Math.floor(now/P.unit)*P.unit;const out=[];for(let k=P.n-1;k>=0;k--)out.push(last-k*P.step);return out.filter(t=>t<now-60e3);};
    /* the series for a set of wallets + period: [{t,p,u,v}] (null v = a gap), plus the live "now" point added by the caller */
    const usePfSeries=(addrs,period,enabled=true)=>{
      const[st,setSt]=useState({state:'idle',pts:[],progress:0});
      const key=addrs.slice().sort().join(',')+'|'+period;
      const[nonce,setNonce]=useState(0);
      useEffect(()=>{
        if(!enabled||!addrs.length){setSt({state:addrs.length?'idle':'empty',pts:[],progress:0});return;}
        let live=true;
        (async()=>{
          setSt(s=>({...s,state:'loading',progress:0}));
          try{
            const[a,px]=await Promise.all([pfhGetAnchors(),pfhPrices()]);
            const times=pfhTimes(period);
            const jobs=[];times.forEach(ts=>{const block=pfhBlockAt(a,ts);addrs.forEach(addr=>['PTGC','UFO'].forEach(tok=>jobs.push({addr,tok,ts,block})));});
            await pfhRead(jobs,pr=>{if(live)setSt(s=>({...s,progress:pr}));});
            const c=pfhLoad();
            const pts=times.map(ts=>{
              let p=0,u=0,ok=true;
              addrs.forEach(addr=>{const bp=(c.v[addr+'|PTGC']||{})[ts],bu=(c.v[addr+'|UFO']||{})[ts];if(bp==null||bu==null){ok=false;return;}p+=bp;u+=bu;});
              if(!ok)return{t:ts,v:null};
              const pp=p>0?pfhPriceAt(px,'PTGC',ts):0,pu=u>0?pfhPriceAt(px,'UFO',ts):0;
              if(pp==null||pu==null)return{t:ts,v:null};
              return{t:ts,p:p*pp,u:u*pu,v:p*pp+u*pu,bp:p,bu:u};
            });
            if(!live)return;
            const gaps=pts.filter(x=>x.v==null).length;
            setSt({state:gaps===pts.length?'failed':'ok',pts,progress:1,gaps});
          }catch(e){if(live)setSt({state:'failed',pts:[],progress:0});}
        })();
        return()=>{live=false;};
      },[key,enabled,nonce]);
      return{...st,retry:()=>setNonce(n=>n+1)};
    };
    /* the real 24 h change: every counted wallet's balances exactly 24 h ago × the price then, vs now */
    const usePf24h=addrs=>{
      const[v,setV]=useState(null);const key=addrs.slice().sort().join(',');
      useEffect(()=>{if(!addrs.length){setV(null);return;}let live=true;(async()=>{try{
        const[a,px]=await Promise.all([pfhGetAnchors(),pfhPrices()]);
        const ts=Math.floor((Date.now()-PFH_D)/60e3)*60e3;const block=pfhBlockAt(a,ts);
        const res=await pfhRpc(addrs.flatMap((addr,i)=>['PTGC','UFO'].map((tok,k)=>({jsonrpc:'2.0',id:i*2+k,method:'eth_call',params:[{to:PFH_TOK[tok],data:'0x70a08231'+addr.slice(2).padStart(64,'0')},'0x'+block.toString(16)]}))));
        const by={};(res||[]).forEach(r=>{if(r)by[r.id]=r;});let p=0,u=0;
        for(let i=0;i<addrs.length;i++)for(let k=0;k<2;k++){const r=by[i*2+k];if(!r||r.error||r.result==null)throw new Error('read');const x=r.result==='0x'?0:Number(BigInt(r.result))/1e18;if(k===0)p+=x;else u+=x;}
        const pp=p>0?pfhPriceAt(px,'PTGC',ts):0,pu=u>0?pfhPriceAt(px,'UFO',ts):0;if(pp==null||pu==null)throw new Error('price');
        if(live)setV({p:p*pp,u:u*pu,v:p*pp+u*pu});
      }catch(e){if(live)setV(null);}})();return()=>{live=false;};},[key]);
      return v;
    };
    const pfhMoney=v=>v==null?'—':v>=1e9?'$'+(v/1e9).toFixed(2)+'B':v>=1e6?'$'+(v/1e6).toFixed(2)+'M':v>=1e4?'$'+Math.round(v/1e3)+'K':v>=1e3?'$'+(v/1e3).toFixed(1)+'K':'$'+Math.round(v);
    const pfhDate=(t,withTime)=>{const d=new Date(t);const s=d.toLocaleDateString('en-US',{month:'short',day:'numeric'});return withTime?s+' '+d.toLocaleTimeString('en-US',{hour:'numeric'}):s;};
    const PfSpark=({vals,col})=>{
      const v=(vals||[]).filter(x=>x!=null);if(v.length<2)return <svg className="pf2-spk" viewBox="0 0 96 46" aria-hidden="true"></svg>;
      const mn=Math.min(...v),mx=Math.max(...v),W=96,H=46;const pts=v.map((y,i)=>[i/(v.length-1)*W,H-4-(mx>mn?(y-mn)/(mx-mn):.5)*(H-10)]);
      const d=pts.map((p,i)=>(i?'L':'M')+p[0].toFixed(1)+' '+p[1].toFixed(1)).join('');const id='pfs'+col.slice(1);
      return(<svg className="pf2-spk" viewBox={`0 0 ${W} ${H}`} aria-hidden="true"><defs><linearGradient id={id} x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor={col} stopOpacity=".42"/><stop offset="1" stopColor={col} stopOpacity="0"/></linearGradient></defs><path d={d+`L${W} ${H}L0 ${H}Z`} fill={`url(#${id})`}/><path d={d} fill="none" stroke={col} strokeWidth="1.6" strokeLinejoin="round" style={{filter:`drop-shadow(0 0 3px ${col})`}}/></svg>);
    };
    /* the chart: one series (the total), area + 2 px line, recessive grid, crosshair + tooltip on hover / touch */
    const PfHistChart=({pts,period,txs})=>{
      const ref=React.useRef(null);const[hov,setHov]=useState(null);
      const vals=pts.filter(p=>p.v!=null);
      if(vals.length<2)return <div className="pf2-hwait">Not enough points yet.</div>;
      const t0=pts[0].t,t1=pts[pts.length-1].t;const mx=Math.max(...vals.map(p=>p.v));
      const nice=(()=>{const raw=mx*1.12||1;const e=Math.pow(10,Math.floor(Math.log10(raw)));const m=raw/e;return(m<=1.5?1.5:m<=2?2:m<=2.5?2.5:m<=3?3:m<=4?4:m<=5?5:m<=6?6:m<=8?8:10)*e;})();
      const X=t=>(t-t0)/Math.max(1,t1-t0)*100,Y=v=>100-v/nice*100;
      let d='',area='',seg=[];const segs=[];pts.forEach(p=>{if(p.v==null){if(seg.length)segs.push(seg);seg=[];}else seg.push(p);});if(seg.length)segs.push(seg);
      segs.forEach(s=>{const l=s.map((p,i)=>(i?'L':'M')+X(p.t).toFixed(3)+' '+Y(p.v).toFixed(3)).join('');d+=l;area+=l+`L${X(s[s.length-1].t).toFixed(3)} 100L${X(s[0].t).toFixed(3)} 100Z`;});
      const ticks=[0,.25,.5,.75,1].map(f=>f*nice);
      const nx=period==='7D'?7:period==='30D'?6:period==='90D'?6:6;const xl=Array.from({length:nx+1},(_,i)=>t0+(t1-t0)*i/nx);
      const move=e=>{const r=ref.current.getBoundingClientRect();const cx=(e.touches?e.touches[0].clientX:e.clientX)-r.left;const t=t0+(cx/r.width)*(t1-t0);let best=null;vals.forEach(p=>{if(!best||Math.abs(p.t-t)<Math.abs(best.t-t))best=p;});setHov(best);};
      const last=vals[vals.length-1];
      /* buy / sell markers.
         round 14 (Shaka: "a bunch of sells… yet no red dots"): the dots now come from the REAL trades in Recent Transactions —
         every Sell / Send / Add LP is a red dot, every Buy / Receive / Remove LP a green one, however small (the old balance-
         change dots hid anything under 1 % of the bag, i.e. every normal-sized sell). Each trade lands on the first chart point
         at or after it (where the balance already shows it); a step with both buys and sells gets both dots. Claims and moves
         between your own wallets are not trades and get no dot.
         Older than the trade list reaches (PulseScan's latest 50 per wallet and token), the round-8 dots still fill in:
         where the token COUNT moved by more than 1 % between two points. */
      /* round 15 (Shaka): claims get their own BLUE dot and liquidity adds / removes a YELLOW one (the table's colours) */
      const ev=[];const TIN={Buy:1,Receive:1},TOUT={Sell:1,Send:1},TCL={Claim:1},TLP={'Add LP':1,'Remove LP':1};
      const KINDS=[['in',TIN],['out',TOUT],['cl',TCL],['lp',TLP]];
      const since=txs?txs.since:Infinity;
      if(txs){const by=new Map();txs.rows.forEach(r=>{if(!KINDS.some(([,m])=>m[r.type]))return;if(r.t<=vals[0].t||r.t<since)return;
          const p=vals.find(q=>q.t>=r.t)||vals[vals.length-1];const e=by.get(p.t)||{p,tx:[]};e.tx.push(r);by.set(p.t,e);});
        by.forEach(e=>{const ks=KINDS.filter(([,m])=>e.tx.some(r=>m[r.type])).map(([k])=>k);
          ks.forEach((k,j)=>ev.push({p:e.p,k,off:(j-(ks.length-1)/2)*12,tx:e.tx}));});}
      for(let i=1;i<vals.length;i++){const a=vals[i-1],b=vals[i];if(b.t>=since)break;const ch=[];[['PTGC','bp'],['UFO','bu']].forEach(([k,f])=>{if(a[f]==null||b[f]==null)return;const d=b[f]-a[f];if(Math.abs(d)>Math.max(a[f],b[f])*0.01&&Math.abs(d)>1)ch.push({k,d});});if(ch.length)ev.push({p:b,ch,off:0,up:ch.reduce((x,c)=>x+c.d*(c.k==='PTGC'?b.p/(b.bp||1):b.u/(b.bu||1)),0)>=0});}
      const evAt=t=>ev.find(e=>e.p.t===t);
      const txLine=r=>{const k=TOUT[r.type]?'out':TCL[r.type]?'cl':TLP[r.type]?'lp':'in';const g={out:'\u25BC ',in:'\u25B2 ',cl:'\u2B07 ',lp:r.type==='Add LP'?'\u2295 ':'\u2296 '}[k];
        return <span key={r.id} className={k}>{g}{r.type} {pfAbbr(Math.abs(r.amt))} {r.tok}{r.usd!=null&&<em> {'\u00B7'} {pfhMoney(r.usd)}</em>}</span>;};
      return(
        <div className="pf2-hc">
          <div className="pf2-hy" aria-hidden="true">{ticks.slice().reverse().map((v,i)=><span key={i}>{pfhMoney(v)}</span>)}</div>
          <div className="pf2-hp" ref={ref} onMouseMove={move} onMouseLeave={()=>setHov(null)} onTouchStart={move} onTouchMove={move} onTouchEnd={()=>setHov(null)} role="img" aria-label={`Portfolio value from ${pfhDate(t0)} to now: ${pfhMoney(vals[0].v)} to ${pfhMoney(last.v)}`}>
            {ticks.map((v,i)=><i key={i} className="g" style={{top:Y(v)+'%'}}></i>)}
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="pfhA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#5CE13A" stopOpacity=".5"/><stop offset="1" stopColor="#1F6B12" stopOpacity=".06"/></linearGradient></defs>
              <path d={area} fill="url(#pfhA)"/><path d={d} fill="none" stroke="#7CFC00" strokeWidth="2" vectorEffect="non-scaling-stroke" strokeLinejoin="round"/></svg>
            {ev.map((e,i)=><b key={'e'+i} className={`ev ${e.k||(e.up?'in':'out')}`} style={{left:`calc(${X(e.p.t)}% + ${e.off}px)`,top:Y(e.p.v)+'%'}}></b>)}
            <b className="dot" style={{left:X(last.t)+'%',top:Y(last.v)+'%'}}></b>
            {hov&&<><i className="xh" style={{left:X(hov.t)+'%'}}></i><b className="dot h" style={{left:X(hov.t)+'%',top:Y(hov.v)+'%'}}></b>
              <div className={`pf2-htip${X(hov.t)>62?' l':''}`} style={{left:X(hov.t)+'%'}}><div className="d">{hov.now?'Now':pfhDate(hov.t,period==='7D')}</div><div className="v">{fmtDollar(hov.v)}</div><div className="s"><span className="p">PTGC {fmtDollar(hov.p,0)}</span><span className="u">UFO {fmtDollar(hov.u,0)}</span></div>{(()=>{const e=evAt(hov.t);if(!e)return null;if(e.tx){const l=e.tx.slice().sort((a,b)=>b.t-a.t);return <div className="ev">{l.slice(0,4).map(txLine)}{l.length>4&&<small>+{l.length-4} more {'\u2014'} see Recent Transactions</small>}<small>{l.length===1?'transaction':'transactions'} since the point before</small></div>;}return <div className="ev">{e.ch.map(c=><span key={c.k} className={c.d>0?'in':'out'}>{c.d>0?'\u25B2 +':'\u25BC \u2212'}{pfAbbr(Math.abs(c.d))} {c.k}</span>)}<small>since the point before</small></div>;})()}</div></>}
          </div>
          {ev.length>0&&<div className="pf2-hlg"><span><b className="in"></b>bought or received</span><span><b className="out"></b>sold or sent</span><span><b className="cl"></b>rewards claimed</span><span><b className="lp"></b>liquidity added / removed</span>{txs&&since>vals[0].t&&<span className="o">older dots: token count moved over 1 %</span>}</div>}
          <div className="pf2-hx" aria-hidden="true">{xl.map((t,i)=><span key={i} style={{left:(i/nx*100)+'%'}}>{i===nx?'Now':pfhDate(t)}</span>)}</div>
        </div>
      );
    };
    const PfValueHistory=({addrs,live,period,setPeriod,txs})=>{
      const s=usePfSeries(addrs,period);
      const pts=s.pts.length&&live&&live.v!=null?[...s.pts,{t:Date.now(),v:live.v,p:live.p,u:live.u,bp:live.bp,bu:live.bu,now:true}]:s.pts;
      const vals=pts.filter(p=>p.v!=null);
      const first=vals[0],hi=vals.reduce((a,p)=>!a||p.v>a.v?p:a,null),lo=vals.reduce((a,p)=>!a||p.v<a.v?p:a,null);
      const cur=live&&live.v!=null?live.v:null;const chg=first&&cur!=null&&first.v>0?(cur-first.v)/first.v*100:null;
      return(
        <section className="pf2-pn pf2-sec pf2-vh">
          <div className="pf2-sech"><div><h2 className="oh">PORTFOLIO VALUE HISTORY</h2><div className="pf2-vhn">Your real balances, read from the chain {'—'} sells show as drops, buys as rises.</div></div>
            <div className="pf2-pp" role="group" aria-label="Period">{Object.keys(PFH_PERIODS).map(k=><button key={k} className={period===k?'on':''} aria-pressed={period===k} onClick={()=>setPeriod(k)}>{k}</button>)}</div></div>
          <div className="pf2-vhb">
            <div className="pf2-vhc">
              {s.state==='loading'&&<div className="pf2-hwait"><div>Reading {addrs.length} wallet{addrs.length===1?'':'s'} from the chain{'…'} <b>{Math.round(s.progress*100)}%</b></div><div className="bar"><i style={{width:Math.max(4,s.progress*100)+'%'}}></i></div><small>The first look reads every day; after that only what is new.</small></div>}
              {s.state==='failed'&&<div className="pf2-hwait"><div>Couldn{'’'}t read the history from the chain right now.</div><button className="pf2-lnk" onClick={s.retry}>Retry</button></div>}
              {s.state==='ok'&&<PfHistChart pts={pts} period={period} txs={txs}/>}
              {s.state==='ok'&&s.gaps>0&&<div className="pf2-hnote">{s.gaps} point{s.gaps>1?'s':''} could not be read and {s.gaps>1?'are':'is'} left as a gap. <button onClick={s.retry}>Retry</button></div>}
            </div>
            <div className="pf2-vhs">
              <div className="lb">Current value</div><div className="cv">{fmtDollar(cur)}</div>
              <div className={`chg ${chg==null?'':chg>=0?'up':'dn'}`}>{chg==null?<span>{'—'}</span>:<>{chg>=0?'▲':'▼'} {chg>=0?'+':'−'}{Math.abs(chg).toFixed(2)}% <small>{chg>=0?'+':'−'}{fmtDollar(Math.abs(cur-first.v))} ({period})</small></>}</div>
              <div className="hl"><div><div className="lb">Period high</div><b>{hi?pfhMoney(hi.v):'—'}</b><small>{hi?(hi.now?'now':pfhDate(hi.t)):''}</small></div><div><div className="lb">Period low</div><b>{lo?pfhMoney(lo.v):'—'}</b><small>{lo?(lo.now?'now':pfhDate(lo.t)):''}</small></div></div>
            </div>
          </div>
        </section>
      );
    };
