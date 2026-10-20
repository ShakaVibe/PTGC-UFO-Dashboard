import json,sys,time,urllib.request,urllib.parse
tok,out=sys.argv[1],sys.argv[2]
base=f'https://api.scan.pulsechain.com/api/v2/tokens/{tok}/holders'
rows=[];params=None;t0=time.time()
while True:
    u=base+('?'+urllib.parse.urlencode(params) if params else '')
    for k in range(5):
        try:
            j=json.load(urllib.request.urlopen(u,timeout=30));break
        except Exception as e:
            time.sleep(2+3*k)
    else: sys.exit('failed '+u)
    for it in j['items']:
        a=it['address'];rows.append([a['hash'].lower(),it['value'],bool(a.get('is_contract')),a.get('name') or ''])
    params=j.get("next_page_params")
    if len(rows)%2500==0: print(len(rows),"rows",round(time.time()-t0),"s",flush=True)
    if not params: break
json.dump(rows,open(out,'w'))
print(tok,len(rows),'rows',round(time.time()-t0),'s')
