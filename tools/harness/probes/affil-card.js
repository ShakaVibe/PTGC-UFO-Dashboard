/* a54 probe: open one referrer's modal and read the Current Month Progress card — the bar, the
   pending commission, the footer's threshold wording and rate, and the log's status badge.
   Set the name first: eval=window.__who='bob'. */
(async()=>{
  const sleep=ms=>new Promise(r=>setTimeout(r,ms));
  const who=window.__who||'bob';
  const cell=[...document.querySelectorAll('td,div,span')].find(e=>e.children.length===0&&e.innerText.trim()===who);
  if(!cell)return{error:'no element for '+who};
  let node=cell,opened=false;
  for(let i=0;i<4&&node;i++){
    node.click(); await sleep(700);
    if(/Current Month Progress/.test(document.body.innerText)){opened=true;break;}
    node=node.parentElement;
  }
  const t=document.body.innerText.replace(/\s+/g,' ');
  return {who,opened,
    card:(t.match(/Current Month Progress[\s\S]{0,320}/)||[''])[0],
    logStatus:(t.match(new RegExp(who+'[\\s\\S]{0,60}?(BELOW MIN|UNPAID|PARTIAL|PAID)'))||[])[1]||null};
})()
