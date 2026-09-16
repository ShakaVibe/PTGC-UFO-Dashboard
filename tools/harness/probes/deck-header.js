/* Live Feed header geometry (a25): the close button and every control pill must sit inside the viewport. */
(() => {
  const deck = document.querySelector('[aria-label$="Live Feed"]');
  if (!deck) return { deck: false };
  const rect = el => { const r = el.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.right), Math.round(r.width), Math.round(r.height)]; };
  const close = deck.querySelector('button[aria-label="Close"]');
  const pills = [...deck.querySelectorAll('[role=group] button')].map(b => b.innerText.trim() + ' ' + rect(b).slice(0, 2).join('-'));
  return { vw: innerWidth, close: rect(close), pills, offscreen: [...deck.querySelectorAll('button')].filter(b => b.getBoundingClientRect().right > innerWidth + 1).length };
})()
