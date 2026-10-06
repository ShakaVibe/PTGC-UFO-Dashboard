#!/usr/bin/env python3
"""Charts page, round 3 (2026-10-06, Shaka): (1) the lone "The Grays vs Others" sub-tab box is gone and the page moves up;
(2) the Share Chart badge is the Calculators buttons' glass (cp-btn look, Rajdhani, a drawn camera) at the RIGHT of its row,
its menu dropping down right-aligned; (3) on every page with the metallic "Grays …" / "Socials Hub" title, the gold word
turns the UFO GREEN gradient while UFO is the current token — `html[data-tok]` is stamped by each page's header
(charts.html h2ApplyTheme, h2-header.jsx SiteHeaderV2 for Calculators + Portfolio, index.html DashHeaderV2) and one CSS
rule per page reads it. Run after tools/charts-gt.py: python3 tools/charts-v3.py (a file already done is skipped)."""
import sys,pathlib
root=pathlib.Path(__file__).resolve().parent.parent
class Applied(Exception): pass
def edit(name,fn):
    p=root/name; s=p.read_text()
    try: s2=fn(s)
    except Applied as e: print('already applied:',name); return
    assert s2!=s,name; p.write_text(s2); print('edited',name)
def rep(s,old,new,count=1):
    n=s.count(old); assert n==count,(old[:80],n); return s.replace(old,new)

GREEN='linear-gradient(180deg,#F0FFD0 0%,#A6FF5C 40%,#3E9C12 62%,#8DFF3A 100%)'

def charts(s):
    if 'cp-share' in s: raise Applied()
    # 1. the sub-tab box goes (nothing in the script read it)
    s=rep(s,'''    <!-- Sub-tabs — same glow style as X Multiplier / Moon Math / Rewards -->
    <div class="flex justify-center mb-10">
      <div class="inline-flex gap-2" id="chartSubTabs">
        <button class="relative overflow-hidden rounded-xl font-orbitron font-bold text-sm sm:text-base transition-all hover:brightness-110 chart-sub-tab active" data-tab="compare" style="padding:10px 24px;background:linear-gradient(135deg,rgba(212,175,55,0.45),rgba(212,175,55,0.2));border:1px solid rgba(212,175,55,0.6);box-shadow:0 0 20px rgba(212,175,55,0.25),inset 0 1px 0 rgba(255,255,255,0.15);color:white">The Grays vs Others</button>
      </div>
    </div>
''','')
    s=rep(s,'.cp-page .chart-sub-tab,.cp-page .share-menu-wrap button{backdrop-filter:blur(4px)}',
            '.cp-page .share-menu-wrap button{backdrop-filter:blur(4px)}')
    # 2. the share badge: right of its row, the Calculators buttons' glass, a drawn camera
    s=rep(s,'''    <div class="share-menu-wrap" style="display:flex;justify-content:center">
      <div style="position:relative">
        <button class="camera-btn" onclick="toggleShareMenu()" title="Share to Twitter"><span style="font-size:20px;line-height:1">&#128247;</span> Share Chart</button>''',
'''    <div class="share-menu-wrap cp-share">
      <div style="position:relative">
        <button class="camera-btn" onclick="toggleShareMenu()" title="Share to Twitter" aria-haspopup="menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 8.5h3l1.6-2.5h6.8L17 8.5h3a1.5 1.5 0 0 1 1.5 1.5v8A1.5 1.5 0 0 1 20 19.5H4A1.5 1.5 0 0 1 2.5 18v-8A1.5 1.5 0 0 1 4 8.5z"/><circle cx="12" cy="13.5" r="3.4"/><circle cx="17.6" cy="11" r=".6" fill="currentColor"/></svg>Share Chart</button>''')
    s=rep(s,'''  .cp-page .chart-card{background:rgba(8,8,10,.86);''',
'''  .cp-share{display:flex;justify-content:flex-end;margin:-16px 0 14px}   /* 2026-10-06: the badge at the right of the card's width, menu right-aligned */
  .cp-share .camera-btn{--c:242,201,76;--c2:255,215,120;margin:0;height:46px;padding:0 20px 0 15px;gap:10px;border-radius:12px;border:1.5px solid rgba(var(--c),.6);color:#FFE38A;font-family:'Rajdhani',sans-serif;font-weight:700;font-size:19px;letter-spacing:.02em;text-shadow:0 1px 2px rgba(0,0,0,.8);background:radial-gradient(ellipse at 50% 0%,rgba(var(--c),.24),rgba(0,0,0,0) 70%),repeating-linear-gradient(0deg,rgba(255,255,255,.012) 0 1px,transparent 1px 3px),linear-gradient(180deg,rgba(24,20,8,.92),rgba(8,7,4,.94));box-shadow:0 0 24px -4px rgba(var(--c),.55),0 8px 24px -12px rgba(0,0,0,.9),inset 0 1px 0 rgba(255,255,255,.14)}
  .cp-share .camera-btn svg{width:24px;height:24px;color:#F7D35A;filter:drop-shadow(0 2px 3px rgba(0,0,0,.85))}
  .cp-share .camera-btn:hover{filter:brightness(1.1);transform:translateY(-1px);border-color:rgba(var(--c2),.95);box-shadow:0 0 30px -4px rgba(var(--c),.7),inset 0 1px 0 rgba(255,255,255,.16)}
  .cp-share .share-menu{left:auto;right:0;transform:none}
  html[data-tok="UFO"] .cp-share .camera-btn{--c:141,255,58;--c2:200,255,150;color:#D9FFB0}
  html[data-tok="UFO"] .cp-share .camera-btn svg{color:#8DFF3A}
  html[data-tok="UFO"] .cp-t.g{background-image:'''+GREEN+'''}   /* 2026-10-06: the gold word goes UFO green on UFO (Shaka) */
  .cp-page .chart-card{background:rgba(8,8,10,.86);''')
    s=rep(s,'''    .cp-t{font-size:30px;letter-spacing:0}.cp-t.w{margin-left:.18em}''',
'''    .cp-t{font-size:30px;letter-spacing:0}.cp-t.w{margin-left:.18em}
    .cp-share .camera-btn{height:40px;font-size:16px;padding:0 14px 0 11px}.cp-share .camera-btn svg{width:20px;height:20px}''')
    # 3. the page stamps the token on <html>
    s=rep(s,'''function h2ApplyTheme(t, other) {
  h2All('.h2', e => e.dataset.tok = t.name);''','''function h2ApplyTheme(t, other) {
  h2All('.h2', e => e.dataset.tok = t.name);
  document.documentElement.dataset.tok = t.name;   // 2026-10-06: the metallic title + share badge read it (gold on PTGC, green on UFO)''')
    return s

def calculators(s):
    if 'html[data-tok="UFO"] .cp-t.g' in s: raise Applied()
    return rep(s,'''    .cp-t.w{background-image:linear-gradient(180deg,#FFF 0%,#E6E6E6 45%,#8C8C8C 60%,#DDD 100%);margin-left:.22em}''',
'''    .cp-t.w{background-image:linear-gradient(180deg,#FFF 0%,#E6E6E6 45%,#8C8C8C 60%,#DDD 100%);margin-left:.22em}
    html[data-tok="UFO"] .cp-t.g{background-image:'''+GREEN+'''}   /* 2026-10-06: the gold word goes UFO green on UFO (Shaka); h2-header.jsx stamps html[data-tok] */''')

def h2header(s):
    if 'documentElement.dataset.tok' in s: raise Applied()
    return rep(s,'''const SiteHeaderV2=(p)=>{
  const{token,logo,otherLogo,address,data,loading,hdrDaysOld,copied,copyAddress,plsRatio,xToATH,xToPenny,fmtX,renderPrice,onBack,onSwitch,onBuy,navTo,active}=p;
  const sc=useH2Scale();''','''const SiteHeaderV2=(p)=>{
  const{token,logo,otherLogo,address,data,loading,hdrDaysOld,copied,copyAddress,plsRatio,xToATH,xToPenny,fmtX,renderPrice,onBack,onSwitch,onBuy,navTo,active}=p;
  const sc=useH2Scale();
  React.useEffect(()=>{document.documentElement.dataset.tok=token;},[token]);   // 2026-10-06: the pages' metallic titles read html[data-tok] (gold on PTGC, green on UFO)''')

def index(s):
    if 'html[data-tok="UFO"] .sh-t.g' in s: raise Applied()
    s=rep(s,'''    .sh-t.w{background-image:linear-gradient(180deg,#FFF 0%,#E6E6E6 45%,#8C8C8C 60%,#DDD 100%);margin-left:.22em}''',
'''    .sh-t.w{background-image:linear-gradient(180deg,#FFF 0%,#E6E6E6 45%,#8C8C8C 60%,#DDD 100%);margin-left:.22em}
    html[data-tok="UFO"] .sh-t.g{background-image:'''+GREEN+'''}   /* 2026-10-06: "Socials" goes UFO green on UFO (Shaka); DashHeaderV2 stamps html[data-tok] */''')
    s=rep(s,'''    const DashHeaderV2=(p)=>{
      const{token,cfg,data,loading,hdrDaysOld,copied,copyAddress,changeKnown,priceUp,plsRatio,xToATH,xToPenny,athPrice,fmtX,onBack,onSwitch,openSwap,activeTab,gotoTab,openBeam,onAffiliates,fresh}=p;
      const sc=useH2Scale();''','''    const DashHeaderV2=(p)=>{
      const{token,cfg,data,loading,hdrDaysOld,copied,copyAddress,changeKnown,priceUp,plsRatio,xToATH,xToPenny,athPrice,fmtX,onBack,onSwitch,openSwap,activeTab,gotoTab,openBeam,onAffiliates,fresh}=p;
      const sc=useH2Scale();
      useEffect(()=>{document.documentElement.dataset.tok=token;},[token]);   // 2026-10-06: the Socials Hub title reads html[data-tok] (gold on PTGC, green on UFO)''')
    return s

edit('charts.html',charts); edit('calculators.html',calculators); edit('h2-header.jsx',h2header); edit('index.html',index)
