// Audit V mock-up (v1 + v7) on the real Humans vs Bots window, PTGC 24H. window.__mv = 'A' (value boxes removed) | 'B' (kept, marked est.)
(()=>{const d=[...document.querySelectorAll('[role=dialog]')].pop();if(!d)return'nodialog';const v=window.__mv||'A';
const hu=d.querySelector('.vs-card.hu'),bo=d.querySelector('.vs-card.bo');
hu.querySelector('.s').innerHTML='<b class="text-white">117</b> transactions by <b class="text-white">73</b> wallets through 6 routers';
bo.querySelector('.s').innerHTML='<b class="text-white">1,358</b> transactions from 19 bot contracts';
const strip=d.querySelector('.vs-strip');[...strip.children].forEach(sp=>{const k=sp.querySelector('.k');if(!k)return;
  if(k.textContent==='Trades'){k.textContent='Transactions';sp.querySelector('.v').textContent='1,475';}
  if(k.textContent==='Value generated'){if(v==='A')sp.remove();else k.textContent='Value generated · est.';}});
d.querySelectorAll('.vs-card .vg').forEach(g=>{if(v==='A'){g.remove();return;}
  g.querySelector('.k').textContent='Value generated · est.';
  const s=g.querySelector('.s');s.textContent='volume × 5% — a bot loop is two swaps but pays one fee, so this side reads high';s.style.color='rgba(252,211,77,.8)';});
if(v==='A'){const n=document.createElement('div');n.className='vs-note';n.style.cssText='margin-top:10px;padding:10px 12px;border:1px solid rgba(255,255,255,.12);border-radius:14px;background:rgba(0,0,0,.3);font-size:13px;color:rgba(255,255,255,.7)';
  n.innerHTML='<b style="color:#fff">Value generated</b> comes back here once it is measured from the fee transfers on chain — the old figure (volume × fee) gave bots about twice their real share.';
  d.querySelector('.vs-card.bo').parentElement.after(n);}
return 'ok '+v;})()
