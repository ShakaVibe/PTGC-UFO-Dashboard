(async()=>{const q=s=>[...document.querySelectorAll(s)];const S=ms=>new Promise(r=>setTimeout(r,ms));const out={};
const tiny=q('.pf2 button, .pf2 a, .pf2 [role=switch]').filter(e=>e.offsetParent).map(e=>{const r=e.getBoundingClientRect();return{t:(e.getAttribute('aria-label')||e.innerText||'').trim().slice(0,22),w:Math.round(r.width),h:Math.round(r.height)}}).filter(x=>x.w<24||x.h<24);
out.smallTargets=tiny;
const small=q('.pf2 *').filter(e=>e.children.length===0&&e.innerText&&e.innerText.trim()&&e.offsetParent&&!/^(SUB|SUP)$/.test(e.tagName)).map(e=>({t:e.innerText.trim().slice(0,22),fs:parseFloat(getComputedStyle(e).fontSize)})).filter(x=>x.fs<12);out.smallText=small;
/* keyboard: focus the chart, press ArrowLeft twice, read the live region */
const hp=document.querySelector('.pf2-hp');hp.focus();await S(50);hp.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}));hp.dispatchEvent(new KeyboardEvent('keydown',{key:'ArrowLeft',bubbles:true}));await S(200);out.live=(document.querySelector('.pf2-vh .pf2-sr')||{}).innerText;out.tip=!!document.querySelector('.pf2-htip');
/* focus trap: open edit, Tab from the last focusable wraps to the first */
document.querySelector('.pf2-ed').click();await S(300);const dlg=document.querySelector('[role=dialog]');const f=[...dlg.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled])')].filter(x=>x.offsetParent);
out.editFocus=document.activeElement&&document.activeElement.id;f[f.length-1].focus();document.dispatchEvent(new KeyboardEvent('keydown',{key:'Tab',bubbles:true}));await S(50);out.wrapped=document.activeElement===f[0];
document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));await S(300);out.focusBack=(document.activeElement.getAttribute('aria-label')||'').slice(0,20);out.bodyPos=document.body.style.position||'static';
document.querySelector('.pf2-how').click();await S(300);out.howDialog=!!document.querySelector('.pf2-modal[role=dialog]');document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));await S(200);out.howClosed=!document.querySelector('.pf2-modal');
return out;})()
