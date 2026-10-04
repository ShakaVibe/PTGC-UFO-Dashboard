/* New Holder Details share card (2026-10-04): which card is up, the pressed toolbar pills, the counts and the load overlay. */
(()=>{
  const d=document.querySelector('[role="dialog"][aria-label="New holders share card"]');
  if(!d)return JSON.stringify({open:false});
  const card=d.querySelector('.nhs');
  return JSON.stringify({
    open:true,
    mode:card?(card.classList.contains('combo')?'BOTH':card.classList.contains('ufo')?'UFO':'PTGC'):null,
    pressed:[...d.querySelectorAll('[aria-pressed="true"]')].map(b=>b.textContent.trim()),
    title:(d.querySelector('.nhs-title')||{}).textContent,
    period:(d.querySelector('.nhs-period')||{}).textContent,
    counts:[...d.querySelectorAll('.nhs-big .n, .nhs-col .n')].map(e=>e.textContent),
    holds:[...d.querySelectorAll('.nhs .v')].map(e=>e.textContent),
    usd:[...d.querySelectorAll('.nhs .u')].map(e=>e.textContent),
    fit:[...d.querySelectorAll('.nhs-fit>div')].map(e=>e.style.transform),
    overlay:(d.querySelector('[role="status"]')||{}).textContent||null
  });
})();
