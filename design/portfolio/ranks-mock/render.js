const {chromium}=require('playwright-core');
(async()=>{const [,,file,out,w]=process.argv;const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium',args:['--no-sandbox','--headless=new'],ignoreDefaultArgs:['--headless=old','--headless']});
const p=await b.newPage({viewport:{width:+w,height:900},deviceScaleFactor:1});await p.goto('file://'+file);await p.waitForTimeout(800);
const o=await p.evaluate(()=>{const r=[];document.querySelectorAll('.pf2-bdt').forEach(t=>{const p=t.closest('.pf2-bd');r.push([t.scrollWidth,p.clientWidth]);});return {tables:r,sw:document.documentElement.scrollWidth};});console.log(JSON.stringify(o));
await p.screenshot({path:out,fullPage:true});await b.close();})();
