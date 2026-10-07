// pipeline-run.mjs — runs the Data Pipeline's steps in THREE PARALLEL LANES (2026-10-06).
//
//   node scripts/pipeline-run.mjs            run (env: ONLY, FORCE, COINGECKO_API_KEY; writes the summary)
//   node scripts/pipeline-run.mjs --report   after the commit: job summary + annotations, exit 1 if a step failed
//
// Why: the workflow used to run its twelve steps one after another — 22 minutes a run, 20 of them three
// sources that have nothing to do with each other (pair-volume 9 min, value-generated 6, coingecko 3.5,
// charts 2.3). The lanes keep every ordering that matters: the CoinGecko-keyed scripts stay serial so
// their 2 s pacing holds (charts before coingecko, which reads charts-data for d90); the public-RPC /
// PulseScan scripts stay serial so they never share the RPC's rate limit (treasury before dao-buys);
// pair-volume has a lane of its own. A run is now as long as its longest lane (~6–7 min).
//
// Same rules as before: a step runs when its file-age gate says so (scripts/pipeline-gate.mjs — ONLY
// names a subset, FORCE ignores the ages); a failing step never stops the others; the Commit step
// then lands whatever was written; --report goes red afterwards if anything failed, naming the step
// and quoting its last lines, so the reason is on the run page without opening the log.
import fs from 'node:fs';
import path from 'node:path';
import { spawn } from 'node:child_process';

const SUMMARY = path.join(process.env.RUNNER_TEMP || '/tmp', 'pipeline-summary.json');
const STATUS = 'data/pipeline-status.json';   // c20 (Audit III): the per-step record that outlives the runner (the freshness strip's file)
const KEY_ENV = { COINGECKO_API_KEY: process.env.COINGECKO_API_KEY || '' };

// name → script, env, gate (file + min hours; none = every run). The name is what ONLY= takes.
const STEPS = {
  'charts':          { run: 'scripts/build-charts-data.js',         gate: ['data/charts-data.json', 2] },
  'charts-intraday': { run: 'scripts/build-charts-intraday.js' },
  'coingecko':       { run: 'scripts/fetch-coingecko-data.js' },
  'value-generated': { run: 'scripts/build-value-generated.mjs',    env: { OUT_PATH: 'data/value-generated.json' } },
  'burn-history':    { run: 'scripts/fetch-burn-history.js' },
  'treasury':        { run: 'scripts/fetch-treasury-transactions.js' },
  'dao-buys':        { run: 'scripts/build-dao-buys.mjs' },
  'ufo-ptgc-burns':  { run: 'scripts/fetch-ufo-ptgc-burns.js',      gate: ['data/ufo-ptgc-burns.json', 6] },
  'token-allocation':{ run: 'scripts/build-token-allocation.mjs',   gate: ['data/token-allocation.json', 6] },
  'lv-snapshot':     { run: 'scripts/lv-snapshot.js',               gate: ['data/lv-snapshots.json', 6] },
  'pair-volume':     { run: 'scripts/build-pair-volume.mjs' },
  'new-holders':     { run: 'scripts/build-new-holders.mjs' },
  'swap-volume':     { run: 'scripts/build-swap-volume.mjs' },   // 2026-10-06: human vs arb-bot volume (reads charts-intraday for prices — last in the rpc lane)
};
const LANES = [
  { name: 'coingecko-key', steps: ['charts', 'charts-intraday', 'coingecko'] },
  // c19 (Audit III, 2026-10-07): value-generated LAST — it rescans the 90-day window every hour (~6 min) and held the eight quick
  // files behind it (burn-summary, treasury, dao-buys, new-holders, swap-volume all stamped 7–8 min after dispatch).
  { name: 'rpc',           steps: ['burn-history', 'treasury', 'dao-buys', 'ufo-ptgc-burns', 'token-allocation', 'lv-snapshot', 'new-holders', 'swap-volume', 'value-generated'] },
  { name: 'pair-volume',   steps: ['pair-volume'] },
];

const stamp = () => new Date().toISOString().slice(11, 19);
const log = (step, line) => process.stdout.write(`${stamp()} [${step}] ${line}\n`);

/* Pipe a child's output through, one prefixed line at a time; keep the last lines for the report. */
function runChild(step, cmd, args, env, tail) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { env: { ...process.env, ...env }, stdio: ['ignore', 'pipe', 'pipe'] });
    let bufOut = '', bufErr = '';
    const feed = (buf, chunk, isErr) => {
      buf += chunk.toString();
      const lines = buf.split('\n'); buf = lines.pop();
      for (const l of lines) { log(step, l); tail.push((isErr ? 'stderr: ' : '') + l); if (tail.length > 12) tail.shift(); if (/::warning::/.test(l)) tail.carried = true; }   // c20: a carry-forward exits 0 — remember the warning
      return buf;
    };
    child.stdout.on('data', c => { bufOut = feed(bufOut, c, false); });
    child.stderr.on('data', c => { bufErr = feed(bufErr, c, true); });
    child.on('error', e => { log(step, `spawn error: ${e.message}`); tail.push(`spawn error: ${e.message}`); resolve(-1); });
    child.on('close', code => { if (bufOut) log(step, bufOut); if (bufErr) log(step, bufErr); resolve(code); });
  });
}

/* The gate, as the workflow ran it: `node scripts/pipeline-gate.mjs <step> <file> <hours>` prints run=true|false. */
async function gateSays(step) {
  const def = STEPS[step];
  const args = def.gate ? [step, def.gate[0], String(def.gate[1])] : [step, 'none', '0'];
  const tail = [];
  await runChild(step, process.execPath, ['scripts/pipeline-gate.mjs', ...args], {}, tail);
  const line = tail.find(l => /\[gate\]/.test(l)) || '';
  return { run: /run=true/.test(line), why: line.replace(/^.*— /, '') };
}

async function runLane(lane, results) {
  for (const step of lane.steps) {
    const def = STEPS[step];
    const g = await gateSays(step);
    if (!g.run) { results[step] = { outcome: 'skipped', seconds: 0, why: g.why, lane: lane.name }; continue; }
    const t0 = Date.now(), tail = [];
    log(step, `▶ ${def.run}`);
    const code = await runChild(step, process.execPath, [def.run], { ...KEY_ENV, ...(def.env || {}) }, tail);
    const seconds = Math.round((Date.now() - t0) / 1000);
    results[step] = { outcome: code === 0 ? 'success' : 'failure', code, seconds, tail, lane: lane.name, carried: !!tail.carried };
    log(step, `${code === 0 ? '✓' : '✗'} exit ${code} after ${seconds} s`);
  }
}

async function main() {
  const t0 = Date.now();
  console.log(`pipeline-run: ${LANES.length} lanes — ${LANES.map(l => `${l.name}: ${l.steps.join(' → ')}`).join(' | ')}`);
  console.log(`ONLY=${process.env.ONLY || '(all)'} FORCE=${process.env.FORCE || 'false'} key=${KEY_ENV.COINGECKO_API_KEY ? 'set' : 'MISSING'}`);
  const results = {};
  await Promise.all(LANES.map(l => runLane(l, results)));
  const summary = { startedAt: new Date(t0).toISOString(), seconds: Math.round((Date.now() - t0) / 1000), steps: results };
  fs.writeFileSync(SUMMARY, JSON.stringify(summary, null, 2));
  writeStatus(summary);
  const failed = Object.entries(results).filter(([, r]) => r.outcome === 'failure').map(([k]) => k);
  console.log(`pipeline-run: done in ${summary.seconds} s — ${Object.values(results).filter(r => r.outcome === 'success').length} ok, ${Object.values(results).filter(r => r.outcome === 'skipped').length} skipped, ${failed.length} failed${failed.length ? ` (${failed.join(', ')})` : ''}`);
}

/* c20 (Audit III, 2026-10-07): data/pipeline-status.json — what the job summary says, kept across runs. Per step: this run's
   outcome / seconds / why, and the last time it succeeded or failed (carried over from the previous file when the step was
   skipped or did not run), the failing step's last lines, and `carried` when the step printed a ::warning:: (dao-buys keeping
   the previous file exits 0 and used to show as a plain ✅). Readers: the freshness strip (roadmap g4), anyone curious. */
function writeStatus(summary) {
  let prev = {}; try { prev = JSON.parse(fs.readFileSync(STATUS, 'utf8')).steps || {}; } catch (e) {}
  const now = new Date().toISOString();
  const steps = {};
  for (const name of Object.keys(STEPS)) {
    const r = summary.steps[name], p = prev[name] || {};
    const s = { outcome: r ? r.outcome : 'not-run', seconds: r ? r.seconds : 0, lane: r ? r.lane : (LANES.find(l => l.steps.includes(name)) || {}).name };
    if (r && r.outcome === 'skipped' && r.why) s.why = r.why;
    s.lastSuccessAt = r && r.outcome === 'success' ? now : (p.lastSuccessAt || null);
    s.lastFailureAt = r && r.outcome === 'failure' ? now : (p.lastFailureAt || null);
    const said = (r && r.tail || []).filter(l => !/^(stderr: )?\s+at /.test(l));   // the message, not the stack frames
    s.lastError = r && r.outcome === 'failure' ? said.slice(-2).join(' ⏎ ').slice(0, 300) : (r && r.outcome === 'success' ? null : (p.lastError || null));
    s.carried = !!(r && r.carried);
    steps[name] = s;
  }
  const env = process.env;
  const status = {
    schema: 1, generatedAt: now, seconds: summary.seconds,
    trigger: env.GITHUB_EVENT_NAME || 'local', only: env.ONLY || null, force: env.FORCE === 'true',
    runUrl: env.GITHUB_RUN_ID ? `${env.GITHUB_SERVER_URL || 'https://github.com'}/${env.GITHUB_REPOSITORY}/actions/runs/${env.GITHUB_RUN_ID}` : null,
    lanes: LANES.map(l => ({ name: l.name, steps: l.steps })),
    counts: { ok: Object.values(steps).filter(s => s.outcome === 'success').length, skipped: Object.values(steps).filter(s => s.outcome === 'skipped').length, failed: Object.values(steps).filter(s => s.outcome === 'failure').length, carried: Object.values(steps).filter(s => s.carried).length },
    steps
  };
  fs.writeFileSync(STATUS + '.tmp', JSON.stringify(status, null, 2)); fs.renameSync(STATUS + '.tmp', STATUS);
  console.log(`pipeline-run: wrote ${STATUS}`);
}

function report() {
  let s; try { s = JSON.parse(fs.readFileSync(SUMMARY, 'utf8')); } catch (e) { console.error(`::error::no pipeline summary at ${SUMMARY} — the run step did not finish`); process.exit(1); }
  const order = Object.keys(STEPS);
  const rows = Object.entries(s.steps).sort((a, b) => order.indexOf(a[0]) - order.indexOf(b[0]));   // the workflow's order, not completion order
  const failed = rows.filter(([, r]) => r.outcome === 'failure');
  const md = [`### Data Pipeline — ${s.seconds} s, ${rows.filter(([, r]) => r.outcome === 'success').length} ok · ${rows.filter(([, r]) => r.outcome === 'skipped').length} skipped · ${failed.length} failed`, '',
    '| step | lane | outcome | time | note |', '|---|---|---|---:|---|'];
  for (const [k, r] of rows) {
    const icon = r.outcome === 'success' ? (r.carried ? '⚠️' : '✅') : r.outcome === 'failure' ? '❌' : '⏭️';   // c20: ⚠️ = exited 0 but printed a ::warning:: (kept the previous file)
    const note = r.outcome === 'skipped' ? (r.why || '') : r.outcome === 'failure' ? `exit ${r.code} — ${(r.tail || []).slice(-2).join(' ⏎ ').replace(/\|/g, '\\|').slice(0, 200)}` : (r.carried ? 'carried forward (see ::warning:: in the log)' : '');
    md.push(`| ${k} | ${r.lane} | ${icon} ${r.outcome} | ${r.seconds} s | ${note} |`);
  }
  if (process.env.GITHUB_STEP_SUMMARY) fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, md.join('\n') + '\n');
  console.log(md.join('\n'));
  for (const [k, r] of failed) console.log(`::error title=${k} failed::${(r.tail || []).slice(-4).join(' ⏎ ').slice(0, 900)}`);
  if (failed.length) { console.log(`::error::Steps failed: ${failed.map(([k]) => k).join(', ')} — their files were NOT refreshed this run (the others were committed).`); process.exit(1); }
  console.log('All steps that ran succeeded.');
}

if (process.argv.includes('--report')) report();
else main().catch(e => { console.error('pipeline-run crashed:', e); process.exit(1); });
