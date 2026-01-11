/**
 * Fetch Burn History Script - MORALIS VERSION
 * 
 * Uses Moralis API for reliable data fetching on PulseChain
 * 
 * Tracks:
 * 1. PTGC burns (all transfers to burn address)
 * 2. UFO burns (all transfers to burn address)
 * 3. PTGC Buyback Burns = PTGC burns FROM the LP pair (automated swaps)
 * 4. UFO Buyback Burns = UFO burns FROM the UFO LP pair
 * 
 * Also fetches: LP pairs, volume, holders, prices
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

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

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
 * Load existing data for incremental updates
 */
function loadExistingData(outputPath) {
  try {
    if (fs.existsSync(outputPath)) {
      const data = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
      console.log('Loaded existing data from:', data.lastUpdated);
      return data;
    }
  } catch (e) {
    console.log('Could not load existing data:', e.message);
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
  
  // Merge with existing burns
  const allBurns = [...newBurns, ...existingBurns];
  
  // Sort by timestamp descending (newest first)
  allBurns.sort((a, b) => b.t - a.t);
  
  console.log(`Total ${tokenSymbol} burns: ${allBurns.length}`);
  return allBurns;
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
  
  const result = {
    h12: { count: 0, amount: 0 },
    h24: { count: 0, amount: 0 },
    d7: { count: 0, amount: 0 },
    d30: { count: 0, amount: 0 }
  };
  
  for (const burn of burns) {
    const age = now - burn.t;
    if (age <= h12) { result.h12.count++; result.h12.amount += burn.a; }
    if (age <= h24) { result.h24.count++; result.h24.amount += burn.a; }
    if (age <= d7) { result.d7.count++; result.d7.amount += burn.a; }
    if (age <= d30) { result.d30.count++; result.d30.amount += burn.a; }
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
    
    const pairs = data.pairs.map(p => ({
      pairAddress: p.pair_address,
      exchange: p.exchange_name || 'Unknown',
      token0: p.pair?.[0]?.token_symbol,
      token1: p.pair?.[1]?.token_symbol,
      liquidity: p.liquidity_usd || 0,
      price: p.usd_price || 0,
      priceChange24h: p.usd_price_24hr_percent_change || 0
    }));
    
    const totalLiquidity = pairs.reduce((s, p) => s + p.liquidity, 0);
    console.log(`  Total liquidity: $${totalLiquidity.toLocaleString()}`);
    
    return {
      pairs,
      totalLiquidity
    };
  }
  
  return { pairs: [], totalLiquidity: 0 };
}

/**
 * Fetch token holder count from Moralis
 */
async function fetchHolderCount(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} holder stats...`);
  
  const data = await moralisRequest(`/erc20/${tokenAddress}/owners`, {
    chain: CHAIN,
    limit: 1
  });
  
  if (data) {
    // Moralis returns total in the response
    const holders = data.total || 0;
    console.log(`  ${tokenSymbol} holders: ${holders.toLocaleString()}`);
    return holders;
  }
  
  return 0;
}

/**
 * Fetch top token holders from Moralis
 */
async function fetchTopHolders(tokenAddress, tokenSymbol, limit = 100) {
  console.log(`\nFetching ${tokenSymbol} top holders...`);
  
  const data = await moralisRequest(`/erc20/${tokenAddress}/owners`, {
    chain: CHAIN,
    limit: limit,
    order: 'DESC'
  });
  
  if (data && data.result) {
    console.log(`  Got ${data.result.length} top holders`);
    return data.result.map(h => ({
      address: h.owner_address,
      balance: h.balance_formatted || 0,
      percentage: h.percentage_relative_to_total_supply || 0
    }));
  }
  
  return [];
}

/**
 * Main function
 */
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('BURN HISTORY FETCHER - MORALIS VERSION');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));
  
  const outputPath = path.join(__dirname, '..', 'data', 'burn-history.json');
  const existingData = loadExistingData(outputPath);
  
  // Get existing burns (for incremental update)
  const existingPTGCBurns = existingData?.PTGC?.burns || [];
  const existingUFOBurns = existingData?.UFO?.burns || [];
  
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
  
  const ptgcTotal = ptgcBurns.reduce((s, b) => s + b.a, 0);
  const ufoTotal = ufoBurns.reduce((s, b) => s + b.a, 0);
  const ptgcBuybackTotal = ptgcBuybackBurns.reduce((s, b) => s + b.a, 0);
  const ufoBuybackTotal = ufoBuybackBurns.reduce((s, b) => s + b.a, 0);
  
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
  
  const ptgcPairs = await fetchTokenPairs(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoPairs = await fetchTokenPairs(UFO_ADDRESS, 'UFO');
  await delay(300);
  
  const ptgcHolders = await fetchHolderCount(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoHolders = await fetchHolderCount(UFO_ADDRESS, 'UFO');
  
  // ============================================
  // BUILD SNAPSHOTS (for daily changes)
  // ============================================
  
  const today = new Date().toISOString().split('T')[0];
  const existingPTGCSnapshots = existingData?.PTGC?.snapshots || [];
  const existingUFOSnapshots = existingData?.UFO?.snapshots || [];
  
  const ptgcSnapshot = {
    date: today,
    holders: ptgcHolders,
    liquidity: ptgcPairs.totalLiquidity,
    price: ptgcPrice.usd
  };
  
  const ufoSnapshot = {
    date: today,
    holders: ufoHolders,
    liquidity: ufoPairs.totalLiquidity,
    price: ufoPrice.usd
  };
  
  const ptgcSnapshots = [ptgcSnapshot, ...existingPTGCSnapshots.filter(s => s.date !== today)].slice(0, 30);
  const ufoSnapshots = [ufoSnapshot, ...existingUFOSnapshots.filter(s => s.date !== today)].slice(0, 30);
  
  // Calculate changes vs yesterday
  const ptgcYesterday = ptgcSnapshots[1];
  const ufoYesterday = ufoSnapshots[1];
  
  const ptgcChanges = ptgcYesterday ? {
    holders: ptgcYesterday.holders ? ((ptgcHolders - ptgcYesterday.holders) / ptgcYesterday.holders * 100) : 0,
    liquidity: ptgcYesterday.liquidity ? ((ptgcSnapshot.liquidity - ptgcYesterday.liquidity) / ptgcYesterday.liquidity * 100) : 0
  } : null;
  
  const ufoChanges = ufoYesterday ? {
    holders: ufoYesterday.holders ? ((ufoHolders - ufoYesterday.holders) / ufoYesterday.holders * 100) : 0,
    liquidity: ufoYesterday.liquidity ? ((ufoSnapshot.liquidity - ufoYesterday.liquidity) / ufoYesterday.liquidity * 100) : 0
  } : null;
  
  // ============================================
  // BUILD OUTPUT
  // ============================================
  
  const outputData = {
    lastUpdated: new Date().toISOString(),
    dataSource: 'Moralis',
    
    PTGC: {
      totalBurned: ptgcTotal,
      burnCount: ptgcBurns.length,
      periods: ptgcPeriods,
      burns: ptgcBurns.map(b => ({ t: b.t, a: b.a, f: b.f })),
      price: ptgcPrice,
      pairs: ptgcPairs,
      holders: ptgcHolders,
      snapshots: ptgcSnapshots,
      changes: ptgcChanges
    },
    
    UFO: {
      totalBurned: ufoTotal,
      burnCount: ufoBurns.length,
      periods: ufoPeriods,
      burns: ufoBurns.map(b => ({ t: b.t, a: b.a, f: b.f })),
      price: ufoPrice,
      pairs: ufoPairs,
      holders: ufoHolders,
      snapshots: ufoSnapshots,
      changes: ufoChanges
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
  
  // ============================================
  // WRITE OUTPUT
  // ============================================
  
  const dataDir = path.dirname(outputPath);
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, JSON.stringify(outputData, null, 2));
  
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
  
  console.log(`\nUFO BURNS (all):`);
  console.log(`  Total: ${ufoTotal.toLocaleString()} tokens (${ufoBurns.length} txs)`);
  console.log(`  12H: ${ufoPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ufoPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ufoPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ufoPeriods.d30.amount.toLocaleString()}`);
  
  console.log(`\nPTGC BURNED BY UFO (buybacks from LP):`);
  console.log(`  Total: ${ptgcBuybackTotal.toLocaleString()} tokens (${ptgcBuybackBurns.length} txs)`);
  console.log(`  12H: ${ptgcBuybackPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ptgcBuybackPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ptgcBuybackPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ptgcBuybackPeriods.d30.amount.toLocaleString()}`);
  
  console.log(`\nUFO BUYBACK BURNS (from LP):`);
  console.log(`  Total: ${ufoBuybackTotal.toLocaleString()} tokens (${ufoBuybackBurns.length} txs)`);
  
  console.log(`\nPRICES:`);
  console.log(`  PTGC: $${ptgcPrice.usd}`);
  console.log(`  UFO: $${ufoPrice.usd}`);
  
  console.log(`\nHOLDERS:`);
  console.log(`  PTGC: ${ptgcHolders.toLocaleString()}`);
  console.log(`  UFO: ${ufoHolders.toLocaleString()}`);
  
  console.log('\n' + '='.repeat(60));
  console.log('Output written to:', outputPath);
  console.log('Completed:', new Date().toISOString());
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
