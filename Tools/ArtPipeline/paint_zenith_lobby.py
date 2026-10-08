"""Zenith Studio lobby, built from the client's concept painting (Assets/References/ref_zenith_office.jpg).

The painting is a frontal, one-point-perspective view of the studio at night. It becomes the backdrop of
the final level; Jean Paul walks along a line on its floor (WALK_Y) in front of the furniture:

  * the black letterbox bars are cropped and the ceiling is extended upwards so a 16:9 view fits;
  * the two painted pedestals (behind the sofa) are painted out: the real awards stand on pedestals in the
    walking plane, where he can reach them;
  * the round wall sign is redrawn crisply with the supplied cream "Z." mark;
  * the crates and filing cabinet at the bottom right are cut out as a foreground layer, so he enters the
    room from behind them;
  * a separate close crop (depth-of-field blurred) is the backdrop of the front-facing finale.

World mapping (see levels.zenith): 1 world unit = ORIG_PPU source pixels at the walking line.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from common import *
from env_kit import *
import logos

SRC = 'ref_zenith_office.jpg'
CROP_Y0, CROP_Y1 = 60, 716     # painted area inside the black bars (source rows)
CEIL_EXT = 118                 # source rows of ceiling added on top ((656 + 118) * UP = 1152, a multiple of 4)
UP = 64 / 43                   # texture scale vs. source pixels: 1376 -> 2048 (the importer's max size)
ORIG_PPU = 104.0               # source px per world unit at the walking line (Jean Paul = 2.4 u = 250 px)
PPU = ORIG_PPU * UP
WALK_Y = 640                   # source row of Jean Paul's feet
CENTER_X = 688                 # source column at world x = 0
SIGN_C = (801.0, 343.2)        # wall sign centre (source px) and radius of its dark disc
SIGN_R = 60.5
PEDESTALS = [(350, 403, 421, 490), (449, 403, 519, 490)]   # painted pedestals, objects and shadows (x0,y0,x1,y1)

# Foreground pieces at the bottom right (source px). Base rows are below WALK_Y, so they are in front of him.
FG_POLYS = {
    'crate_a': [(1030.7, 716), (1030.7, 653.3), (1051.7, 648.3), (1055.0, 636.7), (1060.0, 624.0), (1080.0, 620.0),
                (1113.3, 620.7), (1128.3, 626.7), (1130.7, 636.7), (1133.3, 648.3), (1156.7, 661.7), (1161.7, 668.3),
                (1161.7, 716)],
    'crate_b': [(1135.0, 716), (1135.0, 618.3), (1176.7, 615.0), (1176.7, 593.3), (1193.3, 586.7), (1233.3, 586.7),
                (1243.3, 591.7), (1251.7, 605.0), (1253.3, 613.3), (1248.3, 626.7), (1285.0, 636.7), (1285.0, 716)],
    'cabinet': [(1255.0, 716), (1255.0, 550.0), (1266.7, 546.7), (1376.0, 546.7), (1376.0, 716)],
}


def world_x(sx):
    return (sx - CENTER_X) / ORIG_PPU


def world_y(sy, ground_y=-3.5):
    return ground_y + (WALK_Y - sy) / ORIG_PPU


def tex_xy(sx, sy):
    """Source px -> texture px of the processed backdrop."""
    return sx * UP, (sy - CROP_Y0 + CEIL_EXT) * UP


def _load():
    im = Image.open(ref(SRC)).convert('RGB')
    return np.asarray(im).astype(np.float32)


def _harmonic_fill(a, mask, fixed_below=False, iters=900):
    """Fill masked pixels by solving Laplace's equation (smooth interpolation from the surroundings).
    Pixels directly below the hole are treated as a free (Neumann) edge so the sofa does not bleed upwards."""
    out = a.copy()
    ys, xs = np.where(mask)
    y0, y1, x0, x1 = ys.min() - 1, ys.max() + 2, xs.min() - 1, xs.max() + 2
    sub = out[y0:y1, x0:x1].copy()
    m = mask[y0:y1, x0:x1]
    # initial guess: row-wise linear interpolation between left/right known pixels
    for r in range(sub.shape[0]):
        row_m = m[r]
        if not row_m.any():
            continue
        known = np.where(~row_m)[0]
        for c in range(3):
            sub[r, row_m, c] = np.interp(np.where(row_m)[0], known, sub[r, known, c])
    below_free = np.zeros_like(m)
    below_free[:-1] = m[:-1] & ~m[1:]          # last hole row of each column: mirror instead of reading below
    for _ in range(iters):
        up = np.roll(sub, 1, 0)
        dn = np.roll(sub, -1, 0)
        dn[below_free] = sub[below_free]
        lf = np.roll(sub, 1, 1)
        rt = np.roll(sub, -1, 1)
        avg = (up + dn + lf + rt) * 0.25
        sub[m] = avg[m]
    out[y0:y1, x0:x1] = sub
    return out


def _texture_from(a, box, shape, seed):
    """High-frequency texture (paint grain) borrowed from a clean wall patch, tiled to `shape`."""
    x0, y0, x1, y1 = box
    patch = a[y0:y1, x0:x1]
    blur = np.asarray(Image.fromarray(np.clip(patch, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))).astype(np.float32)
    hf = patch - blur
    r = np.random.default_rng(seed)
    h, w = shape
    reps_y = h // hf.shape[0] + 2
    reps_x = w // hf.shape[1] + 2
    tiled = np.tile(hf, (reps_y, reps_x, 1))
    oy, ox = r.integers(0, hf.shape[0]), r.integers(0, hf.shape[1])
    return tiled[oy:oy + h, ox:ox + w]


def remove_pedestals(a):
    mask = np.zeros(a.shape[:2], bool)
    for x0, y0, x1, y1 in PEDESTALS:
        mask[y0:y1, x0:x1] = True
    filled = _harmonic_fill(a, mask)
    tex = _texture_from(a, (404, 300, 446, 398), a.shape[:2], seed=5)
    soft = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.2))).astype(np.float32) / 255
    filled = filled + tex * 0.9 * soft[..., None]
    return a * (1 - soft[..., None]) + filled * soft[..., None]


def extend_ceiling(a, ext):
    """Adds `ext` rows above: the ceiling plane continues, slightly darker, with the same grain."""
    h, w, _ = a.shape
    top = a[:24].mean(axis=0)                                   # per-column ceiling colour
    top = np.asarray(Image.fromarray(np.clip(top[None], 0, 255).astype(np.uint8)).resize((w, 1)).filter(
        ImageFilter.GaussianBlur(6))).astype(np.float32)[0]
    rows = []
    for i in range(ext):
        k = 1.0 - (ext - i) / ext                               # 0 at the new top, 1 at the old top
        shade = 0.72 + 0.28 * k
        rows.append(top * shade)
    ext_img = np.stack(rows, 0)
    ext_img += _texture_from(a, (300, 0, 460, 30), (ext, w), seed=9) * 0.8
    out = np.concatenate([ext_img, a], 0)
    # soften the seam
    seam = ext
    for d in range(-6, 7):
        r = seam + d
        wgt = 1 - abs(d) / 7
        out[r] = out[r] * (1 - wgt * 0.5) + (out[r - 1] + out[r + 1]) * 0.25 * wgt
    return out


def draw_sign(img, cx, cy, r, blur=0.0):
    """The wall sign: black disc, cream Z. mark and 'Zenith Studio' lettering (texture px coords)."""
    S = 4
    size = int(r * 2.6)
    cv = Canvas(size * S // 2, size * S // 2)
    k = S / 2
    c = size * S / 4
    R = r * k
    cv.ellipse(c, c, R, R, (16, 18, 18), shader=None)
    cv.ellipse(c - R * 0.15, c - R * 0.2, R * 0.92, R * 0.92, (32, 34, 33), alpha=0.35, blur=R * 0.25)
    mark = logos.mark('zenith', R * 0.66, (250, 248, 232))
    cv.image(mark, c - R * 0.50 - mark.width / 2, c - mark.height / 2 - R * 0.02, mark.width, mark.height)
    import skia
    tf = skia.Typeface.MakeFromFile(FONTS + '/Jost-SemiBold.ttf')
    fs = R * 0.86 / (skia.Font(tf, 100).measureText('Zenith') / 100)     # 'Zenith' spans 0.86 R
    cv.text('Zenith', c - R * 0.08, c - R * 0.03, fs, (244, 242, 236), 'Jost-SemiBold.ttf')
    cv.text('Studio', c - R * 0.08, c + R * 0.31, fs, (244, 242, 236), 'Jost-SemiBold.ttf')
    sign = cv.np()
    sign = Image.fromarray(np.clip(sign, 0, 255).astype(np.uint8), 'RGBA').resize((size, size), Image.LANCZOS)
    if blur > 0:
        sign = sign.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(sign, (int(round(cx - size / 2)), int(round(cy - size / 2))))
    return img


def backdrop():
    """Returns (RGBA backdrop texture, processed float RGB at source scale with ceiling)."""
    a = _load()
    a = remove_pedestals(a)
    a = a[CROP_Y0:CROP_Y1]
    a = extend_ceiling(a, CEIL_EXT)
    h, w, _ = a.shape
    big = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB').resize((int(w * UP), int(h * UP)), Image.LANCZOS)
    big = big.filter(ImageFilter.UnsharpMask(radius=1.6, percent=60, threshold=2)).convert('RGBA')
    sx, sy = tex_xy(*SIGN_C)
    draw_sign(big, sx, sy, (SIGN_R + 0.8) * UP)
    return big, a


def foreground_offset():
    """Texture px (x0, bottom) of the foreground piece inside the backdrop (recomputed from the polygons)."""
    xs = [tex_xy(x, y)[0] for pts in FG_POLYS.values() for x, y in pts]
    x0 = int(math.floor(min(xs) - 2))
    return x0 - x0 % 4, int(round((CROP_Y1 - CROP_Y0 + CEIL_EXT) * UP))


def foreground(big):
    """Cut the bottom-right crates and cabinet out of the processed backdrop (same size, transparent elsewhere)."""
    W, H = big.size
    m = Image.new('L', (W * 2, H * 2), 0)
    d = ImageDraw.Draw(m)
    for pts in FG_POLYS.values():
        d.polygon([(tex_xy(x, y)[0] * 2, tex_xy(x, y)[1] * 2) for x, y in pts], fill=255)
    m = m.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.8))
    fg = big.copy()
    fg.putalpha(m)
    # crop to the pieces (keeps the texture small); the crop's bottom-left corner is foreground_offset()
    x0, y1 = foreground_offset()
    top = m.getbbox()[1]
    w4 = (W - x0 + 3) // 4 * 4
    h4 = (y1 - top + 3) // 4 * 4
    piece = Image.new('RGBA', (w4, h4), (0, 0, 0, 0))
    piece.alpha_composite(fg.crop((x0, y1 - h4, W, y1)), (0, 0))
    return piece, (x0, y1)


def sign_glow(size=512):
    """Warm halo behind the sign; pulsed at runtime."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
    a = np.clip(1 - r, 0, 1) ** 2.2
    ring = np.exp(-((r - 0.42) / 0.08) ** 2) * 0.6
    alpha = np.clip(a * 0.55 + ring * (r > 0.38), 0, 1)
    out = np.zeros((size, size, 4), np.float32)
    out[..., 0], out[..., 1], out[..., 2] = 255, 226, 176
    out[..., 3] = alpha * 255
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


HALO_INNER = 0.42       # disc radius as a fraction of the halo sprite's half-size


def sign_halo(size=512):
    """Back-light halo around the wall sign for the runtime pulse: clear over the disc, soft outside it."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.hypot(xx - size / 2, yy - size / 2) / (size / 2)
    inner = smoothstep(HALO_INNER - 0.005, HALO_INNER + 0.02, r)
    fall = np.clip((1 - r) / (1 - HALO_INNER), 0, 1) ** 2.4
    alpha = inner * fall * 0.85
    out = np.zeros((size, size, 4), np.float32)
    out[..., 0], out[..., 1], out[..., 2] = 255, 228, 182
    out[..., 3] = alpha * 255
    return Image.fromarray(out.astype(np.uint8), 'RGBA')


def pedestal_concrete(w=300, h=420, seed=81):
    """Display pedestal in the painting's concrete (matches the reception desk)."""
    cv = Canvas(w, h)
    cv.ellipse(w / 2, h - 10, w * 0.48, 15, (0, 0, 0), alpha=0.55, blur=7)
    cv.poly([(34, 46), (w - 34, 46), (w - 38, h - 14), (38, h - 14)], (110, 120, 118), outline=2.0,
            shader=lin_grad((34, 0), (w - 34, 0), [(150, 160, 156), (118, 128, 126), (78, 88, 88)]))
    cv.poly([(26, 28), (w - 26, 28), (w - 34, 48), (34, 48)], (170, 176, 170), outline=1.8,
            shader=lin_grad((0, 28), (0, 48), [(196, 198, 190), (130, 138, 134)]))
    r = np.random.default_rng(seed)
    for _ in range(26):
        x, y = r.uniform(50, w - 50), r.uniform(70, h - 40)
        cv.ellipse(x, y, r.uniform(1.5, 4), r.uniform(1.0, 3), (70, 78, 78), alpha=0.35)
    cv.rect(38, h - 70, w - 76, 56, (0, 0, 0), alpha=0.18, blur=10)
    cv.rect(w / 2 - 70, h / 2 - 20, 140, 36, (230, 200, 160), alpha=0.10, blur=8)
    return cv.finish(texture=1.0, seed=seed, grain=0.05, mottling=0.08)


FINALE = {'ppu': 200.0, 'size': (1600, 1000), 'center_y': -2.6, 'room_scale': 0.78, 'sign': (1.15, -2.42)}


def finale_backdrop(a):
    """Close, defocused view of the room for the front-facing finale (placed at stage + (0, center_y), pivot
    centre, FINALE['ppu']). The room is shown at room_scale of its walking-line scale (it is further behind
    him) and the sign sits to his left (screen right) at head height, clear of the trophies."""
    out_w, out_h = FINALE['size']
    ppu = FINALE['ppu']
    scale = ppu * FINALE['room_scale'] / ORIG_PPU          # output px per source px
    sx, sy = SIGN_C
    ox = out_w / 2 + FINALE['sign'][0] * ppu
    oy = out_h / 2 - (FINALE['sign'][1] - FINALE['center_y']) * ppu
    src_x0 = sx - ox / scale
    src_y0 = (sy - CROP_Y0 + CEIL_EXT) - oy / scale
    src = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGB')
    crop = src.transform((out_w, out_h), Image.AFFINE, (1 / scale, 0, src_x0, 0, 1 / scale, src_y0),
                         resample=Image.BICUBIC)
    crop = crop.filter(ImageFilter.GaussianBlur(5.0)).convert('RGBA')
    arr = np.asarray(crop).astype(np.float32)
    yy, xx = np.mgrid[0:out_h, 0:out_w].astype(np.float32)
    vig = 1 - 0.35 * np.clip(np.hypot((xx - out_w / 2) / (out_w * 0.6), (yy - out_h / 2) / (out_h * 0.7)), 0, 1) ** 2
    arr[..., :3] *= (0.82 * vig)[..., None]
    crop = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), 'RGBA')
    glow = sign_glow(int(SIGN_R * scale * 3.4))
    crop.alpha_composite(glow, (int(ox - glow.width / 2), int(oy - glow.height / 2)))
    draw_sign(crop, ox, oy, (SIGN_R + 0.8) * scale, blur=1.4)
    return crop


def build():
    out = {}
    big, a = backdrop()
    out['lobby'] = big
    piece, (fx0, fy1) = foreground(big)
    out['lobby_fg'] = piece
    out['sign_halo'] = sign_halo()
    out['pedestal_concrete'] = pedestal_concrete()
    out['finale_backdrop'] = finale_backdrop(a)
    for k, v in out.items():
        save_png(v, 'Zenith/' + k)
    meta = {
        'ppu': PPU, 'size': big.size, 'fg_offset_px': [fx0, fy1], 'fg_size': piece.size,
        'world_left': world_x(0), 'world_bottom': world_y(CROP_Y1), 'world_top': world_y(CROP_Y0 - CEIL_EXT),
        'sign': [world_x(SIGN_C[0]), world_y(SIGN_C[1])], 'sign_r': SIGN_R / ORIG_PPU,
    }
    return out, meta


if __name__ == '__main__':
    out, meta = build()
    print({k: v.size for k, v in out.items()})
    print(meta)
