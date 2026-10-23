/* The compile check (handover "Testing"). Audit IV e20 (2026-10-23): it compiles EVERY inline text/babel block of the five pages
   plus h2-header.jsx, and syntax-checks every plain inline <script>. It used to take the FIRST babel tag only — on portfolio.html and
   calculators.html that is <script type="text/babel" src="h2-header.jsx"> with an empty body, so it printed "compiled ok 0 bytes"
   for two pages it never compiled. Usage: node compile.js [file …] (default: all five pages + h2-header.jsx). Exit 1 on any error.
   compiled.js = index.html's block (the acorn scope pass in the handover reads it). deploy.yml runs this before every deploy. */
const fs=require('fs'),path=require('path'),vm=require('vm'),Babel=require('@babel/standalone');
const ROOT=path.resolve(__dirname,'..','..');
const files=process.argv.length>2?process.argv.slice(2):['index.html','portfolio.html','calculators.html','charts.html','ledger.html','h2-header.jsx'].map(f=>path.join(ROOT,f));
let bad=0;
for(const f of files){
  const src=fs.readFileSync(f,'utf8'),name=path.basename(f);
  const babel=f.endsWith('.jsx')?[src]:[...src.matchAll(/<script type="text\/babel"(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  const plain=f.endsWith('.jsx')?[]:[...src.matchAll(/<script(?![^>]*\b(?:src|type)=)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  babel.forEach((b,i)=>{const t0=Date.now();
    try{const out=Babel.transform(b,{presets:['react'],filename:name+(babel.length>1?'#'+(i+1):'')});
      if(name==='index.html'&&i===0)fs.writeFileSync(path.join(__dirname,'compiled.js'),out.code);
      console.log(name.padEnd(18),'babel block',i+1,'compiled ok',out.code.length,'bytes',Date.now()-t0,'ms');}
    catch(e){bad++;console.error(name,'babel block',i+1,'COMPILE ERROR',e.message.split('\n').slice(0,6).join('\n'));}});
  plain.forEach((b,i)=>{try{new vm.Script(b,{filename:name+' inline script '+(i+1)});}catch(e){bad++;console.error(name,'inline script',i+1,'SYNTAX ERROR',e.message);}});
  if(!babel.length&&!plain.length)console.log(name.padEnd(18),'nothing to compile');
  else if(plain.length)console.log(name.padEnd(18),plain.length,'plain inline script(s) parse ok');
}
if(bad){console.error(bad+' block(s) failed — a page with a compile error renders nothing');process.exit(1);}
console.log('all pages compile');
