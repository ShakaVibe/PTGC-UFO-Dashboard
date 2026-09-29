#!/usr/bin/env python3
"""PTGC dashboard header — Shaka's reference mock-up rebuilt on our pieces (2026-09-29).
No global top nav / search line (Shaka: drop it). Hero banner on the home page's cosmic art, our BUY/SELL + SWITCH,
tab row, KPI tiles with 30-day sparklines. Live numbers read off ptgc-ufo.com at ~15:40 UTC."""
import os, json, importlib.util, sys
H = os.path.abspath(os.path.dirname(__file__))
spec = importlib.util.spec_from_file_location('g2', os.path.join(H, 'gen2.py')); g2 = importlib.util.module_from_spec(spec)
_a = sys.argv; sys.argv = ['x']; spec.loader.exec_module(g2); sys.argv = _a
CSS = g2.CSS + """
.t-gold2{background:linear-gradient(180deg,#FFF6C8 0%,#F7E08A 22%,#E8C044 48%,#C9971F 72%,#8a6414 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
sub{font-size:.6em;vertical-align:-.2em;margin:0 .04em}
"""
R = '/home/claude/ptgc'
BNR = f'file://{R}/logos/combined/TheGraysXBnr.png'
COSMIC, GROUND = f'file://{R}/logos/home/cosmic-bg.jpg', f'file://{R}/logos/home/cosmic-ground.jpg'
PTGC, UFO = f'file://{R}/06_PTGC_V1_transparent_bg.png', f'file://{R}/07_Ufo_transparent.png'
UP = '#22E07A'

# --- 30-day series for the sparklines -------------------------------------------------------------
cd = json.load(open(f'{R}/data/charts-data.json'))
px = [p[1] for p in cd['tokens']['PTGC']['series'][-31:]]
hh = [s['PTGC'] for s in json.load(open(f'{R}/data/holder-history.json'))['snapshots'] if s.get('PTGC')][-60:]
import math, random
random.seed(7)
def wobble(base, amp):   # illustrative only — see the caption
    return [b * (1 + amp * (random.random() - .5)) for b in base]
SER = {
    'mcap': px,
    'vol': wobble([abs(px[i] - px[i-1]) + px[i] * .02 for i in range(1, len(px))], .6),
    'liq': wobble(px, .15),
    'ratio': wobble([1 / p for p in px], .1),
    'hold': hh,
    'lp': wobble(px[::-1], .08)[::-1],
    'tx': wobble([abs(px[i] - px[i-1]) + px[i] * .03 for i in range(1, len(px))], .8),
}

def spark(vals, w, h, col, gid):
    lo, hi = min(vals), max(vals); rng = (hi - lo) or 1
    pts = [(i * w / (len(vals) - 1), h - 4 - (v - lo) / rng * (h - 10)) for i, v in enumerate(vals)]
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
    area = d + f' L{w},{h} L0,{h} Z'
    return f'''<svg width="100%" height="{h}" viewBox="0 0 {w} {h}" preserveAspectRatio="none" style="display:block;overflow:visible">
<defs><linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{col}" stop-opacity=".35"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient></defs>
<path d="{area}" fill="url(#{gid})"/><path d="{d}" fill="none" stroke="{col}" stroke-width="2" stroke-linejoin="round" style="filter:drop-shadow(0 0 4px {col})"/></svg>'''

INFO = '<span style="display:inline-flex;width:15px;height:15px;border-radius:50%;border:1.5px solid currentColor;font-size:10px;align-items:center;justify-content:center;font-weight:700;opacity:.8;margin-left:7px">i</span>'

def stat(label, val):
    return f'''<div style="padding:0 20px"><div style="display:flex;align-items:center;white-space:nowrap;text-shadow:0 1px 4px #000;font-size:15px;font-weight:600;letter-spacing:.14em;color:rgba(255,255,255,.9)">{label}{INFO}</div>
<div class="t-gold2 tn" style="margin-top:8px;font-size:42px;font-weight:700;line-height:1;filter:drop-shadow(0 2px 6px rgba(0,0,0,.95))">{val}</div></div>'''

def vrule():
    return '<div style="width:1px;align-self:stretch;margin:18px 0;background:rgba(255,255,255,.28)"></div>'

def banner():
    buy = f'''<div style="display:flex;align-items:center;gap:14px;padding:10px 26px 10px 12px;border-radius:16px;background:linear-gradient(180deg,#F6DB7A 0%,#E2B53C 55%,#B8861C 100%);box-shadow:inset 0 1px 0 rgba(255,255,255,.6), 0 0 26px rgba(232,192,68,.55), 0 10px 24px -8px rgba(0,0,0,.8)">
<img src="{PTGC}" style="width:50px;height:50px;border-radius:50%;box-shadow:0 0 0 2px rgba(0,0,0,.35)">
<div class="orb" style="display:flex;flex-direction:column;align-items:center;color:#241802;font-weight:900;font-size:18px;letter-spacing:.2em;line-height:1"><span>BUY</span><span style="width:74px;height:1.5px;background:rgba(36,24,2,.45);margin:7px 0"></span><span>SELL</span></div></div>'''
    sw = f'''<div style="display:flex;align-items:center;gap:12px;padding:10px 22px 10px 12px;border-radius:16px;background:rgba(6,10,6,.72);border:1.5px solid rgba(157,255,58,.55);box-shadow:0 0 22px -6px rgba(124,252,0,.6), inset 0 1px 0 rgba(255,255,255,.08);backdrop-filter:blur(4px)">
<img src="{UFO}" style="width:44px;height:44px;border-radius:50%;box-shadow:0 0 12px rgba(124,252,0,.6)">
<span class="orb" style="font-size:15px;font-weight:700;letter-spacing:.22em;color:#fff">SWITCH</span></div>'''
    return f'''<div style="position:relative;height:258px;overflow:hidden;background:#070604">
<img src="{BNR}" style="position:absolute;left:500px;top:-26px;width:1180px">
<img src="{BNR}" style="position:absolute;left:-680px;top:-26px;width:1180px;transform:scaleX(-1);-webkit-mask-image:linear-gradient(270deg,transparent 0%,transparent 62%,#000 74%)">
<div style="position:absolute;left:760px;top:40px;width:520px;height:170px;background:radial-gradient(closest-side,rgba(0,0,0,.55),rgba(0,0,0,0))"></div>
<div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(6,5,3,.45) 0%,rgba(6,5,3,.3) 22%,rgba(6,5,3,.5) 42%,rgba(6,5,3,.35) 60%,rgba(6,5,3,.05) 74%,rgba(6,5,3,.15) 100%)"></div>
<div style="position:absolute;left:0;right:0;bottom:0;height:26px;background:linear-gradient(180deg,rgba(0,0,0,0),rgba(5,5,4,.8))"></div>
<div style="position:absolute;left:22px;top:18px;font-size:26px;color:rgba(255,255,255,.6)">←</div>
<div style="position:absolute;left:0;right:0;top:0;bottom:0;max-width:1440px;margin:0 auto;padding:0 34px 0 44px;display:flex;align-items:center">
  <div style="position:relative;width:140px;height:140px;flex-shrink:0">
    <div style="position:absolute;inset:-30px;border-radius:50%;background:radial-gradient(circle, rgba(255,210,90,.75) 0%, rgba(255,170,40,.35) 50%, rgba(255,150,30,.12) 62%, rgba(0,0,0,0) 72%)"></div>
    <img src="{PTGC}" style="position:relative;width:140px;height:140px;border-radius:50%;box-shadow:0 0 0 3px rgba(250,230,160,.9), 0 0 0 7px rgba(232,192,68,.25), 0 0 46px rgba(255,190,60,.8)">
  </div>
  <div style="margin-left:24px">
    <div class="orb t-gold2" style="font-size:64px;font-weight:900;line-height:.95;letter-spacing:.02em;filter:drop-shadow(0 3px 8px rgba(0,0,0,.7))">PTGC</div>
    <div class="tn" style="margin-top:12px;display:flex;align-items:center;gap:10px;font-size:19px;font-weight:600;color:rgba(255,255,255,.72);letter-spacing:.06em">0x9453...DE93 <span style="font-size:15px;opacity:.8">📋</span></div>
    <div style="margin-top:12px;display:inline-flex;align-items:center;gap:12px;padding:7px 26px 7px 16px;border-radius:99px;border:1.5px solid rgba(232,192,68,.75);background:rgba(20,14,2,.6);box-shadow:0 0 16px -4px rgba(232,192,68,.6)">
      <span style="font-size:15px;opacity:.8">📅</span><span style="font-size:15px;font-weight:700;letter-spacing:.2em;color:rgba(255,255,255,.75)">DAY</span><span class="orb t-gold2" style="font-size:20px;font-weight:700">1,084</span></div>
  </div>
  {vrule().replace('margin:18px 0','margin:60px 0 60px 30px')}
  <div style="padding:0 26px;text-align:center">
    <div class="t-gold2 tn" style="font-size:60px;font-weight:700;line-height:1;letter-spacing:.01em;filter:drop-shadow(0 3px 8px rgba(0,0,0,.7))">$0.0<sub>4</sub>4080</div>
    <div class="tn" style="margin-top:6px;font-size:30px;font-weight:700;color:{UP};text-shadow:0 1px 4px rgba(0,0,0,.8)"><span style="font-size:1.05em">▲</span> +10.89%</div>
    <div style="margin-top:0;font-size:17px;font-weight:500;color:rgba(255,255,255,.78)">24h change</div>
  </div>
  {vrule().replace('margin:18px 0','margin:60px 0')}
  {stat('PLS RATIO','3.72')}{vrule().replace('margin:18px 0','margin:96px 0 70px')}{stat("X'S TO ATH",'32.6x')}{vrule().replace('margin:18px 0','margin:96px 0 70px')}{stat("X'S TO A PENNY",'245x')}
  <div style="margin-left:auto;padding-left:18px;display:flex;flex-direction:column;gap:12px;align-items:stretch">{buy}{sw}</div>
</div></div>'''

def tabs():
    items = ['Dashboard', 'KPI Report', 'Socials', 'Calculators', 'Charts', 'Live Feed', 'Portfolio', 'Affiliates']
    out = ''
    for i, t in enumerate(items):
        on = i == 0
        chip = '<span style="margin-left:9px;font-size:12px;font-weight:800;letter-spacing:.08em;color:#241802;background:linear-gradient(180deg,#F6DB7A,#D9A92E);padding:3px 10px 2px;border-radius:99px">NEW</span>' if t == 'Live Feed' else ''
        out += f'''<div style="position:relative;display:flex;align-items:center;padding:15px 0;font-size:18px;font-weight:{700 if on else 600};color:{'#F2CC5A' if on else 'rgba(255,255,255,.85)'}">{t}{chip}{'<div style="position:absolute;left:0;right:0;bottom:0;height:3px;border-radius:3px;background:linear-gradient(90deg,#F6DB7A,#E8C044);box-shadow:0 0 10px rgba(232,192,68,.8)"></div>' if on else ''}</div>'''
    return f'''<div style="background:linear-gradient(180deg,#0b0a07,#070605);border-top:1px solid rgba(232,192,68,.18);border-bottom:1px solid rgba(255,255,255,.08)"><div style="max-width:1440px;margin:0 auto;padding:0 34px 0 44px;display:flex;align-items:center;gap:40px">{out}
<div style="margin-left:auto;display:flex;align-items:center;gap:12px;font-size:15px;color:rgba(255,255,255,.6)"><span style="width:8px;height:8px;border-radius:50%;background:{UP};box-shadow:0 0 8px {UP}"></span>Updated just now <span style="font-size:18px;opacity:.8">↻</span></div></div></div>'''

ICON = {  # gold line icons like the reference (no emoji)
 'mcap':'<path d="M3 17h3v-5H3zM9 17h3V8H9zM15 17h3V4h-3z" fill="currentColor"/>',
 'vol':'<path d="M4 18h3v-7H4zM10.5 18h3V6h-3zM17 18h3v-9h-3z" fill="currentColor"/>',
 'liq':'<path d="M12 3c3 4 6 7.5 6 11a6 6 0 0 1-12 0c0-3.5 3-7 6-11z" fill="currentColor"/>',
 'ratio':'<path d="M11 3a9 9 0 1 0 9 9h-9z" fill="currentColor"/><path d="M13 1v9h9a9 9 0 0 0-9-9z" fill="currentColor" opacity=".7"/>',
 'hold':'<circle cx="8" cy="8" r="3.2" fill="currentColor"/><circle cx="16.5" cy="8.5" r="2.7" fill="currentColor"/><path d="M2 19c0-3.5 2.7-6 6-6s6 2.5 6 6zM13.5 19c.2-2.6-.6-4.4-1.8-5.6 3.8-1.2 8.3.6 8.3 5.6z" fill="currentColor"/>',
 'lp':'<ellipse cx="12" cy="6" rx="7" ry="3" fill="currentColor"/><path d="M5 9c0 1.7 3.1 3 7 3s7-1.3 7-3v3c0 1.7-3.1 3-7 3s-7-1.3-7-3zM5 15c0 1.7 3.1 3 7 3s7-1.3 7-3v3c0 1.7-3.1 3-7 3s-7-1.3-7-3z" fill="currentColor"/>',
 'tx':'<path d="M4 8h13l-3-3M20 16H7l3 3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>',
}
def tile(key, label, val, sub, hot=False, badge='', col='#E8C044', gid='g'):
    bg = 'linear-gradient(180deg,rgba(110,82,22,.62) 0%,rgba(46,34,10,.85) 60%,rgba(26,20,8,.92) 100%)' if hot else 'linear-gradient(180deg,rgba(58,46,20,.55) 0%,rgba(22,18,10,.9) 55%,rgba(14,12,8,.95) 100%)'
    bd = 'rgba(245,205,95,.9)' if hot else 'rgba(232,192,68,.42)'
    return f'''<div style="position:relative;flex:1;min-width:0;border-radius:14px;padding:14px 16px 10px;background:{bg};border:1.5px solid {bd};box-shadow:inset 0 1px 0 rgba(255,235,170,.14){', 0 0 24px -6px rgba(232,192,68,.75)' if hot else ''};overflow:hidden">
<div style="display:flex;align-items:center;gap:9px;white-space:nowrap;font-size:15px;font-weight:600;letter-spacing:.04em;color:rgba(255,255,255,.9)"><svg width="20" height="20" viewBox="0 0 24 24" style="color:#E8B83A;flex-shrink:0">{ICON[key]}</svg>{label}<span style="margin-left:auto;font-size:12px;font-weight:700;color:#E8C044">{badge}</span></div>
<div class="tn" style="margin-top:8px;font-size:31px;font-weight:700;color:#fff;line-height:1">{val}</div>
<div class="tn" style="margin-top:5px;font-size:17px;font-weight:700;color:{UP};height:20px">{sub}</div>
<div style="margin-top:4px">{spark(SER[key], 160, 34, col, gid)}</div></div>'''

def kpis():
    t = [
        tile('mcap', 'MARKET CAP', '$11,730,465', '▲ 10.89%', hot=True, gid='a'),
        tile('vol', 'VOLUME 24H', '$142,521', '▲ 127.2% <span style="color:rgba(255,255,255,.6);font-weight:600">vs 7d avg</span>', gid='b'),
        tile('liq', 'LIQUIDITY', '$1,146,549', '', badge='RH', gid='c'),
        tile('ratio', 'LIQ / MCAP', '9.77%', '', col='#C8E04A', gid='d'),
        tile('hold', 'HOLDERS', '18,117', '↑ +2', badge=INFO.replace('margin-left:7px', 'margin-left:0'), gid='e'),
        tile('lp', 'TOKENS IN LP', '13.91B', '', badge='4.17%', gid='f'),
        tile('tx', 'TXNS 24H', '733 <span style="font-size:18px;color:#22E07A">283</span><span style="font-size:18px;color:rgba(255,255,255,.5)"> / </span><span style="font-size:18px;color:#FF4D6A">450</span>', '↑ 110.3%', col='#5CE65C', gid='h'),
    ]
    return f'<div style="max-width:1440px;margin:0 auto;padding:18px 34px 26px 44px;display:flex;gap:12px">{"".join(t)}</div>'

html = f'''<!doctype html><html><head><meta charset="utf-8"><style>{CSS}</style></head>
<body style="width:1440px;padding:0;background:#050504">{banner()}{tabs()}{kpis()}</body></html>'''
open(os.path.join(H, 'mock-hdr.html'), 'w').write(html)
print('ok')
