#!/usr/bin/env node
/* ──────────────────────────────────────────────────────────────────────────
   build-charts-intraday.js  —  prebuilt INTRADAY series for charts.html (2026-10-06)
   ----------------------------------------------------------------------------
   The sibling of build-charts-data.js (daily candles, the 1M–1Y ranges). This one
   fetches the two live tiers the browser used to pull from GeckoTerminal itself:
     • hourly  — 14 days of 1-hour closes   (the 7D and 14D ranges)
     • minute  — 24 hours of 15-minute closes (the 24H range)
   for every PulseChain chart token, and the same two windows for the majors from
   CoinGecko's market_chart (hourly over 14 d, ~5-minute over 1 d). Server-side,
   authenticated (COINGECKO_API_KEY), no browser CORS limits, no anonymous rate cap —
   the page paints every range at once from one same-origin file and asks
   GeckoTerminal only for the candles since the file was written.

   Writes data/charts-intraday.json:
     { lastUpdated, generatedBy, network,
       tokens: { SYM: { hourly: { source, points, series: [[tsMs, price], …] },
                        minute: { … } } } }
   Prices are rounded to 7 significant digits (the file is ~170 KB). On a partial
   failure the previous run's series is carried forward per token-tier and flagged
   `carriedForward: true`; a run that built nothing fresh leaves the file untouched.

   Requires: Node 18+ (global fetch). Secret: COINGECKO_API_KEY (already set).
   ────────────────────────────────────────────────────────────────────────── */

'use strict';

const fs = require('fs');
const path = require('path');

const API_KEY = process.env.COINGECKO_API_KEY;
const PRO_BASE = 'https://pro-api.coingecko.com/api/v3';
const NETWORK = 'pulsechain';
const OUT_PATH = path.join(__dirname, '..', 'data', 'charts-intraday.json');

/* Same tokens, addresses and known pools as build-charts-data.js / charts.html TOKENS.
   `pair` = the pool charts.html asks GeckoTerminal for (so the live top-up continues the
   same price series); null = let CoinGecko pick the most liquid pool (token endpoint). */
const TOKENS = [
  { sym: 'PTGC', addr: '0x94534EeEe131840b1c0F61847c572228bdfDDE93', pair: '0xf5A89A6487D62df5308CDDA89c566C5B5ef94C11' },
  { sym: 'UFO',  addr: '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6', pair: '0xE221e6fC30e5787F0d551f980B4da1055D832A03' },
  { sym: 'WPLS', addr: '0xA1077a294dDE1B09bB078844df40758a5D0f9a27', pair: null },
  { sym: 'PLSX', addr: '0x95B303987A60C71504D99Aa1b13B4DA07b0790ab', pair: '0x1b45b9148791d3a104184Cd5DFE5CE57193a3ee9' },
  { sym: 'HEX',  addr: '0x2b591e99afE9f32eAA6214f7B7629768c40Eeb39', pair: '0xf1F4ee610b2bAbB05C635F726eF8B0C568c8dc65' },
  { sym: 'EHEX', addr: '0x57fde0a71132198BBeC939B98976993d8D89D225', pair: '0x55D5c232D921B9eAA6b37b5845E439aCD04b4DBa' },
  { sym: 'INC',  addr: '0x2fa878Ab3F87CC1C9737Fc071108F904c0B0C95d', pair: '0xf808Bb6265e9Ca27002c0A04562Bf50d4FE37EAA' },
  { sym: 'PRVX', addr: '0xF6f8Db0aBa00007681F8fAF16A0FDa1c9B030b11', pair: null },
];
const MAJORS = [
  { sym: 'BTC', id: 'bitcoin' },
  { sym: 'ETH', id: 'ethereum' },
  { sym: 'SOL', id: 'solana' },
  { sym: 'BNB', id: 'binancecoin' },
  { sym: 'XRP', id: 'ripple' },
];

/* The two tiers, as charts.html's gtParamsForTier / ccParamsForTier define them (plus headroom). */
const TIERS = {
  hourly: { timeframe: 'hour',   aggregate: 1,  limit: 400, maxAgeDays: 15, cgDays: 14, stepMs: 3600000 },
  minute: { timeframe: 'minute', aggregate: 15, limit: 120, maxAgeDays: 1.5, cgDays: 1,  stepMs: 900000 },
};

const REQUEST_TIMEOUT_MS = 20000;
const CG_DELAY_MS = 2000;           // the sibling scripts' pacing — one shared Pro key, never 429'd
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

if (!API_KEY) { console.error('FATAL: COINGECKO_API_KEY is not set.'); process.exit(1); }

async function apiGet(urlPath, attempt = 0) {
  await sleep(CG_DELAY_MS);
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), REQUEST_TIMEOUT_MS);
  try {
    const r = await fetch(`${PRO_BASE}${urlPath}`, { signal: ctrl.signal, headers: { 'x-cg-pro-api-key': API_KEY, accept: 'application/json' } });
    if (r.status === 429 && attempt < 3) { clearTimeout(timer); console.warn(`  429 rate-limited, waiting 30s (attempt ${attempt + 1})…`); await sleep(30000); return apiGet(urlPath, attempt + 1); }
    if (!r.ok) { const body = await r.text().catch(() => ''); throw new Error(`HTTP ${r.status} for ${urlPath} :: ${body.slice(0, 200)}`); }
    return await r.json();
  } catch (e) {
    if ((e.name === 'AbortError' || /network|fetch/i.test(e.message)) && attempt < 2) { console.warn(`  request error (${e.message}); retry ${attempt + 1}…`); return apiGet(urlPath, attempt + 1); }
    throw e;
  } finally { clearTimeout(timer); }
}

const sig7 = (p) => Number(Number(p).toPrecision(7));

/* Sort, dedupe to the tier's step, drop zeros and anything older than the window. */
function clean(rows, tier) {
  if (!rows || rows.length < 2) return null;
  const cutoff = Date.now() - TIERS[tier].maxAgeDays * 86400000;
  const seen = new Set(), out = [];
  for (const [ts, price] of rows.sort((a, b) => a[0] - b[0])) {
    if (!(price > 0) || !(ts > cutoff)) continue;
    const key = Math.round(ts / 60000);
    if (seen.has(key)) continue;
    seen.add(key);
    out.push([ts, sig7(price)]);
  }
  if (out.length < 2) return null;
  if (out.every(([, p]) => p > 0.95 && p < 1.05)) return null;   // stablecoin-pair guard (the daily builder's)
  return out;
}

function ohlcvRows(j) {
  const list = (j && j.data && j.data.attributes && j.data.attributes.ohlcv_list) || [];
  return list.map((c) => [c[0] * 1000, parseFloat(c[4])]).filter(([ts, p]) => ts && p > 0);   // [tsSec, o, h, l, close, vol]
}

async function buildToken(token, tier) {
  const { timeframe, aggregate, limit } = TIERS[tier];
  const q = `?aggregate=${aggregate}&limit=${limit}&currency=usd`;
  // 1) the page's own pool (same series the browser tops up); 2) the token endpoint (CoinGecko picks the most liquid pool)
  if (token.pair) {
    try {
      const s = clean(ohlcvRows(await apiGet(`/onchain/networks/${NETWORK}/pools/${token.pair}/ohlcv/${timeframe}${q}&token=base`)), tier);
      if (s) return { source: 'coingecko-pool', pool: token.pair, points: s.length, series: s };
      console.warn(`  ${token.sym} [${tier}]: pool ${token.pair.slice(0, 10)}… gave no usable series — trying the token endpoint`);
    } catch (e) { console.warn(`  ${token.sym} [${tier}]: pool ohlcv failed: ${e.message}`); }
  }
  try {
    const s = clean(ohlcvRows(await apiGet(`/onchain/networks/${NETWORK}/tokens/${token.addr}/ohlcv/${timeframe}${q}`)), tier);
    if (s) return { source: 'coingecko-token', pool: 'auto(token-address)', points: s.length, series: s };
  } catch (e) { console.warn(`  ${token.sym} [${tier}]: token ohlcv failed: ${e.message}`); }
  return null;
}

async function buildMajor(m, tier) {
  try {
    const j = await apiGet(`/coins/${m.id}/market_chart?vs_currency=usd&days=${TIERS[tier].cgDays}`);
    const rows = ((j && j.prices) || []).map((p) => [p[0], parseFloat(p[1])]).filter(([ts, pr]) => ts && pr > 0);
    const s = clean(rows, tier);
    if (s) return { source: 'coingecko-market', pool: 'market_chart', points: s.length, series: s };
  } catch (e) { console.warn(`  ${m.sym} [${tier}]: market_chart failed: ${e.message}`); }
  return null;
}

const spanH = (s) => (s && s.length >= 2 ? ((s[s.length - 1][0] - s[0][0]) / 3600000).toFixed(1) : '0');

(async () => {
  console.log(`Building charts-intraday.json — hourly 14d + 15-min 24h, network "${NETWORK}", ${CG_DELAY_MS}ms pacing`);
  let prev = {};
  try { if (fs.existsSync(OUT_PATH)) prev = (JSON.parse(fs.readFileSync(OUT_PATH, 'utf8')).tokens) || {}; } catch {}

  const tokens = {};
  let fresh = 0;
  const jobs = [...TOKENS.map((t) => ({ sym: t.sym, build: (tier) => buildToken(t, tier) })),
                ...MAJORS.map((m) => ({ sym: m.sym, build: (tier) => buildMajor(m, tier) }))];
  for (const job of jobs) {
    console.log(`\n${job.sym}`);
    tokens[job.sym] = {};
    for (const tier of Object.keys(TIERS)) {
      let built = null;
      try { built = await job.build(tier); } catch (e) { console.warn(`  unexpected error for ${job.sym} [${tier}]: ${e.message}`); }
      if (built) {
        fresh++;
        tokens[job.sym][tier] = built;
        const s = built.series;
        console.log(`  ✓ ${tier}: ${s.length} points, ${spanH(s)} h (… → ${new Date(s[s.length - 1][0]).toISOString().slice(0, 16)}Z) via ${built.pool}`);
      } else if (prev[job.sym] && prev[job.sym][tier]) {
        tokens[job.sym][tier] = { ...prev[job.sym][tier], carriedForward: true };
        console.warn(`  → kept previous ${job.sym} [${tier}] series`);
      } else {
        console.warn(`  ✗ no ${tier} series for ${job.sym}`);
      }
    }
    if (!Object.keys(tokens[job.sym]).length) delete tokens[job.sym];
  }

  if (fresh === 0) { console.error('No fresh series built this run. Leaving existing file untouched.'); process.exit(1); }

  const payload = {
    lastUpdated: new Date().toISOString(),
    generatedBy: 'build-charts-intraday.js (CoinGecko Pro on-chain + market_chart, server-side)',
    network: NETWORK,
    tiers: { hourly: { stepMs: TIERS.hourly.stepMs, days: 14 }, minute: { stepMs: TIERS.minute.stepMs, days: 1 } },
    tokens,
  };
  fs.mkdirSync(path.dirname(OUT_PATH), { recursive: true });
  fs.writeFileSync(OUT_PATH, JSON.stringify(payload));
  console.log(`\nWrote ${OUT_PATH} — ${fresh} fresh series / ${Object.keys(tokens).length} tokens, ${(fs.statSync(OUT_PATH).size / 1024).toFixed(1)} KB`);
})().catch((e) => { console.error('FATAL:', e); process.exit(1); });
