/* Portfolio v2 (2026-10-13): the classic body's fingerprint with the faint preview dot taken out — run on portfolio.orig.html
   and portfolio.html with no preview flag; the two `h` must match. */
(()=>{const r=document.getElementById('root').cloneNode(true);r.querySelectorAll('.pf2-dotbtn').forEach(e=>e.remove());const s=r.innerHTML;let h=0;for(let i=0;i<s.length;i++)h=(h*31+s.charCodeAt(i))|0;return JSON.stringify({h:h>>>0,len:s.length,dot:!!document.querySelector('.pf2-dotbtn'),v2:!!document.querySelector('.pf2')})})()
