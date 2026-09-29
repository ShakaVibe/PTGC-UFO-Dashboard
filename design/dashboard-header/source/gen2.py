#!/usr/bin/env python3
"""Affiliates Report share card, round 2 (2026-09-29): built in the Value Generated card's language —
Rajdhani letter-spaced title + pill, glowing coin, one hero number, a split bar, accent tiles,
SocialNebulaBackdrop frame. Real September 2026 numbers from the live endpoint."""
import os, random
H = os.path.abspath(os.path.dirname(__file__))
FONTS = '/home/claude/ptgc/tools/harness/node_modules/@fontsource'
LOGO = 'file:///home/claude/ptgc/logos/ptgc/06_PTGC_V1_transparent_bg.png'
TROPHY = {'Whale':'file:///home/claude/ptgc/logos/ptgc/trophy_whale_gold.png','Shark':'file:///home/claude/ptgc/logos/ptgc/trophy_shark_silver.png','Dolphin':'file:///home/claude/ptgc/logos/ptgc/trophy_dolphin_gold.png'}

CSS = f"""
@font-face{{font-family:Orbitron;font-weight:700;src:url(file://{FONTS}/orbitron/files/orbitron-latin-700-normal.woff2)}}
@font-face{{font-family:Orbitron;font-weight:900;src:url(file://{FONTS}/orbitron/files/orbitron-latin-900-normal.woff2)}}
@font-face{{font-family:Rajdhani;font-weight:500;src:url(file://{FONTS}/rajdhani/files/rajdhani-latin-500-normal.woff2)}}
@font-face{{font-family:Rajdhani;font-weight:600;src:url(file://{FONTS}/rajdhani/files/rajdhani-latin-600-normal.woff2)}}
@font-face{{font-family:Rajdhani;font-weight:700;src:url(file://{FONTS}/rajdhani/files/rajdhani-latin-700-normal.woff2)}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:#000;font-family:Rajdhani,sans-serif;color:#fff;padding:26px 48px 30px}}
.orb{{font-family:Orbitron,sans-serif}}
.tn{{font-variant-numeric:tabular-nums}}
.emo{{font-family:'Noto Color Emoji';letter-spacing:0}}
.t-purple{{background:linear-gradient(180deg,#FBF5FF 0%,#EBD9FF 18%,#C69BFF 40%,#A36BFF 60%,#7B3FE4 82%,#4B1F9E 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.t-gold{{background:linear-gradient(180deg,#FAEAA0 0%,#F0DC78 18%,#E0B843 38%,#D4AF37 55%,#A8841C 78%,#7A5C12 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.t-sea{{background:linear-gradient(180deg,#F0FEFF 0%,#BDF4FF 20%,#67E1FF 42%,#22B8F0 62%,#1479C9 82%,#0B3F7A 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.bar{{display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:10px 14px;margin-bottom:24px}}
.pills{{display:inline-flex;align-items:center;gap:2px;padding:4px;border-radius:99px;background:rgba(0,0,0,.7)}}
.pills span{{padding:7px 13px;border-radius:99px;font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}}
.yr{{font-size:11px;font-weight:700;letter-spacing:.2em;padding:0 8px 0 10px;opacity:.55}}
.close{{position:absolute;right:48px;top:30px;font-size:22px;opacity:.6}}
.caption{{margin:16px auto 0;color:rgba(255,255,255,.6);font-size:19px;font-weight:600;line-height:1.35}}
.caption b{{color:#fff}}
"""

def stars(W, Hh, seed, n):
    r = random.Random(seed)
    return f'<svg width="{W}" height="{Hh}" style="position:absolute;inset:0">' + ''.join(
        f'<circle cx="{r.random()*W:.1f}" cy="{r.random()*Hh:.1f}" r="{0.6+r.random()*1.9:.1f}" fill="rgba(255,255,255,{0.15+r.random()*0.6:.2f})"/>' for _ in range(n)) + '</svg>'

def backdrop(W, Hh, rgb, edge, seed, tall=False, base='#07040b', watermark=True):
    wm = ('' if not watermark else
          (f'<img src="{LOGO}" style="position:absolute;left:50%;margin-left:-330px;top:190px;width:660px;height:660px;opacity:.09">' if tall else
           f'<img src="{LOGO}" style="position:absolute;right:-50px;top:30px;width:420px;height:420px;opacity:.09">'))
    return f'''
<div style="position:absolute;inset:0;background:radial-gradient(120% 80% at 50% 115%, rgba({rgb},.30) 0%, rgba({rgb},.12) 40%, rgba(0,0,0,0) 72%), linear-gradient(180deg,{base} 0%,{base} 60%,#0a080c 100%)"></div>
<div style="position:absolute;right:-200px;top:-260px;width:720px;height:720px;border-radius:50%;background:radial-gradient(circle, rgba({rgb},.30) 0%, rgba({rgb},.08) 40%, rgba(0,0,0,0) 68%)"></div>
<div style="position:absolute;left:-220px;bottom:-300px;width:760px;height:760px;border-radius:50%;background:radial-gradient(circle, rgba({rgb},.22) 0%, rgba({rgb},.06) 42%, rgba(0,0,0,0) 68%)"></div>
{stars(W,Hh,seed,110 if tall else 90)}{wm}
<div style="position:absolute;inset:14px;border-radius:26px;border:2px solid transparent;background:linear-gradient(#0000,#0000) padding-box, linear-gradient(180deg,{edge[0]} 0%,{edge[1]} 50%,{edge[2]} 100%) border-box;-webkit-mask:linear-gradient(#000 0 0) padding-box, linear-gradient(#000 0 0);-webkit-mask-composite:xor;mask-composite:exclude"></div>
<div style="position:absolute;inset:14px;border-radius:26px;box-shadow:0 0 0 1px rgba(255,255,255,.06) inset, 0 0 70px -8px rgba({rgb},.75), 0 0 24px -4px rgba({rgb},.5)"></div>
<div style="position:absolute;left:90px;right:90px;top:14px;height:2px;background:linear-gradient(90deg, rgba(255,255,255,0), {edge[0]}, rgba(255,255,255,0))"></div>'''

MONTHS = ['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP']
def toolbar(th, tall=False):
    ring, glow, grad, ontxt, offtxt = th['ring'], th['glow'], th['grad'], th['on'], th['off']
    m = ''.join(f'<span style="{"background:"+grad+";color:"+ontxt+";box-shadow:0 0 16px "+glow+", inset 0 1px 0 rgba(255,255,255,.45)" if x=="SEP" else "color:"+offtxt}">{x}</span>' for x in MONTHS)
    w = ('<span style="color:%s">▭ Wide</span><span style="background:%s;color:%s;box-shadow:0 0 16px %s">▯ Tall</span>' if tall else
         '<span style="background:%s;color:%s;box-shadow:0 0 16px %s">▭ Wide</span><span style="color:%s">▯ Tall</span>')
    w = (w % (offtxt, grad, ontxt, glow)) if tall else (w % (grad, ontxt, glow, offtxt))
    return (f'<div class="close">×</div><div class="bar"><div class="pills" style="border:1px solid {ring};box-shadow:0 0 26px -8px {glow}"><span class="yr" style="color:{offtxt}">2026</span>{m}</div>'
            f'<div class="pills" style="border:1px solid {ring};box-shadow:0 0 26px -8px {glow}">{w}</div></div>')

def page(tb, card, caption, W):
    return f'<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body style="width:{W+96}px">{tb}<div style="position:relative;width:{W}px;margin:0 auto">{card}</div><div class="caption" style="width:{W}px">{caption}</div></body></html>'

# ---------------- live numbers (2026-09-29, /public/commissions) ----------------
M = dict(long='September 2026', pill="SEP '26", ref=12, buys=171, ptgc='1.96B', usd='$91,934', comm='39.12M', avg='$538', creat=[('🦈','Shark',5),('🐬','Dolphin',8),('🦑','Squid',7)])
A = dict(ref=71, buys='1,439', ptgc='7.37B', usd='$580,253', comm='146.70M', paid='107.58M')
TOP = [('@ptgcofficialonboard','1.42B','$67,938',18),('DomDoos','196.95M','$9,341',79),('getrichdiefinessing','126.14M','$5,452',12),('DeFiMission','70.41M','$2,784',14),('McCloud','41.03M','$1,818',15)]
SHARE = [('@ptgcofficialonboard',72.4,'#C084FC'),('DomDoos',10.0,'#E8C044'),('getrichdiefinessing',6.4,'#38BDF8'),('DeFiMission',3.6,'#34D399'),('8 others',7.6,'#64748B')]

def tile(icon, label, value, sub, accent, z):
    return f'''<div style="flex:1 1 0;min-width:0;position:relative;border-radius:16px;padding:{z['tp']};background:linear-gradient(180deg,rgba(24,14,40,.92),rgba(10,6,20,.95));border:1px solid rgba(255,255,255,.10);box-shadow:inset 0 1px 0 rgba(255,255,255,.08), 0 0 22px -10px {accent};overflow:hidden">
<div style="position:absolute;left:0;top:10px;bottom:10px;width:3px;border-radius:3px;background:{accent};box-shadow:0 0 10px {accent}"></div>
<div style="font-size:{z['tl']}px;letter-spacing:.14em;text-transform:uppercase;font-weight:700;color:{accent};white-space:nowrap;display:flex;align-items:center;gap:7px"><span class="emo" style="font-size:1.25em">{icon}</span>{label}</div>
<div class="tn" style="font-size:{z['tv']}px;font-weight:700;line-height:1.05;margin-top:8px;white-space:nowrap">{value}</div>
<div class="tn" style="font-size:{z['tq']}px;font-weight:600;color:rgba(255,255,255,.62);margin-top:5px;white-space:nowrap">{sub}</div></div>'''

def coin(size, rgb, ring):
    return f'''<div style="position:relative;width:{size}px;height:{size}px;flex-shrink:0"><div style="position:absolute;inset:-{int(size*.2)}px;border-radius:50%;background:radial-gradient(circle, rgba({rgb},.45) 0%, rgba(0,0,0,0) 68%)"></div>
<img src="{LOGO}" style="position:relative;width:{size}px;height:{size}px;border-radius:50%;box-shadow:0 0 0 3px {ring}, 0 0 0 6px rgba({rgb},.3), 0 0 46px rgba({rgb},.75)"></div>'''

def title(icon, text, cls, pill, pillbg, pillfg, glow, size, center=False):
    return f'''<div style="display:flex;align-items:center;gap:16px;{"justify-content:center;" if center else ""}font-size:{size}px;font-weight:700;letter-spacing:.18em;text-transform:uppercase;line-height:1">
<span class="emo" style="font-size:.9em">{icon}</span><span class="{cls}" style="filter:drop-shadow(0 0 14px {glow})">{text}</span>
<span style="font-size:.6em;letter-spacing:.14em;color:{pillfg};background:{pillbg};padding:.28em .7em .22em;border-radius:999px;box-shadow:0 0 18px {glow}">{pill}</span></div>'''

def site(cls, sub, date='Sep 29, 2026'):
    return f'''<div style="text-align:right;flex-shrink:0"><div class="orb {cls}" style="font-size:24px;font-weight:700;line-height:1">ptgc-ufo.com</div>
<div style="margin-top:10px;font-size:14px;letter-spacing:.26em;text-transform:uppercase;color:rgba(255,255,255,.4)"><span style="color:#E8C044">PTGC</span> · {sub}</div>
<div class="tn" style="margin-top:6px;font-size:13px;letter-spacing:.08em;color:rgba(255,255,255,.3)">{date}</div></div>'''

def creatures_inline(size, cnt, col):
    return ''.join(f'<span style="display:inline-flex;align-items:center;gap:3px;margin-right:12px"><span class="emo" style="font-size:{size}px">{e}</span><b style="font-size:{cnt}px;color:{col}">x{n}</b></span>' for e,_,n in M['creat'])

def share_bar(z, center=False):
    segs = ''.join(f'<div style="width:{p}%;background:{c};box-shadow:0 0 14px {c}"></div>' for _,p,c in SHARE)
    leg = ''.join(f'<span style="display:inline-flex;align-items:center;gap:7px;white-space:nowrap"><span style="width:.6em;height:.6em;border-radius:50%;background:{c};box-shadow:0 0 8px {c}"></span>{n} <b class="tn" style="color:#fff">{p:.0f}%</b></span>' for n,p,c in SHARE)
    return f'''<div style="width:100%"><div style="font-size:{z['leg']-2}px;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,.45);font-weight:700;margin-bottom:8px;{"text-align:center" if center else ""}">Who referred it · share of the month's PTGC</div>
<div style="display:flex;height:{z['barH']}px;border-radius:99px;overflow:hidden;background:rgba(255,255,255,.07);border:1px solid rgba(192,132,252,.25)">{segs}</div>
<div style="display:flex;flex-wrap:wrap;gap:6px 22px;margin-top:10px;font-size:{z['leg']}px;color:rgba(255,255,255,.8);{"justify-content:center" if center else ""}">{leg}</div></div>'''

PUR = dict(rgb='168,85,247', edge=['#EBD9FF','#A855F7','#4B1F9E'], ring='rgba(192,132,252,.4)', glow='rgba(168,85,247,.6)', grad='linear-gradient(180deg,#F5E9FF 0%,#C084FC 50%,#7E22CE 100%)', on='#1c0633', off='rgba(233,213,255,.7)',
           pillbg='linear-gradient(180deg,#F1E4FF,#B57BFF 55%,#7E22CE)', pillfg='#1c0633')
GLD = dict(rgb='232,192,68', edge=['#FFF8DC','#E8C044','#6B4E0E'], ring='rgba(250,204,21,.4)', glow='rgba(232,192,68,.55)', grad='linear-gradient(180deg,#FFF8DC,#E8C044 55%,#A67C1E)', on='#2a1d05', off='rgba(254,240,138,.7)',
           pillbg='linear-gradient(180deg,#FFF8DC,#E8C044 55%,#A67C1E)', pillfg='#2a1d05')
SEA = dict(rgb='34,184,240', edge=['#E0FAFF','#22B8F0','#0B3F7A'], ring='rgba(56,189,248,.4)', glow='rgba(34,184,240,.6)', grad='linear-gradient(180deg,#E0FAFF 0%,#38BDF8 50%,#0369A1 100%)', on='#021a2b', off='rgba(186,230,253,.72)',
           pillbg='linear-gradient(180deg,#E0FAFF,#38BDF8 55%,#0369A1)', pillfg='#021a2b')

ZW = dict(W=1200,H=675,pad=48,top=38,bottom=34,title=38,logo=170,big=118,note=25,barH=16,leg=17,tl=15,tv=34,tq=16,tp='13px 14px 14px 18px',gap=12)
ZT = dict(W=1080,H=1350,pad=56,top=54,bottom=44,title=48,logo=220,big=160,note=32,barH=20,leg=22,tl=19,tv=46,tq=21,tp='18px 20px 20px 24px',gap=16)

# ================= D · Program report (purple, the Value Generated layout) =================
def tiles_d(z):
    return [
        ('🤝','Referrers',str(M['ref']),'active this month','#C084FC'),
        ('🛒','Buys',str(M['buys']),f"avg {M['avg']} each",'#38BDF8'),
        ('🪙','PTGC referred',M['ptgc'],creatures_inline(int(z['tq']*1.2),z['tq'],'rgba(255,255,255,.6)'),'#E8C044'),
        ('💸','Commissions',M['comm'],'PTGC at 2%','#34D399'),
        ('🌌','All-time',A['usd'],f"{A['ptgc']} PTGC · {A['buys']} buys",'#F472B6'),
    ]

def mock_d(tall=False):
    z = ZT if tall else ZW; th = PUR
    t = title('🤝','Affiliate report','t-purple',M['pill'],th['pillbg'],th['pillfg'],'rgba(168,85,247,.55)',z['title'],center=tall)
    amount = f'''<div style="font-size:{z['note']}px;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,.55);font-weight:600;{"text-align:center" if tall else ""}"><span style="color:#E8C044">PTGC</span> · bought through referral links</div>
<div class="t-purple tn" style="font-size:{z['big']}px;font-weight:700;line-height:.95;margin-top:6px;{"text-align:center" if tall else ""}">{M['usd']}</div>
<div style="font-size:{z['note']}px;color:rgba(255,255,255,.72);margin-top:10px;line-height:1.25;{"text-align:center" if tall else ""}"><b style="color:#fff">{M['ptgc']} PTGC</b> in <b style="color:#fff">{M['buys']}</b> buys from <b style="color:#fff">{M['ref']}</b> referrers</div>'''
    tl = ''.join(tile(*x, z=z) for x in tiles_d(z))
    if tall:
        tl_html = f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:{z["gap"]}px">{tl}</div>'
        inner = f'''{t}<div style="display:flex;justify-content:center;margin-top:28px">{coin(z['logo'],th['rgb'],'rgba(216,180,254,.9)')}</div><div style="margin-top:24px">{amount}</div>
<div style="flex:1"></div>{share_bar(z,True)}<div style="margin-top:22px">{tl_html}</div>
<div style="margin-top:22px;display:flex;justify-content:center;align-items:center;gap:18px;font-size:18px;letter-spacing:.2em;text-transform:uppercase"><span class="orb" style="font-size:28px;font-weight:700;letter-spacing:0;text-transform:none;color:#F3E8FF;text-shadow:0 0 18px rgba(168,85,247,.6)">ptgc-ufo.com</span><span style="color:rgba(240,230,255,.75)">· <span style="color:#E8C044">PTGC</span> · Sep 29, 2026</span></div>'''
    else:
        inner = f'''<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:24px">{t}{site('t-purple',"referrals, sep '26")}</div>
<div style="display:flex;align-items:center;gap:30px;margin-top:16px">{coin(z['logo'],th['rgb'],'rgba(216,180,254,.9)')}<div style="flex:1;min-width:0">{amount}</div></div>
<div style="flex:1;min-height:14px"></div>{share_bar(z)}<div style="display:flex;gap:{z['gap']}px;margin-top:18px">{tl}</div>'''
    card = f'''<div style="position:relative;overflow:hidden;width:{z['W']}px;height:{z['H']}px;background:#07040b">{backdrop(z['W'],z['H'],th['rgb'],th['edge'],5,tall)}
<div style="position:absolute;left:{z['pad']}px;right:{z['pad']}px;top:{z['top']}px;bottom:{z['bottom']}px;display:flex;flex-direction:column">{inner}</div></div>'''
    return page(toolbar(th,tall), card, ('<b>D · Program report (Tall).</b>' if tall else '<b>D · Program report.</b> The Value Generated layout in the Affiliates page\'s purple: the month\'s referred dollars as the hero, the PTGC / buys / referrers line under it, a bar showing who referred it, and five accent tiles including all-time.'), z['W'])

# ================= E · Champions podium (gold) =================
def mock_e():
    z = ZW; th = GLD
    t = title('🏆','Affiliate champions','t-gold',M['pill'],th['pillbg'],th['pillfg'],'rgba(232,192,68,.55)',z['title'])
    def pillar(rank, h, medal, n, p, u, b, glow):
        return f'''<div style="width:252px;display:flex;flex-direction:column;align-items:center">
<div class="emo" style="font-size:{58 if rank==1 else 46}px;filter:drop-shadow(0 0 16px {glow})">{medal}</div>
<div style="font-size:{25 if rank==1 else 22}px;font-weight:700;color:#fff;margin-top:6px;white-space:nowrap;max-width:252px;overflow:hidden;text-overflow:ellipsis">{n}</div>
<div class="t-gold tn" style="font-size:{46 if rank==1 else 36}px;font-weight:700;line-height:1.05">{p}</div>
<div class="tn" style="font-size:17px;font-weight:600;color:rgba(255,255,255,.62)">{u} · {b} buys</div>
<div style="margin-top:12px;width:100%;height:{h}px;border-radius:16px 16px 6px 6px;background:linear-gradient(180deg,rgba({glow[5:-4]},.30),rgba({glow[5:-4]},.06));border:1px solid rgba({glow[5:-4]},.6);border-bottom:none;box-shadow:inset 0 1px 0 rgba(255,255,255,.25), 0 0 34px -8px {glow};display:flex;align-items:flex-start;justify-content:center;padding-top:10px"><span class="orb" style="font-size:40px;font-weight:900;color:rgba(255,255,255,.18)">{rank}</span></div></div>'''
    pod = (pillar(2,88,'🥈',*TOP[1][:3],TOP[1][3],'rgba(203,213,225,.7)') +
           pillar(1,128,'🥇',*TOP[0][:3],TOP[0][3],'rgba(232,192,68,.8)') +
           pillar(3,64,'🥉',*TOP[2][:3],TOP[2][3],'rgba(217,119,6,.7)'))
    stat = lambda l,v,c: f'<div style="padding:10px 0;border-bottom:1px solid rgba(232,192,68,.16)"><div style="font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:rgba(254,240,138,.55);font-weight:700">{l}</div><div class="tn {c}" style="font-size:31px;font-weight:700;line-height:1.1">{v}</div></div>'
    side = (stat('Referred this month', M['usd'], 't-gold') + stat('PTGC', M['ptgc'], '') + stat('Buys · referrers', f"{M['buys']} · {M['ref']}", '') +
            stat('Commissions', M['comm']+' <span style="font-size:18px;color:rgba(255,255,255,.55)">PTGC</span>', ''))
    at = f'''<div style="margin-top:12px;font-size:13px;letter-spacing:.2em;text-transform:uppercase;color:rgba(254,240,138,.55);font-weight:700">All-time</div>
<div class="tn" style="font-size:20px;font-weight:700;color:rgba(255,255,255,.85);line-height:1.3">{A['usd']} · {A['ptgc']} PTGC<br><span style="color:rgba(255,255,255,.55);font-size:17px">{A['ref']} referrers · {A['paid']} PTGC paid</span></div>'''
    base = '<div style="position:absolute;left:0;right:0;bottom:0;height:3px;background:linear-gradient(90deg,rgba(232,192,68,0),#E8C044,rgba(232,192,68,0));box-shadow:0 0 18px rgba(232,192,68,.8)"></div>'
    inner = f'''<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:24px">{t}{site('t-gold',"referrals, sep '26")}</div>
<div style="flex:1;display:flex;gap:34px;margin-top:10px;min-height:0">
 <div style="position:relative;flex:1;display:flex;align-items:flex-end;justify-content:center;gap:10px">{pod}{base}</div>
 <div style="width:290px;display:flex;flex-direction:column;justify-content:flex-end;padding-bottom:4px">{side}{at}</div></div>'''
    card = f'''<div style="position:relative;overflow:hidden;width:1200px;height:675px;background:#0a0804">{backdrop(1200,675,th['rgb'],th['edge'],17,base='#0a0804',watermark=False)}
<div style="position:absolute;left:{z['pad']}px;right:{z['pad']}px;top:{z['top']}px;bottom:{z['bottom']}px;display:flex;flex-direction:column">{inner}</div></div>'''
    return page(toolbar(th), card, '<b>E · Champions podium.</b> The month\'s top three referrers on a lit gold podium (medal, name, PTGC, dollars, buys), month totals and all-time down the right. Gold like the DAO Buys card.', 1200)

# ================= F · The month's haul (ocean) =================
def mock_f():
    z = ZW; th = SEA
    t = title('🌊','Affiliate haul','t-sea',M['pill'],th['pillbg'],th['pillfg'],'rgba(34,184,240,.55)',z['title'])
    bubble = lambda e,n,c: f'''<div style="display:flex;flex-direction:column;align-items:center;width:168px">
<div style="position:relative;width:132px;height:132px;border-radius:50%;background:radial-gradient(circle at 35% 30%, rgba(224,250,255,.22), rgba(34,184,240,.10) 45%, rgba(3,20,40,.6) 100%);border:1px solid rgba(125,211,252,.55);box-shadow:inset 0 0 24px rgba(125,211,252,.25), 0 0 34px -6px rgba(34,184,240,.8);display:flex;align-items:center;justify-content:center">
<span class="emo" style="font-size:70px">{e}</span><span class="tn" style="position:absolute;right:-6px;bottom:-4px;font-size:26px;font-weight:700;color:#021a2b;background:linear-gradient(180deg,#E0FAFF,#38BDF8 55%,#0369A1);padding:1px 11px;border-radius:99px;box-shadow:0 0 14px rgba(34,184,240,.7)">x{c}</span></div>
<div style="margin-top:10px;font-size:17px;letter-spacing:.2em;text-transform:uppercase;color:rgba(186,230,253,.75);font-weight:700">{n}</div></div>'''
    bubbles = ''.join(bubble(e,n,c) for e,n,c in M['creat'])
    tl = ''.join(tile(*x, z=z) for x in [
        ('🤝','Referrers',str(M['ref']),f"{M['buys']} buys","#38BDF8"),
        ('💵','USD value',M['usd'],f"avg {M['avg']} a buy","#34D399"),
        ('💸','Commissions',M['comm'],'PTGC at 2%','#C084FC'),
        ('🥇','Top referrer',TOP[0][1],TOP[0][0],'#E8C044'),
        ('🌌','All-time',A['ptgc'],f"{A['usd']} · {A['ref']} referrers",'#F472B6')])
    inner = f'''<div style="display:flex;justify-content:space-between;align-items:flex-start;gap:24px">{t}{site('t-sea',"referrals, sep '26")}</div>
<div style="display:flex;align-items:center;gap:26px;margin-top:22px">
 <div style="width:420px"><div style="font-size:{z['note']}px;letter-spacing:.22em;text-transform:uppercase;color:rgba(255,255,255,.55);font-weight:600"><span style="color:#E8C044">PTGC</span> referred · {M['long']}</div>
 <div class="t-sea tn" style="font-size:112px;font-weight:700;line-height:.95;margin-top:6px">{M['ptgc']}</div>
 <div style="font-size:{z['note']}px;color:rgba(255,255,255,.72);margin-top:10px">that's this many sea creatures of supply →</div></div>
 <div style="flex:1;display:flex;justify-content:space-around">{bubbles}</div></div>
<div style="flex:1"></div><div style="display:flex;gap:{z['gap']}px">{tl}</div>'''
    card = f'''<div style="position:relative;overflow:hidden;width:1200px;height:675px;background:#03080d">{backdrop(1200,675,th['rgb'],th['edge'],29,base='#03080d')}
<div style="position:absolute;left:{z['pad']}px;right:{z['pad']}px;top:{z['top']}px;bottom:{z['bottom']}px;display:flex;flex-direction:column">{inner}</div></div>'''
    return page(toolbar(th), card, '<b>F · The haul.</b> Ocean-blue, built around your sea creatures: the month\'s PTGC as the hero and the creatures it adds up to in glowing bubbles, then five accent tiles.', 1200)

for name, fn in [('d', mock_d), ('d-tall', lambda: mock_d(True)), ('e', mock_e), ('f', mock_f)]:
    open(os.path.join(H, f'mock-{name}.html'), 'w').write(fn())
print('written')
