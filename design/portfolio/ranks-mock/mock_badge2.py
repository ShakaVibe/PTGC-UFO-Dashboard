import re, io, contextlib, sys
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
sys.path.insert(0,S)
with contextlib.redirect_stdout(io.StringIO()):
    import mock_badge as B
box=B.box
def c1(c,r):   # P1 — the plaque, quieter: no glow, hairline border, dark fill, gold number only
    return f'<span class="pq1 {c}"><small>RANK</small><b>#{r}</b></span>'
def c2(c,r):   # P2 — the number alone, large, with "RANK" stacked tiny at its left
    return f'<span class="pq2 {c}"><span class="st"><small>HOLDER</small><small>RANK</small></span><b>#{r}</b></span>'
def c3(c,r):   # P3 — plaque with a thin left accent bar in the token colour
    return f'<span class="pq3 {c}"><i></i><small>RANK</small><b>#{r}</b></span>'
def c4(c,r):   # P4 — the plaque with a tiny token logo instead of the word
    logo='../../logos/ptgc/logo-512.webp' if c=='p' else '../../logos/ufo/logo-512.webp'
    return f'<span class="pq4 {c}"><img src="{logo}" alt=""><b>#{r}</b></span>'
CSS='''
/* all four: one line tall, no glow, no gradient fill — only a hairline and the number carries the colour */
.pq1,.pq3,.pq4{display:inline-flex;align-items:center;gap:8px;height:32px;padding:0 12px;border-radius:7px;border:1px solid rgba(242,211,91,.45);background:rgba(0,0,0,.45);box-shadow:inset 0 1px 0 rgba(255,255,255,.08)}
.pq1.u,.pq3.u,.pq4.u{border-color:rgba(124,252,0,.4)}
.pq1 small,.pq3 small{font:700 10px Orbitron;letter-spacing:.16em;color:rgba(255,255,255,.5)}
.pq1 b,.pq2 b,.pq3 b,.pq4 b{font:900 20px Orbitron;letter-spacing:.02em;color:#F2D35B;line-height:1}
.pq1.u b,.pq2.u b,.pq3.u b,.pq4.u b{color:#8DFF3A}
/* P2 */
.pq2{display:inline-flex;align-items:center;gap:8px;padding:0 4px}
.pq2 .st{display:flex;flex-direction:column;line-height:1.1;text-align:right}
.pq2 .st small{font:700 8.5px Orbitron;letter-spacing:.14em;color:rgba(255,255,255,.45)}
.pq2 b{font-size:24px}
/* P3 */
.pq3{padding-left:0;overflow:hidden}.pq3 i{display:block;width:4px;height:32px;background:#F2D35B;margin-right:2px}.pq3.u i{background:#8DFF3A}
/* P4 */
.pq4 img{width:18px;height:18px;border-radius:50%;opacity:.9}
'''
OPTS=[('P1 — PLAQUE, QUIET','The B3 plaque without the glow or the metal shine: a hairline border, dark fill, "RANK" in small grey caps, the number in gold / green.',c1),
      ('P2 — NUMBER ONLY','No box at all: a bigger gold / green number with "HOLDER RANK" stacked in tiny grey caps beside it. Lightest of the four.',c2),
      ('P3 — ACCENT BAR','P1 with a thin gold / green bar down the left edge instead of a coloured border — the colour is in the bar and the number only.',c3),
      ('P4 — TOKEN LOGO','P1 with the small PTGC / UFO coin in place of the word "RANK" — matches the breakdown badges, which already carry the coin.',c4)]
head=B.head.replace('Rank badge designs for the League box — B1 shield · B2 medal coin · B3 plaque · B4 rank ring · B5 hex','Rank badge, quieter — four takes on the plaque: P1 quiet · P2 number only · P3 accent bar · P4 token logo')
out=head+B.CSS+CSS+'''</style></head><body><div class="pf2"><div class="wrap">'''+B.DEFS+'''
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">RANK BADGE — QUIETER, FROM THE PLAQUE</h1>
<div class="note">Four takes on B3, all one line tall, no glow. Your numbers (5 wallets as one, #14 · 694.87M more to pass #13); PTGC left, UFO right.</div>'''
for i,(k,note,f) in enumerate(OPTS):
    if i: out+='<div class="sep"></div>'
    out+=f'<div class="opt">{k}</div><span class="note">{note}</span><div class="pair">{box("p",f)}{box("u",f,"7","651.70K","6")}</div>'
out+='</div></div></body></html>'
out=out.replace('src="logos/','src="../../logos/')
open(S+'/repo/design/portfolio/mock-rank-badge-v2.html','w').write(out); print('written',len(out))
