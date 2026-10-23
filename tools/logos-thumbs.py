#!/usr/bin/env python3
"""Logos windows: small thumbnails instead of the full-size downloads (Audit IV P-4; Shaka, 2026-10-24: "1 yes").
Idempotent, from the repo root:   python3 tools/logos-thumbs.py   (needs Pillow; a second run prints "0 edit(s), 0 thumb(s)")

The three Logos windows (PTGC / UFO / Combined) drew each logo from its 2000–3000 px download file — 5.8 MB for the three
windows, and a phone decodes seven 16 MB bitmaps to open Combined. Now each tile shows logos/<dir>/thumbs/<name>.webp
(longest side 480 px = a ~230 px tile on a 2× screen, transparency kept, lazy-loaded); the tile's link and `download` still
point at the original file, so what people download is unchanged.
"""
import os, re, sys
from PIL import Image

n = 0
made = 0
LISTS = {
    'ptgc': ['06_PTGC_V1_transparent_bg.png', '06_PTGC_V2_transparent_bg.png', '06_PTGC_Horizontal_V6_transparent_bg.png',
             '06_PTGC_Horizontal_V7_transparent_bg.png', '12_PTGC_V1_transparent_bg_grayscale.png',
             '12_PTGC_V3_grayscale_transparent_bg.png', '18_PTGC_V1_BW_transparent_bg.png'],
    'ufo': ['06_Ufo_New_transparent_bg.png', '06_Ufo_New_V2_transparent_bg.png', '06_Ufo_New_V3_transparent_bg.png',
            '06_Ufo_New_V4_transparent_bg.png', '12_Ufo_New_transparent_bg_Grayscale.png', '18_Ufo_New_transparent_bg_BW.png'],
    'combined': ['07_Combined_PTGC_UFO_Transparent.png', '07_Two_Color_Alien_Transparent.png',
                 '14_Two_Color__Alien_2_Transparent.png', '04_Two_logos_pattern_bg.jpg', 'TheGraysXBnr.png'],
}
MAX = 480

for d, files in LISTS.items():
    os.makedirs(f'logos/{d}/thumbs', exist_ok=True)
    for f in files:
        src = f'logos/{d}/{f}'
        dst = f'logos/{d}/thumbs/{os.path.splitext(f)[0]}.webp'
        if os.path.exists(dst) and os.path.getmtime(dst) >= os.path.getmtime(src):
            continue
        im = Image.open(src)
        im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
        im.thumbnail((MAX, MAX), Image.LANCZOS)
        im.save(dst, 'WEBP', quality=82, method=6)
        made += 1

def edit(path, old, new, count=1):
    global n
    s = open(path, encoding='utf-8').read()
    if new in s: return
    assert s.count(old) == count, f'{path}: anchor x{s.count(old)} (want {count}): {old[:90]!r}'
    open(path, 'w', encoding='utf-8').write(s.replace(old, new)); n += 1

for d in LISTS:
    edit('index.html',
         '<img src={`logos/%s/${logo.file}`} alt={logo.name} className="max-w-full max-h-full object-contain"/>' % d,
         '<img src={`logos/%s/thumbs/${logo.file.replace(/\\.\\w+$/,\'.webp\')}`} alt={logo.name} loading="lazy" decoding="async" className="max-w-full max-h-full object-contain"/>' % d)

print(f'{n} edit(s), {made} thumb(s)')
