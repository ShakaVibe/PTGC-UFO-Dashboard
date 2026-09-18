/* ledger.html: the summary tile counts and, per month in the picker, the table's row hashes +
   amounts — so a run with treasury-recent.json can be compared row-for-row against a run on the
   four full files (a36). Also lists which treasury files the page fetched. */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const months=[...document.querySelectorAll('button')].filter(b=>/^[A-Z][a-z]{2} \d\d$|^[A-Z][a-z]+ \d{4}$/.test(b.textContent.trim()));
  const out={fetched:performance.getEntriesByType('resource').map(e=>e.name).filter(n=>/treasury/.test(n)).map(n=>n.replace(/.*\/data\//,'').replace(/\?.*/,'')),months:{}};
  for(const b of months){
    b.click(); await sleep(300);
    const sum=(document.body.innerText.match(/(\w+ \d{4}) Summary[\s\S]{0,260}?TRANSFERS/)||[])[0];
    const txt=document.body.innerText.replace(/\s+/g,' ');
    const rows=txt.split(/(?=[A-Z][a-z]{2} \d{1,2}, \d{1,2}:\d\d [AP]M)/).slice(1).map(r=>r.slice(0,160));
    out.months[b.textContent.trim()]={summary:sum?sum.replace(/\s+/g,' '):null,n:rows.length,rows:[...new Set(rows)].slice(0,300)};
  }
  out.summary=(document.body.innerText.match(/\d[\d,]*\s+total transactions[^\n]*/i)||[])[0]||null;
  out.text=document.body.innerText.slice(0,300).replace(/\n+/g,' | ');
  return out;
})()
