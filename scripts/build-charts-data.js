#!/usr/bin/env node
/* ──────────────────────────────────────────────────────────────────────────
   build-charts-data.js  —  standalone daily-series builder for charts.html
   ----------------------------------------------------------------------------
   Fetches a full YEAR of DAILY price history for each PulseChain chart token
   from the CoinGecko Pro on-chain (DEX) API — server-side, authenticated, with
   no browser CORS limits and no anonymous 30/min rate cap. Writes the result to
   data/charts-data.json, which charts.html reads for the 1M/3M/6M/1Y ranges.

   Why this exists: the browser was calling GeckoTerminal anonymously for long
   ranges. Past ~30 req/min those calls 429 *without* CORS headers, so the page
   sees CORS failures and the charts break. CoinGecko's on-chain data IS
   GeckoTerminal's data (same company) — but with your Pro key it has a real rate
   budget and runs fine from a server. This script is the server.

   This is ADDITIVE. It does not touch fetch-coingecko-data.js or any existing
   data file. If it ever misbehaves, the main dashboard is unaffected.

   Requires: Node 18+ (global fetch). Secret: COINGECKO_API_KEY (already set).
   ────────────────────────────────────────────────────────────────────────── */

'use strict';

const fs = require('fs');
const path = require('path');

const API_KEY = process.env.COINGECKO_API_KEY;
const PRO_BASE = 'https://pro-api.coingecko.com/api/v3';
const NETWORK = 'pulsechain';          // CoinGecko on-chain network id (mirrors GeckoTerminal)
const RANGE_DAYS = 365;                 // we want a full year
const OUT_PATH = path.join(__dirname, '..', 'data', 'charts-data.json');

/* Tokens to build daily series for. Addresses are the TOKEN contract addresses
   (dexAddr in charts.html). pairAddr, where known, is a specific pool we also
   try as a candidate. Everything here is already in your charts.html config. */
const TOKENS = [
  { sym: 'PTGC', addr: '0x94534EeEe131840b1c0F61847c572228bdfDDE93', pair: '0xf5A89A6487D62df5308CDDA89c566C5B5ef94C11' },
  { sym: 'UFO',  addr: '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018', pair: '0xbeA0e55b82Eb975280041F3b49C4D0bD937b72d5' },
  { sym: 'WPLS', addr: '0xA1077a294dDE1B09bB078844df40758a5D0f9a27', pair: null },
  { sym: 'PLSX', addr: '0x95B303987A60C71504D99Aa1b13B4DA07b0790ab', pair: '0x1b45b9148791d3a104184Cd5DFE5CE57193a3ee9' },
  { sym: 'HEX',  addr: '0x2b591e99afE9f32eAA6214f7B7629768c40Eeb39', pair: '0xf1F4ee610b2bAbB05C635F726eF8B0C568c8dc65' },
  { sym: 'EHEX', addr: '0x57fde0a71132198BBeC939B98976993d8D89D225', pair: '0x55D5c232D921B9eAA6b37b5845E439aCD04b4DBa' },
  { sym: 'INC',  addr: '0x2fa878Ab3F87CC1C9737Fc071108F904c0B0C95d', pair: '0xf808Bb6265e9Ca27002c0A04562Bf50d4FE37EAA' },
  { sym: 'PRVX', addr: '0xF6f8Db0aBa00007681F8fAF16A0FDa1c9B030b11', pair: null },
];

const REQUEST_TIMEOUT_MS = 20000;       // never let a hung socket stall the job
const BETWEEN_CALLS_MS = 300;           // gentle spacing (Pro key has plenty of headroom)
const MAX_PAGES = 6;                    // 6 × ~180d ≈ 3yr of backward headroom
const MIN_RESERVE_USD = 500;            // ignore dust pools when picking candidates

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

if (!API_KEY) {
  console.error('FATAL: COINGECKO_API_KEY is not set. Add it as a repo secret.');
  process.exit(1);
}

/* ---- HTTP with timeout + light retry ---------------------------------- */
async function apiGet(urlPath, attempt = 0) {
  const url = `${PRO_BASE}${urlPath}`;
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), REQUEST_TIMEOUT_MS);
  try {
    const r = await fetch(url, {
      signal: ctrl.signal,
      headers: { 'x-cg-pro-api-key': API_KEY, accept: 'application/json' },
    });
    if (r.status === 429 && attempt < 3) {
      clearTimeout(timer);
      const wait = 2000 * (attempt + 1);
      console.warn(`  429 rate-limited, backing off ${wait}ms…`);
      await sleep(wait);
      return apiGet(urlPath, attempt + 1);
    }
    if (!r.ok) {
      const body = await r.text().catch(() => '');
      throw new Error(`HTTP ${r.status} for ${urlPath} :: ${body.slice(0, 200)}`);
    }
    return await r.json();
  } catch (e) {
    if ((e.name === 'AbortError' || /network|fetch/i.test(e.message)) && attempt < 2) {
      console.warn(`  request error (${e.message}); retry ${attempt + 1}…`);
      await sleep(1500 * (attempt + 1));
      return apiGet(urlPath, attempt + 1);
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

/* ---- Preflight: confirm the network id is right ----------------------- */
async function preflight() {
  try {
    await apiGet(`/onchain/networks/${NETWORK}/pools?page=1`);
    console.log(`Preflight OK — network "${NETWORK}" is valid on CoinGecko on-chain.`);
    return true;
  } catch (e) {
    console.error(`Preflight FAILED for network "${NETWORK}": ${e.message}`);
    console.error('If this is a "network not found"-type error, the on-chain id may differ.');
    console.error('List valid ids with: GET /onchain/networks  (look for PulseChain).');
    return false;
  }
}

/* ---- Candidate pools for a token -------------------------------------- */
// Returns [{ pool, side, created, reserve }] — deepest history + best liquidity first.
async function candidatePools(token) {
  const out = [];
  if (token.pair) out.push({ pool: token.pair.toLowerCase(), side: null, created: Infinity, reserve: Infinity });
  try {
    const j = await apiGet(`/onchain/networks/${NETWORK}/tokens/${token.addr}/pools`);
    const key = token.addr.toLowerCase();
    const pools = (j && j.data ? j.data : [])
      .map((p) => {
        const a = (p && p.attributes) || {};
        const rel = (p && p.relationships) || {};
        const baseId = ((rel.base_token && rel.base_token.data && rel.base_token.data.id) || '').toLowerCase();
        return {
          pool: (a.address || '').toLowerCase(),
          side: baseId.endsWith(key) ? 'base' : 'quote',
          created: a.pool_created_at ? Date.parse(a.pool_created_at) : Infinity,
          reserve: parseFloat(a.reserve_in_usd || '0'),
        };
      })
      .filter((p) => p.pool && p.reserve >= MIN_RESERVE_USD);

    // Earliest-created liquid pool (deepest history) — the one we most want.
    const byAge = [...pools].sort((x, y) => x.created - y.created);
    if (byAge[0]) out.push(byAge[0]);
    // Highest-liquidity pool (best price accuracy) as a second candidate.
    const byLiq = [...pools].sort((x, y) => y.reserve - x.reserve);
    if (byLiq[0]) out.push(byLiq[0]);
  } catch (e) {
    console.warn(`  pool lookup failed for ${token.sym}: ${e.message}`);
  }
  // De-dup by pool address, keep first occurrence (priority order above).
  const seen = new Set();
  return out.filter((p) => (seen.has(p.pool) ? false : (seen.add(p.pool), true)));
}

/* ---- Page daily OHLCV backward to RANGE_DAYS -------------------------- */
// kind: 'pool' uses pool endpoint (+token=side); 'token' uses the paid
// token-address endpoint (auto-selects the most liquid pool, side handled for us).
async function fetchDaily(kind, idOrPool, side) {
  const targetFromSec = Math.floor((Date.now() - RANGE_DAYS * 86400000) / 1000);
  let before = Math.floor(Date.now() / 1000) + 60;
  let oldest = Infinity;
  const rows = [];

  for (let page = 0; page < MAX_PAGES; page++) {
    const base =
      kind === 'pool'
        ? `/onchain/networks/${NETWORK}/pools/${idOrPool}/ohlcv/day`
        : `/onchain/networks/${NETWORK}/tokens/${idOrPool}/ohlcv/day`;
    const q =
      `?aggregate=1&before_timestamp=${before}&limit=1000&currency=usd` +
      (kind === 'pool' && side ? `&token=${side}` : '');

    let j;
    try { j = await apiGet(base + q); }
    catch (e) { console.warn(`  ohlcv page ${page} failed: ${e.message}`); break; }

    const list = (j && j.data && j.data.attributes && j.data.attributes.ohlcv_list) || [];
    if (!list.length) break;

    let pageOldest = Infinity;
    for (const c of list) {            // c = [tsSec, open, high, low, close, volume]
      const ts = c[0], price = parseFloat(c[4]);
      if (ts && price > 0) rows.push([ts * 1000, price]);
      if (ts < pageOldest) pageOldest = ts;
    }
    if (!isFinite(pageOldest)) break;
    if (pageOldest <= targetFromSec) break;   // reached a full year
    if (pageOldest >= oldest) break;          // no backward progress — out of history
    oldest = pageOldest;
    before = pageOldest;                      // step further back
    await sleep(BETWEEN_CALLS_MS);
  }
  return rows;
}

/* ---- Clean: positive, de-duped per day, sorted, no stablecoin pairs --- */
function clean(rows) {
  if (!rows || rows.length < 2) return null;
  const cutoff = Date.now() - (RANGE_DAYS + 2) * 86400000;
  const seen = new Set();
  const out = [];
  for (const [ts, price] of rows.sort((a, b) => a[0] - b[0])) {
    if (!(price > 0) || ts < cutoff) continue;
    const dayKey = Math.round(ts / 86400000);
    if (seen.has(dayKey)) continue;
    seen.add(dayKey);
    out.push([ts, price]);
  }
  if (out.length < 2) return null;
  // Discard obvious stablecoin-pair mistakes (all prices ~$1).
  if (out.every(([, p]) => p > 0.95 && p < 1.05)) return null;
  return out;
}

function spanDays(series) {
  return series && series.length >= 2
    ? Math.round((series[series.length - 1][0] - series[0][0]) / 86400000)
    : 0;
}

/* ---- Build one token: try candidates, keep the longest clean series --- */
async function buildToken(token) {
  console.log(`\n${token.sym} (${token.addr})`);
  const attempts = [];

  // 1) Paid token-address endpoint (auto most-liquid pool, side handled).
  try {
    const r = clean(await fetchDaily('token', token.addr));
    if (r) attempts.push({ series: r, pool: 'auto(token-address)' });
  } catch (e) { console.warn(`  token-address ohlcv failed: ${e.message}`); }
  await sleep(BETWEEN_CALLS_MS);

  // 2) Specific pools (configured pair + deepest-history + highest-liquidity).
  const pools = await candidatePools(token);
  for (const p of pools) {
    await sleep(BETWEEN_CALLS_MS);
    try {
      // If side unknown (configured pair), try base then quote; keep the non-$1 one.
      const sides = p.side ? [p.side] : ['base', 'quote'];
      for (const side of sides) {
        const r = clean(await fetchDaily('pool', p.pool, side));
        if (r) { attempts.push({ series: r, pool: `${p.pool} (${side})` }); break; }
      }
    } catch (e) { console.warn(`  pool ${p.pool} failed: ${e.message}`); }
  }

  if (!attempts.length) { console.warn(`  ✗ no usable series for ${token.sym}`); return null; }

  // Winner = longest day-span, then most points.
  attempts.sort((a, b) => spanDays(b.series) - spanDays(a.series) || b.series.length - a.series.length);
  const win = attempts[0];
  const s = win.series;
  const first = new Date(s[0][0]).toISOString().slice(0, 10);
  const last = new Date(s[s.length - 1][0]).toISOString().slice(0, 10);
  console.log(`  ✓ ${s.length} candles, span ${spanDays(s)}d (${first} → ${last}) via ${win.pool}`);
  return { source: 'coingecko', pool: win.pool, points: s.length, span: spanDays(s), series: s };
}

/* ---- Main ------------------------------------------------------------- */
(async () => {
  console.log(`Building charts-data.json — ${RANGE_DAYS}d daily series, network "${NETWORK}"`);
  const ok = await preflight();
  if (!ok) process.exit(1);

  const tokens = {};
  for (const t of TOKENS) {
    try {
      const built = await buildToken(t);
      if (built) tokens[t.sym] = built;
    } catch (e) {
      console.warn(`  unexpected error for ${t.sym}: ${e.message}`);
    }
    await sleep(BETWEEN_CALLS_MS);
  }

  const built = Object.keys(tokens).length;
  if (built === 0) {
    console.error('FATAL: produced 0 token series — not writing file.');
    process.exit(1);
  }

  const payload = {
    lastUpdated: new Date().toISOString(),
    rangeDays: RANGE_DAYS,
    generatedBy: 'build-charts-data.js (CoinGecko Pro on-chain, server-side)',
    network: NETWORK,
    tokens,
  };

  fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
  fs.writeFileSync(OUT_PATH, JSON.stringify(payload));
  console.log(`\nWrote ${OUT_PATH} — ${built}/${TOKENS.length} tokens, ${(fs.statSync(OUT_PATH).size / 1024).toFixed(1)} KB`);
})().catch((e) => {
  console.error('FATAL:', e);
  process.exit(1);
});
