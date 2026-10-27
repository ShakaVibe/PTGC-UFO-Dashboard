#!/usr/bin/env python3
"""Humans vs Bots — the COUNT switch OFF (2026-10-27, same day as tools/hvb-count-switch.py). Shaka: "actually take the
selector off... just make it match dex screener".

The window and the share card always count every swap (DexScreener's way, = the Volume window). Only the two pill groups go;
the `count` plumbing (vsView / vsShow / HvbShareCard, default 'swaps') stays, so EACH TX can come back by restoring one line.
The note under the boxes still gives the each-transaction-once figure and bot share. Run AFTER hvb-count-switch.py.

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

rep("\n                {view&&view.m&&<NhPills items={VS_COUNT} value={vsCountK(count)} onChange={k=>setCount(vsCountOf(k))} label=\"Count\" rgb={rgb}/>}",
    "{/* COUNT switch removed 2026-10-27 (Shaka: \"just make it match dex screener\") — always every swap */}",
    "{/* COUNT switch removed 2026-10-27")
rep("\n        {setCount&&<NhPills items={VS_COUNT} value={vsCountK(count)} onChange={k=>setCount(vsCountOf(k))} label=\"Count\" rgb={T.rgb}/>}",
    "",
    "COUNT switch removed 2026-10-27 (share card)")
rep("const HvbShareModal=({token:initial,file,win,setWin,count='swaps',setCount,",
    "const HvbShareModal=({token:initial,file,win,setWin,count='swaps',setCount,   // COUNT switch removed 2026-10-27 (share card): count stays 'swaps'\n      ",
    "COUNT switch removed 2026-10-27 (share card)")
rep("The volume counts every swap, the way DexScreener does (EACH TX counts a bot{'\\u2019'}s loop {'\\u2014'} two swaps, one fee {'\\u2014'} once), and the fees are read from the chain.",
    "The volume counts every swap, the way DexScreener does (a bot{'\\u2019'}s loop is two swaps but one transaction and one fee), and the fees are read from the chain.",
    "(a bot{'\\u2019'}s loop is two swaps but one transaction and one fee)")

P.write_text(s)
print(f'{edits} edit(s)')
