#!/usr/bin/env python3
"""The burn wallet counts as a sea creature again (2026-10-24, Shaka: "what happened to the poseidon???? … it was the burn wallet" →
picked "Count it as Poseidon"). Audit IV e13 made the creature counts PEOPLE ONLY, which took out 0x…0369 — PTGC's only Poseidon
(46.34 B, 13.9 % of the starting supply). Now everything stays people-only EXCEPT the burn wallet, which counts in the league its
balance puts it in (PTGC: Poseidon; UFO: 96.06 B = 9.6 % → a Whale until it passes 10 %), and is marked with a small 🔥.
  - scripts/build-token-allocation.mjs: the tiers + the burn wallet; `burnIn` (its league) in the file.
  - index.html: the strip's 🔥 on that creature (hover: "includes the burn wallet"); the live fallback scan counts 0x…0369 too.
  - (League History: scripts/build-league-history.mjs + tools/league-history/lh.jsx carry it themselves — every day's counts include
    the burn wallet, `burnIn` per basis, a 🔥 on its league's card; this script only re-splices them.)
Idempotent, from the repo root:   python3 tools/burn-poseidon.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

TA, IX, LHB, LHJ = 'scripts/build-token-allocation.mjs', 'index.html', 'scripts/build-league-history.mjs', 'tools/league-history/lh.jsx'
TIER_ORDER = "const TIER_OF = pct => pct >= 10 ? 'Poseidon' : pct >= 1 ? 'Whale' : pct >= 0.1 ? 'Shark' : pct >= 0.01 ? 'Dolphin' : null;"
# ---- the allocation file
edit(TA, "function tiersFromRanks(sym, supply) {", TIER_ORDER + "\nfunction tiersFromRanks(sym, supply, burnedTok) {")
edit(TA, "  return { tiers: { ...counts, SquidAndBelow: Math.max(0, t.holders - counted) }, asOf: t.readAt };",
         "  /* 2026-10-24 (Shaka: \"what happened to the poseidon … it was the burn wallet\"): people only, PLUS the burn wallet in its league */\n"
         "  const burnIn = burnedTok > 0 ? TIER_OF(burnedTok / sup * 100) : null;\n"
         "  if (burnIn) counts[burnIn]++;\n"
         "  return { tiers: { ...counts, SquidAndBelow: Math.max(0, t.holders - counted), burnIn }, asOf: t.readAt };")
edit(TA, "  const tr = tiersFromRanks(sym, cfg.supply);", "  const tr = tiersFromRanks(sym, cfg.supply, toTok(burned));")
edit(TA, "tiersSource: tiersOk ? 'holder-ranks (people only)' :", "tiersSource: tiersOk ? 'holder-ranks (people only) + the burn wallet' :")

# ---- the page: the strip's flame + the fallback scan
edit(IX, "applyTiers({Poseidon:t.Poseidon||0,Whale:t.Whale||0,Shark:t.Shark||0,Dolphin:t.Dolphin||0,SquidAndBelow:(t.SquidAndBelow!=null?t.SquidAndBelow:null),ok:true,partial:false,error:null,asOfTs},true);",
         "applyTiers({Poseidon:t.Poseidon||0,Whale:t.Whale||0,Shark:t.Shark||0,Dolphin:t.Dolphin||0,SquidAndBelow:(t.SquidAndBelow!=null?t.SquidAndBelow:null),burnIn:t.burnIn||null,ok:true,partial:false,error:null,asOfTs},true);")
edit(IX, "<span key={k}><span className=\"e\">{e?<SeaIcon e={e} size={38}/>",
         "<span key={k} title={tiers&&tiers.burnIn===k?'Includes the burn wallet (0x…0369)':undefined}><span className=\"e\">{tiers&&tiers.burnIn===k&&<span className=\"bw\" aria-label=\"includes the burn wallet\">{'\\u{1F525}'}</span>}{e?<SeaIcon e={e} size={38}/>")
edit(IX, "    .p2 .p2-strip>span{display:flex;align-items:center;gap:8px}",
         "    .p2 .p2-strip>span{display:flex;align-items:center;gap:8px}\n"
         "    .p2 .p2-strip .e{position:relative}.p2 .p2-strip .bw{position:absolute;right:-7px;top:-9px;font-size:13px;line-height:1;filter:drop-shadow(0 0 4px rgba(255,120,0,.8));pointer-events:none}   /* 2026-10-24: the burn wallet's league */")
edit(IX, "              if(TIER_NOT_PEOPLE.has(holderAddr)||holder.address?.is_contract)continue;   // e13: people only",
         "              if((TIER_NOT_PEOPLE.has(holderAddr)&&holderAddr!=='0x0000000000000000000000000000000000000369')||holder.address?.is_contract)continue;   // e13: people only — plus the burn wallet (2026-10-24, Shaka)")

# ---- League History: the burn wallet is in scripts/build-league-history.mjs (schema 3) and tools/league-history/lh.jsx directly
#      (those two files are the source — edited by hand in the same session), spliced by tools/league-history.py below.
out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'burn-poseidon: {n} edit(s); index.html {sha(IX)}, build-token-allocation {sha(TA)}, build-league-history {sha(LHB)}')
