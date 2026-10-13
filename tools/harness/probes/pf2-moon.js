/* Portfolio v2 round 11: Moon Math — PLS ×2 must double PTGC + UFO values (same price in PLS); ATH / Live toggle state */
(async()=>{const S=ms=>new Promise(r=>setTimeout(r,ms));const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const t=(el,v)=>{Object.getOwnPropertyDescriptor(HTMLInputElement.prototype,'value').set.call(el,v);el.dispatchEvent(new Event('input',{bubbles:true}));};
const num=s=>parseFloat(s.replace(/[^0-9.]/g,''));const o={};
o.before=$('.pf2-st.p .v').textContent;$('.pf2-st.mm').click();await S(300);
o.liveOn=$$('.pf2-mmt button').map(b=>b.className).join('|');
const pls=$$('.pf2-mmf input')[2];const livePls=num(pls.placeholder);t(pls,String(livePls*2));await S(300);
o.after=$('.pf2-st.p .v').textContent;o.ratio=(num(o.after)/num(o.before)).toFixed(4);o.hint=($('.pf2-mmp .hint')||{}).textContent;o.mode=$$('.pf2-mmt button').map(b=>b.className).join('|')+' '+(($('.pf2-mmt .cu')||{}).textContent||'');
$$('.pf2-mmt button')[1].click();await S(300);o.athOn=$$('.pf2-mmt button').map(b=>b.className).join('|');
$$('.pf2-mmt button')[0].click();await S(300);o.backLive=$('.pf2-st.p .v').textContent===o.before;
return JSON.stringify(o);})()
