// LEAGUE HISTORY: the centre of card window.__ci (default 3 = Dolphin) — for hoverfile=
(()=>{const c=[...document.querySelectorAll('.lh-cd')][window.__ci??3];if(!c)return null;const r=c.getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2};})()
