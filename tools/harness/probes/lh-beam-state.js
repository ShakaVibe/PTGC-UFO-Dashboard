// LEAGUE HISTORY beam: section widths (px), the tip's text and its box against the beam's, the selected card, the page width
(()=>{const b=document.querySelector('.lh-bm');if(!b)return 'no beam';const br=b.getBoundingClientRect(),tp=b.querySelector('.lh-bm-tip'),tr=tp&&tp.getBoundingClientRect();
 return{secs:[...b.querySelectorAll('.lh-bm-s')].map(s=>s.dataset.i+':'+Math.round(s.getBoundingClientRect().width)).join(' '),beamW:Math.round(br.width),
  tip:tp?tp.innerText.replace(/\n/g,' | '):null,tipL:tr?Math.round(tr.left-br.left):null,tipR:tr?Math.round(br.right-tr.right):null,
  sel:(document.querySelector('.lh-cd[aria-pressed="true"] .nm')||{}).innerText,card:(document.querySelector('.lh-cd .vr')||{}).innerText,pageW:document.documentElement.scrollWidth};})()
