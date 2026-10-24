// LEAGUE HISTORY: the readout row, the big chart's title lines, the subtitle, card 3 (Shark), the pill labels, the page width
(()=>{const q=s=>document.querySelector(s);const rd=q('.lh-rd');return{sub:(q('.lh-sub')||{}).innerText,rd:rd&&rd.innerText.replace(/\n/g,' | '),latestBtn:!!(rd&&rd.querySelector('.lh-rdx')),
  bh:q('.lh-bh')&&q('.lh-bh .l').innerText.replace(/\n/g,' | '),pills:[...document.querySelectorAll('.lh-pill .k')].map(e=>e.innerText).join(' / '),
  shark:[...document.querySelectorAll('.lh-cd')][2].innerText.replace(/\n/g,' | '),aria0:[...document.querySelectorAll('.lh-cd')][0].getAttribute('aria-label'),pageW:document.documentElement.scrollWidth};})()
