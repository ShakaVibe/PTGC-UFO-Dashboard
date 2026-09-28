(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>/RH Cores share card/i.test(x.getAttribute('aria-label')||''))||document.querySelector('[role=dialog]');if(!d)return 'NO MODAL';
const card=[...d.querySelectorAll('div')].find(e=>e.style.width==='1200px'&&e.style.height==='675px'&&e.style.fontFamily);if(!card)return 'NO CARD';
const cols=[...card.querySelectorAll('div')].filter(e=>e.style.width==='352px');const wrap=cols[0].parentElement.parentElement;const spacer=wrap.children[0];
const r=card.getBoundingClientRect();const sc=r.width/1200;
return JSON.stringify({scale:+sc.toFixed(3),spacerPx:Math.round(spacer.getBoundingClientRect().height/sc),colH:cols.map(c=>Math.round(c.getBoundingClientRect().height/sc)),brandBottom:Math.round((wrap.lastElementChild.getBoundingClientRect().bottom-r.top)/sc),text:card.innerText.replace(/\n+/g,' | ').slice(0,400)});})()
