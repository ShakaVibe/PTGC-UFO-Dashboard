#!/usr/bin/env python3
"""Panel backdrops from Shaka's own art, hue-shifted to each panel's colour (2026-09-30).
Usage: python3 tint.py  — writes bg-*.jpg next to this file. Source images are in the repo (logos/)."""
import os, numpy as np
from PIL import Image
H=os.path.dirname(os.path.abspath(__file__)); R=os.path.abspath(os.path.join(H,'..','..','..'))
def shift(im,dh,sat=1.0,val=1.0):
    a=np.array(im.convert('RGB')).astype(np.float32)/255.0
    r,g,b=a[...,0],a[...,1],a[...,2]
    mx=a.max(-1);mn=a.min(-1);d=mx-mn+1e-9
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))/6.0
    s=np.where(mx>0,d/(mx+1e-9),0);v=mx
    h=(h+dh/360.0)%1.0; s=np.clip(s*sat,0,1); v=np.clip(v*val,0,1)
    i=(h*6).astype(int)%6;f=h*6-np.floor(h*6);p=v*(1-s);q=v*(1-f*s);t=v*(1-(1-f)*s)
    sel=lambda *o:np.select([i==0,i==1,i==2,i==3,i==4,i==5],list(o))
    return Image.fromarray((np.stack([sel(v,q,p,p,t,v),sel(t,v,v,q,p,p),sel(p,p,t,v,v,q)],-1)*255).astype(np.uint8))
cosmic=Image.open(os.path.join(R,'logos/home/cosmic-bg.jpg'))
left=cosmic.crop((0,100,600,560))           # gold nebula + planet rim + mountains, left of the alien
shift(left,-22,1.15,0.9).resize((1200,920),Image.LANCZOS).save(os.path.join(H,'bg-burn.jpg'),quality=82,optimize=True)   # fire
band=Image.open(os.path.join(R,'logos/header/dash-bg.jpg'))
green=band.crop((1300,0,2168,350))            # the band's green side: two planets, green nebula, mountains (as painted)
shift(green,0,1.1,1.0).resize((1736,700),Image.LANCZOS).save(os.path.join(H,'bg-vg.jpg'),quality=84,optimize=True)   # value generated
mid=band.crop((500,0,1250,350))              # the band's centre: big planet rim, nebula, mountains (gold, no green)
shift(mid,240,1.0,0.95).resize((1500,700),Image.LANCZOS).save(os.path.join(H,'bg-alloc.jpg'),quality=84,optimize=True)   # token allocation: gold → purple
leftband=band.crop((0,0,760,350))            # the band's left: gold planet rim, nebula, mountains
shift(leftband,178,1.35,1.2).resize((1520,700),Image.LANCZOS).save(os.path.join(H,'bg-dao.jpg'),quality=84,optimize=True)   # dao treasury: gold → blue
fl=Image.open(os.path.join(H,'flames.png')).convert('RGBA'); a=fl.split()[3]
fg=shift(fl.convert('RGB'),85,1.15,1.05); fg.putalpha(a); fg.save(os.path.join(H,'flames-green.png'),optimize=True)   # the same flame strip, fire → UFO green (PTGC Burned by UFO's bar)
print('ok')
