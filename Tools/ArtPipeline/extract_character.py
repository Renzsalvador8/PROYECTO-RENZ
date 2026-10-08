"""Cut Jean Paul Tester into a jointed cut-out rig from the provided turnaround sheet.

Source: Assets/References/ref_tester_turnaround_awards.jpg (figure 2 = side pose).
Outputs part images (later packed into the character atlas by build_character.py).
"""
import numpy as np
from scipy import ndimage
from PIL import Image
from common import *
from matte import key_region
import char_polys as P

SRC = 'ref_tester_turnaround_awards.jpg'
BOX = (255, 85, 415, 715)          # crop holding figure 2
BLAZER = np.array([102, 77, 50], np.float32)
TROUSER = np.array([34, 38, 37], np.float32)
INK_C = np.array([28, 20, 17], np.float32)


def local(poly):
    return [(x - BOX[0], y - BOX[1]) for x, y in poly]


def largest_component(alpha):
    lab, n = ndimage.label(alpha > 0.4)
    if n <= 1:
        return alpha
    sizes = ndimage.sum(np.ones_like(alpha), lab, range(1, n + 1))
    keep = np.argmax(sizes) + 1
    grown = ndimage.binary_dilation(lab == keep, iterations=3)
    return alpha * grown


def tweed_texture(h, w, seed=3, base=BLAZER, dark=0.0):
    """Procedural tweed: noise + fine diagonal herringbone, tuned to the reference blazer."""
    r = rng(seed)
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    band = np.sign(np.sin(xx * 2 * np.pi / 10.0))
    herring = np.sin((yy + band * xx) * 2 * np.pi / 3.6)
    n = ndimage.gaussian_filter(r.standard_normal((h, w)).astype(np.float32), 0.8)
    n2 = ndimage.gaussian_filter(r.standard_normal((h, w)).astype(np.float32), 6)
    v = 1.0 + 0.06 * herring + 0.10 * n + 0.10 * n2 - dark
    return np.clip(base[None, None, :] * v[:, :, None], 0, 255)


def extract():
    full = to_np(Image.open(ref(SRC)))
    keyed = key_region(full, BOX)
    alpha = largest_component(keyed[:, :, 3] / 255.0)
    rgb = keyed[:, :, :3].copy()
    H, W = alpha.shape
    size = (W, H)

    m = {name: poly_mask(size, [local(getattr(P, name))]) for name in
         ['HEAD', 'UPPER_ARM', 'FOREARM', 'HAND', 'THIGH', 'SHIN', 'SHOE', 'TORSO']}

    parts = {}

    def part(name, mask, rgb_override=None):
        a = alpha * mask
        out = np.dstack([rgb_override if rgb_override is not None else rgb, a * 255])
        parts[name] = out

    # --- head --------------------------------------------------------------------------
    blazerish = (np.linalg.norm(rgb - BLAZER, axis=2) < 48) & (rgb[:, :, 0] > 70)
    neck_zone = poly_mask(size, [local([(270, 180), (400, 180), (400, 230), (270, 230)])]) > 0.5
    head_kill = blazerish & neck_zone
    head_kill = ndimage.binary_dilation(head_kill, iterations=1)
    part('head', m['HEAD'])

    # --- arm ---------------------------------------------------------------------------
    part('upperarm', m['UPPER_ARM'])
    part('forearm', m['FOREARM'])
    hand_mask = m['HAND']
    # remove trouser pixels caught inside the hand polygon (dark green-grey, low red)
    trouserish = (rgb[:, :, 1] >= rgb[:, :, 0] - 4) & (rgb.mean(axis=2) < 90)
    blz = np.linalg.norm(rgb - BLAZER, axis=2) < 42
    kill = ndimage.binary_opening(trouserish | blz, iterations=1)
    ha = alpha * hand_mask * (1 - kill)
    lab, n = ndimage.label(ha > 0.3)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(ha), lab, range(1, n + 1))
        ha = ha * ndimage.binary_dilation(lab == (np.argmax(sizes) + 1), iterations=1)
    parts['hand'] = np.dstack([rgb, ha * 255])

    # --- torso: everything not head(above neck)/legs, with the arm hole inpainted -------
    arm_area = np.maximum.reduce([m['UPPER_ARM'], m['FOREARM'], m['HAND']])
    neck_band = poly_mask(size, [local([(294, 183), (342, 183), (347, 196), (349, 207), (300, 200), (292, 196)])])
    head_only = m['HEAD'] * (1 - neck_band)
    hem_cut = poly_mask(size, [local([(250, 80), (420, 80), (420, 437), (365, 438), (330, 436), (300, 437), (250, 437)])])
    torso_a = alpha * hem_cut * (1 - head_only)
    # where the arm was: fill with tweed shaded darker (arm casts shadow on the side panel)
    hole = (arm_area > 0.02) & (hem_cut > 0.02)
    hole_d = ndimage.binary_dilation(hole, iterations=1)
    tex = tweed_texture(H, W, seed=11, dark=0.22)
    # shading: darker toward the back (left), a little lighter toward the front
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    shade = np.clip((xx - (280 - BOX[0])) / 50.0, 0, 1)[:, :, None]
    tex = tex * (0.80 + 0.25 * shade)
    torso_rgb = rgb.copy()
    torso_rgb[hole_d] = tex[hole_d]
    # fill alpha inside the hole region (silhouette of torso = union of torso+arm silhouettes)
    sil = alpha * hem_cut
    torso_a = np.where(hole_d, np.maximum(torso_a, sil), torso_a)
    # hem bottom under the hand: the blazer hem continues where the hand covered it
    # redraw the back outline where the sleeve used to define the silhouette
    rows = range(220 - BOX[1], 436 - BOX[1])
    for y in rows:
        xs = np.nonzero(torso_a[y] > 0.5)[0]
        if len(xs) == 0:
            continue
        x0 = xs[0]
        for k in range(3):
            t = [1.0, 0.85, 0.35][k]
            torso_rgb[y, x0 + k] = torso_rgb[y, x0 + k] * (1 - t) + INK_C * t
    # hem line under the hand: draw the blazer hem edge across the hand region
    for x in range(316 - BOX[0], 356 - BOX[0]):
        col = torso_a[:, x]
        ys = np.nonzero(col > 0.5)[0]
        if len(ys) == 0:
            continue
        yb = ys[-1]
        for k in range(3):
            t = [1.0, 0.8, 0.3][k]
            torso_rgb[yb - k, x] = torso_rgb[yb - k, x] * (1 - t) + INK_C * t
    parts['torso'] = np.dstack([torso_rgb, torso_a * 255])

    # --- legs -------------------------------------------------------------------------
    leg_rgb = rgb.copy()
    leg_a = alpha.copy()
    clean_row = 476 - BOX[1]
    for y in range(408 - BOX[1], clean_row):
        leg_rgb[y] = rgb[clean_row]
        leg_a[y] = alpha[clean_row]
    parts['thigh'] = np.dstack([leg_rgb, leg_a * m['THIGH'] * 255])
    parts['shin'] = np.dstack([leg_rgb, leg_a * m['SHIN'] * 255])
    shoe_a = alpha * m['SHOE']
    lum = rgb.mean(axis=2)
    sat = rgb.max(axis=2) - rgb.min(axis=2)
    shadow = (lum > 140) & (sat < 30)
    shoe_a[shadow] = 0
    parts['shoe'] = np.dstack([rgb, shoe_a * 255])
    return parts


if __name__ == '__main__':
    import sys
    parts = extract()
    from matte import composite_check
    out = SCRATCH
    W = max(p.shape[1] for p in parts.values())
    for name, p in parts.items():
        composite_check(p, (90, 160, 110)).save(f'{out}/part_{name}.png')
    print('parts:', list(parts))
