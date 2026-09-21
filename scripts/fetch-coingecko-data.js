/**
 * CoinGecko Pro API Data Fetcher — Optimized
 *
 * Fetches volume, liquidity, transaction data, holder counts, and price changes
 * for PTGC and UFO tokens, plus RH Core price changes.
 * Runs every hour via GitHub Actions.
 *
 * NOTE: Does NOT update holder-history.json — managed by fetch-burn-history.js
 *
 * OPTIMIZATIONS vs original:
 *  1. Proactive 1200ms delay before every CoinGecko call → zero rate-limit hits
 *  2. Batch pool-info fetches via /pools/multi (up to 30 at once) → cuts ~50 calls to 2
 *  3. NO pool cap — ALL pools processed regardless of count
 *  4. Retries: 3 → 2, rate-limit wait: 60s → 30s
 *  5. Free APIs (PulseScan, DexScreener) use 500ms delay only
 *  6. Delay lives in fetchAPI only — no scattered sleep() calls
 */

const fs   = require('fs');
const path = require('path');

// ─── Configuration ─────────────────────────────────────────────────────────────
const CONFIG = {
  apiKey:        process.env.COINGECKO_API_KEY,
  baseUrl:       'https://pro-api.coingecko.com/api/v3',
  network:       'pulsechain',
  outputDir:     './data',
  cgDelay:       2000,   // ms before every CoinGecko call (proactive rate-limit prevention)
  freeDelay:     500,    // ms before free API calls
  retries:       3,      // max retries on failure
  rateLimitWait: 30000,  // ms to wait if a 429 still occurs

  tokens: {
    PTGC: {
      address:     '0x94534EeEe131840b1c0F61847c572228bdfDDE93',
      mainPool:    '0xf5A89A6487D62df5308CDDA89c566C5B5ef94C11',
      decimals:    18,
      totalSupply: 333333333333
    },
    UFO: {
      // MIGRATION: new UFO contract + new UFO/WPLS main pool (post-2026-07-08).
      address:     '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6',
      mainPool:    '0xE221e6fC30e5787F0d551f980B4da1055D832A03',
      decimals:    18,
      totalSupply: 999999999051
    }
  },

  rhCores: {
    WPLS: '0xa1077a294dde1b09bb078844df40758a5d0f9a27',
    PLSX: '0x95b303987a60c71504d99aa1b13b4da07b0790ab',
    INC:  '0x2fa878ab3f87cc1c9737fc071108f904c0b0c95d',
    HEX:  '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39',
    EHEX: '0x57fde0a71132198bbec939b98976993d8d89d225'
  }
};

// ─── Helpers ───────────────────────────────────────────────────────────────────
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

/**
 * CoinGecko Pro API call.
 * Waits cgDelay BEFORE every request — prevents rate limiting proactively.
 */
async function fetchAPI(endpoint) {
  const url = `${CONFIG.baseUrl}${endpoint}`;
  await sleep(CONFIG.cgDelay);

  for (let attempt = 1; attempt <= CONFIG.retries; attempt++) {
    try {
      const res = await fetch(url, {
        headers: {
          'x-cg-pro-api-key': CONFIG.apiKey,
          'Content-Type': 'application/json'
        }
      });

      if (res.status === 429) {
        console.log(`Rate limited — waiting ${CONFIG.rateLimitWait / 1000}s (attempt ${attempt}/${CONFIG.retries})`);
        await sleep(CONFIG.rateLimitWait);
        continue;
      }

      if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
      return await res.json();

    } catch (err) {
      console.error(`Attempt ${attempt}/${CONFIG.retries} failed [${endpoint.slice(0, 60)}]:`, err.message);
      if (attempt === CONFIG.retries) throw err;
      await sleep(2000 * attempt);
    }
  }
}

// ─── CoinGecko fetchers ────────────────────────────────────────────────────────

/* 90-day change from the repo's own daily series (data/charts-data.json, built by
   build-charts-data.js). CoinGecko's contract endpoint has 7d/30d/60d/200d/1y but NO 90d;
   until 2026-09-16 d90 was filled with the 200-day figure and the dashboard printed it as
   "90D" (roadmap a3). Same arithmetic as index.html's _chgAt fallback: the last point vs the
   newest point at or before now-90d; null when the series is missing or too short. */
function changeFromDailySeries(symbol, days) {
  try {
    const j = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'data', 'charts-data.json'), 'utf8'));
    const s = j?.tokens?.[symbol]?.series;
    if (!Array.isArray(s) || s.length < 2) return null;
    const target = Date.now() - days * 86400000;
    if (s[0][0] > target) return null;                 // series younger than the window — no honest figure
    let base = s[0];
    for (const p of s) { if (p[0] <= target) base = p; else break; }
    const p0 = base[1], now = s[s.length - 1][1];
    return (p0 > 0 && now > 0) ? ((now - p0) / p0) * 100 : null;
  } catch (e) { return null; }
}

async function fetchPriceChanges(address, name) {
  console.log(`  Price changes: ${name} (${address.slice(0, 10)}...)`);
  try {
    const data = await fetchAPI(`/coins/pulsechain/contract/${address}`);
    if (!data?.market_data) return null;
    const md = data.market_data;
    const pc = {
      h24:  md.price_change_percentage_24h  || null,
      d7:   md.price_change_percentage_7d   || null,
      d30:  md.price_change_percentage_30d  || null,
      d60:  md.price_change_percentage_60d  || null,
      d90:  changeFromDailySeries(name, 90),        // CoinGecko has no 90d field — see above
      d200: md.price_change_percentage_200d || null,
      d1y:  md.price_change_percentage_1y   || null
    };
    console.log(`    7d=${pc.d7?.toFixed(2)}%  30d=${pc.d30?.toFixed(2)}%`);
    return pc;
  } catch (e) {
    console.error(`  Price change error [${name}]:`, e.message);
    return null;
  }
}

async function fetchTokenPools(address) {
  console.log(`  Fetching pool list for ${address.slice(0, 10)}...`);
  try {
    const data = await fetchAPI(`/onchain/networks/${CONFIG.network}/tokens/${address}/pools?page=1`);
    return data?.data || [];
  } catch (e) {
    console.error('  Pool list error:', e.message);
    return [];
  }
}

/**
 * KEY OPTIMIZATION: Batch fetch pool info for up to 30 pools per request.
 * Replaces N individual fetchPoolInfo calls with ceil(N/30) calls.
 * For 30 pools: 30 calls → 1 call. For 50 pools: 50 calls → 2 calls.
 * Returns map: { poolAddress (lowercase) → attributes }
 */
/* a61 (2026-09-21): these three fetchers used to swallow every error and hand back an empty
   answer, so a rate-limited run produced a total that was simply missing a pool and looked exactly
   like a quiet day. They now return null / report the chunk, and fetchTokenData records what did
   not load so main() can keep the previous figures instead of publishing a partial one as fresh. */
async function fetchPoolsBatch(poolAddresses, errors) {
  if (!poolAddresses.length) return {};
  const result = {};
  // Split into chunks of 30 (CoinGecko multi endpoint limit)
  for (let i = 0; i < poolAddresses.length; i += 30) {
    const chunk = poolAddresses.slice(i, i + 30);
    console.log(`  Batch pool info: chunk ${Math.floor(i/30)+1} (${chunk.length} pools)`);
    try {
      const data = await fetchAPI(
        `/onchain/networks/${CONFIG.network}/pools/multi/${chunk.join(',')}`
      );
      for (const item of (data?.data || [])) {
        const addr = (item.id?.split('_')[1] || '').toLowerCase();
        if (addr) result[addr] = item.attributes;
      }
    } catch (e) {
      console.error('  Batch pool error:', e.message);
      if (errors) errors.push({ kind: 'liquidity', chunk: Math.floor(i / 30) + 1, error: e.message });
    }
  }
  return result;
}

async function fetchOHLCV(poolAddress, days = 90) {
  try {
    const data = await fetchAPI(
      `/onchain/networks/${CONFIG.network}/pools/${poolAddress}/ohlcv/day?aggregate=1&limit=${days}`
    );
    return data?.data?.attributes?.ohlcv_list || [];
  } catch (e) {
    console.error(`  OHLCV error [${poolAddress.slice(0, 10)}]:`, e.message);
    return null;   // a61: null = we do not know this pool's volume; [] would read as "no trades"
  }
}

async function fetchTrades(poolAddress) {
  try {
    const data = await fetchAPI(
      `/onchain/networks/${CONFIG.network}/pools/${poolAddress}/trades`
    );
    return data?.data || [];
  } catch (e) {
    console.error(`  Trades error [${poolAddress.slice(0, 10)}]:`, e.message);
    return null;   // a61: null = unknown, not "no trades in 24 h"
  }
}

// ─── Free API fetchers ─────────────────────────────────────────────────────────

async function fetchHolderCount(address) {
  try {
    await sleep(CONFIG.freeDelay);
    const res = await fetch(`https://api.scan.pulsechain.com/api/v2/tokens/${address}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    const holders = data.holders ? parseInt(data.holders) : null;
    console.log(`  Holders: ${holders}`);
    return holders;
  } catch (e) {
    console.error(`  PulseScan error [${address.slice(0, 10)}]:`, e.message);
    return null;
  }
}

async function fetchTokensInLP(address) {
  try {
    await sleep(CONFIG.freeDelay);
    const res = await fetch(`https://api.dexscreener.com/latest/dex/tokens/${address}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (!data.pairs?.length) return 0;
    let total = 0;
    for (const pair of data.pairs) {
      const isBase = pair.baseToken?.address?.toLowerCase() === address.toLowerCase();
      if (isBase && pair.liquidity?.base)       total += pair.liquidity.base;
      else if (!isBase && pair.liquidity?.quote) total += pair.liquidity.quote;
    }
    console.log(`  Tokens in LP: ${total.toLocaleString()}`);
    return total;
  } catch (e) {
    console.error(`  DexScreener error [${address.slice(0, 10)}]:`, e.message);
    return null;
  }
}

// ─── Data processors ───────────────────────────────────────────────────────────

function processVolume(ohlcvList) {
  if (!ohlcvList?.length) return { vol7d: 0, vol30d: 0, vol90d: 0 };
  let vol7d = 0, vol30d = 0, vol90d = 0;
  ohlcvList.forEach((c, i) => {
    const v = c[5] || 0;
    if (i < 7)  vol7d  += v;
    if (i < 30) vol30d += v;
    if (i < 90) vol90d += v;
  });
  return { vol7d, vol30d, vol90d };
}

function processTrades(trades) {
  if (!trades?.length) return { buys: 0, sells: 0, total: 0, buyVolume: 0, sellVolume: 0 };
  let buys = 0, sells = 0, buyVolume = 0, sellVolume = 0;
  const h24 = Date.now() - 86400000;
  for (const t of trades) {
    const a = t.attributes;
    if (!a) continue;
    if (new Date(a.block_timestamp).getTime() < h24) continue;
    const usd = parseFloat(a.volume_in_usd) || 0;
    if (a.kind === 'buy') { buys++;  buyVolume  += usd; }
    else                  { sells++; sellVolume += usd; }
  }
  return { buys, sells, total: buys + sells, buyVolume, sellVolume };
}

// ─── File helpers ──────────────────────────────────────────────────────────────

function loadHistory(filename) {
  const fp = path.join(CONFIG.outputDir, filename);
  try {
    if (fs.existsSync(fp)) return JSON.parse(fs.readFileSync(fp, 'utf8'));
  } catch (e) { console.error(`Error loading ${filename}:`, e.message); }
  return { snapshots: [] };
}

function saveData(filename, data) {
  if (!fs.existsSync(CONFIG.outputDir)) fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  const fp = path.join(CONFIG.outputDir, filename);
  fs.writeFileSync(fp, JSON.stringify(data, null, 2));
  console.log(`Saved: ${fp}`);
}

// ─── Main token fetcher ────────────────────────────────────────────────────────

async function fetchTokenData(tokenName, tokenConfig) {
  console.log(`\n${'='.repeat(10)} Fetching ${tokenName} ${'='.repeat(10)}`);

  const result = {
    liquidity:    0,
    volume:       { vol7d: 0, vol30d: 0, vol90d: 0 },
    transactions: { buys: 0, sells: 0, total: 0, buyVolume: 0, sellVolume: 0 },
    holders:      null,
    tokensInLP:   null,
    poolCount:    0,
    priceChanges: null,
    errors:       []
  };

  try {
    // 1. Price changes (1 CoinGecko call)
    result.priceChanges = await fetchPriceChanges(tokenConfig.address, tokenName);

    // 2. Free APIs — holders + tokensInLP (no CoinGecko quota used)
    result.holders    = await fetchHolderCount(tokenConfig.address);
    result.tokensInLP = await fetchTokensInLP(tokenConfig.address);

    // 3. Get ALL pools (1 CoinGecko call)
    const pools = await fetchTokenPools(tokenConfig.address);
    result.poolCount = pools.length;
    console.log(`  Found ${pools.length} pools — processing ALL`);

    const poolAddresses = pools.map(p => p.id?.split('_')[1]).filter(Boolean);

    // 4. BATCH pool info — 30 pools per call instead of 1 per call (huge saving!)
    const poolInfoMap = await fetchPoolsBatch(poolAddresses, result.errors);
    for (const attrs of Object.values(poolInfoMap)) {
      result.liquidity += parseFloat(attrs?.reserve_in_usd) || 0;
    }
    console.log(`  Total liquidity: $${result.liquidity.toLocaleString()}`);

    // 5. OHLCV + Trades per pool (2 calls each — unavoidable but fast with proactive delay)
    for (let idx = 0; idx < poolAddresses.length; idx++) {
      const poolAddr = poolAddresses[idx];
      const poolName = pools[idx]?.attributes?.name || 'Unknown';
      console.log(`  [${idx + 1}/${poolAddresses.length}] ${poolName}`);

      try {
        const ohlcv = await fetchOHLCV(poolAddr, 90);
        if (ohlcv === null) {
          result.errors.push({ kind: 'volume', pool: poolAddr, error: 'ohlcv unavailable' });
          console.error(`    7D Vol: unknown (ohlcv failed) — this token's volume totals are incomplete`);
        } else {
          const vol = processVolume(ohlcv);
          result.volume.vol7d  += vol.vol7d;
          result.volume.vol30d += vol.vol30d;
          result.volume.vol90d += vol.vol90d;
          console.log(`    7D Vol: $${vol.vol7d.toLocaleString()}`);
        }

        const trades = await fetchTrades(poolAddr);
        if (trades === null) {
          result.errors.push({ kind: 'transactions', pool: poolAddr, error: 'trades unavailable' });
          console.error(`    24H Txns: unknown (trades failed) — this token's txn totals are incomplete`);
        } else {
          const txns = processTrades(trades);
          result.transactions.buys       += txns.buys;
          result.transactions.sells      += txns.sells;
          result.transactions.total      += txns.total;
          result.transactions.buyVolume  += txns.buyVolume;
          result.transactions.sellVolume += txns.sellVolume;
          console.log(`    24H Txns: ${txns.total} (${txns.buys}B / ${txns.sells}S)`);
        }

      } catch (e) {
        console.error(`    Error [${poolAddr.slice(0, 10)}]:`, e.message);
        result.errors.push({ kind: 'pool', pool: poolAddr, error: e.message });
      }
    }

  } catch (e) {
    console.error(`Fatal error for ${tokenName}:`, e.message);
    result.errors.push({ kind: 'fatal', type: 'fatal', error: e.message });
  }

  /* a61: which of this token's figures are whole. A partial total is worse than an old one:
     the reader's gates (fresh < 24 h, positive, monotonic) all pass for a 7D volume that is
     simply missing its biggest pool, and the dashboard then prints that as "7D volume",
     "vs 7D avg" and PTGC Value Generated. */
  const bad = k => result.errors.some(e => e.kind === k || e.kind === 'fatal' || e.kind === 'pool');
  result.complete = {
    volume:       !bad('volume'),
    transactions: !bad('transactions'),
    liquidity:    !bad('liquidity')
  };
  const missing = Object.entries(result.complete).filter(([, ok]) => !ok).map(([k]) => k);
  if (missing.length) console.warn(`  \u26a0 ${tokenName}: incomplete this run \u2014 ${missing.join(', ')} (${result.errors.length} error(s))`);

  console.log(`\n${tokenName} TOTALS:`);
  console.log(`  Pools     : ${result.poolCount}`);
  console.log(`  Holders   : ${result.holders ?? 'N/A'}`);
  console.log(`  In LP     : ${result.tokensInLP?.toLocaleString() ?? 'N/A'}`);
  console.log(`  Liquidity : $${result.liquidity.toLocaleString()}`);
  console.log(`  Vol 7D    : $${result.volume.vol7d.toLocaleString()}`);
  console.log(`  Vol 30D   : $${result.volume.vol30d.toLocaleString()}`);
  console.log(`  Txns      : ${result.transactions.total}`);

  return result;
}

// ─── RH Core price changes ─────────────────────────────────────────────────────

async function fetchRHCorePriceChanges() {
  console.log('\n========== Fetching RH Core Price Changes ==========');
  const coreData = {};
  for (const [name, address] of Object.entries(CONFIG.rhCores)) {
    coreData[name] = { address, priceChanges: await fetchPriceChanges(address, name) };
  }
  return coreData;
}

// ─── Main ──────────────────────────────────────────────────────────────────────

async function main() {
  const startTime = Date.now();
  console.log('='.repeat(60));
  console.log('CoinGecko Data Fetch — Optimized');
  console.log(`Time     : ${new Date().toISOString()}`);
  console.log(`CG delay : ${CONFIG.cgDelay}ms | Retries: ${CONFIG.retries} | Pool cap: NONE`);
  console.log('='.repeat(60));

  if (!CONFIG.apiKey) {
    console.error('ERROR: COINGECKO_API_KEY not set!');
    process.exit(1);
  }

  const timestamp = new Date().toISOString();

  const previous           = loadHistory('coingecko-data.json');   // a61: what is published now
  const liquidityHistory   = loadHistory('liquidity-history.json');
  const transactionHistory = loadHistory('transaction-history.json');
  const tokensInLPHistory  = loadHistory('tokensinlp-history.json');

  // Fetch all token data
  const tokenData = {};
  for (const [name, cfg] of Object.entries(CONFIG.tokens)) {
    tokenData[name] = await fetchTokenData(name, cfg);
  }

  // Fetch RH Core price changes
  const rhCoreData = await fetchRHCorePriceChanges();

  // ─── SAFETY VALIDATION ────────────────────────────────────────────────────
  // If either token came back with 0 pools and $0 liquidity, the CoinGecko
  // calls failed (likely rate limited). Do NOT save corrupted data — exit
  // cleanly so existing history files stay untouched.
  const ptgcValid = tokenData.PTGC.poolCount > 0 || tokenData.PTGC.liquidity > 0;
  const ufoValid  = tokenData.UFO.poolCount  > 0 || tokenData.UFO.liquidity  > 0;

  if (!ptgcValid && !ufoValid) {
    console.error('\n⛔ VALIDATION FAILED: Both PTGC and UFO returned 0 pools and $0 liquidity.');
    console.error('   This indicates CoinGecko API calls failed (rate limited or quota exhausted).');
    console.error('   Skipping all file saves to protect existing data. Will retry next run.');
    process.exit(1);
  }

  if (!ptgcValid) {
    console.warn('\n⚠ WARNING: PTGC returned 0 pools / $0 liquidity — skipping PTGC data, keeping previous.');
  }
  if (!ufoValid) {
    console.warn('\n⚠ WARNING: UFO returned 0 pools / $0 liquidity — skipping UFO data, keeping previous.');
  }
  // ─────────────────────────────────────────────────────────────────────────

  /* a61 (2026-09-21): the history files are append-only and averaged by their readers, so ONE
     understated point is permanent. A token contributes a point only when the figure behind it
     came back whole this run — a run that lost a pool's OHLCV or trades writes no point for
     that token rather than a low one. (Same defect the LV snapshot had with zeroed rows.) */
  const valid = { PTGC: ptgcValid, UFO: ufoValid };
  const whole = (name, figure) => valid[name] && tokenData[name].complete[figure];

  const liqPoint = { timestamp };
  if (whole('PTGC', 'liquidity')) liqPoint.PTGC = tokenData.PTGC.liquidity;
  if (whole('UFO',  'liquidity')) liqPoint.UFO  = tokenData.UFO.liquidity;
  if (liqPoint.PTGC !== undefined || liqPoint.UFO !== undefined) liquidityHistory.snapshots.push(liqPoint);
  else console.warn('\u26a0 liquidity-history: no complete figure this run \u2014 no point appended.');

  const txnPoint = { timestamp };
  if (whole('PTGC', 'transactions')) txnPoint.PTGC = tokenData.PTGC.transactions;
  if (whole('UFO',  'transactions')) txnPoint.UFO  = tokenData.UFO.transactions;
  if (txnPoint.PTGC !== undefined || txnPoint.UFO !== undefined) transactionHistory.snapshots.push(txnPoint);
  else console.warn('\u26a0 transaction-history: no complete figure this run \u2014 no point appended.');

  if ((ptgcValid && tokenData.PTGC.tokensInLP !== null) || (ufoValid && tokenData.UFO.tokensInLP !== null)) {
    tokensInLPHistory.snapshots.push({
      timestamp,
      ...(ptgcValid && tokenData.PTGC.tokensInLP !== null ? { PTGC: tokenData.PTGC.tokensInLP } : {}),
      ...(ufoValid  && tokenData.UFO.tokensInLP  !== null ? { UFO:  tokenData.UFO.tokensInLP  } : {})
    });
  }

  // Trim to last 500 snapshots
  for (const h of [liquidityHistory, transactionHistory, tokensInLPHistory]) {
    if (h.snapshots.length > 500) h.snapshots = h.snapshots.slice(-500);
  }

  // Save histories
  liquidityHistory.lastUpdated   = timestamp;
  transactionHistory.lastUpdated = timestamp;
  tokensInLPHistory.lastUpdated  = timestamp;

  saveData('liquidity-history.json',   liquidityHistory);
  saveData('transaction-history.json', transactionHistory);
  saveData('tokensinlp-history.json',  tokensInLPHistory);

  /* a61: a figure that did not come back whole is published as the PREVIOUS run's figure, with
     the stamp it was actually measured at, instead of this run's partial total. The reader's
     freshness gate (< 24 h on lastUpdated) could never see the difference before — a 7D volume
     missing its biggest pool is positive, monotonic and "fresh". carriedFrom says which figures
     are older than lastUpdated; `complete` says what this run managed. */
  const section = (name) => {
    const t = tokenData[name];
    const p = (previous && previous[name]) || null;
    const out = {
      volume:       t.volume,
      liquidity:    t.liquidity,
      transactions: t.transactions,
      holders:      t.holders,
      tokensInLP:   t.tokensInLP,
      poolCount:    t.poolCount,
      priceChanges: t.priceChanges,
      complete:     { ...t.complete }
    };
    const carriedFrom = {};
    const carry = (figure, key) => {
      if (t.complete[figure] && valid[name]) return;
      if (!p || p[key] == null) {           // nothing to fall back to: keep what we have and say so
        console.warn(`\u26a0 ${name} ${figure} incomplete and no previous value to keep \u2014 publishing the partial figure.`);
        return;
      }
      out[key] = p[key];
      carriedFrom[figure] = (p.carriedFrom && p.carriedFrom[figure]) || (previous && previous.lastUpdated) || null;
      out.complete[figure] = false;
      console.warn(`\u26a0 ${name} ${figure}: kept the previous value (measured ${carriedFrom[figure] || 'unknown'}).`);
    };
    carry('volume', 'volume');
    carry('transactions', 'transactions');
    carry('liquidity', 'liquidity');
    if (Object.keys(carriedFrom).length) out.carriedFrom = carriedFrom;
    return out;
  };

  // Save current snapshot
  saveData('coingecko-data.json', {
    lastUpdated: timestamp,
    PTGC: section('PTGC'),
    UFO:  section('UFO'),
    rhCores: rhCoreData
  });

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log('\n' + '='.repeat(60));
  console.log(`Fetch Complete! Total time: ${elapsed}s`);
  console.log('NOTE: holder-history.json managed by fetch-burn-history.js');
  console.log('='.repeat(60));
}

/* a61: `main().catch(console.error)` printed the stack and exited 0, so a throw anywhere outside
   fetchTokenData was a green run with nothing written and no alert. The pipeline's "Report step
   failures" step turns a non-zero exit into a red run. */
main().catch(e => { console.error(e); process.exit(1); });
