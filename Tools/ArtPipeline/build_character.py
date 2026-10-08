"""Builds the side-view cut-out rig of Jean Paul Tester: atlas + rig JSON."""
import numpy as np
from scipy import ndimage
from PIL import Image
from common import *
from extract_character import extract, BOX
from props_painted import magnifier
from atlas import pack
import char_polys as P

PPU = 250.0  # source pixels per world unit (character ~2.4 units tall)
SKIN = np.array([222, 178, 146], np.float32)


def crop_part(arr, pad=3):
    a = arr[:, :, 3]
    ys, xs = np.nonzero(a > 1)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad + 1, arr.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad + 1, arr.shape[1])
    return arr[y0:y1, x0:x1], (x0, y0)


def split_face(head):
    """Separate eyebrow and moustache so they can be animated. Returns head, brow, stache arrays (same size)."""
    h = head.copy()
    rgb = h[:, :, :3]
    lum = rgb.mean(axis=2)
    ox, oy = BOX[0], BOX[1]

    def region(x0, y0, x1, y1):
        m = np.zeros(lum.shape, bool)
        m[y0 - oy:y1 - oy, x0 - ox:x1 - ox] = True
        return m

    brow_m = region(345, 140, 367, 148) & (lum < 150)
    brow_m = ndimage.binary_dilation(brow_m, iterations=1) & region(344, 139, 368, 149)
    st_m = region(350, 164, 374, 181) & (lum < 135) & (rgb[:, :, 0] > rgb[:, :, 2] + 8)
    st_m = ndimage.binary_closing(st_m, iterations=1)
    st_m = ndimage.binary_dilation(st_m, iterations=1) & region(349, 163, 375, 182)

    brow = np.zeros_like(h); brow[brow_m] = h[brow_m]
    st = np.zeros_like(h); st[st_m] = h[st_m]
    # soften cut edges
    for arr, m in ((brow, brow_m), (st, st_m)):
        soft = ndimage.gaussian_filter(m.astype(np.float32), 0.6)
        arr[:, :, 3] = np.minimum(h[:, :, 3], soft * 255) * (m | (soft > 0.2))

    # fill the holes on the head with skin sampled around them
    def fill_hole(m, sample_m):
        samp = rgb[sample_m & ~m]
        col = np.median(samp, axis=0) if len(samp) else SKIN
        noise = ndimage.gaussian_filter(np.random.default_rng(5).standard_normal(lum.shape), 1.0)[:, :, None] * 6
        rgb[m] = (col + noise[m])
    fill_hole(brow_m, region(344, 136, 368, 152))
    lip_m = st_m.copy()
    fill_hole(st_m, region(348, 160, 376, 186))
    # a faint lip line under the moustache so a lifted moustache reveals a mouth
    for x in range(357, 371):
        y = 178 - oy - int((x - 357) * 0.15)
        xx = x - ox
        if st_m[y, xx]:
            rgb[y, xx] = rgb[y, xx] * 0.55 + np.array([110, 60, 50]) * 0.45
    h[:, :, :3] = rgb
    return h, brow, st


def build():
    parts = extract()
    head, brow, stache = split_face(parts['head'])
    parts['head'] = head
    parts['brow'] = brow
    parts['stache'] = stache

    # pivots in figure-crop coordinates
    piv = {k: (x - BOX[0], y - BOX[1]) for k, (x, y) in P.PIVOTS.items()}
    part_pivot = {
        'head': piv['neck'], 'brow': (356 - BOX[0], 145 - BOX[1]), 'stache': (362 - BOX[0], 172 - BOX[1]),
        'torso': piv['hip'], 'upperarm': piv['shoulder'], 'forearm': piv['elbow'], 'hand': piv['wrist'],
        'thigh': piv['hip'], 'shin': piv['knee'], 'shoe': piv['ankle'],
    }
    images, pivots = {}, {}
    for name, arr in parts.items():
        c, (x0, y0) = crop_part(arr)
        images[name] = Image.fromarray(np.clip(c, 0, 255).astype(np.uint8), 'RGBA')
        px, py = part_pivot[name]
        pivots[name] = (px - x0, py - y0)

    # props
    mag, grip, lc, lr = magnifier(0.85)
    images['magnifier'] = mag
    pivots['magnifier'] = grip
    magbig, gripb, lcb, lrb = magnifier(1.7)
    images['magnifier_big'] = magbig
    pivots['magnifier_big'] = gripb

    atlas, rects = pack(images, pad=8, max_w=1024)
    save_png(atlas, 'Character/tester_side_atlas')

    sprites = {}
    for name, (x, y, w, h) in rects.items():
        px, py = pivots[name]
        sprites[name] = {'rect': [x, y, w, h], 'pivot': [round(px / w, 5), round(1 - py / h, 5)]}

    def U(p):  # figure px -> units relative to root (feet centre on ground)
        return [round((p[0] - (P.ROOT_X - BOX[0])) / PPU, 5), round(((P.GROUND_Y - BOX[1]) - p[1]) / PPU, 5)]

    def rel(child, parent):
        a, b = U(child), U(parent)
        return [round(a[0] - b[0], 5), round(a[1] - b[1], 5)]

    O = (P.ROOT_X - BOX[0], P.GROUND_Y - BOX[1])
    hip, neck, sh, el, wr, kn, an = piv['hip'], piv['neck'], piv['shoulder'], piv['elbow'], piv['wrist'], piv['knee'], piv['ankle']
    grip_hand = (336 - BOX[0], 448 - BOX[1])
    back = (3, 0)
    bones = [
        {'name': 'root', 'parent': '', 'pos': [0, 0]},
        {'name': 'hip', 'parent': 'root', 'pos': rel(hip, O)},
        {'name': 'torso', 'parent': 'hip', 'pos': [0, 0]},
        {'name': 'head', 'parent': 'torso', 'pos': rel(neck, hip)},
        {'name': 'brow', 'parent': 'head', 'pos': rel(part_pivot['brow'], neck)},
        {'name': 'stache', 'parent': 'head', 'pos': rel(part_pivot['stache'], neck)},
        {'name': 'shoulder_f', 'parent': 'torso', 'pos': rel(sh, hip)},
        {'name': 'elbow_f', 'parent': 'shoulder_f', 'pos': rel(el, sh)},
        {'name': 'wrist_f', 'parent': 'elbow_f', 'pos': rel(wr, el)},
        {'name': 'prop_f', 'parent': 'wrist_f', 'pos': rel(grip_hand, wr), 'rot': 180},
        {'name': 'shoulder_b', 'parent': 'torso', 'pos': rel((sh[0] + back[0], sh[1] + back[1]), hip)},
        {'name': 'elbow_b', 'parent': 'shoulder_b', 'pos': rel(el, sh)},
        {'name': 'wrist_b', 'parent': 'elbow_b', 'pos': rel(wr, el)},
        {'name': 'prop_b', 'parent': 'wrist_b', 'pos': rel(grip_hand, wr), 'rot': 180},
        {'name': 'thigh_f', 'parent': 'hip', 'pos': [0, 0]},
        {'name': 'knee_f', 'parent': 'thigh_f', 'pos': rel(kn, hip)},
        {'name': 'ankle_f', 'parent': 'knee_f', 'pos': rel(an, kn)},
        {'name': 'thigh_b', 'parent': 'hip', 'pos': [round(4 / PPU, 5), 0]},
        {'name': 'knee_b', 'parent': 'thigh_b', 'pos': rel(kn, hip)},
        {'name': 'ankle_b', 'parent': 'knee_b', 'pos': rel(an, kn)},
    ]
    FAR = [0.62, 0.62, 0.68, 1.0]
    slots = [
        {'name': 'hand_b', 'bone': 'wrist_b', 'sprite': 'hand', 'order': 10, 'tint': FAR},
        {'name': 'prop_b', 'bone': 'prop_b', 'sprite': '', 'order': 9, 'tint': [1, 1, 1, 1], 'hidden': 1},
        {'name': 'forearm_b', 'bone': 'elbow_b', 'sprite': 'forearm', 'order': 20, 'tint': FAR},
        {'name': 'upperarm_b', 'bone': 'shoulder_b', 'sprite': 'upperarm', 'order': 30, 'tint': FAR},
        {'name': 'shoe_b', 'bone': 'ankle_b', 'sprite': 'shoe', 'order': 40, 'tint': FAR},
        {'name': 'shin_b', 'bone': 'knee_b', 'sprite': 'shin', 'order': 50, 'tint': FAR},
        {'name': 'thigh_b', 'bone': 'thigh_b', 'sprite': 'thigh', 'order': 60, 'tint': FAR},
        {'name': 'shoe_f', 'bone': 'ankle_f', 'sprite': 'shoe', 'order': 70, 'tint': [1, 1, 1, 1]},
        {'name': 'shin_f', 'bone': 'knee_f', 'sprite': 'shin', 'order': 80, 'tint': [1, 1, 1, 1]},
        {'name': 'thigh_f', 'bone': 'thigh_f', 'sprite': 'thigh', 'order': 90, 'tint': [1, 1, 1, 1]},
        {'name': 'torso', 'bone': 'torso', 'sprite': 'torso', 'order': 100, 'tint': [1, 1, 1, 1]},
        {'name': 'head', 'bone': 'head', 'sprite': 'head', 'order': 110, 'tint': [1, 1, 1, 1]},
        {'name': 'brow', 'bone': 'brow', 'sprite': 'brow', 'order': 111, 'tint': [1, 1, 1, 1]},
        {'name': 'stache', 'bone': 'stache', 'sprite': 'stache', 'order': 112, 'tint': [1, 1, 1, 1]},
        {'name': 'prop_f', 'bone': 'prop_f', 'sprite': '', 'order': 119, 'tint': [1, 1, 1, 1], 'hidden': 1},
        {'name': 'hand_f', 'bone': 'wrist_f', 'sprite': 'hand', 'order': 120, 'tint': [1, 1, 1, 1]},
        {'name': 'forearm_f', 'bone': 'elbow_f', 'sprite': 'forearm', 'order': 130, 'tint': [1, 1, 1, 1]},
        {'name': 'upperarm_f', 'bone': 'shoulder_f', 'sprite': 'upperarm', 'order': 140, 'tint': [1, 1, 1, 1]},
    ]
    rig = {'name': 'tester_side', 'ppu': PPU, 'atlas': 'Art/Character/tester_side_atlas',
           'atlasSize': [atlas.width, atlas.height], 'sprites': sprites, 'bones': bones, 'slots': slots}
    save_json(rig, 'Rigs/tester_side')
    return rig, atlas


if __name__ == '__main__':
    rig, atlas = build()
    print('atlas', atlas.size, 'sprites', list(rig['sprites']))
