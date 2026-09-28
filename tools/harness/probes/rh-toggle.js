/* 2026-09-28: the pairs table's RH-only switch state + the distinct pair names on the page.
   Run once before and once after click=button[aria-label='Show only RH Core pairs']:visible. */
(()=>{const sw=document.querySelector('button[aria-label="Show only RH Core pairs"]');const t=document.body.innerText;return JSON.stringify({checked:sw&&sw.getAttribute('aria-checked'),pairs:(t.match(/(?:UFO|PTGC)\/[A-Za-z]+|[A-Za-z]+\/(?:UFO|PTGC)/g)||[]).filter((v,i,a)=>a.indexOf(v)===i)});})()
