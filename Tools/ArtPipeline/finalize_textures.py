"""Final pass over every exported texture: pad to multiples of 4 (transparent pixels added on the right and
top, so bottom-anchored pivots are unchanged) which keeps GPU block compression (DXT/ETC) available on WebGL.
Seamless tiles are skipped (they are authored at multiple-of-4 widths). Prints a texture memory summary."""
import os
import numpy as np
from PIL import Image
from common import ART_OUT, UI_OUT

SKIP = ('/Showroom/floor.png', '/Zenith/floor.png', '/Drive/road.png', '/UI/grain.png')


def main():
    total_px = 0
    padded = []
    for root in (ART_OUT, UI_OUT):
        for dirpath, _, files in os.walk(root):
            for f in files:
                if not f.endswith('.png'):
                    continue
                p = os.path.join(dirpath, f)
                im = Image.open(p)
                w, h = im.size
                total_px += w * h
                if any(p.endswith(s) for s in SKIP):
                    if w % 4 or h % 4:
                        print('WARNING tile not multiple of 4:', p, im.size)
                    continue
                nw, nh = w + (-w) % 4, h + (-h) % 4
                if (nw, nh) != (w, h):
                    out = Image.new('RGBA', (nw, nh), (0, 0, 0, 0))
                    out.paste(im.convert('RGBA'), (0, nh - h))
                    out.save(p, optimize=True)
                    padded.append((os.path.relpath(p, root), (w, h), (nw, nh)))
    print('padded', len(padded), 'textures')
    print('total texels: %.1f M  (~%.0f MB as DXT5/BC3, ~%.0f MB uncompressed)' % (total_px / 1e6, total_px / 1e6, total_px * 4 / 1e6))


if __name__ == '__main__':
    main()
