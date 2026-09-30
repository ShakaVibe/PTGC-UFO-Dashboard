/* LP Pairs v2 (2026-10-01): the LP Pairs section's markup — run on the classic render of two builds and diff:
   with the preview switch off the section must be byte-identical to the build before the v2 table. */
(()=>{const d=[...document.querySelectorAll('div.max-w-7xl')].find(x=>/LP Pairs/.test(x.textContent));return d?d.outerHTML.replace(/Updated [^<]*/g,''):'no LP section';})()
