/* a59 probe: which token charts.html opened as, and how the x axis labels its points.
   `daily` is the 1M+ tier, where every candle is a UTC midnight, so the labels must not move
   with the viewer's time zone — run this under two TZ values and compare `ticks`. */
(function(){
  const cv = document.querySelector('canvas');
  const c = (window.Chart && Chart.getChart) ? Chart.getChart(cv) : null;
  const sx = c && c.scales && c.scales.x;
  const ds = c && c.data && c.data.datasets && c.data.datasets.find(d => d.data && d.data.length);
  const pt = ds && ds.data[ds.data.length - 1];
  const x = pt && (pt.x != null ? pt.x : pt[0]);
  return {
    token: typeof currentHdrToken !== 'undefined' ? currentHdrToken : '(undefined)',
    lastTokenKey: (()=>{try{return localStorage.getItem('ptgc_last_token')}catch(e){return 'n/a'}})(),
    days: typeof getDays === 'function' ? getDays() : null,
    daily: typeof isDailyTier === 'function' ? isDailyTier() : 'no isDailyTier',
    tz: Intl.DateTimeFormat().resolvedOptions().timeZone,
    ticks: sx ? sx.ticks.map(t => t.label) : 'no x scale',
    lastPointUtc: x ? new Date(x).toISOString() : null,
    lastPointIsUtcMidnight: x ? (x % 86400000 === 0) : null,
    tooltipSample: (function(){
      if (!x) return null;
      const daily = typeof isDailyTier === 'function' && isDailyTier();
      return new Date(x).toLocaleDateString('en-US', Object.assign(
        { month: 'short', day: 'numeric' },
        (typeof getDays === 'function' && getDays() <= 7) ? { hour: '2-digit', minute: '2-digit' } : {},
        daily ? { timeZone: 'UTC' } : {}
      )) + (daily ? ' UTC' : '');
    })()
  };
})()
