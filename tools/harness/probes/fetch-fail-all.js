/* a18/a19 probe: from now on DexScreener, the affiliate API and every RPC POST reject —
   the share cards / KPI compare card must show their honest failure state, never "$0". */
(()=>{
  if(!window.__realFetch)window.__realFetch=window.fetch;
  window.fetch=(u,o)=>{
    const s=String(u);
    if(s.includes('commissions')||s.includes('dexscreener')||(o&&o.method==='POST'))return Promise.reject(new TypeError('fetch-fail probe'));
    return window.__realFetch(u,o);
  };
  return 'fetch patched (all)';
})();
