// Audit III batch 5b (c15): broken images (naturalWidth 0 after load) and background-image urls that did not paint (checked by
// fetching each url once); plus the distinct image urls on the page
(async()=>{const imgs=[...document.images];const broken=imgs.filter(i=>i.complete&&i.naturalWidth===0&&i.getAttribute('src')).map(i=>i.getAttribute('src')).slice(0,10);
const urls=new Set();for(const e of document.querySelectorAll('*')){const b=getComputedStyle(e).backgroundImage;if(b&&b!=='none'){for(const m of b.matchAll(/url\(["']?([^"')]+)["']?\)/g))urls.add(m[1]);}}
const bad=[];for(const u of urls){if(/^data:/.test(u))continue;try{const r=await fetch(u,{method:'GET'});if(!r.ok)bad.push(u.split('/').slice(-2).join('/')+':'+r.status);}catch(e){bad.push(u+':err');}}
return JSON.stringify({imgs:imgs.length,broken,bgUrls:urls.size,bgBad:bad,webp:[...urls].filter(u=>/\.webp/.test(u)).length,jpgLeft:[...urls].filter(u=>/\.(jpg|png)(\?|$)/.test(u)).map(u=>u.split('/').pop()).slice(0,12)});})()
