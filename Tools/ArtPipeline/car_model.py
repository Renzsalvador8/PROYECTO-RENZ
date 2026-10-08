"""A stylised Hyundai IONIQ 5 built as a light 3D construction (millimetres) and rendered in the
game's ink + gouache style. The same model provides the side view (showroom / test drive) and the
front three-quarter close-up used by the exterior inspection.

Car frame: x forward (0 = rear bumper, 4635 = front), y up (0 = ground), z towards the car's LEFT
(driver side). A camera on +z sees the left side with the car facing screen-right.
"""
import math
import numpy as np
import skia
from PIL import Image
from paint import *

LEN, WB, R_AX, F_AX = 4635.0, 3000.0, 800.0, 3800.0
WHEEL_R, TIRE_W = 365.0, 255.0
HALF_W = 945.0

PAINTS = {
    'teal': dict(base=(66, 106, 114), lit=(140, 178, 180), dark=(20, 38, 46), spec=(226, 238, 234)),
    'white': dict(base=(206, 204, 196), lit=(240, 238, 230), dark=(118, 122, 124), spec=(255, 255, 250)),
    'bronze': dict(base=(150, 112, 80), lit=(206, 166, 124), dark=(66, 46, 34), spec=(244, 222, 190)),
    'midnight': dict(base=(30, 44, 60), lit=(86, 108, 128), dark=(10, 16, 24), spec=(200, 214, 222)),
}
TRIM = (24, 26, 29)
GLASS = (18, 30, 38)
TIRE = (27, 27, 29)


# ----------------------------------------------------------------------------- cameras
class Camera:
    def __init__(self, kind, pos=None, target=None, fov=30.0, size=(1600, 900), scale=0.25, origin=None,
                 up=(0, 1, 0)):
        self.kind, self.size = kind, size
        if kind == 'side':
            self.scale = scale                       # px per mm
            self.origin = origin or (40, size[1] - 40)  # screen pos of car (x=0, y=0)
        else:
            self.pos = np.array(pos, float)
            t = np.array(target, float)
            f = t - self.pos; f /= np.linalg.norm(f)
            r = np.cross(f, np.array(up, float)); r /= np.linalg.norm(r)
            u = np.cross(r, f)
            self.f, self.r, self.u = f, r, u
            self.focal = (size[1] / 2) / math.tan(math.radians(fov) / 2)

    def p(self, P):
        P = np.asarray(P, float)
        if self.kind == 'side':
            return (self.origin[0] + P[0] * self.scale, self.origin[1] - P[1] * self.scale)
        d = P - self.pos
        z = d @ self.f
        x = d @ self.r
        y = d @ self.u
        return (self.size[0] / 2 + self.focal * x / z, self.size[1] / 2 - self.focal * y / z)

    def depth(self, P):
        if self.kind == 'side':
            return -P[2]
        return (np.asarray(P, float) - self.pos) @ self.f

    def facing(self, normal, at):
        """True if a surface with this normal at point 'at' faces the camera."""
        n = np.asarray(normal, float)
        if self.kind == 'side':
            return n[2] > 1e-3
        return (self.pos - np.asarray(at, float)) @ n > 0

    def pp(self, pts):
        return [self.p(q) for q in pts]


# ----------------------------------------------------------------------------- geometry
def side_outline():
    """Full body silhouette in (x, y), clockwise from rear bottom (without wheel arch cut-outs)."""
    return [(70, 380), (14, 520), (0, 700), (6, 830), (30, 1000), (80, 1120), (175, 1400), (300, 1535),
            (430, 1582), (1200, 1602), (2400, 1600), (2700, 1588), (3060, 1430), (3500, 1066), (3800, 1022),
            (4300, 966), (4545, 930), (4612, 880), (4632, 700), (4635, 600), (4616, 430), (4560, 335),
            (4230, 330), (3360, 330), (1230, 330), (370, 330)]


def lower_side():
    """Body side below the belt line (door panels + fenders + quarters)."""
    return [(70, 380), (14, 520), (0, 700), (6, 830), (30, 1000), (70, 1090), (560, 1080), (3440, 1066),
            (3500, 1066), (3800, 1022), (4300, 966), (4545, 930), (4612, 880), (4632, 700), (4635, 600),
            (4616, 430), (4560, 335), (4230, 330), (3360, 330), (1230, 330), (370, 330)]


def dlo():
    """Side window graphic (daylight opening)."""
    return [(600, 1100), (3400, 1100), (3020, 1405), (2700, 1540), (2400, 1552), (1200, 1554), (790, 1546), (700, 1500),
            (610, 1200)]


def arch(cx, r, n=24, y0=330):
    a0 = math.asin(min((y0 - WHEEL_R + 5) / r, 0.99)) if r > 0 else 0
    pts = []
    for i in range(n + 1):
        t = math.pi - a0 - (math.pi - 2 * a0) * i / n
        pts.append((cx + r * math.cos(t), WHEEL_R + r * math.sin(t)))
    return pts


def lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def zside(y):
    """Lateral half-width of the body side at height y (tumblehome above the belt)."""
    if y <= 1080:
        return HALF_W - max(0, (y - 900)) * 0.04
    return HALF_W - 7 - (y - 1080) * 0.36


# ----------------------------------------------------------------------------- painting helpers
def shade(paint, k):
    """k in -1..1: -1 darkest, 0 base, 1 lit."""
    b, l, d = paint['base'], paint['lit'], paint['dark']
    if k >= 0:
        return tuple(b[i] + (l[i] - b[i]) * k for i in range(3))
    return tuple(b[i] + (d[i] - b[i]) * (-k) for i in range(3))


class CarPainter:
    def __init__(self, cam, paint='teal', w=None, h=None, lights_on=True, draw_wheels=True, door_open=0.0, glass_alpha=1.0):
        self.cam = cam
        self.paint = PAINTS[paint]
        self.w, self.h = cam.size
        self.surf = surface(self.w, self.h)
        self.c = self.surf.getCanvas()
        self.lights_on = lights_on
        self.draw_wheels = draw_wheels
        self.door_open = door_open
        self.glass_alpha = glass_alpha
        self.ink = 2.2 if cam.kind != 'side' else 1.7

    # 3D helpers
    def P(self, pts3):
        return self.cam.pp(pts3)

    def poly(self, pts3, color, shader=None, outline=True, width=None, alpha=None, smooth=False):
        pts = self.P(pts3)
        path = path_smooth(pts, True, 0.35) if smooth else path_poly(pts)
        fill(self.c, path, color, shader=shader, alpha=alpha)
        if outline:
            stroke(self.c, path, width=width or self.ink, wobble=0.35, seed=len(pts))
        return path

    def line(self, pts3, width=None, color=None, alpha=None, smooth=False):
        pts = self.P(pts3)
        path = path_smooth(pts, False, 0.4) if smooth else path_poly(pts, False)
        stroke(self.c, path, color=color, width=width or self.ink * 0.8, wobble=0.3, alpha=alpha)

    def side_pts(self, pts2, z=None):
        return [(x, y, zside(y) if z is None else z) for x, y in pts2]

    # ------------------------------------------------------------------ parts
    def ground_shadow(self):
        cam = self.cam
        pts = [(-120, 2, 760), (LEN + 120, 2, 760), (LEN + 120, 2, -760), (-120, 2, -760)]
        path = path_smooth(self.P([(LEN * 0.5 + (LEN * 0.62) * math.cos(t), 2, 980 * math.sin(t))
                                   for t in np.linspace(0, 2 * math.pi, 40)]), True)
        p = skia.Paint(AntiAlias=True, Color=skia.Color(8, 12, 16, 150),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 22 if cam.kind != 'side' else 10))
        self.c.drawPath(path, p)
        # contact darkness under wheels
        for ax in (R_AX, F_AX):
            for zz in (HALF_W - 120, -(HALF_W - 120)):
                q = self.P([(ax - 260, 1, zz), (ax + 260, 1, zz)])
                cx, cy = (q[0][0] + q[1][0]) / 2, (q[0][1] + q[1][1]) / 2
                rw = abs(q[1][0] - q[0][0]) / 2
                pr = skia.Paint(AntiAlias=True, Color=skia.Color(5, 8, 10, 190),
                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6))
                self.c.drawOval(skia.Rect.MakeLTRB(cx - rw, cy - rw * 0.12 - 3, cx + rw, cy + rw * 0.12 + 3), pr)

    def wheel(self, ax, zface, far=False, angle=0.0):
        """Tyre + rim projected onto the plane z = zface (outer face)."""
        cam = self.cam
        n = 48
        def circ(r, z, a0=0.0, k=n):
            return [(ax + r * math.cos(a0 + 2 * math.pi * i / k), WHEEL_R + r * math.sin(a0 + 2 * math.pi * i / k), z) for i in range(k)]
        inner_z = zface - TIRE_W * (1 if zface > 0 else -1)
        # tyre tread (side band between inner and outer circles) – draw inner first
        self.poly(circ(WHEEL_R, inner_z), TIRE, outline=False)
        # tread hull: connect silhouettes approximately by drawing many quads
        outer = circ(WHEEL_R, zface)
        innerc = circ(WHEEL_R, inner_z)
        for i in range(n):
            j = (i + 1) % n
            self.poly([outer[i], outer[j], innerc[j], innerc[i]], (32, 32, 34), outline=False)
        self.poly(outer, TIRE, outline=True, smooth=True)
        # sidewall highlight
        self.line(circ(WHEEL_R * 0.93, zface + (4 if zface > 0 else -4), k=n)[n // 8: n // 2 + 2], width=2.2,
                  color=(70, 70, 72), alpha=0.8)
        rim_r = WHEEL_R * 0.70
        zr = zface - 18 * (1 if zface > 0 else -1)
        if far:
            self.poly(circ(rim_r, zr), (70, 74, 78), outline=True)
            return
        self.wheel_face(ax, zr, rim_r, angle)

    def wheel_face(self, ax, z, rim_r, angle=0.0):
        """Aero rim: dark barrel, five broad silver spokes, ring of 'pixel' windows, centre cap."""
        def P2(r, a):
            return (ax + r * math.cos(a), WHEEL_R + r * math.sin(a), z)
        n = 64
        self.poly([P2(rim_r, 2 * math.pi * i / n) for i in range(n)], (150, 156, 160), outline=True)
        self.poly([P2(rim_r * 0.90, 2 * math.pi * i / n) for i in range(n)], (26, 29, 33), outline=False)
        spokes = 5
        for s_ in range(spokes):
            a = angle + 2 * math.pi * s_ / spokes
            pts = [P2(rim_r * 0.26, a - 0.34), P2(rim_r * 0.90, a - 0.22), P2(rim_r * 0.90, a + 0.22), P2(rim_r * 0.26, a + 0.34)]
            k = 0.5 + 0.5 * math.cos(a - math.radians(110))
            col_ = tuple(118 + (206 - 118) * k for _ in range(3))
            self.poly(pts, (col_[0], col_[1] + 3, col_[2] + 5), outline=True, width=self.ink * 0.6)
            # facet line down the spoke
            self.line([P2(rim_r * 0.3, a), P2(rim_r * 0.88, a)], width=1.0, color=(250, 250, 250), alpha=0.35 * k + 0.1)
        # ring of square 'pixel' windows between spokes
        for i in range(spokes * 3):
            a = angle + 2 * math.pi * (i + 0.5) / (spokes * 3)
            if i % 3 == 1:
                continue
            c0 = P2(rim_r * 0.74, a)
            sq = rim_r * 0.06
            self.poly([(c0[0] - sq, c0[1] - sq, z), (c0[0] + sq, c0[1] - sq, z), (c0[0] + sq, c0[1] + sq, z), (c0[0] - sq, c0[1] + sq, z)],
                      (178, 184, 188), outline=False)
        self.poly([P2(rim_r * 0.27, 2 * math.pi * i / 24) for i in range(24)], (184, 188, 192), outline=True)
        self.poly([P2(rim_r * 0.13, 2 * math.pi * i / 24) for i in range(24)], (52, 56, 62), outline=False)

    def wheel_wells(self):
        for ax in (R_AX, F_AX):
            pts2 = arch(ax, 440, 28)
            self.poly(self.side_pts(pts2, HALF_W - 4), (12, 14, 16), outline=False)

    def body_side(self):
        cam, pt = self.cam, self.paint
        pts3 = self.side_pts(lower_side(), HALF_W)
        # base fill with vertical reflection gradient (sky above / floor below): crisp horizon line
        top = self.cam.p((2000, 1080, HALF_W))
        bot = self.cam.p((2000, 330, HALF_W))
        hz = 0.38
        sh = lin_grad(top, bot, [shade(pt, 0.55), shade(pt, 0.25), shade(pt, 0.05), shade(pt, -0.55), shade(pt, -0.35)],
                      [0.0, hz - 0.02, hz, hz + 0.05, 1.0])
        path = self.poly(pts3, pt['base'], shader=sh, outline=False)
        self.c.save(); self.c.clipPath(path, skia.ClipOp.kIntersect, True)
        # soft reflections of tall showroom windows
        for x0, w, a in ((350, 380, 0.10), (1500, 520, 0.13), (2900, 300, 0.09), (3900, 420, 0.11)):
            q = self.P([(x0, 330, HALF_W), (x0 + w, 330, HALF_W), (x0 + w + 140, 1080, HALF_W), (x0 + 140, 1080, HALF_W)])
            pr = skia.Paint(AntiAlias=True, Color=col(pt['spec'], int(255 * a)),
                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10))
            self.c.drawPath(path_poly(q), pr)
        # shoulder highlight just below the belt line
        q = self.P([(120, 1045, HALF_W), (4400, 985, HALF_W), (4400, 960, HALF_W), (120, 1015, HALF_W)])
        pr = skia.Paint(AntiAlias=True, Color=col(pt['spec'], 120), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 3))
        self.c.drawPath(path_poly(q), pr)
        # occlusion near the sill
        q = self.P([(0, 330, HALF_W), (LEN, 330, HALF_W), (LEN, 470, HALF_W), (0, 470, HALF_W)])
        pr = skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, 70), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12))
        self.c.drawPath(path_poly(q), pr)
        self.c.restore()
        stroke(self.c, path, width=self.ink * 1.3, wobble=0.35, seed=3)
        return path

    def cladding(self):
        for ax in (R_AX, F_AX):
            outer = arch(ax, 470, 28)
            inner = arch(ax, 430, 28)
            ring = outer + inner[::-1]
            self.poly(self.side_pts(ring, HALF_W + 2), TRIM, outline=True, width=self.ink * 0.8)
        # sill
        sill = [(1240, 330), (3350, 330), (3330, 420), (1260, 420)]
        self.poly(self.side_pts(sill, HALF_W + 2), (30, 33, 36), outline=True, width=self.ink * 0.8)
        # front & rear bumper lower trims
        self.poly(self.side_pts([(4230, 330), (4560, 335), (4600, 400), (4250, 400)], HALF_W + 2), TRIM, outline=False)
        self.poly(self.side_pts([(70, 380), (370, 330), (380, 420), (40, 450)], HALF_W + 2), TRIM, outline=False)

    def greenhouse(self):
        pt = self.paint
        # pillars/roof side in body colour
        gh = [(440, 1080), (3440, 1068), (3060, 1430), (2700, 1588), (2400, 1600), (1200, 1602), (430, 1582), (300, 1535),
              (175, 1400), (80, 1120)]
        top = self.cam.p((2000, 1600, zside(1600)))
        bot = self.cam.p((2000, 1080, zside(1080)))
        sh = lin_grad(top, bot, [shade(pt, 0.75), shade(pt, 0.35)])
        self.poly([(x, y, zside(y)) for x, y in gh], pt['base'], shader=sh, outline=True)
        # glass
        g = [(x, y, zside(y) + 4) for x, y in dlo()]
        gtop, gbot = self.cam.p((2000, 1550, zside(1550))), self.cam.p((2000, 1100, zside(1100)))
        gs = lin_grad(gtop, gbot, [(64, 86, 96), (24, 38, 48), (14, 24, 32)], [0, 0.45, 1])
        if self.glass_alpha < 1.0:
            # punch the glass out, then paint it translucent so the cabin shows through
            gp = path_poly(self.P(g))
            pc = skia.Paint(AntiAlias=True, BlendMode=skia.BlendMode.kClear)
            self.c.drawPath(gp, pc)
        self.poly(g, GLASS, shader=gs, outline=True, alpha=self.glass_alpha)
        # reflection streaks across the glass (clip to glass)
        path = path_poly(self.P(g))
        self.c.save(); self.c.clipPath(path, skia.ClipOp.kIntersect, True)
        for k, (x0, w) in enumerate(((900, 260), (1500, 110), (2600, 300))):
            q = self.P([(x0, 1100, zside(1100)), (x0 + w, 1100, zside(1100)), (x0 + w + 420, 1560, zside(1560)), (x0 + 420, 1560, zside(1560))])
            fill(self.c, path_poly(q), (200, 220, 225), alpha=0.10 + 0.05 * k)
        self.c.restore()
        # B pillar (black) and C pillar trim
        self.poly([(x, y, zside(y) + 6) for x, y in [(2380, 1100), (2470, 1100), (2470, 1552), (2380, 1554)]], TRIM, outline=True)
        self.poly([(x, y, zside(y) + 6) for x, y in [(1150, 1100), (1215, 1100), (1215, 1554), (1150, 1554)]], TRIM, outline=True)
        # window surround chrome-less black line
        self.line([(x, y, zside(y) + 7) for x, y in dlo()] + [(560, 1100, zside(1100) + 7)], width=self.ink * 1.0, color=(14, 16, 18))

    def roof_and_glass_top(self):
        pt = self.paint
        cam = self.cam
        zr = zside(1600)
        roof = [(430, 1582, zr), (2700, 1588, zr), (2700, 1588, -zr), (430, 1582, -zr)]
        if cam.facing((0, 1, 0), (1500, 1600, 0)):
            sh = lin_grad(cam.p((1500, 1600, zr)), cam.p((1500, 1600, -zr)), [(30, 34, 38), (52, 60, 66)])
            self.poly([(430, 1582, zr), (2700, 1590, zr), (2700, 1590, -zr), (430, 1582, -zr)], (34, 38, 44), shader=sh)
            # panoramic glass roof stripe
            self.poly([(650, 1595, zr - 120), (2550, 1598, zr - 120), (2550, 1598, -zr + 120), (650, 1595, -zr + 120)],
                      (16, 26, 34), outline=True, width=self.ink * 0.7)
        # windshield
        ws = [(3440, 1066, zside(1066) - 10), (2700, 1588, zr - 8), (2700, 1588, -zr + 8), (3440, 1066, -zside(1066) + 10)]
        n = np.cross(np.array(ws[1]) - np.array(ws[0]), np.array(ws[3]) - np.array(ws[0]))
        if cam.facing(n if n[1] > 0 else -n, ws[0]):
            sh = lin_grad(cam.p(ws[1]), cam.p(ws[0]), [(70, 94, 104), (20, 34, 44)])
            self.poly(ws, GLASS, shader=sh)
            path = path_poly(self.P(ws))
            self.c.save(); self.c.clipPath(path, skia.ClipOp.kIntersect, True)
            for k in range(3):
                t0 = 0.15 + 0.28 * k
                a = lerp3(ws[1], ws[2], t0); b = lerp3(ws[1], ws[2], t0 + 0.12)
                c_ = lerp3(ws[0], ws[3], t0 + 0.2); d = lerp3(ws[0], ws[3], t0 + 0.08)
                fill(self.c, path_poly(self.P([a, b, c_, d])), (220, 232, 236), alpha=0.07 + 0.03 * k)
            self.c.restore()
            # far A pillar and roof header (body colour)
            ap = [(3440, 1066, -zside(1066) + 10), (2700, 1588, -zr + 8), (2660, 1590, -zr - 4), (3380, 1066, -zside(1066) - 6)]
            self.poly(ap, shade(pt, 0.3), outline=True)
            hdr = [(2700, 1588, zr - 8), (2700, 1588, -zr + 8), (2640, 1596, -zr + 8), (2640, 1596, zr - 8)]
            self.poly(hdr, shade(pt, 0.55), outline=True, width=self.ink * 0.8)

    def hood(self):
        pt, cam = self.paint, self.cam
        hz = HALF_W - 60
        hood = [(3500, 1066, hz), (4545, 930, hz - 40), (4545, 930, -hz + 40), (3500, 1066, -hz)]
        if cam.kind == 'side':
            return
        sh = lin_grad(cam.p((3600, 1080, 0)), cam.p((4545, 936, 0)), [shade(pt, 0.85), shade(pt, 0.45), shade(pt, 0.6)], [0, 0.6, 1])
        hp = self.poly(hood, pt['base'], shader=sh)
        self.c.save(); self.c.clipPath(hp, skia.ClipOp.kIntersect, True)
        for zc, a in ((-300, 0.16), (250, 0.10)):
            q = self.P([(3550, 1060, zc - 90), (4520, 935, zc - 140), (4520, 935, zc + 140), (3550, 1060, zc + 90)])
            pr = skia.Paint(AntiAlias=True, Color=col(pt['spec'], int(255 * a)), MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 14))
            self.c.drawPath(path_poly(q), pr)
        self.c.restore()
        # clamshell seam along the fender tops
        self.line([(3520, 1080, hz - 10), (4100, 1010, hz - 25), (4520, 945, hz - 45)], width=self.ink * 0.8)
        self.line([(3520, 1080, -hz + 10), (4100, 1010, -hz + 25), (4520, 945, -hz + 45)], width=self.ink * 0.8)
        # fender top strip between hood seam and side (left side only visible)
        self.poly([(3500, 1066, HALF_W), (4545, 930, HALF_W - 30), (4545, 930, hz - 40), (3500, 1066, hz)],
                  shade(pt, 0.5), outline=True, width=self.ink * 0.8)

    def front_face(self):
        pt, cam = self.paint, self.cam
        if cam.kind == 'side':
            return
        X = 4600
        def F(z, y, dx=0.0):
            # slight curvature: front face recedes toward the corners and the top
            return (X + dx - (abs(z) / HALF_W) ** 2 * 70 - max(0, y - 700) * 0.12, y, z)
        zz = HALF_W - 30
        face = [F(-zz, 340), F(zz, 340), F(zz + 10, 700), F(zz - 30, 900), F(-zz + 30, 900), F(-zz - 10, 700)]
        sh = lin_grad(cam.p(F(0, 900)), cam.p(F(0, 340)), [shade(pt, 0.35), shade(pt, -0.1), shade(pt, -0.45)], [0, 0.5, 1])
        self.poly(face, pt['base'], shader=sh, outline=True, width=self.ink * 1.2)
        # corner blend between front and left side
        self.poly([F(zz, 340), (4560, 335, HALF_W), (4635, 600, HALF_W), (4612, 882, HALF_W), F(zz - 30, 900), F(zz + 10, 700)],
                  shade(pt, 0.0), outline=True, width=self.ink)
        # headlamp band: black strip with parametric pixel units
        band = [F(-zz + 40, 800), F(zz - 40, 800), F(zz - 50, 880), F(-zz + 50, 880)]
        self.poly(band, (20, 24, 28), outline=True)
        for side in (-1, 1):
            z0, z1 = side * (zz - 330), side * (zz - 70)
            unit = [F(z0, 808), F(z1, 808), F(z1, 872), F(z0, 872)]
            self.poly(unit, (36, 40, 44), outline=True, width=self.ink * 0.7)
            cols, rows = 6, 2
            for i in range(cols):
                for j in range(rows):
                    if j == 1 and 0 < i < cols - 1 and i % 2 == 1:
                        continue
                    za = z0 + (z1 - z0) * (i + 0.18) / cols
                    zb = z0 + (z1 - z0) * (i + 0.82) / cols
                    ya, yb = 815 + j * 30, 838 + j * 30
                    on = (250, 246, 230) if self.lights_on else (150, 152, 150)
                    q = [F(za, ya, 3), F(zb, ya, 3), F(zb, yb, 3), F(za, yb, 3)]
                    self.poly(q, on, outline=False)
            if self.lights_on:
                c = self.cam.p(F((z0 + z1) / 2, 840))
                pg = skia.Paint(AntiAlias=True, Color=skia.Color(255, 250, 230, 60),
                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 16))
                self.c.drawCircle(c[0], c[1], 40, pg)
        # bonnet edge line
        self.line([F(-zz + 30, 900), F(zz - 30, 900)], width=self.ink)
        # lower grille / intake with pixel pattern
        gr = [F(-560, 430), F(560, 430), F(600, 560), F(-600, 560)]
        self.poly(gr, (18, 20, 23), outline=True)
        for i in range(14):
            for j in range(3):
                za = -540 + i * 78
                ya = 450 + j * 36
                q = [F(za, ya, 2), F(za + 40, ya, 2), F(za + 40, ya + 20, 2), F(za, ya + 20, 2)]
                self.poly(q, (58, 64, 70), outline=False)
        # skid plate + licence plate
        self.poly([F(-330, 600), F(330, 600), F(330, 700), F(-330, 700)], (226, 224, 214), outline=True, width=self.ink * 0.7)
        self.line([F(-280, 650), F(280, 650)], width=1.0, color=(120, 120, 120), alpha=0.5)
        # emblem: slanted H in an ellipse (placeholder for the official badge)
        e = [F(55 * math.cos(t), 760 + 26 * math.sin(t), 4) for t in np.linspace(0, 2 * math.pi, 24)]
        self.poly(e, (196, 200, 204), outline=True, width=self.ink * 0.6, smooth=True)
        self.line([F(-22, 745, 6), F(-10, 775, 6)], width=2.4, color=(40, 44, 48))
        self.line([F(10, 745, 6), F(22, 775, 6)], width=2.4, color=(40, 44, 48))
        self.line([F(-14, 760, 6), F(16, 760, 6)], width=2.0, color=(40, 44, 48))

    def side_details(self):
        pt = self.paint
        z = HALF_W + 3
        dz = lambda pts: [(x, y, z) for x, y in pts]
        # door seams
        self.line(dz([(3430, 1080), (3440, 720), (3400, 430), (3360, 340)]), width=self.ink * 0.9)
        self.line(dz([(2420, 1080), (2420, 340)]), width=self.ink * 0.9)
        self.line(dz([(1360, 1080), (1330, 860), (1240, 760), (1238, 420)]), width=self.ink * 0.9)
        # the Z crease: diagonal light line + shadow below
        self.line(dz([(3300, 440), (1250, 905)]), width=self.ink * 1.0)
        a = self.P(dz([(3300, 440), (1250, 905), (1250, 860), (3300, 405)]))
        fill(self.c, path_poly(a), shade(pt, 0.9), alpha=0.35)
        # flush handles
        for x0 in (2620, 1560):
            h = dz([(x0, 985), (x0 + 220, 985), (x0 + 220, 1010), (x0, 1010)])
            self.poly(h, shade(pt, -0.3), outline=True, width=self.ink * 0.6)
        # charge-port style fuel flap on rear quarter (left side carries a discreet panel)
        self.poly(dz([(480, 920), (640, 920), (640, 1010), (480, 1010)]), shade(pt, 0.05), outline=True, width=self.ink * 0.5)
        # side repeater / pixel tail light corner
        for i in range(4):
            q = dz([(22 + i * 12, 880 + i * 0), (30 + i * 12, 880), (30 + i * 12, 940), (22 + i * 12, 940)])
        self.poly(dz([(8, 850), (120, 850), (110, 990), (26, 990)]), (110, 24, 26), outline=True, width=self.ink * 0.6)
        for i in range(3):
            for j in range(2):
                q = dz([(26 + i * 28, 870 + j * 55), (46 + i * 28, 870 + j * 55), (46 + i * 28, 905 + j * 55), (26 + i * 28, 905 + j * 55)])
                self.poly(q, (210, 60, 52) if self.lights_on else (150, 40, 40), outline=False)
        # headlamp corner seen from the side
        self.poly(dz([(4450, 800), (4625, 805), (4612, 880), (4470, 900)]), (24, 28, 32), outline=True, width=self.ink * 0.6)
        for i in range(3):
            q = dz([(4490 + i * 40, 818), (4515 + i * 40, 818), (4515 + i * 40, 860), (4490 + i * 40, 860)])
            self.poly(q, (246, 242, 226) if self.lights_on else (150, 152, 150), outline=False)
        # mirror
        m = [(3330, 1090), (3520, 1100), (3530, 1205), (3360, 1215)]
        if self.cam.kind == 'side':
            self.poly(dz(m), shade(pt, 0.2), outline=True)
        else:
            mz = HALF_W + 210
            mirror = [(3330, 1100, HALF_W), (3330, 1100, mz), (3360, 1210, mz), (3360, 1210, HALF_W)]
            self.poly([(3330, 1095, mz), (3520, 1100, mz), (3530, 1205, mz), (3360, 1215, mz)], shade(pt, 0.1))
            self.poly([(3520, 1100, HALF_W), (3520, 1100, mz), (3530, 1205, mz), (3530, 1205, HALF_W)], shade(pt, 0.45))
        # roof rail
        self.poly([(500, 1590, zside(1590) - 20), (2650, 1594, zside(1594) - 20), (2650, 1625, zside(1625) - 30),
                   (520, 1622, zside(1622) - 30)], (30, 32, 36), outline=True, width=self.ink * 0.6)

    def door_open_view(self):
        """Side view with the driver's door swung open toward the camera (interior inspection bay)."""
        if self.door_open <= 0:
            return
        z = HALF_W + 4
        opening = [(2420, 1080), (3430, 1080), (3440, 720), (3400, 430), (2420, 430)]
        self.poly([(x, y, z) for x, y in opening], (14, 16, 20), outline=True)
        # seat bolster + headrest visible inside
        seat = [(2470, 470), (2950, 470), (3000, 760), (2860, 820), (2600, 780), (2520, 1180), (2600, 1360), (2560, 1420),
                (2450, 1400)]
        self.poly([(x, y, z + 1) for x, y in seat], (54, 44, 40), outline=True)
        self.line([(2520, 1150, z + 2), (2560, 800, z + 2)], width=1.2, color=(90, 74, 64))
        # steering wheel rim (foreshortened)
        sw = [(3150 + 70 * math.cos(t), 1050 + 190 * math.sin(t), z + 2) for t in np.linspace(0, 2 * math.pi, 24)]
        self.line(sw, width=7, color=(30, 30, 32))
        # door panel: foreshortened, hinged at x=3430
        k = math.cos(math.radians(70 * self.door_open))
        hinge = 3430
        dz_ = lambda x: hinge + (x - hinge) * k
        door = [(dz_(2420), 1075), (dz_(3430), 1080), (3440, 720), (3400, 430), (dz_(2420), 430)]
        top = self.cam.p((3000, 1080, z)); bot = self.cam.p((3000, 430, z))
        sh = lin_grad(top, bot, [shade(self.paint, 0.4), shade(self.paint, -0.3)])
        self.poly([(x, y, z + 40) for x, y in door], self.paint['base'], shader=sh, outline=True)
        # window frame of door (glass up)
        self.poly([(dz_(2440), 1095, z + 40), (3420, 1095, z + 40), (3040, 1400, z + 40), (dz_(2500), 1540, z + 40)],
                  GLASS, outline=True, alpha=0.85)
        self.line([(dz_(2420) + 40, 600, z + 42), (3380, 600, z + 42)], width=1.2, color=(20, 30, 36), alpha=0.6)

    # ------------------------------------------------------------------ assemble
    def render(self, wheel_angle=0.0):
        cam = self.cam
        self.ground_shadow()
        if cam.kind != 'side' and self.draw_wheels:
            self.wheel(F_AX, -(HALF_W - 40), far=True, angle=wheel_angle)
        self.body_side()
        self.wheel_wells()
        if self.draw_wheels:
            self.wheel(R_AX, HALF_W - 40, angle=wheel_angle)
            self.wheel(F_AX, HALF_W - 40, angle=wheel_angle + 0.4)
        self.cladding()
        self.greenhouse()
        self.roof_and_glass_top()
        self.hood()
        self.front_face()
        self.side_details()
        self.door_open_view()
        return self

    def image(self, texture=True, seed=1):
        img = to_np(self.surf)
        if texture:
            img = gouache(img, 1.0, seed=seed, grain=0.03, mottling=0.04, streak_dir='h', streak=0.015)
        return pil_from(img)


def render_wheel_sprite(px_per_mm=0.2, paint='teal'):
    """Side-view wheel (tyre + rim) as a standalone sprite for rotation in-game."""
    size = int(2 * WHEEL_R * px_per_mm + 8)
    cam = Camera('side', size=(size, size), scale=px_per_mm, origin=(size / 2 - F_AX * px_per_mm, size / 2 + WHEEL_R * px_per_mm))
    cp = CarPainter(cam, paint)
    cp.wheel(F_AX, HALF_W - 40)
    return cp.image(seed=9)
