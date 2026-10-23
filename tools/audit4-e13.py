#!/usr/bin/env python3
"""Audit IV e13 (2026-10-23) — Token Allocation tier counts: PEOPLE ONLY (Shaka: "People only"). Idempotent, from the repo root:
    python3 tools/audit4-e13.py        (twice: the second run must print "0 edit(s)")

Before: the tiers (Poseidon / Whale / Shark / Dolphin / Squid & below) counted every PulseScan holder row except the token's
LP pools and the staking contract — so the burn address was PTGC's only "Poseidon", the DAO treasury and pools of other DEXes
were Sharks, ~1,000 contracts sat in "Squid & below", and PulseScan's page-boundary repeats (e10) were counted twice.
After: the same thresholds (% of the STARTING supply, unchanged), counted over the people-only list the Top 100 and the
Portfolio HOLDER RANK already use (data/holder-ranks.json `b`: burn addresses, DAO wallets, every contract, the UFO OA wallet
left out, repeats dropped). Squid & below = people − the four tiers. Real data 2026-10-23:
    PTGC  1 / 13 / 104 / 714 / 17,361  →  0 / 12 / 96 / 692 / 16,317
    UFO   0 / 18 / 104 / 510 /  4,684  →  0 / 16 / 98 / 500 /  4,373
  - scripts/build-token-allocation.mjs: tiers from data/holder-ranks.json (≤ 12 h old, not carried); otherwise the previous
    file's tiers are kept (::warning::). No more PulseScan tier scan in this step.
  - index.html fetchHolderTiers (the live fallback when token-allocation.json is missing / > 24 h old): de-duplicates rows, skips
    the known non-people and every `is_contract`; Squid & below = holder-ranks.json's people count − the four tiers (null = "—"
    when that file is unavailable — never the address count). Tier cache key v2 → v3 (old live scans counted addresses).
"""
import hashlib, re
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    if s.count(old) != count:
        alt = ''.join(c if ord(c) < 128 else '\\u%04x' % ord(c) for c in old)
        if s.count(alt) == count: old = alt
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:80]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

B = 'scripts/build-token-allocation.mjs'
edit(B, '''// ⚠ THE ONE THING THAT WILL BREAK IF YOU TOUCH IT:''', '''// Audit IV e13 (2026-10-23, Shaka: "people only"): the TIERS are counted over data/holder-ranks.json — the people-only list
// the Top 100 window and the Portfolio HOLDER RANK use (burn addresses, DAO wallets, every contract, the UFO OA wallet left out,
// PulseScan's page repeats dropped). Same thresholds as before (% of the starting supply). Squid & below = people − the four
// tiers. That file is built by the holder-ranks step (gate 2 h); older than 12 h or carried → the previous tiers are kept
// (::warning::). This step no longer pages PulseScan itself; the note below is kept for anyone who brings the scan back.
//
// ⚠ THE ONE THING THAT WILL BREAK IF YOU TOUCH IT:''')
edit(B, '''async function holderCount(address) {
  const j = await getJson(`${SCAN}/tokens/${address}/counters`);
  const n = j && parseInt(j.token_holders_count);
  return Number.isFinite(n) && n > 0 ? n : null;   // a33: null = unknown, never 0
}

// Page all holders, classify by % of supply, stop once we drop below Dolphin (list is desc).
async function scanTiers(address, supply, exclude) {
  const counts = { Poseidon: 0, Whale: 0, Shark: 0, Dolphin: 0 };
  const supplyWei = supply * DIV;
  let counted = 0, cursor = null, complete = false;
  for (let page = 0; page < 40; page++) {
    const qs = cursor ? new URLSearchParams(cursor).toString() : 'limit=50';
    const d = await getJson(`${SCAN}/tokens/${address}/holders?${qs}`);
    if (!d || !Array.isArray(d.items) || d.items.length === 0) break;
    let below = false;
    for (const h of d.items) {
      const addr = (h.address?.hash || '').toLowerCase();
      if (exclude.has(addr)) continue;
      const pct = Number(BigInt(h.value)) / Number(supplyWei) * 100;
      if (pct < 0.01) { below = true; break; }
      if (pct >= 10) counts.Poseidon++;
      else if (pct >= 1) counts.Whale++;
      else if (pct >= 0.1) counts.Shark++;
      else counts.Dolphin++;
      counted++;
    }
    if (below) { complete = true; break; }
    if (!d.next_page_params) { complete = true; break; }
    // *** cursor from the last holder's STRING value — never next_page_params.value ***
    cursor = { ...d.next_page_params, value: String(d.items[d.items.length - 1].value) };
  }
  return { counts, counted, complete };
}''', '''// Audit IV e13: the tiers over the PEOPLE in data/holder-ranks.json (`b` = every person's balance, whole tokens from 1 up,
// high → low). null = not usable (missing, carried, older than RANKS_MAX_AGE_H) → the caller keeps the previous tiers.
const RANKS = 'data/holder-ranks.json';
const RANKS_MAX_AGE_H = 12;
let _ranks;
function tiersFromRanks(sym, supply) {
  if (_ranks === undefined) { try { _ranks = JSON.parse(fs.readFileSync(RANKS, 'utf8')); } catch { _ranks = null; } }
  const t = _ranks && _ranks.tokens && _ranks.tokens[sym];
  const at = t && Date.parse(t.readAt);
  if (!t || t.carried || !Array.isArray(t.b) || !Number.isFinite(t.holders) || !Number.isFinite(at)) return null;
  if (Date.now() - at > RANKS_MAX_AGE_H * 3600e3) return null;
  const counts = { Poseidon: 0, Whale: 0, Shark: 0, Dolphin: 0 };
  const sup = Number(supply);
  let counted = 0;
  for (const k of t.b) {                       // high → low: stop at the first balance under the Dolphin line
    const pct = k / sup * 100;
    if (pct < 0.01) break;
    if (pct >= 10) counts.Poseidon++;
    else if (pct >= 1) counts.Whale++;
    else if (pct >= 0.1) counts.Shark++;
    else counts.Dolphin++;
    counted++;
  }
  return { tiers: { ...counts, SquidAndBelow: Math.max(0, t.holders - counted) }, asOf: t.readAt };
}''')
edit(B, '''  // Tiers. Exclude LP pools + staking; do NOT exclude the burn address (matches the app).
  const exclude = new Set(pools);
  if (cfg.staking) exclude.add(cfg.staking.toLowerCase());
  const total = await holderCount(cfg.address);
  const { counts, counted, complete } = await scanTiers(cfg.address, cfg.supply, exclude);
  const excludedCount = pools.size + (cfg.staking ? 1 : 0);
  // a33: no holder count → SquidAndBelow is unknown (null; the dashboard prints "—"), and the
  // caller keeps the previous file's tiers instead when it has them.
  const squid = total == null ? null : Math.max(0, total - counted - excludedCount);

  return {
    complete: complete && total != null,
    tiers: complete ? { ...counts, SquidAndBelow: squid } : null,''', '''  // Tiers — people only (Audit IV e13): from the holder-ranks list; null → the caller keeps the previous file's tiers.
  const tr = tiersFromRanks(sym, cfg.supply);

  return {
    complete: !!tr,
    tiers: tr ? tr.tiers : null,
    tiersAsOf: tr ? tr.asOf : null,''')
edit(B, '''      tiersUpdatedAt: tiersOk ? now : (old.tiersUpdatedAt ?? old.updatedAt ?? null),
    };''', '''      tiersUpdatedAt: tiersOk ? now : (old.tiersUpdatedAt ?? old.updatedAt ?? null),
      tiersSource: tiersOk ? 'holder-ranks (people only)' : (old.tiersSource ?? null),   // Audit IV e13
      tiersAsOf: tiersOk ? r.tiersAsOf : (old.tiersAsOf ?? null),                         // when holder-ranks read PulseScan
    };
    if (!tiersOk) console.warn(`::warning::token-allocation ${sym}: ${RANKS} missing, carried or older than ${RANKS_MAX_AGE_H} h — tiers kept from ${out.tokens[sym].tiersUpdatedAt || 'nothing'}`);''')
edit(B, "    tiers: tiersOk ? r.tiers : (old.tiers ?? (r.tiers || null)),   // an incomplete scan keeps the previous exact tiers; a squid-less scan only if there is nothing older",
        "    tiers: tiersOk ? r.tiers : (old.tiers ?? null),   // no usable people list → the previous tiers")
# the old line's exact text (it is inside the object literal)
P = 'index.html'
edit(P, "      TIERS:'grays_tiers_v2_',", "      TIERS:'grays_tiers_v3_',   // v3 (Audit IV e13): people only — a v2 live scan counted addresses")
edit(P, "    const LS_RETIRED_PREFIXES=['grays_tiers_0x'];", "    const LS_RETIRED_PREFIXES=['grays_tiers_0x','grays_tiers_v2_'];")
edit(P, '''    const fetchHolderTiers=async(addr,cfg,totalHolderCount,lpAddresses=[],signal=null)=>{
      const counts={Poseidon:0,Whale:0,Shark:0,Dolphin:0};''', '''    /* Audit IV e13 (2026-10-23, Shaka: "people only"): the tiers count PEOPLE, like the Top 100 and the Portfolio rank —
       never the burn address (it was PTGC's only "Poseidon"), the DAO wallets, the token / staking / router contracts, or any
       contract PulseScan flags (pools of every DEX). The builders' list (scripts/build-holder-ranks.mjs EXCLUDE). */
    const TIER_NOT_PEOPLE=new Set(['0x0000000000000000000000000000000000000369','0x0000000000000000000000000000000000000000','0x000000000000000000000000000000000000dead',
      '0xeeac1da7f930078ab757ad8a64cf7c5e17b931e1','0x440773b5104a102c00ef26979a5c897155336a34','0x305acfab82103c2b82b19543919d1c93b44e55db',
      '0x92dd8e86fdb206fa41e451398a9f03fbd36d574d','0xc71f597a2ac39e47f07102e849d18489c96f39ef','0x165c3410fc91ef562c50559f7d2289febed552d9',
      '0x94534eeee131840b1c0f61847c572228bdfdde93','0x49ed499433bee42dd34c169470fef2c8f9fae6e6','0x456548a9b56efbbd89ca0309edd17a9e20b04018']);
    const fetchHolderTiers=async(addr,cfg,totalHolderCount,lpAddresses=[],signal=null)=>{
      const counts={Poseidon:0,Whale:0,Shark:0,Dolphin:0};
      const seen=new Set();   // e13: PulseScan repeats the last row of some pages as the first of the next (e10)''')
edit(P, '''              const holderAddr=holder.address?.hash?.toLowerCase();
              if(allLPAddresses.includes(holderAddr))continue;
              if(cfg.stakingContract&&holderAddr===cfg.stakingContract.toLowerCase())continue;''', '''              const holderAddr=holder.address?.hash?.toLowerCase();
              if(seen.has(holderAddr))continue;seen.add(holderAddr);   // e13: a page repeat is not a second holder
              if(allLPAddresses.includes(holderAddr))continue;
              if(cfg.stakingContract&&holderAddr===cfg.stakingContract.toLowerCase())continue;
              if(TIER_NOT_PEOPLE.has(holderAddr)||holder.address?.is_contract)continue;   // e13: people only''')
edit(P, '''      const squidAndBelow=(typeof totalHolderCount==='number'&&isFinite(totalHolderCount)&&totalHolderCount>0)
        ?Math.max(0,totalHolderCount-countedHolders-excludedAddresses)
        :null;''', '''      /* Audit IV e13: Squid & below = PEOPLE − the four tiers. PulseScan's holder total counts every address (pools,
         ~1,000 contracts, the burn address), so the people count comes from data/holder-ranks.json (≤ 48 h old); without it
         the cell is "—", never the address count. (totalHolderCount / excludedAddresses are no longer used for it.) */
      let squidAndBelow=null;
      if(complete&&!(signal&&signal.aborted)){
        try{
          const hr=await fetch('https://raw.githubusercontent.com/shakavibe/PTGC-UFO-Dashboard/main/data/holder-ranks.json?t='+Math.floor(Date.now()/3600000),signal?{signal}:undefined).then(r=>r.ok?r.json():null);
          const e=hr&&hr.tokens&&hr.tokens[cfg.name];
          const at=e&&Date.parse(e.readAt);
          if(e&&Number.isFinite(e.holders)&&isFinite(at)&&Date.now()-at<48*3600*1000)squidAndBelow=Math.max(0,e.holders-countedHolders);
        }catch(e){}
      }
      void totalHolderCount;void excludedAddresses;''')
# the panel says what it counts (a hover title on the tier block)
edit(P, '''                    <div className={`w-full sm:w-auto sm:border-l border-white/[0.08] sm:pl-6 sm:ml-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-white/[0.08] ${hdrV2?'p2-tiers':''}`}>''',
        '''                    <div title="People only: liquidity pools, contracts, the burn address and the DAO wallets are not counted" className={`w-full sm:w-auto sm:border-l border-white/[0.08] sm:pl-6 sm:ml-auto pt-3 sm:pt-0 border-t sm:border-t-0 border-white/[0.08] ${hdrV2?'p2-tiers':''}`}>''')
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'audit4-e13: {n} edit(s), index {sha(P)}, build-token-allocation {sha(B)}')
