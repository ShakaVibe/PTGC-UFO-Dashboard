// a46: buttons inside the open window smaller than 32 × 32 px (visible ones only)
(()=>{const d=[...document.querySelectorAll('[role=dialog]')].pop()||document;const out=[];
d.querySelectorAll('button,a[href],[role=button],input[type=checkbox]').forEach(b=>{const r=b.getBoundingClientRect();if(!r.width||!r.height)return;const cs=getComputedStyle(b);if(cs.visibility==='hidden')return;
if(r.width<32||r.height<32)out.push(`${(b.getAttribute('aria-label')||b.innerText||b.title||b.tagName).trim().slice(0,24)} ${Math.round(r.width)}x${Math.round(r.height)}`);});
return out.join(' | ')||'all ≥ 32';})()
