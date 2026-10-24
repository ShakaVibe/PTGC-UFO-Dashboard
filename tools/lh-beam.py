#!/usr/bin/env python3
"""League History — the ownership BEAM + the card layout (2026-10-24, Shaka; mock-ups v1–v3, picked "B").
  - A thin glowing beam (the dashboard burn bars' look) between the controls and the cards: one section per league, its length = the
    league's share of the tokens in holders' wallets (B: the leagues stretched to fill the whole beam — pools / contracts / the DAO are
    not on it), colours matched to the sea-creature art, a white-hot node where two leagues meet. No labels: hover a section (or tap
    it on a phone) for the creature, its wallets, its share of the supply and the tokens it holds; a click / tap also selects that
    league for the chart below. Follows the supply basis (STARTING / CIRCULATING) — the leagues differ, the total is the same.
  - The dashboard strip drops "incl. the Burn address" (UFO's Whales): the label only when the burn wallet is alone in its league.
  - Cards: the up / down sits to the right of the count; the hold, per-wallet and joined / left lines are bigger.
Idempotent, from the repo root:   python3 tools/lh-beam.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
J, C = 'tools/league-history/lh.jsx', 'tools/league-history/lh.css'

BEAM = """    /* the ownership BEAM (2026-10-24, Shaka's mock-up v3 "B"): one glowing section per league, its length = the league's share of the
       tokens in holders' wallets on the last day (pools / contracts / the DAO are not on it, so the leagues fill the beam). No labels —
       hover (mouse) or tap (finger) shows the creature, wallets, share of the supply (shareOf: the basis supply) and tokens; a click /
       tap also selects the league. The tip is clamped inside the beam's width (never off a phone's edge). */
    const LH_BEAM_C=[['#6B4A06','#E8B828','#FFF0A0','255,200,60'],['#0A2A7A','#2F7BFF','#BFDDFF','60,130,255'],['#2E3646','#8D99AC','#F2F5FA','190,200,220'],['#05506E','#1FB6EE','#C8F6FF','40,190,245'],
      ['#5E0A12','#E8434B','#FFC2C4','240,70,80'],['#0C4E18','#3FC24A','#D2FFC0','70,210,80'],['#6A2A06','#FF8A3D','#FFDDB8','255,140,60'],['#6E463C','#EDB7A6','#FFF4EE','240,190,175']];   // [dark, core, hot end, glow] per league
    const LhBeam=({t,tok,basis,last,onSel,shareOf})=>{
      const box=useRef(null),tipRef=useRef(null);const[hv,setHv]=useState(null);const[pin,setPin]=useState(false);
      const held=t&&t.held&&t.held[basis],row=held?held[last]:null,cnt=t&&t[basis]?t[basis][last]:null;
      const tot=row?row.reduce((s,v)=>s+v,0):0;
      useEffect(()=>{setHv(null);setPin(false);},[tok,basis]);
      useEffect(()=>{if(!pin)return;const f=e=>{if(box.current&&!box.current.contains(e.target)){setHv(null);setPin(false);}};
        document.addEventListener('pointerdown',f);return()=>document.removeEventListener('pointerdown',f);},[pin]);
      useLayoutEffect(()=>{const b=box.current,tp=tipRef.current;if(!b||!tp||hv==null)return;const sg=b.querySelector(`[data-i="${hv}"]`);if(!sg)return;
        const W=b.clientWidth,tw=tp.offsetWidth,c=sg.offsetLeft+sg.offsetWidth/2,x=Math.max(0,Math.min(W-tw,c-tw/2));
        tp.style.left=`${x}px`;tp.style.setProperty('--ax',`${Math.max(14,Math.min(tw-14,c-x))}px`);},[hv,tok,basis,last]);
      if(!row||!cnt||!(tot>0))return null;
      const lastI=row.reduce((k,v,i)=>v>0?i:k,-1);
      const tap=i=>{const off=hv===i&&pin;setHv(off?null:i);setPin(!off);};
      const h=hv!=null&&row[hv]>0?hv:null;
      return(
        <div className="lh-bm" ref={box}>
          <div className="lh-bm-tr" role="group" aria-label={`Who holds ${tok}: the leagues' share of the tokens in holders' wallets`}
            onPointerLeave={e=>{if(e.pointerType==='mouse'&&!pin)setHv(null);}}>
            {LH_TIERS.map(([nm],i)=>{if(!(row[i]>0))return null;const[k,m,l,g]=LH_BEAM_C[i],sh=shareOf(row[i],last);return(
              <button type="button" key={nm} data-i={i} className={`lh-bm-s${h===i?' hv':''}`} style={{flex:`${(row[i]/tot*100).toFixed(5)} 1 0`,'--k':k,'--m':m,'--l':l,'--g':g}}
                aria-label={`${nm}: ${lhFmt(cnt[i])} wallet${cnt[i]===1?'':'s'} hold ${fmtAbbr(row[i])} ${tok}${sh!=null?`, ${sh}% of the supply`:''} — show the chart`}
                onPointerEnter={e=>{if(e.pointerType==='mouse'&&!pin)setHv(i);}} onPointerDown={e=>{if(e.pointerType!=='mouse')tap(i);}}
                onFocus={()=>setHv(i)} onBlur={()=>{if(!pin)setHv(null);}} onClick={()=>onSel(i)}>{i!==lastI&&<i aria-hidden="true"></i>}</button>);})}
          </div>
          {h!=null&&(()=>{const[nm,img]=LH_TIERS[h],c=cnt[h],sh=shareOf(row[h],last),bw=t.burnIn&&t.burnIn[basis]===h;return(
            <div className="lh-bm-tip" ref={tipRef} style={{'--g':LH_BEAM_C[h][3]}} aria-hidden="true">
              <img src={lhSea(img)} alt=""/><div><div className="n">{nm.toUpperCase()} {'\\u00B7'} {lhFmt(c)} WALLET{c===1?'':'S'}</div>
                <div className="v">{sh!=null?`${sh}%`:'\\u2014'}<small>{fmtAbbr(row[h])} {tok}</small></div>
                {bw&&<div className="bn">{'\\u{1F525}'} {c===1?'the Burn address':'incl. the Burn address'}</div>}</div></div>);})()}
        </div>);
    };
"""
edit(J, "    /* the share card:", BEAM + "    /* the share card:")
edit(J, "              {rows&&<>\n                <div className=\"lh-cards\">",
        "              {rows&&<>\n                <LhBeam t={t} tok={tok} basis={basis} last={last} onSel={setSel} shareOf={shareOf}/>\n                <div className=\"lh-cards\">")
# cards: the change beside the count
edit(J, "<div className=\"v\">{lhFmt(b)}</div><div className=\"ch\"><LhChange a={a} b={b}/></div>",
        "<div className=\"vr\"><div className=\"v\">{lhFmt(b)}</div><div className=\"ch\"><LhChange a={a} b={b}/></div></div>")

CSS = """
    /* the ownership beam + the card layout (2026-10-24, Shaka's mock-up v3 "B") */
    .lh-bm{position:relative;margin:12px 6px 22px}
    .lh-bm-tr{position:relative;height:10px;border-radius:99px;display:flex;background:linear-gradient(180deg,#0b0d14,#04050a);border:1px solid rgba(255,255,255,.22);box-shadow:inset 0 2px 4px rgba(0,0,0,.8)}
    .lh-bm-s{position:relative;height:100%;min-width:3px;margin:0;padding:0;border:0;appearance:none;-webkit-appearance:none;font:inherit;cursor:pointer;
      background:linear-gradient(90deg,var(--k) 0%,var(--m) 45%,var(--m) 80%,var(--l) 100%);box-shadow:0 0 16px rgba(var(--g),.8),0 0 5px rgba(var(--g),1);transition:filter .15s,box-shadow .15s}
    .lh-bm-s:first-child{border-radius:99px 0 0 99px}.lh-bm-s:last-child{border-radius:0 99px 99px 0}.lh-bm-s:only-child{border-radius:99px}
    .lh-bm-s::before{content:'';position:absolute;inset:0;border-radius:inherit;background:url(logos/panels/flames.webp) left center/auto 100% repeat-x;filter:grayscale(1) brightness(1.25);mix-blend-mode:overlay;opacity:.5}
    .lh-bm-s::after{content:'';position:absolute;left:0;right:0;top:0;height:40%;border-radius:inherit;background:linear-gradient(180deg,rgba(255,255,255,.35),rgba(255,255,255,0))}
    .lh-bm-s i{position:absolute;right:-5px;top:50%;width:10px;height:10px;margin-top:-5px;border-radius:50%;z-index:2;pointer-events:none;background:radial-gradient(circle,#fff 0%,#fff 28%,var(--l) 55%,rgba(var(--g),0) 75%);box-shadow:0 0 10px 3px rgba(var(--g),.8)}
    .lh-bm-s.hv{filter:brightness(1.35) saturate(1.15);box-shadow:0 0 22px rgba(var(--g),1),0 0 6px rgba(255,255,255,.8);z-index:3}
    .lh-bm-s:focus-visible{outline:2px solid #fff;outline-offset:3px;z-index:4}
    .lh-bm-tip{position:absolute;left:0;bottom:22px;display:flex;align-items:center;gap:10px;padding:8px 13px 8px 9px;border-radius:13px;white-space:nowrap;pointer-events:none;z-index:6;
      background:rgba(5,7,12,.95);border:1px solid rgba(var(--g),.8);box-shadow:0 0 20px rgba(var(--g),.35),0 8px 24px rgba(0,0,0,.7)}
    .lh-bm-tip::after{content:'';position:absolute;left:var(--ax,50%);bottom:-6px;width:10px;height:10px;margin-left:-5px;transform:rotate(45deg);background:rgba(5,7,12,.95);border-right:1px solid rgba(var(--g),.8);border-bottom:1px solid rgba(var(--g),.8)}
    .lh-bm-tip img{width:38px;height:38px;object-fit:contain}
    .lh-bm-tip .n{font:700 11.5px 'Orbitron',sans-serif;letter-spacing:.14em;color:rgba(255,255,255,.75)}
    .lh-bm-tip .v{font:700 20px 'Orbitron',sans-serif;color:#fff;line-height:1.1;margin-top:2px}.lh-bm-tip .v small{font:600 15px 'Rajdhani',sans-serif;color:rgba(255,255,255,.6);margin-left:8px;letter-spacing:0}
    .lh-bm-tip .bn{font-size:12.5px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:#FDBA74;margin-top:2px}
    .lh-cd .vr{display:flex;align-items:baseline;flex-wrap:wrap;gap:2px 10px;margin-top:8px}.lh-cd .vr .v{margin-top:0}.lh-cd .vr .ch{margin-top:0;font-size:15.5px}
    .lh-cd .hd2{font-size:16.5px;margin-top:8px}.lh-cd .av{font-size:15.5px;margin-top:4px}.lh-cd .jl{font-size:16px;margin-top:5px}
    @media(max-width:700px){.lh-bm{margin:10px 4px 18px}.lh-bm-tip .v{font-size:18px}.lh-cd .vr .ch{font-size:13.5px}.lh-cd .hd2{font-size:14.5px}.lh-cd .av{font-size:13.5px}.lh-cd .jl{font-size:14px}}
"""
s = open(C, encoding='utf-8').read()
if 'the ownership beam + the card layout' not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1

# ---- the dashboard strip (Shaka, 2026-10-24: "get the text off the dashboards that say include the burn address"): the label shows
#      only when the burn wallet is ALONE in its league ("The Burn address", PTGC's 1 Poseidon); a shared league keeps just the 🔥
IX = 'index.html'
edit(IX, "{tiers&&tiers.burnIn===k&&<span className=\"bwl\">{tiers[k]===1?'The Burn address':'incl. the Burn address'}</span>}",
         "{tiers&&tiers.burnIn===k&&tiers[k]===1&&<span className=\"bwl\">The Burn address</span>}")
edit(IX, "{tiers&&tiers.burnIn&&<div className=\"bwn\">{'\\u{1F525}'} {tiers[tiers.burnIn]===1?`${tiers.burnIn} = the Burn address`:`${tiers.burnIn}s include the Burn address`}</div>}",
         "{tiers&&tiers.burnIn&&tiers[tiers.burnIn]===1&&<div className=\"bwn\">{'\\u{1F525}'} {`${tiers.burnIn} = the Burn address`}</div>}")

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-beam: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
