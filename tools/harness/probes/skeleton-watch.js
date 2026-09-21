/* a51 probe: tap Refresh, then watch for the dashboard falling back to its loading skeleton.
   Polls fast, because a re-load that throws again can come and go inside a second — the
   flicker IS the bug. Use with a build that throws after first paint (see the README). */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const isSkeleton=()=>!!document.querySelector('[aria-busy="true"][aria-label^="Loading "]');
  const btn=document.querySelector('button[aria-label^="Refresh"]');
  if(!btn)return{error:'no refresh button'};
  let sawSkeleton=false,samples=0;
  btn.click();
  for(let i=0;i<80;i++){samples++;if(isSkeleton())sawSkeleton=true;await sleep(50);}
  return{sawSkeletonAfterRefresh:sawSkeleton,samples,skeletonNow:isSkeleton()};
})()
