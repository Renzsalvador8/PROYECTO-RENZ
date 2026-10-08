"""Front-facing Jean Paul Tester holding both awards (figure 6 of the turnaround sheet).

Produces a static body + a separate head with expression variants (liquify warps), used for the
awards finale close-up and for the 'looks at the camera' beat at the end of the test drive.
"""
import numpy as np
from scipy import ndimage
from PIL import Image
from common import *
from matte import key_region
from atlas import pack

SRC = 'ref_tester_turnaround_awards.jpg'
BOX = (1138, 85, 1376, 715)
NECK = (1262, 206)
GROUND_Y = 698.0
ROOT_X = 1255.0
PPU = 250.0


def L(poly):
    return [(x - BOX[0], y - BOX[1]) for x, y in poly]


HEAD = [(1205, 90), (1320, 90), (1320, 180), (1300, 186), (1291, 196), (1277, 203), (1262, 207), (1248, 204),
        (1235, 197), (1226, 188), (1205, 182)]
NEIGHBOUR = [(1138, 85), (1157, 85), (1157, 240), (1138, 240)]
NECK_BAND = [(1230, 184), (1294, 184), (1296, 222), (1228, 222)]


def liquify(rgba, blobs):
    """blobs: list of (cx, cy, dx, dy, sigma) in crop px. Moves content by (dx,dy) near centres."""
    h, w = rgba.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    DX = np.zeros((h, w), np.float32)
    DY = np.zeros((h, w), np.float32)
    for cx, cy, dx, dy, s in blobs:
        g = np.exp(-((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * s * s))
        DX += g * dx
        DY += g * dy
    out = np.empty_like(rgba)
    for c in range(4):
        out[:, :, c] = ndimage.map_coordinates(rgba[:, :, c], [yy - DY, xx - DX], order=1, mode='nearest')
    return out


def P(x, y):
    return (x - BOX[0], y - BOX[1])


def head_variants(head):
    lb, rb = P(1251, 147), P(1277, 147)        # brows (viewer's left / right)
    le, re = P(1251, 155), P(1277, 155)        # eyes
    ml, mr = P(1249, 180), P(1281, 180)        # moustache corners
    mo = P(1265, 187)                          # mouth centre
    v = {'neutral': head}
    v['brow_one'] = liquify(head, [(rb[0], rb[1], 0, -3.2, 5.0), (rb[0] + 5, rb[1] - 1, 0.6, -1.0, 4),
                                    (lb[0], lb[1] + 1, 0, 0.8, 4.0)])
    v['brows_up'] = liquify(head, [(lb[0], lb[1], 0, -2.6, 5.0), (rb[0], rb[1], 0, -2.6, 5.0)])
    v['smile'] = liquify(head, [(ml[0], ml[1], -0.6, -1.6, 3.2), (mr[0], mr[1], 0.6, -1.6, 3.2),
                                (mo[0] - 7, mo[1], 0, -1.2, 3), (mo[0] + 7, mo[1], 0, -1.2, 3),
                                (le[0], le[1] + 3, 0, -0.8, 3), (re[0], re[1] + 3, 0, -0.8, 3)])
    v['smile_brow'] = liquify(v['smile'], [(rb[0], rb[1], 0, -2.6, 5.0)])
    v['look_l'] = liquify(head, [(le[0], le[1], -1.6, 0.2, 2.2), (re[0], re[1], -1.6, 0.2, 2.2)])
    v['look_r'] = liquify(head, [(le[0], le[1], 1.6, 0.2, 2.2), (re[0], re[1], 1.6, 0.2, 2.2)])
    v['look_dl'] = liquify(head, [(le[0], le[1], -1.4, 1.0, 2.2), (re[0], re[1], -1.4, 1.0, 2.2),
                                  (lb[0], lb[1], 0, 0.8, 4), (rb[0], rb[1], 0, 0.8, 4)])
    v['look_dr'] = liquify(head, [(le[0], le[1], 1.4, 1.0, 2.2), (re[0], re[1], 1.4, 1.0, 2.2),
                                  (lb[0], lb[1], 0, 0.8, 4), (rb[0], rb[1], 0, 0.8, 4)])
    v['frown'] = liquify(head, [(lb[0] + 4, lb[1], 0.8, 1.6, 4.0), (rb[0] - 4, rb[1], -0.8, 1.6, 4.0),
                                (ml[0], ml[1], 0, 0.8, 3), (mr[0], mr[1], 0, 0.8, 3)])
    # blink: pull the upper lids down over the eyes (liquify), then darken the closed lash line
    bl = liquify(head, [(le[0], le[1] - 3.5, 0, 3.6, 2.6), (re[0], re[1] - 3.5, 0, 3.6, 2.6),
                        (le[0] - 4, le[1] - 3, 0, 2.4, 2.2), (re[0] + 4, re[1] - 3, 0, 2.4, 2.2),
                        (le[0] + 4, le[1] - 3, 0, 2.4, 2.2), (re[0] - 4, re[1] - 3, 0, 2.4, 2.2)])
    v['blink'] = bl
    return v


def extract():
    full = to_np(Image.open(ref(SRC)))
    keyed = key_region(full, BOX)
    rgb = keyed[:, :, :3]
    alpha = keyed[:, :, 3] / 255.0
    h, w = alpha.shape
    alpha = alpha * (1 - poly_mask((w, h), [L(NEIGHBOUR)]))
    lab, n = ndimage.label(alpha > 0.4)
    sizes = ndimage.sum(np.ones_like(alpha), lab, range(1, n + 1))
    alpha = alpha * ndimage.binary_dilation(lab == (np.argmax(sizes) + 1), iterations=3)
    # remove floor shadow (light grey, low saturation) near the feet
    lum, sat = rgb.mean(axis=2), rgb.max(axis=2) - rgb.min(axis=2)
    feet = np.zeros_like(alpha, bool); feet[640 - BOX[1]:, :] = True
    alpha[feet & (lum > 140) & (sat < 30)] = 0

    hm = poly_mask((w, h), [L(HEAD)])
    head = np.dstack([rgb, alpha * hm * 255])
    body_a = alpha * (1 - hm)
    band = poly_mask((w, h), [L(NECK_BAND)]) > 0.5
    # neck band: keep turtleneck behind the chin, replacing any skin with turtleneck black
    body_rgb = rgb.copy()
    skinish = band & (rgb[:, :, 0] > 140) & (rgb[:, :, 0] - rgb[:, :, 2] > 35) & (rgb.mean(axis=2) > 120)
    tn = np.median(rgb[band & (lum < 50)].reshape(-1, 3), axis=0)
    body_rgb[skinish] = tn + ndimage.gaussian_filter(np.random.default_rng(2).standard_normal((h, w)), 1)[skinish][:, None] * 3
    body_a = np.where(band & (alpha > 0.5), 1.0, body_a)
    body = np.dstack([body_rgb, body_a * 255])
    return head, body


def crop(arr, pad=3):
    a = arr[:, :, 3]
    ys, xs = np.nonzero(a > 1)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, arr.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, arr.shape[1])
    return arr[y0:y1, x0:x1], (x0, y0)


def build():
    head, body = extract()
    variants = head_variants(head)
    images, pivots = {}, {}
    hc, (hx, hy) = crop(head, pad=6)
    for name, arr in variants.items():
        c = arr[hy:hy + hc.shape[0], hx:hx + hc.shape[1]]
        images['head_' + name] = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8), 'RGBA')
        pivots['head_' + name] = (NECK[0] - BOX[0] - hx, NECK[1] - BOX[1] - hy)
    bc, (bx, by) = crop(body)
    images['body'] = Image.fromarray(np.clip(bc, 0, 255).astype(np.uint8), 'RGBA')
    pivots['body'] = (ROOT_X - BOX[0] - bx, GROUND_Y - BOX[1] - by)
    atlas, rects = pack(images, pad=6, max_w=1024)
    save_png(atlas, 'Character/tester_front_atlas')
    sprites = {}
    for name, (x, y, w_, h_) in rects.items():
        px, py = pivots[name]
        sprites[name] = {'rect': [x, y, w_, h_], 'pivot': [round(px / w_, 5), round(1 - py / h_, 5)]}
    neck_u = [round((NECK[0] - ROOT_X) / PPU, 5), round((GROUND_Y - NECK[1]) / PPU, 5)]
    rig = {'name': 'tester_front', 'ppu': PPU, 'atlas': 'Art/Character/tester_front_atlas',
           'atlasSize': [atlas.width, atlas.height], 'sprites': sprites,
           'bones': [{'name': 'root', 'parent': '', 'pos': [0, 0]},
                     {'name': 'body', 'parent': 'root', 'pos': [0, 0]},
                     {'name': 'head', 'parent': 'body', 'pos': neck_u}],
           'slots': [{'name': 'body', 'bone': 'body', 'sprite': 'body', 'order': 0, 'tint': [1, 1, 1, 1]},
                     {'name': 'head', 'bone': 'head', 'sprite': 'head_neutral', 'order': 10, 'tint': [1, 1, 1, 1]}]}
    save_json(rig, 'Rigs/tester_front')
    return rig, atlas, images


if __name__ == '__main__':
    rig, atlas, images = build()
    print('front atlas', atlas.size)
    names = [n for n in images if n.startswith('head_')]
    tiles = [images[n].resize((images[n].width * 3, images[n].height * 3), Image.LANCZOS) for n in names]
    W = sum(t.width for t in tiles)
    sheet = Image.new('RGBA', (W, tiles[0].height), (214, 203, 192, 255))
    x = 0
    for t in tiles:
        sheet.alpha_composite(t, (x, 0)); x += t.width
    sheet.save(SCRATCH + '/front_heads.png')
    b = images['body']
    bg = Image.new('RGBA', b.size, (214, 203, 192, 255)); bg.alpha_composite(b); bg.save(SCRATCH + '/front_body.png')
