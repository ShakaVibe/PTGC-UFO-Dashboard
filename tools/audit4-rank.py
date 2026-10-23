#!/usr/bin/env python3
r"""Audit IV — the holder-rank trio (e9, e10, e11), 2026-10-23. Idempotent, run from the repo root:
    python3 tools/audit4-rank.py      (run it twice: the second run must print "0 edit(s)")
It edits the two builders and the page FRAGMENTS, then re-splices the pages with tools/pf-v2.py and tools/top100.py.

e10 (the real cause, found 2026-10-23): PulseScan's holder paging REPEATS the last row of some pages as the first row of the next
    (its next_page_params carries the balance as a rounded float). Unique addresses = PulseScan's own holder count exactly, so the
    repeats are pure artefact — and build-holder-ranks.mjs kept them: ~126 phantom PTGC holders and ~44 UFO, spread evenly down the
    list, so every rank below ~#150 was too low (#8,000 shown as #8,065; the bottom ~+110), "people holding" was overstated, and
    the rank window's live point sat that far below its own history (built from the chain, no repeats). Now: dedupe by address,
    and the 98 % completeness check counts unique addresses. Also: the history index (build-rank-history.mjs) ranks ties the way
    the badge does — 1 + how many hold strictly more, compared on the same rounded key — instead of breaking ties by address.
e9  A wallet that sold since the 2-hourly list was read was ranked against its OWN old entry (one place low, "to pass #N" = itself).
    The builder now writes `t`: the first 6 hex characters of every listed address, aligned with `b` (6 chars per entry). The page
    finds the wallet's own entry by that tag and leaves it out before ranking — for every holder, not only the top 110 (the Top 100
    checker used `top`, so #111 and below kept the ghost). Without `t` (a file from before this change) the page ranks as before.
e11 The rank window's BEST EVER / LOWEST tiles are the wallet's whole life, not the selected period (the chart keeps the period).
"""
import hashlib, re, subprocess, sys

n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    if s.count(old) != count and count == 1:   # blank lines in the files carry their indent; the anchors here may not
        pat = '\n'.join('[ \t]*' if not ln.strip() else re.escape(ln) for ln in old.split('\n'))
        m = list(re.finditer(pat, s))
        if len(m) == 1: old = m[0].group(0)
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))
    n += 1

HR, RH = 'scripts/build-holder-ranks.mjs', 'scripts/build-rank-history.mjs'
LG, V2, RK, T1 = 'tools/pf-v2/PfLeagues.jsx', 'tools/pf-v2/PortfolioV2.jsx', 'tools/pf-v2/PfRank.jsx', 'tools/top100/t1.jsx'

# ================================================= e10 + e9 — build-holder-ranks.mjs ===========================================
edit(HR, """// Node 20+ (global fetch; run locally with NODE_USE_ENV_PROXY=1 behind a proxy). ESM.""",
"""// 2026-10-23 (Audit IV e10 + e9): PulseScan's paging repeats the last row of some pages as the first row of the next (the
// next_page_params balance is a rounded float) — ~126 PTGC / ~44 UFO repeats per read, unique addresses = PulseScan's own count.
// Rows are now de-duplicated by address (they were ranked as extra people, every rank below ~#150 too low). And `t` = the first
// 6 hex characters of every listed address, 6 chars per entry, aligned with `b`, so the page can leave a wallet's OWN (possibly
// stale) entry out before ranking it (tools/pf-v2/PfLeagues.jsx pfRank, tools/top100/t1.jsx).
//
// Node 20+ (global fetch; run locally with NODE_USE_ENV_PROXY=1 behind a proxy). ESM.""")
edit(HR, """  const kept = [], top = [];
  let leftKnown = 0, leftContracts = 0, leftDust = 0;""",
"""  const kept = [], top = [], seen = new Set();
  let leftKnown = 0, leftContracts = 0, leftDust = 0, repeats = 0;""")
edit(HR, """      const a = String(it.address && it.address.hash || '').toLowerCase();
      if (EXCLUDE.has(a)) { leftKnown++; continue; }""",
"""      const a = String(it.address && it.address.hash || '').toLowerCase();
      if (seen.has(a)) { repeats++; continue; }   // e10: a page-boundary repeat, never a second holder
      seen.add(a);
      if (EXCLUDE.has(a)) { leftKnown++; continue; }""")
edit(HR, """      kept.push(key(v));""", """      kept.push([key(v), a.slice(2, 8)]);   // e9: [balance key, address tag]""")
edit(HR, """  if (expected && rows < expected * 0.98) throw new Error(`${sym}: read ${rows} rows but PulseScan counts ${expected} holders`);
  kept.sort((x, y) => y - x);
  console.log(`${sym}: ${rows} rows in ${Math.round((Date.now() - t0) / 1000)} s → ${kept.length} ranked (left out: ${leftKnown} known, ${leftContracts} contracts, ${leftDust} at zero)`);
  return { holders: kept.length, listed: rows, left: { known: leftKnown, contracts: leftContracts, dust: leftDust }, readAt: new Date().toISOString(), top: top.sort((x, y) => y[1] - x[1] || (x[0] < y[0] ? -1 : 1)), b: kept };""",
"""  if (expected && seen.size < expected * 0.98) throw new Error(`${sym}: read ${seen.size} addresses but PulseScan counts ${expected} holders`);
  kept.sort((x, y) => (y[0] - x[0]) || (x[1] < y[1] ? -1 : x[1] > y[1] ? 1 : 0));
  console.log(`${sym}: ${rows} rows (${repeats} page repeats dropped) in ${Math.round((Date.now() - t0) / 1000)} s → ${kept.length} ranked (left out: ${leftKnown} known, ${leftContracts} contracts, ${leftDust} at zero)`);
  return { holders: kept.length, listed: seen.size, repeats, left: { known: leftKnown, contracts: leftContracts, dust: leftDust }, readAt: new Date().toISOString(), top: top.sort((x, y) => y[1] - x[1] || (x[0] < y[0] ? -1 : 1)), b: kept.map(x => x[0]), t: kept.map(x => x[1]).join('') };""")

# ================================================= e10 — build-rank-history.mjs index(): shared ties ===========================
edit(RH, """    const order = [...cur.entries()].sort((x, y) => (y[1] - x[1]) || (x[0] < y[0] ? -1 : 1));   // ties: by address, so a rank is reproducible
    counts.push(order.length);
    order.forEach(([a], i) => { let t = tracks.get(a); if (!t) tracks.set(a, t = new Map()); t.set(di, i + 1); });""",
"""    const order = [...cur.entries()].sort((x, y) => (y[1] - x[1]) || (x[0] < y[0] ? -1 : 1));   // order: by balance, then address (reproducible)
    counts.push(order.length);
    /* Audit IV e10 (2026-10-23): ties SHARE a rank, compared on the rounded key the badge uses (whole tokens from 1 up, 6 decimals
       below) — rank = 1 + how many hold strictly more, exactly pfRank / t1Rank. Ties used to be broken by address, so a wallet in a
       tie block sat up to the block's size below the rank the badge shows for the same balance. */
    const rk = k => k >= 1 ? Math.floor(k + 1e-9) : Math.floor(k * 1e6 + 1e-6) / 1e6;
    let prevK = null, prevR = 0;
    order.forEach(([a, k], i) => { const kk = rk(k); const r = kk === prevK ? prevR : i + 1; prevK = kk; prevR = r;
      let t = tracks.get(a); if (!t) tracks.set(a, t = new Map()); t.set(di, r); });""")

# ================================================= e9 — the page: pfRank leaves the wallet's own entry out ======================
edit(LG, """    /* → null when the list is missing / stale or the balance is 0; else {r, pass} */
    const pfRank=(ranks,tok,bal)=>{const t=ranks&&!ranks.stale&&ranks.tokens&&ranks.tokens[tok];if(!t||!Array.isArray(t.b)||!(bal>0))return null;
      const b=t.b,x=pfRankKey(bal);let lo=0,hi=b.length;while(lo<hi){const m=(lo+hi)>>1;if(b[m]>x)lo=m+1;else hi=m;}""",
"""    /* Audit IV e9 (2026-10-23): the list is up to 2 h old, so a wallet that SOLD since it was read still had its old, higher entry in
       it — ranked one place low and told to "pass" itself. holder-ranks.json now carries `t`, the first 6 hex characters of every
       listed address aligned with `b` (6 chars per entry): find the wallet's own entry by its tag (the closest balance if two share
       one — about 1 in 1,000) and rank against the list WITHOUT it. A file without `t` ranks as before. Lists cached per address. */
    const PF_RK_OWN=new WeakMap();
    const pfRankList=(t,addr)=>{const b=t.b,T=t.t;if(!addr||typeof T!=='string'||T.length!==b.length*6)return b;
      let c=PF_RK_OWN.get(b);if(!c){c=new Map();PF_RK_OWN.set(b,c);}const a=String(addr).toLowerCase();if(c.has(a))return c.get(a);
      const tag=a.slice(2,8);let j=-1,i=T.indexOf(tag),js=[];while(i>=0){if(i%6===0)js.push(i/6);i=T.indexOf(tag,i+1);}
      if(js.length===1)j=js[0];else if(js.length>1)j=js[0];   // a shared tag: the first (highest) — the caller re-picks by balance below
      const out=j<0?b:b.slice(0,j).concat(b.slice(j+1));out.js=js;c.set(a,out);return out;};
    /* → null when the list is missing / stale or the balance is 0; else {r, pass} */
    const pfRank=(ranks,tok,bal,addr)=>{const t=ranks&&!ranks.stale&&ranks.tokens&&ranks.tokens[tok];if(!t||!Array.isArray(t.b)||!(bal>0))return null;
      const x=pfRankKey(bal);let b=pfRankList(t,addr);
      if(b.js&&b.js.length>1){const j=b.js.reduce((p,q)=>Math.abs(t.b[q]-x)<Math.abs(t.b[p]-x)?q:p);b=t.b.slice(0,j).concat(t.b.slice(j+1));}   // e9: tag collision → the entry nearest this balance
      let lo=0,hi=b.length;while(lo<hi){const m=(lo+hi)>>1;if(b[m]>x)lo=m+1;else hi=m;}""")
edit(V2, """rankRow={rkOne&&<PfRankRow tok="PTGC" x={pfRank(ranks,'PTGC',pt.totalHolding)}""",
         """rankRow={rkOne&&<PfRankRow tok="PTGC" x={pfRank(ranks,'PTGC',pt.totalHolding,counted[0]&&counted[0].address)}""")
edit(V2, """rankRow={rkOne&&<PfRankRow tok="UFO" x={pfRank(ranks,'UFO',uf.balance)}""",
         """rankRow={rkOne&&<PfRankRow tok="UFO" x={pfRank(ranks,'UFO',uf.balance,counted[0]&&counted[0].address)}""")
edit(V2, """const x=pfRank(ranks,tok,tok==='PTGC'?d.ptgc.totalHolding:d.ufo.balance);""",
         """const x=pfRank(ranks,tok,tok==='PTGC'?d.ptgc.totalHolding:d.ufo.balance,w.address);""")
edit(V2, """rp:pfRank(ranks,'PTGC',pT),ru:pfRank(ranks,'UFO',uT)};""", """rp:pfRank(ranks,'PTGC',pT,a),ru:pfRank(ranks,'UFO',uT,a)};""")
edit(RK, """      const live=pfRank(ranks,tok,bal);""", """      const live=pfRank(ranks,tok,bal,w&&w.address);   // e9: without the wallet's own (possibly stale) entry""")

# ================================================= e11 — BEST EVER / LOWEST over the whole life ================================
edit(RK, """      const first=pts.find(r=>r>0)||null,best=held.length?Math.min(...held):null,worst=held.length?Math.max(...held):null;
      const bestI=best!=null?pts.indexOf(best):-1,worstI=worst!=null?pts.lastIndexOf(worst):-1;""",
"""      /* Audit IV e11 (2026-10-23): BEST EVER / LOWEST are the wallet's whole life (they were the selected period's — "best ever #9,786"
         for a wallet that was #307). The chart keeps the period's own best for its gridline and marker. Indexes are into `full`. */
      const life=full?full.filter(r=>r>0):[];
      const first=pts.find(r=>r>0)||null,best=life.length?Math.min(...life):null,worst=life.length?Math.max(...life):null;
      const bestI=best!=null?full.indexOf(best):-1,worstI=worst!=null?full.lastIndexOf(worst):-1;""")
edit(RK, """{bestI>=0?pfrFmt(pfrDate(h.day0,i0+bestI),true):''}""", """{bestI>=0?pfrFmt(pfrDate(h.day0,bestI),true):''}""")
edit(RK, """{worstI>=0?pfrFmt(pfrDate(h.day0,i0+worstI),true):''}""", """{worstI>=0?pfrFmt(pfrDate(h.day0,worstI),true):''}""")

# ================================================= e9 — the Top 100 checker, every holder (not only `top`) =====================
edit(T1, """        return{top:Array.isArray(t.top)?t.top.map(r=>({a:String(r[0]).toLowerCase(),v:r[1]})):null,all:t.b,count:t.holders,tot:SUP,at:Date.parse(t.readAt)};""",
"""        return{top:Array.isArray(t.top)?t.top.map(r=>({a:String(r[0]).toLowerCase(),v:r[1]})):null,all:t.b,tg:typeof t.t==='string'&&t.t.length===t.b.length*6?t.t:null,count:t.holders,tot:SUP,at:Date.parse(t.readAt)};""")
edit(T1, """        const own=view.top&&view.top.find(x=>x.a===al);""",
"""        /* Audit IV e9: `top` has addresses for the first 110 only; holder-ranks.json's `t` tags every entry (first 6 hex chars,
           aligned with the list), so a checked wallet below #110 also has its own old entry left out (the nearest balance on a
           shared tag). */
        const own=(view.top&&view.top.find(x=>x.a===al))||(()=>{if(!view.tg)return null;const tag=al.slice(2,8),js=[];let i=view.tg.indexOf(tag);
          while(i>=0){if(i%6===0)js.push(i/6);i=view.tg.indexOf(tag,i+1);}if(!js.length)return null;
          const j=js.reduce((p,q)=>Math.abs(view.all[q]-k)<Math.abs(view.all[p]-k)?q:p);return{a:al,v:view.all[j]};})();""")

for tool in ('tools/pf-v2.py', 'tools/top100.py'):
    out = subprocess.run([sys.executable, tool], capture_output=True, text=True)
    if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
    print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-rank: {n} edit(s), index.html {sha("index.html")}, portfolio.html {sha("portfolio.html")}')
