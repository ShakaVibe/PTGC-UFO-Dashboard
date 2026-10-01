(()=>{const out=[];const st=document.createElement('style');document.head.appendChild(st);
for(const [fs,ls,ico,gap,pr] of [[12,'.05em',52,8,8],[12,'.04em',52,7,6],[12.5,'.04em',50,7,6],[13,'.03em',50,7,6],[13,'.02em',48,7,6]]){
 st.textContent=`.p2 .p2-vgt{column-gap:${gap}px!important;padding-right:${pr}px!important}.p2 .p2-vgt>div:first-child>span:first-child{max-width:${ico}px!important}.p2 .p2-vgt img.p2-vgi{max-width:${ico}px!important}.p2 .p2-vgt .p2-vgn{font-size:${fs}px!important;letter-spacing:${ls}!important;white-space:nowrap!important}`;
 const r=[...document.querySelectorAll('.p2-vgt .p2-vgn')].map(n=>{const rg=document.createRange();rg.selectNodeContents(n.firstChild);return [n.firstChild.textContent.trim(),Math.round(rg.getBoundingClientRect().width*10)/10,n.clientWidth]});
 out.push({fs,ls,ico,gap,pr,fits:r.every(x=>x[1]<=x[2]-1),r:r.map(x=>x.join(':')).join(' ')});}
return JSON.stringify(out)})()
