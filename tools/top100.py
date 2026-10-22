#!/usr/bin/env python3
"""TOP 100 window (2026-10-22) — builds Shaka's picks from design/top100/mock-top100-v1.html (button B1, look B) into index.html.
Idempotent, run from the repo root:   python3 tools/top100.py      (run it twice: the second run must print "0 edit(s)")
  - the CSS  (tools/top100/t1.css) between /* T100:CSS:BEGIN */ … /* T100:CSS:END */, just before the LEAGUES CSS
  - the JSX  (tools/top100/t1.jsx: TOP100_LIVE, t1Fetch, T1Dot, Top100Modal) between /* T100:JSX:BEGIN */ … END, before PriceEl
  - LS.T100_PREVIEW; the Dashboard's state (showTop100, t100Preview); the "Top 100" button right of Leagues in the Token
    Allocation panel (only when TOP100_LIVE or this device tapped the dot); the modal mount; the faint dot beside the others
Edit the two fragment files, never the spliced copy in index.html — the next run overwrites it.
"""
import hashlib, re
P = 'index.html'
s = open(P, encoding='utf-8').read()
n = 0

def splice(tag, body, anchor):
    global s, n
    b, e = f'/* T100:{tag}:BEGIN */', f'/* T100:{tag}:END */'
    block = f'    {b}\n{body.rstrip()}\n    {e}\n'
    if b in s:
        i, j = s.index('    ' + b), s.index(e) + len(e) + 1
        if s[i:j] != block: s = s[:i] + block + s[j:]; n += 1
    else:
        assert s.count(anchor) == 1, f'anchor x{s.count(anchor)}: {anchor[:60]!r}'
        s = s.replace(anchor, block + anchor); n += 1

def edit(old, new):
    global s, n
    if new in s: return
    assert s.count(old) == 1, f'anchor x{s.count(old)}: {old[:70]!r}'
    s = s.replace(old, new); n += 1

splice('CSS', open('tools/top100/t1.css', encoding='utf-8').read(),
       '    /* LEAGUES (2026-10-04) — the holder-tiers modal')
splice('JSX', open('tools/top100/t1.jsx', encoding='utf-8').read(),
       '    /* u4: hoisted out of Dashboard (Combined share card)')
edit("""      HANDOFF_TOKEN:'ptgc_last_token',""",
     """      T100_PREVIEW:'grays_t100_preview_v1',       // 1 = this device shows the Token Allocation panel's Top 100 button before TOP100_LIVE (T1Dot, 2026-10-22)
      HANDOFF_TOKEN:'ptgc_last_token',""")
edit("""      const[showTierInfo,setShowTierInfo]=useState(false);""",
     """      const[showTierInfo,setShowTierInfo]=useState(false);
      const[showTop100,setShowTop100]=useState(false);   // TOP 100 window (2026-10-22) — the button right of Leagues
      const[t100Preview,setT100Preview]=useState(()=>lsGet(LS.T100_PREVIEW)===1);   // the faint dot's device flag while !TOP100_LIVE""")
LEAGUES_BTN = """<button onClick={()=>setShowTierInfo(true)} className="p2-lg tap-h ml-auto px-2.5 rounded-md text-[11px] font-semibold tracking-wider uppercase text-purple-300 border border-purple-400/30 bg-purple-500/10 hover:bg-purple-500/20 hover:border-purple-400/60 transition-colors">Leagues</button>"""
edit(LEAGUES_BTN, """<span className={`t1btns${(TOP100_LIVE||t100Preview)?' two':''}`}>""" + LEAGUES_BTN + """
                    {(TOP100_LIVE||t100Preview)&&<button onClick={()=>setShowTop100(true)} className="p2-lg tap-h px-2.5 rounded-md text-[11px] font-semibold tracking-wider uppercase text-purple-300 border border-purple-400/30 bg-purple-500/10 hover:bg-purple-500/20 hover:border-purple-400/60 transition-colors">Top 100</button>}</span>""")
edit("""          {!VOL_SPLIT_LIVE&&activeTab==='dashboard'&&<VsDot token={token} onOpen={()=>setShowVolSplit(true)}/>}""",
     """          {!VOL_SPLIT_LIVE&&activeTab==='dashboard'&&<VsDot token={token} onOpen={()=>setShowVolSplit(true)}/>}
          {/* TOP 100 (2026-10-22): the Token Allocation panel's window. The button is hidden until TOP100_LIVE; the faint dot shows / hides it on this device. */}
          {showTop100&&<Top100Modal token={token} price={data&&data.price>0?data.price:0} onClose={()=>setShowTop100(false)}/>}
          {!TOP100_LIVE&&activeTab==='dashboard'&&<T1Dot token={token} on={t100Preview} onToggle={()=>{const v=!t100Preview;setT100Preview(v);lsSet(LS.T100_PREVIEW,v?1:0);}}/>}""")

if n: open(P, 'w', encoding='utf-8').write(s)
print(f'top100: {n} edit(s), index.html sha256 {hashlib.sha256(s.encode()).hexdigest()[:8]}')
