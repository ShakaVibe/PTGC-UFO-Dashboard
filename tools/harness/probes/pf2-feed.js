(async()=>{const q=s=>[...document.querySelectorAll(s)];const out={chips:q('.pf2-chips button').map(b=>b.innerText.replace(/\n/g,' ')),days:q('.pf2-fday').map(d=>d.innerText.replace(/\n/g,' ')),rows:q('.pf2-fr').map(r=>r.innerText.replace(/\n/g,' | '))};
const b=q('.pf2-fr .cp')[0];if(b){b.click();await new Promise(r=>setTimeout(r,150));out.copied=b.innerText;}
const s=q('.pf2-chips button').find(x=>x.innerText.startsWith('Sells'));if(s){s.click();await new Promise(r=>setTimeout(r,200));out.sellsOnly=q('.pf2-fr .t1').map(x=>x.innerText);}
const a=q('.pf2-chips button').find(x=>x.innerText.startsWith('All'));if(a)a.click();
return out;})()
