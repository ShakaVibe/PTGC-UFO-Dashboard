/* a54 probe: the affiliates figures that used to disagree with each other — the ALL-TIME tiles
   and, per referrer, the commission-log row (commission + status badge). Run with AFFIL_DATA=1,
   whose fixture is three referrers against a $100 monthly minimum: alice clears it, bob does not
   (meetsThreshold:false, commissionPtgc:0), carol has her own 5% rate. */
(function(){
  const t=document.body.innerText.replace(/\s+/g,' ');
  const after=(label)=>{const m=t.match(new RegExp(label+' ([\\$0-9BKM.,]+(?: PTGC)?)'));return m?m[1]:null;};
  const rows={};
  document.querySelectorAll('tr').forEach(tr=>{
    const c=[...tr.querySelectorAll('td')].map(td=>td.innerText.trim());
    if(c.length>4&&/^(alice|bob|carol)$/.test(c[0]))rows[c[0]]=c;
  });
  return {
    headerThreshold:(t.match(/Min Threshold (\S+)/)||[])[1],
    allTimeCommissions:after('COMMISSIONS'),
    tiles:(t.match(/ALL-TIME[\s\S]{0,220}/)||[null])[0],
    logRows:rows
  };
})()
