// backfill-rank-history.mjs — rebuilds every real holder's balance for every UTC day of a token's life, walking BACKWARDS
// from today's full holder list (data/holder-ranks.json's reading, re-read here by address) using Transfer events:
//   day D's balances = day D+1's balances, with every wallet that had a Transfer during day D+1 re-read exactly at the
//   last block of day D (one archive balanceOf each). Exact by construction; UFO reflections scale every balance alike,
//   so the ORDER (the rank) is unaffected.
// Writes data/rank-history/<TOKEN>.json: { schema, token, days:[{d:'YYYY-MM-DD', b:lastBlock, n:holders}], and the
// per-day sorted balance lists in a compact side file so the daily step can extend it. Resumable: progress is in the file.
//   node backfill-rank-history.mjs PTGC [stopDate]
import fs from 'node:fs';
const RPC = process.env.RPC || 'https://rpc.pulsechain.com';
const [, , SYM, STOP] = process.argv;
const TOK = { PTGC: { a: '0x94534eeee131840b1c0f61847c572228bdfdde93', launch: '2023-10-10' }, UFO: { a: '0x49ed499433bee42dd34c169470fef2c8f9fae6e6', launch: '2026-07-08' } }[SYM];
const OUT = process.env.OUT || `rank-history-${SYM}.json`;
const EXCL = new Set(['0x0000000000000000000000000000000000000369','0x0000000000000000000000000000000000000000','0x000000000000000000000000000000000000dead','0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1','0x440773b5104a102c00ef26979a5c897155336a34','0x305acfab82103c2b82b19543919d1c93b44e55db','0x92dd8e86fdb206fa41e451398a9f03fbd36d574d','0xc71f597a2ac39e47f07102e849d18489c96f39ef','0x165c3410fc91ef562c50559f7d2289febed552d9','0x94534eeee131840b1c0f61847c572228bdfdde93','0x49ed499433bee42dd34c169470fef2c8f9fae6e6','0x456548a9b56efbbd89ca0309edd17a9e20b04018']);
const TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const sleep = ms => new Promise(r => setTimeout(r, ms));
let id = 1;
async function rpc(method, params, tries = 6) {
  for (let k = 0; k < tries; k++) {
    try {
      const r = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: id++, method, params }) });
      const j = await r.json();
      if (j.error) throw new Error(JSON.stringify(j.error).slice(0, 120));
      return j.result;
    } catch (e) { if (k === tries - 1) throw e; await sleep(800 * (k + 1)); }
  }
}
async function batchBalances(addrs, block) {
  const out = new Map(); const C = 24;
  for (let i = 0; i < addrs.length; i += C) {
    const chunk = addrs.slice(i, i + C);
    const rs = await Promise.all(chunk.map(a => rpc('eth_call', [{ to: TOK.a, data: '0x70a08231' + a.slice(2).padStart(64, '0') }, block])));
    chunk.forEach((a, j) => { const h = rs[j]; if (!h || h === '0x') throw new Error('bad balance read ' + a); out.set(a, BigInt(h)); });
  }
  return out;
}
const tsOf = async b => parseInt((await rpc('eth_getBlockByNumber', [b, false])).timestamp, 16);
async function blockAt(t, lo, hi) { while (lo < hi) { const m = Math.floor((lo + hi) / 2); if (await tsOf('0x' + m.toString(16)) < t) lo = m + 1; else hi = m; } return lo; }
const dayStr = t => new Date(t * 1000).toISOString().slice(0, 10);
const utc0 = d => Math.floor(Date.parse(d + 'T00:00:00Z') / 1000);
async function getLogs(from, to) {
  // the RPC caps big ranges: split on error
  try { return await rpc('eth_getLogs', [{ fromBlock: '0x' + from.toString(16), toBlock: '0x' + to.toString(16), address: TOK.a, topics: [TOPIC] }], 2); }
  catch (e) { if (to - from < 200) throw e; const m = Math.floor((from + to) / 2); return [...await getLogs(from, m), ...await getLogs(m + 1, to)]; }
}
// contracts: PulseScan told us which holders are contracts (today's list); for unknown addresses seen in old transfers, eth_getCode once
const isC = new Map();
async function isContract(a) { if (isC.has(a)) return isC.get(a); const c = await rpc('eth_getCode', [a, 'latest']); const v = !!c && c !== '0x'; isC.set(a, v); return v; }

(async () => {
  let st = fs.existsSync(OUT) ? JSON.parse(fs.readFileSync(OUT, 'utf8')) : null;
  const head = parseInt(await rpc('eth_blockNumber', []), 16);
  if (!st) {
    // seed: today's holders by address (PulseScan list, dumped by holders.py), balances re-read at the END of yesterday (UTC)
    const seedRows = JSON.parse(fs.readFileSync(process.env.SEED, 'utf8'));
    for (const [a, , c] of seedRows) if (c) isC.set(a, true);
    const today = dayStr(Math.floor(Date.now() / 1000));
    const yEnd = utc0(today) - 1;                         // last second of yesterday
    const bEnd = await blockAt(yEnd + 1, head - 20000, head) - 1;
    const addrs = seedRows.map(r => r[0]).filter(a => !EXCL.has(a) && !isC.get(a));
    console.log(`${SYM}: seeding ${addrs.length} people at block ${bEnd} (${dayStr(yEnd)})`);
    const bal = await batchBalances(addrs, '0x' + bEnd.toString(16));
    const cur = {}; for (const [a, v] of bal) if (v > 0n) cur[a] = v.toString();
    st = { schema: 1, token: SYM, launch: TOK.launch, cursorDay: dayStr(yEnd), cursorBlock: bEnd, cur, days: {}, contracts: [...isC.entries()].filter(x => x[1]).map(x => x[0]) };
    st.days[dayStr(yEnd)] = snapshot(cur, bEnd);
    save(st);
  } else { for (const a of st.contracts) isC.set(a, true); }
  const stopDay = STOP || TOK.launch;
  let t0 = Date.now(), n = 0;
  while (st.cursorDay > stopDay) {
    // the day we are about to compute = cursorDay − 1; its last block = the block before cursor-day's first block
    const dayStart = utc0(st.cursorDay);                   // first second of cursorDay
    const firstBlk = await blockAt(dayStart, Math.max(1, st.cursorBlock - 12000), st.cursorBlock);
    const prevEnd = firstBlk - 1, prevDay = dayStr(dayStart - 1);
    // who moved during cursorDay (firstBlk .. cursorBlock)?
    const logs = await getLogs(firstBlk, st.cursorBlock);
    const moved = new Set();
    for (const l of logs) { moved.add('0x' + l.topics[1].slice(26)); moved.add('0x' + l.topics[2].slice(26)); }
    const todo = [];
    for (const a of moved) { if (EXCL.has(a)) continue; if (await isContract(a)) continue; todo.push(a); }
    const bal = await batchBalances(todo, '0x' + prevEnd.toString(16));
    for (const [a, v] of bal) { if (v > 0n) st.cur[a] = v.toString(); else delete st.cur[a]; }
    st.days[prevDay] = snapshot(st.cur, prevEnd);
    st.cursorDay = prevDay; st.cursorBlock = prevEnd; st.contracts = [...isC.entries()].filter(x => x[1]).map(x => x[0]);
    n++; if (n % 5 === 0 || prevDay <= stopDay) { save(st); console.log(`${SYM}: ${prevDay} done — ${Object.keys(st.cur).length} holders, ${logs.length} transfers, ${todo.length} re-read; ${((Date.now() - t0) / 1000 / n).toFixed(1)} s/day`); }
  }
  save(st); console.log(`${SYM}: backfill complete to ${st.cursorDay}`);
})().catch(e => { console.error('FAILED', e.message); process.exit(1); });

// a day's record: holder count + the sorted balances as whole tokens (≥1) or 6-decimals (<1) — the same key as holder-ranks.json
function snapshot(cur, blk) {
  // every holder that day: [address, key] sorted high → low — the index step derives each wallet's rank from it
  const ONE = 10n ** 18n, MICRO = 10n ** 12n;
  const rows = Object.entries(cur).map(([a, s]) => { const v = BigInt(s); const w = v / ONE; return [a, w >= 1n ? Number(w) : Math.max(1, Number(v / MICRO)) / 1e6]; });
  rows.sort((x, y) => y[1] - x[1]);
  return { b: blk, n: rows.length, h: rows };
}
function save(st) { fs.writeFileSync(OUT + '.tmp', JSON.stringify(st)); fs.renameSync(OUT + '.tmp', OUT); }
