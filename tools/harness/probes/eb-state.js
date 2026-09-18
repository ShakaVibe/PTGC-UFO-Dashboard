/* index.html: is the ErrorBoundary card showing, and which token/route is on screen (a26). */
(()=>{const t=document.body.innerText.replace(/\s+/g,' ');return{card:/Something went wrong/.test(t),hash:location.hash,head:t.slice(0,90)};})()
