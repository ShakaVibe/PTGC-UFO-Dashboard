/* calculators.html: the page must never print NaN / Infinity / undefined / "$0.00" market caps.
   Returns the offending snippets (40 chars of context) and the tab that is open. */
(()=>{
  const t=document.body.innerText;
  const bad=[];
  for(const re of [/NaN/g,/Infinity/g,/undefined/g]){let m;while((m=re.exec(t)))bad.push(t.slice(Math.max(0,m.index-30),m.index+20).replace(/\n/g,' '));}
  const tab=[...document.querySelectorAll('button')].find(b=>/X Multiplier|Moon Math|Rewards|New Capital|10 Yr/.test(b.textContent)&&getComputedStyle(b).boxShadow!=='none');
  return{bad,len:t.length,mcaps:(t.match(/MCap:[^\n|]{0,14}/g)||[]).slice(0,6)};
})()
