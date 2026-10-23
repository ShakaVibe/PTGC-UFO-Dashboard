// Audit IV e20 (2026-10-23): did the page really render? React pages: the boot shell ([data-boot]) is gone and #root holds real
// content; charts.html (plain JS): a chart canvas and text. Read by ci-mount.js.
(()=>{const root=document.getElementById('root'),t=(document.body.innerText||'').trim();
  if(root){const boot=!!root.querySelector('[data-boot]'),nodes=root.querySelectorAll('*').length;
    return JSON.stringify({ok:!boot&&nodes>40&&t.length>200,boot,nodes,text:t.length});}
  const canvas=document.querySelectorAll('canvas').length;
  return JSON.stringify({ok:canvas>0&&t.length>200,canvas,text:t.length});})()
