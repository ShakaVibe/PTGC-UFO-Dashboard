/**
 * CoinGecko Pro API Data Fetcher
 * 
 * Fetches volume, liquidity, and transaction data for PTGC and UFO tokens.
 * Runs every 30 minutes via GitHub Actions.
 * Stores timestamped snapshots for rolling window calculations.
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
  
  // Recent trades from last 24 hours
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
    poolCount: 0,
    errors: []
  };
  
  try {
    // Get all pools
    const pools = await fetchTokenPools(tokenConfig.address);
    result.poolCount = pools.length;
    console.log(`Found ${pools.length} pools`);
    await sleep(300);
    
    // Process each pool (limit to top 15 by liquidity)
    const poolsToProcess = pools.slice(0, 15);
    
    for (const poolData of poolsToProcess) {
      const poolAddress = poolData.id?.split('_')[1];
      if (!poolAddress) continue;
      
      const poolName = poolData.attributes?.name || 'Unknown';
      console.log(`  Processing: ${poolName} (${poolAddress.slice(0, 10)}...)`);
      
      try {
        // Get pool liquidity
        const poolInfo = await fetchPoolInfo(poolAddress);
        if (poolInfo) {
          const liq = parseFloat(poolInfo.reserve_in_usd) || 0;
          result.liquidity += liq;
          console.log(`    Liquidity: $${liq.toLocaleString()}`);
        }
        await sleep(300);
        
        // Get OHLCV for volume
        const ohlcv = await fetchOHLCV(poolAddress, 90);
        const vol = processVolume(ohlcv);
        result.volume.vol7d += vol.vol7d;
        result.volume.vol30d += vol.vol30d;
        result.volume.vol90d += vol.vol90d;
        console.log(`    7D Vol: $${vol.vol7d.toLocaleString()}`);
        await sleep(300);
        
        // Get trades for transaction counts
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
  console.log(`  Liquidity: $${result.liquidity.toLocaleString()}`);
  console.log(`  Volume 7D: $${result.volume.vol7d.toLocaleString()}`);
  console.log(`  Volume 30D: $${result.volume.vol30d.toLocaleString()}`);
  console.log(`  Transactions: ${result.transactions.total}`);
  
  return result;
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
  
  // Load existing histories
  const liquidityHistory = loadHistory('liquidity-history.json');
  const transactionHistory = loadHistory('transaction-history.json');
  
  // Fetch data for each token
  const tokenData = {};
  
  for (const [tokenName, tokenConfig] of Object.entries(CONFIG.tokens)) {
    tokenData[tokenName] = await fetchTokenData(tokenName, tokenConfig);
    await sleep(2000); // Pause between tokens
  }
  
  // Append to histories
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
  
  // Save history files
  liquidityHistory.lastUpdated = timestamp;
  transactionHistory.lastUpdated = timestamp;
  
  saveData('liquidity-history.json', liquidityHistory);
  saveData('transaction-history.json', transactionHistory);
  
  // Save current aggregates (volume periods + current snapshot)
  const coingeckoData = {
    lastUpdated: timestamp,
    PTGC: {
      volume: tokenData.PTGC.volume,
      liquidity: tokenData.PTGC.liquidity,
      transactions: tokenData.PTGC.transactions,
      poolCount: tokenData.PTGC.poolCount
    },
    UFO: {
      volume: tokenData.UFO.volume,
      liquidity: tokenData.UFO.liquidity,
      transactions: tokenData.UFO.transactions,
      poolCount: tokenData.UFO.poolCount
    }
  };
  
  saveData('coingecko-data.json', coingeckoData);
  
  console.log('\n' + '='.repeat(60));
  console.log('Fetch Complete!');
  console.log('='.repeat(60));
}

main().catch(console.error);
