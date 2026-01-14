/**
 * Fetch Burn History Script - MORALIS VERSION (SPLIT FILES)
 * 
 * Splits burn data into multiple files to stay under GitHub's 100MB limit
 * 
 * Files created:
 * - burn-summary.json (totals, prices, periods, snapshots)
 * - ptgc-burns-2023-h2.json (May-Dec 2023)
 * - ptgc-burns-2024-h1.json (Jan-Jun 2024)
 * - ptgc-burns-2024-h2.json (Jul-Dec 2024)
 * - ptgc-burns-2025-h1.json (Jan-Jun 2025)
 * - ptgc-burns-2025-h2.json (Jul-Dec 2025)
 * - ptgc-burns-2026.json (2026+, current file for updates)
 * - ufo-burns.json (all UFO burns - small file)
 */

const fs = require('fs');
const path = require('path');

// Moralis API Key - set via environment variable
const MORALIS_API_KEY = process.env.MORALIS_API_KEY;
if (!MORALIS_API_KEY) {
  console.error('ERROR: MORALIS_API_KEY environment variable not set');
  process.exit(1);
}

// PulseChain chain identifier for Moralis
const CHAIN = '0x171'; // PulseChain mainnet (369 in hex)

// Addresses
const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const UFO_ADDRESS = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018';

// LP Pairs (for identifying automated buyback burns)
const PTGC_LP_PAIR = '0xf5a89a6487d62df5308cdda89c566c5b5ef94c11';
const UFO_LP_PAIR = '0xbea0e55b82eb975280041f3b49c4d0bd937b72d5';

const PTGC_DECIMALS = 18;
const UFO_DECIMALS = 18;

const MORALIS_BASE = 'https://deep-index.moralis.io/api/v2.2';
const DEXSCREENER_BASE = 'https://api.dexscreener.com/latest/dex';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// Time period boundaries (timestamps)
const PERIODS = {
  '2023-h2': { start: new Date('2023-05-01').getTime(), end: new Date('2024-01-01').getTime() },
  '2024-h1': { start: new Date('2024-01-01').getTime(), end: new Date('2024-07-01').getTime() },
  '2024-h2': { start: new Date('2024-07-01').getTime(), end: new Date('2025-01-01').getTime() },
  '2025-h1': { start: new Date('2025-01-01').getTime(), end: new Date('2025-07-01').getTime() },
  '2025-h2': { start: new Date('2025-07-01').getTime(), end: new Date('2026-01-01').getTime() },
  '2026': { start: new Date('2026-01-01').getTime(), end: new Date('2030-01-01').getTime() }
};

/**
 * Get period key for a timestamp
 */
function getPeriodKey(timestamp) {
  for (const [key, range] of Object.entries(PERIODS)) {
    if (timestamp >= range.start && timestamp < range.end) {
      return key;
    }
  }
  return '2026'; // Default to current
}

/**
 * Make Moralis API request
 */
async function moralisRequest(endpoint, params = {}) {
  const url = new URL(`${MORALIS_BASE}${endpoint}`);
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null) url.searchParams.set(k, v);
  });
  
  try {
    const response = await fetch(url.toString(), {
      headers: {
        'X-API-Key': MORALIS_API_KEY,
        'Accept': 'application/json'
      }
    });
    
    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }
    
    return await response.json();
  } catch (error) {
    console.log(`  API Error: ${error.message}`);
    return null;
  }
}

/**
 * Fetch transaction count from DexScreener
 */
async function fetchTransactionCount(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} transaction count from DexScreener...`);
  
  try {
    const response = await fetch(`${DEXSCREENER_BASE}/tokens/${tokenAddress}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    
    if (data.pairs && data.pairs.length > 0) {
      // Sum up all transactions across all pairs
      let totalBuys = 0;
      let totalSells = 0;
      
      for (const pair of data.pairs) {
        totalBuys += pair.txns?.h24?.buys || 0;
        totalSells += pair.txns?.h24?.sells || 0;
      }
      
      const totalTxns = totalBuys + totalSells;
      console.log(`  ${tokenSymbol} 24h transactions: ${totalTxns} (${totalBuys} buys, ${totalSells} sells)`);
      
      return totalTxns;
    }
    
    return 0;
  } catch (error) {
    console.log(`  DexScreener Error: ${error.message}`);
    return 0;
  }
}

/**
 * Load existing burn files for a token
 */
function loadExistingBurns(dataDir, token) {
  let allBurns = [];
  console.log(`\nLoading existing ${token} burns...`);
  console.log(`  Data directory: ${dataDir}`);
  
  if (token === 'PTGC') {
    // Load all PTGC period files
    for (const period of Object.keys(PERIODS)) {
      const filePath = path.join(dataDir, `ptgc-burns-${period}.json`);
      console.log(`  Checking: ${filePath}`);
      try {
        if (fs.existsSync(filePath)) {
          const stats = fs.statSync(filePath);
          console.log(`    File exists, size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
          const fileContent = fs.readFileSync(filePath, 'utf8');
          console.log(`    Read ${fileContent.length} characters`);
          const data = JSON.parse(fileContent);
          console.log(`    Parsed JSON, burns array length: ${data.burns?.length || 0}`);
          if (data.burns && data.burns.length > 0) {
            // Use concat instead of spread to avoid stack overflow
            allBurns = allBurns.concat(data.burns);
            console.log(`    Added ${data.burns.length} burns, total now: ${allBurns.length}`);
          }
        } else {
          console.log(`    File does not exist`);
        }
      } catch (e) {
        console.log(`    ERROR loading ${filePath}: ${e.message}`);
        console.log(`    Stack: ${e.stack}`);
      }
    }
  } else {
    // Load UFO file
    const filePath = path.join(dataDir, 'ufo-burns.json');
    console.log(`  Checking: ${filePath}`);
    try {
      if (fs.existsSync(filePath)) {
        const stats = fs.statSync(filePath);
        console.log(`    File exists, size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
        const fileContent = fs.readFileSync(filePath, 'utf8');
        console.log(`    Read ${fileContent.length} characters`);
        const data = JSON.parse(fileContent);
        console.log(`    Parsed JSON, burns array length: ${data.burns?.length || 0}`);
        if (data.burns && data.burns.length > 0) {
          // Use concat instead of spread to avoid stack overflow
          allBurns = allBurns.concat(data.burns);
          console.log(`    Added ${data.burns.length} burns, total now: ${allBurns.length}`);
        }
      } else {
        console.log(`    File does not exist`);
      }
    } catch (e) {
      console.log(`    ERROR loading ${filePath}: ${e.message}`);
      console.log(`    Stack: ${e.stack}`);
    }
  }
  
  console.log(`  Total ${token} burns loaded from files: ${allBurns.length}`);
  
  // Sort by timestamp descending
  allBurns.sort((a, b) => b.t - a.t);
  
  // Log timestamp range
  if (allBurns.length > 0) {
    console.log(`  Oldest burn: ${new Date(allBurns[allBurns.length - 1].t).toISOString()}`);
    console.log(`  Newest burn: ${new Date(allBurns[0].t).toISOString()}`);
  }
  
  return allBurns;
}

/**
 * Load existing summary
 */
function loadExistingSummary(dataDir) {
  const filePath = path.join(dataDir, 'burn-summary.json');
  try {
    if (fs.existsSync(filePath)) {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
      console.log('Loaded existing summary from:', data.lastUpdated);
      return data;
    }
  } catch (e) {
    console.log('Could not load summary:', e.message);
  }
  return null;
}

/**
 * Fetch ALL token transfers to burn address using Moralis
 */
async function fetchAllBurns(tokenAddress, tokenSymbol, decimals, existingBurns = []) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Fetching ${tokenSymbol} burns via Moralis...`);
  console.log(`${'='.repeat(50)}`);
  
  // Get the most recent timestamp we have (for incremental updates)
  const lastTimestamp = existingBurns.length > 0 ? existingBurns[0].t : 0;
  if (lastTimestamp) {
    console.log(`Incremental mode: fetching after ${new Date(lastTimestamp).toISOString()}`);
  } else {
    console.log('Full fetch mode: getting all historical burns');
  }
  
  const newBurns = [];
  let cursor = null;
  let page = 0;
  let reachedOldData = false;
  
  while (!reachedOldData) {
    // Moralis endpoint for wallet token transfers (burn address is the wallet receiving)
    const data = await moralisRequest(`/${BURN_ADDRESS}/erc20/transfers`, {
      chain: CHAIN,
      contract_addresses: [tokenAddress],
      cursor: cursor,
      limit: 100
    });
    
    if (!data) {
      console.log(`  Page ${page + 1}: API error, retrying in 5s...`);
      await delay(5000);
      continue;
    }
    
    if (!data.result || data.result.length === 0) {
      console.log(`  No more data after page ${page + 1}`);
      break;
    }
    
    for (const tx of data.result) {
      const timestamp = new Date(tx.block_timestamp).getTime();
      
      // Stop if we've reached data we already have
      if (lastTimestamp && timestamp <= lastTimestamp) {
        console.log(`  Reached existing data at ${new Date(timestamp).toISOString()}`);
        reachedOldData = true;
        break;
      }
      
      const amount = Number(BigInt(tx.value || '0')) / Math.pow(10, decimals);
      const fromAddr = (tx.from_address || '').toLowerCase();
      
      newBurns.push({
        t: timestamp,
        a: amount,
        f: fromAddr
      });
    }
    
    // Log progress
    if (page % 10 === 0 || page < 5) {
      console.log(`  Page ${page + 1}: ${newBurns.length} new burns collected`);
    }
    
    // Check for next page
    cursor = data.cursor;
    if (!cursor || reachedOldData) {
      break;
    }
    
    page++;
    await delay(200); // Gentle rate limiting
  }
  
  console.log(`Fetched ${newBurns.length} new ${tokenSymbol} burns`);
  console.log(`Existing ${tokenSymbol} burns: ${existingBurns.length}`);
  
  // Merge with existing burns
  const allBurns = [...newBurns, ...existingBurns];
  
  // Sort by timestamp descending (newest first)
  allBurns.sort((a, b) => b.t - a.t);
  
  console.log(`Total ${tokenSymbol} burns after merge: ${allBurns.length}`);
  
  // Log timestamp range
  if (allBurns.length > 0) {
    console.log(`  Oldest: ${new Date(allBurns[allBurns.length - 1].t).toISOString()}`);
    console.log(`  Newest: ${new Date(allBurns[0].t).toISOString()}`);
  }
  
  return allBurns;
}

/**
 * Split burns into period files
 */
function splitBurnsByPeriod(burns) {
  const byPeriod = {};
  
  for (const period of Object.keys(PERIODS)) {
    byPeriod[period] = [];
  }
  
  for (const burn of burns) {
    const period = getPeriodKey(burn.t);
    byPeriod[period].push(burn);
  }
  
  return byPeriod;
}

/**
 * Filter burns that came from LP pair (these are buyback burns from swaps)
 */
function filterBuybackBurns(burns, lpPairAddress) {
  const lpAddr = lpPairAddress.toLowerCase();
  return burns.filter(b => b.f === lpAddr);
}

/**
 * Calculate period totals (12H, 24H, 7D, 30D)
 */
function calculatePeriods(burns) {
  const now = Date.now();
  const h12 = 12 * 60 * 60 * 1000;
  const h24 = 24 * 60 * 60 * 1000;
  const d7 = 7 * 24 * 60 * 60 * 1000;
  const d30 = 30 * 24 * 60 * 60 * 1000;
  const d90 = 90 * 24 * 60 * 60 * 1000;
  
  const result = {
    h12: { count: 0, amount: 0 },
    h24: { count: 0, amount: 0 },
    d7: { count: 0, amount: 0 },
    d30: { count: 0, amount: 0 },
    d90: { count: 0, amount: 0 }
  };
  
  for (const burn of burns) {
    const age = now - burn.t;
    if (age <= h12) { result.h12.count++; result.h12.amount += burn.a; }
    if (age <= h24) { result.h24.count++; result.h24.amount += burn.a; }
    if (age <= d7) { result.d7.count++; result.d7.amount += burn.a; }
    if (age <= d30) { result.d30.count++; result.d30.amount += burn.a; }
    if (age <= d90) { result.d90.count++; result.d90.amount += burn.a; }
  }
  
  return result;
}

/**
 * Fetch token price from Moralis
 */
async function fetchTokenPrice(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} price...`);
  
  const data = await moralisRequest(`/erc20/${tokenAddress}/price`, {
    chain: CHAIN,
    include: 'percent_change'
  });
  
  if (data) {
    const price = data.usdPrice || 0;
    console.log(`  ${tokenSymbol} price: $${price}`);
    return {
      usd: price,
      change24h: data['24hrPercentChange'] || 0
    };
  }
  
  return { usd: 0, change24h: 0 };
}

/**
 * Fetch volume stats from Moralis
 */
async function fetchVolumeStats(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} volume...`);
  
  const data = await moralisRequest(`/erc20/${tokenAddress}/analytics`, {
    chain: CHAIN
  });
  
  if (data) {
    console.log(`  ${tokenSymbol} 24h volume: $${data.totalVolume24h || 0}`);
    return {
      volume24h: data.totalVolume24h || 0,
      change24h: data.volumeChange24h || 0
    };
  }
  
  return { volume24h: 0, change24h: 0 };
}

/**
 * Fetch token pairs and liquidity from Moralis
 */
async function fetchTokenPairs(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} LP pairs...`);
  
  const data = await moralisRequest(`/erc20/${tokenAddress}/pairs`, {
    chain: CHAIN,
    limit: 50
  });
  
  if (data && data.pairs) {
    console.log(`  Found ${data.pairs.length} pairs`);
    
    let totalLiquidity = 0;
    let totalTokensInLP = 0;
    
    for (const pair of data.pairs) {
      totalLiquidity += pair.usdValueCombined || 0;
      
      // Find this token's reserve in the pair
      if (pair.token0 && pair.token0.address.toLowerCase() === tokenAddress.toLowerCase()) {
        totalTokensInLP += Number(pair.reserve0 || 0);
      } else if (pair.token1 && pair.token1.address.toLowerCase() === tokenAddress.toLowerCase()) {
        totalTokensInLP += Number(pair.reserve1 || 0);
      }
    }
    
    console.log(`  Total liquidity: $${totalLiquidity.toLocaleString()}`);
    
    return {
      pairs: data.pairs,
      totalLiquidity,
      totalTokensInLP
    };
  }
  
  return { pairs: [], totalLiquidity: 0, totalTokensInLP: 0 };
}

/**
 * Fetch holder count from Moralis
 */
async function fetchHolderCount(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} holder stats...`);
  
  const data = await moralisRequest(`/erc20/${tokenAddress}/owners`, {
    chain: CHAIN,
    limit: 1
  });
  
  if (data && data.totalHolders !== undefined) {
    console.log(`  ${tokenSymbol} holders: ${data.totalHolders}`);
    return data.totalHolders;
  }
  
  console.log(`  ${tokenSymbol} holders: 0`);
  return 0;
}

/**
 * Main function
 */
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('BURN HISTORY FETCHER - MORALIS VERSION (SPLIT FILES)');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));
  
  const dataDir = path.join(__dirname, '..', 'data');
  console.log(`\nData directory: ${dataDir}`);
  console.log(`Script directory: ${__dirname}`);
  
  // Ensure data directory exists
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
    console.log('Created data directory');
  }
  
  // List files in data directory
  console.log('\nFiles in data directory:');
  try {
    const files = fs.readdirSync(dataDir);
    for (const file of files) {
      const filePath = path.join(dataDir, file);
      const stats = fs.statSync(filePath);
      console.log(`  ${file} - ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
    }
  } catch (e) {
    console.log(`  ERROR listing directory: ${e.message}`);
  }
  
  // Load existing data
  const existingSummary = loadExistingSummary(dataDir);
  const existingPTGCBurns = loadExistingBurns(dataDir, 'PTGC');
  const existingUFOBurns = loadExistingBurns(dataDir, 'UFO');
  
  // ============================================
  // FETCH ALL BURNS
  // ============================================
  
  const ptgcBurns = await fetchAllBurns(PTGC_ADDRESS, 'PTGC', PTGC_DECIMALS, existingPTGCBurns);
  await delay(500);
  
  const ufoBurns = await fetchAllBurns(UFO_ADDRESS, 'UFO', UFO_DECIMALS, existingUFOBurns);
  await delay(500);
  
  // ============================================
  // IDENTIFY BUYBACK BURNS (from LP pairs)
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Identifying Buyback Burns...');
  console.log(`${'='.repeat(50)}`);
  
  const ptgcBuybackBurns = filterBuybackBurns(ptgcBurns, PTGC_LP_PAIR);
  console.log(`PTGC Buyback Burns (from LP): ${ptgcBuybackBurns.length} transactions`);
  
  const ufoBuybackBurns = filterBuybackBurns(ufoBurns, UFO_LP_PAIR);
  console.log(`UFO Buyback Burns (from LP): ${ufoBuybackBurns.length} transactions`);
  
  // ============================================
  // CALCULATE TOTALS AND PERIODS
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('CALCULATING PERIODS');
  console.log(`${'='.repeat(50)}`);
  console.log(`PTGC burns to process: ${ptgcBurns.length}`);
  console.log(`UFO burns to process: ${ufoBurns.length}`);
  
  const ptgcTotal = ptgcBurns.reduce((s, b) => s + b.a, 0);
  const ufoTotal = ufoBurns.reduce((s, b) => s + b.a, 0);
  const ptgcBuybackTotal = ptgcBuybackBurns.reduce((s, b) => s + b.a, 0);
  const ufoBuybackTotal = ufoBuybackBurns.reduce((s, b) => s + b.a, 0);
  
  console.log(`PTGC total tokens: ${ptgcTotal.toLocaleString()}`);
  console.log(`UFO total tokens: ${ufoTotal.toLocaleString()}`);
  
  const ptgcPeriods = calculatePeriods(ptgcBurns);
  const ufoPeriods = calculatePeriods(ufoBurns);
  const ptgcBuybackPeriods = calculatePeriods(ptgcBuybackBurns);
  const ufoBuybackPeriods = calculatePeriods(ufoBuybackBurns);
  
  // ============================================
  // FETCH ADDITIONAL DATA
  // ============================================
  
  const ptgcPrice = await fetchTokenPrice(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoPrice = await fetchTokenPrice(UFO_ADDRESS, 'UFO');
  await delay(300);
  
  const ptgcVolume = await fetchVolumeStats(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoVolume = await fetchVolumeStats(UFO_ADDRESS, 'UFO');
  await delay(300);
  
  const ptgcPairs = await fetchTokenPairs(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoPairs = await fetchTokenPairs(UFO_ADDRESS, 'UFO');
  await delay(300);
  
  const ptgcHolders = await fetchHolderCount(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoHolders = await fetchHolderCount(UFO_ADDRESS, 'UFO');
  await delay(300);
  
  // Fetch transaction counts from DexScreener
  const ptgcTxns = await fetchTransactionCount(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoTxns = await fetchTransactionCount(UFO_ADDRESS, 'UFO');
  
  // Get tokens in LP from pairs data
  const ptgcTokensInLP = ptgcPairs.totalTokensInLP || 0;
  const ufoTokensInLP = ufoPairs.totalTokensInLP || 0;

  // ============================================
  // BUILD SNAPSHOTS (for daily changes)
  // ============================================
  
  const today = new Date().toISOString().split('T')[0];
  const existingPTGCSnapshots = existingSummary?.PTGC?.snapshots || [];
  const existingUFOSnapshots = existingSummary?.UFO?.snapshots || [];
  
  const ptgcSnapshot = {
    date: today,
    holders: ptgcHolders,
    liquidity: ptgcPairs.totalLiquidity,
    price: ptgcPrice.usd,
    volume: ptgcVolume.volume24h,
    tokensInLP: ptgcTokensInLP,
    txns: ptgcTxns
  };
  
  const ufoSnapshot = {
    date: today,
    holders: ufoHolders,
    liquidity: ufoPairs.totalLiquidity,
    price: ufoPrice.usd,
    volume: ufoVolume.volume24h,
    tokensInLP: ufoTokensInLP,
    txns: ufoTxns
  };
  
  const ptgcSnapshots = [ptgcSnapshot, ...existingPTGCSnapshots.filter(s => s.date !== today)].slice(0, 30);
  const ufoSnapshots = [ufoSnapshot, ...existingUFOSnapshots.filter(s => s.date !== today)].slice(0, 30);
  
  // Calculate changes vs yesterday
  const ptgcYesterday = ptgcSnapshots[1];
  const ufoYesterday = ufoSnapshots[1];
  
  const ptgcChanges = ptgcYesterday ? {
    holders: ptgcYesterday.holders ? ((ptgcHolders - ptgcYesterday.holders) / ptgcYesterday.holders * 100) : 0,
    liquidity: ptgcYesterday.liquidity ? ((ptgcSnapshot.liquidity - ptgcYesterday.liquidity) / ptgcYesterday.liquidity * 100) : 0,
    tokensInLP: ptgcYesterday.tokensInLP ? ((ptgcTokensInLP - ptgcYesterday.tokensInLP) / ptgcYesterday.tokensInLP * 100) : 0,
    txns: ptgcYesterday.txns ? ((ptgcTxns - ptgcYesterday.txns) / ptgcYesterday.txns * 100) : 0
  } : null;
  
  const ufoChanges = ufoYesterday ? {
    holders: ufoYesterday.holders ? ((ufoHolders - ufoYesterday.holders) / ufoYesterday.holders * 100) : 0,
    liquidity: ufoYesterday.liquidity ? ((ufoSnapshot.liquidity - ufoYesterday.liquidity) / ufoYesterday.liquidity * 100) : 0,
    tokensInLP: ufoYesterday.tokensInLP ? ((ufoTokensInLP - ufoYesterday.tokensInLP) / ufoYesterday.tokensInLP * 100) : 0,
    txns: ufoYesterday.txns ? ((ufoTxns - ufoYesterday.txns) / ufoYesterday.txns * 100) : 0
  } : null;
  
  // ============================================
  // SPLIT PTGC BURNS BY PERIOD
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Splitting burns by time period...');
  console.log(`${'='.repeat(50)}`);
  
  const ptgcBurnsByPeriod = splitBurnsByPeriod(ptgcBurns);
  
  for (const [period, burns] of Object.entries(ptgcBurnsByPeriod)) {
    console.log(`  ${period}: ${burns.length} burns`);
  }
  
  // ============================================
  // WRITE PTGC BURN FILES (by period)
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Writing PTGC burn files...');
  console.log(`${'='.repeat(50)}`);
  
  for (const [period, burns] of Object.entries(ptgcBurnsByPeriod)) {
    if (burns.length === 0) continue;
    
    const filePath = path.join(dataDir, `ptgc-burns-${period}.json`);
    const periodTotal = burns.reduce((s, b) => s + b.a, 0);
    
    const fileData = {
      period,
      burnCount: burns.length,
      totalBurned: periodTotal,
      burns: burns.map(b => ({ t: b.t, a: b.a, f: b.f }))
    };
    
    fs.writeFileSync(filePath, JSON.stringify(fileData));
    const fileSizeMB = (fs.statSync(filePath).size / (1024 * 1024)).toFixed(2);
    console.log(`  Written: ${filePath} (${fileSizeMB} MB, ${burns.length} burns)`);
  }
  
  // ============================================
  // WRITE UFO BURNS FILE
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Writing UFO burns file...');
  console.log(`${'='.repeat(50)}`);
  
  const ufoFilePath = path.join(dataDir, 'ufo-burns.json');
  const ufoFileData = {
    burnCount: ufoBurns.length,
    totalBurned: ufoTotal,
    burns: ufoBurns.map(b => ({ t: b.t, a: b.a, f: b.f }))
  };
  
  fs.writeFileSync(ufoFilePath, JSON.stringify(ufoFileData));
  const ufoFileSizeMB = (fs.statSync(ufoFilePath).size / (1024 * 1024)).toFixed(2);
  console.log(`  Written: ${ufoFilePath} (${ufoFileSizeMB} MB, ${ufoBurns.length} burns)`);
  
  // ============================================
  // WRITE SUMMARY FILE
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Writing summary file...');
  console.log(`${'='.repeat(50)}`);
  
  const summaryData = {
    lastUpdated: new Date().toISOString(),
    dataSource: 'Moralis',
    
    PTGC: {
      totalBurned: ptgcTotal,
      burnCount: ptgcBurns.length,
      periods: ptgcPeriods,
      price: ptgcPrice,
      volume: {
        usd24h: ptgcVolume.volume24h,
        change24h: ptgcVolume.change24h
      },
      pairs: ptgcPairs,
      holders: ptgcHolders,
      tokensInLP: ptgcTokensInLP,
      txns: ptgcTxns,
      snapshots: ptgcSnapshots,
      changes: ptgcChanges,
      // File references for loading burns
      burnFiles: Object.keys(PERIODS).map(p => `ptgc-burns-${p}.json`).filter(f => 
        fs.existsSync(path.join(dataDir, f))
      )
    },
    
    UFO: {
      totalBurned: ufoTotal,
      burnCount: ufoBurns.length,
      periods: ufoPeriods,
      price: ufoPrice,
      volume: {
        usd24h: ufoVolume.volume24h,
        change24h: ufoVolume.change24h
      },
      pairs: ufoPairs,
      holders: ufoHolders,
      tokensInLP: ufoTokensInLP,
      txns: ufoTxns,
      snapshots: ufoSnapshots,
      changes: ufoChanges,
      burnFile: 'ufo-burns.json'
    },
    
    // PTGC burned via automated buybacks (from LP swaps)
    PTGCbyUFO: {
      totalBurned: ptgcBuybackTotal,
      burnCount: ptgcBuybackBurns.length,
      periods: ptgcBuybackPeriods
    },
    
    // UFO burned via automated buybacks (from LP swaps)
    UFOBuybacks: {
      totalBurned: ufoBuybackTotal,
      burnCount: ufoBuybackBurns.length,
      periods: ufoBuybackPeriods
    }
  };
  
  const summaryPath = path.join(dataDir, 'burn-summary.json');
  fs.writeFileSync(summaryPath, JSON.stringify(summaryData, null, 2));
  const summarySizeMB = (fs.statSync(summaryPath).size / (1024 * 1024)).toFixed(2);
  console.log(`  Written: ${summaryPath} (${summarySizeMB} MB)`);
  
  // ============================================
  // PRINT SUMMARY
  // ============================================
  
  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  
  console.log(`\nPTGC BURNS (all):`);
  console.log(`  Total: ${ptgcTotal.toLocaleString()} tokens (${ptgcBurns.length} txs)`);
  console.log(`  12H: ${ptgcPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ptgcPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ptgcPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ptgcPeriods.d30.amount.toLocaleString()}`);
  console.log(`  90D: ${ptgcPeriods.d90.amount.toLocaleString()}`);
  
  console.log(`\nUFO BURNS (all):`);
  console.log(`  Total: ${ufoTotal.toLocaleString()} tokens (${ufoBurns.length} txs)`);
  console.log(`  12H: ${ufoPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ufoPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ufoPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ufoPeriods.d30.amount.toLocaleString()}`);
  console.log(`  90D: ${ufoPeriods.d90.amount.toLocaleString()}`);
  
  console.log(`\nPTGC BURNED BY UFO (buybacks from LP):`);
  console.log(`  Total: ${ptgcBuybackTotal.toLocaleString()} tokens (${ptgcBuybackBurns.length} txs)`);
  console.log(`  12H: ${ptgcBuybackPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ptgcBuybackPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ptgcBuybackPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ptgcBuybackPeriods.d30.amount.toLocaleString()}`);
  console.log(`  90D: ${ptgcBuybackPeriods.d90.amount.toLocaleString()}`);
  
  console.log(`\nUFO BUYBACK BURNS (from LP):`);
  console.log(`  Total: ${ufoBuybackTotal.toLocaleString()} tokens (${ufoBuybackBurns.length} txs)`);
  
  console.log(`\nPRICES:`);
  console.log(`  PTGC: $${ptgcPrice.usd}`);
  console.log(`  UFO: $${ufoPrice.usd}`);
  
  console.log(`\nHOLDERS:`);
  console.log(`  PTGC: ${ptgcHolders.toLocaleString()}`);
  console.log(`  UFO: ${ufoHolders.toLocaleString()}`);
  
  console.log(`\nTRANSACTIONS (24H):`);
  console.log(`  PTGC: ${ptgcTxns}`);
  console.log(`  UFO: ${ufoTxns}`);
  
  if (ptgcChanges) {
    console.log(`\nPTGC CHANGES vs YESTERDAY:`);
    console.log(`  Txns: ${ptgcChanges.txns.toFixed(1)}%`);
  }
  
  if (ufoChanges) {
    console.log(`\nUFO CHANGES vs YESTERDAY:`);
    console.log(`  Txns: ${ufoChanges.txns.toFixed(1)}%`);
  }
  
  console.log('\n' + '='.repeat(60));
  console.log('FILES WRITTEN:');
  for (const period of Object.keys(PERIODS)) {
    const f = path.join(dataDir, `ptgc-burns-${period}.json`);
    if (fs.existsSync(f)) console.log(`  - ptgc-burns-${period}.json`);
  }
  console.log('  - ufo-burns.json');
  console.log('  - burn-summary.json');
  console.log('Completed:', new Date().toISOString());
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
