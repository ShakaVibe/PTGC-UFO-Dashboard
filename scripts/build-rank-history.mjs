// build-rank-history.mjs
// The Portfolio page's HOLDER RANK history (2026-10-21): every real PTGC / UFO holder's rank for every UTC day of the token's
// life, served as small per-wallet files so the rank window opens from one fetch.
//
// Two stores:
//   data/rank-history/<TOKEN>.json          the archive, as CHANGES (schema 2 — a full per-day list would be ~670 MB for PTGC):
//                                           days: { 'YYYY-MM-DD': { b: lastBlock, f: reflectionFactor, m: { addr: balanceKey|0 } } }
//                                           — m lists only the wallets that had a Transfer that day (0 = left), f is the day's
//                                           reflection growth every untouched holder shares (exact: measured on reference wallets
//                                           that did not move). Any day's full list = walk the days forward: carried balance × f,
//                                           then the day's m applied. Seeded by the one-off backfill (design/portfolio/ranks-mock/
//                                           backfill-fast.mjs), EXTENDED here one UTC day at a time by the same walk forwards.
//                                           NOT deployed (deploy.yml ships an allow-list) — only the index below is.
//   data/rank-index/<TOKEN>/<xxx>.json       the index — 4,096 shards by the address's first three hex chars: for every wallet
//                                           that ever held, [firstDayIndex, [rank delta per day]] (a rank of 0 = not holding);
//                                           data/rank-index/<TOKEN>/meta.json = day 0's date, the day count, holders per day.
// Honest-failure rules (gotcha 20): any RPC failure aborts before the archive is written — a half-extended day would be a
// wrong rank forever. The index is rebuilt from the archive every run (deterministic), so it can never disagree with it.
// Node 20+ (global fetch; run locally with NODE_USE_ENV_PROXY=1 behind a proxy). ESM.
import fs from 'node:fs';
import path from 'node:path';

const RPC = process.env.RPC || 'https://rpc.pulsechain.com';
const ARCH_DIR = 'data/rank-history', IDX_DIR = 'data/rank-index';
const TOKENS = {
  PTGC: { a: '0x94534eeee131840b1c0f61847c572228bdfdde93', launch: '2023-10-10' },
  UFO:  { a: '0x49ed499433bee42dd34c169470fef2c8f9fae6e6', launch: '2026-07-08' },
};
// never a holder (= build-holder-ranks.mjs EXCLUDE)
const EXCLUDE = new Set(['0x0000000000000000000000000000000000000369','0x0000000000000000000000000000000000000000','0x000000000000000000000000000000000000dead','0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1','0x440773b5104a102c00ef26979a5c897155336a34','0x305acfab82103c2b82b19543919d1c93b44e55db','0x92dd8e86fdb206fa41e451398a9f03fbd36d574d','0xc71f597a2ac39e47f07102e849d18489c96f39ef','0x165c3410fc91ef562c50559f7d2289febed552d9','0x94534eeee131840b1c0f61847c572228bdfdde93','0x49ed499433bee42dd34c169470fef2c8f9fae6e6','0x456548a9b56efbbd89ca0309edd17a9e20b04018']);
const TOPIC = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const ONE = 10n ** 18n, MICRO = 10n ** 12n;
const key = v => { const w = v / ONE; return w >= 1n ? Number(w) : Math.max(1, Number(v / MICRO)) / 1e6; };
const sleep = ms => new Promise(r => setTimeout(r, ms));
let id = 1;
async function rpc(method, params, tries = 6) {
  for (let k = 0; k < tries; k++) {
    try {
      const r = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: id++, method, params }) });
      const j = await r.json(); if (j.error) throw new Error(JSON.stringify(j.error).slice(0, 120)); return j.result;
    } catch (e) { if (k === tries - 1) throw e; await sleep(800 * (k + 1)); }
  }
}
const tsOf = async b => parseInt((await rpc('eth_getBlockByNumber', ['0x' + b.toString(16), false])).timestamp, 16);
async function blockAt(t, lo, hi) { while (lo < hi) { const m = Math.floor((lo + hi) / 2); if (await tsOf(m) < t) lo = m + 1; else hi = m; } return lo; }
const dayStr = t => new Date(t * 1000).toISOString().slice(0, 10);
const utc0 = d => Math.floor(Date.parse(d + 'T00:00:00Z') / 1000);
const nextDay = d => dayStr(utc0(d) + 86400);
async function getLogs(tok, from, to) {
  try { return await rpc('eth_getLogs', [{ fromBlock: '0x' + from.toString(16), toBlock: '0x' + to.toString(16), address: tok, topics: [TOPIC] }], 2); }
  catch (e) { if (to - from < 200) throw e; const m = Math.floor((from + to) / 2); return [...await getLogs(tok, from, m), ...await getLogs(tok, m + 1, to)]; }
}
async function balances(tok, addrs, block) {
  const out = new Map(), C = 24;
  for (let i = 0; i < addrs.length; i += C) {
    const chunk = addrs.slice(i, i + C);
    const rs = await Promise.all(chunk.map(a => rpc('eth_call', [{ to: tok, data: '0x70a08231' + a.slice(2).padStart(64, '0') }, '0x' + block.toString(16)])));
    chunk.forEach((a, j) => { const h = rs[j]; if (!h || h === '0x') throw new Error('bad balance read ' + a); out.set(a, BigInt(h)); });
  }
  return out;
}

/* walk the archive's deltas forward → Map addr → wei (as of the last recorded day) */
function replay(st, upTo) {
  const cur = new Map(); const days = Object.keys(st.days).sort();
  for (const d of days) { if (upTo && d > upTo) break; const rec = st.days[d]; const f = rec.f || 1;
    if (f !== 1) for (const [a, v] of cur) cur.set(a, scale(v, f));
    for (const [a, k] of Object.entries(rec.m || {})) { if (k > 0) cur.set(a, fromKey(k)); else cur.delete(a); } }
  return cur;
}
const scale = (v, f) => BigInt(Math.round(Number(v / 10n ** 9n) * f)) * 10n ** 9n;
const fromKey = k => k >= 1 ? BigInt(Math.round(k)) * ONE : BigInt(Math.round(k * 1e6)) * MICRO;
async function extend(sym) {
  const T = TOKENS[sym], f = path.join(ARCH_DIR, sym + '.json');
  if (!fs.existsSync(f)) { console.log(`::warning::rank-history ${sym}: no archive yet (${f}) — run the backfill first`); return null; }
  const st = JSON.parse(fs.readFileSync(f, 'utf8'));
  if (st.schema !== 2) throw new Error('archive schema ' + st.schema + ' — expected 2 (deltas)');
  const contracts = new Set(st.contracts || []), eoa = new Set(st.eoa || []);
  const isContract = async a => { if (contracts.has(a)) return true; if (eoa.has(a)) return false; const c = await rpc('eth_getCode', [a, 'latest']); if (c && c !== '0x') { contracts.add(a); return true; } eoa.add(a); return false; };
  const head = parseInt(await rpc('eth_blockNumber', []), 16);
  const days = Object.keys(st.days).sort(); const lastDone = days[days.length - 1];
  const yesterday = dayStr(Math.floor(Date.now() / 1000) - 86400);
  let day = nextDay(lastDone), n = 0, lastB = st.days[lastDone].b;
  const cur = replay(st);
  // the wallets of `cur` are the holders as of lastDone; their exact wei is in st.cur when the backfill wrote it
  if (st.cur) for (const [a, v] of Object.entries(st.cur)) cur.set(a, BigInt(v));
  while (day <= yesterday) {
    const first = await blockAt(utc0(day), lastB, head), last = (await blockAt(utc0(day) + 86400, first, head)) - 1;
    if (last >= head - 3) break;   // the day's last block must be final
    const logs = await getLogs(T.a, first, last);
    const moved = new Set(); for (const l of logs) { moved.add('0x' + l.topics[1].slice(26)); moved.add('0x' + l.topics[2].slice(26)); }
    const todo = []; for (const a of moved) { if (EXCLUDE.has(a)) continue; if (await isContract(a)) continue; todo.push(a); }
    // the day's reflection factor from 6 holders that did not move today (read at both day ends)
    const refs = []; for (const a of cur.keys()) { if (moved.has(a)) continue; refs.push(a); if (refs.length === 6) break; }
    const [bNow, bPrev, bRef] = await Promise.all([balances(T.a, todo, last), balances(T.a, refs, lastB), balances(T.a, refs, last)]);
    let s0 = 0n, s1 = 0n; for (const a of refs) { const v0 = bPrev.get(a), v1 = bRef.get(a); if (v0 > 0n && v1 > 0n) { s0 += v0; s1 += v1; } }
    const fac = s0 > 0n ? Number(s1 * 10n ** 15n / s0) / 1e15 : 1;
    if (fac !== 1) for (const [a, v] of cur) cur.set(a, scale(v, fac));
    const m = {}; for (const [a, v] of bNow) { if (v > 0n) { cur.set(a, v); m[a] = key(v); } else { cur.delete(a); m[a] = 0; } }
    st.days[day] = { b: last, f: fac, m, n: cur.size };
    console.log(`${sym}: ${day} — ${cur.size} holders, ${logs.length} transfers, ${todo.length} moved, factor ${fac}`);
    lastB = last; day = nextDay(day); n++;
  }
  /* Audit IV e33 (2026-10-23): a run that extended nothing writes nothing (it used to re-stamp and rewrite the 19 MB archive and
     ~4,000 index files), and the stamp is the CLOSE of the last archived day, not the run time — with the 24.5 h gate the step
     runs on the first hourly run after 00:15 UTC and extends exactly one day (the run-time stamp drifted 4 h earlier per cycle). */
  if (n === 0) { console.log(`${sym}: archive already current → ${lastDone} — nothing written`); return { unchanged: true }; }
  st.cur = Object.fromEntries([...cur.entries()].map(([a, v]) => [a, v.toString()]));
  st.contracts = [...contracts]; st.eoa = [...eoa]; st.cursorDay = Object.keys(st.days).sort().pop(); st.generatedAt = new Date((utc0(st.cursorDay) + 86400) * 1000).toISOString();
  fs.writeFileSync(f + '.tmp', JSON.stringify(st)); fs.renameSync(f + '.tmp', f);
  console.log(`${sym}: archive ${n ? 'extended by ' + n + ' day(s)' : 'already current'} → ${st.cursorDay}, ${Object.keys(st.days).length} days`);
  return st;
}

function index(sym, st) {
  const days = Object.keys(st.days).sort(), tracks = new Map(), counts = [];
  const cur = new Map();   // addr → balance key (Number) — enough to order; exact wei is not needed for a rank
  days.forEach((d, di) => {
    const rec = st.days[d], f = rec.f || 1;
    if (f !== 1) for (const [a, k] of cur) cur.set(a, k * f);
    for (const [a, k] of Object.entries(rec.m || {})) { if (k > 0) cur.set(a, k); else cur.delete(a); }
    const order = [...cur.entries()].sort((x, y) => (y[1] - x[1]) || (x[0] < y[0] ? -1 : 1));   // order: by balance, then address (reproducible)
    counts.push(order.length);
    /* Audit IV e10 (2026-10-23): ties SHARE a rank, compared on the rounded key the badge uses (whole tokens from 1 up, 6 decimals
       below) — rank = 1 + how many hold strictly more, exactly pfRank / t1Rank. Ties used to be broken by address, so a wallet in a
       tie block sat up to the block's size below the rank the badge shows for the same balance. */
    const rk = k => k >= 1 ? Math.floor(k + 1e-9) : Math.floor(k * 1e6 + 1e-6) / 1e6;
    let prevK = null, prevR = 0;
    order.forEach(([a, k], i) => { const kk = rk(k); const r = kk === prevK ? prevR : i + 1; prevK = kk; prevR = r;
      let t = tracks.get(a); if (!t) tracks.set(a, t = new Map()); t.set(di, r); });
  });
  // per wallet: [firstDayIndex, [delta per day]] — the day-to-day CHANGE of the rank (0 = unchanged; a rank of 0 = not holding
  // is stored as the delta to 0). Ranks shift by a place or two most days, so deltas are tiny numbers and the shard is ~3× smaller
  // than run-lengths (which almost never repeat). 4,096 shards by the address's first three hex chars → ~10 KB each for PTGC.
  const shards = {};
  for (const [a, t] of tracks) {
    const ks = [...t.keys()].sort((x, y) => x - y), ds = []; let prev = 0;
    for (let k = ks[0]; k <= ks[ks.length - 1]; k++) { const r = t.get(k) || 0; ds.push(r - prev); prev = r; }
    (shards[a.slice(2, 5)] = shards[a.slice(2, 5)] || {})[a] = [ks[0], ds];
  }
  const dir = path.join(IDX_DIR, sym); fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
  for (const [xxx, obj] of Object.entries(shards)) fs.writeFileSync(path.join(dir, xxx + '.json'), JSON.stringify(obj));
  fs.writeFileSync(path.join(dir, 'meta.json'), JSON.stringify({ schema: 2, token: sym, day0: days[0], days: days.length, holders: counts, generatedAt: st.generatedAt || new Date().toISOString() }));
  console.log(`${sym}: index — ${tracks.size} wallets over ${days.length} days in ${Object.keys(shards).length} shards`);
}

let ok = 0;
for (const sym of Object.keys(TOKENS)) {
  try { const st = await extend(sym); if (st) { if (!st.unchanged) index(sym, st); ok++; } }   // e33: no index rebuild on a no-op
  catch (e) { console.log(`::warning::rank-history ${sym} failed: ${e.message} — archive and index left as they were`); }
}
if (!ok) { console.error('rank-history: nothing updated'); process.exit(1); }
