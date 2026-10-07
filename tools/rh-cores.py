#!/usr/bin/env python3
"""The RH Cores window (2026-10-07) — the Liquidity tile's "RH" button rebuilt to design/rh-cores/mock-rh-v1.html.

Idempotent: python3 tools/rh-cores.py [index.html]. Three edits:
  1. the `rc-*` CSS block after the Volume window's `vw-*` block;
  2. `RhCoresModal` at module scope, just above `VolumeModal`;
  3. the old inline "LP with RH Core Coins" JSX in Dashboard → `<RhCoresModal …/>`.
Shaka: "can you mock up a change to the RH button in liquidity?" → mock v1 → "make it live."
"""
import sys, hashlib

path = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
src = open(path, encoding='utf-8').read()
if 'const RhCoresModal=' in src:
    print('already applied'); sys.exit(0)
assert 'const VolumeModal=' in src, 'run tools/volume-window.py first'

CSS = r"""    /* ---- RH Cores window (2026-10-07): rc-* — the Liquidity tile's RH button, rebuilt to design/rh-cores/mock-rh-v1.html. The Volume
       window's shell; plate = Richard Heart on stage (the Socials RH card's photo), him at the right, the coin + title at the left. ---- */
    .rc-sky{position:absolute;inset:0;background:url(logos/socials/rh-heart-stage.jpg) 100% 38%/cover no-repeat}
    .rc-veil{position:absolute;inset:0;background:linear-gradient(90deg,rgba(0,0,0,.55) 0%,rgba(0,0,0,.35) 45%,rgba(0,0,0,0) 70%),linear-gradient(180deg,rgba(0,0,0,.2) 0%,rgba(0,0,0,.25) 55%,rgba(7,7,7,.9) 88%,#070707 100%)}
    .rc-hd{position:relative;overflow:hidden;min-height:300px;display:flex;flex-direction:column;justify-content:center}
    .rc-hc{position:relative;display:flex;align-items:center;gap:22px;text-shadow:0 2px 10px rgba(0,0,0,.95),0 0 24px rgba(0,0,0,.8);padding:8px 0 0 10px}
    .rc-hc .lg-coin{--u:.72px;--halo:255,120,20;--ring:255,190,80;margin:20px 26px 10px 20px}
    .rc-hc.g .lg-coin{--halo:110,255,40;--ring:140,255,60}
    .rc-sub{color:rgba(255,255,255,.85);font-size:16px;font-weight:500;margin-top:6px;max-width:420px}
    .rc-src{font-size:11px;color:rgba(255,255,255,.6);margin-top:14px}
    .rc-hero{display:grid;grid-template-columns:1.6fr 1fr 1fr;gap:12px}
    .rc-hero .vw-tile .l .p{text-transform:uppercase}
    .rc-hero .vw-tile .v{font-size:36px}
    .rc-hero .vw-tile.live .v{font-size:44px}
    .rc-shr{margin-top:10px;height:10px;border-radius:999px;background:rgba(255,255,255,.08);overflow:hidden}
    .rc-shr i{display:block;height:100%;border-radius:999px;background:linear-gradient(90deg,rgba(var(--tg),.6),rgb(var(--tg)));box-shadow:0 0 12px rgba(var(--tg),.5)}
    .rc-stack{display:flex;height:18px;border-radius:999px;overflow:hidden;margin-top:12px;background:rgba(255,255,255,.06);box-shadow:inset 0 1px 2px rgba(0,0,0,.8)}
    .rc-stack i{display:block;height:100%;background:var(--c);box-shadow:inset -1px 0 0 rgba(0,0,0,.5)}
    .rc-keys{display:flex;flex-wrap:wrap;gap:6px 18px;margin-top:10px}
    .rc-keys span{display:inline-flex;align-items:center;gap:7px;font-size:14px;font-weight:600;color:rgba(255,255,255,.8);white-space:nowrap}
    .rc-keys i{width:11px;height:11px;border-radius:3px;display:inline-block;background:var(--c)}
    .rc-keys b{color:rgba(255,255,255,.55);font-weight:600;margin-left:2px}
    .rc-rows{display:flex;flex-direction:column;gap:8px;margin-top:12px}
    .rc-row{display:grid;grid-template-columns:44px 1.5fr 1.2fr 1.3fr .9fr .8fr 38px;align-items:center;gap:14px;padding:10px 14px;border-radius:14px;border:1px solid rgba(255,255,255,.1);background:linear-gradient(180deg,rgba(255,255,255,.04),rgba(0,0,0,.35))}
    .rc-row:hover{border-color:rgba(var(--tg),.45)}
    .rc-logo{width:44px;height:44px;border-radius:50%;object-fit:cover;background:rgba(0,0,0,.5);box-shadow:0 0 0 2px rgba(0,0,0,.6),0 0 0 3.5px var(--c),0 0 14px rgba(0,0,0,.6);max-width:none}
    .rc-row .pr{font-family:'Rajdhani',sans-serif;font-size:19px;font-weight:700;color:rgb(var(--tg));line-height:1.1}
    .rc-row .pn{font-size:12.5px;color:rgba(255,255,255,.5);font-weight:500;margin-top:2px}
    .rc-row .k{font-size:11px;letter-spacing:.18em;text-transform:uppercase;font-weight:600;color:rgba(255,255,255,.5)}
    .rc-row .v{font-family:'Rajdhani',sans-serif;font-size:22px;font-weight:700;color:#fff;font-variant-numeric:tabular-nums;line-height:1.05;margin-top:1px;white-space:nowrap}
    .rc-row .v.sm{font-size:19px}
    .rc-row .rc-sh{display:flex;align-items:center;gap:10px}
    .rc-row .rc-sh .v{min-width:52px}
    .rc-mini{display:inline-flex;height:7px;flex:1;max-width:120px;border-radius:999px;overflow:hidden;background:rgba(255,255,255,.08)}
    .rc-mini i{display:block;height:100%;background:var(--c)}
    .rc-badge{display:inline-flex;align-items:center;gap:4px;font-family:'Rajdhani',sans-serif;font-size:15px;font-weight:700;padding:4px 10px;border-radius:999px;background:rgba(0,0,0,.45);border:1px solid rgba(255,255,255,.12);font-variant-numeric:tabular-nums;white-space:nowrap;color:rgba(255,255,255,.4)}
    .rc-badge.up{color:#4ADE80;border-color:rgba(74,222,128,.4)}.rc-badge.dn{color:#FF2E3B;border-color:rgba(255,46,59,.4)}
    .rc-act{width:36px;height:36px;border-radius:10px;border:1px solid rgba(255,255,255,.14);background:rgba(0,0,0,.5);display:flex;align-items:center;justify-content:center;color:rgba(255,255,255,.75)}
    .rc-act:hover{border-color:rgba(255,255,255,.4);color:#fff}
    .rc-act svg{width:18px;height:18px;stroke:currentColor;fill:none;stroke-width:2;stroke-linecap:round;stroke-linejoin:round}
    @media(max-width:640px){
      .rc-hd{min-height:0}.rc-sky{background-position:100% 30%}.rc-hc{flex-direction:column;align-items:center;text-align:center;gap:6px;padding:0}.rc-hc .lg-coin{--u:.56px;margin:18px 0 12px}.rc-sub{font-size:13px;margin-top:4px}.rc-src{margin-top:8px}
      .rc-hero{grid-template-columns:1fr 1fr}.rc-hero .vw-tile.live{grid-column:1/-1}.rc-hero .vw-tile .v{font-size:27px}.rc-hero .vw-tile.live .v{font-size:36px}
      .rc-row{grid-template-columns:40px 1fr auto;grid-template-areas:"lg pr bd" "liq liq vol" "sh sh act";gap:10px 12px;padding:10px 12px}.rc-logo{width:40px;height:40px;grid-area:lg}
      .rc-row .rc-pp{grid-area:pr}.rc-row .rc-liq{grid-area:liq}.rc-row .rc-vol{grid-area:vol;text-align:right}.rc-row .rc-sh{grid-area:sh}.rc-badge{grid-area:bd;justify-self:end;align-self:center}.rc-act{grid-area:act;justify-self:end;width:32px;height:32px}
      .rc-row .rc-sh .rc-mini{max-width:none}.rc-row .v{font-size:19px}.rc-row .v.sm{font-size:16px}.rc-keys span{font-size:12.5px}}
"""
anchor_css = "    @media(max-width:640px){.vw-coins{height:118px}"
i = src.index(anchor_css)
j = src.index('\n', src.index(".vw-key span{font-size:12.5px}}", i)) + 1
src = src[:j] + CSS + src[j:]

JSX = r"""    /* ---- RH CORES WINDOW (2026-10-07) — the Liquidity tile's RH button, rebuilt to design/rh-cores/mock-rh-v1.html (README = the
       decisions; build tools/rh-cores.py). Same data as the old window: `rhCoresPairs` (the token's pairs flagged as RH cores — WPLS, PLSX,
       INC, HEX, eHEX, PRVX; WETH is a constructor pool, never here) and `rhCoresLiq`; `data.liq` for the share of all liquidity. A chain-read
       pair (`_fromChain`, DexScreener missing it) prints "—" for volume and the move (a14). ---- */
    const RC_CORE={WPLS:{c:'#4F8CFF',n:'Wrapped PLS',s:'WPLS'},PLSX:{c:'#28D17C',n:'PulseX',s:'PLSX'},INC:{c:'#B6FF4A',n:'Incentive',s:'INC'},HEX:{c:'#FF3FA4',n:'HEX',s:'HEX'},EHEX:{c:'#FF8A3D',n:'eHEX (Ethereum HEX)',s:'eHEX'},PRVX:{c:'#A855F7',n:'ProveX',s:'PRVX'}};
    const RhCoresModal=({token,cfg,data,pairs,totalLiq,onClose})=>{
      const tk=token==='UFO'?'UFO':'PTGC',T=NH_THEME[tk],hex=T.hex,rgb=T.rgb;
      const rows=(pairs||[]).map(p=>{
        const core=(p.rhCore||'').toUpperCase(),c=RC_CORE[core]||{c:hex,n:core,s:core};
        const isBase=(p.baseToken&&p.baseToken.address||'').toLowerCase()===(cfg.address||'').toLowerCase();
        const other=isBase?p.quoteToken:p.baseToken;
        const liq=(p.liq!=null&&isFinite(p.liq))?p.liq:null;
        const vol=(!p._fromChain&&p.vol!=null&&isFinite(p.vol))?p.vol:null;
        const chg=(!p._fromChain&&p.priceChange&&p.priceChange.h24!=null&&isFinite(p.priceChange.h24))?p.priceChange.h24:null;
        return{key:p.pairAddress||core,core,c,liq,vol,chg,logo:getLogo(other&&other.address),pair:`${tk}/${c.s}`,addr:p.pairAddress};
      });
      const rh=rows.length?rows.reduce((s,r)=>s+(r.liq||0),0):null;
      const volKnown=rows.length>0&&rows.every(r=>r.vol!=null),vol=volKnown?rows.reduce((s,r)=>s+r.vol,0):null;
      const total=(totalLiq!=null&&isFinite(totalLiq)&&totalLiq>0)?totalLiq:null;
      const share=(rh!=null&&total!=null)?Math.min(1,rh/total):null;
      const top=rows.length?Math.max(1,...rows.map(r=>r.liq||0)):1;
      return(
        <Modal onClose={onClose} label={`${tk} liquidity with the RH core coins`} className="z-50 flex items-center justify-center p-0 sm:p-4 modal-overlay bg-black/85">
          <div onClick={e=>e.stopPropagation()} className="relative w-full h-[100dvh] sm:h-auto sm:max-h-[calc(100dvh-2rem)] sm:max-w-4xl flex flex-col rounded-none sm:rounded-3xl border bg-[#070707] overflow-y-auto overflow-x-hidden overscroll-contain" style={{borderColor:`${hex}55`,boxShadow:`0 0 80px -20px ${hex}66, 0 30px 80px rgba(0,0,0,.8)`,'--tg':rgb}}>
            <div aria-hidden="true" className="pointer-events-none absolute -top-32 left-1/2 -translate-x-1/2 w-[640px] h-[300px] rounded-full blur-3xl opacity-20" style={{background:`radial-gradient(circle, ${hex} 0%, transparent 65%)`}}></div>
            <div aria-hidden="true" className="pointer-events-none absolute inset-x-0 top-0 h-px" style={{background:`linear-gradient(90deg, transparent, ${hex}cc, transparent)`}}></div>
            <div className="rc-hd shrink-0 px-4 sm:px-6 pt-4 sm:pt-5 pb-3">
              <div aria-hidden="true" className="rc-sky"></div>
              <div aria-hidden="true" className="rc-veil"></div>
              <button type="button" onClick={onClose} aria-label="Close" className="tap-h absolute right-4 top-4 sm:right-6 sm:top-6 z-10 w-9 h-9 rounded-full border border-white/25 bg-black/50 text-white/80 hover:text-white hover:border-white/60 flex items-center justify-center text-lg leading-none">{'✕'}</button>
              <div className={`rc-hc${tk==='UFO'?' g':''}`}>
                <LgCoin token={tk}/>
                <div>
                  <h2 className="font-orbitron text-2xl sm:text-[34px] font-bold tracking-wide leading-tight whitespace-nowrap"><span style={{color:hex}}>{tk}</span><span className="text-white ml-3">RH Cores</span></h2>
                  <div className="rc-sub">Liquidity in the {tk} pools paired with Richard Heart's PulseChain core coins {'—'} WPLS, PLSX, INC, HEX, eHEX and PRVX</div>
                  <div className="rc-src">DexScreener {'·'} live</div>
                </div>
              </div>
            </div>
            <div className="relative px-4 sm:px-6 pb-5 sm:pb-6 flex-1 min-h-0">
              <div className="rc-hero">
                <div className="vw-tile live">
                  <div className="l"><span className="p">RH core liquidity</span><img className="ic" src="logos/panels/vg-droplet.webp" alt="" aria-hidden="true"/></div>
                  <div className="v">{rh==null?'—':fmtUSD(rh)}</div>
                  <div className="s">{share==null?<span className="text-white/40">{'—'}</span>:<><b>{(share*100).toFixed(1)}%</b> of all {tk} liquidity ({fmtUSD(total)})</>}</div>
                  <div className="rc-shr" role="img" aria-label={share==null?'unavailable':`${Math.round(share*100)}% of all liquidity`}><i style={{width:`${(share||0)*100}%`}}></i></div>
                </div>
                <div className="vw-tile"><div className="l"><span className="p">Pools</span></div><div className="v">{rows.length||'—'}</div><div className="s">{rows.length===6?'of the six cores, all paired':`of the six cores`}</div></div>
                <div className="vw-tile"><div className="l"><span className="p">24H volume</span></div><div className="v">{vol==null?'—':fmtUSD(vol)}</div><div className="s">through the core pools</div></div>
              </div>
              {rows.length>0&&rh>0&&(
                <div className="vw-card">
                  <div className="vw-hdr"><span className="t">Where it sits</span><span className="c">share of the RH core liquidity</span></div>
                  <div className="rc-stack" role="img" aria-label="Share of the RH core liquidity by pool">{rows.map(r=><i key={r.key} style={{'--c':r.c.c,width:`${(r.liq||0)/rh*100}%`}} title={`${r.pair} ${((r.liq||0)/rh*100).toFixed(1)}%`}></i>)}</div>
                  <div className="rc-keys">{rows.map(r=><span key={r.key} style={{'--c':r.c.c}}><i aria-hidden="true"></i>{r.c.s}<b>{((r.liq||0)/rh*100).toFixed(1)}%</b></span>)}</div>
                </div>
              )}
              {rows.length>0?(
                <div className="rc-rows">
                  {rows.map(r=>(
                    <div key={r.key} className="rc-row" style={{'--c':r.c.c}}>
                      <img className="rc-logo" src={r.logo||''} alt="" onError={e=>{e.target.style.visibility='hidden';}}/>
                      <div className="rc-pp"><div className="pr">{r.pair}</div><div className="pn">{r.c.n} pair</div></div>
                      <div className="rc-liq"><div className="k">Liquidity</div><div className="v">{r.liq==null?'—':fmtUSD(r.liq)}</div></div>
                      <div className="rc-sh"><div className="v sm">{(rh>0&&r.liq!=null)?((r.liq/rh*100).toFixed(1)+'%'):'—'}</div><span className="rc-mini" aria-hidden="true"><i style={{width:`${(r.liq||0)/top*100}%`}}></i></span></div>
                      <div className="rc-vol"><div className="k">Volume 24h</div><div className="v sm">{r.vol==null?'—':fmtUSD(r.vol)}</div></div>
                      {r.chg==null?<span className="rc-badge" title="24h price change unavailable">{'—'}</span>:<span className={`rc-badge ${r.chg<0?'dn':'up'}`} title="Price change, 24h (DexScreener)">{r.chg<0?'▼':'▲'} {Math.abs(r.chg).toFixed(1)}%</span>}
                      {r.addr?<a className="rc-act" href={`https://dexscreener.com/pulsechain/${r.addr}`} target="_blank" rel="noopener noreferrer" aria-label={`${r.pair} on DexScreener`} title="DexScreener"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 17l5-6 4 4 5-7 4 3"/></svg></a>:<span className="rc-act" aria-hidden="true"></span>}
                    </div>))}
                </div>
              ):(
                <div className="vw-card text-center text-white/50 py-8">No RH core pairs found</div>
              )}
              <div className="vw-conf">The RH Cores are the PulseChain core coins: WPLS, PLSX, INC, HEX, eHEX and PRVX. WETH is a constructor pool, not a core, and is not counted. Liquidity, volume and the 24h move are DexScreener's; a pool DexScreener does not list is read on-chain (its volume and move print {'“—”'}).</div>
            </div>
          </div>
        </Modal>
      );
    };
"""
anchor_jsx = "    const VolumeModal=({token,data,volumeByPeriod,onClose})=>{"
i = src.index(anchor_jsx)
src = src[:i] + JSX + src[i:]

start = src.index("          {showRHModal&&(\n            <Modal className=\"z-50 flex items-center justify-center p-4 modal-overlay bg-black/80\" onClose={()=>setShowRHModal(false)} label=\"LP with RH Core Coins\">")
end_marker = "            </Modal>\n          )}\n"
j = src.index(end_marker, start) + len(end_marker)
old = src[start:j]
assert 'No RH Core pairs found' in old and 'Total Liquidity' in old, 'the old RH modal block was not where expected'
NEW = "          {/* RH Cores window (2026-10-07) — RhCoresModal at module scope; the old inline card is in git history */}\n          {showRHModal&&<RhCoresModal token={token} cfg={cfg} data={data} pairs={rhCoresPairs} totalLiq={data?.liq} onClose={()=>setShowRHModal(false)}/>}\n"
src = src[:start] + NEW + src[j:]

open(path, 'w', encoding='utf-8').write(src)
print('applied', path, 'md5', hashlib.md5(src.encode('utf-8')).hexdigest(), 'removed', old.count('\n'), 'lines of the old modal')
