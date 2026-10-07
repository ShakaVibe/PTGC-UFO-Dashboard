// Audit III batch 3 (c28 / c31): for every visible button / link whose box is under 32 px in either dimension, does the page
// still hit it 15 px above and below (and left / right) its centre? (the `.hit` / ::before boxes). Reports the ones that do not.
// Also: scrollY, the tab band's top and the active tab, for the c31 scroll check.
(()=>{const vis=e=>{const r=e.getBoundingClientRect();if(!r.width||!r.height)return null;const s=getComputedStyle(e);if(s.visibility==='hidden'||s.display==='none')return null;return r;};
const own=(el,b)=>el&&(el===b||b.contains(el));
const out=[],ok=[];const dlg=document.querySelector('[role=dialog]');const root=dlg||document;
for(const b of root.querySelectorAll('button,a')){const r=vis(b);if(!r)continue;if(r.width>=32&&r.height>=32)continue;
  const cx=r.left+r.width/2,cy=r.top+r.height/2;if(cx<0||cy<0||cx>innerWidth||cy>innerHeight)continue;
  const pts=[[cx,cy-15],[cx,cy+15],[cx-15,cy],[cx+15,cy]];const miss=pts.filter(([x,y])=>!own(document.elementFromPoint(x,y),b)).length;
  const name=(b.getAttribute('aria-label')||b.textContent||'').trim().slice(0,28);const rec=Math.round(r.width)+'x'+Math.round(r.height)+' '+name;
  (miss?out:ok).push(rec+(miss?' miss'+miss:''));}
const band=document.querySelector('.h2-tabs');const cur=band&&band.querySelector('[aria-current=page]');
return JSON.stringify({small:ok.length+out.length,covered:ok.length,notCovered:out.slice(0,30),scrollY:Math.round(scrollY),bandTop:band?Math.round(band.getBoundingClientRect().top):null,active:cur?cur.textContent.trim():null,docH:document.documentElement.scrollHeight});})()
