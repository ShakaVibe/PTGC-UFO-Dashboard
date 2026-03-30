/**
 * fetch-ufo-ptgc-burns.js
 *
 * Fast standalone script to accurately identify PTGC burned by the UFO mechanism.
 *
 * HOW IT WORKS:
 * 1. Fetch all UFO burns via eth_getLogs (incremental — only new ones each run)
 * 2. For each UFO burn tx hash, call eth_getTransactionReceipt to get all logs
 * 3. Look for PTGC Transfer events to the burn address in those receipts
 * 4. Those PTGC burns are definitively triggered by UFO's buyback mechanism
 *
 * WHY THIS IS FAST:
 * UFO has ~3,500 burn transactions total. We only need ~3,500 receipt lookups
 * instead of scanning 6 million blocks of PTGC history.
 * Subsequent runs are even faster — only new UFO burns since last run.
 *
 * OUTPUT:
 * Writes ONLY to data/ufo-ptgc-burns.json — does NOT touch any existing files.
 */

const fs   = require('fs');
const path = require('path');

// Addresses
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const UFO_ADDRESS  = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018';
const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';

const UFO_DECIMALS  = 18;
const PTGC_DECIMALS = 18;

// UFO launched May 18, 2024 (confirmed from on-chain data)
const UFO_LAUNCH_DATE = new Date('2024-05-18').getTime();

const RPC_URL         = 'https://rpc.pulsechain.com';
const TRANSFER_SIG    = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const BURN_ADDR_TOPIC = '0x0000000000000000000000000000000000000000000000000000000000000369';
const LOG_CHUNK       = 2000;
const MS_PER_BLOCK    = 10000;
const RECEIPT_CONCURRENCY = 20;

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
        if (attempt < retries - 1) await delay(2000 * (attempt + 1));
        continue;
      }
      return json.result;
    } catch (e) {
      if (attempt < retries - 1) await delay(2000 * (attempt + 1));
    }
  }
  return null;
}

// ============================================
// FETCH UFO BURNS (incremental)
// ============================================
async function fetchUFOBurns(existingBurns = []) {
  console.log('\n' + '='.repeat(50));
  console.log('Fetching UFO burns via eth_getLogs...');
  console.log('='.repeat(50));

  const blockHex = await rpcCall('eth_blockNumber', []);
  if (!blockHex) throw new Error('Could not get block number');
  const currentBlock = parseInt(blockHex, 16);

  const latestBlockData = await rpcCall('eth_getBlockByNumber', ['latest', false]);
  if (!latestBlockData) throw new Error('Could not get latest block');
  const latestTs = parseInt(latestBlockData.timestamp, 16) * 1000;
  const tsFromBlock = (blockNum) => latestTs - (currentBlock - blockNum) * MS_PER_BLOCK;

  // Incremental: start from just before the newest stored burn
  let fromBlock;
  if (existingBurns.length > 0) {
    const lastTs = existingBurns[0].t;
    const blocksAgo = Math.ceil((latestTs - lastTs) / MS_PER_BLOCK);
    fromBlock = Math.max(0, currentBlock - blocksAgo - 1000);
    console.log(`Incremental mode: last burn ${new Date(lastTs).toISOString()}`);
  } else {
    const msAgo = latestTs - UFO_LAUNCH_DATE;
    const blocksAgo = Math.ceil(msAgo / MS_PER_BLOCK);
    fromBlock = Math.max(0, currentBlock - blocksAgo);
    console.log(`First run: scanning from UFO launch ${new Date(UFO_LAUNCH_DATE).toISOString()}`);
  }

  const totalBlocks = currentBlock - fromBlock;
  const totalChunks = Math.ceil(totalBlocks / LOG_CHUNK);
  console.log(`Scanning ${totalBlocks.toLocaleString()} blocks in ~${totalChunks} chunks...`);

  const allLogs = [];
  let chunksDone = 0;

  for (let start = fromBlock; start <= currentBlock; start += LOG_CHUNK) {
    const end = Math.min(start + LOG_CHUNK - 1, currentBlock);
    const result = await rpcCall('eth_getLogs', [{
      address: UFO_ADDRESS,
      fromBlock: '0x' + start.toString(16),
      toBlock:   '0x' + end.toString(16),
      topics: [TRANSFER_SIG, null, BURN_ADDR_TOPIC]
    }]);
    if (result && result.length > 0) allLogs.push(...result);
    chunksDone++;
    if (chunksDone % 100 === 0 || chunksDone === totalChunks) {
      console.log(`  ${chunksDone}/${totalChunks} chunks | ${allLogs.length} new UFO burn logs`);
    }
    await delay(50);
  }

  console.log(`New UFO burn logs: ${allLogs.length}`);

  const newBurns = allLogs.map(log => {
    const blockNum = parseInt(log.blockNumber, 16);
    const bigVal   = BigInt(log.data);
    const divisor  = BigInt(10) ** BigInt(UFO_DECIMALS);
    const whole    = Number(bigVal / divisor);
    const frac     = Number(bigVal % divisor) / Math.pow(10, UFO_DECIMALS);
    return { t: tsFromBlock(blockNum), a: whole + frac, tx: log.transactionHash };
  });

  // Deduplicate against existing
  const existingTxSet = new Set(existingBurns.map(b => b.tx));
  const dedupedNew = newBurns.filter(b => !existingTxSet.has(b.tx));
  console.log(`New unique UFO burns: ${dedupedNew.length}`);

  const allBurns = [...dedupedNew, ...existingBurns];
  allBurns.sort((a, b) => b.t - a.t);
  console.log(`Total UFO burns: ${allBurns.length}`);
  return allBurns;
}

// ============================================
// LOOK UP PTGC BURNS VIA RECEIPTS (incremental)
// ============================================
async function findPTGCBurnsInReceipts(ufoBurns, existingPTGCByUFO = []) {
  console.log('\n' + '='.repeat(50));
  console.log('Looking up PTGC burns in UFO burn transaction receipts...');
  console.log('='.repeat(50));

  // Only process tx hashes we haven't already looked up
  const existingTxSet = new Set(existingPTGCByUFO.map(b => b.tx));
  const newUFOBurns   = ufoBurns.filter(b => !existingTxSet.has(b.tx));
  console.log(`New UFO burn txs to look up: ${newUFOBurns.length}`);
  console.log(`Already cached: ${existingPTGCByUFO.length} PTGC burns`);

  if (newUFOBurns.length === 0) {
    console.log('Nothing new to look up — using cached data');
    return existingPTGCByUFO;
  }

  const burnAddrPadded = '0x000000000000000000000000' + BURN_ADDRESS.slice(2).toLowerCase();
  const newPTGCBurns   = [];

  for (let i = 0; i < newUFOBurns.length; i += RECEIPT_CONCURRENCY) {
    const batch    = newUFOBurns.slice(i, i + RECEIPT_CONCURRENCY);
    const receipts = await Promise.all(
      batch.map(b => rpcCall('eth_getTransactionReceipt', [b.tx]))
    );

    for (let j = 0; j < batch.length; j++) {
      const receipt = receipts[j];
      if (!receipt || !receipt.logs) continue;

      for (const log of receipt.logs) {
        if (
          log.address.toLowerCase() === PTGC_ADDRESS.toLowerCase() &&
          log.topics[0]             === TRANSFER_SIG &&
          log.topics.length         >= 3 &&
          log.topics[2].toLowerCase() === burnAddrPadded
        ) {
          const bigVal  = BigInt(log.data);
          const divisor = BigInt(10) ** BigInt(PTGC_DECIMALS);
          const whole   = Number(bigVal / divisor);
          const frac    = Number(bigVal % divisor) / Math.pow(10, PTGC_DECIMALS);
          newPTGCBurns.push({
            t:  batch[j].t,
            a:  whole + frac,
            f:  ('0x' + log.topics[1].slice(26)).toLowerCase(),
            tx: batch[j].tx
          });
        }
      }
    }

    if ((i + RECEIPT_CONCURRENCY) % 200 === 0 || i + RECEIPT_CONCURRENCY >= newUFOBurns.length) {
      console.log(`  ${Math.min(i + RECEIPT_CONCURRENCY, newUFOBurns.length)}/${newUFOBurns.length} receipts | ${newPTGCBurns.length} PTGC burns found`);
    }
    await delay(50);
  }

  const allPTGCByUFO = [...newPTGCBurns, ...existingPTGCByUFO];
  allPTGCByUFO.sort((a, b) => b.t - a.t);
  console.log(`Total PTGC burns by UFO: ${allPTGCByUFO.length}`);
  return allPTGCByUFO;
}

// ============================================
// CALCULATE PERIOD TOTALS
// ============================================
function calculatePeriods(burns) {
  const now = Date.now();
  const result = {
    h12: { count: 0, amount: 0 },
    h24: { count: 0, amount: 0 },
    d7:  { count: 0, amount: 0 },
    d30: { count: 0, amount: 0 },
    d90: { count: 0, amount: 0 }
  };
  for (const burn of burns) {
    const age = now - burn.t;
    if (age <=  12 * 3600000) { result.h12.count++; result.h12.amount += burn.a; }
    if (age <=  24 * 3600000) { result.h24.count++; result.h24.amount += burn.a; }
    if (age <=   7 * 86400000) { result.d7.count++;  result.d7.amount  += burn.a; }
    if (age <=  30 * 86400000) { result.d30.count++; result.d30.amount += burn.a; }
    if (age <=  90 * 86400000) { result.d90.count++; result.d90.amount += burn.a; }
  }
  return result;
}

// ============================================
// MAIN
// ============================================
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('UFO → PTGC BURN FETCHER v2 (fast, incremental)');
  console.log('Does NOT modify any existing burn files.');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));

  const dataDir    = path.join(__dirname, '..', 'data');
  const outputPath = path.join(dataDir, 'ufo-ptgc-burns.json');

  // Load existing cached data for incremental mode
  let existingUFOBurns  = [];
  let existingPTGCByUFO = [];
  try {
    if (fs.existsSync(outputPath)) {
      const existing    = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
      existingUFOBurns  = existing._ufoBurnsCache  || [];
      existingPTGCByUFO = existing._ptgcByUFOCache || [];
      console.log(`Loaded cache: ${existingUFOBurns.length} UFO burns, ${existingPTGCByUFO.length} PTGC burns`);
    } else {
      console.log('No existing cache — full fetch from UFO launch');
    }
  } catch (e) {
    console.log('Cache load failed, starting fresh:', e.message);
  }

  // Step 1: Fetch UFO burns (fast — incremental)
  const ufoBurns = await fetchUFOBurns(existingUFOBurns);

  // Step 2: Look up PTGC burns via receipts (only new txs)
  const ptgcByUFOBurns = await findPTGCBurnsInReceipts(ufoBurns, existingPTGCByUFO);

  // Step 3: Calculate totals
  const totalPTGCbyUFO   = ptgcByUFOBurns.reduce((s, b) => s + b.a, 0);
  const totalUFOBurned   = ufoBurns.reduce((s, b) => s + b.a, 0);
  const ptgcByUFOPeriods = calculatePeriods(ptgcByUFOBurns);
  const ufoPeriods       = calculatePeriods(ufoBurns);

  // Step 4: Write output — includes internal caches for next incremental run
  const output = {
    lastUpdated: new Date().toISOString(),
    note: 'PTGCbyUFO identified by fetching UFO burn tx receipts and finding PTGC burns within the same transaction.',

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

    // Internal caches — used for incremental runs, not for dashboard consumption
    _ufoBurnsCache:  ufoBurns,
    _ptgcByUFOCache: ptgcByUFOBurns
  };

  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`\nWritten: ${outputPath}`);

  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  console.log(`\nPTGC burned by UFO:`);
  console.log(`  Lifetime: ${totalPTGCbyUFO.toLocaleString()} PTGC (${ptgcByUFOBurns.length} burn events)`);
  console.log(`  12H:  ${ptgcByUFOPeriods.h12.amount.toLocaleString()}`);
  console.log(`  24H:  ${ptgcByUFOPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:   ${ptgcByUFOPeriods.d7.amount.toLocaleString()}`);
  console.log(`  30D:  ${ptgcByUFOPeriods.d30.amount.toLocaleString()}`);
  console.log(`  90D:  ${ptgcByUFOPeriods.d90.amount.toLocaleString()}`);
  console.log(`\nUFO burned (reference):`);
  console.log(`  Lifetime: ${totalUFOBurned.toLocaleString()} UFO (${ufoBurns.length} txs)`);
  console.log(`  24H:  ${ufoPeriods.h24.amount.toLocaleString()}`);
  console.log(`  7D:   ${ufoPeriods.d7.amount.toLocaleString()}`);
  console.log(`\nCompleted: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
