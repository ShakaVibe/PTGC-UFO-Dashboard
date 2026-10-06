# Humans vs Bots GO-LIVE (2026-10-06, Shaka: "lets make it live!"): VOL_SPLIT_LIVE=true, the Classic bot icon right of the Volume tile's ⓘ (the Holders pattern), the dot goes by itself. Idempotent.
import sys
p=sys.argv[1] if len(sys.argv)>1 else 'index.html'
s=open(p,encoding='utf-8').read()
s=s.replace("    const VOL_SPLIT_LIVE=false;","    const VOL_SPLIT_LIVE=true;   // LIVE 2026-10-06 (Shaka: \"lets make it live!\"). false = hidden behind the faint bottom-right dot (2026-10-06 preview rounds 1-13)",1)
# KpiTilesV2: an openVolSplit prop, the icon button next to the ⓘ
s=s.replace("burnHistoryCache,openVolume,openRH,openHolders,openNewHolders=null}=p;","burnHistoryCache,openVolume,openRH,openHolders,openNewHolders=null,openVolSplit=null}=p;",1)
old='''            {badge:<button type="button" onClick={openVolume} aria-label="Volume by period" className="tap-h"><H2Info/></button>})}'''
new='''            {badge:<><button type="button" onClick={openVolume} aria-label="Volume by period" className="tap-h"><H2Info/></button>{openVolSplit&&<button type="button" onClick={openVolSplit} aria-label="Humans vs Bots — who moves the volume" title="Humans vs Bots" className="tap-h"><img className="h2-hd h2-bot" src="logos/hvb/ic-bot.svg" alt="" aria-hidden="true"/></button>}</>})}{/* Humans vs Bots LIVE 2026-10-06: the Classic bot icon right of the ⓘ, like the Holders people icon */}'''
if 'h2-bot' not in s: assert old in s; s=s.replace(old,new,1)
old2="openNewHolders={NEW_HOLDERS_LIVE?()=>setShowNewHolders(true):null}/>:(<>"
new2="openNewHolders={NEW_HOLDERS_LIVE?()=>setShowNewHolders(true):null} openVolSplit={VOL_SPLIT_LIVE?()=>setShowVolSplit(true):null}/>:(<>"
if 'openVolSplit={' not in s: assert old2 in s; s=s.replace(old2,new2,1)
assert 'VOL_SPLIT_LIVE=true' in s
open(p,'w',encoding='utf-8').write(s); print('ok')
