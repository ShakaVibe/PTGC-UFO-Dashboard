(()=>{const b=[...document.querySelectorAll('button.p2-lg')].filter(x=>/Leagues|Top 100/.test(x.textContent));const sec=b[0]&&b[0].closest('section');const h=sec.querySelector('h3');const row=h.parentElement;
const R=e=>{const r=e.getBoundingClientRect();return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]};
return JSON.stringify({row:R(row),h3:R(h),btns:b.map(x=>[x.textContent,R(x)])});})()
