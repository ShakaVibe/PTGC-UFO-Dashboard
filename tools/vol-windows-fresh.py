#!/usr/bin/env python3
"""2026-10-20: the Volume window's 7D / 30D / 90D tiles (and Value Generated's 7D / 30D / 90D) went "—" on a tab left open.
Idempotent — run from the repo root:   python3 tools/vol-windows-fresh.py   ("0 edit(s)" = already applied)

Cause: fetchCoingeckoData() kept coingecko-data.json in a module variable for the whole page life and never re-read it, and the
windows were gated on that copy's own lastUpdated being < 12 h old (c17). The pipeline writes the file every hour, but a tab
opened last night judged it by the copy it fetched last night — any load() after that (a token switch, the retry ladder) failed
the gate and blanked all three windows; the 5-min quickRefresh only ever updated the 24 h figure (a52), so nothing recovered
until a full reload. Shaka's screenshot 2026-10-20: 24H $11,128, 7D / 30D / 90D "—", the chart below it fine.

Fix:
  1. fetchCoingeckoData re-reads after 15 min (DATA_FETCH is no-cache → a cheap revalidation); a failed read keeps the last
     good copy instead of returning null.
  2. The gate (window <= token age, monotonic, file < 12 h) moves into one module-scope helper, cgVolWindows(token, d), used by
     load() unchanged in behaviour.
  3. quickRefresh (every 5 min) re-reads the file and re-gates the three windows too, so a long-open tab recovers by itself
     and an outage still reads "—" (a14 / a19: unknown stays unknown, never $0).
"""
import hashlib

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)
def md5(s): return hashlib.md5(s.encode('utf-8')).hexdigest()

class Edit:
    def __init__(self, path):
        self.path = path; self.s = read(path); self.n = 0
    def rep(self, old, new, count=1, done_marker=None):
        if done_marker is not None:
            if done_marker in self.s: return False
        elif new in self.s and old not in self.s:
            return False
        c = self.s.count(old)
        assert c == count, f'{self.path}: expected {count}x anchor, found {c}: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def save(self):
        write(self.path, self.s); print(f'{self.path}: {self.n} edit(s), md5 {md5(self.s)}')

ix = Edit('index.html')

# 1 — the module cache gets a TTL and keeps the last good copy on a failed read
ix.rep("""    const fetchCoingeckoData = async () => {
      if (coingeckoDataCache) return coingeckoDataCache;
      try {
        const r = await fetch(COINGECKO_DATA_URL, DATA_FETCH);
        coingeckoDataCache = await r.json();
        console.log('CoinGecko data loaded:', coingeckoDataCache.lastUpdated);
        return coingeckoDataCache;
      } catch (e) {
        console.error('Failed to load CoinGecko data:', e);
        return null;
      }
    };
""", """    /* 2026-10-20 (tools/vol-windows-fresh.py): re-read after CG_TTL_MS. It used to be read ONCE per page life, so a tab open
       overnight judged the hourly file by last night's copy, failed cgVolWindows' 12 h gate and blanked the 7D / 30D / 90D
       volume windows until a full reload. A failed read keeps the last good copy (the gate still checks its age). */
    let coingeckoFetchedAt = 0;
    const CG_TTL_MS = 15*60*1000;
    const fetchCoingeckoData = async () => {
      if (coingeckoDataCache && Date.now()-coingeckoFetchedAt < CG_TTL_MS) return coingeckoDataCache;
      try {
        const r = await fetch(COINGECKO_DATA_URL, DATA_FETCH);
        if (!r.ok) throw new Error('HTTP '+r.status);
        const j = await r.json();
        coingeckoDataCache = j; coingeckoFetchedAt = Date.now();
        console.log('CoinGecko data loaded:', coingeckoDataCache.lastUpdated);
        return coingeckoDataCache;
      } catch (e) {
        console.error('Failed to load CoinGecko data:', e);
        return coingeckoDataCache;
      }
    };
    /* The 7D / 30D / 90D volume windows for `token` from coingecko-data.json, gated — moved here from load() so the 5-min
       quickRefresh applies the same rules. Coherence guards (roadmap d9; MIGRATION: the repo file was once built for the OLD
       UFO token): (a) the window is not longer than the token's life (DexScreener's oldest pairCreatedAt in `d`), (b) the
       series is monotonic (7d <= 30d <= 90d — a series built for another contract or a broken run fails this), (c) the file
       itself is fresh (< 12 h, c17; it is rebuilt hourly). Anything failing → null → "—", never $0 (a14 / a19). */
    const cgVolWindows = (token, d) => {
      const none = { vol7d: null, vol30d: null, vol90d: null };
      const cg = coingeckoDataCache;
      if (!cg || !cg[token]) return none;
      const fp = d?.pairs?.reduce((m,p)=>(p.pairCreatedAt&&p.pairCreatedAt<m)?p.pairCreatedAt:m, Infinity);
      const ageDays = (fp && isFinite(fp)) ? (Date.now()-fp)/86400000 : null;
      const cgAgeMs = cg.lastUpdated ? (Date.now()-Date.parse(cg.lastUpdated)) : Infinity;
      const cgFresh = isFinite(cgAgeMs) && cgAgeMs < 12*3600*1000;
      const gate = (windowDays, val) => {
        if (!cgFresh) return null;
        if (val == null || !isFinite(val) || val <= 0) return null;
        if (ageDays == null || ageDays < windowDays) return null;  // younger than the window
        return val;
      };
      const cv = cg[token].volume || {};
      let v7 = gate(7, cv.vol7d), v30 = gate(30, cv.vol30d), v90 = gate(90, cv.vol90d);
      const mono = (v7==null||v30==null||v7<=v30*1.001) && (v30==null||v90==null||v30<=v90*1.001) && (v7==null||v90==null||v7<=v90*1.001);
      if (!mono) { console.warn(`${token}: cached volume windows are not monotonic (7d ${v7} / 30d ${v30} / 90d ${v90}); treating as unavailable`); return none; }
      return { vol7d: v7, vol30d: v30, vol90d: v90 };
    };
""")

# 2 — load(): the inline gate → the helper (same rules, same result)
S = ix.s
a = S.find("          const _vFirstPool = d?.pairs?.reduce(")
b_anchor = "            setVolumeByPeriod({ vol24h: v24, vol7d: null, vol30d: null, vol90d: null });\n          }\n"
if a != -1:
    assert S.count("          const _vFirstPool = d?.pairs?.reduce(") == 1
    b = S.find(b_anchor, a); assert b != -1 and S.count(b_anchor) == 1, 'load() volume block drifted'
    ix.s = S[:a] + "          setVolumeByPeriod({ vol24h: v24, ...cgVolWindows(token, d) });   // 2026-10-20: the gate lives in cgVolWindows (quickRefresh uses it too)\n" + S[b+len(b_anchor):]
    ix.n += 1

# 3 — quickRefresh: re-read the file and re-gate the windows every 5 min (after the a52 24 h line)
ix.rep("""          if(d){const nv=(d.vol!=null&&isFinite(d.vol))?d.vol:null;setVolumeByPeriod(v=>(v&&v.vol24h===nv)?v:{...v,vol24h:nv});}
          // No-op guards""", """          if(d){const nv=(d.vol!=null&&isFinite(d.vol))?d.vol:null;setVolumeByPeriod(v=>(v&&v.vol24h===nv)?v:{...v,vol24h:nv});}
          /* 2026-10-20: the 7D / 30D / 90D windows too — they were set only in load(), so a tab that had blanked them (file copy
             past the 12 h gate) never got them back. fetchCoingeckoData re-reads after 15 min; the same gate as load(). */
          if(d){await fetchCoingeckoData();if(tokenRef.current===t){const w=cgVolWindows(t,d);setVolumeByPeriod(v=>(v&&v.vol7d===w.vol7d&&v.vol30d===w.vol30d&&v.vol90d===w.vol90d)?v:{...v,...w});}}
          // No-op guards""")

ix.save()
