#!/usr/bin/env python3
"""Audit III, batch 5b (2026-10-07): c15 — the image pass. Idempotent — run from the repo root:
    python3 tools/audit3-p5b.py
The files themselves were made once (PIL, WebP q80 method 6; the trophies q82 with alpha; lg-sea-wide at half resolution; the two
token logos resized to 512×512 at q90) and committed under NEW names (gotcha 38 — never swap bytes under the same name):
  logos/leagues/lg-sea-wide.webp (568 → 123 KB)   lg-sea.webp (543 → 311)   logos/calculators/calc-bg.webp (353 → 143)
  logos/socials/hub-sky.webp (309 → 125)   logos/livefeed/deck-bg.webp (305 → 191)   logos/hvb/banner.webp (258 → 160)
  card-gold.webp (175 → 93)   card-blue.webp (167 → 88)   wave.webp (154 → 93)   logos/kpi/kpi-bg-gold.webp (241 → 101)
  kpi-bg-green.webp (229 → 94)   logos/panels/bg-vg.webp (197 → 109)   bg-dao.webp (150 → 76)   bg-alloc.webp (145 → 73)
  logos/holders/nh-sky.webp (175 → 117)   logos/home/cosmic-bg.webp (175 → 97)   logos/ptgc/trophy_*.webp (735 → 64 for the three)
  logos/ptgc/logo-512.webp (28 KB) + logos/ufo/logo-512.webp (33 KB) for the 2000×2000 originals drawn at ≤ 130 px everywhere
  — 4.9 MB → 2.1 MB for the set. The originals stay in the repo (the Logos windows' download list still points at them).
This script swaps the references: every CSS url() / JS path / <img src> of those files, on index.html, calculators.html,
charts.html, portfolio.html and ledger.html — except the Logos windows' `{file:'…'}` download entries, which keep the originals.
"""
import sys, re, hashlib

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)
def md5(s): return hashlib.md5(s.encode('utf-8')).hexdigest()

SWAPS = [
    ('logos/leagues/lg-sea-wide.jpg', 'logos/leagues/lg-sea-wide.webp'),
    ('logos/leagues/lg-sea.jpg', 'logos/leagues/lg-sea.webp'),
    ('logos/calculators/calc-bg.jpg', 'logos/calculators/calc-bg.webp'),
    ('logos/socials/hub-sky.jpg', 'logos/socials/hub-sky.webp'),
    ('logos/livefeed/deck-bg.jpg', 'logos/livefeed/deck-bg.webp'),
    ('logos/hvb/banner.jpg', 'logos/hvb/banner.webp'),
    ('logos/hvb/card-gold.jpg', 'logos/hvb/card-gold.webp'),
    ('logos/hvb/card-blue.jpg', 'logos/hvb/card-blue.webp'),
    ('logos/hvb/wave.jpg', 'logos/hvb/wave.webp'),
    ('logos/kpi/kpi-bg-gold.jpg', 'logos/kpi/kpi-bg-gold.webp'),
    ('logos/kpi/kpi-bg-green.jpg', 'logos/kpi/kpi-bg-green.webp'),
    ('logos/panels/bg-vg.jpg', 'logos/panels/bg-vg.webp'),
    ('logos/panels/bg-dao.jpg', 'logos/panels/bg-dao.webp'),
    ('logos/panels/bg-alloc.jpg', 'logos/panels/bg-alloc.webp'),
    ('logos/holders/nh-sky.jpg', 'logos/holders/nh-sky.webp'),
    ('logos/home/cosmic-bg.jpg', 'logos/home/cosmic-bg.webp'),
    ('logos/ptgc/trophy_whale_gold.png', 'logos/ptgc/trophy_whale_gold.webp'),
    ('logos/ptgc/trophy_dolphin_gold.png', 'logos/ptgc/trophy_dolphin_gold.webp'),
    ('logos/ptgc/trophy_shark_silver.png', 'logos/ptgc/trophy_shark_silver.webp'),
]
# the two token logos: every reference except the Logos windows' download entries (`file:'…'`)
LOGO_RE = [
    (re.compile(r"(?<!file:')06_PTGC_V1_transparent_bg\.png"), 'logos/ptgc/logo-512.webp'),
    (re.compile(r"(?<!file:')07_Ufo_transparent\.png"), 'logos/ufo/logo-512.webp'),
]

def swap(path):
    s = read(path); n = 0
    for old, new in SWAPS:
        c = s.count(old)
        if c: s = s.replace(old, new); n += c
    for rx, new in LOGO_RE:
        s, c = rx.subn(new, s); n += c
    if n: write(path, s)
    print(f'{path}: {n} reference(s) swapped, md5 {md5(s)}')

for p in ['index.html', 'calculators.html', 'charts.html', 'portfolio.html', 'ledger.html']:
    swap(p)
print('audit3-p5b: done')
