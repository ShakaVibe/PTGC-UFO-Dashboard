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
  cgDelay:       1200,   // ms before every CoinGecko call (proactive rate-limit prevention)
  freeDelay:     500,    // ms before free API calls
  retries:       2,      // max retries on failure
  rateLimitWait: 30000,  // ms to wait if a 429 still occurs

  tokens: {
    PTGC: {
      address:     '0x94534EeEe131840b1c0F61847c572228bdfDDE93',
      mainPool:    '0xf5A89A6487D62df5308CDDA89c566C5B5ef94C11',
      decimals:    18,
      totalSupply: 333333333333
    },
    UFO: {
      address:     '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018',
      mainPool:    '0xbeA0e55b82Eb975280041F3b49C4D0bD937b72d5',
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
      d90:  md.price_change_percentage_200d || null,
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
async function fetchPoolsBatch(poolAddresses) {
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
    return [];
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
    return [];
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
    const poolInfoMap = await fetchPoolsBatch(poolAddresses);
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
        const vol   = processVolume(ohlcv);
        result.volume.vol7d  += vol.vol7d;
        result.volume.vol30d += vol.vol30d;
        result.volume.vol90d += vol.vol90d;
        console.log(`    7D Vol: $${vol.vol7d.toLocaleString()}`);

        const trades = await fetchTrades(poolAddr);
        const txns   = processTrades(trades);
        result.transactions.buys       += txns.buys;
        result.transactions.sells      += txns.sells;
        result.transactions.total      += txns.total;
        result.transactions.buyVolume  += txns.buyVolume;
        result.transactions.sellVolume += txns.sellVolume;
        console.log(`    24H Txns: ${txns.total} (${txns.buys}B / ${txns.sells}S)`);

      } catch (e) {
        console.error(`    Error [${poolAddr.slice(0, 10)}]:`, e.message);
        result.errors.push({ pool: poolAddr, error: e.message });
      }
    }

  } catch (e) {
    console.error(`Fatal error for ${tokenName}:`, e.message);
    result.errors.push({ type: 'fatal', error: e.message });
  }

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

  // Append snapshots
  liquidityHistory.snapshots.push({ timestamp, PTGC: tokenData.PTGC.liquidity, UFO: tokenData.UFO.liquidity });
  transactionHistory.snapshots.push({ timestamp, PTGC: tokenData.PTGC.transactions, UFO: tokenData.UFO.transactions });

  if (tokenData.PTGC.tokensInLP !== null || tokenData.UFO.tokensInLP !== null) {
    tokensInLPHistory.snapshots.push({ timestamp, PTGC: tokenData.PTGC.tokensInLP, UFO: tokenData.UFO.tokensInLP });
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

  // Save current snapshot
  saveData('coingecko-data.json', {
    lastUpdated: timestamp,
    PTGC: {
      volume:       tokenData.PTGC.volume,
      liquidity:    tokenData.PTGC.liquidity,
      transactions: tokenData.PTGC.transactions,
      holders:      tokenData.PTGC.holders,
      tokensInLP:   tokenData.PTGC.tokensInLP,
      poolCount:    tokenData.PTGC.poolCount,
      priceChanges: tokenData.PTGC.priceChanges
    },
    UFO: {
      volume:       tokenData.UFO.volume,
      liquidity:    tokenData.UFO.liquidity,
      transactions: tokenData.UFO.transactions,
      holders:      tokenData.UFO.holders,
      tokensInLP:   tokenData.UFO.tokensInLP,
      poolCount:    tokenData.UFO.poolCount,
      priceChanges: tokenData.UFO.priceChanges
    },
    rhCores: rhCoreData
  });

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log('\n' + '='.repeat(60));
  console.log(`Fetch Complete! Total time: ${elapsed}s`);
  console.log('NOTE: holder-history.json managed by fetch-burn-history.js');
  console.log('='.repeat(60));
}

main().catch(console.error);
