import sys, html
sys.path.insert(0,'/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad')
import mock_ranks as M
import mock_ranks2 as M2
rows,T,SP,SU,SPEND,asone,R,PX,ab,usd,topt,medal=M.rows,M.T,M.SP,M.SU,M.SPEND,M.asone,M.R,M.PX,M.ab,M.usd,M.topt,M.medal
LOGO=M2.LOGO; nxt=M2.nxt; header=M2.header; SORTS=M2.SORTS; FOOT=M2.FOOT; share=M2.share
def badge(tk,x,dense):
    c='p' if tk=='PTGC' else 'u'
    if not x: return f'<div class="bG {c} none"><img src="{LOGO[tk]}" alt=""><span class="k">{tk}</span><b>—</b><small>not holding</small></div>'
    md=medal(x['r'])
    nx=f'<em>{nxt(x)}</em>'
    return (f'<div class="bG {c}{" md" if md else ""}{" dense" if dense else ""}"><img src="{LOGO[tk]}" alt=""><span class="k">{tk}</span><b>#{x["r"]:,}</b><small>{topt(x["top"])}</small>'
            + (f'<i class="medal">{md}</i>' if md else '') + nx + '</div>')
def optG(dense):
    cols='<colgroup><col style="width:17%"><col style="width:%s"><col><col><col><col style="width:16%%"></colgroup>'
    h=[f'<section class="pf2-pn pf2-fold">{header("holder rank, PTGC, pending, UFO and the total for each")}<div class="pf2-foldb pf2-bd">{SORTS}'
       f'<table class="pf2-bdt G{" dn" if dense else ""}">'+('<colgroup><col style="width:13%"><col style="width:41%"><col style="width:11%"><col style="width:11%"><col style="width:10%"><col style="width:14%"></colgroup>' if dense else '<colgroup><col style="width:15%"><col style="width:31%"><col style="width:13%"><col style="width:13%"><col style="width:12%"><col style="width:16%"></colgroup>')+f'<thead><tr><th>WALLET</th><th class="rkh">HOLDER RANK</th><th><img src="{LOGO["PTGC"]}" alt="">PTGC</th>'
       f'<th><img src="{LOGO["PTGC"]}" alt="">PENDING TO CLAIM</th><th><img src="{LOGO["UFO"]}" alt="">UFO</th><th>TOTAL · SHARE</th></tr></thead><tbody>']
    for r in rows:
        h.append(f'<tr style="--c:{r["c"]}"><td><div class="n">{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></td>'
                 f'<td class="rkc">{badge("PTGC",r["rp"],dense)}{badge("UFO",r["ru"],dense)}</td>'
                 f'<td><span class="tk p">{ab(r["p"])}</span><span class="us">{usd(r["p"]*PX["PTGC"])}</span></td>'
                 f'<td><span class="tk p">{ab(r["pend"])}</span><span class="us">{usd(r["pend"]*PX["PTGC"])}</span></td>'
                 f'<td><span class="tk u">{ab(r["u"]) if r["u"] else "—"}</span><span class="us">{usd(r["u"]*PX["UFO"]) if r["u"] else ""}</span></td>'
                 f'<td><span class="tot">{usd(r["tot"])}</span>{share(r)}</td></tr>')
    one=(f'<td class="rkc"><div class="asone">As one wallet</div><div class="bG p sm"><img src="{LOGO["PTGC"]}" alt=""><span class="k">PTGC</span><b>#{asone["PTGC"]["r"]:,}</b><small>{topt(asone["PTGC"]["top"])}</small></div>'
         f'<div class="bG u sm"><img src="{LOGO["UFO"]}" alt=""><span class="k">UFO</span><b>#{asone["UFO"]["r"]:,}</b><small>{topt(asone["UFO"]["top"])}</small></div></td>')
    h.append(f'<tr class="sub tot"><td><div class="n">ALL WALLETS</div></td>{one}<td><span class="tk p">{ab(SP)}</span><span class="us">{usd(SP*PX["PTGC"])}</span></td>'
             f'<td><span class="tk p">{ab(SPEND)}</span><span class="us">{usd(SPEND*PX["PTGC"])}</span></td><td><span class="tk u">{ab(SU)}</span><span class="us">{usd(SU*PX["UFO"])}</span></td>'
             f'<td><span class="tot">{usd(T)}</span><div class="bar"><span><b style="width:50%;background:#F2D35B"></b><b style="width:50%;background:#7CFC00"></b></span><small>100%</small></div></td></tr></tbody></table>{FOOT}</div></section>')
    return ''.join(h)
CSS=M2.CSS+'''
.pf2-bdt.G{table-layout:fixed}
.pf2-bdt.G th.rkh,.pf2-bdt.G td.rkc{text-align:left}
.pf2-bdt.G td.rkc{padding-top:10px;padding-bottom:10px}
.bG{display:flex;align-items:center;gap:7px;flex-wrap:wrap;font:700 12.5px Rajdhani;letter-spacing:.06em;color:rgba(255,255,255,.65);padding:6px 11px 6px 6px;border-radius:11px;border:1px solid rgba(255,255,255,.12);background:rgba(0,0,0,.35)}
.bG+.bG{margin-top:6px}
.bG img{width:18px;height:18px;border-radius:50%}
.bG b{font:900 14px Orbitron;letter-spacing:.04em}
.bG.p{border-color:rgba(242,211,91,.36);background:linear-gradient(90deg,rgba(242,211,91,.09),rgba(0,0,0,.32) 65%)}.bG.p b{color:#F2D35B}
.bG.u{border-color:rgba(124,252,0,.3);background:linear-gradient(90deg,rgba(124,252,0,.08),rgba(0,0,0,.32) 65%)}.bG.u b{color:#8DFF3A}
.pf2-bdt.G td{white-space:nowrap}.pf2-bdt.G .bar span{width:100px!important}
.bG small{font:600 12.5px Rajdhani;letter-spacing:.02em;color:rgba(255,255,255,.55)}
.bG em{flex-basis:100%;padding-left:25px;font:600 12.5px Rajdhani;font-style:normal;letter-spacing:.01em;color:rgba(255,255,255,.48);margin-top:-2px}
.bG.md.p{box-shadow:0 0 12px rgba(242,211,91,.18)}.bG.md.u{box-shadow:0 0 12px rgba(124,252,0,.16)}
.bG.none{opacity:.5}.bG.none b{color:rgba(255,255,255,.5)}
/* dense: one line, "more to pass" pushed right */
.bG.dense{flex-wrap:nowrap;padding:4px 10px 4px 5px;border-radius:999px}
.bG.dense em{flex-basis:auto;padding-left:0;margin:0 0 0 auto;white-space:nowrap}
.bG.sm{padding:3px 10px 3px 4px;border-radius:999px;width:max-content}.bG.sm b{font-size:12.5px}.bG.sm img{width:16px;height:16px}
.asone{margin-bottom:5px}
'''
out=M2.head_all.replace('three layouts: D rank strip · E rank inside the token columns · F wallet cards','rank badges in their own column next to the wallet')+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">HOLDER RANK — ITS OWN COLUMN, RIGHT NEXT TO THE WALLET</h1>
<div class="note">Wallet · HOLDER RANK · PTGC · Pending · UFO · Total — the badges from option C. Two badge sizes so you can see the row height.
Real ranks from today's holder lists; names, addresses and balances are examples.</div>'''
NOTES={'G1':'Two-line badges: rank, top %, TOP 100 / 1,000 badge on the first line, "more to pass" under it.',
       'G2':'One-line badges: everything on a single line, "more to pass" at the right end — the rows stay close to today’s height.'}
for i,(k,d) in enumerate((('G1',False),('G2',True))):
    if i: out+='<div class="sep"></div>'
    out+=f'<div class="opt">LAYOUT {k}</div><span class="note">{NOTES[k]}</span>'+optG(d)
out+='</div></div></body></html>'
open(M.S+'/repo/design/portfolio/mock-ranks-v3.html','w').write(out); print('v3 written',len(out))
