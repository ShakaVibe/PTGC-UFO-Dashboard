// a56: page scroll width and the first elements that stick out past the viewport
(()=>{const W=window.innerWidth;const xs=[...document.querySelectorAll('body *')].filter(e=>e.offsetParent&&e.getBoundingClientRect().right>W+1&&getComputedStyle(e).position!=='fixed');
const leaf=xs.filter(e=>!xs.some(o=>o!==e&&e.contains(o)));
return document.documentElement.scrollWidth+'/'+W+' '+leaf.slice(0,4).map(e=>(e.innerText||e.tagName).trim().replace(/\s+/g,' ').slice(0,30)+'@'+Math.round(e.getBoundingClientRect().right)).join(' | ');})()
