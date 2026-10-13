#!/usr/bin/env python3
"""UFO reflections earned on the OLD UFO contract — one-time build of data/ufo-v1-earned/{0-f}.json.

Why (Shaka, 2026-10-13: "are these rewards just from the new contract? … hopefully it includes the old one"):
the portfolio's UFO reflections are  balance − (received − sent)  on the NEW contract only. The migration airdrop
counts as "received" there, and that airdrop was each wallet's OLD balance — reflections earned on the old contract
included — so without this file those old reflections are counted as principal, not as earned.

Facts it rests on (all checked on chain 2026-10-13):
  · old UFO 0x456548A9B56eFBbD89Ca0309edd17a9E20b04018, deployed at block 20,262,928.
  · migration snapshot = state after block 26,963,880 (2026-07-06 12:29 UTC): every airdrop the distributor
    0xcfcb00f1… sent on the NEW contract (5,168 transfers, blocks 26,990,368–26,990,857) equals ROUND(old balanceOf at
    that block) — 477 of 478 sampled wallets within ±0.5 token (the 478th is 0x0). So a recipient's snapshot balance is
    taken from its airdrop; everyone else's is read with balanceOf at the snapshot block.
  · old fee 5 % + a 1 % holders' share with NO Transfer event (same as the new contract): on a fee-paying send the leg to
    the token contract is 5/95 of the other legs (328,535 of 330,000 sends; the rest are dust) and the balance falls by
    emitted + (that leg ÷ 5). BUT the old contract also received tokens with no fee: addLiquidity through the old token
    routed the UFO to the contract itself (wallet balance fell by exactly the amount, no hidden 1 %). So the hidden 1 % is
    added back only for the part of a to-contract leg that matches 5/95 of the same tx's other sends.
  · earned = snapshot balance − received + sent + hidden 1 %, floored at 0. Liquidity adds / removes are netted as
    sent / received, so a position that came back with more UFO than went in (price fell — impermanent loss) lowers the
    figure; that is why it is floored rather than allowed negative.

Output: data/ufo-v1-earned/<first hex char of the address>.json = {"<address lowercase, no 0x>": whole tokens}, plus
data/ufo-v1-earned/meta.json. Only wallets that earned ≥ 1 token are listed. The old contract is frozen at the snapshot,
so this never needs re-running. Usage:  python3 tools/ufo-v1-earned.py <work-dir>   (work-dir caches every RPC answer;
a cold run is ~350 eth_getLogs calls + ~100 batched balanceOf calls on rpc.pulsechain.com, archive node, ~1–2 h).
"""
import concurrent.futures as cf, glob, json, os, ssl, sys, time, urllib.request

RPC = 'https://rpc.pulsechain.com'
OLD = '0x456548A9B56eFBbD89Ca0309edd17a9E20b04018'
NEW = '0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6'
DIST = 'cfcb00f1b13c1738f4eae45a1dde20f4c9d3b636'
T = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
OLD_DEPLOY, SNAPSHOT = 20262928, 26963880
AIR_FROM, AIR_TO = 26989200, 26992000
ctx = ssl.create_default_context(cafile=os.environ.get('SSL_CERT_FILE') or None)
W = sys.argv[1] if len(sys.argv) > 1 else '/tmp/ufo-v1'
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def post(body, timeout=120):
    for t in range(6):
        try:
            return json.loads(urllib.request.urlopen(urllib.request.Request(RPC, json.dumps(body).encode(),
                              {'content-type': 'application/json'}), context=ctx, timeout=timeout).read())
        except Exception as e:  # noqa
            err = e; time.sleep(2 + 2 * t)
    raise RuntimeError(err)


def logs(addr, topics, a, b):
    r = post({'jsonrpc': '2.0', 'id': 1, 'method': 'eth_getLogs',
              'params': [{'address': addr, 'topics': topics, 'fromBlock': hex(a), 'toBlock': hex(b)}]})
    return r.get('result')


def fetch_old_logs():
    d = f'{W}/logs'; os.makedirs(d, exist_ok=True)

    have = [tuple(map(int, os.path.basename(x)[:-5].split('-'))) for x in glob.glob(f'{d}/*.json')]

    def covered(a, b):  # already fetched as one file or as split halves
        cur = a
        for x, y in sorted(r for r in have if a <= r[0] and r[1] <= b):
            if x != cur: return False
            cur = y + 1
        return cur == b + 1

    def rng(a, b):
        f = f'{d}/{a}-{b}.json'
        if covered(a, b): return
        try: r = logs(OLD, [T], a, b)
        except RuntimeError: r = None   # a too-big answer comes back cut off → split
        if r is None or len(r) >= 9000:
            m = (a + b) // 2; rng(a, m); rng(m + 1, b); return
        json.dump([[l['blockNumber'], l['transactionHash'], l['topics'][1][-40:], l['topics'][2][-40:], l['data']] for l in r],
                  open(f + '.tmp', 'w')); os.rename(f + '.tmp', f)
    jobs = [(s, min(s + 19999, SNAPSHOT)) for s in range(OLD_DEPLOY, SNAPSHOT + 1, 20000)]
    with cf.ThreadPoolExecutor(4) as ex: list(ex.map(lambda j: rng(*j), jobs))
    rs = sorted(tuple(map(int, os.path.basename(f)[:-5].split('-'))) for f in glob.glob(f'{d}/*.json'))
    cur = OLD_DEPLOY
    for a, b in rs:
        assert a == cur, f'gap {cur}..{a}'; cur = b + 1
    assert cur == SNAPSHOT + 1


def airdrops():
    f = f'{W}/air.json'
    if os.path.exists(f): return {k: int(v) for k, v in json.load(open(f)).items()}
    air = {}
    for l in logs(NEW, [T, '0x' + DIST.rjust(64, '0')], AIR_FROM, AIR_TO):
        a = l['topics'][2][-40:]; air[a] = air.get(a, 0) + int(l['data'], 16)
    json.dump({k: str(v) for k, v in air.items()}, open(f, 'w')); return air


def balances(addrs):
    f = f'{W}/bal.json'
    bal = json.load(open(f)) if os.path.exists(f) else {}
    need = [a for a in addrs if a not in bal]
    for i in range(0, len(need), 40):
        ch = need[i:i + 40]
        r = post([{'jsonrpc': '2.0', 'id': j, 'method': 'eth_call',
                   'params': [{'to': OLD, 'data': '0x70a08231' + a.rjust(64, '0')}, hex(SNAPSHOT)]} for j, a in enumerate(ch)])
        by = {x['id']: x for x in r}
        for j, a in enumerate(ch): bal[a] = str(int(by[j]['result'], 16))
        json.dump(bal, open(f, 'w'))
    return {a: int(bal[a]) for a in addrs}


def main():
    os.makedirs(W, exist_ok=True)
    fetch_old_logs()
    OL = OLD.lower()[2:]
    inn, out, per = {}, {}, {}
    for f in glob.glob(f'{W}/logs/*.json'):
        for _b, h, fr, to, data in json.load(open(f)):
            v = int(data, 16) if data != '0x' else 0
            inn[to] = inn.get(to, 0) + v; out[fr] = out.get(fr, 0) + v
            c, o = per.get((h, fr), (0, 0)); per[(h, fr)] = (c + v, o) if to == OL else (c, o + v)
    hid = {}
    for (h, fr), (c, o) in per.items():
        if c and o: hid[fr] = hid.get(fr, 0) + min(c, o * 5 // 95) // 5
    air = airdrops()
    addrs = sorted(set(inn) | set(out))
    bal = balances([a for a in addrs if a not in air])
    skip = {'0' * 40, '0' * 37 + '369', '0' * 36 + 'dead', OL}
    shards = {c: {} for c in '0123456789abcdef'}; n = 0; tot = 0
    for a in addrs:
        if a in skip: continue
        b = air.get(a, bal.get(a, 0))
        e = (b - inn.get(a, 0) + out.get(a, 0) + hid.get(a, 0)) // 10 ** 18
        if e >= 1: shards[a[0]][a] = e; n += 1; tot += e
    od = f'{REPO}/data/ufo-v1-earned'; os.makedirs(od, exist_ok=True)
    for c, m in shards.items(): json.dump(m, open(f'{od}/{c}.json', 'w'), separators=(',', ':'), sort_keys=True)
    json.dump({'contract': OLD, 'deployBlock': OLD_DEPLOY, 'snapshotBlock': SNAPSHOT, 'snapshotUtc': '2026-07-06T12:29:55Z',
               'wallets': n, 'totalTokens': tot, 'built': time.strftime('%Y-%m-%d'),
               'note': 'Whole UFO reflections earned on the old contract up to the migration snapshot. See tools/ufo-v1-earned.py.'},
              open(f'{od}/meta.json', 'w'), indent=1)
    print(f'{n} wallets, {tot:,} tokens → {od}')


if __name__ == '__main__':
    main()
