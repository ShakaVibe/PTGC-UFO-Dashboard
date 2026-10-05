#!/usr/bin/env python3
"""Charts page — GeckoTerminal refusals (2026-10-05, Shaka's live look: 14D showed two days, "limited data", slow). His console:
every GeckoTerminal OHLCV call after the first was refused (a 429 / 5xx without CORS headers prints as a CORS error), the page's
fetchRetry retried each one UNGATED two seconds later (refused again), then fell back to DexScreener's 2-point line and CACHED it
for the tier's TTL, so Refresh kept the two points. Three changes:
  1. one global GeckoTerminal back-off: a refusal pauses EVERY GT call (6 s, then 12 s) and the same page is retried through the
     gate — the LP Pairs curves' cure from 2026-09-30 (index.html `_lpPauseUntil`);
  2. 7D / 14D: when GeckoTerminal's hourly candles are not to be had, the prebuilt DAILY file (charts-data.json, the 1M–1Y
     source) clipped to the range draws the line — 8 / 15 real daily closes, tagged "DAILY", before DexScreener's two points;
  3. a 2-point / daily fallback is never "fresh" in the cache: the next load tries GeckoTerminal again.
Run after tools/charts-v2.py: python3 tools/charts-gt.py (refuses to run twice)."""
import sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
p=root/'charts.html'; s=p.read_text()
if '_gtPauseUntil' in s: sys.exit('already applied')
def rep(old,new,count=1):
    global s
    n=s.count(old); assert n==count,(old[:70],n); s=s.replace(old,new)

# 1. the gate honours a global pause; a refusal sets it
rep('''let _gtChain = Promise.resolve();
let _gtLast = 0;
const GT_MIN_INTERVAL = 2200;
function gtGate() {
  const p = _gtChain.then(async () => {
    const wait = GT_MIN_INTERVAL - (Date.now() - _gtLast);
    if (wait > 0) await sleep(wait);
    _gtLast = Date.now();
  });''','''let _gtChain = Promise.resolve();
let _gtLast = 0;
let _gtRefusals = 0;        // 2026-10-05: consecutive refusals, across tokens; any success resets it
let _gtCircuitUntil = 0;   // 2026-10-05: three refusals in a row open the circuit for 45 s — every other GT fetch returns null at once and the fallbacks draw
let _gtPauseUntil = 0;   // 2026-10-05: a refusal (429 / 5xx — the browser prints it as a CORS error) pauses EVERY GT call, not just the one
const GT_MIN_INTERVAL = 2200;
function gtGate() {
  const p = _gtChain.then(async () => {
    const pause = _gtPauseUntil - Date.now();
    if (pause > 0) await sleep(pause);
    const wait = GT_MIN_INTERVAL - (Date.now() - _gtLast);
    if (wait > 0) await sleep(wait);
    _gtLast = Date.now();
  });''')
rep('''  for (let p = 0; p < MAX_PAGES; p++) {
    if (signal && signal.aborted) return null;
    const url = `https://api.geckoterminal.com/api/v2/networks/${GT_NETWORK}/pools/${pairAddr}/ohlcv/${timeframe}` +''','''  if (_gtCircuitUntil > Date.now()) { console.warn(`GeckoTerminal circuit open — skipping ${sym} [${tier}] (fallbacks instead)`); return null; }
  for (let p = 0; p < MAX_PAGES; p++) {
    if (signal && signal.aborted) return null;
    const url = `https://api.geckoterminal.com/api/v2/networks/${GT_NETWORK}/pools/${pairAddr}/ohlcv/${timeframe}` +''')
rep('''    await gtGate();
    const r = await fetchRetry(url, 2, 2000, signal, { 'accept': 'application/json' });
    if (!r) break;
    let j;''','''    /* 2026-10-05: one gated attempt per try, fetchRetry's own retry off (retries = 1 — it fired 2 s later, outside the gate, and was
       refused too). A refusal = fetchRetry's null: a network error (a 429 / 5xx without CORS headers, which the browser prints as a
       CORS error), a 429 it could read, or a 404 (a pool GT does not list — same handling, cheap). */
    let r = null;
    for (let attempt = 0; attempt < 3 && !r; attempt++) {
      if (_gtCircuitUntil > Date.now()) return null;   // the circuit opened (this token's refusals or another's) — the fallbacks draw
      await gtGate();
      if (signal && signal.aborted) return null;
      r = await fetchRetry(url, 1, 2000, signal, { 'accept': 'application/json' });
      if (!r) {   // refusals count ACROSS tokens: the 1st pauses every GT call 4 s, the 2nd 8 s, the 3rd opens the circuit for 45 s
        _gtRefusals++;
        if (_gtRefusals >= 3) { _gtCircuitUntil = Date.now() + 45000; console.warn(`GeckoTerminal refused ${_gtRefusals} calls in a row — circuit open 45 s, the fallbacks draw the rest of this load`); return null; }
        _gtPauseUntil = Math.max(_gtPauseUntil, Date.now() + 4000 * _gtRefusals); console.warn(`GeckoTerminal refused ${sym} [${tier}] page ${p} — pausing ${4 * _gtRefusals}s`);
      }
    }
    if (!r) return null;
    _gtRefusals = 0;
    _gtCircuitUntil = 0;
    let j;''')

# 2. 7D / 14D from the daily file when the hourly candles are not to be had (before the 2-point line)
rep('''        /* Last resort for PulseChain tokens: DexScreener 2-point */
        if ((!data || data.length < 2) && (t.pairAddr || t.dexAddr)) {''','''        /* 2026-10-05: 7D / 14D without GeckoTerminal's hourly candles → the prebuilt DAILY file clipped to the range (real daily
           closes, 8 / 15 points, tagged DAILY) — far better than the two-point line that used to stand in for a fortnight. */
        if ((!data || data.length < 2) && tier === 'hourly' && t.source === 'moralis') {
          try {
            const json = await loadStaticDaily(signal);
            const series = getStaticDailySeries(json, k);
            const coarse = series ? cleanData(series, days + 1) : null;
            if (coarse && coarse.length >= 3) {
              console.log(`Daily-file fallback for ${k} [${tier}]: ${coarse.length} daily closes over ${days}d`);
              setCached(k, tier, coarse, false, true);
              applyTokenData(k, coarse, false, days, true);
              continue;
            }
          } catch (e) { if (e.name !== 'AbortError') console.warn(`Daily-file fallback failed for ${k}:`, e); }
        }

        /* Last resort for PulseChain tokens: DexScreener 2-point */
        if ((!data || data.length < 2) && (t.pairAddr || t.dexAddr)) {''')

# 3. the cache: a fallback entry is shown at once but never counts as fresh
rep('''  return {
    data: entry.data,
    limited: entry.limited || false,
    fresh: age < cfg.ttl,    // Within primary TTL — no refetch needed
    stale: age < cfg.staleTtl // Within stale TTL — show immediately, refetch in bg
  };
}

function setCached(tokenKey, tier, data, limited = false) {
  const ck = `${tokenKey}_${tier}`;
  cache[ck] = { data, tier, ts: Date.now(), limited };
}''','''  const fallback = !!(entry.limited || entry.coarse);   // 2026-10-05: a 2-point / daily stand-in is shown at once but never "fresh" — the next load asks GeckoTerminal again
  return {
    data: entry.data,
    limited: entry.limited || false,
    coarse: entry.coarse || false,
    fresh: age < cfg.ttl && !fallback,    // Within primary TTL — no refetch needed
    stale: age < cfg.staleTtl // Within stale TTL — show immediately, refetch in bg
  };
}

function setCached(tokenKey, tier, data, limited = false, coarse = false) {
  const ck = `${tokenKey}_${tier}`;
  cache[ck] = { data, tier, ts: Date.now(), limited, coarse };
}''')
# applyTokenData carries the flag; the stale-while-revalidate path and the two live paths pass it
rep('''  const filtered = filterToRange(clampToTokenStart(k, data), days);
  if (filtered && filtered.length >= 2) {
    TOKENS[k]._data = filtered;
    TOKENS[k]._limited = limited;
    return true;
  }''','''  const filtered = filterToRange(clampToTokenStart(k, data), days);
  if (filtered && filtered.length >= 2) {
    TOKENS[k]._data = filtered;
    TOKENS[k]._limited = limited;
    TOKENS[k]._coarse = !!coarse;   // daily closes standing in for hourly candles (2026-10-05)
    return true;
  }''')
import re
s,n=re.subn(r'function applyTokenData\(k, data, limited, days\)','function applyTokenData(k, data, limited, days, coarse = false)',s); assert n==1,n
rep('        applyTokenData(k, cached.data, cached.limited, days);\n        anyStaleShown = true;','        applyTokenData(k, cached.data, cached.limited, days, cached.coarse);\n        anyStaleShown = true;')
rep("        delete t._data; delete t._limited; delete t._carried;","        delete t._data; delete t._limited; delete t._carried; delete t._coarse;")
# the status line + the card badge say so
rep('''  const limited = Object.entries(TOKENS).filter(([k, t]) => t.on && t._limited).map(([k]) => k);
  const carried =''','''  const limited = Object.entries(TOKENS).filter(([k, t]) => t.on && t._limited).map(([k]) => k);
  const coarse = Object.entries(TOKENS).filter(([k, t]) => t.on && t._coarse && !t._limited).map(([k]) => k);
  const carried =''')
rep('''    if (limited.length) msg += ` \\u00B7 <span style="color:#eab308">${limited.join(', ')} limited data</span>`;''',
    '''    if (limited.length) msg += ` \\u00B7 <span style="color:#eab308">${limited.join(', ')} limited data</span>`;
    if (coarse.length) msg += ` \\u00B7 <span style="color:#eab308">${coarse.join(', ')} daily candles</span>`;''')
rep("const item = { sym: t.sym, color: t.color, logo: t.logo, pct, ps: fmtCardPrice(pN), limited: !!t._limited, spark: sparkSample(d) };",
    "const item = { sym: t.sym, color: t.color, logo: t.logo, pct, ps: fmtCardPrice(pN), limited: !!t._limited, coarse: !!t._coarse, spark: sparkSample(d) };")
rep("const limitedBadge = it.limited ? '<span class=\"card-limited\">24H ONLY</span>' : '';",
    "const limitedBadge = it.limited ? '<span class=\"card-limited\">24H ONLY</span>' : it.coarse ? '<span class=\"card-limited\">DAILY</span>' : '';")
p.write_text(s); print('applied',len(s))
