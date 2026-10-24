// rpc-pool.js — one PulseChain RPC pool for every pipeline script (Audit IV e33 / D-4, 2026-10-24).
//
// Before: eight scripts posted every call to rpc.pulsechain.com and nothing else (~5,600 calls an hour); an outage
// or a rate-limit storm there failed the whole rpc lane at once. The pages have rotated three endpoints since a41.
//
// What this does, so the scripts can keep their own retry / halving logic untouched:
//   poolFetch(init) has fetch()'s shape for a JSON-RPC POST (init.body = the JSON string, single call or batch) and
//   resolves a Response-like {status, ok, json()} from the first endpoint that answered — or throws the last error.
//   * The PRIMARY (the first URL) is always tried first: while it is healthy nothing changes. A fallback is used
//     only when the primary fails: a transport error / timeout, HTTP 429 or 5xx, or a JSON-RPC rate limit
//     (-32005, "rate limit", "too many requests"). A failed endpoint sits out RPC_COOLDOWN_MS (30 s, as a41).
//   * HEAD CHECK (why the handover parked D-4): a fallback that lags the chain head answers an eth_getLogs for blocks
//     it does not have yet with an EMPTY list, and an incremental scan would then step past those blocks for good.
//     So every call that names a block (eth_getLogs' toBlock, eth_call / eth_getBalance at a block,
//     eth_getBlockByNumber) goes only to an endpoint whose last seen eth_blockNumber is at or past that block
//     (re-probed when it looks short). Calls on 'latest' skip endpoints more than LAG_MAX blocks behind the best head.
//   * Archive state reads (balanceOf at an old block) stay on the primary unless it fails; a non-archive fallback
//     answers those with a JSON-RPC error, which the caller's own retry already handles.
// Env: RPC_URLS (comma list, primary first) overrides the list; a script's own RPC= (one URL) makes the pool that URL.
// At exit a script that used a fallback prints one "rpc pool:" line (calls per endpoint, cooldowns, lagging nodes).
'use strict';

const DEFAULT_URLS = ['https://rpc.pulsechain.com', 'https://rpc-pulsechain.g4mm4.io', 'https://pulsechain-rpc.publicnode.com'];
const URLS = (process.env.RPC_URLS ? process.env.RPC_URLS.split(',') : process.env.RPC ? [process.env.RPC] : DEFAULT_URLS)
  .map(s => s.trim()).filter(Boolean);
const RPC_COOLDOWN_MS = 30000;
const ATTEMPT_MS = +process.env.RPC_ATTEMPT_MS || 30000;   // one endpoint's answer time before the next one is tried
const PROBE_MS = 8000;
const HEAD_TTL_MS = 60000;   // eth_blockNumber per endpoint, re-read at most once a minute (+ on demand when short)
const LAG_MAX = 30;          // blocks (~5 min): a node further behind the best head is not asked 'latest' questions

const st = URLS.map(url => ({ url, host: url.replace(/^https?:\/\//, '').replace(/\/.*$/, ''), failedAt: 0, head: null, headAt: 0, probedAt: 0, probing: null, calls: 0, fails: 0, last: '' }));
let probeAll = null, probeAllAt = 0, fallbackUsed = false;

const isRateLimit = j => {
  const errs = Array.isArray(j) ? j.map(x => x && x.error).filter(Boolean) : (j && j.error ? [j.error] : []);
  return errs.some(e => e.code === -32005 || /rate limit|too many requests|429/i.test(String(e.message || '')));
};
const hexNum = v => (typeof v === 'string' && /^0x[0-9a-f]+$/i.test(v)) ? parseInt(v, 16) : null;
/* the highest block a request names (null = none / 'latest') */
function needBlock(body) {
  let need = null;
  for (const q of Array.isArray(body) ? body : [body]) {
    if (!q || !Array.isArray(q.params)) continue;
    const p = q.params; let b = null;
    if (q.method === 'eth_getLogs') b = p[0] && hexNum(p[0].toBlock);
    else if (q.method === 'eth_getBlockByNumber') b = hexNum(p[0]);
    else if (q.method === 'eth_call' || q.method === 'eth_getBalance' || q.method === 'eth_getCode' || q.method === 'eth_getStorageAt') b = hexNum(p[p.length - 1]);
    if (b != null && (need == null || b > need)) need = b;
  }
  return need;
}

async function post(s, text, ms) {
  const r = await fetch(s.url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: text, signal: AbortSignal.timeout(ms) });
  if (r.status === 429 || r.status >= 500) throw new Error('HTTP ' + r.status);
  const j = await r.json();
  return { r, j };
}
function probe(s) {
  if (s.probing) return s.probing;
  s.probedAt = Date.now();
  s.probing = (async () => {
    try { const { j } = await post(s, JSON.stringify({ jsonrpc: '2.0', id: 1, method: 'eth_blockNumber', params: [] }), PROBE_MS);
      const h = hexNum(j && j.result); if (h != null) { s.head = h; s.headAt = Date.now(); } }
    catch (e) { /* unknown head: a fallback with no head is not asked block-specific questions */ }
    finally { s.probing = null; }
  })();
  return s.probing;
}
function probeHeads() {
  if (st.length < 2) return Promise.resolve();
  if (probeAll && Date.now() - probeAllAt < HEAD_TTL_MS) return probeAll;
  probeAllAt = Date.now();
  probeAll = Promise.all(st.map(probe));
  return probeAll;
}
const bestHead = () => st.reduce((m, s) => s.head != null && s.head > m ? s.head : m, 0);

async function eligible(s, i, need) {
  if (Date.now() - s.failedAt < RPC_COOLDOWN_MS) return false;
  if (st.length < 2) return true;
  const stale = Date.now() - s.probedAt > 15000;
  if (need != null) {
    if ((s.head == null || s.head < need) && stale) await probe(s);   // short or unknown: look again (at most every 15 s)
    if (s.head == null) return i === 0;          // the primary with an unreadable head: as before the pool existed
    return s.head >= need;
  }
  if (s.head == null && stale) await probe(s);
  const best = bestHead();
  if (s.head == null) return i === 0;
  return !(best && s.head < best - LAG_MAX);
}

async function poolFetch(init) {
  const text = typeof init === 'string' ? init : init.body;
  const ms = (init && init.attemptMs) || ATTEMPT_MS;           // the caller's own per-try budget, per endpoint
  let body = null; try { body = JSON.parse(text); } catch (e) {}
  const need = body ? needBlock(body) : null;
  await probeHeads();
  let lastErr = null, lastAnswer = null;
  for (let pass = 0; pass < 2; pass++) {
    let tried = 0;
    for (let i = 0; i < st.length; i++) {
      const s = st[i];
      // pass 0: the eligible endpoints in order (primary first). pass 1 runs only when pass 0 had NONE to try (all
      // cooling down): it ignores the cooldowns — but never sends a block-specific call to a node short of that block.
      const ok = pass === 0 ? await eligible(s, i, need)
        : (need == null || st.length < 2 || i === 0 || (s.head != null && s.head >= need));
      if (!ok) continue;
      tried++; s.calls++;
      try {
        const { r, j } = await post(s, text, ms);
        if (isRateLimit(j)) { lastAnswer = { r, j }; throw new Error('rate limited'); }
        if (i > 0) { if (!fallbackUsed) console.log(`rpc pool: ${st[0].host} unavailable (${st[0].last || 'cooling down'}) → answered by ${s.host}`); fallbackUsed = true; }
        return { status: r.status, ok: r.ok, json: async () => j };
      } catch (e) {
        lastErr = e; s.fails++; s.failedAt = Date.now(); s.last = String(e.message || e).slice(0, 80);
      }
    }
    if (tried > 0) break;
  }
  if (lastAnswer) return { status: lastAnswer.r.status, ok: lastAnswer.r.ok, json: async () => lastAnswer.j };   // let the caller see the rate-limit error and back off
  throw lastErr || new Error(need != null ? `no RPC endpoint has reached block ${need} yet` : 'no RPC endpoint available');
}

function summary() {
  return st.map(s => `${s.host} ${s.calls} call${s.calls === 1 ? '' : 's'}${s.fails ? `, ${s.fails} failed (${s.last})` : ''}${s.head != null ? `, head ${s.head}` : ''}`).join(' · ');
}
process.on('exit', () => { if (fallbackUsed) console.log('rpc pool: ' + summary()); });

module.exports = { poolFetch, needBlock, summary, URLS, _state: st, _reset: () => { probeAll = null; probeAllAt = 0; st.forEach(s => { s.failedAt = 0; s.head = null; s.headAt = 0; s.probedAt = 0; }); } };
