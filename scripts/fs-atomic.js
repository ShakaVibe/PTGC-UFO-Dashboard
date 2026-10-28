// fs-atomic.js — one way for every pipeline script to write a data file (Audit VI item 6, 2026-10-28).
//
// Why: the Data Pipeline's job has a 45-minute timeout and its "Commit if changed" step runs `if: always()`, so a run that
// is killed mid-write still commits whatever is on disk. A plain fs.writeFileSync that is cut short leaves a truncated JSON
// file; the pages read every data file live, so JSON.parse fails in every visitor's browser until the next good run. Six
// writers already did tmp + rename (burn archive, coingecko, ufo-ptgc-burns, league-history, rank-history state, the
// pipeline status); fourteen did not. They all use this now.
//
// writeAtomic(path, text): writes `${path}.tmp` and renames it over `path`. A rename on the same filesystem is atomic, so a
// reader (or `git add`) sees either the old file or the new one, never half of one. A killed run can leave a `.tmp` beside
// the file; `*.tmp` is in .gitignore, so it is never committed, and the next run overwrites it.
const fs = require('fs');

function writeAtomic(path, text) {
  const tmp = path + '.tmp';
  fs.writeFileSync(tmp, text);
  fs.renameSync(tmp, path);
}

module.exports = { writeAtomic };
