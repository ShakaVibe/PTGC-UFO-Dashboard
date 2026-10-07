#!/usr/bin/env python3
"""Audit III, batch 2 (2026-10-07): the honesty-and-copy items c23, c24, c26, c27. Idempotent — run from the repo root on both copies:
    python3 tools/audit3-p2.py
Each edit asserts its anchor exists exactly once (or is already applied) so a drifted file fails loudly instead of half-applying.
  c23 honesty pass II — LP Pairs v2 rows + band print "—" (not "$0" / "0 / 0") for chain-read pairs and on a DexScreener outage;
      the Socials RH Core Liquidity card prints "—" for a core whose pair did not load (and no total); the KPI card's 30D burn USD
      is "—" without a price; fetchDex's market cap is null-through (implied supply from the price) instead of a literal 0
  c24 the Volume window's foot said all four figures were DexScreener's — only 24H is; 7D / 30D / 90D are CoinGecko on-chain
      daily candles over the 20 largest pools (fetch-coingecko-data.js)
  c26 "RH core liquidity" counts the LARGEST pool per core (the dedupe at the band filter, the window and the Socials card) — the
      window's subtitle and the band's ⓘ now say so instead of "the pools paired with"
  c27 the Humans vs Bots chart labels its UTC day bins in UTC (was the visitor's local date); the Volume window's chart heading says
      "UTC days"; the 24H hour labels are en-US
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
    def save(self):
        write(self.path, self.s); print(f'{self.path}: {self.n} edit(s), md5 {md5(self.s)}')

ix = Edit('index.html')

# ---------------------------------------------------------------- c23 — honesty pass II
# LpRowV2: a chain-read pair (DexScreener missing it) has fabricated 0s for volume / buys / sells — the RhCoresModal rule (a14)
ix.rep("""      const liq=pair.liq,vol=pair.vol;
      const ratio=liq>0&&vol!=null?(vol/liq).toFixed(3):'\\u2014';
      const buys=pair.txns?.h24?.buys,sells=pair.txns?.h24?.sells,txTotal=(buys!=null&&sells!=null)?buys+sells:null;""",
       """      /* c23 (Audit III): a chain-read pair (`_fromChain`, DexScreener missing it) carries fabricated 0s for volume and
         txns — the RhCoresModal rule (a14): those are UNKNOWN here, "—", never $0 / 0 / 0 */
      const liq=pair.liq,vol=(!pair._fromChain&&pair.vol!=null&&isFinite(pair.vol))?pair.vol:null;
      const ratio=liq>0&&vol!=null?(vol/liq).toFixed(3):'\\u2014';
      const buys=pair._fromChain?null:pair.txns?.h24?.buys,sells=pair._fromChain?null:pair.txns?.h24?.sells,txTotal=(buys!=null&&sells!=null)?buys+sells:null;""")

# the band's totals: null when the tile's own volume / liquidity is unknown (DexScreener outage), never a sum of fabricated zeros
ix.rep("""      // Calculate totals based on filter
      const filteredVol=filteredSorted.reduce((s,p)=>s+(p.vol||0),0);
      const filteredLiq=filteredSorted.reduce((s,p)=>s+(p.liq||0),0);""",
       """      // Calculate totals based on filter — c23 (Audit III): null when the tile's own figure is null (a DexScreener outage, a14),
      // so the band prints "—" like the tile instead of summing the chain pairs' fabricated 0s into "$0"
      const filteredVol=data?.vol==null?null:filteredSorted.reduce((s,p)=>s+(p._fromChain?0:(p.vol||0)),0);
      const filteredLiq=data?.liq==null?null:filteredSorted.reduce((s,p)=>s+(p.liq||0),0);""")
ix.rep("vol={filteredVol} vgen={cfg.feeRate>0?filteredVol*cfg.feeRate:null}",
       "vol={filteredVol} vgen={(filteredVol!=null&&cfg.feeRate>0)?filteredVol*cfg.feeRate:null}")
ix.rep("""<span><i>Value Gen</i><b className="g">{cfg.feeRate>0?fmtUSD(filteredVol*cfg.feeRate):'\\u2014'}</b></span>""",
       """<span><i>Value Gen</i><b className="g">{(filteredVol!=null&&cfg.feeRate>0)?fmtUSD(filteredVol*cfg.feeRate):'\\u2014'}</b></span>""")

# Socials RH Core Liquidity card: a core whose pair did not load is unknown, not $0; the total only when every core is known
ix.rep("""    const rhCoreLiq=(pairs,core)=>{
      if(!pairs||!pairs.length)return null;   // a18: unknown column → "—"
      const p=pairs.find(p=>{const q=(p.quoteToken?.symbol||'').toUpperCase(),b=(p.baseToken?.symbol||'').toUpperCase();return q===core||b===core;});
      return p?(p.liq||0):0;
    };
    const rhCoreTotal=pairs=>pairs&&pairs.length?RH_CARD_CORES.reduce((s,c)=>s+(rhCoreLiq(pairs,c)||0),0):null;""",
       """    const rhCoreLiq=(pairs,core)=>{
      if(!pairs||!pairs.length)return null;   // a18: unknown column → "—"
      /* the LARGEST pool per core (the pairs arrive sorted by liquidity) — the same rule as the band filter and the RH window (c26) */
      const p=pairs.find(p=>{const q=(p.quoteToken?.symbol||'').toUpperCase(),b=(p.baseToken?.symbol||'').toUpperCase();return q===core||b===core;});
      return p?(p.liq>0?p.liq:null):null;   // c23 (Audit III): a pinned core pair that did not load is UNKNOWN → "—", never $0
    };
    const rhCoreTotal=pairs=>{   // c23: the total only when every core is known
      if(!pairs||!pairs.length)return null;
      let s=0;for(const c of RH_CARD_CORES){const v=rhCoreLiq(pairs,c);if(v==null)return null;s+=v;}return s;
    };""")

# KPI card: the 30D burn's USD needs a price
ix.rep("      const burn7dUSD=burn7dAmt*(d?.price||0);",
       "      const burn7dUSD=(burn7dKnown&&d?.price>0)?burn7dAmt*d.price:null;   // c23 (Audit III): no price → \"—\", never \"$0\"")

# fetchDex: a priced main pair with neither marketCap nor fdv → the implied-supply cap, never a literal 0
ix.rep("""              if(_dsPrice <= 0 && _price > 0) return mcapFromPrice(addr, _price, _m);
              return _m;
            })(),""",
       """              if(_dsPrice <= 0 && _price > 0) return mcapFromPrice(addr, _price, _m);
              if(_m > 0) return _m;
              /* c23 (Audit III): a priced pair with neither marketCap nor fdv — derive from the price (the remembered implied
                 supply, else starting supply minus the known burn), and null when there is no price either → "—", never "$0" */
              return _price > 0 ? mcapFromPrice(addr, _price, 0) : null;
            })(),""")

# ---------------------------------------------------------------- c24 — the Volume window's sources
ix.rep("""              <div className="vw-conf">The four figures are DexScreener's, summed over every pair {'—'} the same numbers as the Volume tile. The daily chart and the pool table are on-chain swap volume from the hourly file (the Humans vs Bots data), so they will not match DexScreener to the dollar.</div>""",
       """              <div className="vw-conf">24H is DexScreener's, summed over every pair {'—'} the Volume tile's own number. 7D / 30D / 90D are CoinGecko's on-chain daily candles over the 20 largest pools (today counts as a partial day). The daily chart and the pool table are on-chain swap volume from the hourly file (the Humans vs Bots data). Three sources, so they will not match each other to the dollar.</div>""")

# ---------------------------------------------------------------- c26 — "largest pool per core"
ix.rep("""                  <div className="rc-sub">Liquidity in the {tk} pools paired with Richard Heart's PulseChain core coins {'—'} WPLS, PLSX, INC, HEX, eHEX and PRVX</div>""",
       """                  <div className="rc-sub">Liquidity in the largest {tk} pool paired with each Richard Heart core coin {'—'} WPLS, PLSX, INC, HEX, eHEX and PRVX</div>""")
ix.rep("""          <p>Switch it on to show only the {token} pools paired with one of them.</p>""",
       """          <p>Switch it on to show only the largest {token} pool paired with each of them (a core with a v1 and a v2 pool shows the bigger one).</p>""")

# ---------------------------------------------------------------- c27 — UTC labels
ix.rep("""      const fmtT=t=>{const d=new Date(t);return binMs<86400000&&binMs<6*3600000?d.toLocaleTimeString([],{hour:'numeric'}):d.toLocaleDateString('en-US',{month:'short',day:'numeric'});};""",
       """      /* c27 (Audit III): the day bins start at UTC midnight, so label them in UTC (a New York visitor saw "Sep 30" on the Oct 1 bin); hour bins keep local time, en-US */
      const fmtT=t=>{const d=new Date(t);return binMs<86400000&&binMs<6*3600000?d.toLocaleTimeString('en-US',{hour:'numeric'}):d.toLocaleDateString('en-US',{month:'short',day:'numeric',timeZone:'UTC'});};""")
ix.rep("""<div className="vw-hdr"><span className="t">Daily volume {'·'} past {P.d} days</span>""",
       """<div className="vw-hdr"><span className="t">Daily volume {'·'} past {P.d} UTC days</span>""")

ix.save()
print('audit3-p2: done')
