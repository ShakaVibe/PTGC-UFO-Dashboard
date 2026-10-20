import re, sys
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
sys.path.insert(0,S)
import mock_ranks as M
src=open(S+'/cards.html').read()
i=src.index('<section class="pf2-tk u"')
P0,U0=src[src.index('<section class="pf2-tk p"'):i], src[i:src.rindex('</div>')]
def sub1(s,pat,rep,flags=0):
    n=len(re.findall(pat,s,flags)); assert n>=1,('miss',pat[:60]); return re.sub(pat,rep,s,count=1,flags=flags)
def crw(lst):
    return '<div class="pf2-crw">'+''.join(f'<span title="{n} × {k.title()}"><img src="logos/panels/sea-{k}.webp?v=4" alt="{k.title()}">×{n}</span>' for k,n in lst)+'</div>'
def ring(parts):   # [(color, fraction)]
    C=2*3.14159265*46; off=0; out=''
    for c,f in parts:
        d=C*f; out+=f'<circle cx="60" cy="60" r="46" fill="none" stroke="{c}" stroke-width="22" stroke-dasharray="{max(d-1.5,0.5):.2f} {C:.2f}" stroke-dashoffset="{-off:.2f}" transform="rotate(-90 60 60)"></circle>'; off+=d
    return f'<svg viewBox="0 0 120 120" aria-hidden="true" style="width:132px;height:132px"><circle cx="60" cy="60" r="46" fill="none" stroke="rgba(255,255,255,.06)" stroke-width="22"></circle><g style="filter:drop-shadow(rgba(255,255,255,.18) 0 0 5px)">{out}</g></svg>'
def lg2(rows):
    return '<div class="pf2-lg2">'+''.join(f'<div class="r"><i style="background:{c}"></i><span>{n}</span><b>{a}</b><span class="usd">{u}</span><em>{p}</em></div>' for c,n,a,u,p in rows)+'</div>'
def base_p(s):
    s=sub1(s,r'<span>\$0\.0<sub[^>]*>3</sub>1420</span>','<span>$0.0<sub style="font-size:.6em">4</sub>1734</span>')
    s=sub1(s,r'\+3\.21% \(24h\)','+12.52% (24h)')
    s=sub1(s,r'<div class="pf2-crw">.*?</div>',crw([('whale',1),('shark',1),('dolphin',6),('squid',5),('turtle',3),('shrimp',7)]))
    s=sub1(s,r'(Total holdings</div><div class="v"[^>]*>)[^<]*(</div><div class="s">)[^<]*',r'\g<1>3.88B\g<2>$67,358.73')
    s=sub1(s,r'(Lifetime earned</div><div class="v"[^>]*>)[^<]*(</div><div class="s">)[^<]*',r'\g<1>1.17B\g<2>$20,254.83')
    s=sub1(s,r'<svg viewBox="0 0 120 120".*?</svg>',ring([('#F2D35B',1.0)]),re.S)
    s=sub1(s,r'<div class="pf2-lg2">.*?</div></div></div>',lg2([('#F2D35B','Liquid','3.88B','$67,358.73','100.0%')])+'</div>',re.S)
    s=sub1(s,r'(<div class="pf2-fl" style="width: )[^;]*;',r'\g<1>1.8%;'); s=sub1(s,r'(<i class="pf2-tip" style="left: )[^;]*;',r'\g<1>1.8%;')
    s=sub1(s,r'<div class="pf2-lgbf">.*?</div>','<div class="pf2-lgbf"><span><b>1.8%</b> to <b class="c2">Poseidon</b></span><span>need <b>29.45B</b> ≈ $510,641</span></div>')
    for k,v,u,p in (('Staking','681.16M','$11,811.27','58.3%'),('Locking','76.14M','$1,320.21','6.5%'),('Reflections','410.80M','$7,123.34','35.2%')):
        s=sub1(s,rf'(<div class="l">{k}</div><div class="v"[^>]*>)[^<]*(</div><div class="s">)[^<]*(</div><div class="p">)[^<]*',rf'\g<1>{v}\g<2>{u}\g<3>{p} of earned')
    s=sub1(s,r'<div class="pf2-spot">.*?</div></div></div>','',re.S)       # nothing to claim on his wallet
    s=sub1(s,r'<div class="pf2-extw">.*?</div></div>','',re.S)              # no locks
    return s
def base_u(s):
    s=sub1(s,r'<span>\$0\.0<sub[^>]*>3</sub>1420</span>','<span>$0.0<sub style="font-size:.6em">5</sub>2315</span>')
    s=sub1(s,r'\+3\.21% \(24h\)','+6.74% (24h)')
    s=sub1(s,r'<div class="pf2-crw">.*?</div>',crw([('whale',1),('shark',8),('squid',4),('shrimp',9)]))
    s=sub1(s,r'(Total holdings</div><div class="v"[^>]*>)[^<]*(</div><div class="s">)[^<]*',r'\g<1>18.04B\g<2>$41,764.77')
    s=sub1(s,r'(Lifetime earned</div><div class="v"[^>]*>)[^<]*(</div><div class="s">)[^<]*',r'\g<1>367.16M\g<2>$849.97')
    s=sub1(s,r'<svg viewBox="0 0 120 120".*?</svg>',ring([('#7CFC00',0.98),('#22D3EE',0.02)]),re.S)
    s=sub1(s,r'<div class="pf2-lg2">.*?</div></div></div>',lg2([('#7CFC00','Principal','17.67B','$40,914.80','98.0%'),('#22D3EE','From reflections','367.16M','$849.97','2.0%')])+'</div>',re.S)
    s=sub1(s,r'(<div class="pf2-fl" style="width: )[^;]*;',r'\g<1>8.9%;'); s=sub1(s,r'(<i class="pf2-tip" style="left: )[^;]*;',r'\g<1>8.9%;')
    s=sub1(s,r'<div class="pf2-lgbf">.*?</div>','<div class="pf2-lgbf"><span><b>8.9%</b> to <b class="c2">Poseidon</b></span><span>need <b>81.96B</b> ≈ $189,735</span></div>')
    s=sub1(s,r'(<div class="l">Reflections</div><div class="v"[^>]*>)[^<]*(</div><div class="s">)[^<]*',r'\g<1>367.16M\g<2>$849.97')
    s=sub1(s,r'≈ 24\.56%','≈ 2.48%'); s=sub1(s,r'width: 24\.5564%','width: 2.48%')
    s=sub1(s,r'Your <b>16\.61B</b> of the <b>67\.63B</b>','Your <b>18.04B</b> of the <b>727.97B</b>')
    s=sub1(s,r'<div class="pf2-lkd x">.*?</div>','',re.S)
    return s
P,U=base_p(P0),base_u(U0)
# ---- the ranks (real, from today's lists) ----
L={k:M.R[k] for k in ('PTGC','UFO')}
def info(tk,bal):
    x=M.rank(tk,bal); r=x['r']; below=bal-L[tk][r-1] if r-1<len(L[tk]) else None
    return dict(r=r,n=x['n'],top=M.topt(x['top']),md=M.medal(r),ahead=M.ab(x['next']+1),behind=M.ab(below) if below and below>0 else None)
RP,RU=info('PTGC',3.88e9),info('UFO',18.04e9)
LOGO={'p':'logos/ptgc/logo-512.webp','u':'logos/ufo/logo-512.webp'}
def med(x,c): return f'<i class="medal{" u" if c=="u" else ""}">{x["md"]}</i>' if x['md'] else ''
def H1(s,c,x):   # header pill under the price
    pill=f'<div class="rk1 {c}"><span class="k">HOLDER RANK</span><b>#{x["r"]:,}</b>{med(x,c)}</div>'
    return sub1(s,r'(<div class="c"><span class="pos">[^<]*</span></div>)',lambda m:m.group(1)+pill)
def H2(s,c,x):   # third tile
    tile=(f'<div class="pf2-bx {"gold" if c=="p" else "grn"} big rk2"><span class="bic rkic">#</span><div><div class="lb">Holder rank</div>'
          f'<div class="v">#{x["r"]:,}</div><div class="s">{x["top"]} of {x["n"]:,}</div></div></div>')
    s=sub1(s,r'<div class="pf2-t4 t2">','<div class="pf2-t4 t2 t3">')
    return sub1(s,r'(Lifetime earned</div><div class="v"[^>]*>[^<]*</div><div class="s">[^<]*</div></div></div>)',lambda m:m.group(1)+tile)
def H3(s,c,x):   # inside the League box
    row=(f'<div class="rk3 {c}"><div class="l"><span class="k">HOLDER RANK</span><b>#{x["r"]:,}</b><small>of {x["n"]:,} · {x["top"]}</small>{med(x,c)}</div>'
         f'<div class="r">▲ <b>{x["ahead"]}</b> more to pass #{x["r"]-1:,}</div></div>')
    return sub1(s,r'(<div class="pf2-lgbf">.*?</div>)',lambda m:m.group(1)+row)
def H4(s,c,x,tk):  # spotlight at the foot of the card
    ladder=(f'<div class="lad"><div class="st up"><span>#{x["r"]-1:,}</span><em>▲ {x["ahead"]} ahead of you</em></div>'
            f'<div class="st me"><span>#{x["r"]:,}</span><em>YOU</em></div>'
            + (f'<div class="st dn"><span>#{x["r"]+1:,}</span><em>▼ {x["behind"]} behind you</em></div>' if x['behind'] else '') + '</div>')
    spot=(f'<div class="pf2-spot rk4{" u" if c=="u" else ""}"><img src="{LOGO[c]}" alt=""><div class="b"><div class="k"><i aria-hidden="true"></i>YOUR {tk} HOLDER RANK</div>'
          f'<div class="v">#{x["r"]:,}<small>of {x["n"]:,} {tk} holders</small>{med(x,c)}</div><div class="u">{x["top"]} · liquidity pools, burn and contracts left out</div>{ladder}</div></div>')
    # end of the earned-by-source block
    if c=='p':
        return sub1(s,r'(<div class="pf2-src3">(?:<div class="pf2-src [a-z]+">(?:<div[^>]*>[^<]*</div>){4}</div>){3}</div>)',lambda m:m.group(1)+spot)
    return sub1(s,r'(that earns rewards</span></div></div></div>)',lambda m:m.group(1)+spot)
CSS='''
.wrap{padding:28px 40px 60px;max-width:1300px}
.opt{font-family:Orbitron;font-weight:900;font-size:13px;letter-spacing:.14em;color:#04060a;background:#F2D35B;display:inline-block;padding:5px 12px;border-radius:5px}
.note{display:block;margin:8px 0 14px;color:rgba(255,255,255,.72);font-size:16px;font-weight:600;max-width:1180px}
.sep{height:1px;background:linear-gradient(90deg,transparent,rgba(242,211,91,.5),transparent);margin:40px 0 28px}
.medal{font:900 9.5px Orbitron;font-style:normal;letter-spacing:.08em;padding:2px 6px;border-radius:4px;color:#1a1200;background:linear-gradient(180deg,#FFE58A,#E0B53A);white-space:nowrap}
.medal.u{background:linear-gradient(180deg,#B8FF6A,#5ED000);color:#061000}
/* H1 */
.rk1{display:inline-flex;align-items:center;gap:7px;margin-top:8px;padding:4px 9px;border-radius:999px;border:1px solid rgba(242,211,91,.45);background:rgba(0,0,0,.4);font:700 11.5px Rajdhani;letter-spacing:.1em;color:rgba(255,255,255,.65)}
.rk1.u{border-color:rgba(124,252,0,.4)}
.rk1 b{font:900 15px Orbitron;letter-spacing:.03em;color:#F2D35B}.rk1.u b{color:#8DFF3A}
/* H2 */
.pf2-t4.t2.t3{grid-template-columns:repeat(3,minmax(0,1fr))}
.rkic{width:58px;height:58px;flex:none;display:flex;align-items:center;justify-content:center;border-radius:50%;font:900 30px Orbitron;color:#1a1200;background:radial-gradient(circle at 35% 30%,#FFF2B0,#E0B53A 60%,#8a6a10);box-shadow:0 0 18px rgba(242,211,91,.35)}
.pf2-bx.grn .rkic{color:#061000;background:radial-gradient(circle at 35% 30%,#E6FFB8,#5ED000 60%,#2a6a00);box-shadow:0 0 18px rgba(124,252,0,.3)}
.rk2 .v{font-family:Orbitron!important;letter-spacing:.02em}
/* H3 */
.rk3{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:12px;padding-top:11px;border-top:1px solid rgba(255,255,255,.08);flex-wrap:wrap}
.rk3 .l{display:flex;align-items:center;gap:8px}
.rk3 .k{font:700 12px Rajdhani;letter-spacing:.14em;color:rgba(255,255,255,.6)}
.rk3 b{font:900 17px Orbitron;color:#F2D35B}.rk3.u b{color:#8DFF3A}
.rk3 small{font:600 13.5px Rajdhani;color:rgba(255,255,255,.6)}
.rk3 .r{font:600 13.5px Rajdhani;color:rgba(255,255,255,.6)}.rk3 .r b{font:700 14px Rajdhani;color:#fff}
/* H4 */
.pf2-spot.rk4{margin-top:12px}
.pf2-spot.rk4:not(.u){border-color:rgba(242,211,91,.6);background:linear-gradient(135deg,rgba(242,211,91,.17),rgba(178,107,255,.06) 55%,rgba(0,0,0,.3));box-shadow:0 0 30px rgba(242,211,91,.12)}
.pf2-spot.rk4:not(.u) .k{color:#F6E98A}.pf2-spot.rk4:not(.u) .k i{background:#F2D35B;box-shadow:0 0 10px #F2D35B}
.pf2-spot.rk4:not(.u)>img{border-radius:50%;filter:drop-shadow(0 0 14px rgba(242,211,91,.45))}
.pf2-spot.rk4 .v small{font-size:20px;color:rgba(255,255,255,.75);font-weight:600}
.pf2-spot.rk4 .v{display:flex;align-items:center;gap:10px;font-family:Orbitron}
.pf2-spot.rk4 .v small{font-family:Rajdhani}
.lad{display:flex;flex-direction:column;gap:4px;margin-top:10px}
.lad .st{display:flex;align-items:center;gap:10px;font:600 13.5px Rajdhani;color:rgba(255,255,255,.6);padding:4px 10px;border-radius:8px;background:rgba(0,0,0,.25)}
.lad .st span{font:900 12.5px Orbitron;min-width:50px;color:rgba(255,255,255,.7)}
.lad .st.me{background:rgba(242,211,91,.14);border:1px solid rgba(242,211,91,.45);color:#fff}.lad .st.me span{color:#F2D35B}.lad .st.me em{font:900 11px Orbitron;letter-spacing:.12em;font-style:normal;color:#F2D35B}
.rk4.u .lad .st.me{background:rgba(124,252,0,.12);border-color:rgba(124,252,0,.4)}.rk4.u .lad .st.me span,.rk4.u .lad .st.me em{color:#8DFF3A}
.lad em{font-style:normal}
'''
OPTS=[('H1','A small HOLDER RANK pill under the price in each card’s header — the lightest touch, always in view.',lambda:(H1(P,'p',RP),H1(U,'u',RU))),
      ('H2','A third tile beside Total holdings and Lifetime earned — the rank as a headline number with its top % and the holder count.',lambda:(H2(P,'p',RP),H2(U,'u',RU))),
      ('H3','Inside the LEAGUE box, under the league bar — league and rank together ("where you stand"), with "more to pass" on the right.',lambda:(H3(P,'p',RP),H3(U,'u',RU))),
      ('H4','A spotlight panel at the foot of each card (fills the empty space under PTGC’s Earned by source): the big rank, top %, and a mini ladder — the holder above you, you, the holder below.',lambda:(H4(P,'p',RP,'PTGC'),H4(U,'u',RU,'UFO')))]
head=open(S+'/repo/design/portfolio/mock-ranks-v3.html').read().split('</style></head>')[0]
head=re.sub(r'<title>.*?</title>','<title>Holder rank on the token cards when ONE wallet is counted — H1 header pill · H2 third tile · H3 in the League box · H4 spotlight — 2026-10-20</title>',head)
out=head+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">HOLDER RANK ON THE PTGC / UFO CARDS — ONE WALLET COUNTED</h1>
<div class="note">The cards from your screenshot (3.88B PTGC, 18.04B UFO). Real ranks from today’s holder lists: <b>PTGC #12</b> of 12,114 (top 0.10%),
<b>UFO #7</b> of 4,906 (top 0.14%). Shown only when exactly ONE wallet is counted — with 2+ wallets the cards are a sum (see the question at the bottom).</div>'''
for n,(k,note,f) in enumerate(OPTS):
    p,u=f()
    if n: out+='<div class="sep"></div>'
    out+=f'<div class="opt">OPTION {k}</div><span class="note">{note}</span><div class="pf2-tok2">{p}{u}</div>'
out+='''<div class="sep"></div><div class="note"><b>With 2 or more wallets counted:</b> either hide it (the Per-wallet breakdown has each wallet’s rank), or show the
same thing as "ALL 3 WALLETS AS ONE · #28". Your call.</div></div></div></body></html>'''
out=out.replace('src="logos/','src="../../logos/')
open(S+'/repo/design/portfolio/mock-ranks-single-v1.html','w').write(out); print('written',len(out),RP,RU)
