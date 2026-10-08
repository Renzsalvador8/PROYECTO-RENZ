"""UI art: title lockup, frames, icons, magnifier cursor, vignette, grain, touch controls."""
import math
import numpy as np
from PIL import Image, ImageFilter
from env_kit import *
from common import *

CREAM = (236, 228, 214)


def stache_path(cx, cy, s):
    """A curled handlebar moustache glyph as a list of points (filled)."""
    pts = []
    for side in (-1, 1):
        seg = []
        for t in np.linspace(0, 1, 26):
            x = cx + side * (6 + 92 * t) * s
            y = cy + (10 * math.sin(t * math.pi) - 26 * t ** 3) * s
            seg.append((x, y))
        # curl tip
        tip = seg[-1]
        for a in np.linspace(0, 1.6 * math.pi, 18):
            seg.append((tip[0] + side * (10 * math.sin(a)) * s, tip[1] - (10 - 10 * math.cos(a)) * s))
        lower = []
        for t in np.linspace(1, 0, 26):
            x = cx + side * (6 + 88 * t) * s
            y = cy + (22 * math.sin(t * math.pi * 0.9) + 2 - 22 * t ** 3) * s
            lower.append((x, y))
        pts.append(seg + lower)
    return pts


def title_lockup(w=1600, h=520):
    cv = Canvas(w, h)
    cv.text('UN JUEGO ORIGINAL DE ZENITH STUDIO', w / 2, 60, 26, (182, 160, 130), 'Jost-Regular.ttf', spacing=9, align='center')
    cv.text('THE TESTER', w / 2, 270, 196, CREAM, 'CormorantGaramond-SemiBold.ttf', spacing=24, align='center')
    for side in (-1, 1):
        cv.line([(w / 2 + side * 110, 340), (w / 2 + side * 520, 340)], color=(182, 120, 84), width=2.0, wobble=0.0)
    for poly in stache_path(w / 2, 336, 0.9):
        cv.poly(poly, (182, 120, 84), smooth=True)
    cv.text('THE ULTIMATE TEST', w / 2, 430, 42, (206, 198, 186), 'Jost-Light.ttf', spacing=22, align='center')
    return cv.finish(texture=0.25, seed=70, grain=0.02, mottling=0.0)


def end_lockup(w=1600, h=520):
    cv = Canvas(w, h)
    logo = Image.open(UI_OUT + '/zenith_logo_mark.png')
    lw = 150; lh = int(logo.height * lw / logo.width)
    cv.image(logo, w / 2 - lw / 2, 10, lw, lh)
    cv.text('ZENITH STUDIO', w / 2, 240, 76, CREAM, 'Jost-Medium.ttf', spacing=30, align='center')
    cv.text('CREATE BEYOND REAL', w / 2, 300, 30, (182, 120, 84), 'Jost-Regular.ttf', spacing=16, align='center')
    cv.line([(w / 2 - 240, 352), (w / 2 + 240, 352)], color=(120, 130, 140), width=1.4, wobble=0.0)
    cv.text('THE TESTER — THE ULTIMATE TEST', w / 2, 410, 30, (206, 198, 186), 'CormorantGaramond-Medium.ttf', spacing=8, align='center')
    return cv.finish(texture=0.2, seed=71, grain=0.02, mottling=0.0)


def frame9(w=96, h=96, r=14, fill_c=(9, 27, 45), alpha=0.82, border=(182, 160, 130), bw=1.6):
    cv = Canvas(w, h)
    import skia
    p = skia.Path(); p.addRoundRect(skia.Rect.MakeXYWH(2, 2, w - 4, h - 4), r, r)
    cv.path(p, fill_c, alpha=alpha)
    pp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=bw, Color=col(border))
    pp.setAlphaf(0.75)
    cv.c.drawPath(p, pp)
    return cv.finish(texture=0.0)


def keycap(w=96, h=96):
    cv = Canvas(w, h)
    import skia
    p = skia.Path(); p.addRoundRect(skia.Rect.MakeXYWH(6, 6, w - 12, h - 12), 14, 14)
    pp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3.0, Color=col(CREAM))
    cv.c.drawPath(p, pp)
    p2 = skia.Path(); p2.addRoundRect(skia.Rect.MakeXYWH(6, h - 18, w - 12, 12), 6, 6)
    cv.path(p2, CREAM, alpha=0.25)
    return cv.finish(texture=0.0)


def circle(w=256, soft=False):
    cv = Canvas(w, w)
    if soft:
        cv.glow(w / 2, w / 2, w / 2, (255, 255, 255), 1.0)
    else:
        cv.ellipse(w / 2, w / 2, w / 2 - 2, w / 2 - 2, (255, 255, 255))
    return cv.finish(texture=0.0)


def ring(w=256, thick=10):
    cv = Canvas(w, w)
    import skia
    p = skia.Path(); p.addCircle(w / 2, w / 2, w / 2 - thick)
    pp = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=thick, Color=skia.ColorWHITE)
    cv.c.drawPath(p, pp)
    return cv.finish(texture=0.0)


def check(w=96):
    cv = Canvas(w, w)
    cv.line([(w * 0.2, w * 0.52), (w * 0.42, w * 0.74), (w * 0.82, w * 0.26)], color=(255, 255, 255), width=w * 0.11, wobble=0.0)
    return cv.finish(texture=0.0)


def arrow(w=128, left=True):
    cv = Canvas(w, w)
    cv.ellipse(w / 2, w / 2, w / 2 - 3, w / 2 - 3, (9, 27, 45), alpha=0.55)
    cv.line([(w / 2 + w * 0.42 * math.cos(t), w / 2 + w * 0.42 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 60)], color=CREAM, width=3, wobble=0.0, alpha=0.8)
    d = -1 if left else 1
    cv.line([(w / 2 - d * 10, w / 2 - 22), (w / 2 + d * 14, w / 2), (w / 2 - d * 10, w / 2 + 22)], color=CREAM, width=7, wobble=0.0)
    return cv.finish(texture=0.0)


def chevron(w=128, up=True):
    cv = Canvas(w, w)
    cv.ellipse(w / 2, w / 2, w / 2 - 3, w / 2 - 3, (9, 27, 45), alpha=0.55)
    cv.line([(w / 2 + w * 0.42 * math.cos(t), w / 2 + w * 0.42 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 60)], color=CREAM, width=3, wobble=0.0, alpha=0.8)
    d = -1 if up else 1
    cv.line([(w / 2 - 22, w / 2 - d * 10), (w / 2, w / 2 + d * 14), (w / 2 + 22, w / 2 - d * 10)], color=CREAM, width=7, wobble=0.0)
    return cv.finish(texture=0.0)


def pause_icon(w=96):
    cv = Canvas(w, w)
    cv.rect(w * 0.32, w * 0.26, w * 0.1, w * 0.48, CREAM)
    cv.rect(w * 0.58, w * 0.26, w * 0.1, w * 0.48, CREAM)
    return cv.finish(texture=0.0)


def vignette(w=1024, h=576):
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a = np.clip((d - 0.55) / 0.75, 0, 1) ** 1.6 * 255
    arr = np.dstack([np.full((h, w), 4.0), np.full((h, w), 10.0), np.full((h, w), 18.0), a])
    return pil_from(arr)


def grain(w=256):
    r = np.random.default_rng(80)
    n = r.standard_normal((w, w)).astype(np.float32)
    from scipy import ndimage
    n = ndimage.gaussian_filter(n, 0.6, mode='wrap')
    n = (n - n.mean()) / n.std()
    v = np.clip(128 + n * 60, 0, 255)
    a = np.clip(np.abs(n) * 70, 0, 255)
    arr = np.dstack([v, v, v, a])
    return pil_from(arr)


def magnifier_cursor(w=560, h=760):
    """Large magnifier frame for inspection mode (lens centre at (280, 280), radius 230)."""
    cv = Canvas(w, h)
    cx, cy, R = w / 2, 280, 250
    # handle
    hp = [(cx - 26, cy + R - 10), (cx + 26, cy + R - 10), (cx + 40, h - 30), (cx, h - 6), (cx - 40, h - 30)]
    cv.poly(hp, (40, 28, 22), shader=lin_grad((cx - 40, 0), (cx + 40, 0), [(26, 18, 14), (86, 60, 44), (30, 22, 18)]), outline=3.0, smooth=True)
    cv.poly([(cx - 34, cy + R + 10), (cx + 34, cy + R + 10), (cx + 36, cy + R + 60), (cx - 36, cy + R + 60)], BRONZE,
            shader=lin_grad((cx - 36, 0), (cx + 36, 0), [(120, 74, 44), (226, 170, 120), (110, 66, 40)]), outline=2.4)
    # rim ring
    import skia
    p = skia.Path(); p.addCircle(cx, cy, R)
    p.addCircle(cx, cy, R - 26)
    p.setFillType(skia.PathFillType.kEvenOdd)
    cv.path(p, BRONZE, shader=lin_grad((cx - R, cy - R), (cx + R, cy + R), [(226, 170, 120), (150, 92, 56), (86, 52, 32)]))
    for rr in (R, R - 26):
        cv.line([(cx + rr * math.cos(t), cy + rr * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 120)], width=3.0, wobble=0.0)
    # glass sheen (very light; the lens interior is drawn by the game)
    cv.line([(cx + (R - 50) * math.cos(t), cy + (R - 50) * math.sin(t)) for t in np.linspace(math.radians(200), math.radians(260), 30)],
            color=(255, 255, 250), width=10, alpha=0.35, wobble=0.0)
    return cv.finish(texture=0.4, seed=81)


def paper_card(w=256, h=256):
    cv = Canvas(w, h)
    cv.rect(4, 4, w - 8, h - 8, (232, 224, 208), outline=1.2, ocolor=(150, 130, 110))
    for y in range(40, h - 10, 26):
        cv.line([(16, y), (w - 16, y)], color=(170, 180, 190), width=1.0, alpha=0.5, wobble=0.0)
    cv.line([(36, 8), (36, h - 8)], color=(200, 120, 110), width=1.2, alpha=0.5, wobble=0.0)
    return cv.finish(texture=0.8, seed=82, mottling=0.05)


def exterior_inspection_bg():
    """Blurred, darkened showroom behind the 3/4 hero car, with the car's floor reflection baked in."""
    W_, H_ = 1920, 1080
    cv = Canvas(W_, H_, clear=(14, 24, 34))
    bayw = Image.open(ART_OUT + '/Showroom/bay_window.png')
    far = Image.open(ART_OUT + '/Showroom/city_far.png')
    cv.image(far, -200, 200, 2400, 600, alpha=0.9)
    for i in range(6):
        cv.image(bayw, i * 400 - 100, -60, 400, 860 * 1.0)
    cv.vgrad(0, 0, W_, H_, [(9, 27, 45, 140), (9, 27, 45, 60), (9, 27, 45, 200)], [0, 0.5, 1])
    # floor
    cv.vgrad(0, 760, W_, 320, [(56, 66, 74), (28, 36, 44), (12, 18, 26)], [0, 0.4, 1])
    cv.rect(0, 756, W_, 6, (120, 134, 140), alpha=0.5)
    img = soften(cv.finish(texture=0.0), 7)
    base = np.asarray(img).astype(np.float32)
    # reflection of the hero car
    hero = np.asarray(Image.open(ART_OUT + '/Inspection/ioniq5_34_teal.png')).astype(np.float32)
    ys = np.nonzero(hero[:, :, 3].max(axis=1) > 200)[0]
    yb = int(ys.max()) - 8
    refl = hero[:yb][::-1]
    rh = min(refl.shape[0], H_ - yb)
    refl = refl[:rh]
    fade = np.linspace(0.32, 0.0, rh)[:, None]
    a = refl[:, :, 3:4] / 255.0 * fade[:, :, None]
    region = base[yb:yb + rh]
    region[:, :, :3] = region[:, :, :3] * (1 - a) + refl[:, :, :3] * a
    base[yb:yb + rh] = region
    # spotlight pool on floor
    out = pil_from(base)
    cv2 = Canvas(W_, H_)
    cv2.image(out, 0, 0)
    cv2.ellipse(1000, 860, 820, 120, (255, 244, 220), alpha=0.10, blur=40)
    cv2.glow(960, 120, 700, (220, 230, 236), 0.10)
    return cv2.finish(texture=0.8, seed=83)


def build():
    out = {
        'title_lockup': title_lockup(), 'end_lockup': end_lockup(), 'frame': frame9(), 'frame_light': frame9(fill_c=(236, 228, 214), alpha=0.92, border=(150, 130, 110)),
        'keycap': keycap(), 'circle': circle(), 'circle_soft': circle(soft=True), 'ring': ring(), 'check': check(),
        'arrow_left': arrow(left=True), 'arrow_right': arrow(left=False), 'chevron_up': chevron(up=True), 'chevron_down': chevron(up=False),
        'pause': pause_icon(), 'vignette': vignette(), 'grain': grain(), 'magnifier_cursor': magnifier_cursor(),
        'paper_card': paper_card(), 'stache_icon': None,
    }
    st = Canvas(240, 90)
    for poly in stache_path(120, 40, 1.05):
        st.poly(poly, (255, 255, 255), smooth=True)
    out['stache_icon'] = st.finish(texture=0.0)
    for k, v in out.items():
        save_png(v, k, root=UI_OUT)
    save_png(exterior_inspection_bg(), 'Inspection/bg_exterior')
    return out


if __name__ == '__main__':
    out = build()
    print({k: v.size for k, v in out.items()})
