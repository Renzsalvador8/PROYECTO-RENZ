"""Hyundai showroom: modular painted pieces + intro exterior. Layout lives in levels.py."""
import math
import numpy as np
from PIL import Image
from env_kit import *
from common import *

WALL = (196, 190, 181)
WALL_D = (150, 148, 144)
MULL = (27, 50, 66)
CEIL = (22, 36, 48)
FLOOR = (46, 56, 64)
WARM = (240, 232, 214)
H_BAY = 860          # px, y from -2.4 (bottom) to +6.2 (top) at 100 px/unit


def city_far(day=True, w=2048, h=512, seed=4):
    cv = Canvas(w, h)
    if day:
        cv.vgrad(0, 0, w, h, [(178, 196, 206), (206, 214, 214), (222, 222, 216)], [0, 0.6, 1])
    else:
        cv.vgrad(0, 0, w, h, [(18, 34, 56), (46, 66, 88), (92, 98, 110)], [0, 0.65, 1])
    # Andes: two ridge layers + a snow-capped volcano
    for k, (base, amp, colr, sd) in enumerate([(300, 70, (126, 146, 160), 1), (350, 40, (104, 124, 140), 2)]):
        c = colr if day else tuple(int(v * 0.35) for v in colr)
        pts = ridge(80, w, base, amp, seed + sd, 5) + [(w, h), (0, h)]
        cv.poly(pts, c)
    vx = w * 0.62
    vol = [(vx - 300, 330), (vx - 60, 140), (vx - 20, 128), (vx + 30, 132), (vx + 80, 150), (vx + 320, 330)]
    cv.poly(vol + [(vx + 320, h), (vx - 300, h)], (118, 138, 152) if day else (30, 40, 56))
    snow = [(vx - 95, 172), (vx - 60, 140), (vx - 20, 128), (vx + 30, 132), (vx + 80, 150), (vx + 110, 175), (vx + 70, 168),
            (vx + 40, 182), (vx + 10, 170), (vx - 20, 186), (vx - 55, 176)]
    cv.poly(snow, (232, 236, 236) if day else (120, 130, 150), smooth=True)
    # skyline (Quito-like: low-rise + a few towers + a dome)
    r = np.random.default_rng(seed)
    x = 0
    while x < w:
        bw = r.uniform(40, 120)
        bh = r.uniform(40, 150) if r.random() > 0.15 else r.uniform(160, 240)
        c = (150, 166, 176) if day else (40, 56, 76)
        c = tuple(int(v * r.uniform(0.92, 1.06)) for v in c)
        cv.rect(x, h - 70 - bh, bw, bh + 70, c)
        if day:
            for wy in range(int(h - 60 - bh), h - 70, 14):
                cv.rect(x + 6, wy, bw - 12, 3, (170, 186, 194), alpha=0.6)
        else:
            for wy in range(int(h - 60 - bh), h - 70, 12):
                for wx in range(int(x + 5), int(x + bw - 8), 10):
                    if r.random() < 0.35:
                        cv.rect(wx, wy, 5, 4, (240, 200, 140), alpha=0.8)
        x += bw + r.uniform(2, 14)
    dome_x = w * 0.3
    cv.ellipse(dome_x, h - 220, 46, 40, (160, 172, 178) if day else (46, 60, 80))
    cv.rect(dome_x - 50, h - 222, 100, 160, (156, 168, 176) if day else (42, 56, 76))
    cv.rect(dome_x - 4, h - 300, 8, 50, (150, 160, 168) if day else (40, 52, 70))
    # haze band near the horizon
    cv.vgrad(0, h - 200, w, 200, [(220, 224, 222, 0), (220, 224, 222, 120)] if day else [(80, 90, 110, 0), (80, 90, 110, 90)])
    img = cv.finish(texture=0.8, seed=seed, mottling=0.03)
    return soften(img, 1.2)


def bay(kind='window', w=400, seed=0):
    """Back-wall module. Glass panes are semi-transparent so the city layer shows through."""
    h = H_BAY
    cv = Canvas(w, h)
    floor_y = h          # bottom edge = y -2.4 world (wall base)
    ceil_y = 180         # ceiling line at y = +4.4 world -> 620 px above base -> 860-620=240? keep 180 band
    if kind in ('window', 'window_b'):
        # frame
        cv.rect(0, ceil_y, w, h - ceil_y, MULL, alpha=0.0)
        glass = (150, 176, 186)
        cv.rect(0, ceil_y, w, h - ceil_y, glass, alpha=0.16)
        # reflection streaks on glass
        cv.poly([(w * 0.15, ceil_y), (w * 0.32, ceil_y), (w * 0.12, h), (-w * 0.05, h)], (255, 255, 255), alpha=0.07)
        cv.poly([(w * 0.6, ceil_y), (w * 0.66, ceil_y), (w * 0.5, h), (w * 0.44, h)], (255, 255, 255), alpha=0.06)
        # mullions
        cv.rect(0, ceil_y, 14, h - ceil_y, MULL, outline=1.2)
        cv.rect(w - 8, ceil_y, 8, h - ceil_y, MULL)
        if kind == 'window':
            cv.rect(w / 2 - 4, ceil_y, 8, h - ceil_y, MULL)
        tr = ceil_y + 230
        cv.rect(0, tr, w, 10, MULL)
        # low sill / base
        cv.rect(0, h - 40, w, 40, (34, 44, 52), outline=1.2)
    elif kind == 'solid':
        cv.vgrad(0, ceil_y, w, h - ceil_y, [WALL, WALL_D])
        cv.rect(0, ceil_y, w, h - ceil_y, WALL, alpha=0.0, outline=1.4)
        for x in range(0, w, 100):
            cv.line([(x, ceil_y + 4), (x, h - 44)], color=(160, 156, 150), width=1.2, alpha=0.6, wobble=0.2)
        cv.rect(0, h - 40, w, 40, (52, 58, 64), outline=1.2)
    elif kind == 'exit':
        cv.vgrad(0, ceil_y, w, h - ceil_y, [(70, 84, 96), (44, 56, 66)])
        dx, dw, dh = 90, w - 180, 470
        dy = h - 40 - dh
        cv.rect(dx - 16, dy - 16, dw + 32, dh + 16, (26, 34, 42), outline=1.8)
        cv.vgrad(dx, dy, dw, dh, [(176, 182, 182), (128, 136, 140)])
        for k in range(1, 9):
            yy = dy + dh * k / 9
            cv.line([(dx, yy), (dx + dw, yy)], color=(90, 98, 104), width=2.0, wobble=0.2)
        cv.rect(dx, dy, dw, dh, (0, 0, 0), alpha=0.0, outline=1.8)
        # sign
        cv.rect(w / 2 - 190, dy - 110, 380, 64, (14, 22, 30), outline=1.6)
        cv.text('PRUEBA DE MANEJO', w / 2, dy - 68, 26, (230, 226, 214), 'Jost-Medium.ttf', spacing=4, align='center')
        cv.rect(w / 2 - 40, dy - 40, 80, 6, (182, 120, 84))
        cv.rect(0, h - 40, w, 40, (34, 44, 52), outline=1.2)
    elif kind == 'brand':
        cv.vgrad(0, ceil_y, w, h - ceil_y, [(34, 54, 70), (22, 36, 48)])
        cv.rect(0, ceil_y, w, h - ceil_y, (0, 0, 0), alpha=0.0, outline=1.6)
        cy = ceil_y + 250
        # the official lockup (emblem over wordmark) is composited after the paint finish, so it stays crisp
        cv.glow(w / 2, cy, 220, (200, 220, 230), 0.12)
        cv.text('IONIQ  ·  PRUEBA DE EXCELENCIA', w / 2, cy + 205, 20, (150, 170, 182), 'Jost-Regular.ttf', spacing=6, align='center')
        cv.rect(0, h - 40, w, 40, (20, 28, 36), outline=1.2)
    # ceiling band (always)
    cv.vgrad(0, 0, w, ceil_y, [(16, 26, 36), CEIL])
    cv.rect(0, ceil_y - 10, w, 10, (12, 18, 26))
    for x in range(40, w, 200):
        cv.rect(x, ceil_y - 40, 120, 8, WARM)
        cv.glow(x + 60, ceil_y - 30, 110, (255, 240, 210), 0.10)
    img = cv.finish(texture=1.0, seed=seed + 11, streak=0.01)
    if kind == 'brand':
        import logos
        logos.paste_center(img, logos.mark('stacked', 250, (232, 230, 222)), w / 2, ceil_y + 250 + 45)
    return img


def floor_tile(w=512, h=320, seed=2):
    cv = Canvas(w, h)
    cv.vgrad(0, 0, w, h, [(70, 82, 90), (44, 54, 62), (30, 38, 46)], [0, 0.4, 1])
    # wall base reflection (bright line) and window reflections (vertical soft bars)
    cv.rect(0, 0, w, 6, (120, 134, 140), alpha=0.6)
    r = np.random.default_rng(seed)
    for k in range(3):
        x = k * w / 3 + r.uniform(0, 60)
        cv.poly([(x, 0), (x + 70, 0), (x + 90, h), (x + 10, h)], (220, 230, 232), alpha=0.06, blur=6)
    # tile joints (perspective-free, subtle)
    for x in range(0, w, 256):
        cv.line([(x, 0), (x, h)], color=(26, 34, 40), width=1.2, alpha=0.5, wobble=0.2)
    cv.line([(0, 110), (w, 110)], color=(26, 34, 40), width=1.0, alpha=0.4, wobble=0.2)
    img = cv.finish(texture=0.9, seed=seed, streak=0.05, streak_dir='v', mottling=0.06)
    # make tileable horizontally by cross-fading edges
    a = np.asarray(img).astype(np.float32)
    k = 40
    for i in range(k):
        t = i / k
        a[:, i] = a[:, i] * t + a[:, w - k + i] * (1 - t)
    a = a[:, :w - k]
    return pil_from(a)


def platform(w=820, h=150, seed=3):
    cv = Canvas(w, h)
    cv.ellipse(w / 2, h * 0.55, w * 0.49, h * 0.40, (30, 36, 42), outline=1.8)
    cv.ellipse(w / 2, h * 0.45, w * 0.48, h * 0.36, (98, 108, 114),
               shader=lin_grad((0, 0), (0, h), [(150, 158, 160), (86, 96, 104)]), outline=1.8)
    cv.ellipse(w / 2, h * 0.45, w * 0.40, h * 0.28, (120, 128, 132), alpha=0.25)
    cv.line([(w * 0.06, h * 0.52), (w * 0.94, h * 0.52)], color=(240, 230, 210), width=2.0, alpha=0.5, wobble=0)
    return cv.finish(texture=0.7, seed=seed)


def reception(w=760, h=330, seed=5):
    cv = Canvas(w, h)
    # walnut desk with bronze inlay and a small iMac-like screen
    cv.poly([(20, 90), (w - 20, 90), (w - 40, h - 10), (40, h - 10)], TWEED,
            shader=lin_grad((0, 90), (0, h), [(150, 112, 80), (96, 70, 50)]), outline=2.0)
    cv.rect(20, 76, w - 40, 22, (60, 46, 36), outline=1.6)
    cv.rect(60, 150, w - 120, 6, BRONZE, alpha=0.9)
    for x in range(80, w - 80, 46):
        cv.line([(x, 170), (x + 6, h - 20)], color=(80, 58, 42), width=1.2, alpha=0.6)
    cv.rect(470, 10, 150, 70, (20, 26, 30), outline=1.6)
    cv.rect(478, 18, 134, 54, (60, 96, 110), shader=lin_grad((478, 18), (612, 72), [(90, 130, 140), (30, 56, 70)]))
    cv.rect(535, 80, 20, 10, (40, 44, 48))
    # bell & card holder
    cv.ellipse(200, 72, 22, 12, (190, 150, 100), outline=1.4)
    cv.rect(120, 52, 46, 26, (230, 226, 214), outline=1.2)
    cv.text('BIENVENIDO', w / 2 - 140, 132, 22, (238, 226, 206), 'Jost-Medium.ttf', spacing=8)
    return cv.finish(texture=1.0, seed=seed)


def station_sign(title, sub, w=320, h=520, seed=6):
    cv = Canvas(w, h)
    cv.rect(w / 2 - 6, 140, 12, h - 150, (30, 36, 40), outline=1.2)
    cv.ellipse(w / 2, h - 8, 70, 10, (30, 36, 40), outline=1.2)
    cv.rect(10, 10, w - 20, 150, (14, 24, 34), outline=1.8)
    cv.text(title, w / 2, 70, 30, (232, 226, 214), 'Jost-Medium.ttf', spacing=5, align='center')
    cv.rect(w / 2 - 30, 88, 60, 4, BRONZE)
    cv.text(sub, w / 2, 126, 18, (150, 172, 184), 'Jost-Regular.ttf', spacing=3, align='center')
    return cv.finish(texture=0.8, seed=seed)


def brochure_stand(w=160, h=300, seed=7):
    cv = Canvas(w, h)
    cv.rect(w / 2 - 5, 120, 10, h - 128, (36, 40, 44), outline=1.2)
    cv.ellipse(w / 2, h - 6, 50, 8, (36, 40, 44), outline=1.2)
    cv.poly([(16, 20), (w - 16, 20), (w - 10, 128), (10, 128)], (60, 66, 72), outline=1.6)
    for i, c in enumerate([(220, 216, 206), (66, 106, 114), (182, 120, 84)]):
        cv.rect(26 + i * 38, 30 + i * 4, 34, 86, c, outline=1.0)
    return cv.finish(texture=0.8, seed=seed)


def coffee_station(w=300, h=330, seed=8):
    cv = Canvas(w, h)
    cv.rect(10, 140, w - 20, h - 148, (40, 46, 52), outline=1.8)
    cv.rect(10, 130, w - 20, 16, (150, 112, 80), outline=1.4)
    cv.rect(60, 40, 120, 92, (176, 180, 182), shader=lin_grad((60, 0), (180, 0), [(200, 204, 206), (120, 126, 130)]), outline=1.6)
    cv.rect(80, 92, 20, 26, (30, 30, 32))
    cv.ellipse(150, 64, 12, 12, (40, 44, 48))
    cv.rect(200, 100, 30, 32, (230, 226, 214), outline=1.2)
    cv.rect(236, 108, 24, 24, (230, 226, 214), outline=1.2)
    return cv.finish(texture=0.9, seed=seed)


def column_fg(w=170, h=1300, seed=9):
    cv = Canvas(w, h)
    cv.rect(10, 0, w - 20, h, (10, 18, 26), shader=lin_grad((10, 0), (w - 10, 0), [(14, 24, 34), (22, 36, 48), (8, 14, 20)]))
    cv.rect(10, 0, 6, h, (60, 80, 96), alpha=0.5)
    return soften(cv.finish(texture=0.6, seed=seed), 2.5)


def plant_fg(w=420, h=620, seed=10):
    cv = Canvas(w, h)
    plant(cv, w / 2, h - 4, h * 0.95, seed=seed, leaf=(12, 22, 26), pot=(8, 14, 20), dark=True)
    return soften(cv.finish(texture=0.4, seed=seed), 3.0)


def plant_mid(w=300, h=420, seed=11):
    cv = Canvas(w, h)
    plant(cv, w / 2, h - 4, h * 0.95, seed=seed, leaf=(60, 86, 70), pot=(196, 190, 181))
    return cv.finish(texture=0.9, seed=seed)


def light_shaft(w=700, h=1000):
    cv = Canvas(w, h)
    cv.poly([(w * 0.25, 0), (w * 0.55, 0), (w * 0.98, h), (w * 0.45, h)], (255, 250, 236), alpha=0.18, blur=40)
    a = cv.np()
    yy = np.linspace(1, 0.15, h)[:, None]
    a[:, :, 3] *= yy
    return pil_from(a)


def spot_cone(w=900, h=900):
    cv = Canvas(w, h)
    cv.poly([(w * 0.42, 0), (w * 0.58, 0), (w * 0.98, h * 0.92), (w * 0.02, h * 0.92)], (255, 246, 226), alpha=0.16, blur=30)
    cv.ellipse(w / 2, h * 0.92, w * 0.46, h * 0.06, (255, 246, 226), alpha=0.22, blur=20)
    a = cv.np()
    yy = np.linspace(0.35, 1.0, h)[:, None]
    a[:, :, 3] *= yy
    return pil_from(a)


def exterior(day=True, w=2048, h=1080, seed=12, top=300, ground_y=860, sign_dx=520, city_y=260):
    """Arrival shot: the dealership facade seen from the plaza. The title screen uses a lower framing
    (more sky) so the title lockup has room."""
    cv = Canvas(w, h)
    sky = [(150, 176, 194), (200, 210, 212), (226, 222, 212)] if day else [(10, 24, 44), (28, 50, 74), (96, 100, 108)]
    cv.vgrad(0, 0, w, h, sky, [0, 0.55, 0.8])
    far = city_far(day, w, 512, seed)
    cv.image(far, 0, city_y, w, 512)
    # building: long glass box, cantilevered roof, warm interior
    bx0, bx1 = 640, 2048
    interior = (226, 216, 196) if day else (220, 170, 110)
    cv.rect(bx0, top + 60, bx1 - bx0, ground_y - top - 60, interior,
            shader=lin_grad((0, top), (0, ground_y), [(214, 210, 200), (180, 176, 168)] if day else [(232, 186, 122), (150, 104, 66)]))
    # interior hints: cars + lights
    from car_model import Camera, CarPainter
    for i, (paint, xx) in enumerate((('white', 1020), ('bronze', 1560))):
        cam = Camera('side', size=(560, 230), scale=0.115, origin=(10, 222))
        car = CarPainter(cam, paint).render().image(seed=i)
        cv.image(car, xx, ground_y - 230, 560, 230, alpha=0.75)
    for x in range(bx0 + 40, bx1, 160):
        cv.rect(x, top + 72, 90, 5, (255, 246, 226))
    # glass + mullions
    cv.rect(bx0, top + 60, bx1 - bx0, ground_y - top - 60, (150, 180, 196) if day else (40, 60, 80), alpha=0.28)
    for x in range(bx0, bx1, 128):
        cv.rect(x, top + 60, 8, ground_y - top - 60, MULL)
    cv.rect(bx0, top + 330, bx1 - bx0, 8, MULL)
    # roof slab
    cv.poly([(bx0 - 120, top), (bx1, top), (bx1, top + 60), (bx0 - 80, top + 60)], (226, 224, 218) if day else (40, 48, 58),
            outline=2.2, shader=lin_grad((0, top), (0, top + 60), [(236, 234, 228), (182, 180, 176)] if day else [(52, 60, 70), (26, 32, 40)]))
    # entrance doors
    dx = 1300
    cv.rect(dx, ground_y - 330, 180, 330, (40, 60, 74), alpha=0.35, outline=2.0)
    cv.rect(dx + 88, ground_y - 330, 4, 330, MULL)
    cv.rect(dx - 30, ground_y - 360, 240, 26, MULL, outline=1.6)
    # plaza
    cv.vgrad(0, ground_y, w, h - ground_y, [(150, 150, 146), (110, 112, 112)] if day else [(40, 46, 54), (20, 26, 32)])
    for x in range(-200, w, 180):
        cv.line([(x, ground_y), (x - 160, h)], color=(90, 92, 92) if day else (20, 24, 30), width=1.4, alpha=0.5)
    cv.line([(0, ground_y), (w, ground_y)], color=(30, 30, 30), width=2.4)
    # reflections of the warm interior on the plaza at dusk
    if not day:
        cv.rect(bx0, ground_y + 2, bx1 - bx0, 120, (230, 180, 120), alpha=0.18, blur=18)
    # trees + street lamp on the left
    tree(cv, 220, ground_y, 520, seed=3, colr=(60, 82, 70) if day else (16, 26, 30), trunk=(50, 40, 32) if day else (10, 14, 18))
    tree(cv, 470, ground_y, 420, seed=8, colr=(66, 88, 74) if day else (18, 30, 34), trunk=(50, 40, 32) if day else (10, 14, 18))
    cv.rect(560, ground_y - 470, 10, 470, (30, 34, 38), outline=1.2)
    cv.rect(520, ground_y - 476, 64, 12, (30, 34, 38), outline=1.2)
    if not day:
        cv.glow(552, ground_y - 462, 140, (255, 214, 150), 0.35)
    img = cv.finish(texture=1.0, seed=seed, streak=0.01)
    # roof fascia: the official emblem + wordmark, side by side (composited after the finish: crisp)
    import logos
    lock = logos.lockup_h(40, (24, 40, 56) if day else (236, 232, 222), gap=0.42, word_scale=0.42)
    img.alpha_composite(lock, (int(bx0 + sign_dx), int(top + 30 - lock.height / 2)))
    return img


def build():
    out = {}
    out['city_far'] = city_far(True)
    for k in ('window', 'window_b', 'solid'):
        out['bay_' + k] = bay(k)
    out['bay_brand'] = bay('brand', 1200)
    out['bay_exit'] = bay('exit', 800)
    out['floor'] = floor_tile()
    out['platform'] = platform()
    out['reception'] = reception()
    out['sign_station1'] = station_sign('ESTACIÓN 01', 'EXTERIOR')
    out['sign_station2'] = station_sign('ESTACIÓN 02', 'INTERIOR')
    out['brochure_stand'] = brochure_stand()
    out['coffee_station'] = coffee_station()
    out['column_fg'] = column_fg()
    out['plant_fg'] = plant_fg()
    out['plant_mid'] = plant_mid()
    out['light_shaft'] = light_shaft()
    out['spot_cone'] = spot_cone()
    out['exterior_day'] = exterior(True)
    for name, img in out.items():
        save_png(img, 'Showroom/' + name)
    # title / menu background (dusk): lower framing, more sky for the title lockup
    save_png(exterior(False, top=470, ground_y=960, sign_dx=980, city_y=420), 'Menu/title_dusk')
    return out


if __name__ == '__main__':
    out = build()
    print({k: v.size for k, v in out.items()})
