#!/usr/bin/env node
/* One-time rebuild of a burn archive straight from the chain — burn archive v2 (2026-10-24).
   See "BURN ARCHIVE v2" in scripts/fetch-burn-history.js for why; this tool uses that script's own scanBurns.

     node tools/rebuild-burn-archive.js PTGC 2025-07-01     # every PTGC burn from that UTC date to the head
     node tools/rebuild-burn-archive.js UFO 2024-05-01      # the retired UFO contract (ufo-burns.json), all of it

   Writes data/ptgc-burns-rebuild-<token>-<YYYY-MM>-p<n>.json (≤ 120k rows a file, rows {b, i, t, a, f}). The next
   pipeline run swaps them in for every stored row from that date on, continues from their last block and
   deletes them. Nothing is written unless BOTH checks pass against balanceOf(0x…369):
     1. the rebuilt rows add up to the burn address's balance change over exactly the rebuilt blocks;
     2. the kept older rows + the rebuilt rows add up to the balance at the last rebuilt block.
   Needs public RPC access (rpc.pulsechain.com); ~15 min for PTGC from 2025-07. */
const fs = require('fs');
const path = require('path');
const B = require('../scripts/fetch-burn-history.js');

const [tokenArg, dateArg] = process.argv.slice(2);
const TOKEN = (tokenArg || '').toUpperCase();
if (!['PTGC', 'UFO'].includes(TOKEN) || !/^\d{4}-\d{2}-\d{2}$/.test(dateArg || '')) {
  console.error('usage: node tools/rebuild-burn-archive.js PTGC|UFO YYYY-MM-DD');
  process.exit(2);
}
const ADDRESS = TOKEN === 'PTGC' ? B.PTGC_ADDRESS : B.UFO_ADDRESS;
const DECIMALS = TOKEN === 'PTGC' ? B.PTGC_DECIMALS : B.UFO_DECIMALS;
const DATA = path.join(__dirname, '..', 'data');

/* The first block whose real timestamp is ≥ tsMs. */
async function blockAt(tsMs, head) {
  let lo = 17000000, hi = head;
  while (lo < hi) {
    const mid = Math.floor((lo + hi) / 2);
    const t = (await B.blockTimes([mid])).get(mid);
    if (t < tsMs) lo = mid + 1; else hi = mid;
  }
  return lo;
}

(async () => {
  const replaceFromTs = Date.parse(dateArg + 'T00:00:00Z');
  const head = await B.headBlock(TOKEN);
  const toBlock = head - B.CONFIRM_BLOCKS;
  const fromBlock = await blockAt(replaceFromTs, head);
  const toTs = (await B.blockTimes([toBlock])).get(toBlock);
  console.log(`${TOKEN}: rebuilding blocks ${fromBlock}–${toBlock} (${new Date(replaceFromTs).toISOString()} → ${new Date(toTs).toISOString()})`);

  const rows = await B.scanBurns(ADDRESS, DECIMALS, fromBlock, toBlock, { chunk: TOKEN === 'UFO' ? 10000 : 4000, concurrency: 4, label: TOKEN, retries: 8 });
  rows.sort((x, y) => (y.t - x.t) || (y.b - x.b) || (y.i - x.i));
  if (rows.some(r => !(r.t >= replaceFromTs && r.t <= toTs))) throw new Error('a rebuilt row has a time outside the rebuilt range');

  // check 1 — the rebuilt blocks alone
  let balBefore = await B.burnAddressBalance(ADDRESS, DECIMALS, fromBlock - 1);
  if (balBefore == null && (await B.rpcCall('eth_getCode', [ADDRESS, '0x' + (fromBlock - 1).toString(16)])) === '0x') balBefore = 0;   // the token did not exist yet
  const balTo = await B.burnAddressBalance(ADDRESS, DECIMALS, toBlock);
  if (balBefore == null || balTo == null) throw new Error('could not read the burn address balance — nothing written');
  const sumRows = rows.reduce((s, r) => s + r.a, 0);
  const d1 = sumRows - (balTo - balBefore);
  console.log(`check 1: rebuilt ${rows.length} burns = ${sumRows.toLocaleString()} | balance change over the same blocks ${(balTo - balBefore).toLocaleString()} | diff ${d1.toFixed(6)}`);
  if (!(Math.abs(d1) <= B.RECONCILE_TOLERANCE)) throw new Error('check 1 failed — nothing written');

  // check 2 — the whole archive the pipeline will hold
  const stored = B.loadExistingBurns(DATA, TOKEN);
  const kept = stored.filter(r => r.t < replaceFromTs);
  const sumKept = kept.reduce((s, r) => s + r.a, 0);
  const d2 = sumKept + sumRows - balTo;
  console.log(`check 2: kept ${kept.length} older rows ${sumKept.toLocaleString()} + rebuilt ${sumRows.toLocaleString()} vs balance ${balTo.toLocaleString()} at block ${toBlock} | diff ${d2.toFixed(6)}`);
  if (!(Math.abs(d2) <= B.RECONCILE_TOLERANCE)) throw new Error('check 2 failed — the rows kept from before the rebuild date do not add up; rebuild from an earlier date. Nothing written');
  const dropped = stored.filter(r => r.t >= replaceFromTs);
  console.log(`the stored archive had ${dropped.length} rows = ${dropped.reduce((s, r) => s + r.a, 0).toLocaleString()} from ${dateArg} on; the chain has ${rows.length} = ${sumRows.toLocaleString()}`);

  // write: oldest first, ≤ 120,000 rows (~13 MB) a file, named after the month its first burn is in
  const prefix = B.REBUILD_PREFIX + TOKEN.toLowerCase() + '-';
  for (const f of fs.readdirSync(DATA)) if (f.startsWith(prefix)) fs.unlinkSync(path.join(DATA, f));
  const asc = rows.slice().reverse();
  const chunks = [];
  for (let k = 0; k < asc.length; k += 120000) chunks.push(asc.slice(k, k + 120000));
  if (!chunks.length) chunks.push([]);
  chunks.forEach((part, k) => {
    const name = `${prefix}${part.length ? new Date(part[0].t).toISOString().slice(0, 7) : dateArg.slice(0, 7)}-p${k + 1}.json`;
    const file = path.join(DATA, name);
    fs.writeFileSync(file, JSON.stringify({
      schema: 2, token: TOKEN, address: ADDRESS, replaceFromTs, fromBlock, toBlock, toTs, parts: chunks.length, part: k + 1,
      note: 'One-time rebuild input for scripts/fetch-burn-history.js (archive v2). The next pipeline run swaps these rows in and deletes this file.',
      checks: { rebuiltSum: sumRows, balanceChange: balTo - balBefore, keptSum: sumKept, balanceAtTo: balTo },
      burns: part.map(r => ({ b: r.b, i: r.i, t: r.t, a: r.a, f: r.f }))
    }));
    console.log(`  wrote ${name} (${part.length} burns, ${(fs.statSync(file).size / 1048576).toFixed(1)} MB)`);
  });
  console.log('done');
})().catch(e => { console.error('REBUILD FAILED:', e.message); process.exit(1); });
