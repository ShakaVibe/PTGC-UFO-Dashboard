/* The four dashboard panels (Burn / Value Generated / Token Allocation / DAO Treasury or PTGC Burned by UFO) as classic
   markup (switch off): run on two builds and cmp — must be identical. Ages ("5.7h ago") are masked so the clock does not differ. */
(()=>{const s=[...document.querySelectorAll('section')].filter(x=>/TOTAL SUPPLY BURNED|VALUE GENERATED|TOKEN ALLOCATION|DAO TREASURY|PTGC BURNED BY UFO/i.test(x.textContent));return s.length+' '+s.map(x=>x.outerHTML).join('').replace(/\d+(?:\.\d+)?[smh] ago/g,'AGO');})()
