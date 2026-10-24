#!/usr/bin/env python3
"""Audit IV D-6 (2026-10-24, Shaka picked "256 bigger files"): the rank index is sharded by the address's first TWO hex
characters (256 files per token) instead of three (4,096). Every daily rebuild rewrote ~4,000 PTGC + ~2,900 UFO files into
main's history (~2.5 M git objects a year); now ~512 a day — 16x fewer. A wallet lookup reads one ~110 KB file (~35 KB
gzipped) instead of ~8 KB. meta.json gains `shard: 2`; the Portfolio rank window reads meta first-or-together and takes the
shard named by it, falling back to the other layout, so the page works before, during and after the switch-over.
The builder reshards on its next run even when the archive did not move (`meta.shard` differs), or now with
`INDEX_ONLY=1 node scripts/build-rank-history.mjs` (no RPC, rebuilds the index from the archive).
Idempotent, from the repo root:   python3 tools/rank-index-256.py   (twice: "0 edit(s)")
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

B = 'scripts/build-rank-history.mjs'
edit(B, "//   data/rank-index/<TOKEN>/<xxx>.json       the index — 4,096 shards by the address's first three hex chars: for every wallet",
        "//   data/rank-index/<TOKEN>/<xx>.json        the index — 256 shards by the address's first TWO hex chars (D-6, 2026-10-24; was\n"
        "//                                           4,096 by three — ~6,900 files rewritten into git every day): for every wallet")
edit(B, "const ARCH_DIR = 'data/rank-history', IDX_DIR = 'data/rank-index';",
        "const ARCH_DIR = 'data/rank-history', IDX_DIR = 'data/rank-index';\n"
        "const SHARD_HEX = 2;   // D-6: the index shard = the address's first SHARD_HEX hex chars (meta.json `shard`; the page reads either layout)")
edit(B, "  // than run-lengths (which almost never repeat). 4,096 shards by the address's first three hex chars → ~10 KB each for PTGC.",
        "  // than run-lengths (which almost never repeat). 256 shards by the address's first two hex chars → ~110 KB each for PTGC (D-6).")
edit(B, "    (shards[a.slice(2, 5)] = shards[a.slice(2, 5)] || {})[a] = [ks[0], ds];",
        "    const sk = a.slice(2, 2 + SHARD_HEX); (shards[sk] = shards[sk] || {})[a] = [ks[0], ds];")
edit(B, "JSON.stringify({ schema: 2, token: sym, day0: days[0], days: days.length, holders: counts,",
        "JSON.stringify({ schema: 2, shard: SHARD_HEX, token: sym, day0: days[0], days: days.length, holders: counts,")
edit(B, """for (const sym of Object.keys(TOKENS)) {
  try { const st = await extend(sym); if (st) { if (!st.unchanged) index(sym, st); ok++; } }   // e33: no index rebuild on a no-op""",
"""/* D-6: an index in another shard layout is rebuilt from the archive even when the archive did not move (no RPC);
   INDEX_ONLY=1 does just that for every token (a local reshard / check) */
const metaShard = sym => { try { return JSON.parse(fs.readFileSync(path.join(IDX_DIR, sym, 'meta.json'), 'utf8')).shard || 3; } catch { return null; } };
const archiveOf = sym => JSON.parse(fs.readFileSync(path.join(ARCH_DIR, sym + '.json'), 'utf8'));
for (const sym of Object.keys(TOKENS)) {
  try {
    if (process.env.INDEX_ONLY) { index(sym, archiveOf(sym)); ok++; continue; }
    const st = await extend(sym);
    if (st) { if (!st.unchanged) index(sym, st); else if (metaShard(sym) !== SHARD_HEX) { console.log(`${sym}: index is in the ${metaShard(sym)}-char layout → resharding to ${SHARD_HEX}`); index(sym, archiveOf(sym)); } ok++; }
  }   // e33: no index rebuild on a no-op""")

R = 'tools/pf-v2/PfRank.jsx'
edit(R, "       Opens from any rank badge. Reads data/rank-index/<TOKEN>/meta.json + the wallet's shard (<first three hex>.json): for every",
        "       Opens from any rank badge. Reads data/rank-index/<TOKEN>/meta.json + the wallet's shard (<first two hex>.json since D-6, 2026-10-24;\n"
        "       three before — meta.shard says which): for every")
edit(R, """      const[meta,shard]=await Promise.all([pfrGet(`${PFR_RAW}${tok}/meta.json`),pfrGet(`${PFR_RAW}${tok}/${a.slice(2,5)}.json`)]);
      if(!meta||meta.schema!==2)return null;""",
"""      /* D-6 (2026-10-24): 256 shards by two hex chars (meta.shard 2); the old layout had 4,096 by three. The two-char file is read
         together with meta (the usual case after the switch-over); the other layout only when meta names it or the file is missing. */
      const[meta,s2]=await Promise.all([pfrGet(`${PFR_RAW}${tok}/meta.json`),pfrGet(`${PFR_RAW}${tok}/${a.slice(2,4)}.json`)]);
      if(!meta||meta.schema!==2)return null;
      const shard=meta.shard===2?(s2||await pfrGet(`${PFR_RAW}${tok}/${a.slice(2,5)}.json`)):(await pfrGet(`${PFR_RAW}${tok}/${a.slice(2,5)}.json`)||s2);""")

out = subprocess.run([sys.executable, 'tools/pf-v2.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'rank-index-256: {n} edit(s); build-rank-history.mjs {sha(B)}, portfolio.html {sha("portfolio.html")}')
