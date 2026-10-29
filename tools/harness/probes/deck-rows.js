// 2026-10-29 (Live Feed BUY / SELL only): every tape row's type badge, its words, pool line and lifted amount, plus the sum of the
// lifted amounts and whether "ARB" / "looped" appears anywhere in the open window. Run with DECK_LOOP=1 DECK_LOGS=n: the newest
// transaction is a loop (a BUY on the stub pair + a SELL on a second pool) — it must read as TWO rows, BUY and SELL, sharing one fee.
(()=>{const d=document.querySelector('[role=dialog]');if(!d)return'no dialog';
  const rows=[...d.querySelectorAll('.deck-row')].map(r=>{const q=s=>(r.querySelector(s)||{}).innerText||'';
    return{side:q('.deck-side'),what:q('.deck-contact span'),pool:q('.deck-contact a').replace(/\s+/g,' '),lift:q('.deck-gen').replace(/\s+/g,'')};});
  const lifted=rows.reduce((a,r)=>a+(parseFloat(r.lift.replace(/[^0-9.]/g,''))||0),0);
  return{n:rows.length,rows,liftedSum:+lifted.toFixed(4),arbText:/\bARB\b/.test(d.innerText),loopedText:/looped/i.test(d.innerText)};})()
