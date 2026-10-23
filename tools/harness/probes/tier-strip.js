(()=>{const el=[...document.querySelectorAll('[title^="People only"]')][0];return {txt:el?el.innerText.replace(/\s+/g,' '):null,ls:Object.keys(localStorage).filter(k=>/tiers/.test(k))}})()
