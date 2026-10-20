#!/usr/bin/env python3
"""Portfolio v2 CLEANUP round (2026-10-20) — v2 has been the only page anyone sees since 2026-10-16 (`bc8e60b8b`).
Idempotent, run from the repo root:   python3 tools/pf-cleanup.py   then   python3 tools/pf-v2.py   (twice: "0 edit(s)")

  1. tools/pf-v2/PortfolioV2.jsx: PF_V2_LIVE, LS_PF_V2, pfV2Saved and PfV2Dot gone; a device that still carries the old
     preview flag (localStorage grays_pf_v2_preview) has it removed once
  2. tools/pf-v2/pf2.css: the dot's .pf2-dotbtn rules gone
  3. portfolio.html: `{pfV2?<PortfolioV2 …/>:(<> classic body </>)}` → `<PortfolioV2 …/>` (the classic body — address input,
     Moon Math, cards, per-wallet breakdown, ~570 lines — is deleted); the pfV2 state + togglePfV2, the dot and the classic
     footer (v2 prints its own .pf2-foot) are gone. The shared modals (Get Code / Load Code / Edit wallet / Leagues) stay.
  5. the classic-only leftovers: ptgcDonut(+Colors), formatLockTime, dataLoaded, showWalletBreakdown, fmtComma, UFO_TOTAL_SUPPLY
  4. tools/pf-v2.py is rewritten by hand alongside this script: steps 3–5 and the PF_V2_LIVE guard were dead.
Nothing visible changes: the harness renders the same #root markup before and after (sessions/2026-10-20.md).
"""
import os, sys, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(ROOT, *a)
total = 0

class Edit:
    def __init__(self, path):
        self.path = path; self.s = open(path, encoding='utf-8').read(); self.n = 0
    def rep(self, old, new, gone_marker=None):
        """old → new once; skipped when `gone_marker` (default: old) is already absent."""
        if (gone_marker or old) not in self.s: return
        assert self.s.count(old) == 1, f'{self.path}: expected 1x anchor, found {self.s.count(old)}: {old[:80]!r}'
        self.s = self.s.replace(old, new); self.n += 1
    def save(self):
        global total
        if self.n: open(self.path, 'w', encoding='utf-8').write(self.s)
        total += self.n
        print(f'{os.path.relpath(self.path, ROOT)}: {self.n} edit(s), sha256 {hashlib.sha256(self.s.encode()).hexdigest()[:8]}')

# 1 — the v2 source
j = Edit(P('tools', 'pf-v2', 'PortfolioV2.jsx'))
j.rep("""       (TOKENS, fmtDollar, usd, agg / dp / prices / portfolioData passed in as props, PF_V2_LIVE…). */
    /* ===== PORTFOLIO v2 (2026-10-13) — the page body of design/portfolio/mock-portfolio-v4.html, built by tools/pf-v2.py =====
       HIDDEN: PF_V2_LIVE=false → the classic body stays the default and a faint dot bottom-right (PfV2Dot) flips this device
       to v2 and back (localStorage LS_PF_V2). Go-live = PF_V2_LIVE=true (the dot goes, v2 for everyone).
       Same state, same loaders, same maths as the classic body (agg, dp, getHoldingCreatures, LEAGUE_TIERS) — only the look
       is new. Step 2 (not built yet): the value history from real chain balances and Recent Transactions (placeholders below). */
    const PF_V2_LIVE=true;    // GO-LIVE 2026-10-16: Portfolio v2 for everyone (the dot is gone)
    const LS_PF_V2='grays_pf_v2_preview';
    const pfV2Saved=()=>{try{return localStorage.getItem(LS_PF_V2)==='1'}catch(e){return false}};
""", """       (TOKENS, fmtDollar, usd, agg / dp / prices / portfolioData passed in as props). */
    /* ===== PORTFOLIO v2 (2026-10-13) — the page body of design/portfolio/mock-portfolio-v4.html, built by tools/pf-v2.py =====
       LIVE for everyone since 2026-10-16; the classic body, the preview dot and PF_V2_LIVE were removed 2026-10-20
       (tools/pf-cleanup.py). Same state, same loaders, same maths as the classic page had (agg, dp, getHoldingCreatures,
       LEAGUE_TIERS) — PortfolioPage owns the state and passes it in. */
    try{localStorage.removeItem('grays_pf_v2_preview');}catch(e){}   // 2026-10-20: the old preview-dot flag, now meaningless
""", gone_marker='const PF_V2_LIVE=')
j.rep("""    const PfV2Dot=({on,toggle})=>(
      <button className="pf2-dotbtn" onClick={toggle} aria-label={on?'Back to the current portfolio page':'Preview the new portfolio page'} title={on?'Back to the current page':'Preview'}></button>
    );
""", "")
j.save()

# 2 — the dot's CSS
c = Edit(P('tools', 'pf-v2', 'pf2.css'))
c.rep("    /* ===== Portfolio v2 (2026-10-13, design/portfolio/mock-portfolio-v4.html) — hidden behind the faint dot until PF_V2_LIVE ===== */",
      "    /* ===== Portfolio v2 (2026-10-13, design/portfolio/mock-portfolio-v4.html) — live since 2026-10-16, the only body since 2026-10-20 ===== */")
c.rep("""    .pf2-dotbtn{position:fixed;right:10px;bottom:10px;z-index:70;width:12px;height:12px;border-radius:50%;border:0;padding:0;background:rgba(255,255,255,.14);opacity:.5;cursor:pointer}
    .pf2-dotbtn:hover{opacity:1;background:rgba(242,211,91,.6)}
""", "")
c.save()

# 3 — the page
h = Edit(P('portfolio.html'))
h.rep("""      const[pfV2,setPfV2]=useState(()=>PF_V2_LIVE||pfV2Saved());   // Portfolio v2 (2026-10-13): hidden preview, see PortfolioV2
""", "")
h.rep("""      const togglePfV2=()=>setPfV2(v=>{const n=!v;try{n?localStorage.setItem(LS_PF_V2,'1'):localStorage.removeItem(LS_PF_V2);}catch(e){}try{window.scrollTo(0,0);}catch(e){}return n;});
""", "")
A = '          {/* Portfolio v2 (2026-10-13): the new body behind the faint dot; the classic body below is untouched */}\n          {pfV2?<PortfolioV2 '
B = '          </>)}\n          \n          {/* Get Code Modal */}\n'
if A in h.s:
    assert h.s.count(A) == 1 and h.s.count(B) == 1, 'portfolio.html: classic body anchors drifted'
    i = h.s.index(A); k = h.s.index('/>:(<>\n', i); jx = h.s.index(B, k)
    props = h.s[i + len(A):k]
    assert '\n' not in props, 'portfolio.html: the PortfolioV2 props line is not one line'
    h.s = (h.s[:i] + '          {/* Portfolio v2 — the page body (tools/pf-v2.py); the classic body was removed 2026-10-20 (tools/pf-cleanup.py) */}\n'
           + '          <PortfolioV2 ' + props + '/>\n          \n          {/* Get Code Modal */}\n' + h.s[jx + len(B):])
    h.n += 1
h.rep("""          {!PF_V2_LIVE&&<PfV2Dot on={pfV2} toggle={togglePfV2}/>}
          {/* Footer */}
          {!pfV2&&<footer className="text-center py-6 border-t border-white/10 mt-4">
            <p className="text-white/30 text-sm">Portfolio data is read directly from the PulseChain blockchain. Not financial advice.</p>
            <p className="text-white/25 text-sm mt-1">Your portfolio is saved locally in your browser.</p>
          </footer>}
""", "")
# 5 — what only the classic body used (found by a declared-but-never-read scan after step 3)
h.rep("""    const UFO_TOTAL_SUPPLY=999999999051; // _tTotal from the contract (human units, 18 decimals)
""", "")
h.rep("""    const fmtComma=(n,dec=2)=>n==null||isNaN(n)?'\\u2014':Number(n).toLocaleString('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec});
""", "")
h.rep("""      const[showWalletBreakdown,setShowWalletBreakdown]=useState(false);
""", "")
h.rep("""      const dataLoaded=Object.keys(portfolioData).length>0;
""", "")
h.rep("""      // PTGC Donut data (non-overlapping segments)
      const ptgcDonut=[
        {label:'Liquid',value:agg.ptgc.walletFree},
        {label:'Staked (not locked)',value:agg.ptgc.stakedOnly},
        {label:'Locked & Staked',value:agg.ptgc.locked},
      ].filter(d=>d.value>0);
      const ptgcDonutColors=['#D9CA5D','#a855f7','#ec4899'];
      
      const formatLockTime=(endTime)=>{
        if(!endTime)return'—';
        const now=Date.now()/1000;
        if(endTime<=now)return'Unlockable';
        const diff=endTime-now;
        const days=Math.floor(diff/86400);
        if(days>365)return Math.floor(days/365)+'y '+Math.floor((days%365)/30)+'m';
        if(days>30)return Math.floor(days/30)+'m '+days%30+'d';
        return days+'d';
      };
      
""", "")
h.save()
print(f'pf-cleanup: {total} edit(s) in all — now run python3 tools/pf-v2.py (twice)')
