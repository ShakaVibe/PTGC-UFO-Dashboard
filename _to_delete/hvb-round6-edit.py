import pathlib,sys
root=pathlib.Path(sys.argv[1]) if len(sys.argv)>1 else pathlib.Path('.')
for f in ['tools/volume-split.py','index.html']:
    p=root/f; s=p.read_text()
    def rep(old,new):
        global s
        assert s.count(old)==1,(f,old[:70],s.count(old)); s=s.replace(old,new)
    # the banner: his panorama, darkened ~50 % (Shaka), fading into the body at the foot — no more DAO plate / holders fade
    rep("""    .vs-sky{position:absolute;inset:0;background:url(logos/panels/bg-dao.jpg) center 42%/cover no-repeat;opacity:.95}   /* round 3: the DAO panel's blue mountains — a plate no window wears yet (Shaka: "pick a new background") */""",
"""    .vs-sky{position:absolute;inset:0;background:url(logos/hvb/banner.jpg) center 38%/cover no-repeat}   /* round 6: his humans-vs-bots panorama (logos/hvb/banner.jpg) */
    .vs-sky-veil{position:absolute;inset:0;background:linear-gradient(180deg,rgba(0,0,0,.5) 0%,rgba(0,0,0,.5) 60%,rgba(7,7,7,.8) 88%,#070707 100%)}   /* "darken it by about 50 %" + the fade into the body */""")
    rep("""              <div aria-hidden="true" className="vs-sky"></div>
              <div aria-hidden="true" className="nh-sky-fade"></div>""",
"""              <div aria-hidden="true" className="vs-sky"></div>
              <div aria-hidden="true" className="vs-sky-veil"></div>""")
    # the cards: a veil over the frame art so the type wins at the bright corners; the figure at the right, whole, mid-height
    rep("""    .vs-card .fig{position:absolute;right:2%;bottom:-4%;height:96%;width:auto;max-width:58%;object-fit:contain;object-position:right bottom;opacity:.62;pointer-events:none;-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 38%);mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 38%)}
    .vs-card>*:not(.fig){position:relative;text-shadow:0 1px 3px rgba(0,0,0,.9),0 0 14px rgba(0,0,0,.7)}""",
"""    .vs-card::after{content:'';position:absolute;inset:0;background:linear-gradient(90deg,rgba(4,6,10,.72) 0%,rgba(4,6,10,.5) 50%,rgba(4,6,10,.22) 100%),linear-gradient(180deg,rgba(4,6,10,.35),rgba(4,6,10,0) 30%);pointer-events:none}
    .vs-card .fig{position:absolute;right:3%;top:5%;height:90%;width:auto;max-width:56%;object-fit:contain;object-position:right center;opacity:.6;pointer-events:none;z-index:1;-webkit-mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 40%);mask-image:linear-gradient(90deg,rgba(0,0,0,0) 0%,#000 40%)}
    .vs-card>*:not(.fig){position:relative;z-index:2;text-shadow:0 1px 3px rgba(0,0,0,.95),0 0 16px rgba(0,0,0,.8)}""")
    p.write_text(s); print('ok',f)
