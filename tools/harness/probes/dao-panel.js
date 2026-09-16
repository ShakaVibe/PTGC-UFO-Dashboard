/* DAO Treasury panel text (a16) + the Holders tile/modal (a24) + the header price's accessible name (a48). */
(() => {
  const txt = document.body.innerText;
  const dao = (txt.match(/AVAILABLE FOR PROPOSALS[\s\S]{0,200}?TOTAL DAO VALUE[\s\S]{0,40}/) || [''])[0].replace(/\n+/g, ' | ');
  const priceEl = document.querySelector('[role="text"][aria-label^="$"]');
  return { dao, priceLabel: priceEl && priceEl.getAttribute('aria-label'), priceVisible: priceEl && priceEl.innerText, deckReopen: sessionStorage.getItem('grays_deck_reopen') };
})()
