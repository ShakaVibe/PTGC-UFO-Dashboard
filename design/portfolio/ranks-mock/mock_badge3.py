import io, contextlib, sys
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
sys.path.insert(0,S)
with contextlib.redirect_stdout(io.StringIO()):
    import mock_badge as B, mock_badge2 as B2
box=B.box
def h1(c,r):   # plaque, "HOLDER RANK" stacked inside, number right
    return f'<span class="hq hq1 {c}"><span class="st"><small>HOLDER</small><small>RANK</small></span><b>#{r}</b></span>'
def h2(c,r):   # plaque, "HOLDER RANK" on one line, number right, a hairline between
    return f'<span class="hq hq2 {c}"><small>HOLDER RANK</small><i></i><b>#{r}</b></span>'
def h3(c,r):   # plaque, the words ABOVE the number, centred (taller, like a mini tile)
    return f'<span class="hq hq3 {c}"><small>HOLDER RANK</small><b>#{r}</b></span>'
CSS='''
.hq{display:inline-flex;align-items:center;gap:9px;border-radius:7px;border:1px solid rgba(242,211,91,.45);background:rgba(0,0,0,.45);box-shadow:inset 0 1px 0 rgba(255,255,255,.08);padding:0 12px;height:34px}
.hq.u{border-color:rgba(124,252,0,.4)}
.hq small{font:700 9.5px Orbitron;letter-spacing:.16em;color:rgba(255,255,255,.5);white-space:nowrap}
.hq b{font:900 20px Orbitron;letter-spacing:.02em;color:#F2D35B;line-height:1}.hq.u b{color:#8DFF3A}
.hq1 .st{display:flex;flex-direction:column;line-height:1.15}.hq1 .st small{font-size:8.5px}
.hq2 i{width:1px;height:18px;background:rgba(255,255,255,.18)}
.hq3{flex-direction:column;gap:2px;height:auto;padding:6px 14px 5px}.hq3 small{font-size:8.5px}.hq3 b{font-size:21px}
'''
OPTS=[('H1 — STACKED WORDS','The quiet plaque with "HOLDER / RANK" stacked in tiny caps at the left (B4’s words), the number at the right. One line tall.',h1),
      ('H2 — ONE LINE','"HOLDER RANK" on one line, a hairline, then the number. One line tall, a little wider.',h2),
      ('H3 — WORDS ABOVE','"HOLDER RANK" over the number, centred — a small tile. Two lines tall, the number gets more room.',h3)]
head=B.head.replace('Rank badge designs for the League box — B1 shield · B2 medal coin · B3 plaque · B4 rank ring · B5 hex','Rank badge — the quiet plaque with the words HOLDER RANK: H1 stacked · H2 one line · H3 words above')
out=head+B.CSS+B2.CSS+CSS+'''</style></head><body><div class="pf2"><div class="wrap">'''+B.DEFS+'''
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">RANK BADGE — THE QUIET PLAQUE, WITH "HOLDER RANK"</h1>
<div class="note">The P1 plaque (hairline, dark fill, no glow) carrying the words from B4. The line’s own label stays "ALL 5 WALLETS AS ONE" (or nothing when it is one wallet, since the badge says it). PTGC left, UFO right.</div>'''
for i,(k,note,f) in enumerate(OPTS):
    if i: out+='<div class="sep"></div>'
    out+=f'<div class="opt">{k}</div><span class="note">{note}</span><div class="pair">{box("p",f)}{box("u",f,"7","651.70K","6")}</div>'
out+='</div></div></body></html>'
out=out.replace('src="logos/','src="../../logos/')
open(S+'/repo/design/portfolio/mock-rank-badge-v3.html','w').write(out); print('written',len(out))
