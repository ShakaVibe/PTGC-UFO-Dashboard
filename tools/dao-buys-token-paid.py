#!/usr/bin/env python3
"""Audit IV M-13 (2026-10-24, Shaka: "Chart counts it too"): the DAO Buys chart counts a PTGC buy the DAO paid for with
another TOKEN (not PLS), as the Ledger already does — July 2026 read 6 buys / 183.0 M PTGC on the Ledger and 5 / 168.1 M on
the chart; the extra one is 0x43a877df… (2026-07-05, wallet 2: 5.56 B "Burn" token → 14.87 M PTGC via a multicall router).
Rule (the Ledger's, in the builder): a tx the wallet SENT, PTGC arrived, no PLS paid, not an LP removal / add, the wallet sent
at least one token that is not an LP token, and no PTGC went to the burn address. Priced at the PTGC market price of its own
block (pair reserves × PLS/USD, the same read every buy gets): usd = PTGC × market; `pls` = the PLS-equivalent (usd ÷ PLS/USD)
so the PLS totals and averages stay comparable; `paidWith {symbol, amount}` is what the wallet really sent, and the page
prints that instead of "N PLS" on the buy's own row / tooltip / share card.
Idempotent, from the repo root:   python3 tools/dao-buys-token-paid.py   (twice: "0 edit(s)")
"""
import hashlib
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

B, IX = 'scripts/build-dao-buys.mjs', 'index.html'
edit(B, "const LP_REMOVAL_SELECTORS = new Set(['0x2195995c', '0x02751cec', '0xded9382a', '0x5b0d5984', '0xaf2979eb']); // removeLiquidityETH* family",
        "const LP_REMOVAL_SELECTORS = new Set(['0x2195995c', '0x02751cec', '0xded9382a', '0x5b0d5984', '0xaf2979eb']); // removeLiquidityETH* family\n"
        "const LP_ADD_SELECTORS = new Set(['0xe8e33700', '0xf305d719']);   // addLiquidity / addLiquidityETH (the Ledger's rule 1)\n"
        "const BURN_ADDR = '0x0000000000000000000000000000000000000369';\n"
        "/* M-13 (2026-10-24): the Ledger's LP-token test (ledger.html isLPToken), so the two surfaces agree on what a token-paid buy is */\n"
        "const isLpToken = t => { const s = (t.tokenSymbol || '').toUpperCase(), nm = (t.tokenName || '').toLowerCase();\n"
        "  return s.includes('LP') || s.includes('PLP') || s.includes('UNI-V2') || nm.includes('liquidity') || nm.includes('lp token') || nm.includes('pulsex'); };\n"
        "const cleanSym = s => String(s || '').replace(/[^A-Za-z0-9.\\- ]/g, '').trim().slice(0, 12) || 'tokens';")
edit(B, """  const byHash = new Map();
  for (const t of transfers) {
    if (lc(t.contractAddress) !== PTGC) continue;""", """  const byHash = new Map(), outByHash = new Map();
  for (const t of transfers) {
    if (lc(t.from) === WALLET) { const o = outByHash.get(t.hash) || []; o.push(t); outByHash.set(t.hash, o); }   // M-13: every token the wallet sent
    if (lc(t.contractAddress) !== PTGC) continue;""")
edit(B, "  const buys = []; let lpRemovals = 0, noPlsPaid = 0;\n  for (const tx of txns) {",
        "  const buys = []; let lpRemovals = 0, noPlsPaid = 0, tokenPaid = 0;\n  for (const tx of txns) {")
edit(B, """    if (tx.value === '0') { noPlsPaid++; continue; }""", """    if (tx.value === '0') {
      /* M-13 (2026-10-24, Shaka: "Chart counts it too"): a buy PAID IN ANOTHER TOKEN, by the Ledger's rule — the wallet sent a
         non-LP token, no PTGC went to the burn address, and it is not an LP add. Priced in main() at its block's market price. */
      const outs = outByHash.get(tx.hash) || [];
      const paid = outs.filter(t => lc(t.contractAddress) !== PTGC && !isLpToken(t));
      const burnt = outs.some(t => lc(t.contractAddress) === PTGC && lc(t.to) === BURN_ADDR);
      if (!LP_ADD_SELECTORS.has(sel) && paid.length && !outs.some(isLpToken) && !burnt) {
        const p0 = paid[0], dec = Number(p0.tokenDecimal) || 18;
        const amt = paid.filter(t => lc(t.contractAddress) === lc(p0.contractAddress)).reduce((a, t) => a + Number(BigInt(t.value)) / 10 ** dec, 0);
        buys.push({ hash: tx.hash, block: Number(tx.block_number), ts: Number(tx.timeStamp), ptgc: Number(flow.inn) / 1e18, pls: null,
          paidWith: { symbol: cleanSym(p0.tokenSymbol), amount: amt, token: lc(p0.contractAddress) }, router: lc(tx.to), wallet: WALLET });
        tokenPaid++; continue;
      }
      noPlsPaid++; continue;
    }""")
edit(B, "  return { buys, lpRemovals, noPlsPaid };", "  return { buys, lpRemovals, noPlsPaid, tokenPaid };")
edit(B, "  const buys = []; let lpRemovals = 0, noPlsPaid = 0; const source = {};",
        "  const buys = []; let lpRemovals = 0, noPlsPaid = 0, tokenPaid = 0; const source = {};")
edit(B, "    console.log(`${w.addr.slice(0, 6)}…${w.addr.slice(-4)}: ${d.buys.length} buys (excluded: ${d.lpRemovals} LP removals, ${d.noPlsPaid} with no PLS paid)`);\n    buys.push(...d.buys); lpRemovals += d.lpRemovals; noPlsPaid += d.noPlsPaid;",
        "    console.log(`${w.addr.slice(0, 6)}…${w.addr.slice(-4)}: ${d.buys.length} buys (${d.tokenPaid} paid in another token; excluded: ${d.lpRemovals} LP removals, ${d.noPlsPaid} with no PLS paid)`);\n    buys.push(...d.buys); lpRemovals += d.lpRemovals; noPlsPaid += d.noPlsPaid; tokenPaid += d.tokenPaid;")
edit(B, "    return !(p && p.plsUsd > 0 && same(p.pls, b.pls) && same(p.ptgc, b.ptgc));",
        "    return !(p && p.plsUsd > 0 && (b.paidWith ? p.marketUsd > 0 : same(p.pls, b.pls)) && same(p.ptgc, b.ptgc));   // M-13: a token-paid buy has no PLS of its own to compare")
edit(B, """    if (!(b.plsUsd > 0)) throw new Error(`buy ${b.hash} has no price — aborting write`);
    b.usd = b.pls * b.plsUsd;""", """    if (!(b.plsUsd > 0)) throw new Error(`buy ${b.hash} has no price — aborting write`);
    if (b.paidWith) {   // M-13: valued at the PTGC market price of its block; pls = the PLS-equivalent
      if (!(b.marketUsd > 0)) throw new Error(`token-paid buy ${b.hash} has no market price — aborting write`);
      b.pls = b.ptgc * b.marketUsd / b.plsUsd;
    }
    b.usd = b.pls * b.plsUsd;""")
edit(B, "    excluded: { lpRemovals, noPlsPaid },", "    excluded: { lpRemovals, noPlsPaid },\n    tokenPaidBuys: tokenPaid,   // M-13: buys paid in another token (their `pls` is the PLS-equivalent)")
edit(B, "      plsUsd: round(b.plsUsd, 6), usd: round(b.usd, 8), price: round(b.price, 6), marketUsd: round(b.marketUsd || b.price, 6) })),",
        "      plsUsd: round(b.plsUsd, 6), usd: round(b.usd, 8), price: round(b.price, 6), marketUsd: round(b.marketUsd || b.price, 6),\n"
        "      ...(b.paidWith ? { paidWith: { symbol: b.paidWith.symbol, amount: round(b.paidWith.amount, 10), token: b.paidWith.token } } : {}) })),")

# ---- the page: a token-paid buy shows what was really sent
edit(IX, "    const DaoPrice=({v,unit,c=''})=>",
         "    /* M-13 (2026-10-24): a buy paid in another token prints that token, not its PLS-equivalent */\n"
         "    const daoPaidTxt=b=>b&&b.paidWith?`${fmtAbbr(b.paidWith.amount)} ${String(b.paidWith.symbol).replace(/[^A-Za-z0-9.\\- ]/g,'')}`:`${fmtAbbr(b.pls)} PLS`;\n"
         "    const DaoPrice=({v,unit,c=''})=>")
edit(IX, "font-semibold tabular-nums\">${fmtAbbr(b.pls)} PLS <span class=\"text-white/45 font-normal\">",
         "font-semibold tabular-nums\">${daoPaidTxt(b)} <span class=\"text-white/45 font-normal\">")
edit(IX, "for <span className=\"text-white font-semibold\">{fmtAbbr(buy.pls)} PLS</span>",
         "for <span className=\"text-white font-semibold\">{daoPaidTxt(buy)}</span>")
edit(IX, "<div className=\"mt-1 text-white/60 text-sm whitespace-nowrap\">{fmtAbbr(b.pls)} PLS <span",
         "<div className=\"mt-1 text-white/60 text-sm whitespace-nowrap\">{daoPaidTxt(b)} <span")
edit(IX, "text-white/80\">{fmtAbbr(b.pls)} <span className=\"text-white/45 text-base\">PLS</span></td>",
         "text-white/80\">{b.paidWith?<>{fmtAbbr(b.paidWith.amount)} <span className=\"text-white/45 text-base\">{daoPaidTxt(b).split(' ').slice(1).join(' ')}</span></>:<>{fmtAbbr(b.pls)} <span className=\"text-white/45 text-base\">PLS</span></>}</td>")
edit(IX, "{has&&isL&&<>for <b style={{color:'#fff'}}>{fmtAbbr(hero.pls)} PLS</b>",
         "{has&&isL&&<>for <b style={{color:'#fff'}}>{daoPaidTxt(hero)}</b>")
edit(IX, "<b style={{color:'#fff'}}>{fmtAbbr(L.ptgc)} PTGC</b> for {fmtAbbr(L.pls)} PLS",
         "<b style={{color:'#fff'}}>{fmtAbbr(L.ptgc)} PTGC</b> for {daoPaidTxt(L)}")

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'dao-buys-token-paid: {n} edit(s); build-dao-buys.mjs {sha(B)}, index.html {sha(IX)}')
