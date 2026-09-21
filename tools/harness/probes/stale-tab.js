/* a52 probe: put the Value Generated panel on its 24H window, then report the volume it says it
   used next to the header's own VOLUME 24H tile, plus every "as of" label on the page.
   Volume: run with DS_VOL_DRIFT=1, then clock-shift.js, then tap Refresh — the two figures must
   still agree (they did not before a52: the panel kept its first-load volume for the life of the
   tab). Labels: age data/value-generated.json to ~95 min, load #/ufo, clock-shift 180 min and
   re-render — "as of 1.6h ago" must become "as of 4.6h ago", not stay put. */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const head=[...document.querySelectorAll('*')].find(e=>e.children.length===0&&/^VALUE GENERATED$/i.test(e.textContent.trim()));
  const panel=head&&head.closest('div.rounded-2xl,div.rounded-xl,section')||document.body;
  const btn=[...panel.querySelectorAll('button')].find(b=>b.textContent.trim()==='24H');
  if(btn){btn.click();await sleep(900);}
  const t=document.body.innerText.replace(/\s+/g,' ');
  const grab=re=>{const m=t.match(re);return m?m[1]:null;};
  return {
    selected24H:!!btn,
    headerVolume24h:grab(/VOLUME 24H \$?([\d,.KMB]+)/i),
    valueGenFromVol:grab(/from \$?([\d,.KMB]+) vol/i),
    asOfLabels:[...document.querySelectorAll('*')].filter(e=>e.children.length===0&&/^as of /i.test(e.textContent.trim())).map(e=>e.textContent.trim())
  };
})()
