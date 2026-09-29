#!/usr/bin/env python3
"""Generates assets/coin-corona.png — the fire light behind the PTGC coin (2026-09-29, v10/v11).
Tight, cloudy flame (2-D noise, not rays), strongest on the left and upper right like Shaka's reference, a few embers.
520×520 RGBA; coin radius 97.5 px (a 195 px coin) centred. Place it at left/top -162 px around the coin, mix-blend screen.
Needs numpy + Pillow. Run: python3 make-corona.py  (writes ../assets/coin-corona.png)"""
import os
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

rng = np.random.default_rng(5)
N = 520; c = N / 2; r0 = 97.5
y, x = np.mgrid[0:N, 0:N]; dx = x - c; dy = y - c; d = np.hypot(dx, dy); a = np.arctan2(dy, dx)

def ang_noise(k, n):
    t = np.zeros_like(a)
    for h in range(1, k + 1):
        t += rng.normal(0, 1 / h ** n) * np.cos(h * a + rng.uniform(0, 6.3))
    return t

def fbm():  # cloudy fire texture
    f = np.zeros((N, N))
    for s, w in [(4, 1), (8, .6), (16, .4), (32, .25)]:
        g = rng.random((N // s + 2, N // s + 2))
        im = Image.fromarray((g * 255).astype(np.uint8)).resize((N + 2 * s, N + 2 * s), Image.BICUBIC).crop((s, s, N + s, N + s))
        f += w * (np.asarray(im) / 255.0)
    return (f - f.min()) / (f.max() - f.min())

F = fbm()
base = 0.5 + 0.5 * np.cos(a - np.deg2rad(195)) ** 2 + 0.4 * np.clip(np.cos(a - np.deg2rad(-55)), 0, 1)
reach = np.clip((7 + 17 * base) * (1 + 0.3 * ang_noise(16, 1.0)), 4, 40)
out = np.clip(d - r0, 0, None)
I = np.exp(-out / reach) * (0.45 + 0.9 * F)
I = np.clip(I * np.clip((d - r0 + 3) / 3, 0, 1), 0, 1)
stops = [(0, (30, 6, 0)), (0.22, (150, 40, 5)), (0.45, (245, 110, 15)), (0.7, (255, 180, 60)), (0.9, (255, 225, 140)), (1, (255, 250, 225))]
rgb = np.zeros((N, N, 3))
for (p0, c0), (p1, c1) in zip(stops, stops[1:]):
    m = (I >= p0) & (I <= p1); t = ((I - p0) / (p1 - p0))[m][:, None]
    rgb[m] = np.array(c0) * (1 - t) + np.array(c1) * t
alpha = np.clip(I ** 0.9 * 255, 0, 255)
im = Image.fromarray(np.dstack([rgb, alpha]).astype(np.uint8), 'RGBA').filter(ImageFilter.GaussianBlur(0.8))
dr = ImageDraw.Draw(im)
for _ in range(36):
    ang = rng.uniform(0, 2 * np.pi); rr = r0 + rng.uniform(6, 50)
    if np.cos(ang - np.deg2rad(20)) > 0.6 and rng.random() < .8:
        continue
    px, py = c + rr * np.cos(ang), c + rr * np.sin(ang); s = rng.uniform(.5, 1.4)
    dr.ellipse([px - s, py - s, px + s, py + s], fill=(255, 205, 120, int(rng.uniform(110, 240))))
im.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'coin-corona.png'))
print('written')
