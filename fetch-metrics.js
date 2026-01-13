/**
 * PTGC/UFO Dashboard - Metrics Collector
 * Runs every 30 minutes via GitHub Actions
 * Collects: Volume, Liquidity, Liq/MCap Ratio, Holders, Tokens in LP
 */

const fs = require('fs');
const path = require('path');

// Token configurations
const TOKENS = {
  PTGC: {
    address: '0x94534EeEe131840b1c0F61847c572228bdfDDE93',
    mainPair: '0xf5A89A6487D62df5308CDDA89c566C5B5ef94C11'
  },
  UFO: {
    address: '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018',
    mainPair: '0xbeA0e55b82Eb975280041F3b49C4D0bD937b72d5'
  }
};

const MORALIS_API_KEY = process.env.MORALIS_API_KEY;
const DATA_DIR = './data';
const METRICS_FILE = path.join(DATA_DIR, 'metrics-history.json');

// Retention settings
const MAX_30MIN_SNAPSHOTS = 96;  // 48 hours of 30-min data
const MAX_HOURLY_SNAPSHOTS = 168; // 7 days of hourly data
const MAX_DAILY_SNAPSHOTS = 90;   // 90 days of daily data

/**
 * Fetch data from DexScreener for a token
 */
async function fetchDexScreener(tokenAddress) {
  try {
    const url = `https://api.dexscreener.com/latest/dex/tokens/${tokenAddress}`;
    const res = await fetch(url);
    const data = await res.json();
    
    if (!data.pairs || data.pairs.length === 0) {
      console.error(`No pairs found for ${tokenAddress}`);
      return null;
    }

    // Sort by liquidity to get main pairs first
    const pairs = data.pairs
      .map(p => ({
        ...p,
        liq: p.liquidity?.usd || 0,
        vol: p.volume?.h24 || 0
      }))
      .sort((a, b) => b.liq - a.liq);

    // Aggregate totals across all pairs
    let totalLiq = 0;
    let totalVol = 0;
    let totalTokensInLP = 0;

    pairs.forEach(p => {
      totalLiq += p.liq;
      totalVol += p.vol;
      
      // Calculate tokens in LP
      const isBase = p.baseToken?.address?.toLowerCase() === tokenAddress.toLowerCase();
      if (isBase && p.liquidity?.base) {
        totalTokensInLP += p.liquidity.base;
      } else if (!isBase && p.liquidity?.quote) {
        totalTokensInLP += p.liquidity.quote;
      }
    });

    // Get price and mcap from highest liquidity pair
    const mainPair = pairs[0];
    const price = parseFloat(mainPair.priceUsd) || 0;
    const mcap = mainPair.marketCap || mainPair.fdv || 0;

    return {
      price,
      mcap,
      volume24h: totalVol,
      liquidity: totalLiq,
      tokensInLP: totalTokensInLP,
      liqMcapRatio: mcap > 0 ? (totalLiq / mcap) * 100 : 0,
      pairCount: pairs.length
    };
  } catch (error) {
    console.error(`DexScreener error for ${tokenAddress}:`, error.message);
    return null;
  }
}

/**
 * Fetch holder count from Moralis
 */
async function fetchHolderCount(tokenAddress) {
  if (!MORALIS_API_KEY) {
    console.error('MORALIS_API_KEY not set');
    return null;
  }

  try {
    const url = `https://deep-index.moralis.io/api/v2.2/erc20/${tokenAddress}/owners?chain=pulsechain&order=DESC`;
    const res = await fetch(url, {
      headers: {
        'X-API-Key': MORALIS_API_KEY,
        'Accept': 'application/json'
      }
    });

    if (!res.ok) {
      console.error(`Moralis API error: ${res.status} ${res.statusText}`);
      return null;
    }

    const data = await res.json();
    
    // Moralis returns total count in the response
    // The 'result' array contains holders, but we need the total
    // Check if there's a cursor or total field
    if (data.result) {
      // If no explicit total, we may need to paginate or use page info
      // Moralis typically provides this in the response metadata
      const total = data.total || data.result.length;
      return total;
    }
    
    return null;
  } catch (error) {
    console.error(`Moralis error for ${tokenAddress}:`, error.message);
    return null;
  }
}

/**
 * Alternative: Fetch holder count from PulseScan (backup)
 */
async function fetchHolderCountPulseScan(tokenAddress) {
  try {
    const url = `https://api.scan.pulsechain.com/api/v2/tokens/${tokenAddress}`;
    const res = await fetch(url);
    const data = await res.json();
    return data.holders ? parseInt(data.holders) : null;
  } catch (error) {
    console.error(`PulseScan error for ${tokenAddress}:`, error.message);
    return null;
  }
}

/**
 * Collect all metrics for a token
 */
async function collectTokenMetrics(tokenName, tokenConfig) {
  console.log(`\nCollecting metrics for ${tokenName}...`);
  
  // Fetch DexScreener data
  const dexData = await fetchDexScreener(tokenConfig.address);
  if (!dexData) {
    console.error(`Failed to fetch DexScreener data for ${tokenName}`);
    return null;
  }

  // Fetch holder count (try Moralis first, fallback to PulseScan)
  let holders = await fetchHolderCount(tokenConfig.address);
  if (holders === null) {
    console.log(`Moralis failed for ${tokenName}, trying PulseScan...`);
    holders = await fetchHolderCountPulseScan(tokenConfig.address);
  }

  return {
    price: dexData.price,
    volume24h: dexData.volume24h,
    liquidity: dexData.liquidity,
    mcap: dexData.mcap,
    liqMcapRatio: parseFloat(dexData.liqMcapRatio.toFixed(2)),
    holders: holders,
    tokensInLP: dexData.tokensInLP,
    pairCount: dexData.pairCount
  };
}

/**
 * Load existing metrics history
 */
function loadMetricsHistory() {
  try {
    if (fs.existsSync(METRICS_FILE)) {
      const data = fs.readFileSync(METRICS_FILE, 'utf8');
      return JSON.parse(data);
    }
  } catch (error) {
    console.error('Error loading metrics history:', error.message);
  }
  
  // Return default structure
  return {
    lastUpdated: null,
    PTGC: {
      snapshots: [],    // 30-min snapshots
      hourly: [],       // Hourly rollups
      daily: []         // Daily rollups
    },
    UFO: {
      snapshots: [],
      hourly: [],
      daily: []
    }
  };
}

/**
 * Roll up old snapshots to hourly/daily
 */
function rollupSnapshots(tokenData) {
  const now = new Date();
  
  // Roll up 30-min snapshots older than 48h to hourly
  if (tokenData.snapshots.length > MAX_30MIN_SNAPSHOTS) {
    const cutoff = new Date(now.getTime() - 48 * 60 * 60 * 1000);
    const toKeep = [];
    const toRollup = [];
    
    tokenData.snapshots.forEach(s => {
      const ts = new Date(s.timestamp);
      if (ts > cutoff) {
        toKeep.push(s);
      } else {
        toRollup.push(s);
      }
    });
    
    // Group by hour and average
    const hourlyGroups = {};
    toRollup.forEach(s => {
      const hourKey = s.timestamp.substring(0, 13); // YYYY-MM-DDTHH
      if (!hourlyGroups[hourKey]) {
        hourlyGroups[hourKey] = [];
      }
      hourlyGroups[hourKey].push(s);
    });
    
    // Create hourly averages
    Object.entries(hourlyGroups).forEach(([hourKey, snapshots]) => {
      if (snapshots.length > 0) {
        const avg = {
          timestamp: hourKey + ':00:00.000Z',
          price: snapshots.reduce((s, x) => s + (x.price || 0), 0) / snapshots.length,
          volume24h: snapshots.reduce((s, x) => s + (x.volume24h || 0), 0) / snapshots.length,
          liquidity: snapshots.reduce((s, x) => s + (x.liquidity || 0), 0) / snapshots.length,
          liqMcapRatio: snapshots.reduce((s, x) => s + (x.liqMcapRatio || 0), 0) / snapshots.length,
          holders: Math.round(snapshots.reduce((s, x) => s + (x.holders || 0), 0) / snapshots.length),
          tokensInLP: snapshots.reduce((s, x) => s + (x.tokensInLP || 0), 0) / snapshots.length
        };
        tokenData.hourly.unshift(avg);
      }
    });
    
    tokenData.snapshots = toKeep;
  }
  
  // Roll up hourly data older than 7 days to daily
  if (tokenData.hourly.length > MAX_HOURLY_SNAPSHOTS) {
    const cutoff = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
    const toKeep = [];
    const toRollup = [];
    
    tokenData.hourly.forEach(s => {
      const ts = new Date(s.timestamp);
      if (ts > cutoff) {
        toKeep.push(s);
      } else {
        toRollup.push(s);
      }
    });
    
    // Group by day and average
    const dailyGroups = {};
    toRollup.forEach(s => {
      const dayKey = s.timestamp.substring(0, 10); // YYYY-MM-DD
      if (!dailyGroups[dayKey]) {
        dailyGroups[dayKey] = [];
      }
      dailyGroups[dayKey].push(s);
    });
    
    // Create daily averages
    Object.entries(dailyGroups).forEach(([dayKey, snapshots]) => {
      if (snapshots.length > 0) {
        const avg = {
          timestamp: dayKey + 'T12:00:00.000Z',
          price: snapshots.reduce((s, x) => s + (x.price || 0), 0) / snapshots.length,
          volume24h: snapshots.reduce((s, x) => s + (x.volume24h || 0), 0) / snapshots.length,
          liquidity: snapshots.reduce((s, x) => s + (x.liquidity || 0), 0) / snapshots.length,
          liqMcapRatio: snapshots.reduce((s, x) => s + (x.liqMcapRatio || 0), 0) / snapshots.length,
          holders: Math.round(snapshots.reduce((s, x) => s + (x.holders || 0), 0) / snapshots.length),
          tokensInLP: snapshots.reduce((s, x) => s + (x.tokensInLP || 0), 0) / snapshots.length
        };
        tokenData.daily.unshift(avg);
      }
    });
    
    tokenData.hourly = toKeep;
  }
  
  // Trim daily to max
  if (tokenData.daily.length > MAX_DAILY_SNAPSHOTS) {
    tokenData.daily = tokenData.daily.slice(0, MAX_DAILY_SNAPSHOTS);
  }
  
  return tokenData;
}

/**
 * Calculate 24h changes
 */
function calculate24hChanges(tokenData, currentMetrics) {
  const now = new Date();
  const target = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  
  // Find the snapshot closest to 24h ago
  let closest = null;
  let closestDiff = Infinity;
  
  // Search in snapshots first (most accurate)
  [...tokenData.snapshots, ...tokenData.hourly].forEach(s => {
    const ts = new Date(s.timestamp);
    const diff = Math.abs(ts.getTime() - target.getTime());
    if (diff < closestDiff) {
      closestDiff = diff;
      closest = s;
    }
  });
  
  if (!closest || closestDiff > 2 * 60 * 60 * 1000) {
    // No snapshot within 2 hours of target, return null changes
    return {
      volume24h: null,
      liquidity: null,
      liqMcapRatio: null,
      holders: null,
      tokensInLP: null
    };
  }
  
  // Calculate percentage changes
  const calcChange = (current, previous) => {
    if (previous === null || previous === 0 || current === null) return null;
    return ((current - previous) / previous) * 100;
  };
  
  return {
    volume24h: calcChange(currentMetrics.volume24h, closest.volume24h),
    liquidity: calcChange(currentMetrics.liquidity, closest.liquidity),
    liqMcapRatio: calcChange(currentMetrics.liqMcapRatio, closest.liqMcapRatio),
    holders: currentMetrics.holders !== null && closest.holders !== null 
      ? currentMetrics.holders - closest.holders 
      : null,  // Absolute change for holders
    tokensInLP: calcChange(currentMetrics.tokensInLP, closest.tokensInLP)
  };
}

/**
 * Main execution
 */
async function main() {
  console.log('='.repeat(50));
  console.log('PTGC/UFO Metrics Collector');
  console.log('Started at:', new Date().toISOString());
  console.log('='.repeat(50));

  // Ensure data directory exists
  if (!fs.existsSync(DATA_DIR)) {
    fs.mkdirSync(DATA_DIR, { recursive: true });
  }

  // Load existing history
  const history = loadMetricsHistory();
  const timestamp = new Date().toISOString();

  // Collect metrics for each token
  for (const [tokenName, tokenConfig] of Object.entries(TOKENS)) {
    const metrics = await collectTokenMetrics(tokenName, tokenConfig);
    
    if (metrics) {
      // Create snapshot
      const snapshot = {
        timestamp,
        ...metrics
      };
      
      // Add to snapshots (most recent first)
      history[tokenName].snapshots.unshift(snapshot);
      
      // Perform rollups if needed
      history[tokenName] = rollupSnapshots(history[tokenName]);
      
      // Calculate 24h changes
      const changes = calculate24hChanges(history[tokenName], metrics);
      history[tokenName].changes24h = changes;
      
      console.log(`\n${tokenName} Metrics:`);
      console.log(`  Price: $${metrics.price.toFixed(8)}`);
      console.log(`  Volume 24H: $${metrics.volume24h.toLocaleString()}`);
      console.log(`  Liquidity: $${metrics.liquidity.toLocaleString()}`);
      console.log(`  Liq/MCap: ${metrics.liqMcapRatio}%`);
      console.log(`  Holders: ${metrics.holders || 'N/A'}`);
      console.log(`  Tokens in LP: ${metrics.tokensInLP.toLocaleString()}`);
      console.log(`  24H Changes:`, changes);
    } else {
      console.error(`Failed to collect metrics for ${tokenName}`);
    }
    
    // Small delay between tokens to be nice to APIs
    await new Promise(r => setTimeout(r, 1000));
  }

  // Update timestamp and save
  history.lastUpdated = timestamp;
  
  fs.writeFileSync(METRICS_FILE, JSON.stringify(history, null, 2));
  console.log(`\nMetrics saved to ${METRICS_FILE}`);
  console.log('Completed at:', new Date().toISOString());
}

main().catch(error => {
  console.error('Fatal error:', error);
  process.exit(1);
});
