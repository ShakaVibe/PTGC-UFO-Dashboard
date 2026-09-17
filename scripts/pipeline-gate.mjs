// pipeline-gate — decides whether a step of the combined hourly workflow should run this hour.
//
//   node scripts/pipeline-gate.mjs <step> <data-file> <min-hours>
//
// Prints `run=true|false` (and a reason) and appends `run=` to $GITHUB_OUTPUT when set. A step
// runs when its file is missing / unreadable, when its newest timestamp is at least <min-hours>
// old, when FORCE=true, or when ONLY names the step. ONLY naming *other* steps means "don't run".
//
// Why file age and not the clock: GitHub delays scheduled runs by hours when a repo asks for too
// many of them (a29 — that is the bug this workflow fixes), so "run at 00/06/12/18" would skip
// whole windows. "Run when the file is ≥ N h old" is right whatever time the run actually starts.
//
// Timestamp lookup, in order: top-level lastUpdated / generatedAt / timestamp; for an array,
// the last element's timestamp. Anything else counts as "unknown" → run.
import fs from 'node:fs';

const [step, file, hoursArg] = process.argv.slice(2);
const minHours = Number(hoursArg || 0);
const only = (process.env.ONLY || '').split(',').map(s => s.trim()).filter(Boolean);
const force = /^(1|true|yes)$/i.test(process.env.FORCE || '');

function newestStamp(p) {
  const d = JSON.parse(fs.readFileSync(p, 'utf8'));
  const pick = o => o && (o.lastUpdated || o.generatedAt || o.timestamp);
  const s = Array.isArray(d) ? pick(d[d.length - 1]) : pick(d);
  const t = s ? Date.parse(s) : NaN;
  return Number.isFinite(t) ? t : null;
}

let run, why;
if (only.length) {
  run = only.includes(step); why = run ? `ONLY names ${step}` : `ONLY=${only.join(',')} does not name ${step}`;
} else if (force) {
  run = true; why = 'FORCE';
} else if (!(minHours > 0)) {
  run = true; why = 'runs every hour';
} else {
  let t = null;
  try { t = newestStamp(file); } catch (e) { run = true; why = `${file}: ${e.message} → run`; }
  if (run === undefined) {
    if (t == null) { run = true; why = `${file}: no timestamp field → run`; }
    else {
      const ageH = (Date.now() - t) / 36e5;
      // 15-min tolerance: an hourly run at :07 that follows a 12:08 write is 5.98 h later at
      // 18:07 — without it a "6 h" step would drift to every 7 h.
      run = ageH >= minHours - 0.25;
      why = `${file} is ${ageH.toFixed(1)} h old (gate ${minHours} h)`;
    }
  }
}
console.log(`[gate] ${step}: run=${run} — ${why}`);
if (process.env.GITHUB_OUTPUT) fs.appendFileSync(process.env.GITHUB_OUTPUT, `run=${run}\n`);
