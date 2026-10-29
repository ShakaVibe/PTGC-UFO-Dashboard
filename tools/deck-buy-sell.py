#!/usr/bin/env python3
"""Live Feed — BUY / SELL only (2026-10-29). Shaka: "On the live feed.. I dont like the new ARB badges.. I just want buy or
sell.. and we dont need to put looped by a bot...".

Audit V v23 (2026-10-25) grouped a loop (a buy in one pool + a sell in another, one transaction) into ONE purple "ARB" row
reading "$X looped by a bot". Now a loop is shown as its two sides again — a BUY row (the pool it bought from) and a SELL row
(the pool it sold into), the way DexScreener lists them and the way the tape looked before v23. What v23 fixed stays fixed:
the transaction paid ONE fee (measured from its fee legs, or the estimate counted once), and the two rows SHARE it by size —
half each for a plain loop — so the pods and totals still count it once (the LP Pairs table splits a loop's fee the same way).
A router-split buy stays one BUY row. The ARB badge colours, its tooltip and the "looped by a bot" words are gone; the
footnote under the tape says how the fee is read.

Idempotent (done-markers); a second run prints "0 edit(s)". Run from the repo root.
"""
import sys, pathlib

P = pathlib.Path('index.html')
s = P.read_text()
edits = 0

def rep(old, new, marker, count=1):
    global s, edits
    if marker in s:
        return
    n = s.count(old)
    if n != count:
        sys.exit(f'anchor found {n}x (want {count}): {old[:100]!r}')
    s = s.replace(old, new)
    edits += 1

def rep_span(start, end, new, marker):
    """Replace from `start` through `end` (both included, each found exactly once) with `new`."""
    global s, edits
    if marker in s:
        return
    if s.count(start) != 1:
        sys.exit(f'start anchor found {s.count(start)}x: {start[:100]!r}')
    i = s.index(start)
    j = s.find(end, i)
    if j < 0 or j - i > 4000:
        sys.exit(f'end anchor not found near start: {end[:100]!r}')
    s = s[:i] + new + s[j + len(end):]
    edits += 1

# 1. the type badge: BUY green / SELL red / TRANSFER gold — no ARB colour, no ARB tooltip
rep("style={{color:r.side==='BUY'?'#86efac':r.side==='SELL'?'#fca5a5':r.side==='ARB'?'#c4b5fd':'#F5DE8A',"
    "background:r.side==='BUY'?'rgba(22,101,52,0.5)':r.side==='SELL'?'rgba(127,29,29,0.5)':r.side==='ARB'?'rgba(76,29,149,0.45)':'rgba(120,53,15,0.45)',"
    "border:`1px solid ${r.side==='BUY'?'rgba(74,222,128,0.55)':r.side==='SELL'?'rgba(248,113,113,0.55)':r.side==='ARB'?'rgba(167,139,250,0.55)':'rgba(232,192,68,0.55)'}`}} "
    "title={r.side==='ARB'?'A bot\\'s loop: bought in one pool and sold in another in one transaction — the token moved once, so one fee':undefined}>{r.side}</div>",
    "style={{color:r.side==='BUY'?'#86efac':r.side==='SELL'?'#fca5a5':'#F5DE8A',"
    "background:r.side==='BUY'?'rgba(22,101,52,0.5)':r.side==='SELL'?'rgba(127,29,29,0.5)':'rgba(120,53,15,0.45)',"
    "border:`1px solid ${r.side==='BUY'?'rgba(74,222,128,0.55)':r.side==='SELL'?'rgba(248,113,113,0.55)':'rgba(232,192,68,0.55)'}`}}>{r.side}</div>",
    "r.side==='SELL'?'#fca5a5':'#F5DE8A',")

# 2. the row's words: "bought" / "sold" / "transferred" — never "looped by a bot"
rep("{r.side==='BUY'?'bought':r.side==='SELL'?'sold':r.side==='ARB'?'looped by a bot':'transferred'}",
    "{r.side==='BUY'?'bought':r.side==='SELL'?'sold':'transferred'}",
    "{r.side==='BUY'?'bought':r.side==='SELL'?'sold':'transferred'}")

# 3. deckGroupTx: a loop → a BUY row + a SELL row sharing the transaction's one fee
rep_span("/* Audit V v23 (2026-10-25): the fee is charged per TRANSFER, not per Swap event.",
         "Fee legs unread for that tx → the old estimate, a loop once. */",
         "/* Audit V v23 (2026-10-25): the fee is charged per TRANSFER, not per Swap event. A loop (buy in one pool, sell in another,\n"
         "           one transaction) moves the token pool → pool once and pays ONE fee, but its two rows each lifted 5 %; a router-split buy\n"
         "           pays TWICE (pools → router → buyer) but lifted once per pool leg. So the tape lifts the fee actually paid: the tx's legs\n"
         "           into the token contract ÷ the contract's share × the full rate (the same reading the TRANSFER rows use); fee legs unread\n"
         "           for that tx → the old estimate, a loop once. A split is ONE BUY / SELL row. A loop was one purple ARB row (v23) until\n"
         "           2026-10-29 (Shaka: \"I just want buy or sell\"): it is its BUY row + its SELL row again, like DexScreener, and the two\n"
         "           SHARE the one fee by size (half each for a plain loop), so every total still counts it once. tools/deck-buy-sell.py */",
         "A loop was one purple ARB row (v23) until")
rep_span("            if(loop){\n              const tokens=Math.max(sum(buys,'tokens'),sum(sells,'tokens')),usd=tokens*st.price;",
         "pool:`${buys[0].pool} \\u2192 ${sells[0].pool}`,legs:g});\n              return;\n            }",
         "            if(loop){   // 2026-10-29: a BUY row + a SELL row, sharing the one fee by size — never an ARB row\n"
         "              const bt=sum(buys,'tokens'),stk=sum(sells,'tokens'),all=bt+stk;\n"
         "              const fee=feeTok!=null?feeTok*st.price:Math.max(bt,stk)*st.price*st.fee;   // the estimate counts a loop once, as before\n"
         "              [[buys,'BUY',bt],[sells,'SELL',stk]].forEach(([lg,side,tk])=>{const pools=[...new Set(lg.map(r=>r.pool))];\n"
         "                out.push({...lg[0],id:tx+':'+side.toLowerCase(),side,tokens:tk,usd:tk*st.price,gen:all>0?fee*tk/all:0,measured:feeTok!=null,\n"
         "                  pool:pools.length>1?`${pools[0]} +${pools.length-1}`:pools[0],legs:lg});});\n"
         "              return;\n"
         "            }",
         "// 2026-10-29: a BUY row + a SELL row, sharing the one fee by size")

# 4. the footnote under the tape: how "lifted" is read now (it still said the v4-era "a swap's lifted is an estimate")
rep("Trade size = token-side amount × current price; lifted = trade size × the live fee rate (transfers are sized from the fee leg that reaches the contract), split by the live bucket weights. A swap{'\\u2019'}s “lifted” is an estimate: the fee is charged per token transfer, so an arbitrage loop that shows here as a buy and a sell paid one fee, and a buy a router splits across pools paid two.",
    "Trade size = token-side amount × current price. Lifted = the fee the transaction actually paid, read from its fee transfers on chain (trade size × the live fee rate when that read is missing; transfers are sized from the fee leg that reaches the contract), split by the live bucket weights. The fee is charged per token transfer, so a buy in one pool and a sell in another in the same transaction paid one fee — its two rows share it — and a buy a router splits across pools paid two.",
    "its two rows share it")

P.write_text(s)
print(f'{edits} edit(s)')
