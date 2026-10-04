/* The Holders tile's two buttons (2026-10-04): the ⓘ and the Holders Details icon to its RIGHT — rects + the icon's natural size. */
(()=>{
  const hd=document.querySelector('button[aria-label^="Holders details —"]'),info=document.querySelector('button[aria-label="Holders by period"]');
  const R=e=>e?(r=>[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)])(e.getBoundingClientRect()):null;
  const img=hd&&hd.querySelector('img');
  return JSON.stringify({hd:R(hd),info:R(info),img:img?[img.naturalWidth,img.clientWidth,img.clientHeight,img.complete]:null,rightOfInfo:!!(hd&&info)&&hd.getBoundingClientRect().left>=info.getBoundingClientRect().right});
})();
