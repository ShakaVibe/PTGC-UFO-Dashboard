/* Top 100 window mock — renders every option from mock-data.js (real PulseScan holders + the staking contract's mapUserInfo,
   read 2026-10-22). Nothing here ships; the build will be JSX in index.html. */
(function(){
const D=window.T100;
const fmt=n=>{const a=Math.abs(n);if(a>=1e12-1e4)return(n/1e12).toFixed(2)+'T';if(a>=1e9)return(n/1e9).toFixed(2)+'B';if(a>=1e6)return(n/1e6).toFixed(2)+'M';if(a>=1e3)return(n/1e3).toFixed(2)+'K';return n.toFixed(2)};
const usd=n=>'$'+(n>=100?Math.round(n).toLocaleString('en-US'):n.toFixed(2));
const short=a=>a.slice(0,6)+'…'+a.slice(-4);
const TIERS=[['Poseidon','trident',.10],['Whale','whale',.01],['Shark','shark',.001],['Dolphin','dolphin',.0001],['Squid','squid',.00001],['Turtle','turtle',.000001],['Shrimp','shrimp',.0000001],['Shell','shell',0]];
const league=(b,sup)=>{const i=TIERS.findIndex(t=>b>=sup*t[2]);return{name:TIERS[i][0],ic:`../../logos/panels/sea-${TIERS[i][1]}.webp`}};
const ICO={
 trophy:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 21h8M12 17v4M7 4h10v5a5 5 0 0 1-10 0z"/><path d="M17 5h3v2a4 4 0 0 1-4 4M7 5H4v2a4 4 0 0 0 4 4"/></svg>',
 ticket:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 8a2 2 0 0 0 0 4v0a2 2 0 0 0 0 4v2h18v-2a2 2 0 0 1 0-4 2 2 0 0 1 0-4V6H3z"/><path d="M13 6v12" stroke-dasharray="2 2"/></svg>',
 pie:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v9h9a9 9 0 1 1-9-9z"/><path d="M15 3.5A9 9 0 0 1 20.5 9H15z" fill="currentColor"/></svg>',
 crown:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"><path d="M3 7l4.5 4L12 4l4.5 7L21 7l-2 11H5z"/></svg>',
 users:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="9" cy="8" r="3.5"/><path d="M2.5 20a6.5 6.5 0 0 1 13 0M16 4.5a3.5 3.5 0 0 1 0 7M18 14a6 6 0 0 1 3.5 6"/></svg>',
 lock:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V8a4 4 0 0 1 8 0v3"/></svg>',
 search:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg>',
 bolt:'<svg viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L4 14h7l-1 8 9-12h-7z"/></svg>',
 copy:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 0 0-1-1H5a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h3"/></svg>',
 ext:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M14 4h6v6M20 4l-9 9M18 14v5a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V7a1 1 0 0 1 1-1h5"/></svg>',
};
const tile=(l,ic,v,f,cls='')=>`<div class="tile ${cls}"><div class="l">${ic?ICO[ic]:''}${l}</div><div class="v">${v}</div>${f?`<div class="f">${f}</div>`:''}</div>`;

function win(c){
  const tok=c.tok,stk=c.mode==='s',P=D.price[tok],SUP=D.supply[tok];
  const list=stk?D.stakers.map(x=>({a:x.a,v:x.s,l:x.l,b:x.b})):D.holders[tok].map(x=>({a:x.a,v:x.b}));
  const tot=stk?D.stakedTotal:SUP;
  const T=list[99].v,top1=list[0].v,sum100=list.slice(0,100).reduce((s,x)=>s+x.v,0);
  const coin=`<div class="coin"><div class="halo"></div><img class="corona" src="../../logos/header/coin-corona${tok==='UFO'?'-green':''}.webp" alt=""><img class="lg" src="../../logos/${tok.toLowerCase()}/logo-512.webp" alt=""></div>`;
  const sw=tok==='PTGC'?`<div class="sw"><b class="${stk?'':'on'}">TOP HOLDERS</b><b class="${stk?'on':''}">TOP STAKERS</b></div>`:'';
  const hd=`<div class="hd"><div class="sky"></div>${c.look==='A'?`<img class="whale" src="../../logos/leagues/lg-whale.webp" alt=""><img class="shark" src="../../logos/leagues/lg-shark.webp" alt="">`:''}<div class="fade"></div>${sw}${coin}
    <div class="ttl"><div class="k">${tok} <em>TOP 100</em></div><div class="s">${stk?'The 100 biggest PTGC stakers — staked + locked, read from the staking contract':`The 100 biggest ${tok} wallets — people only`}</div></div></div><div class="x">✕</div>`;
  const tiles=`<div class="st4">${
    tile(stk?'#100 has staked':'#100 holds','ticket',`${fmt(T)}<small>${tok}</small>`,`≈ <span class="usd">${usd(T*P)}</span> — the line to beat`,'lead')+
    tile(stk?'Top 100 stake':'Top 100 hold','pie',`${(sum100/tot*100).toFixed(1)}%`,stk?`of all ${fmt(D.stakedTotal)} staked PTGC`:`of the ${fmt(SUP)} starting supply`)+
    tile(stk?'#1 has staked':'#1 holds','crown',`${fmt(top1)}<small>${tok}</small>`,`≈ <span class="usd">${usd(top1*P)}</span>`)+
    tile(stk?'Stakers':'Holders','users',(stk?D.stakerCount:D.holderCount[tok]).toLocaleString('en-US'),stk?'wallets with PTGC staked now':'wallets holding any '+tok)}</div>`;

  // check-a-wallet
  let chk='',me=null;
  const ck=c.chk||{kind:'empty'};
  if(ck.kind!=='empty'){me={...list[ck.idx],rank:ck.idx+1};}
  const head=`<div class="hh"><span>${ICO.search}${stk?'CHECK A WALLET — HOW MUCH TO STAKE':'CHECK A WALLET'}</span><span class="r">rank, tokens to break in, cost today</span></div>`;
  const bar=`<div class="bar1"><div class="inp">${ICO.search}<span class="tx ${me?'':'ph'}">${me?me.a:'Paste any wallet address (0x…)'}</span></div><div class="go">CHECK</div></div>`;
  let res='';
  if(ck.kind==='empty'){
    res=`<div class="mine">Your wallets from Portfolio: <i>Main</i><i>Cold storage</i><i>Wallet 3</i> — tap one to check it</div>`;
  }else if(ck.kind==='out'&&!stk){
    const need=T-me.v+1,lg=league(me.v,SUP);
    res=`<div class="res">${tile('Holds',null,`${fmt(me.v)}<small>${tok}</small>`,`≈ <span class="usd">${usd(me.v*P)}</span>`)+
      tile('Rank',null,`#${me.rank}`,`<span class="lgc"><img src="${lg.ic}" alt="">${lg.name}</span>`)+
      tile('To break in','bolt',`+${fmt(need)}<small>${tok}</small>`,`to pass #100 (${fmt(T)})`,'hot')+
      tile('Cost today <span class="ii">i</span>',null,`<span class="usd">${usd(need*P)}</span>`,`at $${P} per ${tok}`)}</div>
      <div class="prog"><span>${(me.v/T*100).toFixed(1)}% of the way</span><div class="tr"><i style="width:${Math.min(100,me.v/T*100)}%"></i></div><b>#100</b></div>`;
  }else if(ck.kind==='in'&&!stk){
    const up=list[me.rank-2],cush=me.v-list[100].v,lg=league(me.v,SUP);
    res=`<div class="res">${tile('Holds',null,`${fmt(me.v)}<small>${tok}</small>`,`≈ <span class="usd">${usd(me.v*P)}</span>`)+
      tile("You're in",'trophy',`#${me.rank}`,`<span class="lgc"><img src="${lg.ic}" alt="">${lg.name}</span> · in the top 100`,'in')+
      tile(`To pass #${me.rank-1}`,'bolt',`+${fmt(up.v-me.v+1)}<small>${tok}</small>`,`≈ <span class="usd">${usd((up.v-me.v+1)*P)}</span> today`,'hot')+
      tile('Your cushion',null,`${fmt(cush)}<small>${tok}</small>`,`above #101 — sell more and you drop out`)}</div>`;
  }else if(stk){
    const need=T-me.v+1,free=Math.max(0,(me.b||0)-me.v),buy=Math.max(0,need-free);
    res=`<div class="res">${tile('Staked',null,`${fmt(me.v)}<small>PTGC</small>`,me.l>0?`${fmt(me.l)} of it locked`:`none of it locked`)+
      tile('Staker rank',null,`#${me.rank}`,`of ${D.stakerCount.toLocaleString('en-US')} stakers`)+
      tile('Stake more','bolt',`+${fmt(need)}<small>PTGC</small>`,`to pass #100 (${fmt(T)} staked)`,'hot')+
      tile('Cost today <span class="ii">i</span>',null,`<span class="usd">${buy>0?usd(buy*P):'$0'}</span>`,free>0?(buy>0?`stake your ${fmt(free)} unstaked + buy ${fmt(buy)}`:`stake ${fmt(need)} of your ${fmt(free)} unstaked`):`buy ${fmt(need)} and stake it`)}</div>
      <div class="prog"><span>${(me.v/T*100).toFixed(1)}% of the way</span><div class="tr"><i style="width:${Math.min(100,me.v/T*100)}%"></i></div><b>#100</b></div>`;
  }
  chk=`<div class="chk">${head}${bar}${res}</div>`;

  // podium
  const pc=(i,cls)=>{const x=list[i],lg=league(stk?(x.b||x.v):x.v,SUP);return`<div class="pc ${cls}"><img class="cr" src="${lg.ic}" alt=""><div class="md">${i+1}</div><div class="ad">${short(x.a)}</div><div class="bl">${fmt(x.v)}<small>${tok}</small></div><div class="uv">${usd(x.v*P)}</div><div class="sh">${(x.v/tot*100).toFixed(2)}% ${stk?'of staked':'of supply'}</div></div>`};
  const pod=`<div class="pod">${pc(1,'s')}${pc(0,'g')}${pc(2,'b')}</div>`;

  // list
  const mx=Math.sqrt(list[3].v);
  const row=(x,rank,cls='')=>{
    const isMe=me&&me.rank===rank;
    const ad=`<div class="ad">${short(x.a)}${ICO.copy}${ICO.ext}${isMe?'<span class="tag you">CHECKED</span>':''}</div>`;
    const w=Math.max(2,Math.sqrt(x.v)/mx*100);
    if(stk) return `<div class="r ${cls} ${isMe?'me':''}"><div class="rk">${rank}</div>${ad}<div class="bal"><div class="bb"><i style="width:${w}%"></i><i class="lk" style="width:${w*(x.l/x.v)}%"></i></div><div class="n">${fmt(x.v)}<span class="u2">${usd(x.v*P)}</span></div></div><div class="lk2 hp">${x.l>0?fmt(x.l):'—'}</div><div class="pc2 hp">${(x.v/tot*100).toFixed(2)}%</div><div class="uv hp">${usd(x.v*P)}</div></div>`;
    const lg=league(x.v,SUP);
    return `<div class="r ${cls} ${isMe?'me':''}"><div class="rk">${rank}</div>${ad}<img class="sea" src="${lg.ic}" alt="${lg.name}" title="${lg.name}"><div class="bal"><div class="bb"><i style="width:${w}%"></i></div><div class="n">${fmt(x.v)}<span class="u2">${usd(x.v*P)}</span></div></div><div class="pc2 hp">${(x.v/SUP*100).toFixed(2)}%</div><div class="uv hp">${usd(x.v*P)}</div></div>`;
  };
  const th=stk?`<div class="th"><b>#</b><b>Wallet</b><b>Staked <span class="hp" style="color:#F9A8D4">▨ locked</span></b><b class="hp">Locked</b><b class="hp">Share</b><b class="hp">Value</b></div>`
             :`<div class="th"><b>#</b><b>Wallet</b><b></b><b>Balance</b><b class="hp">Supply</b><b class="hp">Value</b></div>`;
  const n=c.rows||8;let rows='';
  for(let i=3;i<3+n;i++)rows+=row(list[i],i+1);
  rows+=`<div class="gap">· · ·  #${4+n} – #97  · · ·</div>`;
  for(let i=97;i<100;i++)rows+=row(list[i],i+1,i===99?'cut':'');
  rows+=`<div class="line">THE TOP 100 LINE</div>`;
  if(me&&me.rank>100){rows+=row(list[me.rank-2],me.rank-1)+row(me,me.rank);}
  else rows+=row(list[100],101);
  const lst=`<div class="lst ${stk?'stk':''}">${th}${rows}</div>`;

  const ft=`<div class="ft">${stk?'Read from the PTGC staking contract (every wallet that ever staked, its <b>mapUserInfo</b> amount now) · refreshed every 2 h':'From PulseScan’s holder list, refreshed every 2 h · left out: liquidity pools, every contract, the burn addresses, the DAO wallets'+(tok==='UFO'?', the UFO OA wallet':'')} · read ${D.readAt}</div>`;
  const tip=c.tip?`<div class="tipc" style="right:30px;top:${c.tipTop||520}px"><b>Cost is a snapshot.</b> It's the tokens you'd need at today's price. A real buy moves the price as it fills — slippage and the price rising while you buy aren't included, so expect the real cost to be higher.</div>`:'';
  return `<div class="t1 ${c.look} ${tok==='UFO'?'ufo':''} ${c.phone?'ph':''}">${hd}${tiles}${chk}${pod}${lst}${ft}<div class="cl">Close</div>${tip}</div>`;
}

/* ---------- the button in the Token Allocation header ---------- */
const btn=(kind,tok)=>{
  if(kind==='twin')return `<span class="pbtn">Leagues</span><span class="pbtn">Top 100</span>`;
  const g=tok==='UFO'?'green':'gold';
  return `<span class="pbtn">Leagues</span><span class="pbtn ${g}">${ICO.trophy}Top <span class="n">100</span></span>`;
};
const strip=(kind,tok,ph)=>`<div class="ta ${ph?'ph':''}"><div class="h"><div class="t"><img src="../../logos/panels/alloc-pie.webp" alt="">TOKEN ALLOCATION<img class="lg" src="../../logos/${tok.toLowerCase()}/logo-512.webp" alt=""></div><div class="bs">${btn(kind,tok)}</div></div>${ph?'':`<div class="body"><div class="ring"></div><div class="lines">Burned · In LP · Staked · Lock &amp; Stk · Held</div></div>`}</div>`;

const P=[];
const sec=(tag,note,html,g)=>P.push(`<span class="opt ${g?'g':''}">${tag}</span><span class="note">${note}</span>${html}<div class="sep"></div>`);
const h=D.holders.PTGC,ix=118-1;
sec('THE BUTTON','Where it lives: the Token Allocation panel, right of <b>LEAGUES</b>, on both PTGC and UFO. <b>B1</b> a twin of the Leagues button (same purple). <b>B2</b> gold with a trophy so it reads as the new thing — green on UFO. Both wrap under the title on a phone, the same as Leagues does today.',
 `<div class="row2">${strip('twin','PTGC')}<div style="font:700 13px Orbitron;color:#F2D35B;align-self:center">B1</div></div><div style="height:14px"></div><div class="row2">${strip('gold','PTGC')}<div style="font:700 13px Orbitron;color:#F2D35B;align-self:center">B2</div></div><div style="height:14px"></div><div class="row2">${strip('gold','UFO')}${strip('gold','PTGC',1)}</div>`);
sec('LOOK A — THE DEEP','<b>The Leagues window’s family</b>: his underwater ruins as the header, the whale + shark cut-outs, the lit coin, "PTGC TOP 100". Four tiles: <b>the line to beat</b> (what #100 holds) · how much of the supply the top 100 hold · what #1 holds · how many holders. Then <b>CHECK A WALLET</b>, the podium (#2 · #1 · #3 with medals) and the list #4 → #100 (scrolls in the real window; the mock cuts the middle). The wallet checked here is the real #118.',
 win({look:'A',tok:'PTGC',mode:'h',chk:{kind:'out',idx:ix},rows:8}));
sec('LOOK B — HALL OF FAME','<b>The rank window’s family</b>: the gold mountain plate, and #1 sits in <b>his laurel art</b> (rk-hero) like the TODAY tile. Same content as A, so you’re only picking the look.',
 win({look:'B',tok:'PTGC',mode:'h',chk:{kind:'out',idx:ix},rows:8}));
sec('PTGC — TOP STAKERS','The toggle at the top of the header flips the whole window to <b>stakers</b> (PTGC only). Ranked by what each wallet has in the staking contract right now, locked included — the pink stripes in each bar are the locked part. The checker answers <b>how much more to stake</b>, and if the wallet already holds unstaked PTGC it says so: "stake what you hold + buy the rest". The ⓘ disclaimer is shown open here. Real numbers: 3,428 wallets stake today, #100 has 271.94M staked.',
 win({look:'A',tok:'PTGC',mode:'s',chk:{kind:'out',idx:126},rows:6,tip:true,tipTop:542}));
sec('ALREADY IN THE TOP 100','When the checked wallet is in: a green <b>YOU’RE IN</b> tile with its rank, what it takes to pass the one above, and its <b>cushion</b> — how much it can sell before it drops out. Its row lights up in the list. (Real #9 shown.) Empty state below it: before anything is typed, the bar offers the wallets he saved on the Portfolio page.',
 win({look:'A',tok:'PTGC',mode:'h',chk:{kind:'in',idx:8},rows:8})+`<div style="height:22px"></div>`+`<div style="max-width:980px">`+win({look:'A',tok:'PTGC',mode:'h',chk:{kind:'empty'},rows:0}).replace(/<div class="pod">[\s\S]*$/,'</div>')+`</div>`);
sec('UFO','UFO in green, no stakers toggle (UFO has no staking). Real data: #100 holds 1.06B UFO.',
 win({look:'A',tok:'UFO',mode:'h',chk:{kind:'out',idx:111},rows:8}),1);
sec('PHONE (390 px)','The same window on a phone, A and B: tiles two across, the checker\'s answer two across, the podium stays three across, and each list row shows rank · wallet · league · balance with its $ under it.',
 `<div class="row2">${win({look:'A',tok:'PTGC',mode:'h',chk:{kind:'out',idx:ix},rows:6,phone:1})}${win({look:'B',tok:'PTGC',mode:'s',chk:{kind:'out',idx:126},rows:6,phone:1})}</div>`);
document.getElementById('page').innerHTML=P.join('');
})();
