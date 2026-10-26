#!/usr/bin/env python3
"""Affiliates → Leaderboard window v2 (2026-10-26). Shaka: "update the leader board page to be more in line with all the
cosmetic changes … make it exciting" → design/affiliates-leaderboard/mock-v1.html (lb-*.png) → "do it".

- The window is ONE board at a time: period switch ALL-TIME (gold) / <Month 'YY ▾> (green, the month picker sits inside the
  pill) and metric switch MOST PTGC BOUGHT / MOST REFERRALS. Header plate = the Affiliates hero's sky + the corona coin.
- Top three on his 1st / 2nd / 3rd beam-UFO medals (the page podium's look, bigger), ranks 4–10 as "the chase" rows with a bar
  against #4 and the sea-creature art × count (getCreatureForPtgc). A name opens that referrer, as before.
- Numbers: all-time = the sum of every monthly log per username (as before); the header's all-time totals are the page's
  own `stats` (the ALL-TIME band); a month = that month's entries. Top 10 (was 5 per board, four boards).
- LeaderboardCard + medal() (only used by the old window) are removed. CSS `.alb-*` after the podium rules.

Idempotent (done-markers); a second run prints "0 edit(s)". Run from the repo root.
"""
import sys, pathlib

P = pathlib.Path('index.html')
s = P.read_text()
edits = 0

def rep(old, new, marker, count=1):
    global s, edits
    if marker in s:
        return
    n = s.count(old)
    if n != count:
        sys.exit(f'anchor found {n}x (want {count}): {old[:100]!r}')
    s = s.replace(old, new)
    edits += 1

# ---- 1. the component (replaces medal + LeaderboardCard) ---------------------------------------------------------------
COMP = r"""    /* ===== Affiliates → Leaderboard window v2 (2026-10-26, design/affiliates-leaderboard/mock-v1.html) =====
       One board at a time: ALL-TIME / a month × MOST PTGC BOUGHT / MOST REFERRALS; podium on the medals + ranks 4–10. */
    const ALB_MEDALS=['t1-1st','t1-2nd','t1-3rd'];
    const AfLeaderboard=({data,stats,currentMonth,allMonths,formatMonthYear,month,setMonth,onPick,onClose})=>{
      const[per,setPer]=useState('all');
      const[met,setMet]=useState('ptgc');
      const lbMonth=month||currentMonth;
      const allRows=useMemo(()=>{
        const agg={};
        Object.values(data?.monthlyLogs||{}).forEach(l=>(l.entries||[]).forEach(e=>{
          const n=e.username;const a=agg[n]||(agg[n]={name:n,buys:0,ptgc:0,usd:0});
          a.buys+=e.buysCount||0;a.ptgc+=e.ptgcAmount||0;a.usd+=e.usdAmount||0;}));
        return Object.values(agg);
      },[data]);
      const moRows=useMemo(()=>(data?.monthlyLogs?.[lbMonth]?.entries||[]).map(e=>({name:e.username,buys:e.buysCount||0,ptgc:e.ptgcAmount||0,usd:e.usdAmount||0})),[data,lbMonth]);
      const mo=per==='mo',isP=met==='ptgc';
      const pool=mo?moRows:allRows;
      const val=r=>isP?r.ptgc:r.buys;
      const rows=[...pool].filter(r=>val(r)>0).sort((a,b)=>val(b)-val(a)||b.ptgc-a.ptgc).slice(0,10);
      const sum=k=>pool.reduce((t,r)=>t+r[k],0);
      const tot=mo?{refs:moRows.length,buys:sum('buys'),ptgc:sum('ptgc'),usd:sum('usd')}:{refs:stats?.totalReferrers,buys:stats?.allTimeBuys,ptgc:stats?.allTimePtgc,usd:stats?.allTimeUsd};
      const moShort=`${new Date(lbMonth+'-01T12:00:00Z').toLocaleDateString('en-US',{month:'long',timeZone:'UTC'})} '${lbMonth.slice(2,4)}`;
      const unit=r=>isP?'PTGC':(r.buys===1?'BUY':'BUYS');
      const big=r=>isP?fmtAbbr(r.ptgc):fmt(r.buys);
      const sub=r=>isP?`${fmt(r.buys)} ${r.buys===1?'buy':'buys'}`:`${fmtAbbr(r.ptgc)} PTGC`;
      const sea=(r,size)=>{const c=getCreatureForPtgc(r.ptgc);return c?<><SeaIcon e={c.emoji} size={size}/><span>{'×'}{c.count}</span></>:null;};
      const pick=n=>onPick(n);
      const key=n=>ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();pick(n);}};
      const pc=i=>{const r=rows[i];const g=['g1','g2','g3'][i];
        if(!r)return<div key={i} className={`alb-pc ${g} none`} aria-hidden="true"><img className="md" src={`logos/top100/${ALB_MEDALS[i]}.webp?v=2`} alt=""/><div className="pad"><div className="nm">{'—'}</div></div></div>;
        return(
          <div key={i} className={`alb-pc ${g}`} role="button" tabIndex={0} title={r.name} onClick={()=>pick(r.name)} onKeyDown={key(r.name)}>
            {i===0&&<span className="crown">Champion</span>}
            <img className="md" src={`logos/top100/${ALB_MEDALS[i]}.webp?v=2`} alt={['1st','2nd','3rd'][i]}/>
            <div className="pad">
              <div className="nm">{r.name}</div>
              <div className="big">{big(r)}<small>{unit(r)}</small></div>
              <div className="usd">{fmtUSD(r.usd)}</div>
              <div className="f"><span>{sub(r)}</span>{sea(r,28)}</div>
            </div>
          </div>);};
      const ref4=rows[3]?val(rows[3]):1;
      return(
        <div className={`alb${mo?' mo':''}`} onClick={e=>e.stopPropagation()}>
          <div className="alb-hd">
            <div className="sky" aria-hidden="true"></div><div className="fade" aria-hidden="true"></div>
            <button type="button" className="x" aria-label="Close" onClick={onClose}>{'✕'}</button>
            <div className="coin" aria-hidden="true"><div className="halo"></div><img className="corona" src="logos/header/coin-corona.webp" alt=""/><div className="fl"></div><div className="flv"></div><img className="lg" src="logos/ptgc/logo-512.webp" alt=""/></div>
            <div className="ttl"><h2>AFFILIATE <em>LEADERBOARD</em></h2>
              <p>{mo?`${formatMonthYear(lbMonth)}${lbMonth===currentMonth?' · live':''}`:'Since the program began'} {'·'} <b>{fmt(tot.refs)}</b> referrers {'·'} <b>{fmt(tot.buys)}</b> buys {'·'} <b>{fmtAbbr(tot.ptgc)}</b> PTGC {'·'} <b>{fmtUSD(tot.usd)}</b></p></div>
          </div>
          <div className="alb-ctl">
            <div className="alb-sw" role="group" aria-label="Period">
              <button type="button" aria-pressed={!mo} onClick={()=>setPer('all')}>All-time</button>
              <span className={`mo${mo?' on':''}`}>
                <span aria-hidden="true">{moShort} {'▾'}</span>
                <select aria-label="Month" value={lbMonth} onChange={e=>{setMonth(e.target.value);setPer('mo');}} onClick={()=>setPer('mo')} onFocus={()=>setPer('mo')}>
                  {allMonths.map(m=><option key={m} value={m} className="bg-gray-900">{formatMonthYear(m)}{m===currentMonth?' (current)':''}</option>)}
                </select>
              </span>
            </div>
            <div className="alb-sw" role="group" aria-label="Ranking">
              <button type="button" aria-pressed={isP} onClick={()=>setMet('ptgc')}>Most PTGC bought</button>
              <button type="button" aria-pressed={!isP} onClick={()=>setMet('buys')}>Most referrals</button>
            </div>
          </div>
          {rows.length?(
            <>
              <div className="alb-pod">{pc(1)}{pc(0)}{pc(2)}</div>
              {rows.length>3&&(
                <div className="alb-rows">
                  <div className="rh"><span>The chase {'·'} ranks 4–{rows.length}</span><span>bar = vs <b>#4</b></span></div>
                  {rows.slice(3).map((r,j)=>(
                    <div key={r.name} className="alb-r" role="button" tabIndex={0} onClick={()=>pick(r.name)} onKeyDown={key(r.name)}>
                      <div className="bar" aria-hidden="true" style={{width:`calc((100% - 72px) * ${Math.max(0.03,Math.min(1,val(r)/ref4)).toFixed(4)})`}}></div>
                      <div className="rk">{j+4}</div>
                      <div className="n">{r.name}<small>{sub(r)}</small></div>
                      <div className="v">{big(r)}<small>{unit(r)}</small><span className="uu">{fmtUSD(r.usd)}</span></div>
                      <div className="u">{fmtUSD(r.usd)}</div>
                      <div className="c">{sea(r,32)}</div>
                    </div>))}
                </div>)}
            </>
          ):<div className="alb-empty">No referred buys {mo?`in ${formatMonthYear(lbMonth)}`:'yet'}</div>}
          <div className="alb-ft"><span>Tap a name to open their referrals</span><span>{mo?formatMonthYear(lbMonth):'All-time'} {'·'} <b>{isP?'most PTGC bought':'most referrals'}</b></span></div>
        </div>
      );
    };
"""
a = s.find('    const medal=(i)=>')
b = s.find('    const LeaderboardCard=(')
if 'const AfLeaderboard=(' not in s:
    if a < 0 or b < 0 or b - a > 200:
        sys.exit('medal / LeaderboardCard anchors not found')
    e = s.find('\n    };\n', b)
    if e < 0:
        sys.exit('LeaderboardCard end not found')
    s = s[:a] + COMP + s[e + len('\n    };\n'):]
    edits += 1

# ---- 2. the window ----------------------------------------------------------------------------------------------------
a = s.find('          {/* Leaderboard Modal */}')
b = s.find('          {/* Payment Receipts Modal */}')
NEW_WIN = """          {/* Leaderboard Modal — v2 (AfLeaderboard, 2026-10-26) */}
          {showLeaderboard&&(
            <Modal className="z-[100] flex items-center justify-center p-4 bg-black/95 backdrop-blur-sm" onClose={()=>setShowLeaderboard(false)} label="Affiliate leaderboard">
              <AfLeaderboard data={data} stats={stats} currentMonth={currentMonth} allMonths={allMonths} formatMonthYear={formatMonthYear}
                month={leaderboardMonth} setMonth={setLeaderboardMonth}
                onPick={name=>{setShowLeaderboard(false);setSelectedReferrer(name);}} onClose={()=>setShowLeaderboard(false)}/>
            </Modal>
          )}

"""
if 'Leaderboard Modal — v2' not in s:
    if a < 0 or b < 0 or b < a:
        sys.exit('window anchors not found')
    s = s[:a] + NEW_WIN + s[b:]
    edits += 1

# ---- 3. CSS -----------------------------------------------------------------------------------------------------------
ANCH = "    .af-pc .f img.sea-ic{display:inline-block;width:20px;height:20px;object-fit:contain}\n"
CSS = ANCH + r"""    /* ===== the Leaderboard window v2 (alb, 2026-10-26) — gold = all-time, green = a month ===== */
    .alb{--a:#F2C94C;--rgb:242,201,76;--usd:#4ade80;position:relative;width:100%;max-width:1000px;max-height:92dvh;overflow-y:auto;border-radius:20px;border:1.5px solid rgba(var(--rgb),.55);background:#06070a;box-shadow:0 0 0 1px rgba(255,255,255,.04) inset,0 0 60px -14px rgba(var(--rgb),.55),0 30px 80px -20px #000;color:#fff;font-family:'Rajdhani',sans-serif}
    .alb.mo{--a:#7CFC00;--rgb:124,252,0}
    .alb-hd{position:relative;height:300px;overflow:hidden}
    .alb-hd .sky{position:absolute;inset:0;background:url(logos/portfolio/rk-plate-nf.webp) center 38%/cover no-repeat;transition:filter .4s}
    .alb.mo .alb-hd .sky{filter:hue-rotate(62deg) saturate(1.15)}
    .alb-hd .fade{position:absolute;inset:0;background:radial-gradient(ellipse 34% 46% at 50% 48%,rgba(0,0,0,.45),rgba(0,0,0,0)),linear-gradient(180deg,rgba(0,0,0,.25) 0,rgba(0,0,0,0) 30%,rgba(6,7,10,.25) 70%,#06070a 100%)}
    .alb-hd .x{position:absolute;right:16px;top:14px;z-index:3;width:36px;height:36px;border-radius:50%;border:1px solid rgba(255,255,255,.25);background:rgba(0,0,0,.55);color:#fff;display:flex;align-items:center;justify-content:center;font-size:17px;cursor:pointer}
    .alb-hd .x:hover{border-color:var(--a)}
    .alb-hd .coin{--u:.56px;position:absolute;left:50%;top:40px;transform:translateX(-50%);width:calc(195*var(--u));height:calc(195*var(--u))}
    .alb-hd .coin .halo{position:absolute;inset:calc(-70*var(--u));border-radius:50%;background:radial-gradient(circle,rgba(255,120,20,.22) 45%,rgba(255,120,20,.06) 60%,rgba(0,0,0,0) 72%)}
    .alb-hd .coin .corona{position:absolute;left:calc(-162*var(--u));top:calc(-162*var(--u));width:calc(520*var(--u));height:calc(520*var(--u));max-width:none;mix-blend-mode:screen;pointer-events:none}
    .alb-hd .coin .fl{position:absolute;left:calc(104*var(--u));top:calc(-8*var(--u));width:calc(30*var(--u));height:calc(9*var(--u));border-radius:50%;background:radial-gradient(closest-side,#fff,rgba(255,220,130,.7) 45%,rgba(255,180,60,0))}
    .alb-hd .coin .flv{position:absolute;left:calc(118*var(--u));top:calc(-18*var(--u));width:calc(2*var(--u));height:calc(30*var(--u));background:linear-gradient(180deg,rgba(255,240,200,0),#fff 50%,rgba(255,240,200,0))}
    .alb-hd .coin>img.lg{position:relative;width:100%;height:100%;max-width:none;border-radius:50%;filter:brightness(1.08) contrast(1.05);box-shadow:0 0 calc(10*var(--u)) calc(2*var(--u)) rgba(255,190,80,.55)}
    .alb-hd .ttl{position:absolute;left:0;right:0;top:172px;text-align:center;text-shadow:0 2px 8px #000,0 0 18px rgba(0,0,0,.9)}
    .alb-hd .ttl h2{margin:0;font:900 36px 'Orbitron',monospace;letter-spacing:.08em;line-height:1;color:#fff}
    .alb-hd .ttl h2 em{font-style:normal;color:var(--a);text-shadow:0 0 20px rgba(var(--rgb),.7),0 2px 8px #000}
    .alb-hd .ttl p{margin:10px 0 0;font-size:16px;font-weight:600;color:rgba(255,255,255,.82);padding:0 16px}
    .alb-hd .ttl p b{color:var(--a)}
    .alb-ctl{position:relative;z-index:2;display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin-top:-6px;padding:0 16px}
    .alb-sw{display:flex;padding:3px;border-radius:999px;background:rgba(0,0,0,.6);border:1px solid rgba(var(--rgb),.45);box-shadow:0 0 18px -6px rgba(var(--rgb),.6)}
    .alb-sw>button,.alb-sw>.mo{position:relative;border:0;background:none;cursor:pointer;font:700 11px 'Orbitron',monospace;letter-spacing:.14em;padding:10px 16px;border-radius:999px;color:rgba(255,255,255,.6);white-space:nowrap;text-transform:uppercase}
    .alb-sw>button:hover,.alb-sw>.mo:hover{color:#fff}
    .alb-sw>button[aria-pressed="true"],.alb-sw>.mo.on{color:#1a1200;background:linear-gradient(180deg,#FFE27A,#F2C94C 55%,#D9A520);box-shadow:0 0 14px rgba(242,201,76,.55)}
    .alb.mo .alb-sw>button[aria-pressed="true"],.alb.mo .alb-sw>.mo.on{color:#0b2200;background:linear-gradient(180deg,#F4FFE6,#A8FF4A 55%,#4CB800);box-shadow:0 0 14px rgba(124,252,0,.55)}
    .alb-sw>.mo select{position:absolute;inset:0;width:100%;height:100%;opacity:0;cursor:pointer;font-size:16px}
    .alb-sw>.mo:focus-within{outline:2px solid var(--a);outline-offset:2px}
    .alb-pod{display:grid;grid-template-columns:1fr 1.15fr 1fr;gap:14px;align-items:end;padding:22px 22px 6px}
    .alb-pc{position:relative;overflow:hidden;border-radius:16px;border:1.5px solid rgba(255,255,255,.14);background:#06070a;padding:16px 12px 14px;text-align:center;min-width:0;--m:235,120,50;cursor:pointer}
    .alb-pc::before{content:'';position:absolute;inset:0;background:url(logos/holders/nh-sky.webp) center/cover;filter:grayscale(1);opacity:.34}
    .alb-pc::after{content:'';position:absolute;inset:0;background:rgba(var(--m),.45);mix-blend-mode:color;pointer-events:none}
    .alb-pc>*{position:relative;z-index:1}
    .alb-pc.g1{--m:242,190,60;border-color:#F2C94C;box-shadow:0 0 36px -6px rgba(242,201,76,.75);padding-top:22px}
    .alb-pc.g2{--m:80,160,255;border-color:rgba(150,200,255,.6)}
    .alb-pc.g3{--m:235,120,50;border-color:rgba(235,140,70,.6)}
    .alb-pc.none{cursor:default;opacity:.5}
    .alb-pc:hover .nm,.alb-pc:focus-visible .nm{text-decoration:underline}
    .alb-pc .md{width:108px;height:108px;max-width:none;object-fit:contain;margin:0 auto;filter:drop-shadow(0 6px 10px rgba(0,0,0,.9))}
    .alb-pc.g1 .md{width:138px;height:138px}
    .alb-pc .pad{margin-top:8px;border-radius:12px;background:radial-gradient(ellipse at 50% 40%,rgba(3,4,7,.88),rgba(3,4,7,.4));padding:10px 8px}
    .alb-pc .nm{font-weight:700;font-size:19px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    .alb-pc.g1 .nm{font-size:22px}
    .alb-pc .big{font-weight:700;font-size:34px;line-height:1.05;color:var(--a);font-variant-numeric:tabular-nums;margin-top:2px;text-shadow:0 0 18px rgba(var(--rgb),.45)}
    .alb-pc.g1 .big{font-size:44px}
    .alb-pc .big small{font-size:13px;color:rgba(255,255,255,.55);margin-left:4px;text-shadow:none}
    .alb-pc .usd{font-weight:700;font-size:21px;color:var(--usd);font-variant-numeric:tabular-nums;margin-top:2px}
    .alb-pc.g1 .usd{font-size:25px}
    .alb-pc .f{display:flex;justify-content:center;align-items:center;gap:6px;margin-top:6px;font-size:14px;font-weight:600;color:rgba(255,255,255,.65);flex-wrap:wrap}
    .alb-pc .crown{position:absolute;left:50%;top:6px;transform:translateX(-50%);z-index:2;font:900 10px 'Orbitron',monospace;letter-spacing:.3em;text-transform:uppercase;color:#1a1200;background:linear-gradient(180deg,#FFE27A,#D9A520);padding:4px 12px;border-radius:999px;box-shadow:0 0 14px rgba(242,201,76,.7)}
    .alb-rows{padding:14px 22px 6px}
    .alb-rows .rh{display:flex;justify-content:space-between;align-items:baseline;font:700 11px 'Orbitron',monospace;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,.5);padding:0 4px 0}
    .alb-rows .rh b{color:var(--a)}
    .alb-r{position:relative;display:grid;grid-template-columns:44px minmax(0,1fr) 150px 120px 82px;align-items:center;gap:12px;height:62px;padding:0 14px 6px 10px;margin-top:8px;border-radius:12px;border:1px solid rgba(var(--rgb),.22);background:linear-gradient(90deg,rgba(var(--rgb),.07),rgba(6,7,10,.9) 55%);overflow:hidden;cursor:pointer}
    .alb-r:hover,.alb-r:focus-visible{border-color:rgba(var(--rgb),.6)}
    .alb-r:hover .n,.alb-r:focus-visible .n{text-decoration:underline}
    .alb-r::before{content:'';position:absolute;left:58px;right:14px;bottom:6px;height:3px;border-radius:2px;background:rgba(255,255,255,.07)}
    .alb-r .bar{position:absolute;left:58px;bottom:6px;height:3px;border-radius:2px;background:linear-gradient(90deg,rgba(var(--rgb),.35),var(--a));box-shadow:0 0 10px rgba(var(--rgb),.8)}
    .alb-r .rk{width:34px;height:34px;border-radius:50%;display:flex;align-items:center;justify-content:center;font:900 14px 'Orbitron',monospace;color:var(--a);border:1.5px solid rgba(var(--rgb),.55);background:rgba(0,0,0,.6)}
    .alb-r .n{font-weight:700;font-size:19px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}
    .alb-r .n small{display:block;font-size:12.5px;font-weight:600;color:rgba(255,255,255,.5);margin-top:1px}
    .alb-r .v{text-align:right;font-weight:700;font-size:23px;color:var(--a);font-variant-numeric:tabular-nums;white-space:nowrap}
    .alb-r .v small{font-size:11px;color:rgba(255,255,255,.5);margin-left:3px}
    .alb-r .v .uu{display:none}
    .alb-r .u{text-align:right;font-weight:700;font-size:18px;color:var(--usd);font-variant-numeric:tabular-nums}
    .alb-r .c{display:flex;align-items:center;justify-content:flex-end;gap:4px;font-weight:700;font-size:14px;color:rgba(255,255,255,.7)}
    .alb-empty{padding:40px 16px;text-align:center;color:rgba(255,255,255,.45);font-size:16px}
    .alb-ft{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:16px 22px 20px;font:700 11px 'Orbitron',monospace;letter-spacing:.2em;text-transform:uppercase;color:rgba(255,255,255,.45)}
    .alb-ft b{color:var(--a)}
    @media(max-width:640px){
      .alb{max-height:94dvh;border-radius:16px}
      .alb-hd{height:250px}.alb-hd .coin{--u:.44px;top:34px}.alb-hd .ttl{top:132px}.alb-hd .ttl h2{font-size:22px}.alb-hd .ttl p{font-size:13px;padding:0 12px}
      .alb-sw>button,.alb-sw>.mo{font-size:9.5px;padding:9px 11px;letter-spacing:.1em}
      .alb-pod{gap:6px;padding:16px 8px 4px}
      .alb-pc{padding:10px 5px 8px}.alb-pc.g1{padding-top:12px}.alb-pc .crown{display:none}
      .alb-pc .md{width:58px;height:58px}.alb-pc.g1 .md{width:72px;height:72px}
      .alb-pc .pad{padding:6px 4px}
      .alb-pc .nm{font-size:12.5px}.alb-pc.g1 .nm{font-size:13.5px}
      .alb-pc .big{font-size:18px}.alb-pc.g1 .big{font-size:22px}.alb-pc .big small{display:block;font-size:9px;margin:0}
      .alb-pc .usd{font-size:13px}.alb-pc.g1 .usd{font-size:15px}
      .alb-pc .f{font-size:10.5px;gap:3px}.alb-pc .f img.sea-ic{width:18px!important;height:18px!important}
      .alb-rows{padding:12px 8px 4px}.alb-rows .rh{gap:10px;font-size:9px;letter-spacing:.14em}
      .alb-r{grid-template-columns:30px minmax(0,1fr) auto 44px;gap:7px;height:56px;padding:0 8px 6px 6px}
      .alb-r::before,.alb-r .bar{left:40px;bottom:5px}
      .alb-r .rk{width:26px;height:26px;font-size:11px}
      .alb-r .n{font-size:15px}.alb-r .n small{font-size:11px}
      .alb-r .v{font-size:16px;line-height:1.05}.alb-r .v small{display:none}.alb-r .v .uu{display:block;font-size:12.5px;color:var(--usd)}
      .alb-r .u{display:none}
      .alb-r .c{font-size:11px;gap:1px}.alb-r .c img.sea-ic{width:24px!important;height:24px!important}
      .alb-ft{flex-direction:column;gap:8px;padding:14px 8px 18px;font-size:9.5px;text-align:center}
    }
"""
rep(ANCH, CSS, '/* ===== the Leaderboard window v2 (alb')

P.write_text(s)
print(f'{edits} edit(s)')
