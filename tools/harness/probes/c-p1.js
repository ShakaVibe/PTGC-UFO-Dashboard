// Audit III P1 session: c2 overflow, c3 cues, c5 one holders number (tile vs KPI vs card chip)
(()=>{const W=document.documentElement.clientWidth;const sw=document.documentElement.scrollWidth;
const cues=[...document.querySelectorAll('.h2-cue')].map(c=>c.className.replace('h2-cue ','')+':'+c.dataset.on);
const row=document.querySelector('.h2-tabrow');const cur=row&&row.querySelector('[aria-current="page"]');
const tileChg=(document.querySelector('.h2-tile.h2-holders .h2-tc, .h2-tile[data-k="holders"] .h2-tc')||{}).textContent;
const tiles=[...document.querySelectorAll('.h2-tile')].map(t=>t.textContent.replace(/\s+/g,' ').slice(0,60));
return JSON.stringify({W,sw,cues,rowScroll:row?Math.round(row.scrollLeft):null,curX:cur?Math.round(cur.getBoundingClientRect().left):null,curW:cur?Math.round(cur.offsetWidth):null,tiles:tiles.filter(t=>/HOLDERS/.test(t))});})()
