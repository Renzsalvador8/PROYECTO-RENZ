"""Painted props in the ink/gouache style: magnifying glasses."""
import numpy as np
import skia
from PIL import Image
from paint import *
from common import BRONZE


def magnifier(scale=1.0):
    """Returns (PIL RGBA, grip pivot px). Lens on top, handle pointing down."""
    S = scale
    R = 26 * S            # lens outer radius
    W, H = int(2 * R + 16 * S), int(2 * R + 70 * S)
    s = surface(W, H)
    c = s.getCanvas()
    cx, cy = W / 2, 8 * S + R
    # handle
    hx0, hy0 = cx, cy + R - 2 * S
    handle = path_smooth([(cx - 4 * S, hy0), (cx + 4 * S, hy0), (cx + 5.5 * S, hy0 + 14 * S), (cx + 6.5 * S, hy0 + 52 * S),
                          (cx, hy0 + 58 * S), (cx - 6.5 * S, hy0 + 52 * S), (cx - 5.5 * S, hy0 + 14 * S)], True, 0.3)
    fill(c, handle, (40, 28, 22), shader=lin_grad((cx - 7 * S, 0), (cx + 7 * S, 0), [(25, 18, 15), (78, 55, 40), (30, 22, 18)]))
    stroke(c, handle, width=1.6 * S)
    # brass ferrule
    fer = path_poly([(cx - 6 * S, hy0 + 6 * S), (cx + 6 * S, hy0 + 6 * S), (cx + 6.5 * S, hy0 + 15 * S), (cx - 6.5 * S, hy0 + 15 * S)])
    fill(c, fer, BRONZE, shader=lin_grad((cx - 7 * S, 0), (cx + 7 * S, 0), [(120, 74, 44), (226, 170, 120), (110, 66, 40)]))
    stroke(c, fer, width=1.3 * S)
    # rim
    rim = skia.Path(); rim.addCircle(cx, cy, R)
    fill(c, rim, BRONZE, shader=lin_grad((cx - R, cy - R), (cx + R, cy + R), [(214, 156, 108), (150, 92, 56), (96, 58, 36)]))
    lens = skia.Path(); lens.addCircle(cx, cy, R - 4.2 * S)
    fill(c, lens, (190, 205, 210, 150), shader=rad_grad((cx - R * 0.3, cy - R * 0.35), R * 1.25,
                                                         [(236, 246, 246, 70), (188, 214, 222, 60), (96, 132, 150, 150)], [0, 0.6, 1]))
    # glare streaks
    g = skia.Path()
    g.moveTo(cx - R * 0.55, cy - R * 0.1); g.cubicTo(cx - R * 0.5, cy - R * 0.55, cx - R * 0.15, cy - R * 0.68, cx + R * 0.15, cy - R * 0.62)
    stroke(c, g, color=(255, 255, 250), width=3.2 * S, alpha=0.75)
    g2 = skia.Path(); g2.moveTo(cx + R * 0.35, cy + R * 0.45); g2.lineTo(cx + R * 0.5, cy + R * 0.25)
    stroke(c, g2, color=(255, 255, 250), width=2.0 * S, alpha=0.5)
    stroke(c, rim, width=1.8 * S)
    stroke(c, lens, width=1.2 * S, alpha=0.8)
    img = to_np(s)
    img = gouache(img, 0.6, seed=4, grain=0.03, mottling=0.03)
    grip = (cx, hy0 + 34 * S)
    return pil_from(img), grip, (cx, cy), R
