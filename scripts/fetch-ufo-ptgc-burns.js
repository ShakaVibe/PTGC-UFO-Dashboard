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
 * UFO has a few thousand burn transactions total. We only need that many receipt
 * lookups instead of scanning millions of blocks of PTGC history.
 * Subsequent runs are even faster — only new UFO burns since last run.
 *
 * MIGRATION (Sep 2026): UFO moved to a new contract on 2026-07-08. Both contracts
 * burn pTGC — the retired one still does on residual trading — so this script now
 * scans EVERY contract in CONTRACTS and tags each row with `c` (the contract key).
 * Totals are reported combined AND per contract (`byContract`), so the dashboard can
 * treat v1 as a frozen historical base and v2 as the live token. Rows in an older
 * cache file that carry no `c` are v1 rows and are upgraded in place.
 *
 * OUTPUT:
 * Writes ONLY to data/ufo-ptgc-burns.json — does NOT touch any existing files.
 */

const fs   = require('fs');
const path = require('path');

// Addresses
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';

/* Every UFO contract that has ever burned pTGC, oldest first. `launch` bounds the
   first (non-incremental) scan for that contract. Add a new entry here if UFO ever
   migrates again; nothing else needs to change. */
const CONTRACTS = [
  { key: 'v1', address: '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018', launch: '2024-05-18', label: 'UFO v1 (retired 2026-07-08, still burns on residual trades)' },
  { key: 'v2', address: '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6', launch: '2026-07-08', label: 'UFO v2 (live)' }
];
const LIVE_KEY = 'v2';   // the contract the dashboard shows as "UFO"

const UFO_DECIMALS  = 18;
const PTGC_DECIMALS = 18;

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
// CHAIN HEAD (read once per run, shared by every contract)
// ============================================
async function readHead() {
  const blockHex = await rpcCall('eth_blockNumber', []);
  if (!blockHex) throw new Error('Could not get block number');
  const currentBlock = parseInt(blockHex, 16);
  const latestBlockData = await rpcCall('eth_getBlockByNumber', ['latest', false]);
  if (!latestBlockData) throw new Error('Could not get latest block');
  const latestTs = parseInt(latestBlockData.timestamp, 16) * 1000;
  return { currentBlock, latestTs, tsFromBlock: (blockNum) => latestTs - (currentBlock - blockNum) * MS_PER_BLOCK };
}

// ============================================
// FETCH UFO BURNS for one contract (incremental)
// ============================================
async function fetchUFOBurns(contract, head, existingBurns = []) {
  console.log('\n' + '='.repeat(50));
  console.log(`Fetching ${contract.key} burns via eth_getLogs (${contract.address})...`);
  console.log('='.repeat(50));

  const { currentBlock, latestTs, tsFromBlock } = head;

  // Incremental: start from just before the newest stored burn
  let fromBlock;
  if (existingBurns.length > 0) {
    const lastTs = existingBurns[0].t;
    const blocksAgo = Math.ceil((latestTs - lastTs) / MS_PER_BLOCK);
    fromBlock = Math.max(0, currentBlock - blocksAgo - 1000);
    console.log(`Incremental mode: last burn ${new Date(lastTs).toISOString()}`);
  } else {
    const launchMs = new Date(contract.launch).getTime();
    const msAgo = latestTs - launchMs;
    const blocksAgo = Math.ceil(msAgo / MS_PER_BLOCK);
    fromBlock = Math.max(0, currentBlock - blocksAgo - 5000);   // small pad: MS_PER_BLOCK is nominal
    console.log(`First run for ${contract.key}: scanning from launch ${new Date(launchMs).toISOString()}`);
  }

  const totalBlocks = currentBlock - fromBlock;
  const totalChunks = Math.ceil(totalBlocks / LOG_CHUNK);
  console.log(`Scanning ${totalBlocks.toLocaleString()} blocks in ~${totalChunks} chunks...`);

  const allLogs = [];
  let chunksDone = 0;

  for (let start = fromBlock; start <= currentBlock; start += LOG_CHUNK) {
    const end = Math.min(start + LOG_CHUNK - 1, currentBlock);
    const result = await rpcCall('eth_getLogs', [{
      address: contract.address,
      fromBlock: '0x' + start.toString(16),
      toBlock:   '0x' + end.toString(16),
      topics: [TRANSFER_SIG, null, BURN_ADDR_TOPIC]
    }]);
    if (result && result.length > 0) allLogs.push(...result);
    chunksDone++;
    if (chunksDone % 100 === 0 || chunksDone === totalChunks) {
      console.log(`  ${chunksDone}/${totalChunks} chunks | ${allLogs.length} new ${contract.key} burn logs`);
    }
    await delay(50);
  }

  console.log(`New ${contract.key} burn logs: ${allLogs.length}`);

  const newBurns = allLogs.map(log => {
    const blockNum = parseInt(log.blockNumber, 16);
    const bigVal   = BigInt(log.data);
    const divisor  = BigInt(10) ** BigInt(UFO_DECIMALS);
    const whole    = Number(bigVal / divisor);
    const frac     = Number(bigVal % divisor) / Math.pow(10, UFO_DECIMALS);
    return { t: tsFromBlock(blockNum), a: whole + frac, tx: log.transactionHash, c: contract.key };
  });

  // Deduplicate against existing
  const existingTxSet = new Set(existingBurns.map(b => b.tx));
  const dedupedNew = newBurns.filter(b => !existingTxSet.has(b.tx));
  console.log(`New unique ${contract.key} burns: ${dedupedNew.length}`);

  const allBurns = [...dedupedNew, ...existingBurns];
  allBurns.sort((a, b) => b.t - a.t);
  console.log(`Total ${contract.key} burns: ${allBurns.length}`);
  return allBurns;
}

// ============================================
// LOOK UP PTGC BURNS VIA RECEIPTS (incremental)
// ============================================
async function findPTGCBurnsInReceipts(ufoBurns, existingPTGCByUFO = [], existingNoPtgc = []) {
  console.log('\n' + '='.repeat(50));
  console.log('Looking up PTGC burns in UFO burn transaction receipts...');
  console.log('='.repeat(50));

  /* Only process tx hashes we haven't already looked up. A UFO burn tx with NO pTGC burn
     in its receipt used to be re-fetched on every run (it never entered the PTGC cache),
     ~160 wasted receipt lookups per run; `_noPtgcTxCache` remembers those now. */
  const existingTxSet = new Set([...existingPTGCByUFO.map(b => b.tx), ...existingNoPtgc]);
  const newUFOBurns   = ufoBurns.filter(b => !existingTxSet.has(b.tx));
  console.log(`New UFO burn txs to look up: ${newUFOBurns.length}`);
  console.log(`Already cached: ${existingPTGCByUFO.length} PTGC burns, ${existingNoPtgc.length} txs known to have none`);

  if (newUFOBurns.length === 0) {
    console.log('Nothing new to look up — using cached data');
    return { rows: existingPTGCByUFO, noPtgc: existingNoPtgc };
  }

  const burnAddrPadded = '0x000000000000000000000000' + BURN_ADDRESS.slice(2).toLowerCase();
  const newPTGCBurns   = [];
  const newNoPtgc      = [];

  for (let i = 0; i < newUFOBurns.length; i += RECEIPT_CONCURRENCY) {
    const batch    = newUFOBurns.slice(i, i + RECEIPT_CONCURRENCY);
    const receipts = await Promise.all(
      batch.map(b => rpcCall('eth_getTransactionReceipt', [b.tx]))
    );

    for (let j = 0; j < batch.length; j++) {
      const receipt = receipts[j];
      if (!receipt || !receipt.logs) continue;   // unreadable receipt: not cached, retried next run
      let found = 0;

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
            tx: batch[j].tx,
            c:  batch[j].c
          });
          found++;
        }
      }
      if (!found) newNoPtgc.push(batch[j].tx);
    }

    if ((i + RECEIPT_CONCURRENCY) % 200 === 0 || i + RECEIPT_CONCURRENCY >= newUFOBurns.length) {
      console.log(`  ${Math.min(i + RECEIPT_CONCURRENCY, newUFOBurns.length)}/${newUFOBurns.length} receipts | ${newPTGCBurns.length} PTGC burns found`);
    }
    await delay(50);
  }

  const allPTGCByUFO = [...newPTGCBurns, ...existingPTGCByUFO];
  allPTGCByUFO.sort((a, b) => b.t - a.t);
  console.log(`Total PTGC burns by UFO: ${allPTGCByUFO.length} (+${newNoPtgc.length} txs with no pTGC burn remembered)`);
  return { rows: allPTGCByUFO, noPtgc: [...newNoPtgc, ...existingNoPtgc] };
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

function summarize(rows) {
  return {
    totalBurned: rows.reduce((s, b) => s + b.a, 0),
    burnCount:   rows.length,
    periods:     calculatePeriods(rows)
  };
}

// ============================================
// MAIN
// ============================================
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('UFO → PTGC BURN FETCHER v3 (fast, incremental, multi-contract)');
  console.log('Does NOT modify any existing burn files.');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));

  const dataDir    = path.join(__dirname, '..', 'data');
  const outputPath = path.join(dataDir, 'ufo-ptgc-burns.json');

  // Load existing cached data for incremental mode. Rows without `c` predate the
  // multi-contract format and are v1 rows.
  let existingUFOBurns  = [];
  let existingPTGCByUFO = [];
  let existingNoPtgc    = [];
  try {
    if (fs.existsSync(outputPath)) {
      const existing    = JSON.parse(fs.readFileSync(outputPath, 'utf8'));
      const tag = rows => (rows || []).map(r => (r.c ? r : { ...r, c: 'v1' }));
      existingUFOBurns  = tag(existing._ufoBurnsCache);
      existingPTGCByUFO = tag(existing._ptgcByUFOCache);
      existingNoPtgc    = Array.isArray(existing._noPtgcTxCache) ? existing._noPtgcTxCache : [];
      console.log(`Loaded cache: ${existingUFOBurns.length} UFO burns, ${existingPTGCByUFO.length} PTGC burns`);
    } else {
      console.log('No existing cache — full fetch from each contract\'s launch');
    }
  } catch (e) {
    console.log('Cache load failed, starting fresh:', e.message);
  }

  const head = await readHead();

  // Step 1: Fetch UFO burns per contract (fast — incremental per contract)
  let ufoBurns = [];
  for (const contract of CONTRACTS) {
    const mine = existingUFOBurns.filter(b => b.c === contract.key);
    const rows = await fetchUFOBurns(contract, head, mine);
    ufoBurns = ufoBurns.concat(rows);
  }
  ufoBurns.sort((a, b) => b.t - a.t);

  // Step 2: Look up PTGC burns via receipts (only new txs)
  const { rows: ptgcByUFOBurns, noPtgc } = await findPTGCBurnsInReceipts(ufoBurns, existingPTGCByUFO, existingNoPtgc);

  // Step 3: Totals — combined and per contract
  const byContract = {};
  for (const contract of CONTRACTS) {
    byContract[contract.key] = {
      address: contract.address,
      label:   contract.label,
      launch:  contract.launch,
      PTGCbyUFO: summarize(ptgcByUFOBurns.filter(b => b.c === contract.key)),
      UFOBurns:  summarize(ufoBurns.filter(b => b.c === contract.key))
    };
  }
  const ptgcAll = summarize(ptgcByUFOBurns);
  const ufoAll  = summarize(ufoBurns);

  // Step 4: Write output — includes internal caches for next incremental run
  const output = {
    lastUpdated: new Date().toISOString(),
    schema: 2,
    note: 'PTGCbyUFO identified by fetching UFO burn tx receipts and finding PTGC burns within the same transaction. Combined totals cover every UFO contract; byContract splits them. liveContract is the token the dashboard currently shows.',
    liveContract: LIVE_KEY,
    liveAddress:  CONTRACTS.find(c => c.key === LIVE_KEY).address,

    // Combined (all contracts) — same shape as before, so older readers keep working
    PTGCbyUFO: ptgcAll,
    UFOBurns:  ufoAll,

    byContract,

    // Internal caches — used for incremental runs, not for dashboard consumption
    _ufoBurnsCache:  ufoBurns,
    _ptgcByUFOCache: ptgcByUFOBurns,
    _noPtgcTxCache:  noPtgc
  };

  fs.writeFileSync(outputPath, JSON.stringify(output, null, 2));
  console.log(`\nWritten: ${outputPath}`);

  console.log('\n' + '='.repeat(60));
  console.log('SUMMARY');
  console.log('='.repeat(60));
  for (const contract of CONTRACTS) {
    const s = byContract[contract.key];
    console.log(`\n[${contract.key}] ${contract.label}`);
    console.log(`  PTGC burned by UFO — lifetime: ${s.PTGCbyUFO.totalBurned.toLocaleString()} PTGC (${s.PTGCbyUFO.burnCount} events)`);
    console.log(`    24H: ${s.PTGCbyUFO.periods.h24.amount.toLocaleString()}   7D: ${s.PTGCbyUFO.periods.d7.amount.toLocaleString()}   30D: ${s.PTGCbyUFO.periods.d30.amount.toLocaleString()}   90D: ${s.PTGCbyUFO.periods.d90.amount.toLocaleString()}`);
    console.log(`  UFO burned (reference) — lifetime: ${s.UFOBurns.totalBurned.toLocaleString()} UFO (${s.UFOBurns.burnCount} txs)`);
  }
  console.log(`\nCombined PTGC burned by UFO: ${ptgcAll.totalBurned.toLocaleString()} PTGC (${ptgcAll.burnCount} events)`);
  console.log(`\nCompleted: ${new Date().toISOString()}`);
  console.log('='.repeat(60));
}

main().catch(err => {
  console.error('FATAL ERROR:', err);
  process.exit(1);
});
