// Combined Value Generated card (2026-09-29): the room inside each token panel (its flex spacer above the split bar)
// and whether the panel's own content spills past its bottom edge. Want spacer >= 25 px on each (a Mac draws ~10 px taller).
(()=>[...document.querySelectorAll('div')].filter(d=>(d.offsetWidth===1200&&d.offsetHeight===675)||(d.offsetWidth===1080&&d.offsetHeight===1350)).map(c=>{
  const sc=c.getBoundingClientRect().width/c.offsetWidth;
  const panels=[...c.querySelectorAll('div')].filter(d=>d.style.borderRadius==='20px'&&d.style.flexDirection==='column');
  return{card:c.offsetWidth+'x'+c.offsetHeight,panels:panels.map(p=>{const pb=p.getBoundingClientRect();const sp=[...p.children].find(k=>k.style.minHeight==='10px');
    const last=p.lastElementChild.getBoundingClientRect();return{spacer:sp?Math.round(sp.getBoundingClientRect().height/sc):null,spill:Math.round((last.bottom-pb.bottom)/sc)};})};
}).filter(x=>x.panels.length))()
