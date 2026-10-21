import sys, re, html, io, contextlib
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
sys.path.insert(0,S)
with contextlib.redirect_stdout(io.StringIO()):
    import mock_ranks as M, mock_ranks3 as G, mock_single as H
rows,T,SP,SU,asone,PX,ab,usd,topt,medal=M.rows,M.T,M.SP,M.SU,M.asone,M.PX,M.ab,M.usd,M.topt,M.medal
LOGO=G.LOGO
def badge(tk,x):   # the G2 badge; on a phone it wraps "more to pass" under the rank
    c='p' if tk=='PTGC' else 'u'
    if not x: return f'<div class="bG {c} none"><img src="{LOGO[tk]}" alt=""><span class="k">{tk}</span><b>—</b><small>not holding</small></div>'
    md=medal(x['r'])
    return (f'<div class="bG {c}{" md" if md else ""}"><img src="{LOGO[tk]}" alt=""><span class="k">{tk}</span><b>#{x["r"]:,}</b><small>{topt(x["top"])}</small>'
            + (f'<i class="medal{" u" if c=="u" else ""}">{md}</i>' if md else '') + f'<em>{G.nxt(x)}</em></div>')
def card(r):
    ps=r['p']*PX['PTGC']/r['tot']*100 if r['tot'] else 0; us=r['u']*PX['UFO']/r['tot']*100 if r['tot'] else 0
    cell=lambda v,d,k:f'<span class="tk {k}">{ab(v) if v else "—"}</span><span class="us">{usd(d) if v else ""}</span>'
    return (f'<div class="wc"><div class="top"><div class="who"><div class="n"><i style="background:{r["c"]}"></i>{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></div>'
            f'<div class="tv">{usd(r["tot"])}<small>{r["tot"]/T*100:.1f}% of portfolio</small></div></div>'
            f'<div class="sb"><b style="width:{ps:.1f}%;background:#F2D35B"></b><b style="width:{us:.1f}%;background:#7CFC00"></b></div>'
            f'<div class="rkm">{badge("PTGC",r["rp"])}{badge("UFO",r["ru"])}</div>'
            f'<div class="cols"><div class="cl"><div class="l">PTGC</div>{cell(r["p"],r["p"]*PX["PTGC"],"p")}</div><div class="cl"><div class="l">Pending to claim</div>{cell(r["pend"],r["pend"]*PX["PTGC"],"p")}</div>'
            f'<div class="cl"><div class="l">UFO</div>{cell(r["u"],r["u"]*PX["UFO"],"u")}</div></div></div>')
allrow=(f'<div class="wsum"><span class="l">ALL WALLETS</span><b>{usd(T)}</b></div>'
        f'<div class="rkm one"><span class="asone">As one wallet</span><div class="bG p sm"><img src="{LOGO["PTGC"]}" alt=""><span class="k">PTGC</span><b>#{asone["PTGC"]["r"]:,}</b><small>{topt(asone["PTGC"]["top"])}</small></div>'
        f'<div class="bG u sm"><img src="{LOGO["UFO"]}" alt=""><span class="k">UFO</span><b>#{asone["UFO"]["r"]:,}</b><small>{topt(asone["UFO"]["top"])}</small></div></div>')
bd=(f'<section class="pf2-pn pf2-fold">{G.header("holder rank, PTGC, pending, UFO and the total for each")}<div class="pf2-foldb pf2-bd">{G.SORTS}'
    f'<div class="pf2-bdc">{"".join(card(r) for r in rows)}{allrow}</div>{G.FOOT}</div></section>')
def crop(s): k=s.index('<div class="pf2-ebs">'); return s[:k]+'</section>'
cards='<div class="pf2-tok2">'+crop(H.H3(H.P,'p',H.RP))+crop(H.H3(H.U,'u',H.RU))+'</div>'
CSS=G.CSS+H.CSS+'''
.wrap{padding:16px 12px 40px;max-width:none}
.opt{font-size:11.5px}.note{font-size:14.5px}
.rkm{display:flex;flex-direction:column;gap:6px;margin:0 0 10px}
.rkm .bG+.bG{margin-top:0}
.rkm.one{margin:8px 0 0;flex-direction:row;flex-wrap:wrap;align-items:center;gap:6px}
.rkm.one .asone{flex-basis:100%;margin:0}
.rk3 .l{flex-wrap:wrap;row-gap:4px}.rk3 .k,.rk3 small{white-space:nowrap}
.pf2-bdc .bG{font-size:12px}.pf2-bdc .bG b{font-size:13.5px}
'''
head=open(S+'/repo/design/portfolio/mock-ranks-v3.html').read().split('</style></head>')[0]
head=re.sub(r'<title>.*?</title>','<title>Holder rank on a phone (390 px) — breakdown cards with the rank badges · the League box rank line — 2026-10-21</title>',head)
out=head+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:16px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">HOLDER RANK — PHONE</h1>
<div class="note">On a phone the breakdown is one card per wallet (as today). The two rank badges sit between the share bar and the amounts; "more to pass" drops under the rank when the line is full.</div>
<div class="opt">PER-WALLET BREAKDOWN</div>'''+bd+'''<div class="sep"></div><div class="opt">THE CARDS — ONE WALLET</div>
<span class="note">The rank line in the League box wraps: rank on the first line, "more to pass" under it.</span>'''+cards+'</div></div></body></html>'
out=out.replace('src="logos/','src="../../logos/').replace('refreshed hourly','refreshed every 2 hours')
open(S+'/repo/design/portfolio/mock-ranks-phone-v1.html','w').write(out); print('written',len(out))
