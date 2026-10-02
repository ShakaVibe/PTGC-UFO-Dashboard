#!/usr/bin/env python3
"""The v2 header on the sibling pages (2026-10-03, go-live prep) — applies the same edits to a repo
checkout (cloud clone and Shaka's Mac alike, so the two copies end byte-identical). Idempotent: every
edit checks its marker first.  usage: python3 tools/sibling-header.py <repo-root>"""
import sys, re, pathlib
root = pathlib.Path(sys.argv[1]).resolve()
def rd(n): return (root/n).read_text(encoding='utf-8')
def wr(n, s): (root/n).write_text(s, encoding='utf-8'); print('wrote', n, len(s))
def once(s, old, new, label, count=1):
    assert old in s, f'MISSING anchor for {label}: {old[:80]!r}'
    assert s.count(old) == count, f'anchor for {label} found {s.count(old)}x, want {count}'
    return s.replace(old, new)

LINK = '  <link rel="stylesheet" href="h2.css?v=1">'
# ---------------------------------------------------------------- index.html: h2.css out, ?open= in
idx = rd('index.html')
if 'href="h2.css' not in idx:
    lines = idx.split('\n')
    a = next(i for i,l in enumerate(lines) if l.startswith('    /* ===== DASHBOARD HEADER v2 (2026-09-30)'))
    b = next(i for i,l in enumerate(lines) if l.startswith('    @media(max-width:1023.98px){.h2-tabs,.h2-tiles{--u:'))
    assert lines[b+1].startswith('    /* ===== DASHBOARD PANELS v2'), lines[b+1][:60]
    block = lines[a:b+1]
    css = '/* h2.css — the dashboard header v2 skin (h2-*), moved out of index.html on 2026-10-03 so calculators.html,\n   charts.html and portfolio.html wear the SAME header from the same file. Every rule here used to sit inline in\n   index.html between the HOME (hc-*) and PANELS (p2-*) blocks; the <link> is in that exact spot, so the cascade is\n   unchanged. Change a size by changing N in calc(N*var(--u)) (gotcha 36). When this file changes, bump ?v= on the\n   four <link> tags (GitHub Pages caches it 10 min, gotcha 38). */\n'
    css += '\n'.join(l[4:] if l.startswith('    ') else l for l in block) + '\n'
    wr('h2.css', css)
    repl = ['  </style>',
            '  <!-- the v2 header skin (h2-*) lives in h2.css since 2026-10-03 — shared with calculators / charts / portfolio. The',
            '       link sits exactly where the inline block was (between the hc-* and p2-* blocks) so the cascade is unchanged. -->',
            LINK,
            '  <style>']
    lines[a:b+1] = repl
    idx = '\n'.join(lines)
if '_bootOpen' not in idx:
    idx = once(idx, "    const configListeners=new Set();\n    const App=()=>{",
        "    const configListeners=new Set();\n"
        "    /* 2026-10-03: a sibling page's v2 header sends ?open=swap (BUY / SELL) or ?open=feed (Live Feed) along with\n"
        "       ?token=; the dashboard opens that window once it is up. Read-and-clear, like lsTake. */\n"
        "    let _bootOpen=null;const takeBootOpen=()=>{const v=_bootOpen;_bootOpen=null;return v;};\n"
        "    const App=()=>{", 'takeBootOpen')
    idx = once(idx, "        const qs=new URLSearchParams(window.location.search);\n        const p=qs.get('token');\n        if(p==='PTGC'||p==='UFO'){",
        "        const qs=new URLSearchParams(window.location.search);\n        const p=qs.get('token');\n"
        "        const o=qs.get('open');if(o==='swap'||o==='feed'){_bootOpen=o;qs.delete('open');}\n"
        "        if(_bootOpen&&!(p==='PTGC'||p==='UFO')){const rest=qs.toString();window.history.replaceState({},'',window.location.pathname+(rest?'?'+rest:'')+window.location.hash);}\n"
        "        if(p==='PTGC'||p==='UFO'){", 'open param')
    idx = once(idx, "      const[showSwap,setShowSwap]=useState(false);   // BUY / SELL: the switch.win widget modal (SwapModal)\n",
        "      const[showSwap,setShowSwap]=useState(false);   // BUY / SELL: the switch.win widget modal (SwapModal)\n"
        "      useEffect(()=>{const o=takeBootOpen();if(o==='swap')setShowSwap(true);else if(o==='feed')setShowBeam(true);},[]);   // ?open=swap|feed from a sibling page's v2 header (2026-10-03)\n", 'boot open effect')
if "uid=''" not in idx:
    # the phone banner's change triangle never painted: both banners' H2Tri shared the gradient ids h2ua/h2da, and the
    # desktop copy (display:none under lg) owned them — a gradient defined inside a hidden SVG does not paint (found 2026-10-03
    # building the sibling headers; the harness's 390 px dashboard render confirms it). Per-instance ids.
    idx = once(idx, "    const H2Tri=({down=false})=>(<svg viewBox=\"0 0 30 26\" aria-hidden=\"true\"><defs><linearGradient id=\"h2ua\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stopColor=\"#6BF7A8\"/><stop offset=\"1\" stopColor=\"#00C865\"/></linearGradient><linearGradient id=\"h2da\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stopColor=\"#FF8AA6\"/><stop offset=\"1\" stopColor=\"#E0284F\"/></linearGradient></defs><path d=\"M15 1 L29 25 L1 25 Z\" fill={down?'url(#h2da)':'url(#h2ua)'}/></svg>);\n",
        "    const H2Tri=({down=false,uid=''})=>(<svg viewBox=\"0 0 30 26\" aria-hidden=\"true\"><defs><linearGradient id={'h2ua'+uid} x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stopColor=\"#6BF7A8\"/><stop offset=\"1\" stopColor=\"#00C865\"/></linearGradient><linearGradient id={'h2da'+uid} x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\"><stop offset=\"0\" stopColor=\"#FF8AA6\"/><stop offset=\"1\" stopColor=\"#E0284F\"/></linearGradient></defs><path d=\"M15 1 L29 25 L1 25 Z\" fill={down?`url(#h2da${uid})`:`url(#h2ua${uid})`}/></svg>);   // uid: the phone banner's copy needs its own gradient ids — a gradient defined in the hidden desktop SVG does not paint (2026-10-03)\n", 'H2Tri uid')
    idx = once(idx, "        <div className={`h2-chg tn ${chgCls}`} title={chgTip}>{loading?<Sk w=\"4em\" h=\".9em\" className=\"opacity-60\"/>:<>{changeKnown&&<H2Tri down={!priceUp}/>}{chgTxt}{inline&&<span className=\"h2-chgl\">24h</span>}</>}</div>);\n",
        "        <div className={`h2-chg tn ${chgCls}`} title={chgTip}>{loading?<Sk w=\"4em\" h=\".9em\" className=\"opacity-60\"/>:<>{changeKnown&&<H2Tri down={!priceUp} uid={inline?'p':''}/>}{chgTxt}{inline&&<span className=\"h2-chgl\">24h</span>}</>}</div>);\n", 'H2Tri phone uid')
wr('index.html', idx)

# ---------------------------------------------------------------- calculators.html
c = rd('calculators.html')
if 'href="h2.css' not in c:
    c = once(c, '  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">\n',
        '  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">\n'
        + LINK + '   <!-- the v2 header skin, shared with index.html (2026-10-03) -->\n', 'calc css link')
    c = once(c, '  <div id="root"></div>\n  <script type="text/babel">\n',
        '  <div id="root"></div>\n  <!-- the v2 site header (SiteHeaderV2) — shared with portfolio.html; Babel runs it before the block below -->\n'
        '  <script type="text/babel" src="h2-header.jsx?v=1"></script>\n  <script type="text/babel">\n', 'calc jsx')
    c = once(c, "    const {useState,useEffect,useMemo}=React;\n",
        "    const {useState,useEffect,useMemo}=React;\n"
        "    /* Header design (2026-10-03): 'classic' = the sticky header + nav strip below; 'v2' = SiteHeaderV2 (h2-header.jsx), the\n"
        "       dashboard's art banner + gold tab band. Flip = 'v2' here, in index.html, charts.html and portfolio.html in the SAME push.\n"
        "       Until then this device shows v2 only with the dashboard's preview flag (h2PreviewOn). */\n"
        "    const HEADER_DESIGN='classic';\n"
        "    const hdrV2=HEADER_DESIGN==='v2'||h2PreviewOn();\n", 'calc constant')
    # navTo: feed + swap go to the dashboard with ?open=
    c = once(c, "        } else if(page==='affiliates'){\n          try{localStorage.setItem('ptgc_nav_view','affiliates')}catch(e){}\n          window.location.href='./index.html?token='+token;\n        }",
        "        } else if(page==='affiliates'){\n          try{localStorage.setItem('ptgc_nav_view','affiliates')}catch(e){}\n          window.location.href='./index.html?token='+token;\n        } else if(page==='feed'||page==='swap'){   // v2 header: the Live Feed deck / the BUY-SELL window open on the dashboard (2026-10-03)\n          window.location.href='./index.html?token='+token+'&open='+page;\n        }", 'calc navTo')
    m = re.search(r'(\n          <header className="sticky top-0 z-50 bg-\[#0a0a0a\]/95 backdrop-blur-md border-b border-white/10">.*?\n          </header>\n)', c, re.S)
    assert m, 'calc classic header'
    classic = m.group(1)
    v2 = ("<SiteHeaderV2 token={token} logo={cfg.logo} otherLogo={token==='PTGC'?TOKENS.UFO.logo:TOKENS.PTGC.logo} address={cfg.address} data={data} loading={loading}"
          " hdrDaysOld={hdrDaysOld} copied={copied} copyAddress={copyAddress} plsRatio={plsRatio} xToATH={xToATH} xToPenny={xToPenny} fmtX={hdrFmtX}"
          " renderPrice={(p,cls)=><Price p={p} c={cls}/>} onBack={goBack} onSwitch={switchToken} onBuy={()=>navTo('swap')} navTo={navTo} active=\"calculators\"/>")
    fork = ('\n          {hdrV2?' + v2 + ':(' + classic.rstrip('\n') + '\n          )}\n')
    c = c.replace(classic, fork, 1)
wr('calculators.html', c)

# ---------------------------------------------------------------- charts.html (plain JS: a static twin of SiteHeaderV2)
ch = rd('charts.html')
if 'href="h2.css' not in ch:
    ch = once(ch, '&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>\n<style>\n',
        '&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet"/>\n'
        + LINK.strip() + '   <!-- the v2 header skin, shared with index.html (2026-10-03) -->\n'
        + '<style>\n  /* v2 header (charts-only glue): the token · price line waits for the scroll, the change triangle follows the sign */\n'
        + '  #hdrV2:not([hidden]){display:contents}   /* no box of its own, so the band\'s position:sticky answers to <body>, as on the dashboard (gotcha 36) */\n  #hdrV2:not(.h2-scrolled) .js-h2-mini{display:none!important}#hdrV2 .h2-up .h2-tri-dn,#hdrV2 .h2-dn .h2-tri-up,#hdrV2 .h2-na .h2-tri-up,#hdrV2 .h2-na .h2-tri-dn{display:none}#hdrV2 .h2-chg svg{width:calc(28*var(--u));height:calc(24*var(--u))}#hdrV2 .h2-phone .h2-chg svg{width:calc(18*var(--u));height:calc(16*var(--u))}\n', 'charts css link')
    def tri(cls, idp):
        return (f'<svg class="h2-tri-{cls}" viewBox="0 0 30 26" aria-hidden="true"><defs><linearGradient id="{idp}" x1="0" y1="0" x2="0" y2="1">'
                + ('<stop offset="0" stop-color="#6BF7A8"/><stop offset="1" stop-color="#00C865"/>' if cls=='up' else '<stop offset="0" stop-color="#FF8AA6"/><stop offset="1" stop-color="#E0284F"/>')
                + f'</linearGradient></defs><path d="M15 1 L29 25 L1 25 Z" fill="url(#{idp})"/></svg>')
    cal = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true" style="color:var(--a)"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M3 10h18M8 3v4M16 3v4"/></svg>'
    copy = '<svg width="1em" height="1em" viewBox="0 0 24 26" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="5" y="5" width="14" height="18" rx="2"/><path d="M9 3h6v4H9z" fill="currentColor"/><path d="M8 12h8M8 16h8"/></svg>'
    def coin(): return ('<div class="h2-coin"><div class="h2-halo" aria-hidden="true"></div><img class="h2-corona js-h2-corona" src="logos/header/coin-corona.webp" alt="" aria-hidden="true"/>'
                        '<div class="h2-flare" aria-hidden="true"></div><div class="h2-flare-v" aria-hidden="true"></div><div class="h2-flare-h" aria-hidden="true"></div><img class="h2-logo js-h2-logo" src="06_PTGC_V1_transparent_bg.png" alt="PTGC"/></div>')
    def ident(): return ('<div class="h2-id"><div class="orb h2-tref h2-name js-h2-name">PTGC</div>'
                         '<div class="h2-addr tn"><span class="js-h2-addr">0x9453...DE93</span><button type="button" onclick="copyAddr()" aria-label="Copy contract address" class="-my-2 -mx-1 js-h2-copy" style="font-size:.85em">' + copy + '</button></div>'
                         '<div class="h2-day"><span class="h2-daypill js-h2-day" hidden>' + cal + '<span class="h2-dayl">DAY</span><span class="orb h2-tref2 h2-dayn tn js-h2-dayn">—</span></span></div></div>')
    def chg(inline, idp): return ('<div class="h2-chg tn h2-na js-h2-chg">' + tri('up', idp+'u') + tri('dn', idp+'d') + '<span class="js-h2-chgt">—</span>' + ('<span class="h2-chgl">24h</span>' if inline else '') + '</div>')
    def stats(): return ('<div class="h2-stats">'
        '<div class="h2-stat"><div class="h2-statl">PLS Ratio</div><div class="h2-tref2 tn h2-statv h2-sh js-h2-pls">—</div></div>'
        '<div class="h2-stat"><div class="h2-statl">X\'s to ATH</div><div class="h2-tref2 tn h2-statv h2-sh js-h2-ath">—</div></div>'
        '<div class="h2-stat"><div class="h2-statl">X\'s to a Penny</div><div class="h2-tref2 tn h2-statv h2-sh js-h2-penny">—</div></div></div>')
    def btns(): return ('<div class="h2-btns"><button type="button" onclick="navTo(\'swap\')" aria-label="Buy or sell" class="h2-buy js-h2-buy"><img class="js-h2-logo" src="06_PTGC_V1_transparent_bg.png" alt=""/><span class="orb h2-bt"><span>BUY</span><span class="h2-hr" aria-hidden="true"></span><span>SELL</span></span></button>'
                        '<button type="button" onclick="switchToken()" aria-label="Switch token" class="h2-sw js-h2-sw"><img class="js-h2-swlogo" src="07_Ufo_transparent.png" alt=""/><span class="orb">SWITCH</span></button></div>')
    def mini(cls): return (f'<div class="{cls}"><img class="js-h2-logo" src="06_PTGC_V1_transparent_bg.png" alt=""/><span class="h2-mname h2-tref js-h2-name">PTGC</span>'
                           '<span class="h2-mright"><span class="h2-mprice h2-tprice tn js-h2-price">—</span><span class="h2-mchg tn na js-h2-mchg">—</span></span></div>')
    tabs = ''
    for key, label, badge in [('dashboard','Dashboard',''),('kpi','KPI Report',''),('social','Socials',''),('calculators','Calculators',''),('charts','Charts',''),('feed','Live Feed','NEW'),('portfolio','Portfolio',''),('affiliates','Affiliates','')]:
        b = f'<span class="h2-new">{badge}</span>' if badge else ''
        if key == 'charts':
            tabs += f'<span aria-current="page" class="h2-tab">{label}</span>'
        elif key == 'calculators':
            tabs += f'<a href="./calculators.html" onclick="try{{localStorage.setItem(\'ptgc_last_token\',currentHdrToken)}}catch(e){{}};window.location.href=\'./calculators.html?from=\'+currentHdrToken;return false" class="h2-tab">{label}</a>'
        elif key == 'portfolio':
            tabs += f'<a href="#" onclick="window.location.href=\'portfolio.html?from=\'+currentHdrToken;return false" class="h2-tab h2-pf"><span>{label}</span></a>'
        else:
            tabs += f'<a href="#" onclick="navTo(\'{key}\');return false" class="h2-tab{" h2-aff" if key=="affiliates" else ""}">{label}{b}</a>'
    art_d = '<div class="h2-art" aria-hidden="true"><img class="h2-band" src="logos/header/dash-bg.jpg" alt=""/><img class="h2-band2" src="logos/header/dash-bg.jpg" alt=""/><img class="h2-head" src="logos/header/alien-head.webp" alt=""/><div class="h2-shade"></div><div class="h2-shade-r"></div><div class="h2-fade"></div></div>'
    art_p = '<div class="h2-art" aria-hidden="true"><img class="h2-band" src="logos/header/dash-bg.jpg" alt=""/><img class="h2-head" src="logos/header/alien-head.webp" alt=""/><div class="h2-shade"></div><div class="h2-shade2"></div></div>'
    back = '<a href="#" onclick="navTo(\'dashboard\');return false" aria-label="Back to the dashboard" class="h2-back">&#8592;</a>'
    v2 = ('\n  <!-- ===== HEADER v2 (2026-10-03): a static twin of SiteHeaderV2 (h2-header.jsx) — the dashboard\'s banner + gold tab\n'
          '       band, styled by h2.css. Hidden until HEADER_DESIGN is \'v2\' or this device holds the preview flag (h2Boot below);\n'
          '       applyHeaderTheme / applyHeaderValues fill the js-h2-* hooks. Keep the markup in step with the jsx. ===== -->\n'
          '  <div id="hdrV2" hidden>\n'
          '    <div class="h2" data-tok="PTGC">\n'
          '      <div class="h2-desk hidden lg:block">' + art_d + back + '<div class="h2-row">' + coin() + ident()
          + '<div class="h2-vl" aria-hidden="true"></div><div class="h2-price"><span class="h2-tprice tn h2-sh h2-pricev js-h2-price">—</span>' + chg(False,'h2cd') + '<div class="h2-chgl">24h change</div></div>'
          + '<div class="h2-vl" aria-hidden="true"></div>' + stats() + btns() + '</div></div>\n'
          '      <div class="h2-phone lg:hidden">' + art_p + back + '<div class="h2-top">' + coin() + ident() + '</div>'
          + '<div class="h2-price"><span class="h2-tprice tn h2-sh h2-pricev js-h2-price">—</span>' + chg(True,'h2cp') + '</div>' + stats() + btns() + '</div>\n'
          '    </div>\n'
          '    <div class="h2 h2-tabs" data-tok="PTGC"><div class="lg:hidden js-h2-mini">' + mini('h2-phone-mini') + '</div><div class="h2-tabband"><nav aria-label="Site sections" class="h2-tabrow"><div class="hidden lg:flex js-h2-mini">' + mini('h2-mini') + '</div>' + tabs + '</nav></div></div>\n'
          '  </div>\n')
    ch = once(ch, '\n  <header class="sticky top-0 z-50 bg-[#0a0a0a]/95 backdrop-blur-md border-b border-white/10">\n', v2 + '  <header class="sticky top-0 z-50 bg-[#0a0a0a]/95 backdrop-blur-md border-b border-white/10">\n', 'charts markup')
    # JS: the switch, the boot, the two fillers
    ch = once(ch, "let currentHdrToken = (() => {",
        "/* Header design (2026-10-03): 'classic' = the sticky <header> below; 'v2' = #hdrV2, the dashboard's banner + gold band.\n"
        "   Flip = 'v2' here, in index.html, calculators.html and portfolio.html in the SAME push. Until then this device shows v2\n"
        "   only with the dashboard's preview flag (grays_hdr_preview_v1, the same one index.html's HeaderPreviewGate sets). */\n"
        "const HEADER_DESIGN = 'classic';\n"
        "const hdrV2 = HEADER_DESIGN === 'v2' || (() => { try { return JSON.parse(localStorage.getItem('grays_hdr_preview_v1')) === 1; } catch (e) { return false; } })();\n"
        "function h2Boot() {\n"
        "  if (!hdrV2) return;\n"
        "  const v = document.getElementById('hdrV2'), classic = document.querySelector('header.sticky');\n"
        "  if (!v) return;\n"
        "  if (classic) classic.hidden = true;\n"
        "  v.hidden = false;\n"
        "  // --u is one reference pixel (gotcha 36): desktop width/2166 (floor .47), phone width/390 (.9–1.3) — useH2Scale in the jsx\n"
        "  const scale = () => { const w = document.documentElement.clientWidth || window.innerWidth || 1440; const hsd = Math.max(.47, Math.min(1, w / 2166)), hsp = Math.max(.9, Math.min(1.3, w / 390)); v.querySelectorAll('.h2').forEach(e => { e.style.setProperty('--hsd', hsd); e.style.setProperty('--hsp', hsp); }); };\n"
        "  scale(); window.addEventListener('resize', scale);\n"
        "  // the token · price line shows on the band once the banner has scrolled away (the dashboard's rule)\n"
        "  const onScroll = () => { const a = v.querySelector('.h2-desk'), b = v.querySelector('.h2-phone'); const h = (a && a.offsetHeight) || (b && b.offsetHeight) || 300; v.classList.toggle('h2-scrolled', window.scrollY > h - 40); };\n"
        "  onScroll(); window.addEventListener('scroll', onScroll, { passive: true });\n"
        "}\n"
        "function h2All(sel, fn) { const v = document.getElementById('hdrV2'); if (v) v.querySelectorAll(sel).forEach(fn); }\n"
        "function h2ApplyTheme(t, other) {\n"
        "  h2All('.h2', e => e.dataset.tok = t.name);\n"
        "  h2All('.js-h2-logo', e => { e.src = t.logo; if (e.alt) e.alt = t.name; });\n"
        "  h2All('.js-h2-corona', e => e.src = t.name === 'UFO' ? 'logos/header/coin-corona-green.webp' : 'logos/header/coin-corona.webp');\n"
        "  h2All('.js-h2-name', e => e.textContent = t.name);\n"
        "  h2All('.js-h2-addr', e => e.textContent = t.address.slice(0, 6) + '...' + t.address.slice(-4));\n"
        "  h2All('.js-h2-swlogo', e => e.src = HDR_TOKENS[other].logo);\n"
        "  h2All('.js-h2-sw', e => e.setAttribute('aria-label', 'Switch to ' + other));\n"
        "  h2All('.js-h2-buy', e => e.setAttribute('aria-label', 'Buy or sell ' + t.name));\n"
        "}\n"
        "function h2ApplyValues(data) {\n"
        "  const { price, chg, plsRatio, xToATH, xToPenny, atATH, abovePenny, days } = data;\n"
        "  const known = chg != null && !isNaN(chg), up = known && chg >= 0;\n"
        "  const chgTxt = known ? (up ? '+' : '\\u2212') + Math.abs(chg).toFixed(2) + '%' : '\\u2014';\n"
        "  h2All('.js-h2-price', e => e.textContent = fmtPrice(price));\n"
        "  h2All('.js-h2-chg', e => { e.classList.remove('h2-up', 'h2-dn', 'h2-na'); e.classList.add(known ? (up ? 'h2-up' : 'h2-dn') : 'h2-na'); e.classList.remove('up', 'dn', 'na'); e.classList.add(known ? (up ? 'up' : 'dn') : 'na'); });\n"
        "  h2All('.js-h2-chgt', e => e.textContent = chgTxt);\n"
        "  h2All('.js-h2-mchg', e => { e.textContent = chgTxt; e.classList.remove('up', 'dn', 'na'); e.classList.add(known ? (up ? 'up' : 'dn') : 'na'); });\n"
        "  h2All('.js-h2-pls', e => e.textContent = plsRatio);\n"
        "  h2All('.js-h2-ath', e => e.textContent = atATH ? 'AT ATH' : fmtX(xToATH));\n"
        "  h2All('.js-h2-penny', e => e.textContent = abovePenny ? '\\u2713' : fmtX(xToPenny));\n"
        "  h2All('.js-h2-day', e => e.hidden = !(days != null));\n"
        "  h2All('.js-h2-dayn', e => e.textContent = days != null ? days.toLocaleString() : '\\u2014');\n"
        "}\n"
        "let currentHdrToken = (() => {", 'charts boot js')
    ch = once(ch, "  document.getElementById('copyBtn').textContent = '\\u2713';\n  setTimeout(() => { document.getElementById('copyBtn').innerHTML = '&#128203;' }, 2000);\n",
        "  document.getElementById('copyBtn').textContent = '\\u2713';\n  setTimeout(() => { document.getElementById('copyBtn').innerHTML = '&#128203;' }, 2000);\n"
        "  h2All('.js-h2-copy', e => { if (!e.dataset.svg) e.dataset.svg = e.innerHTML; e.textContent = '\\u2713'; setTimeout(() => { e.innerHTML = e.dataset.svg; }, 2000); });\n", 'charts copy')
    ch = once(ch, "  const indicator = document.getElementById('navChartsIndicator');\n  if (indicator) indicator.style.background = c;\n}\n",
        "  const indicator = document.getElementById('navChartsIndicator');\n  if (indicator) indicator.style.background = c;\n  h2ApplyTheme(t, other);\n}\n", 'charts theme hook')
    ch = once(ch, "    const price = parseFloat(p.priceUsd);\n    const chg = p.priceChange?.h24 ? parseFloat(p.priceChange.h24) : 0;\n",
        "    const price = parseFloat(p.priceUsd);\n    const chg = p.priceChange?.h24 ? parseFloat(p.priceChange.h24) : 0;\n"
        "    const days = p.pairCreatedAt ? Math.max(0, Math.floor((Date.now() - p.pairCreatedAt) / 86400000)) : null;   // the v2 header's Day pill (2026-10-03)\n", 'charts days')
    ch = once(ch, "    const data = { price, chg, plsRatio, xToATH, xToPenny, atATH, abovePenny, ts: Date.now() };",
        "    const data = { price, chg, plsRatio, xToATH, xToPenny, atATH, abovePenny, days, ts: Date.now() };", 'charts data')
    ch = once(ch, "function applyHeaderValues(data, t) {\n  const { price, chg, plsRatio, xToATH, xToPenny, atATH, abovePenny } = data;\n",
        "function applyHeaderValues(data, t) {\n  h2ApplyValues(data);\n  const { price, chg, plsRatio, xToATH, xToPenny, atATH, abovePenny } = data;\n", 'charts values hook')
    ch = once(ch, "function navTo(tab) {\n  try {\n    localStorage.setItem('ptgc_last_token', currentHdrToken);\n",
        "function navTo(tab) {\n  if (tab === 'feed' || tab === 'swap') {   // v2 header: the Live Feed deck / the BUY-SELL window open on the dashboard (2026-10-03)\n    try { localStorage.setItem('ptgc_last_token', currentHdrToken); } catch (e) {}\n    window.location.href = `./index.html?token=${currentHdrToken}&open=${tab}`;\n    return;\n  }\n  try {\n    localStorage.setItem('ptgc_last_token', currentHdrToken);\n", 'charts navTo')
    ch = once(ch, "  loadSelections();\n  cache = loadCache();\n  applyHeaderTheme();\n  loadHeaderData();\n",
        "  loadSelections();\n  cache = loadCache();\n  h2Boot();\n  applyHeaderTheme();\n  loadHeaderData();\n", 'charts boot call')
wr('charts.html', ch)

# ---------------------------------------------------------------- portfolio.html (two-token page: its own banner on the shared pieces)
pf = rd('portfolio.html')
if 'href="h2.css' not in pf:
    pf = once(pf, '  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">\n  <style>\n',
        '  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">\n'
        + LINK + '   <!-- the v2 header skin, shared with index.html (2026-10-03) -->\n  <style>\n', 'pf css link')
    pf = once(pf, "    .animate-pulse-slow{animation:pulse 1.5s ease-in-out infinite}\n  </style>\n",
        "    .animate-pulse-slow{animation:pulse 1.5s ease-in-out infinite}\n"
        "    /* v2 header, the portfolio-only pieces (2026-10-03; h2.css has the rest): two coins, the gold→green PORTFOLIO title,\n"
        "       PTGC / UFO / PLS quotes in the stat slots, the page's three buttons as glass pills */\n"
        "    .h2 .h2-pfcoins{display:flex;align-items:center;flex:none}\n"
        "    .h2 .h2-pfc{position:relative;flex:none;width:calc(150*var(--u));height:calc(150*var(--u))}\n"
        "    .h2 .h2-pfc+.h2-pfc{margin-left:calc(-30*var(--u))}\n"
        "    .h2 .h2-pfc .h2-coin{position:absolute;left:50%;top:50%;margin:0;transform:translate(-50%,-50%) scale(.77)}\n"
        "    .h2 .h2-pftitle{background-image:linear-gradient(90deg,#F8DB7C 0%,#E7B843 38%,#C8FF78 62%,#7CFC00 100%);-webkit-background-clip:text;background-clip:text;-webkit-text-fill-color:transparent;color:transparent}\n"
        "    .h2-desk .h2-pftitle{font-size:calc(62*var(--u))}\n"
        "    .h2 .h2-pfsub{margin-top:calc(10*var(--u));font-size:max(calc(22*var(--u)),.75rem);font-weight:500;color:rgba(255,255,255,.8);text-shadow:0 1px 3px #000}\n"
        "    /* each quote keeps its own token's price gradient whatever the band's colour (the h2 root takes the ?from= token) — the\n"
        "       PTGC / UFO pair = h2.css's h2-tprice gradients; the sub-zero digit prints solid (the h2-tprice sub rule) */\n"
        "    .h2 .h2-pfq.ptgc .h2-tprice{background-image:linear-gradient(180deg,#FFF6D6 0%,#FBE6B0 24%,#F8D88C 42%,#F6C866 58%,#EEB852 74%,#E3A945 90%,#D69C40 100%)}.h2 .h2-pfq.ptgc .h2-tprice sub{-webkit-text-fill-color:#F0BE5E;color:#F0BE5E}\n"
        "    .h2 .h2-pfq.ufo .h2-tprice{background-image:linear-gradient(180deg,#F4FFE4 0%,#E0FFB8 24%,#CBFF8C 42%,#B2F760 58%,#9BEA45 74%,#86D83A 90%,#76C634 100%)}.h2 .h2-pfq.ufo .h2-tprice sub{-webkit-text-fill-color:#A8EE55;color:#A8EE55}\n"
        "    .h2 .h2-pfq.pls .h2-tprice{background-image:linear-gradient(180deg,#FFFFFF 0%,#ECEAF6 36%,#CFCBE0 66%,#AEA9C4 100%)}.h2 .h2-pfq.pls .h2-tprice sub{-webkit-text-fill-color:#C9C6DA;color:#C9C6DA}\n"
        "    .h2 .h2-pfchg{margin-top:calc(8*var(--u));font-size:max(calc(21*var(--u)),.7rem);font-weight:700;line-height:1;text-shadow:0 1px 3px #000}\n"
        "    .h2 .h2-pfchg.up{color:var(--up)}.h2 .h2-pfchg.dn{color:var(--dn)}.h2 .h2-pfchg.na{color:rgba(255,255,255,.4)}\n"
        "    .h2 .h2-pfb{display:inline-flex;align-items:center;justify-content:center;gap:calc(10*var(--u));height:calc(46*var(--u));padding:0 calc(20*var(--u));border-radius:calc(12*var(--u));background:linear-gradient(135deg,rgba(var(--a-rgb),.22),rgba(var(--a-rgb),.06)),#0a0905;border:calc(1.5*var(--u)) solid rgba(var(--a-rgb),.7);box-shadow:0 0 calc(18*var(--u)) calc(-4*var(--u)) rgba(var(--a-rgb),.6),inset 0 1px 0 rgba(255,255,255,.1);color:#fff;font-family:'Orbitron',monospace;font-weight:700;font-size:max(calc(14*var(--u)),.6rem);letter-spacing:.16em;white-space:nowrap;cursor:pointer;transition:filter .2s,transform .2s}\n"
        "    .h2-desk .h2-pfb{min-width:calc(200*var(--u))}\n"
        "    .h2 .h2-pfb:hover{filter:brightness(1.12);transform:translateY(-1px)}\n"
        "    .h2-desk .h2-pfbtns{flex:none;display:flex;flex-direction:column;gap:calc(12*var(--u));margin-left:auto;padding-left:calc(24*var(--u))}\n"
        "    .h2-phone .h2-pfbtns{position:relative;z-index:1;margin-top:calc(16*var(--u));display:flex;gap:calc(8*var(--u))}\n"
        "    .h2-phone .h2-pfbtns .h2-pfb{flex:1;padding:0;height:calc(42*var(--u));font-size:max(calc(11*var(--u)),.55rem);letter-spacing:.1em}\n"
        "    .h2-phone .h2-pftitle{font-size:calc(27*var(--u))}\n"
        "    .h2-phone .h2-pfsub{font-size:max(calc(13*var(--u)),.7rem);margin-top:calc(6*var(--u))}\n"
        "    .h2-phone .h2-pfc{width:calc(80*var(--u));height:calc(80*var(--u))}.h2-phone .h2-pfc+.h2-pfc{margin-left:calc(-16*var(--u))}\n"
        "    .h2-phone .h2-pfchg{font-size:max(calc(14*var(--u)),.65rem);margin-top:calc(5*var(--u))}\n"
        "    .h2-tabs .h2-mini.h2-pfmini img+img,.h2-phone-mini.h2-pfmini img+img{margin-left:calc(-10*var(--u))}\n"
        "  </style>\n", 'pf css')
    pf = once(pf, '  <div id="root"></div>\n  <script type="text/babel">\n',
        '  <div id="root"></div>\n  <!-- the v2 site header pieces (h2-header.jsx) — shared with calculators.html; Babel runs it before the block below -->\n'
        '  <script type="text/babel" src="h2-header.jsx?v=1"></script>\n  <script type="text/babel">\n', 'pf jsx')
    pf = once(pf, "    const usdOf=async(addr)=>{\n",
        "    /* Header design (2026-10-03): 'classic' = the sticky header below; 'v2' = PortfolioHeaderV2 — the dashboard's art banner with both\n"
        "       coins, the PTGC / UFO / PLS quotes and the page's three buttons, then the gold tab band. Flip = 'v2' here, in index.html,\n"
        "       calculators.html and charts.html in the SAME push. Until then this device shows v2 only with the dashboard's preview flag. */\n"
        "    const HEADER_DESIGN='classic';\n"
        "    const hdrV2=HEADER_DESIGN==='v2'||h2PreviewOn();\n"
        "    const pfFromToken=()=>{try{const q=new URLSearchParams(window.location.search).get('from');if(q==='PTGC'||q==='UFO')return q;}catch(e){}try{const t=localStorage.getItem('ptgc_last_token');if(t==='PTGC'||t==='UFO')return t;}catch(e){}return'PTGC';};\n"
        "    const pfNavTo=(page)=>{   // the band's tabs — the same handoff calculators.html uses (ptgc_last_token + ?token= / ?from=)\n"
        "      const token=pfFromToken();try{localStorage.setItem('ptgc_last_token',token)}catch(e){}\n"
        "      if(page==='dashboard'||page==='kpi'||page==='social'){try{localStorage.setItem('ptgc_nav_tab',page)}catch(e){}window.location.href='./index.html?token='+token;}\n"
        "      else if(page==='calculators'){window.location.href='./calculators.html?from='+token;}\n"
        "      else if(page==='charts'){window.location.href='./charts.html?from='+token;}\n"
        "      else if(page==='affiliates'){try{localStorage.setItem('ptgc_nav_view','affiliates')}catch(e){}window.location.href='./index.html?token='+token;}\n"
        "      else if(page==='feed'||page==='swap'){window.location.href='./index.html?token='+token+'&open='+page;}\n"
        "    };\n"
        "    // price + 24h change for the v2 header's quotes; null/null on failure (never a fake 0). usdOf below stays for everything else.\n"
        "    const quoteOf=async(addr)=>{\n"
        "      try{\n"
        "        const r=await fetch(`https://api.dexscreener.com/latest/dex/tokens/${addr}`);\n"
        "        const d=await r.json();\n"
        "        const pp=pricePair(d.pairs,addr);\n"
        "        const c=pp&&pp.priceChange&&pp.priceChange.h24!=null?parseFloat(pp.priceChange.h24):null;\n"
        "        return{price:pp?(parseFloat(pp.priceUsd)||null):null,change:(c==null||isNaN(c))?null:c};\n"
        "      }catch{return{price:null,change:null};}\n"
        "    };\n"
        "    const PortfolioHeaderV2=({prices,changes,loading,onBack,onGetCode,onLoadCode,onRefresh,hasWallets,navTo})=>{\n"
        "      const tok=pfFromToken();\n"
        "      const sc=useH2Scale();\n"
        "      const[scrolled,setScrolled]=useState(false);\n"
        "      const artRef=React.useRef(null),artRef2=React.useRef(null);\n"
        "      useEffect(()=>{\n"
        "        const on=()=>{const a=artRef.current,b=artRef2.current;const h=(a&&a.offsetHeight)||(b&&b.offsetHeight)||300;setScrolled(window.scrollY>h-40);};\n"
        "        on();window.addEventListener('scroll',on,{passive:true});\n"
        "        return()=>window.removeEventListener('scroll',on);\n"
        "      },[]);\n"
        "      const quote=(key,label,cls)=>{\n"
        "        const p=prices[key],c=changes[key];const known=c!=null&&!isNaN(c),up=known&&c>=0;\n"
        "        return(<div key={key} className={`h2-stat h2-pfq ${cls}`}>\n"
        "          <div className=\"h2-statl\">{label}</div>\n"
        "          {loading?<div className=\"h2-statv\"><H2Sk w=\"3em\" h=\"1em\" className=\"opacity-60\"/></div>:<div className=\"h2-tprice tn h2-statv h2-sh\">{fmtPriceNode(p)}</div>}\n"
        "          <div className={`h2-pfchg tn ${known?(up?'up':'dn'):'na'}`}>{loading?'\\u00a0':known?`${up?'+':'\\u2212'}${Math.abs(c).toFixed(2)}%`:'\\u2014'}</div>\n"
        "        </div>);\n"
        "      };\n"
        "      const quotes=(<>{quote('ptgc','PTGC','ptgc')}{quote('ufo','UFO','ufo')}{quote('pls','PLS','pls')}</>);\n"
        "      const coins=(<div className=\"h2-pfcoins\"><div className=\"h2-pfc\"><H2Coin token=\"PTGC\" logo={TOKENS.PTGC.logo}/></div><div className=\"h2-pfc\"><H2Coin token=\"UFO\" logo={TOKENS.UFO.logo}/></div></div>);\n"
        "      const title=(<div className=\"h2-id\"><div className=\"orb h2-name h2-pftitle\">PORTFOLIO</div><div className=\"h2-pfsub\">Track your holdings across wallets</div></div>);\n"
        "      const btns=(<>\n"
        "        {hasWallets&&<button type=\"button\" onClick={onGetCode} className=\"h2-pfb\">{'\\u{1F4CB}'} GET CODE</button>}\n"
        "        <button type=\"button\" onClick={onLoadCode} className=\"h2-pfb\">{'\\u{1F4E5}'} LOAD CODE</button>\n"
        "        {hasWallets&&<button type=\"button\" onClick={onRefresh} className=\"h2-pfb\">{'\\u{1F504}'} REFRESH</button>}\n"
        "      </>);\n"
        "      const mini=(cls)=>(<div className={cls+' h2-pfmini'}><img src={TOKENS.PTGC.logo} alt=\"\"/><img src={TOKENS.UFO.logo} alt=\"\"/><span className=\"h2-mname h2-pftitle\">PORTFOLIO</span></div>);\n"
        "      const vars={'--hsd':sc.hsd,'--hsp':sc.hsp};\n"
        "      return(<>\n"
        "        <div className=\"h2\" data-tok={tok} style={vars}>\n"
        "          <div className=\"h2-desk hidden lg:block\" ref={artRef}>\n"
        "            <div className=\"h2-art\" aria-hidden=\"true\">\n"
        "              <img className=\"h2-band\" src={H2_ASSETS.band} alt=\"\"/><img className=\"h2-band2\" src={H2_ASSETS.band} alt=\"\"/><img className=\"h2-head\" src={H2_ASSETS.head} alt=\"\"/>\n"
        "              <div className=\"h2-shade\"></div><div className=\"h2-shade-r\"></div><div className=\"h2-fade\"></div>\n"
        "            </div>\n"
        "            <button type=\"button\" onClick={onBack} aria-label=\"Back\" className=\"h2-back\">{'\\u2190'}</button>\n"
        "            <div className=\"h2-row\">\n"
        "              {coins}{title}\n"
        "              <div className=\"h2-vl\" aria-hidden=\"true\"></div>\n"
        "              <div className=\"h2-stats\">{quotes}</div>\n"
        "              <div className=\"h2-pfbtns\">{btns}</div>\n"
        "            </div>\n"
        "          </div>\n"
        "          <div className=\"h2-phone lg:hidden\" ref={artRef2}>\n"
        "            <div className=\"h2-art\" aria-hidden=\"true\">\n"
        "              <img className=\"h2-band\" src={H2_ASSETS.band} alt=\"\"/><img className=\"h2-head\" src={H2_ASSETS.head} alt=\"\"/>\n"
        "              <div className=\"h2-shade\"></div><div className=\"h2-shade2\"></div>\n"
        "            </div>\n"
        "            <button type=\"button\" onClick={onBack} aria-label=\"Back\" className=\"h2-back\">{'\\u2190'}</button>\n"
        "            <div className=\"h2-top\">{coins}{title}</div>\n"
        "            <div className=\"h2-stats\">{quotes}</div>\n"
        "            <div className=\"h2-pfbtns\">{btns}</div>\n"
        "          </div>\n"
        "        </div>\n"
        "        <H2TabBand token={tok} vars={vars} active=\"portfolio\" navTo={navTo} mini={mini} miniOn={scrolled}/>\n"
        "      </>);\n"
        "    };\n"
        "    const usdOf=async(addr)=>{\n", 'pf components')
    pf = once(pf, "      const[prices,setPrices]=useState({ptgc:null,ufo:null,pls:null});\n",
        "      const[prices,setPrices]=useState({ptgc:null,ufo:null,pls:null});\n"
        "      const[changes,setChanges]=useState({ptgc:null,ufo:null,pls:null});   // 24h %, for the v2 header's quotes (2026-10-03)\n", 'pf changes state')
    pf = once(pf, "          const[ptgcPrice,ufoPrice,plsPrice]=await Promise.all([\n            usdOf(PTGC_TOKEN_ADDR),\n            usdOf(UFO_TOKEN_ADDR),\n            fetchPLS()\n          ]);\n          setPrices({ptgc:ptgcPrice,ufo:ufoPrice,pls:plsPrice});\n",
        "          const[pq,uq,wq]=await Promise.all([\n            quoteOf(PTGC_TOKEN_ADDR),\n            quoteOf(UFO_TOKEN_ADDR),\n            quoteOf(WPLS_ADDR)\n          ]);\n"
        "          const ptgcPrice=pq.price,ufoPrice=uq.price,plsPrice=wq.price;\n"
        "          setPrices({ptgc:ptgcPrice,ufo:ufoPrice,pls:plsPrice});\n"
        "          setChanges({ptgc:pq.change,ufo:uq.change,pls:wq.change});\n", 'pf init prices')
    m = re.search(r'(\n          <header className="sticky top-0 z-50 bg-\[#0a0a0a\]/95 backdrop-blur border-b border-white/10">.*?\n          </header>\n)', pf, re.S)
    assert m, 'pf classic header'
    classic = m.group(1)
    v2 = ("<PortfolioHeaderV2 prices={prices} changes={changes} loading={initialLoad} onBack={onBack} onGetCode={handleGetCode}"
          " onLoadCode={()=>{setShowLoadModal(true);setCodeError('');setCodeInput('')}} onRefresh={refreshAll} hasWallets={wallets.length>0} navTo={pfNavTo}/>")
    pf = pf.replace(classic, '\n          {hdrV2?' + v2 + ':(' + classic.rstrip('\n') + '\n          )}\n', 1)
wr('portfolio.html', pf)

# ---------------------------------------------------------------- deploy.yml: the two shared files must reach _site/
dy = rd('.github/workflows/deploy.yml')
if '*.css *.jsx' not in dy:
    dy = once(dy, "          cp *.html *.png robots.txt sitemap.xml _site/\n",
        "          cp *.html *.css *.jsx *.png robots.txt sitemap.xml _site/   # h2.css + h2-header.jsx: the v2 header shared by the pages (2026-10-03)\n", 'deploy cp')
wr('.github/workflows/deploy.yml', dy)

# ---------------------------------------------------------------- index.html (later the same day): KPI sparklines — loading ≠ unavailable, candles cached
idx = rd('index.html')
if 'H2_PX:' not in idx:
    idx = once(idx, "      LP_VOL:'grays_lp_vol_v1',                   // {pairAddress:{at,pts:[{t,v}]|null}} the LP Pairs table's 7-day volume curves, 30 min (fetchPoolVol7d)\n",
        "      LP_VOL:'grays_lp_vol_v1',                   // {pairAddress:{at,pts:[{t,v}]|null}} the LP Pairs table's 7-day volume curves, 30 min (fetchPoolVol7d)\n"
        "      H2_PX:'grays_h2_px_v1',                     // {token:{at,pts:[{t,v}]}} the KPI tiles' 30-day price candles (GeckoTerminal), 30 min (fetchH2Price7d) — a reload paints Market Cap / Liq-MCap at once\n", 'LS.H2_PX')
    idx = once(idx, "    const H2_TTL=10*60*1000;\n",
        "    const H2_TTL=10*60*1000;\n"
        "    const H2_PX_TTL=30*60*1000;   // the candles' cache (memory + localStorage LS.H2_PX): GeckoTerminal is the one slow read behind the tiles (2026-10-03)\n", 'H2_PX_TTL')
    idx = once(idx, "    const fetchH2Price7d=async(token)=>{\n      const hit=_h2PxCache[token];\n      if(hit&&Date.now()-hit.at<H2_TTL)return hit.pts;\n",
        "    const fetchH2Price7d=async(token)=>{\n"
        "      const hit=_h2PxCache[token];\n"
        "      if(hit&&Date.now()-hit.at<H2_PX_TTL)return hit.pts;\n"
        "      const ls=lsGet(LS.H2_PX,v=>v&&typeof v==='object'&&!Array.isArray(v));   // a reload / token switch within 30 min: the cached candles, no wait (2026-10-03)\n"
        "      const lh=ls&&ls[token];\n"
        "      if(lh&&typeof lh.at==='number'&&Date.now()-lh.at<H2_PX_TTL&&Array.isArray(lh.pts)&&lh.pts.length>=12){_h2PxCache[token]=lh;return lh.pts;}\n", 'px cache read')
    idx = once(idx, "        if(pts.length<12)return null;\n        _h2PxCache[token]={at:Date.now(),pts};\n        return pts;\n",
        "        if(pts.length<12)return null;\n        _h2PxCache[token]={at:Date.now(),pts};\n"
        "        lsSet(LS.H2_PX,{...(ls||{}),[token]:_h2PxCache[token]});\n"
        "        return pts;\n", 'px cache write')
    idx = once(idx, "          setSt(s=>({...s,mcap:pr||s.mcap||null,vol:vol||s.vol||null,liq:liq||s.liq||null,ratio:ratio||s.ratio||null}));   // a miss never blanks a series that was already drawn\n          if((!pr||!vol)&&attempt<3)timers.push(setTimeout(()=>go(attempt+1),[4000,12000,30000][attempt]));\n",
        "          /* a miss never blanks a series that was already drawn; and while retries remain a series that has not landed stays\n"
        "             undefined (= loading, a faint pulsing baseline) — null (= the dashed \"history unavailable\" line) is only said once\n"
        "             the last attempt has missed (2026-10-03; the tiles used to claim \"unavailable\" for the ~5 s GeckoTerminal takes) */\n"
        "          const last=attempt>=3;const keep=(fresh,old)=>fresh||old||(last?null:undefined);\n"
        "          setSt(s=>({...s,mcap:keep(pr,s.mcap),vol:keep(vol,s.vol),liq:keep(liq,s.liq),ratio:keep(ratio,s.ratio)}));\n"
        "          if((!pr||!vol)&&attempt<3)timers.push(setTimeout(()=>go(attempt+1),[4000,12000,30000][attempt]));\n", 'pending series')
    idx = once(idx, "    const H2Spark=({pts,color,id,label})=>{\n      if(!pts||pts.length<3)return(\n",
        "    const H2Spark=({pts,color,id,label})=>{\n"
        "      if(pts===undefined)return(   // still loading (2026-10-03): a faint pulsing baseline, not the dashed \"unavailable\" line\n"
        "        <svg viewBox=\"0 0 240 60\" preserveAspectRatio=\"none\" role=\"img\" aria-label={`${label}: loading ${H2_DAYS} day history`}>\n"
        "          <path className=\"h2-spwait\" d=\"M0,30 L240,30\" fill=\"none\" strokeWidth=\"2\" vectorEffect=\"non-scaling-stroke\"/>\n"
        "        </svg>);\n"
        "      if(!pts||pts.length<3)return(\n", 'H2Spark wait')
    idx = once(idx, "<H2Spark pts={loading?null:ser[key]} color=", "<H2Spark pts={loading?undefined:ser[key]} color=", 'tiles loading undefined')
wr('index.html', idx)
css = rd('h2.css')
if 'h2-spwait' not in css:
    css = once(css, ".h2-tile .h2-sp .h2-spflat{stroke:rgba(255,255,255,.18);stroke-dasharray:6 6}\n",
        ".h2-tile .h2-sp .h2-spflat{stroke:rgba(255,255,255,.18);stroke-dasharray:6 6}\n"
        ".h2-tile .h2-sp .h2-spwait{stroke:rgba(255,255,255,.14);animation:pulse 2s cubic-bezier(.4,0,.6,1) infinite}   /* a series still loading (2026-10-03) — solid, breathing; dashed means it is not coming */\n", 'spwait css')
wr('h2.css', css)
