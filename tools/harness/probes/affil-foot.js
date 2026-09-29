// Affiliates Report card (2026-09-29): the flex spacer above the All-Time bar is the card's slack (want >= 25 px;
// a Mac draws these cards ~10 px taller than the harness, gotcha 31), and the footer must sit at the bottom padding.
(()=>[...document.querySelectorAll('div')].filter(d=>(d.offsetWidth===1200&&d.offsetHeight===675)||(d.offsetWidth===1080&&d.offsetHeight===1350)).map(c=>{
  const cb=c.getBoundingClientRect(),sc=cb.width/c.offsetWidth;
  const f=[...c.querySelectorAll('span')].find(x=>(x.textContent||'').startsWith('Join:'));
  const sp=[...c.querySelectorAll('div')].find(d=>d.style.flex==='1 1 0%'&&d.style.minHeight==='12px');
  return {card:c.offsetWidth+'x'+c.offsetHeight,underFooter:f?Math.round((cb.bottom-f.getBoundingClientRect().bottom)/sc):null,slack:sp?Math.round(sp.getBoundingClientRect().height/sc):null};
}).filter(x=>x.underFooter!=null))()
