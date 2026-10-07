#!/usr/bin/env python3
"""Audit III, batch 6 (2026-10-07 evening): c30 — the phone / tablet list — plus two honesty follow-ups found live during the
DexScreener outage. Idempotent — run from the repo root:
    python3 tools/audit3-p6.py
  M-11 (URGENT since c13): `.lg-m{overflow:hidden}` beat the panel's Tailwind `overflow-y-auto` once tw.css moved ahead of the
       inline <style> — the Leagues window could not scroll on phones. Now `overflow:hidden auto` in the rule itself.
  M-4  KPI card < 640: the Value Gen "7D" tag sat on the ⓘ (the right:34px rule was overridden by a later rule of equal
       specificity) — the tag rule moves below it.
  M-8  Live Feed 641–1040 px: the 1,040-px tape scrolled sideways with no cue — a right-edge fade on the wrapper in that range.
  M-9  Live Feed < 640: the TOP POOLS ticker was pushed off-screen — the HUD row wraps, the ticker takes its own line.
  M-10 phone LP cards: the four pool-logo <img>s get alt="" (decorative), the fallback initials aria-hidden.
  M-12 contrast (colour only, no size changes): deck contact link /35 → /55, affiliates tx links /40 → /70, charts preset
       buttons .3 → .55, the calculators' "Enter an amount…" /20 → /45.
  M-13 ledger phone: the summary heading and the count wrap instead of running together.
  M-16 calculators phone: the three Current Market Prices / Moon Math / 10 Yr strips go one column under 640 (`grid-cols-1
       sm:grid-cols-3`, `text-2xl sm:text-3xl`).
  +    the Liquidity tile says "chain · core pools" under the figure when DexScreener is out and the sum is the six pinned pools
       read on chain (seen live 20:05 UTC: $648K shown as if whole, the real figure ~$980K).
  +    calculators 10 Yr Projection: Market Cap "—" instead of "$0" when fetchDex has no cap (c23's null-through).
"""
import sys, re, hashlib

def read(p): return open(p, encoding='utf-8').read()
def write(p, s): open(p, 'w', encoding='utf-8').write(s)
def md5(s): return hashlib.md5(s.encode('utf-8')).hexdigest()

class Edit:
    def __init__(self, path):
        self.path = path; self.s = read(path); self.n = 0
    def rep(self, old, new, count=1, done_marker=None):
        if done_marker is not None:
            if done_marker in self.s: return False
        elif new in self.s and old not in self.s:
            return False
        c = self.s.count(old)
        assert c == count, f'{self.path}: expected {count}× anchor, found {c}: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def rep_all(self, old, new, done_marker):
        if done_marker in self.s: return False
        assert old in self.s, f'{self.path}: anchor missing: {old[:90]!r}'
        self.s = self.s.replace(old, new); self.n += 1; return True
    def save(self):
        write(self.path, self.s); print(f'{self.path}: {self.n} edit(s), md5 {md5(self.s)}')

ix = Edit('index.html')

# M-11 — the Leagues window scrolls again
ix.rep("""border:2px solid var(--a);background:#06070a;overflow:hidden;position:relativ""",
       """border:2px solid var(--a);background:#06070a;overflow:hidden auto;position:relativ""")   # c30 / M-11: tw.css sits before this <style> since c13, so the inline rule wins — scroll must be here

# M-4 — the KPI tag rule after the rule that overrode it
ix.rep("""      .kp .kp-t .r1 .kp-chip.tag{right:34px;bottom:11px;height:20px;font-size:9.5px;padding:0 6px;margin:0}   /* left of the ⓘ, bottom-right */
      .kp .kp-t .r1 .sp{display:none}
      .kp .kp-t .r1 .kp-chg,.kp .kp-t .r1 .kp-info,.kp .kp-t .r1 .kp-chip.tag{grid-area:1/1/-1/-1;position:absolute;right:10px;bottom:12px}""",
       """      .kp .kp-t .r1 .sp{display:none}
      .kp .kp-t .r1 .kp-chg,.kp .kp-t .r1 .kp-info,.kp .kp-t .r1 .kp-chip.tag{grid-area:1/1/-1/-1;position:absolute;right:10px;bottom:12px}
      .kp .kp-t .r1 .kp-chip.tag{right:34px;bottom:11px;height:20px;font-size:9.5px;padding:0 6px;margin:0}   /* left of the ⓘ, bottom-right — AFTER the rule above (same specificity; c30 / M-4: it used to lose and sit on the ⓘ) */""")

# M-8 — a fade cue on the tape wrapper between the phone layout and the tape's own width
ix.rep("""            @media(max-width:640px){
              /* phone: the boxes are a strip across the top of the art""",
       """            @media(min-width:641px) and (max-width:1060px){.deck-tapewrap::after{content:"";position:absolute;top:0;right:0;bottom:0;width:56px;pointer-events:none;background:linear-gradient(to left,rgba(4,6,10,.92),rgba(4,6,10,0))}}   /* c30 / M-8: tablets scroll the 1,040-px tape sideways — say so */
            @media(max-width:640px){
              /* phone: the boxes are a strip across the top of the art""", done_marker='.deck-tapewrap::after')
ix.rep("""              <div className="relative overflow-x-auto">
                <div className="deck-tape" style={{minWidth:1040}}>""",
       """              <div className="relative overflow-x-auto deck-tapewrap">
                <div className="deck-tape" style={{minWidth:1040}}>""")

# M-9 — the HUD row wraps on phones; the ticker takes its own line
ix.rep("""              <div className="relative flex items-center gap-4 px-4 py-2.5 whitespace-nowrap overflow-x-auto" style={{borderBottom:`1px solid ${deckHexA(ac,0.18)}`}}>""",
       """              <div className="relative flex flex-wrap sm:flex-nowrap items-center gap-x-4 gap-y-1.5 px-4 py-2.5 whitespace-nowrap overflow-x-auto" style={{borderBottom:`1px solid ${deckHexA(ac,0.18)}`}}>{/* c30 / M-9: wraps under 640 so TOP POOLS starts its own line instead of sitting off-screen */}""")
ix.rep("""                <span className="ml-auto inline-flex items-center gap-4 sm:gap-5 font-mono text-[11px] text-white/40 tracking-[0.06em]">""",
       """                <span className="sm:ml-auto inline-flex items-center gap-4 sm:gap-5 font-mono text-[11px] text-white/40 tracking-[0.06em]">""")

# M-10 — alt="" on the phone LP card logos
ix.rep("""<img src={ETH_LOGO} className="w-10 h-10 rounded-full"/>""", """<img src={ETH_LOGO} alt="" className="w-10 h-10 rounded-full"/>""")
ix.rep("""<img src={logo} className="w-10 h-10 rounded-full bg-black/50" onError={()=>setLogoErr(true)}/>""", """<img src={logo} alt="" className="w-10 h-10 rounded-full bg-black/50" onError={()=>setLogoErr(true)}/>""")
ix.rep("""<img src={ETH_LOGO} className="w-8 h-8 rounded-full"/>""", """<img src={ETH_LOGO} alt="" className="w-8 h-8 rounded-full"/>""")
ix.rep("""<img src={logo} className="w-8 h-8 rounded-full bg-black/50" onError={()=>setLogoErr(true)}/>""", """<img src={logo} alt="" className="w-8 h-8 rounded-full bg-black/50" onError={()=>setLogoErr(true)}/>""")

# M-12 — contrast, colours only
ix.rep("""className="block text-[11px] text-white/35 font-normal font-mono hover:text-white/70">""",
       """className="block text-[11px] text-white/55 font-normal font-mono hover:text-white/80">""")
ix.rep("""className="text-purple-500/40 hover:text-purple-400 font-mono text-xs transition">{truncateWallet(tx.txHash)}</a>""",
       """className="text-purple-400/70 hover:text-purple-300 font-mono text-xs transition">{truncateWallet(tx.txHash)}</a>""")

# + the Liquidity tile's partial-sum note during a DexScreener outage
ix.rep("""          {T('liq','LIQUIDITY',fmtUSD(data?.liq),null,{badge:""",
       """          {T('liq','LIQUIDITY',fmtUSD(data?.liq),(data&&data._fromChain&&data.liq!=null)?{cls:'na',node:'chain · core pools only'}:null,{badge:""")   # DexScreener out → the six pinned pools read on chain, not the whole list — say so (2026-10-07 outage)
ix.rep('tw.css?v=1', 'tw.css?v=2')   # new utilities in this batch → tw.css rebuilt → bump
ix.save()

# ================================================================= calculators.html — M-16, M-12, the "$0" cap
ca = Edit('calculators.html')
ca.rep("""                  <div className="grid grid-cols-3 gap-4">
                    <div className="flex items-center gap-3">
                      <img src={cfg.logo} alt={cfg.name} className="w-9 h-9" style={{filter:`drop-shadow(0 0 6px ${glowColor}0.3))`}}/>""",
       """                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">{/* c30 / M-16: one column on phones — three 3xl figures overprinted at 390 */}
                    <div className="flex items-center gap-3">
                      <img src={cfg.logo} alt={cfg.name} className="w-9 h-9" style={{filter:`drop-shadow(0 0 6px ${glowColor}0.3))`}}/>""", count=2)
ca.rep("""                  <div className="grid grid-cols-3 gap-4">
                    <div className="flex items-center gap-3">
                      <img src={mCfg.logo} alt={mCfg.name} className="w-9 h-9" style={{filter:`drop-shadow(0 0 6px ${moonGlow}0.3))`}}/>""",
       """                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">{/* c30 / M-16 */}
                    <div className="flex items-center gap-3">
                      <img src={mCfg.logo} alt={mCfg.name} className="w-9 h-9" style={{filter:`drop-shadow(0 0 6px ${moonGlow}0.3))`}}/>""")
for old in ["""<div className={`text-3xl font-bold ${theme.text}`}><Price p={price} c={theme.text}/></div>""",
            """<div className="text-3xl font-bold text-white"><Price p={pairedCurrentPrice}/></div>""",
            """<div className={`text-3xl font-bold ${theme.text}`}>{ratio>0?(ratio>=1?fmtComma(ratio,2):ratio>=0.01?fmtComma(ratio,4):ratio.toFixed(6)):'\\u2014'}</div>""",
            """<div className={`text-3xl font-bold ${moonThemeText}`}><Price p={mPrice} c={moonThemeText}/></div>""",
            """<div className="text-3xl font-bold text-white">{fmtMcap(mMcap)}</div>""",
            """<div className="text-3xl font-bold text-white">{fmtMcap(mTotalTokenLiq)}</div>""",
            """<div className={`text-3xl font-bold ${theme.text}`}>{fmtUSD(liveVol24hUSD)}</div>"""]:
    c = ca.s.count(old)
    new = old.replace('text-3xl', 'text-2xl sm:text-3xl')
    if c: ca.rep(old, new, count=c)
ca.rep("""<div className="text-3xl font-bold text-white">{fmtMcap(data?.mcap||0)}</div>""",
       """<div className="text-2xl sm:text-3xl font-bold text-white">{data?.mcap>0?fmtMcap(data.mcap):'\\u2014'}</div>""")   # never "$0" (c23's null-through)
ca.rep("""<div className="text-white/20 text-base py-2">Enter an amount to see reward projections</div>""",
       """<div className="text-white/45 text-base py-2">Enter an amount to see reward projections</div>""")
ca.rep('tw.css?v=1', 'tw.css?v=2')
ca.save()

# ================================================================= charts.html — M-12 preset buttons
ch = Edit('charts.html')
ch.rep("""background:rgba(255,255,255,0.02);color:rgba(255,255,255,0.3);font-family:'JetBrains Mono',monospace;white-space:nowrap}""",
       """background:rgba(255,255,255,0.02);color:rgba(255,255,255,0.55);font-family:'JetBrains Mono',monospace;white-space:nowrap}   /* c30 / M-12: was .3 (2.6:1) */""")
ch.rep('tw.css?v=1', 'tw.css?v=2')
ch.save()

# ================================================================= ledger.html — M-13
le = Edit('ledger.html')
le.rep("""rounded-2xl p-5 mb-4" aria-busy={loading ? 'true' : undefined}>
              <div className="flex items-center justify-between mb-4">""",
       """rounded-2xl p-5 mb-4" aria-busy={loading ? 'true' : undefined}>
              <div className="flex flex-wrap items-baseline justify-between gap-x-3 gap-y-1 mb-4">{/* c30 / M-13: the heading and the count wrap on phones */}""")
le.rep('tw.css?v=1', 'tw.css?v=2')
le.save()
pf = Edit('portfolio.html'); pf.rep('tw.css?v=1', 'tw.css?v=2'); pf.save()
print('audit3-p6: done')
