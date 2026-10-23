#!/usr/bin/env python3
"""Home token cards → the Atlantis look (Shaka, 2026-10-23: "I want to make the two boxes on the landing page look a lot better" —
his mockup + two background artworks; then "can you darken the backgrounds more"; then "make it live").
Idempotent, from the repo root:   python3 tools/home-cards-atlantis.py   (a second run prints "0 edit(s)")

Art: logos/home/hc-art-ptgc.webp (gold ruins) and logos/home/hc-art-ufo.webp (green ruins + saucer), 1200 wide, from the two PNGs he
sent. The art sits INSIDE the card frame (.hc-art, clipped by the card's overflow:hidden) under a navy veil (.hc-veil) that is
darkest behind the logo / name / price. Layout per his mockup: "NATIVE TOKEN" under the name, price + 24h chip on one row, contract
+ DAY on one row, icon stat tiles, the 24H chart in its own panel with a price axis, 15-minute volume bars and an end dot, and a dark
glass ENTER DASHBOARD button. No number, source or formula changes: the chart's volume is column 5 of the same GeckoTerminal
candles the card already fetched (the price line is unchanged); the axis labels are the same fmtPrice format the card prints.
"""
import sys
n = 0
IX = 'index.html'

def edit(path, old, new, count=1, done=None):
    global n
    s = open(path, encoding='utf-8').read()
    if new and new in s: return
    if done and done in s: return
    if not new and old not in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

def lines_range(path, first, last, new, done):
    """Replace the run of lines from the one starting with `first` to the one starting with `last` (inclusive)."""
    global n
    s = open(path, encoding='utf-8').read()
    if done in s: return
    L = s.split('\n')
    i = [k for k, l in enumerate(L) if l.startswith(first)]
    assert len(i) == 1, f'{first[:60]!r} x{len(i)}'
    j = [k for k, l in enumerate(L) if l.startswith(last) and k >= i[0]]
    assert j, f'{last[:60]!r} not found after {first[:40]!r}'
    L[i[0]:j[0] + 1] = new.split('\n')
    open(path, 'w', encoding='utf-8').write('\n'.join(L)); n += 1

# ------------------------------------------------------------------ CSS
CARD_CSS = r"""    /* 2026-10-23 (Shaka's mockup): the Atlantis cards — art inside the frame (.hc-art), a navy veil darkest behind the logo / name /
       price (.hc-veil; "darken the backgrounds more"), a glowing token-colour edge, glass panels over the art. */
    .hc-card{position:relative;isolation:isolate;overflow:hidden;display:flex;flex-direction:column;gap:14px;padding:16px;border:1.5px solid var(--hc-c);border-radius:18px;cursor:pointer;background:#04060b;
      box-shadow:0 0 0 1px rgba(0,0,0,.55),0 0 22px var(--hc-glow),inset 0 0 0 1px var(--hc-rim),inset 0 0 26px var(--hc-glow2);transition:transform .25s ease,box-shadow .25s ease}
    .hc-card:hover{transform:translateY(-3px);box-shadow:0 0 0 1px rgba(0,0,0,.55),0 0 40px var(--hc-glow),inset 0 0 0 1px var(--hc-rim),inset 0 0 34px var(--hc-glow2)}
    .hc-card.hc-masked{opacity:.6}
    @media(min-width:1024px){.hc-card{padding:clamp(18px,1.9vw,30px) clamp(18px,1.9vw,30px) clamp(18px,1.7vw,26px);gap:clamp(14px,1.25vw,20px)}}
    .hc-art{position:absolute;inset:0;z-index:-2;pointer-events:none;background:var(--hc-art) center 30%/cover no-repeat;filter:saturate(.9);transition:transform 6s ease}
    .hc-card:hover .hc-art{transform:scale(1.03)}
    .hc-veil{position:absolute;inset:0;z-index:-1;pointer-events:none;background:radial-gradient(ellipse 62% 40% at 30% 22%,rgba(2,4,8,.78) 0%,rgba(2,4,8,.45) 55%,transparent 80%),
      linear-gradient(180deg,rgba(2,4,8,.42) 0%,rgba(2,4,8,.52) 32%,rgba(2,4,8,.70) 52%,rgba(2,4,8,.68) 78%,rgba(2,4,8,.50) 100%)}
    .hc-gold{--hc-c:#F2C230;--hc-t:#F5C84A;--hc-rim:rgba(255,226,120,.35);--hc-glow:rgba(242,194,48,.55);--hc-glow2:rgba(242,194,48,.22);--hc-bg1:#241C05;--hc-line:#FFD23F;--hc-panel:rgba(242,194,48,.38);--hc-art:url(logos/home/hc-art-ptgc.webp)}
    .hc-green{--hc-c:#5CF03A;--hc-t:#6CF04A;--hc-rim:rgba(160,255,130,.32);--hc-glow:rgba(92,240,58,.55);--hc-glow2:rgba(92,240,58,.2);--hc-bg1:#0A2207;--hc-line:#6CFF3E;--hc-panel:rgba(92,240,58,.36);--hc-art:url(logos/home/hc-art-ufo.webp)}
    .hc-skel{--hc-glow:rgba(0,0,0,0);--hc-glow2:rgba(0,0,0,0);--hc-rim:rgba(255,255,255,.05);--hc-panel:rgba(255,255,255,.1);cursor:default}
    .hc-skel.hc-gold{--hc-c:rgba(242,194,48,.35)}.hc-skel.hc-green{--hc-c:rgba(92,240,58,.35)}
    .hc-skel:hover{transform:none}.hc-skel:hover .hc-art{transform:none}
    .hc-top{display:flex;align-items:center;gap:14px}
    @media(min-width:1024px){.hc-top{gap:clamp(16px,1.7vw,28px)}}
    .hc-logo{width:84px;height:84px;flex-shrink:0;object-fit:contain;border-radius:50%;filter:drop-shadow(0 0 14px var(--hc-glow)) drop-shadow(0 0 3px var(--hc-glow))}
    @media(min-width:640px){.hc-logo{width:104px;height:104px}}
    @media(min-width:1024px){.hc-logo{width:clamp(104px,10vw,150px);height:clamp(104px,10vw,150px)}}
    .hc-info{display:flex;flex-direction:column;min-width:0}
    .hc-name{padding-right:110px;font-family:'Orbitron',monospace;font-weight:900;font-size:2rem;line-height:.95;letter-spacing:.02em;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;filter:drop-shadow(0 2px 6px rgba(0,0,0,.8))}
    .hc-gold .hc-name{background-image:linear-gradient(180deg,#FFF0A8 0%,#F7CC45 45%,#D9980F 100%)}
    .hc-green .hc-name{background-image:linear-gradient(180deg,#D2FFAE 0%,#73F24C 45%,#2FB914 100%)}
    @media(min-width:1024px){.hc-name{font-size:clamp(2.2rem,3.3vw,3.4rem)}}
    .hc-sub{margin-top:6px;font-weight:600;font-size:.68rem;letter-spacing:.42em;color:#D5D9E0;white-space:nowrap}
    @media(min-width:1024px){.hc-sub{font-size:clamp(.7rem,.82vw,.9rem);margin-top:8px}}
    .hc-pricerow{display:flex;align-items:center;flex-wrap:wrap;gap:6px 12px;margin-top:8px}
    @media(min-width:1024px){.hc-pricerow{margin-top:clamp(8px,1vw,14px);gap:6px 16px}}
    .hc-price{font-weight:700;font-size:1.9rem;line-height:1;font-variant-numeric:tabular-nums;color:#fff;text-shadow:0 2px 10px rgba(0,0,0,.85)}
    @media(min-width:1024px){.hc-price{font-size:clamp(2rem,3.1vw,3.2rem)}}
    .hc-chip{display:inline-flex;align-items:center;gap:4px;font-weight:700;font-size:1rem;line-height:1;padding:6px 9px;border-radius:6px;border:1.5px solid;white-space:nowrap}
    @media(min-width:1024px){.hc-chip{font-size:clamp(1rem,1.45vw,1.45rem);padding:6px 12px}}
    .hc-up{color:#4BF07F;background:rgba(10,70,30,.75);border-color:rgba(75,240,127,.55);box-shadow:0 0 12px rgba(75,240,127,.18)}
    .hc-down{color:#FF5D5D;background:rgba(95,10,14,.78);border-color:rgba(255,93,93,.55);box-shadow:0 0 12px rgba(255,93,93,.18)}
    .hc-flat{color:rgba(255,255,255,.55);background:rgba(255,255,255,.06);border-color:rgba(255,255,255,.15)}
    .hc-meta{display:flex;align-items:center;flex-wrap:wrap;gap:2px 8px;margin-top:8px;font-weight:600;font-size:.9rem;letter-spacing:.03em;color:#E2E4EA}
    @media(min-width:1024px){.hc-meta{font-size:clamp(.92rem,1.15vw,1.15rem);margin-top:clamp(8px,.9vw,12px)}}
    .hc-copy{width:28px;height:28px;display:inline-flex;align-items:center;justify-content:center;border:0;background:transparent;color:#C9CDD6;border-radius:6px}
    .hc-copy:hover{color:#fff}
    .hc-day{margin-left:10px;color:var(--hc-t);letter-spacing:.12em;white-space:nowrap}   /* plain text: the pill made it look like a button (Shaka) */
    .hc-day b{font-weight:600;margin-left:2px}"""

DASH_CSS = r"""    .hc-dash{position:absolute;top:14px;right:14px;z-index:2;display:inline-flex;align-items:center;gap:9px;height:38px;padding:0 16px;border-radius:999px;border:1.5px solid var(--hc-c);
      background:rgba(4,6,10,.62);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);color:var(--hc-t);font-family:'Orbitron',monospace;font-weight:700;font-size:.62rem;letter-spacing:.2em;white-space:nowrap;
      box-shadow:0 0 14px var(--hc-glow2),inset 0 0 10px var(--hc-glow2);transition:background .2s ease,color .2s ease,box-shadow .2s ease,transform .2s ease}
    @media(min-width:1024px){.hc-dash{top:clamp(16px,1.7vw,26px);right:clamp(16px,1.7vw,26px);height:clamp(40px,3.3vw,50px);padding:0 clamp(16px,1.6vw,24px);font-size:clamp(.66rem,.78vw,.82rem)}}"""

STATS_CSS = r"""    .hc-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}
    .hc-stats>div{display:flex;align-items:center;gap:10px;min-width:0;padding:10px;border-radius:10px;background:rgba(3,6,10,.62);border:1px solid var(--hc-panel);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);box-shadow:inset 0 1px 0 rgba(255,255,255,.05)}
    @media(min-width:1024px){.hc-stats{gap:clamp(10px,1.1vw,16px)}.hc-stats>div{gap:clamp(8px,.8vw,14px);padding:clamp(12px,1.1vw,18px) clamp(10px,1vw,18px)}}
    .hc-stats>div>div{display:flex;flex-direction:column;gap:3px;min-width:0}
    .hc-ico{flex-shrink:0;width:22px;height:22px;color:var(--hc-t);filter:drop-shadow(0 0 5px var(--hc-glow))}
    @media(min-width:1024px){.hc-ico{width:clamp(22px,1.75vw,28px);height:clamp(22px,1.75vw,28px)}}
    @media(max-width:480px){.hc-ico{display:none}.hc-stats>div{justify-content:center;text-align:center}.hc-stats>div>div{align-items:center}}
    .hc-lbl{font-weight:700;font-size:.66rem;letter-spacing:.16em;color:var(--hc-t);white-space:nowrap}
    .hc-val{font-weight:700;font-size:1.05rem;line-height:1.05;font-variant-numeric:tabular-nums;color:#fff;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    @media(min-width:1024px){.hc-lbl{font-size:clamp(.7rem,.82vw,.9rem)}.hc-val{font-size:clamp(1.1rem,1.38vw,1.6rem)}}
    .hc-full{display:none}
    @media(min-width:640px){.hc-full{display:inline}.hc-abbr{display:none}}
    .hc-chart{position:relative;padding:10px 0 8px 12px;border-radius:10px;background:rgba(3,6,10,.58);border:1px solid rgba(255,255,255,.09);-webkit-backdrop-filter:blur(2px);backdrop-filter:blur(2px)}
    .hc-chart-hd{display:flex;align-items:center;gap:7px;font-weight:700;font-size:.85rem;letter-spacing:.06em;color:#E6E8EE}
    .hc-chart-hd svg{width:17px;height:17px;color:var(--hc-t)}
    @media(min-width:1024px){.hc-chart{padding:clamp(10px,1vw,14px) 0 clamp(8px,.8vw,12px) clamp(12px,1.1vw,18px)}.hc-chart-hd{font-size:clamp(.85rem,1vw,1.1rem)}}
    .hc-plot{display:grid;grid-template-columns:minmax(0,1fr) auto;margin-top:4px;padding-right:12px}
    .hc-plot.hc-has-ax{padding-right:0}
    .hc-plotl{position:relative}
    .hc-spark{display:block;width:100%;height:96px}
    @media(min-width:1024px){.hc-spark{height:clamp(110px,max(9vw,13vh),190px)}}
    .hc-spark .hc-sl{filter:drop-shadow(0 0 4px var(--hc-line))}
    .hc-dot{position:absolute;right:-5px;width:10px;height:10px;margin-top:-5px;border-radius:50%;background:#fff;border:2.5px solid var(--hc-line);box-shadow:0 0 10px var(--hc-line),0 0 3px var(--hc-line)}
    .hc-yax{position:relative;min-width:6.4em;margin-left:8px;border-left:1px dashed rgba(255,255,255,.22);font-weight:600;font-size:.72rem;color:#CDD0D8;font-variant-numeric:tabular-nums;white-space:nowrap}
    .hc-yax span{position:absolute;left:8px;transform:translateY(-50%)}
    .hc-yax sub{font-size:.7em;vertical-align:-.25em}
    @media(min-width:1024px){.hc-yax{font-size:clamp(.72rem,.85vw,.92rem);min-width:7.2em}.hc-yax span{left:clamp(8px,.9vw,14px)}}"""

BUY_CSS = r"""    .hc-buy{position:relative;overflow:hidden;height:58px;width:100%;border:1.5px solid var(--hc-c);border-radius:14px;display:flex;align-items:center;justify-content:center;gap:14px;
      background:linear-gradient(180deg,rgba(255,255,255,.07),rgba(255,255,255,0) 45%),rgba(3,6,10,.72);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px);color:var(--hc-t);
      font-family:'Orbitron',monospace;font-weight:700;font-size:.82rem;letter-spacing:.26em;cursor:pointer;
      box-shadow:0 0 18px var(--hc-glow2),inset 0 0 18px var(--hc-glow2),inset 0 1px 0 rgba(255,255,255,.12);animation:hcGlow 3s ease-in-out infinite;transition:background .2s ease,transform .2s ease}
    .hc-buy span{text-shadow:0 0 10px var(--hc-glow)}
    @media(min-width:1024px){.hc-buy{height:clamp(62px,5.4vw,82px);font-size:clamp(.85rem,1.2vw,1.2rem);gap:clamp(14px,1.6vw,26px)}}
    .hc-buy img{position:relative;width:40px;height:40px;border-radius:50%;flex-shrink:0;filter:drop-shadow(0 0 8px var(--hc-glow))}
    @media(min-width:1024px){.hc-buy img{width:clamp(42px,3.6vw,56px);height:clamp(42px,3.6vw,56px)}}
    .hc-wave{position:absolute;top:0;height:100%;width:34%;color:var(--hc-c);opacity:.35;pointer-events:none}
    .hc-wave.l{left:0}.hc-wave.r{right:0;transform:scaleX(-1)}
    .hc-buy::after{content:'';position:absolute;top:0;left:0;width:100%;height:100%;pointer-events:none;
      background:linear-gradient(105deg,transparent 40%,rgba(255,255,255,.10) 48%,rgba(255,255,255,.18) 50%,rgba(255,255,255,.10) 52%,transparent 60%);animation:hcSweep 4s ease-in-out infinite}
    @keyframes hcSweep{0%{transform:translateX(-100%)}60%,100%{transform:translateX(100%)}}
    @keyframes hcGlow{0%,100%{box-shadow:0 0 16px var(--hc-glow2),inset 0 0 16px var(--hc-glow2),inset 0 1px 0 rgba(255,255,255,.12)}50%{box-shadow:0 0 30px var(--hc-glow),inset 0 0 22px var(--hc-glow2),inset 0 1px 0 rgba(255,255,255,.16)}}
    .hc-buy:hover{background:linear-gradient(180deg,rgba(255,255,255,.1),rgba(255,255,255,0) 45%),rgba(12,14,10,.8);transform:translateY(-1px)}
    .hc-buy:active{transform:translateY(0)}"""

PHONE_CSS = r"""    @media(max-width:639.98px){.hc-logo{width:72px;height:72px}.hc-top{gap:12px}.hc-name{font-size:1.7rem;padding-right:0}.hc-sub{font-size:.6rem;letter-spacing:.34em}.hc-price{font-size:1.7rem}.hc-chip{font-size:.9rem;padding:5px 7px}
      .hc-dash{top:12px;right:12px;height:32px;padding:0 11px;gap:7px;font-size:.52rem;letter-spacing:.14em}.hc-buy{font-size:.7rem;letter-spacing:.18em;gap:10px}.hc-buy img{width:34px;height:34px}}   /* 2026-10-23: phones — the compact pill clears the name */
    @media(max-width:379.98px){.hc-dash{width:34px;height:34px;padding:0;justify-content:center;gap:0}.hc-dash span{display:none}}   /* Audit IV e37, now from 380: the ⇄ icon alone (its aria-label stays) */
    @media(max-width:360px){.hc-t2{font-size:1.9rem}}   /* Audit IV e37: DASHBOARD lost a letter each side on a 320 phone */"""

lines_range(IX, "    .hc-card{position:relative;display:flex;flex-direction:column;gap:14px;padding:16px;border:2px solid",
            "    @media(min-width:1024px){.hc-day{font-size:.8rem;padding-left:8px}}", CARD_CSS, done='.hc-art{position:absolute')
lines_range(IX, "    .hc-dash{position:absolute;top:12px;right:12px;display:inline-flex",
            "    @media(min-width:1024px){.hc-dash{top:14px;right:14px;height:40px", DASH_CSS, done='.hc-dash{position:absolute;top:14px;right:14px;z-index:2')
edit(IX, "    @media(max-width:360px){.hc-dash{width:36px;padding:0;justify-content:center;gap:0}.hc-dash span{display:none}.hc-t2{font-size:1.9rem}}   /* Audit IV e37: on a 320 phone the BUY / SELL pill sat on the token name (now the ⇄ icon alone; its aria-label stays) and DASHBOARD lost a letter each side */\n", "")
edit(IX, "    .hc-dash:hover{background:var(--hc-c);color:#0b0b06;box-shadow:0 0 22px var(--hc-glow),inset 0 1px 0 rgba(255,255,255,.3);transform:translateY(-1px)}",
         "    .hc-dash:hover{background:var(--hc-c);color:#0b0b06;box-shadow:0 0 24px var(--hc-glow);transform:translateY(-1px)}")
lines_range(IX, "    .hc-stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:8px}",
            "    .hc-spark .hc-sl{filter:drop-shadow(0 0 3px var(--hc-line))}", STATS_CSS, done='.hc-chart{position:relative')
lines_range(IX, "    .hc-buy{position:relative;overflow:hidden;height:52px",
            "    .hc-buy:active{transform:translateY(0);filter:brightness(.97)}", BUY_CSS, done='.hc-wave{position:absolute')
edit(IX, "    .hc-skel .hc-buy.hc-sk{background:rgba(255,255,255,.08);box-shadow:none;animation:none}.hc-skel .hc-buy.hc-sk::after{content:none}",
         "    .hc-skel .hc-buy.hc-sk{background:rgba(255,255,255,.08);border-color:transparent;box-shadow:none;animation:none}.hc-skel .hc-buy.hc-sk::after{content:none}")
edit(IX, "    @media(prefers-reduced-motion:reduce){.hc-card,.hc-buy,.hc-dash{transition:none!important}.hc-card:hover,.hc-buy:hover,.hc-dash:hover{transform:none}",
         "    @media(prefers-reduced-motion:reduce){.hc-card,.hc-buy,.hc-dash,.hc-art{transition:none!important}.hc-card:hover,.hc-buy:hover,.hc-dash:hover,.hc-card:hover .hc-art{transform:none}")
# phone rules go after every base rule they override
edit(IX, "    .hc-status .text-white\\/40{color:rgba(255,255,255,.78)}", PHONE_CSS + "\n    .hc-status .text-white\\/40{color:rgba(255,255,255,.78)}")

# ------------------------------------------------------------------ JSX: the chart
edit(IX, "          .map(c=>({t:Number(c[0])*1000,p:parseFloat(c[4])}))",
         "          .map(c=>({t:Number(c[0])*1000,p:parseFloat(c[4]),v:parseFloat(c[5])}))   // v: the candle's USD volume (the bars under the line)")

OLD_FLAT = """    const HomeSparkFlat=({label})=>(
      <svg className="hc-spark" viewBox="0 0 600 140" preserveAspectRatio="none" role="img" aria-label={label}>
        <path d="M0,70 L600,70" fill="none" style={{stroke:'rgba(255,255,255,0.18)'}} strokeWidth="2" strokeDasharray="6 6" vectorEffect="non-scaling-stroke"/>
      </svg>
    );"""
NEW_FLAT = """    const HomeSparkFlat=({label})=>(
      <div className="hc-plot"><div className="hc-plotl">
        <svg className="hc-spark" viewBox="0 0 600 160" preserveAspectRatio="none" role="img" aria-label={label}>
          <path d="M0,80 L600,80" fill="none" style={{stroke:'rgba(255,255,255,0.18)'}} strokeWidth="2" strokeDasharray="6 6" vectorEffect="non-scaling-stroke"/>
        </svg>
      </div></div>
    );
    /* The price axis: up to 4 round prices inside the drawn range (the card's own fmtPrice format, 0.0₄2000). */
    const hcTicks=(lo,hi)=>{
      const r=hi-lo;if(!(r>0))return[];
      const mag=Math.pow(10,Math.floor(Math.log10(r/4)));
      const fit=[1,2,2.5,5,10,20].map(m=>m*mag).filter(s=>Math.floor(hi/s)-Math.ceil(lo/s)+1<=4);
      const step=fit.sort((a,b)=>Math.abs(r/a-4)-Math.abs(r/b-4))[0];if(!step)return[];
      const out=[];for(let k=Math.ceil(lo/step);k*step<=hi;k++)out.push(+(k*step).toPrecision(12));
      return out;
    };
    const HcTick=({p})=>{const f=fmtPrice(p);return typeof f==='string'?f:<>{f.pre}<sub>{f.z}</sub>{f.d}</>;};"""
edit(IX, OLD_FLAT, NEW_FLAT)

OLD_DRAW = """      const up=(d?.change!=null&&isFinite(d.change))?d.change>=0:null;
      const ps=pts.map(q=>q.p),lo=Math.min(...ps),hi=Math.max(...ps),span=hi-lo;
      const line='M'+pts.map(q=>`${(q.x*600).toFixed(1)},${span>0?(132-((q.p-lo)/span)*116).toFixed(1):'70.0'}`).join(' L');
      const gid=`hcg-${token}`;
      return(
        <svg className="hc-spark" viewBox="0 0 600 140" preserveAspectRatio="none" role="img" aria-label={`${token} price over the last 24 hours${up==null?'':up?', up':', down'}`}>
          <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" style={{stopColor:'var(--hc-line)',stopOpacity:0.75}}/><stop offset="0.6" style={{stopColor:'var(--hc-line)',stopOpacity:0.22}}/><stop offset="1" style={{stopColor:'var(--hc-line)',stopOpacity:0}}/></linearGradient></defs>
          <path d={`${line} L600,140 L0,140 Z`} fill={`url(#${gid})`}/>
          <path className="hc-sl" d={line} fill="none" style={{stroke:'var(--hc-line)'}} strokeWidth="2.5" strokeLinejoin="round" vectorEffect="non-scaling-stroke"/>
        </svg>
      );"""
NEW_DRAW = """      const up=(d?.change!=null&&isFinite(d.change))?d.change>=0:null;
      /* 2026-10-23 (Shaka's mockup): a 600×160 plot — the line in 10…150 with 12 % headroom above and below, the price axis on the
         right (hcTicks), and the candles' USD volume as bars along the bottom 34 units (real candles only; the 5-point fallback has none). */
      const ps=pts.map(q=>q.p);let lo=Math.min(...ps),hi=Math.max(...ps);
      const pad=hi>lo?(hi-lo)*0.12:(hi*0.02||1e-12);lo-=pad;hi+=pad;
      const Y=p=>150-((p-lo)/(hi-lo))*140;
      const line='M'+pts.map(q=>`${(q.x*600).toFixed(1)},${Y(q.p).toFixed(1)}`).join(' L');
      const ticks=hcTicks(lo,hi);
      const vs=seriesOk?series.filter(s=>s.v>0&&isFinite(s.v)):[];
      const vmax=vs.length?Math.max(...vs.map(s=>s.v)):0;
      const t0=Date.now()-86400000;
      const gid=`hcg-${token}`;
      const last=pts[pts.length-1];
      return(
        <div className={`hc-plot${ticks.length?' hc-has-ax':''}`}>
          <div className="hc-plotl">
            <svg className="hc-spark" viewBox="0 0 600 160" preserveAspectRatio="none" role="img" aria-label={`${token} price over the last 24 hours${up==null?'':up?', up':', down'}`}>
              <defs><linearGradient id={gid} x1="0" y1="0" x2="0" y2="1"><stop offset="0" style={{stopColor:'var(--hc-line)',stopOpacity:0.42}}/><stop offset="0.7" style={{stopColor:'var(--hc-line)',stopOpacity:0.1}}/><stop offset="1" style={{stopColor:'var(--hc-line)',stopOpacity:0}}/></linearGradient></defs>
              <g stroke="rgba(255,255,255,0.06)" strokeWidth="1" vectorEffect="non-scaling-stroke">
                {ticks.map(v=><line key={'h'+v} x1="0" x2="600" y1={Y(v).toFixed(1)} y2={Y(v).toFixed(1)} vectorEffect="non-scaling-stroke"/>)}
                {[1,2,3,4,5,6,7].map(i=><line key={'v'+i} x1={i*75} x2={i*75} y1="0" y2="160" vectorEffect="non-scaling-stroke"/>)}
              </g>
              {vmax>0&&<g style={{fill:'var(--hc-line)'}} opacity="0.42">{vs.map(s=>{const x=Math.max(0,Math.min(1,(s.t-t0)/86400000))*600,h=Math.max(1,s.v/vmax*34);return<rect key={s.t} x={(x-2).toFixed(1)} y={(160-h).toFixed(1)} width="4" height={h.toFixed(1)}/>;})}</g>}
              <path d={`${line} L600,160 L0,160 Z`} fill={`url(#${gid})`}/>
              <path className="hc-sl" d={line} fill="none" style={{stroke:'var(--hc-line)'}} strokeWidth="2.4" strokeLinejoin="round" vectorEffect="non-scaling-stroke"/>
            </svg>
            {last&&last.x>0.98&&<span className="hc-dot" aria-hidden="true" style={{top:`${(Y(last.p)/160*100).toFixed(2)}%`}}></span>}
          </div>
          {ticks.length>0&&<div className="hc-yax" aria-hidden="true">{ticks.map(v=><span key={v} style={{top:`${(Y(v)/160*100).toFixed(2)}%`}}><HcTick p={v}/></span>)}</div>}
        </div>
      );"""
edit(IX, OLD_DRAW, NEW_DRAW, done='HOME_SPARK_WIN')

# ------------------------------------------------------------------ JSX: the card
edit(IX, """    const HC_DONE_ICON=<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 13l4 4L19 7"/></svg>;""",
"""    const HC_DONE_ICON=<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#4ade80" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 13l4 4L19 7"/></svg>;
    /* 2026-10-23 (Shaka's mockup): the stat-tile icons, the chart's clock, the ENTER DASHBOARD waves. */
    const HC_ICO_BARS=<svg className="hc-ico" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><rect x="3" y="13" width="4" height="8" rx="1"/><rect x="10" y="8" width="4" height="13" rx="1"/><rect x="17" y="3" width="4" height="18" rx="1"/></svg>;
    const HC_ICO_COINS=<svg className="hc-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true"><ellipse cx="12" cy="5.5" rx="7.5" ry="2.8"/><path d="M4.5 5.5v4c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8v-4M4.5 9.5v4c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8v-4M4.5 13.5v4c0 1.5 3.4 2.8 7.5 2.8s7.5-1.3 7.5-2.8v-4"/></svg>;
    const HC_ICO_LINK=<svg className="hc-ico" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true"><path d="M10 14a4.5 4.5 0 0 0 6.4 0l3.2-3.2a4.5 4.5 0 0 0-6.4-6.4L11.6 6"/><path d="M14 10a4.5 4.5 0 0 0-6.4 0l-3.2 3.2a4.5 4.5 0 0 0 6.4 6.4l1.6-1.6"/></svg>;
    const HC_CLOCK=<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/></svg>;
    const HcWave=({side})=><svg className={`hc-wave ${side}`} viewBox="0 0 200 80" preserveAspectRatio="none" fill="none" stroke="currentColor" strokeWidth="0.8" aria-hidden="true"><path d="M0 52C40 30 80 70 120 46S180 30 200 40"/><path d="M0 58C40 36 80 76 120 52S180 36 200 46" opacity="0.7"/><path d="M0 64C40 42 80 82 120 58S180 42 200 52" opacity="0.45"/></svg>;""")

edit(IX, """        <div onClick={open} className={`hc-card ${isGold?'hc-gold':'hc-green'}${masked?' hc-masked':''}`}>
          {masked""", """        <div onClick={open} className={`hc-card ${isGold?'hc-gold':'hc-green'}${masked?' hc-masked':''}`}>
          <div className="hc-art" aria-hidden="true"></div><div className="hc-veil" aria-hidden="true"></div>
          {masked""")
edit(IX, """              <div className="hc-name">{token}</div>
              <div className="hc-pricerow">
                {masked?""", """              <div className="hc-name">{token}</div>
              <div className="hc-sub">NATIVE TOKEN</div>
              <div className="hc-pricerow">
                {masked?""")
edit(IX, """{!masked&&daysOld!=null&&<span className="hc-day">DAY {daysOld.toLocaleString('en-US')}</span>}""",
         """{!masked&&daysOld!=null&&<span className="hc-day">DAY <b>{daysOld.toLocaleString('en-US')}</b></span>}""")
edit(IX, """            <div><span className="hc-lbl">MCAP</span><span className="hc-val">{masked?'—':<><span className="hc-full">{fmtUSD(d?.mcap)}</span><span className="hc-abbr">{abbr(d?.mcap)}</span></>}</span></div>
            <div><span className="hc-lbl">VOL (24H)</span><span className="hc-val">{masked?'—':fmtUSD(d?.vol)}</span></div>
            <div><span className="hc-lbl">PLS RATIO</span><span className="hc-val">{masked?'—':plsRatio}</span></div>
          </div>
          {masked?<HomeSparkFlat label={`${token} chart hidden during maintenance`}/>:<HomeSpark token={token} d={d}/>}
          {!masked&&<button type="button" className="hc-buy" onClick={e=>{e.stopPropagation();onSelect(token);}} aria-label={`Open the ${token} dashboard`}><img src={cfg.logo} alt=""/>""",
"""            <div>{HC_ICO_BARS}<div><span className="hc-lbl">MCAP</span><span className="hc-val">{masked?'—':<><span className="hc-full">{fmtUSD(d?.mcap)}</span><span className="hc-abbr">{abbr(d?.mcap)}</span></>}</span></div></div>
            <div>{HC_ICO_COINS}<div><span className="hc-lbl">VOL (24H)</span><span className="hc-val">{masked?'—':fmtUSD(d?.vol)}</span></div></div>
            <div>{HC_ICO_LINK}<div><span className="hc-lbl">PLS RATIO</span><span className="hc-val">{masked?'—':plsRatio}</span></div></div>
          </div>
          <div className="hc-chart"><div className="hc-chart-hd">{HC_CLOCK}24H</div>
            {masked?<HomeSparkFlat label={`${token} chart hidden during maintenance`}/>:<HomeSpark token={token} d={d}/>}
          </div>
          {!masked&&<button type="button" className="hc-buy" onClick={e=>{e.stopPropagation();onSelect(token);}} aria-label={`Open the ${token} dashboard`}><HcWave side="l"/><HcWave side="r"/><img src={cfg.logo} alt=""/>""", done='{HC_CLOCK}7D')

# the skeleton mirrors the new geometry (gotcha 11): art + veil, NATIVE TOKEN line, icon tiles, the chart panel
edit(IX, """      <div aria-hidden="true" className={`hc-card hc-skel ${gold?'hc-gold':'hc-green'}`}>
        <div className="hc-top">""", """      <div aria-hidden="true" className={`hc-card hc-skel ${gold?'hc-gold':'hc-green'}`}>
        <div className="hc-art"></div><div className="hc-veil"></div>
        <div className="hc-top">""")
edit(IX, """            <div className="hc-name"><HcSk w="3.4em"/></div>
            <div className="hc-pricerow">""", """            <div className="hc-name"><HcSk w="3.4em"/></div>
            <div className="hc-sub"><HcSk w="11em" h="0.8em"/></div>
            <div className="hc-pricerow">""")
edit(IX, """          {[0,1,2].map(i=><div key={i}><span className="hc-lbl"><HcSk w="5em" h="0.9em"/></span><span className="hc-val"><HcSk w="5.5em"/></span></div>)}
        </div>
        <span className="hc-spark hc-sk animate-pulse"></span>""", """          {[0,1,2].map(i=><div key={i}><span className="hc-ico"></span><div><span className="hc-lbl"><HcSk w="5em" h="0.9em"/></span><span className="hc-val"><HcSk w="5.5em"/></span></div></div>)}
        </div>
        <div className="hc-chart"><div className="hc-chart-hd">{HC_CLOCK}24H</div><div className="hc-plot"><span className="hc-spark hc-sk animate-pulse"></span></div></div>""", done='{HC_CLOCK}7D')

print(f'{n} edit(s)')

# ---- round 2 (Shaka, 2026-10-24: "the boxes are taller than than used to be. Can you shorter up the boxes" + "make the backgrounds in
#      the ufo box a little darker") — overrides placed AFTER every round-1 rule (anchored past the round-1 phone block, never inside it):
#      smaller logo / name / price and tighter gaps, compact stat tiles, a one-line 24H label, a shorter chart and button. 1440×900:
#      613 → ~455 px (the cards before the redesign: 457). The UFO art gets brightness .78 under the same veil.
R2_CSS = r"""    /* 2026-10-24 round 2: shorter cards (back to the old height) + a darker UFO background (Shaka) */
    .hc-card{gap:10px}
    @media(min-width:1024px){.hc-card{padding:clamp(16px,1.45vw,24px) clamp(18px,1.6vw,26px) clamp(16px,1.35vw,22px);gap:clamp(10px,.85vw,14px)}}
    @media(min-width:640px){.hc-logo{width:92px;height:92px}}
    @media(min-width:1024px){.hc-logo{width:clamp(92px,7.6vw,124px);height:clamp(92px,7.6vw,124px)}.hc-name{font-size:clamp(1.9rem,2.6vw,2.9rem)}.hc-sub{margin-top:5px}.hc-pricerow{margin-top:clamp(6px,.6vw,10px)}.hc-price{font-size:clamp(1.8rem,2.5vw,2.7rem)}.hc-chip{font-size:clamp(.95rem,1.2vw,1.25rem);padding:5px 10px}.hc-meta{margin-top:clamp(4px,.4vw,8px)}}
    .hc-stats>div{padding:8px 10px}
    @media(min-width:1024px){.hc-stats>div{padding:clamp(9px,.75vw,13px) clamp(10px,1vw,16px)}}
    .hc-chart{padding:7px 0 6px 10px}
    @media(min-width:1024px){.hc-chart{padding:clamp(7px,.6vw,11px) 0 clamp(6px,.5vw,9px) clamp(10px,1vw,16px)}}
    .hc-chart-hd{font-size:.74rem;line-height:1;gap:6px}.hc-chart-hd svg{width:14px;height:14px}
    @media(min-width:1024px){.hc-chart-hd{font-size:clamp(.74rem,.8vw,.9rem)}}
    .hc-plot{margin-top:2px}
    .hc-spark{height:62px}
    @media(min-width:1024px){.hc-spark{height:clamp(78px,max(5.4vw,8vh),120px)}}
    .hc-buy{height:48px}
    @media(min-width:1024px){.hc-buy{height:clamp(52px,4.2vw,66px)}.hc-buy img{width:clamp(36px,3vw,46px);height:clamp(36px,3vw,46px)}}
    @media(max-width:639.98px){.hc-logo{width:68px;height:68px}.hc-sub{margin-top:4px}.hc-pricerow{margin-top:6px}.hc-meta{margin-top:4px}.hc-buy img{width:32px;height:32px}.hc-card{gap:9px}}
    @media(max-width:399.98px){.hc-meta{font-size:.84rem;gap:2px 6px}.hc-day{margin-left:4px}}
    @media(max-width:639.98px){.hc-yax span:nth-child(2n){display:none}}   /* a 62 px phone chart: every other price label */
    .hc-green .hc-art{filter:saturate(.85) brightness(.78)}"""
edit(IX, "    .hc-status>div{font-size:.8rem}\n", "    .hc-status>div{font-size:.8rem}\n" + R2_CSS + "\n")

# ---- round 3 (Shaka, 2026-10-24: "make both backgrounds a little darker... and maybe we shold do the graph at 7 days not 24 hrs?") ----
# The chart: GeckoTerminal HOURLY candles for the last 7 days (the same main pool, token= side, USD; <=170 rows, one request per card,
# 10-minute cache) instead of 15-minute candles for 24 h. Fallback: the repo's data/charts-intraday.json hourly series (the pipeline's
# CoinGecko on-chain closes for the same pool, 14 days, refreshed hourly) - used only when its last close is < 3 h old. The old 24 h
# five-point fallback is gone (it cannot honestly be labelled 7D); with neither source the chart is the dashed "unavailable" line.
# Volume bars use a square-root scale (one busy hour no longer flattens the other 167).
# The chart label reads "7D" with the 7-day change beside it: the card's price / the first close inside the window - 1. The 24 h chip
# by the price is unchanged (DexScreener's 24 h change).
edit(IX, "      const url=`https://api.geckoterminal.com/api/v2/networks/pulsechain/pools/${cfg.mainPair}/ohlcv/minute?aggregate=15&limit=100&currency=usd&token=${cfg.address}`;",
         "      const url=`https://api.geckoterminal.com/api/v2/networks/pulsechain/pools/${cfg.mainPair}/ohlcv/hour?aggregate=1&limit=170&currency=usd&token=${cfg.address}`;   // round 3: 7 days of hourly candles")
edit(IX, "        const since=Date.now()-86400000;", "        const since=Date.now()-HOME_SPARK_WIN;")
edit(IX, "        if(pts.length<4)return null;\n        _homeSparkCache[token]={at:Date.now(),pts};",
         "        if(pts.length<12)return homeSparkRepo(token);\n        _homeSparkCache[token]={at:Date.now(),pts};")
edit(IX, "      }catch(e){return null;}\n      finally{clearTimeout(to);}\n    };\n    const homeSparkFallback=(d)=>{",
         "      }catch(e){return homeSparkRepo(token);}\n      finally{clearTimeout(to);}\n    };\n    const homeSparkFallback=(d)=>{",
         done="      }catch(e){return homeSparkRepo(token);}")
edit(IX, "        if(!r.ok)return null;\n        const j=await r.json();\n        const since=Date.now()-HOME_SPARK_WIN;",
         "        if(!r.ok)return homeSparkRepo(token);\n        const j=await r.json();\n        const since=Date.now()-HOME_SPARK_WIN;")
edit(IX, "    const HOME_SPARK_TTL=10*60*1000;\n    const _homeSparkCache={};",
"""    const HOME_SPARK_TTL=10*60*1000;
    const HOME_SPARK_WIN=7*86400000;   // round 3 (Shaka, 2026-10-24): the card chart is 7 days, hourly
    const _homeSparkCache={};
    /* Round 3 fallback: the repo's hourly closes (data/charts-intraday.json - the pipeline's CoinGecko on-chain series for the same
       pool, 14 days). No volume. Only when the newest close is under 3 h old; one file read shared by both cards. */
    let _hcRepoP=null;
    const homeSparkRepo=async(token)=>{
      try{
        if(!_hcRepoP)_hcRepoP=dataFetch('https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/charts-intraday.json').then(r=>r.ok?r.json():null).catch(()=>null);
        const j=await _hcRepoP;if(!j){_hcRepoP=null;return null;}
        const ser=j?.tokens?.[token]?.hourly?.series;if(!Array.isArray(ser))return null;
        const since=Date.now()-HOME_SPARK_WIN;
        const pts=ser.map(c=>({t:Number(c[0]),p:parseFloat(c[1])})).filter(x=>isFinite(x.t)&&x.t>=since&&x.p>0&&isFinite(x.p)).sort((a,b)=>a.t-b.t);
        if(pts.length<12||Date.now()-pts[pts.length-1].t>3*3600000)return null;
        return pts;   // not put in _homeSparkCache: the next tick tries GeckoTerminal again
      }catch(e){return null;}
    };""")
# the five-point 24 h fallback goes (it cannot be labelled 7D)
edit(IX, "      if(!pts)pts=homeSparkFallback(d);\n      if(!pts)return<HomeSparkFlat label={`${token} 24 hour chart unavailable`}/>;",
         "      if(!pts)return<><div className=\"hc-chart-hd\">{HC_CLOCK}7D</div><HomeSparkFlat label={`${token} 7 day chart unavailable`}/></>;")
edit(IX, """      const seriesOk=series&&series.length>=4&&(!(d?.price>0)||Math.abs(series[series.length-1].p/d.price-1)<0.25);
      if(seriesOk){
        const now=Date.now(),t0=now-86400000;
        const all=(d?.price>0)?series.concat([{t:now,p:d.price}]):series;   // end on the price the card prints
        pts=all.map(s=>({x:Math.max(0,Math.min(1,(s.t-t0)/86400000)),p:s.p}));
      }""", """      const seriesOk=series&&series.length>=12&&(!(d?.price>0)||Math.abs(series[series.length-1].p/d.price-1)<0.25);
      let chg7=null;
      if(seriesOk){
        const now=Date.now(),t0=now-HOME_SPARK_WIN;
        const all=(d?.price>0)?series.concat([{t:now,p:d.price}]):series;   // end on the price the card prints
        pts=all.map(s=>({x:Math.max(0,Math.min(1,(s.t-t0)/HOME_SPARK_WIN)),p:s.p}));
        chg7=(all[all.length-1].p/all[0].p-1)*100;   // 7D change: the price now / the first close inside the window
      }""")
edit(IX, "      const t0=Date.now()-86400000;\n      const gid=`hcg-${token}`;", "      const t0=Date.now()-HOME_SPARK_WIN;\n      const gid=`hcg-${token}`;")
edit(IX, """      return(
        <div className={`hc-plot${ticks.length?' hc-has-ax':''}`}>""", """      return(<>
        <div className="hc-chart-hd">{HC_CLOCK}7D{chg7!=null&&isFinite(chg7)&&<span className={`hc-c7 ${chg7>=0?'up':'dn'}`}>{chg7>=0?'▲':'▼'} {Math.abs(chg7).toFixed(2)}%</span>}</div>
        <div className={`hc-plot${ticks.length?' hc-has-ax':''}`}>""", done='round 4: no 7D %')
edit(IX, """          {ticks.length>0&&<div className="hc-yax" aria-hidden="true">{ticks.map(v=><span key={v} style={{top:`${(Y(v)/160*100).toFixed(2)}%`}}><HcTick p={v}/></span>)}</div>}
        </div>
      );""", """          {ticks.length>0&&<div className="hc-yax" aria-hidden="true">{ticks.map(v=><span key={v} style={{top:`${(Y(v)/160*100).toFixed(2)}%`}}><HcTick p={v}/></span>)}</div>}
        </div>
      </>);""")
edit(IX, "aria-label={`${token} price over the last 24 hours${up==null?'':up?', up':', down'}`}>",
         "aria-label={`${token} price over the last 7 days${chg7==null?'':chg7>=0?', up':', down'}`}>")
edit(IX, "                {[1,2,3,4,5,6,7].map(i=><line key={'v'+i} x1={i*75} x2={i*75} y1=\"0\" y2=\"160\" vectorEffect=\"non-scaling-stroke\"/>)}",
         "                {[1,2,3,4,5,6].map(i=>{const x=(i*600/7).toFixed(1);return<line key={'v'+i} x1={x} x2={x} y1=\"0\" y2=\"160\" vectorEffect=\"non-scaling-stroke\"/>;})}")
edit(IX, "const x=Math.max(0,Math.min(1,(s.t-t0)/86400000))*600,h=Math.max(1,s.v/vmax*34);return<rect key={s.t} x={(x-2).toFixed(1)} y={(160-h).toFixed(1)} width=\"4\" height={h.toFixed(1)}/>;",
         "const x=Math.max(0,Math.min(1,(s.t-t0)/HOME_SPARK_WIN))*600,h=Math.max(1,Math.sqrt(s.v/vmax)*34);return<rect key={s.t} x={(x-1.1).toFixed(1)} y={(160-h).toFixed(1)} width=\"2.2\" height={h.toFixed(1)}/>;")
edit(IX, "      const up=(d?.change!=null&&isFinite(d.change))?d.change>=0:null;\n      /* 2026-10-23 (Shaka's mockup)", "      /* 2026-10-23 (Shaka's mockup)",
     done="price over the last 7 days")
# remove the dead five-point helper
_s = open(IX, encoding='utf-8').read()
_i = _s.find("    const homeSparkFallback=(d)=>{")
if _i >= 0:
    _j = _s.index("    const HomeSparkFlat=", _i)
    open(IX, 'w', encoding='utf-8').write(_s[:_i] + _s[_j:]); n += 1
# the card + skeleton: HomeSpark draws its own label (it knows the 7D change)
edit(IX, """          <div className="hc-chart"><div className="hc-chart-hd">{HC_CLOCK}24H</div>
            {masked?<HomeSparkFlat label={`${token} chart hidden during maintenance`}/>:<HomeSpark token={token} d={d}/>}""",
         """          <div className="hc-chart">
            {masked?<><div className="hc-chart-hd">{HC_CLOCK}7D</div><HomeSparkFlat label={`${token} chart hidden during maintenance`}/></>:<HomeSpark token={token} d={d}/>}""")
edit(IX, """<div className="hc-chart"><div className="hc-chart-hd">{HC_CLOCK}24H</div><div className="hc-plot"><span className="hc-spark hc-sk animate-pulse"></span></div></div>""",
         """<div className="hc-chart"><div className="hc-chart-hd">{HC_CLOCK}7D</div><div className="hc-plot"><span className="hc-spark hc-sk animate-pulse"></span></div></div>""")
R3_CSS = r"""    /* 2026-10-24 round 3: both backgrounds a step darker (Shaka); the 7D change beside the chart label */
    .hc-veil{background:radial-gradient(ellipse 62% 40% at 30% 22%,rgba(2,4,8,.82) 0%,rgba(2,4,8,.52) 55%,transparent 80%),linear-gradient(180deg,rgba(2,4,8,.54) 0%,rgba(2,4,8,.62) 32%,rgba(2,4,8,.76) 52%,rgba(2,4,8,.74) 78%,rgba(2,4,8,.60) 100%)}
    .hc-c7{margin-left:4px;font-weight:700;letter-spacing:.02em}.hc-c7.up{color:#4BF07F}.hc-c7.dn{color:#FF5D5D}
    @media(max-width:639.98px){.hc-yax span:nth-child(2):last-child{display:inline}}   /* two axis labels: keep both (round 2 hid every other one) */"""
edit(IX, "    .hc-green .hc-art{filter:saturate(.85) brightness(.78)}\n", "    .hc-green .hc-art{filter:saturate(.85) brightness(.78)}\n" + R3_CSS + "\n")

print(f'{n} edit(s)')

# ---- round 4 (Shaka, 2026-10-24: "dont show the up down percentage for the 7D" + "make the ufo background a little darker") ----
edit(IX, """        <div className="hc-chart-hd">{HC_CLOCK}7D{chg7!=null&&isFinite(chg7)&&<span className={`hc-c7 ${chg7>=0?'up':'dn'}`}>{chg7>=0?'▲':'▼'} {Math.abs(chg7).toFixed(2)}%</span>}</div>""",
         """        <div className="hc-chart-hd">{HC_CLOCK}7D{/* round 4: no 7D % (Shaka) - chg7 only feeds the aria-label's up / down */}</div>""")
R4_CSS = """    .hc-green .hc-art{filter:saturate(.85) brightness(.66)}   /* 2026-10-24 round 4: the UFO art a step darker again (Shaka; was .78) */"""
edit(IX, "    @media(max-width:639.98px){.hc-yax span:nth-child(2):last-child{display:inline}}   /* two axis labels: keep both (round 2 hid every other one) */\n",
         "    @media(max-width:639.98px){.hc-yax span:nth-child(2):last-child{display:inline}}   /* two axis labels: keep both (round 2 hid every other one) */\n" + R4_CSS + "\n")

# ---- round 5 (Shaka, 2026-10-24: "make the two backgrounds inside the ptgc and ufo box on the landing page darker" + "get rid of
#      the numbers to the right of the graph") ----
R5_CSS = """    /* 2026-10-24 round 5: both card backgrounds a step darker again (Shaka) — veil .54/.62/.76/.74/.60 → .64/.70/.80/.78/.68, art dimmed */
    .hc-veil{background:radial-gradient(ellipse 62% 40% at 30% 22%,rgba(2,4,8,.86) 0%,rgba(2,4,8,.6) 55%,transparent 80%),linear-gradient(180deg,rgba(2,4,8,.64) 0%,rgba(2,4,8,.70) 32%,rgba(2,4,8,.80) 52%,rgba(2,4,8,.78) 78%,rgba(2,4,8,.68) 100%)}
    .hc-gold .hc-art{filter:saturate(.9) brightness(.85)}.hc-green .hc-art{filter:saturate(.85) brightness(.58)}
    .hc-yax{display:none}.hc-plot.hc-has-ax{padding-right:12px}   /* round 5: no price labels right of the chart (Shaka: "we dont need them there") — the faint price gridlines stay */"""
edit(IX, R4_CSS + "\n", R4_CSS + "\n" + R5_CSS + "\n")
print(f'{n} edit(s) (round 5)')
