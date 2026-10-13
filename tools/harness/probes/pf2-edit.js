/* Portfolio v2 round 2: the Edit window — rename the first wallet and move it to a new group, saved to localStorage. */
(async()=>{const S=ms=>new Promise(r=>setTimeout(r,ms));const $=s=>document.querySelector(s);
const t=(el,v)=>{Object.getOwnPropertyDescriptor(el.tagName==='SELECT'?HTMLSelectElement.prototype:HTMLInputElement.prototype,'value').set.call(el,v);el.dispatchEvent(new Event(el.tagName==='SELECT'?'change':'input',{bubbles:true}));};
const out={pencils:document.querySelectorAll('.pf2-ed').length,pencilVisible:getComputedStyle($('.pf2-ed')).opacity};
$('.pf2-ed').click();await S(300);out.open=!!$('.pf2-ew');out.addr=$('.pf2-ew .adr .mono').textContent;
t($('#pf2-ew-n'),'Main Vault');t($('#pf2-ew-g'),'__new');await S(150);t($('.pf2-ew input[aria-label="New group name"]'),'Cold');await S(100);
$('.pf2-ew .sv').click();await S(400);
out.closed=!$('.pf2-ew');const c=document.querySelectorAll('.pf2-wc')[0];out.card=c.innerText.replace(/\n/g,' | ');
out.saved=JSON.parse(localStorage.getItem('ptgc_ufo_portfolio'))[0];out.segs=[...document.querySelectorAll('.pf2-seg button')].map(b=>b.textContent);
$('.pf2-ed').click();await S(300);document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape'}));await S(200);out.escCloses=!$('.pf2-ew');
return JSON.stringify(out);})()
