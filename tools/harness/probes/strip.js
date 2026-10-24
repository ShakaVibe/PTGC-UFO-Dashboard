// the Token Allocation creature strip: scroll to it, its text + the page's width (no horizontal scroll)
(()=>{const s=document.querySelector('.p2-strip');if(!s)return 'nostrip';s.scrollIntoView({block:'center'});return s.innerText.replace(/\n/g,' | ')+' || pageW '+document.documentElement.scrollWidth+' stripW '+Math.round(s.getBoundingClientRect().width)+'/'+s.scrollWidth})()
