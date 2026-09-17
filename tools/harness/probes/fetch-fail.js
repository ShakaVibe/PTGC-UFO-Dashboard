/* a18 probe: make the affiliate API and every DexScreener call reject from now on,
   so the share cards that depend on a second fetch hit their error state. */
(()=>{
  if(!window.__realFetch)window.__realFetch=window.fetch;
  window.fetch=(u,o)=>{
    const s=String(u);
    if(s.includes('commissions')||s.includes('dexscreener'))return Promise.reject(new TypeError('fetch-fail probe'));
    return window.__realFetch(u,o);
  };
  return 'fetch patched';
})();
