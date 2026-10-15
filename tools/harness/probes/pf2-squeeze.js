/* round 39: text that spills, clips or collides at a given width. For every text node under .pf2: its range rect vs the
   nearest box ancestor (container padding edge) and vs other elements' rects (collisions, e.g. a sparkline). Also elements
   with nowrap that are wider than their box (ellipsis clipping). Returns {width, spill:[], clip:[], hit:[]}. */
(()=>{const out={width:innerWidth,spill:[],clip:[],hit:[]};const root=document.querySelector('.pf2');if(!root)return out;
const boxSel='.pf2-st,.pf2-spot,.pf2-src,.pf2-wc,.pf2-bx,.pf2-lkh,.pf2-foldh,.pf2-fr,.pf2-tl,.pf2-edload,.pf2-hwait,.pf2-tkh,.pf2-lgw,.pf2-dn,.pf2-pn';
const txt=e=>(e.innerText||'').trim().replace(/\s+/g,' ').slice(0,40);
const seen=new Set();
const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:n=>n.nodeValue.trim()?NodeFilter.FILTER_ACCEPT:NodeFilter.FILTER_REJECT});
let n;while((n=walker.nextNode())){const el=n.parentElement;if(!el||!el.offsetParent)continue;const r=document.createRange();r.selectNodeContents(n);const rects=[...r.getClientRects()];if(!rects.length)continue;
  const box=el.closest(boxSel);if(!box)continue;const b=box.getBoundingClientRect();const cs=getComputedStyle(box);const right=b.right-parseFloat(cs.paddingRight||0),left=b.left+parseFloat(cs.paddingLeft||0);
  rects.forEach(rc=>{if(rc.width<2)return;
    if(rc.right>right+1||rc.left<left-1){const k='s'+el.className+txt(el);if(!seen.has(k)){seen.add(k);out.spill.push({t:txt(el),cls:el.className,box:box.className.split(' ')[0],over:Math.round(rc.right-right)});}}
  });
  /* collisions with sibling-ish elements that are not ancestors / descendants */
  const cand=[...box.querySelectorAll('svg,img,.pf2-spk,button,a,.bar,.g')].filter(x=>x!==el&&!x.contains(el)&&!el.contains(x)&&x.offsetParent);
  cand.forEach(x=>{const xr=x.getBoundingClientRect();rects.forEach(rc=>{const ox=Math.min(rc.right,xr.right)-Math.max(rc.left,xr.left),oy=Math.min(rc.bottom,xr.bottom)-Math.max(rc.top,xr.top);if(ox>3&&oy>3){const k='h'+txt(el)+x.tagName+x.className;if(!seen.has(k)){seen.add(k);out.hit.push({t:txt(el),with:(x.tagName+'.'+(x.getAttribute('class')||'')).slice(0,30),ox:Math.round(ox)});}}});});
}
[...root.querySelectorAll('*')].forEach(el=>{if(!el.offsetParent)return;const cs=getComputedStyle(el);if(cs.whiteSpace==='nowrap'&&el.scrollWidth>el.clientWidth+1&&(cs.overflow==='hidden'||cs.textOverflow==='ellipsis')&&!el.closest('.pf2-wc')&&!el.closest('.pf2-fr .wc')&&!el.closest('.pf2-fr .t1')){out.clip.push({t:txt(el),cls:el.className,by:el.scrollWidth-el.clientWidth});}});
return out;})()
