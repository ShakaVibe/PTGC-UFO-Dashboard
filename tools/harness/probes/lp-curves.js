/* LP Pairs v2: how many rows' curves are rising / falling / unavailable / loading */
(()=>{const c={};document.querySelectorAll('.p2-lpsp svg').forEach(s=>{const k=(s.getAttribute('aria-label').match(/rising|falling|unavailable|loading/)||['?'])[0];c[k]=(c[k]||0)+1;});return JSON.stringify(c);})()
