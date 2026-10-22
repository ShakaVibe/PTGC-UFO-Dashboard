#!/usr/bin/env python3
"""TOP 100 STAKERS (2026-10-22): wires scripts/build-top-stakers.mjs into the hourly Data Pipeline. Idempotent, repo root:
    python3 tools/top100-pipeline.py        ("0 edit(s)" = already applied)
  - scripts/pipeline-run.mjs: step 'top-stakers' (gate: data/top-stakers.json, 2 h) at the end of the holder-ranks lane
    (~30 s: the Deposit logs since the last run + one mapUserInfo / balanceOf per known staker)
  - .github/workflows/data-pipeline.yml: the step in the `only` description; data/top-stakers.json + its cache in the Commit list
  - .github/workflows/deploy.yml: the cache (5,000+ addresses, nothing reads it) is not shipped to the site
  (the device bridge refuses .github/ — this script is how the ymls get edited, run on the Mac)
"""
import hashlib
total = 0
def edit(path, pairs):
    global total
    s = open(path, encoding='utf-8').read(); n = 0
    for old, new in pairs:
        if new in s: continue
        assert s.count(old) == 1, f'{path}: anchor x{s.count(old)}: {old[:70]!r}'
        s = s.replace(old, new); n += 1
    if n: open(path, 'w', encoding='utf-8').write(s)
    total += n
    print(f'{path}: {n} edit(s), md5 {hashlib.md5(s.encode()).hexdigest()[:8]}')
edit('scripts/pipeline-run.mjs', [
  ("""  'rank-history':    { run: 'scripts/build-rank-history.mjs',""",
   """  'top-stakers':     { run: 'scripts/build-top-stakers.mjs',        gate: ['data/top-stakers.json', 2] },   // 2026-10-22: the TOP 100 window's stakers — Deposit logs + mapUserInfo (~30 s)
  'rank-history':    { run: 'scripts/build-rank-history.mjs',"""),
  ("""steps: ['holder-ranks', 'rank-history'] },""", """steps: ['holder-ranks', 'rank-history', 'top-stakers'] },"""),
])
edit('.github/workflows/data-pipeline.yml', [
  ("holder-ranks, rank-history. Empty", "holder-ranks, rank-history, top-stakers. Empty"),
  ("""            data/holder-ranks.json \\
""", """            data/holder-ranks.json \\
            data/top-stakers.json data/top-stakers-cache.json \\
"""),
])
edit('.github/workflows/deploy.yml', [
  ("""! -name 'swap-volume-cache.json' -exec""", """! -name 'swap-volume-cache.json' ! -name 'top-stakers-cache.json' -exec"""),
])
print(f'top100-pipeline: {total} edit(s)')
