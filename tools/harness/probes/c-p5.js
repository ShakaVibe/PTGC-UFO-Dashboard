// Audit III batch 5a (c12 / c13 / c14): the boot shell gone after mount, the preload links (dashboard routes only), the stylesheet
// in use, and whether any repo data fetch still carries a ?t= buster (performance entries)
(()=>{const root=document.getElementById('root');const pre=[...document.querySelectorAll('link[rel=preload]')].map(l=>l.getAttribute('href'));
const css=[...document.querySelectorAll('link[rel=stylesheet]')].map(l=>l.getAttribute('href'));const tw=!![...document.scripts].find(s=>/cdn\.tailwindcss/.test(s.src));
const ent=performance.getEntriesByType('resource').map(e=>e.name).filter(n=>/main\/data\//.test(n));const busted=ent.filter(n=>/[?&]t=\d{10,}/.test(n)).length;
return JSON.stringify({shell:!!root.querySelector('[style*="LOADING"]')||/LOADING…/.test(root.textContent.slice(0,2000)),mounted:!!root.querySelector('.h2, .hc-card, [class*=home]'),preload:pre,css,playCdn:tw,dataFetches:ent.length,busted,bustedSample:ent.filter(n=>/[?&]t=\d{10,}/.test(n)).slice(0,3).map(n=>n.split('/').pop())});})()
