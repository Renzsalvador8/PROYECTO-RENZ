"""Test drive: Quito-inspired city layers, road and street props."""
import math
import numpy as np
from PIL import Image
from env_kit import *
from common import *
from paint_showroom import city_far

FACADES = [(196, 186, 170), (176, 150, 120), (150, 166, 170), (206, 198, 184), (168, 128, 98), (120, 138, 146), (214, 206, 190)]


def sky(w=64, h=1024):
    cv = Canvas(w, h)
    cv.vgrad(0, 0, w, h, [(120, 150, 172), (176, 196, 206), (226, 222, 210)], [0, 0.55, 1])
    return cv.finish(texture=0.0)


def andes(w=2048, h=512, seed=21):
    cv = Canvas(w, h)
    pts = ridge(90, w, 330, 90, seed, 5) + [(w, h), (0, h)]
    cv.poly(pts, (132, 152, 168))
    # Cotopaxi-like cone with snow
    vx = w * 0.4
    cone = [(vx - 420, 360), (vx - 70, 120), (vx - 20, 104), (vx + 30, 108), (vx + 80, 124), (vx + 440, 360)]
    cv.poly(cone + [(vx + 440, h), (vx - 420, h)], (120, 142, 160))
    snow = [(vx - 125, 180), (vx - 70, 120), (vx - 20, 104), (vx + 30, 108), (vx + 80, 124), (vx + 140, 185), (vx + 100, 176),
            (vx + 60, 196), (vx + 20, 178), (vx - 20, 200), (vx - 60, 182), (vx - 95, 196)]
    cv.poly(snow, (236, 240, 240), smooth=True)
    pts2 = ridge(90, w, 380, 50, seed + 4, 5) + [(w, h), (0, h)]
    cv.poly(pts2, (112, 132, 148))
    cv.vgrad(0, 300, w, 212, [(200, 210, 212, 0), (200, 210, 212, 150)])
    return soften(cv.finish(texture=0.6, seed=seed), 1.5)


def skyline(w=2048, h=400, seed=22):
    cv = Canvas(w, h)
    r = np.random.default_rng(seed)
    x = 0
    while x < w:
        bw = r.uniform(50, 140); bh = r.uniform(60, 220) if r.random() > 0.12 else r.uniform(240, 330)
        c = tuple(int(v * r.uniform(0.94, 1.04)) for v in (140, 156, 166))
        cv.rect(x, h - bh, bw, bh, c)
        for wy in range(int(h - bh + 10), h - 10, 16):
            cv.rect(x + 6, wy, bw - 12, 3, (160, 176, 184), alpha=0.5)
        x += bw + r.uniform(0, 10)
    # church domes / towers (colonial Quito silhouette)
    for dx in (500, 1500):
        cv.rect(dx, h - 260, 60, 260, (134, 150, 160))
        cv.poly([(dx - 4, h - 260), (dx + 64, h - 260), (dx + 30, h - 330)], (128, 144, 156))
        cv.ellipse(dx + 140, h - 190, 60, 54, (136, 152, 162))
        cv.rect(dx + 80, h - 192, 120, 192, (138, 154, 164))
    cv.vgrad(0, h - 160, w, 160, [(214, 220, 220, 0), (214, 220, 220, 140)])
    return soften(cv.finish(texture=0.6, seed=seed), 0.8)


def facade_block(cv, x, base, w, h, color, seed, style):
    r = np.random.default_rng(seed)
    dark = tuple(int(v * 0.72) for v in color)
    cv.rect(x, base - h, w, h, color, outline=2.0, shader=lin_grad((x, 0), (x + w, 0), [tuple(min(255, int(v * 1.06)) for v in color), color, dark]))
    cv.rect(x - 6, base - h - 14, w + 12, 16, dark, outline=1.6)   # cornice
    rows = int((h - 60) // 110)
    cols = max(1, int(w // 90))
    for i in range(cols):
        for j in range(rows):
            wx = x + (i + 0.5) * w / cols - 22
            wy = base - h + 40 + j * 110
            if style == 'colonial':
                cv.rect(wx - 6, wy - 6, 56, 86, tuple(min(255, v + 18) for v in color), outline=1.2)
                cv.rect(wx, wy, 44, 74, (40, 50, 58), outline=1.4)
                cv.line([(wx + 22, wy), (wx + 22, wy + 74)], color=(150, 140, 120), width=1.2)
                if j > 0 and r.random() < 0.5:   # balcony
                    cv.rect(wx - 10, wy + 66, 64, 8, (40, 36, 34), outline=1.0)
                    for k in range(6):
                        cv.line([(wx - 8 + k * 12, wy + 70), (wx - 8 + k * 12, wy + 88)], color=(40, 36, 34), width=1.6)
                    cv.line([(wx - 10, wy + 88), (wx + 54, wy + 88)], color=(40, 36, 34), width=2.0)
            else:
                cv.rect(wx - 14, wy, 72, 70, (52, 70, 82), outline=1.2, shader=lin_grad((wx, wy), (wx + 70, wy + 70), [(90, 116, 128), (40, 56, 66)]))
    # ground floor shop
    sh = 120
    cv.rect(x + 10, base - sh, w - 20, sh, (36, 44, 52), outline=1.6)
    cv.rect(x + 10, base - sh - 26, w - 20, 26, tuple(int(v * 0.6) for v in color), outline=1.2)
    if r.random() < 0.6:
        cv.poly([(x + 14, base - sh), (x + w - 14, base - sh), (x + w - 30, base - sh + 30), (x + 30, base - sh + 30)],
                (182, 120, 84) if r.random() < 0.5 else (86, 120, 137), outline=1.4)


def city_mid(w=2048, h=760, seed=23):
    cv = Canvas(w, h)
    r = np.random.default_rng(seed)
    x = 0
    base = h
    k = 0
    while x < w - 40:
        bw = r.uniform(240, 420)
        if x + bw > w:
            bw = w - x
        bh = r.uniform(380, 640)
        style = 'colonial' if r.random() < 0.6 else 'modern'
        facade_block(cv, x, base, bw, bh, FACADES[(k + seed) % len(FACADES)], seed + k, style)
        x += bw
        k += 1
    return cv.finish(texture=1.0, seed=seed, streak=0.01)


def street_tree(w=420, h=560, seed=24):
    cv = Canvas(w, h)
    tree(cv, w / 2, h - 2, h * 0.98, seed=seed, colr=(70, 94, 72), trunk=(64, 52, 40))
    cv.ellipse(w / 2, h - 8, 50, 8, (30, 30, 30), alpha=0.5)
    return cv.finish(texture=1.0, seed=seed)


def street_lamp(w=180, h=720, seed=25):
    cv = Canvas(w, h)
    cv.rect(w / 2 - 6, 60, 12, h - 60, (34, 38, 42), outline=1.4)
    cv.poly([(w / 2, 70), (w / 2 + 70, 40), (w / 2 + 74, 50), (w / 2 + 4, 84)], (34, 38, 42), outline=1.2)
    cv.poly([(w / 2 + 50, 36), (w / 2 + 92, 36), (w / 2 + 88, 52), (w / 2 + 54, 52)], (40, 44, 48), outline=1.4)
    cv.rect(w / 2 - 14, h - 40, 28, 40, (34, 38, 42), outline=1.2)
    return cv.finish(texture=0.8, seed=seed)


def road(w=512, h=430, seed=26):
    """Top edge = back kerb (y -1.9). Lanes centred at -2.7 (far) and -3.6 (near)."""
    cv = Canvas(w, h)
    # back sidewalk
    cv.rect(0, 0, w, 40, (170, 166, 158), outline=0)
    cv.rect(0, 36, w, 10, (120, 118, 112))
    # asphalt
    cv.vgrad(0, 46, w, 300, [(76, 80, 84), (60, 64, 68), (54, 58, 62)])
    # lane divider dashes (between far & near lanes at y = -3.15 -> 125 px below top)
    for x in range(0, w, 256):
        cv.rect(x + 20, 124, 140, 8, (226, 222, 210), alpha=0.9)
    # front kerb + sidewalk
    cv.rect(0, 346, w, 12, (140, 138, 132))
    cv.rect(0, 358, w, h - 358, (176, 172, 164))
    for x in range(0, w, 128):
        cv.line([(x, 358), (x - 20, h)], color=(140, 136, 130), width=1.4, alpha=0.7)
    img = cv.finish(texture=1.0, seed=seed, mottling=0.06, grain=0.05)
    return img


def traffic_light(w=200, h=760, seed=27):
    cv = Canvas(w, h)
    cv.rect(w / 2 - 7, 200, 14, h - 200, (36, 40, 44), outline=1.4)
    cv.rect(w / 2 - 34, 20, 68, 190, (26, 28, 30), outline=1.8)
    for k in range(3):
        cv.ellipse(w / 2, 56 + k * 58, 22, 22, (50, 52, 54), outline=1.2)
    cv.rect(w / 2 - 16, h - 30, 32, 30, (36, 40, 44), outline=1.2)
    return cv.finish(texture=0.6, seed=seed)


def lamp_glow(color, w=96, h=96):
    cv = Canvas(w, h)
    cv.glow(w / 2, h / 2, w / 2, color, 0.55)
    cv.ellipse(w / 2, h / 2, 20, 20, color)
    return cv.finish(texture=0.0)


def stop_line(w=60, h=230):
    cv = Canvas(w, h)
    cv.poly([(16, 0), (44, 0), (52, h), (8, h)], (236, 232, 222), alpha=0.92)
    return cv.finish(texture=0.6, seed=3)


def cone(w=60, h=90, seed=28):
    cv = Canvas(w, h)
    cv.poly([(w / 2 - 6, 4), (w / 2 + 6, 4), (w / 2 + 22, h - 14), (w / 2 - 22, h - 14)], (226, 110, 60), outline=1.6)
    cv.poly([(w / 2 - 12, 34), (w / 2 + 12, 34), (w / 2 + 15, 46), (w / 2 - 15, 46)], (236, 232, 222))
    cv.rect(4, h - 16, w - 8, 12, (40, 40, 40), outline=1.2)
    return cv.finish(texture=0.8, seed=seed)


def van(w=640, h=330, seed=29):
    cv = Canvas(w, h)
    g = h - 20
    cv.ellipse(w / 2, g + 6, w * 0.46, 10, (0, 0, 0), alpha=0.35, blur=6)
    cv.poly([(20, g - 40), (20, 30), (430, 30), (440, g - 40)], (214, 210, 200), outline=2.2,
            shader=lin_grad((0, 30), (0, g), [(232, 228, 218), (176, 172, 164)]))
    cv.poly([(440, 90), (540, 100), (610, 180), (620, g - 40), (440, g - 40)], (210, 206, 196), outline=2.2)
    cv.poly([(452, 104), (530, 112), (586, 178), (452, 178)], (40, 56, 66), outline=1.6)
    cv.rect(10, g - 50, w - 20, 26, (54, 58, 62), outline=1.6)
    cv.text('ENVÍOS RÁPIDOS', 60, 150, 34, (86, 120, 137), 'Jost-Medium.ttf', spacing=4)
    cv.text('(casi siempre)', 64, 186, 22, (120, 120, 116), 'CormorantGaramond-Italic.ttf')
    for wx in (130, 520):
        cv.ellipse(wx, g - 20, 54, 54, (28, 28, 30), outline=2.0)
        cv.ellipse(wx, g - 20, 26, 26, (140, 144, 148), outline=1.4)
    cv.rect(612, g - 120, 14, 30, (240, 200, 120), outline=1.0)
    return cv.finish(texture=1.0, seed=seed)


def sign_school(w=220, h=560, seed=30, end=False):
    cv = Canvas(w, h)
    cv.rect(w / 2 - 6, 160, 12, h - 160, (60, 64, 68), outline=1.2)
    if not end:
        cv.poly([(w / 2, 10), (w - 14, 100), (w / 2, 190), (14, 100)], (236, 196, 72), outline=2.2)
        cv.text('ZONA', w / 2, 86, 26, (30, 30, 30), 'Jost-SemiBold.ttf', spacing=2, align='center')
        cv.text('ESCOLAR', w / 2, 116, 22, (30, 30, 30), 'Jost-SemiBold.ttf', spacing=1, align='center')
        cv.ellipse(w / 2, 236, 54, 54, (236, 232, 222), outline=2.0)
        cv.line([(w / 2 + 54 * math.cos(t), 236 + 54 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 40)], color=(200, 50, 44), width=9, wobble=0)
        cv.text('30', w / 2, 252, 40, (30, 30, 30), 'Jost-SemiBold.ttf', align='center')
    else:
        cv.rect(30, 40, w - 60, 140, (236, 232, 222), outline=2.0)
        cv.text('FIN ZONA', w / 2, 100, 24, (30, 30, 30), 'Jost-SemiBold.ttf', spacing=2, align='center')
        cv.text('ESCOLAR', w / 2, 132, 22, (30, 30, 30), 'Jost-SemiBold.ttf', spacing=1, align='center')
        cv.line([(40, 170), (w - 40, 50)], color=(40, 40, 40), width=5, wobble=0)
    return cv.finish(texture=0.8, seed=seed)


def parking_box(w=720, h=150, seed=31):
    cv = Canvas(w, h)
    pts = [(40, 10), (w - 10, 10), (w - 40, h - 10), (10, h - 10)]
    cv.line(pts + [pts[0]], color=(236, 232, 222), width=7, wobble=0.6)
    cv.text('P', w / 2, h / 2 + 22, 64, (236, 232, 222), 'Jost-Medium.ttf', align='center', alpha=0.85)
    return cv.finish(texture=0.8, seed=seed)


def sign_parking(w=200, h=520, seed=32):
    cv = Canvas(w, h)
    cv.rect(w / 2 - 6, 150, 12, h - 150, (60, 64, 68), outline=1.2)
    cv.rect(20, 10, w - 40, 150, (40, 80, 140), outline=2.2)
    cv.text('P', w / 2, 112, 96, (240, 240, 236), 'Jost-SemiBold.ttf', align='center')
    cv.rect(10, 170, w - 20, 60, (236, 232, 222), outline=1.8)
    cv.text('PRUEBA', w / 2, 210, 22, (30, 30, 30), 'Jost-SemiBold.ttf', spacing=3, align='center')
    return cv.finish(texture=0.8, seed=seed)


def hedge_fg(w=1024, h=300, seed=33):
    cv = Canvas(w, h)
    r = np.random.default_rng(seed)
    for i in range(26):
        x = r.uniform(0, w); y = r.uniform(80, 200); rr = r.uniform(50, 100)
        cv.ellipse(x, y, rr, rr * 0.8, (10, 20, 22))
    cv.rect(0, 180, w, h - 180, (10, 20, 22))
    for x in range(0, w, 64):
        cv.rect(x, 40, 8, h - 40, (6, 12, 16))
    cv.rect(0, 60, w, 8, (6, 12, 16))
    return soften(cv.finish(texture=0.4, seed=seed), 2.5)


def garage_exit(w=900, h=900, seed=34):
    """The dealership's garage mouth at the start of the drive."""
    cv = Canvas(w, h)
    cv.rect(0, 0, w, h, (196, 190, 181), shader=lin_grad((0, 0), (w, 0), [(210, 206, 198), (170, 166, 160)]), outline=2.0)
    cv.rect(140, 300, 620, h - 300, (30, 36, 42), outline=2.4)
    cv.rect(140, 300, 620, 60, (20, 24, 30))
    for x in range(160, 760, 120):
        cv.rect(x, 316, 70, 6, (255, 240, 210))
    cv.rect(220, 160, 460, 80, (14, 22, 30), outline=1.8)
    cv.text('HYUNDAI · SALIDA', w / 2, 212, 30, (232, 226, 214), 'Jost-Medium.ttf', spacing=6, align='center')
    return cv.finish(texture=1.0, seed=seed)


def cabin_interior(paint_w, paint_h):
    """Dark cabin backdrop that sits behind the translucent-glass car body."""
    from car_model import Camera, dlo, zside, LEN
    from build_cars import SCALE
    cv = Canvas(paint_w, paint_h)
    cam = Camera('side', size=(paint_w, paint_h), scale=SCALE, origin=(20, paint_h - 20))
    pts = [cam.p((x, y, 0)) for x, y in dlo()]
    cv.poly(pts, (22, 26, 30))
    # seat backs + headrests (dark)
    for sx in (2700, 1700):
        a = cam.p((sx - 120, 1100, 0)); b = cam.p((sx + 40, 1460, 0))
        cv.poly([(a[0], a[1]), (a[0] + 50, a[1]), (b[0] + 10, b[1] + 40), (b[0] - 30, b[1] + 40)], (36, 30, 28))
        cv.ellipse(b[0] - 10, b[1] + 10, 26, 34, (40, 34, 30))
    # steering wheel rim seen side-on
    s = cam.p((3200, 1200, 0))
    cv.poly([(s[0] - 10, s[1] - 60), (s[0] + 10, s[1] - 60), (s[0] + 18, s[1] + 50), (s[0] - 2, s[1] + 50)], (16, 16, 18))
    return cv.finish(texture=0.5, seed=5)


def build():
    out = {
        'sky': sky(), 'andes': andes(), 'skyline': skyline(), 'city_mid_a': city_mid(seed=23), 'city_mid_b': city_mid(seed=41),
        'tree': street_tree(), 'tree_b': street_tree(seed=44), 'lamp': street_lamp(), 'road': road(),
        'traffic_light': traffic_light(), 'lamp_red': lamp_glow((240, 70, 56)), 'lamp_amber': lamp_glow((246, 186, 70)),
        'lamp_green': lamp_glow((96, 226, 150)), 'stop_line': stop_line(), 'cone': cone(), 'van': van(),
        'sign_school': sign_school(), 'sign_school_end': sign_school(end=True), 'parking_box': parking_box(),
        'sign_parking': sign_parking(), 'hedge_fg': hedge_fg(), 'garage_exit': garage_exit(),
    }
    from PIL import Image as _I
    car = _I.open(ART_OUT + '/Vehicles/ioniq5_side_teal_cabin.png')
    out['cabin_interior'] = cabin_interior(*car.size)
    for k, v in out.items():
        save_png(v, 'Drive/' + k)
    return out


if __name__ == '__main__':
    out = build()
    print({k: v.size for k, v in out.items()})
