import re
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
head=open(S+'/repo/design/portfolio/mock-ranks-v3.html').read().split('</style></head>')[0]
head=re.sub(r'<title>.*?</title>','<title>Rank badge designs for the League box — B1 shield · B2 medal coin · B3 plaque · B4 rank ring · B5 hex — 2026-10-21</title>',head)
LEAGUE={'p':('Shark','Whale','71.9%','841.96M','$16,822',71.9,'#F2D35B','logos/panels/sea-shark.webp?v=4','logos/panels/sea-whale.webp?v=4'),
        'u':('Whale','Poseidon','8.9%','81.96B','$189,735',8.9,'#7CFC00','logos/panels/sea-whale.webp?v=4','logos/panels/sea-trident.webp?v=4')}
def box(c,badge,rank='14',gap='694.87M',nxt='13'):
    cur,nx,pct,need,usd,w,hexc,i1,i2=LEAGUE[c]
    return f'''<section class="pf2-tk {c} cut"><div class="pf2-lgw"><div class="pf2-lgb">
  <div class="pf2-lgbh"><span class="lb">League</span><span class="cur"><img src="{i1}" alt="">{cur}</span><button class="lnk">Leagues</button></div>
  <div class="pf2-bar"><img src="{i1}" alt=""><div class="pf2-trk"><div class="pf2-fl" style="width:{w}%"></div><i class="pf2-tip" style="left:{w}%"></i></div><img src="{i2}" alt=""></div>
  <div class="pf2-lgbf"><span><b>{pct}</b> to <b class="c2">{nx}</b></span><span>need <b>{need}</b> ≈ {usd}</span></div>
  <div class="pf2-rk3 {c} bd"><div class="l"><span class="k">ALL 5 WALLETS AS ONE</span>{badge(c,rank)}</div><div class="r">▲ <strong>{gap}</strong> more to pass #{nxt}</div></div>
</div></div></section>'''
# ---- the badge designs ----
def b1(c,r):   # shield
    return f'<span class="rkS {c}"><svg viewBox="0 0 40 46" aria-hidden="true"><path d="M20 2 L37 8 V22 C37 33 29 41 20 44 C11 41 3 33 3 22 V8 Z"/><path class="in" d="M20 6 L33.5 10.8 V22 C33.5 30.6 27.4 37.4 20 40.2 C12.6 37.4 6.5 30.6 6.5 22 V10.8 Z"/></svg><b><i>#</i>{r}</b></span>'
def b2(c,r):   # medal coin with ribbon
    return f'<span class="rkM {c}"><span class="rib" aria-hidden="true"></span><span class="coin"><small>RANK</small><b>{r}</b></span></span>'
def b3(c,r):   # metal plaque
    return f'<span class="rkP {c}"><small>RANK</small><b>#{r}</b></span>'
def b4(c,r):   # ring + big number (like the Total tile's pills)
    return f'<span class="rkR {c}"><span class="ring"><b>{r}</b></span><span class="tx"><small>HOLDER</small><small>RANK</small></span></span>'
def b5(c,r):   # hexagon
    return f'<span class="rkH {c}"><svg viewBox="0 0 52 46" aria-hidden="true"><polygon points="14,2 38,2 50,23 38,44 14,44 2,23"/><polygon class="in" points="16.5,6 35.5,6 45.3,23 35.5,40 16.5,40 6.7,23"/></svg><b><i>#</i>{r}</b></span>'
CSS='''
.wrap{padding:28px 40px 60px;max-width:1300px}
.opt{font-family:Orbitron;font-weight:900;font-size:13px;letter-spacing:.14em;color:#04060a;background:#F2D35B;display:inline-block;padding:5px 12px;border-radius:5px}
.note{display:block;margin:8px 0 14px;color:rgba(255,255,255,.72);font-size:16px;font-weight:600;max-width:1180px}
.sep{height:1px;background:linear-gradient(90deg,transparent,rgba(242,211,91,.5),transparent);margin:36px 0 26px}
.pair{display:grid;grid-template-columns:1fr 1fr;gap:22px}
.pf2-tk.cut{padding:16px;min-height:0!important;height:auto!important;display:block!important}.pf2-tk.cut .pf2-lgw{margin:0}
.pf2-rk3{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px;padding-top:11px;border-top:1px solid rgba(255,255,255,.08);flex-wrap:wrap}
.pf2-rk3 .l{display:flex;align-items:center;gap:12px}
.pf2-rk3 .k{font:700 12px Rajdhani;letter-spacing:.14em;color:rgba(255,255,255,.6);white-space:nowrap}
.pf2-rk3 .r{font:600 13.5px Rajdhani;color:rgba(255,255,255,.6)}.pf2-rk3 .r strong{font-weight:700;color:#fff}
.pf2-rk3.bd{padding-top:10px;margin-top:10px}
/* shared metals */
:root{--gA:#FFF2B0;--gB:#F2D35B;--gC:#B8891A;--gD:#5a3f06;--nA:#E6FFB8;--nB:#8DFF3A;--nC:#3E9E00;--nD:#153f00}
/* B1 shield */
.rkS{position:relative;display:inline-flex;align-items:center;justify-content:center;width:48px;height:55px;flex:none;filter:drop-shadow(0 0 10px rgba(242,211,91,.35))}
.rkS.u{filter:drop-shadow(0 0 10px rgba(124,252,0,.3))}
.rkS svg{position:absolute;inset:0;width:100%;height:100%}
.rkS svg path{fill:url(#gold)}.rkS.u svg path{fill:url(#grn)}
.rkS svg path.in{fill:#0b0d12}
.rkS b{position:relative;font:900 15px Orbitron;color:#F2D35B;letter-spacing:.02em;margin-top:1px}.rkS.u b{color:#8DFF3A}.rkS b i{font-style:normal;font-size:10px;opacity:.75;margin-right:1px}
/* B2 medal */
.rkM{display:inline-flex;flex-direction:column;align-items:center;flex:none;position:relative}
.rkM .rib{width:22px;height:14px;background:linear-gradient(90deg,#c0392b,#e74c3c 50%,#c0392b);clip-path:polygon(0 0,100% 0,100% 100%,50% 70%,0 100%);margin-bottom:-4px}
.rkM.p .rib{background:linear-gradient(90deg,#7b1fa2,#B26BFF 50%,#7b1fa2)}.rkM.u .rib{background:linear-gradient(90deg,#0e6b8a,#22D3EE 50%,#0e6b8a)}
.rkM .coin{width:50px;height:50px;border-radius:50%;display:flex;flex-direction:column;align-items:center;justify-content:center;background:radial-gradient(circle at 35% 30%,var(--gA),var(--gB) 45%,var(--gC) 80%,var(--gD));box-shadow:0 0 0 2px rgba(0,0,0,.6),0 0 0 3.5px var(--gB),0 0 16px rgba(242,211,91,.45),inset 0 -3px 6px rgba(0,0,0,.35);color:#1a1200}
.rkM.u .coin{background:radial-gradient(circle at 35% 30%,var(--nA),var(--nB) 45%,var(--nC) 80%,var(--nD));box-shadow:0 0 0 2px rgba(0,0,0,.6),0 0 0 3.5px var(--nB),0 0 16px rgba(124,252,0,.4),inset 0 -3px 6px rgba(0,0,0,.35);color:#061000}
.rkM .coin small{font:900 7px Orbitron;letter-spacing:.14em;opacity:.8;line-height:1}
.rkM .coin b{font:900 17px Orbitron;letter-spacing:.01em;line-height:1.05}
/* B3 plaque */
.rkP{display:inline-flex;align-items:baseline;gap:7px;padding:5px 12px 5px 10px;border-radius:7px;flex:none;background:linear-gradient(180deg,rgba(242,211,91,.22),rgba(242,211,91,.06));border:1px solid rgba(242,211,91,.6);box-shadow:inset 0 1px 0 rgba(255,255,255,.35),inset 0 -1px 0 rgba(0,0,0,.5),0 0 14px rgba(242,211,91,.22)}
.rkP.u{background:linear-gradient(180deg,rgba(124,252,0,.2),rgba(124,252,0,.05));border-color:rgba(124,252,0,.55);box-shadow:inset 0 1px 0 rgba(255,255,255,.3),inset 0 -1px 0 rgba(0,0,0,.5),0 0 14px rgba(124,252,0,.2)}
.rkP small{font:900 9.5px Orbitron;letter-spacing:.16em;color:rgba(255,255,255,.6)}
.rkP b{font:900 22px Orbitron;letter-spacing:.02em;background:linear-gradient(180deg,#FFF6C8,#F2D35B 55%,#C9A227);-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 1px 0 rgba(0,0,0,.6))}
.rkP.u b{background:linear-gradient(180deg,#EFFFD0,#8DFF3A 55%,#4FB300);-webkit-background-clip:text;background-clip:text;color:transparent}
/* B4 ring */
.rkR{display:inline-flex;align-items:center;gap:8px;flex:none}
.rkR .ring{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;justify-content:center;border:3px solid #F2D35B;background:radial-gradient(circle,rgba(242,211,91,.22),rgba(0,0,0,.4) 70%);box-shadow:0 0 14px rgba(242,211,91,.45),inset 0 0 10px rgba(242,211,91,.25)}
.rkR.u .ring{border-color:#8DFF3A;background:radial-gradient(circle,rgba(124,252,0,.2),rgba(0,0,0,.4) 70%);box-shadow:0 0 14px rgba(124,252,0,.4),inset 0 0 10px rgba(124,252,0,.22)}
.rkR .ring b{font:900 17px Orbitron;color:#fff;letter-spacing:.01em}
.rkR .tx{display:flex;flex-direction:column;line-height:1.15}.rkR .tx small{font:900 9px Orbitron;letter-spacing:.14em;color:#F2D35B}.rkR.u .tx small{color:#8DFF3A}
/* B5 hex */
.rkH{position:relative;display:inline-flex;align-items:center;justify-content:center;width:58px;height:52px;flex:none;filter:drop-shadow(0 0 10px rgba(242,211,91,.35))}
.rkH.u{filter:drop-shadow(0 0 10px rgba(124,252,0,.3))}
.rkH svg{position:absolute;inset:0;width:100%;height:100%}
.rkH svg polygon{fill:url(#gold)}.rkH.u svg polygon{fill:url(#grn)}.rkH svg polygon.in{fill:#0b0d12}
.rkH b{position:relative;font:900 15px Orbitron;color:#F2D35B;letter-spacing:.02em}.rkH.u b{color:#8DFF3A}.rkH b i{font-style:normal;font-size:10px;opacity:.75;margin-right:1px}
'''
DEFS='''<svg width="0" height="0" style="position:absolute"><defs>
<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FFF2B0"/><stop offset=".45" stop-color="#F2D35B"/><stop offset=".8" stop-color="#B8891A"/><stop offset="1" stop-color="#5a3f06"/></linearGradient>
<linearGradient id="grn" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#E6FFB8"/><stop offset=".45" stop-color="#8DFF3A"/><stop offset=".8" stop-color="#3E9E00"/><stop offset="1" stop-color="#153f00"/></linearGradient>
</defs></svg>'''
OPTS=[('B1 — SHIELD','A gold / green shield with the rank inside — the "rank" reads like a crest. 48 px tall, so the line grows a little.',b1),
      ('B2 — MEDAL','A coin-style medal with a ribbon: "RANK" over the number, metallic gradient, token-coloured ribbon.',b2),
      ('B3 — PLAQUE','A metal nameplate: "RANK" caps + a big gold / green number with a brushed-metal shine. Stays one line tall.',b3),
      ('B4 — RING','The number in a glowing ring, "HOLDER RANK" stacked beside it — matches the page’s round icons.',b4),
      ('B5 — HEXAGON','A hex badge, gaming-style, number inside.',b5)]
out=head+CSS+'''</style></head><body><div class="pf2"><div class="wrap">'''+DEFS+'''
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">RANK BADGE — FIVE LOOKS FOR THE LEAGUE BOX LINE</h1>
<div class="note">Your numbers from the screenshot (5 wallets as one, #14, 694.87M more to pass #13). Same badge would be used in the breakdown column and on the phone cards. PTGC on the left, UFO on the right.</div>'''
for i,(k,note,f) in enumerate(OPTS):
    if i: out+='<div class="sep"></div>'
    out+=f'<div class="opt">{k}</div><span class="note">{note}</span><div class="pair">{box("p",f)}{box("u",f,"7","651.70K","6")}</div>'
out+='''<div class="sep"></div><div class="note"><b>Big numbers:</b> #1,234 and #12,345 fit in B3 and B4 as they are; B1 / B2 / B5 shrink the type for four and five digits.</div></div></div></body></html>'''
out=out.replace('src="logos/','src="../../logos/')
open(S+'/repo/design/portfolio/mock-rank-badge-v1.html','w').write(out); print('written',len(out))
