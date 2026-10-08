"""Environment painting kit: consistent ink + gouache scenery for every level."""
import math
import numpy as np
import skia
from PIL import Image
from scipy import ndimage
from paint import *
from common import *
from paint import to_np as sk_to_np


class Canvas:
    def __init__(self, w, h, clear=None):
        self.w, self.h = int(w), int(h)
        self.s = surface(self.w, self.h)
        self.c = self.s.getCanvas()
        if clear is not None:
            self.c.clear(col(clear))

    # ---- primitives -------------------------------------------------------------------
    def rect(self, x, y, w, h, color, alpha=None, shader=None, rough=0.0, outline=0.0, ocolor=None, blur=0.0):
        p = skia.Path(); p.addRect(skia.Rect.MakeXYWH(x, y, w, h))
        self.path(p, color, alpha, shader, rough, outline, ocolor, blur)

    def poly(self, pts, color, alpha=None, shader=None, rough=0.0, outline=0.0, ocolor=None, blur=0.0, smooth=False):
        p = path_smooth(pts, True, 0.4) if smooth else path_poly(pts)
        self.path(p, color, alpha, shader, rough, outline, ocolor, blur)

    def ellipse(self, cx, cy, rx, ry, color, alpha=None, shader=None, blur=0.0, outline=0.0, ocolor=None):
        p = skia.Path(); p.addOval(skia.Rect.MakeLTRB(cx - rx, cy - ry, cx + rx, cy + ry))
        self.path(p, color, alpha, shader, 0.0, outline, ocolor, blur)

    def path(self, p, color, alpha=None, shader=None, rough=0.0, outline=0.0, ocolor=None, blur=0.0):
        paint = skia.Paint(AntiAlias=True, Color=col(color))
        if shader is not None:
            paint.setShader(shader)
        if alpha is not None:
            paint.setAlphaf(alpha)
        if rough > 0:
            paint.setPathEffect(skia.DiscretePathEffect.Make(8.0, rough, 7))
        if blur > 0:
            paint.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        self.c.drawPath(p, paint)
        if outline > 0:
            stroke(self.c, p, color=ocolor or (30, 23, 20), width=outline, wobble=0.4, seed=5)

    def line(self, pts, color=(30, 23, 20), width=2.0, alpha=None, wobble=0.4, smooth=False, blur=0.0):
        p = path_smooth(pts, False, 0.4) if smooth else path_poly(pts, False)
        paint = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width, Color=col(color),
                           StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join)
        if wobble > 0:
            paint.setPathEffect(skia.DiscretePathEffect.Make(6.0, wobble, 3))
        if alpha is not None:
            paint.setAlphaf(alpha)
        if blur > 0:
            paint.setMaskFilter(skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        self.c.drawPath(p, paint)

    def glow(self, cx, cy, r, color, alpha=0.5):
        sh = rad_grad((cx, cy), r, [color + (int(255 * alpha),), color + (0,)])
        paint = skia.Paint(AntiAlias=True); paint.setShader(sh)
        self.c.drawCircle(cx, cy, r, paint)

    def vgrad(self, x, y, w, h, colors, pos=None, alpha=None):
        self.rect(x, y, w, h, colors[0], alpha=alpha, shader=lin_grad((0, y), (0, y + h), colors, pos))

    def hgrad(self, x, y, w, h, colors, pos=None, alpha=None):
        self.rect(x, y, w, h, colors[0], alpha=alpha, shader=lin_grad((x, 0), (x + w, 0), colors, pos))

    def text(self, s, x, y, size, color, font='Jost-Medium.ttf', spacing=0.0, alpha=None, align='left'):
        tf = skia.Typeface.MakeFromFile(FONTS + '/' + font)
        f = skia.Font(tf, size)
        paint = skia.Paint(AntiAlias=True, Color=col(color))
        if alpha is not None:
            paint.setAlphaf(alpha)
        widths = [f.measureText(ch) for ch in s]
        total = sum(widths) + spacing * (len(s) - 1)
        if align == 'center':
            x -= total / 2
        elif align == 'right':
            x -= total
        for ch, wd in zip(s, widths):
            self.c.drawString(ch, x, y, f, paint)
            x += wd + spacing
        return total

    def image(self, img, x, y, w=None, h=None, alpha=1.0):
        if isinstance(img, Image.Image):
            arr = np.asarray(img.convert('RGBA')).copy()
        else:
            arr = np.clip(img, 0, 255).astype(np.uint8)
        si = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
        w = w or si.width(); h = h or si.height()
        p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
        self.c.drawImageRect(si, skia.Rect.MakeXYWH(x, y, w, h), skia.SamplingOptions(skia.FilterMode.kLinear), p)

    def clip(self, pts):
        self.c.save(); self.c.clipPath(path_poly(pts), skia.ClipOp.kIntersect, True)

    def unclip(self):
        self.c.restore()

    # ---- output -----------------------------------------------------------------------
    def np(self):
        return sk_to_np(self.s)

    def finish(self, texture=1.0, seed=0, grain=0.035, mottling=0.05, streak=0.0, streak_dir='v', haze=None, haze_amt=0.0):
        a = self.np()
        if haze is not None and haze_amt > 0:
            a[:, :, :3] = a[:, :, :3] * (1 - haze_amt) + np.array(haze, np.float32) * haze_amt
        if texture > 0:
            a = gouache(a, texture, seed=seed, grain=grain, mottling=mottling, streak=streak, streak_dir=streak_dir)
        return pil_from(a)


def soften(img, radius):
    from PIL import ImageFilter
    return img.filter(ImageFilter.GaussianBlur(radius))


def ridge(n, w, base, amp, seed, rough=4):
    """1D ridge line (mountains/skyline noise)."""
    r = np.random.default_rng(seed)
    xs = np.linspace(0, w, n)
    y = np.zeros(n)
    a = amp
    for o in range(rough):
        k = 2 ** o
        phase = r.uniform(0, 2 * np.pi, 3)
        y += a * (np.sin(xs / w * 2 * np.pi * k + phase[0]) * 0.6 + np.sin(xs / w * 2 * np.pi * k * 1.7 + phase[1]) * 0.4)
        a *= 0.5
    return list(zip(xs, base - y))


def plant(cv, x, y, h, seed=0, leaf=(52, 74, 62), pot=(36, 40, 44), dark=False):
    """Tall sculptural indoor plant (strelitzia-like) in a cylindrical pot. (x,y) = pot base centre."""
    r = np.random.default_rng(seed)
    pw, ph = h * 0.28, h * 0.26
    for i in range(9):
        a = math.radians(r.uniform(-38, 38))
        L = h * r.uniform(0.55, 0.95)
        bx, by = x + r.uniform(-pw * 0.2, pw * 0.2), y - ph
        tx, ty = bx + math.sin(a) * L, by - math.cos(a) * L
        cv.line([(bx, by), ((bx + tx) / 2 + math.sin(a) * 6, (by + ty) / 2), (tx, ty)], color=(40, 54, 44), width=max(2, h * 0.012), wobble=0.3, smooth=True)
        lw = h * r.uniform(0.07, 0.11)
        ll = h * r.uniform(0.22, 0.34)
        ang = a + r.uniform(-0.4, 0.4)
        cx, cy = tx, ty
        dx, dy = math.sin(ang), -math.cos(ang)
        nx, ny = -dy, dx
        pts = [(cx - dx * ll * 0.1, cy - dy * ll * 0.1), (cx + nx * lw + dx * ll * 0.4, cy + ny * lw + dy * ll * 0.4),
               (cx + dx * ll, cy + dy * ll), (cx - nx * lw + dx * ll * 0.4, cy - ny * lw + dy * ll * 0.4)]
        k = r.uniform(-0.25, 0.3)
        c = tuple(int(max(0, min(255, v * (1 + k)))) for v in leaf)
        cv.poly(pts, c, smooth=True, outline=1.6 if not dark else 0, ocolor=(24, 30, 26))
        cv.line([(cx, cy), (cx + dx * ll * 0.9, cy + dy * ll * 0.9)], color=(30, 44, 36), width=1.0, alpha=0.6, wobble=0.2)
    cv.poly([(x - pw / 2, y - ph), (x + pw / 2, y - ph), (x + pw * 0.42, y), (x - pw * 0.42, y)], pot,
            shader=lin_grad((x - pw / 2, 0), (x + pw / 2, 0), [tuple(min(255, v + 30) for v in pot), pot, tuple(max(0, v - 14) for v in pot)]),
            outline=1.8 if not dark else 0)


def tree(cv, x, y, h, seed=0, colr=(48, 66, 58), trunk=(44, 36, 30), outline=1.4):
    r = np.random.default_rng(seed)
    cv.poly([(x - h * 0.025, y), (x + h * 0.025, y), (x + h * 0.012, y - h * 0.5), (x - h * 0.012, y - h * 0.5)], trunk,
            outline=outline)
    blobs = []
    for i in range(7):
        bx = x + r.uniform(-0.22, 0.22) * h
        by = y - h * r.uniform(0.5, 0.92)
        br = h * r.uniform(0.14, 0.22)
        blobs.append((bx, by, br))
    for bx, by, br in sorted(blobs, key=lambda b: -b[1]):
        k = (y - by) / h
        c = tuple(int(v * (0.8 + 0.4 * k)) for v in colr)
        n = 12
        pts = [(bx + br * (1 + r.uniform(-0.12, 0.12)) * math.cos(2 * math.pi * i / n),
                by + br * 0.85 * (1 + r.uniform(-0.12, 0.12)) * math.sin(2 * math.pi * i / n)) for i in range(n)]
        cv.poly(pts, c, smooth=True, outline=outline)
