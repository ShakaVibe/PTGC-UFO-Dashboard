/* a48: what a screen reader / a copy of the header price gets vs what is painted. */
(() => {
  const sr = document.querySelector('.sr-only');
  if (!sr) return { srOnly: null };
  const wrap = sr.parentElement;
  const range = document.createRange(); range.selectNodeContents(wrap);
  const sel = getSelection(); sel.removeAllRanges(); sel.addRange(range);
  const copied = sel.toString(); sel.removeAllRanges();
  return { srOnly: sr.textContent, painted: wrap.querySelector('[aria-hidden]').innerText, copied };
})()
