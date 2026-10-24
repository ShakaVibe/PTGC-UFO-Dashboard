#!/usr/bin/env python3
"""Portfolio: the PTGC "READY TO CLAIM" box shows for every wallet, 0 included (2026-10-24, Shaka: "if a wallet has no stakes or
locks, its just this big blank space... I still want to show the box but show just they have 0 to claim").
Before: the box needed pending > 0 or something staked, so a wallet that had claimed everything and unstaked left the Earned by
source panel half empty beside UFO's spotlight. Now: once any counted wallet has read, the box is always there — 0 PTGC, an empty
Staking / Locks bar with "Staking 0 · Locks 0", and a line saying why there is nothing.
Idempotent, from the repo root:   python3 tools/pf-claim-zero.py   (twice: the second run must print "0 edit(s)")
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

PV = 'tools/pf-v2/PortfolioV2.jsx'
edit(PV, "                {(pt.totalPending>0||pt.staked>0)&&(()=>{const tp=pt.totalPending||0,ps=pt.pendingStake||0,pl=pt.pendingLocks||0;return(",
         "                {/* 2026-10-24 (Shaka: no stakes or locks left a big blank space): always shown once a wallet has read — 0 included */}\n"
         "                {(anyData||pt.totalPending>0||pt.staked>0)&&(()=>{const tp=pt.totalPending||0,ps=pt.pendingStake||0,pl=pt.pendingLocks||0;return(")
edit(PV, "<>Nothing to claim yet {'\\u2014'} rewards build up while you stake</>}</div>",
         "(pt.staked>0||pt.locks.length>0)?<>Nothing to claim yet {'\\u2014'} rewards build up while you stake</>:<>Nothing to claim {'\\u2014'} no PTGC staked or locked in {counted.length===1?'this wallet':'these wallets'}</>}</div>")
edit(PV, "                      {tp>0&&<><div className=\"bar\" aria-hidden=\"true\"><i style={{width:ps/tp*100+'%',background:'#B26BFF'}}></i><i style={{width:pl/tp*100+'%',background:'#EC4899'}}></i></div>",
         "                      {<><div className=\"bar\" aria-hidden=\"true\"><i style={{width:(tp>0?ps/tp*100:0)+'%',background:'#B26BFF'}}></i><i style={{width:(tp>0?pl/tp*100:0)+'%',background:'#EC4899'}}></i></div>")

out = subprocess.run([sys.executable, 'tools/pf-v2.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
print(f'pf-claim-zero: {n} edit(s), portfolio.html {hashlib.sha256(open("portfolio.html", "rb").read()).hexdigest()[:8]}')
