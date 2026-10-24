// LEAGUE HISTORY (2026-10-24): the window's state — title, pressed controls, the eight cards, the big chart header, the foot
(()=>{const w=document.querySelector('.lh-win');if(!w)return JSON.stringify({open:false,dot:!!document.querySelector('[aria-label="League history (preview)"]'),strip:!!document.querySelector('.lh-strip')});
 const T=e=>e?e.innerText.replace(/\s+/g,' ').trim():null;
 return JSON.stringify({open:true,title:T(w.querySelector('h2')),pressed:[...w.querySelectorAll('.lh-tg button[aria-pressed=true]')].map(T),
  cards:[...w.querySelectorAll('.lh-cd')].map(c=>T(c).replace(/ of supply/,'').slice(0,70)),sel:T(w.querySelector('.lh-cd[aria-pressed=true] .nm')),
  big:T(w.querySelector('.lh-bh')),tip:T(w.querySelector('.lh-tip')),wait:T(w.querySelector('.lh-wait')),foot:T(w.querySelector('.lh-foot'))&&T(w.querySelector('.lh-foot')).slice(-120),
  sw:document.documentElement.scrollWidth,winW:Math.round(w.getBoundingClientRect().width)});})()
