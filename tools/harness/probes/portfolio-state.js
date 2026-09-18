/* portfolio.html: the wallet chips (dot colour = loading / data / failed), the UFO reflections tile,
   the lifetime bar and each wallet box's reflections text — for the a12 queue / pending / failed checks. */
(()=>{
  const t=document.body.innerText.replace(/\s+/g,' ');const tl=t.toLowerCase();
  const chips=[...document.querySelectorAll('input[type=checkbox][aria-label^="Include"]')].map(cb=>{const row=cb.parentElement;const dot=row.querySelector('span.w-2');return{name:row.innerText.replace(/\s+/g,' ').trim().slice(0,40),dot:dot?[...dot.classList].find(c=>/^bg-/.test(c)):null,retry:!!row.querySelector('button[aria-label^="Retry"]')};});
  const tile=(tl.match(/reflections (scanning[^t]{0,40}|unavailable ?retry|[\d.,]+[kmbt]? \$[\d,]+)/)||[])[1]||null;
  const bar=(tl.match(/total lifetime earned ([^•]{0,90})/g)||[]).map(x=>x.slice(0,110));
  const boxes=(tl.match(/ufo reflections ([^u]{0,30})/g)||[]).map(x=>x.replace('ufo reflections ','').trim().slice(0,28));
  return{chips,tile,bar,boxes,errors:(t.match(/Something went wrong|calculating soon/g)||[])};
})()
