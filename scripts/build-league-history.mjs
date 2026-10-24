// build-league-history.mjs — data/league-history.json for the LEAGUE HISTORY window (2026-10-24, design/creatures/README.md):
// how many of each sea creature (the eight leagues) held PTGC / UFO on every UTC day since launch.
//
// Source: data/rank-history/<TOKEN>.json — the rank window's archive (build-rank-history.mjs): every PEOPLE holder's balance for
// every UTC day (contracts, pools, burn, token contracts, DAO / UFO OA wallets left out — the same population as the Token
// Allocation strip since Audit IV e13). Walking its days forward gives each day's league counts on two bases:
//   start = % of the STARTING supply (the strip's basis)        circ = % of that day's CIRCULATING supply (starting − burned)
// "burned" for a day = balanceOf(0x…369) at the day's last block (the archive's `b`) — one archive read per NEW day, cached in
// this file's `burned` array, so a normal run makes 1 call per token.
// Joined / left per league for 7D / 30D / 90D / 6M / 1Y / ALL: a wallet's league on the period's first day vs the last day
// (joined − left = the change; ALL compares with day 0).
// Runs in the holder-ranks lane after rank-history; writes only when the archive has a day this file has not (or the file is
// missing / another schema). Honest failures (gotcha 20): any failed burn read aborts the write (the old file stays).
// Node 22 (ESM; the RPC goes through scripts/rpc-pool.js).
import fs from 'node:fs';
import path from 'node:path';
import rpcPool from './rpc-pool.js';

const OUT = process.env.OUT_PATH || 'data/league-history.json';
const ARCH = 'data/rank-history';
const SCHEMA = 4;   // 2 (2026-10-24): the burn wallet counts in its league (`burnIn`); 3: + `held` — the tokens each league holds per day;
                    // 4 (lh7): start / circ / held DELTA-encoded per day (row 0 whole), held in units of HELD_UNIT tokens, burned in whole tokens
const HELD_UNIT = 1e4;   // 10,000 tokens — the window prints 2 decimals of M / B, so nothing it shows changes
const delta = rows => rows.map((r, k) => k ? r.map((v, i) => v - rows[k - 1][i]) : r.slice());
const TIERS = [['Poseidon', 10], ['Whale', 1], ['Shark', 0.1], ['Dolphin', 0.01], ['Squid', 0.001], ['Turtle', 0.0001], ['Shrimp', 0.00001], ['Shell', 0]];
const TOKENS = {   // starting supply = token-allocation.json's (the strip's) — whole tokens
  PTGC: { a: '0x94534eeee131840b1c0f61847c572228bdfdde93', supply: 333333333333 },
  UFO:  { a: '0x49ed499433bee42dd34c169470fef2c8f9fae6e6', supply: 999999999051 },
};
const PERIODS = [['7D', 7], ['30D', 30], ['90D', 90], ['6M', 182], ['1Y', 365], ['ALL', null]];
const BURN = '0x0000000000000000000000000000000000000369';
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function rpc(method, params, tries = 5) {
  let last;
  for (let k = 0; k < tries; k++) {
    try {
      const r = await rpcPool.poolFetch({ attemptMs: 30000, method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }) });
      const j = await r.json(); if (j.error) throw new Error(JSON.stringify(j.error).slice(0, 140)); return j.result;
    } catch (e) { last = e; await sleep(700 * (k + 1)); }
  }
  throw last;
}
const burnedAt = async (tok, block) => {
  const h = await rpc('eth_call', [{ to: TOKENS[tok].a, data: '0x70a08231' + BURN.slice(2).padStart(64, '0') }, '0x' + block.toString(16)]);
  if (h === '0x') {   // the token not deployed yet at that block (PTGC's day 0 closes before its creation) → nothing burned
    const code = await rpc('eth_getCode', [TOKENS[tok].a, '0x' + block.toString(16)]);
    if (code === '0x') return 0;
  }
  if (!h || h === '0x') throw new Error(`no burn balance for ${tok} at block ${block}`);
  return Number(BigInt(h) / 10n ** 12n) / 1e6;   // whole tokens, 6 decimals
};
const pmap = async (items, fn, n = 8) => { const out = new Array(items.length); let i = 0;
  await Promise.all(Array.from({ length: Math.min(n, items.length) }, async () => { while (i < items.length) { const k = i++; out[k] = await fn(items[k], k); } })); return out; };
const tierOf = (v, sup) => { const p = v / sup * 100; for (let i = 0; i < 7; i++) if (p >= TIERS[i][1]) return i; return 7; };
const nextDay = d => new Date(Date.parse(d + 'T00:00:00Z') + 86400e3).toISOString().slice(0, 10);

async function build(tok, prev) {
  const f = path.join(ARCH, tok + '.json');
  if (!fs.existsSync(f)) { console.log(`::warning::league-history ${tok}: no archive ${f}`); return prev || null; }
  const st = JSON.parse(fs.readFileSync(f, 'utf8'));
  if (st.schema !== 2) throw new Error(`${tok}: archive schema ${st.schema} — expected 2`);
  const days = Object.keys(st.days).sort();
  for (let k = 1; k < days.length; k++) if (nextDay(days[k - 1]) !== days[k]) throw new Error(`${tok}: archive skips from ${days[k - 1]} to ${days[k]}`);
  const lastDay = days[days.length - 1];
  if (prev && prevFile.schema === SCHEMA && prev.archiveDay0 === days[0] && prev.lastDay === lastDay && !process.env.FORCE_LH) { console.log(`${tok}: already current → ${lastDay} — nothing to do`); return prev; }
  const S = TOKENS[tok].supply;
  // the burned line: reuse every day the previous file already read (same day0), read the rest at the day's last block
  const burned = new Array(days.length).fill(null);
  if (prev && prev.archiveDay0 === days[0] && Array.isArray(prev.burned)) prev.burned.forEach((v, k) => { if (k < burned.length && v != null) burned[k] = v; });
  const todo = days.map((d, k) => k).filter(k => burned[k] == null);
  console.log(`${tok}: ${days.length} days ${days[0]} → ${lastDay}; ${todo.length} burn reading(s) to take`);
  await pmap(todo, async k => { burned[k] = await burnedAt(tok, st.days[days[k]].b); });
  // the archive's day 0 closes before anyone held (PTGC 2023-10-10, UFO 2026-07-08): the history starts on the first day with
  // a holder, so "since launch" does not draw every league up from 0
  let k0 = 0;
  { const c = new Map(); for (let k = 0; k < days.length; k++) { const rec = st.days[days[k]]; for (const [a, v] of Object.entries(rec.m || {})) { if (v > 0) c.set(a, v); else c.delete(a); } if (c.size) { k0 = k; break; } } }
  // which days start a period (the period's first day = the last day − n, never before k0)
  const need = new Map(), span = days.length - k0;
  for (const [lab, n] of PERIODS) { const k = n == null || n >= span ? k0 : days.length - 1 - n; need.set(k, [...(need.get(k) || []), lab]); }
  const cur = new Map(), start = [], circ = [], hS = [], hC = [], snaps = new Map();
  days.forEach((d, k) => {
    const rec = st.days[d], fct = rec.f || 1;
    if (fct !== 1) for (const [a, v] of cur) cur.set(a, v * fct);
    for (const [a, v] of Object.entries(rec.m || {})) { if (v > 0) cur.set(a, v); else cur.delete(a); }
    const cs = S - burned[k], s8 = new Array(8).fill(0), c8 = new Array(8).fill(0), h8 = new Array(8).fill(0), g8 = new Array(8).fill(0);
    for (const v of cur.values()) { const a = tierOf(v, S), b = tierOf(v, cs); s8[a]++; c8[b]++; h8[a] += v; g8[b] += v; }
    if (burned[k] > 0) { const a = tierOf(burned[k], S), b = tierOf(burned[k], cs); s8[a]++; c8[b]++; h8[a] += burned[k]; g8[b] += burned[k]; }   // 2026-10-24 (Shaka): the burn wallet counts, in its league
    start.push(s8); circ.push(c8); hS.push(h8.map(Math.round)); hC.push(g8.map(Math.round));   // held: whole tokens (Shaka: "how many tokens do those 107 wallets hold")
    if (need.has(k) || k === days.length - 1) {
      const a = new Map(), b = new Map();
      for (const [w, v] of cur) { a.set(w, tierOf(v, S)); b.set(w, tierOf(v, cs)); }
      if (burned[k] > 0) { a.set('burn', tierOf(burned[k], S)); b.set('burn', tierOf(burned[k], cs)); }
      snaps.set(k, [a, b]);
    }
  });
  const [endS, endC] = snaps.get(days.length - 1), flows = {};
  const move = (m0, m1) => {
    const j = new Array(8).fill(0), l = new Array(8).fill(0);
    for (const w of new Set([...m0.keys(), ...m1.keys()])) { const t0 = m0.get(w), t1 = m1.get(w); if (t0 === t1) continue; if (t1 != null) j[t1]++; if (t0 != null) l[t0]++; }
    return [j, l];
  };
  for (const [k, labs] of need) for (const lab of labs) {
    const [s0, c0] = snaps.get(k);   // the period's first day (ALL = day 0), so joined − left = the change shown
    flows[lab] = { from: days[k], start: move(s0, endS), circ: move(c0, endC) };
  }
  const last = start[start.length - 1];
  console.log(`${tok}: ${lastDay} start ${last.join(' / ')} · circ ${circ[circ.length - 1].join(' / ')} · circulating ${Math.round(S - burned[burned.length - 1]).toLocaleString('en-US')}`);
  const bl = burned[burned.length - 1], burnIn = bl > 0 ? { start: tierOf(bl, S), circ: tierOf(bl, S - bl) } : null;   // the burn wallet's league today
  return { day0: days[k0], lastDay, days: days.length - k0, supply: S, start: delta(start.slice(k0)), circ: delta(circ.slice(k0)),
    held: { start: delta(hS.slice(k0).map(r => r.map(v => Math.round(v / HELD_UNIT)))), circ: delta(hC.slice(k0).map(r => r.map(v => Math.round(v / HELD_UNIT)))) }, flows, burnIn,
    archiveDay0: days[0], burned: burned.map(v => v == null ? null : Math.round(v)) };   // `burned` = per ARCHIVE day (the cache for the next run)
}

const prevFile = (() => { try { const j = JSON.parse(fs.readFileSync(OUT, 'utf8')); return j && j.schema >= 2 ? j : null; } catch (e) {   // any schema ≥ 2: its burn readings are reused (a schema change rebuilds the rest)
  if (fs.existsSync(OUT)) { console.error(`::error::league-history: ${OUT} exists but is unreadable — not rebuilding over it (${e.message})`); process.exit(1); }
  return null; } })();
const out = { schema: SCHEMA, generatedAt: null, enc: { rows: 'delta', heldUnit: HELD_UNIT }, tiers: TIERS.map(t => t[0]), thresholds: TIERS.map(t => t[1]),
  note: 'people only plus the burn wallet (the Token Allocation strip population); start = % of the starting supply, circ = % of the circulating supply that day (starting − balanceOf(0x369) at the day\'s last block); one row per UTC day from day0', tokens: {} };
let changed = false;
for (const tok of Object.keys(TOKENS)) {
  const prev = prevFile && prevFile.tokens && prevFile.tokens[tok];
  const t = await build(tok, prev);
  if (t) out.tokens[tok] = t;
  if (t && t !== prev) changed = true;
}
if (!changed) { console.log('league-history: nothing new — file left as it was'); process.exit(0); }
out.generatedAt = new Date().toISOString();
fs.writeFileSync(OUT + '.tmp', JSON.stringify(out)); fs.renameSync(OUT + '.tmp', OUT);
console.log(`wrote ${OUT} (${(fs.statSync(OUT).size / 1024).toFixed(0)} KB)`);
