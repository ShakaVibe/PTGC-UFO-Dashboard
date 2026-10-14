(async()=>{const q=s=>[...document.querySelectorAll(s)];const b=q('.pf2-edb')[0];if(!b)return'no button';b.click();
for(let i=0;i<40&&!document.querySelector('.pf2-ed .sum');i++)await new Promise(r=>setTimeout(r,500));
const ed=document.querySelector('.pf2-ed');if(!ed)return'no window';
const out={tiles:q('.pf2-ed .tl').map(t=>t.innerText.replace(/\n/g,' | ')),rows:q('.pf2-ed .dt tbody tr').slice(0,4).map(t=>t.innerText.replace(/\n|\t/g,' | ')),bars:q('.pf2-edplot path').length};
const p=document.querySelector('.pf2-edplot');const r=p.getBoundingClientRect();p.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:r.left+r.width*0.6,clientY:r.top+50}));await new Promise(r=>setTimeout(r,200));
out.tip=(document.querySelector('.pf2-edtip')||{}).innerText;
return out;})()
