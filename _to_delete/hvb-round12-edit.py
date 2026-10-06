# Humans vs Bots round 12 (2026-10-06): UFO greens the human side of the banner; a confidence note at the foot. Idempotent.
import re,sys
p=sys.argv[1] if len(sys.argv)>1 else 'index.html'
s=open(p,encoding='utf-8').read(); o=s
# 1) CSS: a hue-tint over the left of the banner, only on UFO
anchor='    .vs-sky-veil{'
css='    .vs-sky-tint{position:absolute;inset:0;mix-blend-mode:color;background:linear-gradient(90deg,rgba(120,230,60,.95) 0%,rgba(120,230,60,.95) 30%,rgba(120,230,60,0) 56%)}   /* round 12: on UFO the gold human side of the banner goes UFO green (colour blend — luminosity of the art kept, hue swapped), fading out before the robot */\n'
if '.vs-sky-tint{' not in s: s=s.replace(anchor,css+anchor,1)
# 2) JSX: the tint element after .vs-sky, UFO only
old='              <div aria-hidden="true" className="vs-sky"></div>\n              <div aria-hidden="true" className="vs-sky-veil"></div>'
new='              <div aria-hidden="true" className="vs-sky"></div>\n              {token===\'UFO\'&&<div aria-hidden="true" className="vs-sky-tint"></div>}\n              <div aria-hidden="true" className="vs-sky-veil"></div>'
if 'vs-sky-tint"' not in s: assert old in s; s=s.replace(old,new,1)
# 3) the confidence note after the How we tell fold
old2='''                  </Fold>
                </>
              )}
            </div>
          </div>
        </Modal>'''
new2='''                  </Fold>
                  {/* round 12 (Shaka): a confidence note — the split is vastly right, a few small trades at the edges may still be mislabelled */}
                  <p className="vs-conf">How sure are we? Very. Every trade is classified from the chain itself {'—'} who called the pool, where the tokens went, and whether the same transaction bought in one pool and sold in another {'—'} so the overwhelming majority land exactly where they belong. A handful of small trades at the edges can still be mislabelled, so read this as a very close picture rather than a to-the-cent ledger.</p>
                </>
              )}
            </div>
          </div>
        </Modal>'''
if 'vs-conf' not in s: assert old2 in s; s=s.replace(old2,new2,1)
css2='    .vs-conf{margin:14px 4px 2px;font-size:12.5px;line-height:1.55;color:rgba(255,255,255,.42);text-align:center}\n    .vs-conf::before{content:"";display:block;width:120px;height:1px;margin:0 auto 12px;background:linear-gradient(90deg,transparent,rgba(255,255,255,.25),transparent)}\n'
if '.vs-conf{' not in s: s=s.replace('    .vs-note{',css2+'    .vs-note{',1)
assert s!=o or 'vs-conf' in o
open(p,'w',encoding='utf-8').write(s); print('ok')
# round 12b: darker banner (Shaka) — the flat veil 40 % → 56 %
s=open(p,encoding='utf-8').read()
s=s.replace('linear-gradient(180deg,rgba(0,0,0,.4) 0%,rgba(0,0,0,.4) 58%,rgba(7,7,7,.84) 88%,#070707 100%)}','linear-gradient(180deg,rgba(0,0,0,.56) 0%,rgba(0,0,0,.56) 58%,rgba(7,7,7,.88) 88%,#070707 100%)}',1)
open(p,'w',encoding='utf-8').write(s); print('veil ok')
# round 12c: "Round trips" column explained in place; How we tell catches up with the wallet-via-router rule
s=open(p,encoding='utf-8').read()
old='<th className="vs-th">Round trips</th></tr></thead>'
new='<th className="vs-th"><span className="inline-flex items-center">Round trips<InfoTip label="a round trip" className="-my-2 ml-1" glyphClass="text-[11px]" tone="text-white/40 hover:text-white/80">The share of this contract\'s trades that were round trips — one transaction buying the token in one pool and selling it in another, the arbitrage itself. The higher the share, the surer we are it is a bot; a low share means it is counted as a bot only because it calls the pools directly rather than through a router.</InfoTip></span></th></tr></thead>'
if 'label="a round trip"' not in s: assert old in s; s=s.replace(old,new,1)
old2='that is how an unnamed aggregator such as switch.win is recognised. The Round trips column on the bot list shows how sure we are about each one.'
new2='that is how an unnamed aggregator such as switch.win is recognised. One more catch: a wallet that trades through a router 50 or more times a day is a bot driving a router, so its trades count as bots too (listed as "bot wallet via …"). The Round trips column on the bot list shows how sure we are about each one.'
if 'bot wallet via' not in s.split('How we tell')[1][:3000]: assert old2 in s; s=s.replace(old2,new2,1)
open(p,'w',encoding='utf-8').write(s); print('tips ok')
