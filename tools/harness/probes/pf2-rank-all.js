// 2026-10-24 (combined rank): the League boxes' rank rows (text + aria-label) and, when the rank window is open, its header,
// picker, hero, tiles and chart-area text. Used with T1_BAL + T1_BY_ADDR=1 and 2–3 seeded wallets.
(()=>{const T=e=>e?e.innerText.replace(/\s+/g,' ').trim():null;
  const rows=[...document.querySelectorAll('.pf2-rk3')].map(e=>({t:T(e),aria:(e.querySelector('button')||{}).ariaLabel||null}));
  const lg=[...document.querySelectorAll('.pf2-lgw')].map(e=>T(e).slice(0,160));
  const w=document.querySelector('.pf2-rkw');
  const win=w?{sub:T(w.querySelector('.ehd .sub')),pick:[...w.querySelectorAll('.pf2-edsel button')].map(b=>(b.ariaPressed==='true'?'*':'')+T(b)),
    hero:T(w.querySelector('.hero .big')),tiles:[...w.querySelectorAll('.hero .tiles .tl')].map(T),ch:T(w.querySelector('.ch')).slice(0,200),
    wt:w.querySelector('.wt')?T(w.querySelector('.wt')).slice(0,260):null,ft:T(w.querySelector('.ft'))}:null;
  return JSON.stringify({rows,lg,win});})()
