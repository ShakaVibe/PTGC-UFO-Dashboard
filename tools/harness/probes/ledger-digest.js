/* a60 probe: a compact per-month digest of the Ledger — the summary tile counts and the set of
   transaction hashes in the table — so the same page can be compared across time zones and across
   builds. Since a60 the month buckets are cut at UTC midnight, so every viewer's digest is
   identical: run this under TZ=UTC, TZ=Australia/Sydney and TZ=America/Los_Angeles and diff. */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const months=[...document.querySelectorAll('button')].filter(b=>/^[A-Z][a-z]{2} \d\d$/.test(b.textContent.trim()));
  const out={tz:Intl.DateTimeFormat().resolvedOptions().timeZone,offsetMin:new Date().getTimezoneOffset(),months:{}};
  for(const b of months){
    b.click(); await sleep(350);
    const txt=document.body.innerText.replace(/\s+/g,' ');
    const hashes=[...document.querySelectorAll('a[href*="/tx/"]')].map(a=>a.href.split('/tx/')[1]).sort();
    out.months[b.textContent.trim()]={
      total:(txt.match(/(\S+) total transactions/)||[])[1]||null,
      rows:hashes.length,
      digest:hashes.map(h=>h.slice(2,8)).join(' ')
    };
  }
  return out;
})()
