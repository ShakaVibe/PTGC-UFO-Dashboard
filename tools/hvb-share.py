# Humans vs Bots share card (2026-10-06, Shaka: "lets make the socials live... as well as the share button inside the window").
# Built from design/volume-split/mock-share-v1.html (v3): wide 1200x675 only, screenshot-only (gradient text + blend modes).
#  - CSS .hvs-* (next to the New Holders share card's .nhs-*)
#  - HvbShareCard / HvbShareModal / HvbShareSocial (above VolumeSplitModal)
#  - the camera in the window's toolbar, the card inside the window
#  - Socials: a "Humans vs Bots" row in all three columns (his robot, logos/hvb/sh-bot.webp), Dashboard state showHvbShare
# Idempotent. Usage: python3 tools/hvb-share.py [index.html]
import sys
p=sys.argv[1] if len(sys.argv)>1 else 'index.html'
s=open(p,encoding='utf-8').read()

CSS='''    /* ---- Humans vs Bots share card (2026-10-06; design/volume-split/mock-share-v1.html v3) — 1200×675, screenshot-only ---- */
    .hvs{--a:#E8C044;--rgb:232,192,68;--b:#4FD1FF;--brgb:79,209,255;position:relative;overflow:hidden;background:#06070a;width:1200px;height:675px;font-family:'Rajdhani',sans-serif;color:#fff;text-align:left}
    .hvs.ufo{--a:#9DFF3A;--rgb:124,252,0}
    .hvs-sky{position:absolute;inset:0;background:url(logos/hvb/banner.jpg) 50% 30%/cover no-repeat}
    .hvs-tint{position:absolute;inset:0;mix-blend-mode:color;background:linear-gradient(90deg,rgba(120,230,60,.95) 0%,rgba(120,230,60,.95) 30%,rgba(120,230,60,0) 56%)}
    .hvs-veil{position:absolute;inset:0;background:radial-gradient(ellipse 36% 70% at 50% 28%,rgba(0,0,0,.5),rgba(0,0,0,0) 100%),linear-gradient(180deg,rgba(0,0,0,.28) 0%,rgba(0,0,0,.3) 40%,rgba(6,7,10,.86) 64%,#06070a 100%)}
    .hvs-c{position:absolute;inset:0;padding:30px 56px 30px;display:flex;flex-direction:column;align-items:center}
    .hvs-date{position:absolute;right:56px;top:40px;font-size:15px;font-weight:600;letter-spacing:.22em;text-transform:uppercase;color:#fff;text-shadow:0 2px 6px #000;z-index:1}
    .hvs-coin{margin-top:6px}.hvs-coin .lg-coin{--u:.66px}
    .hvs-coins{display:flex;gap:26px;margin-top:6px}.hvs-coins .lg-coin{--u:.62px}
    .hvs .g .lg-coin{--halo:110,255,40;--ring:140,255,60}
    .hvs-title{font-family:'Orbitron',monospace;font-weight:700;font-size:56px;letter-spacing:.04em;line-height:1;margin-top:14px;text-shadow:0 3px 3px #000,0 0 30px rgba(0,0,0,.9);white-space:nowrap}
    .hvs-title .h{color:var(--a)}.hvs-title .v{color:#C8CDD6;font-size:40px;letter-spacing:.1em;margin:0 10px}.hvs-title .b{color:var(--b)}
    .hvs.both .hvs-title .h{background:linear-gradient(90deg,#F6D56A 0%,#E8C044 35%,#B9F24A 70%,#9DFF3A 100%);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none;filter:drop-shadow(0 3px 3px #000)}
    .hvs-period{display:inline-block;margin-top:14px;font-family:'Orbitron',monospace;font-weight:700;font-size:13px;letter-spacing:.24em;padding:9px 18px;border-radius:999px;background:rgba(0,0,0,.6);border:1px solid rgba(255,255,255,.3);color:rgba(255,255,255,.85);white-space:nowrap}
    .hvs-split{flex:none;margin-top:auto;padding-top:14px;width:100%;display:grid;grid-template-columns:1fr 1fr;gap:22px}
    .hvs-side{position:relative;border-radius:22px;padding:18px 26px 14px;background:linear-gradient(180deg,rgba(var(--srgb),.14),rgba(6,8,12,.86) 50%,rgba(6,8,12,.92));border:2px solid rgba(var(--srgb),.7);box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 0 40px -12px rgba(var(--srgb),.7);overflow:hidden;min-width:0}
    .hvs-side.hu{--s:var(--a);--srgb:var(--rgb)}
    .hvs-side.bo{--s:var(--b);--srgb:var(--brgb)}
    .hvs.both .hvs-side.hu{--s:#D9E85A;--srgb:200,235,80}
    .hvs-side .art{position:absolute;right:14px;top:4px;width:200px;height:142px;object-fit:contain;object-position:right top;opacity:.9;filter:drop-shadow(0 0 22px rgba(var(--srgb),.35))}
    .hvs.ufo .hvs-side.hu .art{filter:hue-rotate(60deg) drop-shadow(0 0 22px rgba(120,255,60,.35))}
    .hvs-side .tag{font-family:'Orbitron',monospace;font-weight:700;font-size:24px;letter-spacing:.14em;color:var(--s);text-shadow:0 2px 4px #000}
    .hvs-side .pct{font-family:'Orbitron',monospace;font-weight:700;font-size:80px;line-height:1;margin-top:4px;color:#fff;text-shadow:0 4px 6px #000,0 0 30px rgba(0,0,0,.8);font-variant-numeric:tabular-nums}
    .hvs-side .pct b{color:var(--s);font-size:48px;font-weight:700;margin-left:2px}
    .hvs.both .hvs-side.hu .pct b{background:linear-gradient(180deg,#F6D56A,#B9F24A);-webkit-background-clip:text;background-clip:text;color:transparent}
    .hvs-side .rule{height:1px;margin-top:12px;background:linear-gradient(90deg,rgba(var(--srgb),.7),rgba(var(--srgb),.15))}
    .hvs-side .cols{display:grid;grid-template-columns:1fr 1fr 1.3fr;margin-top:10px}
    .hvs-side .cols>div{padding:0 14px;border-left:1px solid rgba(255,255,255,.14);min-width:0}
    .hvs-side .cols>div:first-child{padding-left:0;border-left:0}
    .hvs-side .k{font-family:'Orbitron',monospace;font-weight:500;font-size:11px;letter-spacing:.22em;color:rgba(255,255,255,.65);text-transform:uppercase;white-space:nowrap}
    .hvs-side .v{font-size:34px;font-weight:700;line-height:1.05;white-space:nowrap;margin-top:4px;font-variant-numeric:tabular-nums}
    .hvs-side .v.gen{color:var(--s)}
    .hvs-side .note{margin-top:8px;text-align:center;font-family:'Orbitron',monospace;font-weight:500;font-size:11px;letter-spacing:.2em;text-transform:uppercase;color:rgba(255,255,255,.6);white-space:nowrap}
    .hvs-side .note b{color:var(--s);font-weight:700}
    .hvs-bar{flex:none;width:100%;height:16px;border-radius:999px;margin-top:14px;background:rgba(255,255,255,.08);overflow:hidden;display:flex;box-shadow:inset 0 1px 2px rgba(0,0,0,.8)}
    .hvs-bar i{display:block;height:100%}
    .hvs-bar .h{background:linear-gradient(90deg,rgba(var(--rgb),.85),var(--a));box-shadow:0 0 16px rgba(var(--rgb),.7)}
    .hvs.both .hvs-bar .h{background:linear-gradient(90deg,#E8C044,#B9F24A)}
    .hvs-bar .b{background:linear-gradient(90deg,var(--b),rgba(var(--brgb),.8));flex:1}
    .hvs-strip{flex:none;width:100%;margin-top:12px;display:flex;align-items:center;justify-content:center;position:relative}
    .hvs-strip .it{padding:0 34px;text-align:center;border-left:1px solid rgba(255,255,255,.18)}
    .hvs-strip .it:first-child{border-left:0}
    .hvs-strip .k{font-family:'Orbitron',monospace;font-weight:500;font-size:12px;letter-spacing:.24em;text-transform:uppercase;color:rgba(255,255,255,.6)}
    .hvs-strip b{display:block;font-size:30px;line-height:1.05;color:#fff;margin-top:2px;font-variant-numeric:tabular-nums}
    .hvs-strip .site{position:absolute;right:0;top:50%;transform:translateY(-50%);font-family:'Orbitron',monospace;font-weight:700;font-size:24px;color:var(--a);text-shadow:0 2px 6px #000}
    .hvs.both .hvs-strip .site{background:linear-gradient(90deg,#E8C044,#9DFF3A);-webkit-background-clip:text;background-clip:text;color:transparent;text-shadow:none}
'''
anchor='    .nhs{--a:#E8C044;'
if '.hvs{' not in s:
    assert anchor in s; s=s.replace(anchor,CSS+anchor,1)

JSX='''    /* ================= Humans vs Bots — share card (2026-10-06) =================
       design/volume-split/mock-share-v1.html (v3). Wide 1200×675 only, `ShareCardModal screenshot` (the BOTH title and the
       UFO banner tint are gradient text / a colour blend — html2canvas flattens both). Opens on the window's token and
       period; PTGC / UFO / BOTH toolbar. Value generated = volume × the token's fee (PTGC 5 %, UFO 6 %), per token on BOTH.
       Socials → "Humans vs Bots" in all three columns (HvbShareSocial fetches the hourly file itself). */
    const hvsVg=(file,mode,P,feeRates)=>{
      const per=tk=>file&&file.tokens[tk]&&file.tokens[tk].periods&&file.tokens[tk].periods[P.p];
      const toks=mode==='BOTH'?['PTGC','UFO']:[mode];
      let h=0,b=0;for(const tk of toks){const q=per(tk);if(!q)continue;const f=(feeRates&&feeRates[tk])||(tk==='UFO'?0.06:0.05);h+=q.human.usd*f;b+=q.bot.usd*f;}
      return{h,b};
    };
    const HvbShareCard=({mode,file,P,feeRates})=>{
      const both=mode==='BOTH',ufo=mode==='UFO';
      const view=React.useMemo(()=>file?vsView(file,mode,P,{}):null,[file,mode,P]);
      if(!view)return <div className={`hvs${ufo?' ufo':both?' both':''}`}><div className="hvs-sky" aria-hidden="true"></div><div className="hvs-veil" aria-hidden="true"></div></div>;
      const vg=hvsVg(file,mode,P,feeRates);
      const tot=view.human.usd+view.bot.usd;
      const pH=tot>0?Math.round(view.human.usd/tot*100):0,pB=tot>0?100-pH:0;
      const routers=view.humans.length,botN=Object.values(view.senders).filter(x=>x.kind==='bot').length;
      const Side=({cls,tag,pct,vol,n,gen,note,art})=>(
        <div className={`hvs-side ${cls}`}>
          <img className="art" src={art} alt="" aria-hidden="true"/>
          <div className="tag">{tag}</div>
          <div className="pct">{pct}<b>%</b></div>
          <div className="rule" aria-hidden="true"></div>
          <div className="cols">
            <div><div className="k">Volume</div><div className="v">{fmtUSD(vol)}</div></div>
            <div><div className="k">Trades</div><div className="v">{fmt(n)}</div></div>
            <div><div className="k">Value generated</div><div className="v gen">{fmtUSD(gen)}</div></div>
          </div>
          <div className="note">{note}</div>
        </div>);
      return(
        <div className={`hvs${ufo?' ufo':both?' both':''}`}>
          <div className="hvs-sky" aria-hidden="true"></div>
          {ufo&&<div className="hvs-tint" aria-hidden="true"></div>}
          <div className="hvs-veil" aria-hidden="true"></div>
          <div className="hvs-date">{nhsToday()}</div>
          <div className="hvs-c">
            {both?<div className="hvs-coins"><div><LgCoin token="PTGC"/></div><div className="g"><LgCoin token="UFO"/></div></div>:<div className={`hvs-coin${ufo?' g':''}`}><LgCoin token={mode}/></div>}
            <div className="hvs-title"><span className="h">HUMANS</span><span className="v">vs</span><span className="b">BOTS</span></div>
            <span className="hvs-period">{both?'PTGC + UFO':mode} VOLUME {'\\u00b7'} {P.label.toUpperCase()}</span>
            <div className="hvs-split">
              <Side cls="hu" tag="HUMANS" pct={pH} vol={view.human.usd} n={view.human.n} gen={vg.h} art="logos/hvb/human.webp"
                note={<><b>{pH}%</b> of total volume {'\\u00b7'} via <b>{fmt(routers)}</b> router{routers===1?'':'s'}</>}/>
              <Side cls="bo" tag="ARB BOTS" pct={pB} vol={view.bot.usd} n={view.bot.n} gen={vg.b} art="logos/hvb/bot.webp"
                note={<><b>{pB}%</b> of total volume {'\\u00b7'} from <b>{fmt(botN)}</b> bot contract{botN===1?'':'s'}</>}/>
            </div>
            <div className="hvs-bar" aria-hidden="true"><i className="h" style={{width:`${pH}%`}}></i><i className="b"></i></div>
            <div className="hvs-strip">
              <div className="it"><div className="k">Total volume</div><b>{fmtUSD(tot)}</b></div>
              <div className="it"><div className="k">Trades</div><b>{fmt(view.human.n+view.bot.n)}</b></div>
              <div className="it"><div className="k">Value generated</div><b>{fmtUSD(vg.h+vg.b)}</b></div>
              <span className="site">ptgc-ufo.com</span>
            </div>
          </div>
        </div>);
    };
    const HvbShareModal=({token:initial,file,win,setWin,feeRates,loading=false,error=false,onRetry,onClose})=>{
      const[mode,setMode]=useState(initial==='BOTH'?'BOTH':initial==='UFO'?'UFO':'PTGC');
      const P=VS_PERIODS.find(w=>w.k===win)||VS_PERIODS[2];
      const T=NH_THEME[mode==='UFO'?'UFO':'PTGC'];
      const controls=(<>
        <NhPills items={[{k:'PTGC',label:'PTGC card'},{k:'UFO',label:'UFO card'},{k:'BOTH',label:'Both tokens on one card'}]} value={mode} onChange={setMode} label="Card" rgb={T.rgb}/>
        {setWin&&<NhPills items={VS_PERIODS} value={win} onChange={setWin} label="Period" rgb={T.rgb}/>}
      </>);
      const stamp=new Date().toISOString().slice(0,10);
      return(
        <ShareCardModal onClose={onClose} width={1200} height={675} screenshot controls={controls} toolbarClass="mb-6" label="Humans vs Bots share card" filename={`${mode.toLowerCase()}-humans-vs-bots-${win.toLowerCase()}-${stamp}.png`}>
          <div style={{position:'relative',width:1200,height:675}}>
            <HvbShareCard mode={mode} file={file} P={P} feeRates={feeRates}/>
            <CardLoadState loading={loading} error={error} what="the volume file" onRetry={onRetry} radius="0" font="'Rajdhani',sans-serif"/>
          </div>
        </ShareCardModal>);
    };
    const HvbShareSocial=({mode,feeRates,onClose})=>{
      const[win,setWin]=useState('30D');
      const[file,setFile]=useState(undefined);
      const[tries,setTries]=useState(0);
      useEffect(()=>{let live=true;setFile(undefined);fetchSwapVolume(tries>0).then(j=>{if(live)setFile(j);});return()=>{live=false;};},[tries]);
      return <HvbShareModal token={mode} file={file||null} win={win} setWin={setWin} feeRates={feeRates} loading={file===undefined} error={file===null} onRetry={()=>setTries(n=>n+1)} onClose={onClose}/>;
    };
'''
anchor2="    const VolumeSplitModal=({token:initial,feeRates,pairs,otherPairs,onClose})=>{"
if 'const HvbShareCard=' not in s:
    assert anchor2 in s; s=s.replace(anchor2,JSX+anchor2,1)

# the window: share state, the camera after the Period pills, the card
old="      const[showHumans,setShowHumans]=useState(false);\n      const load=(force)=>{setFile(undefined);fetchSwapVolume(force).then(setFile);};"
new="      const[showHumans,setShowHumans]=useState(false);\n      const[shareCard,setShareCard]=useState(false);   // the 📷: HvbShareModal (2026-10-06)\n      const load=(force)=>{setFile(undefined);fetchSwapVolume(force).then(setFile);};"
if 'const[shareCard,setShareCard]=useState(false);   // the 📷: HvbShareModal' not in s:
    assert old in s; s=s.replace(old,new,1)
old='''                <NhPills items={VS_PERIODS} value={win} onChange={setWin} label="Period" rgb={rgb}/>
                <div className="ml-auto text-[11px] text-white/60 tabular-nums" style={{textShadow:'0 1px 6px rgba(0,0,0,.9)'}}>
                  {file===undefined?'Loading…':file?'''
new='''                <NhPills items={VS_PERIODS} value={win} onChange={setWin} label="Period" rgb={rgb}/>
                <button type="button" onClick={()=>setShareCard(true)} disabled={!view} aria-label="Share Humans vs Bots as an image" title="Share card" className="tap h-[30px] w-[34px] rounded-[10px] border border-white/15 bg-black/55 text-white/70 hover:text-white hover:border-white/40 flex items-center justify-center text-[15px] leading-none disabled:opacity-30 transition-colors" style={{minHeight:0,backdropFilter:'blur(8px)',WebkitBackdropFilter:'blur(8px)'}}>{'\\u{1F4F7}'}</button>
                <div className="ml-auto text-[11px] text-white/60 tabular-nums" style={{textShadow:'0 1px 6px rgba(0,0,0,.9)'}}>
                  {file===undefined?'Loading…':file?'''
if 'Share Humans vs Bots as an image' not in s:
    assert old in s; s=s.replace(old,new,1)
# the card inside the window — before the window's closing </Modal> (the one after .vs-conf)
old='''                  <p className="vs-conf">'''
i=s.index(old); j=s.index('        </Modal>',i)
seg=s[i:j]
if 'shareCard&&file&&<HvbShareModal' not in seg:
    s=s[:j]+"          {shareCard&&file&&<HvbShareModal token={token} file={file} win={win} setWin={setWin} feeRates={feeRates} onClose={()=>setShareCard(false)}/>}\n"+s[j:]

# Socials rows (all three columns), Dashboard state + render
row=lambda mode,sub:f'''<ShRow tone="blue" icon={{`logos/hvb/sh-bot.webp?v=${{HVB_ART_V}}`}} title="Humans vs Bots" sub="{sub}" onClick={{()=>{{setSocialReturn(true);setShowHvbShare('{mode}')}}}}/>'''
for mode,sub,nh in [('PTGC','Who moves the volume','''<ShRow tone="green" icon={`logos/holders/nh-ic-new.webp?v=${NH_ART_V}`} title="New Holder Details" sub="New holder analytics" onClick={()=>{setSocialReturn(true);setShowNhShare('PTGC')}}/>'''),
                    ('UFO','Who moves the volume','''<ShRow tone="green" icon={`logos/holders/nh-ic-new.webp?v=${NH_ART_V}`} title="New Holder Details" sub="New holder analytics" onClick={()=>{setSocialReturn(true);setShowNhShare('UFO')}}/>'''),
                    ('BOTH','Who moves the volume, both tokens','''<ShRow tone="green" icon={`logos/holders/nh-ic-new.webp?v=${NH_ART_V}`} title="New Holder Details" sub="New holder analytics for both tokens" onClick={()=>{setSocialReturn(true);setShowNhShare('BOTH')}}/>''')]:
    if f"setShowHvbShare('{mode}')" not in s:
        assert s.count(nh)==1,(mode,s.count(nh)); s=s.replace(nh,nh+"\n                  "+row(mode,sub),1)
old="      const[showNhShare,setShowNhShare]=useState(null);   // Socials → New Holder Details: 'PTGC' | 'UFO' | 'BOTH' (2026-10-04)"
new=old+"\n      const[showHvbShare,setShowHvbShare]=useState(null);   // Socials → Humans vs Bots share card: 'PTGC' | 'UFO' | 'BOTH' (2026-10-06)"
if 'setShowHvbShare]=useState' not in s:
    assert old in s; s=s.replace(old,new,1)
old="          {showNhShare&&<NhShareSocial mode={showNhShare} token={token} price={data&&data.price>0?data.price:0} onClose={()=>closeModalAndReturn(setShowNhShare)}/>}"
new=old+"\n          {showHvbShare&&<HvbShareSocial mode={showHvbShare} feeRates={{PTGC:TOKENS.PTGC.feeRate||0.05,UFO:TOKENS.UFO.feeRate||0.06}} onClose={()=>closeModalAndReturn(setShowHvbShare)}/>}"
if '<HvbShareSocial mode={showHvbShare}' not in s:
    assert old in s; s=s.replace(old,new,1)
# art version for the Socials robot
old="    const VOL_SPLIT_LIVE=true;"
if 'const HVB_ART_V=' not in s:
    assert old in s; s=s.replace(old,"    const HVB_ART_V=1;   // bump when logos/hvb/sh-bot.webp changes under the same name (gotcha 38)\n"+old,1)
open(p,'w',encoding='utf-8').write(s); print('hvb-share ok')
