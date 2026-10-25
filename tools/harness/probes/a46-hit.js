// a46: tap test — for each small control in the open window, does a tap 15 px above/below its centre still land on it?
(()=>{const d=[...document.querySelectorAll('[role=dialog]')].pop()||document;const bad=[];
d.querySelectorAll('.nh-tg button,.lh-tg button,.lh-cam,.lh-lgb,button[aria-label="Share Humans vs Bots as an image"],.vw-more').forEach(b=>{const r=b.getBoundingClientRect();if(!r.width)return;
const cx=r.left+r.width/2,cy=r.top+r.height/2;for(const dy of [-15,15]){const e=document.elementFromPoint(cx,cy+dy);if(!(e&&(e===b||b.contains(e))))bad.push((b.getAttribute('aria-label')||b.innerText).trim().slice(0,18)+' '+Math.round(r.height)+'px dy'+dy);}});
return bad.length?bad.join(' | '):'every control hit at ±15 px';})()
