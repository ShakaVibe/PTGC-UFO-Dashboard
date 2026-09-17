// scripts/build-token-allocation.mjs
//
// Builds data/token-allocation.json for both tokens: holder tiers (Poseidon/Whale/Shark/
// Dolphin/Squid) + allocation (burned/inLP/staked/held). The dashboard reads this file so the
// Token Allocation "Leagues" render instantly, with no live PulseScan scan per visitor.
//
// Run by the token-allocation step of .github/workflows/data-pipeline.yml every 6 h (file age).
// Node 20+ (global fetch).
//
// a33 (2026-09-17): a read that fails is UNKNOWN, never 0 — rpc() returns null, balanceOf /
// getPair / holderCount throw or return null, and a token whose reads did not all succeed keeps
// its previous tiers AND allocation from the file (with `updatedAt` left at the old stamp).
// Before: rpc() answered '0x0' after four failures, so a dead RPC produced burned 0 / inLP 0, a
// getPair miss left the PTGC/WPLS pool out of the exclusion list (its balance then counted as a
// Whale), and a PulseScan /counters miss published "SquidAndBelow: 0" as an exact count. The
// staking contract (0xC71f…) is PTGC's — it was listed under UFO, which counted it as a Shark
// for UFO and reported PTGC staked 0%.
//
// ⚠ THE ONE THING THAT WILL BREAK IF YOU TOUCH IT: PulseScan returns each holder's `value`
// (balance in wei) as a STRING, but the pagination cursor `next_page_params.value` as a raw
// JSON NUMBER larger than 2^53. JSON.parse silently rounds it to a float and corrupts the
// digits, and PulseScan then 500s on every page after the first. So the cursor MUST be built
// from the last holder's string `value` — see scanTiers(). This is the exact bug that made the
// live scan flaky; don't reintroduce it.

import fs from 'node:fs';

const RPC  = 'https://rpc.pulsechain.com';
const SCAN = 'https://api.scan.pulsechain.com/api/v2';
const OUT  = 'data/token-allocation.json';
const DIV  = 10n ** 18n;                                   // all tokens are 18 decimals
const BURN = '0x0000000000000000000000000000000000000369';
const FACTORY = '0x29eA7545DEf87022BAdc76323F373EA1e707C523'; // PulseX V2

// RH-core token addresses; the token's LP pools are getPair(token, core) on the V2 factory.
// EHEX in particular is a real UFO pool that DexScreener does NOT index.
const CORES = [
  '0xA1077a294dDE1B09bB078844df40758a5D0f9a27', // WPLS
  '0x95B303987A60C71504D99Aa1b13B4DA07b0790ab', // PLSX
  '0x2fa878ab3f87cc1c9737fc071108f904c0b0c95d', // INC
  '0x2b591e99afe9f32eaa6214f7b7629768c40eeb39', // HEX
  '0x57fde0a71132198bbec939b98976993d8d89d225', // EHEX
  '0xF6f8Db0aBa00007681F8fAF16A0FDa1c9B030b11', // PRVX
  '0x02DcdD04e3F455D838cd1249292C58f3B79e3C3C', // WETH
];

const TOKENS = {
  PTGC: { address: '0x94534EeEe131840b1c0F61847c572228bdfDDE93', supply: 333333333333n,
          staking: '0xC71f597a2AC39E47F07102E849d18489C96f39EF' },   // = TOKENS.PTGC.stakingContract in index.html (a33: was under UFO)
  UFO:  { address: '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6', supply: 999999999051n, staking: null },
};

const sleep = ms => new Promise(r => setTimeout(r, ms));
const pad   = a  => a.replace(/^0x/, '').toLowerCase().padStart(64, '0');

async function rpc(to, data) {
  const body = { jsonrpc: '2.0', method: 'eth_call', params: [{ to, data }, 'latest'], id: 1 };
  for (let a = 0; a < 4; a++) {
    try {
      const r = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });
      const j = await r.json();
      if (j && typeof j.result === 'string' && j.result.startsWith('0x')) return j.result;
    } catch {}
    await sleep(500 * (a + 1));
  }
  return null;   // a33: unknown — callers throw, never read this as 0
}

class ReadFailed extends Error {}

async function balanceOf(token, holder) {
  const r = await rpc(token, '0x70a08231' + pad(holder));
  if (r == null) throw new ReadFailed(`balanceOf(${holder}) on ${token} failed`);
  return BigInt(r === '0x' ? '0x0' : r);
}

async function getPair(a, b) {
  const r = await rpc(FACTORY, '0xe6a43905' + pad(a) + pad(b)); // getPair(address,address)
  if (r == null || r.length < 66) throw new ReadFailed(`getPair(${a}, ${b}) failed`);   // a33: a miss must not silently drop a pool from the exclusion list
  const p = '0x' + r.slice(-40);
  return p === '0x' + '0'.repeat(40) ? null : p.toLowerCase();
}

async function getJson(url, tries = 6) {
  for (let a = 0; a < tries; a++) {
    try {
      const r = await fetch(url);
      if (r.status >= 500) { await sleep(600 * (a + 1)); continue; }
      if (!r.ok) return null;
      return await r.json();
    } catch { await sleep(600 * (a + 1)); }
  }
  return null;
}

async function holderCount(address) {
  const j = await getJson(`${SCAN}/tokens/${address}/counters`);
  const n = j && parseInt(j.token_holders_count);
  return Number.isFinite(n) && n > 0 ? n : null;   // a33: null = unknown, never 0
}

// Page all holders, classify by % of supply, stop once we drop below Dolphin (list is desc).
async function scanTiers(address, supply, exclude) {
  const counts = { Poseidon: 0, Whale: 0, Shark: 0, Dolphin: 0 };
  const supplyWei = supply * DIV;
  let counted = 0, cursor = null, complete = false;
  for (let page = 0; page < 40; page++) {
    const qs = cursor ? new URLSearchParams(cursor).toString() : 'limit=50';
    const d = await getJson(`${SCAN}/tokens/${address}/holders?${qs}`);
    if (!d || !Array.isArray(d.items) || d.items.length === 0) break;
    let below = false;
    for (const h of d.items) {
      const addr = (h.address?.hash || '').toLowerCase();
      if (exclude.has(addr)) continue;
      const pct = Number(BigInt(h.value)) / Number(supplyWei) * 100;
      if (pct < 0.01) { below = true; break; }
      if (pct >= 10) counts.Poseidon++;
      else if (pct >= 1) counts.Whale++;
      else if (pct >= 0.1) counts.Shark++;
      else counts.Dolphin++;
      counted++;
    }
    if (below) { complete = true; break; }
    if (!d.next_page_params) { complete = true; break; }
    // *** cursor from the last holder's STRING value — never next_page_params.value ***
    cursor = { ...d.next_page_params, value: String(d.items[d.items.length - 1].value) };
  }
  return { counts, counted, complete };
}

async function buildToken(sym, cfg) {
  const supplyWei = cfg.supply * DIV;
  const pct   = w => Number((w * 10000n) / supplyWei) / 100;
  const toTok = w => Number(w * 100n / DIV) / 100;

  // Discover the token's LP pools on the V2 factory (token/core + the cross PTGC<->UFO pool).
  const others = [...CORES, sym === 'PTGC' ? TOKENS.UFO.address : TOKENS.PTGC.address];
  const pools = new Set();
  for (const o of others) { const p = await getPair(cfg.address, o); if (p) pools.add(p); }

  // Allocation (all on-chain). staked = UFO actually held by the staking contract (0 if none).
  const burned = await balanceOf(cfg.address, BURN);
  let inLP = 0n;
  for (const p of pools) inLP += await balanceOf(cfg.address, p);
  const staked = cfg.staking ? await balanceOf(cfg.address, cfg.staking) : 0n;
  let held = supplyWei - burned - inLP - staked;
  if (held < 0n) held = 0n;

  // Tiers. Exclude LP pools + staking; do NOT exclude the burn address (matches the app).
  const exclude = new Set(pools);
  if (cfg.staking) exclude.add(cfg.staking.toLowerCase());
  const total = await holderCount(cfg.address);
  const { counts, counted, complete } = await scanTiers(cfg.address, cfg.supply, exclude);
  const excludedCount = pools.size + (cfg.staking ? 1 : 0);
  // a33: no holder count → SquidAndBelow is unknown (null; the dashboard prints "—"), and the
  // caller keeps the previous file's tiers instead when it has them.
  const squid = total == null ? null : Math.max(0, total - counted - excludedCount);

  return {
    complete: complete && total != null,
    tiers: complete ? { ...counts, SquidAndBelow: squid } : null,
    allocation: {
      burned: { amount: toTok(burned), pct: pct(burned) },
      inLP:   { amount: toTok(inLP),   pct: pct(inLP) },
      staked: { amount: toTok(staked), pct: pct(staked) },
      held:   { amount: toTok(held),   pct: pct(held) },
    },
  };
}

async function main() {
  // Keep the previous file's tiers if a scan can't complete this run (never publish a "≥" bound).
  let prev = {};
  try { prev = JSON.parse(fs.readFileSync(OUT, 'utf8')); } catch {}

  const now = new Date().toISOString();
  const out = { lastUpdated: prev.lastUpdated || now, tokens: {} };
  let refreshed = 0, failed = 0;
  for (const [sym, cfg] of Object.entries(TOKENS)) {
    const old = prev.tokens?.[sym] || {};
    let r;
    try { r = await buildToken(sym, cfg); }
    catch (e) {
      // a33: an RPC / explorer read failed → this token keeps its previous entry, stamp and all.
      failed++;
      console.error(`${sym}: read failed — keeping the previous entry (${old.updatedAt || 'none'}): ${e.message}`);
      out.tokens[sym] = { ...old, tiers: old.tiers ?? null, allocation: old.allocation ?? null, updatedAt: old.updatedAt ?? null };
      continue;
    }
    const tiersOk = r.complete && r.tiers;
    out.tokens[sym] = {
      tiers: tiersOk ? r.tiers : (old.tiers ?? (r.tiers || null)),   // an incomplete scan keeps the previous exact tiers; a squid-less scan only if there is nothing older
      allocation: r.allocation,
      updatedAt: now,
      tiersUpdatedAt: tiersOk ? now : (old.tiersUpdatedAt ?? old.updatedAt ?? null),
    };
    refreshed++;
    console.log(`${sym}: tiers ${tiersOk ? 'exact' : 'incomplete (kept previous)'}`, out.tokens[sym].tiers,
                '| alloc', Object.fromEntries(Object.entries(out.tokens[sym].allocation).map(([k, v]) => [k, v.pct + '%'])));
  }
  // lastUpdated drives the pipeline's 6-h age gate: only advance it when BOTH tokens refreshed, so a
  // half-failed run is retried next hour rather than in six (the good token is re-scanned too — cheap).
  if (refreshed && !failed) out.lastUpdated = now;

  if (!refreshed) {
    // Nothing new to say — leave the file exactly as it was (the pipeline's age gate will retry next hour).
    console.error('Both tokens failed — file left untouched');
    process.exit(1);
  }
  fs.mkdirSync('data', { recursive: true });
  fs.writeFileSync(OUT, JSON.stringify(out, null, 2));
  console.log('wrote', OUT, failed ? `(${failed} token kept from the previous run)` : '');
  if (failed) process.exit(1);   // the pipeline's report step goes red; the good token still landed
}

main().catch(e => { console.error(e); process.exit(1); });
