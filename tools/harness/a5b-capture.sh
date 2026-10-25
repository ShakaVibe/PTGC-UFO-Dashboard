#!/bin/bash
# Audit V batch B before/after (2026-10-25): LP Pairs Value Gen + Price 24h (v24, quote-side %), Combined Value Generated wording
# (v26/v28), UFO Value Generated panel. Frozen data/ (swap-volume.json from the v24 builder). Usage: bash a5b-capture.sh before|after
L=${1:-before}; O=out/a5b/$L; mkdir -p $O; export CHROME=${CHROME:-/opt/pw-browsers/chromium-1243/chrome-linux64/chrome} DS_PAIRS=burn
run(){ local name=$1; shift; timeout 200 node run.js "$@" > $O/$name.log 2>&1; }
[ "$L" = before ] && export HTML=index-before.html
LP="eval=document.querySelector('.p2-lphb').scrollIntoView({block:'start'}),window.scrollBy(0,-120);wait=800;shot=lp;eval=window.__sel='.p2-lp';evalfile=probes/a5-grab.js"
LPP="eval=(document.querySelector('.p2-lphp')||document.body).scrollIntoView({block:'start'}),window.scrollBy(0,-120);wait=800;shot=lp;eval=window.__sel='.p2-lp';evalfile=probes/a5-grab.js"
for T in ptgc ufo; do
 ( run lp-$T "#/$T" 1440 1300 $O/lp-$T "wait=7000;$LP"
   run lpphone-$T "#/$T" 390 1600 $O/lpphone-$T "wait=7000;$LPP"
   run vg-$T "#/$T" 1440 1000 $O/vg-$T "wait=7000;eval=window.__h3='Value Generated';eval=document.querySelector('[aria-label=\"Value Generated\"]').scrollIntoView({block:'start'}),window.scrollBy(0,-120);wait=800;shot=vg;evalfile=probes/a5-panel.js" ) &
done
( run soc-cvg "#/ptgc" 1440 1400 $O/soc "wait=6000;click=button:has-text('Socials'):visible;wait=1500;click=button:has-text('Combined Value Generated'):visible;wait=3500;shot=cvg;evalfile=probes/a5-grab.js" ) &
wait; ls $O | wc -l
