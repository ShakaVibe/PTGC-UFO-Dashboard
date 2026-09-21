/* Move the page's clock forward by window.__shiftMin minutes (default 20). Two uses: stepping
   past the 5-minute DexScreener cache bucket (cacheBucket()) so the next refresh really
   re-fetches, and ageing a snapshot without waiting for it (a52). Touches nothing but Date.now.
   Note: harness actions are split on ';', so a clock shift has to live in a probe file, not an
   inline eval=. */
(function(){
  if(window.__clockShifted)return'already shifted';
  const orig=Date.now, add=(window.__shiftMin||20)*60*1000;
  window.__clockShifted=true;
  Date.now=()=>orig()+add;
  return 'clock +'+(add/60000)+'min';
})()
