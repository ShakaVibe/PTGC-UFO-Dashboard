import sys, re
S='/tmp/claude-0/-home-claude/5494307a-e2bb-55ac-90f7-c87a6acea9b7/scratchpad'
sys.path.insert(0,S)
import io, contextlib
with contextlib.redirect_stdout(io.StringIO()):
    import mock_ranks3 as G
    import mock_single as H
P,U,RP,RU,sub1,med=H.P,H.U,H.RP,H.RU,H.sub1,H.med
def H3one(s,c,x,n):
    row=(f'<div class="rk3 {c}"><div class="l"><span class="k">ALL {n} WALLETS AS ONE</span><b>#{x["r"]:,}</b><small>of {x["n"]:,} · {x["top"]}</small>{med(x,c)}</div>'
         f'<div class="r">▲ <b>{x["ahead"]}</b> more to pass #{x["r"]-1:,}</div></div>')
    return sub1(s,r'(<div class="pf2-lgbf">.*?</div>)',lambda m:m.group(1)+row)
def crop(s):   # cards only down to the League box — the part that changes
    k=s.index('<div class="pf2-ebs">'); return s[:k]+'</section>'
head=open(S+'/repo/design/portfolio/mock-ranks-v3.html').read().split('</style></head>')[0]
head=re.sub(r'<title>.*?</title>','<title>Holder rank — the two choices: G1 vs G2 badges · H3 with 2+ wallets (as one vs hidden) — 2026-10-21</title>',head)
CSS=H.CSS+'''
.pick{display:grid;grid-template-columns:1fr 1fr;gap:26px}
.pick .opt{margin-bottom:8px}
.pf2-tok2.cut .pf2-tk{padding-bottom:4px}
.deck{display:flex;gap:8px;align-items:center;margin:0 0 12px;font:700 13px Rajdhani;color:rgba(255,255,255,.65)}
.deck span{padding:4px 10px;border-radius:999px;border:1px solid rgba(124,252,0,.4);background:rgba(124,252,0,.08);color:#fff}
.h2t{font-family:Orbitron;font-size:17px;letter-spacing:.1em;color:#F6E98A;margin:6px 0 4px}
'''
out=head+CSS+'''</style></head><body><div class="pf2"><div class="wrap">
<h1 style="font-family:Orbitron;font-size:22px;letter-spacing:.08em;color:#F6E98A;margin:0 0 6px">HOLDER RANK — PICK ONE OF EACH</h1>
<div class="note">1 · the badges in the Per-wallet breakdown · 2 · what the League box shows when 2 or more wallets are selected. Real ranks, example wallets.</div>
<div class="sep"></div><div class="h2t">1 · PER-WALLET BREAKDOWN BADGES</div>'''
out+='<div class="opt">G1 — TWO-LINE</div><span class="note">"More to pass" on its own line under the rank — easier to read, taller rows.</span>'+G.optG(False)
out+='<div style="height:26px"></div><div class="opt">G2 — ONE-LINE</div><span class="note">Everything on one line, "more to pass" at the right end — rows stay close to today’s height.</span>'+G.optG(True)
out+='''<div class="sep"></div><div class="h2t">2 · THE LEAGUE BOX WITH 3 WALLETS SELECTED</div>
<div class="deck">Wallets counted: <span>Main</span><span>Cold storage</span><span>Locks</span> — the cards show the three added together</div>'''
out+='<div class="opt">A — RANK AS ONE WALLET</div><span class="note">The line stays and ranks the three wallets added together. With one wallet selected it reads "HOLDER RANK" as in H3.</span>'
out+='<div class="pf2-tok2 cut">'+crop(H3one(P,'p',RP,3))+crop(H3one(U,'u',RU,3))+'</div>'
out+='<div style="height:26px"></div><div class="opt">B — HIDDEN</div><span class="note">No rank line while 2+ wallets are selected — it only appears for a single wallet (the breakdown table still has every wallet’s rank).</span>'
out+='<div class="pf2-tok2 cut">'+crop(P)+crop(U)+'</div>'
out+='</div></div></body></html>'
out=out.replace('src="logos/','src="../../logos/')
open(S+'/repo/design/portfolio/mock-ranks-choices-v1.html','w').write(out); print('written',len(out))
