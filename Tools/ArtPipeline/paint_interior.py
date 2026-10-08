"""IONIQ 5 cabin (view from between the rear seats) for the interior detail test."""
import math
import numpy as np
from PIL import Image
from env_kit import *
from common import *

W, H = 1920, 1080
DASH_D = (34, 38, 43)
DASH_L = (196, 190, 180)
TRIM_C = (24, 26, 30)


def build():
    cv = Canvas(W, H, clear=(20, 26, 32))
    # --- windshield: blurred showroom outside -------------------------------------------
    ws = [(150, 40), (1770, 40), (1600, 470), (320, 470)]
    out = Canvas(W, H)
    out.vgrad(0, 0, W, 520, [(150, 168, 178), (206, 212, 210), (120, 130, 136)], [0, 0.55, 1])
    for x in range(-100, W, 260):
        out.rect(x, 60, 130, 360, (232, 236, 232), alpha=0.5)
    out.rect(0, 340, W, 130, (60, 70, 80), alpha=0.7)
    out.ellipse(1200, 420, 300, 60, (90, 110, 116), alpha=0.8)
    for x in range(80, W, 220):
        out.rect(x, 40, 120, 10, (255, 246, 226))
    bl = soften(out.finish(texture=0.0), 9)
    cv.clip(ws); cv.image(bl, 0, 0); cv.unclip()
    # reflections on glass
    cv.poly([(700, 40), (900, 40), (760, 470), (600, 470)], (255, 255, 255), alpha=0.05)
    # headliner and A pillars
    cv.poly([(0, 0), (W, 0), (W, 60), (0, 60)], (40, 42, 46))
    cv.poly([(0, 0), (150, 40), (320, 470), (230, 560), (0, 640)], (46, 48, 52), outline=2.0,
            shader=lin_grad((0, 0), (300, 500), [(70, 72, 76), (34, 36, 40)]))
    cv.poly([(W, 0), (1770, 40), (1600, 470), (1690, 560), (W, 640)], (46, 48, 52), outline=2.0,
            shader=lin_grad((W, 0), (1620, 500), [(70, 72, 76), (34, 36, 40)]))
    cv.line([(150, 40), (1770, 40)], width=2.4)
    # rear-view mirror
    cv.rect(948, 40, 24, 50, (30, 32, 36))
    cv.poly([(860, 86), (1060, 86), (1052, 140), (868, 140)], (28, 30, 34), outline=2.0, smooth=False)
    cv.poly([(872, 94), (1048, 94), (1042, 132), (878, 132)], (120, 136, 144), shader=lin_grad((872, 94), (1048, 132), [(150, 166, 172), (70, 84, 92)]))
    # --- dashboard ------------------------------------------------------------------------
    cv.poly([(320, 470), (1600, 470), (1760, 560), (160, 560)], DASH_D, outline=2.2,
            shader=lin_grad((0, 470), (0, 560), [(28, 31, 35), (54, 58, 62)]))
    cv.line([(330, 474), (1590, 474)], color=(90, 96, 100), width=1.5, alpha=0.6)
    # light lower dash
    cv.poly([(160, 560), (1760, 560), (1840, 720), (80, 720)], DASH_L, outline=2.2,
            shader=lin_grad((0, 560), (0, 720), [(214, 208, 198), (170, 164, 156)]))
    # ambient light strip
    cv.line([(170, 566), (1750, 566)], color=(250, 214, 168), width=3.0, wobble=0.0)
    cv.rect(170, 562, 1580, 10, (250, 214, 168), alpha=0.25, blur=6)
    # air vents (long slim vent across the passenger side + centre module)
    cv.poly([(1180, 600), (1700, 600), (1716, 646), (1170, 646)], (22, 24, 28), outline=1.8)
    for k in range(5):
        y = 606 + k * 8
        cv.line([(1188, y), (1704, y + 1)], color=(70, 76, 82), width=2.2, wobble=0.0)
    # centre vent module (target: slats)
    vx, vy, vw, vh = 1000, 596, 150, 70
    cv.poly([(vx, vy), (vx + vw, vy), (vx + vw + 4, vy + vh), (vx - 4, vy + vh)], (18, 20, 24), outline=2.0)
    for k in range(6):
        y = vy + 8 + k * 10
        cv.line([(vx + 6, y), (vx + vw - 6, y)], color=(122, 128, 134), width=3.0, wobble=0.0)
        cv.line([(vx + 6, y + 2), (vx + vw - 6, y + 2)], color=(40, 44, 48), width=1.2, wobble=0.0)
    cv.ellipse(vx + vw / 2, vy + vh / 2, 6, 6, (200, 204, 206))
    # hazard button
    cv.rect(1172, 664, 44, 24, (40, 44, 48), outline=1.4)
    cv.poly([(1194, 668), (1206, 684), (1182, 684)], (220, 70, 60))
    # glovebox drawer line
    cv.line([(1260, 700), (1800, 700)], color=(140, 134, 126), width=2.0)
    cv.rect(1480, 676, 90, 8, (120, 114, 106), alpha=0.8)
    # --- panoramic display ------------------------------------------------------------------
    dx0, dy0, dx1, dy1 = 380, 448, 1080, 578
    cv.poly([(dx0, dy0), (dx1, dy0 + 6), (dx1, dy1 + 2), (dx0, dy1)], (14, 16, 18), outline=2.4)
    cv.poly([(dx0 + 10, dy0 + 10), (dx1 - 10, dy0 + 15), (dx1 - 10, dy1 - 8), (dx0 + 10, dy1 - 10)], (16, 30, 40),
            shader=lin_grad((dx0, dy0), (dx1, dy1), [(22, 40, 52), (12, 22, 30)]))
    mid = (dx0 + dx1) / 2
    cv.line([(mid, dy0 + 14), (mid, dy1 - 10)], color=(40, 60, 72), width=1.2)
    # cluster
    cv.text('0', dx0 + 120, dy0 + 82, 52, (230, 236, 236), 'Jost-Light.ttf', align='center')
    cv.text('km/h', dx0 + 120, dy0 + 104, 14, (140, 170, 180), 'Jost-Regular.ttf', spacing=2, align='center')
    cv.line([(dx0 + 200, dy0 + 90), (dx0 + 320, dy0 + 90)], color=(90, 200, 190), width=4, wobble=0)
    cv.text('481 km', dx0 + 260, dy0 + 76, 18, (200, 220, 222), 'Jost-Regular.ttf', align='center')
    cv.text('P  R  N  D', dx0 + 260, dy0 + 50, 15, (140, 170, 180), 'Jost-Medium.ttf', spacing=2, align='center')
    # infotainment: map + clock (target 4)
    cv.rect(mid + 16, dy0 + 22, 220, 92, (26, 44, 54), outline=0.0)
    for k in range(6):
        cv.line([(mid + 20 + k * 40, dy0 + 24), (mid + 60 + k * 28, dy0 + 112)], color=(52, 76, 86), width=2.0, wobble=0.0)
    cv.line([(mid + 30, dy0 + 90), (mid + 120, dy0 + 70), (mid + 200, dy0 + 84)], color=(110, 200, 190), width=3.0, wobble=0.0)
    cv.text('10:08', dx1 - 70, dy0 + 70, 34, (236, 240, 240), 'Jost-Regular.ttf', align='center')
    cv.text('JUE 8 OCT', dx1 - 70, dy0 + 94, 12, (140, 170, 180), 'Jost-Regular.ttf', spacing=2, align='center')
    # --- steering wheel (target 1: four dots = Morse "H") ------------------------------------
    sx, sy = 640, 800
    cv.rect(sx - 40, 640, 80, 150, (26, 28, 32), outline=1.8)   # column
    # drive selector stalk (column, right)
    cv.poly([(sx + 40, 680), (sx + 190, 650), (sx + 196, 668), (sx + 44, 702)], (36, 38, 42), outline=1.6)
    cv.ellipse(sx + 196, 659, 18, 16, (40, 42, 46), outline=1.6)
    # rim
    cv.ellipse(sx, sy, 300, 250, (20, 22, 26), alpha=0.0, outline=0)
    rim = [(sx + 300 * math.cos(t), sy + 250 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 90)]
    cv.line(rim + [rim[0]], color=(26, 28, 31), width=46, wobble=0.0)
    cv.line(rim[50:85], color=(70, 74, 78), width=6, wobble=0.0, alpha=0.6)
    cv.line(rim + [rim[0]], color=(12, 13, 15), width=2.0, wobble=0.0)
    inner = [(sx + 277 * math.cos(t), sy + 228 * math.sin(t)) for t in np.linspace(0, 2 * math.pi, 90)]
    cv.line(inner + [inner[0]], color=(10, 10, 12), width=2.0, wobble=0.0)
    # two spokes + pad
    cv.poly([(sx - 290, sy + 30), (sx - 120, sy - 10), (sx - 120, sy + 70), (sx - 280, sy + 90)], (40, 42, 46), outline=2.0)
    cv.poly([(sx + 290, sy + 30), (sx + 120, sy - 10), (sx + 120, sy + 70), (sx + 280, sy + 90)], (40, 42, 46), outline=2.0)
    pad = [(sx - 130, sy - 40), (sx + 130, sy - 40), (sx + 140, sy + 90), (sx - 140, sy + 90)]
    cv.poly(pad, (46, 50, 54), outline=2.4, shader=lin_grad((0, sy - 40), (0, sy + 90), [(66, 70, 74), (36, 40, 44)]))
    for k in range(4):
        cv.ellipse(sx - 45 + k * 30, sy + 22, 7, 7, (214, 218, 220))
        cv.glow(sx - 45 + k * 30, sy + 22, 18, (230, 240, 240), 0.25)
    # spoke buttons
    for k in range(3):
        cv.ellipse(sx - 220 + k * 30, sy + 40, 9, 8, (90, 94, 98))
        cv.ellipse(sx + 160 + k * 30, sy + 40, 9, 8, (90, 94, 98))
    # --- centre console (Universal Island) ----------------------------------------------------
    cv.poly([(840, 720), (1080, 720), (1260, 1080), (660, 1080)], (180, 174, 166), outline=2.2,
            shader=lin_grad((0, 720), (0, 1080), [(204, 198, 190), (150, 144, 136)]))
    cv.poly([(870, 760), (1050, 760), (1090, 860), (830, 860)], (34, 38, 42), outline=1.8)     # wireless pad
    cv.line([(900, 790), (1030, 790)], color=(70, 76, 82), width=1.4, wobble=0.0)
    for cxx in (880, 1040):
        cv.ellipse(cxx, 940, 62, 30, (40, 42, 46), outline=1.8)       # cup holders
        cv.ellipse(cxx, 946, 52, 22, (24, 26, 28))
    cv.rect(930, 1000, 60, 14, (40, 42, 46), outline=1.2)            # usb
    # --- front seats (backs) ------------------------------------------------------------------
    seatL = [(0, 640), (120, 600), (300, 630), (390, 740), (410, 1080), (0, 1080)]
    cv.poly(seatL, (60, 50, 44), outline=2.6, smooth=True, shader=lin_grad((0, 600), (560, 1080), [(92, 76, 64), (40, 32, 28)]))
    seatR = [(1920, 620), (1780, 590), (1600, 610), (1480, 720), (1440, 1080), (1920, 1080)]
    cv.poly(seatR, (60, 50, 44), outline=2.6, smooth=True, shader=lin_grad((1920, 600), (1360, 1080), [(92, 76, 64), (40, 32, 28)]))
    # headrests
    cv.poly([(60, 470), (250, 462), (262, 600), (50, 606)], (70, 58, 50), outline=2.4, smooth=True)
    cv.poly([(1640, 450), (1830, 458), (1840, 596), (1626, 588)], (70, 58, 50), outline=2.4, smooth=True)
    # stitching on the right seat bolster (target 2): double running stitch
    st = [(1545, 690), (1515, 770), (1495, 870), (1484, 980), (1480, 1080)]
    for off in (0, 14):
        pts = [(x + off, y) for x, y in st]
        cv.line(pts, color=(214, 196, 168), width=2.6, wobble=0.0, smooth=True)
    a = cv.np()
    # turn the stitch lines into dashes by masking every other segment
    # (done by overpainting short gaps)
    gap = Canvas(W, H)
    for off in (0, 14):
        for i in range(0, 60):
            t = i / 60.0
            k = min(int(t * (len(st) - 1)), len(st) - 2)
            u = t * (len(st) - 1) - k
            x = st[k][0] + (st[k + 1][0] - st[k][0]) * u + off
            y = st[k][1] + (st[k + 1][1] - st[k][1]) * u
            if i % 2 == 0:
                gap.ellipse(x, y, 4.5, 4.5, (0, 0, 0))
    g = gap.np()[:, :, 3:4] / 255.0
    seat_col = np.array([66, 54, 46], np.float32)
    a[:, :, :3] = a[:, :, :3] * (1 - g) + seat_col * g
    cv2 = Canvas(W, H)
    cv2.image(pil_from(a), 0, 0)
    # seat panel seams
    cv2.line([(1680, 620), (1650, 1080)], color=(36, 28, 24), width=2.0, alpha=0.7)
    cv2.line([(220, 630), (260, 1080)], color=(36, 28, 24), width=2.0, alpha=0.7)
    # door handle/pocket at the far left
    cv2.rect(0, 640, 60, 26, (180, 174, 166), outline=1.4)
    img = cv2.finish(texture=0.9, seed=31, mottling=0.04, grain=0.03)
    save_png(img, 'Inspection/ioniq5_interior')

    targets = {
        'volante': {'center': [sx, sy + 22], 'radius': 70},
        'costura': {'center': [1505, 860], 'radius': 70},
        'rejilla': {'center': [vx + vw / 2, vy + vh / 2], 'radius': 70},
        'reloj': {'center': [dx1 - 70, dy0 + 62], 'radius': 62},
    }
    decoys = {
        'espejo': {'center': [960, 112], 'radius': 80},
        'portavasos': {'center': [960, 940], 'radius': 110},
        'cargador': {'center': [960, 810], 'radius': 70},
        'guantera': {'center': [1520, 690], 'radius': 90},
        'palanca': {'center': [sx + 190, 659], 'radius': 50},
        'velocimetro': {'center': [dx0 + 120, dy0 + 70], 'radius': 70},
        'reposacabezas': {'center': [156, 534], 'radius': 90},
        'luz_ambiental': {'center': [1400, 566], 'radius': 60},
        'emergencia': {'center': [1194, 676], 'radius': 34},
        'parabrisas': {'center': [1300, 250], 'radius': 160},
    }
    # clue crops (2x magnified details shown on the notebook cards)
    clues = {}
    for name, t in targets.items():
        cx, cy = t['center']
        r = 56
        crop = img.crop((int(cx - r * 1.4), int(cy - r), int(cx + r * 1.4), int(cy + r)))
        crop = crop.resize((int(r * 2.8 * 2), int(r * 2 * 2)), Image.LANCZOS)
        save_png(crop, 'Inspection/clue_' + name)
        clues[name] = 'Art/Inspection/clue_' + name
    save_json({'size': [W, H], 'targets': targets, 'decoys': decoys, 'clues': clues}, 'Inspection/interior')
    return img


if __name__ == '__main__':
    img = build()
    img.convert('RGB').resize((960, 540)).save(SCRATCH + '/interior.png')
