// to-deltas.mjs <full.json> <out.json> — backfill-fast's full per-day lists → the schema-2 delta archive the daily step extends
import fs from 'node:fs';
const [, , IN, OUT] = process.argv;
const st = JSON.parse(fs.readFileSync(IN, 'utf8'));
const days = Object.keys(st.days).sort();
const out = { schema: 2, token: st.token, launch: st.launch, days: {}, contracts: st.contracts, eoa: st.eoa, cur: st.cur, cursorDay: st.cursorDay, generatedAt: st.generatedAt };
let prev = new Map();
for (const d of days) {
  const rec = st.days[d], f = (st.factors && st.factors[d]) || 1, now = new Map(rec.h);
  const m = {};
  // moved = any wallet whose key is not (prev × f) within rounding, plus arrivals and departures
  for (const [a, k] of now) { const p = prev.get(a); if (p === undefined) { m[a] = k; continue; } const exp = p * f; const tol = Math.max(1, exp * 2e-7); if (Math.abs(k - exp) > tol) m[a] = k; }
  for (const a of prev.keys()) if (!now.has(a)) m[a] = 0;
  out.days[d] = { b: rec.b, f, m, n: rec.n };
  prev = now;
}
fs.writeFileSync(OUT, JSON.stringify(out));
const sz = fs.statSync(OUT).size; console.log(`${st.token}: ${days.length} days → ${(sz / 1e6).toFixed(1)} MB (was ${(fs.statSync(IN).size / 1e6).toFixed(1)} MB)`);
