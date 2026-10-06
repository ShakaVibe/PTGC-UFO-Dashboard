import pathlib,sys
root=pathlib.Path(sys.argv[1])
for f in ['tools/volume-split.py','index.html']:
    p=root/f; s=p.read_text()
    def rep(old,new):
        global s
        assert s.count(old)==1,(f,old[:70],s.count(old)); s=s.replace(old,new)
    # 1. opens on 30D
    rep("""      const[win,setWin]=useState('7D');
      const[file,setFile]=useState(undefined);
      const[showPools,setShowPools]=useState(false);""","""      const[win,setWin]=useState('30D');   // round 7: opens on 30 days (Shaka)
      const[file,setFile]=useState(undefined);
      const[showPools,setShowPools]=useState(false);""")
    # 2/3. the card art as its own layer so it can be hue-shifted: UFO = green, BOTH = gold fading to green
    rep("""    .vs-card{position:relative;overflow:hidden;border-radius:20px;background:#05070c center/cover no-repeat;padding:16px 18px 14px;min-height:238px;box-shadow:0 12px 30px -16px rgba(0,0,0,.9)}
    .vs-card.hu{background-image:url(logos/hvb/card-gold.jpg)}
    .vs-card.bo{background-image:url(logos/hvb/card-blue.jpg)}""",
"""    .vs-card{position:relative;overflow:hidden;border-radius:20px;background:#05070c;padding:16px 18px 14px;min-height:238px;box-shadow:0 12px 30px -16px rgba(0,0,0,.9)}
    .vs-card .bg,.vs-card .bg2{position:absolute;inset:0;background:center/cover no-repeat;pointer-events:none}
    .vs-card.hu .bg,.vs-card.hu .bg2{background-image:url(logos/hvb/card-gold.jpg)}
    .vs-card.bo .bg{background-image:url(logos/hvb/card-blue.jpg)}
    .vs-card.ufo .bg,.vs-card.ufo .fig{filter:hue-rotate(62deg) saturate(1.05)}   /* round 7: UFO's human card is GREEN — the gold frame and silhouette hue-shifted */
    .vs-card.both .bg2{filter:hue-rotate(62deg) saturate(1.05);-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 30%,#000 70%);mask-image:linear-gradient(90deg,rgba(0,0,0,0) 30%,#000 70%)}   /* BOTH: gold at the left fading to green at the right */
    .vs-card.both .fig{filter:hue-rotate(30deg)}""")
    rep("""    .vs-card::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(4,6,10,.72) 0%,rgba(4,6,10,.5) 50%,rgba(4,6,10,.22) 100%),linear-gradient(180deg,rgba(4,6,10,.35),rgba(4,6,10,0) 30%);pointer-events:none}""",
"""    .vs-card::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(4,6,10,.72) 0%,rgba(4,6,10,.5) 50%,rgba(4,6,10,.22) 100%),linear-gradient(180deg,rgba(4,6,10,.7),rgba(4,6,10,.25) 28%,rgba(4,6,10,0) 45%);pointer-events:none}   /* round 7: darker at the top — the frames' lit corners sat under the label and the percentage */
    .vs-card .hd .n,.vs-card .pct{background:rgba(3,5,9,.62);border-radius:10px;padding:3px 10px;box-shadow:0 0 0 1px rgba(255,255,255,.06)}   /* round 7: the label and the percentage on their own dark pills — "you can't read the percentage" */
    .vs-card .hd{margin:-3px -4px 0}""")
    rep("""                    <div className="vs-card hu" style={{'--acc':rgb}}>
                      <img className="fig" src="logos/hvb/human.webp" alt="" aria-hidden="true"/>""",
"""                    <div className={`vs-card hu${token==='UFO'?' ufo':both?' both':''}`} style={{'--acc':rgb}}>
                      <div className="bg" aria-hidden="true"></div>{both&&<div className="bg2" aria-hidden="true"></div>}
                      <img className="fig" src="logos/hvb/human.webp" alt="" aria-hidden="true"/>""")
    rep("""                    <div className="vs-card bo" style={{'--acc':VS_BOT}}>
                      <img className="fig" src="logos/hvb/bot.webp" alt="" aria-hidden="true"/>""",
"""                    <div className="vs-card bo" style={{'--acc':VS_BOT}}>
                      <div className="bg" aria-hidden="true"></div>
                      <img className="fig" src="logos/hvb/bot.webp" alt="" aria-hidden="true"/>""")
    rep("""    .vs-card>*:not(.fig){position:relative;z-index:2;text-shadow:0 1px 3px rgba(0,0,0,.95),0 0 16px rgba(0,0,0,.8)}""",
        """    .vs-card>*:not(.fig):not(.bg):not(.bg2){position:relative;z-index:2;text-shadow:0 1px 3px rgba(0,0,0,.95),0 0 16px rgba(0,0,0,.8)}""")
    # 4. the banner dimmer
    rep("""    .vs-sky-veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,.5) 60%,rgba(7,7,7,.8) 88%,#070707 100%)}   /* "darken it by about 50 %" + the fade into the body */""",
        """    .vs-sky-veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.64) 0%,rgba(0,0,0,.64) 60%,rgba(7,7,7,.86) 88%,#070707 100%)}   /* round 7: ~64 % ("dim it a little more" than the 50 %) + the fade into the body */""")
    p.write_text(s); print('ok',f)
import pathlib,sys
root=pathlib.Path(sys.argv[1])
for f in ['tools/volume-split.py','index.html']:
    p=root/f; s=p.read_text()
    def rep(old,new):
        global s
        assert s.count(old)==1,(f,old[:70],s.count(old)); s=s.replace(old,new)
    rep("""    .vs-card .hd .n.gg{background:linear-gradient(90deg,#E8C044,#A8FF4A 70%,#7CFC00);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent}""",
        """    .vs-card .hd .n.gg{color:#C9D96A}   /* BOTH: the gold-green midpoint, solid — gradient text vanished on its dark pill (round 7) */""")
    rep("""    .vs-card .pct.gg{background:linear-gradient(90deg,#E8C044,#7CFC00);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent}""",
        """    .vs-card .pct.gg{color:#C9D96A}""")
    p.write_text(s); print('ok',f)
