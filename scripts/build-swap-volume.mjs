// build-swap-volume.mjs — data/swap-volume.json: PTGC and UFO trading volume split into HUMAN and ARB-BOT
// trades, from the pools' own Swap events (2026-10-06, Shaka: "both ptgc and ufo heavily rely on the volume that
// it gets from the arb bots… have it broken down between Human Volume and ARB Bot volume").
//
// How a trade is classed — by the Swap event's `sender`, the contract that called the pool:
//   • a known router / aggregator (PulseX v1, v2, the current PulseXSwapRouter, Piteas, …) = HUMAN — that is
//     the only way a person's wallet reaches a pool; a router multi-hop (PTGC→WPLS→UFO) is still one human;
//   • any other contract = BOT — arbitrage bots call the pools from their own contracts (a day of real trades,
//     2026-10-06: 160 of 172 swaps on the main pools came from six unverified contracts, ~28 each, 13 txs hitting
//     two pools in one breath). A sender PulseScan names as a verified Router / Aggregator / Swap contract is
//     promoted to HUMAN automatically (looked up once, cached), so a new aggregator does not read as a bot for
//     long; the top bot senders are listed in the file so Shaka can spot one that slipped through.
// USD per trade = the token-side amount × the token's hourly close from data/charts-intraday.json (daily close
// from charts-data.json beyond 14 d). A trade with no price is counted but not valued (`unpriced`).
//
// Incremental: data/swap-volume-cache.json keeps every trade of the last 91 days (compact rows: [ts, block, tx
// prefix, pool#, sender#, kind, PTGC amount, PTGC usd, UFO amount, UFO usd, PTGC dir, UFO dir, wallet#, to#] over index tables —
// dir = +1 a buy of the token, −1 a sell; wallet# = tx.from of a HUMAN trade, looked up FROM_CAP per run; to# = the Swap's `to`,
// who received the output) + a block cursor; each run
//
// THE ARBITRAGE PATTERN ITSELF (Shaka, round 7: "don't arb bots usually buy it from one pool and sell into another?"): a
// transaction that BUYS the token in one pool and SELLS it in another is a round trip — only a bot does that. Such a trade is a
// bot's whatever its sender; a sender whose trades are mostly round trips is a bot even if it pays out to many wallets, and the
// aggregator rule below only promotes a sender whose round-trip share is small. The file carries per-side `arb` totals and each
// sender's round-trip share, so the window can show how sure we are.
// Aggregators we have not listed (switch.win, a new router) are caught by the `to` field: a router / aggregator delivers the
// output to the trader's wallet — many different recipients — while a bot sends it to itself or on to the next pool. A sender
// with ≥ AGG_MIN_RECIPIENTS distinct recipients that are neither itself nor a pool, over ≥ AGG_MIN_SHARE of its trades, is
// classed human and labelled "aggregator (delivers to wallets)". That is in addition to the PulseScan-name promotion.
// scans only the new blocks (first run: BACKFILL_DAYS). Block times are interpolated between the chunk ends
// (PulseChain's ~10 s blocks; hourly bins do not need better). Pools = DexScreener's list for both tokens +
// the pinned RH-core pools (index.html HARDCODED_*_PAIRS — DexScreener drops a quiet pool). Honest failure:
// a refused log chunk aborts the run (exit 1) and the previous files stay — the cursor never skips a range.
//
// Node 20+ (global fetch; locally: NODE_USE_ENV_PROXY=1 node scripts/build-swap-volume.mjs). ESM.
import fs from 'node:fs';
import rpcPool from './rpc-pool.js';   // Audit IV e33 / D-4: the shared RPC pool with a head check (scripts/rpc-pool.js)

const OUT_PATH = process.env.OUT_PATH || 'data/swap-volume.json';
const CACHE_PATH = process.env.CACHE_PATH || 'data/swap-volume-cache.json';
const RPC = process.env.RPC || 'https://rpc.pulsechain.com';
const BACKFILL_DAYS = Number(process.env.BACKFILL_DAYS || 90);   // 2026-10-06 round 3: a 90D period (Shaka)
const KEEP_DAYS = 91;
const BLOCKS_PER_DAY = 8640;
const HEAD_LAG = 3;
const LOG_CHUNK = Number(process.env.LOG_CHUNK || 4000);
const HOUR = 3600000;
const SCHEMA = 3;   // 3 (2026-10-06 round 6): rows carry the Swap's `to` as well — a sender that delivers to many different wallets is an aggregator, not a bot; 2: direction + tx.from; an older cache is rebuilt
const FROM_CAP = Number(process.env.FROM_CAP || 1500);
const AGG_MIN_RECIPIENTS = 5, AGG_MIN_SHARE = 0.6;
const ARB_BOT_SHARE = 0.5, ARB_AGG_MAX = 0.2;   // a sender ≥ 50 % round trips is a bot; the aggregator rule needs < 20 %
const ARB_MIN_BALANCE = 0.5;                    // 2026-10-06 audit: a router-sent round trip counts only if the buy and sell legs are within 2× of each other (arbitrage is balanced; a split sell with a small buy leg is a person)
const WALLET_BOT_PER_DAY = 50;                   // a wallet trading through a router ≥ 50 times in one UTC day is a bot on the router (round 9 self-check: one did 144 in a day)   // eth_getTransactionByHash lookups per run (the human trades' wallets; the backlog drains over a few runs)

const SWAP_TOPIC = '0xd78ad95fa46c994b6551d0da85fc275fe613ce37657fb8d5e3d130840159d822';
/* Audit V v12 / v13 / v14 (2026-10-25) — the per-transfer fee model. PTGC (5 %) and UFO (~6 %) charge their fee on every TRANSFER;
   an arb bot's loop moves the token pool → pool once (1 transfer, 1 fee) but shows as 2 Swap events, and a router-split buy pays the
   fee twice (pools → router → buyer). So this builder now ALSO writes, per period, a `measured` block next to the old figures
   (which stay exactly as they were until the page is switched over):
     measured.human / .bot   — volume with each transaction counted ONCE per token (max of its buy legs and its sell legs), and
                               the number of transactions (not swap legs)
     measured.protocol       — UFO's own swapback swaps (the contract selling its fee UFO, buying + burning UFO and PTGC through
                               the PulseX v2 router); counted inside `human` in the old figures
     measured.fees           — the fee actually paid, read from the fee legs on chain, split by who paid it:
                               PTGC: each taxed transfer sends 0.5 % to 0x…0369 AND 1 % to the staking contract, from the same sender
                               in the same tx (exactly 2×) → taxed gross = burn leg ÷ 0.005; UFO: the 5 % leg into the UFO contract →
                               gross = leg ÷ 0.05. Fee = gross × FEE_TOTAL. Class: a tx with a bot swap → bot; else with a person's
                               swap → human; else with only the contract's swapback → protocol; no tracked swap → transfer (sends
                               between wallets, staking moves, untracked pools).
   Fee legs are cached (cache.fees) and backfilled FEE_BACKFILL_DAYS a run, newest first, until the 90 days are covered; until then
   `measured.fees.since` says how far back they reach. Reference + truth table: tools/audit5-measure-fees.py,
   handover/sessions/2026-10-25-audit5.md. */
const TRANSFER_TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const BURN_ADDR = '0x0000000000000000000000000000000000000369';
const PTGC_STAKING = '0xc71f597a2ac39e47f07102e849d18489c96f39ef';
const PULSEX_V2_ROUTER = '0x165c3410fc91ef562c50559f7d2289febed552d9';   // UFO's swapback swaps through it
const FEE_TOTAL = { PTGC: 0.05, UFO: 0.06 };   // PTGC renounced; UFO = its 5 % contract leg + ~1 % reflections at today's rates (the owner can change them)
const FEE_LEG_SHARE = { PTGC: 0.005, UFO: 0.05 };   // the leg we read, as a share of the taxed gross
const FEE_BACKFILL_DAYS = Number(process.env.FEE_BACKFILL_DAYS || 30);
const topicAddr = a => '0x' + '0'.repeat(24) + a.slice(2).toLowerCase();   // Swap(address,uint,uint,uint,uint,address)
const TOKENS = {   // same as index.html TOKENS / ADDR (gotcha 00)
  PTGC: { address: '0x94534eeee131840b1c0f61847c572228bdfdde93', decimals: 18 },
  UFO:  { address: '0x49ed499433bee42dd34c169470fef2c8f9fae6e6', decimals: 18 },
};
// index.html HARDCODED_*_PAIRS (2026-10-06): a pool DexScreener drops still counts here.
const PINNED = {
  PTGC: ['0xf5a89a6487d62df5308cdda89c566c5b5ef94c11', '0xdb08cc9f70725b30204355a39a92ace9266c3819', '0x0d68d64c70e204c1cff6180b5ec656a7840d8131',
         '0xdc995338cf3f84b92ec6015bbb19c036f16bf9d5', '0x0057604c09007b8d020931ba507f8591bc4e8658', '0x975c7ab1dae5c97327ef7019587dffc66096f5d8'],
  UFO:  ['0xe221e6fc30e5787f0d551f980b4da1055d832a03', '0x145bc3a8a5ec0c84061511a5db6023360cadf654', '0xc4434600f1f263ee38c38dfe32c8def8c0047c0b',
         '0xe61aa9a9b7a13ceedeaa8d26bff5222003a40634', '0xf7d75a0bbe1ef90cda220dea7450105a956abf19', '0x9abd84eae174c6cf7fbf67cbb550930845866e05',
         '0x1693b411ca2df63c15292ad1fccf8ff06a643b25'],
};
const SYMBOLS = {   // for a pool's name when DexScreener has not named it (lower-case addresses)
  [TOKENS.PTGC.address]: 'PTGC', [TOKENS.UFO.address]: 'UFO',
  '0xa1077a294dde1b09bb078844df40758a5d0f9a27': 'WPLS', '0x95b303987a60c71504d99aa1b13b4da07b0790ab': 'PLSX', '0x2fa878ab3f87cc1c9737fc071108f904c0b0c95d': 'INC',
  '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39': 'HEX', '0x57fde0a71132198bbec939b98976993d8d89d225': 'eHEX', '0xf6f8db0aba00007681f8faf16a0fda1c9b030b11': 'PRVX',
  '0x02dcdd04e3f455d838cd1249292c58f3b79e3c3c': 'WETH', '0xefd766ccb38eaf1dfd701853bfce31359239f305': 'DAI',
};
// Known human paths. Lower-case. Extend when the file's top "bot" list shows a named aggregator.
const ROUTERS = {
  '0x98bf93ebf5c380c0e6ae8e192a7e2ae08edacc02': 'PulseX v1 router',
  '0x165c3410fc91ef562c50559f7d2289febed552d9': 'PulseX v2 router',
  '0xda9aba4eacf54e0273f56dffee6b8f1e20b23bba': 'PulseXSwapRouter',       // the PulseX app's current router (verified on PulseScan)
  '0x6bf228eb7f8ad948d37ded07e595efddfaaf88a6': 'Piteas router',
  // switch.win (the dashboard's own Buy / Sell): SwitchRouter → UniswapV2DirectPairAdapter → pool. Shaka's tx 0x6393f6c8… (2026-09-23,
  // a DAO buy, split over the v1 + v2 PTGC/WPLS pools) shows the adapters as the Swap senders — PulseScan names them, so they were
  // already human by name; labelled here so the Human-routes list says what they are (round 9).
  '0x2dfc8b6e13ff7f04e37ef97006084805d65a6f19': 'switch.win (SwitchRouter)',
  '0x6f5ccfca1f1d3fff70202463df05573cc1668cb6': 'switch.win adapter',
  '0x393e382520b93b8f662dc76295000930c06d689f': 'switch.win adapter',
};
const HUMAN_NAME = /router|aggregat|swap|exchange|dex/i;   // a verified, named contract matching this is a human path

const sleep = ms => new Promise(r => setTimeout(r, ms));
const lc = s => (s || '').toLowerCase();
const hex = n => '0x' + Number(n).toString(16);
const rpc = async (method, params, tries = 5) => {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 30000);
      const res = await rpcPool.poolFetch({ attemptMs: 30000, method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }), signal: ctl.signal });
      clearTimeout(t);
      if (res.status === 429 || res.status >= 500) throw new Error('HTTP ' + res.status);
      const j = await res.json();
      if (j.error) throw new Error(j.error.message || JSON.stringify(j.error));
      return j.result;
    } catch (e) { lastErr = e; await sleep(500 * (i + 1) + Math.random() * 400); }
  }
  throw lastErr;
};
const pmap = async (items, fn, n = 4) => { const out = new Array(items.length); let i = 0; await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => { while (i < items.length) { const k = i++; out[k] = await fn(items[k], k); } })); return out; };
const blockTs = async b => parseInt((await rpc('eth_getBlockByNumber', [hex(b), false])).timestamp, 16) * 1000;
const readJson = (p, fb) => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return fb; } };
const getJson = async (url, tries = 3) => {
  for (let a = 0; a < tries; a++) {
    try { const r = await fetch(url, { headers: { accept: 'application/json', 'user-agent': 'grays-dashboard-pipeline/1.0 (+https://ptgc-ufo.com)' }, signal: AbortSignal.timeout(20000) });
      if (r.status === 404) return null; if (!r.ok) throw new Error('HTTP ' + r.status); return await r.json(); }
    catch (e) { if (a === tries - 1) throw e; await sleep(2000 * (a + 1)); }
  }
};

// ---------------------------------------------------------------- pools
async function discoverPools(cache) {
  const pools = cache.pools || {};
  for (const [tk, t] of Object.entries(TOKENS)) {
    let listed = [];
    try {
      const j = await getJson(`https://api.dexscreener.com/latest/dex/tokens/${t.address}`);
      listed = ((j && j.pairs) || []).filter(p => p.chainId === 'pulsechain' && /^0x[0-9a-fA-F]{40}$/.test(p.pairAddress || ''));
    } catch (e) { console.warn(`  DexScreener pairs for ${tk}: ${e.message} — pinned pools only this run`); }
    const want = new Map();
    for (const p of listed) want.set(lc(p.pairAddress), `${p.baseToken?.symbol}/${p.quoteToken?.symbol}`);
    for (const a of PINNED[tk]) if (!want.has(a)) want.set(a, null);
    for (const [addr, name] of want) {
      const rec = pools[addr] || (pools[addr] = { tokens: [], name: null, token0: null, token1: null });
      if (!rec.tokens.includes(tk)) rec.tokens.push(tk);
      if (name) rec.name = name;
    }
  }
  // token0 / token1 once per pool (the Swap amounts are in that order)
  const need = Object.entries(pools).filter(([, r]) => !r.token0);
  await pmap(need, async ([addr, rec]) => {
    const t0 = await rpc('eth_call', [{ to: addr, data: '0x0dfe1681' }, 'latest']);   // token0()
    const t1 = await rpc('eth_call', [{ to: addr, data: '0xd21220a7' }, 'latest']);   // token1()
    rec.token0 = '0x' + t0.slice(-40); rec.token1 = '0x' + t1.slice(-40);
    if (!rec.name) { const sym = a => SYMBOLS[a] || a.slice(0, 6); rec.name = `${sym(rec.token0)}/${sym(rec.token1)}`; }
  }, 6);
  cache.pools = pools;
  return pools;
}

// ---------------------------------------------------------------- prices (hourly file, daily beyond it)
function loadPrices() {
  const intra = readJson('data/charts-intraday.json', null), daily = readJson('data/charts-data.json', null);
  const out = {};
  for (const tk of Object.keys(TOKENS)) {
    const h = new Map((intra?.tokens?.[tk]?.hourly?.series || []).map(([ts, p]) => [Math.floor(ts / HOUR), p]));
    const d = (daily?.tokens?.[tk]?.series || []).slice().sort((a, b) => a[0] - b[0]);
    out[tk] = ts => {
      const k = Math.floor(ts / HOUR);
      for (let i = 0; i < 6; i++) { const p = h.get(k - i); if (p > 0) return p; }   // this hour or up to 5 hours back
      let best = null; for (const [t, p] of d) { if (t <= ts) best = p; else break; }   // the last daily close before ts
      return best > 0 ? best : null;
    };
  }
  return out;
}

// ---------------------------------------------------------------- senders
async function classifySenders(cache, addrs) {
  const senders = cache.senders || (cache.senders = {});
  const unknown = addrs.filter(a => !ROUTERS[a] && !senders[a]);
  await pmap(unknown, async a => {
    let label = null, kind = 'bot';
    try {
      const j = await getJson(`https://api.scan.pulsechain.com/api/v2/addresses/${a}`);
      if (j && j.is_contract === false) { kind = 'human'; label = 'wallet (direct swap)'; }   // an EOA calling the pool itself — a person, oddly
      else if (j && j.name) { label = j.name; if (j.is_verified && HUMAN_NAME.test(j.name)) kind = 'human'; }
    } catch (e) { /* unknown stays a bot; retried next run (not cached) */ return; }
    senders[a] = kind === 'human' ? { label, kind, checkedAt: Date.now(), by: 'name' } : { label, kind, checkedAt: Date.now() };   // `by` = what made it human: a name never gets undone by the round-trip rule
  }, 3);
  return a => ROUTERS[a] ? { kind: 'human', label: ROUTERS[a] } : (senders[a] || { kind: 'bot', label: null });
}

// ---------------------------------------------------------------- main
async function main() {
  const t0 = Date.now();
  let cache = readJson(CACHE_PATH, { schema: SCHEMA, cursor: null, pools: {}, senders: {}, swaps: [] });
  if ((cache.schema || 1) < SCHEMA) { console.log(`cache is schema ${cache.schema || 1} — rebuilding the ${BACKFILL_DAYS}-day history with directions and wallets`); cache = { schema: SCHEMA, cursor: null, pools: cache.pools || {}, senders: cache.senders || {}, swaps: [], from: {} }; }
  cache.from = cache.from || {};
  const head = parseInt(await rpc('eth_blockNumber', []), 16) - HEAD_LAG;
  const target = head - BACKFILL_DAYS * BLOCKS_PER_DAY;
  const from = cache.cursor ? cache.cursor.block + 1 : target;
  // the oldest block the cache covers — a cache built for fewer days (the 30-day first cut) is extended BACKWARDS once
  const oldest = cache.fromBlock || (cache.swaps && cache.swaps.length ? Math.min(...cache.swaps.map(r => r[1])) : null);
  const back = cache.cursor && oldest && oldest > target + BLOCKS_PER_DAY ? [target, oldest - 1] : null;
  const pools = await discoverPools(cache);
  const addrs = Object.keys(pools);
  console.log(`${addrs.length} pools (${addrs.filter(a => pools[a].tokens.includes('PTGC')).length} PTGC, ${addrs.filter(a => pools[a].tokens.includes('UFO')).length} UFO); scanning ${from}…${head} (${head - from + 1} blocks${cache.cursor ? '' : ', first run — backfill'})${back ? ` + backfill ${back[0]}…${back[1]} (${back[1] - back[0] + 1} blocks, the cache covered ${Math.round((head - oldest) / BLOCKS_PER_DAY)} d)` : ''}`);

  // Swap logs, chunked, addresses in one filter; a refused chunk is split
  const ranges = []; for (let s = from; s <= head; s += LOG_CHUNK) ranges.push([s, Math.min(s + LOG_CHUNK - 1, head)]);
  if (back) for (let s = back[0]; s <= back[1]; s += LOG_CHUNK) ranges.push([s, Math.min(s + LOG_CHUNK - 1, back[1])]);
  const fetchRange = async ([a, b]) => {
    try { return await rpc('eth_getLogs', [{ address: addrs, topics: [SWAP_TOPIC], fromBlock: hex(a), toBlock: hex(b) }], 3); }
    catch (e) { if (b - a < 100) throw e; const m = Math.floor((a + b) / 2); console.log(`    getLogs ${a}-${b} refused (${String(e.message).slice(0, 60)}) — splitting`); return [...await fetchRange([a, m]), ...await fetchRange([m + 1, b])]; }
  };
  const parts = await pmap(ranges, fetchRange, 4);
  const logs = parts.flat();

  // Audit V v12: the fee legs. Forward from the fee cursor, and backward FEE_BACKFILL_DAYS a run until the 90 days are covered.
  cache.fees = cache.fees || [];   // [ts, block, tx10, tok (0 PTGC · 1 UFO), taxed gross tokens summed over the tx's fee legs]
  const feeFrom = cache.feeCursor ? cache.feeCursor.block + 1 : Math.max(target, head - FEE_BACKFILL_DAYS * BLOCKS_PER_DAY);
  const feeOldest = cache.feeFromBlock || feeFrom;
  const feeBack = feeOldest > target + 1 ? [Math.max(target, feeOldest - FEE_BACKFILL_DAYS * BLOCKS_PER_DAY), feeOldest - 1] : null;
  const feeRanges = []; for (let a = feeFrom; a <= head; a += LOG_CHUNK) feeRanges.push([a, Math.min(a + LOG_CHUNK - 1, head)]);
  const feeBackUsed = !!(cache.feeCursor && feeBack);
  if (feeBackUsed) for (let a = feeBack[0]; a <= feeBack[1]; a += LOG_CHUNK) feeRanges.push([a, Math.min(a + LOG_CHUNK - 1, feeBack[1])]);
  const feeFetch = (address, to) => async ([a, b]) => {
    try { return await rpc('eth_getLogs', [{ address, topics: [TRANSFER_TOPIC, null, topicAddr(to)], fromBlock: hex(a), toBlock: hex(b) }], 3); }
    catch (e) { if (b - a < 100) throw e; const m = Math.floor((a + b) / 2); return [...await feeFetch(address, to)([a, m]), ...await feeFetch(address, to)([m + 1, b])]; }
  };
  const [burnLegs, stakeLegs, ufoLegs] = await Promise.all([
    pmap(feeRanges, feeFetch(TOKENS.PTGC.address, BURN_ADDR), 3).then(x => x.flat()),
    pmap(feeRanges, feeFetch(TOKENS.PTGC.address, PTGC_STAKING), 3).then(x => x.flat()),
    pmap(feeRanges, feeFetch(TOKENS.UFO.address, TOKENS.UFO.address), 3).then(x => x.flat()),
  ]);
  const legAmt = l => Number(BigInt(l.data)) / 1e18;
  const stakeBy = new Map();
  for (const l of stakeLegs) { const k = l.transactionHash + '|' + l.topics[1]; (stakeBy.get(k) || stakeBy.set(k, []).get(k)).push(legAmt(l)); }
  const feeAgg = new Map();   // one row per (block, tx, token): the taxed gross of all its fee legs (a router split has several)
  const addFee = (l, tok, gross) => { const k = parseInt(l.blockNumber, 16) + '|' + l.transactionHash.slice(0, 10) + '|' + tok; feeAgg.set(k, (feeAgg.get(k) || 0) + gross); };
  for (const l of burnLegs) {   // a fee leg: the same sender sent exactly 2× the burn leg to the staking contract in the same tx
    const a = legAmt(l), st = stakeBy.get(l.transactionHash + '|' + l.topics[1]) || [];
    if (a > 0 && st.some(x => Math.abs(x - 2 * a) <= Math.max(1e-6, 2 * a * 1e-6))) addFee(l, 0, a / FEE_LEG_SHARE.PTGC);
  }
  for (const l of ufoLegs) {   // UFO: the 5 % leg into the UFO contract (not the contract's own moves)
    if ('0x' + l.topics[1].slice(26) === TOKENS.UFO.address) continue;
    const a = legAmt(l); if (a > 0) addFee(l, 1, a / FEE_LEG_SHARE.UFO);
  }
  const freshFees = [...feeAgg].map(([k, g]) => { const [b, tx, tok] = k.split('|'); return [+b, tx, +tok, Number(g.toPrecision(7))]; });
  console.log(`fee legs: ${freshFees.length} tx rows new (${feeRanges.length} chunk(s); PTGC burn legs ${burnLegs.length}, UFO contract legs ${ufoLegs.length})`);
  console.log(`${logs.length} swaps in ${ranges.length} chunk(s)`);

  // block → time: the chunk ends, interpolated between (PulseChain ~10 s blocks)
  const marks = [...new Set([...ranges.flat(), ...feeRanges.flat()])].sort((a, b) => a - b);
  const markTs = new Map(await pmap(marks, async b => [b, await blockTs(b)], 6).then(r => r));
  const tsOf = b => { let lo = marks[0], hi = marks[marks.length - 1]; for (const m of marks) { if (m <= b) lo = m; if (m >= b) { hi = m; break; } } if (hi === lo) return markTs.get(lo); return Math.round(markTs.get(lo) + (markTs.get(hi) - markTs.get(lo)) * (b - lo) / (hi - lo)); };

  // decode + class + price
  const prices = loadPrices();
  const classOf = await classifySenders(cache, [...new Set(logs.map(l => '0x' + l.topics[1].slice(26)))]);
  let unpriced = 0;
  const word = (d, i) => BigInt('0x' + d.slice(2 + 64 * i, 2 + 64 * (i + 1)));
  const idx = cache.index || (cache.index = { pools: [], senders: [] });
  const ix = (list, v) => { let i = list.indexOf(v); if (i < 0) { list.push(v); i = list.length - 1; } return i; };
  const fresh = [];
  for (const l of logs) {
    const addr = lc(l.address), rec = pools[addr]; if (!rec) continue;
    const sender = '0x' + l.topics[1].slice(26);
    const [a0i, a1i, a0o, a1o] = [0, 1, 2, 3].map(i => word(l.data, i));
    const ts = tsOf(parseInt(l.blockNumber, 16));
    const amounts = {}, dirs = {};
    for (const tk of rec.tokens) {
      const is0 = TOKENS[tk].address === rec.token0, is1 = TOKENS[tk].address === rec.token1;
      const tin = is0 ? a0i : is1 ? a1i : 0n, tout = is0 ? a0o : is1 ? a1o : 0n;   // the token's amount INTO the pool (a sell) / OUT of it (a buy)
      const amt = Number(tin + tout) / 10 ** TOKENS[tk].decimals;
      const p = prices[tk](ts);
      if (!(p > 0)) unpriced++;
      amounts[tk] = [Number(amt.toPrecision(7)), p > 0 ? Number((amt * p).toPrecision(6)) : null];
      dirs[tk] = tout > tin ? 1 : tin > 0n ? -1 : 0;
    }
    const P = amounts.PTGC || [null, null], U = amounts.UFO || [null, null];
    const tx10 = l.transactionHash.slice(0, 10);
    const to = '0x' + l.topics[2].slice(26);
    idx.wallets = idx.wallets || [];
    fresh.push([ts, parseInt(l.blockNumber, 16), tx10, ix(idx.pools, addr), ix(idx.senders, sender), classOf(sender).kind === 'human' ? 1 : 0, P[0], P[1], U[0], U[1], dirs.PTGC || 0, dirs.UFO || 0, -1, ix(idx.wallets, lc(to)), l.transactionHash]);
  }

  // the human trades' wallets: tx.from, FROM_CAP lookups a run, newest first; remembered in cache.from by tx prefix
  const need = []; const seenTx = new Set();
  for (const r of [...fresh].sort((a, b) => b[0] - a[0])) if (r[5] === 1 && !cache.from[r[2]] && !seenTx.has(r[2])) { seenTx.add(r[2]); need.push([r[2], r[14]]); }
  const pending = [...(cache.fromPending || [])];   // full hashes still to look up from earlier runs
  const todo = [...need, ...pending.filter(([t]) => !seenTx.has(t))].slice(0, FROM_CAP);
  if (todo.length) {
    console.log(`looking up ${todo.length} human trades' wallets (${need.length + pending.length} outstanding)`);
    await pmap(todo, async ([t, hash]) => { try { const tx = await rpc('eth_getTransactionByHash', [hash], 3); if (tx && tx.from) cache.from[t] = lc(tx.from); } catch (e) { /* next run */ } }, 12);
  }
  cache.fromPending = [...need, ...pending].filter(([t]) => !cache.from[t]).slice(0, 20000);
  idx.wallets = idx.wallets || [];
  for (const r of fresh) { if (r[5] === 1 && cache.from[r[2]]) r[12] = ix(idx.wallets, cache.from[r[2]]); r.length = 14; }   // the full hash leaves the row

  // merge with the cache (dedupe by tx+pool+logIndex-free key: tx + pool + amounts), prune to KEEP_DAYS
  const keepFrom = Date.now() - KEEP_DAYS * 86400000;
  const seen = new Set();
  const rows = [...(cache.swaps || []), ...fresh].filter(r => { if (r[0] < keepFrom) return false; const k = r[2] + '|' + r[1] + '|' + r[3] + '|' + r[6] + '|' + r[8]; if (seen.has(k)) return false; seen.add(k); return true; })
    .sort((x, y) => x[0] - y[0]);
  /* Audit IV e33 (2026-10-23): re-price the rows of the last 6 h with this run's price file — the newest hours were priced from
     the PREVIOUS run's charts-intraday.json (it is rebuilt later in the other lane) and never revisited. Amounts are untouched. */
  { const cut = Date.now() - 6 * HOUR; let rp = 0;
    for (const r of rows) { if (r[0] < cut) continue;
      const pp = prices.PTGC ? prices.PTGC(r[0]) : null, pu = prices.UFO ? prices.UFO(r[0]) : null;
      if (r[6] != null && pp > 0) { const v = Number((r[6] * pp).toPrecision(6)); if (v !== r[7]) { r[7] = v; rp++; } }
      if (r[8] != null && pu > 0) { const v = Number((r[8] * pu).toPrecision(6)); if (v !== r[9]) { r[9] = v; rp++; } } }
    if (rp) console.log(`re-priced ${rp} value(s) from the last 6 h with this run's prices`); }
  // round trips: a tx that buys a token in one pool and sells it in another (the arbitrage itself)
  const byTx = new Map();
  for (const r of rows) { const k = r[2] + '|' + r[1]; (byTx.get(k) || byTx.set(k, []).get(k)).push(r); }
  const arbRows = new Set();
  for (const grp of byTx.values()) {
    if (grp.length < 2) continue;
    for (const [i, j] of [[10, 6], [11, 8]]) {   // [dir slot, amount slot] for PTGC, UFO
      const buys = grp.filter(r => r[j] != null && r[i] > 0), sells = grp.filter(r => r[j] != null && r[i] < 0);
      if (!(buys.length && sells.length && new Set([...buys, ...sells].map(r => r[3])).size >= 2)) continue;
      // 2026-10-06 audit: a swap ROUTED THROUGH the token is not arbitrage — every leg via a human path (router / aggregator) and the
      // asset it was bought with is not the asset it was sold for (UFO→PTGC→WPLS = a person selling UFO for PLS). Arbitrage starts
      // and ends in the same asset, and bots call the pools from their own contracts anyway.
      const tokAddr = i === 10 ? TOKENS.PTGC.address : TOKENS.UFO.address;
      const partner = r => { const pl = pools[idx.pools[r[3]]] || {}; return pl.token0 === tokAddr ? pl.token1 : pl.token0; };
      const viaHuman = grp.every(r => classOf(idx.senders[r[4]]).kind === 'human');
      const inSet = new Set(buys.map(partner)), outSet = new Set(sells.map(partner));
      // …and arbitrage buys and sells ABOUT THE SAME amount of the token. A big sell split by the smart router across five pools
      // with one small buy leg on the way (every router "round trip" in 90 d: ratio ≤ 0.3, $108K of UFO sells) is a person selling.
      const bAmt = buys.reduce((a, r) => a + r[j], 0), sAmt = sells.reduce((a, r) => a + r[j], 0), balance = Math.min(bAmt, sAmt) / Math.max(bAmt, sAmt);
      if (viaHuman && (![...inSet].some(a => outSet.has(a)) || balance < ARB_MIN_BALANCE)) continue;
      [...buys, ...sells].forEach(r => arbRows.add(r));
    }
  }
  // aggregators by behaviour: who does each unlisted sender deliver to? (the whole 90 days) — and how much of it is round trips
  const poolSet = new Set(Object.keys(pools));
  // a "wallet" is never a pool, a contract that has ever called a pool (routers, aggregators, bots), the burn or zero address
  // (round 9 self-check: the `to` of a multi-hop buy is the router itself, and UFO's fee lands on the burn address — both had
  // been counted as wallets, and "trading 230 times a day" turned 3,400 human trades into bots)
  const notWallet = new Set([...poolSet, ...idx.senders, ...Object.keys(ROUTERS), '0x0000000000000000000000000000000000000369', '0x0000000000000000000000000000000000000000', '0x000000000000000000000000000000000000dead']);
  const isWallet = a => !!a && !notWallet.has(a);
  const recip = {};
  for (const r of rows) { const sd = idx.senders[r[4]], to = idx.wallets[r[13]]; const o = recip[sd] || (recip[sd] = { n: 0, other: 0, arb: 0, set: new Set() }); o.n++; if (arbRows.has(r)) o.arb++; if (to && to !== sd && isWallet(to)) { o.other++; o.set.add(to); } }
  for (const [sd, o] of Object.entries(recip)) {
    const arbShare = o.n ? o.arb / o.n : 0;
    if (ROUTERS[sd]) { cache.senders[sd] = { ...(cache.senders[sd] || {}), arbShare }; continue; }
    const cur = cache.senders[sd] || (cache.senders[sd] = { label: null, kind: 'bot', checkedAt: 0 });
    cur.arbShare = arbShare;
    const named = cur.by === 'name' || (cur.label && cur.by !== 'recipients');   // a PulseScan-named router (older caches have no `by`)
    if (arbShare >= ARB_BOT_SHARE && cur.kind === 'human' && !named) { cur.kind = 'bot'; cur.label = cur.label && cur.by === 'recipients' ? null : cur.label; cur.by = 'arb'; console.log(`  ${sd.slice(0, 10)}… ${Math.round(arbShare * 100)} % round trips → bot`); continue; }
    const agg = arbShare < ARB_AGG_MAX && o.set.size >= AGG_MIN_RECIPIENTS && o.other / o.n >= AGG_MIN_SHARE;
    if (agg && cur.kind !== 'human') { cur.kind = 'human'; cur.label = cur.label || 'aggregator (delivers to wallets)'; cur.by = 'recipients'; console.log(`  ${sd.slice(0, 10)}… delivers to ${o.set.size} wallets over ${o.other}/${o.n} trades → human (aggregator)`); }
    else if (!agg && cur.by === 'recipients') { cur.kind = 'bot'; cur.label = null; cur.by = null; }   // the pattern faded — back to bot
  }
  // re-class everything with the current knowledge (a sender promoted to human applies to its past trades too)
  for (const r of rows) { r[5] = classOf(idx.senders[r[4]]).kind === 'human' && !arbRows.has(r) ? 1 : 0; if (r[5] === 1 && r[12] < 0 && cache.from[r[2]]) r[12] = ix(idx.wallets, cache.from[r[2]]); }
  // bots that use a public router: the wallet behind a human-classed trade (tx.from, or the recipient of a buy) trading ≥ WALLET_BOT_PER_DAY
  // times in one day is a bot — every trade of that wallet becomes a bot's, attributed to the wallet (round 9)
  const walletOf = r => r[12] >= 0 ? idx.wallets[r[12]] : ((r[10] > 0 || r[11] > 0) && r[13] >= 0 && isWallet(idx.wallets[r[13]]) ? idx.wallets[r[13]] : null);
  // 2026-10-06 audit: count TRANSACTIONS a day, not legs — the PulseX smart router splits one swap across 3-4 pools (a person's
  // 18 swaps read as 57 "trades" and became a bot's)
  const perDay = {};
  for (const r of rows) { if (r[5] !== 1) continue; const w = walletOf(r); if (!w) continue; const k = w + '|' + Math.floor(r[0] / 86400000); (perDay[k] || (perDay[k] = new Set())).add(r[2] + '|' + r[1]); }
  const botWallets = new Set(Object.entries(perDay).filter(([, set]) => set.size >= WALLET_BOT_PER_DAY).map(([k]) => k.split('|')[0]));
  let viaRouter = 0;
  for (const r of rows) { if (r[5] === 1 && botWallets.has(walletOf(r))) { r[5] = 0; viaRouter++; } }
  if (botWallets.size) console.log(`  ${botWallets.size} wallet(s) trade ≥ ${WALLET_BOT_PER_DAY}× a day through a router → bots (${viaRouter} trades)`);
  const arbRowSet = new Set([...arbRows].map(r => r[2] + '|' + r[1] + '|' + r[3]));
  { const seenF = new Set(); const fr = [...cache.fees, ...freshFees.map(r => [tsOf(r[0]), ...r])]   // [ts, block, tx10, tok, gross]; the scanned ranges never overlap the cached ones — the key only guards a re-scan
      .filter(r => { if (r[0] < keepFrom) return false; const k = r[1] + '|' + r[2] + '|' + r[3]; if (seenF.has(k)) return false; seenF.add(k); return true; }).sort((x, y) => x[0] - y[0]);
    cache.fees = fr; cache.feeCursor = { block: head }; cache.feeFromBlock = Math.min(cache.feeFromBlock || Infinity, feeFrom, feeBackUsed ? feeBack[0] : Infinity); }
  cache.swaps = rows; cache.cursor = { block: head, ts: Date.now() }; cache.schema = SCHEMA; cache.fromBlock = Math.min(cache.fromBlock || Infinity, from, back ? back[0] : Infinity);
  // the view the aggregation below reads
  // a bot trade that came through a router is attributed to the wallet behind it, labelled "via <router>" — the router stays a human path
  const senderOf = r => { const sd = idx.senders[r[4]]; if (r[5] === 0 && classOf(sd).kind === 'human') { const w = walletOf(r); return w ? { addr: w, label: `bot wallet via ${classOf(sd).label || 'router'}` } : { addr: sd + ':via', label: `unknown wallets via ${classOf(sd).label || 'router'}` }; } return { addr: sd, label: classOf(sd).label }; };   // ':via' = not an address — the window shows no link
  /* Audit V v14: UFO's own swapback — in a tx where the PulseX v2 router swaps to 0x…0369 or the UFO contract, that router's legs
     to 0x…0369 / the UFO contract / itself are the contract's (fee-exempt) selling, buying-and-burning; the trader's own legs in the
     same tx (to a wallet) stay theirs. Kept inside the old human figures; split out in `measured`. */
  const protoRows = new Set();
  { const ufoA = TOKENS.UFO.address, toOf = r => r[13] >= 0 ? idx.wallets[r[13]] : null, sdOf = r => idx.senders[r[4]];
    const groups = new Map(); for (const r of rows) { const k = r[2] + '|' + r[1]; (groups.get(k) || groups.set(k, []).get(k)).push(r); }
    for (const g of groups.values()) {
      if (!g.some(r => sdOf(r) === PULSEX_V2_ROUTER && (toOf(r) === BURN_ADDR || toOf(r) === ufoA))) continue;
      for (const r of g) if (sdOf(r) === PULSEX_V2_ROUTER && [BURN_ADDR, ufoA, PULSEX_V2_ROUTER].includes(toOf(r))) protoRows.add(r);
    } }
  // per-tx class for the fee legs: any bot swap → bot; else a person's swap → human; else only swapback legs → protocol
  const txClass = new Map();
  for (const r of rows) { const k = r[2] + '|' + r[1], c = protoRows.has(r) ? 'protocol' : r[5] ? 'human' : 'bot', was = txClass.get(k);
    if (!was || c === 'bot' || (c === 'human' && was === 'protocol')) txClass.set(k, c); }
  const all = rows.map(r => ({ proto: protoRows.has(r), block: r[1], ts: r[0], tx: r[2], pool: idx.pools[r[3]], sender: senderOf(r).addr, senderLabel: senderOf(r).label, kind: r[5] ? 'human' : 'bot', arb: arbRowSet.has(r[2] + '|' + r[1] + '|' + r[3]), wallet: r[5] ? walletOf(r) : null, amounts: { ...(r[6] != null ? { PTGC: [r[6], r[7], r[10]] } : {}), ...(r[8] != null ? { UFO: [r[8], r[9], r[11]] } : {}) } }));

  // ---- the public file
  const now = Date.now();
  const periods = { '24h': 1, '7d': 7, '30d': 30, '90d': 90 };
  const zero = () => ({ n: 0, usd: 0 });
  const add = (o, usd) => { o.n++; o.usd += usd || 0; };
  const tokensOut = {};
  for (const tk of Object.keys(TOKENS)) {
    const mine = all.filter(s => s.amounts[tk]);
    // hourly series, 30 d: [hourTs, humanN, humanUsd, botN, botUsd]
    const hours = new Map();
    for (const s of mine) { const h = Math.floor(s.ts / HOUR) * HOUR; const row = hours.get(h) || [h, 0, 0, 0, 0]; const usd = s.amounts[tk][1] || 0; if (s.kind === 'human') { row[1]++; row[2] += usd; } else { row[3]++; row[4] += usd; } hours.set(h, row); }
    /* Audit V v13: each transaction counted ONCE per token — per (tx, side) the larger of its buy legs and its sell legs (a bot loop =
       a buy in one pool + a sell in another; a router split = several legs of one trade). Protocol legs apart (v14). */
    const txAgg = new Map();   // tx|block → {ts, side, buy, sell}
    for (const s of mine) { const side = s.proto ? 'protocol' : s.kind, k = s.tx + '|' + s.block + '|' + side, [, usd, dir] = s.amounts[tk];
      const t = txAgg.get(k) || txAgg.set(k, { ts: s.ts, side, buy: 0, sell: 0 }).get(k); if (dir < 0) t.sell += usd || 0; else t.buy += usd || 0; }
    const txList = [...txAgg.values()].map(t => ({ ts: t.ts, side: t.side, usd: Math.max(t.buy, t.sell) }));
    // the fee legs of this token, priced at the hour, classed by their tx
    const ti = tk === 'PTGC' ? 0 : 1;
    /* Audit V v24: each fee credited to the pool(s) its transaction traded in, split by the token amount each pool moved (a bot loop
       = half to each pool, a router split = by leg size); a fee with no swap of this token in its tx is a wallet send (`noPool`). */
    const amtSlot = ti === 0 ? 6 : 8;
    const poolsOfTx = k => { const g = (byTx.get(k) || []).filter(r => r[amtSlot] > 0); const tot = g.reduce((a, r) => a + r[amtSlot], 0); if (!(tot > 0)) return null;
      const m = new Map(); for (const r of g) { const pa = idx.pools[r[3]]; m.set(pa, (m.get(pa) || 0) + r[amtSlot] / tot); } return [...m]; };
    const feeList = (cache.fees || []).filter(r => r[3] === ti).map(r => { const p = prices[tk](r[0]); return { ts: r[0], side: txClass.get(r[2] + '|' + r[1]) || 'transfer', tok: r[4] * FEE_TOTAL[tk], usd: p > 0 ? r[4] * FEE_TOTAL[tk] * p : null, k: r[2] + '|' + r[1], pools: poolsOfTx(r[2] + '|' + r[1]) }; });
    const feeSince = feeList.reduce((m, f) => f.ts < m ? f.ts : m, Infinity), feeSinceOk = isFinite(feeSince);
    const mHours = new Map();   // [hourTs, humanUsd, botUsd, humanFeeUsd, botFeeUsd, transferFeeUsd]
    for (const t of txList) { if (t.side === 'protocol') continue; const h = Math.floor(t.ts / HOUR) * HOUR, row = mHours.get(h) || [h, 0, 0, 0, 0, 0]; row[t.side === 'human' ? 1 : 2] += t.usd; mHours.set(h, row); }
    for (const f of feeList) { if (f.usd == null || f.side === 'protocol') continue; const h = Math.floor(f.ts / HOUR) * HOUR, row = mHours.get(h) || [h, 0, 0, 0, 0, 0]; row[f.side === 'human' ? 3 : f.side === 'bot' ? 4 : 5] += f.usd; mHours.set(h, row); }
    const per = {};
    for (const [p, days] of Object.entries(periods)) {
      const since = now - days * 86400000;
      const o = { human: zero(), bot: zero(), tokens: { human: 0, bot: 0 }, pools: {}, senders: {},
        buys: { human: zero(), bot: zero() }, sells: { human: zero(), bot: zero() },        // round 5: direction per side
        hod: Array.from({ length: 24 }, () => [0, 0]),                                        // round 5: USD by UTC hour of day [human, bot]
        wallets: { human: 0, humanTxs: 0, humanTxsKnown: 0 },                                 // round 5: distinct wallets behind the human trades
        arb: { n: 0, usd: 0, txs: 0 } };                                                       // round 7: round-trip trades (buy one pool, sell another, one tx)
      const arbTx = new Set();
      const hw = new Set(), htx = new Set(), htxKnown = new Set();
      for (const s of mine) {
        if (s.ts < since) continue;
        const [amt, usd, dir] = s.amounts[tk];
        add(o[s.kind], usd); o.tokens[s.kind] += amt;
        if (dir > 0) add(o.buys[s.kind], usd); else if (dir < 0) add(o.sells[s.kind], usd);
        o.hod[new Date(s.ts).getUTCHours()][s.kind === 'human' ? 0 : 1] += usd || 0;
        if (s.kind === 'human') { htx.add(s.tx); if (s.wallet) { hw.add(s.wallet); htxKnown.add(s.tx); } }
        if (s.arb) { add(o.arb, usd); arbTx.add(s.tx); }
        const pl = o.pools[s.pool] || (o.pools[s.pool] = { name: pools[s.pool].name, human: zero(), bot: zero() }); add(pl[s.kind], usd);
        const sd = o.senders[s.sender] || (o.senders[s.sender] = { kind: s.kind, label: s.senderLabel, n: 0, usd: 0, arb: 0 }); sd.n++; sd.usd += usd || 0; if (s.arb) sd.arb++;
      }
      const round = x => Number(x.toPrecision(6));
      o.human.usd = round(o.human.usd); o.bot.usd = round(o.bot.usd); o.tokens.human = round(o.tokens.human); o.tokens.bot = round(o.tokens.bot);
      for (const k of ['human', 'bot']) { o.buys[k].usd = round(o.buys[k].usd); o.sells[k].usd = round(o.sells[k].usd); }
      o.hod = o.hod.map(([h, b]) => [round(h), round(b)]);
      o.wallets = { human: hw.size, humanTxs: htx.size, humanTxsKnown: htxKnown.size };
      o.arb = { n: o.arb.n, usd: round(o.arb.usd), txs: arbTx.size };
      for (const pl of Object.values(o.pools)) { pl.human.usd = round(pl.human.usd); pl.bot.usd = round(pl.bot.usd); }
      { const r6 = x => Number((x || 0).toPrecision(6)), m = { human: { usd: 0, txs: 0 }, bot: { usd: 0, txs: 0 }, protocol: { usd: 0, txs: 0 } };
        for (const t of txList) { if (t.ts < since) continue; m[t.side].usd += t.usd; m[t.side].txs++; }
        const fees = { human: { tokens: 0, usd: 0, txs: 0 }, bot: { tokens: 0, usd: 0, txs: 0 }, transfer: { tokens: 0, usd: 0, txs: 0 }, protocol: { tokens: 0, usd: 0, txs: 0 }, unpriced: 0 };
        const feeTx = { human: new Set(), bot: new Set(), transfer: new Set(), protocol: new Set() };
        const poolFees = {}, noPool = { tokens: 0, usd: 0, txs: 0 };
        for (const f of feeList) { if (f.ts < since) continue; const b = fees[f.side]; b.tokens += f.tok; if (f.usd == null) fees.unpriced++; else b.usd += f.usd; feeTx[f.side].add(f.k);
          if (!f.pools) { noPool.tokens += f.tok; noPool.usd += f.usd || 0; noPool.txs++; continue; }
          for (const [pa, w] of f.pools) { const q = poolFees[pa] || (poolFees[pa] = { tokens: 0, usd: 0, txs: 0 }); q.tokens += f.tok * w; q.usd += (f.usd || 0) * w; q.txs++; } }
        for (const q of Object.values(poolFees)) { q.tokens = r6(q.tokens); q.usd = r6(q.usd); }
        fees.pools = poolFees; fees.noPool = { tokens: r6(noPool.tokens), usd: r6(noPool.usd), txs: noPool.txs };   // Audit V v24
        for (const k of ['human', 'bot', 'transfer', 'protocol']) { fees[k] = { tokens: r6(fees[k].tokens), usd: r6(fees[k].usd), txs: feeTx[k].size }; }
        fees.total = { tokens: r6(fees.human.tokens + fees.bot.tokens + fees.transfer.tokens + fees.protocol.tokens), usd: r6(fees.human.usd + fees.bot.usd + fees.transfer.usd + fees.protocol.usd) };
        fees.since = feeSinceOk ? new Date(feeSince).toISOString() : null; fees.complete = !!(feeSinceOk && feeSince <= since + 6 * HOUR); fees.rate = FEE_TOTAL[tk];
        const allSenders = Object.values(o.senders);
        o.measured = { human: { usd: r6(m.human.usd), txs: m.human.txs }, bot: { usd: r6(m.bot.usd), txs: m.bot.txs }, protocol: { usd: r6(m.protocol.usd), txs: m.protocol.txs },
          botContracts: allSenders.filter(v => v.kind === 'bot' && !String(v.label || '').startsWith('bot wallet')).length, botWallets: allSenders.filter(v => v.kind === 'bot' && String(v.label || '').startsWith('bot wallet')).length, routers: allSenders.filter(v => v.kind === 'human').length,
          fees }; }
      o.senders = Object.entries(o.senders).map(([addr, v]) => ({ addr, ...v, usd: round(v.usd), arbShare: v.n ? Number((v.arb / v.n).toFixed(3)) : 0 })).sort((a, b) => b.usd - a.usd || b.n - a.n).slice(0, 25);
      per[p] = o;
    }
    tokensOut[tk] = { hours: [...hours.values()].sort((a, b) => a[0] - b[0]).map(r => [r[0], r[1], Number(r[2].toPrecision(6)), r[3], Number(r[4].toPrecision(6))]),
      measuredHours: [...mHours.values()].sort((a, b) => a[0] - b[0]).map(r => [r[0], ...r.slice(1).map(x => Number(x.toPrecision(6)))]),   // Audit V: [hourTs, humanUsd, botUsd (each tx once), humanFeeUsd, botFeeUsd, transferFeeUsd]
      periods: per };
  }
  const out = {
    schema: SCHEMA, generatedAt: new Date(now).toISOString(),
    method: 'Swap events of every PTGC / UFO pool. Bot: a round trip (buys the token in one pool and sells it in another inside one transaction), or a sender that is not a known router / aggregator (named on PulseScan, or delivering to many different wallets). USD = token-side amount × hourly close (charts-intraday.json); direction = the token leaving the pool is a buy; wallets = tx.from / the buy recipient of the human trades',
    cursor: cache.cursor, since: new Date(Math.max(keepFrom, all.length ? all[0].ts : keepFrom)).toISOString(),
    routers: { ...ROUTERS, ...Object.fromEntries(Object.entries(cache.senders).filter(([, v]) => v.kind === 'human' && v.label).map(([a, v]) => [a, v.label])) },
    pools: Object.fromEntries(Object.entries(pools).map(([a, r]) => [a, { name: r.name, tokens: r.tokens, token0: r.token0, token1: r.token1 }])),   // token0/1: the window draws the other token's logo
    tokens: tokensOut,
    measuredSchema: 2,   // Audit V: periods[p].measured + measuredHours (v12–v14); 2 = measured.fees.pools / noPool (v24)
    stats: { feeLegs: (cache.fees || []).length, feeSince: cache.fees && cache.fees.length ? new Date(cache.fees[0][0]).toISOString() : null, swaps: all.length, walletsPending: (cache.fromPending || []).length, newThisRun: fresh.length, unpricedThisRun: unpriced, pools: addrs.length, ms: now - t0 },
  };
  fs.mkdirSync('data', { recursive: true });
  fs.writeFileSync(CACHE_PATH, JSON.stringify(cache));
  fs.writeFileSync(OUT_PATH, JSON.stringify(out));
  const s = out.tokens;
  console.log(`wrote ${OUT_PATH} (${(fs.statSync(OUT_PATH).size / 1024).toFixed(1)} KB) + cache (${(fs.statSync(CACHE_PATH).size / 1024).toFixed(1)} KB) in ${Math.round((now - t0) / 1000)} s — cursor ${head}, ${all.length} swaps kept, ${unpriced} unpriced this run`);
  for (const tk of Object.keys(TOKENS)) for (const p of Object.keys(periods)) { const o = s[tk].periods[p]; console.log(`  ${tk} ${p}: human ${o.human.n} trades $${Math.round(o.human.usd).toLocaleString()} · bot ${o.bot.n} trades $${Math.round(o.bot.usd).toLocaleString()}`); }
}

main().catch(e => { console.error('build-swap-volume failed:', e); process.exit(1); });
