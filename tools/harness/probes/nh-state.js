/* Holders Details (2026-10-02): the dot, the window's headline, rows and states. Run after the window is open. */
(()=>{
  const dot=document.querySelector('button[aria-label="Holders details (preview)"]');
  const dlg=document.querySelector('[role="dialog"][aria-label$="holders details"]');
  const tileBtn=document.querySelector('button[aria-label^="Holders details —"]');
  const r={dot:!!dot,dotRect:dot?(b=>({x:b.x,y:b.y,w:b.width,h:b.height}))(dot.getBoundingClientRect()):null,tileBtn:!!tileBtn,open:!!dlg};
  if(dlg){
    const stats=[...dlg.querySelectorAll('.nh-stat .v')].map(e=>e.textContent.trim());
    r.stats=stats.slice(0,3);
    r.title=(dlg.querySelector('h2')||{}).textContent;
    r.rows=dlg.querySelectorAll('tbody tr').length;
    r.cards=dlg.querySelectorAll('.rounded-2xl.border.bg-black\\/40.p-3').length;
    r.pressed=[...dlg.querySelectorAll('[aria-pressed="true"]')].map(b=>b.textContent.trim());
    r.asOf=(dlg.querySelector('.ml-auto')||{}).textContent;
    r.err=/Couldn't load/.test(dlg.textContent);
    r.loading=!!dlg.querySelector('[aria-busy="true"]');
    r.firstRow=(dlg.querySelector('tbody tr')||dlg.querySelector('.rounded-2xl.border.bg-black\\/40.p-3')||{}).textContent;
    r.scrollX=dlg.scrollWidth>dlg.clientWidth;
    const panel=dlg.firstElementChild;r.panelW=panel.clientWidth;r.panelScrollW=panel.scrollWidth;
  }
  return JSON.stringify(r);
})();
