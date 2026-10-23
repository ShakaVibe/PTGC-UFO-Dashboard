// pipeline-watchdog.mjs — Audit IV e22 (2026-10-23). Run every 3 h by .github/workflows/pipeline-watchdog.yml: exits 1 (→ GitHub's
// failure e-mail to the repo owner) when the hourly data pipeline has stopped — not run for 3 h (the Worker's hourly dispatch or its
// DISPATCH_TOKEN died; GitHub's own schedule only fires a few times a day), or a step has not succeeded within twice its gate + 3 h.
// A step that ran but carried old data forward is a ::warning:: (yellow), not a failure. Needs no secret.
// Usage: node scripts/pipeline-watchdog.mjs [data/pipeline-status.json] [scripts/pipeline-run.mjs]
import fs from 'node:fs';
const [sf = 'data/pipeline-status.json', rf = 'scripts/pipeline-run.mjs'] = process.argv.slice(2);
const st = JSON.parse(fs.readFileSync(sf, 'utf8')), src = fs.readFileSync(rf, 'utf8'), now = Date.now(), H = 3600e3;
const gates = {};   // step → gate hours (1 = every hourly run), read from pipeline-run.mjs's STEPS so this never drifts from it
for (const m of src.matchAll(/'([a-z0-9-]+)':\s*\{\s*run:\s*'[^']+'(?:,\s*gate:\s*\[\s*'[^']+',\s*(\d+(?:\.\d+)?)\s*\])?/g)) gates[m[1]] = m[2] ? +m[2] : 1;   // Audit IV e33: decimal gates (24.5)
if (!Object.keys(gates).length) { console.log('::error::could not read the step list from ' + rf); process.exit(1); }
const age = t => (t ? (now - Date.parse(t)) / H : Infinity), f = h => (h === Infinity ? 'never' : h.toFixed(1) + ' h');
const problems = [];
const runAge = age(st.generatedAt);
if (runAge > 3) problems.push(`the pipeline has not run for ${f(runAge)} (last run ${st.generatedAt}, ${st.trigger}) — check the Cloudflare Worker's hourly dispatch and its DISPATCH_TOKEN`);
for (const [step, g] of Object.entries(gates)) {
  const s = st.steps && st.steps[step], limit = 2 * g + 3, a = age(s && s.lastSuccessAt);
  if (a > limit) problems.push(`${step}: last success ${f(a)} ago (gate ${g} h → limit ${limit} h)${s && s.lastError ? ' — last error: ' + String(s.lastError).slice(0, 160) : ''}`);
  else if (s && s.carried) console.log(`::warning::${step} carried data forward in the last run (it ran, but kept an older figure)`);
}
if (problems.length) { for (const p of problems) console.log('::error::' + p); process.exit(1); }
console.log(`pipeline OK — last run ${f(runAge)} ago; all ${Object.keys(gates).length} steps within their limits`);
