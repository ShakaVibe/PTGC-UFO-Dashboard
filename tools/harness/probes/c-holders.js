// c5: the tile's change line, the KPI card's holders change, the Holders ⓘ card chip — must be one number
(()=>{const tile=[...document.querySelectorAll('.h2-tile')].map(t=>t.textContent.replace(/\s+/g,' ')).find(t=>/HOLDERS/.test(t))||'';
const kp=[...document.querySelectorAll('.kp-chg, .kp .kp-t')].map(e=>e.textContent.replace(/\s+/g,' ')).filter(t=>/holder|HOLDER|\+|−|-/i.test(t)).slice(0,6);
const dlg=document.querySelector('[role=dialog]');const chip=dlg?[...dlg.querySelectorAll('span')].map(e=>e.textContent.trim()).filter(t=>/today$/.test(t)||/^[▲▼±+−-]\s?\d+ today/.test(t)).slice(0,3):null;
const quiet=dlg?[...dlg.querySelectorAll('span')].map(e=>e.textContent.trim()).filter(t=>/quiet|%$/.test(t)).slice(0,6):null;
return JSON.stringify({tile,kp,chip,quiet});})()
