# Tile badges in the dashboard colour (2026-10-06, Shaka): the clickable bot / Holders icons and RH take the token colour (--a: gold / UFO green);
# the ⓘ circles and the LP % stay grey. The icons become CSS masks (alpha of the same images) filled with var(--a); RH is a badge the icons' size. Idempotent.
import sys,re
p=sys.argv[1] if len(sys.argv)>1 else 'index.html'
s=open(p,encoding='utf-8').read()
# Holders icon: img → masked span
old_h='<img className="h2-hd" src={`logos/holders/nh-ic-new.webp?v=${NH_ART_V}`} alt="" aria-hidden="true"/>'
new_h='<span className="h2-hd" style={{"--ic":`url(logos/holders/nh-ic-new.webp?v=${NH_ART_V})`}} aria-hidden="true"></span>'
if old_h in s: s=s.replace(old_h,new_h,1)
old_b='<img className="h2-hd h2-bot" src="logos/hvb/ic-bot.svg" alt="" aria-hidden="true"/>'
new_b='<span className="h2-hd h2-bot" style={{"--ic":"url(logos/hvb/ic-bot.svg)"}} aria-hidden="true"></span>'
if old_b in s: s=s.replace(old_b,new_b,1)
old_r='aria-label="Liquidity with RH Core coins" className="tap-h">RH</button>'
new_r='aria-label="Liquidity with RH Core coins" className="tap-h h2-rh">RH</button>'
if old_r in s: s=s.replace(old_r,new_r,1)
assert '"--ic"' in s and 'h2-rh' in s
open(p,'w',encoding='utf-8').write(s); print('index ok')
# the LP % stays grey (it is not clickable)
s=open(p,encoding='utf-8').read()
s=s.replace("{badge:<span>{tokensInLPKnown?tokensInLPPct+'%':'—'}</span>})}","{badge:<span className=\"h2-pct\">{tokensInLPKnown?tokensInLPPct+'%':'—'}</span>})}",1)
open(p,'w',encoding='utf-8').write(s); print('pct ok')
