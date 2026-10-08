"""Debug helper: crop a region of an image, upscale, overlay a coordinate grid (source pixel coords)."""
import sys
from PIL import Image, ImageDraw, ImageFont
def gridcrop(src, box, scale, out, step=10, label_every=50):
    im = Image.open(src).convert('RGB')
    x0,y0,x1,y1 = box
    c = im.crop(box).resize(((x1-x0)*scale,(y1-y0)*scale), Image.NEAREST)
    d = ImageDraw.Draw(c, 'RGBA')
    for x in range((x0//step)*step, x1+1, step):
        if x < x0: continue
        X=(x-x0)*scale; strong = x % label_every == 0
        d.line([(X,0),(X,c.height)], fill=(255,0,0,110 if strong else 40), width=1)
        if strong: d.text((X+2,2), str(x), fill=(255,0,0,255))
    for y in range((y0//step)*step, y1+1, step):
        if y < y0: continue
        Y=(y-y0)*scale; strong = y % label_every == 0
        d.line([(0,Y),(c.width,Y)], fill=(0,0,255,110 if strong else 40), width=1)
        if strong: d.text((2,Y+2), str(y), fill=(0,0,255,255))
    c.save(out)
if __name__ == '__main__':
    src,out = sys.argv[1], sys.argv[2]
    box = tuple(int(v) for v in sys.argv[3].split(','))
    scale = int(sys.argv[4]) if len(sys.argv)>4 else 3
    gridcrop(src, box, scale, out)
