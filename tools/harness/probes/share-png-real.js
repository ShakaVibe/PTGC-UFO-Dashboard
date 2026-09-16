(async()=>{
  if(typeof window.html2canvas!=='function'){await new Promise((res,rej)=>{const el=document.createElement('script');el.src='https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';el.onload=res;el.onerror=rej;document.head.appendChild(el);});}
  // Drive the real Download button, but capture the blob instead of saving it.
  const wrap=document.querySelector('[data-share-wrap]');const W=parseInt(wrap.style.width),H=parseInt(wrap.style.height);
  const origCreate=URL.createObjectURL;let blob=null;URL.createObjectURL=(b)=>{blob=b;return origCreate.call(URL,b);};
  const a0=HTMLAnchorElement.prototype.click;HTMLAnchorElement.prototype.click=function(){if(this.download)return;return a0.call(this);};
  // The card's own button first (aria-label "Download PNG"); the Socials tab also has "Download official logos" buttons earlier in DOM order.
  const btn=document.querySelector('button[aria-label="Download PNG"]')||[...document.querySelectorAll('button')].find(b=>/download/i.test(b.textContent)||/download/i.test(b.getAttribute('aria-label')||''));
  if(!btn)return 'no download button';
  btn.click();
  for(let i=0;i<60&&!blob;i++)await new Promise(r=>setTimeout(r,250));
  if(!blob)return 'no blob';
  const img=new Image();img.src=origCreate.call(URL,blob);await new Promise(r=>img.onload=r);
  document.body.innerHTML='';document.body.style.margin='0';img.style.width=W+'px';img.style.height=H+'px';img.style.display='block';document.body.appendChild(img);
  return 'png '+img.naturalWidth+'x'+img.naturalHeight;
})()
