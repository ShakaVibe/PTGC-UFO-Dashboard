#!/usr/bin/env python3
"""Audit IV (handover/sessions/2026-10-22-audit4.md) — e1 + e2, 2026-10-23. Idempotent, run from the repo root:
    python3 tools/audit4-e1e2.py        (run it twice: the second run must print "0 edit(s)")

e1  Top 100 "Your cushion": tools/top100/t1.jsx subtracts list[99] (the overall #101 once the checked wallet is taken out of
    the list), not list[100]. The script edits the FRAGMENT and then re-splices index.html via tools/top100.py.
e2  portfolio.html — the UFO reflections scan (computeUfoReflectionsWei):
    (a) getLogsChunked / _getLogsChunked take `exactTo` (index.html's gotcha-4 flag): the last slice is sent as toBlock:<head>,
        never 'latest', so what is cached as {to:head} is exactly what was read — a transfer mined between head and 'latest' was
        counted now AND again by the next visit's incremental scan (c.to+1 → head').
    (b) the wallet's balance is read at block `head` inside the scan (one eth_call with a block tag) so balance and the two
        sums come from the same block; a failed at-head read falls back to the mount-time balance (the old behaviour).
"""
import re, subprocess, sys

n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:80]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new))
    n += 1

# ---- e1 — the fragment, then the splice --------------------------------------------------------------------------------
edit('tools/top100/t1.jsx',
     "        const cush=Math.max(0,k-(list[100]||0));\n",
     "        /* Audit IV e1 (2026-10-23): `list` has the checked wallet removed, so list[99] IS the overall #101 — the line the wallet\n"
     "           drops under. list[100] was #102 and made every cushion too generous by list[99]−list[100]. */\n"
     "        const cush=Math.max(0,k-(list[99]||0));\n")
out = subprocess.run([sys.executable, 'tools/top100.py'], capture_output=True, text=True).stdout.strip().splitlines()[-1]
print('  ' + out)

# ---- e2 — portfolio.html ---------------------------------------------------------------------------------------------
P = 'portfolio.html'
edit(P,
     "    const getLogsChunked=async(address,topics,fromBlock,toBlock)=>{\n"
     "      if(toBlock<fromBlock)return[];\n"
     "      const key=`${address}|${JSON.stringify(topics)}|${fromBlock}|${toBlock}|${cacheBucket()}`;\n"
     "      if(logsInflight[key])return logsInflight[key];\n"
     "      const p=_getLogsChunked(address,topics,fromBlock,toBlock);\n",
     "    /* exactTo (Audit IV e2, 2026-10-23 — index.html's gotcha-4 flag, ported): getLogsRange sends the final slice as\n"
     "       toBlock:'latest' when it reaches the scan's end block. For a scan that is CACHED as \"read to block N\" that is wrong:\n"
     "       'latest' silently extends the last slice past N, and the next incremental scan (N+1 → head') reads those blocks\n"
     "       again — a transfer mined in the gap was double-counted into the UFO reflections for ever. exactTo=true pins it. */\n"
     "    const getLogsChunked=async(address,topics,fromBlock,toBlock,exactTo=false)=>{\n"
     "      if(toBlock<fromBlock)return[];\n"
     "      const key=`${address}|${JSON.stringify(topics)}|${fromBlock}|${toBlock}|${exactTo?1:0}|${cacheBucket()}`;\n"
     "      if(logsInflight[key])return logsInflight[key];\n"
     "      const p=_getLogsChunked(address,topics,fromBlock,toBlock,exactTo);\n")
edit(P,
     "    const _getLogsChunked=async(address,topics,fromBlock,toBlock)=>{\n",
     "    const _getLogsChunked=async(address,topics,fromBlock,toBlock,exactTo=false)=>{\n")
edit(P,
     "        const res=await Promise.all(ranges.slice(i,i+CONC).map(([a,b])=>getLogsRange(address,topics,a,b,0,toBlock)));\n",
     "        const res=await Promise.all(ranges.slice(i,i+CONC).map(([a,b])=>getLogsRange(address,topics,a,b,0,exactTo?Infinity:toBlock)));\n")
# the scan: exact end + balance at that block
edit(P,
     "      const head=await getHeadBlock();\n"
     "      if(head==null)return null;\n"
     "      // Scan the token's ENTIRE history, from its deploy block to head.",
     "      const head=await getHeadBlock();\n"
     "      if(head==null)return null;\n"
     "      /* Audit IV e2: balance and the two transfer sums must be from ONE block, or a transfer that lands while the scan runs\n"
     "         skews the result by its whole size. Read balanceOf AT `head` (the block the scan ends on); if the node will not\n"
     "         answer for that block, keep the mount-time balance (the pre-e2 behaviour, never a fake 0). */\n"
     "      try{\n"
     "        const r=await rpcFetch({jsonrpc:'2.0',method:'eth_call',params:[{to:UFO_TOKEN_ADDR,data:SEL.balanceOf+padAddr(address)},'0x'+head.toString(16)],id:1});\n"
     "        const h=r&&r.result;if(h&&h!=='0x'&&h.length>=66)balanceWei=parseWord(h);\n"
     "      }catch(e){}\n"
     "      if(balanceWei<=0n)return 0;\n"
     "      // Scan the token's ENTIRE history, from its deploy block to head.")
edit(P,
     "          getLogsChunked(UFO_TOKEN_ADDR,[TRANSFER_TOPIC,null,wtopic],fromBlock,head),   // to = wallet\n"
     "          getLogsChunked(UFO_TOKEN_ADDR,[TRANSFER_TOPIC,wtopic,null],fromBlock,head),   // from = wallet\n",
     "          getLogsChunked(UFO_TOKEN_ADDR,[TRANSFER_TOPIC,null,wtopic],fromBlock,head,true),   // to = wallet   (exactTo: never 'latest')\n"
     "          getLogsChunked(UFO_TOKEN_ADDR,[TRANSFER_TOPIC,wtopic,null],fromBlock,head,true),   // from = wallet\n")

import hashlib
print(f'audit4-e1e2: {n} edit(s), portfolio.html sha256 {hashlib.sha256(open(P,"rb").read()).hexdigest()[:8]}, '
      f'index.html sha256 {hashlib.sha256(open("index.html","rb").read()).hexdigest()[:8]}')
