/* A fingerprint of the page as rendered — for proving a classic render is unchanged between two builds
   (run the same line on <page>.orig.html and <page>.html and cmp the EVAL lines). React pages: #root's
   markup; charts.html: the <header> + the content column. Times that tick ("12s ago") are blanked. */
(()=>{const el=document.getElementById('root')||document.querySelector('header').parentElement;const s=el.innerHTML.replace(/\d+[smh] ago/g,'').replace(/<script[\s\S]*?<\/script>/g,'').replace(/<div id="hdrV2"[\s\S]*?<\/div>\n  <header/,'<header');let h=0;for(let i=0;i<s.length;i++){h=(h*31+s.charCodeAt(i))|0;}return{hash:h>>>0,len:s.length,hdr:(document.querySelector('header')||{}).outerHTML?.length};})()
