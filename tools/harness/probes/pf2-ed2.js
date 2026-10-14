(async()=>{const q=s=>[...document.querySelectorAll(s)];q('.pf2-edb')[1].click();
for(let i=0;i<40&&!document.querySelector('.pf2-erw .sum');i++)await new Promise(r=>setTimeout(r,500));
const on=q('.pf2-erw .tabs button.on').filter(b=>b.offsetParent).map(b=>b.innerText);
const out={on,tiles:q('.pf2-erw .tl').map(t=>t.innerText.replace(/\n/g,' | ')),rows:q('.pf2-erw .dt tbody tr').length,firstRows:q('.pf2-erw .dt tbody tr').slice(0,2).map(t=>t.innerText.replace(/\n|\t/g,' | '))};
const s=document.querySelector('.pf2-erw .dts');if(s)out.scroll={h:s.clientHeight,sh:s.scrollHeight};
const p=document.querySelector('.pf2-edplot');const r=p.getBoundingClientRect();p.dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:r.left+r.width*0.4,clientY:r.top+50}));await new Promise(r=>setTimeout(r,200));
out.tip=(document.querySelector('.pf2-edtip')||{}).innerText;return out;})()
