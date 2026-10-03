#!/usr/bin/env python3
"""Socials Hub redesign (2026-10-03) — applies the build to index.html in place. Exact-string edits, each asserted once,
so the same script runs on the cloud clone (harness) and on Shaka's Mac. Mock-up + every decision: design/socials-hub/.

    python3 tools/socials-hub.py            # edit index.html
    python3 tools/socials-hub.py --check    # just say whether it is already applied

Three edits: (1) the `sh-*` CSS block at the end of the p2 block; (2) ShRow / ShCol at module scope above
DashboardSkeleton; (3) the Socials tab's JSX — same handlers, new frame, the 2026-10-03 row order.
"""
import sys, re, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
p = ROOT / 'index.html'
s = p.read_text(encoding='utf-8')
if '.sh-col{' in s:
    print('already applied'); sys.exit(0)
if '--check' in sys.argv:
    print('not applied'); sys.exit(1)

def once(old, new, label):
    global s
    n = s.count(old)
    assert n == 1, f'{label}: expected 1 match, found {n}'
    s = s.replace(old, new)

# ── (1) CSS ───────────────────────────────────────────────────────────────────────────────────────────────────────────
CSS = r'''
    /* ===== SOCIALS HUB (2026-10-03) — Shaka's redesign of the Socials tab (design/socials-hub/mock-hub-v1.html, renders
       there). His sky once, covering the hub (logos/socials/hub-sky.jpg); three framed columns gold / green / blue; his icon on
       every row (logos/socials/hub/<col>-<key>.png — cut from his mock-up, to be swapped for the full-size sheet). Rows reordered
       2026-10-03 so the five cards every column has sit level across the page. Every handler is the old hub's. */
    .sh{position:relative;overflow:hidden;background:#030405;padding:36px 18px 44px;margin-top:18px}
    .sh-sky{position:absolute;inset:0;pointer-events:none;overflow:hidden}
    .sh-sky img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center top;display:block}
    .sh-sky img.ft{display:none}
    @media(max-width:900px){.sh-sky img{height:auto;object-fit:unset;top:0;bottom:auto}.sh-sky img.ft{display:block;top:auto;bottom:0;height:auto}}
    .sh-sky::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,#0a0a0a 0,rgba(10,10,10,.55) 28px,rgba(10,10,10,0) 90px,rgba(3,4,5,0) 70%,rgba(3,4,5,.35) 100%)}
    .sh-in{position:relative;max-width:1200px;margin:0 auto}
    .sh-title{position:relative;text-align:center;margin:-10px auto 22px;padding:22px 40px 18px;max-width:900px}
    .sh-title::before{content:"";position:absolute;inset:0;border-radius:50%;background:radial-gradient(ellipse 55% 60% at 50% 48%,rgba(0,0,0,.86) 0%,rgba(0,0,0,.72) 40%,rgba(0,0,0,.35) 70%,rgba(0,0,0,0) 100%);filter:blur(6px);z-index:0}
    .sh-title>*{position:relative;z-index:1}
    .sh-title h2{margin:0;line-height:1}
    .sh-t{font-family:'Orbitron',monospace;font-weight:900;font-size:64px;line-height:1;letter-spacing:.01em;-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent;filter:drop-shadow(0 3px 3px #000) drop-shadow(0 0 22px rgba(0,0,0,.9))}
    .sh-t.g{background-image:linear-gradient(180deg,#FFF3B0 0%,#F7D35A 40%,#C9921A 62%,#F2C94C 100%)}
    .sh-t.w{background-image:linear-gradient(180deg,#FFF 0%,#E6E6E6 45%,#8C8C8C 60%,#DDD 100%);margin-left:.22em}
    .sh-sub{margin-top:10px;font-weight:700;font-size:20px;letter-spacing:.12em;color:#fff;text-shadow:0 2px 4px #000,0 0 14px rgba(0,0,0,.9)}
    .sh-tag{margin-top:8px;font-weight:600;font-size:18px;letter-spacing:.06em;color:rgba(255,255,255,.9);text-shadow:0 2px 4px #000,0 0 14px rgba(0,0,0,.9)}
    .sh-tag i{font-style:normal;color:rgba(255,255,255,.5);margin:0 10px}
    .sh-cols{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px;align-items:start}
    @media(max-width:900px){.sh-cols{grid-template-columns:1fr;max-width:520px;margin:0 auto}.sh-t{font-size:44px}.sh-sub{font-size:16px;letter-spacing:.08em}.sh-tag{font-size:14px}.sh{padding:26px 12px 36px}.sh-title{padding:18px 10px 14px}}
    .sh-col{--a:#E8B53A;--rgb:232,181,58;border-radius:18px;border:2px solid rgba(var(--rgb),.85);padding:14px 12px 14px;
      background:linear-gradient(180deg,rgba(var(--rgb),.1) 0%,rgba(4,5,7,.88) 18%,rgba(4,5,7,.9) 100%);
      box-shadow:0 0 34px -10px rgba(var(--rgb),.65),inset 0 1px 0 rgba(255,255,255,.08),0 10px 30px rgba(0,0,0,.6)}
    .sh-col.g{--a:#6CE83A;--rgb:94,234,58}.sh-col.b{--a:#4FA8FF;--rgb:59,130,246}
    .sh-hd{display:flex;align-items:center;gap:14px;padding:8px 10px 12px;margin:-4px -2px 12px;border-bottom:1px solid rgba(var(--rgb),.35);border-radius:12px 12px 0 0;
      background:radial-gradient(ellipse 70% 120% at 38% 50%,rgba(0,0,0,.7) 0%,rgba(0,0,0,.5) 45%,rgba(0,0,0,.2) 80%,rgba(0,0,0,0) 100%)}
    .sh-hd .lg{width:96px;height:96px;flex:none;border-radius:50%;object-fit:contain;filter:drop-shadow(0 0 18px rgba(var(--rgb),.55))}
    .sh-hd .lg2{width:120px;height:96px;flex:none;object-fit:contain;transform:scale(1.55);transform-origin:center;filter:drop-shadow(0 0 18px rgba(var(--rgb),.45))}
    .sh-hd .nm{font-family:'Orbitron',monospace;font-weight:900;font-size:27px;line-height:1;color:var(--a);text-shadow:0 2px 2px #000}
    .sh-col.b .sh-hd .nm{color:#fff}
    .sh-hd .ln{margin-top:7px;font-weight:600;font-size:15px;line-height:1.25;color:rgba(255,255,255,.78)}
    .sh-hd .go{margin-left:auto;width:36px;height:36px;flex:none;border-radius:50%;border:2px solid var(--a);display:grid;place-items:center;color:var(--a);box-shadow:0 0 14px -3px rgba(var(--rgb),.9)}
    .sh-hd .go svg{width:16px;height:16px}
    .sh-rows{display:flex;flex-direction:column;gap:9px}
    .sh-row{--c:#F2C94C;--crgb:242,201,76;--bg:#231902;display:flex;align-items:center;gap:12px;width:100%;text-align:left;cursor:pointer;
      min-height:62px;padding:4px 14px 4px 10px;border-radius:11px;border:1px solid rgba(var(--crgb),.7);color:#fff;font:inherit;
      background:linear-gradient(180deg,var(--bg) 0%,var(--bg) 100%);
      box-shadow:inset 0 1px 0 rgba(255,255,255,.07);transition:transform .15s ease,box-shadow .15s ease,filter .15s ease}
    .sh-row:hover{transform:translateY(-1px);filter:brightness(1.15);box-shadow:inset 0 1px 0 rgba(255,255,255,.1),0 0 18px -4px rgba(var(--crgb),.8)}
    .sh-row:focus-visible{outline:2px solid var(--c);outline-offset:2px}
    .sh-row img{width:70px;height:56px;flex:none;object-fit:contain;filter:drop-shadow(0 3px 5px rgba(0,0,0,.8))}
    .sh-row img.globe{height:60px;width:70px;filter:drop-shadow(0 0 8px rgba(242,201,76,.55)) drop-shadow(0 3px 5px rgba(0,0,0,.8))}
    .sh-row img.own{height:54px;filter:drop-shadow(0 0 7px rgba(var(--crgb),.55)) drop-shadow(0 3px 5px rgba(0,0,0,.8))}
    .sh-row .t{display:block;font-weight:700;font-size:17.5px;line-height:1.1;color:var(--c);text-shadow:0 1px 2px #000}
    .sh-row .s{display:block;margin-top:3px;font-weight:500;font-size:13.5px;line-height:1.1;color:rgba(255,255,255,.82)}
    .sh-row .ch{margin-left:auto;color:var(--c);flex:none}.sh-row .ch svg{width:14px;height:14px}
    .sh-row.gold{--c:#F2C94C;--crgb:242,201,76;--bg:#231902}
    .sh-row.fire{--c:#FF9A3D;--crgb:255,138,61;--bg:#2C1001}
    .sh-row.green{--c:#5EEA7A;--crgb:94,234,122;--bg:#021F16}
    .sh-row.lime{--c:#8DFF3A;--crgb:124,252,0;--bg:#0D2503}
    .sh-row.purple{--c:#D08BFF;--crgb:192,132,252;--bg:#1E062E}
    .sh-row.blue{--c:#5BB8FF;--crgb:59,160,255;--bg:#00152D}
    .sh-row.red{--c:#FF7A5C;--crgb:255,96,80;--bg:#2A0D01}
    .sh-back{display:flex;justify-content:center;margin-top:30px}
    .sh-back button{display:inline-flex;align-items:center;gap:10px;padding:12px 26px;border-radius:12px;border:1px solid rgba(255,255,255,.35);background:rgba(0,0,0,.65);color:#fff;font-weight:600;font-size:17px;box-shadow:0 0 18px -6px rgba(255,255,255,.4);transition:border-color .15s}
    .sh-back button:hover{border-color:rgba(255,255,255,.7)}
    @media(prefers-reduced-motion:reduce){.sh-row,.sh-row:hover{transform:none;transition:none}}
  </style>'''
once('''    @media(prefers-reduced-motion:reduce){.h2 .h2-buy::after{animation:none}.h2 .h2-buy,.h2 .h2-sw{transition:none}.h2 .h2-buy:hover,.h2 .h2-sw:hover{transform:none}.h2-tile .h2-sk{animation:none}}
  </style>''',
'''    @media(prefers-reduced-motion:reduce){.h2 .h2-buy::after{animation:none}.h2 .h2-buy,.h2 .h2-sw{transition:none}.h2 .h2-buy:hover,.h2 .h2-sw:hover{transform:none}.h2-tile .h2-sk{animation:none}}'''+CSS, 'css')

# ── (2) components ───────────────────────────────────────────────────────────────────────────────────────────────────
COMP = r'''    /* ===== SOCIALS HUB (2026-10-03) — the frame of the redesigned Socials tab (CSS: the sh-* block; mock-up and decisions:
       design/socials-hub/). Pure presentation at module scope (u4): the rows' onClick are the old hub's handlers, unchanged. */
    const SH_CHEV=<svg viewBox="0 0 14 14" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 2l5 5-5 5"/></svg>;
    const shIcon=(col,key)=>`logos/socials/hub/${col}-${key}.png`;
    /* tone = the row's colour family (gold / fire / green / lime / purple / blue / red); own = a token logo (glow in the row's
       colour); globe = Shaka's gold globe (The Grays & The Cores), drawn a touch larger. */
    const ShRow=({tone,icon,own,globe,title,sub,onClick})=>(
      <button type="button" onClick={onClick} className={`sh-row ${tone}`}>
        <img src={icon} alt="" className={own?'own':globe?'globe':undefined} loading="lazy" decoding="async"/>
        <span className="min-w-0"><span className="t">{title}</span><span className="s">{sub}</span></span>
        <span className="ch">{SH_CHEV}</span>
      </button>
    );
    const ShCol=({tone,logo,wide,name,line1,line2,children})=>(
      <div className={`sh-col ${tone}`}>
        <div className="sh-hd">
          <img src={logo} alt="" className={wide?'lg2':'lg'}/>
          <div><div className="nm">{name}</div><div className="ln">{line1}<br/>{line2}</div></div>
          <span className="go" aria-hidden="true"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round"><path d="M6 3l5 5-5 5"/></svg></span>
        </div>
        <div className="sh-rows">{children}</div>
      </div>
    );

'''
once('''    const DashboardSkeleton=({token,tiles=true})=>(''', COMP+'''    const DashboardSkeleton=({token,tiles=true})=>(''', 'components')

# ── (3) the tab ──────────────────────────────────────────────────────────────────────────────────────────────────────
start_marker = "          {/* Social Tab Content */}\n"
end_marker = "          {/* KPI Report Modal (legacy - kept for direct link) */}\n"
i = s.index(start_marker); j = s.index(end_marker)
assert s.count(start_marker) == 1 and s.count(end_marker) == 1 and i < j
old_block = s[i:j]
# the handlers, lifted verbatim from the old block so nothing about what a row DOES changes.
# the old block has three columns; the shared labels (Burn Stats, Value Generated, Token Allocation, KPI Report, Holders, Targets)
# appear more than once, so split the block into its columns first
cols = re.split(r'\{/\* (?:PTGC|UFO|Combined) Column \*/\}', old_block)
assert len(cols) == 4, len(cols)
col_src = {'ptgc': cols[1], 'ufo': cols[2], 'combined': cols[3]}
def handler_in(col, label):
    """The onClick of the old column's button whose bold line ends with `label`: find the label, then the nearest
    `<button onClick={` before it, and take what sits between that and its ` className="w-full`."""
    src = col_src[col]
    hits = [m.start() for m in re.finditer(r'<div className="font-bold">[^<]*?' + re.escape(label) + r'</div>', src)]
    assert len(hits) == 1, f'{col}/{label!r}: {len(hits)} labels'
    b = src.rfind('<button onClick={', 0, hits[0]); assert b >= 0
    e = src.index('} className="w-full', b)
    return src[b+len('<button onClick={'):e].strip()

def row(col, key, tone, label, sub, *, own=False, globe=False, icon=None):
    h = handler_in(col, label.replace('&amp;','&'))
    icon = icon or f'{{shIcon(\'{col}\',\'{key}\')}}'
    flags = (' own' if own else '') + (' globe' if globe else '')
    return f'                  <ShRow tone="{tone}" icon={icon}{flags} title="{label}" sub="{sub}" onClick={{{h}}}/>\n'

NEW = ("          {/* Social Tab Content */}\n"
"          {/* MAINT-MIGRATION: Socials is now LIVE. Removed the \"Under Maintenance\" screen and the\n"
"              operator-only preview dot; the tab renders its real content for everyone. (socialPreview\n"
"              state is left in place but unused.) */}\n"
"          {/* 2026-10-03: Shaka's redesign — his sky, three framed columns, his icons (ShRow / ShCol, the sh-* CSS;\n"
"              design/socials-hub/ = mock-up + decisions). Row ORDER: the five cards every column has first (Logos, Burn,\n"
"              Value Generated, KPI, Holders — level across the page), then the two the token columns share (Token\n"
"              Allocation, Targets — Combined uses those rows for RH Core Liquidity and Leagues), then each column's own.\n"
"              Every onClick is the previous hub's handler, unchanged. */}\n"
"          {activeTab==='social'&&(\n"
"            <section className=\"sh\" aria-label=\"Socials Hub\">\n"
"              <div className=\"sh-sky\" aria-hidden=\"true\"><img src=\"logos/socials/hub-sky.jpg\" alt=\"\"/><img className=\"ft\" src=\"logos/socials/hub-sky.jpg\" alt=\"\"/></div>\n"
"              <div className=\"sh-in\">\n"
"                <div className=\"sh-title\">\n"
"                  <h2><span className=\"sh-t g\">Socials</span><span className=\"sh-t w\">Hub</span></h2>\n"
"                  <div className=\"sh-sub\">Shareable Cards &amp; Images for the Community</div>\n"
"                  <div className=\"sh-tag\">Logos<i>•</i>Stats<i>•</i>Charts<i>•</i>Reports<i>•</i>And More</div>\n"
"                </div>\n"
"                <div className=\"sh-cols\">\n"
"                <ShCol tone=\"\" logo={TOKENS.PTGC.logo} name=\"PTGC\" line1=\"PulseChain\" line2=\"The Grays\">\n"
+ row('ptgc','logos','gold','PTGC Logos','Download official logos', own=True, icon='{TOKENS.PTGC.logo}')
+ row('ptgc','burn','fire','Burn Stats','Total supply burned')
+ row('ptgc','valuegen','green','Value Generated','Fee distribution breakdown')
+ row('ptgc','kpi','gold','KPI Report','Full stats card')
+ row('ptgc','holders','blue','Holders','PTGC holder analytics')
+ row('ptgc','alloc','purple','Token Allocation','Supply distribution')
+ row('ptgc','targets','red','Targets','Price milestone multipliers')
+ row('ptgc','dao-treasury','blue','DAO Treasury','Treasury breakdown')
+ row('ptgc','dao-buys','gold','DAO Buys','All time, any period, or the latest buy')
+ row('ptgc','affiliates','purple','Affiliates Report','Month leaderboard &amp; all-time totals')
+ "                </ShCol>\n"
"                <ShCol tone=\"g\" logo={TOKENS.UFO.logo} name=\"UFO\" line1=\"PulseChain\" line2=\"The Grays\">\n"
+ row('ufo','logos','lime','UFO Logos','Download official logos', own=True, icon='{TOKENS.UFO.logo}')
+ row('ufo','burn','fire','Burn Stats','Total supply burned')
+ row('ufo','valuegen','green','Value Generated','Fee distribution breakdown')
+ row('ufo','kpi','lime','KPI Report','Full stats card')
+ row('ufo','holders','blue','Holders','UFO holder analytics')
+ row('ufo','alloc','purple','Token Allocation','Supply distribution')
+ row('ufo','targets','lime','Targets','Price milestone multipliers')
+ row('ufo','ptgc-by-ufo','blue','PTGC Burned by UFO','Cross-token burn stats')
+ "                </ShCol>\n"
"                <ShCol tone=\"b\" logo={COMBINED_LOGO} wide name=\"Combined\" line1=\"PTGC + UFO\" line2=\"The Grays\">\n"
+ row('combined','logos','blue','Combined Logos','Download official logos')
+ row('combined','burn','red','Combined Burn Stats','Both tokens burn history &amp; totals')
+ row('combined','valuegen','blue','Combined Value Generated','Fee distribution for both tokens')
+ row('combined','kpi','blue','Combined KPI Report','Both tokens side-by-side')
+ row('combined','holders','blue','Holders','Holder analytics for both tokens')
+ row('combined','rh-cores','blue','RH Core Liquidity','LP breakdown by RH cores', icon="'logos/panels/vg-droplet.webp'")
+ row('combined','leagues','purple','PTGC &amp; UFO Leagues','Combined tier price table')
+ row('combined','grays-cores','gold','The Grays &amp; The Cores','24Hr price comparison', globe=True)
+ "                </ShCol>\n"
"                </div>\n"
"                <div className=\"sh-back\"><button type=\"button\" onClick={()=>gotoTab('dashboard')}>&larr;&nbsp; Back to Dashboard</button></div>\n"
"              </div>\n"
"            </section>\n"
"          )}\n"
"          \n"
"          \n")
s = s[:i] + NEW + s[j:]
p.write_text(s, encoding='utf-8')
print('applied')
