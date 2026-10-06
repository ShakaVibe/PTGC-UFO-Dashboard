// build-pair-volume.mjs — data/pair-volume-7d.json: every PTGC and UFO pool's trading volume over the last
// 7 days in 28 six-hour bins, from GeckoTerminal's hourly candles, fetched HERE (one place, ~1 call/s) instead
// of by every visitor's browser.
//
// Why (2026-09-30, the LP Pairs table under v2): the browser read one pool at a time from GeckoTerminal —
// first it was refused as a burst, then its SPARSE candles (only the hours that traded) were misread, and even
// done right it is 20+ calls per visitor, i.e. 20 s of empty rows on a cold cache. Shaka: "it's not like they
// have to be super live and accurate". So the pipeline writes one small file (~6 KB) and index.html
// (`useLpVolSeries`) reads it first; the live per-pool read stays only as the fallback for a pool this file
// does not have (a brand-new pair) or a file older than PAIR_VOL_MAX_AGE (36 h).
//
// Honest-failure rules (a61): a pool GeckoTerminal does not list (404) is `null` — the table draws it dashed;
// a pool it REFUSED this run (429 / 5xx / timeout after the retries) is carried from the previous file with
// `carried: <generatedAt>` and otherwise left out (the browser then reads it live); a throw exits non-zero so the
// pipeline's "Report step failures" step goes red. A pool with candles but no trade in the week is a real row
// of zeros (the table draws the floor line) — never a guessed shape.
//
// 2026-10-06: with COINGECKO_API_KEY set (the pipeline's secret) the candles come from CoinGecko Pro's on-chain
// API — the same data as GeckoTerminal (CoinGecko owns it), served fast and keyed: ~1.5 min for 47 pools instead of
// 9 (GeckoTerminal answered GitHub's runners in ~10 s per pool). Without the key: GeckoTerminal, as before.
//
// Local run (Node 22): NODE_USE_ENV_PROXY=1 node scripts/build-pair-volume.mjs   (OUT_PATH= to write elsewhere)
import fs from 'node:fs';

const OUT = process.env.OUT_PATH || 'data/pair-volume-7d.json';
const TOKENS = {
  PTGC: '0x94534EeEe131840b1c0F61847c572228bdfDDE93',
  UFO:  '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6',   // the LIVE contract (post-migration)
};
const MIN_LIQ = 1000;              // index.html's MIN_LIQ: the rows shown by default; the under-$1K rows come too, up to the cap
const MAX_POOLS_PER_TOKEN = 45;
const CG_KEY = process.env.COINGECKO_API_KEY || '';
const GAP_MS = Number(process.env.GAP_MS || (CG_KEY ? 1500 : 1200));   // GeckoTerminal free tier: ~30 calls/min; the Pro key is paced like the sibling scripts
const OHLCV_BASE = CG_KEY
  ? 'https://pro-api.coingecko.com/api/v3/onchain/networks/pulsechain/pools/'
  : 'https://api.geckoterminal.com/api/v2/networks/pulsechain/pools/';
const BIN_MS = 6 * 3600 * 1000, BINS = 28;   // 7 days
const UA = 'grays-dashboard-pipeline/1.0 (+https://ptgc-ufo.com)';

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function getJson(url, tries = 3) {
  for (let a = 0; a < tries; a++) {
    try {
      const headers = { accept: 'application/json', 'user-agent': UA };
      if (CG_KEY && url.startsWith(OHLCV_BASE)) headers['x-cg-pro-api-key'] = CG_KEY;
      const r = await fetch(url, { headers, signal: AbortSignal.timeout(20000) });
      if (r.status === 429 || r.status >= 500) { console.log(`  ${r.status} from ${url.slice(0, 90)} — waiting`); await sleep(5000 * (a + 1)); continue; }
      if (r.status === 404) return { status: 404 };
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      return { status: 200, json: await r.json() };
    } catch (e) {
      if (a === tries - 1) return { status: 0, error: String(e && e.message || e) };
      await sleep(3000);
    }
  }
  return { status: 0, error: 'refused' };
}

async function poolsFor(token, addr) {
  const { status, json, error } = await getJson(`https://api.dexscreener.com/latest/dex/tokens/${addr}`);
  if (status !== 200 || !json || !Array.isArray(json.pairs)) throw new Error(`DexScreener pairs for ${token}: ${error || status}`);
  const ps = json.pairs.filter(p => p.chainId === 'pulsechain' && /^0x[0-9a-fA-F]{40}$/.test(p.pairAddress || ''));
  const liq = p => (p.liquidity && p.liquidity.usd) || 0, vol = p => (p.volume && p.volume.h24) || 0;
  // the default rows (≥ $1K liquidity) first, by volume; then the under-$1K rows by volume, up to the cap
  const high = ps.filter(p => liq(p) >= MIN_LIQ).sort((a, b) => vol(b) - vol(a));
  const low  = ps.filter(p => liq(p) <  MIN_LIQ).sort((a, b) => vol(b) - vol(a));
  return high.concat(low).slice(0, MAX_POOLS_PER_TOKEN).map(p => ({ token, addr: p.pairAddress.toLowerCase(), name: `${p.baseToken && p.baseToken.symbol}/${p.quoteToken && p.quoteToken.symbol}` }));
}

function binCandles(list, binStart) {
  const v = new Array(BINS).fill(0);
  for (const c of list) {
    const t = Number(c[0]) * 1000, x = parseFloat(c[5]);       // [ts, o, h, l, c, volume_usd]
    if (!Number.isFinite(t) || !Number.isFinite(x) || x < 0) continue;
    const i = Math.floor((t - binStart) / BIN_MS);
    if (i >= 0 && i < BINS) v[i] += x;
  }
  return v.map(x => Math.round(x * 100) / 100);
}

async function main() {
  const t0 = Date.now();
  let prev = null;
  try { prev = JSON.parse(fs.readFileSync(OUT, 'utf8')); } catch (e) { /* first run */ }

  const seen = new Map();
  for (const [token, addr] of Object.entries(TOKENS)) {
    const list = await poolsFor(token, addr);
    for (const p of list) if (!seen.has(p.addr)) seen.set(p.addr, p);   // the PTGC/UFO pool is in both lists
    await sleep(500);
  }
  const pools = [...seen.values()];
  console.log(`candles from ${CG_KEY ? 'CoinGecko Pro (keyed)' : 'GeckoTerminal (keyless)'}, ${GAP_MS} ms apart`);
  console.log(`${pools.length} pools to read (${pools.filter(p => p.token === 'PTGC').length} PTGC, ${pools.filter(p => p.token === 'UFO').length} UFO)`);

  const now = Date.now();
  const binStart = Math.floor((now - 7 * 86400000) / BIN_MS) * BIN_MS;
  const out = {};
  let ok = 0, missing = 0, refused = 0, carried = 0, streak = 0, down = false;
  const carry = (p) => {   // the previous run's bins, shifted onto this run's grid
    const old = prev && prev.pools && prev.pools[p.addr];
    if (!(old && old.v && prev.binStart)) return false;
    const shift = Math.round((binStart - Number(prev.binStart)) / BIN_MS);
    if (shift < 0 || shift >= BINS) return false;
    const v = old.v.slice(shift); while (v.length < BINS) v.push(0);
    out[p.addr] = { n: p.name, v, carried: prev.generatedAt }; carried++; return true;
  };
  for (const p of pools) {
    if (down) { refused++; carry(p); continue; }   // GeckoTerminal is down this run: don't spend 30 × 3 retries on it
    const url = `${OHLCV_BASE}${p.addr}/ohlcv/hour?aggregate=1&limit=168&currency=usd`;
    const { status, json, error } = await getJson(url);
    if (status === 404) { out[p.addr] = null; missing++; streak = 0; }
    else if (status === 200 && json && json.data && json.data.attributes && Array.isArray(json.data.attributes.ohlcv_list)) {
      out[p.addr] = { n: p.name, v: binCandles(json.data.attributes.ohlcv_list, binStart) }; ok++; streak = 0;
    } else {
      refused++;
      const kept = carry(p);
      console.log(`  refused: ${p.name} ${p.addr.slice(0, 10)} (${error || status})${kept ? ' — carried' : ' — left out, the browser reads it live'}`);
      if (++streak >= 3) { down = true; console.log(`  three refusals in a row — ${CG_KEY ? 'CoinGecko' : 'GeckoTerminal'} is down this run; carrying the rest`); }
    }
    await sleep(GAP_MS);
  }

  const file = {
    schema: 1,
    generatedAt: new Date(now).toISOString(),
    source: `${CG_KEY ? 'CoinGecko Pro on-chain' : 'GeckoTerminal'} hourly candles, volume_usd, summed into 6-hour bins`,
    binMs: BIN_MS, bins: BINS, binStart,
    pools: out,
    meta: { pools: pools.length, ok, missing, refused, carried, ms: Date.now() - t0 },
  };
  fs.mkdirSync(OUT.replace(/\/[^/]*$/, ''), { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(file));
  console.log(`wrote ${OUT}: ${ok} read, ${missing} not listed, ${refused} refused (${carried} carried), ${Math.round((Date.now() - t0) / 1000)} s, ${fs.statSync(OUT).size} bytes`);
}

main().catch(e => { console.error('build-pair-volume failed:', e); process.exit(1); });
