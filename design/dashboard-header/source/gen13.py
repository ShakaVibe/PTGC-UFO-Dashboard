#!/usr/bin/env python3
"""Dashboard header redesign — PHONE layout (390 px wide, iPhone 14/15/16), PTGC + UFO. 2026-09-29.
Same pieces as the desktop v11 (gen11) / UFO (gen12): Shaka's background band + alien head, fire-light coin, sampled golds,
solid BUY/SELL + SWITCH, dark shading behind text, KPI tiles with sparklines — rearranged for a phone:
coin + name row, price, the three stats in a row, BUY/SELL + SWITCH half-and-half (today's phone pattern), sliding tabs,
tiles two per row."""
import os, json, importlib.util, sys
H = os.path.abspath(os.path.dirname(__file__))
def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(H, name + '.py')); m = importlib.util.module_from_spec(spec)
    _a = sys.argv; sys.argv = ['x']; spec.loader.exec_module(m); sys.argv = _a; return m
g11 = load('gen11')
CSS = g11.CSS + '''
.t-gref{background:linear-gradient(180deg,#F2FFE0 0%,#D6FFA0 14%,#B8FF62 34%,#9CF53A 52%,#7EE01E 62%,#5FB814 74%,#3F8A0C 90%,#4C9A10 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.t-gprice{background:linear-gradient(180deg,#F4FFE4 0%,#E0FFB8 24%,#CBFF8C 42%,#B2F760 58%,#9BEA45 74%,#86D83A 90%,#76C634 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.t-gprice sub{-webkit-text-fill-color:#A8EE55}
.t-gref2{background:linear-gradient(180deg,#E6FFC4 0%,#C6FF80 30%,#A8F554 50%,#86D836 72%,#6CBE2A 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
'''
R = g11.R
spark, ICON = g11.spark, g11.ICON
BG, HEAD = g11.BG, g11.HEAD
PTGC, UFO = g11.PTGC, g11.UFO
W = 390
CAL = lambda c: f'<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="{c}" stroke-width="2.2"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>'
COPY = '<svg width="13" height="14" viewBox="0 0 24 26" fill="none" stroke="rgba(255,255,255,.75)" stroke-width="2.2"><rect x="5" y="5" width="14" height="18" rx="2"/><path d="M9 3h6v4H9z" fill="rgba(255,255,255,.75)"/></svg>'

def info(sz=13):
    return f'<span style="display:inline-flex;width:{sz}px;height:{sz}px;border-radius:50%;border:1.3px solid rgba(255,255,255,.8);font-size:{sz*0.62:.0f}px;align-items:center;justify-content:center;font-weight:700;color:#fff;margin-left:5px">i</span>'

def series(tok):
    cd = json.load(open(f'{R}/data/charts-data.json'))
    px = [p[1] for p in cd['tokens'][tok]['series'][-31:]]
    hh = [s[tok] for s in json.load(open(f'{R}/data/holder-history.json'))['snapshots'] if s.get(tok)][-60:]
    return dict(g11.SER, mcap=px, hold=hh)

T = {
 'PTGC': dict(name='PTGC', coin=PTGC, other=UFO, corona=f'file://{R}/logos/home/coin-corona.png', halo='255,120,20', ring='255,190,80',
              name_cls='t-ref', price_cls='t-price', stat_cls='t-ref2', accent='#E9B949', accent_rgb='232,192,68', addr='0x9453...DE93', day='1,084',
              price='$0.0<sub>4</sub>4080', chg='+10.89%', stats=[('PLS RATIO', '3.72'), ("X'S TO ATH", '32.6x'), ("X'S TO A PENNY", '245x')],
              buy_bg='linear-gradient(180deg,#F8DB7C 0%,#E7B843 50%,#C58F22 100%)', buy_ink='#241802', buy_glow='240,180,60',
              sw_rgb='124,252,0', sw_edge='157,255,58', tab='#F1C552', tabbar='linear-gradient(90deg,#F8DB7C,#E7B843)',
              tile_hot='linear-gradient(180deg,rgba(40,32,12,.9) 0%,rgba(24,20,10,.95) 45%,rgba(70,52,14,.9) 100%)',
              tile_bg='linear-gradient(180deg,rgba(18,19,14,.96) 0%,rgba(14,14,10,.97) 55%,rgba(34,28,12,.95) 100%)',
              tile_bd='rgba(190,150,70,.5)', tile_bd_hot='rgba(240,196,90,.95)', spark='#E9B949', hotval='#FBE7B0',
              tiles=[('mcap', 'MARKET CAP', '$11,730,465', '▲ 10.89%'), ('vol', 'VOLUME 24H', '$142,521', '▲ 127.2%'),
                     ('liq', 'LIQUIDITY', '$1,146,549', ''), ('ratio', 'LIQ / MCAP', '9.77%', ''),
                     ('hold', 'HOLDERS', '18,117', '↑ +2'), ('lp', 'TOKENS IN LP', '13.91B', ''),
                     ('tx', 'TXNS 24H', '733 <span style="font-size:14px;color:#2BE07F">283</span><span style="font-size:14px;color:rgba(255,255,255,.5)"> / </span><span style="font-size:14px;color:#FF5A78">450</span>', '↑ 110.3%')],
              badges={'liq': 'RH', 'lp': '4.17%'}),
 'UFO': dict(name='UFO', coin=UFO, other=PTGC, corona=f'file://{R}/logos/home/coin-corona-green.png', halo='110,255,40', ring='140,255,60',
             name_cls='t-gref', price_cls='t-gprice', stat_cls='t-gref2', accent='#9DFF3A', accent_rgb='157,255,58', addr='0x49eD...e6e6', day='82',
             price='$0.0<sub>5</sub>6326', chg='+8.07%', stats=[('PLS RATIO', '0.58'), ("X'S TO ATH", '17.9x'), ("X'S TO A PENNY", '1.6K')],
             buy_bg='linear-gradient(180deg,#C8FF78 0%,#8EEB2A 50%,#5DB512 100%)', buy_ink='#0E2402', buy_glow='124,252,0',
             sw_rgb='232,192,68', sw_edge='240,200,90', tab='#9DFF3A', tabbar='linear-gradient(90deg,#C8FF78,#7CFC00)',
             tile_hot='linear-gradient(180deg,rgba(20,36,10,.9) 0%,rgba(12,22,8,.95) 45%,rgba(36,70,12,.9) 100%)',
             tile_bg='linear-gradient(180deg,rgba(14,19,14,.96) 0%,rgba(10,14,10,.97) 55%,rgba(18,34,12,.95) 100%)',
             tile_bd='rgba(110,190,60,.5)', tile_bd_hot='rgba(160,255,70,.95)', spark='#8EEB2A', hotval='#E4FFC4',
             tiles=[('mcap', 'MARKET CAP', '$5,725,507', '▲ 8.07%'), ('vol', 'VOLUME 24H', '$63,213', '▲ 349.8%'),
                    ('liq', 'LIQUIDITY', '$1,394,635', ''), ('ratio', 'LIQ / MCAP', '24.36%', ''),
                    ('hold', 'HOLDERS', '5,311', '<span style="color:#FF5A78">↓ -2</span>'), ('lp', 'TOKENS IN LP', '105.96B', ''),
                    ('tx', 'TXNS 24H', '304 <span style="font-size:14px;color:#2BE07F">130</span><span style="font-size:14px;color:rgba(255,255,255,.5)"> / </span><span style="font-size:14px;color:#FF5A78">174</span>', '↑ 366.2%')],
             badges={'liq': 'RH', 'lp': '10.60%'}),
}

def ab(x, y, inner, extra=''):
    return f'<div style="position:absolute;left:{x}px;top:{y}px;{extra}">{inner}</div>'

def banner(t):
    BH = 452
    # art: the band scaled so its height fills the banner, slid so the gold→green middle sits behind the text;
    # the alien head on the right behind the name row, darkened so the text wins
    art = f'''<img src="{BG}" style="position:absolute;left:-560px;top:-10px;width:{round(2168*470/350)}px;height:470px">
<img src="{HEAD}" style="position:absolute;left:196px;top:-24px;width:250px;height:222px;-webkit-mask-image:linear-gradient(180deg,#000 0%,#000 60%,transparent 92%),linear-gradient(90deg,transparent 0%,#000 30%);-webkit-mask-composite:source-in;filter:brightness(.62) contrast(1.1) drop-shadow(6px 0 10px rgba(90,255,90,.3))">
<div style="position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.25) 0%,rgba(0,0,0,.35) 30%,rgba(0,0,0,.62) 48%,rgba(0,0,0,.66) 78%,rgba(0,0,0,.5) 100%)"></div>
<div style="position:absolute;left:-40px;top:40px;width:330px;height:170px;background:radial-gradient(closest-side,rgba(0,0,0,.55),rgba(0,0,0,0))"></div>'''
    coin = f'''<div style="position:absolute;left:22px;top:52px;width:96px;height:96px">
<div style="position:absolute;inset:-34px;border-radius:50%;background:radial-gradient(circle, rgba({t['halo']},.22) 45%, rgba({t['halo']},.05) 60%, rgba(0,0,0,0) 72%)"></div>
<img src="{t['corona']}" style="position:absolute;left:-80px;top:-80px;width:256px;height:256px;mix-blend-mode:screen">
<img src="{t['coin']}" style="position:relative;width:96px;height:96px;border-radius:50%;box-shadow:0 0 6px 1px rgba({t['ring']},.55)"></div>'''
    name = ab(134, 56, f'<div class="orb {t["name_cls"]}" style="font-size:40px;font-weight:900;line-height:1;letter-spacing:.02em;filter:drop-shadow(0 2px 2px rgba(0,0,0,.9))">{t["name"]}</div>') + \
        ab(136, 104, f'<div class="tn" style="display:flex;align-items:center;gap:8px;font-size:14px;font-weight:500;color:rgba(255,255,255,.82);text-shadow:0 1px 3px #000">{t["addr"]} {COPY}</div>') + \
        ab(136, 126, f'<div style="display:flex;align-items:center;gap:7px;height:26px;padding:0 13px 0 10px;border-radius:99px;border:1.3px solid rgba({t["accent_rgb"]},.85);background:rgba(8,8,4,.6)">{CAL(t["accent"])}<span style="font-size:11px;font-weight:700;letter-spacing:.14em;color:rgba(255,255,255,.85)">DAY</span><span class="orb {t["stat_cls"]}" style="font-size:13px;font-weight:700">{t["day"]}</span></div>')
    tri = '<svg width="18" height="16" viewBox="0 0 30 26"><defs><linearGradient id="ua" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#6BF7A8"/><stop offset="1" stop-color="#00C865"/></linearGradient></defs><path d="M15 1 L29 25 L1 25 Z" fill="url(#ua)"/></svg>'
    price = ab(0, 176, f'''<div style="width:{W}px;text-align:center"><div class="{t["price_cls"]} tn" style="font-size:44px;font-weight:700;line-height:1;filter:drop-shadow(0 2px 3px rgba(0,0,0,1)) drop-shadow(0 0 12px rgba(0,0,0,.9))">{t["price"]}</div>
<div class="tn" style="margin-top:9px;display:flex;align-items:center;justify-content:center;gap:9px;font-size:24px;font-weight:700;color:#12E28A;line-height:1;text-shadow:0 1px 4px #000">{tri}{t["chg"]} <span style="font-size:14px;font-weight:500;color:rgba(255,255,255,.65);margin-left:4px">24h</span></div></div>''')
    cells = ''
    for i, (lab, val) in enumerate(t['stats']):
        cells += f'''<div style="flex:1;text-align:center;{'border-left:1px solid rgba(235,235,235,.35);' if i else ''}"><div style="display:flex;justify-content:center;align-items:center;font-size:10.5px;font-weight:600;letter-spacing:.1em;color:#fff;white-space:nowrap;text-shadow:0 1px 3px #000">{lab}{info()}</div>
<div class="{t["stat_cls"]} tn" style="margin-top:6px;font-size:27px;font-weight:700;line-height:1;filter:drop-shadow(0 2px 3px rgba(0,0,0,1))">{val}</div></div>'''
    stats = ab(14, 282, f'<div style="width:{W-28}px;display:flex;padding:12px 0;border-radius:14px;background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.08)">{cells}</div>')
    buy = f'''<div style="position:relative;flex:1;height:58px;border-radius:12px;display:flex;align-items:center;justify-content:center;gap:12px;overflow:hidden;background:{t["buy_bg"]};box-shadow:inset 0 1px 0 rgba(255,255,255,.6), 0 0 18px rgba({t["buy_glow"]},.5)">
<div style="position:absolute;inset:0;background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,.18) 47%,rgba(255,255,255,.28) 50%,rgba(255,255,255,.18) 53%,transparent 60%)"></div>
<img src="{t["coin"]}" style="position:relative;width:38px;height:38px;border-radius:50%;box-shadow:0 0 0 1.5px rgba(0,0,0,.4)">
<div class="orb" style="position:relative;display:flex;flex-direction:column;align-items:center;color:{t["buy_ink"]};font-weight:900;font-size:14px;letter-spacing:.2em;line-height:1"><span>BUY</span><span style="width:64px;height:1.2px;background:rgba(0,0,0,.4);margin:5px 0"></span><span>SELL</span></div></div>'''
    sw = f'''<div style="flex:1;height:58px;border-radius:12px;display:flex;align-items:center;justify-content:center;gap:12px;box-sizing:border-box;background:linear-gradient(135deg, rgba({t["sw_rgb"]},.22), rgba({t["sw_rgb"]},.06)), #080906;border:1.3px solid rgba({t["sw_edge"]},.78);box-shadow:0 0 16px -4px rgba({t["sw_rgb"]},.6)">
<img src="{t["other"]}" style="width:36px;height:36px;border-radius:50%;box-shadow:0 0 10px rgba({t["sw_rgb"]},.6)">
<span class="orb" style="font-size:14px;font-weight:700;letter-spacing:.2em;color:#fff">SWITCH</span></div>'''
    btns = ab(14, 372, f'<div style="width:{W-28}px;display:flex;gap:10px">{buy}{sw}</div>')
    back = ab(14, 12, '<div style="font-size:22px;color:rgba(255,255,255,.65)">←</div>')
    return f'<div style="position:relative;width:{W}px;height:{BH}px;overflow:hidden;background:#050504">{art}{back}{coin}{name}{price}{stats}{btns}</div>'

def tabs(t):
    items = ['Dashboard', 'KPI Report', 'Socials', 'Calculators', 'Charts']
    out = ''; x = 16
    for i, n in enumerate(items):
        on = i == 0
        out += ab(x, 14, f'<div style="font-size:15px;font-weight:{700 if on else 500};color:{t["tab"] if on else "rgba(255,255,255,.88)"};white-space:nowrap">{n}</div>')
        if on: out += f'<div style="position:absolute;left:{x-2}px;top:41px;width:82px;height:3px;border-radius:2px;background:{t["tabbar"]}"></div>'
        x += len(n) * 8.6 + 26
    out += f'<div style="position:absolute;right:0;top:0;bottom:0;width:48px;background:linear-gradient(90deg,rgba(5,13,14,0),#050d0e 70%)"></div>'
    out += ab(W - 22, 12, '<div style="font-size:18px;color:rgba(255,255,255,.55)">›</div>')
    return f'<div style="position:relative;width:{W}px;height:46px;overflow:hidden;background:#050d0e;border-top:1px solid rgba({t["accent_rgb"]},.25);border-bottom:1px solid rgba(255,255,255,.07)">{out}</div>'

def tiles(t):
    SER = series(t['name'])
    out = ''
    for i, (key, label, val, sub) in enumerate(t['tiles']):
        hot = i == 0; full = key == 'tx'
        badge = t['badges'].get(key, '')
        if key == 'hold': badge = info(14)
        col = '#4BE26A' if key == 'tx' else ('#C9DC4A' if key == 'ratio' else t['spark'])
        out += f'''<div style="position:relative;{'grid-column:1 / -1;' if full else ''}height:128px;border-radius:12px;background:{t["tile_hot"] if hot else t["tile_bg"]};border:1.3px solid {t["tile_bd_hot"] if hot else t["tile_bd"]};{'box-shadow:0 0 16px -4px rgba(' + t["accent_rgb"] + ',.55);' if hot else ''}overflow:hidden">
<div style="position:absolute;left:12px;top:11px;display:flex;align-items:center;gap:8px;white-space:nowrap;font-size:12px;font-weight:600;letter-spacing:.03em;color:rgba(255,255,255,.88)"><svg width="18" height="18" viewBox="0 0 24 24" style="color:{t["accent"]}">{ICON[key]}</svg>{label}</div>
<div style="position:absolute;right:10px;top:11px;font-size:11px;font-weight:700;color:{t["accent"]}">{badge}</div>
<div class="tn" style="position:absolute;left:13px;top:38px;font-size:23px;font-weight:700;color:{t["hotval"] if hot else "#fff"};line-height:1;white-space:nowrap">{val}</div>
<div class="tn" style="position:absolute;left:13px;top:64px;font-size:14px;font-weight:700;color:#2BE07F;white-space:nowrap">{sub}</div>
<div style="position:absolute;left:10px;right:10px;bottom:8px">{spark(SER[key], 160, 30, col, t["name"] + key)}</div></div>'''
    return f'<div style="width:{W}px;box-sizing:border-box;padding:14px;display:grid;grid-template-columns:1fr 1fr;gap:10px">{out}</div>'

def status_bar():
    return f'<div style="height:44px;display:flex;align-items:center;justify-content:space-between;padding:0 26px 0 30px;background:#050504;color:#fff;font-size:15px;font-weight:700"><span>9:41</span><span style="font-size:13px;letter-spacing:.1em">●●● ▮</span></div>'

for tok in ('PTGC', 'UFO'):
    t = T[tok]
    html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body style="width:{W}px;padding:0;background:#04070a">{status_bar()}{banner(t)}{tabs(t)}{tiles(t)}</body></html>'''
    open(os.path.join(H, f'mock-phone-{tok.lower()}.html'), 'w').write(html)
print('ok')
