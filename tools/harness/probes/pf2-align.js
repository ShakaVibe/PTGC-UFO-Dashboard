/* Portfolio v2 round 2: the two token cards' bands must line up — each band's top y in the PTGC card vs the UFO card, and
   the two cards' bottoms. Desktop only (≥ 981 px: side by side). */
(()=>{const c=[...document.querySelectorAll('.pf2-tk')];if(c.length<2)return'no cards';
const rows=k=>[...c[k].children].map(e=>Math.round(e.getBoundingClientRect().top));
const a=rows(0),b=rows(1);return JSON.stringify({ptgc:a,ufo:b,same:a.join()===b.join(),bottoms:c.map(e=>Math.round(e.getBoundingClientRect().bottom)),crw:[...document.querySelectorAll('.pf2-crw')].map(e=>Math.round(e.getBoundingClientRect().height))});})()
