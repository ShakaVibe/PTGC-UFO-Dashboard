// Audit V: the text of the panel whose heading is labelled window.__h3 (climbs to the first ancestor ≥ 280 px tall)
(()=>{const h=document.querySelector(`[aria-label="${window.__h3}"]`);if(!h)return 'NO PANEL '+window.__h3;let e=h;while(e.parentElement&&e.getBoundingClientRect().height<280)e=e.parentElement;
return e.innerText.replace(/[ \t]+/g,' ').replace(/\n\s*\n+/g,'\n').trim().slice(0,5000);})()
