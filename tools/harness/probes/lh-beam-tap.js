// LEAGUE HISTORY beam: a finger tap (pointerType touch) on section window.__bi
(()=>{const s=document.querySelector(`.lh-bm-s[data-i="${window.__bi??7}"]`);if(!s)return null;const r=s.getBoundingClientRect();
 s.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,pointerType:'touch',clientX:r.left+r.width/2,clientY:r.top+3}));return 'tapped '+s.dataset.i;})()
