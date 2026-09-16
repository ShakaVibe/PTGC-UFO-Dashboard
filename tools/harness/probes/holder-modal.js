/* Holder Analytics modal (a24): the hero count and the chart's last data point. */
(() => {
  const d = [...document.querySelectorAll('[role=dialog]')].pop();
  if (!d) return { modal: false };
  const hero = (d.innerText.match(/Current Holders\s*\n?\s*([^\n]+)/) || [])[1];
  const inst = window.Chart && Object.values(Chart.instances).find(c => d.contains(c.canvas));
  const data = inst ? inst.data.datasets[0].data : null;
  return { hero, points: data ? data.length : null, last: data ? data[data.length - 1] : null, min: data ? Math.min(...data.map(v => typeof v === 'object' ? v.y : v)) : null };
})()
