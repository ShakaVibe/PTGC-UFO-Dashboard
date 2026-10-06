# build-swap-volume.mjs — the 2026-10-06 evening audit's two fixes (Shaka: "fix it"). Idempotent.
#  1. The wallet rule counts TRANSACTIONS per day, not legs — PulseX's smart router splits one swap across 3-4 pools, and a person
#     doing 18 swaps a day (0x2a96…507f, a rewards harvester) showed 57 "trades" and became a bot ($3,787 of today's $9,691 "bot" volume).
#  2. A round trip is not a round trip when every leg came through a human path (router / aggregator) AND the asset bought with
#     differs from the asset sold for — that is a swap routed THROUGH the token (UFO→PTGC→WPLS: a person selling UFO for PLS),
#     not arbitrage, which starts and ends in the same asset. 24 txs / $2,933 over 90 d had been bots.
import sys
p=sys.argv[1] if len(sys.argv)>1 else 'scripts/build-swap-volume.mjs'
s=open(p,encoding='utf-8').read()
old='''      const buys = grp.filter(r => r[j] != null && r[i] > 0), sells = grp.filter(r => r[j] != null && r[i] < 0);
      if (buys.length && sells.length && new Set([...buys, ...sells].map(r => r[3])).size >= 2) [...buys, ...sells].forEach(r => arbRows.add(r));'''
new='''      const buys = grp.filter(r => r[j] != null && r[i] > 0), sells = grp.filter(r => r[j] != null && r[i] < 0);
      if (!(buys.length && sells.length && new Set([...buys, ...sells].map(r => r[3])).size >= 2)) continue;
      // 2026-10-06 audit: a swap ROUTED THROUGH the token is not arbitrage — every leg via a human path (router / aggregator) and the
      // asset it was bought with is not the asset it was sold for (UFO→PTGC→WPLS = a person selling UFO for PLS). Arbitrage starts
      // and ends in the same asset, and bots call the pools from their own contracts anyway.
      const tokAddr = i === 10 ? TOKENS.PTGC.address : TOKENS.UFO.address;
      const partner = r => { const pl = pools[idx.pools[r[3]]] || {}; return pl.token0 === tokAddr ? pl.token1 : pl.token0; };
      const viaHuman = grp.every(r => classOf(idx.senders[r[4]]).kind === 'human');
      const inSet = new Set(buys.map(partner)), outSet = new Set(sells.map(partner));
      // …and arbitrage buys and sells ABOUT THE SAME amount of the token. A big sell split by the smart router across five pools
      // with one small buy leg on the way (every router "round trip" in 90 d: ratio ≤ 0.3, $108K of UFO sells) is a person selling.
      const bAmt = buys.reduce((a, r) => a + r[j], 0), sAmt = sells.reduce((a, r) => a + r[j], 0), balance = Math.min(bAmt, sAmt) / Math.max(bAmt, sAmt);
      if (viaHuman && (![...inSet].some(a => outSet.has(a)) || balance < ARB_MIN_BALANCE)) continue;
      [...buys, ...sells].forEach(r => arbRows.add(r));'''
if 'a swap ROUTED THROUGH the token is not arbitrage' not in s:
    assert old in s; s=s.replace(old,new,1)
old3="const WALLET_BOT_PER_DAY = 50;"
if 'const ARB_MIN_BALANCE' not in s:
    assert old3 in s; s=s.replace(old3,"const ARB_MIN_BALANCE = 0.5;                    // 2026-10-06 audit: a router-sent round trip counts only if the buy and sell legs are within 2× of each other (arbitrage is balanced; a split sell with a small buy leg is a person)\n"+old3,1)
old2='''  const perDay = {};
  for (const r of rows) { if (r[5] !== 1) continue; const w = walletOf(r); if (!w) continue; const k = w + '|' + Math.floor(r[0] / 86400000); perDay[k] = (perDay[k] || 0) + 1; }
  const botWallets = new Set(Object.entries(perDay).filter(([, n]) => n >= WALLET_BOT_PER_DAY).map(([k]) => k.split('|')[0]));'''
new2='''  // 2026-10-06 audit: count TRANSACTIONS a day, not legs — the PulseX smart router splits one swap across 3-4 pools (a person's
  // 18 swaps read as 57 "trades" and became a bot's)
  const perDay = {};
  for (const r of rows) { if (r[5] !== 1) continue; const w = walletOf(r); if (!w) continue; const k = w + '|' + Math.floor(r[0] / 86400000); (perDay[k] || (perDay[k] = new Set())).add(r[2] + '|' + r[1]); }
  const botWallets = new Set(Object.entries(perDay).filter(([, set]) => set.size >= WALLET_BOT_PER_DAY).map(([k]) => k.split('|')[0]));'''
if 'count TRANSACTIONS a day, not legs' not in s:
    assert old2 in s; s=s.replace(old2,new2,1)
open(p,'w',encoding='utf-8').write(s); print('audit fix ok')
