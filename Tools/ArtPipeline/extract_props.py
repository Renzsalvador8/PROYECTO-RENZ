"""Cut props, awards and the Zenith logo out of the provided reference sheets."""
import numpy as np
from scipy import ndimage
from PIL import Image
from common import *
from matte import key_region


def keyed(src, box, excl=(), t_bg=22, t_fg=60, keep_largest=True, min_frac=0.02):
    full = to_np(Image.open(ref(src)))
    k = key_region(full, box, t_bg=t_bg, t_fg=t_fg)
    a = k[:, :, 3] / 255.0
    h, w = a.shape
    if excl:
        a = a * (1 - poly_mask((w, h), [[(x - box[0], y - box[1]) for x, y in p] for p in excl]))
    if keep_largest:
        lab, n = ndimage.label(a > 0.35)
        if n > 1:
            sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
            keep = [i + 1 for i, s in enumerate(sizes) if s >= sizes.max() * min_frac]
            a = a * ndimage.binary_dilation(np.isin(lab, keep), iterations=2)
    k[:, :, 3] = a * 255
    return k


def trimmed(arr, pad=3):
    a = arr[:, :, 3]
    ys, xs = np.nonzero(a > 2)
    return arr[max(ys.min() - pad, 0):ys.max() + pad + 1, max(xs.min() - pad, 0):xs.max() + pad + 1]


def save(arr, name):
    img = Image.fromarray(np.clip(trimmed(arr), 0, 255).astype(np.uint8), 'RGBA')
    from atlas import bleed
    img = bleed(img, 4)
    save_png(img, name)
    return img


AW = 'ref_awards_lux_effie.jpg'
PROPS = 'ref_props_sheet.jpg'
PROP_BOXES = {
    'papers': (405, 48, 650, 228), 'mug': (790, 66, 948, 218), 'laptop': (1056, 36, 1310, 252),
    'chair': (76, 266, 294, 558), 'paper_stack': (400, 292, 668, 512), 'lamp': (752, 252, 990, 508),
    'camera': (1050, 320, 1300, 508), 'key': (76, 576, 304, 724), 'switch': (480, 560, 580, 718),
    'box': (736, 536, 990, 728), 'envelope': (1080, 550, 1310, 718), 'sparkles': (90, 36, 276, 236),
}


def build():
    out = {}
    # Awards — front views (with GRAND PRIX emboss) and 3/4 views
    lux = keyed(AW, (124, 36, 282, 370), excl=[[(238, 20), (300, 20), (300, 62), (238, 62)]], t_bg=18, t_fg=50)
    out['lux'] = save(lux, 'Props/award_lux_grand_prix')
    lux34 = keyed(AW, (436, 36, 600, 370), t_bg=18, t_fg=50)
    out['lux34'] = save(lux34, 'Props/award_lux_grand_prix_34')
    effie = keyed(AW, (86, 466, 322, 692), t_bg=18, t_fg=50)
    out['effie'] = save(effie, 'Props/award_effie_bronze')
    effie34 = keyed(AW, (396, 466, 650, 700), t_bg=18, t_fg=50)
    out['effie34'] = save(effie34, 'Props/award_effie_bronze_34')
    for name, box in PROP_BOXES.items():
        k = keyed(PROPS, box, t_bg=20, t_fg=55, keep_largest=(name != 'sparkles'))
        out[name] = save(k, 'Props/' + name)
    # Zenith logo: cream mark on transparent (tinted at runtime)
    logo = np.asarray(Image.open(ref('ref_zenith_logo.png')).convert('RGBA')).astype(np.float32)
    lum = logo[:, :, :3].mean(axis=2)
    a = smoothstep(60, 200, lum) * (logo[:, :, 3] / 255.0)
    # remove the white outside the black disc (corner background)
    h, w = a.shape
    yy, xx = np.mgrid[0:h, 0:w]
    disc = ((xx - w / 2) ** 2 + (yy - h / 2) ** 2) < (w * 0.47) ** 2
    a = a * disc
    cream = np.dstack([np.full((h, w), 250.0), np.full((h, w), 246.0), np.full((h, w), 228.0), a * 255])
    lock = trimmed(cream, 8)
    img = Image.fromarray(np.clip(lock, 0, 255).astype(np.uint8), 'RGBA')
    img = img.resize((img.width // 2, img.height // 2), Image.LANCZOS)
    save_png(img, 'zenith_logo_lockup', root=UI_OUT)
    # mark only (left circle)
    mark = cream[:, : int(w * 0.43)]
    mi = Image.fromarray(np.clip(trimmed(mark, 8), 0, 255).astype(np.uint8), 'RGBA')
    mi = mi.resize((mi.width // 2, mi.height // 2), Image.LANCZOS)
    save_png(mi, 'zenith_logo_mark', root=UI_OUT)
    return out


if __name__ == '__main__':
    out = build()
    tiles = list(out.items())
    W = sum(im.width for _, im in tiles) + 10 * len(tiles)
    H = max(im.height for _, im in tiles)
    sheet = Image.new('RGBA', (W, H), (60, 120, 90, 255))
    x = 0
    for n, im in tiles:
        sheet.alpha_composite(im, (x, 0)); x += im.width + 10
    sheet.save(SCRATCH + '/props_sheet_out.png')
    print({n: im.size for n, im in tiles})
