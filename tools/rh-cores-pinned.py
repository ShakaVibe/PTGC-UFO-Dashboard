#!/usr/bin/env python3
"""Every RH-core pool is pinned (2026-10-06, Shaka: the RH Cores card read UFO/INC $0 — DexScreener had dropped the pool for want
of volume while it holds ~$120K; "force all the RH cores to always display regardless of what DexScreener currently shows").
The mechanism already existed — HARDCODED_*_PAIRS are read from the chain (fetchLPFromChain: the token's balance in the pool
× price × 2) whenever DexScreener's list lacks them — but it only named PTGC/PRVX and UFO's constructor pools + eHEX. Now all
six cores for both tokens are in the lists (addresses from the PulseX factories' getPair, v2 unless noted), so a core
DexScreener drops still shows on the RH Cores card, the RH modal, the LP Pairs table and the IN-LP count. The chain row
carries volume 0 / no txns (DexScreener had none to give). Run once: python3 tools/rh-cores-pinned.py"""
import sys,pathlib
p=pathlib.Path(__file__).resolve().parent.parent/'index.html'; s=p.read_text()
if 'PAIR_UFO_INC' in s: sys.exit('already applied')
def rep(old,new):
    global s
    assert s.count(old)==1,(old[:70],s.count(old)); s=s.replace(old,new)
rep("""      PAIR_UFO_EHEX:'0xe61aA9a9b7a13ceedEAa8D26bfF5222003a40634',
""","""      PAIR_UFO_EHEX:'0xe61aA9a9b7a13ceedEAa8D26bfF5222003a40634',
      /* 2026-10-06: the rest of the RH-core pools, pinned (PulseX v2 factory getPair) so a pool DexScreener drops still shows */
      PAIR_UFO_INC:'0xf7d75a0bbe1ef90cda220dea7450105a956abf19',
      PAIR_UFO_HEX:'0x9abd84eae174c6cf7fbf67cbb550930845866e05',
      PAIR_UFO_PRVX:'0x1693b411ca2df63c15292ad1fccf8ff06a643b25',
      PAIR_PTGC_PLSX:'0xdb08cc9f70725b30204355a39a92ace9266c3819',
      PAIR_PTGC_INC:'0x0d68d64c70e204c1cff6180b5ec656a7840d8131',
      PAIR_PTGC_HEX:'0xdc995338cf3f84b92ec6015bbb19c036f16bf9d5',
      PAIR_PTGC_EHEX:'0x0057604c09007b8d020931ba507f8591bc4e8658',
""")
rep("""    const HARDCODED_PTGC_PAIRS = [
      { address: ADDR.PAIR_PTGC_PRVX, quoteSymbol: 'PRVX', quoteName: 'ProveX', quoteAddress: ADDR.PRVX, isRHCore: true, version: 'v2' }
    ];""","""    const HARDCODED_PTGC_PAIRS = [   // 2026-10-06: all six RH cores (was PRVX alone) — read from the chain only when DexScreener's list lacks one
      { address: ADDR.PAIR_PTGC_WPLS, quoteSymbol: 'WPLS', quoteName: 'Wrapped PLS', quoteAddress: ADDR.WPLS, isRHCore: true, version: 'v1' },
      { address: ADDR.PAIR_PTGC_PLSX, quoteSymbol: 'PLSX', quoteName: 'PulseX',      quoteAddress: ADDR.PLSX, isRHCore: true, version: 'v2' },
      { address: ADDR.PAIR_PTGC_INC,  quoteSymbol: 'INC',  quoteName: 'Incentive',   quoteAddress: ADDR.INC,  isRHCore: true, version: 'v2' },
      { address: ADDR.PAIR_PTGC_HEX,  quoteSymbol: 'HEX',  quoteName: 'HEX',         quoteAddress: ADDR.HEX,  isRHCore: true, version: 'v2' },
      { address: ADDR.PAIR_PTGC_EHEX, quoteSymbol: 'EHEX', quoteName: 'eHEX',        quoteAddress: ADDR.EHEX, isRHCore: true, version: 'v2' },
      { address: ADDR.PAIR_PTGC_PRVX, quoteSymbol: 'PRVX', quoteName: 'ProveX',      quoteAddress: ADDR.PRVX, isRHCore: true, version: 'v2' }
    ];""")
rep("""      { address: ADDR.PAIR_UFO_EHEX, quoteSymbol: 'EHEX', quoteName: 'eHEX',          quoteAddress: ADDR.EHEX, isRHCore: true, version: 'v2' }/* MIGRATION:""",
"""      { address: ADDR.PAIR_UFO_INC,  quoteSymbol: 'INC',  quoteName: 'Incentive',      quoteAddress: ADDR.INC,  isRHCore: true, version: 'v2' },   // 2026-10-06: DexScreener dropped it (no volume) while it holds ~$120K
      { address: ADDR.PAIR_UFO_HEX,  quoteSymbol: 'HEX',  quoteName: 'HEX',            quoteAddress: ADDR.HEX,  isRHCore: true, version: 'v2' },   // 2026-10-06
      { address: ADDR.PAIR_UFO_PRVX, quoteSymbol: 'PRVX', quoteName: 'ProveX',         quoteAddress: ADDR.PRVX, isRHCore: true, version: 'v2' },   // 2026-10-06
      { address: ADDR.PAIR_UFO_EHEX, quoteSymbol: 'EHEX', quoteName: 'eHEX',          quoteAddress: ADDR.EHEX, isRHCore: true, version: 'v2' }/* MIGRATION:""")
p.write_text(s); print('edited index.html')
