// LEAGUE HISTORY: a point near the LEFT edge of the big chart (for hoverfile=) — the hover box must stay inside the window
(()=>{const c=document.querySelector('.lh-ch');if(!c)return null;const r=c.getBoundingClientRect();return{x:r.left+r.width*.12,y:r.top+r.height*.5};})()
