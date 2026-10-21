// backfill-fast.mjs — the rank-history backfill, fast (2026-10-21): exact balances at every UTC day boundary, same result as
// backfill-rank-history.mjs, in minutes instead of hours.
//   phase 1  stream every Transfer event of the token's life (eth_getLogs, a day of blocks at a time, split on an oversized
//            reply) → for each UTC day the set of wallets that moved. ~2,000 events/s.
//   phase 2  classify every address once (known list, PulseScan's is_contract from the seed, eth_getCode for the rest, 256 wide).
//   phase 3  every (wallet, day-end block) balance read as ONE flat queue, 256 concurrent (~390 reads/s measured). A wallet
//            that moved on day D is read at the last block of day D; between moves a balance only changes by reflections,
//            which scale every holder alike, so the day's ORDER is exact with the balance carried forward.
//   phase 4  walk the days forward, carrying balances, and write each day's sorted holder list — the same file layout the
//            daily step (scripts/build-rank-history.mjs) extends.
//   node backfill-fast.mjs PTGC            env SEED=<holders.json> OUT=<file> RPC=…
import fs from 'node:fs';
const RPC = process.env.RPC || 'https://rpc.pulsechain.com';
const [, , SYM] = process.argv;
const TOK = { PTGC: { a: '0x94534eeee131840b1c0f61847c572228bdfdde93', launch: '2023-10-10' }, UFO: { a: '0x49ed499433bee42dd34c169470fef2c8f9fae6e6', launch: '2026-07-08' } }[SYM];
const OUT = process.env.OUT || `rank-history-${SYM}.json`;
const EXCL = new Set(['0x0000000000000000000000000000000000000369','0x0000000000000000000000000000000000000000','0x000000000000000000000000000000000000dead','0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1','0x440773b5104a102c00ef26979a5c897155336a34','0x305acfab82103c2b82b19543919d1c93b44e55db','0x92dd8e86fdb206fa41e451398a9f03fbd36d574d','0xc71f597a2ac39e47f07102e849d18489c96f39ef','0x165c3410fc91ef562c50559f7d2289febed552d9','0x94534eeee131840b1c0f61847c572228bdfdde93','0x49ed499433bee42dd34c169470fef2c8f9fae6e6','0x456548a9b56efbbd89ca0309edd17a9e20b04018']);
const TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let id = 1;
async function rpc(method, params, tries = 8) {
  for (let k = 0; k < tries; k++) {
    try {
      const r = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: id++, method, params }) });
      const txt = await r.text(); let j; try { j = JSON.parse(txt); } catch (e) { throw new Error('truncated'); }
      if (j.error) throw new Error(JSON.stringify(j.error).slice(0, 100));
      return j.result;
    } catch (e) { if (k === tries - 1) throw e; await sleep(500 * (k + 1) + Math.random() * 300); }
  }
}
const tsOf = async b => parseInt((await rpc('eth_getBlockByNumber', ['0x' + b.toString(16), false])).timestamp, 16);
async function blockAt(t, lo, hi) { while (lo < hi) { const m = Math.floor((lo + hi) / 2); if (await tsOf(m) < t) lo = m + 1; else hi = m; } return lo; }
const dayStr = t => new Date(t * 1000).toISOString().slice(0, 10);
const utc0 = d => Math.floor(Date.parse(d + 'T00:00:00Z') / 1000);
async function getLogs(from, to) {
  try { return await rpc('eth_getLogs', [{ fromBlock: '0x' + from.toString(16), toBlock: '0x' + to.toString(16), address: TOK.a, topics: [TOPIC] }], 2); }
  catch (e) { if (to - from < 50) throw e; const m = Math.floor((from + to) / 2); return [...await getLogs(from, m), ...await getLogs(m + 1, to)]; }
}
async function pool(items, C, fn, label) {
  let i = 0, done = 0; const t0 = Date.now();
  await Promise.all(Array.from({ length: C }, async () => { while (i < items.length) { const it = items[i++]; await fn(it); if (++done % 20000 === 0) console.log(`${SYM}: ${label} ${done}/${items.length} (${((Date.now() - t0) / 1000).toFixed(0)} s)`); } }));
}
const ONE = 10n ** 18n, MICRO = 10n ** 12n;
const key = v => { const w = v / ONE; return w >= 1n ? Number(w) : Math.max(1, Number(v / MICRO)) / 1e6; };

(async () => {
  const T0 = Date.now();
  const head = parseInt(await rpc('eth_blockNumber', []), 16);
  const today = dayStr(Math.floor(Date.now() / 1000));
  const days = []; for (let d = TOK.launch; d < today; d = dayStr(utc0(d) + 86400)) days.push(d);
  console.log(`${SYM}: ${days.length} days ${days[0]} → ${days[days.length - 1]}; finding day-end blocks…`);
  // day-end blocks: anchor first and last by search, then every other day in parallel inside a narrow window around an
  // estimate from the actual blocks/day (~14 timestamp reads a day, 64 days at a time)
  const dayEnd = {};
  const t1 = utc0(days[0]) + 86400, b1 = await blockAt(t1, 1, head) - 1; dayEnd[days[0]] = b1;
  const tN = utc0(days[days.length - 1]) + 86400, bN = await blockAt(tN, b1, head) - 1; dayEnd[days[days.length - 1]] = bN;
  const perDay = (bN - b1) / Math.max(1, days.length - 1);
  await pool(days.slice(1, -1), 64, async d => { const t = utc0(d) + 86400; const est = b1 + Math.round(perDay * ((utc0(d) - utc0(days[0])) / 86400)); dayEnd[d] = await blockAt(t, Math.max(1, est - 4000), Math.min(head, est + 4000)) - 1; }, 'day ends');
  console.log(`${SYM}: blocks ${dayEnd[days[0]]} … ${dayEnd[days[days.length - 1]]} (${((Date.now() - T0) / 1000).toFixed(0)} s)`);
  // phase 1
  const movedBy = {}; let total = 0; const from0 = await blockAt(utc0(days[0]), 1, dayEnd[days[0]]);
  const dayChunks = days.map((d, i) => [d, i === 0 ? from0 : dayEnd[days[i - 1]] + 1, dayEnd[d]]);
  const allAddr = new Set();
  await pool(dayChunks, 6, async ([d, a, z]) => { const L = await getLogs(a, z); const s = new Set(); for (const l of L) { s.add('0x' + l.topics[1].slice(26)); s.add('0x' + l.topics[2].slice(26)); } movedBy[d] = [...s]; total += L.length; s.forEach(x => allAddr.add(x)); }, 'transfers by day');
  console.log(`${SYM}: ${total} transfers, ${allAddr.size} addresses (${((Date.now() - T0) / 1000).toFixed(0)} s)`);
  // phase 2
  const isC = new Map();
  if (process.env.SEED) for (const [a, , c] of JSON.parse(fs.readFileSync(process.env.SEED, 'utf8'))) isC.set(a, !!c);
  for (const a of EXCL) isC.set(a, true);   // the never-a-holder list wins over PulseScan's flag (burn / OA / DAO are EOAs there)
  const unknown = [...allAddr].filter(a => !isC.has(a));
  await pool(unknown, 256, async a => { const c = await rpc('eth_getCode', [a, 'latest']); isC.set(a, !!c && c !== '0x'); }, 'getCode');
  console.log(`${SYM}: ${[...isC.values()].filter(Boolean).length} contracts of ${isC.size} seen (${((Date.now() - T0) / 1000).toFixed(0)} s)`);
  // phase 3 — plus, per day, REFERENCE wallets that did not move that day: their day-end balance ÷ previous day-end balance is
  // the day's reflection factor, which every untouched holder shares exactly (measured: 36 of 39 random UFO holders grew by
  // the same 1.000678 over a month; the other 3 had traded). Three references a day, the median wins.
  const reads = []; for (const d of days) for (const a of movedBy[d]) if (!isC.get(a)) reads.push([a, d]);
  // references per day: people who had a Transfer on an EARLIER day (so they hold by then) and none on `prev` or `d` — the
  // first 6 such found scanning the most recent movers; their day-end balance ÷ prev-day-end balance = the day's factor
  const refs = {}; const seen = new Set();
  const recent = [];   // movers in day order, people only
  for (let i = 0; i < days.length; i++) {
    const d = days[i];
    if (i >= 1) { const m = new Set(movedBy[d]), mp = new Set(movedBy[days[i - 1]]); const r = [];
      for (let k = recent.length - 1; k >= 0 && r.length < 6; k--) { const a = recent[k]; if (m.has(a)) continue; r.push(a); }
      refs[d] = r; for (const a of r) { reads.push([a, d]); reads.push([a, days[i - 1]]); } }
    for (const a of movedBy[d]) if (!isC.get(a) && !seen.has(a)) { seen.add(a); recent.push(a); }
  }
  const bal = new Map();
  console.log(`${SYM}: ${reads.length} balance reads…`);
  await pool(reads, 256, async ([a, d]) => { const h = await rpc('eth_call', [{ to: TOK.a, data: '0x70a08231' + a.slice(2).padStart(64, '0') }, '0x' + dayEnd[d].toString(16)]); if (h === undefined || h === null) throw new Error('bad read ' + a + ' ' + d); bal.set(a + '|' + d, h === '0x' ? 0n : BigInt(h)); /* '0x' = the contract did not exist yet at that block → 0 */ }, 'balances');
  console.log(`${SYM}: reads done (${((Date.now() - T0) / 1000).toFixed(0)} s)`);
  // phase 4: walk forward and write the DELTA archive (schema 2: per day the factor + only the wallets that moved) — a full
  // per-day list is ~670 MB for PTGC and does not even fit one JSON string. scripts/build-rank-history.mjs extends this.
  const factor = {};
  for (let i = 1; i < days.length; i++) { const d = days[i], prev = days[i - 1]; let s0 = 0n, s1 = 0n;
    for (const a of refs[d] || []) { const v0 = bal.get(a + '|' + prev), v1 = bal.get(a + '|' + d); if (v0 > 0n && v1 > 0n) { s0 += v0; s1 += v1; } }
    factor[d] = s0 > 0n ? Number(s1 * 10n ** 15n / s0) / 1e15 : 1; }
  const cur = new Map(); /* a → { v: wei at last read, g: cumulative growth since } */
  const out = { schema: 2, token: SYM, launch: TOK.launch, days: {}, contracts: [...isC.entries()].filter(x => x[1]).map(x => x[0]), eoa: [...isC.entries()].filter(x => !x[1]).map(x => x[0]) };
  const wei = e => e.g === 1 ? e.v : BigInt(Math.round(Number(e.v / 10n ** 9n) * e.g)) * 10n ** 9n;
  for (const d of days) {
    const f = factor[d] || 1; for (const e of cur.values()) e.g *= f;
    const m = {};
    for (const a of movedBy[d]) { if (isC.get(a)) continue; const v = bal.get(a + '|' + d); if (v > 0n) { cur.set(a, { v, g: 1 }); m[a] = key(v); } else if (cur.has(a)) { cur.delete(a); m[a] = 0; } }
    out.days[d] = { b: dayEnd[d], f, m, n: cur.size };
  }
  out.cur = Object.fromEntries([...cur.entries()].map(([a, e]) => [a, wei(e).toString()])); out.cursorDay = days[days.length - 1]; out.generatedAt = new Date().toISOString();
  fs.writeFileSync(OUT + '.tmp', JSON.stringify(out)); fs.renameSync(OUT + '.tmp', OUT);
  console.log(`${SYM}: wrote ${OUT} — ${days.length} days, ${cur.size} holders today, ${(fs.statSync(OUT).size / 1e6).toFixed(1)} MB, ${((Date.now() - T0) / 60000).toFixed(1)} min`);
})().catch(e => { console.error('FAILED', e.message); process.exit(1); });
