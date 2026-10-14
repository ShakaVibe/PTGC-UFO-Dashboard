    /* Expects from PfLeagues.jsx (loaded first): PF_ADDR, PF_TOKEN_ADDR, PF_SUPPLY, pfAbbr, pfAddr, pfLsSet, PfModal. Used by PfTx.jsx
       and PortfolioV2.jsx: PFH_TOK, pfhPrices, pfhPriceAt, pfhRpc, usePfSeries, usePf24h, PfValueHistory, PfEarnedModal, usePfUfoV1.
       pf-v2.py concatenates PfLeagues → PfHistory → PfTx → PortfolioV2; only use another file's names inside functions. */
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
    const PFH_TOK=PF_TOKEN_ADDR;   // round 27 (audit E2): one source (PfLeagues.jsx)
    const PFH_RAW='https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/';
    const PFH_H=3600e3,PFH_D=86400e3,PFH_BLOCK_MS=10300,PFH_RPC_TIMEOUT=20000,PFH_BATCH=80;   // PulseChain ~10.3 s blocks; batched eth_call size
    const PFH_PERIODS={'7D':{step:6*PFH_H,n:28,unit:6*PFH_H},'30D':{step:PFH_D,n:30,unit:PFH_D},'90D':{step:PFH_D,n:90,unit:PFH_D},'1Y':{step:4*PFH_D,n:92,unit:4*PFH_D}};   // round 24 (audit B5): 1Y points on 4-day boundaries so they repeat day to day
    let pfhCache=null;   // {v:{'addr|TOK':{ts:bal}}}
    const pfhLoad=()=>{if(pfhCache)return pfhCache;try{const s=localStorage.getItem(PFH_LS);pfhCache=s?JSON.parse(s):{v:{}};if(!pfhCache.v)pfhCache={v:{}};}catch(e){pfhCache={v:{}};}
      /* round 24 (audit B5): the cache grew forever — drop points older than 400 days, and 6-hour (7D) points older than 15 days */
      try{const now=Date.now();let n=0;Object.values(pfhCache.v).forEach(m=>Object.keys(m).forEach(k=>{const t=+k;if(now-t>400*PFH_D||(t%PFH_D!==0&&now-t>15*PFH_D)){delete m[k];n++;}}));if(n)pfhSave();}catch(e){}
      return pfhCache;};
    let pfhSaveT=null;
    /* round 27 (audit E3): on quota, drop the OLDEST points (not a third of the wallets) until it fits — same idea as the tx cache */
    const pfhSave=()=>{clearTimeout(pfhSaveT);pfhSaveT=setTimeout(()=>pfLsSet(PFH_LS,pfhCache,c=>{const all=[];Object.entries(c.v).forEach(([k,m])=>Object.keys(m).forEach(t=>all.push([+t,k])));if(!all.length)return false;all.sort((a,b)=>a[0]-b[0]);all.slice(0,Math.max(1,Math.ceil(all.length/10))).forEach(([t,k])=>{delete c.v[k][t];});return true;}),800);};
    let pfhEp=0;
    const pfhRpc=async(body,tries=3)=>{
      for(let t=0;t<tries;t++){
        const ep=PFH_RPC[(pfhEp+t)%PFH_RPC.length];
        try{const ac=new AbortController();const to=setTimeout(()=>ac.abort(),PFH_RPC_TIMEOUT);
          const r=await fetch(ep,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:ac.signal});clearTimeout(to);
          if(!r.ok)throw new Error('HTTP '+r.status);const j=await r.json();
          if(Array.isArray(body)&&!Array.isArray(j))throw new Error('no batch');
          pfhEp=(pfhEp+t)%PFH_RPC.length;return j;
        }catch(e){if(t===tries-1)throw e;}
      }
    };
    /* timestamp → block: anchors at the head and ~7 / 30 / 90 / 180 / 365 / 420 days back, linear between them */
    let pfhAnchors=null,pfhAnchorsAt=0,pfhAnchorsP=null;
    /* round 24 (audit B2): one request at a time — the chart, the 24 h tiles and the Details window all ask at mount */
    const pfhGetAnchors=()=>{
      if(pfhAnchors&&Date.now()-pfhAnchorsAt<10*60e3)return Promise.resolve(pfhAnchors);
      if(pfhAnchorsP)return pfhAnchorsP;
      pfhAnchorsP=pfhGetAnchors0().finally(()=>{pfhAnchorsP=null;});return pfhAnchorsP;
    };
    const pfhGetAnchors0=async()=>{
      const head=await pfhRpc({jsonrpc:'2.0',id:1,method:'eth_getBlockByNumber',params:['latest',false]});
      const hn=parseInt(head.result.number,16),ht=parseInt(head.result.timestamp,16)*1000;
      const nums=[7,30,90,180,365,420].map(d=>Math.max(1,hn-Math.round(d*PFH_D/PFH_BLOCK_MS)));
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
      const[nonce,setNonce]=useState(0);   // round 23 (audit A11 / B6): retry + a 20 s timeout per shard
      useEffect(()=>{let live=true;const cs=[...new Set(addrs.map(a=>a.toLowerCase()[2]))];
        if(!cs.length){setSt({state:'ok',m:{}});return;}
        const get=c=>{const ac=new AbortController();const to=setTimeout(()=>ac.abort(),20000);return fetch(PFH_RAW+'ufo-v1-earned/'+c+'.json',{signal:ac.signal}).then(r=>{if(!r.ok)throw new Error('HTTP '+r.status);return r.json();}).finally(()=>clearTimeout(to));};
        Promise.all(cs.map(c=>pfV1Shard[c]||(pfV1Shard[c]=get(c).catch(e=>{delete pfV1Shard[c];throw e;}))))
          .then(ms=>{if(live)setSt({state:'ok',m:Object.assign({},...ms)});}).catch(()=>{if(live)setSt({state:'failed',m:{}});});
        return()=>{live=false;};},[key,nonce]);
      return{state:st.state,of:a=>st.m[a.toLowerCase().slice(2)]||0,retry:()=>{setSt(s=>({...s,state:'loading'}));setNonce(n=>n+1);}};
    };
    /* prices: the Charts page's prebuilt files (refetched every 30 min) */
    let pfhPx=null,pfhPxAt=0,pfhPxP=null;
    const pfhPrices=()=>{
      if(pfhPx&&Date.now()-pfhPxAt<30*60e3)return Promise.resolve(pfhPx);
      if(pfhPxP)return pfhPxP;   // round 24 (audit B2): was fetched up to 5× at first paint
      pfhPxP=pfhPrices0().finally(()=>{pfhPxP=null;});return pfhPxP;
    };
    const pfhPrices0=async()=>{
      const g=async f=>{try{const r=await fetch(PFH_RAW+f,{cache:'no-cache'});return r.ok?await r.json():null;}catch(e){return null;}};
      const[d,h]=await Promise.all([g('charts-data.json'),g('charts-intraday.json')]);
      if(!d&&!h){pfhPx=null;throw new Error('price files unavailable');}   // round 23 (audit A3): a failed load is not cached for 30 min
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
      const B=PFH_BATCH,batches=[];for(let i=0;i<need.length;i+=B)batches.push(need.slice(i,i+B));
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
    /* round 25 (audit C2): chart points sit on LOCAL midnights (and local 6-hour slots on 7D) so a point labelled "Oct 13" is the
       end of Oct 13 where the viewer is — the feed already groups by local day. 1Y keeps 4-day boundaries. */
    const pfhLocalMidnight=t=>{const d=new Date(t);d.setHours(0,0,0,0);return d.getTime();};
    const pfhTimes=period=>{const P=PFH_PERIODS[period];const now=Date.now();const out=[];
      if(period==='1Y'){const last=Math.floor(now/P.unit)*P.unit;for(let k=P.n-1;k>=0;k--)out.push(last-k*P.step);}
      else if(period==='7D'){const d=new Date(now);d.setMinutes(0,0,0);d.setHours(Math.floor(d.getHours()/6)*6);for(let k=P.n-1;k>=0;k--)out.push(d.getTime()-k*P.step);}
      else{const d0=new Date(pfhLocalMidnight(now));for(let k=P.n-1;k>=0;k--){const d=new Date(d0);d.setDate(d0.getDate()-k);out.push(d.getTime());}}
      return out.filter(t=>t<now-60e3);};
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
    const pf24Mem={};   // round 24 (audit B2): per-wallet balances 24 h ago, keyed by the 10-minute slot — a toggle no longer re-reads every wallet
    const usePf24h=addrs=>{
      const[v,setV]=useState(null);const key=addrs.slice().sort().join(',');
      useEffect(()=>{if(!addrs.length){setV(null);return;}let live=true;(async()=>{try{
        const[a,px]=await Promise.all([pfhGetAnchors(),pfhPrices()]);
        const ts=Math.floor((Date.now()-PFH_D)/600e3)*600e3;const block=pfhBlockAt(a,ts);
        const need=addrs.filter(addr=>!pf24Mem[addr+'|'+ts]);
        if(need.length){const res=await pfhRpc(need.flatMap((addr,i)=>['PTGC','UFO'].map((tok,k)=>({jsonrpc:'2.0',id:i*2+k,method:'eth_call',params:[{to:PFH_TOK[tok],data:'0x70a08231'+addr.slice(2).padStart(64,'0')},'0x'+block.toString(16)]}))));
          const by={};(res||[]).forEach(r=>{if(r)by[r.id]=r;});
          need.forEach((addr,i)=>{const v2=[0,0];for(let k=0;k<2;k++){const r=by[i*2+k];if(!r||r.error||r.result==null)return;v2[k]=r.result==='0x'?0:Number(BigInt(r.result))/1e18;}if(by[i*2]&&by[i*2+1])pf24Mem[addr+'|'+ts]=v2;});}
        let p=0,u=0;for(const addr of addrs){const m=pf24Mem[addr+'|'+ts];if(!m)throw new Error('read');p+=m[0];u+=m[1];}
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
    const PfHistChart=React.memo(({pts,period,txs,wallets})=>{   // round 24 (audit B1): memoised — redraws only when its points / period / transactions / wallets change
      const ref=React.useRef(null);const[hov,setHov]=useState(null);
      const[day,setDay]=useState(null);   // round 28: the strip bar (its chart-point time) whose day window is open
      const nameOf=React.useMemo(()=>pftNameOf(wallets||[]),[wallets]);
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
      /* round 23 (audit A1, Shaka picked option B of mock-dots-v1): NOTHING on the line any more. The transactions become an
         activity strip under the chart — one thin bar per chart point (a day; 6 h on 7D), stacked green / red / blue / yellow by
         how many of each kind, taller with more, a count on the busy ones. Dust under $1 is left out. Hovering the chart lights
         the matching bar and the tooltip lists the transactions. Each wallet + token only counts back to its own coverage. */
      const cov=txs&&txs.cov||{};
      const stepName=period==='7D'?'6 hours':period==='1Y'?'4 days':'day';
      const kindOf=r=>TOUT[r.type]?'out':TCL[r.type]?'cl':TLP[r.type]?'lp':TIN[r.type]?'in':null;
      if(txs){const by=new Map();txs.rows.forEach(r=>{const k=kindOf(r);if(!k)return;if(r.usd!=null&&r.usd<1)return;if(r.t<=vals[0].t||!pftCovered(txs,r.addr,r.tok,r.t))return;
          const p=vals.find(q=>q.t>=r.t)||vals[vals.length-1];const e=by.get(p.t)||{p,tx:[],n:{in:0,out:0,cl:0,lp:0}};e.tx.push(r);e.n[k]++;by.set(p.t,e);});
        by.forEach(e=>ev.push(e));}
      ev.sort((a,b)=>a.p.t-b.p.t);
      const covFrom=Math.max(0,...Object.values(cov));
      const evAt=t=>ev.find(e=>e.p.t===t);
      /* round 28 (Shaka: "mouse over or click on the little daily bars and it pops a window showing the day's moves"): each bar
         is a button — hover / tap lights it and shows the chart tooltip (5 trades + "click the bar for all N"), click or Enter
         on the chart opens PfDayModal with every transaction of that step. A bar's trades fall in (previous point, this point]:
         the daily points sit at local midnight, so the bar at Oct 5 00:00 holds OCT 4's trades — bucketName labels it so. */
      const step=period==='7D'?6*PFH_H:period==='1Y'?4*PFH_D:PFH_D;
      const bucketOf=e=>{const k=vals.indexOf(e.p);return{a:k>0?vals[k-1].t:e.p.t-step,b:e.p.t,now:!!e.p.now};};
      const bucketName=(e,long)=>{const{a,b,now}=bucketOf(e);
        if(period==='7D')return pfhDate(a,true)+' \u2013 '+(now?'now':new Date(b).toLocaleTimeString('en-US',{hour:'numeric'}));
        if(period==='1Y'||b-a>1.5*PFH_D)return pfhDate(a)+' \u2013 '+(now?'now':pfhDate(b-1));
        if(now)return long?'Today':'today';
        return long?new Date(b-1).toLocaleDateString('en-US',{weekday:'long',month:'short',day:'numeric'}):pfhDate(b-1);};
      const when=e=>{const n=bucketName(e);return period==='7D'||period==='1Y'||n.indexOf('\u2013')>=0?n:e.p.now?n:'on '+n;};
      const di=day!=null?ev.findIndex(e=>e.p.t===day):-1;
      const txLine=r=>{const k=TOUT[r.type]?'out':TCL[r.type]?'cl':TLP[r.type]?'lp':'in';const g={out:'\u25BC ',in:'\u25B2 ',cl:'\u2B07 ',lp:r.type==='Add LP'?'\u2295 ':'\u2296 '}[k];
        return <span key={r.id} className={k}>{g}{r.type} {pfAbbr(Math.abs(r.amt))} {r.tok}{r.usd!=null&&<em> {'\u00B7'} {pfhMoney(r.usd)}</em>}</span>;};
      return(
        <div className="pf2-hc">
          <div className="pf2-hy" aria-hidden="true">{ticks.slice().reverse().map((v,i)=><span key={i}>{pfhMoney(v)}</span>)}</div>
          {/* round 26 (audit D3): the chart is keyboard-readable — Tab to it, ← → step through the points, Home / End; the
              tooltip text is announced through the live region below */}
          <div className="pf2-hp" ref={ref} tabIndex={0} onMouseMove={move} onMouseLeave={()=>setHov(null)} onTouchStart={move} onTouchMove={move} onTouchEnd={()=>setHov(null)} onBlur={()=>setHov(null)}
            onKeyDown={e=>{const i=hov?vals.indexOf(hov):vals.length-1;let j=null;if(e.key==='ArrowLeft')j=Math.max(0,i-1);else if(e.key==='ArrowRight')j=Math.min(vals.length-1,i+1);else if(e.key==='Home')j=0;else if(e.key==='End')j=vals.length-1;else if(e.key==='Escape')setHov(null);else if(e.key==='Enter'&&hov){const x=evAt(hov.t);if(x){e.preventDefault();setDay(x.p.t);}}if(j!=null){e.preventDefault();setHov(vals[j]);}}}
            role="img" aria-label={`Portfolio value from ${pfhDate(t0)} to now: ${pfhMoney(vals[0].v)} to ${pfhMoney(last.v)}. Use the arrow keys to step through the points; Enter opens that day's transactions.`}>
            {ticks.map((v,i)=><i key={i} className="g" style={{top:Y(v)+'%'}}></i>)}
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true"><defs><linearGradient id="pfhA" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#5CE13A" stopOpacity=".5"/><stop offset="1" stopColor="#1F6B12" stopOpacity=".06"/></linearGradient></defs>
              <path d={area} fill="url(#pfhA)"/><path d={d} fill="none" stroke="#7CFC00" strokeWidth="2" vectorEffect="non-scaling-stroke" strokeLinejoin="round"/></svg>
            <b className="dot" style={{left:X(last.t)+'%',top:Y(last.v)+'%'}}></b>
            {hov&&<><i className="xh" style={{left:X(hov.t)+'%'}}></i><b className="dot h" style={{left:X(hov.t)+'%',top:Y(hov.v)+'%'}}></b>
              <div className={`pf2-htip${X(hov.t)>62?' l':''}`} style={{left:X(hov.t)+'%'}}><div className="d">{hov.now?'Now':pfhDate(hov.t,period==='7D')}</div><div className="v">{fmtDollar(hov.v)}</div><div className="s"><span className="p">PTGC {fmtDollar(hov.p,0)}</span><span className="u">UFO {fmtDollar(hov.u,0)}</span></div>{(()=>{const e=evAt(hov.t);if(!e)return null;const l=e.tx.slice().sort((a,b)=>b.t-a.t);return <div className="ev">{l.slice(0,5).map(txLine)}<small>{l.length} {l.length===1?'transaction':'transactions'} {when(e)}</small><small className="go">{l.length>5?`+${l.length-5} more \u2014 `:''}click the bar for the full list {'\u2192'}</small></div>;})()}</div></>}
          </div>
          <div className="pf2-sr" aria-live="polite">{hov?`${hov.now?'Now':pfhDate(hov.t,period==='7D')}: ${fmtDollar(hov.v)} (PTGC ${fmtDollar(hov.p,0)}, UFO ${fmtDollar(hov.u,0)})${(()=>{const e=evAt(hov.t);return e?`, ${e.tx.length} transaction${e.tx.length===1?'':'s'}`:'';})()}`:''}</div>
          {txs&&<div className="pf2-strip" role="group" aria-label={`Trades per ${stepName}`} onMouseLeave={()=>setHov(null)}><span className="lab" aria-hidden="true">{period==='7D'?'TRADES / 6H':period==='1Y'?'TRADES / 4D':'TRADES'}</span>
            {ev.map((e,i)=>{const n=e.tx.length,h=Math.min(26,4+n*4);const on=hov&&hov.t===e.p.t;return(<button key={i} type="button" tabIndex={-1} className={`day${on?' on':''}${n>=4?' hot':''}`} data-n={n} style={{left:X(e.p.t)+'%',height:h+'px'}}
              aria-label={`${bucketName(e,true)}: ${n} transaction${n===1?'':'s'}`} title={`${bucketName(e,true)} \u00B7 ${n} transaction${n===1?'':'s'} \u00B7 click for the list`} onMouseEnter={()=>setHov(e.p)} onTouchStart={ev2=>{ev2.stopPropagation();setHov(e.p);}} onClick={()=>setDay(e.p.t)}>
              {KINDS.map(([k])=>e.n[k]>0&&<i key={k} className={k} style={{flex:e.n[k]}}></i>)}</button>);})}</div>}
          {di>=0&&<PfDayModal ev={ev} i={di} go={setDay} close={()=>setDay(null)} vals={vals} bucketName={bucketName} kindOf={kindOf} nameOf={nameOf}/>}
          {txs&&<div className="pf2-hlg"><span><b className="in"></b>buys</span><span><b className="out"></b>sells</span><span><b className="cl"></b>claims</span><span><b className="lp"></b>liquidity</span><span className="o">one bar per {stepName} {'\u00B7'} taller = more {'\u00B7'} dust under $1 left out</span><span className="go">{'\u261D'} click a bar for the {stepName==='day'?'day\u2019s':stepName+'\u2019'} moves</span>{covFrom>vals[0].t&&<span className="o">complete from {pfhDate(covFrom)}</span>}</div>}
          <div className="pf2-hx" aria-hidden="true">{xl.map((t,i)=><span key={i} style={{left:(i/nx*100)+'%'}}>{i===nx?'Now':pfhDate(t)}</span>)}</div>
        </div>
      );
    });
    /* round 28: the day window — every transaction of one strip bar, in the Recent Transactions rows (PfTxRow, PfTx.jsx) */
    const PfDayModal=({ev,i,go,close,vals,bucketName,kindOf,nameOf})=>{
      const e=ev[i];const l=e.tx.slice().sort((a,b)=>b.t-a.t);
      const[cp,copy]=usePftCopy();
      const k=vals.indexOf(e.p),prev=k>0?vals[k-1]:null;const chg=prev&&prev.v>0?(e.p.v-prev.v)/prev.v*100:null;
      const K={in:{n:0,usd:0},out:{n:0,usd:0},cl:{n:0,usd:0},lp:{n:0,usd:0}};let tin=0,tout=0;
      l.forEach(r=>{const x=K[kindOf(r)];if(x){x.n++;x.usd+=r.usd||0;}const s=PFT_AMT[r.type];if(s==='neg')tout+=r.usd||0;else if(s==='pos')tin+=r.usd||0;});
      const nw=new Set(l.map(r=>r.addr)).size;const title=bucketName(e,true);
      const toFeed=()=>{close();setTimeout(()=>{const s=document.querySelector('.pf2-rt');if(s)s.scrollIntoView({behavior:'smooth',block:'start'});},60);};
      return(
        <PfModal className="z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80" onClose={close} label={`${title}: ${l.length} transaction${l.length===1?'':'s'}`}>
          <div className="pf2-dw" onClick={ev2=>ev2.stopPropagation()}>
            <div className="hd"><h2 className="oh">{title}<small>{l.length} transaction{l.length===1?'':'s'}{prev&&prev.v!=null&&e.p.v!=null&&<> {'\u00B7'} portfolio {fmtDollar(prev.v,0)} {'\u2192'} {fmtDollar(e.p.v,0)}{chg!=null&&<b className={chg<0?'neg':'pos'}> {chg<0?'\u25BC':'\u25B2'} {chg>=0?'+':'\u2212'}{Math.abs(chg).toFixed(1)}%</b>}</>}</small></h2>
              <div className="nav"><button disabled={i===0} onClick={()=>go(ev[i-1].p.t)} aria-label="Previous day with trades">{'\u25C0'} {i>0?bucketName(ev[i-1]):''}</button><button disabled={i>=ev.length-1} onClick={()=>go(ev[i+1].p.t)} aria-label="Next day with trades">{i<ev.length-1?bucketName(ev[i+1]):''} {'\u25B6'}</button></div>
              <button className="x" onClick={close} aria-label="Close">{'\u00D7'}</button></div>
            <div className="pf2-dsum">{[['in','BUYS','paid'],['out','SELLS','received'],['cl','CLAIMS','earned'],['lp','LIQUIDITY','moved']].map(([q,n,w])=><div key={q} className={q}><b>{n}</b><span>{K[q].n}</span><small>{K[q].n?fmtDollar(K[q].usd,0)+' '+w:'\u2014'}</small></div>)}</div>
            <div className="net">Tokens out <b className="neg">{'\u2212'}{fmtDollar(tout,0)}</b> {'\u00B7'} tokens in <b className="pos">+{fmtDollar(tin,0)}</b> {'\u00B7'} across <b>{nw} wallet{nw===1?'':'s'}</b></div>
            <div className="list">{l.map(r=><PfTxRow key={r.id} r={r} who={pftWhoOf(nameOf,r)} cp={cp===r.id} onCopy={copy}/>)}</div>
            <div className="ft"><span>Dust under $1 left out {'\u00B7'} times in your local time</span><button onClick={toFeed}>Go to Recent Transactions {'\u2193'}</button></div>
          </div>
        </PfModal>);
    };
    const PfValueHistory=({addrs,live,period,setPeriod,txs,wallets})=>{
      const s=usePfSeries(addrs,period);
      const lv=live&&live.v!=null?live:null;
      const pts=React.useMemo(()=>s.pts.length&&lv?[...s.pts,{t:Date.now(),v:lv.v,p:lv.p,u:lv.u,bp:lv.bp,bu:lv.bu,now:true}]:s.pts,[s.pts,lv&&lv.v,lv&&lv.p,lv&&lv.u,lv&&lv.bp,lv&&lv.bu]);   // round 24 (audit B1): stable between renders
      const vals=pts.filter(p=>p.v!=null);
      const first=vals[0],hi=vals.reduce((a,p)=>!a||p.v>a.v?p:a,null),lo=vals.reduce((a,p)=>!a||p.v<a.v?p:a,null);
      const cur=live&&live.v!=null?live.v:null;const chg=first&&cur!=null&&first.v>0?(cur-first.v)/first.v*100:null;
      return(
        <section className="pf2-pn pf2-sec pf2-vh">
          <div className="pf2-sech"><div><h2 className="oh">PORTFOLIO VALUE HISTORY</h2><div className="pf2-vhn">Your real balances, read from the chain {'—'} sells show as drops, buys as rises.</div></div>
            <div className="pf2-pp" role="group" aria-label="Period">{Object.keys(PFH_PERIODS).map(k=><button key={k} className={period===k?'on':''} aria-pressed={period===k} onClick={()=>setPeriod(k)}>{k}</button>)}</div></div>
          <div className="pf2-vhb">
            <div className="pf2-vhc">
              {s.state==='loading'&&!s.pts.length&&<div className="pf2-hwait"><div>Reading {addrs.length} wallet{addrs.length===1?'':'s'} from the chain{'…'} <b>{Math.round(s.progress*100)}%</b></div><div className="bar"><i style={{width:Math.max(4,s.progress*100)+'%'}}></i></div><small>The first look reads every day; after that only what is new.</small></div>}
              {s.state==='failed'&&<div className="pf2-hwait"><div>Couldn{'’'}t read the history from the chain right now.</div><button className="pf2-lnk" onClick={s.retry}>Retry</button></div>}
              {(s.state==='ok'||(s.state==='loading'&&s.pts.length>0))&&<div className={s.state==='loading'?'pf2-hstale':''}>{s.state==='loading'&&<span className="pf2-upd">updating{'\u2026'} {Math.round(s.progress*100)}%</span>}<PfHistChart pts={pts} period={period} txs={txs} wallets={wallets}/></div>}   {/* round 25 (audit C4): the old chart stays while a toggle / period change reloads */}
              {s.state==='ok'&&s.gaps>0&&<div className="pf2-hnote">{s.gaps} point{s.gaps>1?'s':''} could not be read and {s.gaps>1?'are':'is'} left as a gap. <button onClick={s.retry}>Retry</button></div>}
            </div>
            <div className="pf2-vhs">
              <div className="lb">Current value</div><div className="cv">{fmtDollar(cur)}</div>
              <div className={`chg ${chg==null?'':chg>=0?'up':'dn'}`}>{chg==null?<span>{'—'}</span>:<>{chg>=0?'▲':'▼'} {chg>=0?'+':'−'}{Math.abs(chg).toFixed(2)}% <small>{chg>=0?'+':'−'}{fmtDollar(Math.abs(cur-first.v))} ({period})</small></>}</div>
              <div className="hl"><div><div className="lb">Period high</div><b>{hi?fmtDollar(hi.v):'—'}</b><small>{hi?(hi.now?'now':pfhDate(hi.t)):''}</small></div><div><div className="lb">Period low</div><b>{lo?fmtDollar(lo.v):'—'}</b><small>{lo?(lo.now?'now':pfhDate(lo.t)):''}</small></div></div>
            </div>
          </div>
        </section>
      );
    };
    /* ===== round 20 — EARNED BY SOURCE · 30-DAY DETAILS (design/portfolio/mock-earned-details-v1.html, approved) =====
       Each day = the change in a running total between two UTC midnights (the last bar = today so far, to the live head block).
       Running totals per wallet, read at past blocks (archive eth_call, batched like the value history):
         staking S = mapUserInfo.claimed + mapUserInfo.pendingToClaimed + pendingReward      (staking contract)
         locking L = mapUserInfo.lockClaimed + Σ pendingRewardLock(i), i = 1..lockCount       (staking contract)
         PTGC reflections R = balanceOf + totalSend − totalReceived                           (PTGC's own counters, exact)
         UFO balance U = balanceOf; UFO reflections of a day = ΔU − that day's net transfers (Recent Transactions' flows, the
         hidden 1 % added back), split at the boundary blocks' REAL timestamps so a transfer near midnight lands on the right day.
       So staking / locking show rewards as they build up, not only on claim days (checked on chain 2026-10-14: S, L, R only rise).
       A day whose reads failed — or, for UFO, whose transfers aren't all in reach — is a gap, never a guess. Past midnights are
       cached for good (PFE_LS); the head is read fresh. */
    const PFE_LS='grays_pf_ed_v1';
    const PFE_ST=PF_ADDR.STAKING;
    let pfeC=null;
    const pfeLoad=()=>{if(pfeC)return pfeC;try{pfeC=JSON.parse(localStorage.getItem(PFE_LS)||'{}')||{};}catch(e){pfeC={};}if(!pfeC.v)pfeC={v:{},bt:{}};if(!pfeC.bt)pfeC.bt={};return pfeC;};
    const pfeSave=()=>pfLsSet(PFE_LS,pfeC,c=>{const ks=[...new Set(Object.values(c.v).flatMap(m=>Object.keys(m)))].sort((a,b)=>+a-+b);if(!ks.length)return false;ks.slice(0,Math.max(1,Math.ceil(ks.length/10))).forEach(k=>{Object.values(c.v).forEach(m=>{delete m[k];});delete c.bt[k];});return true;});   // round 27 (audit E3): drop the oldest days, never wipe
    const pfePad=a=>a.toLowerCase().replace(/^0x/,'').padStart(64,'0');
    const pfeWord=(h,i)=>{try{const x=h.slice(2+64*i,2+64*(i+1));return x.length===64?Number(BigInt('0x'+x))/1e18:null;}catch(e){return null;}};
    const pfeNum=h=>h&&h!=='0x'&&h.length>=66?pfeWord(h,0):null;
    const pfeBatch=async calls=>{const out=new Array(calls.length).fill(null);const B=PFH_BATCH;const bs=[];for(let i=0;i<calls.length;i+=B)bs.push(i);
      let q=0;const w=async()=>{while(q<bs.length){const s0=bs[q++];const ch=calls.slice(s0,s0+B);let res=null;try{res=await pfhRpc(ch.map((c,i)=>({jsonrpc:'2.0',id:i,...c})));}catch(e){res=null;}
        (res||[]).forEach(r=>{if(r&&!r.error&&r.result!=null)out[s0+r.id]=r.result;});}};
      await Promise.all([w(),w()]);return out;};
    const usePfEarned=(addrs,open,nDays=30)=>{
      const[st,setSt]=useState({state:'idle',progress:0,pts:null});
      const[nonce,setNonce]=useState(0);
      const key=addrs.slice().sort().join(',')+'|'+nDays;
      useEffect(()=>{
        if(!open||!addrs.length)return;let live=true;
        (async()=>{
          setSt(s=>({...s,state:s.pts?'ok':'loading',progress:0}));
          try{
            const a=await pfhGetAnchors();const head=a[a.length-1];
            /* round 25 (audit C2 / C16): LOCAL midnights (the feed groups by local day), 7 / 30 / 90 of them */
            const d0=new Date(pfhLocalMidnight(Date.now()));const last=d0.getTime();const tss=[];for(let k=nDays-1;k>=0;k--){const d=new Date(d0);d.setDate(d0.getDate()-k);tss.push(d.getTime());}
            const pts=tss.map(ts=>({ts,block:pfhBlockAt(a,ts)})).concat([{ts:'now',block:head[0],bt:head[1]}]);
            const c=pfeLoad();
            /* the boundary blocks' real timestamps (cached with the midnight) */
            const nbt=pts.filter(p=>p.ts!=='now'&&c.bt[p.ts]==null);
            if(nbt.length){const r=await pfeBatch(nbt.map(p=>({method:'eth_getBlockByNumber',params:['0x'+p.block.toString(16),false]})));
              r.forEach((x,i)=>{if(x&&x.timestamp)c.bt[nbt[i].ts]=parseInt(x.timestamp,16)*1000;});}
            pts.forEach(p=>{if(p.ts!=='now')p.bt=c.bt[p.ts]!=null?c.bt[p.ts]:p.ts;});
            /* phase A — 7 reads per wallet + boundary not cached yet (the head always) */
            const need=[];pts.forEach(p=>addrs.forEach(ad=>{const hit=p.ts!=='now'&&c.v[ad]&&c.v[ad][p.ts];if(!hit)need.push({p,ad});}));
            const blk=p=>'0x'+p.block.toString(16),P=PFH_TOK.PTGC,U=PFH_TOK.UFO;
            const callsA=[];need.forEach(({p,ad})=>{const x=pfePad(ad),b=blk(p);[[P,'0x70a08231'],[P,'0xc64a041b'],[P,'0x4df9cfb3'],[PFE_ST,'0x15612933'],[PFE_ST,'0xf40f0f52'],[PFE_ST,'0xdf034586'],[U,'0x70a08231']].forEach(([to,sel])=>callsA.push({method:'eth_call',params:[{to,data:sel+x},b]}));});
            if(live)setSt(s=>({...s,progress:.05}));
            const rA=callsA.length?await pfeBatch(callsA):[];
            if(live)setSt(s=>({...s,progress:.6}));
            const partial=need.map((n,i)=>{const g=k=>rA[i*7+k];const ui=g(3);
              const bal=pfeNum(g(0)),snd=pfeNum(g(1)),rcv=pfeNum(g(2)),pr=pfeNum(g(4)),u=pfeNum(g(6));let lc=null;try{lc=g(5)&&g(5).length>=66?Number(BigInt(g(5).slice(0,66))):null;}catch(e){}
              const ok=ui&&ui.length>=2+64*7&&[bal,snd,rcv,pr,u,lc].every(v=>v!=null);
              return ok?{...n,r:bal+snd-rcv,s:pfeWord(ui,3)+pfeWord(ui,6)+pr,lcl:pfeWord(ui,4),lc,u}:{...n,bad:true};});
            /* phase B — each lock's pending reward */
            const callsB=[],idx=[];partial.forEach((x,j)=>{if(x.bad)return;for(let i=1;i<=x.lc;i++){callsB.push({method:'eth_call',params:[{to:PFE_ST,data:'0xddeecc24'+pfePad(x.ad)+i.toString(16).padStart(64,'0')},blk(x.p)]});idx.push(j);}});
            const rB=callsB.length?await pfeBatch(callsB):[];
            const pl=partial.map(()=>0),plBad=partial.map(()=>false);rB.forEach((h,k)=>{const v=pfeNum(h);if(v==null)plBad[idx[k]]=true;else pl[idx[k]]+=v;});
            const nowV={};
            partial.forEach((x,j)=>{if(x.bad||plBad[j])return;const v=[x.s,x.lcl+pl[j],x.r,x.u];if(x.p.ts==='now')nowV[x.ad]=v;else(c.v[x.ad]=c.v[x.ad]||{})[x.p.ts]=v;});
            /* keep the cache to the last ~100 days */
            Object.values(c.v).forEach(m=>Object.keys(m).forEach(k=>{if(+k<last-100*PFH_D)delete m[k];}));Object.keys(c.bt).forEach(k=>{if(+k<last-100*PFH_D)delete c.bt[k];});
            pfeSave();
            const val=(ad,p)=>p.ts==='now'?nowV[ad]:(c.v[ad]||{})[p.ts];
            const out=pts.map(p=>({ts:p.ts==='now'?Date.now():p.ts,bt:p.bt,w:Object.fromEntries(addrs.map(ad=>[ad,val(ad,p)||null]))}));
            if(!live)return;
            setSt({state:'ok',progress:1,pts:out});
          }catch(e){if(live)setSt(s=>({...s,state:s.pts?'ok':'failed'}));}
        })();
        return()=>{live=false;};
      },[key,open,nonce]);
      return{...st,retry:()=>setNonce(n=>n+1)};
    };
    const PFE_LS_DAYS='grays_pf_ed_days';
    const PFE_C={st:'#A970FF',lk:'#EC4899',rf:'#E8BE3F',uf:'#7CFC00'};
    const PFE_N={st:'Staking',lk:'Locking',rf:'Reflections',uf:'Reflections'};
    const pfeUseW=()=>{const ref=React.useRef(null);const[w,setW]=useState(0);useEffect(()=>{if(!ref.current)return;const ro=new ResizeObserver(e=>setW(Math.round(e[0].contentRect.width)));ro.observe(ref.current);return()=>ro.disconnect();},[]);return[ref,w];};
    const pfeNice=m=>{if(!(m>0))return 1;const e=Math.pow(10,Math.floor(Math.log10(m)));const f=m/e;return(f<=1.5?1.5:f<=2?2:f<=2.5?2.5:f<=3?3:f<=4?4:f<=5?5:f<=6?6:f<=8?8:10)*e;};
    const pfeDay=t=>new Date(t).toLocaleDateString('en-US',{month:'short',day:'numeric'});   // round 25 (audit C2): local days now
    const pfeWd=t=>new Date(t).toLocaleDateString('en-US',{weekday:'short'});
    /* round 21: views — PTGC (tokens), UFO (tokens), BOTH (dollars: the two tokens can't share a token scale; the default).
       Each view says which sources it stacks, how to read a source's value off a day, and how a day counts as complete. */
    const PFE_NB={st:'PTGC staking',lk:'PTGC locking',rf:'PTGC reflections',uf:'UFO reflections'};
    const pfeView=v=>v==='BOTH'?{keys:['st','lk','rf','uf'],name:k=>PFE_NB[k],val:(d,k)=>(d[k]||0)*(k==='uf'?d.pU:d.pP),usd:(d,k)=>(d[k]||0)*(k==='uf'?d.pU:d.pP),ok:d=>d.okP&&d.okU&&d.pP!=null&&d.pU!=null,why:d=>!d.okP?d.whyP:!d.okU?d.whyU:'No price for this day',fmt:v=>'$'+pfAbbr(v),unit:'$'}
      :v==='UFO'?{keys:['uf'],name:k=>PFE_N[k],val:(d,k)=>d[k]||0,usd:(d,k)=>d.pU!=null?(d[k]||0)*d.pU:null,ok:d=>d.okU,why:d=>d.whyU,fmt:pfAbbr,unit:'UFO'}
      :{keys:['st','lk','rf'],name:k=>PFE_N[k],val:(d,k)=>d[k]||0,usd:(d,k)=>d.pP!=null?(d[k]||0)*d.pP:null,ok:d=>d.okP,why:d=>d.whyP,fmt:pfAbbr,unit:'PTGC'};
    /* the stacked daily columns: ≤ 20 px, 2 px surface gaps between segments, 4 px rounded top, hover / tap a day */
    const PfEdChart=({days,keys,V})=>{
      const[ref,W]=pfeUseW();const[hov,setHov]=useState(null);
      const phone=W>0&&W<520,H=phone?190:260,L=phone?48:62,R=10,T=12,B=26;
      const n=days.length,iw=Math.max(1,W-L-R),ih=H-T-B,band=iw/n,bw=Math.min(phone?8:20,band*.62);
      const tot=d=>V.ok(d)?keys.reduce((t,k)=>t+V.val(d,k),0):0;
      const mx=pfeNice(Math.max(1e-9,...days.map(tot))*1.05),y=v=>T+ih-v/mx*ih;
      const ok=days.filter(V.ok),avg=ok.length?ok.reduce((t,d)=>t+tot(d),0)/ok.length:0;
      const move=e=>{const r=ref.current.getBoundingClientRect();const cx=(e.touches?e.touches[0].clientX:e.clientX)-r.left;const i=Math.floor((cx-L)/band);setHov(i>=0&&i<n?i:null);};
      const h=hov!=null?days[hov]:null;
      return(
        <div className="pf2-edplot" ref={ref} tabIndex={0} onMouseMove={move} onMouseLeave={()=>setHov(null)} onTouchStart={move} onTouchMove={move} onBlur={()=>setHov(null)}
          onKeyDown={e=>{const i=hov==null?n-1:hov;let j=null;if(e.key==='ArrowLeft')j=Math.max(0,i-1);else if(e.key==='ArrowRight')j=Math.min(n-1,i+1);else if(e.key==='Home')j=0;else if(e.key==='End')j=n-1;else if(e.key==='Escape')setHov(null);if(j!=null){e.preventDefault();setHov(j);}}}
          aria-label="Daily rewards chart. Use the arrow keys to step through the days.">
          <div className="pf2-sr" aria-live="polite">{h?(hov===n-1?'Today so far':pfeWd(h.t0)+' '+pfeDay(h.t0))+': '+(V.ok(h)?keys.map(k=>V.name(k)+' '+(V.unit==='$'?fmtDollar(V.val(h,k)):pfAbbr(V.val(h,k)))).join(', '):V.why(h)):''}</div>
          {W>0&&<svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} role="img" aria-label={`Rewards earned per day`}>
            {[0,1,2,3,4].map(i=>{const v=mx*i/4,yy=y(v);return(<g key={i}><line x1={L} x2={W-R} y1={yy} y2={yy} stroke={`rgba(255,255,255,${i?0.07:0.18})`} strokeWidth="1"/><text x={L-8} y={yy+4} textAnchor="end" className="ax">{V.fmt(v)}</text></g>);})}
            {days.map((d,i)=>{const cx=L+band*i+band/2,x=cx-bw/2;let acc=0;const good=V.ok(d);const vis=good?keys.filter(k=>V.val(d,k)>0):[];const dim=hov!=null&&i!==hov;
              return(<g key={i} opacity={dim?.78:1}>
                {i===hov&&<rect x={L+band*i+1} y={T} width={Math.max(1,band-2)} height={ih} rx="6" fill="rgba(255,255,255,.05)"/>}
                {!good&&<rect x={x} y={T+ih-3} width={bw} height="3" rx="1.5" fill="rgba(255,255,255,.25)"/>}
                {vis.map((k,j)=>{const v=V.val(d,k),top=j===vis.length-1,yy=y(acc+v),hh=Math.max(0,v/mx*ih-(j>0?2:0));acc+=v;
                  if(!top||hh<1)return <rect key={k} x={x} y={yy} width={bw} height={Math.max(hh,.5)} fill={PFE_C[k]}/>;
                  const r=Math.min(4,bw/2,hh);return <path key={k} d={`M${x},${yy+hh} L${x},${yy+r} Q${x},${yy} ${x+r},${yy} L${x+bw-r},${yy} Q${x+bw},${yy} ${x+bw},${yy+r} L${x+bw},${yy+hh} Z`} fill={PFE_C[k]}/>;})}
                {(i===n-1||(i%Math.max(1,Math.round(n/(phone?3:6)))===0&&i<n-1))&&<text x={cx} y={H-6} textAnchor="middle" className="ax">{i===n-1?'Today':pfeDay(d.t0)}</text>}
              </g>);})}
            {/* round 21b (Shaka): the average's number moved up beside DAILY (pf2-avg) where it reads clearly; the line stays, dashed to match its key */}
            {avg>0&&<line x1={L} x2={W-R} y1={y(avg)} y2={y(avg)} stroke="rgba(255,255,255,.6)" strokeWidth="1.2" strokeDasharray="5 4"/>}
          </svg>}
          {h&&<div className="pf2-edtip" style={phone?{left:'50%',transform:'translateX(-50%)'}:{left:(L+band*hov+band/2)+'px',transform:hov>n/2?'translateX(calc(-100% - 16px))':'translateX(16px)'}}>
            <div className="d">{hov===n-1?'TODAY SO FAR':(pfeWd(h.t0)+' · '+pfeDay(h.t0)).toUpperCase()}</div>
            {!V.ok(h)?<div className="r">{V.why(h)||'Couldn’t be read'}</div>:<>
              {keys.map(k=><div key={k} className="r"><i style={{background:PFE_C[k]}}></i>{V.name(k)}<b>{V.unit==='$'?fmtDollar(V.val(h,k)):pfAbbr(V.val(h,k))}</b><em>{V.unit==='$'?pfAbbr(h[k]||0)+(k==='uf'?' UFO':' PTGC'):fmtDollar(V.usd(h,k))}</em></div>)}
              {keys.length>1&&<div className="r t">Total<b>{V.unit==='$'?fmtDollar(tot(h)):pfAbbr(tot(h))+' '+V.unit}</b><em>{V.unit==='$'?'':fmtDollar(keys.reduce((t,k)=>t+(V.usd(h,k)||0),0))}</em></div>}</>}
          </div>}
        </div>);
    };
    const PfEarnedModal=({tok:tok0,addrs:addrs0,txs,close,prices,wallets,hasUfo=true})=>{
      /* round 25 (audit C10 / C15 / C16): no UFO in the counted wallets → PTGC only (Both / UFO greyed); a wallet picker
         (All wallets · each wallet) — the per-wallet reads are the same cache, so switching is free; 7D / 30D / 90D. */
      const[tok,setTok]=useState(hasUfo?'BOTH':'PTGC');const[hid,setHid]=useState({});
      const[sel,setSel]=useState('all');
      const[nd,setNd]=useState(()=>{try{const v=+localStorage.getItem(PFE_LS_DAYS);return [7,30,90].includes(v)?v:30;}catch(e){return 30;}});
      const addrs=sel==='all'?addrs0:addrs0.filter(a=>a===sel);
      const e=usePfEarned(addrs,true,nd);
      const[px,setPx]=useState(null);useEffect(()=>{pfhPrices().then(setPx).catch(()=>{});},[]);
      const V=pfeView(tok),isU=tok==='UFO',isB=tok==='BOTH',keys0=V.keys,keys=keys0.filter(k=>!hid[k]);
      /* days from the running totals — PTGC and UFO each complete (or not) on their own */
      const priceOf=(t,mid)=>{let p=px?pfhPriceAt(px,t,mid):null;if(p==null&&prices){const s0=px&&px.hourly[t];const lastT=s0&&s0.length?s0[s0.length-1][0]:null;const cur=prices[t==='UFO'?'ufo':'ptgc'];if(lastT!=null&&mid>=lastT&&cur>0)p=cur;}return p;};
      const days=React.useMemo(()=>{if(!e.pts)return null;const out=[];
        /* round 24 (audit B4): UFO flows bucketed per wallet and sorted once; each day then takes its slice with a moving pointer
           (was: a scan of every flow for every wallet × every day on every tick) */
        const fl={},ptr={};if(txs&&txs.flows){txs.flows.forEach(f=>{if(f.tok==='UFO')(fl[f.addr]=fl[f.addr]||[]).push(f);});Object.values(fl).forEach(a=>a.sort((x,y)=>x.t-y.t));}
        for(let i=0;i<e.pts.length-1;i++){const a=e.pts[i],b=e.pts[i+1];const d={t0:a.ts,t1:b.ts,okP:true,okU:true,st:0,lk:0,rf:0,uf:0};
          for(const ad of addrs){const va=a.w[ad],vb=b.w[ad];if(!va||!vb){d.okP=d.okU=false;d.whyP=d.whyU='Couldn’t be read from the chain';break;}
            d.st+=Math.max(0,vb[0]-va[0]);d.lk+=Math.max(0,vb[1]-va[1]);d.rf+=Math.max(0,vb[2]-va[2]);
            if(d.okU){if(!txs||!txs.flows||!pftCovered(txs,ad,'UFO',a.bt)){d.okU=false;d.whyU=!txs||!txs.flows?'Waiting for your transactions…':'Older than the transactions in reach';}
              else{const arr=fl[ad]||[];let j=ptr[ad]||0;while(j<arr.length&&arr[j].t<=a.bt)j++;let net=0;while(j<arr.length&&arr[j].t<=b.bt){net+=arr[j].net;j++;}ptr[ad]=j;d.uf+=Math.max(0,(vb[3]-va[3])-net);}}}
          const mid=Math.min(Date.now(),(a.ts+b.ts)/2);d.pP=priceOf('PTGC',mid);d.pU=priceOf('UFO',mid);
          out.push(d);}
        return out;},[e.pts,txs,px,addrs.join(),prices&&prices.ptgc,prices&&prices.ufo]);
      const chainDone=!!e.pts,needU=tok!=='PTGC';
      const startBt=e.pts&&e.pts[0]?e.pts[0].bt:0;
      const uReady=!!(txs&&txs.flows&&(!txs.busy||addrs.every(ad=>pftCovered(txs,ad,'UFO',startBt))));
      const waiting=e.state!=='failed'&&(!chainDone||(needU&&!uReady));
      const tot=d=>d&&V.ok(d)?keys.reduce((t,k)=>t+V.val(d,k),0):0;
      const okDays=days?days.filter(V.ok):[];
      const sum=k=>okDays.reduce((t,d)=>t+V.val(d,k),0),sumUsd=k=>okDays.reduce((t,d)=>t+(V.usd(d,k)||0),0),sumTok=k=>okDays.reduce((t,d)=>t+(d[k]||0),0);
      const T=keys.reduce((t,k)=>t+sum(k),0),T$=keys.reduce((t,k)=>t+sumUsd(k),0),nOk=Math.max(1,okDays.length);
      let best=null;okDays.forEach(d=>{if(!best||tot(d)>tot(best))best=d;});
      const list=days?days.slice().reverse():[];
      const logo=isU?TOKENS.UFO.logo:TOKENS.PTGC.logo;
      const tabs=<div className="tabs" role="group" aria-label="Token">{['BOTH','PTGC','UFO'].map(t=><button key={t} aria-pressed={tok===t} disabled={!hasUfo&&t!=='PTGC'} title={!hasUfo&&t!=='PTGC'?'No UFO in the counted wallets':undefined} className={tok===t?'on':''} onClick={()=>{setTok(t);setHid({});}}>{t==='BOTH'?<span className="two"><img src={TOKENS.PTGC.logo} alt=""/><img src={TOKENS.UFO.logo} alt=""/></span>:<img src={t==='UFO'?TOKENS.UFO.logo:TOKENS.PTGC.logo} alt=""/>}{t==='BOTH'?'Both':t}</button>)}</div>;
      const dayName=d=>d===list[0]?'Today so far':pfeWd(d.t0)+' '+pfeDay(d.t0);
      const tk=(v,k)=>pfAbbr(v)+(k==='uf'?' UFO':' PTGC');
      /* BOTH: per-token totals for the tiles and the table */
      const pT=d=>['st','lk','rf'].filter(k=>!hid[k]).reduce((t,k)=>t+(d[k]||0),0),uT=d=>hid.uf?0:(d.uf||0);
      const P30=okDays.reduce((t,d)=>t+pT(d),0),P30$=okDays.reduce((t,d)=>t+pT(d)*d.pP,0),U30=okDays.reduce((t,d)=>t+uT(d),0),U30$=okDays.reduce((t,d)=>t+uT(d)*d.pU,0);
      return(
        <PfModal className="z-50 flex items-center justify-center p-2 sm:p-4 bg-black/80" onClose={close} label={`${isB?'PTGC and UFO':tok} rewards, last ${nd} days`}>
          <div className={`pf2-erw${isU?' u':''}${isB?' b':''}`} onClick={ev=>ev.stopPropagation()}>
            <div className="ehd">{isB?<span className="two big"><img src={TOKENS.PTGC.logo} alt=""/><img src={TOKENS.UFO.logo} alt=""/></span>:<img src={logo} alt=""/>}
              <div className="tt"><h2>{isB?'ALL REWARDS':tok+' REWARDS'}</h2><div className="sub">{isB?'PTGC + UFO in dollars':'Earned by source'} {'·'} last {nd} days {'·'} {sel==='all'?'all counted wallets':((wallets&&(wallets.find(w=>w.address.toLowerCase()===sel)||{}).name)||pfAddr(sel))}</div></div>
              <div className="tw">{tabs}</div><button className="x" onClick={close} aria-label="Close">{'×'}</button></div>
            <div className="tm">{tabs}</div>
            <div className="pf2-edsel"><div className="pp" role="group" aria-label="Period">{[7,30,90].map(n=><button key={n} className={nd===n?'on':''} aria-pressed={nd===n} onClick={()=>{setNd(n);try{localStorage.setItem(PFE_LS_DAYS,String(n));}catch(e){}}}>{n}D</button>)}</div>
              {wallets&&wallets.length>1&&<div className="ws"><button className={sel==='all'?'on':''} aria-pressed={sel==='all'} onClick={()=>setSel('all')}>All wallets</button>{wallets.map(w=>{const a=w.address.toLowerCase();if(!addrs0.includes(a))return null;return <button key={a} className={sel===a?'on':''} aria-pressed={sel===a} onClick={()=>setSel(a)}>{w.name||pfAddr(w.address)}</button>;})}</div>}</div>
            {/* round 22 (Shaka: "we need like a big loading thing so people realize it and wait"): one big loader until
                everything this tab needs is in — the 30 days of chain reads, and (Both / UFO) the UFO transfers back to 30 days */}
            {waiting&&<div className="pf2-edload" role="status" aria-live="polite">
              <div className="orb"><span className="ring"></span><span className="ring r2"></span>{isB?<span className="two big"><img src={TOKENS.PTGC.logo} alt=""/><img src={TOKENS.UFO.logo} alt=""/></span>:<img src={logo} alt=""/>}</div>
              <div className="h">Crunching your last {nd} days{'…'}</div>
              <div className="p">This takes a little while the first time {'—'} after that it opens almost instantly.</div>
              <div className="steps">
                <div className={`st${chainDone?' ok':' on'}`}><i>{chainDone?'✓':'1'}</i><span>Daily reward totals from the chain</span><b>{chainDone?'done':Math.round(e.progress*100)+'%'}</b></div>
                {needU&&<div className={`st${uReady?' ok':' on'}`}><i>{uReady?'✓':'2'}</i><span>Your UFO transfers from PulseScan</span><b>{uReady?'done':!txs?'starting…':(txs.pages||0)+' page'+((txs.pages||0)===1?'':'s')+' read'}</b></div>}
              </div>
              <div className="bar"><i style={{width:Math.max(6,Math.min(100,((chainDone?1:e.progress)*(needU?.6:1)+(needU?(uReady?.4:Math.min(.36,((txs&&txs.pages)||0)*.04)):0))*100))+'%'}}></i></div>
            </div>}
            {e.state==='failed'&&!e.pts&&<div className="pf2-hwait" style={{height:200}}><div>Couldn{'’'}t read the last {nd} days right now.</div><button className="pf2-lnk" onClick={e.retry}>Retry</button></div>}
            {days&&!waiting&&<>
              {isB?<div className="sum">
                  <div className="tl tot"><div className="l">Earned {'·'} {nd} days</div><div className="v">{fmtDollar(T)}</div><div className="s">PTGC + UFO</div><div className="a">{'≈'} {fmtDollar(T/nOk)} a day</div></div>
                  <div className="tl rf"><div className="l"><img src={TOKENS.PTGC.logo} alt=""/>PTGC</div><div className="v">{fmtDollar(P30$)}</div><div className="s">{pfAbbr(P30)} PTGC</div><div className="a">staking + locking + reflections</div><b className="bar" style={{width:(T>0?P30$/T*100:0)+'%',background:'#E8BE3F'}}></b></div>
                  <div className="tl uf"><div className="l"><img src={TOKENS.UFO.logo} alt=""/>UFO</div><div className="v">{fmtDollar(U30$)}</div><div className="s">{pfAbbr(U30)} UFO</div><div className="a">reflections</div><b className="bar" style={{width:(T>0?U30$/T*100:0)+'%',background:'#7CFC00'}}></b></div>
                  <div className="tl best"><span className="ico" aria-hidden="true">{'\u{1F3C6}'}</span><div className="l">Best day</div><div className="v">{best?fmtDollar(tot(best)):'—'}</div><div className="s">{best?pfeWd(best.t0)+' '+pfeDay(best.t0):''}</div><div className="a">{okDays.length<nd?`${okDays.length} of ${nd} days in reach`:`last ${nd} days`}</div></div></div>
              :<div className={`sum${isU?' one':''}`}>
                <div className="tl tot"><div className="l">Earned {'·'} {nd} days</div><div className="v">{pfAbbr(T)} {tok}</div><div className="s">{fmtDollar(T$)}</div><div className="a">{'≈'} {pfAbbr(T/nOk)} a day {'·'} {fmtDollar(T$/nOk)}</div></div>
                {isU?<>
                  <div className="tl uf"><div className="l"><i style={{background:PFE_C.uf}}></i>Daily average</div><div className="v">{pfAbbr(T/nOk)}</div><div className="s">{fmtDollar(T$/nOk)}</div><div className="a">per day{okDays.length<nd?` · ${okDays.length} days in reach`:`, last ${nd} days`}</div></div>
                  <div className="tl uf best"><span className="ico" aria-hidden="true">{'\u{1F3C6}'}</span><div className="l">Best day</div><div className="v">{best?pfAbbr(tot(best)):'—'}</div><div className="s">{best&&best.pU!=null?fmtDollar(tot(best)*best.pU):'—'}</div><div className="a">{best?pfeWd(best.t0)+' '+pfeDay(best.t0):''}</div></div>
                </>:keys0.map(k=>{const v=sum(k);return(<div key={k} className={`tl ${k}`}><div className="l"><i style={{background:PFE_C[k]}}></i>{PFE_N[k]}</div><div className="v">{pfAbbr(v)}</div><div className="s">{fmtDollar(sumUsd(k))}</div><div className="a">{'≈'} {pfAbbr(v/nOk)} a day</div><b className="bar" style={{width:(T>0&&!hid[k]?v/T*100:0)+'%',background:PFE_C[k]}}></b></div>);})}
              </div>}
              <div className="ch"><div className="chh"><b>DAILY{isB?' · IN DOLLARS':''}</b>
                {okDays.length>0&&<span className="pf2-avg" title="Average per day over the days shown (the dashed line)"><i></i>Avg <b>{isB?fmtDollar(T/nOk):pfAbbr(T/nOk)+' '+tok}</b> / day</span>}{e.state==='loading'&&<span className="upd">updating{'…'}</span>}
                {keys0.length>1&&<div className="lg">{keys0.map(k=><button key={k} className={hid[k]?'off':''} aria-pressed={!hid[k]} onClick={()=>setHid(h=>{const n={...h,[k]:!h[k]};return keys0.every(x=>n[x])?h:n;})}><i style={{background:PFE_C[k]}}></i>{V.name(k)}</button>)}</div>}</div>
                <PfEdChart days={days} keys={keys} V={V}/></div>
              {/* round 21 (Shaka): every day in one list that scrolls on its own (a styled scroll bar on the right), no "show all" */}
              <div className="tbh"><b>BY DAY</b><span>newest first {'·'} {list.length} days {'·'} scroll for more</span></div>
              <div className="pf2-dtw"><div className="dts"><table className="dt"><thead><tr><th>DAY</th>
                  {isB?<><th><i style={{background:'#E8BE3F'}}></i>PTGC</th><th><i style={{background:PFE_C.uf}}></i>UFO</th></>:keys.map(k=><th key={k}><i style={{background:PFE_C[k]}}></i>{PFE_N[k].toUpperCase()}</th>)}
                  {!isB&&keys.length>1&&<th>TOTAL</th>}<th>VALUE</th></tr></thead>
                <tbody>{list.map(d=><tr key={d.t0} className={d===best?'best':''}><td className="dd">{dayName(d)}{d===best&&<span className="bd">BEST DAY</span>}</td>
                  {V.ok(d)?(isB?<><td>{pfAbbr(pT(d))}<small>{fmtDollar(pT(d)*d.pP)}</small></td><td>{pfAbbr(uT(d))}<small>{fmtDollar(uT(d)*d.pU)}</small></td><td className="tt">{fmtDollar(tot(d))}</td></>
                    :<>{keys.map(k=><td key={k}>{pfAbbr(V.val(d,k))}</td>)}{keys.length>1&&<td className="tt">{pfAbbr(tot(d))}</td>}<td className="tt">{fmtDollar(keys.reduce((t,k)=>t+(V.usd(d,k)||0),0)||null)}</td></>)
                    :<td colSpan={isB?3:keys.length+(keys.length>1?2:1)} className="na">{V.why(d)}</td>}</tr>)}</tbody></table></div></div>
              <div className="dl">{list.map(d=>{const t=tot(d);const good=V.ok(d);return(<div key={d.t0} className={d===best?'best':''}><span className="d">{dayName(d)}</span>
                {good?<><span className="t">{isB?fmtDollar(t):pfAbbr(t)} {!isB&&<small>{fmtDollar(keys.reduce((a,k)=>a+(V.usd(d,k)||0),0)||null)}</small>}</span>
                  {keys.length>1&&<><div className="mini">{keys.map(k=><b key={k} style={{width:(t>0?V.val(d,k)/t*100:0)+'%',background:PFE_C[k]}}></b>)}</div>
                  <div className="k">{isB?<><span><i style={{background:'#E8BE3F'}}></i>{pfAbbr(pT(d))} PTGC</span><span><i style={{background:PFE_C.uf}}></i>{pfAbbr(uT(d))} UFO</span></>:keys.map(k=><span key={k}><i style={{background:PFE_C[k]}}></i>{pfAbbr(V.val(d,k))}</span>)}</div></>}</>
                  :<span className="t na">{V.why(d)}</span>}</div>);})}</div>
              <div className="fn">{isB?<>Everything in <b>dollars</b>, since PTGC and UFO can{'’'}t share a token scale. <b>PTGC</b> = staking + locking (counted as they build up each day, claimed or not) + reflections; <b>UFO</b> = reflections. Pick PTGC or UFO above for token amounts.</>
                :isU?<><b>Reflections</b> each day = the day{'’'}s change in your UFO balance, minus everything bought, sold or moved that day (the hidden 1% added back). They land in your wallet automatically.</>
                :<><b>Staking</b> and <b>locking</b> count rewards as they build up each day (claimed + waiting to be claimed), not only on the day you claim. <b>Reflections</b> come from PTGC{'’'}s own totals of what each wallet sent and received.</>} Days run midnight to midnight in your local time; dollar values use that day{'’'}s price.</div>
            </>}
          </div>
        </PfModal>);
    };
