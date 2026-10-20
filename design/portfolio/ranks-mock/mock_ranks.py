import json, html
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
BURN={'0x0000000000000000000000000000000000000000','0x0000000000000000000000000000000000000369','0x000000000000000000000000000000000000dead'}
TOK={'PTGC':'0x94534eeee131840b1c0f61847c572228bdfdde93','UFO':'0x49ed499433bee42dd34c169470fef2c8f9fae6e6'}
exu=json.load(open(S+'/excl_ufo.json'))
def ranked(tk):
    rows=json.load(open(S+f'/{tk.lower()}-holders.json'))
    out=[]
    for a,v,isc,name in rows:
        if a in BURN or a==TOK[tk] or isc: continue          # mock: every contract out (production: pools by token0(), see notes)
        if tk=='UFO' and a in exu['wallets']: continue
        b=int(v)/1e18
        if b>=1: out.append(b)
    out.sort(reverse=True); return out
R={tk:ranked(tk) for tk in ('PTGC','UFO')}
def rank(tk,bal):
    if not bal or bal<1: return None
    L=R[tk]; lo,hi=0,len(L)
    while lo<hi:
        m=(lo+hi)//2
        if L[m]>bal: lo=m+1
        else: hi=m
    r=lo+1; nxt=L[lo-1]-bal if lo>0 else None
    return {'r':r,'n':len(L),'top':r/len(L)*100,'next':nxt}
PX={'PTGC':0.00001605,'UFO':0.000002217}
W=[('Main','0x1111…1111','#B26BFF',900e6,6.2e6,2.5e9),
   ('Cold storage','0x2222…2222','#F2D35B',260e6,1.9e6,600e6),
   ('Locks','0x3333…3333','#22D3EE',45e6,0.7e6,0),
   ('Small bag','0x4444…4444','#FF7AB6',1.5e6,0.02e6,12e6)]
def ab(n):
    for d,s in ((1e12,'T'),(1e9,'B'),(1e6,'M'),(1e3,'K')):
        if n>=d: return f'{n/d:.2f}{s}'
    return f'{n:.0f}'
def usd(n): return '${:,.2f}'.format(n)
def topt(p): return f'top {p:.1f}%' if p>=1 else (f'top {p:.2f}%' if p>=0.1 else f'top {p:.2f}%')
def medal(r):
    return 'TOP 10' if r<=10 else 'TOP 100' if r<=100 else 'TOP 1,000' if r<=1000 else None
rows=[]
for nm,ad,c,p,pend,u in W:
    rows.append(dict(nm=nm,ad=ad,c=c,p=p,pend=pend,u=u,rp=rank('PTGC',p),ru=rank('UFO',u),tot=p*PX['PTGC']+pend*PX['PTGC']+u*PX['UFO']))
rows.sort(key=lambda r:-r['tot'])
T=sum(r['tot'] for r in rows)
SP=sum(r['p'] for r in rows); SU=sum(r['u'] for r in rows); SPEND=sum(r['pend'] for r in rows)
asone={'PTGC':rank('PTGC',SP),'UFO':rank('UFO',SU)}
print('PTGC list',len(R['PTGC']),'UFO list',len(R['UFO']))
for r in rows: print(r['nm'],r['rp'],r['ru'])
print('as one',asone)

def rkA(x,cls):
    if not x: return f'<span class="rkA none">not ranked</span>'
    return f'<span class="rkA {cls}"><b>#{x["r"]:,}</b> · {topt(x["top"])}</span>'
def chipB(tk,x,more=False):
    logo='../../logos/ptgc/logo-512.webp' if tk=='PTGC' else '../../logos/ufo/logo-512.webp'
    cls='p' if tk=='PTGC' else 'u'
    if not x: return f'<div class="rkB {cls} none"><img src="{logo}" alt="">{tk}<b>—</b><small>not holding</small></div>'
    md=medal(x['r']) if more else None
    nxt=''
    if more:
        nxt=f'<em>{"#1 — nobody above" if x["next"] is None else "▲ "+ab(x["next"]+1)+" more to pass #"+format(x["r"]-1,",")}</em>'
    return (f'<div class="rkB {cls}{" md" if md else ""}"><img src="{logo}" alt="">{tk}<b>#{x["r"]:,}</b><small>{topt(x["top"])}</small>'
            + (f'<i class="medal">{md}</i>' if md else '') + nxt + '</div>')
def table(opt):
    th_extra='<th class="rkh">HOLDER RANK</th>' if opt in 'BC' else ''
    h=['<table class="pf2-bdt"><thead><tr><th>WALLET</th><th><img src="../../logos/ptgc/logo-512.webp" alt="">PTGC</th><th><img src="../../logos/ptgc/logo-512.webp" alt="">PENDING TO CLAIM</th><th><img src="../../logos/ufo/logo-512.webp" alt="">UFO</th>'+th_extra+'<th>TOTAL · SHARE</th></tr></thead><tbody>']
    for r in rows:
        ps=r['p']*PX['PTGC']/(r['p']*PX['PTGC']+r['u']*PX['UFO'])*100 if (r['p'] or r['u']) else 0
        pc=f'<span class="tk p">{ab(r["p"])}</span><span class="us">{usd(r["p"]*PX["PTGC"])}</span>'
        uc=f'<span class="tk u">{ab(r["u"]) if r["u"] else "—"}</span><span class="us">{usd(r["u"]*PX["UFO"]) if r["u"] else ""}</span>'
        if opt=='A': pc+=rkA(r['rp'],'p'); uc+=rkA(r['ru'],'u')
        rk=f'<td class="rkc">{chipB("PTGC",r["rp"],opt=="C")}{chipB("UFO",r["ru"],opt=="C")}</td>' if opt in 'BC' else ''
        h.append(f'<tr style="--c: {r["c"]};"><td><div class="n">{html.escape(r["nm"])}</div><div class="ad">{r["ad"]}<button class="cp">⧉</button></div></td>'
                 f'<td>{pc}</td><td><span class="tk p">{ab(r["pend"])}</span><span class="us">{usd(r["pend"]*PX["PTGC"])}</span></td><td>{uc}</td>{rk}'
                 f'<td><span class="tot">{usd(r["tot"])}</span><div class="bar"><span><b style="width:{ps:.0f}%;background:#F2D35B"></b><b style="width:{100-ps:.0f}%;background:#7CFC00"></b></span><small>{r["tot"]/T*100:.1f}%</small></div></td></tr>')
    one=''
    if opt=='C':
        one=(f'<td class="rkc one"><div class="asone">as one wallet</div><div class="rkB p sm"><img src="../../logos/ptgc/logo-512.webp" alt="">PTGC<b>#{asone["PTGC"]["r"]:,}</b></div>'
             f'<div class="rkB u sm"><img src="../../logos/ufo/logo-512.webp" alt="">UFO<b>#{asone["UFO"]["r"]:,}</b></div></td>')
    elif opt=='B': one='<td class="rkc one"></td>'
    h.append(f'<tr class="sub tot"><td><div class="n">ALL WALLETS</div></td><td><span class="tk p">{ab(SP)}</span><span class="us">{usd(SP*PX["PTGC"])}</span></td>'
             f'<td><span class="tk p">{ab(SPEND)}</span><span class="us">{usd(SPEND*PX["PTGC"])}</span></td><td><span class="tk u">{ab(SU)}</span><span class="us">{usd(SU*PX["UFO"])}</span></td>{one}'
             f'<td><span class="tot">{usd(T)}</span><div class="bar"><span><b style="width:50%;background:#F2D35B"></b><b style="width:50%;background:#7CFC00"></b></span><small>100%</small></div></td></tr>')
    h.append('</tbody></table>')
    return ''.join(h)
def best(tk):
    xs=[r['rp' if tk=='PTGC' else 'ru'] for r in rows if r['rp' if tk=='PTGC' else 'ru']]
    return min(x['r'] for x in xs)
def section(opt):
    chips=(f'<span class="chip">Total<b>{usd(T)}</b></span>' +
           (f'<span class="chip rk"><i style="background:#F2D35B"></i>Best PTGC rank<b>#{best("PTGC"):,}</b></span><span class="chip rk"><i style="background:#7CFC00"></i>Best UFO rank<b>#{best("UFO"):,}</b></span>' if opt in 'BC' else ''))
    sorts='<button class="on">Value</button><button>Name</button><button>Added</button>' + ('<button>PTGC rank</button><button>UFO rank</button>' if opt=='C' else '')
    foot=(f'<div class="rkfoot">Rank among <b>{len(R["PTGC"]):,}</b> PTGC and <b>{len(R["UFO"]):,}</b> UFO holders (wallets holding at least 1 token). '
          f'Left out: liquidity pools, the burn addresses, the token contracts{", the UFO OA wallet" if True else ""}. Your balance is read live; the holder list is refreshed hourly · list read 25 min ago</div>')
    return (f'<section class="pf2-pn pf2-fold"><button class="pf2-foldh" aria-expanded="true"><span class="ic"><img src="../../logos/portfolio/pf-wallet.webp" alt=""></span>'
            f'<span class="tt"><b class="oh">PER-WALLET BREAKDOWN</b><span class="mt">{len(rows)} wallets · PTGC, pending, UFO{", holder rank" if opt!="A" else ""} and the total for each</span></span>'
            f'<span class="chips">{chips}</span><span class="chev"></span></button><div class="pf2-foldb pf2-bd"><div class="pf2-bds"><span>Sort</span>{sorts}</div>{table(opt)}{foot}</div></section>')
CSS='''
.rkA{display:block;margin-top:5px;font:600 13.5px Rajdhani;color:rgba(255,255,255,.62);letter-spacing:.02em}
.rkA b{font-family:Orbitron;font-weight:900;font-size:12.5px;letter-spacing:.04em;margin-right:2px}
.rkA.p b{color:#F2D35B}.rkA.u b{color:#8DFF3A}.rkA.none{color:rgba(255,255,255,.35)}
.pf2-bdt th.rkh{text-align:left}
.pf2-bdt td.rkc{text-align:left;padding-top:10px;padding-bottom:10px}
.rkB{display:flex;align-items:center;gap:7px;font:700 13px Rajdhani;color:rgba(255,255,255,.7);letter-spacing:.06em;padding:4px 10px 4px 5px;border-radius:999px;border:1px solid rgba(255,255,255,.12);background:rgba(0,0,0,.35);width:max-content;flex-wrap:wrap;max-width:270px}
.rkB+.rkB{margin-top:6px}
.rkB img{width:18px;height:18px;border-radius:50%}
.rkB b{font-family:Orbitron;font-weight:900;font-size:13.5px;letter-spacing:.04em;margin-left:2px}
.rkB.p{border-color:rgba(242,211,91,.38)}.rkB.p b{color:#F2D35B}
.rkB.u{border-color:rgba(124,252,0,.32)}.rkB.u b{color:#8DFF3A}
.rkB small{font:600 12.5px Rajdhani;color:rgba(255,255,255,.55);letter-spacing:.02em}
.rkB.none{opacity:.55}.rkB.none b{color:rgba(255,255,255,.5)}
.rkB:has(em){border-radius:12px;padding:6px 12px 6px 6px}
.rkB em{flex-basis:100%;font:600 12.5px Rajdhani;font-style:normal;color:rgba(255,255,255,.5);padding-left:25px;margin-top:-1px;letter-spacing:.01em}
.rkB .medal{font:900 9.5px Orbitron;font-style:normal;letter-spacing:.08em;padding:2px 6px;border-radius:4px;color:#1a1200;background:linear-gradient(180deg,#FFE58A,#E0B53A)}
.rkB.u .medal{background:linear-gradient(180deg,#B8FF6A,#5ED000);color:#061000}
.rkB.md.p{box-shadow:0 0 12px rgba(242,211,91,.25)}.rkB.md.u{box-shadow:0 0 12px rgba(124,252,0,.22)}
.rkB.sm{padding:3px 9px 3px 4px;font-size:12px}.rkB.sm b{font-size:12.5px}.rkB.sm img{width:16px;height:16px}
.asone{font:700 11.5px Rajdhani;letter-spacing:.1em;text-transform:uppercase;color:rgba(255,255,255,.5);margin-bottom:5px}
.pf2-foldh .chip.rk b{font-family:Orbitron;font-size:12px;letter-spacing:.04em}
.rkfoot{margin:12px 4px 2px;font:600 13.5px Rajdhani;color:rgba(255,255,255,.5)}.rkfoot b{color:rgba(255,255,255,.8)}
'''
HEAD='''<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Holder rank per wallet — A under the amounts · B rank column · C rank column + next step — 2026-10-20</title>
<style>
@font-face{font-family:Orbitron;src:url(../../tools/harness/node_modules/@fontsource/orbitron/files/orbitron-latin-900-normal.woff2);font-weight:900}
@font-face{font-family:Rajdhani;src:url(../../tools/harness/node_modules/@fontsource/rajdhani/files/rajdhani-latin-700-normal.woff2);font-weight:700}
@font-face{font-family:Rajdhani;src:url(../../tools/harness/node_modules/@fontsource/rajdhani/files/rajdhani-latin-600-normal.woff2);font-weight:600}
@font-face{font-family:Rajdhani;src:url(../../tools/harness/node_modules/@fontsource/rajdhani/files/rajdhani-latin-500-normal.woff2);font-weight:500}
</style>
<link rel="stylesheet" href="../../tools/pf-v2/pf2.css">
<style>
body{margin:0;background:#04060a;color:#fff;font-family:Rajdhani;font-weight:500}
.wrap{padding:28px 40px 60px;max-width:1300px}
.opt{font-family:Orbitron;font-weight:900;font-size:13px;letter-spacing:.14em;color:#04060a;background:#F2D35B;display:inline-block;padding:5px 12px;border-radius:5px}
.note{display:block;margin:8px 0 6px;color:rgba(255,255,255,.72);font-size:16px;font-weight:600;max-width:1180px}
.sep{height:1px;background:linear-gradient(90deg,transparent,rgba(242,211,91,.5),transparent);margin:40px 0 28px}
'''+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">HOLDER RANK — PER WALLET, IN THE PER-WALLET BREAKDOWN</h1>
<div class="note">Each wallet's place in the PTGC and the UFO holder list. Ranks below are REAL — today's PulseScan holder lists, with example balances
(900M / 260M / 45M / 1.5M PTGC; 2.5B / 600M / none / 12M UFO). Names and addresses are made up.</div>
'''
NOTES={'A':'The rank sits under each wallet’s PTGC and UFO amounts — no new column, the table stays the same width. Quietest.',
       'B':'A HOLDER RANK column with a PTGC and a UFO pill per wallet; the bar up top shows each token’s best rank across your wallets.',
       'C':'B plus a next-step line ("▲ 12.4M more to pass #102"), a TOP 10 / 100 / 1,000 badge, two extra sort buttons, and in the ALL WALLETS row what your wallets would rank as ONE wallet.'}
out=HEAD
for i,o in enumerate('ABC'):
    if i: out+='<div class="sep"></div>'
    out+=f'<div class="opt">OPTION {o}</div><span class="note">{NOTES[o]}</span>'+section(o)
out+='</div></div></body></html>'
open(S+'/repo/design/portfolio/mock-ranks-v1.html','w').write(out); print('written',len(out))
