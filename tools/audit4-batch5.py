#!/usr/bin/env python3
"""Audit IV batch 5 (2026-10-23): e26 + e27 + e28 + e29 + e30 + e31. Idempotent, from the repo root:
    python3 tools/audit4-batch5.py        (twice: the second run must print "0 edit(s)")
See handover/HANDOVER.md "Current state" for what each item does and the evidence.
"""
import hashlib, re, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    if s.count(old) != count:
        alt = ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in old)
        if s.count(alt) == count: old = alt
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

IX, PF, CA, CH = 'index.html', 'portfolio.html', 'calculators.html', 'charts.html'

# ======================= e29 — index.html data edges =======================
# (1) TXNS 24H: the arrow from the SAME source as the count (DexScreener) — Shaka 2026-10-23 "Yes, DexScreener".
edit(IX, '''          const txnChange = getTransactionChange(token, 24);
          if (txnChange) setTxnChange24h(txnChange.changePercent);''', '''          /* Audit IV e29 (Shaka: "Yes, DexScreener"): the TXNS tile's count is DexScreener's (every pair's h24 buys + sells), so
             its arrow is too — the live count vs the pipeline's last DexScreener reading of yesterday (UTC; burn-summary.json
             snapshots, written hourly). CoinGecko's transaction-history (20 pools, its own direction labels) is only the fallback
             when that snapshot is missing. Before: 879 · ↑96.6 % (CoinGecko 820 vs 417); now ↑43.6 % (DexScreener 879 vs 612). */
          const dsTxnChange=(()=>{
            const live=(d&&isFinite(d.buys)&&isFinite(d.sells)&&d.buys!=null&&d.sells!=null)?d.buys+d.sells:null;
            const snaps=burnHistoryCache&&burnHistoryCache[token]&&burnHistoryCache[token].snapshots;
            if(live==null||!Array.isArray(snaps))return null;
            const today=new Date().toISOString().slice(0,10),yesterday=new Date(Date.now()-864e5).toISOString().slice(0,10);
            const y=snaps.find(s=>s&&s.date===yesterday);   // newest first; the file's own "today" entry is skipped
            return (y&&y.txns>0)?((live-y.txns)/y.txns)*100:null;
          })();
          const txnChange = dsTxnChange==null?getTransactionChange(token, 24):null;
          if (dsTxnChange!=null) setTxnChange24h(dsTxnChange);
          else if (txnChange) setTxnChange24h(txnChange.changePercent);''')
# (2) fetchDex's price fallback: dsPricePair (gotcha 35), never "the first pair with a price"
edit(IX, "          const pp = mp || pairs.find(p=>parseFloat(p.priceUsd)>0) || pairs[0];",
         "          const pp = mp || dsPricePair(pairs, addr) || pairs[0];   // Audit IV e29: base-side pair only (gotcha 35) — a quote-side listing's priceUsd is the OTHER token's")
edit(IX, '''            const mainPairData = existingPairs.find(p => parseFloat(p.priceUsd) > 0) || existingPairs[0];
            ptgcPrice = parseFloat(mainPairData.priceUsd) || 0;''', '''            const mainPairData = dsPricePair(existingPairs, addr) || existingPairs[0];   // e29: base-side pair only
            ptgcPrice = parseFloat(mainPairData.priceUsd) || 0;''')
edit(IX, '''            const mainPairData = existingPairs.find(p => parseFloat(p.priceUsd) > 0) || existingPairs[0];
            ufoPrice = parseFloat(mainPairData.priceUsd) || 0;''', '''            const mainPairData = dsPricePair(existingPairs, addr) || existingPairs[0];   // e29: base-side pair only
            ufoPrice = parseFloat(mainPairData.priceUsd) || 0;''')
# (3) holder-history age gate: a snapshot older than 36 h is not "now" (the Holders tile and its 7D / 30D / 90D)
edit(IX, '''      if(useCache&&holderHistoryCacheNew&&holderHistoryCacheNew.snapshots?.length>0){
        const lastSnap=holderHistoryCacheNew.snapshots[holderHistoryCacheNew.snapshots.length-1];
        if(lastSnap[token]>0)return lastSnap[token];
      }
      if(useCache&&burnHistoryCache&&burnHistoryCache[token]?.holders>0){''', '''      /* Audit IV e29: a cached count is used only while it is recent (HOLDER_SNAP_MAX_AGE_MS) — a stalled pipeline used to
         keep printing a days-old holder count as today's. Older → the live PulseScan counter below. */
      if(useCache&&holderHistoryCacheNew&&holderHistoryCacheNew.snapshots?.length>0){
        const lastSnap=holderHistoryCacheNew.snapshots[holderHistoryCacheNew.snapshots.length-1];
        const age=Date.now()-Date.parse(lastSnap.timestamp);
        if(lastSnap[token]>0&&age<HOLDER_SNAP_MAX_AGE_MS)return lastSnap[token];
      }
      if(useCache&&burnHistoryCache&&burnHistoryCache[token]?.holders>0&&(burnHistoryAgeMs()??Infinity)<HOLDER_SNAP_MAX_AGE_MS){''')
edit(IX, "    const BURN_HISTORY_STALE_MS=2.5*60*60*1000;", "    const HOLDER_SNAP_MAX_AGE_MS=36*60*60*1000;   // Audit IV e29: a holder count / holder-history point older than this is not \"now\"\n    const BURN_HISTORY_STALE_MS=2.5*60*60*1000;")
edit(IX, '''            const newest = snapshots[snapshots.length - 1];
            const newestTime = new Date(newest.timestamp).getTime();
            ''', '''            const newest = snapshots[snapshots.length - 1];
            const newestTime = new Date(newest.timestamp).getTime();
            /* Audit IV e29: past HOLDER_SNAP_MAX_AGE_MS the file's newest point is not "now" — its 7D / 30D / 90D would be
               measured back from a stale day under a "now" label. The live count alone, no period changes ("—"). */
            if (!(now - newestTime < HOLDER_SNAP_MAX_AGE_MS)) {
              setHoldersByPeriod({ current: h, d1Ago: null, d7Ago: null, d30Ago: null, d90Ago: null, avg7d: null, avg30d: null, avg90d: null });
            } else {
            ''')
edit(IX, '''              avg30d: calcAverage(30),
              avg90d: calcAverage(90)
            });
          } else {
            setHoldersByPeriod({ current: h, d1Ago: null, d7Ago: null, d30Ago: null, d90Ago: null, avg7d: null, avg30d: null, avg90d: null });''', '''              avg30d: calcAverage(30),
              avg90d: calcAverage(90)
            });
            }   // e29 age gate
          } else {
            setHoldersByPeriod({ current: h, d1Ago: null, d7Ago: null, d30Ago: null, d90Ago: null, avg7d: null, avg30d: null, avg90d: null });''')
# (4) the Holders tile's 24 h new-holders line: the window must also reach NOW (a 30 h old file printed "0")
edit(IX, "      return{ins,outs,bounced,net:ins.length-outs.length,covered,coveredFrom,",
         "      const endOk=(now/1000-Number(file.head&&file.head.ts))<=Math.max(3*3600,hours*360);   // Audit IV e29: the file reaches (close to) NOW — 3 h, or a tenth of a long window\n      return{ins,outs,bounced,net:ins.length-outs.length,covered,endOk,coveredFrom,")
edit(IX, "    const nhNet=(file,token,hours)=>{const v=nhView(file,token,hours);return v&&v.covered?v.net:null;};",
         "    const nhNet=(file,token,hours)=>{const v=nhView(file,token,hours);return v&&v.covered&&v.endOk?v.net:null;};   // e29: both ends covered, or \"—\"")


# ======================= e28 — charts.html: a series shorter than the range says so =======================
# Shaka 2026-10-23: "Flag UFO" — keep every token's full range; a token whose data starts after the range start (UFO, the new
# contract, from Jul 10) is labelled "since <date>" on the summary cards, every share-card layout and the status line.
edit(CH, '''/* Build sorted share items for all active tokens */
function getShareItems(includeStartPrice) {''', '''/* Audit IV e28 (2026-10-23): "since Jul 10" when a token's series starts well after the range start — its % is measured
   from its own first point, so it must not read as the same period as the others (1Y: PTGC −90.6 % over a year next to UFO
   −35.3 % over 105 days). Tolerance: 3 h, or 5 % of the range. null = the series covers the range. */
function seriesSinceLabel(d) {
  if (!d || d.length < 2) return null;
  const span = getDays() * 864e5, newest = d[d.length - 1].ts, start = newest - span;
  if (!(d[0].ts > start + Math.max(3 * 3600e3, span * 0.05))) return null;
  return 'since ' + new Date(d[0].ts).toLocaleDateString('en-US', { month: 'short', day: 'numeric', timeZone: 'UTC' });
}
/* Build sorted share items for all active tokens */
function getShareItems(includeStartPrice) {''')
edit(CH, "    const item = { sym: t.sym, color: t.color, logo: t.logo, pct, ps: fmtCardPrice(pN), limited: !!t._limited, coarse: !!t._coarse, spark: sparkSample(d) };",
         "    const item = { sym: t.sym, color: t.color, logo: t.logo, pct, ps: fmtCardPrice(pN), limited: !!t._limited, coarse: !!t._coarse, spark: sparkSample(d), since: seriesSinceLabel(d) };   // e28: since")
edit(CH, """    const limitedBadge = it.limited ? '<span class="card-limited">24H ONLY</span>' : it.coarse ? '<span class="card-limited">DAILY</span>' : '';""",
         """    const limitedBadge = it.limited ? '<span class="card-limited">24H ONLY</span>' : it.coarse ? '<span class="card-limited">DAILY</span>' : it.since ? `<span class="card-limited" style="color:#eab308">${it.since.toUpperCase()}</span>` : '';   // e28""")
edit(CH, """letter-spacing:1px">${item.sym}</div>""", """letter-spacing:1px">${item.sym}</div>${item.since ? `<div style="font-size:${Math.max(9, sz.price)}px;color:#eab308;font-family:'JetBrains Mono',monospace;letter-spacing:0.5px;margin-top:2px">${item.since}</div>` : ''}""", 2)
edit(CH, """font-family:'JetBrains Mono',monospace">${i.sym}</span></div>""", """font-family:'JetBrains Mono',monospace">${i.sym}</span>${i.since ? `<span style="font-size:11px;color:#eab308;font-family:'JetBrains Mono',monospace">${i.since}</span>` : ''}</div>""")
edit(CH, """      <div class="ng-bar-label" style="color:${item.color};font-size:${sz.bLbl}px;width:${sz.bLblW}px">${item.sym}</div>""",
         """      <div class="ng-bar-label" style="color:${item.color};font-size:${sz.bLbl}px;width:${sz.bLblW}px">${item.sym}${item.since ? '*' : ''}</div>""")
edit(CH, """    </div>`;
  }).join('');
}

/* Share cards (Scorecard mode) */""", """    </div>`;
  }).join('') + (items.some(i => i.since) ? `<div style="margin-top:6px;font-size:${sz.bPct}px;color:#eab308;font-family:'JetBrains Mono',monospace;text-align:center">* ${items.filter(i => i.since).map(i => i.sym + ' ' + i.since).join(' · ')} — its % is from its first day, not the range start</div>` : '');   // e28
}

/* Share cards (Scorecard mode) */""")
edit(CH, """    if (carried.length) msg += ` \\u00B7 <span style="color:#eab308">${carried.join(', ')} carried forward (builder could not refresh)</span>`;""",
         """    if (carried.length) msg += ` \\u00B7 <span style="color:#eab308">${carried.join(', ')} carried forward (builder could not refresh)</span>`;
    const shortS = Object.values(TOKENS).filter(t => t.on && t._data && t._data.length >= 2 && !t._limited).map(t => [t.sym, seriesSinceLabel(t._data)]).filter(x => x[1]);   // e28
    if (shortS.length) msg += ` \\u00B7 <span style="color:#eab308">${shortS.map(x => x[0] + ' ' + x[1]).join(', ')}</span>`;""")


# ======================= e27 — Portfolio honesty (fragments, re-spliced by tools/pf-v2.py) =======================
PV, PL = 'tools/pf-v2/PortfolioV2.jsx', 'tools/pf-v2/PfLeagues.jsx'
# (1) the 24H pills: when the 24 h-ago holdings read is missing, the fallback is the PRICE change applied to today's balance —
#     a different quantity (a wallet that bought today read red). Label it so: "24H PRICE".
edit(PV, "{pfPill(tChg,'24H')}", "{pfPill(tChg,h24?'24H':'24H PRICE')}")   # Audit IV e27
edit(PV, "{!simulated&&<span className=\"sp\">{pfPill(pChg,'24H')}</span>}", "{!simulated&&<span className=\"sp\">{pfPill(pChg,h24?'24H':'24H PRICE')}</span>}")
edit(PV, "{!simulated&&<span className=\"sp\">{pfPill(uChg,'24H')}</span>}", "{!simulated&&<span className=\"sp\">{pfPill(uChg,h24?'24H':'24H PRICE')}</span>}")
# (2) holder ranks: staleness PER TOKEN from tokens[tok].readAt (a `carried` token keeps its old readAt) — the file's generatedAt
#     is stamped fresh even when one token's list was carried from days ago.
edit(PL, '''      const stale=!!d&&!(Date.now()-Date.parse(d.generatedAt)<PF_RANKS_STALE);
      return d?{...d,stale}:null;};''', '''      /* Audit IV e27: per token — the builder stamps generatedAt fresh even when it CARRIED one token's old list (its readAt
         stays old). A stale token ranks nothing; the column hides only when both are stale. */
      const rdAt=tok=>Date.parse((d&&d.tokens[tok]&&d.tokens[tok].readAt)||(d&&d.generatedAt));
      const staleTok=d?{PTGC:!(Date.now()-rdAt('PTGC')<PF_RANKS_STALE),UFO:!(Date.now()-rdAt('UFO')<PF_RANKS_STALE)}:null;
      const stale=!!d&&staleTok.PTGC&&staleTok.UFO;
      return d?{...d,stale,staleTok,readAt:{PTGC:rdAt('PTGC'),UFO:rdAt('UFO')}}:null;};''')
edit(PL, "    const pfRank=(ranks,tok,bal,addr)=>{const t=ranks&&!ranks.stale&&ranks.tokens&&ranks.tokens[tok];",
         "    const pfRank=(ranks,tok,bal,addr)=>{const t=ranks&&!ranks.stale&&!(ranks.staleTok&&ranks.staleTok[tok])&&ranks.tokens&&ranks.tokens[tok];   // e27: per-token staleness")
edit(PV, "the holder list is refreshed every 2 hours {'\\u00B7'} list read {pfAgo(Date.parse(ranks.generatedAt))}</div>",
         "the holder list is refreshed every 2 hours {'\\u00B7'} PTGC list read {pfAgo(ranks.readAt?ranks.readAt.PTGC:Date.parse(ranks.generatedAt))}, UFO {pfAgo(ranks.readAt?ranks.readAt.UFO:Date.parse(ranks.generatedAt))}{ranks.staleTok&&(ranks.staleTok.PTGC||ranks.staleTok.UFO)?<> {'\\u00B7'} <span style={{color:'#E8C044'}}>{ranks.staleTok.PTGC?'PTGC':'UFO'} ranks hidden — its list is out of date</span></>:null}</div>")   # e27
edit(PV, "Holder ranks are hidden: the holder list is out of date (read {pfAgo(Date.parse(ranks.generatedAt))})",
         "Holder ranks are hidden: the holder list is out of date (read {pfAgo(ranks.readAt?Math.max(ranks.readAt.PTGC||0,ranks.readAt.UFO||0):Date.parse(ranks.generatedAt))})")
out = subprocess.run([sys.executable, 'tools/pf-v2.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])


# ======================= e30 — no iOS focus zoom: inputs ≥ 16 px under 640 px =======================
edit('tools/pf-v2/pf2.css', "    .pf2-add input::placeholder{color:rgba(255,255,255,.45)}",
     "    .pf2-add input::placeholder{color:rgba(255,255,255,.45)}\n    @media(max-width:640px){.pf2-add input,.pf2-add input.ad,.pf2-newg input,.pf2-srch input,.pf2-mmf input{font-size:16px}}   /* Audit IV e30: iOS Safari zooms the page on focus under 16 px and never zooms back */")
edit('tools/top100/t1.css', ".t1go{padding:0 12px;font-size:10.5px!important}.t1inp input{font-size:15px}",
     ".t1go{padding:0 12px;font-size:10.5px!important}.t1inp input{font-size:16px}   /* Audit IV e30: was 15 px → iOS focus zoom */")

# ======================= e31 — buys / sells not by colour alone; the reason for a dash readable on a phone =======================
edit(IX, "    /* Explainer copy, in one place. Each is a function of the token so the wording can name", '''    /* Audit IV e31 (2026-10-23): buys / sells were told apart by green / red alone — a screen reader heard two numbers, a
       red-green colour-blind visitor saw two numbers. A visible B / S letter + the word for screen readers. */
    const BsN=({k,n})=><><span className="sr-only">{k==='b'?'buys ':'sells '}</span><span aria-hidden="true" style={{fontSize:'.78em',opacity:.8,marginRight:'.12em'}}>{k==='b'?'B':'S'}</span>{n}</>;
    /* Audit IV e31: the "unknown, not zero" reason lived only in title= (hover — invisible on phones). The dash + an ⓘ that
       opens it on tap; the title stays for mouse users. */
    const DashWhy=({why})=><span className="inline-flex items-center gap-1">{'\\u2014'}<InfoTip label="Why a dash" glyphClass="text-[10px]"><p>{why}</p><p>A dash means the number could not be read — it is unknown, never zero.</p></InfoTip></span>;
    /* Explainer copy, in one place. Each is a function of the token so the wording can name''')
edit(IX, '''<small><span className="b">{data?.buys||0}</span><span className="sl"> / </span><span className="s">{data?.sells||0}</span></small></>:<span title="24h transaction counts unavailable — DexScreener did not answer.">{'—'}</span>''',
         '''<small><span className="b"><BsN k="b" n={data?.buys||0}/></span><span className="sl"> / </span><span className="s"><BsN k="s" n={data?.sells||0}/></span></small></>:<span title="24h transaction counts unavailable — DexScreener did not answer."><DashWhy why="The 24h transaction counts are unavailable — DexScreener did not answer."/></span>''')
edit(IX, '''title={txnsKnown?undefined:'24h transaction counts unavailable — DexScreener did not answer.'}>{txnsKnown?(data?.buys||0)+(data?.sells||0):'\\u2014'}</span>
                    {txnsKnown&&<span className="text-xs sm:text-sm tabular-nums"><span className="text-emerald-400">{data?.buys||0}</span><span className="text-white/30 mx-0.5">/</span><span className="text-rose-400">{data?.sells||0}</span></span>}''',
         '''title={txnsKnown?undefined:'24h transaction counts unavailable — DexScreener did not answer.'}>{txnsKnown?(data?.buys||0)+(data?.sells||0):<DashWhy why="The 24h transaction counts are unavailable — DexScreener did not answer."/>}</span>
                    {txnsKnown&&<span className="text-xs sm:text-sm tabular-nums"><span className="text-emerald-400"><BsN k="b" n={data?.buys||0}/></span><span className="text-white/30 mx-0.5">/</span><span className="text-rose-400"><BsN k="s" n={data?.sells||0}/></span></span>}''')
edit(IX, '''<span className="text-green-400">{buys}</span>/<span className="text-red-400">{sells}</span>''',
         '''<span className="text-green-400"><BsN k="b" n={buys}/></span>/<span className="text-red-400"><BsN k="s" n={sells}/></span>''', 2)
edit(IX, '''<div className="bs"><b>{buys??'\\u2014'}</b><s aria-hidden="true"></s><i>{sells??'\\u2014'}</i></div>''',
         '''<div className="bs"><b><span className="sr-only">buys </span>{buys??'\\u2014'}</b><s aria-hidden="true"></s><i><span className="sr-only">sells </span>{sells??'\\u2014'}</i></div>''')
edit(IX, '''<LpTh k="txns" name="transactions" className="c-tx c-mid" {...th}>Txns</LpTh>''',
         '''<LpTh k="txns" name="transactions" className="c-tx c-mid" {...th}>Txns<span style={{display:'block',fontSize:'.8em',opacity:.6,letterSpacing:'.08em'}} aria-hidden="true">buys | sells</span></LpTh>''')   # e31: what the green | red pair under each total is
edit(IX, '''<div className="text-base sm:text-xl font-medium text-white/30 leading-none" title="The chain read for this window failed. This is not zero — it is unknown.">{'\\u2014'}</div>''',
         '''<div className="text-base sm:text-xl font-medium text-white/30 leading-none" title="The chain read for this window failed. This is not zero — it is unknown."><DashWhy why="The chain read for this window failed."/></div>''')
edit(IX, '''title={d.value==null?'Not read yet (or the read failed). Unknown, not zero.':undefined}>{d.value==null?'\\u2014':d.value.toFixed(2)+'%'}</span>''',
         '''title={d.value==null?'Not read yet (or the read failed). Unknown, not zero.':undefined}>{d.value==null?<DashWhy why="Not read yet, or the read failed."/>:d.value.toFixed(2)+'%'}</span>''')

# ======================= e26 — Affiliates: reachable by keyboard; Portfolio's code windows are dialogs =======================
edit(IX, "    const SortGlyph=({active,dir})=>", '''    /* Audit IV e26 (2026-10-23): Enter / Space on a focusable non-button (a referrer row, name, "▶ n" expander, sort header) =
       a click. AfPodium already did this; the rest of the page was mouse-only. */
    const afKey=fn=>e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();fn(e);}};
    const SortGlyph=({active,dir})=>''')
s = open(IX, encoding='utf-8').read()
a = s.index('    const SortGlyph=({active,dir})=>')
b = s.index('setExpandedEntries(ns);}}', a) + 6000
seg = s[a:b]
if 'afKey(' not in seg[200:]:
    k = 0
    # sort headers: focusable + aria-sort
    def th(m):
        global k; k += 1
        fn, col = m.group(3), m.group(4)
        sc, sd = ('sortCol', 'sortDir') if fn == 'toggleSort' else ('commSortCol', 'commSortDir')
        return f"{m.group(1)}{m.group(2) or ''} onClick={{()=>{fn}('{col}')}} tabIndex={{0}} onKeyDown={{afKey(()=>{fn}('{col}'))}} aria-sort={{{sc}==='{col}'?({sd}==='asc'?'ascending':'descending'):'none'}}>"
    seg = re.sub(r"(<th className=\"[^\"]*cursor-pointer[^\"]*\")( style=\{\{[^}]*\}\})? onClick=\{\(\)=>(toggleSort|toggleCommSort)\('(\w+)'\)\}>", th, seg)
    # every other cursor-pointer element with an onClick (span / div / tr / td): tabIndex + Enter/Space (+ role=button on span/div)
    out, i = [], 0
    for m in re.finditer(r'<(span|div|tr|td)\b', seg):
        if m.start() < i: continue
        j = m.end(); depth = 0; q = None; end = None
        while j < len(seg):
            c = seg[j]
            if q:
                if c == q: q = None
            elif c in '"\'' and depth == 0: q = c
            elif c == '{': depth += 1
            elif c == '}': depth -= 1
            elif c == '>' and depth == 0: end = j; break
            j += 1
        if end is None: continue
        tag = seg[m.start():end]
        if 'cursor-pointer' not in tag or 'onClick={' not in tag or 'onKeyDown' in tag or '<th' in tag: continue
        h0 = tag.index('onClick={') + len('onClick={'); d = 1; p = h0
        while d:
            if tag[p] == '{': d += 1
            elif tag[p] == '}': d -= 1
            p += 1
        handler = tag[h0:p - 1]
        if handler.startswith('e=>e.stopPropagation'): continue
        extra = f' tabIndex={{0}} onKeyDown={{afKey({handler})}}'
        if m.group(1) in ('span', 'div'): extra = ' role="button"' + extra
        if 'setExpandedEntries' in handler: extra += ' aria-expanded={expanded}'
        if 'setExpandedReceipts' in handler: extra += ' aria-expanded={expandedReceipts.has(dateKey)}'
        out.append(seg[i:end] + extra); i = end; k += 1
    seg = ''.join(out) + seg[i:]
    s = s[:a] + seg + s[b:]
    open(IX, 'w', encoding='utf-8').write(s); n += 1; print(f'  affiliates: {k} controls made keyboard-reachable')

# Portfolio: Get Code / Load Code → PfModal (Escape, focus trap, scroll lock, focus return); the two dead components deleted
edit(PF, '''          {showCodeModal&&(
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80" onClick={()=>setShowCodeModal(false)}>
              <div className="bg-[#111] border border-[#D9CA5D]/30 rounded-2xl max-w-lg w-full p-6" onClick={e=>e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-[#D9CA5D]">{'\\u{1F4CB}'} Portfolio Code</h2>
                  <button onClick={()=>setShowCodeModal(false)} className="text-white/60 hover:text-white text-2xl">{'\\u00D7'}</button>''', '''          {showCodeModal&&(   /* Audit IV e26: a real dialog — PfModal (Escape, Tab stays inside, scroll lock, focus back to GET CODE) */
            <PfModal className="z-50 flex items-center justify-center p-4 bg-black/80" onClose={()=>setShowCodeModal(false)} label="Portfolio code">
              <div className="bg-[#111] border border-[#D9CA5D]/30 rounded-2xl max-w-lg w-full p-6" onClick={e=>e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-[#D9CA5D]">{'\\u{1F4CB}'} Portfolio Code</h2>
                  <button onClick={()=>setShowCodeModal(false)} aria-label="Close" className="text-white/60 hover:text-white text-2xl min-w-[40px] min-h-[40px] -mr-2">{'\\u00D7'}</button>''')
edit(PF, '''                  {codeCopied===true?'✓ Copied!':codeCopied==='fail'?'Copy failed — select the code and copy it':'Copy to Clipboard'}
                </button>
              </div>
            </div>
          )}''', '''                  {codeCopied===true?'✓ Copied!':codeCopied==='fail'?'Copy failed — select the code and copy it':'Copy to Clipboard'}
                </button>
              </div>
            </PfModal>
          )}''')
edit(PF, '''          {showLoadModal&&(
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80" onClick={()=>setShowLoadModal(false)}>
              <div className="bg-[#111] border border-[#D9CA5D]/30 rounded-2xl max-w-lg w-full p-6" onClick={e=>e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-[#D9CA5D]">{'\\u{1F4E5}'} Load Portfolio</h2>
                  <button onClick={()=>setShowLoadModal(false)} className="text-white/60 hover:text-white text-2xl">{'\\u00D7'}</button>''', '''          {showLoadModal&&(   /* Audit IV e26: PfModal — the window that REPLACES the wallet list needs a deliberate Escape */
            <PfModal className="z-50 flex items-center justify-center p-4 bg-black/80" onClose={()=>setShowLoadModal(false)} label="Load a portfolio code">
              <div className="bg-[#111] border border-[#D9CA5D]/30 rounded-2xl max-w-lg w-full p-6" onClick={e=>e.stopPropagation()}>
                <div className="flex justify-between items-center mb-4">
                  <h2 className="text-2xl font-bold text-[#D9CA5D]">{'\\u{1F4E5}'} Load Portfolio</h2>
                  <button onClick={()=>setShowLoadModal(false)} aria-label="Close" className="text-white/60 hover:text-white text-2xl min-w-[40px] min-h-[40px] -mr-2">{'\\u00D7'}</button>''')
edit(PF, '''placeholder="GRAY-..." className="w-full bg-black/50''', '''placeholder="GRAY-..." aria-label="Portfolio code" autoFocus className="w-full bg-black/50''')
edit(PF, '''                <p className="text-white/40 text-sm text-center mt-3">This will replace your current portfolio</p>
              </div>
            </div>
          )}''', '''                <p className="text-white/40 text-sm text-center mt-3">This will replace your current portfolio</p>
              </div>
            </PfModal>
          )}''')
s = open(PF, encoding='utf-8').read()
a0 = s.find('          {/* Edit Wallet Modal */}\n          {editingWallet&&(')
if a0 >= 0:   # dead since v2 (PfEditWallet replaced it; nothing sets editingWallet any more)
    b0 = s.index('          {/* PTGC Leagues Modal */}', a0)
    s = s[:a0] + '          {/* (Audit IV e26: the old Edit Wallet window was deleted — PfEditWallet is the one in use) */}\n          \n' + s[b0:]
    open(PF, 'w', encoding='utf-8').write(s); n += 1
s = open(PF, encoding='utf-8').read()
a0 = s.find('    // Disclaimer Modal Component\n    const DisclaimerModal=({onAccept})=>{')
if a0 >= 0:   # never rendered on this page
    b0 = s.index('    // ===== Standalone App =====', a0)
    s = s[:a0] + '    // (Audit IV e26: an unused DisclaimerModal copy was deleted — index.html owns the disclaimer)\n    \n' + s[b0:]
    open(PF, 'w', encoding='utf-8').write(s); n += 1
for cmd in ('tools/pf-v2.py', 'tools/top100.py'):
    out = subprocess.run([sys.executable, cmd], capture_output=True, text=True)
    if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
    print('  ' + out.stdout.strip().splitlines()[-1])


# tw.css gains min-w-[40px] / min-h-[40px] (the code windows' close buttons) → `cd tools/harness && npm run css`, and the cache key moves on
for p in (IX, PF, CA, CH, 'ledger.html'):
    edit(p, 'href="tw.css?v=4"', 'href="tw.css?v=5"')

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-batch5: {n} edit(s), index {sha(IX)}, portfolio {sha(PF)}, calculators {sha(CA)}, charts {sha(CH)}')
