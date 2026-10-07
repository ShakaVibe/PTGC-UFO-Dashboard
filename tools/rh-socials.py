#!/usr/bin/env python3
"""Socials → RH Core Liquidity rows for PTGC and UFO (2026-10-07). Shaka: "lets add the RH core liquidity to the socials as well. We
already have the combined one.. leave it alone.. but we can add the one you just created to PTGC and UFO."

Idempotent: python3 tools/rh-socials.py [index.html] (after tools/rh-cores.py). Three edits:
  1. a "RH Core Liquidity" ShRow in the PTGC column, right after Humans vs Bots — LEVEL with the Combined column's RH Core Liquidity
     row (so Token Allocation now sits level with Leagues, Targets with The Grays & The Cores);
  2. the same row in the UFO column;
  3. the RH window's onClose → closeModalAndReturn, so closing it from the Socials returns to the hub (the Holders row's pattern).
The rows switch the dashboard to the token first (the window reads the Dashboard's rhCoresPairs), like the Holders / Burn rows.
"""
import sys, hashlib

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()
if 'title="RH Core Liquidity" sub="PTGC LP with the RH cores"' in src:
    print('already applied'); sys.exit(0)
assert 'const RhCoresModal=' in src, 'run tools/rh-cores.py first'

def row(tk):
    return (f'                  <ShRow tone="blue" icon=\'logos/panels/vg-droplet.webp\' title="RH Core Liquidity" sub="{tk} LP with the RH cores" '
            f'onClick={{()=>{{setSocialReturn(true);if(token!==\'{tk}\')onSwitch(\'{tk}\');setTimeout(()=>setShowRHModal(true),100)}}}}/>'
            f'{{/* 2026-10-07: the RH Cores window from the hub, level with the Combined column\'s RH row (tools/rh-socials.py) */}}\n')

for tk in ('PTGC', 'UFO'):
    anchor = f"""title="Humans vs Bots" sub="Who moves the volume" onClick={{()=>{{setSocialReturn(true);setShowHvbShare('{tk}')}}}}/>\n"""
    assert src.count(anchor) == 1, f'{tk} Humans vs Bots row not found once'
    i = src.index(anchor) + len(anchor)
    src = src[:i] + row(tk) + src[i:]

old = "pairs={rhCoresPairs} totalLiq={data?.liq} onClose={()=>setShowRHModal(false)}/>"
assert src.count(old) == 1
src = src.replace(old, "pairs={rhCoresPairs} totalLiq={data?.liq} onClose={()=>closeModalAndReturn(setShowRHModal)}/>")

open(path, 'w', encoding='utf-8').write(src)
print('applied', path, 'md5', hashlib.md5(src.encode('utf-8')).hexdigest())
