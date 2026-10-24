// LEAGUE HISTORY: each card's text lines + its height; scrolls the cards into view
(()=>{const cs=[...document.querySelectorAll('.lh-cd')];cs[0].scrollIntoView({block:'start'});return cs.map(c=>Math.round(c.getBoundingClientRect().height)+' | '+[...c.querySelectorAll('.hd2,.av,.jl')].map(e=>e.innerText+'('+Math.round(e.getBoundingClientRect().height)+')').join(' / '));})()
