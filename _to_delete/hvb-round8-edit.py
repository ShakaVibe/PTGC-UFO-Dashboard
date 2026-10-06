import pathlib,sys
root=pathlib.Path(sys.argv[1])
for f in ['tools/volume-split.py','index.html']:
    p=root/f; s=p.read_text()
    def rep(old,new):
        global s
        assert s.count(old)==1,(f,old[:70],s.count(old)); s=s.replace(old,new)
    # 1+2. banner: a lighter overall veil, a dark pool behind the title block, the crop shifted so the robot sits further right
    rep("""    .vs-sky{position:absolute;inset:0;background:url(logos/hvb/banner.jpg) center 38%/cover no-repeat}   /* round 6: his humans-vs-bots panorama (logos/hvb/banner.jpg) */
    .vs-sky-veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.64) 0%,rgba(0,0,0,.64) 60%,rgba(7,7,7,.86) 88%,#070707 100%)}   /* round 7: ~64 % ("dim it a little more" than the 50 %) + the fade into the body */""",
"""    .vs-sky{position:absolute;inset:0;background:url(logos/hvb/banner.jpg) 42% 36%/cover no-repeat}   /* round 6: his humans-vs-bots panorama; round 8: the crop sits 42 % so the robot moves right and the mountains breathe (one image — the robot cannot be scaled on his own) */
    .vs-sky-veil{position:absolute;inset:0;background:radial-gradient(ellipse 46% 120% at 36% 42%,rgba(0,0,0,.42) 0%,rgba(0,0,0,.22) 55%,rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,.4) 0%,rgba(0,0,0,.4) 58%,rgba(7,7,7,.84) 88%,#070707 100%)}   /* round 8 (his mock-up): a 40 % veil with a ~25 % pool behind the title block, the art still visible; the fade into the body */""")
    # 3. the figures a touch fainter; 4. the percentages bigger
    rep(""".vs-card .fig{position:absolute;right:3%;top:5%;height:90%;width:auto;max-width:56%;object-fit:contain;object-position:right center;opacity:.6;""",
        """.vs-card .fig{position:absolute;right:3%;top:5%;height:90%;width:auto;max-width:56%;object-fit:contain;object-position:right center;opacity:.5;""")
    rep("""    .vs-card .pct{font-family:'Orbitron',monospace;font-weight:900;font-size:30px;line-height:1;color:rgb(var(--acc))}   /* round 4: no glow (Shaka: "makes it kinda fuzzy") */""",
        """    .vs-card .pct{font-family:'Orbitron',monospace;font-weight:900;font-size:34px;line-height:1;color:rgb(var(--acc))}   /* round 4: no glow; round 8: +10 % — "arguably the entire takeaway" */""")
    rep("""@media(max-width:640px){.vs-card{padding:14px 14px 12px}.vs-card .v{font-size:32px}.vs-card .vg .v{font-size:24px}.vs-card .pct{font-size:26px}""",
        """@media(max-width:640px){.vs-card{padding:14px 14px 12px}.vs-card .v{font-size:32px}.vs-card .vg .v{font-size:24px}.vs-card .pct{font-size:29px}""")
    # 5. the summary strip: a gold → blue hairline along its foot with a soft glow
    rep("""    .vs-strip{display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 22px;padding:10px 16px;border-radius:14px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03)}""",
        """    .vs-strip{position:relative;display:flex;flex-wrap:wrap;align-items:baseline;gap:6px 22px;padding:10px 16px 12px;border-radius:14px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.03);overflow:hidden}
    .vs-strip::after{content:'';position:absolute;left:14px;right:14px;bottom:0;height:2px;border-radius:2px;background:linear-gradient(90deg,#E8C044 0%,rgba(232,192,68,.5) 45%,rgba(79,209,255,.5) 55%,#4FD1FF 100%);box-shadow:0 0 14px rgba(232,192,68,.35),0 0 14px rgba(79,209,255,.35)}   /* round 8: the gold → blue hairline ties the whole to the two sides below */""")
    # 6. his network wave behind the chart panel
    rep("""                  <div className="mt-3 rounded-2xl border border-white/10 bg-black/40 p-3 sm:p-4">
                    <div className="flex items-center justify-between gap-3">
                      <span className="vs-key">""",
"""                  <div className="vs-chartcard mt-3 rounded-2xl border border-white/10 p-3 sm:p-4">
                    <div className="flex items-center justify-between gap-3">
                      <span className="vs-key">""")
    rep("""    .vs-chart{display:block;width:100%;height:170px}""",
        """    .vs-chartcard{position:relative;overflow:hidden;background:#06080d url(logos/hvb/wave.jpg) center 60%/cover no-repeat}   /* round 8: his gold → blue network wave behind the chart, under a veil */
    .vs-chartcard::before{content:'';position:absolute;inset:0;background:linear-gradient(180deg,rgba(4,6,10,.78),rgba(4,6,10,.62) 40%,rgba(4,6,10,.72) 100%);pointer-events:none}
    .vs-chartcard>*{position:relative}
    .vs-chart{display:block;width:100%;height:170px}""")
    p.write_text(s); print('ok',f)
import pathlib,sys,re
root=pathlib.Path(sys.argv[1])
for f in ['tools/volume-split.py','index.html']:
    p=root/f; s=p.read_text()
    def rep(old,new):
        global s
        assert s.count(old)==1,(f,old[:70],s.count(old)); s=s.replace(old,new)
    # the Buys / Sells bars and the when-they-trade strip go (Shaka, round 8: "ugly", "irrelevant and clutters the chart area")
    rep("""                      {view.hasDir&&<VsBuySell b={view.buys.human} s={view.sells.human}/>}
""","")
    rep("""                      {view.hasDir&&<VsBuySell b={view.buys.bot} s={view.sells.bot}/>}
""","")
    rep("""                    {view.hod.some(h=>h[0]+h[1]>0)&&<VsHod hod={view.hod} rgb={rgb} gg={both}/>}
""","")
    # the two components and their CSS
    a=s.index("    /* Buys vs sells of the token for one side (round 5)"); b=s.index("    const VolumeSplitModal=({token:initial,feeRates,pairs,otherPairs,onClose})=>{")
    s=s[:a]+"    /* (round 5's Buys / Sells bars and when-they-trade strip were removed in round 8 — the builder still writes `buys` / `sells` / `hod`) */\n"+s[b:]
    a=s.index("    .vs-bs{margin-top:10px}"); b=s.index("    .vs-bar{height:16px;")
    s=s[:a]+s[b:]
    p.write_text(s); print('ok',f)
import pathlib,sys
root=pathlib.Path(sys.argv[1])
for f in ['tools/volume-split.py','index.html']:
    p=root/f; s=p.read_text()
    def rep(old,new):
        global s
        assert s.count(old)==1,(f,old[:70],s.count(old)); s=s.replace(old,new)
    rep("""                <div className="flex-1 min-w-0" style={{textShadow:both?'none':'0 2px 10px rgba(0,0,0,.95), 0 0 24px rgba(0,0,0,.8)'}}>
                  <h2 className={`font-orbitron text-2xl sm:text-4xl font-bold tracking-wide leading-tight${both?' gold-green-text':''}`} style={both?{filter:'drop-shadow(0 2px 6px rgba(0,0,0,.9))'}:{color:hex}}>Humans vs Bots</h2>
                  <div className="text-white/85 text-[13px] sm:text-base mt-1 font-medium" style={{textShadow:'0 2px 10px rgba(0,0,0,.95)'}}>{P.label} {'·'} who moves {both?'the Grays’':token+'’s'} volume {'—'} people, or the arbitrage bots</div>
                </div>""",
"""                {/* round 10 (his mock-up): the title centred in the banner — "Humans" in the token's colour (gold → green on BOTH), "vs" silver, "Bots" in the bots' blue */}
                <div className="flex-1 min-w-0 text-center sm:pr-12" style={{textShadow:'0 2px 10px rgba(0,0,0,.95), 0 0 24px rgba(0,0,0,.8)'}}>
                  <h2 className="font-orbitron text-2xl sm:text-4xl font-bold tracking-wide leading-tight whitespace-nowrap">
                    <span className={both?'gold-green-text':''} style={both?{filter:'drop-shadow(0 2px 6px rgba(0,0,0,.9))'}:{color:hex}}>Humans</span>
                    <span className="text-white/80 mx-2 sm:mx-3">vs</span>
                    <span style={{color:`rgb(${VS_BOT})`}}>Bots</span>
                  </h2>
                  <div className="text-white/85 text-[13px] sm:text-base mt-1 font-medium">{P.label} {'·'} who moves {both?'the Grays’':token+'’s'} volume {'—'} people, or the arbitrage bots</div>
                </div>""")
    p.write_text(s); print('ok',f)
import pathlib,sys
root=pathlib.Path(sys.argv[1])
for f in ['tools/volume-split.py','index.html']:
    p=root/f; s=p.read_text()
    def rep(old,new):
        global s
        assert s.count(old)==1,(f,old[:70],s.count(old)); s=s.replace(old,new)
    a=s.index("""              <div className="relative flex items-start gap-3 sm:gap-4">
                <div className="relative shrink-0 flex items-center">
                  {both?(<><img src={TOKENS.PTGC.logo}""")
    b=s.index("""              <div className="relative mt-5 sm:mt-7 flex flex-wrap items-center gap-2 sm:gap-3">
                <NhPills items={[{k:'PTGC'},{k:'UFO'},{k:'BOTH'}]}""")
    new="""              {/* round 11 (his mock-up): the dashboard's lit coin (LgCoin — halo, corona, flares) centred over the title, everything stacked and
                  centred; "Humans" in the token's colour (a bright gold → green on BOTH, no shadow behind gradient text — that is what read dark),
                  "vs" silver, "Bots" the bots' blue; the subtitle short */}
              <button type="button" onClick={onClose} aria-label="Close" className="tap-h absolute right-4 top-4 sm:right-6 sm:top-6 z-10 w-9 h-9 rounded-full border border-white/25 bg-black/50 text-white/80 hover:text-white hover:border-white/60 flex items-center justify-center text-lg leading-none">{'\\u2715'}</button>
              <div className="relative flex flex-col items-center text-center" style={{textShadow:'0 2px 10px rgba(0,0,0,.95), 0 0 24px rgba(0,0,0,.8)'}}>
                <div className="vs-coins">
                  {both?(<><span className="vs-coin"><LgCoin token="PTGC"/></span><span className="vs-coin g"><LgCoin token="UFO"/></span></>)
                  :(<span className={`vs-coin${token==='UFO'?' g':''}`}><LgCoin token={token}/></span>)}
                </div>
                <h2 className="font-orbitron text-2xl sm:text-4xl font-bold tracking-wide leading-tight whitespace-nowrap mt-2">
                  <span className={both?'vs-hg':''} style={both?{}:{color:hex}}>Humans</span>
                  <span className="text-white/80 mx-2 sm:mx-3">vs</span>
                  <span style={{color:`rgb(${VS_BOT})`}}>Bots</span>
                </h2>
                <div className="text-white/85 text-[13px] sm:text-base mt-1 font-medium">{P.label} {'·'} {both?'PTGC + UFO':token} volume {'—'} people vs bots</div>
              </div>
"""
    s=s[:a]+new+s[b:]
    rep("""            <div className="relative shrink-0 px-4 sm:px-6 pt-4 sm:pt-6 pb-3 overflow-hidden" style={{minHeight:phone?150:190}}>
              <div aria-hidden="true" className="vs-sky"></div>""",
        """            <div className="relative shrink-0 px-4 sm:px-6 pt-4 sm:pt-5 pb-3 overflow-hidden" style={{minHeight:phone?210:270}}>
              <div aria-hidden="true" className="vs-sky"></div>""")
    rep("""    .vs-strip{position:relative;""","""    .vs-coins{display:flex;align-items:center;justify-content:center;gap:10px;height:104px}
    .vs-coin{display:inline-flex}
    .vs-coin .lg-coin{--u:.5px;--halo:255,120,20;--ring:255,190,80}
    .vs-coin.g .lg-coin{--halo:110,255,40;--ring:140,255,60}
    .vs-hg{background-image:linear-gradient(90deg,#FFE37A 0%,#F2C94C 35%,#C9F06A 65%,#8DFF3A 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;text-shadow:none;filter:drop-shadow(0 2px 4px rgba(0,0,0,.85))}
    @media(max-width:640px){.vs-coins{height:84px}.vs-coin .lg-coin{--u:.4px}}
    .vs-strip{position:relative;""")
    p.write_text(s); print('ok',f)
