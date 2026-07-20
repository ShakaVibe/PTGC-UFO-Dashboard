// build-value-generated.mjs
// Prebuilds data/value-generated.json for the UFO dashboard's "Value Generated" and
// "PTGC burned by UFO" boxes. It runs the SAME two on-chain scans the dashboard runs live
// (fetchRealizedFees + fetchDeliveredValue), lifted verbatim from index.html, so the numbers
// match. The site then reads this file instead of scanning on every visit.
//
// Guards: writes ONLY when both scans succeed; on any failure it leaves the existing file
// untouched (carry forward last good), and stamps meta.{generatedAt,headBlock,ufoAddress}.
//
// Node 22+ (global fetch / AbortController). ESM so it runs regardless of repo package.json.
import fs from 'node:fs';
const OUT_PATH = process.env.OUT_PATH || 'data/value-generated.json';

// ===== lifted from index.html: RPC + rpcFetch =====
    const RPC='https://rpc.pulsechain.com';
    const MIN_LIQ=1000;
    
    // Simple RPC fetch with timeout
    const rpcFetch=async(body,timeout=8000)=>{
      try{
        const controller=new AbortController();
        const timeoutId=setTimeout(()=>controller.abort(),timeout);
        const res=await fetch(RPC,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:controller.signal});
        clearTimeout(timeoutId);
        return await res.json();
      }catch(e){
        console.error('RPC error:',e.message);
        return{result:null};
      }
    };

// ===== lifted from index.html: eth_call + address helpers =====
    const ethCallRead=async(to,data)=>{
      const r=await rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to,data},'latest'],id:1});
      return (r&&r.result&&r.result!=='0x')?r.result:null;
    };
    const wordToAddress=w=>(w&&w.length>=42)?('0x'+w.slice(-40)):null;
    const encodeAddress=a=>a.slice(2).toLowerCase().padStart(64,'0');
    const isZeroAddress=a=>!a||/^0x0{40}$/i.test(a);

// ===== lifted from index.html: topics, block timing, log-chunking, fee timeline, boundaries, exemption =====
    const TRANSFER_TOPIC='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
    const FEES_UPDATED_TOPIC='0x020b4e17880b9764de4da2ebf8857a187cc492ae288e9f3ec0db3e2fdb37a2ec';
    /* Do NOT assume a block time. If the real one is faster than the guess, every window
       starts too late and we silently undercount fee events. Measure it from two block
       timestamps instead; fall back to 10s only if the RPC won't answer. */
    const BLOCKS_PER_DAY_FALLBACK=8640;   // PulseChain nominal ~10s
    const PERIOD_DAYS={'24h':1,'7d':7,'30d':30,'90d':90};
    let chainTiming=null; // {secPerBlock, blocksPerDay}

    const getChainTiming=async(headBlock)=>{
      if(chainTiming)return chainTiming;
      try{
        const back=Math.max(1,headBlock-5000);
        const[h1,h2]=await Promise.all([
          rpcFetch({jsonrpc:'2.0',method:'eth_getBlockByNumber',params:['0x'+headBlock.toString(16),false],id:2}),
          rpcFetch({jsonrpc:'2.0',method:'eth_getBlockByNumber',params:['0x'+back.toString(16),false],id:3})
        ]);
        const t1=parseInt(h1&&h1.result&&h1.result.timestamp||'0x0',16);
        const t2=parseInt(h2&&h2.result&&h2.result.timestamp||'0x0',16);
        const span=headBlock-back;
        if(t1&&t2&&t1>t2&&span>0){
          const spb=(t1-t2)/span;
          if(spb>=0.5&&spb<=60){
            chainTiming={secPerBlock:spb,blocksPerDay:Math.round(86400/spb)};
            console.log(`Measured block time: ${spb.toFixed(2)}s -> ${chainTiming.blocksPerDay} blocks/day`);
            return chainTiming;
          }
        }
      }catch(e){console.warn('block-time probe failed:',e.message);}
      chainTiming={secPerBlock:10,blocksPerDay:BLOCKS_PER_DAY_FALLBACK};
      console.warn('Using fallback block time of 10s');
      return chainTiming;
    };

    // ~5 minute cache bucket, wall-clock (independent of block time)
    const cacheBucket=()=>Math.floor(Date.now()/(5*60*1000));
    const LOG_CHUNK=10000;
    const MAX_LOG_RANGES=100;
    /* RPC log caps are almost always round numbers. A result of EXACTLY one of these,
       or any very full batch, may have been silently truncated. Split and refetch. */
    const LOG_CAP_SUSPECTS=[100,128,200,250,256,500,512,1000,1024,2000,2048,4096,5000,10000];
    const looksTruncated=(n)=>n>=900||LOG_CAP_SUSPECTS.indexOf(n)>=0;
    let lastLogError=null;
    // Constructor sets every fee to 100 bps. Rates before the first FeesUpdated event.
    const DEFAULT_FEE_RATES={reflection:100,ufoBurn:100,ptgcBurn:100,plsLP:100,plsxLP:100,wethLP:100};

    // BigInt -> token float without blowing through Number's 2^53 precision.
    /* CAUTION: do NOT write 10n**12n here. Babel (which compiles this page in-browser via
       type="text/babel") transpiles the ** operator into Math.pow(), and Math.pow throws
       "Cannot convert a BigInt value to a number" on BigInt operands. Use a literal. */
    const WEI_SCALE_1E12=1000000000000n;
    const weiToTokens=(bg)=>Number(bg/WEI_SCALE_1E12)/1e6;

    /* Public RPCs cap eth_getLogs by block span AND by result size, and they don't agree
       on the limits. So: try a range; if it fails, halve it and retry, down to 250 blocks.
       On total failure record WHY, so the UI can say "chain read failed" instead of
       silently pretending there's no data. Silence is what made the last two bugs invisible. */
    const getLogsRange=async(address,topics,a,b,depth,headBlock)=>{
      const toParam=(b>=headBlock)?'latest':('0x'+b.toString(16));
      const r=await rpcFetch({jsonrpc:'2.0',method:'eth_getLogs',
        params:[{address,fromBlock:'0x'+a.toString(16),toBlock:toParam,topics}],id:1},20000);
      if(r&&Array.isArray(r.result)){
        /* Public RPCs silently CAP the number of logs returned — no error, just fewer
           rows. A suspiciously full batch is therefore untrustworthy: split and refetch
           until each slice is comfortably under any cap. Silent truncation is how we
           lost 10% of swap legs. */
        if(looksTruncated(r.result.length)&&(b-a)>1&&depth<14){
          const mid=Math.floor((a+b)/2);
          const left=await getLogsRange(address,topics,a,mid,depth+1,headBlock);
          if(left===null)return null;
          const right=await getLogsRange(address,topics,mid+1,b,depth+1,headBlock);
          if(right===null)return null;
          return left.concat(right);
        }
        return r.result;
      }
      const msg=(r&&r.error&&r.error.message)||'no result field';
      if(depth<6&&(b-a)>250){
        const mid=Math.floor((a+b)/2);
        const left=await getLogsRange(address,topics,a,mid,depth+1,headBlock);
        if(left===null)return null;
        const right=await getLogsRange(address,topics,mid+1,b,depth+1,headBlock);
        if(right===null)return null;
        return left.concat(right);
      }
      lastLogError=`eth_getLogs failed (blocks ${a}-${b}): ${msg}`;
      console.warn(lastLogError);
      return null;
    };

    /* SPEED. Four of the scans below are byte-for-byte identical across
       fetchDeliveredValue, fetchBurnPeriodsOnChain and fetchPtgcBurnedByUfo — same
       address, same topics, same block range — because they all clamp to
       max(90d boundary, launch). Each was being fetched twice.

       Memoise on the full query, INCLUDING the 5-minute cache bucket so data still
       refreshes. Store the in-flight promise, not just the result, so two callers
       racing the same query share one round trip instead of issuing two.

       Failures are never cached: a null must stay retryable, and caching it would
       turn one transient RPC hiccup into five minutes of "chain read failed". */
    const logsInflight={};
    const getLogsChunked=async(address,topics,fromBlock,toBlock)=>{
      if(toBlock<fromBlock)return[];
      const key=`${address}|${JSON.stringify(topics)}|${fromBlock}|${toBlock}|${cacheBucket()}`;
      if(logsInflight[key])return logsInflight[key];
      const p=_getLogsChunked(address,topics,fromBlock,toBlock);
      logsInflight[key]=p;
      p.then(r=>{if(r===null)delete logsInflight[key];},()=>{delete logsInflight[key];});
      return p;
    };

    const _getLogsChunked=async(address,topics,fromBlock,toBlock)=>{
      if(toBlock<fromBlock)return[];
      const ranges=[];
      for(let s=fromBlock;s<=toBlock;s+=LOG_CHUNK)ranges.push([s,Math.min(s+LOG_CHUNK-1,toBlock)]);
      if(ranges.length>MAX_LOG_RANGES){
        lastLogError=`window too large: ${ranges.length} ranges (max ${MAX_LOG_RANGES})`;
        console.warn(lastLogError);
        return null;
      }
      const out=[];const CONC=3;
      for(let i=0;i<ranges.length;i+=CONC){
        const res=await Promise.all(ranges.slice(i,i+CONC).map(([a,b])=>getLogsRange(address,topics,a,b,0,toBlock)));
        for(const r of res){ if(r===null)return null; out.push(...r); }
      }
      return out;
    };

    /* FeesUpdated carries SEVEN uint256 words; only six are buckets. Which slot
       holds the total is not something we can verify from the ABI we have, and a
       one-word shift silently misattributes EVERY bucket. So don't assume: the
       total must equal the sum of the other six, which makes the layout
       self-identifying. If neither candidate holds, throw. A thrown error
       surfaces as "couldn't read fees from chain"; a wrong guess surfaces as a
       plausible number that is wrong forever. */
    const decodeFeesUpdated=(data)=>{
      const h=data.startsWith('0x')?data.slice(2):data;
      const n=Math.floor(h.length/64);
      const w=i=>Number(BigInt('0x'+h.slice(i*64,(i+1)*64)));
      const words=[];for(let i=0;i<n;i++)words.push(w(i));
      const shape=a=>({reflection:a[0],ufoBurn:a[1],ptgcBurn:a[2],plsLP:a[3],plsxLP:a[4],wethLP:a[5]});
      const sum=a=>a.reduce((x,y)=>x+y,0);
      if(n===6)return shape(words);
      if(n===7){
        const lead=words.slice(0,6), trail=words.slice(1,7);
        if(words[6]===sum(lead))return shape(lead);   // (buckets…, total)
        if(words[0]===sum(trail))return shape(trail); // (total, buckets…)
      }
      throw new Error(`FeesUpdated layout not recognised (${n} words, no self-consistent total) — refusing to guess fee rates`);
    };

    /* Returns null on failure. NEVER `|| []` — a failed query and "there were no
       fee changes" must not be the same value. If this silently returned [], every
       fee transfer would be attributed with DEFAULT_FEE_RATES and the bucket split
       would be wrong forever, with ok:true. See handoff section 8.4.
       The 0x0->latest fast path is also the query most likely to be silently
       capped, so its result is truncation-checked like any other. */
    const fetchFeeTimeline=async(tokenAddress,fromBlock,toBlock)=>{
      let arr=null;
      const full=await rpcFetch({jsonrpc:'2.0',method:'eth_getLogs',
        params:[{address:tokenAddress,fromBlock:'0x0',toBlock:'latest',topics:[FEES_UPDATED_TOPIC]}],id:1},20000);
      if(full&&Array.isArray(full.result)&&!looksTruncated(full.result.length))arr=full.result;
      else arr=await getLogsChunked(tokenAddress,[FEES_UPDATED_TOPIC],fromBlock,toBlock);
      if(arr===null)return null;
      return arr.map(l=>({block:parseInt(l.blockNumber,16),rates:decodeFeesUpdated(l.data)}))
                .sort((a,b)=>a.block-b.block);
    };

    const ratesAtBlock=(events,block,fallback)=>{
      let r=fallback;
      for(const e of events){ if(e.block<=block)r=e.rates; else break; }
      return r;
    };

    /* Counting blocks (blocksPerDay * days) is an ESTIMATE — any drift in block time
       stretches or shrinks the window. A 29h "24H" window overstates fees by 21%.
       So: find each window's boundary by BINARY SEARCH on real block timestamps.
       Then scan ONCE and bucket the logs against those boundaries, which makes
       24h <= 7d <= 30d <= 90d true by construction rather than by coincidence. */
    const blockTsCache={};
    /* A boundary search makes ~20 sequential reads. rpcFetch returns {result:null} on any
       network hiccup, and findBlockAtTime (correctly) refuses to guess a boundary from a
       failed read — so ONE flake out of twenty used to surface as "could not read block
       timestamps" and a RETRY button. Retrying is the machine's job. Three attempts with
       backoff; only then do we admit defeat, and we say which block failed. */
    const sleep=ms=>new Promise(r=>setTimeout(r,ms));
    const getBlockTs=async(b)=>{
      if(blockTsCache[b]!=null)return blockTsCache[b];
      for(let attempt=0;attempt<3;attempt++){
        if(attempt)await sleep(200*attempt);
        const r=await rpcFetch({jsonrpc:'2.0',method:'eth_getBlockByNumber',params:['0x'+b.toString(16),false],id:1});
        const t=parseInt((r&&r.result&&r.result.timestamp)||'0x0',16);
        if(t){blockTsCache[b]=t;return t;}
      }
      console.warn(`eth_getBlockByNumber failed 3x for block ${b}`);
      return 0;
    };

    // smallest block whose timestamp >= targetSec. Returns null if the chain
    // won't answer — a wrong boundary is worse than no boundary.
    const findBlockAtTime=async(targetSec,headBlock,headTs,spb)=>{
      if(targetSec>=headTs)return headBlock;
      const guess=headBlock-Math.round((headTs-targetSec)/spb);
      const pad=Math.max(5000,Math.abs(headBlock-guess)*0.4);
      let lo=Math.max(0,Math.floor(guess-pad));
      let hi=Math.min(headBlock,Math.ceil(guess+pad));
      const tLo=await getBlockTs(lo);
      if(tLo&&tLo>targetSec)lo=0;                 // guess was too late; widen down
      const tHi=await getBlockTs(hi);
      if(!tHi||tHi<targetSec)hi=headBlock;        // guess was too early; widen up
      let ans=hi;
      while(lo<=hi){
        const mid=Math.floor((lo+hi)/2);
        const t=await getBlockTs(mid);
        if(!t)return null;
        if(t>=targetSec){ans=mid;hi=mid-1;}else{lo=mid+1;}
      }
      return ans;
    };

    let boundariesCache=null;
    /* SPEED: this used to run four binary searches back to back — ~20 sequential
       eth_getBlockByNumber round trips each, ~80 before a single log was fetched.
       On a young token, three of those four boundaries reach back past the token's
       birth and get discarded by max(B[p],launch) at the call site anyway. So:
       resolve the launch block first, answer those three for free, and run only
       the searches that can actually land inside the token's life — in parallel.
       On a 2-day-old token this is one search instead of four. */
    const getPeriodBoundaries=async(headBlock,firstPoolMs)=>{
      const key=`${cacheBucket()}-${firstPoolMs||0}`;
      if(boundariesCache&&boundariesCache.key===key)return boundariesCache.v;
      const headTs=await getBlockTs(headBlock);
      if(!headTs)return null;
      const{secPerBlock}=await getChainTiming(headBlock);
      const launch=estimateLaunchBlock(headBlock,firstPoolMs,secPerBlock);
      const launchTs=launch>0?await getBlockTs(launch):0;

      const DAYS={'24h':1,'7d':7,'30d':30,'90d':90};
      const v={headBlock,headTs,secPerBlock,launch};
      const pending=[];
      for(const p of PERIOD_KEYS){
        const target=headTs-DAYS[p]*86400;
        if(launchTs&&target<=launchTs)v[p]=launch;   // window predates the token
        else pending.push([p,target]);
      }
      const found=await Promise.all(pending.map(([,t])=>findBlockAtTime(t,headBlock,headTs,secPerBlock)));
      for(let i=0;i<pending.length;i++){
        if(found[i]===null)return null;              // never guess a boundary
        v[pending[i][0]]=found[i];
      }
      boundariesCache={key,v};
      console.log(`Period boundaries by timestamp | head ${headBlock} | launch>=${launch} | ${pending.length} search(es), ${PERIOD_KEYS.length-pending.length} resolved to launch | 24h>=${v['24h']} 7d>=${v['7d']} 30d>=${v['30d']} 90d>=${v['90d']}`);
      return v;
    };

    const PERIOD_KEYS=['24h','7d','30d','90d'];
    const mkFeeAcc=()=>({reflection:0,ufoBurn:0,ptgcBurn:0,plsLP:0,plsxLP:0,wethLP:0});

    const realizedFeeCache={};

    /* A token can't have emitted logs before it existed. Clamping every scan to the
       token's launch block means even a 90-day window on a day-old token costs one
       small query instead of 777,600 blocks. */
    const estimateLaunchBlock=(currentBlock,firstPoolMs,secPerBlock)=>{
      if(!firstPoolMs||!isFinite(firstPoolMs))return 0;
      const ageSec=Math.max(0,(Date.now()-firstPoolMs)/1000);
      // 15% slack + 5000 blocks. Starting too EARLY costs one extra query; starting too
      // LATE silently drops fee events, which is the far worse failure.
      const blocks=Math.ceil((ageSec/secPerBlock)*1.15)+5000;
      return Math.max(0,currentBlock-blocks);
    };

    /* Which addresses does the contract not tax? A tax leg can never originate
       from an exempt sender, because an exempt transfer pays no tax. That single
       fact identifies the impostors we cannot spot structurally.
       null means "we don't know" and is never treated as false. */
    const exemptCache={};
    const isExemptFromFee=async(tokenAddress,addr)=>{
      const k=`${tokenAddress}|${addr}`;
      if(exemptCache[k]!==undefined)return exemptCache[k];
      const r=await ethCallRead(tokenAddress,SEL_IS_EXCLUDED_FROM_FEE+encodeAddress(addr));
      const v=(r===null)?null:(BigInt(r)!==BigInt(0));
      exemptCache[k]=v;
      return v;
    };

// ===== lifted from index.html: burn topic + pair/selector constants =====
    const BURN_TOPIC_PADDED='0x0000000000000000000000000000000000000000000000000000000000000369';
    const SEL_IS_EXCLUDED_FROM_FEE='0x5342acb4'; // isExcludedFromFee(address)
    const SEL_OWNER='0x8da5cb5b';                // owner()
    /* A transfer touching a pool is NOT necessarily a swap — adding or removing
       liquidity moves tokens to/from the pair too. The pair tells us which:
       Swap for a trade, Mint for adding liquidity, Burn for removing it. */
    const PAIR_SWAP_TOPIC='0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822';
    /* PulseX's pair is NOT a straight Uniswap V2 fork here: its Mint carries a 4th arg.
         UniV2:   Mint(address,uint256,uint256)
         PulseX:  Mint(address,uint256,uint256,address)
       Different signature => different topic. Filtering on the UniV2 hash silently
       matched nothing, which is why "0 liquidity moves" looked true. Accept both. */
    const PAIR_MINT_TOPIC='0x4c209b5fc8ad50758f13e2e1088ba56a560dff690a1c6fef26394f4c03821c4f';
    const PAIR_MINT_TOPIC_PULSEX='0xdbba30eb0402b389513e87f51f4db2db80bed454384ec6925a24097c3548a02a';
    const PAIR_BURN_TOPIC='0xdccd412f0b1252819cb1fd330b93224ca42612892bb3f4f789976e6d81936496';
    const SEL_TOKEN0='0x0dfe1681';       // token0()
    const SEL_MAX_SLIPPAGE='0x8c04166f'; // maxSlippage()
    const SEL_SWAP_THRESHOLD='0x0445b667'; // swapThreshold()
    /* The contract wraps every swapback action in try/catch and emits this on failure.
       If addPLSLiquidity is reverting, the LP portion of the fee never reaches a pool. */
    const SWAPBACK_FAILED_TOPIC='0xe2cc6589fa66f3a1443517f47ba01474cfe9d23a5177fb4d49653a45468209d3';

// ===== lifted from index.html: fetchRealizedFees =====
    const fetchRealizedFees=async(tokenAddress,firstPoolMs)=>{
      lastLogError=null;
      try{
        const blk=await rpcFetch({jsonrpc:'2.0',method:'eth_blockNumber',params:[],id:1});
        if(!blk.result)return{ok:false,error:'could not read current block'};
        const cur=parseInt(blk.result,16);
        const key=`${tokenAddress}-fees-${cacheBucket()}`;
        if(realizedFeeCache[key])return realizedFeeCache[key];

        const B=await getPeriodBoundaries(cur,firstPoolMs);
        if(!B)return{ok:false,error:'could not read block timestamps'};
        const launch=B.launch;
        const scanFrom=Math.max(0,B['90d'],launch);

        const contractTopic='0x'+encodeAddress(tokenAddress);
        const[transferLogs,feeEvents]=await Promise.all([
          getLogsChunked(tokenAddress,[TRANSFER_TOPIC,null,contractTopic],scanFrom,cur),
          fetchFeeTimeline(tokenAddress,scanFrom,cur)
        ]);
        if(!transferLogs)return{ok:false,error:lastLogError||'chain read failed'};
        if(!feeEvents)return{ok:false,error:lastLogError||'could not read fee-change history'};

        /* ---- parse every inbound leg ---- */
        const rows=[];
        for(const log of transferLogs){
          if(!log.topics||log.topics.length<3)continue;
          const b=parseInt(log.blockNumber,16);
          const r=ratesAtBlock(feeEvents,b,DEFAULT_FEE_RATES);
          const contractBps=r.ufoBurn+r.ptgcBurn+r.plsLP+r.plsxLP+r.wethLP;
          if(contractBps<=0)continue;   // nothing routes to the contract at these rates
          rows.push({
            block:b,
            tx:log.transactionHash,
            from:('0x'+log.topics[1].slice(26)).toLowerCase(),
            tokens:weiToTokens(BigInt(log.data&&log.data!=='0x'?log.data:'0x0')),
            rates:r,
            contractBps:contractBps,
            totalBps:contractBps+r.reflection,
            drop:null    // null = counted as a fee. string = why it was excluded.
          });
        }

        /* ---- (a) direct sends from taxed wallets: two legs, one tx, one sender ----
           A PAIR can legitimately emit several fee legs in one transaction: an arb or
           multi-hop route hits the same pool more than once, and each taxed leg emits
           Transfer(pair -> contract, fee). Their ratio is just the ratio of the two
           trades, so it is arbitrary. Flagging those as "not understood" was noise:
           33 of them on the first run. Pairs are known; exclude them from the test. */
        const pairSet={};
        (Array.isArray(HARDCODED_UFO_PAIRS)?HARDCODED_UFO_PAIRS:[]).forEach(p=>{
          if(p&&p.address)pairSet[p.address.toLowerCase()]=true;
        });
        const groups={};
        for(const row of rows){
          if(pairSet[row.from])continue;   // multiple trades in one tx, not a direct send
          const k=`${row.tx}|${row.from}`;
          if(!groups[k])groups[k]=[];
          groups[k].push(row);
        }
        let directSendCount=0,directSendTokens=0,unclassifiedGroups=0;
        for(const k of Object.keys(groups)){
          const legs=groups[k];
          if(legs.length<2)continue;
          if(legs.length>2){unclassifiedGroups++;continue;}
          const sorted=legs.slice().sort((a,b)=>b.tokens-a.tokens);
          const principal=sorted[0],fee=sorted[1];
          if(principal.tokens<=0)continue;
          const expected=principal.contractBps/(10000-principal.totalBps);
          const actual=fee.tokens/principal.tokens;
          if(Math.abs(actual-expected)/expected<0.01){
            principal.drop='direct send: principal, not a fee';
            directSendCount++;directSendTokens+=principal.tokens;
          }else{
            /* Two same-sender inbound legs that do not match the tax ratio. We do
               not understand this, so we do not silently drop it. Count it, and
               say on screen that we could not classify it. Silence is what hid
               the last three bugs. */
            unclassifiedGroups++;
          }
        }

        /* ---- (b) single legs from fee-exempt senders ---- */
        const surviving=rows.filter(r=>!r.drop);
        const bySender={};
        for(const r of surviving)bySender[r.from]=(bySender[r.from]||0)+r.tokens;
        const liveTotal=surviving.reduce((s,r)=>s+r.tokens,0);
        const ranked=Object.keys(bySender).sort((a,b)=>bySender[b]-bySender[a]);
        const toCheck=[];let covered=0;
        for(const a of ranked){
          if(liveTotal>0&&(liveTotal-covered)/liveTotal<0.005)break;  // remainder is noise
          if(toCheck.length>=25)break;                                // bounded cost
          toCheck.push(a);covered+=bySender[a];
        }
        const verdicts=await Promise.all(toCheck.map(a=>isExemptFromFee(tokenAddress,a)));
        const exemptSenders=[];let exemptTokens=0,unknownSenders=0;
        toCheck.forEach((a,i)=>{
          if(verdicts[i]===true){exemptSenders.push(a);exemptTokens+=bySender[a];}
          else if(verdicts[i]===null)unknownSenders++;
        });
        const exemptSet={};exemptSenders.forEach(a=>{exemptSet[a]=true;});
        for(const r of rows){
          if(!r.drop&&exemptSet[r.from])r.drop='sender is fee-exempt: cannot originate a tax leg';
        }
        const uncheckedShare=liveTotal>0?Math.max(0,(liveTotal-covered)/liveTotal):0;

        /* ---- accumulate what survives ---- */
        const accs={},counts={},changes={};
        PERIOD_KEYS.forEach(p=>{accs[p]=mkFeeAcc();counts[p]=0;changes[p]=0;});
        for(const row of rows){
          if(row.drop)continue;
          const r=row.rates,cb=row.contractBps,cFee=row.tokens;
          for(const p of PERIOD_KEYS){
            if(row.block<B[p])continue;         // outside this window
            const a=accs[p];
            a.reflection+=cFee*(r.reflection/cb);
            a.ufoBurn   +=cFee*(r.ufoBurn/cb);
            a.ptgcBurn  +=cFee*(r.ptgcBurn/cb);
            a.plsLP     +=cFee*(r.plsLP/cb);
            a.plsxLP    +=cFee*(r.plsxLP/cb);
            a.wethLP    +=cFee*(r.wethLP/cb);
            counts[p]++;
          }
        }
        /* Fee changes INSIDE each window, not globally. The old `live.feeChanges`
           read undefined because feeChanges lived on the parent object, so the
           "N fee changes in window" notice never once rendered. */
        for(const e of feeEvents)for(const p of PERIOD_KEYS)if(e.block>=B[p])changes[p]++;

        const droppedTotal=rows.filter(r=>r.drop).reduce((s,r)=>s+r.tokens,0);
        const excluded={
          directSendCount:directSendCount,
          directSendTokens:directSendTokens,
          exemptSenders:exemptSenders,
          exemptTokens:exemptTokens,
          unclassifiedGroups:unclassifiedGroups,
          unknownSenders:unknownSenders,
          uncheckedShare:uncheckedShare,
          droppedTotal:droppedTotal,
          // A tx with several taxed transfers from one sender is a normal multicall bundle,
          // not an anomaly. Only a ratio MATCH means anything. Don't cry wolf.
          any:(directSendCount>0||exemptSenders.length>0||unknownSenders>0)
        };

        /* Four window-start timestamps, resolved together instead of one after another. */
        const startTsByPeriod={};
        await Promise.all(PERIOD_KEYS.map(async p=>{startTsByPeriod[p]=await getBlockTs(Math.max(B[p],scanFrom));}));
        const byPeriod={};
        for(const p of PERIOD_KEYS){
          const startTs=startTsByPeriod[p];
          byPeriod[p]={
            tokens:accs[p],
            totalTokens:Object.values(accs[p]).reduce((a,b)=>a+b,0),
            txCount:counts[p],
            feeChanges:changes[p],
            sinceLaunch:scanFrom>B[p]||B[p]<=launch,
            windowHours:startTs?((B.headTs-startTs)/3600):null
          };
        }
        const out={ok:true,byPeriod:byPeriod,excluded:excluded,feeChanges:feeEvents.length,scanFrom:scanFrom,headBlock:cur};
        realizedFeeCache[key]=out;
        console.log(`Realized UFO fees | blocks ${scanFrom}-${cur} | ${transferLogs.length} inbound legs, ${rows.filter(r=>r.drop).length} excluded, ${feeEvents.length} fee change(s)`);
        if(excluded.any){
          console.warn(`  excluded: ${directSendCount} direct send(s) = ${Math.round(directSendTokens).toLocaleString()} UFO | `+
            `${exemptSenders.length} fee-exempt sender(s) = ${Math.round(exemptTokens).toLocaleString()} UFO | `+
            `${unclassifiedGroups} unclassified | ${unknownSenders} sender(s) we could not check | `+
            `${(uncheckedShare*100).toFixed(2)}% of volume from unchecked senders`);
          if(exemptSenders.length)console.warn('  exempt senders:',exemptSenders);
        }
        PERIOD_KEYS.forEach(p=>console.log(`   ${p}: ${byPeriod[p].txCount} transfers, ${byPeriod[p].totalTokens.toLocaleString()} UFO, ${byPeriod[p].feeChanges} fee change(s), window ~${byPeriod[p].windowHours?byPeriod[p].windowHours.toFixed(1):'?'}h${byPeriod[p].sinceLaunch?' (since launch)':''}`));
        return out;
      }catch(e){console.error('fetchRealizedFees error:',e);return{ok:false,error:e.message||'unexpected error'};}
    };

// ===== lifted from index.html: mkDelivered + fetchDeliveredValue =====
    const deliveredCache={};
    const mkDelivered=()=>({
      ufoBurned:0, ptgcBurned:0,
      lp:{},           // quoteSymbol -> {ufo, quote, mints}
      swapbackTxs:0
    });

    const fetchDeliveredValue=async(ufoAddress,ptgcAddress,firstPoolMs,pairs)=>{
      lastLogError=null;
      try{
        const blk=await rpcFetch({jsonrpc:'2.0',method:'eth_blockNumber',params:[],id:1});
        if(!blk.result)return{ok:false,error:'could not read current block'};
        const cur=parseInt(blk.result,16);
        const key=`${ufoAddress}-delivered-${cacheBucket()}`;
        if(deliveredCache[key])return deliveredCache[key];

        const B=await getPeriodBoundaries(cur,firstPoolMs);
        if(!B)return{ok:false,error:'could not read block timestamps'};
        const scanFrom=Math.max(0,B['90d'],B.launch);
        const contract=ufoAddress.toLowerCase();
        const ufoTopic='0x'+encodeAddress(ufoAddress);

        /* One scan defines the swapback transactions. Everything else is an
           intersection against it. `feeIn` is the inbound fee stream — Transfer to the
           contract — which the reconciliation guardrail needs split by sender: a fee whose
           sender is a PAIR came from a trade; a fee from any other wallet came from a
           transfer (an LP add or a wallet-to-wallet move) and produces no Swap event. Only
           the pair-sourced fees are comparable to pair swap volume. */
        const contractTopic='0x'+encodeAddress(ufoAddress);
        const[ufoOut,ufoBurns,ptgcBurns,feeIn]=await Promise.all([
          getLogsChunked(ufoAddress,[TRANSFER_TOPIC,ufoTopic,null],scanFrom,cur),
          getLogsChunked(ufoAddress,[TRANSFER_TOPIC,null,BURN_TOPIC_PADDED],scanFrom,cur),
          getLogsChunked(ptgcAddress,[TRANSFER_TOPIC,null,BURN_TOPIC_PADDED],scanFrom,cur),
          getLogsChunked(ufoAddress,[TRANSFER_TOPIC,null,contractTopic],scanFrom,cur)
        ]);
        if(!ufoOut)return{ok:false,error:lastLogError||'could not read contract transfers'};
        if(!ufoBurns)return{ok:false,error:lastLogError||'could not read UFO burns'};
        if(!ptgcBurns)return{ok:false,error:lastLogError||'could not read pTGC burns'};

        const swapbackTxs={};
        for(const l of ufoOut)swapbackTxs[l.transactionHash]=true;

        /* Mints per pair. Accept BOTH topic variants — the UniV2 hash matches
           nothing here (handoff 8.2), but never assume a constant is right. */
        const mintsByPair={};
        let mintQueryOk=true;
        /* All three pairs, both queries, in parallel. These were six sequential round
           trips (Mint x3 then token0 x3); one flight now. Swap logs ride along — they
           cost one memoised scan each and they are what the reconciliation guardrail
           needs, so the check survives even when the dev audit is switched off. */
        const ufoIsToken0={};
        const pairSwapUfo={};   // pair -> [{block, ufo}]
        await Promise.all(pairs.map(async p=>{
          const[logs,t0raw,swaps]=await Promise.all([
            getLogsChunked(p.address,[[PAIR_MINT_TOPIC,PAIR_MINT_TOPIC_PULSEX]],scanFrom,cur),
            ethCallRead(p.address,SEL_TOKEN0),
            getLogsChunked(p.address,[PAIR_SWAP_TOPIC],scanFrom,cur)
          ]);
          if(logs===null){mintQueryOk=false;mintsByPair[p.address]=[];}
          else mintsByPair[p.address]=logs;
          const t0=wordToAddress(t0raw);
          if(!t0){mintQueryOk=false;return;}
          const isT0=t0.toLowerCase()===contract;
          ufoIsToken0[p.address]=isT0;
          /* The pair's Swap event carries exact token amounts. Summing the UFO leg
             (in + out) gives swap volume in TOKENS — no price, no DexScreener. */
          const arr=[];
          if(Array.isArray(swaps)){
            for(const l of swaps){
              const h=l.data.startsWith('0x')?l.data.slice(2):l.data;
              if(h.length<256)continue;
              const w=i=>BigInt('0x'+h.slice(i*64,(i+1)*64)); // 0In,1In,0Out,1Out
              const ufo=weiToTokens((isT0?w(0):w(1))+(isT0?w(2):w(3)));
              arr.push({block:parseInt(l.blockNumber,16),ufo,tx:l.transactionHash});
            }
          }
          pairSwapUfo[p.address]=arr;
        }));

        const accs={};
        PERIOD_KEYS.forEach(k=>{accs[k]=mkDelivered();});
        const addTo=(block,fn)=>{for(const k of PERIOD_KEYS)if(block>=B[k])fn(accs[k]);};

        for(const t of Object.keys(swapbackTxs)){/* counted below via ufoOut blocks */}
        const seenTx={};
        for(const l of ufoOut){
          if(seenTx[l.transactionHash])continue;
          seenTx[l.transactionHash]=true;
          addTo(parseInt(l.blockNumber,16),a=>{a.swapbackTxs++;});
        }

        for(const l of ufoBurns){
          if(!swapbackTxs[l.transactionHash])continue;      // launch burn / manual send
          const amt=weiToTokens(BigInt(l.data&&l.data!=='0x'?l.data:'0x0'));
          addTo(parseInt(l.blockNumber,16),a=>{a.ufoBurned+=amt;});
        }
        /* pTGC taxes its own transfers 5%, and part of that tax is itself a burn.
           So a swapback's pTGC buyback emits TWO transfers to 0x369:
               232,845.95  the tokens UFO actually bought and burned   (95.0% of gross)
                 1,225.505 pTGC's own burn fee on that same transfer   ( 0.5% of gross)
           Counting both overstates "pTGC burned by UFO" by 0.5263% (0.005/0.95).
           They share a sender — the pair — so address can't separate them. The RATIO
           can: the fee leg is always 0.005/0.95 of the delivered leg. Same trick as the
           direct-send fingerprint, and it survives a tx containing two swapbacks. */
        const PTGC_FEE_RATIO=0.005/0.95;
        const ptgcByTx={};
        for(const l of ptgcBurns){
          if(!swapbackTxs[l.transactionHash])continue;      // pTGC's own tax burn elsewhere
          (ptgcByTx[l.transactionHash]=ptgcByTx[l.transactionHash]||[]).push(l);
        }
        let ptgcFeeLegsDropped=0;
        for(const tx of Object.keys(ptgcByTx)){
          const legs=ptgcByTx[tx].map(l=>({log:l,amt:weiToTokens(BigInt(l.data&&l.data!=='0x'?l.data:'0x0'))}));
          const drop={};
          for(let i=0;i<legs.length;i++)for(let j=0;j<legs.length;j++){
            if(i===j||drop[i])continue;
            const r=legs[i].amt/legs[j].amt;
            if(legs[j].amt>0&&Math.abs(r-PTGC_FEE_RATIO)/PTGC_FEE_RATIO<0.01){drop[i]=true;ptgcFeeLegsDropped++;}
          }
          legs.forEach((lg,i)=>{
            if(drop[i])return;
            addTo(parseInt(lg.log.blockNumber,16),a=>{a.ptgcBurned+=lg.amt;});
          });
        }

        for(const p of pairs){
          const isT0=ufoIsToken0[p.address];
          if(isT0===undefined)continue;
          for(const l of (mintsByPair[p.address]||[])){
            /* PulseX Mint carries senderOrigin as topics[2]. When present it is
               decisive: the swapback's adds name the UFO contract. Fall back to
               the swapback-tx intersection for the UniV2 shape. */
            const origin=(l.topics&&l.topics.length>2)?('0x'+l.topics[2].slice(26)).toLowerCase():null;
            const mine=origin?(origin===contract):!!swapbackTxs[l.transactionHash];
            if(!mine)continue;                               // the owner's own LP add
            const h=l.data.startsWith('0x')?l.data.slice(2):l.data;
            if(h.length<128)continue;
            const w=i=>BigInt('0x'+h.slice(i*64,(i+1)*64));
            const a0=weiToTokens(w(0)),a1=weiToTokens(w(1));
            const ufoAmt=isT0?a0:a1, qAmt=isT0?a1:a0;
            addTo(parseInt(l.blockNumber,16),a=>{
              const e=a.lp[p.quoteSymbol]||(a.lp[p.quoteSymbol]={ufo:0,quote:0,mints:0});
              e.ufo+=ufoAmt;e.quote+=qAmt;e.mints++;
            });
          }
        }

        /* RECONCILIATION, in tokens, no prices. Bucket every pair's Swap volume into the
           same windows. The panel compares this against the volume IMPLIED by the fees
           the contract collected. If the fee stream is clean the ratio sits near 1.06–1.10x
           (a sell delivers only 94% of its tokens to the pair, so pair volume structurally
           under-reports; taxed wallet-to-wallet transfers push it up a little). A ratio
           outside that band means the fee measurement is off — which is how the original
           bug was caught. This is the smoke detector, and it now lives in the always-on
           scan rather than the dev audit. */
        const pairSwapByPeriod={};PERIOD_KEYS.forEach(p=>{pairSwapByPeriod[p]=0;});
        let swapScanOk=true;
        for(const p of pairs){
          const arr=pairSwapUfo[p.address];
          if(arr===undefined){swapScanOk=false;continue;}
          for(const s of arr)PERIOD_KEYS.forEach(k=>{if(s.block>=B[k])pairSwapByPeriod[k]+=s.ufo;});
        }

        /* Split the inbound fee stream into TRADE fees and TRANSFER fees.
           The discriminator is NOT the fee's sender — on a buy that sender is the pair,
           but on a sell it is the seller's own wallet, so filtering by `from==pair` keeps
           buys and drops sells (that was the 0.44x bug). The robust signal: a fee is
           trade-sourced iff its TRANSACTION also contains a pair Swap event. LP adds and
           wallet-to-wallet transfers never do. Catches both sides of every trade. */
        const swapTxs={};
        for(const p of pairs){
          const arr=pairSwapUfo[p.address];
          if(Array.isArray(arr))for(const s of arr)if(s.tx)swapTxs[s.tx]=true;
        }
        const swapFeeTokensByPeriod={};PERIOD_KEYS.forEach(p=>{swapFeeTokensByPeriod[p]=0;});
        let feeInOk=Array.isArray(feeIn);
        if(feeInOk){
          for(const l of feeIn){
            if(!l.topics||l.topics.length<3)continue;
            if(!swapTxs[l.transactionHash])continue;     // no Swap in this tx => not a trade fee
            const b=parseInt(l.blockNumber,16);
            const amt=weiToTokens(BigInt(l.data&&l.data!=='0x'?l.data:'0x0'));
            PERIOD_KEYS.forEach(k=>{if(b>=B[k])swapFeeTokensByPeriod[k]+=amt;});
          }
        }

        const out={ok:true,byPeriod:accs,mintQueryOk,scanFrom,headBlock:cur,launch:B.launch,
                   ptgcFeeLegsDropped,
                   pairSwapByPeriod,swapScanOk,swapFeeTokensByPeriod,feeInOk,
                   /* Exposed so the PTGC panel can subtract any pre-generated row that names
                      one of these transactions. If the JSON generator is ever repointed at the
                      new contract, its rows would otherwise be added on top of ours and the
                      burn total would silently double. */
                   swapbackTxs:Object.keys(swapbackTxs),
                   pairs:pairs.map(p=>({symbol:p.quoteSymbol,address:p.address}))};
        deliveredCache[key]=out;
        console.log(`Delivered value | blocks ${scanFrom}-${cur} | ${Object.keys(swapbackTxs).length} swapback tx(s)`);
        PERIOD_KEYS.forEach(k=>{
          const a=accs[k];
          console.log(`   ${k}: ${a.swapbackTxs} swapbacks · ${Math.round(a.ufoBurned).toLocaleString()} UFO burned · ${Math.round(a.ptgcBurned).toLocaleString()} pTGC burned · LP ${Object.keys(a.lp).map(s=>`${s}:${a.lp[s].mints}`).join(' ')||'none'}`);
        });
        if(ptgcFeeLegsDropped)console.log(`   (${ptgcFeeLegsDropped} pTGC leg(s) identified as pTGC's own 0.5% burn fee and excluded)`);
        if(swapScanOk&&feeInOk){
          const sf=swapFeeTokensByPeriod['24h']||0, ps=pairSwapByPeriod['24h']||0;
          const impl=sf/0.06;
          console.log(`reconciliation (24h) | trade fees ${Math.round(sf).toLocaleString()} UFO (fees whose tx contained a Swap) imply ${Math.round(impl).toLocaleString()} UFO of swaps · pairs traded ${Math.round(ps).toLocaleString()} UFO · ratio ${ps>0?(impl/ps).toFixed(2):'?'}x (want ~1.06-1.10)`);
        }
        if(!mintQueryOk)console.error('*** Mint query failed for at least one pair — LP delivery is NOT trustworthy ***');
        return out;
      }catch(e){console.error('fetchDeliveredValue error:',e);return{ok:false,error:e.message||'unexpected error'};}
    };

// ===== builder inputs (new migrated UFO) =====
const UFO_ADDRESS  = '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6';
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const UFO_LAUNCH_FALLBACK_MS = Date.parse('2026-07-08T00:00:00Z');
const HARDCODED_UFO_PAIRS = [
  { address: '0xE221e6fC30e5787F0d551f980B4da1055D832A03', quoteSymbol: 'WPLS' },
  { address: '0x145BC3a8a5EC0C84061511a5DB6023360caDF654', quoteSymbol: 'PLSX' },
  { address: '0xc4434600F1f263Ee38c38dfe32c8DEf8c0047C0b', quoteSymbol: 'WETH' },
  { address: '0xe61aA9a9b7a13ceedEAa8D26bfF5222003a40634', quoteSymbol: 'EHEX' }
];

async function main(){
  const firstPoolMs = UFO_LAUNCH_FALLBACK_MS; // safe early floor; costs one extra query at most
  const [realizedFees, delivered] = await Promise.all([
    fetchRealizedFees(UFO_ADDRESS, firstPoolMs),
    fetchDeliveredValue(UFO_ADDRESS, PTGC_ADDRESS, firstPoolMs, HARDCODED_UFO_PAIRS)
  ]);
  if(!realizedFees || !realizedFees.ok || !delivered || !delivered.ok){
    console.error('scan failed — NOT writing (carrying forward last good file).',
      { realizedFees: realizedFees && realizedFees.error, delivered: delivered && delivered.error });
    process.exit(1);
  }
  const out = {
    meta: {
      generatedAt: new Date().toISOString(),
      headBlock: delivered.headBlock || realizedFees.headBlock || null,
      ufoAddress: UFO_ADDRESS,
      ptgcAddress: PTGC_ADDRESS,
      schema: 1
    },
    delivered,
    realizedFees
  };
  fs.writeFileSync(OUT_PATH, JSON.stringify(out, null, 2));
  const d24 = delivered.byPeriod && delivered.byPeriod['24h'];
  console.log(`wrote ${OUT_PATH} | headBlock ${out.meta.headBlock} | 24h: ${d24?Math.round(d24.ufoBurned):'?'} UFO burned, ${d24?Math.round(d24.ptgcBurned):'?'} PTGC burned`);
}
main().catch(e => { console.error('builder crashed:', e); process.exit(1); });
