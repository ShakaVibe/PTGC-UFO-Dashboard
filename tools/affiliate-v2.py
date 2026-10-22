#!/usr/bin/env python3
"""AFFILIATE PROGRAM v2 (2026-10-22) — the page's new look, Shaka's pick from design/affiliate/mock-affiliate-v3.html (3a):
the Top 100 window's gold plate as a hero band + the dashboard header's corona coin, the terms as chips, Leaderboard / Payment
Receipts as the Calculators icon buttons, ALL-TIME / month as framed bands of tiles (sea art, not emoji), the month's podium on his
beam-UFO medals, Recent Activity / Registry / Commission Log as framed cards, his Calculators space art under the whole page.
Idempotent, run from the repo root:   python3 tools/affiliate-v2.py      (run it twice: the second run must print "0 edit(s)")
  - the CSS  (tools/affiliate/af.css) between /* AFFIL2:CSS:BEGIN */ … END, just before the TOP 100 CSS
  - the JSX  (AfSea, AfPodium) between /* AFFIL2:JSX:BEGIN */ … END, just before AffiliatesPage
  - AffiliatesPage's render: the wrapper + art plate, the header → hero, the two stat bars → bands, Recent Activity, the Registry
    and Commission Log headers, the log's rank / buys pill / sea art / status badges, the footer. The lists' own cells are kept.
Edit tools/affiliate/af.css, never the spliced copy in index.html — the next run overwrites it.
"""
import hashlib
P = 'index.html'
s = open(P, encoding='utf-8').read()
n = 0

def splice(tag, body, anchor):
    global s, n
    b, e = f'/* AFFIL2:{tag}:BEGIN */', f'/* AFFIL2:{tag}:END */'
    block = f'    {b}\n{body.rstrip()}\n    {e}\n'
    if b in s:
        i, j = s.index('    ' + b), s.index(e) + len(e) + 1
        if s[i:j] != block: s = s[:i] + block + s[j:]; n += 1
    else:
        assert s.count(anchor) == 1, f'anchor x{s.count(anchor)}: {anchor[:60]!r}'
        s = s.replace(anchor, block + anchor); n += 1

def edit(old, new):
    global s, n
    if new in s: return
    assert s.count(old) == 1, f'anchor x{s.count(old)}: {old[:70]!r}'
    s = s.replace(old, new); n += 1

def between(start, end, new, tag):
    """replace everything from `start` up to (not including) `end` with `new`, wrapped in {/* AFFIL2:tag */} … {/* /AFFIL2:tag */}
    markers; a later run finds the markers and swaps the block for the current `new` (so the fragments here can be edited and re-run)"""
    global s, n
    b, e = f'{{/* {tag} */}}', f'{{/* /{tag} */}}'
    block = f'          {b}\n{new.rstrip()}\n          {e}\n'
    if b in s:
        i, j = s.index('          ' + b), s.index(e) + len(e) + 1
        if s[i:j] != block: s = s[:i] + block + s[j:]; n += 1
        return
    assert s.count(start) == 1, f'start x{s.count(start)}: {start[:60]!r}'
    i = s.index(start); j = s.index(end, i)
    s = s[:i] + block + s[j:]; n += 1

JSX = r"""    /* AFFILIATE PROGRAM v2 (2026-10-22) — two small pieces the page's new look needs (tools/affiliate-v2.py). */
    const AfSea=({ptgc})=>{const pct=((ptgc||0)/PTGC_SUPPLY_GLOBAL)*100;const cs=getBurnC(pct).slice(0,3);   // the stats bars' "x2 🐋" as the sea art
      return <div className="sea">{cs.length?cs.map((c,i)=><span key={i} title={c.n}><SeaIcon e={c.e} size={23}/>×{c.cnt}</span>):<span className="text-gray-600">—</span>}</div>;};
    const AfPodium=({entries,month,onPick})=>{   // the month's top three referrers by PTGC bought on his 1st / 2nd / 3rd medals (the Top 100 podium cards)
      const top=[...entries].filter(e=>(e.ptgcAmount||0)>0).sort((a,b)=>(b.ptgcAmount||0)-(a.ptgcAmount||0)).slice(0,3);
      if(!top.length)return null;
      const cls=['g1','g2','g3'],md=['t1-1st','t1-2nd','t1-3rd'],lab=['1st','2nd','3rd'];
      return(
        <div className="af-card">
          <div className="af-chd"><div className="ic"><img src="logos/top100/t1-1st.webp?v=2" alt=""/></div><div className="tt"><div className="t">{month} podium<em>MOST PTGC BOUGHT</em></div><div className="sub">the month's top three referrers · the full leaderboard is behind the button</div></div></div>
          <div className="af-pod">
            {[1,0,2].map(i=>{const e=top[i];
              if(!e)return <div key={i} className={`af-pc ${cls[i]} none`} aria-hidden="true"><img className="md" src={`logos/top100/${md[i]}.webp?v=2`} alt=""/><div className="pad"><div className="nm">—</div><div className="am">&nbsp;</div></div></div>;
              const c=getCreatureForPtgc(e.ptgcAmount);
              return(
                <div key={i} className={`af-pc ${cls[i]}`} role="button" tabIndex={0} title={e.username} onClick={()=>onPick(e.username)} onKeyDown={ev=>{if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();onPick(e.username);}}}>
                  <img className="md" src={`logos/top100/${md[i]}.webp?v=2`} alt={lab[i]}/>
                  <div className="pad"><div className="nm">{e.username}</div><div className="am">{fmtAbbr(e.ptgcAmount)} <small>PTGC</small></div>
                    <div className="f"><b>{fmtDollar(e.usdAmount||0)}</b><span>· {e.buysCount||0} {e.buysCount===1?'buy':'buys'}</span>{c&&<SeaIcon e={c.emoji} size={20}/>}</div></div>
                </div>);})}
          </div>
        </div>);};
"""

splice('CSS', open('tools/affiliate/af.css', encoding='utf-8').read(), '    /* T100:CSS:BEGIN */')
splice('JSX', JSX, '    const AffiliatesPage=({onBack})=>{')

# 1 — the wrapper + the art plate
edit("""        <div className="min-h-screen bg-gradient-to-b from-gray-900 via-[#0a0a0a] to-gray-900">
          {/* Referrer Detail Modal */}""",
     """        <div className="af min-h-screen">
          <div className="af-art" aria-hidden="true"></div>
          {/* Referrer Detail Modal */}""")

# 2 — the header → the hero band + the terms chips + the icon buttons (+ the open of the content column)
between("""          {/* Header */}
          <header className="border-b border-[#D4AF37]/20 bg-[#0a0a0a]/90 backdrop-blur sm:sticky sm:top-0 z-50">""",
        """            {/* ALL-TIME Stats Bar - Gold */}""",
        """          {/* the Top 100 window's plate, the dashboard header's corona coin, the program terms as chips, the two icon buttons (tools/affiliate-v2.py) */}
          <header className="af-hero">
            <div className="af-sky" aria-hidden="true"></div><div className="af-fade" aria-hidden="true"></div>
            <div className="af-hin">
              <div className="af-top">
                <button type="button" onClick={onBack} className="af-back"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" aria-hidden="true"><path d="M15 19l-7-7 7-7"/></svg>Back to PTGC</button>
                <span className="af-stamp"><AffiliateFreshness data={data} loading={loading}/></span>
              </div>
              <div className="af-coin" aria-hidden="true"><div className="halo"></div><img className="corona" src="logos/header/coin-corona.webp" alt=""/><div className="flare"></div><div className="flare-v"></div><div className="flare-h"></div><img className="logo" src="logos/ptgc/logo-512.webp" alt=""/></div>
              <div className="af-ttl"><h1>PTGC <em>AFFILIATE</em> PROGRAM</h1><p>Earn PTGC on every buy you refer · {currentMonthSettings.commissionRate}% commission, paid monthly in PTGC</p></div>
            </div>
          </header>
          <div className="af-gap" aria-hidden="true"></div>
          <div className="af-in">
            <div className="af-terms">
              <span className="af-chip mo"><span className="k">Month</span><span className="v">{formatMonthYear(currentMonth)}</span></span>
              <span className="af-chip"><span className="k">Rate</span><span className="v">{currentMonthSettings.commissionRate}%</span></span>
              <span className="af-chip ok"><span className="k">Min threshold</span><span className="v">{currentMonthSettings.thresholdType==='usd'?'$':''}{currentMonthSettings.threshold}{currentMonthSettings.thresholdType!=='usd'?' PTGC':''}</span></span>
              <span className={`af-chip ${currentMonthSettings.coverFee!==false?'ok':'bad'}`}><span className="k">5% fee</span><span className="v">{currentMonthSettings.coverFee!==false?'Covered':'Not Covered'}</span></span>
            </div>
            <div className="af-acts">
              <button type="button" onClick={()=>setShowLeaderboard(true)} className="af-btn"><img src="logos/top100/t1-1st.webp?v=2" alt=""/><span className="lb">Leaderboard<small>all-time champions · this month's winners</small></span><span className="ch">›</span></button>
              <button type="button" onClick={()=>setShowPayments(true)} className="af-btn purple"><img src="logos/panels/pbu-money.webp" alt=""/><span className="lb">Payment Receipts<small>every commission paid, on chain</small></span><span className="ch">›</span></button>
            </div>

""", 'AFFIL2:HERO')

# 3 — the two stat bars → the bands of tiles, then the podium
between("""            {/* ALL-TIME Stats Bar - Gold */}""", """            {/* Recent Activity Box */}""",
        """            {/* ALL-TIME (gold) and the month (green) as framed bands of tiles; the month's select stays on its plate */}
            <div className="af-stats">
              <div className="bl"><img src="logos/panels/dao-coins.webp" alt=""/><div className="t">All-time<small>since the program began</small></div></div>
              <div className="af-tiles">
                <div className="af-tl"><div className="l">Referrers</div><div className="v">{stats?.totalReferrers||0}</div></div>
                <div className="af-tl"><div className="l">Total buys</div><div className="v">{fmt(stats?.allTimeBuys)}</div></div>
                <div className="af-tl lead"><div className="l">PTGC referred</div><div className="v cc">{fmtAbbr(stats?.allTimePtgc)}</div></div>
                <div className="af-tl"><div className="l">Sea creatures</div><AfSea ptgc={stats?.allTimePtgc}/></div>
                <div className="af-tl"><div className="l">USD value</div><div className="v usd">{fmtUSD(stats?.allTimeUsd)}</div></div>
                <div className="af-tl"><div className="l">Commissions</div><div className="v cc">{fmtAbbr(stats?.allTimeCommission)} <small>PTGC</small></div></div>
                <div className="af-tl"><div className="l">Paid out</div><div className="v cc">{fmtAbbr(stats?.totalPaid)} <small>PTGC</small></div></div>
              </div>
            </div>
            <div className="af-stats green">
              <div className="bl">
                <select aria-label="Month" value={viewingMonth||currentMonth} onChange={e=>setViewingMonth(e.target.value)}>
                  {allMonths.map(month=><option key={month} value={month} className="bg-gray-900">{formatMonthYear(month)}</option>)}
                </select>
                <img src="logos/panels/pbu-pie.webp" alt=""/>
                <div className="t">{new Date((viewingMonth||currentMonth)+'-01T12:00:00Z').toLocaleDateString('en-US',{month:'long',timeZone:'UTC'})} '{(viewingMonth||currentMonth).slice(2,4)}<span className="ch">▼</span><small>{(viewingMonth||currentMonth)===currentMonth?'this month · live':'a past month'}</small></div>
              </div>
              <div className="af-tiles">
                <div className="af-tl"><div className="l">Referrers</div><div className="v">{stats?.periodReferrers||0}</div></div>
                <div className="af-tl"><div className="l">Buys</div><div className="v">{fmt(stats?.periodBuys)}</div></div>
                <div className="af-tl lead"><div className="l">PTGC referred</div><div className="v cc">{fmtAbbr(stats?.periodPtgc)}</div></div>
                <div className="af-tl"><div className="l">Sea creatures</div><AfSea ptgc={stats?.periodPtgc}/></div>
                <div className="af-tl"><div className="l">USD value</div><div className="v usd">{fmtUSD(stats?.periodUsd)}</div></div>
                <div className="af-tl"><div className="l">Commissions</div><div className="v cc">{fmtAbbr(stats?.periodCommission)} <small>PTGC</small></div></div>
                <div className="af-tl"><div className="l">Paid out</div><div className="v cc">{fmtAbbr(stats?.periodPaid)} <small>PTGC</small></div></div>
              </div>
            </div>
            <AfPodium entries={data?.monthlyLogs?.[viewingMonth||currentMonth]?.entries||[]} month={new Date((viewingMonth||currentMonth)+'-01T12:00:00Z').toLocaleDateString('en-US',{month:'long',timeZone:'UTC'})} onPick={setSelectedReferrer}/>

""", 'AFFIL2:BANDS')

# 4 — Recent Activity → the purple card
between("""            {/* Recent Activity Box */}""", """            {/* Referrers Registry Box */}""",
        """            {/* Recent Activity as the purple card: date chip · name · amount · $ · tx */}
            {recentTransactions.length>0&&(
              <div className="af-card purple">
                <div className="af-chd"><div className="ic"><img src="logos/panels/vg-flame.webp" alt=""/></div><div className="tt"><div className="t">Recent Activity<em>{formatMonthYear(currentMonth).toUpperCase()}</em></div><div className="sub">the latest referred buys · newest first</div></div></div>
                <div className="af-act">
                  {(recentActivityExpanded?recentTransactions:recentTransactions.slice(0,3)).map((tx,i)=>(
                    <div key={i} className="af-ar">
                      <span className="d">{tx.date?new Date(tx.date).toLocaleDateString('en-US',{month:'short',day:'numeric',timeZone:'UTC'}).toUpperCase():'—'}</span>
                      <button type="button" className="n" onClick={()=>setSelectedReferrer(tx.username)} title={tx.username}>{tx.username}<small>referred a buy</small></button>
                      <span className="amt">{fmtAbbr(tx.ptgcAmount)} <small>PTGC</small></span>
                      <span className="usd">{fmtDollar(tx.usdAmount||0)}</span>
                      <span className="tx">{tx.txHash?<><a href={`https://scan.pulsechain.com/tx/${tx.txHash}`} target="_blank" rel="noopener noreferrer">{truncateWallet(tx.txHash)}</a><CopyBtn text={tx.txHash} className="text-purple-500/40 hover:text-purple-300"/></>:null}</span>
                    </div>
                  ))}
                </div>
                {recentTransactions.length>3&&(
                  <button type="button" className="af-more" onClick={()=>setRecentActivityExpanded(!recentActivityExpanded)} aria-expanded={recentActivityExpanded}>
                    <span>{recentActivityExpanded?'SHOW LESS ▲':'SHOW MORE ▼'}</span>
                  </button>
                )}
              </div>
            )}

""", 'AFFIL2:RECENT')

# 5 — the Registry header → the fold bar (icon tile · title · counts · search · sort · SHOW)
between("""            {/* Referrers Registry Box */}
            <div className="bg-black/30 border border-white/10 rounded-xl mb-6 overflow-hidden">""",
        """              {showRegistry&&(
                <div className="sm:hidden divide-y divide-white/5">""",
        """            {/* the Registry's fold bar; the lists under it are the page's own */}
            <div className="af-card">
              <div className="af-chd">
                <div className="ic"><img src="logos/socials/hub/ptgc-affiliates.png" alt=""/></div>
                <button type="button" className="tt" onClick={()=>setShowRegistry(!showRegistry)} aria-expanded={showRegistry}>
                  <div className="t">Referrers Registry<em>({sortedRegistry.filter(s=>!registrySearch||s.name.toLowerCase().includes(registrySearch.toLowerCase())).length})</em></div>
                  <div className="sub">{stats?.totalReferrers||0} referrers · {stats?.activeThisMonth||0} active this month<span className="af-dsk"> · tap a name for their card</span></div>
                </button>
                <div className="r">
                  <label className="af-srch"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-3.5-3.5"/></svg><input type="text" placeholder="Search referrer…" aria-label="Search referrer" value={registrySearch} onChange={e=>setRegistrySearch(e.target.value)}/></label>
                  {showRegistry&&<AffilSortSelect value={sortCol} dir={sortDir} labels={AFFIL_SORT_LABELS} onChange={toggleSort}/>}
                  <button type="button" className="af-show" onClick={()=>setShowRegistry(!showRegistry)} aria-expanded={showRegistry}>{showRegistry?'HIDE':'SHOW'}</button>
                </div>
              </div>

""", 'AFFIL2:REGISTRY')
edit("""<table className="w-full text-sm min-w-[880px]">""", """<table className="af-tbl w-full text-sm min-w-[880px]">""")
edit("""(()=>{const c=getCreatureForPtgc(s.ptgc);return c?<span title={c.name} className="inline-flex items-center gap-0.5"><span className="text-base">{c.emoji}</span>""",
     """(()=>{const c=getCreatureForPtgc(s.ptgc);return c?<span title={c.name} className="inline-flex items-center gap-0.5"><SeaIcon e={c.emoji} size={24}/>""")

# 6 — the Commission Log header + the table's dress
between("""            {/* Commission Log Section */}
            <div className="bg-black/30 border border-white/10 rounded-xl mb-6 overflow-hidden">""",
        """              {/* Commission Log — phone cards (under sm) */}""",
        """            {/* the Commission Log's header; the month select as a gold pill */}
            <div className="af-card">
              <div className="af-chd">
                <div className="ic"><img src="logos/panels/dao-coins.webp" alt=""/></div>
                <div className="tt"><div className="t">Commission Log</div><div className="sub">sorted by {(AFFIL_COMM_SORT_LABELS[commSortCol]||'PTGC bought').toLowerCase()}<span className="af-dsk"> · tap a column head to sort</span></div></div>
                <div className="r">
                  <select className="af-sel" aria-label="Commission log month" value={commLogMonth||currentMonth} onChange={e=>setCommLogMonth(e.target.value)}>
                    {allMonths.map(m=><option key={m} value={m}>{formatMonthYear(m)}{m===currentMonth?' · current':''}</option>)}
                  </select>
                  {commLogEntries.length>0&&<AffilSortSelect value={commSortCol} dir={commSortDir} labels={AFFIL_COMM_SORT_LABELS} onChange={toggleCommSort}/>}
                </div>
              </div>

""", 'AFFIL2:LOG')
edit("""<table className="w-full text-sm table-fixed min-w-[820px]">""", """<table className="af-tbl w-full text-sm table-fixed min-w-[820px]">""")
edit("""<span className="block truncate text-[#D4AF37] font-medium cursor-pointer hover:underline" onClick={()=>setSelectedReferrer(e.username)}>{e.username}</span></td>""",
     """<span className="block truncate text-[#D4AF37] font-medium cursor-pointer hover:underline" onClick={()=>setSelectedReferrer(e.username)}><span className="af-rk" aria-hidden="true"></span>{e.username}</span></td>""")   # the rank is a CSS counter (no text — the a54 probe reads the cell as the name)
edit("""<div className="flex items-center justify-center gap-1"><span className="text-gray-500 text-xs">{expanded?'▼':'▶'}</span><span className="text-blue-400 font-semibold">{e.buysCount||0}</span></div></td>""",
     """<span className="af-bp"><span className="tri">{expanded?'▼':'▶'}</span>{e.buysCount||0}</span></td>""")
edit("""(()=>{const c=getCreatureForPtgc(e.ptgcAmount);return c?<span title={c.name} className="inline-flex items-center gap-0.5"><span className="text-base">{c.emoji}</span>""",
     """(()=>{const c=getCreatureForPtgc(e.ptgcAmount);return c?<span title={c.name} className="inline-flex items-center gap-0.5"><SeaIcon e={c.emoji} size={24}/>""")
STATUS_OLD = """className={`px-2 py-1 rounded text-xs font-bold ${st==='paid'?'bg-green-500/20 text-green-400':st==='partial'?'bg-orange-500/20 text-orange-400':st==='below'?'bg-red-500/20 text-red-400':'bg-yellow-500/20 text-yellow-400'}`}>{st==='below'?'BELOW MIN':st.toUpperCase()}</span>"""
STATUS_NEW = """className={`af-st ${st==='paid'?'pd':st==='partial'?'pa':st==='below'?'bm':'un'}`}>{st==='below'?'BELOW MIN':st.toUpperCase()}</span>"""
edit("""<span className={`shrink-0 px-2 py-1 rounded""" + STATUS_OLD[len('className={`px-2 py-1 rounded'):], """<span className={`shrink-0 af-st""" + STATUS_NEW[len('className={`af-st'):])
edit("""<span """ + STATUS_OLD, """<span """ + STATUS_NEW)
# the phone cards' creature (AffilCreature) = the sea art too
edit("""const AffilCreature=({ptgc})=>{const c=getCreatureForPtgc(ptgc);return c?<span title={c.name} className="inline-flex items-center gap-0.5"><span className="text-base">{c.emoji}</span>""",
     """const AffilCreature=({ptgc})=>{const c=getCreatureForPtgc(ptgc);return c?<span title={c.name} className="inline-flex items-center gap-0.5"><SeaIcon e={c.emoji} size={22}/>""")

# 7 — the footer
between("""          <footer className="text-center py-8 border-t border-white/10 mt-8">
            <a href="https://goptgc.com/#/ptgc-onboarding\"""",
        """          </footer>
        </div>
      );
    };
""",
        """          <footer className="af-foot">
            <a href="https://goptgc.com/#/ptgc-onboarding" target="_blank" rel="noopener noreferrer" className="af-btn purple"><img src="logos/socials/hub/ptgc-affiliates.png" alt=""/><span className="lb">Setup Your Own Referral Link</span><span className="ch">›</span></a>
            <p>PTGC Affiliate Program • Public Dashboard</p>
            <p className="i">Some metrics on this dashboard may be delayed up to 24 hours</p>
""", 'AFFIL2:FOOT')

if n: open(P, 'w', encoding='utf-8').write(s)
print(f'affiliate-v2: {n} edit(s), index.html sha256 {hashlib.sha256(s.encode()).hexdigest()[:8]}')
