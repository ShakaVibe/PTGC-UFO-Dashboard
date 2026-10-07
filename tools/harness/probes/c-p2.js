// Audit III batch 2 (c23 / c24 / c26 / c27): the LP band's three figures + the first rows' volume / txns, the open window's
// subtitle / chart heading / foot, the Humans vs Bots chart's x labels, the Socials RH card totals (when the hub is open)
(()=>{const q=(s,r=document)=>r.querySelector(s),qa=(s,r=document)=>[...r.querySelectorAll(s)];const t=e=>e?e.textContent.replace(/\s+/g,' ').trim():null;
const band=q('.p2-lphb');const rows=qa('.p2-lpr').slice(0,4);const d=q('[role=dialog]');
return JSON.stringify({
  band:band?qa('.p2-lphk',band).map(k=>t(q('.l',k))+'='+t(q('.v',k))):null,
  rows:rows.map(r=>({name:t(q('.p2-lpnm .p',r)),vol:t(q('.p2-lpv',r)),vg:t(q('.c-vg',r)),tx:t(q('.p2-lptx .t',r)),bs:t(q('.p2-lptx .bs',r)),vl:t(q('.c-vl',r))})),
  foot:qa('.p2-lpfoot span, .p2-lpf span').map(t).slice(0,4),
  dlg:d?{sub:t(q('.rc-sub',d)),hdr:qa('.vw-hdr .t',d).map(t),conf:qa('.vw-conf',d).map(t),vs:qa('.vs-chart text',d).map(t)}:null,
  rh:qa('[style*="with RH cores"]').length?null:qa('div').filter(e=>e.textContent==='with RH cores').map(e=>t(e.previousElementSibling))
});})()
