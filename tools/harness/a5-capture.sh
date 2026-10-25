#!/bin/bash
# Audit V before/after capture on the frozen data/ (2026-10-25). Usage: bash a5-capture.sh before|after
L=${1:-before}; O=out/a5/$L; mkdir -p $O; export CHROME=${CHROME:-/opt/pw-browsers/chromium-1243/chrome-linux64/chrome} DS_PAIRS=burn
run(){ local name=$1; shift; timeout 200 node run.js "$@" > $O/$name.log 2>&1; }
VGP=""; for p in 24h 7d 30d 90d; do VGP="$VGP;click=[aria-pressed] >> text='${p^^}' >> nth=0;wait=900;evalfile=probes/a5-panel.js"; done
HV=""; for t in PTGC UFO BOTH; do HV="$HV;click=[role=dialog] button:text-is('$t');wait=900"; for p in 24H 7D 30D 90D; do HV="$HV;click=[role=dialog] button:text-is('$p');wait=700;evalfile=probes/a5-grab.js"; done; HV="$HV;shot=hvb-$t"; done
for T in ptgc ufo; do
 ( run dash-$T "#/$T" 1440 900 $O/dash-$T "wait=7000;evalfile=probes/a5-body.js;eval=window.__h3='Value Generated'$VGP"
   run hvb-$T "#/$T" 1440 1700 $O/hvb-$T "wait=6000;click=button[aria-label^='Humans vs Bots'];wait=2500$HV;click=[role=dialog] button:text-is('PTGC');click=[role=dialog] button:text-is('30D');click=button[aria-label='Share Humans vs Bots as an image'];wait=2500;shot=card;evalfile=probes/a5-grab.js"
   run vol-$T "#/$T" 1440 1700 $O/vol-$T "wait=6000;click=button[aria-label='Volume by period'];wait=2500;shot=win;evalfile=probes/a5-grab.js"
   run kpi-$T "#/$T" 1440 1700 $O/kpi-$T "wait=6000;click=button:has-text('KPI Report'):visible;wait=3500;shot=kpi;evalfile=probes/a5-body.js"
   DECK_LOGS=8 run deck-$T "#/$T" 1440 1000 $O/deck-$T "wait=5000;click=button:has-text('Live Feed'):visible;wait=9000;shot=deck;evalfile=probes/a5-grab.js" ) &
done
( run soc-ptgc "#/ptgc" 1440 1400 $O/soc "wait=6000;click=button:has-text('Socials'):visible;wait=1500;click=button:has-text('Value Generated'):visible;wait=3000;shot=vgcard;evalfile=probes/a5-grab.js;key=Escape;wait=600;click=button:has-text('Combined Value Generated'):visible;wait=3500;shot=cvg;evalfile=probes/a5-grab.js;key=Escape;wait=600;click=button:has-text('Humans vs Bots') >> nth=0;wait=3500;shot=hvbsoc;evalfile=probes/a5-grab.js"
  for t in growth rewards fresh; do lab=$(case $t in growth) echo '10 Yr Projection';; rewards) echo Rewards;; fresh) echo 'New Capital Simulator';; esac)
   HTML=calculators.html run calc-$t "?from=PTGC" 1440 2200 $O/calc-$t "wait=5000;click=button:has-text('$lab'):visible;wait=3000;shot=ptgc;evalfile=probes/a5-body.js;click=button:has-text('Switch'):visible;wait=7000;shot=ufo;evalfile=probes/a5-body.js"; done
  HTML=ledger.html run ledger "" 1440 1600 $O/ledger "wait=7000;shot=top;evalfile=probes/a5-body.js" ) &
wait; ls $O | wc -l
