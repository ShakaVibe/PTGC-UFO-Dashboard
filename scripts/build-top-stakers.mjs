// build-top-stakers.mjs
// Prebuilds data/top-stakers.json for the dashboard's TOP 100 window, STAKERS view (2026-10-22, Shaka: "Top 100 STAKERS … how much
// ptgc you need to have staked to break into the top 100").
//
// Method, per run:
//   1. Every wallet that ever staked: the staking contract's Deposit(address user, uint256 amount) logs (user is NOT indexed — it
//      is the first word of `data`). The address list + the last block scanned live in data/top-stakers-cache.json, so a run only
//      reads the blocks since the previous one (the first run, from the contract's creation block 18,543,401, is ~4 min).
//   2. For every known wallet: mapUserInfo(addr) → amount (staked, locked included) and locked; balanceOf(addr) → the wallet's PTGC.
//      Staked PTGC stays in the wallet's own balance (checked on the eight biggest stakers 2026-10-21), so balance − amount = the
//      PTGC the wallet holds UNSTAKED — the window's "stake what you hold + buy the rest".
//   3. Keep amount > 0, sort high → low (ties by address so a rank is reproducible).
//
// Output (schema 1): { generatedAt, head, count, total, locked, top: [[addr, staked, locked, balance] × 110], s: [every staked
// amount, high → low] } — amounts as whole tokens from 1 up and to 6 decimals below 1 (the holder-ranks `key()` rounding), so the
// page ranks any wallet by binary search on `s` and lists the top 100 (+10 below the line) from `top`.
//
// Honest-failure rules (gotcha 20): a failed log scan or more than 1 % unread wallets → the previous file stays untouched, exit 1.
//
// Node 20+ (global fetch; locally NODE_USE_ENV_PROXY=1 behind a proxy). ESM.
import fs from 'node:fs';
import rpcPool from './rpc-pool.js';   // Audit IV e33 / D-4: the shared RPC pool with a head check (scripts/rpc-pool.js)

const OUT_PATH = process.env.OUT_PATH || 'data/top-stakers.json';
const CACHE_PATH = process.env.CACHE_PATH || 'data/top-stakers-cache.json';
const RPCS = (process.env.RPC_URLS || 'https://rpc.pulsechain.com').split(',');
const STAKING = '0xc71f597a2ac39e47f07102e849d18489c96f39ef';
const PTGC = '0x94534eeee131840b1c0f61847c572228bdfdde93';
const FROM_BLOCK = 18543401;     // the staking contract's creation block
const DEPOSIT = '0xe1fffcc4923d04b559f4d29a8bfc6cda04eb5b0d3c460751c2402c5c5cc9109c';   // keccak('Deposit(address,uint256)')
const SEL_USERINFO = '0x15612933', SEL_BALANCE = '0x70a08231';
const TOP_N = 110;
const ONE = 10n ** 18n, MICRO = 10n ** 12n;
const key = v => { const w = v / ONE; if (w >= 1n) return Number(w); const m = v / MICRO; return Math.max(1, Number(m)) / 1e6; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
const pad = a => a.toLowerCase().replace('0x', '').padStart(64, '0');

let rr = 0;
async function rpc(method, params) {
  let last;
  for (let t = 0; t < 6; t++) {
    try {   // the pool picks the endpoint (primary first; RPC_URLS still overrides the list)
      const r = await rpcPool.poolFetch({ attemptMs: 20000, method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }) });
      const j = await r.json();
      if (j.error) throw new Error(JSON.stringify(j.error).slice(0, 160));
      return j.result;
    } catch (e) { last = e; await sleep(600 * (t + 1)); }
  }
  throw new Error(`${method}: ${last && last.message}`);
}
async function logs(b, e, depth = 0) {
  try {
    return await rpc('eth_getLogs', [{ address: STAKING, topics: [DEPOSIT], fromBlock: '0x' + b.toString(16), toBlock: '0x' + e.toString(16) }]);
  } catch (err) {
    if (e - b < 1000 || depth > 8) throw err;
    const m = (b + e) >> 1;
    return [...await logs(b, m, depth + 1), ...await logs(m + 1, e, depth + 1)];
  }
}
async function pool(n, items, fn) {
  let i = 0;
  await Promise.all(Array.from({ length: n }, async () => { while (i < items.length) { const k = i++; await fn(items[k], k); } }));
}

const t0 = Date.now();
let cache = { lastBlock: FROM_BLOCK - 1, addrs: [] };
try { const c = JSON.parse(fs.readFileSync(CACHE_PATH, 'utf8')); if (c && Array.isArray(c.addrs) && c.lastBlock > 0) cache = c; } catch (e) {}
const known = new Set(cache.addrs.map(a => a.toLowerCase()));
const head = parseInt(await rpc('eth_blockNumber', []), 16);

// 1. new stakers since the last run
const STEP = 25000, chunks = [];
for (let b = cache.lastBlock + 1; b <= head; b += STEP) chunks.push([b, Math.min(head, b + STEP - 1)]);
let added = 0;
await pool(12, chunks, async ([b, e]) => {
  for (const l of await logs(b, e)) {
    const u = '0x' + String(l.data).slice(26, 66).toLowerCase();
    if (!known.has(u)) { known.add(u); added++; }
  }
});
console.log(`top-stakers: scanned ${chunks.length} chunk(s) to block ${head} — ${added} new staker address(es), ${known.size} known (${Math.round((Date.now() - t0) / 1000)} s)`);

// 2. every known wallet's stake + balance
const addrs = [...known].sort();
const rows = []; let miss = 0;
await pool(40, addrs, async a => {
  try {
    const ui = await rpc('eth_call', [{ to: STAKING, data: SEL_USERINFO + pad(a) }, 'latest']);
    if (!ui || ui.length < 2 + 64 * 7) { miss++; return; }
    const w = n => BigInt('0x' + ui.slice(2 + 64 * n, 2 + 64 * (n + 1)));
    const amt = w(0);
    if (amt <= 0n) return;
    rows.push([a, amt, w(5), null]);   // Audit IV e33: the wallet balance is read below for the published TOP_N only
  } catch (e) { miss++; }
});
if (miss > addrs.length * 0.01) { console.error(`top-stakers: ${miss} of ${addrs.length} wallets unread — previous file kept`); process.exit(1); }
rows.sort((x, y) => (y[1] > x[1] ? 1 : y[1] < x[1] ? -1 : (x[0] < y[0] ? -1 : 1)));
/* Audit IV e33 (2026-10-23): `top` is the only place a wallet balance is published — read it for those TOP_N rows (110 calls,
   not one per staker). Same rule as before: an unread balance fails the step (the previous file stays). */
let balMiss = 0;
await pool(20, rows.slice(0, TOP_N), async r => {
  try { r[3] = BigInt(await rpc('eth_call', [{ to: PTGC, data: SEL_BALANCE + pad(r[0]) }, 'latest'])); } catch (e) { balMiss++; }
});
if (balMiss) { console.error(`top-stakers: ${balMiss} of the top ${TOP_N} wallet balances unread — previous file kept`); process.exit(1); }

const total = rows.reduce((s, r) => s + r[1], 0n), locked = rows.reduce((s, r) => s + r[2], 0n);
const out = {
  schema: 1, generatedAt: new Date().toISOString(), head, source: 'PTGC staking contract — Deposit logs + mapUserInfo', contract: STAKING,
  count: rows.length, total: key(total), locked: key(locked), unread: miss,
  top: rows.slice(0, TOP_N).map(r => [r[0], key(r[1]), r[2] > 0n ? key(r[2]) : 0, r[3] > 0n ? key(r[3]) : 0]),
  s: rows.map(r => key(r[1])),
};
const body = JSON.stringify(out);
fs.writeFileSync(OUT_PATH, body);
fs.writeFileSync(CACHE_PATH, JSON.stringify({ lastBlock: head, addrs }));
console.log(`top-stakers: ${rows.length} stakers, ${out.total.toLocaleString('en-US')} PTGC staked (${out.locked.toLocaleString('en-US')} locked), #100 = ${rows[99] ? key(rows[99][1]).toLocaleString('en-US') : '—'} — wrote ${OUT_PATH} (${(body.length / 1024).toFixed(0)} KB) in ${Math.round((Date.now() - t0) / 1000)} s`);
