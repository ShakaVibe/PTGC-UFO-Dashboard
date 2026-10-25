// Audit V before/after: the open window's text (or window.__sel's), whitespace-collapsed — the numbers to compare
(()=>{const sel=window.__sel;const el=sel?document.querySelector(sel):([...document.querySelectorAll('[role=dialog]')].pop()||document.body);
if(!el)return 'NO ELEMENT '+sel;return el.innerText.replace(/[ \t]+/g,' ').replace(/\n\s*\n+/g,'\n').trim().slice(0,6000);})()
