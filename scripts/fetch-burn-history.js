/**
 * CoinGecko Pro API Data Fetcher
 * 
 * Fetches volume, liquidity, transaction data, holder counts, and PRICE CHANGES for PTGC and UFO tokens.
 * Also fetches price changes for RH Core tokens (WPLS, PLSX, INC, HEX, EHEX).
 * Runs every 30 minutes via GitHub Actions.
 * Stores timestamped snapshots for rolling window calculations.
 * 
 * NOTE: This script does NOT update holder-history.json
 *       Holder history is managed exclusively by fetch-burn-history.js
 */

const fs = require('fs');
const path = require('path');

// Configuration
const CONFIG = {
  apiKey: process.env.COINGECKO_API_KEY,
  baseUrl: 'https://pro-api.coingecko.com/api/v3',
  network: 'pulsechain',
  outputDir: './data',
  
  tokens: {
    PTGC: {
      address: '0x94534EeEe131840b1c0F61847c572228bdfDDE93',
      mainPool: '0xf5A89A6487D62df5308CDDA89c566C5B5ef94C11',
      decimals: 18,
      totalSupply: 333333333333
    },
    UFO: {
      address: '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018',
      mainPool: '0xbeA0e55b82Eb975280041F3b49C4D0bD937b72d5',
      decimals: 18,
      totalSupply: 999999999051
    }
  },
  
  // RH Core tokens for price change tracking
  rhCores: {
    WPLS: '0xa1077a294dde1b09bb078844df40758a5d0f9a27',
    PLSX: '0x95b303987a60c71504d99aa1b13b4da07b0790ab',
    INC: '0x2fa878ab3f87cc1c9737fc071108f904c0b0c95d',
    HEX: '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39',
    EHEX: '0x57fde0a71132198bbec939b98976993d8d89d225'
  }
};

// Rate limiting helper
const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

// API fetch with error handling and retry
async function fetchAPI(endpoint, retries = 3) {
  const url = `${CONFIG.baseUrl}${endpoint}`;
  
  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      const response = await fetch(url, {
        headers: {
          'x-cg-pro-api-key': CONFIG.apiKey,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.status === 429) {
        console.log(`Rate limited, waiting 60 seconds (attempt ${attempt}/${retries})`);
        await sleep(60000);
        continue;
      }
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error(`Attempt ${attempt}/${retries} failed for ${endpoint}:`, error.message);
      if (attempt === retries) throw error;
      await sleep(2000 * attempt);
    }
  }
}

// Fetch price changes for a token by contract address
async function fetchPriceChanges(tokenAddress, tokenName) {
  console.log(`  Fetching price changes for ${tokenName} (${tokenAddress.slice(0, 10)}...)`);
  try {
    const data = await fetchAPI(`/coins/pulsechain/contract/${tokenAddress}`);
    
    if (data && data.market_data) {
      const priceChanges = {
        h24: data.market_data.price_change_percentage_24h || null,
        d7: data.market_data.price_change_percentage_7d || null,
        d30: data.market_data.price_change_percentage_30d || null,
        d60: data.market_data.price_change_percentage_60d || null,
        d90: data.market_data.price_change_percentage_200d || null,
        d200: data.market_data.price_change_percentage_200d || null,
        d1y: data.market_data.price_change_percentage_1y || null
      };
      console.log(`    ${tokenName}: 7d=${priceChanges.d7?.toFixed(2)}%, 30d=${priceChanges.d30?.toFixed(2)}%`);
      return priceChanges;
    }
    return null;
  } catch (error) {
    console.error(`  Error fetching price changes for ${tokenName}:`, error.message);
    return null;
  }
}

// Fetch holder count from PulseScan (free, no API key needed)
async function fetchHolderCount(tokenAddress) {
  try {
    const url = `https://api.scan.pulsechain.com/api/v2/tokens/${tokenAddress}`;
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    const holders = data.holders ? parseInt(data.holders) : null;
    console.log(`  Holders for ${tokenAddress.slice(0, 10)}...: ${holders}`);
    return holders;
  } catch (error) {
    console.error(`PulseScan holder error for ${tokenAddress}:`, error.message);
    return null;
  }
}

// Fetch tokensInLP from DexScreener (free, no API key needed)
async function fetchTokensInLP(tokenAddress) {
  try {
    const url = `https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`;
    const res = await fetch(url);
    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }
    const data = await res.json();
    if (!data.pairs || data.pairs.length === 0) {
      return 0;
    }
    
    let totalTokensInLP = 0;
    for (const pair of data.pairs) {
      const isBase = pair.baseToken?.address?.toLowerCase() === tokenAddress.toLowerCase();
      if (isBase && pair.liquidity?.base) {
        totalTokensInLP += pair.liquidity.base;
      } else if (!isBase && pair.liquidity?.quote) {
        totalTokensInLP += pair.liquidity.quote;
      }
    }
    console.log(`  Tokens in LP for ${tokenAddress.slice(0, 10)}...: ${totalTokensInLP.toLocaleString()}`);
    return totalTokensInLP;
  } catch (error) {
    console.error(`DexScreener tokensInLP error for ${tokenAddress}:`, error.message);
    return null;
  }
}

// Fetch all pools for a token
async function fetchTokenPools(address) {
  console.log(`Fetching pools for ${address.slice(0, 10)}...`);
  try {
    const data = await fetchAPI(`/onchain/networks/${CONFIG.network}/tokens/${address}/pools?page=1`);
    return data?.data || [];
  } catch (e) {
    console.error('Error fetching pools:', e.message);
    return [];
  }
}

// Fetch pool info with liquidity
async function fetchPoolInfo(poolAddress) {
  try {
    const data = await fetchAPI(`/onchain/networks/${CONFIG.network}/pools/${poolAddress}`);
    return data?.data?.attributes || null;
  } catch (e) {
    console.error(`Error fetching pool ${poolAddress}:`, e.message);
    return null;
  }
}

// Fetch OHLCV data for volume
async function fetchOHLCV(poolAddress, days = 90) {
  try {
    const data = await fetchAPI(
      `/onchain/networks/${CONFIG.network}/pools/${poolAddress}/ohlcv/day?aggregate=1&limit=${days}`
    );
    return data?.data?.attributes?.ohlcv_list || [];
  } catch (e) {
    console.error(`Error fetching OHLCV for ${poolAddress}:`, e.message);
    return [];
  }
}

// Fetch recent trades
async function fetchTrades(poolAddress) {
  try {
    const data = await fetchAPI(
      `/onchain/networks/${CONFIG.network}/pools/${poolAddress}/trades`
    );
    return data?.data || [];
  } catch (e) {
    console.error(`Error fetching trades for ${poolAddress}:`, e.message);
    return [];
  }
}

// Process OHLCV into volume periods
function processVolume(ohlcvList) {
  if (!ohlcvList || ohlcvList.length === 0) return { vol7d: 0, vol30d: 0, vol90d: 0 };
  
  let vol7d = 0, vol30d = 0, vol90d = 0;
  
  ohlcvList.forEach((candle, i) => {
    const vol = candle[5] || 0;
    if (i < 7) vol7d += vol;
    if (i < 30) vol30d += vol;
    if (i < 90) vol90d += vol;
  });
  
  return { vol7d, vol30d, vol90d };
}

// Process trades into transaction counts
function processTrades(trades) {
  if (!trades || trades.length === 0) return { buys: 0, sells: 0, total: 0, buyVolume: 0, sellVolume: 0 };
  
  let buys = 0, sells = 0, buyVolume = 0, sellVolume = 0;
  
  const now = Date.now();
  const h24 = now - 24 * 60 * 60 * 1000;
  
  for (const trade of trades) {
    const attrs = trade.attributes;
    if (!attrs) continue;
    
    const timestamp = new Date(attrs.block_timestamp).getTime();
    if (timestamp < h24) continue;
    
    const isBuy = attrs.kind === 'buy';
    const volumeUsd = parseFloat(attrs.volume_in_usd) || 0;
    
    if (isBuy) {
      buys++;
      buyVolume += volumeUsd;
    } else {
      sells++;
      sellVolume += volumeUsd;
    }
  }
  
  return { buys, sells, total: buys + sells, buyVolume, sellVolume };
}

// Load existing history file
function loadHistory(filename) {
  const filepath = path.join(CONFIG.outputDir, filename);
  try {
    if (fs.existsSync(filepath)) {
      const data = fs.readFileSync(filepath, 'utf8');
      return JSON.parse(data);
    }
  } catch (e) {
    console.error(`Error loading ${filename}:`, e.message);
  }
  return { snapshots: [] };
}

// Save data to file
function saveData(filename, data) {
  const outputPath = path.join(CONFIG.outputDir, filename);
  
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, JSON.stringify(data, null, 2));
  console.log(`Saved: ${outputPath}`);
}

// Fetch all data for a token
async function fetchTokenData(tokenName, tokenConfig) {
  console.log(`\n========== Fetching ${tokenName} ==========`);
  
  const result = {
    liquidity: 0,
    volume: { vol7d: 0, vol30d: 0, vol90d: 0 },
    transactions: { buys: 0, sells: 0, total: 0, buyVolume: 0, sellVolume: 0 },
    holders: null,
    tokensInLP: null,
    poolCount: 0,
    priceChanges: null,
    errors: []
  };
  
  try {
    result.priceChanges = await fetchPriceChanges(tokenConfig.address, tokenName);
    await sleep(500);
    
    result.holders = await fetchHolderCount(tokenConfig.address);
    await sleep(500);
    
    result.tokensInLP = await fetchTokensInLP(tokenConfig.address);
    await sleep(500);
    
    const pools = await fetchTokenPools(tokenConfig.address);
    result.poolCount = pools.length;
    console.log(`Found ${pools.length} pools`);
    await sleep(300);
    
    const poolsToProcess = pools.slice(0, 15);
    
    for (const poolData of poolsToProcess) {
      const poolAddress = poolData.id?.split('_')[1];
      if (!poolAddress) continue;
      
      const poolName = poolData.attributes?.name || 'Unknown';
      console.log(`  Processing: ${poolName} (${poolAddress.slice(0, 10)}...)`);
      
      try {
        const poolInfo = await fetchPoolInfo(poolAddress);
        if (poolInfo) {
          const liq = parseFloat(poolInfo.reserve_in_usd) || 0;
          result.liquidity += liq;
          console.log(`    Liquidity: $${liq.toLocaleString()}`);
        }
        await sleep(300);
        
        const ohlcv = await fetchOHLCV(poolAddress, 90);
        const vol = processVolume(ohlcv);
        result.volume.vol7d += vol.vol7d;
        result.volume.vol30d += vol.vol30d;
        result.volume.vol90d += vol.vol90d;
        console.log(`    7D Vol: $${vol.vol7d.toLocaleString()}`);
        await sleep(300);
        
        const trades = await fetchTrades(poolAddress);
        const txns = processTrades(trades);
        result.transactions.buys += txns.buys;
        result.transactions.sells += txns.sells;
        result.transactions.total += txns.total;
        result.transactions.buyVolume += txns.buyVolume;
        result.transactions.sellVolume += txns.sellVolume;
        console.log(`    24H Txns: ${txns.total} (${txns.buys} buys / ${txns.sells} sells)`);
        await sleep(300);
        
      } catch (e) {
        console.error(`    Error: ${e.message}`);
        result.errors.push({ pool: poolAddress, error: e.message });
      }
    }
    
  } catch (e) {
    console.error(`Fatal error for ${tokenName}:`, e.message);
    result.errors.push({ type: 'fatal', error: e.message });
  }
  
  console.log(`\n${tokenName} TOTALS:`);
  console.log(`  Price Changes: 7d=${result.priceChanges?.d7?.toFixed(2) || 'N/A'}%, 30d=${result.priceChanges?.d30?.toFixed(2) || 'N/A'}%`);
  console.log(`  Holders: ${result.holders || 'N/A'}`);
  console.log(`  Tokens in LP: ${result.tokensInLP?.toLocaleString() || 'N/A'}`);
  console.log(`  Liquidity: $${result.liquidity.toLocaleString()}`);
  console.log(`  Volume 7D: $${result.volume.vol7d.toLocaleString()}`);
  console.log(`  Volume 30D: $${result.volume.vol30d.toLocaleString()}`);
  console.log(`  Transactions: ${result.transactions.total}`);
  
  return result;
}

// Fetch price changes for all RH Core tokens
async function fetchRHCorePriceChanges() {
  console.log('\n========== Fetching RH Core Price Changes ==========');
  
  const coreData = {};
  
  for (const [name, address] of Object.entries(CONFIG.rhCores)) {
    const priceChanges = await fetchPriceChanges(address, name);
    coreData[name] = {
      address,
      priceChanges
    };
    await sleep(500);
  }
  
  return coreData;
}

// Main execution
async function main() {
  console.log('='.repeat(60));
  console.log('CoinGecko Data Fetch Started');
  console.log(`Time: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
  
  if (!CONFIG.apiKey) {
    console.error('ERROR: COINGECKO_API_KEY environment variable not set!');
    process.exit(1);
  }
  
  const timestamp = new Date().toISOString();
  
  // Load existing histories (NOT holder-history - that's managed by fetch-burn-history.js)
  const liquidityHistory = loadHistory('liquidity-history.json');
  const transactionHistory = loadHistory('transaction-history.json');
  const tokensInLPHistory = loadHistory('tokensinlp-history.json');
  
  // Fetch data for each token
  const tokenData = {};
  
  for (const [tokenName, tokenConfig] of Object.entries(CONFIG.tokens)) {
    tokenData[tokenName] = await fetchTokenData(tokenName, tokenConfig);
    await sleep(2000);
  }
  
  // Fetch RH Core price changes
  const rhCoreData = await fetchRHCorePriceChanges();
  
  // Append to histories (NOT holder-history)
  liquidityHistory.snapshots.push({
    timestamp,
    PTGC: tokenData.PTGC.liquidity,
    UFO: tokenData.UFO.liquidity
  });
  
  transactionHistory.snapshots.push({
    timestamp,
    PTGC: tokenData.PTGC.transactions,
    UFO: tokenData.UFO.transactions
  });
  
  if (tokenData.PTGC.tokensInLP !== null || tokenData.UFO.tokensInLP !== null) {
    tokensInLPHistory.snapshots.push({
      timestamp,
      PTGC: tokenData.PTGC.tokensInLP,
      UFO: tokenData.UFO.tokensInLP
    });
  }
  
  // Trim histories to last 500 snapshots
  if (liquidityHistory.snapshots.length > 500) {
    liquidityHistory.snapshots = liquidityHistory.snapshots.slice(-500);
  }
  if (transactionHistory.snapshots.length > 500) {
    transactionHistory.snapshots = transactionHistory.snapshots.slice(-500);
  }
  if (tokensInLPHistory.snapshots.length > 500) {
    tokensInLPHistory.snapshots = tokensInLPHistory.snapshots.slice(-500);
  }
  
  // Save history files (NOT holder-history)
  liquidityHistory.lastUpdated = timestamp;
  transactionHistory.lastUpdated = timestamp;
  tokensInLPHistory.lastUpdated = timestamp;
  
  saveData('liquidity-history.json', liquidityHistory);
  saveData('transaction-history.json', transactionHistory);
  saveData('tokensinlp-history.json', tokensInLPHistory);
  
  // Save current aggregates
  const coingeckoData = {
    lastUpdated: timestamp,
    PTGC: {
      volume: tokenData.PTGC.volume,
      liquidity: tokenData.PTGC.liquidity,
      transactions: tokenData.PTGC.transactions,
      holders: tokenData.PTGC.holders,
      tokensInLP: tokenData.PTGC.tokensInLP,
      poolCount: tokenData.PTGC.poolCount,
      priceChanges: tokenData.PTGC.priceChanges
    },
    UFO: {
      volume: tokenData.UFO.volume,
      liquidity: tokenData.UFO.liquidity,
      transactions: tokenData.UFO.transactions,
      holders: tokenData.UFO.holders,
      tokensInLP: tokenData.UFO.tokensInLP,
      poolCount: tokenData.UFO.poolCount,
      priceChanges: tokenData.UFO.priceChanges
    },
    rhCores: rhCoreData
  };
  
  saveData('coingecko-data.json', coingeckoData);
  
  console.log('\n' + '='.repeat(60));
  console.log('Fetch Complete!');
  console.log('NOTE: holder-history.json is managed by fetch-burn-history.js only');
  console.log('='.repeat(60));
}

main().catch(console.error);
