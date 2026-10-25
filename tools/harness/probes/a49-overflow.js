// a49: at a 20 px root font, list boxes in the open window whose content is cut (scroll > client with overflow hidden)
(()=>{const d=[...document.querySelectorAll('[role=dialog]')].pop()||document.body;const out=[];
d.querySelectorAll('*').forEach(e=>{const cs=getComputedStyle(e);if(!/hidden|clip/.test(cs.overflow+cs.overflowY+cs.overflowX))return;
if(e.scrollHeight>e.clientHeight+2||e.scrollWidth>e.clientWidth+2){const t=(e.innerText||'').trim().replace(/\s+/g,' ').slice(0,40);if(t&&e.clientHeight>12)out.push(`${t} [${e.clientWidth}x${e.clientHeight} < ${e.scrollWidth}x${e.scrollHeight}]`);}});
return out.slice(0,12).join(' | ')||'nothing cut';})()
