/* Portfolio v2 round 12: Moon Math tile — Live / Custom / ATH; Custom opens the price window; typing PTGC ×2 doubles PTGC value */
(async()=>{const S=ms=>new Promise(r=>setTimeout(r,ms));const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const t=(el,v)=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));};
const num=s=>parseFloat(s.replace(/[^0-9.]/g,''));const st=()=>$$('.pf2-mmt3 button').map(b=>b.className==='on'?'['+b.textContent+']':b.textContent).join(' ');const o={};
o.start=st();o.before=$('.pf2-st.p .v').textContent;
$$('.pf2-mmt3 button')[1].click();await S(300);o.custom=st();o.pop=!!$('.pf2-mmpop');o.inputs=$$('.pf2-mmpop input').length;
const i=$$('.pf2-mmpop input')[0];t(i,String(num(i.placeholder)*2));await S(300);o.ratio=(num($('.pf2-st.p .v').textContent)/num(o.before)).toFixed(3);o.banner=($('.pf2-mm')||{}).textContent;
$('.pf2-mmpop .ok').click();await S(200);o.popClosed=!$('.pf2-mmpop');o.edit=($('.pf2-mmedit')||{}).textContent;
$$('.pf2-mmt3 button')[2].click();await S(300);o.ath=st();o.banner2=($('.pf2-mm')||{}).textContent;
$$('.pf2-mmt3 button')[0].click();await S(300);o.live=st();o.back=$('.pf2-st.p .v').textContent===o.before;
return JSON.stringify(o);})()
