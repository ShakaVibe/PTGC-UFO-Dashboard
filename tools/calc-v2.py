#!/usr/bin/env python3
"""Calculators page skin (2026-10-05): Shaka's gold space art as the page plate, the "Grays Calculators" metallic title, his
five calculator buttons with his icons, the per-calculator disclaimer cards framed, the panels darkened — from
design/calculators/mock-calc-v3.html (README = every decision). Run from the repo root on a clean calculators.html:
python3 tools/calc-v2.py  (refuses to run twice)."""
import re,sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
p=root/'calculators.html'; s=p.read_text()
if 'cp-page' in s: sys.exit('already applied')
def rep(old,new,count=1):
    global s
    n=s.count(old); assert n==count,(old[:70],n); s=s.replace(old,new)

css='''    /* CALCULATORS PAGE SKIN (2026-10-05) — design/calculators/mock-calc-v3.html + README. His art as a FIXED plate under a 62 %
       veil (50 % was "not enough"), the title in the Socials Hub's metallic style, his buttons with his icons, the disclaimer
       cards framed. cp-* only; the calculators' own markup is untouched except the title block and the tab buttons. */
    .cp-page{position:relative;background:#000}
    .cp-art{position:fixed;inset:0;z-index:0;pointer-events:none;background:#000 url(logos/calculators/calc-bg.jpg) center top/cover no-repeat}
    .cp-art::after{content:'';position:absolute;inset:0;background:rgba(0,0,0,.62)}
    .cp-page>:not(.cp-art){position:relative;z-index:1}
    .cp-band{height:0;position:relative}
    .cp-band::before{content:'';position:absolute;left:0;right:0;top:0;height:170px;pointer-events:none;background:linear-gradient(180deg,#000 0%,rgba(0,0,0,.6) 45%,rgba(0,0,0,0) 100%)}   /* a black gap under the tab band, the Hub's rule */
    .cp-ttl{position:relative;text-align:center;margin:-6px auto 26px;padding:22px 40px 18px;max-width:900px}
    .cp-ttl::before{content:"";position:absolute;inset:0;border-radius:50%;background:radial-gradient(ellipse 55% 60% at 50% 48%,rgba(0,0,0,.86) 0%,rgba(0,0,0,.72) 40%,rgba(0,0,0,.35) 70%,rgba(0,0,0,0) 100%);filter:blur(6px);z-index:0}
    .cp-ttl>*{position:relative;z-index:1}
    .cp-ttl h2{margin:0;line-height:1}
    .cp-t{font-family:'Orbitron',monospace;font-weight:900;font-size:64px;line-height:1;letter-spacing:.01em;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;filter:drop-shadow(0 3px 3px #000) drop-shadow(0 0 22px rgba(0,0,0,.9))}
    .cp-t.g{background-image:linear-gradient(180deg,#FFF3B0 0%,#F7D35A 40%,#C9921A 62%,#F2C94C 100%)}
    .cp-t.w{background-image:linear-gradient(180deg,#FFF 0%,#E6E6E6 45%,#8C8C8C 60%,#DDD 100%);margin-left:.22em}
    .cp-ttl p{text-shadow:0 1px 3px #000}
    .cp-btns{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;width:100%;max-width:1070px}
    .cp-btn{grid-column:span 2;--c:242,201,76;--c2:255,215,120;height:66px;border-radius:12px;border:1.5px solid rgba(var(--c),.6);display:flex;align-items:center;gap:16px;padding:0 18px 0 16px;cursor:pointer;color:#fff;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:20px;letter-spacing:.01em;position:relative;
      background:radial-gradient(ellipse at 50% 0%,rgba(var(--c),.16),rgba(0,0,0,0) 70%),repeating-linear-gradient(0deg,rgba(255,255,255,.012) 0 1px,transparent 1px 3px),linear-gradient(180deg,rgba(14,14,10,.9),rgba(6,6,8,.92));
      box-shadow:0 0 18px -6px rgba(var(--c),.45),inset 0 1px 0 rgba(255,255,255,.08),0 8px 20px -10px rgba(0,0,0,.9);transition:filter .2s,transform .2s}
    .cp-btn:nth-child(n+4){grid-column:span 3}   /* three gold over two blue (his mock-up) — a sixth live calculator would take a third row */
    .cp-btn.blue{--c:60,170,255;--c2:140,215,255;color:#7FD4FF;background:radial-gradient(ellipse at 50% 0%,rgba(var(--c),.16),rgba(0,0,0,0) 70%),repeating-linear-gradient(0deg,rgba(255,255,255,.012) 0 1px,transparent 1px 3px),linear-gradient(180deg,rgba(6,14,24,.92),rgba(4,8,14,.94))}
    .cp-btn.on{border-width:2px;border-color:rgba(var(--c2),.95);box-shadow:0 0 26px -2px rgba(var(--c),.75),0 0 60px -14px rgba(var(--c),.6),inset 0 1px 0 rgba(255,255,255,.16);background:radial-gradient(ellipse at 50% 0%,rgba(var(--c),.3),rgba(0,0,0,0) 70%),repeating-linear-gradient(0deg,rgba(255,255,255,.012) 0 1px,transparent 1px 3px),linear-gradient(180deg,rgba(24,20,8,.92),rgba(8,7,4,.94))}
    .cp-btn.blue.on{background:radial-gradient(ellipse at 50% 0%,rgba(var(--c),.3),rgba(0,0,0,0) 70%),repeating-linear-gradient(0deg,rgba(255,255,255,.012) 0 1px,transparent 1px 3px),linear-gradient(180deg,rgba(8,22,36,.92),rgba(4,10,18,.94));color:#fff}
    .cp-btn:hover{filter:brightness(1.1);transform:translateY(-1px)}
    .cp-btn img{width:44px;height:44px;object-fit:contain;flex:none;max-width:none;filter:drop-shadow(0 3px 6px rgba(0,0,0,.85))}
    .cp-btn .lb{flex:1;text-align:left;min-width:0;line-height:1.1}
    .cp-btn .ch{font-weight:700;font-size:22px;color:rgb(var(--c2));line-height:1}
    .cp-dc{background:rgba(8,8,10,.86)!important;border-color:rgba(255,255,255,.1)!important;box-shadow:0 10px 40px -10px rgba(0,0,0,.9)}
    .cp-page [class*="bg-[#111]/80"]{background-color:rgba(10,10,12,.9)}   /* the calculators' panels, a touch more solid over the art */
    @media(max-width:640px){
      .cp-art{position:absolute;inset:auto 0 auto 0;top:0;height:1000px}   /* no fixed attachment on iOS: the art over the top of the page, fading to black */
      .cp-art::before{content:'';position:absolute;left:0;right:0;bottom:0;height:260px;z-index:1;background:linear-gradient(180deg,rgba(0,0,0,0),#000)}
      .cp-band::before{height:110px}
      .cp-ttl{padding:16px 8px 12px;margin-bottom:18px}
      .cp-t{font-size:30px;letter-spacing:0}.cp-t.w{margin-left:.18em}
      .cp-btns{grid-template-columns:1fr 1fr;gap:9px}
      .cp-btn,.cp-btn:nth-child(n+4){grid-column:auto;height:56px;font-size:15px;gap:9px;padding:0 10px}
      .cp-btn img{width:34px;height:34px}.cp-btn .ch{font-size:18px}
    }
'''
rep("    .animate-grow-btn{animation:growBtnPulse 2.5s ease-in-out infinite}\n  </style>","    .animate-grow-btn{animation:growBtnPulse 2.5s ease-in-out infinite}\n"+css+"  </style>")

# the page shell: the plate + the band under the header
rep('''      return(
        <div className="min-h-screen bg-[#0a0a0a]">
          {hdrV2?<SiteHeaderV2''','''      return(
        <div className="min-h-screen bg-[#0a0a0a] cp-page">
          <div className="cp-art" aria-hidden="true"></div>
          {hdrV2?<SiteHeaderV2''')
rep('''          <CalculatorsTab token={token} cfg={cfg}''','''          <div className="cp-band" aria-hidden="true"></div>
          <CalculatorsTab token={token} cfg={cfg}''')

# the title block
rep('''          <div className="text-center mb-8">
            <h2 className="text-3xl sm:text-4xl font-bold text-white font-orbitron tracking-widest">CALCULATOR</h2>
            <div className="w-24 sm:w-32 h-0.5 mx-auto mt-1.5 rounded-full" style={{background:`linear-gradient(90deg,transparent,${glowColor}0.8),transparent)`}}></div>
''','''          <div className="cp-ttl mb-8">
            <h2><span className="cp-t g">Grays</span><span className="cp-t w">Calculators</span></h2>
''')

# the buttons: his, with his icons (CALC_ICONS by id; blue for the two "money" calculators)
a=s.index('            <div className="flex gap-2 flex-wrap justify-center w-full max-w-2xl">\n              {liveCalcs.map(b=>{')
b=s.index('            {/* Coming-soon strip',a)
old=s[a:b]
assert old.rstrip().endswith('</div>') and old.count('liveCalcs.map')==1
new='''            <div className="cp-btns" role="tablist" aria-label="Calculators">
              {liveCalcs.map(b=>{
                const active=calcTab===b.id;
                return(
                  <button key={b.id} type="button" role="tab" aria-selected={active} onClick={()=>setCalcTab(b.id)} className={`cp-btn ${CALC_BLUE.includes(b.id)?'blue':''} ${active?'on':''}`}>
                    {CALC_ICONS[b.id]&&<img src={CALC_ICONS[b.id]} alt="" aria-hidden="true"/>}
                    <span className="lb">{b.label}</span>
                    <span className="ch" aria-hidden="true">{'\\u203A'}</span>
                    {b.isNew&&!active&&(<span style={{position:'absolute',top:'-1px',right:'-1px',background:'linear-gradient(135deg,#7CFC00,#4ade80)',color:'#000',fontSize:'9px',fontWeight:900,padding:'2px 6px',borderRadius:'0 10px 0 6px',letterSpacing:'0.08em',lineHeight:1.4,fontFamily:"'Orbitron',monospace"}}>NEW</span>)}
                  </button>
                );
              })}
            </div>
'''
s=s[:a]+new+s[b:]
rep('''      const ALL_CALCS=[{id:'xmult',label:'X Multiplier'},''','''      /* his icons on the buttons (2026-10-05, calculator_button_icons.zip → logos/calculators/ic-*.webp); the two "money" calculators are blue, his mock-up */
      const CALC_ICONS={xmult:'logos/calculators/ic-x_multiplier.webp',moon:'logos/calculators/ic-moon_math.webp',rewards:'logos/calculators/ic-rewards.webp',fresh:'logos/calculators/ic-new_capital_simulator.webp',growth:'logos/calculators/ic-10_year_projection.webp'};
      const CALC_BLUE=['fresh','growth'];
      const ALL_CALCS=[{id:'xmult',label:'X Multiplier'},''')

# the five disclaimer cards, framed
s,n=re.subn(r'className="rounded-xl bg-white/\[0\.02\] border border-white/\[0\.05\] (p-5|px-5 py-4)',r'className="cp-dc rounded-xl bg-white/[0.02] border border-white/[0.05] \1',s); assert n==6,n   # the five calculators' disclaimer cards (the LV analyser's too)
# Back to Dashboard: a solid plate under it
rep('''<button onClick={onBack} className="px-6 py-2.5 rounded-lg border border-white/10 text-white/40 hover:text-white/70 hover:border-white/20 transition-all text-base">''',
    '''<button onClick={onBack} className="px-6 py-2.5 rounded-lg border border-white/15 bg-black/60 text-white/50 hover:text-white/80 hover:border-white/30 transition-all text-base">''')
p.write_text(s)
print('applied',len(s))
