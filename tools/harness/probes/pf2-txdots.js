(async()=>{const rows=[...document.querySelectorAll('.pf2-txt tbody tr')].map(t=>[...t.children].slice(2,5).map(c=>c.innerText).join(' '));
const ev=[...document.querySelectorAll('.pf2-hp b.ev')].map(b=>b.className+'@'+b.style.left);
const tips=[];for(const e of document.querySelectorAll('.pf2-hp b.ev')){const r=e.getBoundingClientRect();e.closest('.pf2-hp').dispatchEvent(new MouseEvent('mousemove',{bubbles:true,clientX:r.left+r.width/2,clientY:r.top+5}));await new Promise(r=>setTimeout(r,200));const t=document.querySelector('.pf2-htip .ev');tips.push(t?t.innerText.replace(/\n/g,' | '):'none');}
return{rows,ev,tips,legend:(document.querySelector('.pf2-hlg')||{}).innerText};})()
