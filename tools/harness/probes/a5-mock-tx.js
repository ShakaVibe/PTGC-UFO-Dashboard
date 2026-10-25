// Audit V mock-up (v2) — the TXNS tile with today's live numbers (DexScreener 1,789, flipped B506 / S1,283; people from the hourly file)
(()=>{const t=document.querySelector('.h2-tile.h2-tx');if(!t)return'notile';const v=window.__mt||'A';
const tl=t.querySelector('.h2-tl');if(v==='B')tl.lastChild.textContent='SWAPS 24H';
const tv=t.querySelector('.h2-tv');tv.firstChild.textContent='1789';tv.querySelector('.b').lastChild.textContent='506';tv.querySelector('.s').lastChild.textContent='1283';
const tc=t.querySelector('.h2-tc');tc.className='h2-tc tn';tc.style.color='rgba(255,255,255,.75)';tc.innerHTML='<b style="color:#fff">117</b> people · <b style="color:#39E15A">+$18.5K</b>';
return 'ok '+v;})()
