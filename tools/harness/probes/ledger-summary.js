/* a35 probe: the Ledger summary box's text at this moment (while data may still be loading). */
(function(){const h=[...document.querySelectorAll('h2')].find(e=>/Summary/.test(e.textContent));const box=h&&h.closest('div.rounded-2xl');return box?box.innerText.replace(/\n+/g,' | ').slice(0,200):'no summary box'})()
