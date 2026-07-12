#!/usr/bin/env node
/* ──────────────────────────────────────────────────────────────────────────
   build-charts-data.js  —  standalone daily-series builder for charts.html
   ----------------------------------------------------------------------------
   Fetches a full YEAR of DAILY price history for each PulseChain chart token
   from the CoinGecko Pro on-chain (DEX) API — server-side, authenticated, no
   browser CORS limits, no anonymous rate cap. Writes data/charts-data.json,
   which charts.html reads for the 1M/3M/6M/1Y ranges.

   ADDITIVE & SAFE NEIGHBOR to fetch-coingecko-data.js:
     • Writes a DIFFERENT file (charts-data.json) — no collision.
     • Matches that script's 2000ms call pacing so the shared CoinGecko Pro key
       is never rate-limited, even in the unlikely event the two jobs overlap.
     • On partial failure, carries forward the previous run's series for any
       token that didn't build this time — a bad run never blanks a token.

   Requires: Node 18+ (global fetch). Secret: COINGECKO_API_KEY (already set).
   ────────────────────────────────────────────────────────────────────────── */

'use strict';

const fs = require('fs');
const path = require('path');

const API_KEY = process.env.COINGECKO_API_KEY;
const PRO_BASE = 'https://pro-api.coingecko.com/api/v3';
const NETWORK = 'pulsechain';          // confirmed valid via fetch-coingecko-data.js
const RANGE_DAYS = 365;
const OUT_PATH = path.join(__dirname, '..', 'data', 'charts-data.json');

/* Token CONTRACT addresses (dexAddr in charts.html). pair = a known main pool. */
const TOKENS = [
  { sym: 'PTGC', addr: '0x94534EeEe131840b1c0F61847c572228bdfDDE93', pair: '0xf5A89A6487D62df5308CDDA89c566C5B5ef94C11' },
  { sym: 'UFO',  addr: '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6', pair: '0xE221e6fC30e5787F0d551f980B4da1055D832A03' }, // MIGRATION: new contract + UFO/WPLS pool
  { sym: 'WPLS', addr: '0xA1077a294dDE1B09bB078844df40758a5D0f9a27', pair: null },
  { sym: 'PLSX', addr: '0x95B303987A60C71504D99Aa1b13B4DA07b0790ab', pair: '0x1b45b9148791d3a104184Cd5DFE5CE57193a3ee9' },
  { sym: 'HEX',  addr: '0x2b591e99afE9f32eAA6214f7B7629768c40Eeb39', pair: '0xf1F4ee610b2bAbB05C635F726eF8B0C568c8dc65' },
  { sym: 'EHEX', addr: '0x57fde0a71132198BBeC939B98976993d8D89D225', pair: '0x55D5c232D921B9eAA6b37b5845E439aCD04b4DBa' },
  { sym: 'INC',  addr: '0x2fa878Ab3F87CC1C9737Fc071108F904c0B0C95d', pair: '0xf808Bb6265e9Ca27002c0A04562Bf50d4FE37EAA' },
  { sym: 'PRVX', addr: '0xF6f8Db0aBa00007681F8fAF16A0FDa1c9B030b11', pair: null },
];

/* Global majors — fetched from CoinGecko's coin-market endpoint (not on-chain).
   Same Pro key, same server-side safety. charts.html reads these for the daily
   (1M/3M/6M/1Y) ranges; intraday for majors is fetched live in the browser. */
const MAJORS = [
  { sym: 'BTC', id: 'bitcoin' },
  { sym: 'ETH', id: 'ethereum' },
  { sym: 'SOL', id: 'solana' },
  { sym: 'BNB', id: 'binancecoin' },
  { sym: 'XRP', id: 'ripple' },
];

const REQUEST_TIMEOUT_MS = 20000;   // never let a hung socket stall the job
const CG_DELAY_MS = 2000;           // match fetch-coingecko-data.js — proactive anti-429
const MAX_PAGES = 6;                // 6 × ~180d ≈ 3yr backward headroom
const MIN_RESERVE_USD = 500;        // ignore dust pools

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

if (!API_KEY) {
  console.error('FATAL: COINGECKO_API_KEY is not set.');
  process.exit(1);
}

/* HTTP with proactive delay, timeout, and light retry (mirrors the sibling script) */
async function apiGet(urlPath, attempt = 0) {
  await sleep(CG_DELAY_MS);
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
      console.warn(`  429 rate-limited, waiting 30s (attempt ${attempt + 1})…`);
      await sleep(30000);
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
      return apiGet(urlPath, attempt + 1);
    }
    throw e;
  } finally {
    clearTimeout(timer);
  }
}

async function preflight() {
  try {
    await apiGet(`/onchain/networks/${NETWORK}/pools?page=1`);
    console.log(`Preflight OK — network "${NETWORK}" valid.`);
    return true;
  } catch (e) {
    console.error(`Preflight FAILED for "${NETWORK}": ${e.message}`);
    return false;
  }
}

/* Deepest-history liquid pool for a token (earliest pool_created_at). */
async function deepestPool(token) {
  try {
    const j = await apiGet(`/onchain/networks/${NETWORK}/tokens/${token.addr}/pools?page=1`);
    const key = token.addr.toLowerCase();
    const pools = (j && j.data ? j.data : [])
      .map((p) => {
        const a = (p && p.attributes) || {};
        const rel = (p && p.relationships) || {};
        const baseId = ((rel.base_token && rel.base_token.data && rel.base_token.data.id) || '').toLowerCase();
        return {
          pool: (a.address || (p.id ? p.id.split('_')[1] : '') || '').toLowerCase(),
          side: baseId.endsWith(key) ? 'base' : 'quote',
          created: a.pool_created_at ? Date.parse(a.pool_created_at) : Infinity,
          reserve: parseFloat(a.reserve_in_usd || '0'),
        };
      })
      .filter((p) => p.pool && p.reserve >= MIN_RESERVE_USD)
      .sort((x, y) => x.created - y.created);
    return pools[0] || null;
  } catch (e) {
    console.warn(`  pool lookup failed for ${token.sym}: ${e.message}`);
    return null;
  }
}

/* Page daily OHLCV backward to RANGE_DAYS. kind 'token' = paid auto-pool endpoint. */
async function fetchDaily(kind, idOrPool, side) {
  const targetFromSec = Math.floor((Date.now() - RANGE_DAYS * 86400000) / 1000);
  let before = Math.floor(Date.now() / 1000) + 60;
  let oldest = Infinity;
  const rows = [];
  for (let page = 0; page < MAX_PAGES; page++) {
    const base = kind === 'pool'
      ? `/onchain/networks/${NETWORK}/pools/${idOrPool}/ohlcv/day`
      : `/onchain/networks/${NETWORK}/tokens/${idOrPool}/ohlcv/day`;
    const q = `?aggregate=1&before_timestamp=${before}&limit=1000&currency=usd` +
      (kind === 'pool' && side ? `&token=${side}` : '');
    let j;
    try { j = await apiGet(base + q); }
    catch (e) { console.warn(`  ohlcv page ${page} failed: ${e.message}`); break; }
    const list = (j && j.data && j.data.attributes && j.data.attributes.ohlcv_list) || [];
    if (!list.length) break;
    let pageOldest = Infinity;
    for (const c of list) {            // [tsSec, o, h, l, close, vol]
      const ts = c[0], price = parseFloat(c[4]);
      if (ts && price > 0) rows.push([ts * 1000, price]);
      if (ts < pageOldest) pageOldest = ts;
    }
    if (!isFinite(pageOldest)) break;
    if (pageOldest <= targetFromSec) break;
    if (pageOldest >= oldest) break;
    oldest = pageOldest;
    before = pageOldest;
  }
  return rows;
}

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
  if (out.every(([, p]) => p > 0.95 && p < 1.05)) return null;  // stablecoin-pair guard
  return out;
}

const spanDays = (s) => (s && s.length >= 2 ? Math.round((s[s.length - 1][0] - s[0][0]) / 86400000) : 0);

async function buildToken(token) {
  console.log(`\n${token.sym} (${token.addr})`);
  const attempts = [];

  // 1) Paid token-address endpoint — auto-selects the most-liquid pool, side handled.
  try {
    const r = clean(await fetchDaily('token', token.addr));
    if (r) attempts.push({ series: r, pool: 'auto(token-address)' });
  } catch (e) { console.warn(`  token-address ohlcv failed: ${e.message}`); }

  // 2) Deepest-history liquid pool — for maximum backfill.
  const dp = await deepestPool(token);
  if (dp && dp.pool) {
    try {
      const r = clean(await fetchDaily('pool', dp.pool, dp.side));
      if (r) attempts.push({ series: r, pool: `${dp.pool} (${dp.side})` });
    } catch (e) { console.warn(`  deepest-pool ohlcv failed: ${e.message}`); }
  }

  if (!attempts.length) { console.warn(`  ✗ no usable series for ${token.sym}`); return null; }
  attempts.sort((a, b) => spanDays(b.series) - spanDays(a.series) || b.series.length - a.series.length);
  const win = attempts[0], s = win.series;
  console.log(`  ✓ ${s.length} candles, span ${spanDays(s)}d (${new Date(s[0][0]).toISOString().slice(0,10)} → ${new Date(s[s.length-1][0]).toISOString().slice(0,10)}) via ${win.pool}`);
  return { source: 'coingecko', pool: win.pool, points: s.length, span: spanDays(s), series: s };
}

/* Daily price history for a global major via the coin-market endpoint.
   Returns [[tsMs, price], …]. days=365 yields daily granularity (auto). */
async function fetchMajorDaily(cgId) {
  const j = await apiGet(`/coins/${cgId}/market_chart?vs_currency=usd&days=${RANGE_DAYS}`);
  const prices = (j && j.prices) || [];
  return prices
    .map((p) => [p[0], parseFloat(p[1])])
    .filter(([ts, pr]) => ts && pr > 0);
}

async function buildMajor(m) {
  console.log(`\n${m.sym} (coingecko: ${m.id})`);
  try {
    const s = clean(await fetchMajorDaily(m.id));
    if (!s) { console.warn(`  ✗ no usable series for ${m.sym}`); return null; }
    console.log(`  ✓ ${s.length} candles, span ${spanDays(s)}d (${new Date(s[0][0]).toISOString().slice(0,10)} → ${new Date(s[s.length-1][0]).toISOString().slice(0,10)}) via coingecko market_chart`);
    return { source: 'coingecko-market', pool: 'market_chart', points: s.length, span: spanDays(s), series: s };
  } catch (e) {
    console.warn(`  market_chart failed for ${m.sym}: ${e.message}`);
    return null;
  }
}

(async () => {
  console.log(`Building charts-data.json — ${RANGE_DAYS}d daily, network "${NETWORK}", ${CG_DELAY_MS}ms pacing`);
  if (!(await preflight())) process.exit(1);

  // Load previous file so a partial failure carries forward old series.
  let prev = {};
  try { if (fs.existsSync(OUT_PATH)) prev = (JSON.parse(fs.readFileSync(OUT_PATH, 'utf8')).tokens) || {}; } catch {}

  const tokens = {};
  for (const t of TOKENS) {
    try {
      const built = await buildToken(t);
      if (built) tokens[t.sym] = built;
      else if (prev[t.sym]) { tokens[t.sym] = { ...prev[t.sym], carriedForward: true }; console.warn(`  → kept previous ${t.sym} series`); }
    } catch (e) {
      console.warn(`  unexpected error for ${t.sym}: ${e.message}`);
      if (prev[t.sym]) { tokens[t.sym] = { ...prev[t.sym], carriedForward: true }; }
    }
  }

  for (const m of MAJORS) {
    try {
      const built = await buildMajor(m);
      if (built) tokens[m.sym] = built;
      else if (prev[m.sym]) { tokens[m.sym] = { ...prev[m.sym], carriedForward: true }; console.warn(`  → kept previous ${m.sym} series`); }
    } catch (e) {
      console.warn(`  unexpected error for ${m.sym}: ${e.message}`);
      if (prev[m.sym]) { tokens[m.sym] = { ...prev[m.sym], carriedForward: true }; }
    }
  }

  const freshCount = Object.values(tokens).filter((t) => !t.carriedForward).length;
  if (freshCount === 0) {
    console.error('No fresh series built this run. Leaving existing file untouched.');
    process.exit(1);   // don't overwrite a good file with nothing
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
  console.log(`\nWrote ${OUT_PATH} — ${freshCount} fresh / ${Object.keys(tokens).length} total tokens, ${(fs.statSync(OUT_PATH).size/1024).toFixed(1)} KB`);
})().catch((e) => { console.error('FATAL:', e); process.exit(1); });
