"""Zenith Studio: a cinematic production studio with the awards stage."""
import math
import numpy as np
from PIL import Image
from env_kit import *
from common import *

H_BAY = 860
PANEL = (16, 34, 52)
PANEL_D = (10, 22, 36)
LED = (236, 226, 204)


def load(name):
    return Image.open(ART_OUT + '/Props/' + name + '.png')


def bay(kind, w=400, seed=0):
    cv = Canvas(w, H_BAY)
    top = 180
    cv.vgrad(0, top, w, H_BAY - top, [(22, 42, 62), PANEL_D])
    # acoustic panel seams
    for x in range(0, w, 100):
        cv.line([(x, top), (x, H_BAY - 40)], color=(8, 18, 28), width=2.0, alpha=0.8, wobble=0.2)
    if kind == 'led':
        cv.rect(w / 2 - 3, top + 30, 6, H_BAY - top - 90, LED)
        cv.rect(w / 2 - 14, top + 30, 28, H_BAY - top - 90, LED, alpha=0.12, blur=10)
    if kind == 'storyboard':
        bx, by, bw, bh = 30, top + 120, w * 2 - 60, 380
    if kind == 'logo':
        logo = Image.open(UI_OUT + '/zenith_logo_lockup.png')
        lw = int(w * 0.62); lh = int(logo.height * lw / logo.width)
        cv.glow(w / 2, top + 260, 300, (90, 130, 170), 0.35)
        cv.image(logo, w / 2 - lw / 2, top + 260 - lh / 2, lw, lh, alpha=0.95)
        cv.text('CREATE BEYOND REAL', w / 2, top + 260 + lh / 2 + 54, 20, (150, 176, 196), 'Jost-Regular.ttf', spacing=8, align='center')
    cv.rect(0, H_BAY - 40, w, 40, (8, 14, 22), outline=1.2)
    # ceiling band with track lights
    cv.vgrad(0, 0, w, top, [(6, 12, 20), (12, 22, 34)])
    cv.rect(0, top - 18, w, 6, (30, 40, 52))
    for x in range(60, w, 160):
        cv.poly([(x, top - 14), (x + 18, top - 14), (x + 26, top + 18), (x - 8, top + 18)], (40, 46, 54), outline=1.0)
        cv.glow(x + 9, top + 18, 90, (255, 236, 200), 0.12)
    return cv.finish(texture=1.0, seed=seed + 50, streak=0.01)


def storyboard(w=900, h=440, seed=51):
    """Cork board with storyboard frames sketching the game itself."""
    cv = Canvas(w, h)
    cv.rect(0, 0, w, h, (120, 96, 72), outline=2.4, shader=lin_grad((0, 0), (0, h), [(136, 108, 80), (100, 78, 58)]))
    r = np.random.default_rng(seed)
    frames = [('INT. CONCESIONARIO', 'lupa'), ('EXT. FAROS', 'faros'), ('INT. TABLERO', 'puntos'),
              ('EXT. CIUDAD', 'auto'), ('INT. ZENITH', 'premios'), ('FIN', 'bigote')]
    for i, (cap, kind) in enumerate(frames):
        fx = 30 + (i % 3) * 290 + r.uniform(-6, 6)
        fy = 26 + (i // 3) * 206 + r.uniform(-4, 4)
        fw, fh = 250, 170
        cv.rect(fx + 4, fy + 6, fw, fh, (0, 0, 0), alpha=0.3, blur=4)
        cv.rect(fx, fy, fw, fh, (232, 226, 212), outline=1.4)
        cv.rect(fx + 10, fy + 10, fw - 20, fh - 46, (246, 242, 232), outline=1.0)
        ix, iy, iw, ih = fx + 10, fy + 10, fw - 20, fh - 46
        sk = (60, 56, 52)
        if kind == 'lupa':
            cv.line([(ix + 60, iy + ih), (ix + 64, iy + 40)], color=sk, width=2)
            cv.ellipse(ix + 64, iy + 30, 12, 14, (0, 0, 0), alpha=0.0, outline=2, ocolor=sk)
            cv.ellipse(ix + 130, iy + 50, 22, 22, (0, 0, 0), alpha=0.0, outline=2, ocolor=sk)
            cv.line([(ix + 115, iy + 66), (ix + 98, iy + 86)], color=sk, width=3)
        elif kind == 'faros':
            for k in range(6):
                cv.rect(ix + 40 + k * 22, iy + 40, 14, 14, (0, 0, 0), alpha=0.0, outline=1.6, ocolor=sk)
        elif kind == 'puntos':
            cv.ellipse(ix + iw / 2, iy + ih / 2 + 10, 70, 46, (0, 0, 0), alpha=0.0, outline=2, ocolor=sk)
            for k in range(4):
                cv.ellipse(ix + iw / 2 - 30 + k * 20, iy + ih / 2 + 10, 4, 4, sk)
        elif kind == 'auto':
            cv.line([(ix + 20, iy + 80), (ix + 60, iy + 54), (ix + 150, iy + 52), (ix + 196, iy + 74), (ix + 200, iy + 90), (ix + 20, iy + 92), (ix + 20, iy + 80)], color=sk, width=2)
            cv.ellipse(ix + 60, iy + 92, 12, 12, (0, 0, 0), alpha=0.0, outline=2, ocolor=sk)
            cv.ellipse(ix + 160, iy + 92, 12, 12, (0, 0, 0), alpha=0.0, outline=2, ocolor=sk)
        elif kind == 'premios':
            cv.poly([(ix + 80, iy + ih - 10), (ix + 92, iy + 20), (ix + 104, iy + ih - 10)], (0, 0, 0), alpha=0.0, outline=2, ocolor=sk)
            cv.poly([(ix + 130, iy + ih - 10), (ix + 130, iy + 60), (ix + 150, iy + 60), (ix + 150, iy + 44), (ix + 170, iy + 44), (ix + 170, iy + ih - 10)], (0, 0, 0), alpha=0.0, outline=2, ocolor=sk)
        elif kind == 'bigote':
            cv.line([(ix + 60, iy + 60), (ix + 90, iy + 50), (ix + 115, iy + 58), (ix + 140, iy + 50), (ix + 170, iy + 60)], color=sk, width=5, smooth=True)
        cv.text(cap, fx + fw / 2, fy + fh - 14, 15, (70, 60, 52), 'Jost-Medium.ttf', spacing=2, align='center')
        cv.ellipse(fx + fw / 2, fy + 4, 6, 6, (190, 60, 50), outline=1.0)
    return cv.finish(texture=1.0, seed=seed)


def poster(title, sub, kind, w=300, h=420, seed=52):
    cv = Canvas(w, h)
    cv.rect(0, 0, w, h, (10, 10, 12), outline=2.4)
    cv.rect(14, 14, w - 28, h - 28, (20, 30, 40))
    ix, iy, iw, ih = 14, 14, w - 28, h - 28
    if kind == 'car':
        cv.vgrad(ix, iy, iw, ih, [(30, 52, 70), (12, 20, 30)])
        cv.ellipse(ix + iw / 2, iy + ih * 0.55, 90, 14, (230, 220, 200), alpha=0.3, blur=6)
        cv.poly([(ix + 40, iy + ih * 0.55), (ix + 70, iy + ih * 0.45), (ix + 200, iy + ih * 0.45), (ix + 236, iy + ih * 0.55)], (180, 120, 84))
    elif kind == 'mountain':
        cv.vgrad(ix, iy, iw, ih, [(182, 120, 84), (40, 30, 30)])
        cv.poly([(ix, iy + ih * 0.7), (ix + iw * 0.45, iy + ih * 0.3), (ix + iw, iy + ih * 0.7), (ix + iw, iy + ih), (ix, iy + ih)], (20, 24, 30))
        cv.ellipse(ix + iw * 0.7, iy + ih * 0.28, 26, 26, (240, 226, 200))
    elif kind == 'tester':
        cv.vgrad(ix, iy, iw, ih, [(214, 203, 192), (160, 150, 140)])
        cv.line([(ix + iw * 0.3, iy + ih * 0.42), (ix + iw * 0.45, iy + ih * 0.38), (ix + iw * 0.55, iy + ih * 0.42), (ix + iw * 0.65, iy + ih * 0.38), (ix + iw * 0.8, iy + ih * 0.42)],
                color=(60, 40, 30), width=10, smooth=True)
        cv.ellipse(ix + iw * 0.55, iy + ih * 0.3, 40, 40, (0, 0, 0), alpha=0.0, outline=4, ocolor=(60, 40, 30))
        cv.line([(ix + iw * 0.43, iy + ih * 0.38), (ix + iw * 0.3, iy + ih * 0.6)], color=(60, 40, 30), width=6)
    cv.text(title, w / 2, h - 66, 24, (236, 230, 216), 'CormorantGaramond-SemiBold.ttf', spacing=3, align='center')
    cv.text(sub, w / 2, h - 40, 11, (170, 180, 186), 'Jost-Regular.ttf', spacing=3, align='center')
    return cv.finish(texture=0.9, seed=seed)


def desk(w=760, h=520, seed=53):
    """Editing workstation: desk + two monitors with a timeline, lamp, mug, laptop (props from the sheet)."""
    cv = Canvas(w, h)
    top = h - 230
    cv.rect(20, top, w - 40, 22, (60, 44, 34), outline=2.0, shader=lin_grad((0, top), (0, top + 22), [(120, 88, 64), (70, 52, 40)]))
    cv.rect(40, top + 22, 16, h - top - 22, (30, 30, 34), outline=1.2)
    cv.rect(w - 56, top + 22, 16, h - top - 22, (30, 30, 34), outline=1.2)
    for mx, mw in ((110, 280), (410, 230)):
        cv.rect(mx + mw / 2 - 8, top - 50, 16, 50, (26, 28, 32))
        cv.rect(mx, top - 230, mw, 180, (12, 12, 14), outline=2.0)
        sx0, sy0, sw, sh = mx + 8, top - 222, mw - 16, 164
        cv.rect(sx0, sy0, sw, sh, (20, 30, 40))
        if mx == 110:  # timeline
            cv.rect(sx0 + 6, sy0 + 6, sw - 12, 80, (40, 60, 72), shader=lin_grad((sx0, sy0), (sx0 + sw, sy0 + 80), [(60, 90, 100), (182, 120, 84)]))
            for k in range(4):
                y = sy0 + 96 + k * 16
                x = sx0 + 10
                r = np.random.default_rng(seed + k)
                while x < sx0 + sw - 20:
                    ww = r.uniform(20, 70)
                    cv.rect(x, y, ww, 11, [(86, 120, 137), (182, 120, 84), (140, 150, 120), (110, 100, 150)][k], alpha=0.85)
                    x += ww + 3
            cv.rect(sx0 + sw * 0.62, sy0 + 88, 2, 72, (240, 80, 60))
        else:  # colour grading wheels
            for k in range(3):
                cxx = sx0 + 36 + k * 70
                cv.ellipse(cxx, sy0 + 70, 28, 28, (40, 50, 60), outline=1.2, ocolor=(120, 130, 140))
                cv.ellipse(cxx + 6, sy0 + 64, 4, 4, (236, 230, 216))
            cv.line([(sx0 + 10, sy0 + 140), (sx0 + 60, sy0 + 120), (sx0 + 120, sy0 + 130), (sx0 + sw - 10, sy0 + 110)], color=(182, 120, 84), width=2, wobble=0.0)
    lamp = load('lamp'); cv.image(lamp, w - 250, top - 175, 150, 166)
    mug = load('mug'); cv.image(mug, 660, top - 52, 52, 51)
    cv.rect(140, top - 18, 220, 14, (30, 32, 36), outline=1.2)   # keyboard
    return cv.finish(texture=0.9, seed=seed)


def tripod_camera(w=360, h=640, seed=54):
    cv = Canvas(w, h)
    cx = w / 2
    for dx in (-130, 0, 120):
        cv.line([(cx, 250), (cx + dx, h - 6)], color=(30, 32, 36), width=7)
    cv.rect(cx - 30, 230, 60, 30, (40, 42, 46), outline=1.4)
    cam = load('camera')
    cv.image(cam, cx - 150, 60, 300, 236)
    return cv.finish(texture=0.6, seed=seed)


def softbox(w=360, h=820, seed=55):
    cv = Canvas(w, h)
    cx = w / 2
    for dx in (-110, 0, 100):
        cv.line([(cx, 420), (cx + dx, h - 6)], color=(30, 32, 36), width=6)
    cv.line([(cx, 420), (cx, 190)], color=(30, 32, 36), width=8)
    cv.poly([(cx - 150, 30), (cx + 150, 60), (cx + 150, 280), (cx - 150, 310)], (24, 26, 30), outline=2.0)
    cv.poly([(cx - 136, 46), (cx + 136, 72), (cx + 136, 268), (cx - 136, 294)], (240, 232, 214))
    cv.glow(cx, 170, 260, (255, 240, 214), 0.25)
    return cv.finish(texture=0.6, seed=seed)


def pedestal(w=300, h=420, seed=56):
    cv = Canvas(w, h)
    cv.ellipse(w / 2, h - 10, w * 0.46, 14, (0, 0, 0), alpha=0.5, blur=6)
    cv.poly([(30, 50), (w - 30, 50), (w - 40, h - 14), (40, h - 14)], (20, 24, 30), outline=2.2,
            shader=lin_grad((30, 0), (w - 30, 0), [(48, 56, 66), (24, 30, 38), (12, 16, 22)]))
    cv.poly([(16, 26), (w - 16, 26), (w - 30, 52), (30, 52)], (60, 68, 78), outline=2.0,
            shader=lin_grad((0, 26), (0, 52), [(110, 120, 130), (40, 48, 56)]))
    cv.line([(40, 60), (40, h - 20)], color=(120, 130, 140), width=2, alpha=0.4)
    cv.rect(w / 2 - 70, h / 2 - 10, 140, 34, (182, 120, 84), alpha=0.18)
    return cv.finish(texture=0.8, seed=seed)


def plaque(text, w=300, h=70, seed=57):
    cv = Canvas(w, h)
    cv.rect(0, 0, w, h, (182, 120, 84), outline=1.8, shader=lin_grad((0, 0), (w, h), [(214, 160, 116), (140, 90, 60)]))
    cv.text(text, w / 2, h / 2 + 9, 22, (40, 26, 18), 'Jost-Medium.ttf', spacing=4, align='center')
    return cv.finish(texture=0.6, seed=seed)


def stage_backdrop(w=1400, h=860, seed=58):
    cv = Canvas(w, h)
    cv.vgrad(0, 180, w, h - 180, [(14, 28, 44), (6, 12, 20)])
    cv.glow(w / 2, 420, 600, (70, 100, 140), 0.35)
    cv.rect(0, h - 40, w, 40, (6, 10, 16))
    for x in (60, w - 66):
        cv.rect(x, 200, 6, h - 260, LED)
        cv.rect(x - 10, 200, 26, h - 260, LED, alpha=0.1, blur=8)
    cv.text('PREMIOS', w / 2, 330, 30, (182, 120, 84), 'Jost-Medium.ttf', spacing=16, align='center')
    cv.text('Excelencia en narrativa visual', w / 2, 380, 30, (196, 196, 190), 'CormorantGaramond-Italic.ttf', align='center')
    cv.vgrad(0, 0, w, 180, [(6, 12, 20), (12, 22, 34)])
    return cv.finish(texture=1.0, seed=seed)


def floor_tile(w=512, h=320, seed=59):
    cv = Canvas(w, h)
    cv.vgrad(0, 0, w, h, [(34, 44, 56), (16, 22, 30), (8, 12, 18)], [0, 0.45, 1])
    cv.rect(0, 0, w, 5, (80, 96, 110), alpha=0.6)
    for k in range(2):
        x = k * w / 2 + 80
        cv.poly([(x, 0), (x + 30, 0), (x + 40, h), (x + 6, h)], (236, 226, 204), alpha=0.06, blur=6)
    img = cv.finish(texture=0.9, seed=seed, streak=0.04, streak_dir='v', mottling=0.06)
    a = np.asarray(img).astype(np.float32)
    k = 40
    for i in range(k):
        t = i / k
        a[:, i] = a[:, i] * t + a[:, w - k + i] * (1 - t)
    return pil_from(a[:, :w - k])


def boom_fg(w=1400, h=500, seed=60):
    cv = Canvas(w, h)
    cv.line([(0, 380), (w * 0.8, 120)], color=(4, 8, 12), width=26)
    cv.rect(w * 0.78, 80, 120, 90, (4, 8, 12))
    cv.line([(w * 0.84, 170), (w * 0.84, 260)], color=(4, 8, 12), width=6)
    return soften(cv.finish(texture=0.3, seed=seed), 3.0)


def build():
    out = {}
    for k in ('plain', 'led'):
        out['bay_' + k] = bay(k)
    out['bay_logo'] = bay('logo', 1000)
    out['storyboard'] = storyboard()
    out['poster_car'] = poster('IONIQ', 'ZENITH STUDIO PRESENTA', 'car', seed=61)
    out['poster_mountain'] = poster('ANDES', 'UNA HISTORIA DE ALTURA', 'mountain', seed=62)
    out['poster_tester'] = poster('THE TESTER', 'NADA ES PERFECTO', 'tester', seed=63)
    out['desk'] = desk()
    out['tripod_camera'] = tripod_camera()
    out['softbox'] = softbox()
    out['pedestal'] = pedestal()
    out['plaque_lux'] = plaque('LUX GRAND PRIX')
    out['plaque_effie'] = plaque('EFFIE · BRONCE')
    out['stage'] = stage_backdrop()
    out['floor'] = floor_tile()
    out['boom_fg'] = boom_fg()
    for k, v in out.items():
        save_png(v, 'Zenith/' + k)
    return out


if __name__ == '__main__':
    out = build()
    print({k: v.size for k, v in out.items()})
