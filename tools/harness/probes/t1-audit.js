// TOP 100 audit (2026-10-22): runs a scripted check — window.__t1 = {addr, mode?('s'), type?} — and reports results; also tags the
// first list row so a later run can tell whether typing remounted it (window.__rowSame)
(async()=>{
  const m=document.querySelector('.t1m');if(!m)return 'no window';
  const o=window.__t1||{};const inp=m.querySelector('.t1inp input');const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
  const sleep=t=>new Promise(r=>setTimeout(r,t));
  const t=s=>[...m.querySelectorAll(s)].map(e=>e.innerText.replace(/\s+/g,' ').trim());
  if(o.mode){[...m.querySelectorAll('.t1sw button')].find(b=>(o.mode==='s')===/stakers/i.test(b.textContent)).click();await sleep(2500);}
  if(o.typeTest){const r0=m.querySelector('.t1r');if(r0)r0.__tag=1;for(const ch of '0xabc'){set.call(inp,inp.value+ch);inp.dispatchEvent(new Event('input',{bubbles:true}));await sleep(60);}
    const r1=m.querySelector('.t1r');return JSON.stringify({rowSame:!!(r1&&r1.__tag)});}
  if(o.addr){set.call(inp,o.addr);inp.dispatchEvent(new Event('input',{bubbles:true}));m.querySelector('.t1go').click();await sleep(2500);}
  return JSON.stringify({q:inp.value,res:t('.t1res .t1t'),msg:t('.t1msg'),old:t('.t1old'),me:t('.t1r.me'),rows:m.querySelectorAll('.t1r').length,ranks:t('.t1r .rk').slice(0,4),tiles:t('.t1st4 .t1t').map(x=>x.slice(0,40))});
})()
