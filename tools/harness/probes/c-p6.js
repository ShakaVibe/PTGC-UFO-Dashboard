// Audit III batch 6 (c30): Leagues window scrollability, the deck HUD / tape, the KPI Value Gen tag vs its ⓘ, the calculators price strip,
// the Liquidity tile's chain note
(()=>{const q=s=>document.querySelector(s);const r=e=>e&&e.getBoundingClientRect();const o={w:innerWidth};
const lg=q('.lg-m');if(lg){const cs=getComputedStyle(lg);o.lg={oy:cs.overflowY,ox:cs.overflowX,h:Math.round(lg.clientHeight),sh:lg.scrollHeight,canScroll:lg.scrollHeight>lg.clientHeight&&cs.overflowY!=='hidden'};}
const tp=[...document.querySelectorAll('span')].find(e=>e.textContent.trim()==='TOP POOLS');if(tp){const b=r(tp);o.topPools={x:Math.round(b.left),y:Math.round(b.top),onScreen:b.left>=0&&b.right<=innerWidth};}
const tw=q('.deck-tapewrap');if(tw){const cs=getComputedStyle(tw,'::after');o.tape={sw:tw.scrollWidth,cw:tw.clientWidth,fade:cs.content!=='none'&&cs.width!=='auto'?cs.width:'none'};}
const tag=q('.kp .kp-t .r1 .kp-chip.tag'),info=tag&&tag.parentElement.querySelector('.kp-info');if(tag&&info){const a=r(tag),b=r(info);o.kpTag={tag:[Math.round(a.left),Math.round(a.right)],info:[Math.round(b.left),Math.round(b.right)],overlap:a.right>b.left+1&&a.left<b.right-1};}
const liq=q('.h2-tile.h2-liq');if(liq)o.liq=liq.innerText.replace(/\s+/g,' ').trim();
const strips=[...document.querySelectorAll('.grid.grid-cols-1')].filter(e=>/Price/.test(e.textContent)).map(e=>getComputedStyle(e).gridTemplateColumns.split(' ').length);if(strips.length)o.calcStrips=strips;
return JSON.stringify(o);})()
