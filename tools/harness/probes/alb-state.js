// Affiliate leaderboard v2: which switches are on, the podium names / values, the row count, overflow inside the window.
(()=>{const w=document.querySelector('.alb');if(!w)return 'no window';
 const on=[...w.querySelectorAll('.alb-sw [aria-pressed="true"],.alb-sw .mo.on')].map(e=>e.textContent.trim()).join(' + ');
 const pod=[...w.querySelectorAll('.alb-pc .pad')].map(p=>p.innerText.replace(/\n/g,' ')).join(' || ');
 const rows=w.querySelectorAll('.alb-r').length;
 const ov=[...w.querySelectorAll('*')].filter(e=>e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflowX!=='visible'&&!e.matches('.nm,.n,select')).map(e=>e.className).slice(0,5);
 return {mo:w.classList.contains('mo'),on,pod,rows,winW:w.clientWidth,hscroll:document.documentElement.scrollWidth>innerWidth,ov};})()
