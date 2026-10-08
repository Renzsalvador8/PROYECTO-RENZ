import sys
from PIL import Image, ImageDraw
from common import *
import char_polys as P
S = SCRATCH
im = Image.open(ref('ref_tester_turnaround_awards.jpg')).convert('RGB')
box = (255, 85, 415, 715)
sc = 3
c = im.crop(box).resize(((box[2]-box[0])*sc, (box[3]-box[1])*sc), Image.LANCZOS)
d = ImageDraw.Draw(c, 'RGBA')
cols = {'HEAD':(255,0,0),'UPPER_ARM':(0,200,255),'FOREARM':(0,255,120),'HAND':(255,200,0),'THIGH':(255,0,255),'SHIN':(120,120,255),'SHOE':(255,120,0)}
for name, col in cols.items():
    poly = getattr(P, name)
    pts = [((x-box[0])*sc, (y-box[1])*sc) for x,y in poly]
    d.polygon(pts, outline=col+(255,), fill=col+(40,))
for k,(x,y) in P.PIVOTS.items():
    X,Y=(x-box[0])*sc,(y-box[1])*sc
    d.ellipse([X-5,Y-5,X+5,Y+5], outline=(255,255,0,255), width=2)
c.save(sys.argv[1])
