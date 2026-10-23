// build-holder-ranks.mjs
// Prebuilds data/holder-ranks.json for the Portfolio page's HOLDER RANK (2026-10-21): every real PTGC and UFO holder's
// balance, sorted, so the page can say "this wallet is #103 of 12,114 PTGC holders" without reading 18,000 holders itself.
//
// Method, per run (full, not incremental — balances move on every transfer and every UFO reflection):
//   1. Page PulseScan's /api/v2/tokens/<token>/holders (50 a page, already sorted by balance, keyset paging).
//      Measured 2026-10-20: UFO 5,324 rows ~95 s, PTGC 18,195 rows ~7 min.
//   2. Leave out what is not a person (Shaka, 2026-10-21 — "people only"): the burn addresses, the token contracts,
//      the DAO treasury wallets + DAO contract, the UFO OA wallet, and EVERY contract PulseScan flags (`is_contract`):
//      LP pools of every DEX, the staking contract (its 3.31B is the reward pool — stakers keep their staked PTGC in
//      their own balance, checked on the eight biggest stakers 2026-10-21), routers, bridges, multisigs.
//   3. Keep EVERY balance above zero (Shaka, 2026-10-21 pm: "dont exclude dust wallets" — the morning's 1-token floor is gone).
//      Stored high → low as whole tokens at 1 token and up, and to 6 decimals below 1 (at least 0.000001) — `pfRankKey` in
//      tools/pf-v2/PfLeagues.jsx rounds a live balance the same way, so equal balances compare equal.
//
// The page ranks a wallet by its LIVE balance: rank = 1 + how many listed balances are strictly above it (ties share a
// rank); "more to pass" = the next balance above − yours. The list itself is up to a run old (gate 2 h).
//
// Honest-failure rules (gotcha 20): a token whose paging fails, or that comes back with fewer rows than 98 % of
// PulseScan's own holder count, keeps the PREVIOUS file's entry for that token (`carried: true`, ::warning:: so the run
// page shows it); both failing → exit 1 and the previous file stays untouched.
//
// 2026-10-22: `top` = the first 110 people with their addresses, [addr, key] high → low — the dashboard's TOP 100 window lists
// them (the rank of any other wallet still comes from `b`).
//
// 2026-10-23 (Audit IV e10 + e9): PulseScan's paging repeats the last row of some pages as the first row of the next (the
// next_page_params balance is a rounded float) — ~126 PTGC / ~44 UFO repeats per read, unique addresses = PulseScan's own count.
// Rows are now de-duplicated by address (they were ranked as extra people, every rank below ~#150 too low). And `t` = the first
// 6 hex characters of every listed address, 6 chars per entry, aligned with `b`, so the page can leave a wallet's OWN (possibly
// stale) entry out before ranking it (tools/pf-v2/PfLeagues.jsx pfRank, tools/top100/t1.jsx).
//
// Node 20+ (global fetch; run locally with NODE_USE_ENV_PROXY=1 behind a proxy). ESM.
import fs from 'node:fs';

const OUT_PATH = process.env.OUT_PATH || 'data/holder-ranks.json';
const API = process.env.PULSESCAN_API || 'https://api.scan.pulsechain.com/api/v2';
const FLOOR = 0;                       // any balance above zero counts (2026-10-21 pm)
const TOP_N = 110;                     // 2026-10-22: the TOP 100 window's list — the first 110 kept rows WITH their addresses (`top`)
const ONE = 10n ** 18n;
const MICRO = 10n ** 12n;              // 1e-6 token in wei
/* whole tokens from 1 up; 6 decimals below 1, never 0 for a holder (must match pfRankKey on the page) */
const key = v => { const w = v / ONE; if (w >= 1n) return Number(w); const m = v / MICRO; return Math.max(1, Number(m)) / 1e6; };
const TOKENS = {
  PTGC: '0x94534eeee131840b1c0f61847c572228bdfdde93',
  UFO:  '0x49ed499433bee42dd34c169470fef2c8f9fae6e6',
};
// Never a holder here, contract or not (the contracts are caught by is_contract as well; the list is for EOAs
// that belong to the project and for safety if PulseScan ever stops flagging a contract).
const EXCLUDE = new Set([
  '0x0000000000000000000000000000000000000369',   // burn
  '0x0000000000000000000000000000000000000000',
  '0x000000000000000000000000000000000000dead',
  '0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1',   // DAO treasury
  '0x440773b5104a102c00ef26979a5c897155336a34',   // DAO wallet 2
  '0x305acfab82103c2b82b19543919d1c93b44e55db',   // PTGC DAO contract
  '0x92dd8e86fdb206fa41e451398a9f03fbd36d574d',   // UFO OA wallet (PF_UFO_EXCL.wallets)
  '0xc71f597a2ac39e47f07102e849d18489c96f39ef',   // PTGC staking
  '0x165c3410fc91ef562c50559f7d2289febed552d9',   // PulseX router
  '0x94534eeee131840b1c0f61847c572228bdfdde93',   // PTGC
  '0x49ed499433bee42dd34c169470fef2c8f9fae6e6',   // UFO
  '0x456548a9b56efbbd89ca0309edd17a9e20b04018',   // UFO v1 (retired)
]);

const sleep = ms => new Promise(r => setTimeout(r, ms));
async function getJson(url) {
  let last;
  for (let k = 0; k < 6; k++) {
    try {
      const r = await fetch(url, { headers: { accept: 'application/json' } });
      if (r.status === 429 || r.status >= 500) throw new Error('HTTP ' + r.status);
      if (!r.ok) throw new Error('HTTP ' + r.status + ' (not retried)');
      return await r.json();
    } catch (e) {
      last = e;
      if (/not retried/.test(e.message)) break;
      await sleep(1500 * (k + 1) + Math.random() * 500);
    }
  }
  throw new Error(`${url.replace(API, '')}: ${last && last.message}`);
}

async function readToken(sym, addr) {
  const t0 = Date.now();
  const counters = await getJson(`${API}/tokens/${addr}/counters`);
  const expected = Number(counters.token_holders_count || 0);
  let params = null, rows = 0;
  const kept = [], top = [], seen = new Set();
  let leftKnown = 0, leftContracts = 0, leftDust = 0, repeats = 0;
  for (;;) {
    const q = params ? '?' + new URLSearchParams(params).toString() : '';
    const j = await getJson(`${API}/tokens/${addr}/holders${q}`);
    for (const it of j.items || []) {
      rows++;
      const a = String(it.address && it.address.hash || '').toLowerCase();
      if (seen.has(a)) { repeats++; continue; }   // e10: a page-boundary repeat, never a second holder
      seen.add(a);
      if (EXCLUDE.has(a)) { leftKnown++; continue; }
      if (it.address && it.address.is_contract) { leftContracts++; continue; }
      const v = BigInt(it.value);
      if (v <= 0n) { leftDust++; continue; }
      kept.push([key(v), a.slice(2, 8)]);   // e9: [balance key, address tag]
      if (top.length < TOP_N) top.push([a, key(v)]);   // PulseScan pages arrive sorted by balance, high → low
    }
    params = j.next_page_params;
    if (!params) break;
    if (rows % 2500 === 0) console.log(`${sym}: ${rows} rows read (${Math.round((Date.now() - t0) / 1000)} s)`);
  }
  if (expected && seen.size < expected * 0.98) throw new Error(`${sym}: read ${seen.size} addresses but PulseScan counts ${expected} holders`);
  kept.sort((x, y) => (y[0] - x[0]) || (x[1] < y[1] ? -1 : x[1] > y[1] ? 1 : 0));
  console.log(`${sym}: ${rows} rows (${repeats} page repeats dropped) in ${Math.round((Date.now() - t0) / 1000)} s → ${kept.length} ranked (left out: ${leftKnown} known, ${leftContracts} contracts, ${leftDust} at zero)`);
  return { holders: kept.length, listed: seen.size, repeats, left: { known: leftKnown, contracts: leftContracts, dust: leftDust }, readAt: new Date().toISOString(), top: top.sort((x, y) => y[1] - x[1] || (x[0] < y[0] ? -1 : 1)), b: kept.map(x => x[0]), t: kept.map(x => x[1]).join('') };
}

let prev = null;
try { prev = JSON.parse(fs.readFileSync(OUT_PATH, 'utf8')); } catch (e) {}
const out = { schema: 1, generatedAt: null, floorTokens: FLOOR, source: 'PulseScan holders, people only', tokens: {} };
let ok = 0;
for (const [sym, addr] of Object.entries(TOKENS)) {
  try { out.tokens[sym] = await readToken(sym, addr); ok++; }
  catch (e) {
    const old = prev && prev.tokens && prev.tokens[sym];
    console.log(`::warning::holder-ranks ${sym} failed (${e.message})${old ? ' — keeping the previous list from ' + old.readAt : ''}`);
    if (old) out.tokens[sym] = { ...old, carried: true };
  }
}
if (!ok) { console.error('holder-ranks: both tokens failed — previous file kept'); process.exit(1); }
if (!out.tokens.PTGC || !out.tokens.UFO) { console.error('holder-ranks: a token is missing and there is no previous list to carry — previous file kept'); process.exit(1); }
out.generatedAt = new Date().toISOString();
const body = JSON.stringify(out);
fs.writeFileSync(OUT_PATH, body);
console.log(`holder-ranks: wrote ${OUT_PATH} (${(body.length / 1024).toFixed(0)} KB)`);
