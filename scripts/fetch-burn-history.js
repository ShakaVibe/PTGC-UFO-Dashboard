/**
 * Fetch Burn History Script v3
 * 
 * Tracks:
 * 1. ALL PTGC burns (transfers to burn address)
 * 2. ALL UFO burns (transfers to burn address)
 * 3. PTGC Buyback Burns = PTGC burns FROM the PTGC LP pair (automated swaps)
 * 4. UFO Buyback Burns = UFO burns FROM the UFO LP pair (automated swaps)
 * 
 * Key insight: When buybackBurnpTGC() runs, PTGC goes from LP pair → burn address
 * So we can directly measure PTGC burned by UFO by checking the "from" address!
 * 
 * Runs via GitHub Actions every hour.
 */

const fs = require('fs');
const path = require('path');

// Addresses
const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const UFO_ADDRESS = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018';

// LP Pairs - burns FROM these addresses are automated buyback burns
const PTGC_LP_PAIR = '0xf5a89a6487d62df5308cdda89c566c5b5ef94c11'; // PTGC/WPLS
const UFO_LP_PAIR = '0xbea0e55b82eb975280041f3b49c4d0bd937b72d5';  // UFO/PLS

const PTGC_DECIMALS = 18;
const UFO_DECIMALS = 18;

const API_BASE = 'https://api.scan.pulsechain.com/api/v2';
const GECKO_API = 'https://api.geckoterminal.com/api/v2';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Fetch with retry and better error handling
 */
async function fetchWithRetry(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const text = await response.text();
      if (text.startsWith('<') || text.includes('Internal Server Error')) {
        throw new Error('Server returned HTML/error');
      }
      return JSON.parse(text);
    } catch (error) {
      console.log(`  Attempt ${i + 1}/${retries} failed: ${error.message}`);
      if (i < retries - 1) await delay(2000 * (i + 1)); // Exponential backoff
    }
  }
  return null;
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
 * Extract "from" address from API response (handles different field names)
 */
function getFromAddress(tx) {
  if (tx.from?.hash) return tx.from.hash.toLowerCase();
  if (tx.from?.address) return tx.from.address.toLowerCase();
  if (typeof tx.from === 'string') return tx.from.toLowerCase();
  return '';
}

/**
 * Fetch ALL token burns to burn address
 * Saves "from" address to identify buyback burns
 */
async function fetchAllBurns(tokenAddress, tokenSymbol, decimals, existingBurns = []) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Fetching ${tokenSymbol} burns...`);
  console.log(`${'='.repeat(50)}`);
  
  // Find most recent timestamp we have (for incremental updates)
  const lastTimestamp = existingBurns.length > 0 ? existingBurns[0].t : 0;
  if (lastTimestamp) {
    console.log(`Incremental mode: fetching after ${new Date(lastTimestamp).toISOString()}`);
  } else {
    console.log('Full fetch mode: getting all historical burns');
  }
  
  const newBurns = [];
  let nextPageParams = null;
  let page = 0;
  let reachedOldData = false;
  let consecutiveErrors = 0;
  
  while (!reachedOldData && consecutiveErrors < 5) {
    const url = nextPageParams
      ? `${API_BASE}/tokens/${tokenAddress}/transfers?to_address_hash=${BURN_ADDRESS}&${nextPageParams}`
      : `${API_BASE}/tokens/${tokenAddress}/transfers?to_address_hash=${BURN_ADDRESS}`;
    
    const data = await fetchWithRetry(url);
    
    if (!data) {
      consecutiveErrors++;
      console.log(`  Page ${page + 1}: ERROR (attempt ${consecutiveErrors}/5)`);
      await delay(3000);
      continue;
    }
    
    consecutiveErrors = 0;
    
    if (!data.items || data.items.length === 0) {
      console.log(`  Page ${page + 1}: No more data`);
      break;
    }
    
    for (const tx of data.items) {
      const timestamp = new Date(tx.timestamp).getTime();
      
      // Stop if we've reached data we already have
      if (lastTimestamp && timestamp <= lastTimestamp) {
        console.log(`  Reached existing data at ${new Date(timestamp).toISOString()}`);
        reachedOldData = true;
        break;
      }
      
      const amount = Number(BigInt(tx.total?.value || '0')) / Math.pow(10, decimals);
      const fromAddr = getFromAddress(tx);
      
      newBurns.push({
        t: timestamp,
        a: amount,
        f: fromAddr // Save "from" address for buyback detection
      });
    }
    
    // Log progress
    if (page % 25 === 0 || page < 5) {
      console.log(`  Page ${page + 1}: ${newBurns.length} new burns collected`);
    }
    
    // Get next page
    if (data.next_page_params && !reachedOldData) {
      const params = new URLSearchParams();
      Object.entries(data.next_page_params).forEach(([k, v]) => params.set(k, v));
      nextPageParams = params.toString();
    } else {
      break;
    }
    
    page++;
    await delay(300);
  }
  
  console.log(`Fetched ${newBurns.length} new ${tokenSymbol} burns`);
  
  // Merge with existing burns
  // Convert existing burns to have "f" field if missing
  const normalizedExisting = existingBurns.map(b => ({
    t: b.t,
    a: b.a,
    f: b.f || '' // Old data won't have "f", default to empty
  }));
  
  const allBurns = [...newBurns, ...normalizedExisting];
  
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
  const buybacks = burns.filter(b => b.f === lpAddr);
  return buybacks;
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
 * Fetch volume data from GeckoTerminal
 */
async function fetchVolumeData(poolAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} volume data...`);
  
  try {
    const url = `${GECKO_API}/networks/pulsechain/pools/${poolAddress}/ohlcv/day?aggregate=1&limit=90`;
    const data = await fetchWithRetry(url);
    
    if (!data?.data?.attributes?.ohlcv_list) {
      console.log(`  No volume data available`);
      return null;
    }
    
    const ohlcv = data.data.attributes.ohlcv_list;
    const history = ohlcv.map(c => ({
      t: c[0] * 1000, // Convert to milliseconds
      v: c[5],        // Volume
      c: c[4]         // Close price
    })).sort((a, b) => b.t - a.t);
    
    const vol24h = history[0]?.v || 0;
    const volYesterday = history[1]?.v || 0;
    const vol7d = history.slice(0, 7).reduce((s, v) => s + v.v, 0);
    const vol30d = history.slice(0, 30).reduce((s, v) => s + v.v, 0);
    const change24h = volYesterday > 0 ? ((vol24h - volYesterday) / volYesterday) * 100 : 0;
    
    console.log(`  24H: $${vol24h.toLocaleString()}, 7D: $${vol7d.toLocaleString()}`);
    
    return { current24h: vol24h, yesterday24h: volYesterday, change24h, vol7d, vol30d, history: history.slice(0, 90) };
  } catch (e) {
    console.log(`  Error: ${e.message}`);
    return null;
  }
}

/**
 * Fetch pool data (liquidity, price)
 */
async function fetchPoolData(poolAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} pool data...`);
  
  try {
    const data = await fetchWithRetry(`${GECKO_API}/networks/pulsechain/pools/${poolAddress}`);
    
    if (!data?.data?.attributes) {
      console.log(`  No pool data available`);
      return null;
    }
    
    const attrs = data.data.attributes;
    const result = {
      liquidity: parseFloat(attrs.reserve_in_usd) || 0,
      volume24h: parseFloat(attrs.volume_usd?.h24) || 0,
      priceUsd: parseFloat(attrs.base_token_price_usd) || 0,
      priceChange24h: parseFloat(attrs.price_change_percentage?.h24) || 0
    };
    
    console.log(`  Price: $${result.priceUsd}, Liquidity: $${result.liquidity.toLocaleString()}`);
    return result;
  } catch (e) {
    console.log(`  Error: ${e.message}`);
    return null;
  }
}

/**
 * Fetch holder count
 */
async function fetchHolderCount(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} holder count...`);
  
  try {
    const data = await fetchWithRetry(`${API_BASE}/tokens/${tokenAddress}/counters`);
    const holders = parseInt(data?.token_holders_count) || 0;
    console.log(`  Holders: ${holders.toLocaleString()}`);
    return holders;
  } catch (e) {
    console.log(`  Error: ${e.message}`);
    return 0;
  }
}

/**
 * Main function
 */
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('BURN HISTORY FETCHER v3');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));
  
  const outputPath = path.join(__dirname, '..', 'data', 'burn-history.json');
  const existingData = loadExistingData(outputPath);
  
  // Get existing burns (with "f" field if available)
  const existingPTGCBurns = existingData?.PTGC?.burns || [];
  const existingUFOBurns = existingData?.UFO?.burns || [];
  
  // ============================================
  // FETCH ALL BURNS
  // ============================================
  
  const ptgcBurns = await fetchAllBurns(PTGC_ADDRESS, 'PTGC', PTGC_DECIMALS, existingPTGCBurns);
  await delay(1000);
  
  const ufoBurns = await fetchAllBurns(UFO_ADDRESS, 'UFO', UFO_DECIMALS, existingUFOBurns);
  await delay(1000);
  
  // ============================================
  // IDENTIFY BUYBACK BURNS (from LP pairs)
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Identifying Buyback Burns...');
  console.log(`${'='.repeat(50)}`);
  
  // PTGC buyback burns = PTGC that came FROM the PTGC LP pair
  // This is what happens when UFO's buybackBurnpTGC() runs
  const ptgcBuybackBurns = filterBuybackBurns(ptgcBurns, PTGC_LP_PAIR);
  console.log(`PTGC Buyback Burns (from LP): ${ptgcBuybackBurns.length} transactions`);
  
  // UFO buyback burns = UFO that came FROM the UFO LP pair
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
  
  const ptgcVolume = await fetchVolumeData(PTGC_LP_PAIR, 'PTGC');
  await delay(2000);
  
  const ufoVolume = await fetchVolumeData(UFO_LP_PAIR, 'UFO');
  await delay(2000);
  
  const ptgcPool = await fetchPoolData(PTGC_LP_PAIR, 'PTGC');
  await delay(2000);
  
  const ufoPool = await fetchPoolData(UFO_LP_PAIR, 'UFO');
  await delay(1000);
  
  const ptgcHolders = await fetchHolderCount(PTGC_ADDRESS, 'PTGC');
  await delay(500);
  
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
    liquidity: ptgcPool?.liquidity || 0,
    price: ptgcPool?.priceUsd || 0
  };
  
  const ufoSnapshot = {
    date: today,
    holders: ufoHolders,
    liquidity: ufoPool?.liquidity || 0,
    price: ufoPool?.priceUsd || 0
  };
  
  // Keep last 30 days of snapshots
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
    
    PTGC: {
      totalBurned: ptgcTotal,
      burnCount: ptgcBurns.length,
      periods: ptgcPeriods,
      burns: ptgcBurns.map(b => ({ t: b.t, a: b.a, f: b.f })), // Keep "f" for buyback detection
      volume: ptgcVolume,
      pool: ptgcPool,
      snapshots: ptgcSnapshots,
      changes: ptgcChanges
    },
    
    UFO: {
      totalBurned: ufoTotal,
      burnCount: ufoBurns.length,
      periods: ufoPeriods,
      burns: ufoBurns.map(b => ({ t: b.t, a: b.a, f: b.f })), // Keep "f" for buyback detection
      volume: ufoVolume,
      pool: ufoPool,
      snapshots: ufoSnapshots,
      changes: ufoChanges
    },
    
    // PTGC burned via automated buybacks (from LP swaps)
    // This is "PTGC Burned by UFO" - directly measured!
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
  
  console.log('\n' + '='.repeat(60));
  console.log('Output written to:', outputPath);
  console.log('Completed:', new Date().toISOString());
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
