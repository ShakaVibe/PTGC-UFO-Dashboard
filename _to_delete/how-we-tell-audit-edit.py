# How we tell — the 2026-10-06 audit's exception, one clause. Idempotent.
import sys
p=sys.argv[1] if len(sys.argv)>1 else 'index.html'
s=open(p,encoding='utf-8').read()
old='A transaction that buys the token in one pool and sells it in another — a round trip — is the arbitrage itself and counts as a bot whoever sent it.'
new='A transaction that buys the token in one pool and sells it in another — a round trip — is the arbitrage itself and counts as a bot whoever sent it (unless it came through a router as one person\'s swap: a sale split across pools, or a UFO ↔ PLS swap routed through PTGC, is not a round trip).'
if new not in s:
    assert old in s; s=s.replace(old,new,1)
open(p,'w',encoding='utf-8').write(s); print('how ok')
