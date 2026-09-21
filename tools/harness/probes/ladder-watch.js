/* a51 probe: hook console.warn and report every retry-ladder message for ~22 s.
   Run with DS_DOWN=1 AND RPC_DOWN=1 — with only DexScreener down the page still gets a price
   from the chain-reserve fallback (a14) and the ladder correctly never starts.
   The ladder is 4s / 10s / 25s / 60s, so a working one shows two messages inside the window. */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const seen=[];const t0=performance.now();
  const orig=console.warn;
  console.warn=(...a)=>{const s=a.join(' ');if(/retrying in/.test(s))seen.push(Math.round((performance.now()-t0)/1000)+'s: '+s);orig.apply(console,a);};
  await sleep(22000);
  console.warn=orig;
  return{rungs:seen.length,messages:seen};
})()
