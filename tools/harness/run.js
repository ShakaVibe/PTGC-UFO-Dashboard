/* Headless harness for index.html (roadmap b8 groundwork — see README.md).
   - serves the repo root over http
   - swaps the CDN <script> tags for the pinned npm builds (SRI attrs stripped by rewriting the HTML)
   - replaces the Tailwind play CDN with a CLI-built stylesheet
   - stubs RPC (eth_*), DexScreener, PulseScan, GitHub raw, fonts
   Usage: node run.js <route> <width> <height> <outPrefix> [actions]   (env: HTML=, RPC_DOWN=1, SLOW_RPC=ms, DS_DOWN=1, DS_VOL_DRIFT=1, SLOW=ms, SLOW_HISTORY=ms, SLOW_UFO=ms, HEAD_BLOCK=n, LOGS_DOWN=1, DECK_LOGS=n, REDUCED=1, PS_DOWN=1, PS_COUNTERS_DOWN=1, AFFIL_DATA=1, AFFIL_SYNC=iso, AFFIL_BAD=1|<body>, DS_PRICE=n, DS_UFO_PRICE=n, CHROME=)
*/
const fs=require('fs'),path=require('path'),http=require('http');
const {chromium}=require('playwright-core');
const REPO=path.resolve(__dirname,'..','..');   // repo root (tools/harness/../..)
const [route='#/',W='375',H='812',out='shot',actions='']=process.argv.slice(2);

const html0=fs.readFileSync(path.join(REPO,process.env.HTML||'index.html'),'utf8');
const html=html0
  .replace(/<script src="https:\/\/cdn\.tailwindcss\.com\/3\.4\.16"><\/script>/,'<link rel="stylesheet" href="/__tw.css">')
  .replace(/<script src="https:\/\/unpkg\.com\/react@18\.3\.1\/umd\/react\.production\.min\.js"[^>]*><\/script>/,'<script src="/__react.js"></script>')
  .replace(/<script src="https:\/\/unpkg\.com\/react-dom@18\.3\.1\/umd\/react-dom\.production\.min\.js"[^>]*><\/script>/,'<script src="/__react-dom.js"></script>')
  .replace(/<script src="https:\/\/unpkg\.com\/@babel\/standalone@7\.26\.4\/babel\.min\.js"[^>]*><\/script>/,'<script src="/__babel.js"></script>')
  .replace(/<script src="https:\/\/cdn\.jsdelivr\.net\/npm\/chart\.js@4\.4\.1\/dist\/chart\.umd\.js"[^>]*><\/script>/,'<script src="/__chart.js"></script>')
  /* charts.html pins the date-fns adapter too; without it Chart.js throws "Check that a complete
     date adapter is provided" and every time-axis chart on that page stays blank, which is how the
     harness ran from a37 until 2026-09-21 (a59). */
  .replace(/<script src="https:\/\/cdn\.jsdelivr\.net\/npm\/chartjs-adapter-date-fns@3\.0\.0\/dist\/chartjs-adapter-date-fns\.bundle\.min\.js"[^>]*><\/script>/,'<script src="/__chart-adapter.js"></script>')
  .replace(/<link href="https:\/\/fonts\.googleapis\.com[^"]*" rel="stylesheet">/,'<link rel="stylesheet" href="/__fonts.css">');
if(html===html0)console.warn('WARNING: no CDN tags rewritten');

// Real Orbitron / Rajdhani from @fontsource (same faces the Google Fonts link loads), so screenshots
// show the page's actual type instead of a monospace fallback. Missing packages → the old empty-CSS stub.
const FONT_DIR=(f)=>path.join(__dirname,'node_modules/@fontsource',f);
const haveFonts=fs.existsSync(FONT_DIR('orbitron/files'))&&fs.existsSync(FONT_DIR('rajdhani/files'));
const fontCss=haveFonts?[['Orbitron',[400,700,900]],['Rajdhani',[300,400,500,600,700]]].map(([fam,ws])=>ws.map(w=>
  `@font-face{font-family:'${fam}';font-style:normal;font-weight:${w};font-display:swap;src:url(/__font/${fam.toLowerCase()}-latin-${w}-normal.woff2) format('woff2')}`).join('\n')).join('\n'):'';
const files={
  '/__tw.css':['tw.out.css','text/css'],
  '/__react.js':['node_modules/react/umd/react.production.min.js','text/javascript'],
  '/__react-dom.js':['node_modules/react-dom/umd/react-dom.production.min.js','text/javascript'],
  '/__babel.js':['node_modules/@babel/standalone/babel.min.js','text/javascript'],
  '/__chart.js':['node_modules/chart.js/dist/chart.umd.js','text/javascript'],
  '/__chart-adapter.js':['node_modules/chartjs-adapter-date-fns/dist/chartjs-adapter-date-fns.bundle.min.js','text/javascript'],
};
const mime={'.json':'application/json','.png':'image/png','.html':'text/html','.js':'text/javascript','.css':'text/css','.svg':'image/svg+xml','.jpg':'image/jpeg'};
const server=http.createServer((req,res)=>{
  const u=req.url.split('?')[0];
  if(u==='/'||u==='/index.html'){res.writeHead(200,{'content-type':'text/html'});return res.end(html);}
  if(u==='/__fonts.css'){res.writeHead(200,{'content-type':'text/css'});return res.end(fontCss);}
  if(files[u]){res.writeHead(200,{'content-type':files[u][1]});return res.end(fs.readFileSync(path.join(__dirname,files[u][0])));}
  if(u.startsWith('/__font/')){const f=u.slice(8),fam=f.split('-')[0];const fp=path.join(FONT_DIR(fam+'/files'),f);if(fs.existsSync(fp)){res.writeHead(200,{'content-type':'font/woff2'});return res.end(fs.readFileSync(fp));}}
  const p=path.join(REPO,decodeURIComponent(u));
  if(fs.existsSync(p)&&fs.statSync(p).isFile()){res.writeHead(200,{'content-type':mime[path.extname(p)]||'application/octet-stream'});return res.end(fs.readFileSync(p));}
  res.writeHead(404);res.end('nf');
});

// ---- stubs
const hex=n=>'0x'+BigInt(n).toString(16);
const pad=(n)=>'0x'+BigInt(n).toString(16).padStart(64,'0');
const HEAD=+process.env.HEAD_BLOCK||24_000_000;   // HEAD_BLOCK=n: raise the stub chain head (e.g. 27100000 so portfolio's UFO log scan, which starts at the launch block 26989200, has a window to walk — a12)
const rpcAnswer=(body)=>{
  const one=(q)=>{
    const m=q.method;let result;
    if(m==='eth_blockNumber')result=hex(HEAD);
    else if(m==='eth_chainId')result='0x171';
    else if(m==='eth_getBalance')result=hex(125_000_000n*10n**18n);   // 125M PLS — the DAO panel's eth_getBalance anchor read (a16)
    else if(m==='eth_getBlockByNumber'){const n=q.params[0]==='latest'?HEAD:parseInt(q.params[0],16);result={number:hex(n),timestamp:hex(Math.floor(Date.now()/1000)-(HEAD-n)*10)};}
    else if(m==='eth_getLogs'&&process.env.LOGS_DOWN){return {jsonrpc:'2.0',id:q.id,error:{code:-32000,message:'query timeout exceeded'}};}   // LOGS_DOWN=1: every eth_getLogs is a JSON-RPC error (calls still work) — portfolio's reflections scan must end "unavailable", never 0 (a12)
    else if(m==='eth_getLogs'){
      /* DECK_LOGS=n: answer a Swap-topic query with n synthetic PulseX Swap events on the stub pair,
         newest at the head block, so the Live Feed has rows to lift (u11). Everything else stays empty. */
      const f=q.params&&q.params[0]||{};const topics=f.topics||[];const n=+process.env.DECK_LOGS||0;
      const swapTopic='0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822';
      const asks=(Array.isArray(topics[0])?topics[0]:[topics[0]]).includes(swapTopic);
      const to=f.toBlock==='latest'?HEAD:parseInt(f.toBlock,16),from=parseInt(f.fromBlock,16);
      result=[];
      if(n&&asks)for(let i=0;i<n;i++){const b=HEAD-i*3;if(b<from||b>to)continue;const buy=i%3!==2;const amt=pad((1000n+BigInt(i)*250n)*10n**18n).slice(2);const z=pad(0).slice(2);
        result.push({address:'0x'+'ab'.repeat(20),topics:[swapTopic,pad(1),pad(2)],data:'0x'+(buy?z+z+z+amt:z+amt+z+z),blockNumber:hex(b),transactionHash:'0x'+(i+1).toString(16).padStart(64,'0'),logIndex:hex(i),removed:false});}
    }
    else if(m==='eth_call'){
      const d=(q.params[0].data||'').slice(0,10);
      // balanceOf → 5% of a big supply-ish number; totalSupply; getReserves; token0/1; generic
      if(d==='0x70a08231')result=pad(16_666_666_666n*10n**18n);
      else if(d==='0x18160ddd')result=pad(333_333_333_333n*10n**18n);
      else if(d==='0x0902f1ac')result=pad(1_000_000n*10n**18n).slice(0,66)+pad(2_000_000n*10n**18n).slice(2)+pad(1_700_000_000).slice(2);
      else if(d==='0x313ce567')result=pad(18);
      else result=pad(0);
    }else result=null;
    return {jsonrpc:'2.0',id:q.id,result};
  };
  return Array.isArray(body)?body.map(one):one(body);
};
/* DS_VOL_DRIFT=1: every successive DexScreener answer reports a bigger 24 h volume, the way a
   busy afternoon does. Without it the stub returns the same number forever and a figure that
   never follows a refresh looks identical to one that does (a52). */
let dsCalls=0;
const volDrift=v=>process.env.DS_VOL_DRIFT?Math.round(v*(1+0.5*dsCalls)):v;
const dsPair=(base,quote,price,liq,vol0)=>({chainId:'pulsechain',dexId:'pulsex',url:'https://dexscreener.com/pulsechain/x',pairAddress:'0x'+'ab'.repeat(20),
  baseToken:{address:base,name:base==='PTGC'?'The Grays Currency':'UFO',symbol:base},quoteToken:{address:'0x'+'cd'.repeat(20),name:quote,symbol:quote},
  priceNative:'0.5',priceUsd:String(price),txns:{h24:{buys:120,sells:80},h6:{buys:30,sells:20},h1:{buys:5,sells:3},m5:{buys:1,sells:0}},
  volume:(v=>({h24:v,h6:v/4,h1:v/24,m5:v/288}))(volDrift(vol0)),priceChange:{h24:3.21,h6:1,h1:0.2,m5:0},liquidity:{usd:liq,base:1e9,quote:1e9},fdv:price*3e11,marketCap:price*3e11,pairCreatedAt:Date.now()-1062*86400000,
  info:{imageUrl:''}});
const UFO_ADDR=/49eD499433Bee42DD34C169470feF2C8f9fAe6e6|E221e6fC30e5787F0d551f980B4da1055D832A03/i;   // TOKENS.UFO.address | TOKENS.UFO.mainPair
const dsAnswer=(url)=>{
  if(process.env.DS_VOL_DRIFT&&/tokens\//.test(url))dsCalls++;
  const isUFO=UFO_ADDR.test(url);   // the UFO token or its main pair in the URL
  const P=isUFO&&process.env.DS_UFO_PRICE?+process.env.DS_UFO_PRICE:(+process.env.DS_PRICE||0.000142);   // DS_PRICE=4.5e-5: a sub-micro price, to exercise the $0.0₄… notation (a48); DS_UFO_PRICE=n: a DIFFERENT price for UFO calls, so a token-switch race is visible (a7)
  const B=isUFO&&process.env.DS_UFO_PRICE?'UFO':'PTGC';
  const pairs=[dsPair(B,'WPLS',P,850000,42000),dsPair(B,'PRVX',P*0.993,120000,4000),dsPair(B,'PLSX',P*1.007,90000,2000),dsPair(B,'HEX',P,50000,1500)];
  return {schemaVersion:'1.0.0',pairs};
};

(async()=>{
  await new Promise(r=>server.listen(0,r));
  const port=server.address().port;
  const browser=await chromium.launch({executablePath:process.env.CHROME||undefined,args:['--no-sandbox','--headless=new'],ignoreDefaultArgs:['--headless=old','--headless']});
  const ctx=await browser.newContext({viewport:{width:+W,height:+H},deviceScaleFactor:1,isMobile:+W<640,hasTouch:+W<640});
  if(!process.env.NO_ACCEPT)await ctx.addInitScript(()=>{try{localStorage.setItem('grays_disclaimer_v1','1');}catch(e){}});   // NO_ACCEPT=1: leave the disclaimer un-accepted
  const page=await ctx.newPage();
  if(process.env.REDUCED)await page.emulateMedia({reducedMotion:'reduce'});   // REDUCED=1: prefers-reduced-motion for the whole run
  const errors=[],warns=[];
  page.on('console',m=>{if(m.type()==='error')errors.push(m.text().slice(0,300));});
  page.on('pageerror',e=>errors.push('PAGEERROR '+String(e).slice(0,300)));
  const rpcCount={n:0};
  const slow=+process.env.SLOW||0,slowHist=+process.env.SLOW_HISTORY||0,slowUfo=+process.env.SLOW_UFO||0;const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  await page.route('**/*',async r=>{
    const u=r.request().url();
    if(slow&&/rpc\.pulsechain|g4mm4|publicnode|api\.dexscreener\.com|api\.scan\.pulsechain/.test(u))await sleep(slow);
    if(slowUfo&&UFO_ADDR.test(u))await sleep(slowUfo);   // SLOW_UFO=ms: only the UFO token's DexScreener calls wait → the UFO load always lands AFTER a PTGC load started later (a7)
    if(slow&&process.env.SLOW_DATA&&/raw\.githubusercontent\.com\/[^/]+\/[^/]+\/main\/data\//.test(u))await sleep(slow);   // SLOW_DATA=1: the repo's data/*.json wait too (a35: sibling pages that only read those)
    if(slowHist&&/data\/[a-z-]*history[a-z-]*\.json/.test(u))await sleep(slowHist);   // SLOW_HISTORY=ms: delay the data/*history*.json files only (u13)
    if(u.startsWith(`http://localhost:${port}`)||u.startsWith(`http://127.0.0.1:${port}`))return r.continue();
    /* SLOW_RPC=ms: the chain answers, but slowly — the case RPC_DOWN cannot reproduce (a 503
       comes back instantly). This is what delays first paint when the primary endpoint hangs:
       rpcFetch's own per-endpoint timeout is 8 s, longer than the 5 s bootReady race (a62). */
    if(/rpc\.pulsechain|g4mm4|publicnode/.test(u)){rpcCount.n++;if(process.env.RPC_DOWN)return r.fulfill({status:503,body:'down'});if(process.env.SLOW_RPC)await new Promise(res=>setTimeout(res,+process.env.SLOW_RPC));let body={};try{body=JSON.parse(r.request().postData()||'{}');}catch(e){}return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify(rpcAnswer(body))});}
    if(/api\.dexscreener\.com/.test(u)&&process.env.DS_DOWN)return r.fulfill({status:503,body:'down'});
    if(/api\.dexscreener\.com/.test(u))return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify(dsAnswer(u))});
    if(/dd\.dexscreener\.com|dexscreener\.com/.test(u))return r.fulfill({status:200,contentType:'image/png',body:fs.readFileSync(path.join(REPO,'07_Ufo_transparent.png'))});
    if(/api\.scan\.pulsechain\.com/.test(u)&&process.env.PS_DOWN)return r.fulfill({status:503,body:'down'});   // PS_DOWN=1: PulseScan returns 503 (holders → null)
    /* PS_COUNTERS_DOWN=1: only /counters 500s while the holder PAGES keep answering — PulseScan's
       documented intermittent failure, and the one that used to make "Squid & Below" a cached 0
       for a token with thousands of holders (a53). */
    if(/api\.scan\.pulsechain\.com.*counters/.test(u)&&process.env.PS_COUNTERS_DOWN)return r.fulfill({status:500,body:'counters down'});
    if(/api\.scan\.pulsechain\.com.*counters/.test(u))return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({token_holders_count:'4321',transfers_count:'100000'})});
    if(/api\.scan\.pulsechain\.com.*holders/.test(u))return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({items:[],next_page_params:null})});
    if(/raw\.githubusercontent\.com\/[^/]+\/[^/]+\/main\/(data\/.*)/.test(u)){const f=u.match(/main\/(data\/[^?]*)/)[1];const p=path.join(REPO,f);if(fs.existsSync(p))return r.fulfill({status:200,contentType:'application/json',body:fs.readFileSync(p)});return r.fulfill({status:404,body:''});}
    /* AFFIL_DATA=1 serves a shaped /public/commissions body (one referrer, one buy, one
       receipt) instead of the empty default, so the affiliates page renders with data — the
       freshness badge, the leaderboard and the receipts modal have something to show.
       AFFIL_SYNC=<iso> sets monthlyLogs[<current month>].lastSyncDate, which is what the badge
       reads; default is 90 minutes ago. The empty default is unchanged for every other run. */
    if(/ptgcapi/.test(u)){
      /* AFFIL_BAD=1 serves well-formed JSON that is NOT the worker's payload - the 2026-09-22
         case, where a blocker / filtering DNS / VPN / corporate proxy answers that one request
         with 200 and `{}`. The page must show its error screen, never a dashboard of zeros.
         AFFIL_BAD=<body> sends that body verbatim (try '[]' or '{"entries":[]}').
         The DEFAULT is now a valid EMPTY PROGRAM instead of {"entries":[]}: the shape guard
         rejects the latter - correctly, it is not what getPublicCommissions builds - while an
         empty program still renders the same zero state every non-affiliates run has always
         screenshotted. Keep those two cases apart; collapsing them is the whole bug. */
      if(process.env.AFFIL_BAD)return r.fulfill({status:200,contentType:'application/json',body:process.env.AFFIL_BAD==='1'?'{}':process.env.AFFIL_BAD});
      if(!process.env.AFFIL_DATA)return r.fulfill({status:200,contentType:'application/json',body:'{"referrers":{},"monthlyLogs":{},"receipts":[]}'});
      const month=new Date().toISOString().slice(0,7);
      const sync=process.env.AFFIL_SYNC||new Date(Date.now()-90*60000).toISOString();
      /* Three referrers on purpose (a54): alice clears the minimum on the month's total, bob does
         not (meetsThreshold:false, commissionPtgc:0 — the case the "Commissions" tile used to bill
         for anyway), carol has her own commissionRate. thresholdType is deliberately "USD" in the
         wrong case, which used to flip the whole page from dollars to PTGC. */
      const buy=(n,usd,ptgc,paid)=>({date:month+'-1'+n+'T12:00:00.000Z',buyerWallet:'0x'+String(n).repeat(40),usdAmount:usd,ptgcAmount:ptgc,txHash:'0x'+String(n).repeat(64),paid:!!paid});
      const entry=(u,usd,ptgc,meets,comm,rate,buys)=>({id:month+'-'+u,username:u,wallet:'0x'+u.charCodeAt(0).toString(16).repeat(20),
        buysCount:buys.length,usdAmount:usd,ptgcAmount:ptgc,commissionRate:rate,commissionPtgc:comm,meetsThreshold:meets,
        status:'unpaid',paidTxHash:null,paidDate:null,buys,addedDate:sync,lastSyncDate:sync});
      return r.fulfill({status:200,contentType:'application/json',body:JSON.stringify({
        referrers:{alice:{wallet:'0xa'.padEnd(42,'1'),addedDate:sync},bob:{wallet:'0xb'.padEnd(42,'2'),addedDate:sync},carol:{wallet:'0xc'.padEnd(42,'3'),addedDate:sync}},
        monthlyLogs:{[month]:{settings:{commissionRate:2,threshold:100,thresholdType:'USD',coverFee:true},
          lastSyncDate:sync,
          entries:[
            entry('alice',500,1000000,true,20000,undefined,[buy(1,300,600000),buy(2,200,400000)]),
            entry('bob',40,80000,false,0,undefined,[buy(3,40,80000)]),
            entry('carol',200,400000,true,20000,5,[buy(4,200,400000)])
          ]}},
        receipts:[{id:'r1',date:month+'-30T23:30:00.000Z',username:'alice',wallet:'0xa'.padEnd(42,'1'),amount:9000,rate:2,txCount:1,txHash:'0x'+'cd'.repeat(32),month,ptgcPrice:0.000142,usdValue:1.28,feeCovered:true}]
      })});
    }
    if(/fonts\.g/.test(u))return r.fulfill({status:200,contentType:'text/css',body:''});
    if(/cdnjs.*html2canvas/.test(u))return r.fulfill({status:200,contentType:'text/javascript',body:process.env.H2C?fs.readFileSync(path.join(__dirname,'node_modules/html2canvas/dist/html2canvas.min.js'),'utf8'):'window.html2canvas=null;'});
    return r.fulfill({status:404,body:''});
  });
  const t0=Date.now();
  await page.goto(`http://localhost:${port}/${route}`,{waitUntil:'load'});
  // wait for React to mount + dashboard to leave the spinner
  await page.waitForFunction(()=>{const r=document.querySelector('#root');return r?r.children.length>0:true;},{timeout:30000});   // charts.html has no #root (plain JS page) — don't wait for one
  await page.waitForTimeout(2500);
  for(const a of actions.split(';').filter(Boolean)){
    const i=a.indexOf('=');const kind=a.slice(0,i),arg=a.slice(i+1);
    if(kind==='click'){const loc=page.locator(arg).first();await loc.scrollIntoViewIfNeeded().catch(()=>{});await loc.click({timeout:5000}).catch(e=>errors.push('CLICKFAIL '+arg+' '+e.message.split('\n')[0]));await page.waitForTimeout(600);}
    if(kind==='wait')await page.waitForTimeout(+arg);
    if(kind==='reload'){await page.reload({waitUntil:'load'});await page.waitForFunction(()=>{const r=document.querySelector('#root');return r?r.children.length>0:true;},{timeout:30000});await page.waitForTimeout(+arg||2500);}   // reload=<ms>: reload in place (localStorage survives) and wait. Same #root rule as the first load — charts.html has none, and `reload` used to time out there (a59)
    if(kind==='key'){await page.keyboard.press(arg);await page.waitForTimeout(300);}
    if(kind==='scroll'){await page.evaluate(y=>window.scrollTo(0,y),+arg);await page.waitForTimeout(400);}
    if(kind==='scrollnav'){await page.evaluate(()=>{const el=document.querySelector('.no-scrollbar');if(el)el.scrollLeft=9999;});await page.waitForTimeout(400);}
    if(kind==='evalfile'){const v=await page.evaluate(fs.readFileSync(arg,'utf8'));console.log('EVAL',arg,'=>',JSON.stringify(v,null,1));}
    if(kind==='eval'){const v=await page.evaluate(arg);console.log('EVAL',arg,'=>',JSON.stringify(v));}
    if(kind==='shot'){await page.screenshot({path:`${out}-${arg}.png`,fullPage:false});}
    if(kind==='hoverfile'){const pt=await page.evaluate(fs.readFileSync(arg,'utf8'));if(pt&&pt.x!=null){await page.mouse.move(pt.x,pt.y);await page.waitForTimeout(500);}else errors.push('HOVERFAIL '+arg+' returned '+JSON.stringify(pt));}   // hoverfile=<js file returning {x,y} in viewport px> → move the mouse there (tooltips)
  }
  await page.screenshot({path:`${out}.png`,fullPage:true});
  const txt=await page.evaluate(()=>document.body.innerText.slice(0,400).replace(/\n+/g,' | '));
  console.log('route',route,'size',W+'x'+H,'load',Date.now()-t0,'ms','rpc',rpcCount.n);
  console.log('text:',txt);
  console.log('errors:',errors.length?errors.slice(0,8):'none');
  await browser.close();server.close();
})().catch(e=>{console.error('HARNESS FAIL',e);process.exit(1);});
