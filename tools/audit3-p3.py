#!/usr/bin/env python3
"""Audit III, batch 3 (2026-10-07): navigation + taps — c9, c31, c28, c29. Idempotent — run from the repo root on both copies:
    python3 tools/audit3-p3.py
Each edit asserts its anchor exists exactly once (or is already applied) so a drifted file fails loudly instead of half-applying.
  c9  three Back buttons: Calculators' ← lands on the dashboard (was Home); Affiliates' Back remembers the token it came from
      (the sibling-page handoff, else the last dashboard visited); Ledger's Back only uses history.back() for an on-site arrival
  c31 switching tabs on the v2 band scrolls back up to the band when the visitor had scrolled past it (KPI Report no longer opens
      at its own foot)
  c28 tap targets: a `.hit` rule (an invisible 32×32 hit box centred on a small control — the glyph does not move) on the header
      ⓘ triggers, the tile badges, the sibling pages' ← and copy, the LP table's three icons, the window pills, All / RH Cores,
      CopyBtn and the charts presets; `.tap` / `.tap-h` and the u9 focus ring move from index.html into h2.css so the sibling pages
      get them; the jsx mirror gets the 24h-change `title`
  c29 reduced motion: the `.h2-*` guard moves from index.html into h2.css (the sibling pages shimmered for "Reduce motion" users),
      the three sibling pages get their own guard; the calculators' and portfolio's `focus:outline-none` inputs get a visible
      :focus-visible ring (`focus-visible:outline-white/60`)
  +   h2.css / h2-header.jsx ?v=2 → ?v=3 on the pages that load them (gotcha 36 — both changed here)
"""
import sys, re, hashlib

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)
def md5(s): return hashlib.md5(s.encode('utf-8')).hexdigest()

class Edit:
    def __init__(self, path):
        self.path = path; self.s = read(path); self.n = 0
    def rep(self, old, new, count=1, done_marker=None):
        """Replace `old` → `new` exactly `count` times; skip silently when `done_marker` (default: new) is already present."""
        if done_marker is not None:
            if done_marker in self.s: return False
        elif new in self.s and old not in self.s:
            return False
        c = self.s.count(old)
        assert c == count, f'{self.path}: expected {count}× anchor, found {c}: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def rep_all(self, old, new, done_marker):
        """Replace every `old` → `new`; skip when `done_marker` is already present."""
        if done_marker in self.s: return False
        assert old in self.s, f'{self.path}: anchor missing: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def save(self):
        write(self.path, self.s); print(f'{self.path}: {self.n} edit(s), md5 {md5(self.s)}')

HIT = '.hit{position:relative}.hit::before{content:"";position:absolute;left:50%;top:50%;width:max(100%,32px);height:max(100%,32px);transform:translate(-50%,-50%)}'

# ================================================================= h2.css — the shared rules (c28, c29)
h2 = Edit('h2.css')
h2.rep("""/* --- tab row (sticky) --- */""",
       """/* --- tap targets + focus (Audit III c28 / c29, 2026-10-07 — moved here from index.html so calculators / charts / portfolio get them) ---
   u8: a thumb-sized hit area for the small icon controls; the glyph stays its size, only the tappable box grows to 32 px.
   .hit = the same idea for controls whose layout must not move (tile badges, the LP icons, pills): an invisible 32×32 box centred on it. */
.tap{min-width:32px;min-height:32px;display:inline-flex;align-items:center;justify-content:center}
.tap-h{min-height:32px;display:inline-flex;align-items:center}
""" + HIT + """
.h2-back,.h2 .h2-addr button,.h2-tile .h2-tb>button,.h2-tile .h2-tb>a{position:relative}
.h2-tile .h2-tb{z-index:1}   /* the badge row paints above the tile's absolute value line (which came later in the DOM and swallowed the badges' lower pixels) */
.h2-back::before,.h2 .h2-addr button::before{content:"";position:absolute;left:50%;top:50%;width:max(100%,32px);height:max(100%,32px);transform:translate(-50%,-50%)}
.h2-tile .h2-tb>button::before,.h2-tile .h2-tb>a::before{content:"";position:absolute;left:50%;top:50%;width:calc(100% + 6px);height:max(100%,32px);transform:translate(-50%,-50%)}   /* the badges sit ~6 px apart: 3 px each side is all a hit box can take without stealing the neighbour's taps (a real 32 needs wider spacing — a design call) */
/* u7: focus ring for the explainer buttons and popover (keyboard users), not on tap. */
.tap:focus-visible,.tap-h:focus-visible{outline:2px solid rgba(255,255,255,0.6);outline-offset:2px;border-radius:6px}
/* u9: the same ring on every control a keyboard can reach. :focus-visible only — a tap or click never shows it. Dialog containers take programmatic focus and are excluded. */
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,[tabindex]:not([role="dialog"]):focus-visible{outline:2px solid rgba(255,255,255,0.6);outline-offset:2px}
/* the tab strips clip vertically (overflow-y-hidden), so their ring sits inside the box */
nav button:focus-visible,nav a:focus-visible{outline-offset:-2px;border-radius:6px}
/* c29: "Reduce motion" — the BUY shimmer, the switch hover and the skeleton pulse stop on every page that loads this file */
@media(prefers-reduced-motion:reduce){.h2 .h2-buy::after{animation:none}.h2 .h2-buy,.h2 .h2-sw{transition:none}.h2 .h2-buy:hover,.h2 .h2-sw:hover{transform:none}.h2-tile .h2-sk{animation:none}}

/* --- tab row (sticky) --- */""", done_marker='.hit{position:relative}')
h2.save()

# ================================================================= index.html
ix = Edit('index.html')

# c28 / c29 — the rules now live in h2.css (loaded on every page but the ledger); a pointer stays
ix.rep("""    /* u8: a thumb-sized hit area for the small icon controls (ⓘ, 📷, USD/TOK, sort, the RH
       switch). The glyph stays the size it was; only the tappable box grows to 32px. */
    .tap{min-width:32px;min-height:32px;display:inline-flex;align-items:center;justify-content:center}
    .tap-h{min-height:32px;display:inline-flex;align-items:center}
    /* u7: focus ring for the explainer buttons and popover (keyboard users), not on tap. */
    .tap:focus-visible,.tap-h:focus-visible{outline:2px solid rgba(255,255,255,0.6);outline-offset:2px;border-radius:6px}
    /* u9: the same ring on every control a keyboard can reach. :focus-visible only — a tap or
       click never shows it. Dialog containers take programmatic focus and are excluded. */
    button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,
    [tabindex]:not([role="dialog"]):focus-visible{outline:2px solid rgba(255,255,255,0.6);outline-offset:2px}
    /* the tab strips clip vertically (overflow-y-hidden), so their ring sits inside the box */
    nav button:focus-visible,nav a:focus-visible{outline-offset:-2px;border-radius:6px}""",
       """    /* u8 `.tap` / `.tap-h`, the u7 / u9 focus rings and the c28 `.hit` box live in h2.css since 2026-10-07 (Audit III c28 / c29) —
       shared with the sibling pages. Edit them there. */""")
ix.rep("""    @media(prefers-reduced-motion:reduce){.h2 .h2-buy::after{animation:none}.h2 .h2-buy,.h2 .h2-sw{transition:none}.h2 .h2-buy:hover,.h2 .h2-sw:hover{transform:none}.h2-tile .h2-sk{animation:none}}
""", """    /* the .h2-* reduced-motion guard moved to h2.css (c29, 2026-10-07) */
""")
# c28 — hit boxes on the LP table icons (26 px), the Holders / Volume / RH window pills (22 px) and All / RH Cores (24 px)
ix.rep("""    .p2-lpac .info{color:#8FC6FF}.p2-lpac .chart{color:#F3C64C}.p2-lpac .tools{color:#6FE3DC}""",
       """    .p2-lpac a,.p2-lpac button{position:relative}.p2-lpac a::before,.p2-lpac button::before,.nh-tg>button::before,.p2-lphtg>button::before{content:"";position:absolute;left:50%;top:50%;width:max(100%,32px);height:max(100%,32px);transform:translate(-50%,-50%)}   /* c28 (Audit III): 32 px hit boxes, the glyphs unchanged */
    .nh-tg>button,.p2-lphtg>button{position:relative}
    .p2-lpac .info{color:#8FC6FF}.p2-lpac .chart{color:#F3C64C}.p2-lpac .tools{color:#6FE3DC}""", done_marker='c28 (Audit III): 32 px hit boxes')
# the InfoTip with a custom trigger (the header ⓘ: 18 px on desktop, 13 px on phones) and CopyBtn (14 px)
ix.rep("""                  className={trigger?`tap-h rounded-full ${className}`:`tap -my-2 -mx-1 rounded-md transition-colors ${tone} ${className}`}>""",
       """                  className={trigger?`tap-h hit rounded-full ${className}`:`tap -my-2 -mx-1 rounded-md transition-colors ${tone} ${className}`}>""")
ix.rep("""          className={`${className} transition inline-flex items-center`}
          title="Copy"
        >""",
       """          className={`${className} hit transition inline-flex items-center`}
          title="Copy"
        >""")

# c31 — a tab switch scrolls back up to the band when the visitor had scrolled past it
ix.rep("""      const gotoTab=(t)=>{setActiveTab(t);if(onTabRoute&&['dashboard','kpi','social'].includes(t))onTabRoute(t);};""",
       """      const gotoTab=(t)=>{setActiveTab(t);if(onTabRoute&&['dashboard','kpi','social'].includes(t))onTabRoute(t);
        /* c31 (Audit III): the new tab keeps the old scroll offset, so KPI Report tapped from the dashboard's foot opened at its
           own foot. When the sticky band is stuck (the banner scrolled away), scroll to where it sticks — the tab's top. */
        const band=document.querySelector('.h2-tabs'),prev=band&&band.previousElementSibling;
        if(prev){const y=Math.round(prev.getBoundingClientRect().bottom+window.scrollY);if(window.scrollY>y)window.scrollTo({top:y});}};""", done_marker='c31 (Audit III): the new tab keeps')

# c9 — Affiliates' Back: remember the token the visitor came from (the sibling-page handoff), else the last dashboard visited
ix.rep("""          if(lsTake(LS.HANDOFF_VIEW)==='affiliates')target={view:'affiliates',token:null,tab:'dashboard'};""",
       """          if(lsTake(LS.HANDOFF_VIEW)==='affiliates'){target={view:'affiliates',token:null,tab:'dashboard'};_affFrom=p;}   // c9: the page's Affiliates tab remembers its token""")
ix.rep("""    let _bootOpen=null;const takeBootOpen=()=>{const v=_bootOpen;_bootOpen=null;return v;};""",
       """    let _bootOpen=null;const takeBootOpen=()=>{const v=_bootOpen;_bootOpen=null;return v;};
    let _affFrom=null;   // c9 (Audit III): the token a sibling page handed over with the Affiliates view, so its Back returns there""", done_marker='let _affFrom=null;')
ix.rep("""      const[lastToken,setLastToken]=useState(null);""",
       """      const[lastToken,setLastToken]=useState(()=>{   // c9: the handoff token, else the last dashboard this browser visited, else null (→ Home)
        if(_affFrom==='PTGC'||_affFrom==='UFO')return _affFrom;
        try{const t=localStorage.getItem(LS.HANDOFF_TOKEN);return (t==='PTGC'||t==='UFO')?t:null;}catch(e){return null;}
      });""")
ix.rep('h2.css?v=2', 'h2.css?v=3')   # gotcha 36: both shared files changed in this batch
ix.save()

# ================================================================= h2-header.jsx — the change line's title (C-10 mirror drift)
jx = Edit('h2-header.jsx')
jx.rep("""  const chgTxt=changeKnown?`${priceUp?'+':'−'}${Math.abs(data.change).toFixed(2)}%`:'—';""",
       """  const chgTxt=changeKnown?`${priceUp?'+':'−'}${Math.abs(data.change).toFixed(2)}%`:'—';
  const chgTip=changeKnown?undefined:'24h change unavailable — DexScreener did not answer; the price is read from the pool.';   // c28: the dashboard's tooltip, mirrored""", done_marker="c28: the dashboard's tooltip, mirrored")
jx.rep("""    <div className={`h2-chg tn ${chgCls}`}>{loading?""", """    <div className={`h2-chg tn ${chgCls}`} title={chgTip}>{loading?""")
jx.rep("""<span className={`h2-mchg tn ${chgCls}`}>{chgTxt}</span>""", """<span className={`h2-mchg tn ${chgCls}`} title={chgTip}>{chgTxt}</span>""")
jx.save()

# ================================================================= calculators.html
ca = Edit('calculators.html')
# c9 — ← to the dashboard, not Home
ca.rep("""      const goBack=()=>{
        try{localStorage.setItem('ptgc_last_token',token)}catch(e){}
        window.location.href='./index.html';
      };""",
       """      const goBack=()=>navTo('dashboard');   // c9 (Audit III): the dashboard this page came from, not Home (navTo writes the handoff key)""")
# c29 — reduced motion + a visible focus ring on the inputs
ca.rep("""    .animate-grow-btn{animation:growBtnPulse 2.5s ease-in-out infinite}""",
       """    .animate-grow-btn{animation:growBtnPulse 2.5s ease-in-out infinite}
    @media(prefers-reduced-motion:reduce){.animate-fire,.animate-pulse-slow,.animate-grow-btn,.buy-btn::after{animation:none}.buy-btn{transition:none}.buy-btn:hover{transform:none}}   /* c29 (Audit III) */""", done_marker='.animate-grow-btn,.buy-btn::after{animation:none}')
ca.rep_all("focus:outline-none", "focus:outline-none focus-visible:outline-white/60", done_marker="focus-visible:outline-white/60")
ca.rep('h2.css?v=2', 'h2.css?v=3'); ca.rep('h2-header.jsx?v=2', 'h2-header.jsx?v=3')
ca.save()

# ================================================================= portfolio.html
pf = Edit('portfolio.html')
pf.rep("""    .animate-pulse-slow{animation:pulse 1.5s ease-in-out infinite}
    /* v2 header, the portfolio-only pieces""",
       """    .animate-pulse-slow{animation:pulse 1.5s ease-in-out infinite}
    @media(prefers-reduced-motion:reduce){.animate-pulse-slow{animation:none}}   /* c29 (Audit III) */
    /* v2 header, the portfolio-only pieces""")
pf.rep_all("focus:outline-none", "focus:outline-none focus-visible:outline-white/60", done_marker="focus-visible:outline-white/60")
pf.rep('h2.css?v=2', 'h2.css?v=3'); pf.rep('h2-header.jsx?v=2', 'h2-header.jsx?v=3')
pf.save()

# ================================================================= charts.html
ch = Edit('charts.html')
ch.rep("""  .buy-btn:hover{transform:scale(1.05);filter:brightness(1.15)}
  .metallic-gold""",
       """  .buy-btn:hover{transform:scale(1.05);filter:brightness(1.15)}
  @media(prefers-reduced-motion:reduce){.buy-btn::after{animation:none}.buy-btn{transition:none}.buy-btn:hover{transform:none}}   /* c29 (Audit III) */
  .metallic-gold""", done_marker='.buy-btn::after{animation:none}.buy-btn{transition:none}')
# c28 — the 22 px preset pills
ch.rep("""  .preset-btn{padding:3px 9px;""", """  .preset-btn{position:relative}.preset-btn::before{content:"";position:absolute;left:50%;top:50%;width:max(100%,32px);height:max(100%,32px);transform:translate(-50%,-50%)}   /* c28 (Audit III): 32 px hit box */
  .preset-btn{padding:3px 9px;""", done_marker='.preset-btn{position:relative}')
ch.rep('h2.css?v=2', 'h2.css?v=3')
ch.save()

# ================================================================= ledger.html — c9: history.back() only for an on-site arrival
le = Edit('ledger.html')
le.rep("""onClick={(e) => { e.preventDefault(); if(window.history.length>1){window.history.back()}else{window.location.href='index.html?token=PTGC'} }}""",
       """onClick={(e) => { e.preventDefault(); const onSite=(()=>{try{return document.referrer.indexOf(window.location.origin)===0;}catch(x){return false;}})(); if(window.history.length>1&&onSite){window.history.back()}else{window.location.href='index.html?token=PTGC'} }}   /* c9 (Audit III): an external arrival (a pasted link) would have left the site */""")
le.save()
print('audit3-p3: done')
