#!/usr/bin/env python3
"""Charts page — loading speed (2026-10-06, Shaka: "figure out how we can get the chart to load better and faster when people
switch through the different time periods. It sometimes says it can't get HEX… and sometimes takes too long"). Two causes, read
from the code: (a) 24H / 7D / 14D were drawn ONLY from live GeckoTerminal calls — one gated call per token, 2.2 s apart, 4 s / 8 s
pauses on a refusal, so eight tokens meant 20–40 s with nothing on the canvas, and a refused token fell to the daily file or to
"unavailable"; (b) a range or token click while a load was in flight QUEUED behind it (`pendingGo`) — the new range appeared only
after the old load's last gated call. Three changes:
  1. a prebuilt INTRADAY file — scripts/build-charts-intraday.js (CoinGecko Pro, hourly step of data-pipeline.yml) writes
     data/charts-intraday.json: 14 d of hourly closes and 24 h of 15-min closes for every token. The page paints the range from
     it at once and asks GeckoTerminal / CoinGecko only to top it up (skipped when the file reaches within 1.5 candles of now, or
     a top-up for that token + tier ran in the last 3 min); a refused top-up leaves the file's line (amber "as of" past 2 h).
     Missing / stale file (> 36 h) → the old path, unchanged;
  2. a new load supersedes the one in flight: aborted fetches, the old cycle's finally only tidies if it is still the newest;
  3. the GeckoTerminal gate gives no 2.2 s slot to an aborted call.
Run after tools/charts-v3.py: python3 tools/charts-fast.py (refuses to run twice)."""
import sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
p=root/'charts.html'; s=p.read_text()
if 'STATIC_INTRADAY_URL' in s: sys.exit('already applied')
def rep(old,new,count=1):
    global s
    n=s.count(old); assert n==count,(old[:80],n); s=s.replace(old,new)

# 1a. the loader, after the daily file's
rep('''const dexLogo = a => `https://dd.dexscreener.com/ds-data/tokens/pulsechain/${a.toLowerCase()}.png`;
''','''/* ── Static INTRADAY series (server-side prebuilt, 2026-10-06) ───────────────────────
   data/charts-intraday.json — scripts/build-charts-intraday.js (hourly step): 14 d of 1-hour closes
   (the 7D / 14D ranges) and 24 h of 15-minute closes (24H) for every token. go() paints a range from
   it AT ONCE and asks GeckoTerminal / CoinGecko only to top it up with the candles since the file was
   written; when they refuse, the file's line stands (an honest amber "as of" past 2 h) instead of a
   long wait, a "daily candles" stand-in or "unavailable". Missing or stale file → the old path. */
const STATIC_INTRADAY_URL = 'https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/charts-intraday.json';
const INTRADAY_MAX_AGE_MS = 36 * 3600000;   // older = the pipeline has stopped; ignore the file
const TIER_STEP_MS = { minute: 900000, hourly: 3600000, daily: 86400000 };
let _staticIntradayPromise = null, _staticIntradayKey = null;
async function loadStaticIntraday() {
  const key = Math.floor(Date.now() / 300000);   // raw.githubusercontent caches ~5 min — one fetch per 5-min slot, shared by every load
  if (_staticIntradayPromise && _staticIntradayKey === key) return _staticIntradayPromise;
  _staticIntradayKey = key;
  _staticIntradayPromise = (async () => {
    const r = await fetch(`${STATIC_INTRADAY_URL}?t=${key}`);
    if (!r.ok) throw new Error(`static intraday HTTP ${r.status}`);
    const json = await r.json();
    const age = Date.now() - Date.parse((json && json.lastUpdated) || 0);
    console.log('Static intraday series loaded:', json && json.lastUpdated, `(${Math.round(age / 60000)} min old) —`, Object.keys((json && json.tokens) || {}).length, 'tokens');
    if (!(age < INTRADAY_MAX_AGE_MS)) throw new Error(`static intraday file is ${Math.round(age / 3600000)} h old — ignored`);
    return json;
  })();
  _staticIntradayPromise.catch(() => { if (_staticIntradayKey === key) { _staticIntradayPromise = null; _staticIntradayKey = null; } });
  return _staticIntradayPromise;
}
function getStaticIntradaySeries(json, sym, tier) {
  const t = json && json.tokens && json.tokens[sym] && json.tokens[sym][tier];
  if (!t || !Array.isArray(t.series) || t.series.length < 2) return null;
  return t.series.map(p => ({ ts: p[0], price: p[1] }));
}
/* The file's series + the live candles since it — one point per candle of the tier, live wins. */
function mergeSeries(base, live, step) {
  if (!base || !base.length) return live;
  if (!live || !live.length) return base;
  const m = new Map(), q = step || 60000;
  base.forEach(d => m.set(Math.floor(d.ts / q), d));
  live.forEach(d => m.set(Math.floor(d.ts / q), d));
  return [...m.values()].sort((a, b) => a.ts - b.ts);
}
let _statusUpdating = false;   // the chart is painted (file / cache) and a live top-up is running — the status line says so instead of "Loading…"
const _liveTried = {};   // `${k}_${tier}` → when a live top-up last ran; a line painted from the file is not topped up again within 3 min

const dexLogo = a => `https://dd.dexscreener.com/ds-data/tokens/pulsechain/${a.toLowerCase()}.png`;
''')

# 2. a new load supersedes the one in flight
rep('''async function go() {
  if (isRefreshing) { pendingGo = true; return; }
  isRefreshing = true;
  fetchGeneration++;
  const currentGen = fetchGeneration;
''','''async function go() {
  /* 2026-10-06: a new load SUPERSEDES one in flight. A range or token click used to queue behind the running load
     (`pendingGo`) — the new range appeared only after the old load's last gated GeckoTerminal call. Now the old cycle's
     fetches are aborted, its awaits see the generation move and stop, and its finally only tidies up if it is still the
     newest cycle. */
  isRefreshing = true;
  pendingGo = false;
  _statusUpdating = false;
  fetchGeneration++;
  const currentGen = fetchGeneration;
''')
rep('''  const days = getDays();
  const tier = getTier(days);
  const ld = document.getElementById('loadOverlay');
  const rb = document.getElementById('refreshBtn');
''','''  const days = getDays();
  const tier = getTier(days);
  const ld = document.getElementById('loadOverlay');
  const rb = document.getElementById('refreshBtn');
  Object.values(TOKENS).forEach(t => { delete t._file; });   // the intraday file's series for THIS tier only (phase 0.5)
''')
rep('''    if (anyStaleShown) {
      renderChart(); renderSummary(); updateStatusLine(); updatePeriod();
    }

    if (needFetch.length === 0) {
      return; // finally block handles cleanup
    }
''','''    if (anyStaleShown) {
      renderChart(); renderSummary(); updateStatusLine(); updatePeriod();
    }

    /* ── PHASE 0.5: the prebuilt intraday file (2026-10-06) ──────────────────────────────
       24H / 7D / 14D paint from data/charts-intraday.json at once. A token whose file series reaches
       within 1.5 candles of now needs no live call; one topped up in the last 3 min is left as painted;
       the rest keep their place in needFetch and the live candles since the file top them up below. */
    if (tier !== 'daily' && needFetch.length) {
      let json = null;
      try { json = await loadStaticIntraday(); } catch (e) { console.warn('Static intraday unavailable — live path:', e.message); }
      if (currentGen !== fetchGeneration) return;
      if (json) {
        const step = TIER_STEP_MS[tier];
        let painted = false;
        needFetch = needFetch.filter(([k, t]) => {
          const series = getStaticIntradaySeries(json, k, tier);
          if (!series) return true;
          t._file = series;
          const shown = (t._data && t._data.length >= 2 && !t._limited && !t._coarse) ? t._data[t._data.length - 1].ts : 0;
          const newest = series[series.length - 1].ts;
          if (newest >= shown && applyTokenData(k, series, false, days)) { painted = true; t._carried = false; }
          const fileFresh = Date.now() - newest < step * 1.5;
          const triedRecently = (_liveTried[`${k}_${tier}`] || 0) > Date.now() - 180000;
          if (fileFresh) setCached(k, tier, series, false);
          if (fileFresh || triedRecently) return false;
          _liveTried[`${k}_${tier}`] = Date.now();
          return true;
        });
        if (painted) { renderChart(); renderSummary(); updateStatusLine(); updatePeriod(); }
      }
    }

    if (needFetch.length === 0) {
      _statusFromCache = false; updateStatusLine(); updatePeriod();
      return; // finally block handles cleanup
    }
''')
rep('''    rb.classList.add('spinning');
    setStatus('<span class="dot spin"></span>Loading ' + needFetch.length + ' token' + (needFetch.length > 1 ? 's' : '') + '...');
''','''    rb.classList.add('spinning');
    const allPainted = needFetch.every(([k, t]) => t._data && t._data.length >= 2);   // 2026-10-06: the file / cache drew every line — say "updating", not "Loading"
    if (allPainted) { _statusUpdating = true; updateStatusLine(); }
    else setStatus('<span class="dot spin"></span>Loading ' + needFetch.length + ' token' + (needFetch.length > 1 ? 's' : '') + '...');
''')
rep('''    function progress(sym) {
      completed++;
      if (!hasAnyData) setLoadMsg(`${sym}... (${completed}/${total})`);
      setStatus(`<span class="dot spin"></span>Loading... ${completed}/${total}`);
    }''','''    function progress(sym) {
      if (currentGen !== fetchGeneration) return;
      completed++;
      if (!hasAnyData) setLoadMsg(`${sym}... (${completed}/${total})`);
      if (allPainted) updateStatusLine();
      else setStatus(`<span class="dot spin"></span>Loading... ${completed}/${total}`);
    }''')
rep('''    if (currentGen === fetchGeneration) {
      _statusFromCache = false;   // a37: the refetch landed (or nothing needed fetching) — no longer "Cached"
      updateStatusLine();''','''    if (currentGen === fetchGeneration) {
      _statusFromCache = false;   // a37: the refetch landed (or nothing needed fetching) — no longer "Cached"
      _statusUpdating = false;
      updateStatusLine();''')
rep('''    if (carried.length) msg += ` \\u00B7 <span style="color:#eab308">${carried.join(', ')} carried forward (builder could not refresh)</span>`;
    setStatus(msg);''','''    if (carried.length) msg += ` \\u00B7 <span style="color:#eab308">${carried.join(', ')} carried forward (builder could not refresh)</span>`;
    if (_statusUpdating) msg += ` \\u00B7 <span class="dot spin"></span><span style="color:rgba(255,255,255,0.45)">updating</span>`;
    setStatus(msg);''')
rep('''          const data = await fetchMoralisUnified(t, tier, k, signal);
          if (data && data.length >= 2 && currentGen === fetchGeneration) {
            setCached(k, tier, data, false);
            applyTokenData(k, data, false, days);
            ld.style.display = 'none';
            renderChart(); renderSummary();
          }
        } catch (e) { if (e.name !== 'AbortError') console.warn(`Moralis fetch failed for ${k}:`, e); }''',
'''          const live = await fetchMoralisUnified(t, tier, k, signal);
          if (live && live.length >= 2 && currentGen === fetchGeneration) {
            const data = mergeSeries(t._file, live, TIER_STEP_MS[tier]);   // the file's older candles + the live ones since it
            setCached(k, tier, data, false);
            applyTokenData(k, data, false, days);
            ld.style.display = 'none';
            renderChart(); renderSummary();
          }
        } catch (e) { if (e.name !== 'AbortError') console.warn(`Moralis fetch failed for ${k}:`, e); }''')
rep('''          const data = await fetchMajorUnified(t, tier, k, signal);
          if (data && data.length >= 2 && currentGen === fetchGeneration) {
            setCached(k, tier, data, false);
            applyTokenData(k, data, false, days);
            ld.style.display = 'none';
            renderChart(); renderSummary();
          }
        } catch (e) { if (e.name !== 'AbortError') console.warn(`CC fetch failed for ${k}:`, e); }''',
'''          const live = await fetchMajorUnified(t, tier, k, signal);
          if (live && live.length >= 2 && currentGen === fetchGeneration) {
            const data = mergeSeries(t._file, live, TIER_STEP_MS[tier]);
            setCached(k, tier, data, false);
            applyTokenData(k, data, false, days);
            ld.style.display = 'none';
            renderChart(); renderSummary();
          }
        } catch (e) { if (e.name !== 'AbortError') console.warn(`CC fetch failed for ${k}:`, e); }''')
rep('''  } finally {
    // ALWAYS clean up — this can never get stuck
    ld.style.display = 'none';
    rb.classList.remove('spinning');
    isRefreshing = false;
    clearTimeout(_watchdogTimer);

    if (pendingGo) { pendingGo = false; go(); }
  }
}''','''  } finally {
    // ALWAYS clean up — this can never get stuck. A superseded cycle leaves the newest one's overlay,
    // spinner and watchdog alone (2026-10-06).
    if (currentGen === fetchGeneration) {
      ld.style.display = 'none';
      rb.classList.remove('spinning');
      isRefreshing = false;
      clearTimeout(_watchdogTimer);
      if (pendingGo) { pendingGo = false; go(); }
    }
  }
}''')

# 3. the gate gives no slot to an aborted call
rep('''function gtGate() {
  const p = _gtChain.then(async () => {
    const pause = _gtPauseUntil - Date.now();''','''function gtGate(signal) {
  const p = _gtChain.then(async () => {
    if (signal && signal.aborted) return;   // 2026-10-06: a superseded load's calls take no 2.2 s slot
    const pause = _gtPauseUntil - Date.now();''')
rep('''      await gtGate();
      if (signal && signal.aborted) return null;
      r = await fetchRetry(url, 1, 2000, signal, { 'accept': 'application/json' });''',
'''      await gtGate(signal);
      if (signal && signal.aborted) return null;
      r = await fetchRetry(url, 1, 2000, signal, { 'accept': 'application/json' });''')
rep('''    await gtGate();
    const r = await fetchRetry(url, 2, 2000, signal, { accept: 'application/json' });''',
'''    await gtGate(signal);
    const r = await fetchRetry(url, 2, 2000, signal, { accept: 'application/json' });''')

# Refresh re-reads the file and goes live again
rep('''  Object.values(TOKENS).forEach(t => { delete t._data; delete t._limited });
  go();
}''','''  Object.values(TOKENS).forEach(t => { delete t._data; delete t._limited; delete t._coarse; delete t._file; });
  _staticIntradayPromise = null; _staticIntradayKey = null;   // 2026-10-06: Refresh re-reads the intraday file and tops up live again
  Object.keys(_liveTried).forEach(k => delete _liveTried[k]);
  go();
}''')
p.write_text(s); print('edited charts.html')
