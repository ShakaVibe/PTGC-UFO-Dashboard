/**
 * fetch-ufo-ptgc-burns.js
 *
 * Standalone script to accurately identify PTGC burned by the UFO mechanism.
 *
 * HOW IT WORKS:
 * When UFO fires its buyback, it burns UFO AND burns PTGC in the SAME transaction.
 * So we fetch all UFO burns and all PTGC burns (from UFO launch onwards), store
 * the tx hash on each, then cross-reference: any PTGC burn sharing a tx hash
 * with a UFO burn was triggered by the UFO buyback mechanism.
 *
 * OUTPUT:
 * Writes to data/ufo-ptgc-burns.json — does NOT touch any existing files.
 *
 * UFO launch: ~May 2024
 */

const fs = require('fs');
const path = require('path');

// Addresses
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const UFO_ADDRESS  = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018';
const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';

const PTGC_DECIMALS = 18;
const UFO_DECIMALS  = 18;

// Only fetch PTGC burns from UFO launch onwards (May 2024)
// This avoids re-fetching years of pre-UFO history
const UFO_LAUNCH_DATE = new Date('2024-05-01').getTime();

const RPC_URL       = 'https://rpc.pulsechain.com';
const TRANSFER_SIG  = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const BURN_ADDR_TOPIC = '0x0000000000000000000000000000000000000000000000000000000000000369';
const LOG_CHUNK     = 2000;
const MS_PER_BLOCK  = 10000;

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// ============================================
// RPC
// ============================================
async function rpcCall(method, params, retries = 3) {
  for (let attempt = 0; attempt < retries; attempt++) {
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), 30000);
      const res = await fetch(RPC_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', method, params, id: 1 }),
        signal: controller.signal
      });
      clearTimeout(tid);
      const json = await res.json();
      if (json.error) {
        console.log(`  RPC error [${method}]: ${json.error.message}`);
        if (attempt < retries - 1) await delay(2000 * (attempt + 1));
        continue;
      }
      return json.result;
    } catch (e) {
      console.log(`  RPC call failed [${method}]: ${e.message}`);
      if (attempt < retries - 1) await delay(2000 * (attempt + 1));
    }
  }
  return null;
}

// ============================================
// FETCH BURNS VIA eth_getLogs
// ============================================
async function fetchBurns(tokenAddress, tokenSymbol, decimals, fromBlock) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Fetching ${tokenSymbol} burns via eth_getLogs from block ${fromBlock}...`);
  console.log(`${'='.repeat(50)}`);

  const blockHex = await rpcCall('eth_blockNumber', []);
  if (!blockHex) throw new Error('Could not get block number');
  const currentBlock = parseInt(blockHex, 16);

  const latestBlockData = await rpcCall('eth_getBlockByNumber', ['latest', false]);
  if (!latestBlockData) throw new Error('Could not get latest block');
  const latestTs = parseInt(latestBlockData.timestamp, 16) * 1000;

  const tsFromBlock = (blockNum) => latestTs - (currentBlock - blockNum) * MS_PER_BLOCK;

  const totalBlocks = currentBlock - fromBlock;
  const totalChunks = Math.ceil(totalBlocks / LOG_CHUNK);
  console.log(`Scanning ${totalBlocks.toLocaleString()} blocks in ~${totalChunks} chunks...`);

  const allLogs = [];
  let chunksDone = 0;

  for (let start = fromBlock; start <= currentBlock; start += LOG_CHUNK) {
    const end = Math.min(start + LOG_CHUNK - 1, currentBlock);

    const result = await rpcCall('eth_getLogs', [{
      address: tokenAddress,
      fromBlock: '0x' + start.toString(16),
      toBlock:   '0x' + end.toString(16),
      topics: [TRANSFER_SIG, null, BURN_ADDR_TOPIC]
    }]);

    if (result && result.length > 0) {
      allLogs.push(...result);
    }

    chunksDone++;
    if (chunksDone % 100 === 0 || chunksDone === totalChunks) {
      console.log(`  ${chunksDone}/${totalChunks} chunks | ${allLogs.length} logs so far`);
    }

    await delay(50);
  }

  console.log(`Total ${tokenSymbol} burn logs: ${allLogs.length}`);

  // Convert to burn records — store tx hash
  const burns = allLogs.map(log => {
    const blockNum = parseInt(log.blockNumber, 16);
    const bigVal   = BigInt(log.data);
    const divisor  = BigInt(10) ** BigInt(decimals);
    const whole    = Number(bigVal / divisor);
    const frac     = Number(bigVal % divisor) / Math.pow(10, decimals);
    return {
      t:  tsFromBlock(blockNum),
      a:  whole + frac,
      f:  ('0x' + log.topics[1].slice(26)).toLowerCase(),
      tx: log.transactionHash
    };
  });

  // Sort newest first
  burns.sort((a, b) => b.t - a.t);

  console.log(`${tokenSymbol} burns parsed: ${burns.length}`);
  if (burns.length > 0) {
    console.log(`  Oldest: ${new Date(burns[burns.length - 1].t).toISOString()}`);
    console.log(`  Newest: ${new Date(burns[0].t).toISOString()}`);
  }

  return burns;
}

// ============================================
// CALCULATE PERIOD TOTALS
// ============================================
function calculatePeriods(burns) {
  const now  = Date.now();
  const h12  = 12 * 60 * 60 * 1000;
  const h24  = 24 * 60 * 60 * 1000;
  const d7   =  7 * 24 * 60 * 60 * 1000;
  const d30  = 30 * 24 * 60 * 60 * 1000;
  const d90  = 90 * 24 * 60 * 60 * 1000;

  const result = {
    h12: { count: 0, amount: 0 },
    h24: { count: 0, amount: 0 },
    d7:  { count: 0, amount: 0 },
    d30: { count: 0, amount: 0 },
    d90: { count: 0, amount: 0 }
  };

  for (const burn of burns) {
    const age = now - burn.t;
    if (age <= h12) { result.h12.count++; result.h12.amount += burn.a; }
    if (age <= h24) { result.h24.count++; result.h24.amount += burn.a; }
    if (age <= d7)  { result.d7.count++;  result.d7.amount  += burn.a; }
    if (age <= d30) { result.d30.count++; result.d30.amount += burn.a; }
    if (age <= d90) { result.d90.count++; result.d90.amount += burn.a; }
  }

  return result;
}

// ============================================
// MAIN
// ============================================
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('UFO → PTGC BURN FETCHER (standalone, read-only)');
  console.log('Does NOT modify any existing files.');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));

  const dataDir = path.join(__dirname, '..', 'data');

  // Get current block and estimate the block at UFO launch
  console.log('\nEstimating block number at UFO launch (May 2024)...');
  const blockHex = await rpcCall('eth_blockNumber', []);
  const currentBlock = parseInt(blockHex, 16);
  const latestBlockData = await rpcCall('eth_getBlockByNumber', ['latest', false]);
  const latestTs = parseInt(latestBlockData.timestamp, 16) * 1000;

  // Estimate block at UFO launch
  const msAgo = latestTs - UFO_LAUNCH_DATE;
  const blocksAgo = Math.ceil(msAgo / MS_PER_BLOCK);
  const ufoLaunchBlock = Math.max(0, currentBlock - blocksAgo);
  console.log(`  Current block: ${currentBlock.toLocaleString()}`);
  console.log(`  Estimated UFO launch block: ${ufoLaunchBlock.toLocaleString()}`);
  console.log(`  Blocks to scan: ${(currentBlock - ufoLaunchBlock).toLocaleString()}`);

  // Fetch UFO burns (all time — UFO only launched ~May 2024 so this is the full history)
  const ufoBurns = await fetchBurns(UFO_ADDRESS, 'UFO', UFO_DECIMALS, ufoLaunchBlock);
  await delay(500);

  // Fetch PTGC burns from UFO launch onwards only
  const ptgcBurns = await fetchBurns(PTGC_ADDRESS, 'PTGC', PTGC_DECIMALS, ufoLaunchBlock);
  await delay(500);

  // ============================================
  // CROSS-REFERENCE: PTGCbyUFO
  // ============================================
  console.log(`\n${'='.repeat(50)}`);
  console.log('Cross-referencing tx hashes...');
  console.log(`${'='.repeat(50)}`);

  const ufoBurnTxHashes = new Set(ufoBurns.map(b => b.tx).filter(Boolean));
  console.log(`UFO burn tx hashes: ${ufoBurnTxHashes.size}`);

  const ptgcByUFOBurns = ptgcBurns.filter(b => b.tx && ufoBurnTxHashes.has(b.tx));
  console.log(`PTGC burns sharing tx hash with UFO burns: ${ptgcByUFOBurns.length}`);

  const totalPTGCbyUFO = ptgcByUFOBurns.reduce((s, b) => s + b.a, 0);
  const totalUFOBurned = ufoBurns.reduce((s, b) => s + b.a, 0);

  const ptgcByUFOPeriods = calculatePeriods(ptgcByUFOBurns);
  const ufoPeriods       = calculatePeriods(ufoBurns);

  // ============================================
  // WRITE OUTPUT
  // ============================================
  const output = {
    lastUpdated: new Date().toISOString(),
    note: 'Standalone fetch — does not affect existing burn files. PTGCbyUFO identified by tx hash cross-reference with UFO burns.',
    scanFrom: new Date(UFO_LAUNCH_DATE).toISOString(),

    PTGCbyUFO: {
      totalBurned: totalPTGCbyUFO,
      burnCount:   ptgcByUFOBurns.length,
      periods:     ptgcByUFOPeriods
    },

    UFOBurns: {
      totalBurned: totalUFOBurned,
      burnCount:   ufoBurns.length,
      periods:     ufoPeriods
    },

    // Sanity check: period amounts should be roughly equal
    // since both are 1% of the same UFO transaction volume
    sanityCheck: {
      note: 'PTGCbyUFO and UFOBurns amounts should be roughly equal per period (both are 1% of UFO volume). Differences are due to price/slippage at time of swap.',
      h24_ufo_burned:  ufoPeriods.h24.amount,
      h24_ptgc_burned: ptgcByUFOPeriods.h24.amount,
      d7_ufo_burned:   ufoPeriods.d7.amount,
      d7_ptgc_burned:  ptgcByUFOPeriods.d7.amount,
      d30_ufo_burned:  ufoPeriods.d30.amount,
      d30_ptgc_burned: ptgcByUFOPeriods.d30.amount,
    }
  };

  const outputPath = path.join(dataDir, 'ufo-ptgc-burns.json');
  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`\nWritten: ${outputPath}`);

  // ============================================
  // SUMMARY
  // ============================================
  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  console.log(`\nPTGC burned by UFO mechanism:`);
  console.log(`  Lifetime: ${totalPTGCbyUFO.toLocaleString()} PTGC (${ptgcByUFOBurns.length} txs)`);
  console.log(`  12H:  ${ptgcByUFOPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H:  ${ptgcByUFOPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:   ${ptgcByUFOPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D:  ${ptgcByUFOPeriods.d30.amount.toLocaleString()}`);
  console.log(`  90D:  ${ptgcByUFOPeriods.d90.amount.toLocaleString()}`);
  console.log(`\nUFO burned (for comparison — should be similar amounts):`);
  console.log(`  Lifetime: ${totalUFOBurned.toLocaleString()} UFO (${ufoBurns.length} txs)`);
  console.log(`  24H:  ${ufoPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:   ${ufoPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D:  ${ufoPeriods.d30.amount.toLocaleString()}`);
  console.log(`\nCompleted: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
