/* Audit IV e20 (2026-10-23): the CI mount check (.github/workflows/site-check.yml). Mounts every page in headless Chromium through
   run.js (data APIs stubbed, real data/*.json) and fails when a page does not render (probes/ci-mounted.js) or logs an unexpected
   console error. Allowed: Babel's "deoptimised" note, the stub's 404s (GeckoTerminal), and charts.html's html2canvas SRI mismatch
   (the harness serves its own copy). Usage: CHROME=/path/to/chrome node ci-mount.js
   Audit VI item 4 (2026-10-28): four more cases — #/affiliates, #/ptgc/kpi, #/ptgc/social (never mounted before) and #/ptgc at a
   390×844 phone — and ONLY=<names,comma-separated> to run a subset. deploy.yml's gate runs ONLY=home,ptgc,ufo,affiliates,ptgc-390
   (index.html routes, ~70 s) so a page that compiles but throws at mount can no longer go live; site-check.yml runs them all. */
const {spawnSync}=require('child_process');
const CASES=[['home','#/','index.html'],['ptgc','#/ptgc','index.html'],['ufo','#/ufo','index.html'],['portfolio','','portfolio.html'],
  ['calculators','','calculators.html'],['charts','','charts.html'],['ledger','','ledger.html'],
  ['affiliates','#/affiliates','index.html'],['kpi','#/ptgc/kpi','index.html'],['social','#/ptgc/social','index.html'],
  ['ptgc-390','#/ptgc','index.html',390,844]];
const ONLY=(process.env.ONLY||'').split(',').map(s=>s.trim()).filter(Boolean);
const ALLOW=[/\[BABEL\] Note/,/status of 404/,/Failed to find a valid digest/];
let fail=0;
for(const [name,route,html,w=1280,h=900] of CASES){
  if(ONLY.length&&!ONLY.includes(name))continue;
  const t0=Date.now();
  const r=spawnSync(process.execPath,['run.js',route,String(w),String(h),'out/ci-'+name,'wait=2000;evalfile=probes/ci-mounted.js'],{cwd:__dirname,env:{...process.env,HTML:html},encoding:'utf8',timeout:150000});
  const out=(r.stdout||'')+'\n'+(r.stderr||'');
  let probe=null,errs=null;
  try{const m=out.match(/EVAL probes\/ci-mounted\.js => (.*)/);probe=m&&JSON.parse(JSON.parse(m[1]));}catch(e){}
  try{const m=out.match(/ERRORS_JSON (.*)/);errs=m&&JSON.parse(m[1]);}catch(e){}
  const bad=(errs||[]).filter(e=>!ALLOW.some(a=>a.test(e)));
  const ok=r.status===0&&probe&&probe.ok&&errs&&!bad.length;
  console.log(`${ok?'ok  ':'FAIL'} ${name.padEnd(12)} ${Math.round((Date.now()-t0)/1000)}s  ${probe?JSON.stringify(probe):'no probe result'}${bad.length?'  errors: '+JSON.stringify(bad.slice(0,4)):''}`);
  if(!ok){fail++;if(r.status!==0||!probe)console.log(out.split('\n').filter(l=>/HARNESS FAIL|Error|error/.test(l)).slice(0,8).join('\n'));}
}
if(fail){console.log(`::error::${fail} page(s) did not render cleanly — see above`);process.exit(1);}
console.log('every page rendered');
