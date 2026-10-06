# Humans vs Bots round 14 (2026-10-06, Shaka): no round-trip data anywhere — the "N round trips ⓘ" on the Arb Bots card goes. Idempotent.
import re,sys
p=sys.argv[1] if len(sys.argv)>1 else 'index.html'
s=open(p,encoding='utf-8').read()
s2=re.sub(r"\{view\.arb\.txs>0&&<> \{'\\u00b7'\} <b className=\"text-white\">\{fmt\(view\.arb\.txs\)\}</b> round trip.*?</InfoTip></>\}</div>","</div>",s,count=1,flags=re.S)
assert s2!=s or 'round trip{view' not in s
open(p,'w',encoding='utf-8').write(s2); print('ok')
