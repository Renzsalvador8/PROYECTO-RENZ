"""Shared helpers for The Tester art pipeline.

All game art is produced by the scripts in this folder. Run `python3 build_all.py`
from this directory to regenerate every texture in Assets/TheTesterGame/Art/Resources/Art.
"""
import os, json, math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
REFS = os.path.join(ROOT, 'Assets', 'References')
GAME = os.path.join(ROOT, 'Assets', 'TheTesterGame')
ART_OUT = os.path.join(GAME, 'Art', 'Resources', 'Art')
DATA_OUT = os.path.join(GAME, 'Data', 'Resources', 'Data')
FONTS = os.path.join(GAME, 'UI', 'Resources', 'UI', 'Fonts')
UI_OUT = os.path.join(GAME, 'UI', 'Resources', 'UI')
SCRATCH = os.environ.get('TT_SCRATCH', os.path.join(HERE, '_preview'))

# Brief palette
MIDNIGHT = (0x09, 0x1B, 0x2D)
PETROL = (0x1B, 0x34, 0x47)
DESAT_BLUE = (0x56, 0x78, 0x89)
TWEED = (0x8A, 0x6B, 0x50)
BRONZE = (0xB6, 0x78, 0x54)
OFFWHITE = (0xD6, 0xCB, 0xC0)
INK = (0x1E, 0x17, 0x14)


def ref(name):
    return os.path.join(REFS, name)


def ensure_dir(p):
    os.makedirs(p, exist_ok=True)
    return p


def save_png(img, rel_path, root=ART_OUT):
    """Save an RGBA image under the art output root. rel_path without extension."""
    path = os.path.join(root, rel_path + '.png')
    ensure_dir(os.path.dirname(path))
    if isinstance(img, np.ndarray):
        img = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    img.save(path, optimize=True)
    return path


def save_json(obj, rel_path, root=DATA_OUT):
    path = os.path.join(root, rel_path + '.json')
    ensure_dir(os.path.dirname(path))
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(obj, f, indent=1, ensure_ascii=False)
    return path


def to_np(img):
    return np.asarray(img.convert('RGBA')).astype(np.float32)


def from_np(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')


def poly_mask(size, polys, ss=4, blur=0.0):
    """Anti-aliased polygon mask (float 0..1). polys: list of point lists (pixel coords)."""
    w, h = size
    m = Image.new('L', (w * ss, h * ss), 0)
    d = ImageDraw.Draw(m)
    for poly in polys:
        neg = False
        if isinstance(poly, tuple) and poly and poly[0] == '-':
            neg, poly = True, poly[1]
        d.polygon([(x * ss, y * ss) for x, y in poly], fill=0 if neg else 255)
    m = m.resize((w, h), Image.LANCZOS)
    if blur > 0:
        m = m.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(m).astype(np.float32) / 255.0


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def trim(img, pad=2):
    a = np.asarray(img)[:, :, 3]
    ys, xs = np.nonzero(a > 2)
    if len(xs) == 0:
        return img, (0, 0)
    x0, y0 = max(xs.min() - pad, 0), max(ys.min() - pad, 0)
    x1, y1 = min(xs.max() + pad + 1, img.width), min(ys.max() + pad + 1, img.height)
    return img.crop((x0, y0, x1, y1)), (x0, y0)


def next_pot(n):
    p = 1
    while p < n:
        p *= 2
    return p


def lerp(a, b, t):
    return a + (b - a) * t


def mix(c1, c2, t):
    return tuple(int(round(lerp(c1[i], c2[i], t))) for i in range(len(c1)))


def rng(seed):
    return np.random.default_rng(seed)
