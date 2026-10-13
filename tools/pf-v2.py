#!/usr/bin/env python3
"""Portfolio v2 (2026-10-13) — Shaka's portfolio redesign, step 1, HIDDEN behind a faint dot.

Design: design/portfolio/mock-portfolio-v4.html (+ README.md, every decision). Edits portfolio.html in place, idempotent
(run it twice: "0 edit(s)"). Run from the repo root:  python3 tools/pf-v2.py

  1. the pf2-* CSS (tools/pf-v2/pf2.css) at the end of the page's <style>
  2. PortfolioV2 + PfV2Dot + helpers (tools/pf-v2/PortfolioV2.jsx) at module scope above PortfolioPage
  3. PortfolioPage: the pfV2 state (PF_V2_LIVE || this device's saved preview) + its toggle
  4. the classic body (address input … per-wallet breakdown) wrapped: pfV2 ? <PortfolioV2/> : classic — the modals stay shared
  5. the faint dot bottom-right (only while PF_V2_LIVE is false); the classic footer only under classic (v2 has its own foot)
Go-live later = PF_V2_LIVE=true in portfolio.html (one constant).
"""
import os, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.join(ROOT, 'tools', 'pf-v2')
F = os.path.join(ROOT, 'portfolio.html')
s = open(F, encoding='utf-8').read()
edits = 0

def once(marker, fn):
    global s, edits
    if marker in s:
        return
    s2 = fn(s)
    if s2 == s or marker not in s2:
        sys.exit(f'pf-v2: anchor not found for {marker!r}')
    s = s2; edits += 1

def rep(old, new, count=1):
    def f(t):
        if t.count(old) != count:
            sys.exit(f'pf-v2: expected {count}x {old[:70]!r}, found {t.count(old)}')
        return t.replace(old, new)
    return f

css = open(os.path.join(HERE, 'pf2.css'), encoding='utf-8').read().rstrip('\n')
jsx = '\n\n'.join(open(os.path.join(HERE, n), encoding='utf-8').read().rstrip('\n') for n in ('PfLeagues.jsx', 'PfHistory.jsx', 'PfTx.jsx', 'PortfolioV2.jsx'))
# round 2: the Leagues window's CSS, taken from index.html each run (one design for both pages)
ix = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
a = ix.index('    .lg-m{'); b = ix.index('    /* the combined card (Socials', a)
css += ('\n    /* ---- the Leagues window (lg-*), copied from index.html by tools/pf-v2.py — edit it THERE, then re-run ---- */\n'
        + ix[a:b].rstrip('\n'))

CSS_A, CSS_B = '    /* ===== Portfolio v2 (2026-10-13, design', '\n  </style>\n</head>'
JSX_A, JSX_B = '    /* Portfolio v2, round 2 (2026-10-13): the Leagues window', '\n\n    const PortfolioPage=({onBack})=>{'
JSX_A0 = '    /* ===== PORTFOLIO v2 (2026-10-13)'   # step-1 builds started the block here

def sync(start_markers, end, block, what):
    """Insert the block before `end`, or replace what an earlier run inserted (so edits to tools/pf-v2/* flow in)."""
    global s, edits
    starts = [s.find(m) for m in start_markers if s.find(m) >= 0]
    if starts:
        i = min(starts); j = s.index(end, i)
        if s[i:j] != block:
            s = s[:i] + block + s[j:]; edits += 1
    else:
        anchor = '\n  </style>\n</head>' if what == 'css' else '    const PortfolioPage=({onBack})=>{'
        new = ('\n' + block + anchor) if what == 'css' else (block + '\n\n' + anchor)
        if s.count(anchor) != 1: sys.exit(f'pf-v2: anchor for {what} not found')
        s = s.replace(anchor, new); edits += 1

# 1. CSS  2. the components (Leagues window + PortfolioV2)
sync([CSS_A], CSS_B, css, 'css')
sync([JSX_A, JSX_A0], JSX_B, jsx, 'jsx')

# 3. state + toggle
once('const[pfV2,setPfV2]', rep(
    "      const[showUfoLeagues,setShowUfoLeagues]=useState(false);\n",
    "      const[showUfoLeagues,setShowUfoLeagues]=useState(false);\n"
    "      const[pfV2,setPfV2]=useState(()=>PF_V2_LIVE||pfV2Saved());   // Portfolio v2 (2026-10-13): hidden preview, see PortfolioV2\n"
    "      const togglePfV2=()=>setPfV2(v=>{const n=!v;try{n?localStorage.setItem(LS_PF_V2,'1'):localStorage.removeItem(LS_PF_V2);}catch(e){}try{window.scrollTo(0,0);}catch(e){}return n;});\n"))

# 4. wrap the classic body
PROPS = ('wallets={wallets} portfolioData={portfolioData} loadingAddrs={loadingAddrs} scanningAddr={scanningAddr} agg={agg} dp={dp} '
         'prices={prices} changes={changes} groups={groups} isWalletChecked={isWalletChecked} toggleWallet={toggleWallet} '
         'selectAllWallets={selectAllWallets} deselectAllWallets={deselectAllWallets} removeWallet={removeWallet} '
         'fetchWalletData={fetchWalletData} retryFailedReflScans={retryFailedReflScans} truncAddr={truncAddr} initialLoad={initialLoad} '
         'inputAddr={inputAddr} setInputAddr={setInputAddr} inputName={inputName} setInputName={setInputName} '
         'inputGroup={inputGroup} setInputGroup={setInputGroup} newGroupName={newGroupName} setNewGroupName={setNewGroupName} addWallet={addWallet} '
         'setEditingWallet={setEditingWallet} setEditWalletName={setEditWalletName} setShowPtgcLeagues={setShowPtgcLeagues} setShowUfoLeagues={setShowUfoLeagues} '
         'moonMathActive={moonMathActive} setMoonMathActive={setMoonMathActive} customPrices={customPrices} setCustomPrices={setCustomPrices} ATH_PRICES={ATH_PRICES}')
def wrap(t):
    a = '          {/* Address Input + Moon Math side by side */}\n'
    b = '          {/* Get Code Modal */}\n'
    if t.count(a) != 1 or t.count(b) != 1:
        sys.exit('pf-v2: classic body anchors not found')
    i, j = t.index(a), t.index(b)
    body = t[i:j]
    return (t[:i] + '          {/* Portfolio v2 (2026-10-13): the new body behind the faint dot; the classic body below is untouched */}\n'
            + '          {pfV2?<PortfolioV2 ' + PROPS + '/>:(<>\n' + body + '          </>)}\n          \n' + t[j:])
once('{pfV2?<PortfolioV2 ', wrap)

# 6. round 2: updateWallet (edit a wallet's name + group from the v2 Edit window)
once('const updateWalletV2=', rep(
    "      const togglePfV2=",
    "      const updateWalletV2=(addr,patch)=>setWallets(prev=>prev.map(w=>w.address.toLowerCase()===addr?{...w,...patch}:w));   // Portfolio v2 round 2: the Edit window\n"
    "      const togglePfV2="))
once('<PortfolioV2 updateWallet=', rep('{pfV2?<PortfolioV2 ', '{pfV2?<PortfolioV2 updateWallet={updateWalletV2} '))

# 7. round 6: what the safe reflection yield needs — the PTGC "received" total (already read; now kept on the wallet's data)
#    and the UFO received total the reflections scan computes (stashed per address in window.pfUfoRecv). The classic page
#    renders neither, so its output is unchanged.
once('received:tRecv,', rep(
    "          lifetimeEarned:uiClaimed+uiLockClaimed,\n",
    "          lifetimeEarned:uiClaimed+uiLockClaimed,\n          received:tRecv,   // Portfolio v2 round 6: the reflection-yield denominator\n"))
once('(window.pfUfoRecv=window.pfUfoRecv||{})', rep(
    "      const reflWei=balanceWei-(inWei-outWei);\n",
    "      try{(window.pfUfoRecv=window.pfUfoRecv||{})[address.toLowerCase()]=toNum(inWei);}catch(e){}   // Portfolio v2 round 6: yield denominator\n"
    "      const reflWei=balanceWei-(inWei-outWei);\n"))

# 5. the dot + classic-only footer
once('<PfV2Dot ', rep(
    '          {/* Footer */}\n          <footer className="text-center py-6 border-t border-white/10 mt-4">',
    '          {!PF_V2_LIVE&&<PfV2Dot on={pfV2} toggle={togglePfV2}/>}\n'
    '          {/* Footer */}\n          {!pfV2&&<footer className="text-center py-6 border-t border-white/10 mt-4">'))
once('</footer>}', rep(
    '            <p className="text-white/25 text-sm mt-1">Your portfolio is saved locally in your browser.</p>\n          </footer>',
    '            <p className="text-white/25 text-sm mt-1">Your portfolio is saved locally in your browser.</p>\n          </footer>}'))

if edits:
    open(F, 'w', encoding='utf-8').write(s)
print(f'pf-v2: {edits} edit(s); portfolio.html sha256 {hashlib.sha256(s.encode()).hexdigest()[:8]}…')
