#!/usr/bin/env python3
"""League History, 2026-10-24 (Shaka picked mock-up A, "but make them even smaller"): the header's LEAGUES and SHARE as two small
pills in ONE row left of ✕ — 26 px tall, 9.5 px text, a 16 px trident / camera (were 38 px pills stacked). Phone: icon-only small
circles, the trident under the camera (a row of three would run into the coin).
Idempotent, from the repo root:   python3 tools/lh-btns-small.py   (twice: "0 edit(s)"); it re-splices via tools/league-history.py.
"""
import hashlib, subprocess, sys
n = 0
C = 'tools/league-history/lh.css'
CSS = """
    /* 2026-10-24 (Shaka, mock-up A smaller): LEAGUES + SHARE = two small pills in one row left of the close button */
    .lh-cam,.lh-lgb{top:25px;height:26px;padding:0 10px 0 7px;border-radius:13px;font-size:9.5px;letter-spacing:.12em;gap:5px}
    .lh-cam{right:64px}.lh-lgb{right:150px}.lh-lgb img{width:16px;height:16px}
    .lh-x{top:20px;width:34px;height:34px;line-height:32px;font-size:19px}
    @media(max-width:700px){.lh-cam,.lh-lgb{width:30px;height:30px;padding:0;justify-content:center;border-radius:50%}
      .lh-cam span,.lh-lgb span{display:none}.lh-cam{right:56px;top:16px;font-size:13px}.lh-lgb{right:56px;top:52px}.lh-lgb img{width:19px;height:19px}
      .lh-x{top:14px;right:14px;width:34px;height:34px;line-height:32px}}
"""
s = open(C, encoding='utf-8').read()
if 'mock-up A smaller' not in s:
    open(C, 'w', encoding='utf-8').write(s.rstrip('\n') + '\n' + CSS.lstrip('\n')); n += 1
out = subprocess.run([sys.executable, 'tools/league-history.py'], capture_output=True, text=True)
if out.returncode: print(out.stdout, out.stderr); sys.exit(1)
print('  ' + out.stdout.strip().splitlines()[-1])
sha = lambda p: hashlib.sha256(open(p, 'rb').read()).hexdigest()[:8]
print(f'lh-btns-small: {n} edit(s); index.html {sha("index.html")}, lh.css {sha(C)}')
