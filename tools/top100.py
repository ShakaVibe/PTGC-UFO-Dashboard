#!/usr/bin/env python3
"""TOP 100 window (2026-10-22) — builds Shaka's picks from design/top100/mock-top100-v1.html (button B1, look B) into index.html.
Idempotent, run from the repo root:   python3 tools/top100.py      (run it twice: the second run must print "0 edit(s)")
  - the CSS  (tools/top100/t1.css) between /* T100:CSS:BEGIN */ … /* T100:CSS:END */, just before the LEAGUES CSS
  - the JSX  (tools/top100/t1.jsx: TOP100_LIVE, t1Fetch, T1Dot, Top100Modal) between /* T100:JSX:BEGIN */ … END, before PriceEl
  (2026-10-28: the one-time edits — LS key, Dashboard state, the button, the modal mount, the dot — were removed once applied;
   this script now only re-syncs the two fragments, so it is safe to re-run.)
Edit the two fragment files, never the spliced copy in index.html — the next run overwrites it.
"""
import hashlib, re
P = 'index.html'
s = open(P, encoding='utf-8').read()
n = 0

def splice(tag, body, anchor):
    global s, n
    b, e = f'/* T100:{tag}:BEGIN */', f'/* T100:{tag}:END */'
    block = f'    {b}\n{body.rstrip()}\n    {e}\n'
    if b in s:
        i, j = s.index('    ' + b), s.index(e) + len(e) + 1
        if s[i:j] != block: s = s[:i] + block + s[j:]; n += 1
    else:
        assert s.count(anchor) == 1, f'anchor x{s.count(anchor)}: {anchor[:60]!r}'
        s = s.replace(anchor, block + anchor); n += 1

def edit(old, new):
    global s, n
    if new in s: return
    assert s.count(old) == 1, f'anchor x{s.count(old)}: {old[:70]!r}'
    s = s.replace(old, new); n += 1

splice('CSS', open('tools/top100/t1.css', encoding='utf-8').read(),
       '    /* LEAGUES (2026-10-04) — the holder-tiers modal')
splice('JSX', open('tools/top100/t1.jsx', encoding='utf-8').read(),
       '    /* u4: hoisted out of Dashboard (Combined share card)')
# Audit VI item 5 (2026-10-28): the five edit() steps that used to follow (LS.T100_PREVIEW, the Dashboard's showTop100 /
# t100Preview state, the Top 100 button, the modal mount, the preview dot) were ONE-TIME insertions, applied 2026-10-22. Their guard
# was "is the new text already there?", and the inserted text was later edited in place (TOP100_LIVE, Audit IV), so a re-run
# inserted a second `const[showTop100,…]` — a compile error (handover gotcha: "do not re-run tools/top100.py"). They are gone;
# the two splice() steps above are the sync and stay idempotent. The removed text is in git history before 2026-10-28.

if n: open(P, 'w', encoding='utf-8').write(s)
print(f'top100: {n} edit(s), index.html sha256 {hashlib.sha256(s.encode()).hexdigest()[:8]}')
