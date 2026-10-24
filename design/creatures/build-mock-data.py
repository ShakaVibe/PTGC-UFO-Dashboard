#!/usr/bin/env python3
"""Creature history mock data (2026-10-24): walks data/rank-history/<TOKEN>.json day by day (every PEOPLE holder's balance —
contracts, burn, DAO, LP excluded, the same population as the Token Allocation strip since e13) and counts the eight leagues
per UTC day on two bases: % of the STARTING supply (the strip) and % of the CIRCULATING supply (starting − burned that day,
the Leagues window's toggle). Also joined / left per league for 7D / 30D / 90D / 6M / 1Y / ALL (a wallet's league at the
period's first day vs the last day). Writes design/creatures/mock-data.js. Run from the repo root."""
import json, glob, datetime, collections
TIERS = [('Poseidon', 10), ('Whale', 1), ('Shark', .1), ('Dolphin', .01), ('Squid', .001), ('Turtle', .0001), ('Shrimp', .00001), ('Shell', 0)]
SUP = {'PTGC': 333333333333, 'UFO': 999999999051}
PER = [('7D', 7), ('30D', 30), ('90D', 90), ('6M', 182), ('1Y', 365), ('ALL', None)]
day = lambda ms: datetime.datetime.fromtimestamp(ms / 1000, datetime.UTC).strftime('%Y-%m-%d')

def burns(tok):
    by = collections.Counter()
    if tok == 'PTGC':
        for f in glob.glob('data/ptgc-burns-20*.json'):
            for r in json.load(open(f))['burns']: by[day(r['t'])] += r['a']
    else:
        for r in json.load(open('data/ufo-ptgc-burns-cache.json'))['_ufoBurnsCache']:
            if r.get('c') == 'v2': by[day(r['t'])] += r['a']
    return by

def tier(v, sup):
    p = v / sup * 100
    for i, (_, t) in enumerate(TIERS):
        if p >= t: return i
    return 7

out = {}
for tok in ('PTGC', 'UFO'):
    d = json.load(open(f'data/rank-history/{tok}.json'))
    days = sorted(d['days']); S = SUP[tok]; by = burns(tok)
    pre = sum(a for k, a in by.items() if k < days[0])
    need = {}
    for lab, n in PER:
        k = days[0] if n is None or n >= len(days) else days[-1 - n]
        need.setdefault(k, []).append(lab)
    cur = {}; cum = pre; rows = []; snaps = {}
    for k in days:
        r = d['days'][k]; f = r.get('f', 1)
        if f != 1:
            for a in cur: cur[a] *= f
        for a, v in (r.get('m') or {}).items():
            if v > 0: cur[a] = v
            else: cur.pop(a, None)
        cum += by.get(k, 0); circ = S - cum
        cs, cc = [0] * 8, [0] * 8
        for v in cur.values(): cs[tier(v, S)] += 1; cc[tier(v, circ)] += 1
        rows.append([k, cs, cc, round(circ)])
        if k in need or k == days[-1]:
            snaps[k] = ({a: tier(v, S) for a, v in cur.items()}, {a: tier(v, circ) for a, v in cur.items()})
    last = snaps[days[-1]]; flows = {}
    for k, labs in need.items():
        first = snaps[k] if k != days[0] else ({}, {})   # ALL: everyone started outside
        fl = []
        for b in (0, 1):
            a0, a1 = first[b], last[b]; j = [0] * 8; l = [0] * 8
            for a in set(a0) | set(a1):
                t0, t1 = a0.get(a), a1.get(a)
                if t0 == t1: continue
                if t1 is not None: j[t1] += 1
                if t0 is not None: l[t0] += 1
            fl.append([j, l])
        for lab in labs: flows[lab] = {'from': k, 'start': fl[0], 'circ': fl[1]}
    out[tok] = {'day0': days[0], 'rows': rows, 'flows': flows, 'supply': S}
    print(tok, len(rows), 'days; last', rows[-1][0], rows[-1][1], 'circ', rows[-1][2], 'circSupply', rows[-1][3])
open('design/creatures/mock-data.js', 'w').write('window.CRE=' + json.dumps(out, separators=(',', ':')) + ';\n')
