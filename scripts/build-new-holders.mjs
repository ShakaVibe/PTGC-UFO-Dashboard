// build-new-holders.mjs
// Prebuilds data/new-holders.json for the dashboard's "Holders Details" window (2026-10-02):
// every REAL wallet that became a PTGC or UFO holder (balance 0 → above 0) or stopped being one
// (above 0 → 0) over the last ~30 days, with the block, the time and the transaction that did
// it, plus the current balance of every wallet that arrived in that window — so the window
// opens at once from one small file and the Holders box's change line can read the same count.
//
// Method, per run (incremental — the file carries a block cursor):
//   1. eth_getLogs Transfer(address,address,uint256) for each token from cursor+1 to head−3.
//      First run (no file): the last BACKFILL_DAYS days, so the window is full from day one.
//   2. Every address a transfer touched is classified against two EXACT balances:
//      balanceOf at the block before the range (archive read — rpc.pulsechain.com serves it)
//      and balanceOf at head. 0 → >0 is an arrival, >0 → 0 a departure, anything else is a
//      wallet that was already holding (or never held) and is left alone. A wallet that arrived
//      AND left inside one range nets to nothing and is not recorded — PulseScan's holder count
//      would not show it either.
//   3. The transfers are replayed from the exact "before" balance to find WHICH transfer made
//      the crossing (the arrival's block/tx; the departure's block/tx). For a departure the
//      amount it held is read exactly: balanceOf at the block before that last transfer.
//   4. Contracts are never holders here: a known list (pairs, staking, router, burn, the DAO
//      wallets, the token contracts) plus eth_getCode on every unknown address (cached in the
//      file's `contracts` map so each address costs one call, once).
//   5. Current balances: balanceOf at head for every arrival still inside KEEP_DAYS.
//   6. Events older than KEEP_DAYS are pruned; the cursor moves to head.
//
// Honest-failure rules (gotcha 20): any RPC failure that would leave a wallet unclassified
// aborts the run with exit 1 and the previous file stays — a half-scanned range would miss
// arrivals forever (the cursor would have moved past them). Balances that fail to refresh keep
// the previous value with `balAt` unchanged, so the window can show their age.
//
// The RPC answers ~30 concurrent single calls quickly but serialises a JSON-RPC batch, so this
// fans out single calls with CONCURRENCY and never batches (same finding as build-dao-buys).
//
// Node 20+ (global fetch; run locally with NODE_USE_ENV_PROXY=1 behind a proxy). ESM.
import fs from 'node:fs';

const OUT_PATH = process.env.OUT_PATH || 'data/new-holders.json';
const RPC = process.env.RPC || 'https://rpc.pulsechain.com';
const BACKFILL_DAYS = Number(process.env.BACKFILL_DAYS || 30);   // first run only
const KEEP_DAYS = 31;                                             // events kept (the window's 30D + a day)
const BLOCKS_PER_DAY = 8640;                                      // ~10 s blocks
const HEAD_LAG = 3;                                               // blocks behind the tip (reorg margin)
const LOG_CHUNK = Number(process.env.LOG_CHUNK || 20000);         // blocks per eth_getLogs (halved on refusal)
const CONCURRENCY = Number(process.env.CONCURRENCY || 24);
const SCHEMA = 1;

// Same addresses as ADDR / TOKENS in index.html — keep in sync (gotcha 00).
const TOKENS = {
  PTGC: { address: '0x94534eeee131840b1c0f61847c572228bdfdde93', decimals: 18 },
  UFO:  { address: '0x49ed499433bee42dd34c169470fef2c8f9fae6e6', decimals: 18 },
};
// Never holders in this list: contracts the site already knows, the burn address and the two
// DAO treasury wallets (Shaka, 2026-10-02 — "only real wallets"). Everything else unknown is
// tested with eth_getCode.
const EXCLUDE = new Set([
  '0x0000000000000000000000000000000000000369',   // burn
  '0x0000000000000000000000000000000000000000',
  '0x000000000000000000000000000000000000dead',
  '0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1',   // DAO treasury
  '0x440773b5104a102c00ef26979a5c897155336a34',   // DAO wallet 2
  '0x305acfab82103c2b82b19543919d1c93b44e55db',   // PTGC DAO contract
  '0xc71f597a2ac39e47f07102e849d18489c96f39ef',   // PTGC staking
  '0x165c3410fc91ef562c50559f7d2289febed552d9',   // PulseX router
  '0x94534eeee131840b1c0f61847c572228bdfdde93',   // PTGC
  '0x49ed499433bee42dd34c169470fef2c8f9fae6e6',   // UFO
  '0x456548a9b56efbbd89ca0309edd17a9e20b04018',   // UFO v1 (retired)
  '0xf5a89a6487d62df5308cdda89c566c5b5ef94c11',   // PTGC/WPLS
  '0x975c7ab1dae5c97327ef7019587dffc66096f5d8',   // PTGC/PRVX
  '0xe221e6fc30e5787f0d551f980b4da1055d832a03',   // UFO/WPLS
  '0x145bc3a8a5ec0c84061511a5db6023360cadf654',   // UFO/PLSX
  '0xc4434600f1f263ee38c38dfe32c8def8c0047c0b',   // UFO/WETH
  '0xe61aa9a9b7a13ceedeaa8d26bff5222003a40634',   // UFO/eHEX
]);
const TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const BALANCE_OF = '0x70a08231';

// ---------------------------------------------------------------- RPC helpers
const sleep = ms => new Promise(r => setTimeout(r, ms));
const rpc = async (method, params, tries = 5) => {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 30000);
      const res = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }), signal: ctl.signal });
      clearTimeout(t);
      if (res.status === 429 || res.status >= 500) throw new Error('HTTP ' + res.status);
      const j = await res.json();
      if (j.error) throw new Error(j.error.message || JSON.stringify(j.error));
      return j.result;
    } catch (e) {
      lastErr = e;
      await sleep(500 * (i + 1) + Math.random() * 400);
    }
  }
  throw lastErr;
};
const hex = n => '0x' + Number(n).toString(16);
const pool = async (items, fn, n = CONCURRENCY) => {   // run fn over items with n in flight; results in order
  const out = new Array(items.length); let i = 0;
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => {
    while (i < items.length) { const k = i++; out[k] = await fn(items[k], k); }
  }));
  return out;
};
const balanceAt = async (token, addr, block) => {
  const r = await rpc('eth_call', [{ to: token, data: BALANCE_OF + addr.slice(2).padStart(64, '0') }, hex(block)]);
  return BigInt(r && r !== '0x' ? r : '0x0');
};
const isContract = async addr => { const c = await rpc('eth_getCode', [addr, 'latest']); return !!(c && c !== '0x'); };
const blockTs = async b => { const blk = await rpc('eth_getBlockByNumber', [hex(b), false]); return parseInt(blk.timestamp, 16); };

// Transfer logs for one token over [from, to], chunked; a refused chunk is split in two.
const getTransfers = async (token, from, to) => {
  const ranges = []; for (let s = from; s <= to; s += LOG_CHUNK) ranges.push([s, Math.min(s + LOG_CHUNK - 1, to)]);
  const fetchRange = async ([a, b]) => {
    try {
      return await rpc('eth_getLogs', [{ address: token, topics: [TRANSFER_TOPIC], fromBlock: hex(a), toBlock: hex(b) }], 3);
    } catch (e) {
      if (b - a < 200) throw e;
      const m = Math.floor((a + b) / 2);
      console.log(`    getLogs ${a}-${b} refused (${e.message.slice(0, 60)}) — splitting`);
      return [...await fetchRange([a, m]), ...await fetchRange([m + 1, b])];
    }
  };
  const parts = await pool(ranges, fetchRange, 4);
  const logs = parts.flat();
  logs.sort((x, y) => (parseInt(x.blockNumber, 16) - parseInt(y.blockNumber, 16)) || (parseInt(x.logIndex, 16) - parseInt(y.logIndex, 16)));
  return logs.map(l => ({
    b: parseInt(l.blockNumber, 16), i: parseInt(l.logIndex, 16), tx: l.transactionHash,
    from: '0x' + l.topics[1].slice(26), to: '0x' + l.topics[2].slice(26), v: BigInt(l.data === '0x' ? '0x0' : l.data),
  }));
};

// ---------------------------------------------------------------- main
const main = async () => {
  const t0 = Date.now();
  let prev = null;
  try { prev = JSON.parse(fs.readFileSync(OUT_PATH, 'utf8')); if (prev.schema !== SCHEMA) { console.log(`previous file schema ${prev.schema} ≠ ${SCHEMA} — rebuilding`); prev = null; } }
  catch (e) { console.log(`no previous ${OUT_PATH} (${e.code || e.message}) — first run, backfilling ${BACKFILL_DAYS} days`); }

  const tip = parseInt(await rpc('eth_blockNumber', []), 16);
  const head = tip - HEAD_LAG;
  const from = prev ? prev.cursor.block + 1 : head - BACKFILL_DAYS * BLOCKS_PER_DAY;
  if (from > head) { console.log(`cursor ${prev.cursor.block} is at the head (${head}) — nothing to scan`); return; }
  const headTs = await blockTs(head);
  console.log(`head ${head} (${new Date(headTs * 1000).toISOString()}), scanning ${from}…${head} (${head - from + 1} blocks)`);

  const contracts = Object.assign({}, prev?.contracts || {});   // addr → true (only contracts are cached; EOAs are cheap to re-ask)
  const out = { schema: SCHEMA, generatedAt: null, head: { block: head, ts: headTs }, coveredFrom: prev?.coveredFrom || null, cursor: { block: head }, tokens: {}, contracts, stats: {} };
  if (!out.coveredFrom) out.coveredFrom = { block: from, ts: await blockTs(from) };
  const keepFrom = headTs - KEEP_DAYS * 86400;

  for (const [sym, cfg] of Object.entries(TOKENS)) {
    const token = cfg.address;
    const prevTok = prev?.tokens?.[sym] || { events: [], balances: {} };
    const events = prevTok.events.filter(e => e.t >= keepFrom);
    const balances = {};
    console.log(`\n${sym}: transfers ${from}…${head}`);
    const xfers = await getTransfers(token, from, head);
    const byAddr = new Map();
    for (const x of xfers) {
      for (const [a, dir] of [[x.from, 'out'], [x.to, 'in']]) {
        if (EXCLUDE.has(a) || contracts[a]) continue;
        if (!byAddr.has(a)) byAddr.set(a, []);
        byAddr.get(a).push({ ...x, dir });
      }
    }
    console.log(`  ${xfers.length} transfers, ${byAddr.size} candidate addresses`);

    // Contracts out (one eth_getCode per unknown address, cached when true).
    const addrs = [...byAddr.keys()];
    const codeFlags = await pool(addrs, a => isContract(a));
    let nContracts = 0;
    addrs.forEach((a, k) => { if (codeFlags[k]) { contracts[a] = true; byAddr.delete(a); nContracts++; } });
    console.log(`  ${nContracts} contracts skipped, ${byAddr.size} wallets to classify`);

    // Exact balances at both ends of the range.
    const wallets = [...byAddr.keys()];
    const before = await pool(wallets, a => balanceAt(token, a, from - 1));
    const now = await pool(wallets, a => balanceAt(token, a, head));
    const known = new Map(events.map(e => [e.a + ':' + e.k, e]));   // dedupe guard — an event is one (wallet, kind) per crossing
    const lastKindOf = a => { const es = events.filter(e => e.a === a); return es.length ? es[es.length - 1].k : null; };
    let nIn = 0, nOut = 0, nSkipped = 0;
    const newEvents = [];
    for (let k = 0; k < wallets.length; k++) {
      const a = wallets[k], b0 = before[k], b1 = now[k];
      const arrived = b0 === 0n && b1 > 0n, left = b0 > 0n && b1 === 0n;
      if (!arrived && !left) { nSkipped++; continue; }
      // Replay the wallet's transfers from the exact starting balance to find the crossing.
      let run = b0, crossing = null;
      const list = byAddr.get(a);
      for (const x of list) {
        const wasZero = run <= 0n;
        run += x.dir === 'in' ? x.v : -x.v;
        if (arrived && wasZero && run > 0n) crossing = x;            // the LAST 0→>0 wins (a wallet that bounced ends on its final arrival)
        if (left && !wasZero && run <= 0n) crossing = x;              // the LAST >0→0 wins
      }
      if (!crossing) crossing = arrived ? list.find(x => x.dir === 'in') || list[0] : [...list].reverse().find(x => x.dir === 'out') || list[list.length - 1];   // reflection drift — fall back to the first in / last out
      const ev = { a, k: arrived ? 'in' : 'out', b: crossing.b, tx: crossing.tx, t: 0 };
      if (arrived) {
        if (lastKindOf(a) === 'out') ev.r = 1;                        // returning: left inside the window, back again
        nIn++;
      } else {
        try { ev.had = Number(await balanceAt(token, a, crossing.b - 1)) / 10 ** cfg.decimals; } catch (e) { ev.had = null; }
        nOut++;
      }
      newEvents.push(ev);
    }
    // Timestamps for the new events' blocks (one read per distinct block).
    const blocks = [...new Set(newEvents.map(e => e.b))];
    const tsList = await pool(blocks, b => blockTs(b));
    const tsOf = new Map(blocks.map((b, i) => [b, tsList[i]]));
    for (const ev of newEvents) {
      ev.t = tsOf.get(ev.b);
      if (ev.t < keepFrom) continue;                                 // a long-stalled cursor: older than the window, not worth keeping
      const key = ev.a + ':' + ev.k;
      if (known.has(key) && known.get(key).b === ev.b) continue;   // already recorded (overlapping re-run)
      events.push(ev);
    }
    events.sort((x, y) => x.t - y.t || x.b - y.b);
    console.log(`  +${nIn} arrivals, +${nOut} departures, ${nSkipped} already-holding / never-held; ${events.length} events kept (${KEEP_DAYS} d)`);

    // Current balance of every wallet that arrived inside the kept window (and is not known to have left since).
    const holdersNow = [...new Set(events.filter(e => e.k === 'in').map(e => e.a))];
    const bals = await pool(holdersNow, async a => { try { return Number(await balanceAt(token, a, head)) / 10 ** cfg.decimals; } catch (e) { return null; } });
    let nBalFail = 0;
    holdersNow.forEach((a, k) => {
      if (bals[k] == null) { nBalFail++; if (prevTok.balances[a] !== undefined) balances[a] = prevTok.balances[a]; }
      else balances[a] = bals[k];
    });
    if (nBalFail) console.log(`  ${nBalFail} balance reads failed — previous values kept where there were any`);
    out.tokens[sym] = { address: token, events, balances, balAt: nBalFail ? (prevTok.balAt || headTs) : headTs };
    out.stats[sym] = { transfers: xfers.length, candidates: addrs.length, contracts: nContracts, arrivals: nIn, departures: nOut, kept: events.length };
  }

  out.generatedAt = new Date().toISOString();
  fs.mkdirSync(OUT_PATH.replace(/\/[^/]+$/, ''), { recursive: true });
  // One event per line: the hourly data commit's diff then shows exactly who arrived or left.
  const body = JSON.stringify(out).replace(/\{"a":"0x/g, '\n{"a":"0x');
  fs.writeFileSync(OUT_PATH, body);
  const size = fs.statSync(OUT_PATH).size;
  console.log(`\nwrote ${OUT_PATH} (${(size / 1024).toFixed(1)} KB) in ${((Date.now() - t0) / 1000).toFixed(0)} s — cursor ${head}`);
};

main().catch(e => { console.error('build-new-holders FAILED:', e && e.stack || e); process.exit(1); });
