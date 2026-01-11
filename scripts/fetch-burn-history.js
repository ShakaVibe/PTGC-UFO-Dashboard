/**
 * Fetch Burn History Script
 * 
 * This script fetches all burn transactions for PTGC and UFO tokens
 * and saves them to a JSON file for fast dashboard loading.
 * 
 * Tracks:
 * - All PTGC burns (total supply burned)
 * - All UFO burns (total supply burned)  
 * - PTGC burned specifically by UFO contract (for UFO dashboard)
 * 
 * Run via GitHub Actions every 6 hours.
 */

const fs = require('fs');
const path = require('path');

const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const UFO_ADDRESS = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018';
const UFO_CONTRACT = '0x456548a9b56efbbd89ca0309edd17a9e20b04018'; // UFO contract (lowercase)

const PTGC_DECIMALS = 18;
const UFO_DECIMALS = 18;

const API_BASE = 'https://api.scan.pulsechain.com/api/v2';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

/**
 * Fetch all token transfers to burn address
 */
async function fetchBurnTransfers(tokenAddress, tokenSymbol, decimals) {
  console.log(`\nFetching ${tokenSymbol} burns...`);
  
  const burns = [];
  let nextPageParams = null;
  let page = 0;
  const maxPages = 500;
  
  while (page < maxPages) {
    const url = nextPageParams
      ? `${API_BASE}/addresses/${BURN_ADDRESS}/token-transfers?type=ERC-20&token=${tokenAddress}&${nextPageParams}`
      : `${API_BASE}/addresses/${BURN_ADDRESS}/token-transfers?type=ERC-20&token=${tokenAddress}`;
    
    try {
      const response = await fetch(url);
      const data = await response.json();
      
      if (!data.items || !Array.isArray(data.items) || data.items.length === 0) {
        break;
      }
      
      for (const tx of data.items) {
        const toAddr = (tx.to?.hash || '').toLowerCase();
        if (toAddr !== BURN_ADDRESS.toLowerCase()) continue;
        
        burns.push({
          timestamp: new Date(tx.timestamp).getTime(),
          amount: Number(BigInt(tx.total?.value || tx.value || '0')) / Math.pow(10, decimals),
          txHash: tx.transaction_hash,
          from: (tx.from?.hash || '').toLowerCase()
        });
      }
      
      console.log(`  Page ${page + 1}: ${burns.length} burns total`);
      
      if (data.next_page_params) {
        const params = new URLSearchParams();
        Object.entries(data.next_page_params).forEach(([k, v]) => params.set(k, v));
        nextPageParams = params.toString();
      } else {
        break;
      }
      
      page++;
      await delay(200);
      
    } catch (error) {
      console.error(`  Error on page ${page + 1}:`, error.message);
      break;
    }
  }
  
  burns.sort((a, b) => b.timestamp - a.timestamp);
  const totalBurned = burns.reduce((sum, b) => sum + b.amount, 0);
  
  console.log(`  Total: ${burns.length} txs, ${totalBurned.toLocaleString()} tokens`);
  
  return { burns, totalBurned };
}

/**
 * For each PTGC burn, check if the transaction was initiated by UFO contract
 */
async function identifyUFOBurns(ptgcBurns) {
  console.log('\nIdentifying PTGC burns from UFO contract...');
  
  const ufoBurns = [];
  let checked = 0;
  
  for (const burn of ptgcBurns) {
    try {
      // Fetch transaction details to see who initiated it
      const txUrl = `${API_BASE}/transactions/${burn.txHash}`;
      const response = await fetch(txUrl);
      const txData = await response.json();
      
      // Check if transaction was sent FROM the UFO contract
      const txFrom = (txData.from?.hash || '').toLowerCase();
      
      if (txFrom === UFO_CONTRACT) {
        ufoBurns.push(burn);
      }
      
      checked++;
      if (checked % 50 === 0) {
        console.log(`  Checked ${checked}/${ptgcBurns.length} transactions, found ${ufoBurns.length} UFO burns`);
      }
      
      await delay(100); // Rate limiting
      
    } catch (error) {
      // Skip on error
    }
  }
  
  const totalUFOBurned = ufoBurns.reduce((sum, b) => sum + b.amount, 0);
  console.log(`  UFO burned ${totalUFOBurned.toLocaleString()} PTGC in ${ufoBurns.length} transactions`);
  
  return { burns: ufoBurns, totalBurned: totalUFOBurned };
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
 * Main function
 */
async function main() {
  console.log('='.repeat(60));
  console.log('Burn History Fetcher');
  console.log('Started at:', new Date().toISOString());
  console.log('='.repeat(60));
  
  // Fetch ALL PTGC burns (for total supply burned)
  const ptgcData = await fetchBurnTransfers(PTGC_ADDRESS, 'PTGC', PTGC_DECIMALS);
  const ptgcPeriods = calculatePeriodBurns(ptgcData.burns);
  
  // Fetch ALL UFO burns (for total supply burned)
  const ufoData = await fetchBurnTransfers(UFO_ADDRESS, 'UFO', UFO_DECIMALS);
  const ufoPeriods = calculatePeriodBurns(ufoData.burns);
  
  // Identify PTGC burns that came from UFO contract specifically
  const ptgcByUFO = await identifyUFOBurns(ptgcData.burns);
  const ptgcByUFOPeriods = calculatePeriodBurns(ptgcByUFO.burns);
  
  // Build output data
  const outputData = {
    lastUpdated: new Date().toISOString(),
    PTGC: {
      totalBurned: ptgcData.totalBurned,
      burnCount: ptgcData.burns.length,
      periods: ptgcPeriods,
      burns: ptgcData.burns.map(b => ({ t: b.timestamp, a: b.amount }))
    },
    UFO: {
      totalBurned: ufoData.totalBurned,
      burnCount: ufoData.burns.length,
      periods: ufoPeriods,
      burns: ufoData.burns.map(b => ({ t: b.timestamp, a: b.amount }))
    },
    PTGCbyUFO: {
      totalBurned: ptgcByUFO.totalBurned,
      burnCount: ptgcByUFO.burns.length,
      periods: ptgcByUFOPeriods,
      burns: ptgcByUFO.burns.map(b => ({ t: b.timestamp, a: b.amount }))
    }
  };
  
  // Write to file
  const outputPath = path.join(__dirname, '..', 'data', 'burn-history.json');
  const dataDir = path.dirname(outputPath);
  if (!fs.existsSync(dataDir)) {
    fs.mkdirSync(dataDir, { recursive: true });
  }
  
  fs.writeFileSync(outputPath, JSON.stringify(outputData, null, 2));
  
  console.log('\n' + '='.repeat(60));
  console.log('Summary:');
  console.log('='.repeat(60));
  console.log(`PTGC Total Burned: ${ptgcData.totalBurned.toLocaleString()}`);
  console.log(`  12H: ${ptgcPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ptgcPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ptgcPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ptgcPeriods.d30.amount.toLocaleString()}`);
  console.log('');
  console.log(`UFO Total Burned: ${ufoData.totalBurned.toLocaleString()}`);
  console.log(`  12H: ${ufoPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ufoPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ufoPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ufoPeriods.d30.amount.toLocaleString()}`);
  console.log('');
  console.log(`PTGC Burned BY UFO: ${ptgcByUFO.totalBurned.toLocaleString()}`);
  console.log(`  12H: ${ptgcByUFOPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H: ${ptgcByUFOPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:  ${ptgcByUFOPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D: ${ptgcByUFOPeriods.d30.amount.toLocaleString()}`);
  console.log('');
  console.log(`Output written to: ${outputPath}`);
  console.log('Completed at:', new Date().toISOString());
}

main().catch(console.error);
