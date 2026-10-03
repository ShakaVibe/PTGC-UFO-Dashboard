// Socials Hub (2026-10-03): the rows in page order per column, the sky img, and any row whose icon failed to load
(()=>{const cols=[...document.querySelectorAll('.sh-col')];
const out=cols.map(c=>c.querySelector('.nm').textContent+': '+[...c.querySelectorAll('.sh-row .t')].map(t=>t.textContent).join(' | '));
const bad=[...document.querySelectorAll('.sh img')].filter(i=>i.complete&&i.naturalWidth===0).map(i=>i.getAttribute('src'));
const sky=document.querySelector('.sh-sky img');
return out.join('\n')+'\nbroken imgs: '+(bad.length?bad.join(', '):'none')+'\nsky: '+(sky?sky.naturalWidth+'x'+sky.naturalHeight:'MISSING')+'\nhub width: '+document.querySelector('.sh').getBoundingClientRect().width+' / doc '+document.documentElement.scrollWidth;})()
