#!/usr/bin/env python3
"""Audit IV e33 / D-4 (2026-10-24, Shaka: "2 yes"): every pipeline script's PulseChain RPC calls go through ONE pool,
scripts/rpc-pool.js (rpc.pulsechain.com first, then rpc-pulsechain.g4mm4.io and pulsechain-rpc.publicnode.com — the pages'
a41 list), with a HEAD CHECK: a call that names a block only goes to a node that has reached it, so a lagging fallback can
never answer an incremental eth_getLogs with an empty list and make a scan skip blocks for good. While the primary is
healthy nothing changes (it is always tried first). Each script keeps its own retries / range halving; the pool only
picks the endpoint. Idempotent, from the repo root:   python3 tools/pipeline-rpc-pool.py   (twice: "0 edit(s)")
Needs scripts/rpc-pool.js (committed with this script).
"""
import hashlib, os, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

if not os.path.exists('scripts/rpc-pool.js'): sys.exit('scripts/rpc-pool.js is missing — it ships with this script')
IMP = "import rpcPool from './rpc-pool.js';   // Audit IV e33 / D-4: the shared RPC pool with a head check (scripts/rpc-pool.js)\n"

# ---- fetch-burn-history.js (CommonJS; fetch-ufo-ptgc-burns.js uses its rpcCall, so it is covered too)
F = 'scripts/fetch-burn-history.js'
edit(F, "const RPC_URL = 'https://rpc.pulsechain.com';\n",
        "const RPC_URL = 'https://rpc.pulsechain.com';   // the pool's primary; the calls go through scripts/rpc-pool.js (Audit IV e33 / D-4)\nconst rpcPool = require('./rpc-pool.js');\n")
edit(F, "      const res = await fetch(RPC_URL, {\n        method: 'POST',",
        "      const res = await rpcPool.poolFetch({\n        attemptMs: 30000,\n        method: 'POST',")
edit(F, "      const res = await fetch(RPC_URL, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: controller.signal });",
        "      const res = await rpcPool.poolFetch({ attemptMs: 60000, method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body), signal: controller.signal });")

# ---- the .mjs scripts with a small rpc()
for F, ms, old in (
    ('scripts/build-dao-buys.mjs', 20000, "      const res = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' },\n"),
    ('scripts/build-new-holders.mjs', 30000, "      const res = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' },\n"),
    ('scripts/build-swap-volume.mjs', 30000, "      const res = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' }, body:"),
    ('scripts/build-rank-history.mjs', 30000, "      const r = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' }, body:"),
    ('scripts/build-token-allocation.mjs', 20000, "      const r = await fetch(RPC, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(body) });"),
):
    edit(F, "import fs from 'node:fs';\n", "import fs from 'node:fs';\n" + IMP)
    edit(F, old, old.replace('await fetch(RPC, { method:', f'await rpcPool.poolFetch({{ attemptMs: {ms}, method:'))

# ---- top-stakers: its own round-robin over RPC_URLS → the pool (which reads RPC_URLS too)
F = 'scripts/build-top-stakers.mjs'
edit(F, "import fs from 'node:fs';\n", "import fs from 'node:fs';\n" + IMP)
edit(F, "    const url = RPCS[(rr++) % RPCS.length];\n    try {\n      const r = await fetch(url, { method: 'POST', signal: AbortSignal.timeout(20000), headers:",
        "    try {   // the pool picks the endpoint (primary first; RPC_URLS still overrides the list)\n      const r = await rpcPool.poolFetch({ attemptMs: 20000, method: 'POST', headers:")

# ---- value-generated (lifted from index.html; keeps its 8 s per try)
F = 'scripts/build-value-generated.mjs'
edit(F, "import fs from 'node:fs';\n", "import fs from 'node:fs';\n" + IMP)
edit(F, "        const res=await fetch(RPC,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:controller.signal});",
        "        const res=await rpcPool.poolFetch({attemptMs:timeout,method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body),signal:controller.signal});")

sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'pipeline-rpc-pool: {n} edit(s); rpc-pool.js {sha("scripts/rpc-pool.js")}')
