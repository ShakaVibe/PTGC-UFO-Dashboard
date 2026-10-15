#!/usr/bin/env python3
"""Round 31 (2026-10-15): which UFO balances are EXCLUDED from holder rewards (the contract is unverified, no getter).
Method: over the last 12,000 blocks an eligible holder's balance grows by reflections (~0.07 %); an excluded address's
balance moves only by its own transfers (+ the hidden 1 % on its fee-paying sends). Scans the top holders (PulseScan
API) and prints the excluded ones + the implied reward-eligible supply; cross-checks with four untouched holders
(their reflections / balance x the window's total reflected fee must all give the same eligible supply).
Run: python3 tools/ufo-reward-excluded.py   (RPC + api.scan.pulsechain.com; ~3 min).  Update PF_UFO_EXCL in
tools/pf-v2/PfLeagues.jsx when the list changes (a new pool, a newly excluded wallet)."""
import json,urllib.request
RPC='https://rpc.pulsechain.com';UFO='0x49eD499433Bee42DD34C169470feF2C8f9fAe6e6'
TOPIC='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
def call(m,p):
    r=urllib.request.Request(RPC,data=json.dumps({"jsonrpc":"2.0","id":1,"method":m,"params":p}).encode(),headers={'content-type':'application/json'})
    return json.load(urllib.request.urlopen(r,timeout=30))
def pad(a):return a[2:].lower().rjust(64,'0')
def bal(a,b):return int(call('eth_call',[{"to":UFO,"data":'0x70a08231'+pad(a)},hex(b)])['result'],16)
def logs(topics,a,b):
    out=[]
    for s in range(a,b+1,20000):
        r=call('eth_getLogs',[{"address":UFO,"fromBlock":hex(s),"toBlock":hex(min(s+19999,b)),"topics":topics}]);out+=r.get('result',[])
    return out
head=int(call('eth_blockNumber',[])['result'],16);A=head-12000;B=head
def refl(a):
    b0=bal(a,A);b1=bal(a,B);li=logs([TOPIC,None,'0x'+pad(a)],A+1,B);lo=logs([TOPIC,'0x'+pad(a)],A+1,B)
    tin=sum(int(l['data'],16) for l in li);tout=sum(int(l['data'],16) for l in lo)
    fee=sum(int(l['data'],16) for l in lo if l['topics'][2].lower()=='0x'+pad(UFO))
    return (b1-b0-tin+tout+fee//5)/1e18,b0,b1,len(li)+len(lo)
tfee=sum(int(l['data'],16) for l in logs([TOPIC,None,'0x'+pad(UFO)],A+1,B))/5/1e18
print(f'blocks {A}-{B}; reflected to holders in the window: {tfee:,.0f} UFO')
u='https://api.scan.pulsechain.com/api/v2/tokens/'+UFO+'/holders';items=[];nxt=None
for _ in range(5):
    d=json.load(urllib.request.urlopen(urllib.request.Request(u+('?'+'&'.join(f'{k}={v}' for k,v in nxt.items()) if nxt else ''),headers={'accept':'application/json'}),timeout=30))
    items+=d['items'];nxt=d.get('next_page_params')
    if not nxt:break
exc=0;checks=[]
for h in items:
    ad=h['address']['hash'];v=int(h['value'])
    if v<1e27:break
    b0=bal(ad,A);b1=bal(ad,B)
    if b1==b0:r=0.0;n=0
    else:r,b0,b1,n=refl(ad)
    if abs(r)<1e-6:
        code=(len(call('eth_getCode',[ad,'latest'])['result'])-2)//2;exc+=v;print(f'EXCLUDED {ad} {v/1e27:8.3f}B  {"contract "+str(code)+" bytes" if code else "EOA"}')
    elif n==0 and len(checks)<4:checks.append((ad,(b0+b1)/2/1e18*tfee/r))
print(f'excluded {exc/1e27:.2f}B of {999999999051/1e9:.0f}B => eligible {(999999999051e18-exc)/1e27:.2f}B')
for ad,e in checks:print(f'cross-check {ad[:10]} implies eligible {e/1e9:.2f}B')
