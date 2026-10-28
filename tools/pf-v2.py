#!/usr/bin/env python3
"""Portfolio v2 — syncs the page body's source (tools/pf-v2/*) into portfolio.html. Run from the repo root after editing any of
them, twice (the second run must print "0 edit(s)"):   python3 tools/pf-v2.py

  1. the pf2-* CSS (tools/pf-v2/pf2.css) + the Leagues window's lg-* CSS copied from index.html, at the end of the page's <style>
  2. the components (PfLeagues.jsx → PfHistory.jsx → PfTx.jsx → PfRank.jsx → PortfolioV2.jsx, in that order) at module scope above PortfolioPage
Design: design/portfolio/README.md (every decision), audit + roadmap handover/PORTFOLIO-ROADMAP.md.
History: built 2026-10-13 behind a faint preview dot (this script also wrapped the classic body and added the dot); LIVE
2026-10-16; the classic body, the dot and PF_V2_LIVE were removed 2026-10-20 by tools/pf-cleanup.py, and those steps with them.
PortfolioPage (in portfolio.html itself) owns the state and renders <PortfolioV2 …/> — edit its props there.
"""
import os, re, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'tools', 'pf-v2')
F = os.path.join(ROOT, 'portfolio.html')
s = open(F, encoding='utf-8').read()
edits = 0

css = open(os.path.join(HERE, 'pf2.css'), encoding='utf-8').read().rstrip('\n')
jsx = '\n\n'.join(open(os.path.join(HERE, n), encoding='utf-8').read().rstrip('\n') for n in ('PfLeagues.jsx', 'PfHistory.jsx', 'PfTx.jsx', 'PfRank.jsx', 'PortfolioV2.jsx'))
# round 2: the Leagues window's CSS, taken from index.html each run (one design for both pages)
ix = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
a = ix.index('    .lg-m{'); b = ix.index('    /* the combined card (Socials', a)
# Audit VI item 5 (2026-10-28): the Holders share card's hc2-* rules (2026-10-26) were inserted INSIDE this range in index.html,
# so a re-run pasted 25 lines of them into portfolio.html. Copy the Leagues rules only: drop the hc2 header and every .hc2- rule.
lg = '\n'.join(l for l in ix[a:b].split('\n') if not (l.startswith('    .hc2-') or l.startswith('    /* hc2 ')))
css += ('\n    /* ---- the Leagues window (lg-*), copied from index.html by tools/pf-v2.py — edit it THERE, then re-run ---- */\n'
        + lg.rstrip('\n'))

CSS_A, CSS_B = '    /* ===== Portfolio v2 (2026-10-13, design', '\n  </style>\n</head>'
JSX_A, JSX_B = '    /* Portfolio v2, round 2 (2026-10-13): the Leagues window', '\n\n    const PortfolioPage=({onBack})=>{'
JSX_A0 = '    /* ===== PORTFOLIO v2 (2026-10-13)'   # step-1 builds started the block here
JSX_A1 = '    /* ===== Portfolio v2 — shared bits (loaded FIRST by pf-v2.py) ====='   # round 27: PfLeagues.jsx got a header, so the block starts here now

def sync(start_markers, end, block, what):
    """Insert the block before `end`, or replace what an earlier run inserted (so edits to tools/pf-v2/* flow in)."""
    global s, edits
    starts = [s.find(m) for m in start_markers if s.find(m) >= 0]
    if starts:
        i = min(starts); j = s.index(end, i)
        if s[i:j] != block:
            s = s[:i] + block + s[j:]; edits += 1
    else:
        anchor = '\n  </style>\n</head>' if what == 'css' else '    const PortfolioPage=({onBack})=>{'
        new = ('\n' + block + anchor) if what == 'css' else (block + '\n\n' + anchor)
        if s.count(anchor) != 1: sys.exit(f'pf-v2: anchor for {what} not found')
        s = s.replace(anchor, new); edits += 1

# 1. CSS  2. the components (Leagues window + PortfolioV2)
sync([CSS_A], CSS_B, css, 'css')
sync([JSX_A1, JSX_A, JSX_A0], JSX_B, jsx, 'jsx')

# the page must render the v2 body unconditionally (pf-cleanup.py); the data hooks rounds 2 / 6 added to the classic loaders stay
for m in ('          <PortfolioV2 updateWallet={updateWalletV2} ', 'const updateWalletV2=', 'received:tRecv,', '(window.pfUfoRecv=window.pfUfoRecv||{})'):
    if m not in s: sys.exit(f'pf-v2: expected {m!r} in portfolio.html — run tools/pf-cleanup.py first?')

if edits:
    open(F, 'w', encoding='utf-8').write(s)
print(f'pf-v2: {edits} edit(s); portfolio.html sha256 {hashlib.sha256(s.encode()).hexdigest()[:8]}…')
