/* a11y / mobile scan (Audit III sweep M, 2026-10-07). Run after a load (or after opening a window):
   `evalfile=probes/a11y-scan.js`. Reports, for the VISIBLE DOM (the open dialog only when one is open):
   noName      buttons / links with no accessible name (text, aria-label, aria-labelledby, title, img alt)
   noAlt       <img> without an alt attribute (alt="" is fine)
   divClick    cursor:pointer div/span/tr/li/td without role / tabindex / button or link ancestor (click handler, not a button)
   tabRows     element groups that look like a tab row (3+ sibling buttons, one "selected" by class) with no role=tab / aria-selected
   tinyText    elements carrying their own text at font-size < 12 px (first 25, with the text)
   smallTap    interactive elements whose box is under 32×32 (first 30)
   headings    the heading outline in DOM order (tag + text)
   contrast    computed contrast of text whose colour alpha < 0.6 over the page's black (#0b0b0b), grouped by colour, worst first
   noFocusRing interactive elements whose class carries focus:outline-none / outline-none and no focus:ring / focus:border / focus-visible class
   Everything that is display:none / 0×0 / inside a closed dialog is skipped. */
(()=>{
  const root=document.querySelector('[role="dialog"]:not([aria-hidden="true"])')||document.body;
  const vis=e=>{const r=e.getBoundingClientRect();if(!(r.width>0&&r.height>0))return false;const cs=getComputedStyle(e);return cs.visibility!=='hidden'&&cs.display!=='none';};
  const all=[...root.querySelectorAll('*')].filter(vis);
  const txt=e=>(e.textContent||'').replace(/\s+/g,' ').trim();
  const desc=e=>`${e.tagName.toLowerCase()}${e.id?'#'+e.id:''}.${String(e.className&&e.className.baseVal!==undefined?e.className.baseVal:e.className||'').trim().split(/\s+/).slice(0,4).join('.')}`;
  const name=e=>{if(e.getAttribute('aria-label'))return e.getAttribute('aria-label');const lb=e.getAttribute('aria-labelledby');if(lb){const t=lb.split(/\s+/).map(i=>document.getElementById(i)).filter(Boolean).map(txt).join(' ');if(t)return t;}if(txt(e))return txt(e);if(e.title)return e.title;const im=e.querySelector('img[alt]');if(im&&im.alt)return im.alt;const sv=e.querySelector('svg[aria-label],svg title');if(sv)return sv.getAttribute('aria-label')||txt(sv);return '';};
  const inter=all.filter(e=>e.matches('button,a[href],input:not([type=hidden]),select,textarea,[role=button],[role=tab],[role=link],[tabindex]:not([tabindex="-1"])'));
  const noName=inter.filter(e=>e.matches('button,a,[role=button],[role=tab],[role=link]')&&!name(e)).map(e=>desc(e)+' html='+e.outerHTML.slice(0,90).replace(/\s+/g,' ')).slice(0,20);
  const noAlt=all.filter(e=>e.tagName==='IMG'&&!e.hasAttribute('alt')).map(e=>desc(e)+' src='+(e.getAttribute('src')||'').split('/').pop().slice(0,40)).slice(0,20);
  const divClick=all.filter(e=>/^(DIV|SPAN|TR|LI|TD|P|H[1-6]|SECTION|IMG)$/.test(e.tagName)&&getComputedStyle(e).cursor==='pointer'&&!e.getAttribute('role')&&!e.hasAttribute('tabindex')&&!e.closest('button,a[href],[role=button],[role=tab],[role=link],label,summary,[tabindex]')
    && (e.onclick||(()=>{const k=Object.keys(e).find(k=>k.startsWith('__reactProps'));return k&&typeof e[k].onClick==='function';})())
  ).map(e=>desc(e)+' text="'+txt(e).slice(0,40)+'"').slice(0,25);
  /* tab rows: a container with ≥3 direct-child buttons where at least one carries a "selected-looking" class and none has role=tab */
  const tabRows=[];all.forEach(c=>{const kids=[...c.children].filter(k=>k.tagName==='BUTTON'&&vis(k));if(kids.length<3)return;if(kids.some(k=>k.getAttribute('role')==='tab'||k.hasAttribute('aria-selected')||k.hasAttribute('aria-pressed')||k.hasAttribute('aria-current')))return;
    const sel=kids.filter(k=>/\b(active|sel|on|cur|is-active)\b/.test(String(k.className))||/\bbg-(white|\[#|purple|green|yellow|amber|\[var)/.test(String(k.className))&&!/\bbg-(white|\[#|purple|green|yellow|amber|\[var)[^ ]*\/(5|10|15|20)\b/.test(String(k.className)));
    if(sel.length>=1&&sel.length<kids.length)tabRows.push(desc(c)+' kids='+kids.length+' labels='+kids.map(k=>txt(k).slice(0,14)).join('|').slice(0,90));});
  const own=e=>[...e.childNodes].filter(n=>n.nodeType===3).map(n=>n.textContent.replace(/\s+/g,' ').trim()).join(' ').trim();
  const tinyAll=all.filter(e=>{const t=own(e);if(!t||/^[\s—·|•]*$/.test(t))return false;return parseFloat(getComputedStyle(e).fontSize)<12&&!e.closest('.sr-only')&&!e.closest('[data-share-wrap]');});
  const tinyText=tinyAll.map(e=>`${getComputedStyle(e).fontSize} ${desc(e)} "${own(e).slice(0,36)}"`).slice(0,25);
  const smallTap=inter.filter(e=>{const r=e.getBoundingClientRect();return (r.width<32||r.height<32)&&!e.matches('input[type=range]');}).map(e=>{const r=e.getBoundingClientRect();return `${Math.round(r.width)}x${Math.round(r.height)} ${desc(e)} "${name(e).slice(0,30)}"`;}).slice(0,30);
  const headings=[...root.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(vis).map(h=>h.tagName.toLowerCase()+' '+txt(h).slice(0,40));
  /* contrast: WCAG relative luminance, text colour composited over the page background (#0b0b0b unless the body says otherwise) */
  const lum=([r,g,b])=>{const f=v=>{v/=255;return v<=0.03928?v/12.92:Math.pow((v+0.055)/1.055,2.4);};return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b);};
  const parse=c=>{const m=c.match(/rgba?\(([^)]+)\)/);if(!m)return null;const p=m[1].split(/[\s,\/]+/).filter(Boolean).map(Number);return {rgb:p.slice(0,3),a:p.length>3?p[3]:1};};
  const bgc=parse(getComputedStyle(document.body).backgroundColor);const PAGE=(bgc&&bgc.a>0)?bgc.rgb:[11,11,11];
  /* the backdrop under an element: walk up, compositing every ancestor's background-color over the page black;
     an ancestor with a background-image (art, gradient) makes the result unknowable → skipped ("img") */
  const backdrop=e=>{const layers=[];for(let a=e;a;a=a.parentElement){const cs=getComputedStyle(a);if(cs.backgroundImage&&cs.backgroundImage!=='none')return null;const c=parse(cs.backgroundColor);if(c&&c.a>0)layers.push(c);if(c&&c.a>=1)break;}let out=PAGE.slice();for(let i=layers.length-1;i>=0;i--){const l=layers[i];out=out.map((v,k)=>v*(1-l.a)+l.rgb[k]*l.a);}return out;};
  const ratioOn=(fg,bg)=>{const L1=lum(fg),L2=lum(bg);return ((Math.max(L1,L2)+0.05)/(Math.min(L1,L2)+0.05));};
  const byColour={};
  all.forEach(e=>{const t=own(e);if(!t||t.length<2)return;const cs=getComputedStyle(e);const c=parse(cs.color);if(!c||c.a===0)return;if(cs.webkitTextFillColor&&/rgba\(.*, 0\)$/.test(cs.webkitTextFillColor))return;if(e.closest('[data-share-wrap]'))return;const bg=backdrop(e);if(!bg)return;const eff=c.rgb.map((v,i)=>v*c.a+bg[i]*(1-c.a));const r=ratioOn(eff,bg);if(r>=4.5)return;const fs=parseFloat(cs.fontSize),bold=parseInt(cs.fontWeight)>=700;const large=fs>=24||(fs>=18.66&&bold);if(large&&r>=3)return;const key=cs.color+' on rgb('+bg.map(Math.round).join(',')+')';(byColour[key]=byColour[key]||{ratio:+r.toFixed(2),n:0,eg:[]});byColour[key].n++;if(byColour[key].eg.length<3)byColour[key].eg.push(`${desc(e)} ${cs.fontSize} "${t.slice(0,28)}"`);});
  const contrast=Object.entries(byColour).sort((a,b)=>a[1].ratio-b[1].ratio).slice(0,14).map(([k,v])=>({color:k,ratio:v.ratio,count:v.n,eg:v.eg}));
  const noFocusRing=inter.filter(e=>{const c=String(e.className);return /(^|\s)(focus:)?outline-none(\s|$)/.test(c)&&!/focus(-visible)?:(ring|border|outline-(?!none)|shadow|bg)/.test(c)&&!/\b(tap|tap-h)\b/.test(c);}).map(e=>desc(e)+' "'+name(e).slice(0,30)+'"').slice(0,15);
  return {scope:root===document.body?'page':'dialog '+(root.getAttribute('aria-label')||''),vw:innerWidth,scrollW:document.documentElement.scrollWidth,counts:{interactive:inter.length,noName:noName.length,noAlt:noAlt.length,divClick:divClick.length,tabRows:tabRows.length,tinyText:tinyAll.length,smallTap:smallTap.length,noFocusRing:noFocusRing.length},noName,noAlt,divClick,tabRows,tinyText,smallTap,headings,contrast,noFocusRing};
})()
