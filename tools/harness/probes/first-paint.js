/* a62 probe: how long after the page started does each Home card stop being a skeleton?
   Reports ms on the page's own clock. Run with SLOW_RPC=6000 so the on-chain bootstrap
   outlasts the 5 s bootReady race — the case where a card waited on a read it never uses. */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const now=()=>Math.round(performance.now());
  const out={mounted:null,firstCard:null,bothCards:null,cardsAtEnd:0};
  for(let i=0;i<220;i++){
    const root=document.querySelector('#root');
    if(!out.mounted&&root&&root.children.length>0)out.mounted=now();
    const cards=document.querySelectorAll('.token-card').length;
    if(!out.firstCard&&cards>=1)out.firstCard=now();
    if(!out.bothCards&&cards>=2){out.bothCards=now();break;}
    await sleep(100);
  }
  out.cardsAtEnd=document.querySelectorAll('.token-card').length;
  return out;
})()
