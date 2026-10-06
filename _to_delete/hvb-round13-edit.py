# Humans vs Bots round 13 (2026-10-06, Shaka): drop the Round-trips column from Top bot contracts and the Human routes fold. Idempotent.
import re,sys
p=sys.argv[1] if len(sys.argv)>1 else 'index.html'
s=open(p,encoding='utf-8').read()
# 1) Round trips column — header (with its InfoTip) and cell
s=re.sub(r'<th className="vs-th"><span className="inline-flex items-center">Round trips<InfoTip label="a round trip".*?</InfoTip></span></th></tr></thead>','</tr></thead>',s,count=1,flags=re.S)
s=re.sub(r'\n\s*<td className="vs-td" title=\{`\$\{fmt\(b\.arb\|\|0\)\} of its \$\{fmt\(b\.n\)\} trades were round trips`\}>\{b\.n\?vsPct\(\(b\.arb\|\|0\)/b\.n\):\'\\u2014\'\}</td>','',s,count=1)
# How we tell no longer points at the column
s=s.replace(' The Round trips column on the bot list shows how sure we are about each one.','',1)
# 2) Human routes fold (the data — view.humans — stays in vsView; only the fold goes)
lines=s.split('\n')
i=next((k for k,l in enumerate(lines) if 'title="Human routes"' in l),None)
if i is not None:
    j=i
    while '</Fold>' not in lines[j]: j+=1
    del lines[i:j+1]
    s='\n'.join(lines)
assert 'title="Human routes"' not in s and 'label="a round trip"' not in s and 'were round trips`' not in s
open(p,'w',encoding='utf-8').write(s); print('ok')
