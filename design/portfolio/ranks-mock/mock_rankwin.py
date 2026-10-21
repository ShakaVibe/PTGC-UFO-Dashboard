import json, re, math, random
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
# ---- a realistic 1-year PTGC rank track (synthetic, shaped like real ranks: long flats, buys = jumps up, sells = drops) ----
random.seed(7)
N=365; rank=[];r=410
events=[]  # (dayIndex, 'buy'|'sell')
for i in range(N):
    if random.random()<0.025: r=max(1,int(r*random.uniform(0.6,0.9))); events.append((i,'buy'))
    elif random.random()<0.012: r=int(r*random.uniform(1.1,1.5)); events.append((i,'sell'))
    r=max(1,r+random.choice([0,0,0,0,1,-1,1,-1,2,-2]))   # drift from others' moves
    rank.append(r)
# make the ending match his screenshot-ish: #14 today
scale=14/rank[-1]
rank=[max(1,round(x*scale)) for x in rank]
today=rank[-1]; best=min(rank); bi=rank.index(best); worst=max(rank)
def chg(n): return rank[-1]-rank[-1-n] if n<N else rank[-1]-rank[0]
import datetime
d0=datetime.date(2026,10,21)-datetime.timedelta(days=N-1)
dates=[d0+datetime.timedelta(days=i) for i in range(N)]
def svg(period):
    n=min(period,N); ys=rank[-n:]; evs=[(i-(N-n),k) for i,k in events if i>=N-n]
    W,H=820,260; L,R,T,B=46,14,16,30
    lo,hi=min(ys),max(ys); pad=max(1,(hi-lo)*0.12); lo2,hi2=max(1,lo-pad),hi+pad
    X=lambda i:L+(W-L-R)*i/max(1,n-1); Y=lambda v:T+(H-T-B)*(v-lo2)/(hi2-lo2)   # smaller rank = higher = top
    pts=' '.join(f'{X(i):.1f},{Y(v):.1f}' for i,v in enumerate(ys))
    area=f'M{X(0):.1f},{H-B} L'+pts.replace(' ',' L')+f' L{X(n-1):.1f},{H-B} Z'
    # gridlines: 4 ranks
    g=''
    for k in range(5):
        v=lo2+(hi2-lo2)*k/4; y=Y(v)
        g+=f'<line x1="{L}" x2="{W-R}" y1="{y:.1f}" y2="{y:.1f}" stroke="rgba(255,255,255,.07)"/><text x="{L-6}" y="{y+4:.1f}" text-anchor="end" font-size="11" fill="rgba(255,255,255,.5)" font-family="Rajdhani" font-weight="600">#{round(v):,}</text>'
    # x labels
    xl=''
    for k in range(5):
        i=round((n-1)*k/4); dd=dates[N-n+i]
        xl+=f'<text x="{X(i):.1f}" y="{H-8}" text-anchor="middle" font-size="11" fill="rgba(255,255,255,.5)" font-family="Rajdhani" font-weight="600">{dd.strftime("%b %-d") if n<=120 else dd.strftime("%b %y")}</text>'
    ev=''
    for i,k in evs:
        c='#39E15A' if k=='buy' else '#FF4B55'; ev+=f'<circle cx="{X(i):.1f}" cy="{Y(ys[i]):.1f}" r="4" fill="{c}" stroke="#0b0d12" stroke-width="1.5"/>'
    best_i=ys.index(min(ys))
    return f'''<svg viewBox="0 0 {W} {H}" class="rc">{g}<defs><linearGradient id="ga" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#F2D35B" stop-opacity=".35"/><stop offset="1" stop-color="#F2D35B" stop-opacity="0"/></linearGradient></defs>
<path d="{area}" fill="url(#ga)"/><polyline points="{pts}" fill="none" stroke="#F2D35B" stroke-width="2.2" stroke-linejoin="round"/>{ev}
<circle cx="{X(best_i):.1f}" cy="{Y(ys[best_i]):.1f}" r="5" fill="#0b0d12" stroke="#F2D35B" stroke-width="2"/><text x="{X(best_i)+8:.1f}" y="{Y(ys[best_i])-8:.1f}" font-size="11" fill="#F6E98A" font-family="Orbitron" font-weight="900">BEST #{min(ys):,}</text>
<circle cx="{X(n-1):.1f}" cy="{Y(ys[-1]):.1f}" r="5" fill="#F2D35B"/>{xl}</svg>'''
def pills(active):
    return '<div class="pp">'+''.join(f'<button class="{"on" if p==active else ""}">{p}</button>' for p in ('LIFE','1Y','90D','30D','7D'))+'</div>'
def arrow(n):
    if n==0: return '<span class="flat">— no change</span>'
    return f'<span class="{"up" if n<0 else "dn"}">{"▲" if n<0 else "▼"} {abs(n)} place{"s" if abs(n)!=1 else ""}</span>'
# "what it takes": balances for #100 / #50 / #10 from the real file
hr=json.load(open(S+'/repo/data/holder-ranks.json'))['tokens']['PTGC']['b']
mine=hr[13]+1   # exactly #14 on today's list
def ab(n):
    for d,s in ((1e12,'T'),(1e9,'B'),(1e6,'M'),(1e3,'K')):
        if n>=d: return f'{n/d:.2f}{s}'
    return f'{n:.0f}'
need=lambda r: max(0,hr[r-1]-mine+1)
def window(period,sub):
    n=min(period,N)
    return f'''<div class="pf2-erw rkw"><div class="ehd"><img src="../../logos/ptgc/logo-512.webp" alt=""><div class="tt"><h2>PTGC HOLDER RANK</h2><div class="sub">{sub}</div></div>
  <div class="tw"><div class="tabs"><button class="on"><img src="../../logos/ptgc/logo-512.webp" alt="">PTGC</button><button><img src="../../logos/ufo/logo-512.webp" alt="">UFO</button></div></div><button class="x">×</button></div>
  <div class="hero"><div class="big"><small>TODAY</small><b>#{today:,}</b>{arrow(chg(n))}<em>vs {"the start" if period>=N else f"{n} days ago"}</em></div>
    <div class="tiles"><div class="tl"><div class="l">BEST EVER</div><div class="v">#{best:,}</div><div class="s">{dates[bi].strftime("%b %-d, %Y")}</div></div><div class="tl"><div class="l">LOWEST</div><div class="v">#{worst:,}</div><div class="s">{dates[rank.index(worst)].strftime("%b %-d, %Y")}</div></div>
    <div class="tl"><div class="l">TO PASS #{today-1}</div><div class="v">{ab(need(today-1))}</div><div class="s">PTGC more</div></div><div class="tl"><div class="l">DAYS IN TOP 100</div><div class="v">{sum(1 for x in rank if x<=100)}</div><div class="s">of {N} tracked</div></div></div></div>
  <div class="ch"><div class="chh"><span>RANK OVER TIME</span>{pills("1Y" if period==365 else "90D" if period==90 else "LIFE")}</div>{svg(period)}
    <div class="lg"><span><i style="background:#F2D35B"></i>your rank · higher is better</span><span><i style="background:#39E15A"></i>buy</span><span><i style="background:#FF4B55"></i>sell</span><span class="r">one point per day · ranks among every real holder, pools and contracts left out</span></div></div>
  <div class="wt"><div class="chh"><span>WHAT IT TAKES</span><span class="r">from today’s holder list</span></div><div class="lad">
    {"".join(f'<div class="st"><span class="rk">#{r}</span><span class="bar"><i style="width:{min(100,mine/hr[r-1]*100):.0f}%"></i></span><span class="nd">+ {ab(need(r))} PTGC</span></div>' for r in (13,10,5,1))}
  </div></div>
  <div class="ft">Ranked among every wallet holding PTGC, except liquidity pools and other contracts, the burn addresses, the token contracts and the DAO wallets · history rebuilt from the chain, one point per UTC day · today’s point is live</div>
</div>'''
CSS='''
body{margin:0;background:#04060a;color:#fff;font-family:Rajdhani;font-weight:500}
.wrap{padding:28px 40px 60px;max-width:1100px}
.opt{font-family:Orbitron;font-weight:900;font-size:13px;letter-spacing:.14em;color:#04060a;background:#F2D35B;display:inline-block;padding:5px 12px;border-radius:5px}
.note{display:block;margin:8px 0 14px;color:rgba(255,255,255,.72);font-size:16px;font-weight:600;max-width:1000px}
.sep{height:1px;background:linear-gradient(90deg,transparent,rgba(242,211,91,.5),transparent);margin:36px 0 26px}
.rkw{padding:22px 24px 18px;max-width:980px}
.rkw .ehd .tt{flex:1}
.rkw .hero{display:grid;grid-template-columns:260px 1fr;gap:18px;margin-top:18px;align-items:stretch}
.rkw .big{border-radius:14px;padding:16px 18px;border:1px solid rgba(242,211,91,.45);background:radial-gradient(300px 160px at 20% 0%,rgba(242,211,91,.18),transparent 70%),rgba(0,0,0,.4);display:flex;flex-direction:column;justify-content:center}
.rkw .big small{font:700 11px Orbitron;letter-spacing:.16em;color:rgba(255,255,255,.55)}
.rkw .big b{font:900 54px Orbitron;color:#F2D35B;line-height:1;margin:6px 0 8px;letter-spacing:.01em}
.rkw .big span{font:700 15px Rajdhani}.rkw .big .up{color:#39E15A}.rkw .big .dn{color:#FF4B55}.rkw .big .flat{color:rgba(255,255,255,.5)}
.rkw .big em{font:600 13px Rajdhani;font-style:normal;color:rgba(255,255,255,.5)}
.rkw .tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}
.rkw .tl{border-radius:12px;padding:12px 13px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.35)}
.rkw .tl .l{font:700 10.5px Orbitron;letter-spacing:.14em;color:rgba(255,255,255,.5)}
.rkw .tl .v{font:900 24px Orbitron;color:#fff;margin-top:8px;letter-spacing:.01em}
.rkw .tl .s{font:600 13px Rajdhani;color:rgba(255,255,255,.5);margin-top:4px}
.rkw .ch,.rkw .wt{margin-top:16px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:rgba(0,0,0,.3);padding:12px 14px 10px}
.rkw .chh{display:flex;align-items:center;justify-content:space-between;gap:12px;font:900 12.5px Orbitron;letter-spacing:.12em;color:#F6E98A;margin-bottom:8px}
.rkw .chh .r{font:600 12.5px Rajdhani;letter-spacing:0;color:rgba(255,255,255,.5)}
.pp{display:flex;gap:6px}.pp button{font:700 12px Rajdhani;letter-spacing:.06em;padding:4px 11px;border-radius:999px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.03);color:rgba(255,255,255,.72);cursor:pointer}
.pp button.on{border-color:#F2D35B;color:#F2D35B;background:rgba(242,211,91,.1)}
.rc{width:100%;height:auto;display:block}
.rkw .lg{display:flex;gap:16px;flex-wrap:wrap;align-items:center;margin-top:6px;font:600 12.5px Rajdhani;color:rgba(255,255,255,.6)}
.rkw .lg i{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:6px;vertical-align:-1px}.rkw .lg .r{margin-left:auto;color:rgba(255,255,255,.4)}
.lad{display:flex;flex-direction:column;gap:6px}
.lad .st{display:grid;grid-template-columns:62px 1fr 150px;align-items:center;gap:12px;font:600 13.5px Rajdhani}
.lad .rk{font:900 13px Orbitron;color:#F2D35B;text-align:right}
.lad .bar{height:7px;border-radius:4px;background:rgba(255,255,255,.08);overflow:hidden}.lad .bar i{display:block;height:100%;background:linear-gradient(90deg,#B8891A,#F2D35B)}
.lad .nd{color:rgba(255,255,255,.7)}
.rkw .ft{margin-top:12px;font:600 12.5px Rajdhani;color:rgba(255,255,255,.42)}
'''
head=open(S+'/repo/design/portfolio/mock-ranks-v3.html').read().split('<style>\nbody{')[0]
out=head+'<style>'+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">HOLDER RANK WINDOW — opens from the rank badge</h1>
<div class="note">The Earned Details frame (same width, header, token tabs, close). The curve here is a stand-in shaped like a real rank track (long flats, buys jump up, sells drop); the PTGC backfill is running and the real history replaces it. Period pills LIFE · 1Y · 90D · 30D · 7D. Higher on the chart = a better rank.</div>
<div class="opt">1Y</div><span class="note">Big rank + change over the period, four stat tiles, the chart with buy / sell dots and the best point marked, then "what it takes" to reach the next milestones.</span>'''
out+=window(365,f'Main · 0x1111…1111 · {ab(mine)} PTGC')
out+='<div class="sep"></div><div class="opt">90D</div><span class="note">Same window, 90-day period — the y-axis re-scales to the period so small moves are visible.</span>'+window(90,f'Main · 0x1111…1111 · {ab(mine)} PTGC')
out+='</div></div></body></html>'
open(S+'/repo/design/portfolio/mock-rank-window-v1.html','w').write(out); print('written',len(out))
