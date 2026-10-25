// Audit V v32: open the first PTGC buy row of the Ledger and return its details + the burn rows
(async()=>{const S=ms=>new Promise(r=>setTimeout(r,ms));
const rows=[...document.querySelectorAll('button,div,tr,li')].filter(e=>/Bought [0-9.]+[KMB]? PTGC/.test(e.innerText||'')&&e.innerText.length<300);
const row=rows[rows.length-1];if(!row)return 'no buy row';row.click();await S(1200);
const fee=(document.body.innerText.match(/Fee paid[^\n]*(\n[^\n]*)?/g)||[]).slice(0,3);
const burns=(document.body.innerText.match(/Burned [0-9.]+[KMB]? PTGC/g)||[]).slice(0,5);
return {row:row.innerText.replace(/\s+/g,' ').slice(0,160),fee,burns};})()
