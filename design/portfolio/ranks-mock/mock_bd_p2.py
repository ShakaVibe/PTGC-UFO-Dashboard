import io, contextlib, sys, html, re
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
sys.path.insert(0,S)
with contextlib.redirect_stdout(io.StringIO()):
    import mock_ranks as M, mock_ranks3 as G, mock_badge as B, mock_badge2 as B2
rows,T,SP,SU,SPEND,asone,PX,ab,usd=M.rows,M.T,M.SP,M.SU,M.SPEND,M.asone,M.PX,M.ab,M.usd
LOGO=G.LOGO
def nxt(x): return 'Nobody above you' if x['next'] is None else f'▲ {ab(x["next"]+1)} more to pass #{x["r"]-1:,}'
# the P2 look, per token: coin · stacked "PTGC / RANK" · big number · "more to pass" under
def p2(tk,x,sm=False):
    c='p' if tk=='PTGC' else 'u'
    if not x: return f'<div class="bG {c} none"><img src="{LOGO[tk]}" alt=""><span class="k">{tk} RANK</span><b>—</b><small>not holding</small></div>'
    return (f'<div class="bG {c}{" sm" if sm else ""}"><img src="{LOGO[tk]}" alt=""><span class="k">{tk} RANK</span><b>#{x["r"]:,}</b>'
            + ('' if sm else f'<em>{nxt(x)}</em>') + '</div>')
def share(r):
    ps=r['p']*PX['PTGC']/r['tot']*100 if r['tot'] else 0
    return f'<div class="bar"><span><b style="width:{ps:.0f}%;background:#F2D35B"></b><b style="width:{100-ps:.0f}%;background:#7CFC00"></b></span><small>{r["tot"]/T*100:.1f}%</small></div>'
cell=lambda v,d,k:f'<span class="tk {k}">{ab(v) if v else "—"}</span><span class="us">{usd(d) if v else ""}</span>'
def header():
    chips=(f'<span class="chip">Total<b>{usd(T)}</b></span><span class="chip rk"><i style="background:#F2D35B"></i>Best PTGC rank<b>#{min(r["rp"]["r"] for r in rows if r["rp"]):,}</b></span>'
           f'<span class="chip rk"><i style="background:#7CFC00"></i>Best UFO rank<b>#{min(r["ru"]["r"] for r in rows if r["ru"]):,}</b></span>')
    return (f'<button class="pf2-foldh" aria-expanded="true"><span class="ic"><img src="../../logos/portfolio/pf-wallet.webp" alt=""></span>'
            f'<span class="tt"><b class="oh">PER-WALLET BREAKDOWN</b><span class="mt">{len(rows)} wallets · holder rank, PTGC, pending, UFO and the total for each</span></span><span class="chips">{chips}</span><span class="chev"></span></button>')
SORTS='<div class="pf2-bds"><span>Sort</span><button class="on">Value</button><button>Name</button><button>Added</button><button>PTGC rank</button><button>UFO rank</button></div>'
FOOT='<div class="rkfoot">Ranks count every wallet holding PTGC or UFO, except liquidity pools and other contracts, the burn addresses, the token contracts and the DAO and UFO OA wallets. Your balance is read live; the holder list is refreshed every 2 hours · list read 25 min ago</div>'
def table():
    h=[f'<table class="pf2-bdt rk"><colgroup><col style="width:13%"><col style="width:41%"><col style="width:11%"><col style="width:11%"><col style="width:10%"><col style="width:14%"></colgroup><thead><tr><th>WALLET</th><th class="rkh">HOLDER RANK</th>'
       f'<th><img src="{LOGO["PTGC"]}" alt="">PTGC</th><th><img src="{LOGO["PTGC"]}" alt="">PENDING TO CLAIM</th><th><img src="{LOGO["UFO"]}" alt="">UFO</th><th>TOTAL · SHARE</th></tr></thead><tbody>']
    for r in rows:
        h.append(f'<tr style="--c:{r["c"]}"><td><div class="n">{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></td>'
                 f'<td class="rkc">{p2("PTGC",r["rp"])}{p2("UFO",r["ru"])}</td>'
                 f'<td>{cell(r["p"],r["p"]*PX["PTGC"],"p")}</td><td>{cell(r["pend"],r["pend"]*PX["PTGC"],"p")}</td><td>{cell(r["u"],r["u"]*PX["UFO"],"u")}</td>'
                 f'<td><span class="tot">{usd(r["tot"])}</span>{share(r)}</td></tr>')
    h.append(f'<tr class="sub tot"><td><div class="n">ALL WALLETS</div></td><td class="rkc"><div class="asone">As one wallet</div>{p2("PTGC",asone["PTGC"],True)}{p2("UFO",asone["UFO"],True)}</td>'
             f'<td>{cell(SP,SP*PX["PTGC"],"p")}</td><td>{cell(SPEND,SPEND*PX["PTGC"],"p")}</td><td>{cell(SU,SU*PX["UFO"],"u")}</td>'
             f'<td><span class="tot">{usd(T)}</span><div class="bar"><span><b style="width:50%;background:#F2D35B"></b><b style="width:50%;background:#7CFC00"></b></span><small>100%</small></div></td></tr></tbody></table>')
    return ''.join(h)
def cards():
    h=['<div class="pf2-bdc on">']
    for r in rows:
        ps=r['p']*PX['PTGC']/r['tot']*100 if r['tot'] else 0
        h.append(f'<div class="wc"><div class="top"><div class="who"><div class="n"><i style="background:{r["c"]}"></i>{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></div><div class="tv">{usd(r["tot"])}<small>{r["tot"]/T*100:.1f}% of portfolio</small></div></div>'
                 f'<div class="sb"><b style="width:{ps:.1f}%;background:#F2D35B"></b><b style="width:{100-ps:.1f}%;background:#7CFC00"></b></div>'
                 f'<div class="rkm">{p2("PTGC",r["rp"])}{p2("UFO",r["ru"])}</div>'
                 f'<div class="cols"><div class="cl"><div class="l">PTGC</div>{cell(r["p"],r["p"]*PX["PTGC"],"p")}</div><div class="cl"><div class="l">Pending to claim</div>{cell(r["pend"],r["pend"]*PX["PTGC"],"p")}</div><div class="cl"><div class="l">UFO</div>{cell(r["u"],r["u"]*PX["UFO"],"u")}</div></div></div>')
    h.append(f'<div class="wsum"><span class="l">ALL WALLETS</span><b>{usd(T)}</b></div><div class="rkm one"><span class="asone">As one wallet</span>{p2("PTGC",asone["PTGC"],True)}{p2("UFO",asone["UFO"],True)}</div></div>')
    return ''.join(h)
CSS='''
.wrap{padding:28px 40px 60px;max-width:1300px}
.opt{font-family:Orbitron;font-weight:900;font-size:13px;letter-spacing:.14em;color:#04060a;background:#F2D35B;display:inline-block;padding:5px 12px;border-radius:5px}
.note{display:block;margin:8px 0 14px;color:rgba(255,255,255,.72);font-size:16px;font-weight:600;max-width:1180px}
.sep{height:1px;background:linear-gradient(90deg,transparent,rgba(242,211,91,.5),transparent);margin:36px 0 26px}
.pf2-foldh .chip.rk b{font-family:Orbitron;font-size:12px;letter-spacing:.04em}
.rkfoot{margin:12px 4px 2px;font:600 13.5px Rajdhani;color:rgba(255,255,255,.5)}
.asone{font:700 11.5px Rajdhani;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.5);margin-bottom:6px}
.pf2-bdt.rk{table-layout:fixed}.pf2-bdt th.rkh,.pf2-bdt td.rkc{text-align:left}.pf2-bdt td.rkc{padding-top:10px;padding-bottom:10px;white-space:normal}
/* the live pill (.bG, from mock-ranks-v3 G2) with the label "PTGC RANK" / "UFO RANK" */
.bG .k{letter-spacing:.08em}
.pf2-bdt .bG{flex-wrap:nowrap;padding:4px 10px 4px 5px;border-radius:999px}.pf2-bdt .bG em{flex-basis:auto;padding-left:0;margin:0 0 0 auto;white-space:nowrap}
.bG.sm{width:max-content;padding:3px 10px 3px 4px}.bG.sm b{font-size:12.5px}.bG.sm img{width:16px;height:16px}
/* phone cards */
.pf2-bdc.on{display:grid;gap:10px;max-width:390px}
.rkm{display:flex;flex-direction:column;gap:6px;margin:0 0 10px}.rkm .bG+.bG{margin-top:0}
.rkm .bG{border-radius:11px;padding:6px 11px 6px 6px}.rkm .bG em{flex-basis:100%;margin:-2px 0 0;padding-left:25px}
.rkm.one{margin:8px 0 0;flex-direction:row;flex-wrap:wrap;align-items:center}.rkm.one .asone{flex-basis:100%;margin:0}
.rkm .bG.sm{border-radius:999px;padding:3px 10px 3px 4px}
.phone{width:390px}
'''
head=open(S+'/repo/design/portfolio/mock-ranks-v3.html').read().split('</style></head>')[0]
head=re.sub(r'<title>.*?</title>','<title>Per-wallet breakdown — the pill badges labelled PTGC RANK / UFO RANK — desktop + phone — 2026-10-21</title>',head)
out=head+G.CSS+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">PER-WALLET BREAKDOWN — "PTGC RANK" / "UFO RANK" BADGES</h1>
<div class="note">The badges as they are live today, with the label changed to "PTGC RANK" / "UFO RANK" (his ask). The League box line gets the P2 look.</div>
<div class="opt">DESKTOP</div>'''
out+=f'<section class="pf2-pn pf2-fold">{header()}<div class="pf2-foldb pf2-bd">{SORTS}{table()}{FOOT}</div></section>'
out+='<div class="sep"></div><div class="opt">PHONE (390 px)</div><span class="note">The same two badges in each wallet card, "more to pass" wrapping under the rank.</span>'
out+=f'<div class="phone"><section class="pf2-pn pf2-fold"><div class="pf2-foldb pf2-bd">{cards()}</div></section></div>'
out+='</div></div></body></html>'
out=out.replace('src="logos/','src="../../logos/')
open(S+'/repo/design/portfolio/mock-ranks-bd-p2.html','w').write(out); print('written',len(out))
