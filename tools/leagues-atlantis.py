#!/usr/bin/env python3
"""Leagues art → the Atlantis kit (Shaka, 2026-10-23: "use this art work and instructions … this should change the ones in socials as
well as the ones when someone pushes leagues buttons"; "make the background a little darker around the area where the logo and the
price is"). Idempotent, from the repo root:   python3 tools/leagues-atlantis.py   (twice: the second run prints "0 edit(s)")

Kit (design/leagues/atlantis/ — CLAUDE_INSTRUCTIONS.md + the four PNGs as he sent them):
  logos/leagues/lg-atl-split.webp  ← 01_PTGC_UFO_SPLIT (2172×724)  — the Socials combined card (LeaguesCombinedCard, .lgc)
  logos/leagues/lg-atl-ptgc.webp   ← 03_PTGC_GOLD (1160 wide)      — the PTGC Leagues window header + foot (TierInfoModal, PfTierInfoModal)
  logos/leagues/lg-atl-ufo.webp    ← 04_UFO_GREEN (1160 wide)      — the UFO Leagues window
Rules from the kit, applied: the giant whale / shark hero art is gone (the creatures live in the tier rows), the art is an atmospheric
background under a ~35 % navy overlay, darker behind the coin + price, restrained gold (PTGC) / green (UFO), no data drawn into the
art, phone crops keep the token's coloured side. No number, tier or calculation is touched.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new and new in s: return
    if not new and old not in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

IX = 'index.html'
# ---- the Leagues window (index TierInfoModal; tools/pf-v2.py copies these lg-* rules into portfolio.html) ----
edit(IX, "    .lg-hd .sky{position:absolute;inset:0;background:url(logos/leagues/lg-sea-wide.webp) center 28%/cover no-repeat}",
     "    .lg-hd .sky{position:absolute;inset:0;background:url(logos/leagues/lg-atl-ptgc.webp) 30% 42%/cover no-repeat}   /* 2026-10-23: the Atlantis kit — PTGC gold ruins at the left, the deep-blue centre behind the coin */\n"
     "    .lg-m.ufo .lg-hd .sky{background-image:url(logos/leagues/lg-atl-ufo.webp);background-position:70% 42%}   /* UFO: the green side */")
edit(IX, "    .lg-hd .fade{position:absolute;inset:0;background:radial-gradient(ellipse 34% 40% at 50% 62%,rgba(0,0,0,.5),rgba(0,0,0,0)),linear-gradient(180deg,rgba(0,0,0,.3) 0%,rgba(0,0,0,0) 30%,rgba(6,7,10,.15) 72%,#06070a 100%)}",
     "    .lg-hd .fade{position:absolute;inset:0;background:radial-gradient(ellipse 30% 46% at 50% 58%,rgba(2,5,12,.72),rgba(2,5,12,.4) 60%,rgba(2,5,12,0) 100%),linear-gradient(180deg,rgba(3,8,20,.42) 0%,rgba(3,8,20,.32) 40%,rgba(6,7,10,.45) 75%,#06070a 100%)}   /* 2026-10-23: a ~35 % navy over the art, darker behind the coin + price (Shaka) */")
edit(IX, "    .lg-ft{position:absolute;left:0;right:0;bottom:0;height:120px;background:url(logos/leagues/lg-sea-wide.webp) center 95%/cover no-repeat;opacity:.45;",
     "    .lg-ft{position:absolute;left:0;right:0;bottom:0;height:120px;background:url(logos/leagues/lg-atl-ptgc.webp) 30% 92%/cover no-repeat;opacity:.35;")
edit(IX, "    .lg-m.ufo .lg-cl{", "    .lg-m.ufo .lg-ft{background-image:url(logos/leagues/lg-atl-ufo.webp);background-position:70% 92%}\n    .lg-m.ufo .lg-cl{")
edit(IX, "      .lg-hd{height:240px}.lg-hd .lg-coin{--u:.46px;top:58px}", "      .lg-hd .sky{background-position:24% 40%}.lg-m.ufo .lg-hd .sky{background-position:76% 40%}   /* phones: keep the token's coloured ruins in frame */\n      .lg-hd{height:240px}.lg-hd .lg-coin{--u:.46px;top:58px}")
OLD_HD = """<div className="sky" aria-hidden="true"></div><img className="whale" src={`logos/leagues/lg-whale.webp?v=${LG_ART_V}`} alt="" aria-hidden="true"/><img className="shark" src={`logos/leagues/lg-shark.webp?v=${LG_ART_V}`} alt="" aria-hidden="true"/><div className="fade" aria-hidden="true"></div>"""
edit(IX, OLD_HD, """<div className="sky" aria-hidden="true"></div><div className="fade" aria-hidden="true"></div>{/* 2026-10-23: the Atlantis art; no whale / shark hero (the creatures live in the rows) */}""")
edit('tools/pf-v2/PfLeagues.jsx', """<div className="sky" aria-hidden="true"></div><img className="whale" src={`logos/leagues/lg-whale.webp?v=${PF_LG_ART_V}`} alt="" aria-hidden="true"/><img className="shark" src={`logos/leagues/lg-shark.webp?v=${PF_LG_ART_V}`} alt="" aria-hidden="true"/>""",
     """<div className="sky" aria-hidden="true"></div><div className="fade" aria-hidden="true"></div>{/* 2026-10-23: = index.html — the Atlantis art, no whale / shark */}""")

# ---- the Socials combined card (.lgc, 1080×1350) ----
edit(IX, "    .lgc{--g:242,201,76;--u:124,252,0;position:relative;overflow:hidden;width:1080px;height:1350px;background:#04070e url(logos/leagues/lg-sea.webp) center top/100% auto no-repeat;",
     "    .lgc{--g:242,201,76;--u:124,252,0;position:relative;overflow:hidden;width:1080px;height:1350px;background:#04070e url(logos/leagues/lg-atl-split.webp) center top/1560px auto no-repeat;")   # 2026-10-23: PTGC gold left → deep blue → UFO green right
edit(IX, """          <div className="tint tl" aria-hidden="true"></div><div className="tint tl2" aria-hidden="true"></div><div className="tint tr" aria-hidden="true"></div><div className="tint tr2" aria-hidden="true"></div>
          <div className="clipin" aria-hidden="true"><img className="cre whale" src={`logos/leagues/lg-whale.webp?v=${LG_ART_V}`} alt=""/><img className="cre shark" src={`logos/leagues/lg-shark.webp?v=${LG_ART_V}`} alt=""/></div>
          <div className="veil" aria-hidden="true"></div>""", """          {/* 2026-10-23 (the Atlantis kit): the split art carries the gold / green itself — no colour tints, no whale / shark hero */}
          <div className="veil" aria-hidden="true"></div>""")
edit(IX, "    .lgc .veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(2,5,12,.28) 0%,rgba(2,5,12,0) 10%,rgba(2,5,12,0) 36%,rgba(2,5,12,.55) 46%,rgba(2,5,12,.8) 56%,rgba(2,5,12,.84) 92%,rgba(2,5,12,.72) 100%);pointer-events:none}",
     "    .lgc .veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(2,6,16,.45) 0%,rgba(2,6,16,.32) 14%,rgba(2,6,16,.34) 30%,rgba(2,5,12,.66) 40%,rgba(2,5,12,.86) 48%,rgba(2,5,12,.88) 92%,rgba(2,5,12,.8) 100%);pointer-events:none}   /* 2026-10-23: ~35 % navy over the art, the table area dark */")
edit(IX, "    .lgc .tk1::before{content:'';position:absolute;left:50%;top:50%;width:300px;height:300px;transform:translate(-50%,-46%);border-radius:50%;background:radial-gradient(circle,rgba(4,6,12,.72) 0%,rgba(4,6,12,.45) 45%,rgba(4,6,12,0) 70%);z-index:0}",
     "    .lgc .tk1::before{content:'';position:absolute;left:50%;top:50%;width:400px;height:400px;transform:translate(-50%,-44%);border-radius:50%;background:radial-gradient(circle,rgba(2,5,12,.86) 0%,rgba(2,5,12,.7) 38%,rgba(2,5,12,.35) 58%,rgba(2,5,12,0) 72%);z-index:0}   /* 2026-10-23: darker behind each coin + price (Shaka) */")

out = subprocess.run([sys.executable, 'tools/pf-v2.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'leagues-atlantis: {n} edit(s), index {sha(IX)}, portfolio {sha("portfolio.html")}')
