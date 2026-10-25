#!/usr/bin/env python3
"""Audit V (2026-10-25) — measure the REAL PTGC / UFO fees from their fee legs and compare with what the site's formulas give.

  python3 tools/audit5-measure-fees.py 90            # scan the chain (90 days), write audit5-fees-90.json   (~10 min, public RPC)
  python3 tools/audit5-measure-fees.py --table 90    # print the truth table from that file + data/*.json

PTGC: a taxed transfer emits, from the same sender in the same tx, 0.5 % -> 0x...0369 and 1 % -> 0xc71f... (the staking contract)
(+ 2.5 % -> the PTGC contract, ~1 % reflections with no event). A burn leg whose tx holds a staking leg of exactly 2x from the same
sender is a fee leg; taxed gross = burn leg / 0.005; fee = gross x 5 %.  UFO: every transfer into the UFO contract (not sent by the
contract itself) is the 5 % leg; gross = leg / 0.05; fee = gross x 6 % (5 % + ~1 % reflections at today's rates).
Classes come from data/swap-volume-cache.json (tx prefix + block): any bot leg -> bot, only router legs -> human, no tracked swap ->
transfer. Prices: data/charts-intraday.json hourly, data/charts-data.json daily beyond it. Reference for roadmap item v12.
Run from the repo root. Stdlib only.
"""
import json, sys, time, bisect, collections, urllib.request
from concurrent.futures import ThreadPoolExecutor

RPC = 'https://rpc.pulsechain.com'
T = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
PTGC = '0x94534eeee131840b1c0f61847c572228bdfdde93'
UFO = '0x49ed499433bee42dd34c169470fef2c8f9fae6e6'
BURN = '0x0000000000000000000000000000000000000369'
STAKING = '0xc71f597a2ac39e47f07102e849d18489c96f39ef'
pad = lambda a: '0x' + '0' * 24 + a[2:].lower()


def rpc(m, p):
    err = None
    for i in range(8):
        try:
            req = urllib.request.Request(RPC, json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': m, 'params': p}).encode(),
                                         {'content-type': 'application/json'})
            j = json.loads(urllib.request.urlopen(req, timeout=90).read())
            if 'error' in j:
                raise Exception(j['error'])
            return j['result']
        except Exception as e:
            err = e
            time.sleep(1.5 * (i + 1))
    raise err


def scan(days):
    head = int(rpc('eth_blockNumber', []), 16) - 3
    start = head - int(days * 8640)

    def logs(addr, t2, step=4000):
        rng = [(s, min(s + step - 1, head)) for s in range(start, head + 1, step)]

        def f(r):
            try:
                return rpc('eth_getLogs', [{'address': addr, 'topics': [T, None, t2], 'fromBlock': hex(r[0]), 'toBlock': hex(r[1])}])
            except Exception:
                m = (r[0] + r[1]) // 2
                return f((r[0], m)) + f((m + 1, r[1]))
        with ThreadPoolExecutor(6) as ex:
            return [l for part in ex.map(f, rng) for l in part]

    amt = lambda l: int(l['data'], 16) / 1e18
    b, k = logs(PTGC, pad(BURN)), logs(PTGC, pad(STAKING))
    stk = collections.defaultdict(list)
    for l in k:
        stk[l['transactionHash']].append((l['topics'][1], amt(l)))
    fee, nonfee = [], 0.0
    for l in b:
        a, frm = amt(l), l['topics'][1]
        if any(x[0] == frm and abs(x[1] - 2 * a) <= max(1e-6, 2 * a * 1e-6) for x in stk.get(l['transactionHash'], [])):
            fee.append((l['transactionHash'], int(l['blockNumber'], 16), frm, a))
        else:
            nonfee += a
    u = logs(UFO, pad(UFO))
    out = {'head': head, 'start': start, 'headTs': int(rpc('eth_getBlockByNumber', [hex(head), False])['timestamp'], 16),
           'ptgc': {'fee': fee, 'nonFeeBurn': nonfee, 'stakeInflows': len(k)},
           'ufo': {'toContract': [(l['transactionHash'], int(l['blockNumber'], 16), l['topics'][1], amt(l)) for l in u]}}
    name = f'audit5-fees-{int(days)}.json'
    json.dump(out, open(name, 'w'))
    print(f'wrote {name}: {len(fee)} PTGC fee legs, {len(u)} UFO contract legs')


def table(days):
    ci, cd = json.load(open('data/charts-intraday.json')), json.load(open('data/charts-data.json'))

    def pricer(tk):
        H = {int(t // 3600000): p for t, p in ci['tokens'][tk]['hourly']['series']}
        D = sorted(cd['tokens'][tk]['series'])
        Dt = [x[0] for x in D]

        def px(ms):
            k = int(ms // 3600000)
            for i in range(6):
                if H.get(k - i, 0) > 0:
                    return H[k - i]
            j = bisect.bisect_right(Dt, ms) - 1
            return D[j][1] if j >= 0 else None
        return px
    PX = {'PTGC': pricer('PTGC'), 'UFO': pricer('UFO')}
    cache = json.load(open('data/swap-volume-cache.json'))
    cls = {}
    for r in cache['swaps']:   # [ts, block, tx10, pool#, sender#, kind(1=human), ...]
        key = (r[2], r[1])
        if r[5] == 0:
            cls[key] = 'bot'
        elif key not in cls:
            cls[key] = 'human'
    sv, cg = json.load(open('data/swap-volume.json')), json.load(open('data/coingecko-data.json'))
    f = json.load(open(f'audit5-fees-{int(days)}.json'))
    head, hts = f['head'], f['headTs'] * 1000
    tsof = lambda b: hts - (head - b) * 10000
    ufo_self = pad(UFO)
    for tk in ('PTGC', 'UFO'):
        if tk == 'PTGC':
            legs, rate = [(tx, b, a / 0.005) for tx, b, frm, a in f['ptgc']['fee']], 0.05
        else:
            legs, rate = [(tx, b, a / 0.05) for tx, b, frm, a in f['ufo']['toContract'] if frm != ufo_self], 0.06
        for p, d in (('24h', 1), ('7d', 7), ('30d', 30), ('90d', 90)):
            if d > days:
                continue
            cut, tot = head - d * 8640, collections.Counter()
            for tx, b, g in legs:
                if b < cut:
                    continue
                pr = PX[tk](tsof(b))
                if pr:
                    tot[cls.get((tx[:10], b), 'transfer')] += g * pr * rate
            o = sv['tokens'][tk]['periods'][p]
            vh, vb = o['human']['usd'], o['bot']['usd']
            real = sum(tot.values()) or 1
            cgv = cg[tk]['volume'].get('vol' + p) if p != '24h' else None
            print(f"{tk} {p:>3}: REAL ${real:,.0f} (people ${tot['human']:,.0f} · bots ${tot['bot']:,.0f} · transfers "
                  f"${tot['transfer']:,.0f}; bot share {tot['bot'] / real * 100:.0f}%) | swap legs x fee ${(vh + vb) * rate:,.0f} "
                  f"(bot {vb / max(vh + vb, 1) * 100:.0f}%) | CoinGecko x fee {'$%s' % format(cgv * rate, ',.0f') if cgv else '-'}")


if __name__ == '__main__':
    if sys.argv[1] == '--table':
        table(float(sys.argv[2]))
    else:
        scan(float(sys.argv[1]))
