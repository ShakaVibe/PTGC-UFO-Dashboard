#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka: "under the share button or to the left of it, a Leagues button — when clicked it pops up the
leagues chart for the token you are on"): a LEAGUES button under SHARE in the window's header; it opens the dashboard's Leagues window
(TierInfoModal — the same one as the Burn panel's "Leagues" button) ON TOP of League History (Escape / ✕ closes only it). It shows
while the window's token is the dashboard's token (the Leagues window reads that token's live price / burn / holders).
Idempotent, from the repo root:   python3 tools/lh-leagues-btn.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
J, C, IX, LH = 'tools/league-history/lh.jsx', 'tools/league-history/lh.css', 'index.html', 'tools/league-history.py'
MOUNT_OLD = "{showLeagueHist&&<LeagueHistoryModal token={token} onClose={()=>setShowLeagueHist(false)}/>}"
MOUNT_NEW = "{showLeagueHist&&<LeagueHistoryModal token={token} onClose={()=>setShowLeagueHist(false)} onLeagues={()=>setShowTierInfo(true)}/>}"
edit(LH, MOUNT_OLD, MOUNT_NEW)   # the splicer's own copy of the mount line, so a re-run never adds a second one
edit(IX, MOUNT_OLD, MOUNT_NEW)
edit(J, "const LeagueHistoryModal=({token,onClose})=>{", "const LeagueHistoryModal=({token,onClose,onLeagues})=>{")
edit(J, "{rows&&<button type=\"button\" className=\"lh-cam\"",
        "{onLeagues&&tok===token&&<button type=\"button\" className=\"lh-lgb\" onClick={onLeagues} aria-label={`Open the ${tok} Leagues window`}><img src={lhSea('trident')} alt=\"\"/><span>LEAGUES</span></button>}\n"
        "              {rows&&<button type=\"button\" className=\"lh-cam\"")
CSS = """
    /* 2026-10-24 (Shaka): the LEAGUES button under SHARE — opens the dashboard's Leagues window for this token */
    .lh-lgb{position:absolute;right:70px;top:67px;z-index:3;height:38px;padding:0 14px 0 8px;border-radius:19px;border:1px solid rgba(var(--rgb),.5);background:rgba(0,0,0,.55);
      color:var(--a2);font:700 12px 'Orbitron',sans-serif;letter-spacing:.14em;display:flex;align-items:center;gap:7px;cursor:pointer}
    .lh-lgb img{width:26px;height:26px;object-fit:contain;filter:drop-shadow(0 0 5px rgba(var(--rgb),.5))}
    .lh-lgb:hover,.lh-cam:hover{background:rgba(var(--rgb),.16);border-color:rgba(var(--rgb),.85)}
    .lh-lgb:focus-visible{outline:2px solid var(--a2);outline-offset:2px}
    @media(max-width:700px){.lh-lgb{right:62px;top:58px;height:36px;width:38px;padding:0;justify-content:center}.lh-lgb span{display:none}}
"""
s = open(C, encoding='utf-8').read()
if "the LEAGUES button under SHARE" not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1
out = subprocess.run([sys.executable, LH], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-leagues-btn: {n} edit(s); index.html {sha(IX)}, lh.jsx {sha(J)}, lh.css {sha(C)}, league-history.py {sha(LH)}')
