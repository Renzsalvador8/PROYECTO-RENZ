"""Skia-based painting helpers giving a consistent ink + gouache look."""
import math
import numpy as np
import skia
from PIL import Image
from scipy import ndimage

INK = skia.Color(30, 23, 20)


def surface(w, h):
    s = skia.Surface(int(w), int(h))
    s.getCanvas().clear(skia.ColorTRANSPARENT)
    return s


def to_pil(surf):
    img = surf.makeImageSnapshot()
    arr = img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType)
    return Image.fromarray(arr, 'RGBA')


def to_np(surf):
    return np.asarray(to_pil(surf)).astype(np.float32)


def col(c, a=255):
    if len(c) == 4:
        return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(c[3]))
    return skia.Color(int(c[0]), int(c[1]), int(c[2]), int(a))


def path_poly(pts, close=True):
    p = skia.Path()
    p.moveTo(*pts[0])
    for q in pts[1:]:
        p.lineTo(*q)
    if close:
        p.close()
    return p


def path_smooth(pts, close=True, tension=0.5):
    """Catmull-Rom spline through points -> cubic path."""
    n = len(pts)
    p = skia.Path()
    if n < 3:
        return path_poly(pts, close)
    P = [np.array(q, float) for q in pts]
    p.moveTo(*P[0])
    rng_ = range(n) if close else range(n - 1)
    for i in rng_:
        p0 = P[(i - 1) % n] if (close or i > 0) else P[i]
        p1 = P[i]
        p2 = P[(i + 1) % n]
        p3 = P[(i + 2) % n] if (close or i + 2 < n) else P[(i + 1) % n]
        c1 = p1 + (p2 - p0) * tension / 3.0
        c2 = p2 - (p3 - p1) * tension / 3.0
        p.cubicTo(c1[0], c1[1], c2[0], c2[1], p2[0], p2[1])
    if close:
        p.close()
    return p


def fill(canvas, path, color, aa=True, shader=None, blend=None, alpha=None):
    paint = skia.Paint(AntiAlias=aa, Color=col(color) if not isinstance(color, int) else color)
    if shader is not None:
        paint.setShader(shader)
    if alpha is not None:
        paint.setAlphaf(alpha)
    if blend is not None:
        paint.setBlendMode(blend)
    canvas.drawPath(path, paint)


def stroke(canvas, path, color=None, width=2.0, wobble=0.0, seed=1, cap=skia.Paint.kRound_Cap, alpha=None, blend=None):
    paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                       Color=col(color) if color is not None else INK, StrokeCap=cap,
                       StrokeJoin=skia.Paint.kRound_Join)
    if wobble > 0:
        paint.setPathEffect(skia.DiscretePathEffect.Make(6.0, wobble, seed))
    if alpha is not None:
        paint.setAlphaf(alpha)
    if blend is not None:
        paint.setBlendMode(blend)
    canvas.drawPath(path, paint)


def lin_grad(p0, p1, colors, pos=None):
    return skia.GradientShader.MakeLinear([skia.Point(*p0), skia.Point(*p1)], [col(c) for c in colors], pos)


def rad_grad(c, r, colors, pos=None):
    return skia.GradientShader.MakeRadial(skia.Point(*c), r, [col(c_) for c_ in colors], pos)


def noise_np(h, w, scale=1.0, seed=0, octaves=1):
    r = np.random.default_rng(seed)
    out = np.zeros((h, w), np.float32)
    amp = 1.0
    tot = 0
    for o in range(octaves):
        s = scale * (2 ** o)
        n = r.standard_normal((h, w)).astype(np.float32)
        if s > 0.3:
            n = ndimage.gaussian_filter(n, s)
            n /= (n.std() + 1e-6)
        out += n * amp
        tot += amp
        amp *= 0.5
    return out / tot


def gouache(img, strength=1.0, seed=0, grain=0.035, mottling=0.05, streak_dir=None, streak=0.0):
    """Apply paint texture to an RGBA float array (0..255): mottled pigment + paper grain."""
    a = img.astype(np.float32).copy()
    h, w = a.shape[:2]
    mot = noise_np(h, w, 18, seed, 2) * mottling
    gr = noise_np(h, w, 0.6, seed + 7) * grain
    v = 1.0 + (mot + gr) * strength
    if streak > 0:
        n = np.random.default_rng(seed + 3).standard_normal((h, w)).astype(np.float32)
        if streak_dir == 'h':
            n = ndimage.gaussian_filter(n, (0.6, 22))
        else:
            n = ndimage.gaussian_filter(n, (22, 0.6))
        n /= (n.std() + 1e-6)
        v += n * streak * strength
    a[:, :, :3] *= v[:, :, None]
    return np.clip(a, 0, 255)


def pil_from(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), 'RGBA')
