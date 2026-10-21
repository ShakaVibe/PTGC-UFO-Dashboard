#!/usr/bin/env python3
"""Holder rank (2026-10-21): wires scripts/build-holder-ranks.mjs into the hourly Data Pipeline. Idempotent, repo root:
    python3 tools/holder-ranks-pipeline.py        ("0 edit(s)" = already applied)
  - scripts/pipeline-run.mjs: step 'holder-ranks' (gate: data/holder-ranks.json, 2 h) in a lane of its OWN — it pages
    PulseScan for ~9 min, so in the rpc lane it would make every run ~9 min longer
  - .github/workflows/data-pipeline.yml: the step in the `only` description; data/holder-ranks.json in the Commit list
    (the device bridge refuses .github/ — this script is how the yml gets edited, run on the Mac)
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
  ("""  'swap-volume':     { run: 'scripts/build-swap-volume.mjs' },   // 2026-10-06: human vs arb-bot volume (reads charts-intraday for prices — last in the rpc lane)
};""",
   """  'swap-volume':     { run: 'scripts/build-swap-volume.mjs' },   // 2026-10-06: human vs arb-bot volume (reads charts-intraday for prices — last in the rpc lane)
  'holder-ranks':    { run: 'scripts/build-holder-ranks.mjs',       gate: ['data/holder-ranks.json', 2] },   // 2026-10-21: Portfolio HOLDER RANK — every real holder's balance, sorted (~9 min of PulseScan paging)
};"""),
  ("""  { name: 'pair-volume',   steps: ['pair-volume'] },
];""",
   """  { name: 'pair-volume',   steps: ['pair-volume'] },
  { name: 'holder-ranks',  steps: ['holder-ranks'] },   // its own lane: ~9 min of PulseScan paging must not lengthen the rpc lane
];"""),
])
edit('.github/workflows/data-pipeline.yml', [
  ("pair-volume, new-holders, swap-volume. Empty", "pair-volume, new-holders, swap-volume, holder-ranks. Empty"),
  ("""            data/new-holders.json \\
""", """            data/new-holders.json \\
            data/holder-ranks.json \\
"""),
])
print(f'holder-ranks-pipeline: {total} edit(s)')
