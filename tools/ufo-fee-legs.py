#!/usr/bin/env python3
""""PTGC burned by UFO" counts pTGC's own 0.5 % fee burn on each buyback (Shaka, 2026-10-24: "yes that should be included" →
asked → "what do you suggest" → Claude: count it on both contracts → "do it").
Idempotent, from the repo root:   python3 tools/ufo-fee-legs.py   (a second run prints "0 edit(s)")

Before: the live contract's chain scan (scripts/build-value-generated.mjs and its twin in index.html) dropped the leg whose size is
0.005/0.95 of the delivered leg (pTGC's own burn fee on the buyback transfer); the retired contract's figure
(fetch-ufo-ptgc-burns.js) always counted it. Now both count every pTGC burn inside a UFO swapback transaction — what the chain
shows, no ratio fingerprint. The pre-window checkpoints were built the old way, so they are retired: the file's
`delivered.ptgcPreWindow` is accepted only with method 'all-legs', and the browser's localStorage key moves to _v2.
"""
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

VG, IX = 'scripts/build-value-generated.mjs', 'index.html'
for path in (VG, IX):
    # 1. the 24H/7D/30D/90D window scan
    edit(path, """          const drop={};
          for(let i=0;i<legs.length;i++)for(let j=0;j<legs.length;j++){
            if(i===j||drop[i])continue;
            const r=legs[i].amt/legs[j].amt;
            if(legs[j].amt>0&&Math.abs(r-PTGC_FEE_RATIO)/PTGC_FEE_RATIO<0.01){drop[i]=true;ptgcFeeLegsDropped++;}
          }
          legs.forEach((lg,i)=>{
            if(drop[i])return;
            addTo(parseInt(lg.log.blockNumber,16),a=>{a.ptgcBurned+=lg.amt;});
          });""", """          /* 2026-10-24 (Shaka): EVERY leg counts — pTGC's own 0.5% burn fee on the buyback is burned because UFO bought, and the
             retired contract's figure (fetch-ufo-ptgc-burns.js) always counted it. PTGC_FEE_RATIO is kept only to report how many
             legs are fee legs (ptgcFeeLegsDropped is now "fee legs seen", none are dropped). */
          for(let i=0;i<legs.length;i++)for(let j=0;j<legs.length;j++){
            if(i!==j&&legs[j].amt>0&&Math.abs(legs[i].amt/legs[j].amt-PTGC_FEE_RATIO)/PTGC_FEE_RATIO<0.01){ptgcFeeLegsDropped++;break;}
          }
          legs.forEach(lg=>{addTo(parseInt(lg.log.blockNumber,16),a=>{a.ptgcBurned+=lg.amt;});});""")
    # 2. the pre-window (lifetime) slice
    edit(path, """        const legs=byTx[tx].map(l=>({amt:weiToTokens(BigInt(l.data&&l.data!=='0x'?l.data:'0x0'))}));
        const drop={};
        for(let i=0;i<legs.length;i++)for(let j=0;j<legs.length;j++){
          if(i===j||drop[i])continue;
          const r=legs[i].amt/legs[j].amt;
          if(legs[j].amt>0&&Math.abs(r-PTGC_FEE_RATIO)/PTGC_FEE_RATIO<0.01)drop[i]=true;
        }
        legs.forEach((lg,i)=>{if(!drop[i])sum+=lg.amt;});""", """        // 2026-10-24: every leg counts, the 0.5% fee burn included (see the window scan)
        for(const l of byTx[tx])sum+=weiToTokens(BigInt(l.data&&l.data!=='0x'?l.data:'0x0'));""")

for path in (VG, IX):
  edit(path, "        if(ptgcFeeLegsDropped)console.log(`   (${ptgcFeeLegsDropped} pTGC leg(s) identified as pTGC's own 0.5% burn fee and excluded)`);",
       "        if(ptgcFeeLegsDropped)console.log(`   (${ptgcFeeLegsDropped} pTGC leg(s) are pTGC's own 0.5% burn fee — counted since 2026-10-24)`);")
# 3. checkpoints built the old way are not reused
edit(VG, "  const prevCheckpoint=prev&&prev.delivered&&prev.delivered.ptgcPreWindow||null;",
         "  const prevCheckpoint=(prev&&prev.delivered&&prev.delivered.ptgcPreWindow&&prev.delivered.ptgcPreWindow.method==='all-legs')?prev.delivered.ptgcPreWindow:null;   // 2026-10-24: older checkpoints left the fee legs out")
edit(VG, "  if(pre.ok && pre.toBlock!=null) delivered.ptgcPreWindow = { toBlock: pre.toBlock, amount: pre.amount, launch: delivered.launch||0 };",
         "  if(pre.ok && pre.toBlock!=null) delivered.ptgcPreWindow = { toBlock: pre.toBlock, amount: pre.amount, launch: delivered.launch||0, method: 'all-legs' };")
edit(IX, "      PTGC_PRE:'grays_ptgc_by_ufo_pre_v1',        // + ':'+UFO address → {launch,toBlock,amount} pre-window checkpoint",
         "      PTGC_PRE:'grays_ptgc_by_ufo_pre_v2',        // + ':'+UFO address → {launch,toBlock,amount} pre-window checkpoint (v2 2026-10-24: fee legs counted)")
edit(IX, "    const LS_RETIRED_PREFIXES=['grays_tiers_0x','grays_tiers_v2_'];",
         "    const LS_RETIRED_PREFIXES=['grays_tiers_0x','grays_tiers_v2_','grays_ptgc_by_ufo_pre_v1'];")
edit(IX, """         (schema 2, <24h old). Less precise than the chain scan (it cannot separate pTGC's own
         0.5% fee leg), so it is the fallback when the pre-window read failed, not the primary. */""",
         """         (schema 2, <24h old). Since 2026-10-24 both count pTGC's 0.5% fee leg; the file's definition (any tx with a UFO burn)
         is a little wider than the scan's (UFO's swapback txs), so it stays the fallback when the pre-window read failed. */""")
print(f'{n} edit(s)')
