import sys, html
sys.path.insert(0,'/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad')
import mock_ranks as M          # data, ranks, helpers (rebuilds v1 identically as a side effect)
rows,T,SP,SU,SPEND,asone,R,PX,ab,usd,topt,medal=M.rows,M.T,M.SP,M.SU,M.SPEND,M.asone,M.R,M.PX,M.ab,M.usd,M.topt,M.medal
LOGO={'PTGC':'../../logos/ptgc/logo-512.webp','UFO':'../../logos/ufo/logo-512.webp'}
def nxt(x): return '#1 — nobody above you' if x['next'] is None else f'▲ {ab(x["next"]+1)} more to pass #{x["r"]-1:,}'
def best(k): return min(r[k]['r'] for r in rows if r[k])
def header(sub):
    chips=(f'<span class="chip">Total<b>{usd(T)}</b></span><span class="chip rk"><i style="background:#F2D35B"></i>Best PTGC rank<b>#{best("rp"):,}</b></span>'
           f'<span class="chip rk"><i style="background:#7CFC00"></i>Best UFO rank<b>#{best("ru"):,}</b></span>')
    return (f'<button class="pf2-foldh" aria-expanded="true"><span class="ic"><img src="../../logos/portfolio/pf-wallet.webp" alt=""></span>'
            f'<span class="tt"><b class="oh">PER-WALLET BREAKDOWN</b><span class="mt">{len(rows)} wallets · {sub}</span></span><span class="chips">{chips}</span><span class="chev"></span></button>')
SORTS='<div class="pf2-bds"><span>Sort</span><button class="on">Value</button><button>Name</button><button>Added</button><button>PTGC rank</button><button>UFO rank</button></div>'
FOOT=(f'<div class="rkfoot">Rank among <b>{len(R["PTGC"]):,}</b> PTGC and <b>{len(R["UFO"]):,}</b> UFO holders (wallets holding at least 1 token). Left out: liquidity pools, '
      'the burn addresses, the token contracts, the UFO OA wallet. Your balance is read live; the holder list is refreshed hourly · list read 25 min ago</div>')
def share(r):
    ps=r['p']*PX['PTGC']/(r['p']*PX['PTGC']+r['u']*PX['UFO'])*100 if (r['p'] or r['u']) else 0
    return f'<div class="bar"><span><b style="width:{ps:.0f}%;background:#F2D35B"></b><b style="width:{100-ps:.0f}%;background:#7CFC00"></b></span><small>{r["tot"]/T*100:.1f}%</small></div>'
# ---------- D: rank strip under each row ----------
def tileD(tk,x):
    c='p' if tk=='PTGC' else 'u'
    if not x: return f'<div class="rD {c} none"><img src="{LOGO[tk]}" alt=""><span class="k">{tk}</span><b>—</b><small>not holding</small></div>'
    md=medal(x['r'])
    return (f'<div class="rD {c}"><img src="{LOGO[tk]}" alt=""><span class="k">{tk} RANK</span><b>#{x["r"]:,}</b><small>{topt(x["top"])}</small>'
            + (f'<i class="medal">{md}</i>' if md else '') + f'<em>{nxt(x)}</em></div>')
def optD():
    h=[f'<section class="pf2-pn pf2-fold">{header("PTGC, pending, UFO, holder rank and the total for each")}<div class="pf2-foldb pf2-bd">{SORTS}<table class="pf2-bdt D"><thead><tr><th>WALLET</th>'
       f'<th><img src="{LOGO["PTGC"]}" alt="">PTGC</th><th><img src="{LOGO["PTGC"]}" alt="">PENDING TO CLAIM</th><th><img src="{LOGO["UFO"]}" alt="">UFO</th><th>TOTAL · SHARE</th></tr></thead><tbody>']
    for r in rows:
        h.append(f'<tr class="m" style="--c:{r["c"]}"><td rowspan="2"><div class="n">{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></td>'
                 f'<td><span class="tk p">{ab(r["p"])}</span><span class="us">{usd(r["p"]*PX["PTGC"])}</span></td><td><span class="tk p">{ab(r["pend"])}</span><span class="us">{usd(r["pend"]*PX["PTGC"])}</span></td>'
                 f'<td><span class="tk u">{ab(r["u"]) if r["u"] else "—"}</span><span class="us">{usd(r["u"]*PX["UFO"]) if r["u"] else ""}</span></td><td><span class="tot">{usd(r["tot"])}</span>{share(r)}</td></tr>'
                 f'<tr class="rs" style="--c:{r["c"]}"><td colspan="4"><div class="strip">{tileD("PTGC",r["rp"])}{tileD("UFO",r["ru"])}</div></td></tr>')
    h.append(f'<tr class="sub tot"><td><div class="n">ALL WALLETS</div></td><td><span class="tk p">{ab(SP)}</span><span class="us">{usd(SP*PX["PTGC"])}</span></td><td><span class="tk p">{ab(SPEND)}</span><span class="us">{usd(SPEND*PX["PTGC"])}</span></td>'
             f'<td><span class="tk u">{ab(SU)}</span><span class="us">{usd(SU*PX["UFO"])}</span></td><td><span class="tot">{usd(T)}</span><div class="bar"><span><b style="width:50%;background:#F2D35B"></b><b style="width:50%;background:#7CFC00"></b></span><small>100%</small></div></td></tr>'
             f'<tr class="sub one"><td></td><td colspan="4"><div class="strip one"><span class="asone">As one wallet</span><span class="mini p"><img src="{LOGO["PTGC"]}" alt="">PTGC <b>#{asone["PTGC"]["r"]:,}</b> <small>{topt(asone["PTGC"]["top"])}</small></span>'
             f'<span class="mini u"><img src="{LOGO["UFO"]}" alt="">UFO <b>#{asone["UFO"]["r"]:,}</b> <small>{topt(asone["UFO"]["top"])}</small></span></div></td></tr></tbody></table>{FOOT}</div></section>')
    return ''.join(h)
# ---------- E: rank inside each token column ----------
def cellE(tk,amt,x):
    c='p' if tk=='PTGC' else 'u'
    top=f'<span class="tk {c}">{ab(amt) if amt else "—"}</span><span class="us">{usd(amt*PX[tk]) if amt else ""}</span>'
    if not x: return top+'<div class="rE none">not holding</div>'
    md=medal(x['r'])
    return top+(f'<div class="rE {c}"><b>#{x["r"]:,}</b><small>{topt(x["top"])}</small>' + (f'<i class="medal">{md}</i>' if md else '') + f'</div><em class="nE">{nxt(x)}</em>')
def optE():
    h=[f'<section class="pf2-pn pf2-fold">{header("PTGC and UFO with their holder rank, pending, and the total for each")}<div class="pf2-foldb pf2-bd">{SORTS}<table class="pf2-bdt E"><colgroup><col style="width:20%"><col style="width:25%"><col style="width:25%"><col style="width:13%"><col style="width:17%"></colgroup>'
       f'<thead><tr><th>WALLET</th><th><img src="{LOGO["PTGC"]}" alt="">PTGC · RANK</th><th><img src="{LOGO["UFO"]}" alt="">UFO · RANK</th><th><img src="{LOGO["PTGC"]}" alt="">PENDING</th><th>TOTAL · SHARE</th></tr></thead><tbody>']
    for r in rows:
        h.append(f'<tr style="--c:{r["c"]}"><td><div class="n">{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></td>'
                 f'<td>{cellE("PTGC",r["p"],r["rp"])}</td><td>{cellE("UFO",r["u"],r["ru"])}</td><td><span class="tk p">{ab(r["pend"])}</span><span class="us">{usd(r["pend"]*PX["PTGC"])}</span></td>'
                 f'<td><span class="tot">{usd(r["tot"])}</span>{share(r)}</td></tr>')
    h.append(f'<tr class="sub tot"><td><div class="n">ALL WALLETS</div><div class="asone" style="margin-top:4px">ranks as one wallet</div></td>'
             f'<td><span class="tk p">{ab(SP)}</span><span class="us">{usd(SP*PX["PTGC"])}</span><div class="rE p"><b>#{asone["PTGC"]["r"]:,}</b><small>{topt(asone["PTGC"]["top"])}</small></div></td>'
             f'<td><span class="tk u">{ab(SU)}</span><span class="us">{usd(SU*PX["UFO"])}</span><div class="rE u"><b>#{asone["UFO"]["r"]:,}</b><small>{topt(asone["UFO"]["top"])}</small></div></td>'
             f'<td><span class="tk p">{ab(SPEND)}</span><span class="us">{usd(SPEND*PX["PTGC"])}</span></td><td><span class="tot">{usd(T)}</span><div class="bar"><span><b style="width:50%;background:#F2D35B"></b><b style="width:50%;background:#7CFC00"></b></span><small>100%</small></div></td></tr></tbody></table>{FOOT}</div></section>')
    return ''.join(h)
# ---------- F: wallet cards ----------
def halfF(tk,amt,x,pend=None):
    c='p' if tk=='PTGC' else 'u'
    amtl=f'<div class="amt"><img src="{LOGO[tk]}" alt=""><span class="tk {c}">{ab(amt) if amt else "—"}</span><span class="us">{usd(amt*PX[tk]) if amt else "no "+tk}</span></div>'
    pl=f'<div class="pend">+ {ab(pend)} pending to claim · {usd(pend*PX["PTGC"])}</div>' if pend else ''
    if not x: return f'<div class="hf {c} none"><div class="amt"><img src="{LOGO[tk]}" alt=""><span class="us">No {tk} in this wallet</span></div><div class="lab">{tk} HOLDER RANK</div><div class="big">—</div></div>'
    md=medal(x['r'])
    return (f'<div class="hf {c}">{amtl}{pl}<div class="lab">{tk} HOLDER RANK</div><div class="big">#{x["r"]:,}' + (f'<i class="medal">{md}</i>' if md else '') + '</div>'
            f'<div class="top">{topt(x["top"])} of {x["n"]:,} holders</div><div class="nx">{nxt(x)}</div></div>')
def optF():
    h=[f'<section class="pf2-pn pf2-fold">{header("each wallet with its PTGC and UFO holder rank")}<div class="pf2-foldb pf2-bd">{SORTS}<div class="cards">']
    for r in rows:
        h.append(f'<div class="wc" style="--c:{r["c"]}"><div class="wh"><div><div class="n">{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></div>'
                 f'<div class="wt"><span class="tot">{usd(r["tot"])}</span>{share(r)}</div></div><div class="hfs">{halfF("PTGC",r["p"],r["rp"],r["pend"])}{halfF("UFO",r["u"],r["ru"])}</div></div>')
    h.append(f'</div><div class="wc all"><div class="wh"><div><div class="n">ALL WALLETS</div><div class="asone">{len(rows)} wallets · ranked as ONE wallet</div></div>'
             f'<div class="wt"><span class="tot">{usd(T)}</span><div class="bar"><span><b style="width:50%;background:#F2D35B"></b><b style="width:50%;background:#7CFC00"></b></span><small>100%</small></div></div></div>'
             f'<div class="hfs">{halfF("PTGC",SP,asone["PTGC"],SPEND)}{halfF("UFO",SU,asone["UFO"])}</div></div>{FOOT}</div></section>')
    return ''.join(h)
CSS='''
.pf2-foldh .chip.rk b{font-family:Orbitron;font-size:12px;letter-spacing:.04em}
.rkfoot{margin:12px 4px 2px;font:600 13.5px Rajdhani;color:rgba(255,255,255,.5)}.rkfoot b{color:rgba(255,255,255,.8)}
.medal{font:900 9.5px Orbitron;font-style:normal;letter-spacing:.08em;padding:2px 6px;border-radius:4px;color:#1a1200;background:linear-gradient(180deg,#FFE58A,#E0B53A);white-space:nowrap}
.u .medal,.u.medal{background:linear-gradient(180deg,#B8FF6A,#5ED000);color:#061000}
.asone{font:700 11.5px Rajdhani;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.5)}
/* D */
.pf2-bdt.D tr.m td{border-bottom:0;padding-bottom:6px}
.pf2-bdt.D tr.rs td{padding-top:0;padding-bottom:14px;text-align:left}
.pf2-bdt.D tbody tr.rs td:first-child{border-left:0}
.pf2-bdt.D tbody tr.m td[rowspan]{vertical-align:top;padding-top:16px}
.strip{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.rD{display:flex;align-items:center;gap:8px;flex-wrap:wrap;padding:8px 12px 8px 8px;border-radius:12px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.32);font:700 13px Rajdhani;color:rgba(255,255,255,.7)}
.rD.p{border-color:rgba(242,211,91,.32);background:linear-gradient(90deg,rgba(242,211,91,.08),rgba(0,0,0,.3) 60%)}
.rD.u{border-color:rgba(124,252,0,.28);background:linear-gradient(90deg,rgba(124,252,0,.07),rgba(0,0,0,.3) 60%)}
.rD img{width:20px;height:20px;border-radius:50%}
.rD .k{letter-spacing:.1em;font-size:12px;color:rgba(255,255,255,.6)}
.rD b{font:900 15px Orbitron;letter-spacing:.04em}.rD.p b{color:#F2D35B}.rD.u b{color:#8DFF3A}
.rD small{font:600 13px Rajdhani;color:rgba(255,255,255,.55)}
.rD em{margin-left:auto;font:600 13px Rajdhani;font-style:normal;color:rgba(255,255,255,.5)}
.rD.none{opacity:.5}.rD.none b{color:rgba(255,255,255,.5)}
.strip.one{display:flex;align-items:center;gap:12px}
.mini{display:inline-flex;align-items:center;gap:6px;font:700 13px Rajdhani;color:rgba(255,255,255,.7);padding:3px 10px 3px 4px;border-radius:999px;border:1px solid rgba(255,255,255,.12);background:rgba(0,0,0,.3)}
.mini img{width:16px;height:16px;border-radius:50%}.mini b{font:900 13px Orbitron}.mini.p b{color:#F2D35B}.mini.u b{color:#8DFF3A}.mini small{color:rgba(255,255,255,.5);font-weight:600}
.pf2-bdt.D tr.sub.one td{padding-top:4px}
/* E */
.pf2-bdt.E{table-layout:fixed}
.pf2-bdt.E td{vertical-align:top;padding-top:14px;padding-bottom:14px}
.pf2-bdt.E td:first-child{vertical-align:middle}
.rE{display:inline-flex;align-items:center;gap:7px;margin-top:8px;padding:3px 9px;border-radius:8px;border:1px solid rgba(255,255,255,.12);background:rgba(0,0,0,.32)}
.rE.p{border-color:rgba(242,211,91,.35)}.rE.u{border-color:rgba(124,252,0,.3)}
.rE b{font:900 14px Orbitron;letter-spacing:.04em}.rE.p b{color:#F2D35B}.rE.u b{color:#8DFF3A}
.rE small{font:600 13px Rajdhani;color:rgba(255,255,255,.55)}
.rE.none{border:0;background:none;font:600 13px Rajdhani;color:rgba(255,255,255,.35);padding:0}
.nE{display:block;margin-top:5px;font:600 12.5px Rajdhani;font-style:normal;color:rgba(255,255,255,.48)}
/* F */
.cards{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.wc{border-radius:14px;border:1px solid rgba(255,255,255,.1);border-left:3px solid var(--c);background:linear-gradient(180deg,rgba(255,255,255,.03),rgba(0,0,0,.25));padding:14px 16px}
.wc.all{margin-top:14px;border-left-color:#F2D35B;background:linear-gradient(90deg,rgba(242,211,91,.1),rgba(13,17,26,.6) 45%)}
.wc.all .hfs{grid-template-columns:1fr 1fr}
.wh{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;padding-bottom:12px;border-bottom:1px solid rgba(255,255,255,.07)}
.wh .n{font-size:19px;font-weight:700}.wh .ad{font-family:ui-monospace,Menlo,monospace;color:rgba(255,255,255,.55);font-size:14px;display:flex;align-items:center;gap:6px;margin-top:2px}
.wt{text-align:right}.wt .tot{font-size:22px;font-weight:700}.wt .bar{display:flex;align-items:center;gap:8px;justify-content:flex-end;margin-top:4px}
.wt .bar span{display:flex;width:110px;height:6px;border-radius:3px;overflow:hidden;background:rgba(255,255,255,.08)}.wt .bar b{display:block;height:100%}.wt .bar small{color:rgba(255,255,255,.55);font-size:13px}
.hfs{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px}
.hf{border-radius:12px;padding:11px 13px;border:1px solid rgba(255,255,255,.08);background:rgba(0,0,0,.28)}
.hf.p{border-color:rgba(242,211,91,.25);background:linear-gradient(160deg,rgba(242,211,91,.09),rgba(0,0,0,.3) 55%)}
.hf.u{border-color:rgba(124,252,0,.22);background:linear-gradient(160deg,rgba(124,252,0,.07),rgba(0,0,0,.3) 55%)}
.hf .amt{display:flex;align-items:baseline;gap:8px}.hf .amt img{width:18px;height:18px;border-radius:50%;align-self:center}
.hf .amt .tk{font-size:19px;font-weight:700}.hf.p .tk{color:#F2D35B}.hf.u .tk{color:#7CFC00}.hf .amt .us{color:rgba(255,255,255,.55);font-size:14px}
.hf .pend{font:600 13px Rajdhani;color:rgba(255,255,255,.5);margin-top:2px}
.hf .lab{margin-top:10px;font:700 11.5px Rajdhani;letter-spacing:.12em;color:rgba(255,255,255,.5)}
.hf .big{display:flex;align-items:center;gap:8px;font:900 26px Orbitron;letter-spacing:.03em;margin-top:2px}.hf.p .big{color:#F2D35B}.hf.u .big{color:#8DFF3A}
.hf .top{font:600 14px Rajdhani;color:rgba(255,255,255,.7);margin-top:2px}
.hf .nx{font:600 13px Rajdhani;color:rgba(255,255,255,.48);margin-top:3px}
.hf.none{opacity:.55}.hf.none .big{color:rgba(255,255,255,.4)}
'''
HEAD=M.HEAD.split('<style>\n@font-face')[0]
head_all=M.HEAD.replace('Holder rank per wallet — A under the amounts · B rank column · C rank column + next step — 2026-10-20','Holder rank, option C — three layouts: D rank strip · E rank inside the token columns · F wallet cards — 2026-10-20')
head_all=head_all.split('</style></head>')[0]   # keep fonts + base CSS (v1 CSS included, harmless)
out=head_all+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">HOLDER RANK — OPTION C, THREE LAYOUTS</h1>
<div class="note">Same content in all three (rank, top %, TOP 10 / 100 / 1,000 badge, "more to pass", rank sorts, ranked as one wallet) — only the layout changes.
Real ranks from today's holder lists; names, addresses and balances are examples.</div>'''
NOTES={'D':'The table keeps today’s five balanced columns; each wallet gets a full-width rank strip underneath — PTGC tile left, UFO tile right, "more to pass" at the end of the tile.',
       'E':'No extra column: each token’s rank sits in its own column under the amount (PTGC · RANK, UFO · RANK), pending moves next to the total. Fixed column widths so nothing squeezes.',
       'F':'The table becomes wallet cards, two per row: name + total + share on top, then a PTGC half and a UFO half with the rank as the big number. Stacks to one column on a phone with no changes.'}
for i,(k,f) in enumerate((('D',optD),('E',optE),('F',optF))):
    if i: out+='<div class="sep"></div>'
    out+=f'<div class="opt">LAYOUT {k}</div><span class="note">{NOTES[k]}</span>'+f()
out+='</div></div></body></html>'
open(M.S+'/repo/design/portfolio/mock-ranks-v2.html','w').write(out); print('v2 written',len(out))
