import sys
p=sys.argv[1] if len(sys.argv)>1 else 'h2.css'
s=open(p,encoding='utf-8').read()
old=s[s.index('.h2-tile .h2-tb .h2-hd{'):]; old=old[:old.index('\n')+1]
new=('.h2-tile .h2-tb .h2-hd{display:block;width:calc(30*var(--u));height:calc(30*var(--u));margin-left:calc(7*var(--u));background:var(--a);-webkit-mask:var(--ic) center/contain no-repeat;mask:var(--ic) center/contain no-repeat;filter:drop-shadow(0 2px 3px rgba(0,0,0,.8))}'
     '   /* Holders Details icon (2026-10-04) and the Humans vs Bots bot (2026-10-06): the image is a MASK filled with the dashboard colour — gold on PTGC, green on UFO (Shaka 2026-10-06: clickable badges in the token colour; the ⓘ and the LP % stay grey) */\n'
     '.h2-tile .h2-tb .h2-rh{display:inline-flex;align-items:center;justify-content:center;height:calc(26*var(--u));min-width:calc(30*var(--u));padding:0 calc(6*var(--u));border-radius:calc(8*var(--u));border:calc(1.6*var(--u)) solid rgba(var(--a-rgb),.75);font-size:calc(13*var(--u));letter-spacing:.06em;color:var(--a);text-shadow:0 1px 2px rgba(0,0,0,.8)}'
     '   /* RH (2026-10-06): a badge the size of the icons, in the token colour */\n')
if '.h2-tb .h2-rh{' not in s: s=s.replace(old,new,1)
oldp='  .h2-tile .h2-tb .h2-hd{width:calc(22*var(--u));height:calc(22*var(--u));margin-left:calc(5*var(--u))}'
newp='  .h2-tile .h2-tb .h2-hd{width:calc(22*var(--u));height:calc(22*var(--u));margin-left:calc(5*var(--u))}\n  .h2-tile .h2-tb .h2-rh{height:calc(19*var(--u));min-width:calc(22*var(--u));padding:0 calc(4*var(--u));font-size:calc(10*var(--u));border-radius:calc(6*var(--u))}'
if '.h2-tb .h2-rh{height:calc(19' not in s: assert oldp in s; s=s.replace(oldp,newp,1)
open(p,'w',encoding='utf-8').write(s); print('css ok')
s=open(p,encoding='utf-8').read()
if '.h2-pct{' not in s: s=s.replace('.h2-tile .h2-tb .h2-rh{','.h2-tile .h2-tb .h2-pct{color:rgba(255,255,255,.62);font-weight:600}   /* the LP % — not clickable, so grey (Shaka 2026-10-06) */\n.h2-tile .h2-tb .h2-rh{',1)
open(p,'w',encoding='utf-8').write(s); print('pct css ok')
