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
 * v4 (2026-10-24, with the burn archive v2 fix — Shaka: "we need it to be right"):
 *  - a burn is identified by its chain position (block `b` + log index `i`), never by its tx alone;
 *  - each transaction's receipt is read ONCE. v3 read it once per UFO-burn log in that tx, so a tx with two UFO
 *    burns stored its pTGC burns twice (three → nine rows …): 126 txs, +221 M pTGC on the v1 lifetime, +20 M on v2;
 *  - times are the blocks' real timestamps (shared code from fetch-burn-history.js), not head − blocks × 10 s;
 *  - each run re-reads from the last block it finished (`scannedTo`) − 1800 to the head − 96.
 *  The first v4 run rebuilds every row from the receipts of the transactions already known (all-or-nothing: one
 *  unreadable receipt and nothing is written; the next run tries again).
 *
 * OUTPUT:
 * Writes ONLY to data/ufo-ptgc-burns.json + data/ufo-ptgc-burns-cache.json — does NOT touch any other file.
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

const TRANSFER_SIG    = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const BURN_ADDR_TOPIC = '0x0000000000000000000000000000000000000000000000000000000000000369';
const MS_PER_BLOCK    = 10000;   // only to place a first-ever scan near a contract's launch date
const RECEIPT_CONCURRENCY = 20;
const RESCAN_BLOCKS   = 1800;    // each run re-reads ~5 h before where the last one stopped
const SCHEMA = 4;

// The chain reads are shared with the burn archive (scripts/fetch-burn-history.js, archive v2): real block times,
// getLogs with a fatal-on-hole policy, the finality margin.
const B = require('./fetch-burn-history.js');
const rpcCall = B.rpcCall;

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
const key = r => r.b + ':' + r.i;
const isBurnLog = (l, token) => (l.address || '').toLowerCase() === token.toLowerCase() && l.topics && l.topics[0] === TRANSFER_SIG &&
  l.topics.length >= 3 && (l.topics[2] || '').toLowerCase() === BURN_ADDR_TOPIC;
const amountOf = (data, dec) => { const v = BigInt(data && data !== '0x' ? data : '0x0'), d = 10n ** BigInt(dec); return Number(v / d) + Number(v % d) / Number(d); };

/* One receipt per tx (never one per log). Resolves Map tx → receipt; a tx whose receipt could not be read is absent. */
async function readReceipts(txs) {
  const out = new Map();
  for (let k = 0; k < txs.length; k += RECEIPT_CONCURRENCY) {
    const batch = txs.slice(k, k + RECEIPT_CONCURRENCY);
    const rs = await Promise.all(batch.map(tx => rpcCall('eth_getTransactionReceipt', [tx], 4)));
    batch.forEach((tx, j) => { const r = rs[j]; if (r && Array.isArray(r.logs) && r.blockNumber) out.set(tx, r); });
    if ((k / RECEIPT_CONCURRENCY) % 25 === 24 || k + RECEIPT_CONCURRENCY >= txs.length) console.log(`  ${Math.min(k + RECEIPT_CONCURRENCY, txs.length)}/${txs.length} receipts read`);
    await delay(50);
  }
  return out;
}

/* Everything a receipt says: the UFO burns (of any known contract) and the pTGC burns in that tx. Times filled later. */
function rowsFromReceipt(tx, r) {
  const b = parseInt(r.blockNumber, 16);
  const ufo = [], ptgc = [];
  let c = null;
  for (const l of r.logs) {
    if (l.removed) continue;
    const i = parseInt(l.logIndex, 16);
    const ct = CONTRACTS.find(x => isBurnLog(l, x.address));
    if (ct) { ufo.push({ b, i, t: 0, a: amountOf(l.data, UFO_DECIMALS), tx, c: ct.key }); if (!c) c = ct.key; }
  }
  if (!c) return { ufo, ptgc };
  for (const l of r.logs) {
    if (l.removed || !isBurnLog(l, PTGC_ADDRESS)) continue;
    ptgc.push({ b, i: parseInt(l.logIndex, 16), t: 0, a: amountOf(l.data, PTGC_DECIMALS), f: ('0x' + l.topics[1].slice(26)).toLowerCase(), tx, c });
  }
  return { ufo, ptgc };
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
  console.log('UFO → PTGC BURN FETCHER v4 (block + log index, one receipt per tx, real block times)');
  console.log('Does NOT modify any existing burn files.');
  console.log('Started:', new Date().toISOString());
  console.log('='.repeat(60));

  const dataDir    = path.join(__dirname, '..', 'data');
  const outputPath = path.join(dataDir, 'ufo-ptgc-burns.json');
  /* a32 (2026-09-17): the generator's caches (every UFO burn, every PTGC-by-UFO row, the
     no-PTGC tx list — 2.4 MB of the old 3.1 MB file) now live in their own file that nothing
     serves. The dashboard file keeps the summaries plus `rows`: the v1 rows inside the last
     91 days, which is all index.html reads (the 7D/30D/90D "PTGC burned by UFO" windows). */
  const cachePath  = path.join(dataDir, 'ufo-ptgc-burns-cache.json');

  // Load existing cached data for incremental mode. Rows without `c` predate the
  // multi-contract format and are v1 rows. The cache file wins; a pre-a32 checkout still
  // carries the caches inside the served file, so fall back to those once.
  let existingUFOBurns  = [];
  let existingPTGCByUFO = [];
  let existingNoPtgc    = [];
  let cacheSchema = 0, cacheScannedTo = null;
  try {
    const src = fs.existsSync(cachePath) ? cachePath : (fs.existsSync(outputPath) ? outputPath : null);
    if (src) {
      const existing    = JSON.parse(fs.readFileSync(src, 'utf8'));
      const tag = rows => (rows || []).map(r => (r.c ? r : { ...r, c: 'v1' }));
      existingUFOBurns  = tag(existing._ufoBurnsCache);
      existingPTGCByUFO = tag(existing._ptgcByUFOCache);
      existingNoPtgc    = Array.isArray(existing._noPtgcTxCache) ? existing._noPtgcTxCache : [];
      cacheSchema       = existing.schema || 0;
      cacheScannedTo    = existing.scannedTo || null;
      console.log(`Loaded cache: ${existingUFOBurns.length} UFO burns, ${existingPTGCByUFO.length} PTGC burns`);
    } else {
      console.log('No existing cache — full fetch from each contract\'s launch');
    }
  } catch (e) {
    console.error('Cache exists but cannot be read — refusing a full rescan from launch (it outlasts the job timeout):', e.message);   // Audit IV e23
    process.exit(1);
  }

  const migrate = cacheSchema < SCHEMA;
  const ufoByKey = new Map(), ptgcByKey = new Map();
  let noPtgc = new Set(existingNoPtgc);
  const scannedTo = Object.assign({}, cacheScannedTo || {});

  if (migrate) {
    /* v3 → v4: rebuild every row from the receipts of the txs already known. All-or-nothing. */
    const txs = [...new Set(existingUFOBurns.map(r => r.tx).concat(existingPTGCByUFO.map(r => r.tx)))];
    console.log(`\nMIGRATION v3 → v4: re-reading ${txs.length} receipts (one per transaction) …`);
    const rec = await readReceipts(txs);
    const missing = txs.filter(tx => !rec.has(tx));
    if (missing.length) throw new Error(`${missing.length} receipt(s) could not be read (e.g. ${missing[0]}) — nothing written; the next run tries again`);
    noPtgc = new Set();
    for (const tx of txs) {
      const { ufo, ptgc } = rowsFromReceipt(tx, rec.get(tx));
      for (const r of ufo) ufoByKey.set(key(r), r);
      for (const r of ptgc) ptgcByKey.set(key(r), r);
      if (ufo.length && !ptgc.length) noPtgc.add(tx);
    }
    for (const ct of CONTRACTS) {
      let mx = null;
      for (const r of ufoByKey.values()) if (r.c === ct.key && (mx == null || r.b > mx)) mx = r.b;
      if (mx != null) scannedTo[ct.key] = mx;   // known complete up to its newest burn; the scan below re-reads 1800 blocks before it
    }
    const was = existingPTGCByUFO.reduce((s, r) => s + r.a, 0), now = [...ptgcByKey.values()].reduce((s, r) => s + r.a, 0);
    console.log(`  rebuilt: ${ufoByKey.size} UFO burns (was ${existingUFOBurns.length} rows), ${ptgcByKey.size} pTGC burns = ${now.toLocaleString()} (was ${existingPTGCByUFO.length} rows = ${was.toLocaleString()})`);
  } else {
    for (const r of existingUFOBurns) ufoByKey.set(key(r), r);
    for (const r of existingPTGCByUFO) ptgcByKey.set(key(r), r);
  }

  // Step 1: new UFO burns per contract, from the last finished block (minus a re-read margin) to the head minus the finality margin
  const head = await B.headBlock('ufo-ptgc-burns');
  const to = head - B.CONFIRM_BLOCKS;
  for (const ct of CONTRACTS) {
    let from;
    if (Number.isInteger(scannedTo[ct.key])) from = Math.max(0, scannedTo[ct.key] - RESCAN_BLOCKS);
    else {   // first ever scan of this contract: from a little before its launch date
      const headTs = (await B.blockTimes([head])).get(head);
      from = Math.max(0, head - Math.ceil((headTs - Date.parse(ct.launch)) / MS_PER_BLOCK) - 50000);
    }
    if (from > to) { console.log(`  ${ct.key}: nothing to scan (head behind)`); continue; }
    const rows = await B.scanBurns(ct.address, UFO_DECIMALS, from, to, { label: ct.key });
    let fresh = 0;
    for (const r of rows) { const row = { b: r.b, i: r.i, t: r.t, a: r.a, tx: r.tx, c: ct.key }; if (!ufoByKey.has(key(row))) fresh++; ufoByKey.set(key(row), row); }
    scannedTo[ct.key] = to;
    console.log(`  ${ct.key}: ${rows.length} UFO burns in blocks ${from}–${to}, ${fresh} new`);
  }

  // Step 2: pTGC burns in the receipts of txs not read yet (one receipt per tx)
  const doneTx = new Set([...ptgcByKey.values()].map(r => r.tx).concat([...noPtgc]));
  const newTx = [...new Set([...ufoByKey.values()].map(r => r.tx))].filter(tx => !doneTx.has(tx));
  console.log(`\nNew UFO burn txs to look up: ${newTx.length}`);
  if (newTx.length) {
    const rec = await readReceipts(newTx);
    for (const tx of newTx) {
      const r = rec.get(tx);
      if (!r) continue;   // unreadable: not marked done, read again next run
      const { ptgc } = rowsFromReceipt(tx, r);
      for (const row of ptgc) ptgcByKey.set(key(row), row);
      if (!ptgc.length) noPtgc.add(tx);
    }
  }

  // Real block times for every row that has none yet (all of them on the migration run)
  const need = [...ufoByKey.values(), ...ptgcByKey.values()].filter(r => !(r.t > 0)).map(r => r.b);
  if (need.length) {
    const times = await B.blockTimes(need);
    for (const r of [...ufoByKey.values(), ...ptgcByKey.values()]) if (!(r.t > 0)) r.t = times.get(r.b);
  }
  const byNewest = (x, y) => (y.t - x.t) || (y.b - x.b) || (y.i - x.i);
  const ufoBurns = [...ufoByKey.values()].sort(byNewest);
  const ptgcByUFOBurns = [...ptgcByKey.values()].sort(byNewest);
  console.log(`Total: ${ufoBurns.length} UFO burns, ${ptgcByUFOBurns.length} pTGC burns by UFO`);

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
    schema: 2,   // the shape the dashboard reads (unchanged); the generator's own format is the cache's `schema`
    note: 'PTGCbyUFO identified by fetching UFO burn tx receipts and finding PTGC burns within the same transaction. Combined totals cover every UFO contract; byContract splits them. liveContract is the token the dashboard currently shows.',
    liveContract: LIVE_KEY,
    liveAddress:  CONTRACTS.find(c => c.key === LIVE_KEY).address,

    // Combined (all contracts) — same shape as before, so older readers keep working
    PTGCbyUFO: ptgcAll,
    UFOBurns:  ufoAll,

    byContract,

    /* a32: the dated rows the dashboard buckets into its 7D/30D/90D windows — retired-contract
       (v1) rows only, inside the last 91 days, {t,a,tx,c}. The live contract is measured on chain. */
    rows: ptgcByUFOBurns
      .filter(r => (r.c || 'v1') === 'v1' && r.t >= Date.now() - 91 * 86400000)
      .map(r => ({ t: r.t, a: r.a, tx: r.tx, c: 'v1' })),
  };
  const cache = {
    lastUpdated: output.lastUpdated,
    schema: SCHEMA,
    scannedTo,
    note: 'Generator-only caches for fetch-ufo-ptgc-burns.js (incremental runs). Nothing on the site reads this file.',
    _ufoBurnsCache:  ufoBurns,
    _ptgcByUFOCache: ptgcByUFOBurns,
    _noPtgcTxCache:  [...noPtgc]
  };

  const writeAtomic = (f, text) => { fs.writeFileSync(f + '.tmp', text); fs.renameSync(f + '.tmp', f); };
  writeAtomic(cachePath,  JSON.stringify(cache));
  writeAtomic(outputPath, JSON.stringify(output));
  const kb = p => (fs.statSync(p).size / 1024).toFixed(0);
  console.log(`\nWritten: ${outputPath} (${kb(outputPath)} KB, ${output.rows.length} dated v1 rows) + ${cachePath} (${kb(cachePath)} KB, generator only)`);

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
