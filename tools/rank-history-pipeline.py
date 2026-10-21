#!/usr/bin/env python3
"""Holder rank HISTORY (2026-10-21): wires scripts/build-rank-history.mjs into the hourly Data Pipeline. Idempotent, repo root:
    python3 tools/rank-history-pipeline.py        ("0 edit(s)" = already applied)
  - scripts/pipeline-run.mjs: step 'rank-history' (gate: data/rank-index/PTGC/meta.json, 20 h → once a day) in the holder-ranks
    lane, after holder-ranks (both page PulseScan / the RPC; the extend is ~1 min a day per token)
  - .github/workflows/data-pipeline.yml: the step in the `only` description; data/rank-history/*.json + data/rank-index/ in the
    Commit list (the device bridge refuses .github/ — this script is how the yml gets edited, run on the Mac)
"""
import hashlib
def rd(p): return open(p, encoding='utf-8').read()
total = 0
def edit(path, pairs):
    global total
    s = rd(path); n = 0
    for old, new in pairs:
        if new in s: continue
        assert s.count(old) == 1, f'{path}: anchor x{s.count(old)}: {old[:70]!r}'
        s = s.replace(old, new); n += 1
    if n: open(path, 'w', encoding='utf-8').write(s)
    total += n
    print(f'{path}: {n} edit(s), md5 {hashlib.md5(s.encode()).hexdigest()[:8]}')
edit('scripts/pipeline-run.mjs', [
  ("""  'holder-ranks':    { run: 'scripts/build-holder-ranks.mjs',       gate: ['data/holder-ranks.json', 2] },   // 2026-10-21: Portfolio HOLDER RANK — every real holder's balance, sorted (~9 min of PulseScan paging)
};""",
   """  'holder-ranks':    { run: 'scripts/build-holder-ranks.mjs',       gate: ['data/holder-ranks.json', 2] },   // 2026-10-21: Portfolio HOLDER RANK — every real holder's balance, sorted (~9 min of PulseScan paging)
  'rank-history':    { run: 'scripts/build-rank-history.mjs',       gate: ['data/rank-index/PTGC/meta.json', 20] },   // 2026-10-21: the rank window's history — extends the day archive, rebuilds the per-wallet index (once a day)
};"""),
  ("""  { name: 'holder-ranks',  steps: ['holder-ranks'] },   // its own lane: ~9 min of PulseScan paging must not lengthen the rpc lane""",
   """  { name: 'holder-ranks',  steps: ['holder-ranks', 'rank-history'] },   // its own lane: ~9 min of PulseScan paging must not lengthen the rpc lane; rank-history after it (~1 min a day)"""),
])
edit('.github/workflows/data-pipeline.yml', [
  ("swap-volume, holder-ranks. Empty", "swap-volume, holder-ranks, rank-history. Empty"),
  ("""            data/holder-ranks.json \\
""", """            data/holder-ranks.json \\
            data/rank-history/PTGC.json data/rank-history/UFO.json data/rank-index \\
"""),
])
print(f'rank-history-pipeline: {total} edit(s)')
