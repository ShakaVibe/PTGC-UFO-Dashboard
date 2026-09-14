// build-dao-buys.mjs
// Prebuilds data/dao-buys.json for the PTGC dashboard's "DAO Buys" chart: every PTGC buy the
// DAO treasury wallets have ever made, priced in PLS and USD at the block it happened, plus a
// PTGC/USD price line (daily from 30 days before the first buy, hourly for the last 90 days) so
// the chart opens instantly with no third-party API calls in the browser.
//
// Inputs (written by scripts/fetch-treasury-transactions.js, same workflow, earlier step), one
// pair per wallet in WALLETS below:
//   data/treasury-wallet1-txns.json    normal transactions of wallet 1 (0xeeac…31e1, TOKENS.PTGC.daoTreasury)
//   data/treasury-wallet1-tokens.json  ERC-20 transfers touching wallet 1
//   data/treasury-wallet2-txns.json    the same for wallet 2 (0x4407…6A34 — bought PTGC Oct 2023 → May 2025;
//   data/treasury-wallet2-tokens.json  added 2026-09-14 when Shaka found it)
// Every buy carries `wallet`, so the chart can tell them apart if it ever needs to.
//
// What counts as a buy: a transaction SENT BY the wallet, that succeeded, that paid native PLS
// (value > 0) and in which PTGC was transferred TO the wallet. That is the router swap path
// (PLS -> WPLS -> PTGC). `removeLiquidityETH…` calls also deliver PTGC to the wallet but pay no
// PLS, so they fall out on value > 0 — they are LP withdrawals, not buys, and are counted in
// `excluded.lpRemovals` so the number is visible. PLS the router refunds inside the same
// transaction (internal_transactions back to the wallet) is subtracted from the amount spent.
//
// Pricing is on-chain only (no GeckoTerminal/DexScreener — neither is reachable from every
// environment this runs in, and this way the numbers are reproducible):
//   PLS/USD  = WPLS/DAI V1 pair reserves (ADDR.PAIR_WPLS_DAI on the site)   at the block
//   PTGC/USD = PTGC/WPLS main pair reserves x PLS/USD                        at the block
// Buys are priced at their own block; every buy that has been priced once keeps its numbers
// forever (cached by tx hash in the previous output), so an hourly run prices only new buys.
// The price line is sampled on a fixed block grid (DAILY_STRIDE / HOURLY_STRIDE blocks) with
// the real block timestamp on each point; the grid is anchored on the first run and extended
// forward on every run, so a run normally adds ~1 hourly point and ~0-1 daily points.
//
// Guards: writes ONLY when every buy has a price. A price-line failure keeps the previous
// line (carry forward) and still writes the buys. The public RPC answers ~30 concurrent
// single calls in ~0.5 s but processes a JSON-RPC *batch* serially (~1 s/item) — so this
// script fans out single calls with CONCURRENCY and never batches.
//
// Node 20+ (global fetch). ESM so it runs regardless of repo package.json.
import fs from 'node:fs';

const OUT_PATH = process.env.OUT_PATH || 'data/dao-buys.json';
const RPC = process.env.RPC || 'https://rpc.pulsechain.com';

// Same addresses as ADDR in index.html — keep in sync if the main pair ever changes.
// The wallets mirror WALLET1/WALLET2 in fetch-treasury-transactions.js and ADDR.DAO_TREASURY /
// ADDR.DAO_WALLET2 in index.html (fetchFreshDaoBuys scans the same set).
const WALLETS = [
  { addr: '0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1', txns: 'data/treasury-wallet1-txns.json', tokens: 'data/treasury-wallet1-tokens.json' },
  { addr: '0x440773b5104a102c00ef26979a5c897155336a34', txns: 'data/treasury-wallet2-txns.json', tokens: 'data/treasury-wallet2-tokens.json' },
];
const PTGC = '0x94534eeee131840b1c0f61847c572228bdfdde93';
const PAIR_PTGC_WPLS = '0xf5a89a6487d62df5308cdda89c566c5b5ef94c11'; // token0 = PTGC, token1 = WPLS (checked on chain)
const PAIR_WPLS_DAI = '0xe56043671df55de5cdf8459710433c10324de0ae';  // token0 = WPLS, token1 = DAI (checked on chain)
const LP_REMOVAL_SELECTORS = new Set(['0x2195995c', '0x02751cec', '0xded9382a', '0x5b0d5984', '0xaf2979eb']); // removeLiquidityETH* family

const DAILY_STRIDE = 8640;     // ~1 day at PulseChain's ~10 s blocks
const HOURLY_STRIDE = 360;     // ~1 hour
const HOURLY_KEEP_DAYS = 92;   // the chart's 90-day range plus margin
const LIFETIME_LEAD_DAYS = 30; // price line starts this long before the first buy
const CONCURRENCY = 24;

const SCHEMA = 2;   // 2 = multi-wallet (`wallets`, per-buy `wallet`)
const GET_RESERVES = '0x0902f1ac';

// ---------------------------------------------------------------- RPC helpers
const rpc = async (method, params, tries = 4) => {
  let lastErr;
  for (let i = 0; i < tries; i++) {
    try {
      const ctl = new AbortController();
      const t = setTimeout(() => ctl.abort(), 20000);
      const res = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ jsonrpc: '2.0', id: 1, method, params }), signal: ctl.signal });
      clearTimeout(t);
      if (res.status === 429 || res.status >= 500) throw new Error('HTTP ' + res.status);
      const j = await res.json();
      if (j.error) throw new Error(j.error.message || JSON.stringify(j.error));
      return j.result;
    } catch (e) {
      lastErr = e;
      await new Promise(r => setTimeout(r, 400 * (i + 1) + Math.random() * 300));
    }
  }
  throw lastErr;
};
const hexBlock = n => '0x' + Number(n).toString(16);
const word = (hex, i) => BigInt('0x' + hex.slice(2 + i * 64, 2 + (i + 1) * 64));

/** Reserves of a V2 pair at a block → [reserve0, reserve1] as BigInt. */
const reservesAt = async (pair, block) => {
  const r = await rpc('eth_call', [{ to: pair, data: GET_RESERVES }, hexBlock(block)]);
  if (!r || r === '0x' || r.length < 2 + 64 * 2) throw new Error(`empty reserves for ${pair} @ ${block}`);
  return [word(r, 0), word(r, 1)];
};
/** PLS/USD and PTGC/USD at a block, from the two pairs. Both 18-decimal tokens. */
const pricesAt = async (block) => {
  const [[wplsInDai, dai], [ptgcRes, wplsRes]] = await Promise.all([
    reservesAt(PAIR_WPLS_DAI, block), reservesAt(PAIR_PTGC_WPLS, block)]);
  if (wplsInDai === 0n || ptgcRes === 0n) throw new Error(`zero reserve @ ${block}`);
  const plsUsd = Number(dai) / Number(wplsInDai);
  const ptgcPls = Number(wplsRes) / Number(ptgcRes);
  return { plsUsd, ptgcUsd: ptgcPls * plsUsd };
};
const blockTs = async (block) => {
  const b = await rpc('eth_getBlockByNumber', [hexBlock(block), false]);
  if (!b || !b.timestamp) throw new Error(`no block ${block}`);
  return parseInt(b.timestamp, 16);
};

/** Run `fn` over `items` with bounded concurrency; results in order; throws on first error. */
const pmap = async (items, fn, limit = CONCURRENCY) => {
  const out = new Array(items.length); let next = 0;
  const worker = async () => { while (next < items.length) { const i = next++; out[i] = await fn(items[i], i); } };
  await Promise.all(Array.from({ length: Math.min(limit, items.length) }, worker));
  return out;
};

// ---------------------------------------------------------------- buys (pure)
const lc = s => (s || '').toLowerCase();
export function deriveBuys(txns, transfers, wallet) {
  const WALLET = lc(wallet);
  const byHash = new Map();
  for (const t of transfers) {
    if (lc(t.contractAddress) !== PTGC) continue;
    const e = byHash.get(t.hash) || { inn: 0n, out: 0n };
    if (lc(t.to) === WALLET) e.inn += BigInt(t.value);
    if (lc(t.from) === WALLET) e.out += BigInt(t.value);
    byHash.set(t.hash, e);
  }
  const buys = []; let lpRemovals = 0, noPlsPaid = 0;
  for (const tx of txns) {
    if (lc(tx.from) !== WALLET) continue;
    if (tx.isError === '1' || tx.txreceipt_status === '0') continue;
    const flow = byHash.get(tx.hash);
    if (!flow || flow.inn === 0n) continue;
    const sel = (tx.input || '').slice(0, 10);
    if (LP_REMOVAL_SELECTORS.has(sel)) { lpRemovals++; continue; }
    // PTGC arrived but no PLS left the wallet: a token-for-token route or another LP path.
    // Not priceable as a PLS buy; counted so a change here is visible in the file.
    if (tx.value === '0') { noPlsPaid++; continue; }
    let refund = 0n;
    for (const it of (tx.internal_transactions || [])) {
      if (lc(it.to) === WALLET && it.value && it.value !== '0' && !it.error) refund += BigInt(it.value);
    }
    const plsWei = BigInt(tx.value) - refund;
    buys.push({
      hash: tx.hash,
      block: Number(tx.block_number),
      ts: Number(tx.timeStamp),
      ptgc: Number(flow.inn) / 1e18,
      pls: Number(plsWei) / 1e18,
      router: lc(tx.to),
      wallet: WALLET
    });
  }
  buys.sort((a, b) => a.ts - b.ts || a.block - b.block);
  return { buys, lpRemovals, noPlsPaid };
}

// ---------------------------------------------------------------- main
const readJson = (p, fallback) => { try { return JSON.parse(fs.readFileSync(p, 'utf8')); } catch { return fallback; } };
const round = (x, d) => Number(x.toPrecision(d));

async function main() {
  const t0 = Date.now();
  const prev = readJson(OUT_PATH, null);
  const prevBuys = new Map(((prev && prev.buys) || []).map(b => [b.hash, b]));

  const buys = []; let lpRemovals = 0, noPlsPaid = 0; const source = {};
  for (const w of WALLETS) {
    const txnsFile = readJson(w.txns, null), tokensFile = readJson(w.tokens, null);
    if (!txnsFile || !tokensFile) { console.error(`missing treasury input files for ${w.addr}`); process.exit(1); }
    if (lc(txnsFile.wallet) !== w.addr || lc(tokensFile.wallet) !== w.addr) { console.error(`treasury files for ${w.addr} are for ${txnsFile.wallet} / ${tokensFile.wallet}`); process.exit(1); }
    const d = deriveBuys(txnsFile.transactions || [], tokensFile.transfers || [], w.addr);
    console.log(`${w.addr.slice(0, 6)}…${w.addr.slice(-4)}: ${d.buys.length} buys (excluded: ${d.lpRemovals} LP removals, ${d.noPlsPaid} with no PLS paid)`);
    buys.push(...d.buys); lpRemovals += d.lpRemovals; noPlsPaid += d.noPlsPaid;
    source[w.addr] = { txns: txnsFile.lastUpdated, tokens: tokensFile.lastUpdated };
  }
  buys.sort((a, b) => a.ts - b.ts || a.block - b.block);
  console.log(`buys: ${buys.length} across ${WALLETS.length} wallets (cached ${[...prevBuys.keys()].length})`);

  // ---- price each buy at its own block (cached by hash)
  const toPrice = buys.filter(b => {
    const p = prevBuys.get(b.hash);
    const same = (x, y) => Math.abs(x - y) <= 1e-8 * Math.max(Math.abs(x), Math.abs(y), 1); // stored values are rounded to 10 sig figs
    return !(p && p.plsUsd > 0 && same(p.pls, b.pls) && same(p.ptgc, b.ptgc));
  });
  console.log(`pricing ${toPrice.length} new buys…`);
  await pmap(toPrice, async (b) => { const p = await pricesAt(b.block); b.plsUsd = p.plsUsd; b.marketUsd = p.ptgcUsd; });
  for (const b of buys) {
    const p = prevBuys.get(b.hash);
    if (b.plsUsd == null && p) { b.plsUsd = p.plsUsd; b.marketUsd = p.marketUsd; }
    if (!(b.plsUsd > 0)) { console.error(`buy ${b.hash} has no price — aborting write`); process.exit(1); }
    b.usd = b.pls * b.plsUsd;
    b.price = b.ptgc > 0 ? b.usd / b.ptgc : 0;       // effective USD per PTGC (after fee + slippage)
  }

  // ---- price line on a fixed block grid, extended from the previous file
  const head = parseInt(await rpc('eth_blockNumber', []), 16);
  const headTs = await blockTs(head);
  const price = { daily: [], hourly: [], latest: null };
  const prevPrice = (prev && prev.price) || {};
  try {
    const sample = async (blocks, stride) => {
      if (blocks.length) console.log(`  +${blocks.length} points (stride ${stride})`);
      const fresh = await pmap(blocks, async (b) => {
        const ts = await blockTs(b);
        let p; try { p = await pricesAt(b); } catch (e) { return null; }   // pair not deployed yet / empty → no point
        return [b, ts, round(p.ptgcUsd, 6), round(p.plsUsd, 6)];
      });
      return fresh.filter(Boolean);
    };
    const extend = async (series, stride, startBlock) => {
      const pts = Array.isArray(series) ? series.slice() : [];
      // forward: from the last point (or the start) to the head
      let from = pts.length ? pts[pts.length - 1][0] + stride : startBlock;
      const fwd = []; for (let b = from; b <= head; b += stride) fwd.push(b);
      // backward: when the start moved earlier (a wallet with older buys was added), fill the
      // gap on the same grid so the existing points stay where they are
      const back = [];
      if (pts.length && startBlock < pts[0][0]) for (let b = pts[0][0] - stride; b >= startBlock; b -= stride) back.push(b);
      const [b1, f1] = await Promise.all([sample(back.reverse(), stride), sample(fwd, stride)]);
      return b1.concat(pts, f1);
    };
    const firstBuyBlock = buys.length ? buys[0].block : head;
    const dailyStart = Math.max(1, firstBuyBlock - LIFETIME_LEAD_DAYS * DAILY_STRIDE);
    price.daily = await extend(prevPrice.daily, DAILY_STRIDE, dailyStart);
    const hourlyStart = Math.max(1, head - HOURLY_KEEP_DAYS * DAILY_STRIDE);
    price.hourly = (await extend(prevPrice.hourly, HOURLY_STRIDE, hourlyStart))
      .filter(pt => pt[1] >= headTs - HOURLY_KEEP_DAYS * 86400);
    const now = await pricesAt(head);
    price.latest = { block: head, ts: headTs, ptgcUsd: round(now.ptgcUsd, 6), plsUsd: round(now.plsUsd, 6) };
  } catch (e) {
    console.error('price line failed, carrying the previous line forward:', e.message);
    price.daily = prevPrice.daily || []; price.hourly = prevPrice.hourly || []; price.latest = prevPrice.latest || null;
  }

  const totals = buys.reduce((a, b) => ({ count: a.count + 1, ptgc: a.ptgc + b.ptgc, pls: a.pls + b.pls, usd: a.usd + b.usd }),
    { count: 0, ptgc: 0, pls: 0, usd: 0 });
  totals.avgPrice = totals.ptgc > 0 ? totals.usd / totals.ptgc : 0;
  totals.firstTs = buys.length ? buys[0].ts : null;
  totals.lastTs = buys.length ? buys[buys.length - 1].ts : null;

  const out = {
    schema: SCHEMA,
    generatedAt: new Date().toISOString(),
    wallets: WALLETS.map(w => w.addr), token: PTGC, pair: PAIR_PTGC_WPLS, plsPair: PAIR_WPLS_DAI,
    headBlock: head,
    source,
    totals: { ...totals, ptgc: round(totals.ptgc, 12), pls: round(totals.pls, 12), usd: round(totals.usd, 10), avgPrice: round(totals.avgPrice, 8) },
    excluded: { lpRemovals, noPlsPaid },
    buys: buys.map(b => ({ hash: b.hash, wallet: b.wallet, block: b.block, ts: b.ts, ptgc: round(b.ptgc, 10), pls: round(b.pls, 10),
      plsUsd: round(b.plsUsd, 6), usd: round(b.usd, 8), price: round(b.price, 6), marketUsd: round(b.marketUsd || b.price, 6) })),
    price
  };
  fs.mkdirSync(OUT_PATH.slice(0, OUT_PATH.lastIndexOf('/')) || '.', { recursive: true });
  fs.writeFileSync(OUT_PATH, JSON.stringify(out));
  console.log(`wrote ${OUT_PATH}: ${out.buys.length} buys, ${totals.ptgc.toFixed(0)} PTGC for ${totals.pls.toFixed(0)} PLS ($${totals.usd.toFixed(0)}), ` +
    `avg $${totals.avgPrice.toFixed(8)}; line daily=${price.daily.length} hourly=${price.hourly.length}; ${((Date.now() - t0) / 1000).toFixed(1)} s`);
}

if (process.argv[1] && /build-dao-buys\.mjs$/.test(process.argv[1])) {
  main().catch(e => { console.error(e); process.exit(1); });
}
