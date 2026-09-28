/* 2026-09-28: rows + total of the "LP with RH Core Coins" modal (open it first with
   click=button[aria-label='Liquidity with RH Core coins']:visible). UFO must never list WETH. */
(()=>{const d=[...document.querySelectorAll('[role=dialog]')].find(x=>/LP with RH Core Coins/.test(x.innerText));if(!d)return 'NO MODAL';const rows=[...d.querySelectorAll('.text-gray-500')].map(e=>e.innerText).filter(t=>/ pair$/.test(t));return JSON.stringify({total:(d.innerText.match(/\$[\d,]+/)||[])[0],rows});})()
