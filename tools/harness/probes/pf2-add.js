(async()=>{const S=ms=>new Promise(r=>setTimeout(r,ms));const $=s=>document.querySelector(s);const t=(el,v)=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));};
const sel=$('.pf2-add select');const setSel=v=>{Object.getOwnPropertyDescriptor(HTMLSelectElement.prototype,'value').set.call(sel,v);sel.dispatchEvent(new Event('change',{bubbles:true}));};
setSel('__new');await S(200);t($('.pf2-newg input'),'Cold');await S(100);$('.pf2-newg .pf2-lnk').click();await S(200);
t($('.pf2-add input.ad'),'0xabcdefabcdefabcdefabcdefabcdefabcdefabcd');t($$=document.querySelectorAll('.pf2-add input')[1],'Vault');await S(100);$('.pf2-addb').click();await S(6000);
const c=[...document.querySelectorAll('.pf2-wc')];const last=c[c.length-1];
return JSON.stringify({n:c.length,last:last.innerText.replace(/\n/g,' | '),segs:[...document.querySelectorAll('.pf2-seg button')].map(b=>b.textContent),saved:JSON.parse(localStorage.getItem('ptgc_ufo_portfolio')).slice(-1)[0]});})()
