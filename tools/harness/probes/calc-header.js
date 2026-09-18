/* calculators.html: what the header and the mounted tab say right now — for the token-switch
   race (a7) and the keep-mounted switch (a9). Returns the header token, the price text, the
   X-factor / Rewards holding inputs (whichever tab is open), the amber "Loading … data" banner
   and the per-token bags in localStorage. */
(()=>{
  const q=s=>document.querySelector(s);
  const hdr=q('header');
  const tokenEl=hdr&&hdr.querySelector('.font-orbitron');
  const price=(()=>{const t=hdr?hdr.innerText:'';const m=t.match(/\$[0-9.,₀-₉]+/);return m?m[0]:null;})();
  const xf=q('input[type="number"][step="any"]');
  const hold=q('input[placeholder="Enter total held"]');
  const banner=[...document.querySelectorAll('[role="status"]')].map(e=>e.innerText).join(' | ');
  const ls={};for(const k of Object.keys(localStorage))if(k.startsWith('grays_calc_'))ls[k]=localStorage.getItem(k);
  const live=[...document.querySelectorAll('span')].filter(e=>/^(Live|Loading|Unavailable)$/.test(e.textContent.trim())).map(e=>e.textContent.trim());
  return{token:tokenEl?tokenEl.textContent.trim():null,price,xFactor:xf?xf.value:null,holding:hold?hold.value:null,banner,badges:[...new Set(live)],ls};
})()
