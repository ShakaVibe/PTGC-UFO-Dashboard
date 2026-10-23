/**
 * Fetch Burn History Script - RPC VERSION (SPLIT FILES)
 * 
 * Splits burn data into multiple files to stay under GitHub's 100MB limit
 * 
 * UPDATED: Holder count now fetched from PulseScan (not Moralis) for consistency
 * UPDATED: Holder history now stores ONE snapshot per day
 * 
 * Files created:
 * - burn-summary.json (totals, prices, periods, snapshots)
 * - ptgc-burns-2023-h2.json (May-Dec 2023)
 * - ptgc-burns-2024-h1.json (Jan-Jun 2024)
 * - ptgc-burns-2024-h2.json (Jul-Dec 2024)
 * - ptgc-burns-2025-h1.json (Jan-Jun 2025)
 * - ptgc-burns-2025-h2.json (Jul-Dec 2025)
 * - ptgc-burns-2026-h1.json, ptgc-burns-2026-h2.json, … (one file per half-year, from the burn's real block time)
 * Since 2026-10-24 (archive v2) every row from 2025-07 on is {b, i, t, a, f}: block, log index, real block time (ms),
 * amount, sender — see BURN ARCHIVE v2 below.
 * - ufo-burns.json (all UFO burns - small file)
 * - holder-history.json (daily holder snapshots - THIS SCRIPT IS THE ONLY SOURCE)
 */

const fs = require('fs');
const path = require('path');

// No Moralis key needed — price/volume/liquidity now come from DexScreener (keyless).

// Addresses
const BURN_ADDRESS = '0x0000000000000000000000000000000000000369';
const PTGC_ADDRESS = '0x94534EeEe131840b1c0F61847c572228bdfDDE93';
// OLD UFO contract (pre-migration). Kept ONLY for historical burn scanning below,
// so ufo-burns.json and past burn totals stay intact. Do NOT use this for live reads.
const UFO_ADDRESS = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018';
// NEW UFO contract (post-migration, ~2026-07-08). This is the LIVE token. Every
// current-state read — holders, price, volume, pairs, transactions — must use this
// so holder-history.json and the dashboard reflect the real token, not the dead one.
const UFO_ADDRESS_NEW = '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6';

// LP Pairs (for identifying automated buyback burns)
const PTGC_LP_PAIR = '0xf5a89a6487d62df5308cdda89c566c5b5ef94c11';
const UFO_LP_PAIR = '0xbea0e55b82eb975280041f3b49c4d0bd937b72d5';
// Dashboard main pairs (PTGC/WPLS, UFO/WPLS): the price source when present, so data files match the dashboard.
const PRICE_MAIN_PAIRS = new Set(['0xf5a89a6487d62df5308cdda89c566c5b5ef94c11', '0xe221e6fc30e5787f0d551f980b4da1055d832a03']);

const PTGC_DECIMALS = 18;
const UFO_DECIMALS = 18;

const DEXSCREENER_BASE = 'https://api.dexscreener.com/latest/dex';
const PULSESCAN_BASE = 'https://api.scan.pulsechain.com/api/v2';

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// ============================================
// RPC INFRASTRUCTURE (replaces Moralis for burn fetching)
// ============================================
const RPC_URL = 'https://rpc.pulsechain.com';
// Transfer(address indexed from, address indexed to, uint256 value)
const TRANSFER_SIG = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
// Burn address 0x...0369 padded to 32 bytes as a log topic
const BURN_ADDR_TOPIC = '0x0000000000000000000000000000000000000000000000000000000000000369';
const LOG_CHUNK = 2000;     // blocks per eth_getLogs request (conservative)

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

/* ============================================================================================
   BURN ARCHIVE v2 (2026-10-24, Shaka: "lets fix it.. we need it to be right").

   What was wrong (v1): every hourly run re-read the last ~3 h of burn logs and dropped the ones it
   thought it already had by matching "same sender, amount within 1 token, time within 10 minutes".
   The times were GUESSED (head time − blocks × 10 s), and PulseChain runs ~3 % slower than 10 s a
   block, so the same burn got a different guessed time in the next run. Once two runs' guesses were
   more than 10 minutes apart the match failed and the burn was saved again. From Oct 2025 on that
   happened more and more: by Oct 2026 the PTGC archive held 762 M more than the burn address ever
   received, and the 7D / 30D / 90D windows read +12 / +6 / +21 % (UFO v1's archive: 268 B logged vs
   149.6 B real).

   v2 rules:
   1. A burn is identified by WHERE it is on chain: block number `b` + log index `i`. Two rows with the
      same (b, i) are the same burn — no guessing, no tolerance.
   2. Times are the blocks' REAL timestamps (eth_getBlockByNumber, batched), not an estimate.
   3. Each run scans from the last block it finished (`archive.scannedTo` in burn-summary.json) minus
      RESCAN_BLOCKS, to the head minus CONFIRM_BLOCKS. Re-read rows replace themselves by key.
   4. After every run the archive's sum is checked against balanceOf(0x…369) at the same block. A
      mismatch is a ::warning:: in the run, `archive.reconcile.ok:false` in the summary, and the next
      run re-reads everything since the last block where the two agreed (up to ~7 days) with the
      fresh read replacing what is stored — the archive heals itself.
   5. A one-time rebuild (tools/rebuild-burn-archive.js) writes data/ptgc-burns-rebuild-<token>-*.json;
      the next pipeline run swaps those rows in for every stored row from `replaceFromTs` on, carries
      on from the rebuild's last block, and deletes the rebuild files.
   ============================================================================================ */
const CONFIRM_BLOCKS = 96;          // scan to head − 96 blocks (~16 min): past PoS finality (~64 blocks), so a re-org cannot move a stored burn
const RESCAN_BLOCKS = 1800;         // every run re-reads ~5 h before where the last one stopped (one getLogs chunk)
const RECOVERY_MAX_BLOCKS = 60480;  // ~7 days: the furthest back a failed reconciliation widens the next re-read
const RECONCILE_TOLERANCE = 100;    // tokens: float sums over millions of rows vs an exact wei balance
const REBUILD_PREFIX = 'ptgc-burns-rebuild-';   // matches the pipeline's 'data/ptgc-burns-*.json' pathspec, so deleting them is committed
const BATCH_SIZE = 100;             // eth_getBlockByNumber calls per JSON-RPC batch

/* Write via <file>.tmp + rename, so a runner killed mid-write never leaves (and commits) a cut-off archive file.
   The .tmp name matches neither the period-file pattern nor the pipeline's pathspec. */
function writeFileAtomic(file, text) {
  fs.writeFileSync(file + '.tmp', text);
  fs.renameSync(file + '.tmp', file);
}

const hex = n => '0x' + n.toString(16);
const burnKey = r => r.b + ':' + r.i;

async function pool(items, n, fn) {
  let k = 0;
  const workers = Array.from({ length: Math.max(1, Math.min(n, items.length)) }, async () => {
    while (k < items.length) { const it = items[k++]; await fn(it); }
  });
  await Promise.all(workers);
}

/* One JSON-RPC batch. Resolves an array aligned with `reqs` (null where an entry failed); never throws. */
async function rpcBatch(reqs) {
  const body = reqs.map((r, k) => ({ jsonrpc: '2.0', id: k, method: r.method, params: r.params }));
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const controller = new AbortController();
      const tid = setTimeout(() => controller.abort(), 60000);
      const res = await fetch(RPC_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: controller.signal });
      clearTimeout(tid);
      const json = await res.json();
      if (!Array.isArray(json)) throw new Error('the node did not answer the batch with a list: ' + JSON.stringify(json).slice(0, 160));
      const out = new Array(reqs.length).fill(null);
      for (const r of json) if (r && r.result != null && Number.isInteger(r.id) && r.id >= 0 && r.id < reqs.length) out[r.id] = r.result;
      return out;
    } catch (e) {
      console.log(`  RPC batch failed: ${e.message}`);
      if (attempt < 2) await delay(2000 * (attempt + 1));
    }
  }
  return new Array(reqs.length).fill(null);
}

/* Real block timestamps (ms) for a list of block numbers. Batched; what a batch misses is asked again,
   then one by one. A block whose time cannot be read is FATAL (nothing is written). */
async function blockTimes(blocks, { concurrency = 1 } = {}) {
  const out = new Map();
  let todo = [...new Set(blocks)];
  for (let round = 0; round < 4 && todo.length; round++) {
    const miss = [];
    const parts = [];
    for (let k = 0; k < todo.length; k += BATCH_SIZE) parts.push(todo.slice(k, k + BATCH_SIZE));
    await pool(parts, concurrency, async part => {
      const res = await rpcBatch(part.map(b => ({ method: 'eth_getBlockByNumber', params: [hex(b), false] })));
      part.forEach((b, j) => {
        const r = res[j];
        const ts = r && r.timestamp ? parseInt(r.timestamp, 16) : NaN;
        if (Number.isFinite(ts) && ts > 0 && r.number && parseInt(r.number, 16) === b) out.set(b, ts * 1000);
        else miss.push(b);
      });
    });
    todo = miss;
    if (todo.length) { console.log(`  ${todo.length} block time(s) missing after round ${round + 1} — asking again`); await delay(2000 * (round + 1)); }
  }
  for (const b of todo) {   // last resort: one at a time (a node that refuses batches)
    const r = await rpcCall('eth_getBlockByNumber', [hex(b), false]);
    const ts = r && r.timestamp ? parseInt(r.timestamp, 16) : NaN;
    if (!(Number.isFinite(ts) && ts > 0)) throw new Error(`block ${b}: its timestamp could not be read — files left untouched`);
    out.set(b, ts * 1000);
  }
  return out;
}

async function headBlock(label) {
  const blockHex = await rpcCall('eth_blockNumber', []);
  const head = blockHex ? parseInt(blockHex, 16) : NaN;
  if (!Number.isInteger(head) || head <= 0) throw new Error(`${label}: could not read the head block — files left untouched`);
  return head;
}

/* Every Transfer(*, 0x…369) log of `address` in [from, to] → rows {b, i, t, a, f}, t = the block's real time. */
async function scanBurns(address, decimals, from, to, { chunk = LOG_CHUNK, concurrency = 1, label = '', retries = 3 } = {}) {
  const ranges = [];
  for (let s = from; s <= to; s += chunk) ranges.push([s, Math.min(s + chunk - 1, to)]);
  console.log(`  ${label} scanning blocks ${from}–${to} (${(to - from + 1).toLocaleString()} blocks, ${ranges.length} getLogs call(s))`);
  const logs = [];
  let done = 0;
  await pool(ranges, concurrency, async ([s, e]) => {
    const params = [{ address, fromBlock: hex(s), toBlock: hex(e), topics: [TRANSFER_SIG, null, BURN_ADDR_TOPIC] }];
    let result = await rpcCall('eth_getLogs', params, retries);
    if (result === null) { await delay(5000); result = await rpcCall('eth_getLogs', params, retries); }
    /* a31: a range that could not be read is FATAL, not "no burns in it" — throwing leaves every file untouched. */
    if (!Array.isArray(result)) throw new Error(`${label}: eth_getLogs failed for blocks ${s}–${e} after retries — aborting so the files are not written with a hole`);
    for (const l of result) logs.push(l);
    done++;
    if (done % 50 === 0 || done === ranges.length) console.log(`    ${done}/${ranges.length} ranges | ${logs.length} logs`);
  });
  const want = address.toLowerCase();
  const seen = new Set();
  const rows = [];
  const divisor = 10n ** BigInt(decimals);
  for (const log of logs) {
    if (log.removed) continue;
    const b = parseInt(log.blockNumber, 16), i = parseInt(log.logIndex, 16);
    if (!(Number.isInteger(b) && Number.isInteger(i) && b >= from && b <= to)) continue;   // never trust an answer outside the asked range
    if ((log.address || '').toLowerCase() !== want) continue;
    if (!log.topics || log.topics[0] !== TRANSFER_SIG || (log.topics[2] || '').toLowerCase() !== BURN_ADDR_TOPIC) continue;
    const k = b + ':' + i;
    if (seen.has(k)) continue;
    seen.add(k);
    const v = BigInt(log.data);   // exact wei → whole + fraction (no Number precision loss on large values)
    rows.push({ b, i, t: 0, a: Number(v / divisor) + Number(v % divisor) / Number(divisor), f: ('0x' + log.topics[1].slice(26)).toLowerCase(), tx: log.transactionHash });   // tx: for fetch-ufo-ptgc-burns.js (the archive files do not store it — rowOut)
  }
  if (rows.length) {
    const times = await blockTimes(rows.map(r => r.b), { concurrency });
    for (const r of rows) r.t = times.get(r.b);
  }
  return rows;
}

/* balanceOf(0x…369) of `address` at `block`, in tokens (exact wei → float). null if it could not be read. */
async function burnAddressBalance(address, decimals, block) {
  const r = await rpcCall('eth_call', [{ to: address, data: '0x70a08231' + BURN_ADDR_TOPIC.slice(2) }, hex(block)]);
  if (!r || r === '0x') return null;
  const v = BigInt(r), divisor = 10n ** BigInt(decimals);
  return Number(v / divisor) + Number(v % divisor) / Number(divisor);
}

/* The one-time rebuild files for a token (tools/rebuild-burn-archive.js). Every part must agree on the
   range and be present — a partial rebuild is refused (thrown), never half-applied. */
function loadRebuild(dataDir, token, address, prev) {
  const prefix = REBUILD_PREFIX + token.toLowerCase() + '-';
  let files = fs.readdirSync(dataDir).filter(f => f.startsWith(prefix) && f.endsWith('.json')).sort();
  /* Leftovers of a rebuild an earlier run already applied (it got past them: its summary's scannedTo is at or beyond their
     last block) — e.g. a run that died while deleting them. They are removed, not applied again. */
  if (files.length && prev && prev.schema === 2 && Number.isInteger(prev.scannedTo)) {
    files = files.filter(f => {
      const j = JSON.parse(fs.readFileSync(path.join(dataDir, f), 'utf8'));
      if (Number.isInteger(j.toBlock) && j.toBlock <= prev.scannedTo) { fs.unlinkSync(path.join(dataDir, f)); console.log(`  Removed ${f} — an earlier run already applied that rebuild`); return false; }
      return true;
    });
  }
  if (!files.length) return null;
  const parts = files.map(f => ({ f, j: JSON.parse(fs.readFileSync(path.join(dataDir, f), 'utf8')) }));
  const h = parts[0].j;
  const same = ['schema', 'token', 'address', 'replaceFromTs', 'fromBlock', 'toBlock', 'toTs', 'parts'];
  for (const { f, j } of parts) {
    for (const k of same) if (j[k] !== h[k]) throw new Error(`rebuild file ${f}: ${k} = ${j[k]} differs from ${files[0]} (${h[k]}) — refusing a mixed rebuild`);
  }
  if (h.schema !== 2 || (h.address || '').toLowerCase() !== address.toLowerCase()) throw new Error(`rebuild files for ${token} are not schema 2 for ${address}`);
  const idx = parts.map(p => p.j.part).sort((a, b) => a - b);
  if (idx.length !== h.parts || idx.some((p, k) => p !== k + 1)) throw new Error(`rebuild files for ${token}: parts ${idx.join(',')} of ${h.parts} — refusing a partial rebuild`);
  let burns = [];
  for (const { j } of parts) burns = burns.concat(j.burns);
  for (const r of burns) {
    if (!(Number.isInteger(r.b) && Number.isInteger(r.i) && r.b >= h.fromBlock && r.b <= h.toBlock && r.t >= h.replaceFromTs && r.a > 0)) {
      throw new Error(`rebuild files for ${token}: a row outside its declared range (${JSON.stringify(r)})`);
    }
  }
  console.log(`  Rebuild for ${token}: ${files.length} file(s), ${burns.length} burns, blocks ${h.fromBlock}–${h.toBlock}, replaces every stored row from ${new Date(h.replaceFromTs).toISOString()}`);
  return { files, replaceFromTs: h.replaceFromTs, fromBlock: h.fromBlock, toBlock: h.toBlock, toTs: h.toTs, burns };
}

/* Bring a token's archive up to the head. `existing` = the stored rows (rebuild already swapped in),
   `prev` = last run's burn-summary `archive` block for this token. Returns { burns, meta }. */
async function updateArchive(token, address, decimals, existing, rebuild, prev) {
  console.log(`\n${'='.repeat(50)}`);
  console.log(`Updating the ${token} burn archive (v2: block + log index, real block times)`);
  console.log(`${'='.repeat(50)}`);
  const head = await headBlock(token);
  const to = head - CONFIRM_BLOCKS;

  let known = rebuild ? rebuild.toBlock : (prev && Number.isInteger(prev.scannedTo) ? prev.scannedTo : null);
  if (known == null) {
    for (const r of existing) if (Number.isInteger(r.b) && (known == null || r.b > known)) known = r.b;
  }
  if (known == null) {
    throw new Error(`${token}: the stored burns carry no block positions and there are no rebuild files — refusing the old time-guessing merge that saved burns twice. Run tools/rebuild-burn-archive.js first.`);
  }
  /* Recovery: last run's reconciliation failed → re-read from the last block where archive and balance
     agreed, and let the fresh read REPLACE what is stored in that range (removes anything that should
     not be there, adds anything missing). */
  const recovery = !rebuild && !!(prev && prev.reconcile && prev.reconcile.ok === false);
  let from = known - RESCAN_BLOCKS;
  let capped = false;
  if (recovery) {
    const good = Number.isInteger(prev.lastReconciledBlock) ? prev.lastReconciledBlock : known;
    let start = good - RESCAN_BLOCKS;
    // the last re-read did not fix it either → go back twice as far as that one did (up to ~7 days)
    if (prev.recovery && Number.isInteger(prev.rescannedFrom)) start = Math.min(start, known - 2 * (known - prev.rescannedFrom));
    capped = start <= known - RECOVERY_MAX_BLOCKS;
    from = Math.max(known - RECOVERY_MAX_BLOCKS, Math.min(from, start));
    console.log(`  RECOVERY: last run's archive did not match the burn address balance — re-reading blocks ${from}–${to}; this read replaces what is stored there`);
  }
  from = Math.max(0, from);

  if (to < from) {
    console.log(`  The node's head (${head}) is behind where the archive already is (${known}) — nothing to scan this run`);
    const knownTs = (await blockTimes([known])).get(known);   // the windows end where the archive does
    return { burns: existing, meta: { scannedTo: known, scannedToTs: knownTs, rescannedFrom: null, recovery, newBurns: 0, head } };
  }

  const fresh = await scanBurns(address, decimals, from, to, { label: token });
  /* Merge. Rows before `from` cannot meet a fresh row (every fresh row has b ≥ from), so only the re-read range is keyed. */
  const kept = [];
  const overlap = new Map();
  for (const r of existing) {
    if (!Number.isInteger(r.b) || r.b < from) kept.push(r);
    else overlap.set(burnKey(r), r);
  }
  const freshKeys = new Set(fresh.map(burnKey));
  let notReseen = 0;
  for (const [k, r] of overlap) {
    if (r.b > to || freshKeys.has(k)) continue;
    notReseen++;
    if (recovery) overlap.delete(k);   // recovery: the fresh read is the truth for this range — a stored row it does not have goes
  }
  let newBurns = 0;
  for (const r of fresh) { if (!overlap.has(burnKey(r))) newBurns++; overlap.set(burnKey(r), r); }   // same (b, i) = the same burn: the fresh read replaces it
  if (notReseen && recovery) console.log(`  RECOVERY: ${notReseen} stored row(s) in blocks ${from}–${to} are not on chain — removed`);
  else if (notReseen) console.log(`::warning::${token}: ${notReseen} stored burn(s) in blocks ${from}–${to} were not in this run's re-read (kept — a lagging RPC node answers short; the balance check below decides)`);
  if (capped) console.log(`  RECOVERY reached its ~7-day limit — if the balance check still fails, rebuild with tools/rebuild-burn-archive.js`);

  const burns = kept.concat([...overlap.values()]);
  burns.sort((x, y) => (y.t - x.t) || ((y.b || 0) - (x.b || 0)) || ((y.i || 0) - (x.i || 0)));
  const toTs = (await blockTimes([to])).get(to);
  console.log(`  ${token}: ${fresh.length} burns in the re-read, ${newBurns} new; archive now ${burns.length} burns up to block ${to} (${new Date(toTs).toISOString()})`);
  return { burns, meta: { scannedTo: to, scannedToTs: toTs, rescannedFrom: from, recovery, newBurns, head } };
}

/* Archive sum vs balanceOf(0x…369) at the archive's last block. */
async function reconcileArchive(token, address, decimals, burns, meta, prev) {
  const balance = await burnAddressBalance(address, decimals, meta.scannedTo);
  let sum = 0;
  for (const r of burns) if (!Number.isInteger(r.b) || r.b <= meta.scannedTo) sum += r.a;
  const prevGood = prev && Number.isInteger(prev.lastReconciledBlock) ? prev.lastReconciledBlock : null;
  if (balance == null) {
    console.log(`  ${token}: the burn address balance at block ${meta.scannedTo} could not be read — not checked this run`);
    return { reconcile: { atBlock: meta.scannedTo, archive: sum, balance: null, diff: null, ok: null }, lastReconciledBlock: prevGood };
  }
  const diff = sum - balance;
  const ok = Math.abs(diff) <= RECONCILE_TOLERANCE;
  if (ok) console.log(`  ${token}: archive ${sum.toLocaleString()} = burn address balance ${balance.toLocaleString()} at block ${meta.scannedTo} (diff ${diff.toFixed(4)}) ✓`);
  else console.log(`::warning::${token} burn archive is ${diff.toLocaleString()} tokens off the burn address balance at block ${meta.scannedTo} (archive ${sum.toLocaleString()}, balance ${balance.toLocaleString()}) — the next run re-reads from the last matching block`);
  return { reconcile: { atBlock: meta.scannedTo, archive: sum, balance, diff, ok }, lastReconciledBlock: ok ? meta.scannedTo : prevGood };
}

/* a30 (2026-09-17): the PTGC burn archive is split by HALF-YEAR, derived from the date — no
   hard-coded list to extend. The old map ended in '2026' = 2026-01-01 → 2030-01-01, which at
   ~5 MB/month would have crossed GitHub's 100 MB file limit around mid-2027 and turned every
   hourly push red (and burn-summary stale) with no warning. Everything before 2024 stays in
   '2023-h2' so the existing file keeps its name. The first run after this change reads the
   legacy ptgc-burns-2026.json, rewrites it as 2026-h1 + 2026-h2 and deletes it. */
const LEGACY_PERIOD_FILES = ['ptgc-burns-2026.json'];   // removed once their burns are re-split
function getPeriodKey(timestamp) {
  const d = new Date(timestamp);
  const y = d.getUTCFullYear();
  if (y < 2024) return '2023-h2';
  return `${y}-${d.getUTCMonth() < 6 ? 'h1' : 'h2'}`;
}
/* Every period file present in data/ (any key, legacy included), for loading and listing. */
function listPeriodFiles(dataDir) {
  return fs.readdirSync(dataDir)
    .filter(f => /^ptgc-burns-.+\.json$/.test(f) && !f.startsWith(REBUILD_PREFIX))   // v2: rebuild inputs are not period files
    .sort();
}
/* {burnCount,totalBurned} per period file as written last time — a period whose burns did not
   change is not rewritten (six files, ~200 MB, used to be rewritten every hour for a diff in one). */
const _periodFileStats = {};

/**
 * Fetch + aggregate a token's market data from DexScreener, memoized per run.
 * Replaces the old Moralis price / analytics / pairs calls with the same
 * aggregation the dashboard's fetch-metrics.js and index.html already use, so
 * the numbers stay consistent. One HTTP call per token address — the price,
 * volume and pairs functions below all read from this single result.
 */
const _dexCache = {};
function fetchDexAggregated(tokenAddress) {
  const key = tokenAddress.toLowerCase();
  if (_dexCache[key]) return _dexCache[key];

  _dexCache[key] = (async () => {
    const empty = { price: 0, priceChange24h: 0, volume24h: 0, totalLiquidity: 0, totalTokensInLP: 0, pairs: [], pairCount: 0 };
    try {
      const res = await fetch(`${DEXSCREENER_BASE}/tokens/${tokenAddress}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();

      const pairs = (json.pairs || []).filter(p => !p.chainId || p.chainId === 'pulsechain');
      if (!pairs.length) return empty;

      // The pair that drives price + price change (2026-09-29, same rule as index.html's dsPricePair): only pairs
      // where this token is the BASE (UFO also sits as the QUOTE in INC/UFO and pTGC/UFO — their priceUsd is the
      // other token's), only pairs that trade (fake pools claim big "liquidity" with no volume), deepest of those;
      // the dashboard main pair first when present. Totals below still sum every pair.
      const vol = p => parseFloat(p.volume?.h24) || 0, liq = p => parseFloat(p.liquidity?.usd) || 0;
      const based = pairs.filter(p => parseFloat(p.priceUsd) > 0 && (p.baseToken?.address || '').toLowerCase() === key);
      const floor = Math.max(100, 0.02 * Math.max(0, ...based.map(vol)));
      const live = based.filter(p => vol(p) >= floor);
      const main = based.find(p => PRICE_MAIN_PAIRS.has((p.pairAddress || '').toLowerCase()))
        || (live.length ? [...live].sort((a, b) => liq(b) - liq(a))[0] : [...based].sort((a, b) => vol(b) - vol(a))[0]);
      if (!main) return empty;

      let totalLiquidity = 0, totalVolume = 0, totalTokensInLP = 0;
      for (const p of pairs) {
        totalLiquidity += p.liquidity?.usd || 0;
        totalVolume += p.volume?.h24 || 0;
        const isBase = p.baseToken?.address?.toLowerCase() === key;
        if (isBase && p.liquidity?.base) totalTokensInLP += p.liquidity.base;
        else if (!isBase && p.liquidity?.quote) totalTokensInLP += p.liquidity.quote;
      }

      return {
        price: parseFloat(main.priceUsd) || 0,
        priceChange24h: main.priceChange?.h24 || 0,
        volume24h: totalVolume,
        totalLiquidity,
        totalTokensInLP,
        pairs,
        pairCount: pairs.length
      };
    } catch (error) {
      console.log(`  DexScreener error for ${tokenAddress}: ${error.message}`);
      return empty;
    }
  })();

  return _dexCache[key];
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
function loadExistingBurns(dataDir, token, rebuild = null) {
  let allBurns = [];
  console.log(`\nLoading existing ${token} burns...`);
  console.log(`  Data directory: ${dataDir}`);
  
  if (token === 'PTGC') {
    // Load all PTGC period files (a30: whatever is on disk, legacy '2026' included)
    for (const file of listPeriodFiles(dataDir)) {
      const period = file.slice('ptgc-burns-'.length, -'.json'.length);
      const filePath = path.join(dataDir, file);
      console.log(`  Checking: ${filePath}`);
      try {
        if (fs.existsSync(filePath)) {
          const stats = fs.statSync(filePath);
          console.log(`    File exists, size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`);
          const fileContent = fs.readFileSync(filePath, 'utf8');
          console.log(`    Read ${fileContent.length} characters`);
          const data = JSON.parse(fileContent);
          console.log(`    Parsed JSON, burns array length: ${data.burns?.length || 0}`);
          _periodFileStats[period] = { burnCount: data.burnCount, totalBurned: data.totalBurned };
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
        throw new Error(`cannot read ${filePath} — refusing to build totals from a partial burn archive`);   // Audit IV e23 (it was skipped silently)
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
      throw new Error(`cannot read ${filePath} — refusing to rebuild the UFO archive from a few hours of re-read (v2; it was skipped silently)`);
    }
  }
  
  console.log(`  Total ${token} burns loaded from files: ${allBurns.length}`);
  if (rebuild) {   // v2: every stored row from the rebuild's start is dropped; the rebuild's rows take their place
    const before = allBurns.length;
    allBurns = allBurns.filter(b => b.t < rebuild.replaceFromTs).concat(rebuild.burns);
    console.log(`  Rebuild applied: ${before - (allBurns.length - rebuild.burns.length)} stored rows from ${new Date(rebuild.replaceFromTs).toISOString()} on dropped, ${rebuild.burns.length} rebuilt rows in`);
  }
  
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
 * Split burns into period files
 */
function splitBurnsByPeriod(burns) {
  const byPeriod = {};
  for (const burn of burns) {
    const period = getPeriodKey(burn.t);
    (byPeriod[period] = byPeriod[period] || []).push(burn);
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
function calculatePeriods(burns, asOf) {
  // v2: the windows end at the archive's last block (its real time) — the moment the rows are complete to —
  // so a window never counts a stretch the scan has not reached. (Date.now() before.)
  const now = Number.isFinite(asOf) ? asOf : Date.now();
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
    if (age < 0) continue;
    if (age <= h12) { result.h12.count++; result.h12.amount += burn.a; }
    if (age <= h24) { result.h24.count++; result.h24.amount += burn.a; }
    if (age <= d7) { result.d7.count++; result.d7.amount += burn.a; }
    if (age <= d30) { result.d30.count++; result.d30.amount += burn.a; }
    if (age <= d90) { result.d90.count++; result.d90.amount += burn.a; }
  }
  
  return result;
}

/**
 * Fetch token price (from DexScreener)
 */
async function fetchTokenPrice(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} price...`);
  const agg = await fetchDexAggregated(tokenAddress);
  console.log(`  ${tokenSymbol} price: $${agg.price}`);
  return {
    usd: agg.price,
    change24h: agg.priceChange24h
  };
}

/**
 * Fetch 24h volume (from DexScreener)
 */
async function fetchVolumeStats(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} volume...`);
  const agg = await fetchDexAggregated(tokenAddress);
  console.log(`  ${tokenSymbol} 24h volume: $${agg.volume24h}`);
  // DexScreener doesn't expose a 24h volume-change %, so change24h is left at 0.
  return {
    volume24h: agg.volume24h,
    change24h: 0
  };
}

/**
 * Fetch token pairs and liquidity (from DexScreener)
 */
async function fetchTokenPairs(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} LP pairs...`);
  const agg = await fetchDexAggregated(tokenAddress);
  console.log(`  Found ${agg.pairCount} pairs`);
  console.log(`  Total liquidity: $${agg.totalLiquidity.toLocaleString()}`);
  return {
    pairs: agg.pairs,
    totalLiquidity: agg.totalLiquidity,
    totalTokensInLP: agg.totalTokensInLP
  };
}

/**
 * Fetch holder count from PulseScan (NOT Moralis - for consistency with dashboard)
 */
async function fetchHolderCount(tokenAddress, tokenSymbol) {
  console.log(`\nFetching ${tokenSymbol} holder count from PulseScan...`);

  // PulseScan's /counters endpoint 500s intermittently. Retry a few times before giving up
  // so a transient blip doesn't cost us the real count. On total failure we return 0, but the
  // holder-history write below has a guard that NEVER records a 0 — it carries forward the last
  // good value instead. (A failed fetch and "zero holders" must never look the same.)
  for (let attempt = 1; attempt <= 4; attempt++) {
    try {
      const response = await fetch(`${PULSESCAN_BASE}/tokens/${tokenAddress}/counters`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const data = await response.json();
      const holders = parseInt(data.token_holders_count);
      if (Number.isFinite(holders) && holders > 0) {
        console.log(`  ${tokenSymbol} holders: ${holders}`);
        return holders;
      }
      throw new Error(`unexpected holder count: ${data.token_holders_count}`);
    } catch (error) {
      console.log(`  PulseScan attempt ${attempt}/4 [${tokenSymbol}]: ${error.message}`);
      if (attempt < 4) await delay(1500 * attempt);
    }
  }
  console.log(`  ${tokenSymbol} holder count unavailable after retries — returning 0 (write-guard will carry forward the last good value)`);
  return 0;
}

/**
 * Main function
 */
async function main() {
  console.log('\n' + '='.repeat(60));
  console.log('BURN HISTORY FETCHER - DEXSCREENER VERSION (SPLIT FILES)');
  console.log('Holder counts: PulseScan (for consistency with dashboard)');
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
  const ptgcRebuild = loadRebuild(dataDir, 'ptgc', PTGC_ADDRESS, existingSummary?.PTGC?.archive);
  const ufoRebuild = loadRebuild(dataDir, 'ufo', UFO_ADDRESS, existingSummary?.UFO?.archive);
  const existingPTGCBurns = loadExistingBurns(dataDir, 'PTGC', ptgcRebuild);
  const existingUFOBurns = loadExistingBurns(dataDir, 'UFO', ufoRebuild);
  
  // ============================================
  // FETCH NEW BURNS (archive v2) + CHECK AGAINST THE BURN ADDRESS BALANCE
  // ============================================
  
  const ptgcPrev = existingSummary?.PTGC?.archive || null;
  const ptgcRun = await updateArchive('PTGC', PTGC_ADDRESS, PTGC_DECIMALS, existingPTGCBurns, ptgcRebuild, ptgcPrev);
  const ptgcBurns = ptgcRun.burns;
  Object.assign(ptgcRun.meta, await reconcileArchive('PTGC', PTGC_ADDRESS, PTGC_DECIMALS, ptgcBurns, ptgcRun.meta, ptgcPrev));
  await delay(500);
  
  const ufoPrev = existingSummary?.UFO?.archive || null;
  const ufoRun = await updateArchive('UFO', UFO_ADDRESS, UFO_DECIMALS, existingUFOBurns, ufoRebuild, ufoPrev);
  const ufoBurns = ufoRun.burns;
  Object.assign(ufoRun.meta, await reconcileArchive('UFO', UFO_ADDRESS, UFO_DECIMALS, ufoBurns, ufoRun.meta, ufoPrev));
  await delay(500);
  const ptgcAsOf = ptgcRun.meta.scannedToTs ?? Date.now();
  const ufoAsOf = ufoRun.meta.scannedToTs ?? Date.now();
  
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
  
  const ptgcPeriods = calculatePeriods(ptgcBurns, ptgcAsOf);
  const ufoPeriods = calculatePeriods(ufoBurns, ufoAsOf);
  const ptgcBuybackPeriods = calculatePeriods(ptgcBuybackBurns, ptgcAsOf);
  const ufoBuybackPeriods = calculatePeriods(ufoBuybackBurns, ufoAsOf);
  
  // ============================================
  // FETCH ADDITIONAL DATA
  // ============================================
  
  const ptgcPrice = await fetchTokenPrice(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoPrice = await fetchTokenPrice(UFO_ADDRESS_NEW, 'UFO');
  await delay(300);
  
  const ptgcVolume = await fetchVolumeStats(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoVolume = await fetchVolumeStats(UFO_ADDRESS_NEW, 'UFO');
  await delay(300);
  
  const ptgcPairs = await fetchTokenPairs(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoPairs = await fetchTokenPairs(UFO_ADDRESS_NEW, 'UFO');
  await delay(300);
  
  // Fetch holder counts from PulseScan (NOT Moralis)
  const ptgcHolders = await fetchHolderCount(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoHolders = await fetchHolderCount(UFO_ADDRESS_NEW, 'UFO');
  await delay(300);
  
  // Fetch transaction counts from DexScreener
  const ptgcTxns = await fetchTransactionCount(PTGC_ADDRESS, 'PTGC');
  await delay(300);
  
  const ufoTxns = await fetchTransactionCount(UFO_ADDRESS_NEW, 'UFO');
  
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
  
  const rowOut = b => Number.isInteger(b.b) ? { b: b.b, i: b.i, t: b.t, a: b.a, f: b.f } : { t: b.t, a: b.a, f: b.f };   // v2 rows carry their chain position
  const rebuiltFromPeriod = ptgcRebuild ? getPeriodKey(ptgcRebuild.replaceFromTs) : null;
  for (const [period, burns] of Object.entries(ptgcBurnsByPeriod)) {
    if (burns.length === 0) continue;
    
    const filePath = path.join(dataDir, `ptgc-burns-${period}.json`);
    const periodTotal = burns.reduce((s, b) => s + b.a, 0);
    const prev = _periodFileStats[period];
    // v2: a rebuilt period is always rewritten (its rows gain b/i), and so is any half-year this run re-read — a keyed replace can
    // change rows without changing the count or the total, which the skip below would miss
    const forced = (rebuiltFromPeriod != null && period >= rebuiltFromPeriod) || (Number.isInteger(ptgcRun.meta.rescannedFrom) && burns.some(b => Number.isInteger(b.b) && b.b >= ptgcRun.meta.rescannedFrom));
    if (!forced && prev && prev.burnCount === burns.length && prev.totalBurned === periodTotal && fs.existsSync(filePath)) {
      console.log(`  Unchanged: ptgc-burns-${period}.json (${burns.length} burns) — not rewritten`);
      continue;
    }
    
    const fileData = {
      period,
      burnCount: burns.length,
      totalBurned: periodTotal,
      burns: burns.map(rowOut)
    };
    
    writeFileAtomic(filePath, JSON.stringify(fileData));
    const fileSizeMB = (fs.statSync(filePath).size / (1024 * 1024)).toFixed(2);
    console.log(`  Written: ${filePath} (${fileSizeMB} MB, ${burns.length} burns)`);
    if (fileSizeMB > 80) console.warn(`  WARNING: ptgc-burns-${period}.json is ${fileSizeMB} MB — GitHub rejects files over 100 MB; shorten the period in getPeriodKey before it gets there.`);
  }
  // a30: a legacy file whose burns were just re-split into half-years is retired (its burns are
  // all in the new files, so the merge above already carried them; the pipeline's `git add`
  // pathspec stages the deletion).
  // v2: a period file none of whose rows survived (the rebuild moved them) would be loaded again next run — remove it.
  for (const f of listPeriodFiles(dataDir)) {
    const period = f.slice('ptgc-burns-'.length, -'.json'.length);
    if (!LEGACY_PERIOD_FILES.includes(f) && !ptgcBurnsByPeriod[period]) { fs.unlinkSync(path.join(dataDir, f)); console.log(`  Removed ${f} — no burns belong to ${period} any more`); }
  }
  for (const legacy of LEGACY_PERIOD_FILES) {
    const legacyPath = path.join(dataDir, legacy);
    const legacyKey = legacy.slice('ptgc-burns-'.length, -'.json'.length);
    if (fs.existsSync(legacyPath) && !ptgcBurnsByPeriod[legacyKey]) {
      fs.unlinkSync(legacyPath);
      console.log(`  Removed legacy ${legacy} — its burns now live in the half-year files`);
    }
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
    burns: ufoBurns.map(rowOut)
  };
  
  writeFileAtomic(ufoFilePath, JSON.stringify(ufoFileData));
  const ufoFileSizeMB = (fs.statSync(ufoFilePath).size / (1024 * 1024)).toFixed(2);
  console.log(`  Written: ${ufoFilePath} (${ufoFileSizeMB} MB, ${ufoBurns.length} burns)`);
  
  // ============================================
  // WRITE SUMMARY FILE
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Writing summary file...');
  console.log(`${'='.repeat(50)}`);
  
  const archiveOut = (m) => ({
    schema: 2,
    rows: 'block + log index identify a burn; t = the block\'s real time (ms)',
    scannedTo: m.scannedTo,
    scannedToTime: m.scannedToTs ? new Date(m.scannedToTs).toISOString() : null,
    rescannedFrom: m.rescannedFrom,
    recovery: m.recovery,
    reconcile: m.reconcile,
    lastReconciledBlock: m.lastReconciledBlock
  });
  const summaryData = {
    lastUpdated: new Date().toISOString(),
    dataSource: 'RPC/eth_getLogs (burns), DexScreener (price/volume/liquidity), PulseScan (holders)',
    
    PTGC: {
      // a39: the contract this section was scanned from. index.html's cold-cache market cap
      // only subtracts `totalBurned` when this matches the token it is pricing — the UFO
      // section below is the RETIRED contract, and subtracting its 205 B put UFO's mcap ~12%
      // under the truth during a DexScreener outage.
      address: PTGC_ADDRESS,
      totalBurned: ptgcTotal,
      burnCount: ptgcBurns.length,
      periods: ptgcPeriods,
      periodsAsOf: new Date(ptgcAsOf).toISOString(),   // v2: the windows end here (the archive's last block)
      archive: archiveOut(ptgcRun.meta),
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
      burnFiles: listPeriodFiles(dataDir)
    },
    
    UFO: {
      address: UFO_ADDRESS,   // a39: the RETIRED UFO contract — see the note on PTGC.address
      totalBurned: ufoTotal,
      burnCount: ufoBurns.length,
      periods: ufoPeriods,
      periodsAsOf: new Date(ufoAsOf).toISOString(),
      archive: archiveOut(ufoRun.meta),
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
    // a39: this is PTGC's OWN buy-and-burn leg (burns sent from the PTGC/WPLS pair), NOT the
    // "PTGC burned by UFO" figure the dashboard shows — that one comes from ufo-ptgc-burns.json.
    // index.html now clears this field on load so the two can never be confused again.
    PTGCbyUFO: {
      source: 'PTGC burns sent from the PTGC/WPLS pair (PTGC own buy-and-burn leg)',
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
  writeFileAtomic(summaryPath, JSON.stringify(summaryData, null, 2));
  const summarySizeMB = (fs.statSync(summaryPath).size / (1024 * 1024)).toFixed(2);
  console.log(`  Written: ${summaryPath} (${summarySizeMB} MB)`);
  // v2: the rebuild is now inside the archive files — its inputs go (the pipeline's 'data/ptgc-burns-*.json' pathspec stages the deletions)
  for (const rb of [ptgcRebuild, ufoRebuild]) if (rb) for (const f of rb.files) { fs.unlinkSync(path.join(dataDir, f)); console.log(`  Removed rebuild input ${f}`); }
  
  // ============================================
  // UPDATE HOLDER HISTORY FILE
  // ============================================
  // This is the ONLY script that should write to holder-history.json
  // Stores ONE snapshot per day for historical comparisons
  // ============================================
  
  console.log(`\n${'='.repeat(50)}`);
  console.log('Updating holder history file...');
  console.log(`${'='.repeat(50)}`);
  
  const holderHistoryPath = path.join(dataDir, 'holder-history.json');
  let holderHistory = { source: 'PulseScan', lastUpdated: '', snapshots: [] };
  
  try {
    if (fs.existsSync(holderHistoryPath)) {
      holderHistory = JSON.parse(fs.readFileSync(holderHistoryPath, 'utf8'));
      console.log(`  Loaded existing history with ${holderHistory.snapshots?.length || 0} snapshots`);
    }
  } catch (e) {
    console.error(`holder-history.json exists but cannot be read (${e.message}) — refusing to replace the only copy`);   // Audit IV e23
    process.exit(1);
  }
  
  // Ensure snapshots array exists
  if (!holderHistory.snapshots) {
    holderHistory.snapshots = [];
  }
  
  const now = new Date();
  const todayDate = now.toISOString().split('T')[0]; // YYYY-MM-DD
  
  // Check if we already have a snapshot for today
  const existingTodayIndex = holderHistory.snapshots.findIndex(s => {
    if (!s.timestamp) return false;
    return s.timestamp.startsWith(todayDate);
  });
  
  // ── ZERO GUARD (the whole point of this change) ─────────────────────────────
  // fetchHolderCount returns 0 when PulseScan fails. A 0 here is a FAILED FETCH, not
  // "zero holders" — so never record it. Fall back to the most recent good (>0) value for
  // that token. If neither token has anything good (fresh or historical), skip the write
  // entirely so the existing file is left completely untouched. This stops the 0/0 rows.
  const lastGoodCount = (tkn) => {
    for (let i = holderHistory.snapshots.length - 1; i >= 0; i--) {
      const v = holderHistory.snapshots[i] && holderHistory.snapshots[i][tkn];
      if (typeof v === 'number' && v > 0) return v;
    }
    return null;
  };
  const ptgcCount = (ptgcHolders > 0) ? ptgcHolders : lastGoodCount('PTGC');
  const ufoCount  = (ufoHolders  > 0) ? ufoHolders  : lastGoodCount('UFO');
  if (ptgcHolders <= 0) console.log(`  ⚠ PTGC holder fetch returned ${ptgcHolders} — using last good value: ${ptgcCount ?? 'none'}`);
  if (ufoHolders  <= 0) console.log(`  ⚠ UFO holder fetch returned ${ufoHolders} — using last good value: ${ufoCount ?? 'none'}`);

  if (ptgcCount == null && ufoCount == null) {
    console.log('  Both holder counts unavailable and no prior good values — skipping holder-history write (existing file untouched).');
  } else {
    // Only include a token key when we actually have a good number for it.
    const newHolderSnapshot = { timestamp: now.toISOString() };
    if (ptgcCount != null) newHolderSnapshot.PTGC = ptgcCount;
    if (ufoCount  != null) newHolderSnapshot.UFO  = ufoCount;

    if (existingTodayIndex >= 0) {
      // Merge, so a carried-forward value never clobbers a good one already recorded today.
      holderHistory.snapshots[existingTodayIndex] = { ...holderHistory.snapshots[existingTodayIndex], ...newHolderSnapshot };
      console.log(`  Updated existing snapshot for ${todayDate}`);
    } else {
      holderHistory.snapshots.push(newHolderSnapshot);
      console.log(`  Added new snapshot for ${todayDate}`);
    }

    // Sort snapshots by timestamp (oldest first)
    holderHistory.snapshots.sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Audit IV e23 (2026-10-23): NO trim — this daily holder count is the one record the chain cannot give back (~37 KB a year).

    holderHistory.lastUpdated = now.toISOString();
    holderHistory.source = 'PulseScan';

    fs.writeFileSync(holderHistoryPath, JSON.stringify(holderHistory, null, 2));
    console.log(`  Written: ${holderHistoryPath} (${holderHistory.snapshots.length} daily snapshots)`);
  }
  
  // Log date range
  if (holderHistory.snapshots.length > 0) {
    const oldest = holderHistory.snapshots[0].timestamp.split('T')[0];
    const newest = holderHistory.snapshots[holderHistory.snapshots.length - 1].timestamp.split('T')[0];
    console.log(`  Date range: ${oldest} to ${newest}`);
  }
  
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
  
  console.log(`\nHOLDERS (from PulseScan):`);
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
  for (const f of listPeriodFiles(dataDir)) console.log(`  - ${f}`);
  console.log('  - ufo-burns.json');
  console.log('  - burn-summary.json');
  console.log('  - holder-history.json');
  console.log('Completed:', new Date().toISOString());
  console.log('='.repeat(60));
}

if (require.main === module) {
  main().catch(err => {
    console.error('FATAL ERROR:', err);
    process.exit(1);
  });
}

// For tools/rebuild-burn-archive.js — the rebuild uses exactly this code to read the chain.
module.exports = { scanBurns, blockTimes, headBlock, burnAddressBalance, rpcCall, getPeriodKey, listPeriodFiles, loadExistingBurns,
  PTGC_ADDRESS, UFO_ADDRESS, PTGC_DECIMALS, UFO_DECIMALS, CONFIRM_BLOCKS, RECONCILE_TOLERANCE, REBUILD_PREFIX };
