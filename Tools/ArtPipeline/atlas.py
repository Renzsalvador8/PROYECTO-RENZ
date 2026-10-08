"""Tiny shelf atlas packer. Outputs Unity-style rects (origin bottom-left)."""
import numpy as np
from PIL import Image
from common import next_pot


def pack(images, pad=6, max_w=2048):
    """images: dict name -> PIL RGBA. Returns (atlas PIL, rects dict name->(x,y,w,h) bottom-left origin)."""
    items = sorted(images.items(), key=lambda kv: -kv[1].height)
    x = y = pad
    shelf_h = 0
    pos = {}
    width = 0
    for name, im in items:
        w, h = im.size
        if x + w + pad > max_w:
            x = pad
            y += shelf_h + pad
            shelf_h = 0
        pos[name] = (x, y)
        x += w + pad
        width = max(width, x)
        shelf_h = max(shelf_h, h)
    height = y + shelf_h + pad
    W, H = next_pot(width), next_pot(height)
    atlas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rects = {}
    for name, im in items:
        px, py = pos[name]
        atlas.paste(im, (px, py))
        rects[name] = (px, H - py - im.height, im.width, im.height)
    # bleed edge colours into transparent padding to avoid dark fringes with bilinear/mips
    atlas = bleed(atlas)
    return atlas, rects


def bleed(img, iterations=6):
    from scipy import ndimage
    a = np.asarray(img).astype(np.float32)
    rgb = a[:, :, :3].copy()
    alpha = a[:, :, 3]
    known = alpha > 0
    for _ in range(iterations):
        acc = np.zeros_like(rgb)
        cnt = np.zeros(alpha.shape, np.float32)
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            sh_known = np.roll(known, (dy, dx), (0, 1))
            sh_rgb = np.roll(rgb, (dy, dx), (0, 1))
            m = sh_known & ~known
            acc[m] += sh_rgb[m]
            cnt[m] += 1
        new = cnt > 0
        rgb[new] = acc[new] / cnt[new][:, None]
        known = known | new
    out = np.dstack([rgb, alpha])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), 'RGBA')
