// TOP 100 (2026-10-22): types window.__addr (default: the real PTGC #118) into the window's checker and submits; then reports the
// window's state — the four tiles, the checker's tiles / message, podium + list row counts, the checked row, any overflow.
(async()=>{
  const m=document.querySelector('.t1m');if(!m)return 'no window';
  const inp=m.querySelector('.t1inp input');
  if(window.__addr!==null){const set=Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set;
    set.call(inp,window.__addr||'0xB1c0F321731a4b8652e0fD887A63bC452A0D9769');inp.dispatchEvent(new Event('input',{bubbles:true}));
    m.querySelector('.t1go').click();await new Promise(r=>setTimeout(r,2500));}
  const t=s=>[...m.querySelectorAll(s)].map(e=>e.innerText.replace(/\s+/g,' ').trim());
  const r=m.getBoundingClientRect();let over=0;m.querySelectorAll('*').forEach(e=>{const q=e.getBoundingClientRect();if(q.width&&q.right>r.right+1&&!e.closest('.tip'))over++;});
  return JSON.stringify({w:Math.round(r.width),tiles:t('.t1st4 .t1t'),res:t('.t1res .t1t'),msg:t('.t1msg'),pod:t('.t1pc').length,rows:m.querySelectorAll('.t1r').length,me:t('.t1r.me'),over,sw:t('.t1sw button[aria-pressed=true]')});
})()
