import sys, json
from PIL import Image, ImageDraw
from rigtools import *
from common import SCRATCH, GAME
import os

def strip(rig, clip, n, ppu=170, size=(260, 470), slot_sprites=None, travel=False):
    frames = []
    for i in range(n):
        t = clip['length'] * i / n
        pose = eval_clip(clip, t)
        im = render(rig, pose, size=size, ppu_out=ppu, bg=(214, 203, 192, 255), slot_sprites=slot_sprites)
        d = ImageDraw.Draw(im)
        d.line([(0, size[1] - 30), (size[0], size[1] - 30)], fill=(120, 100, 90, 255))
        d.text((4, 4), f"{clip['name']} t={t:.2f}", fill=(0, 0, 0, 255))
        frames.append(im)
    W = size[0] * n
    out = Image.new('RGBA', (W, size[1]))
    for i, f in enumerate(frames):
        out.paste(f, (i * size[0], 0))
    return out

if __name__ == '__main__':
    rig = load_rig('tester_side')
    data = json.load(open(os.path.join(GAME, 'Animations', 'Resources', 'Animations', 'tester_clips.json')))
    clips = {c['name']: c for c in data['clips']}
    names = sys.argv[1].split(',')
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
    rows = [strip(rig, clips[nm], n, slot_sprites={'prop_f': 'magnifier'}) for nm in names]
    out = Image.new('RGBA', (rows[0].width, sum(r.height for r in rows)))
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height
    out.save(os.path.join(SCRATCH, 'strip_' + '_'.join(names) + '.png'))
