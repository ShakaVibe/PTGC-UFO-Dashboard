const fs=require('fs');const Babel=require('@babel/standalone');
const html=fs.readFileSync(process.argv[2]||require('path').resolve(__dirname,'..','..','index.html'),'utf8');
const m=html.match(/<script type="text\/babel"[^>]*>([\s\S]*?)<\/script>/);
if(!m){console.error('no babel block');process.exit(1);}
const t0=Date.now();
try{const out=Babel.transform(m[1],{presets:['react'],filename:'index.jsx'});fs.writeFileSync(require('path').join(__dirname,'compiled.js'),out.code);console.log('compiled ok',out.code.length,'bytes',Date.now()-t0,'ms');}
catch(e){console.error('COMPILE ERROR',e.message.split('\n').slice(0,6).join('\n'));process.exit(1);}
