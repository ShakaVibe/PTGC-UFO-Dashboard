/* affil-registry.js (2026-09-22) — reads the Referrers Registry table AND a referrer's card back.
   The AFFIL_DATA fixture's `referrers` entries carry only wallet + addedDate, no
   totalBuys/totalPtgc/totalUsd — which is exactly the live shape that printed zeros for three
   real referrers. Before the fix every Buys / PTGC Bought / Value (USD) cell in the Registry read
   0 or $0.00 (`r.totalBuys||0` on a field that is not there); after it they are the sums of each
   referrer's monthly entries, from the one shared lifetimeByUser map. The card is checked in the
   same run because it used to keep its OWN copy of that sum and now reads the same map — its
   three tiles must not move. Run with AFFIL_DATA=1. */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const click=(re,maxLen=80)=>{
    const el=[...document.querySelectorAll('button,[role=button],summary,h2,h3,div,td,span')]
      .filter(e=>re.test(e.textContent||'')&&(e.textContent||'').length<maxLen)
      .sort((a,b)=>(a.textContent||'').length-(b.textContent||'').length)[0];
    if(el){(el.closest('button')||el).click();return true;}
    return false;
  };
  const opened=click(/Referrers Registry/);
  await sleep(1200);
  const t=[...document.querySelectorAll('table')].find(x=>/PTGC Bought/.test(x.innerText)&&/Comm\. Paid|Paid \(USD\)/.test(x.innerText));
  if(!t)return{opened,error:'registry table not found'};
  const head=[...t.querySelectorAll('thead th,thead td')].map(c=>c.innerText.trim().replace(/[↑↓↕]/g,''));
  const rows=[...t.querySelectorAll('tbody tr')].map(r=>[...r.children].map(c=>c.innerText.trim().replace(/\n/g,' ')));
  const zeroRows=rows.filter(r=>/^0$/.test(r[2]||'')&&/^\$0(\.00)?$/.test(r[4]||'')).length;
  // the card: its lifetime tiles must match the row above
  click(/^alice$/,30);
  await sleep(1800);
  const dlg=document.querySelector('[role=dialog]');
  const card=dlg?dlg.innerText.split('\n').map(s=>s.trim()).filter(Boolean):null;
  const pick=(label)=>{ if(!card)return null; const i=card.indexOf(label); return i<0?null:card.slice(i+1,i+3).join(' '); };
  return{opened,head,rows,rowsWithZeroBuysAndZeroUsd:zeroRows,
    cardOpen:!!dlg, cardTotalBuys:pick('TOTAL BUYS'), cardPtgcBought:pick('PTGC BOUGHT')};
})()
