#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka, on lh-cards-live.py: "I don't like how the net made you change it all to a new line.. put it back
and let's not put the net" + "I don't like the text 'in the chart' — rather just the border or something makes it more obvious"):
  - NET CHANGE removed; JOINED / LEFT / SHARE back beside the title (desktop) / in one row (phone) as before;
  - the IN THE CHART tab removed; the selected card says it with its frame instead: a 2.5 px bright border in the token colour,
    a brighter outer glow and the lift.
Idempotent, from the repo root:   python3 tools/lh-cards-fix.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
def swap(path, old, new):
    """replace `old` (once) when it is still there — safe when `new` is a part of `old`"""
    global n
    s = open(path, encoding='utf-8').read()
    if old not in s: return
    assert s.count(old) == 1, f'{path}: x{s.count(old)}: {old[:80]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1
J, C = 'tools/league-history/lh.jsx', 'tools/league-history/lh.css'

swap(J, "<div className=\"r\">{(()=>{const nt=fl?fl[0][sel]-fl[1][sel]:b-a;return<div className=\"lh-pill net\"><div className=\"k\"><span className=\"lg\">NET CHANGE</span><span className=\"sm\">NET</span></div>"
        "<div className={`n ${nt>0?'lh-up':nt<0?'lh-dn':''}`}>{nt>0?'+':nt<0?'\\u2212':''}{lhFmt(Math.abs(nt))}</div></div>;})()}",
        "<div className=\"r\">")
swap(J, "\n                    {sel===i&&<span className=\"lh-on\" aria-hidden=\"true\">{'\\u25BC'} IN THE CHART</span>}", "")

swap(C, """    .lh-on{position:absolute;left:50%;bottom:-11px;transform:translateX(-50%);z-index:2;white-space:nowrap;padding:3px 10px;border-radius:99px;
      font:700 9.5px 'Orbitron',sans-serif;letter-spacing:.14em;color:#0a0b10;background:linear-gradient(180deg,var(--a2),var(--a));box-shadow:0 0 12px rgba(var(--rgb),.6)}""",
        """    .lh-cd[aria-pressed=true]{border:2.5px solid var(--a);   /* the selected card: its frame says "this is the chart below" (no tab — Shaka) */
      box-shadow:0 14px 30px rgba(0,0,0,.6),0 0 0 1px rgba(var(--rgb),.35),0 0 34px rgba(var(--rgb),.6),inset 0 0 26px rgba(var(--rgb),.18),inset 0 -18px 34px rgba(56,189,248,.08)}""")
swap(C, """    .lh-bh{flex-wrap:wrap!important}.lh-bh .l{flex:1 1 100%}.lh-bh .r{width:100%;display:grid;grid-template-columns:repeat(4,minmax(0,1fr));margin-top:14px}.lh-bh .r .lh-pill{min-width:0}   /* four boxes: their own row */
    .lh-pill.net{border-color:rgba(var(--rgb),.55);box-shadow:inset 0 0 18px rgba(var(--rgb),.1)}.lh-pill.net .n{font-size:30px}
""", "")
swap(C, "@media(max-width:700px){.lh-cd .hl{font-size:13px}.lh-on{font-size:8.5px;bottom:-9px;padding:2px 8px}", "@media(max-width:700px){.lh-cd .hl{font-size:13px}")
swap(C, "\n      .lh-bh .r{display:grid;grid-template-columns:1fr 1fr;width:100%}.lh-pill.net .n{font-size:24px}}", "}")

# + "I also don't like the fire emoji you added to Poseidon": no 🔥 anywhere for the burn wallet — the card icon, the beam tip, the
#   footers, the share card, the dashboard strip's icon and its phone caption (the words "The Burn address" stay)
swap(J, "{t.burnIn&&t.burnIn[basis]===i&&<span className=\"bw\" title=\"Includes the burn wallet (0x…0369)\" aria-label=\"includes the burn wallet\">{'\\u{1F525}'}</span>}", "")
swap(J, "{bw&&<div className=\"bn\">{'\\u{1F525}'} {c===1", "{bw&&<div className=\"bn\">{c===1")
swap(J, "<span>People only + the {'\\u{1F525}'} burn wallet", "<span>People only + the burn wallet")
swap(J, "<b>People only, plus the {'\\u{1F525}'} burn wallet</b>", "<b>People only, plus the burn wallet</b>")
IX = 'index.html'
swap(IX, "{tiers&&tiers.burnIn===k&&<span className=\"bw\" aria-label=\"includes the burn wallet\">{'\\u{1F525}'}</span>}", "")
swap(IX, "<div className=\"bwn\">{'\\u{1F525}'} {`${tiers.burnIn} = the Burn address`}</div>", "<div className=\"bwn\">{`${tiers.burnIn} = the Burn address`}</div>")

out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-cards-fix: {n} edit(s); index.html {sha("index.html")}, lh.jsx {sha(J)}, lh.css {sha(C)}')
