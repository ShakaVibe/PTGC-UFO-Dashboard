/**
 * Fetch Burn History Script - OPTIMIZED VERSION
 * 
 * This script fetches burn data for PTGC and UFO tokens.
 * 
 * Strategy for "PTGC burned by UFO":
 * - Query UFO contract's outgoing transactions
 * - Find ones that resulted in PTGC burns (buybackBurnpTGC calls)
 * - This is MUCH faster than checking each of 25,000+ PTGC burns
 * 
 * Run via GitHub Actions every 6 hours.
 */

const fs = require('fs');
const path = require('path');

const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const UFO_ADDRESS = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018';
const UFO_CONTRACT = '0x456548a9b56efbbd89ca0309edd17a9e20b04018';

// Main LP pairs for volume tracking
const PTGC_MAIN_PAIR = '0x322e03542678a8e2e926fdd2b5eb0b49ede10c74'; // PTGC/WPLS
const UFO_MAIN_PAIR = '0x33A8348bAb77cf17d4979c34b7EBB6ca4CF78257';  // UFO/WPLS

const PTGC_DECIMALS = 18;
const UFO_DECIMALS = 18;

const API_BASE = 'https://api.scan.pulsechain.com/api/v2';
const GECKO_API = 'https://api.geckoterminal.com/api/v2';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// Fetch with retry logic
async function fetchWithRetry(url, retries = 3) {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url);
      const text = await response.text();
      
      // Check if we got HTML instead of JSON (rate limit error)
      if (text.startsWith('<')) {
        throw new Error('Got HTML instead of JSON - likely rate limited');
      }
      
      return JSON.parse(text);
    } catch (error) {
      console.log(`    Retry ${i + 1}/${retries}: ${error.message}`);
      if (i < retries - 1) {
        await delay(2000); // Wait 2 seconds before retry
      }
    }
  }
  return null; // Return null if all retries failed
}

/**
 * Load existing burn history to append to (incremental updates)
 */
function loadExistingData(outputPath) {
  try {
    if (fs.existsSync(outputPath)) {
      const data = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
      console.log('Loaded existing data, last updated:', data.lastUpdated);
      return data;
    }
  } catch (e) {
    console.log('No existing data or error loading:', e.message);
  }
  return null;
}

/**
 * Fetch token transfers to burn address - with incremental support
 */
async function fetchBurnTransfers(tokenAddress, tokenSymbol, decimals, lastTimestamp = 0) {
  console.log(`\nFetching ${tokenSymbol} burns${lastTimestamp ? ' (incremental, after ' + new Date(lastTimestamp).toISOString() + ')' : ''}...`);
  
  const burns = [];
  let nextPageParams = null;
  let page = 0;
  const maxPages = 1000; // Increased limit
  let reachedOldData = false;
  let consecutiveErrors = 0;
  
  while (page < maxPages && !reachedOldData && consecutiveErrors < 5) {
    const url = nextPageParams
      ? `${API_BASE}/addresses/${BURN_ADDRESS}/token-transfers?type=ERC-20&token=${tokenAddress}&${nextPageParams}`
      : `${API_BASE}/addresses/${BURN_ADDRESS}/token-transfers?type=ERC-20&token=${tokenAddress}`;
    
    const data = await fetchWithRetry(url);
    
    if (!data) {
      consecutiveErrors++;
      console.log(`    Failed to fetch page ${page + 1}, consecutive errors: ${consecutiveErrors}`);
      await delay(3000); // Wait 3 seconds after failed page
      continue;
    }
    
    consecutiveErrors = 0; // Reset on success
    
    if (!data.items || !Array.isArray(data.items) || data.items.length === 0) {
      break;
    }
    
    for (const tx of data.items) {
      const toAddr = (tx.to?.hash || '').toLowerCase();
      if (toAddr !== BURN_ADDRESS.toLowerCase()) continue;
      
      const timestamp = new Date(tx.timestamp).getTime();
      
      // If incremental and we've reached data we already have, stop
      if (lastTimestamp && timestamp <= lastTimestamp) {
        reachedOldData = true;
        break;
      }
      
      burns.push({
        timestamp,
        amount: Number(BigInt(tx.total?.value || tx.value || '0')) / Math.pow(10, decimals),
        txHash: tx.transaction_hash,
        from: (tx.from?.hash || '').toLowerCase()
      });
    }
    
    if (page % 50 === 0 || page < 5) {
      console.log(`  Page ${page + 1}: ${burns.length} burns collected`);
    }
    
    if (data.next_page_params && !reachedOldData) {
      const params = new URLSearchParams();
      Object.entries(data.next_page_params).forEach(([k, v]) => params.set(k, v));
      nextPageParams = params.toString();
    } else {
      break;
    }
    
    page++;
    await delay(300); // Slower delay - 300ms between requests
  }
  
  console.log(`  Fetched ${burns.length} ${reachedOldData ? 'new ' : ''}burns`);
  return burns;
}

/**
 * Fetch PTGC burns initiated by UFO contract
 * Query UFO contract's transactions and find PTGC token transfers in the same tx
 */
async function fetchPTGCBurnsByUFO(lastTimestamp = 0) {
  console.log(`\nFetching PTGC burns by UFO contract...`);
  
  const burns = [];
  let nextPageParams = null;
  let page = 0;
  const maxPages = 500;
  let reachedOldData = false;
  let consecutiveErrors = 0;
  
  // Get all token transfers where UFO contract was involved
  while (page < maxPages && !reachedOldData && consecutiveErrors < 5) {
    const url = nextPageParams
      ? `${API_BASE}/addresses/${UFO_CONTRACT}/token-transfers?type=ERC-20&token=${PTGC_ADDRESS}&${nextPageParams}`
      : `${API_BASE}/addresses/${UFO_CONTRACT}/token-transfers?type=ERC-20&token=${PTGC_ADDRESS}`;
    
    const data = await fetchWithRetry(url);
    
    if (!data) {
      consecutiveErrors++;
      console.log(`    Failed to fetch page ${page + 1}, consecutive errors: ${consecutiveErrors}`);
      await delay(3000);
      continue;
    }
    
    consecutiveErrors = 0;
    
    if (!data.items || !Array.isArray(data.items) || data.items.length === 0) {
      // No direct transfers, try a different approach - check transactions
      break;
    }
    
    for (const tx of data.items) {
      const timestamp = new Date(tx.timestamp).getTime();
      
      if (lastTimestamp && timestamp <= lastTimestamp) {
        reachedOldData = true;
        break;
      }
      
      // Check if this transfer went to burn address
      const toAddr = (tx.to?.hash || '').toLowerCase();
      if (toAddr === BURN_ADDRESS.toLowerCase()) {
        burns.push({
          timestamp,
          amount: Number(BigInt(tx.total?.value || tx.value || '0')) / Math.pow(10, PTGC_DECIMALS),
          txHash: tx.transaction_hash
        });
      }
    }
    
    console.log(`  Page ${page + 1}: ${burns.length} UFO->PTGC burns found`);
    
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
  
  // If no results from token-transfers, try internal-transactions approach
  if (burns.length === 0) {
    console.log('  Trying alternative approach via transactions...');
    burns.push(...await fetchPTGCBurnsByUFOViaTransactions(lastTimestamp));
  }
  
  console.log(`  Total PTGC burned by UFO: ${burns.length} transactions`);
  return burns;
}

/**
 * Alternative: Check UFO contract transactions for PTGC burns
 */
async function fetchPTGCBurnsByUFOViaTransactions(lastTimestamp = 0) {
  const burns = [];
  let nextPageParams = null;
  let page = 0;
  const maxPages = 200;
  let reachedOldData = false;
  let consecutiveErrors = 0;
  
  while (page < maxPages && !reachedOldData && consecutiveErrors < 5) {
    const url = nextPageParams
      ? `${API_BASE}/addresses/${UFO_CONTRACT}/transactions?${nextPageParams}`
      : `${API_BASE}/addresses/${UFO_CONTRACT}/transactions`;
    
    const data = await fetchWithRetry(url);
    
    if (!data) {
      consecutiveErrors++;
      await delay(3000);
      continue;
    }
    
    consecutiveErrors = 0;
    
    if (!data.items || data.items.length === 0) break;
    
    for (const tx of data.items) {
      const timestamp = new Date(tx.timestamp).getTime();
      
      if (lastTimestamp && timestamp <= lastTimestamp) {
        reachedOldData = true;
        break;
      }
      
      // Check if this transaction has token transfers
      if (tx.token_transfers && tx.token_transfers.length > 0) {
        for (const transfer of tx.token_transfers) {
          const tokenAddr = (transfer.token?.address || '').toLowerCase();
          const toAddr = (transfer.to?.hash || '').toLowerCase();
          
          if (tokenAddr === PTGC_ADDRESS.toLowerCase() && toAddr === BURN_ADDRESS.toLowerCase()) {
            burns.push({
              timestamp,
              amount: Number(BigInt(transfer.total?.value || transfer.value || '0')) / Math.pow(10, PTGC_DECIMALS),
              txHash: tx.hash
            });
          }
        }
      }
    }
    
    if (page % 20 === 0) {
      console.log(`    Tx page ${page + 1}: ${burns.length} burns found`);
    }
    
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
  
  return burns;
}

/**
 * Calculate burns for different time periods
 */
function calculatePeriodBurns(burns) {
  const now = Date.now();
  const periods = {
    h12: 12 * 60 * 60 * 1000,
    h24: 24 * 60 * 60 * 1000,
    d7: 7 * 24 * 60 * 60 * 1000,
    d30: 30 * 24 * 60 * 60 * 1000
  };
  
  const result = {};
  for (const [key, ms] of Object.entries(periods)) {
    const cutoff = now - ms;
    const periodBurns = burns.filter(b => b.timestamp >= cutoff);
    result[key] = {
      count: periodBurns.length,
      amount: periodBurns.reduce((sum, b) => sum + b.amount, 0)
    };
  }
  return result;
}

/**
 * Merge new burns with existing burns (remove duplicates by txHash)
 */
function mergeBurns(existingBurns, newBurns) {
  const txHashSet = new Set(existingBurns.map(b => b.txHash || b.t));
  const merged = [...existingBurns];
  
  for (const burn of newBurns) {
    if (!txHashSet.has(burn.txHash)) {
      merged.push(burn);
      txHashSet.add(burn.txHash);
    }
  }
  
  // Sort by timestamp descending
  merged.sort((a, b) => (b.timestamp || b.t) - (a.timestamp || a.t));
  return merged;
}

/**
 * Fetch OHLCV data from GeckoTerminal for volume history
 */
async function fetchVolumeHistory(poolAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} volume history from GeckoTerminal...`);
  
  const url = `${GECKO_API}/networks/pulsechain/pools/${poolAddress}/ohlcv/day?aggregate=1&limit=90`;
  
  const data = await fetchWithRetry(url);
  
  if (!data || !data.data || !data.data.attributes || !data.data.attributes.ohlcv_list) {
    console.log(`  No volume data available for ${tokenSymbol}`);
    return null;
  }
  
  const ohlcvList = data.data.attributes.ohlcv_list;
  
  // OHLCV format: [timestamp, open, high, low, close, volume]
  const volumeHistory = ohlcvList.map(candle => ({
    timestamp: candle[0] * 1000, // Convert to milliseconds
    open: candle[1],
    high: candle[2],
    low: candle[3],
    close: candle[4],
    volume: candle[5]
  })).sort((a, b) => b.timestamp - a.timestamp); // Most recent first
  
  console.log(`  Fetched ${volumeHistory.length} days of volume data`);
  
  // Calculate volume periods
  const now = Date.now();
  const vol24h = volumeHistory.find(v => now - v.timestamp < 24 * 60 * 60 * 1000)?.volume || 0;
  const vol7d = volumeHistory
    .filter(v => now - v.timestamp < 7 * 24 * 60 * 60 * 1000)
    .reduce((sum, v) => sum + v.volume, 0);
  const vol30d = volumeHistory
    .filter(v => now - v.timestamp < 30 * 24 * 60 * 60 * 1000)
    .reduce((sum, v) => sum + v.volume, 0);
  
  // Get yesterday's volume for comparison
  const yesterday = volumeHistory.find(v => {
    const age = now - v.timestamp;
    return age >= 24 * 60 * 60 * 1000 && age < 48 * 60 * 60 * 1000;
  });
  const volYesterday = yesterday?.volume || 0;
  const volChange24h = volYesterday > 0 ? ((vol24h - volYesterday) / volYesterday) * 100 : 0;
  
  console.log(`  24H Volume: $${vol24h.toLocaleString()} (${volChange24h > 0 ? '+' : ''}${volChange24h.toFixed(2)}%)`);
  console.log(`  7D Volume: $${vol7d.toLocaleString()}`);
  console.log(`  30D Volume: $${vol30d.toLocaleString()}`);
  
  return {
    current24h: vol24h,
    yesterday24h: volYesterday,
    change24h: volChange24h,
    vol7d,
    vol30d,
    history: volumeHistory.slice(0, 90).map(v => ({
      t: v.timestamp,
      v: v.volume,
      c: v.close // closing price
    }))
  };
}

/**
 * Fetch current pool data from GeckoTerminal (liquidity, price, etc.)
 */
async function fetchPoolData(poolAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} pool data from GeckoTerminal...`);
  
  const url = `${GECKO_API}/networks/pulsechain/pools/${poolAddress}`;
  
  const data = await fetchWithRetry(url);
  
  if (!data || !data.data || !data.data.attributes) {
    console.log(`  No pool data available for ${tokenSymbol}`);
    return null;
  }
  
  const attrs = data.data.attributes;
  
  const poolData = {
    name: attrs.name,
    liquidity: parseFloat(attrs.reserve_in_usd) || 0,
    volume24h: parseFloat(attrs.volume_usd?.h24) || 0,
    volume1h: parseFloat(attrs.volume_usd?.h1) || 0,
    priceUsd: parseFloat(attrs.base_token_price_usd) || 0,
    priceChange24h: parseFloat(attrs.price_change_percentage?.h24) || 0,
    txns24h: (attrs.transactions?.h24?.buys || 0) + (attrs.transactions?.h24?.sells || 0),
    buys24h: attrs.transactions?.h24?.buys || 0,
    sells24h: attrs.transactions?.h24?.sells || 0
  };
  
  console.log(`  Liquidity: $${poolData.liquidity.toLocaleString()}`);
  console.log(`  24H Volume: $${poolData.volume24h.toLocaleString()}`);
  console.log(`  Price: $${poolData.priceUsd}`);
  
  return poolData;
}

/**
 * Main function
 */
async function main() {
  console.log('='.repeat(60));
  console.log('Burn History Fetcher - OPTIMIZED');
  console.log('Started at:', new Date().toISOString());
  console.log('='.repeat(60));
  
  const outputPath = path.join(__dirname, '..', 'data', 'burn-history.json');
  const existingData = loadExistingData(outputPath);
  
  // Get last timestamps for incremental updates
  const lastPTGCTimestamp = existingData?.PTGC?.burns?.[0]?.t || 0;
  const lastUFOTimestamp = existingData?.UFO?.burns?.[0]?.t || 0;
  const lastPTGCbyUFOTimestamp = existingData?.PTGCbyUFO?.burns?.[0]?.t || 0;
  
  // Fetch new PTGC burns
  const newPTGCBurns = await fetchBurnTransfers(PTGC_ADDRESS, 'PTGC', PTGC_DECIMALS, lastPTGCTimestamp);
  
  // Fetch new UFO burns
  const newUFOBurns = await fetchBurnTransfers(UFO_ADDRESS, 'UFO', UFO_DECIMALS, lastUFOTimestamp);
  
  // Fetch PTGC burned by UFO contract
  const newPTGCbyUFO = await fetchPTGCBurnsByUFO(lastPTGCbyUFOTimestamp);
  
  // Merge with existing data
  const allPTGCBurns = existingData?.PTGC?.burns 
    ? mergeBurns(existingData.PTGC.burns.map(b => ({...b, timestamp: b.t, amount: b.a, txHash: b.tx})), newPTGCBurns)
    : newPTGCBurns;
    
  const allUFOBurns = existingData?.UFO?.burns
    ? mergeBurns(existingData.UFO.burns.map(b => ({...b, timestamp: b.t, amount: b.a, txHash: b.tx})), newUFOBurns)
    : newUFOBurns;
    
  const allPTGCbyUFO = existingData?.PTGCbyUFO?.burns
    ? mergeBurns(existingData.PTGCbyUFO.burns.map(b => ({...b, timestamp: b.t, amount: b.a, txHash: b.tx})), newPTGCbyUFO)
    : newPTGCbyUFO;
  
  // Calculate totals and periods
  const ptgcTotal = allPTGCBurns.reduce((sum, b) => sum + (b.amount || b.a || 0), 0);
  const ufoTotal = allUFOBurns.reduce((sum, b) => sum + (b.amount || b.a || 0), 0);
  const ptgcByUFOTotal = allPTGCbyUFO.reduce((sum, b) => sum + (b.amount || b.a || 0), 0);
  
  const ptgcPeriods = calculatePeriodBurns(allPTGCBurns.map(b => ({...b, timestamp: b.timestamp || b.t})));
  const ufoPeriods = calculatePeriodBurns(allUFOBurns.map(b => ({...b, timestamp: b.timestamp || b.t})));
  const ptgcByUFOPeriods = calculatePeriodBurns(allPTGCbyUFO.map(b => ({...b, timestamp: b.timestamp || b.t})));
  
  // Fetch volume history from GeckoTerminal
  console.log('\n' + '='.repeat(60));
  console.log('Fetching Volume Data from GeckoTerminal');
  console.log('='.repeat(60));
  
  const ptgcVolume = await fetchVolumeHistory(PTGC_MAIN_PAIR, 'PTGC');
  await delay(2500); // Respect rate limits (30 req/min)
  const ufoVolume = await fetchVolumeHistory(UFO_MAIN_PAIR, 'UFO');
  await delay(2500);
  const ptgcPool = await fetchPoolData(PTGC_MAIN_PAIR, 'PTGC');
  await delay(2500);
  const ufoPool = await fetchPoolData(UFO_MAIN_PAIR, 'UFO');
  
  // Build output data (compact format to save space)
  const outputData = {
    lastUpdated: new Date().toISOString(),
    PTGC: {
      totalBurned: ptgcTotal,
      burnCount: allPTGCBurns.length,
      periods: ptgcPeriods,
      burns: allPTGCBurns.slice(0, 50000).map(b => ({ 
        t: b.timestamp || b.t, 
        a: b.amount || b.a 
      })),
      volume: ptgcVolume,
      pool: ptgcPool
    },
    UFO: {
      totalBurned: ufoTotal,
      burnCount: allUFOBurns.length,
      periods: ufoPeriods,
      burns: allUFOBurns.slice(0, 50000).map(b => ({ 
        t: b.timestamp || b.t, 
        a: b.amount || b.a 
      })),
      volume: ufoVolume,
      pool: ufoPool
    },
    PTGCbyUFO: {
      totalBurned: ptgcByUFOTotal,
      burnCount: allPTGCbyUFO.length,
      periods: ptgcByUFOPeriods,
      burns: allPTGCbyUFO.slice(0, 10000).map(b => ({ 
        t: b.timestamp || b.t, 
        a: b.amount || b.a 
      }))
    }
  };
  
  // Ensure directory exists
  const dataDir = path.dirname(outputPath);
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, JSON.stringify(outputData, null, 2));
  
  console.log('\n' + '='.repeat(60));
  console.log('Summary:');
  console.log('='.repeat(60));
  console.log(`PTGC Total Burned: ${ptgcTotal.toLocaleString()} (${allPTGCBurns.length} txs)`);
  console.log(`  12H: ${ptgcPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ptgcPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ptgcPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ptgcPeriods.d30.amount.toLocaleString()}`);
  if (ptgcVolume) {
    console.log(`  Volume 24H: $${ptgcVolume.current24h?.toLocaleString()} (${ptgcVolume.change24h > 0 ? '+' : ''}${ptgcVolume.change24h?.toFixed(2)}%)`);
  }
  console.log('');
  console.log(`UFO Total Burned: ${ufoTotal.toLocaleString()} (${allUFOBurns.length} txs)`);
  console.log(`  12H: ${ufoPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ufoPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ufoPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ufoPeriods.d30.amount.toLocaleString()}`);
  if (ufoVolume) {
    console.log(`  Volume 24H: $${ufoVolume.current24h?.toLocaleString()} (${ufoVolume.change24h > 0 ? '+' : ''}${ufoVolume.change24h?.toFixed(2)}%)`);
  }
  console.log('');
  console.log(`PTGC Burned BY UFO: ${ptgcByUFOTotal.toLocaleString()} (${allPTGCbyUFO.length} txs)`);
  console.log(`  12H: ${ptgcByUFOPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ptgcByUFOPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ptgcByUFOPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ptgcByUFOPeriods.d30.amount.toLocaleString()}`);
  console.log('');
  console.log(`Output written to: ${outputPath}`);
  console.log('Completed at:', new Date().toISOString());
}

main().catch(console.error);
