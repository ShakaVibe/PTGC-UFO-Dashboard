// Holders cards (2026-09-26): how much room is left under the lowest content element, in px, per card on screen.
// Negative = overflow. Backdrop pieces (aria-hidden) and SVG internals are ignored.
(()=>{
  const cards=[...document.querySelectorAll('div')].filter(d=>(d.offsetWidth===1200&&d.offsetHeight===675)||(d.offsetWidth===1080&&d.offsetHeight===1350));
  return cards.map(card=>{
    const cb=card.getBoundingClientRect();const sc=cb.width/card.offsetWidth;
    let maxB=-Infinity,who='';
    card.querySelectorAll('*').forEach(el=>{
      if(el.closest('[aria-hidden="true"]')||el.closest('svg'))return;
      const r=el.getBoundingClientRect();if(!r.height)return;
      if(r.bottom>maxB){maxB=r.bottom;who=(el.textContent||'').trim().slice(0,20);}
    });
    return{card:card.offsetWidth+'x'+card.offsetHeight,slackPx:Math.round((cb.bottom-maxB)/sc),lowest:who};
  });
})()
