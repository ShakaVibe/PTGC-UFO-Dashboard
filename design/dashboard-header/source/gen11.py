#!/usr/bin/env python3
"""PTGC dashboard header — a pixel-placed copy of Shaka's reference (2026-09-29), measured on his 2166×636 image.
Our BUY/SELL + SWITCH in the reference's two button slots, live numbers, The Grays X-banner art placed so the alien's
head sits where the reference's does. Everything is absolutely positioned in the reference's coordinates."""
import os, json, importlib.util, sys
H = os.path.abspath(os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location('g10', os.path.join(H, 'gen10.py')); g10 = importlib.util.module_from_spec(spec)
_a = sys.argv; sys.argv = ['x']; spec.loader.exec_module(g10); sys.argv = _a
CSS, spark, SER, ICON, INFO = g10.CSS + '''
.t-ref{background:linear-gradient(180deg,#FEF7C0 0%,#FFE58E 14%,#FFDA72 34%,#FFD066 52%,#F0B544 62%,#D59A36 74%,#A87226 90%,#B87A28 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.t-price{background:linear-gradient(180deg,#FFF6D6 0%,#FBE6B0 24%,#F8D88C 42%,#F6C866 58%,#EEB852 74%,#E3A945 90%,#D69C40 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.t-price sub{-webkit-text-fill-color:#F0BE5E}
.t-ref2{background:linear-gradient(180deg,#FFE9A8 0%,#F6D27A 30%,#F0C35E 50%,#DCA03A 72%,#C88E31 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
''', g10.spark, g10.SER, g10.ICON, g10.INFO
R = '/home/claude/ptgc'
BNR, GROUND = f'file://{R}/logos/combined/TheGraysXBnr.png', f'file://{R}/logos/home/cosmic-ground.jpg'
PTGC, UFO = f'file://{R}/06_PTGC_V1_transparent_bg.png', f'file://{R}/07_Ufo_transparent.png'
UP, GOLD = '#2BE07F', '#E9B949'
W, BH = 2166, 336          # page width, banner height (reference: y 12 → 348)
S = 0.75                   # banner art scale: head 300 px wide, eyes 150 apart, like the reference
AW = int(2048 * S)         # 1536

def ab(x, y, inner, extra=''):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;{extra}">{inner}</div>'

def info(sz=18):
    return f'<span style="display:inline-flex;width:{sz}px;height:{sz}px;border-radius:50%;border:1.6px solid rgba(255,255,255,.85);font-size:{sz*0.62:.0f}px;align-items:center;justify-content:center;font-weight:700;color:#fff;margin-left:10px;vertical-align:1px">i</span>'

BG, HEAD = f'file://{R}/logos/home/dash-bg.png', f'file://{R}/logos/home/alien-head.png'
def art():
    # Shaka's background band + his transparent alien head, sized and placed like the reference (eyes 150 px apart)
    hs = 0.385; hw, hh = round(1330 * hs), round(1182 * hs)
    return f'''
<img src="{BG}" style="position:absolute;left:0;top:-7px;width:{W}px;height:350px">
<img src="{BG}" style="position:absolute;left:-262px;top:-26px;width:2428px;height:392px;-webkit-mask-image:linear-gradient(90deg,transparent 0px,transparent 1300px,#000 1420px)">
<img src="{HEAD}" style="position:absolute;left:1395px;top:-135px;width:{hw}px;height:{hh}px;-webkit-mask-image:linear-gradient(180deg,#000 0%,#000 74%,transparent 96%);filter:brightness(.78) contrast(1.12) saturate(.95) drop-shadow(10px 0 16px rgba(90,255,90,.35)) drop-shadow(-8px 0 14px rgba(255,170,50,.25))">
<div style="position:absolute;left:-120px;top:40px;width:1700px;height:300px;background:radial-gradient(ellipse 50% 50% at 50% 52%, rgba(0,0,0,.55) 0%, rgba(0,0,0,.4) 55%, rgba(0,0,0,0) 100%)"></div>
<div style="position:absolute;left:280px;top:80px;width:380px;height:240px;background:radial-gradient(closest-side, rgba(0,0,0,.6), rgba(0,0,0,0))"></div>
<div style="position:absolute;left:630px;top:100px;width:370px;height:210px;background:radial-gradient(closest-side, rgba(0,0,0,.7), rgba(0,0,0,0))"></div>
<div style="position:absolute;left:990px;top:130px;width:500px;height:170px;background:radial-gradient(closest-side, rgba(0,0,0,.65), rgba(0,0,0,0))"></div>
<div style="position:absolute;left:960px;top:150px;width:660px;height:140px;background:radial-gradient(closest-side, rgba(0,0,0,.72), rgba(0,0,0,.45) 60%, rgba(0,0,0,0))"></div>
<div style="position:absolute;left:1330px;top:150px;width:300px;height:130px;background:radial-gradient(closest-side, rgba(0,0,0,.7), rgba(0,0,0,0))"></div>
<div style="position:absolute;left:640px;top:40px;width:360px;height:170px;background:radial-gradient(closest-side, rgba(0,0,0,.7), rgba(0,0,0,0))"></div>
<div style="position:absolute;left:1760px;top:60px;width:410px;height:270px;background:radial-gradient(closest-side, rgba(0,0,0,.7), rgba(0,0,0,.35) 70%, rgba(0,0,0,0))"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:18px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(3,8,8,.8))"></div>'''

CORONA = f'file://{R}/logos/home/coin-corona.png'
def coin():
    # no extra rim — the logo with a fire corona behind it (a generated flame image, not rings), star flare on top
    return f'''<div style="position:absolute;left:85px;top:88px;width:195px;height:195px">
<div style="position:absolute;inset:-70px;border-radius:50%;background:radial-gradient(circle, rgba(255,120,20,.22) 45%, rgba(255,90,10,.06) 60%, rgba(0,0,0,0) 72%)"></div>
<img src="{CORONA}" style="position:absolute;left:-162px;top:-162px;width:520px;height:520px;mix-blend-mode:screen">
<div style="position:absolute;left:104px;top:-8px;width:30px;height:9px;border-radius:50%;background:radial-gradient(closest-side, #fff, rgba(255,220,130,.7) 45%, rgba(255,180,60,0))"></div>
<div style="position:absolute;left:118px;top:-18px;width:2px;height:30px;background:linear-gradient(180deg, rgba(255,240,200,0), #fff 50%, rgba(255,240,200,0))"></div>
<div style="position:absolute;left:100px;top:-4px;width:40px;height:1.5px;background:linear-gradient(90deg, rgba(255,240,200,0), #fff 50%, rgba(255,240,200,0))"></div>
<img src="{PTGC}" style="position:relative;width:195px;height:195px;border-radius:50%;filter:brightness(1.08) contrast(1.05);box-shadow:0 0 10px 2px rgba(255,190,80,.55)"></div>'''

def buttons():
    # back to the solid-gold BUY/SELL (Shaka: "your buttons were better"), SWITCH with a green edge and glow
    buy = f'''<div style="position:absolute;left:1840px;top:106px;width:250px;height:72px;border-radius:14px;display:flex;align-items:center;padding:0 0 0 14px;gap:18px;overflow:hidden;background:linear-gradient(180deg,#F8DB7C 0%,#E7B843 50%,#C58F22 100%);box-shadow:inset 0 1px 0 rgba(255,255,255,.65), 0 0 24px rgba(240,180,60,.6), 0 8px 20px -6px rgba(0,0,0,.9)">
<div style="position:absolute;inset:0;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,0.18) 47%,rgba(255,255,255,0.28) 50%,rgba(255,255,255,0.18) 53%,transparent 60%)"></div>
<img src="{PTGC}" style="position:relative;width:50px;height:50px;border-radius:50%;box-shadow:0 0 0 2px rgba(40,26,2,.5)">
<div class="orb" style="position:relative;display:flex;flex-direction:column;align-items:center;color:#241802;font-weight:900;font-size:19px;letter-spacing:.2em;line-height:1"><span>BUY</span><span style="width:96px;height:1.5px;background:rgba(36,24,2,.45);margin:7px 0"></span><span>SELL</span></div></div>'''
    sw = f'''<div style="position:absolute;left:1840px;top:198px;width:250px;height:72px;border-radius:14px;display:flex;align-items:center;padding:0 0 0 14px;gap:22px;background:linear-gradient(135deg, rgba(124,252,0,.22), rgba(124,252,0,.06)), #070a05;border:1.5px solid rgba(157,255,58,.75);box-shadow:0 0 22px -4px rgba(124,252,0,.65), 0 8px 20px -6px rgba(0,0,0,.9), inset 0 1px 0 rgba(255,255,255,.1)">
<img src="{UFO}" style="width:50px;height:50px;border-radius:50%;box-shadow:0 0 14px rgba(124,252,0,.7)">
<span class="orb" style="font-size:19px;font-weight:700;letter-spacing:.22em;color:#fff">SWITCH</span></div>'''
    return buy + sw

def vline(x, y1, y2):
    return f'<div style="position:absolute;left:{x}px;top:{y1}px;width:1.5px;height:{y2-y1}px;background:rgba(235,235,235,.55)"></div>'

def stat(x, label, val):
    return ab(x, 179, f'<div style="font-size:19px;font-weight:600;letter-spacing:.14em;color:#fff;white-space:nowrap;text-shadow:0 1px 3px #000">{label}{info()}</div>') + \
           ab(x - 2, 205, f'<div class="t-ref2 tn" style="font-size:46px;font-weight:700;line-height:1;white-space:nowrap;filter:drop-shadow(0 2px 3px rgba(0,0,0,1)) drop-shadow(0 0 12px rgba(0,0,0,.9))">{val}</div>')

def banner():
    calicon = '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E9B949" stroke-width="2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>'
    copy = '<svg width="20" height="22" viewBox="0 0 24 26" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="2"><rect x="5" y="5" width="14" height="18" rx="2"/><path d="M9 3h6v4H9z" fill="rgba(255,255,255,.75)"/><path d="M8 12h8M8 16h8"/></svg>'
    body = coin() + \
        ab(308, 98, '<div class="orb t-ref" style="font-size:80px;font-weight:900;line-height:1;letter-spacing:.01em;filter:drop-shadow(0 2px 2px rgba(0,0,0,.9))">PTGC</div>') + \
        ab(312, 190, f'<div class="tn" style="display:flex;align-items:center;gap:14px;font-size:24px;font-weight:500;letter-spacing:.03em;color:rgba(255,255,255,.82)">0x9453...DE93 {copy}</div>') + \
        ab(312, 238, f'<div style="display:flex;align-items:center;gap:14px;width:205px;height:45px;box-sizing:border-box;padding:0 0 0 18px;border-radius:99px;border:1.6px solid rgba(233,185,73,.85);background:rgba(10,8,2,.55)">{calicon}<span style="font-size:18px;font-weight:700;letter-spacing:.14em;color:rgba(255,255,255,.85)">DAY</span><span class="orb t-ref2" style="font-size:21px;font-weight:700">1,084</span></div>') + \
        vline(645, 133, 263) + \
        ab(645, 118, f'<div style="width:332px;text-align:center"><div class="t-price tn" style="font-size:66px;font-weight:700;line-height:1;filter:drop-shadow(0 2px 3px rgba(0,0,0,1)) drop-shadow(0 0 14px rgba(0,0,0,.9))">$0.0<sub>4</sub>4080</div>'
                     f'<div class="tn" style="margin-top:14px;display:flex;align-items:center;justify-content:center;gap:14px;font-size:40px;font-weight:700;color:#12E28A;line-height:1;text-shadow:0 1px 4px #000, 0 0 14px #000">'
                     f'<svg width="30" height="26" viewBox="0 0 30 26" style="filter:drop-shadow(0 0 6px rgba(0,230,120,.5))"><defs><linearGradient id="ua" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6BF7A8"/><stop offset="1" stop-color="#00C865"/></linearGradient></defs><path d="M15 1 L29 25 L1 25 Z" fill="url(#ua)"/></svg>+10.89%</div>'
                     f'<div style="margin-top:8px;font-size:21px;font-weight:500;color:rgba(255,255,255,.7)">24h change</div></div>') + \
        vline(977, 133, 263) + \
        stat(1017, 'PLS RATIO', '3.72') + vline(1167, 210, 263) + stat(1207, "X'S TO ATH", '32.6x') + vline(1364, 210, 263) + stat(1400, "X'S TO A PENNY", '245x') + \
        buttons()
    return f'<div style="position:absolute;left:0;top:0;width:{W}px;height:{BH}px;overflow:hidden;background:#050504">{art()}{body}</div>'

def tabs():
    y = BH
    xs = [(40, 'Dashboard'), (204, 'KPI Report'), (359, 'Socials'), (485, 'Calculators'), (644, 'Charts'), (764, 'Live Feed'), (978, 'Portfolio'), (1113, 'Affiliates')]
    out = ''
    for x, t in xs:
        on = t == 'Dashboard'
        out += ab(x, 18, f'<div style="font-size:21px;font-weight:{700 if on else 500};color:{"#F1C552" if on else "rgba(255,255,255,.9)"};white-space:nowrap">{t}</div>')
    out += ab(858, 20, '<div style="font-size:15px;font-weight:800;letter-spacing:.08em;color:#241802;background:linear-gradient(180deg,#F8DB7C,#DDA932);padding:3px 14px 2px;border-radius:99px">NEW</div>')
    out += '<div style="position:absolute;left:35px;top:55px;width:112px;height:5px;border-radius:3px;background:linear-gradient(90deg,#F8DB7C,#E7B843);box-shadow:0 0 10px rgba(232,192,68,.7)"></div>'
    out += ab(1913, 25, f'<div style="width:12px;height:12px;border-radius:50%;background:{UP};box-shadow:0 0 8px {UP}"></div>')
    out += ab(1959, 18, '<div style="font-size:19px;font-weight:500;color:rgba(255,255,255,.72)">Updated 19s ago</div>')
    out += ab(2096, 18, '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="2"><path d="M4 12a8 8 0 1 0 2.3-5.6"/><path d="M4 4v4h4"/><path d="M12 8v4l3 2"/></svg>')
    return f'<div style="position:absolute;left:0;top:{y}px;width:{W}px;height:60px;background:#050d0e;border-top:1px solid rgba(233,185,73,.25);border-bottom:1px solid rgba(255,255,255,.07)">{out}</div>'

def tile(x, w, key, label, val, sub, hot=False, badge='', col='#E9B949', gid='g', valcol='#fff'):
    y, h = BH + 88, 186
    bg = ('linear-gradient(180deg,rgba(40,32,12,.9) 0%,rgba(24,20,10,.95) 45%,rgba(70,52,14,.9) 100%)' if hot
          else 'linear-gradient(180deg,rgba(18,19,14,.96) 0%,rgba(14,14,10,.97) 55%,rgba(34,28,12,.95) 100%)')
    bd = 'rgba(240,196,90,.95)' if hot else 'rgba(190,150,70,.5)'
    glow = ', 0 0 22px -4px rgba(240,190,70,.6)' if hot else ''
    return f'''<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;border-radius:14px;background:{bg};border:1.6px solid {bd};box-shadow:inset 0 1px 0 rgba(255,235,170,.1){glow};overflow:hidden">
<div style="position:absolute;left:20px;top:18px;display:flex;align-items:center;gap:16px;white-space:nowrap;font-size:19px;font-weight:500;letter-spacing:.03em;color:rgba(255,255,255,.88)"><svg width="30" height="30" viewBox="0 0 24 24" style="color:{GOLD}">{ICON[key]}</svg>{label}</div>
<div style="position:absolute;right:16px;top:18px;font-size:15px;font-weight:700;color:{GOLD}">{badge}</div>
<div class="tn" style="position:absolute;left:24px;top:60px;font-size:38px;font-weight:700;color:{valcol};line-height:1;white-space:nowrap">{val}</div>
<div class="tn" style="position:absolute;left:25px;top:103px;font-size:21px;font-weight:700;color:{UP};white-space:nowrap">{sub}</div>
<div style="position:absolute;left:22px;right:18px;bottom:14px">{spark(SER[key], 240, 60, col, gid)}</div></div>'''

def tiles():
    T = [
        (35, 277, 'mcap', 'MARKET CAP', '$11,730,465', '▲ 10.89%', dict(hot=True, gid='a', valcol='#FBE7B0')),
        (331, 293, 'vol', 'VOLUME 24H', '$142,521', '▲ 127.2% <span style="color:rgba(255,255,255,.62);font-weight:500">vs 7d avg</span>', dict(gid='b')),
        (643, 278, 'liq', 'LIQUIDITY', '$1,146,549', '', dict(badge='RH', gid='c')),
        (941, 272, 'ratio', 'LIQ / MCAP', '9.77%', '', dict(col='#C9DC4A', gid='d')),
        (1232, 274, 'hold', 'HOLDERS', '18,117', '<span style="font-size:1em">🠕</span> +2', dict(badge=info(20).replace('margin-left:10px', 'margin-left:0'), gid='e')),
        (1525, 295, 'lp', 'TOKENS IN LP', '13.91B', '', dict(badge='4.17%', gid='f', valcol='#FBE7B0')),
        (1839, 277, 'tx', 'TXNS 24H', '733 <span style="font-size:22px;color:#2BE07F;margin-left:10px">283</span><span style="font-size:22px;color:rgba(255,255,255,.55)"> / </span><span style="font-size:22px;color:#FF5A78">450</span>', '<span>🠕</span> 110.3%', dict(col='#4BE26A', gid='h')),
    ]
    return ''.join(tile(x, w, k, l, v, s, **o) for x, w, k, l, v, s, o in T)

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body style="width:{W}px;height:{BH + 88 + 186 + 26}px;padding:0;position:relative;background:#04070a;overflow:hidden">{banner()}{tabs()}{tiles()}</body></html>'''
open(os.path.join(H, 'mock-hdr2.html'), 'w').write(html)
print('ok')
