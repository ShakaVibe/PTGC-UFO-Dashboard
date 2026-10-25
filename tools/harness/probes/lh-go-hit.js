// 2026-10-25: is the strip's HISTORY tag the element under its own centre, and does it belong to the strip button?
(()=>{const g=document.querySelector('.lh-go');if(!g)return 'no .lh-go';g.scrollIntoView({block:'center'});const r=g.getBoundingClientRect();
const e=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {hitIsTag:e===g,inButton:!!(e&&e.closest('.lh-strip')),pe:getComputedStyle(g).pointerEvents};})()
