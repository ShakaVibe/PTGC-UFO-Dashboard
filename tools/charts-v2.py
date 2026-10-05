#!/usr/bin/env python3
"""Charts page skin (2026-10-05): the Calculators page's treatment — his gold space art as a fixed plate under a 62 % veil, a
black band under the header, "Grays Charts" in the Socials Hub's metallic title, the chart card a touch more solid.
Run from the repo root on a clean charts.html: python3 tools/charts-v2.py  (refuses to run twice)."""
import sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
p=root/'charts.html'; s=p.read_text()
if 'cp-page' in s: sys.exit('already applied')
def rep(old,new,count=1):
    global s
    n=s.count(old); assert n==count,(old[:70],n); s=s.replace(old,new)
css='''  /* CHARTS PAGE SKIN (2026-10-05, Shaka: "the same treatment" as the Calculators page — tools/calc-v2.py, design/calculators/README.md):
     his art as a FIXED plate under a 62 % veil, the Hub-style metallic title, the chart card a touch more solid. cp-* only. */
  .cp-page{position:relative;background:#000}
  .cp-art{position:fixed;inset:0;z-index:0;pointer-events:none;background:#000 url(logos/calculators/calc-bg.jpg) center top/cover no-repeat}
  .cp-art::after{content:'';position:absolute;inset:0;background:rgba(0,0,0,.62)}
  .cp-page>:not(.cp-art){position:relative;z-index:1}
  .cp-band{height:0;position:relative}
  .cp-band::before{content:'';position:absolute;left:0;right:0;top:0;height:170px;pointer-events:none;background:linear-gradient(180deg,#000 0%,rgba(0,0,0,.6) 45%,rgba(0,0,0,0) 100%)}
  .cp-ttl{position:relative;text-align:center;margin:-6px auto 26px;padding:22px 40px 18px;max-width:900px}
  .cp-ttl::before{content:"";position:absolute;inset:0;border-radius:50%;background:radial-gradient(ellipse 55% 60% at 50% 48%,rgba(0,0,0,.86) 0%,rgba(0,0,0,.72) 40%,rgba(0,0,0,.35) 70%,rgba(0,0,0,0) 100%);filter:blur(6px);z-index:0}
  .cp-ttl>*{position:relative;z-index:1}
  .cp-ttl h2{margin:0;line-height:1}
  .cp-t{font-family:'Orbitron',monospace;font-weight:900;font-size:64px;line-height:1;letter-spacing:.01em;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;filter:drop-shadow(0 3px 3px #000) drop-shadow(0 0 22px rgba(0,0,0,.9))}
  .cp-t.g{background-image:linear-gradient(180deg,#FFF3B0 0%,#F7D35A 40%,#C9921A 62%,#F2C94C 100%)}
  .cp-t.w{background-image:linear-gradient(180deg,#FFF 0%,#E6E6E6 45%,#8C8C8C 60%,#DDD 100%);margin-left:.22em}
  .cp-ttl p{text-shadow:0 1px 3px #000;color:rgba(255,255,255,.58)!important;font-size:16px!important}
  .cp-page .chart-card{background:rgba(8,8,10,.86);box-shadow:0 0 40px rgba(212,175,55,.06),0 10px 40px -10px rgba(0,0,0,.9)}
  .cp-page .chart-sub-tab,.cp-page .share-menu-wrap button{backdrop-filter:blur(4px)}
  @media(max-width:640px){
    .cp-art{position:absolute;inset:auto 0 auto 0;top:0;height:1000px}
    .cp-art::before{content:'';position:absolute;left:0;right:0;bottom:0;height:260px;z-index:1;background:linear-gradient(180deg,rgba(0,0,0,0),#000)}
    .cp-band::before{height:110px}
    .cp-ttl{padding:16px 8px 12px;margin-bottom:18px}
    .cp-t{font-size:30px;letter-spacing:0}.cp-t.w{margin-left:.18em}
  }
'''
rep('</style>\n',css+'</style>\n')
rep('<div class="min-h-screen">\n','<div class="min-h-screen cp-page">\n  <div class="cp-art" aria-hidden="true"></div>\n')
rep('''  <div class="max-w-5xl mx-auto px-3 sm:px-6 py-8">

    <!-- Title — same as "CALCULATOR" heading -->
    <div class="text-center mb-8">
      <h2 class="text-3xl sm:text-4xl font-bold text-white font-orbitron tracking-widest">CHARTS</h2>
      <div class="w-24 sm:w-32 h-0.5 mx-auto mt-1.5 rounded-full" style="background:linear-gradient(90deg,transparent,rgba(212,175,55,0.8),transparent)"></div>
''','''  <div class="cp-band" aria-hidden="true"></div>
  <div class="max-w-5xl mx-auto px-3 sm:px-6 py-8">

    <!-- Title — the Calculators page's (2026-10-05): the Hub's metallic Orbitron, "Grays" gold + "Charts" silver -->
    <div class="cp-ttl mb-8">
      <h2><span class="cp-t g">Grays</span><span class="cp-t w">Charts</span></h2>
''')
# the two disabled "—" placeholder sub-tabs (price / volume) go; the one button sits centred (Shaka, 2026-10-05)
import re
s,n=re.subn(r'\n        <button class="relative overflow-hidden rounded-xl font-orbitron font-bold text-sm sm:text-base transition-all chart-sub-tab" data-tab="(price|volume)"[^\n]*</button>','',s); assert n==2,n
p.write_text(s); print('applied',len(s))
