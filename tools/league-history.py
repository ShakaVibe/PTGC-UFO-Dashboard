#!/usr/bin/env python3
"""LEAGUE HISTORY window (2026-10-24, design/creatures/README.md) — built HIDDEN behind the faint bottom-right dot (Shaka: "I dont
want to make it live yet.. hide this behind a small faint dot in the bottom right corner of the dashboard"). Idempotent, from the
repo root:   python3 tools/league-history.py   (twice: the second run must print "0 edit(s)")
  - index.html: the CSS (tools/league-history/lh.css) between /* LH:CSS:BEGIN */ … END, the JSX (tools/league-history/lh.jsx:
    LEAGUE_HISTORY_LIVE, LeagueHistoryModal, LhDot …) between /* LH:JSX:BEGIN */ … END; LS.LH_PER; the Dashboard's state, the
    window + the dot; the creature strip as the button WHEN LEAGUE_HISTORY_LIVE (false today — the strip renders as before).
  - the pipeline: scripts/build-league-history.mjs (committed with this) as step `league-history` in the holder-ranks lane after
    rank-history; data/league-history.json in the commit list; the step in the `only` description.
Going live = LEAGUE_HISTORY_LIVE=true in tools/league-history/lh.jsx, re-run this script (the dot goes, the strip is the button).
Edit the two fragment files, never the spliced copy in index.html — the next run overwrites it.
"""
import hashlib
P = 'index.html'
s = open(P, encoding='utf-8').read()
n = 0

def splice(tag, body, anchor):
    global s, n
    b, e = f'/* LH:{tag}:BEGIN */', f'/* LH:{tag}:END */'
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

splice('CSS', open('tools/league-history/lh.css', encoding='utf-8').read(), '    /* T100:CSS:BEGIN */')
splice('JSX', open('tools/league-history/lh.jsx', encoding='utf-8').read(), '    /* T100:JSX:BEGIN */')
edit("""      HANDOFF_TOKEN:'ptgc_last_token',""",
     """      LH_PER:'grays_lh_per_v1',                   // the League History window's period ('7D' … 'ALL'), remembered per device (2026-10-24)
      HANDOFF_TOKEN:'ptgc_last_token',""")
edit("""      const[showTop100,setShowTop100]=useState(false);""",
     """      const[showTop100,setShowTop100]=useState(false);
      const[showLeagueHist,setShowLeagueHist]=useState(false);   // LEAGUE HISTORY window (2026-10-24) — the dot until LEAGUE_HISTORY_LIVE, then the creature strip""")
edit("""          {!TOP100_LIVE&&activeTab==='dashboard'&&<T1Dot""",
     """          {/* LEAGUE HISTORY (2026-10-24): hidden behind the faint bottom-right dot until LEAGUE_HISTORY_LIVE; then the creature strip opens it */}
          {showLeagueHist&&<LeagueHistoryModal token={token} onClose={()=>setShowLeagueHist(false)} onLeagues={()=>setShowTierInfo(true)}/>}
          {!LEAGUE_HISTORY_LIVE&&activeTab==='dashboard'&&<LhDot token={token} onOpen={()=>setShowLeagueHist(true)}/>}
          {!TOP100_LIVE&&activeTab==='dashboard'&&<T1Dot""")
edit("""):hdrV2?<CreatureStripV2 tiers={holderTiers}/>:(""",
     """):hdrV2?(LEAGUE_HISTORY_LIVE?<button type="button" className="lh-strip" onClick={()=>setShowLeagueHist(true)} aria-label="League history: every sea creature over time"><CreatureStripV2 tiers={holderTiers}/><span className="lh-go" aria-hidden="true">HISTORY {'\\u203A'}</span></button>:<CreatureStripV2 tiers={holderTiers}/>):(""")
if n: open(P, 'w', encoding='utf-8').write(s)
ix_sha = hashlib.sha256(s.encode()).hexdigest()[:8]

# ---- the pipeline step
def fedit(path, old, new):
    global n
    t = open(path, encoding='utf-8').read()
    if new in t: return
    assert t.count(old) == 1, f'{path}: anchor x{t.count(old)}: {old[:70]!r}'
    open(path, 'w', encoding='utf-8').write(t.replace(old, new)); n += 1
R = 'scripts/pipeline-run.mjs'
fedit(R, "  'rank-history':    { run: 'scripts/build-rank-history.mjs', ",
         "  'league-history':  { run: 'scripts/build-league-history.mjs' },   // 2026-10-24: the League History window — the rank archive walked day by day; writes only when the archive has a new day\n"
         "  'rank-history':    { run: 'scripts/build-rank-history.mjs', ")
fedit(R, "steps: ['holder-ranks', 'rank-history', 'top-stakers'] },",
         "steps: ['holder-ranks', 'rank-history', 'league-history', 'top-stakers'] },")
Y = '.github/workflows/data-pipeline.yml'
fedit(Y, "holder-ranks, rank-history, top-stakers. Empty", "holder-ranks, rank-history, league-history, top-stakers. Empty")
fedit(Y, "            data/rank-history/PTGC.json data/rank-history/UFO.json data/rank-index \\\n",
         "            data/rank-history/PTGC.json data/rank-history/UFO.json data/rank-index \\\n            data/league-history.json \\\n")
print(f'league-history: {n} edit(s), index.html sha256 {ix_sha}')
