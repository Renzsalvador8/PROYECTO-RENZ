"""Reference implementation of the cut-out rig + clip evaluation (mirrors TesterRig.cs / RigClip.cs).

Clip curve interpolation: cubic Hermite with Catmull-Rom tangents ("smooth"), "linear" or "step".
"""
import json, math, os
import numpy as np
import skia
from PIL import Image
from common import DATA_OUT, ART_OUT


def load_rig(name):
    with open(os.path.join(DATA_OUT, 'Rigs', name + '.json')) as f:
        rig = json.load(f)
    atlas = Image.open(os.path.join(ART_OUT, rig['atlas'].split('Art/', 1)[1] + '.png')).convert('RGBA')
    rig['_atlas'] = atlas
    rig['_skimg'] = skia.Image.fromarray(np.asarray(atlas).copy(), colorType=skia.kRGBA_8888_ColorType)
    return rig


# ----------------------------------------------------------------------------- curves
def eval_curve(keys, t, interp='smooth', loop=False, length=1.0):
    n = len(keys)
    if n == 0:
        return 0.0
    if n == 1:
        return keys[0][1]
    if loop:
        t = t % length
    if t <= keys[0][0] and not loop:
        return keys[0][1]
    if t >= keys[-1][0] and not loop:
        return keys[-1][1]
    # find segment
    i = 0
    while i < n - 1 and keys[i + 1][0] <= t:
        i += 1
    if i >= n - 1:  # only when looping, wrap to first key
        k0, k1 = keys[-1], (keys[0][0] + length, keys[0][1])
    else:
        k0, k1 = keys[i], keys[i + 1]
    if t < keys[0][0]:  # loop wrap before first key
        k0, k1 = (keys[-1][0] - length, keys[-1][1]), keys[0]
        i = -1
    t0, v0 = k0
    t1, v1 = k1
    dt = max(t1 - t0, 1e-6)
    u = (t - t0) / dt
    if interp == 'step':
        return v0
    if interp == 'linear':
        return v0 + (v1 - v0) * u

    def key_at(j):
        if loop:
            q, r = divmod(j, n)
            return (keys[r][0] + q * length, keys[r][1])
        j = min(max(j, 0), n - 1)
        return keys[j]
    ip = i if i >= 0 else n - 1
    if i < 0:
        km1, k2 = key_at(-2), key_at(1)
    else:
        km1, k2 = key_at(i - 1), key_at(i + 2)
    # tangents (Catmull-Rom, non-uniform)
    def tangent(ka, kb):
        return (kb[1] - ka[1]) / max(kb[0] - ka[0], 1e-6)
    m0 = tangent(km1, k1) if (loop or i > 0) else (v1 - v0) / dt
    m1 = tangent(k0, k2) if (loop or i + 2 <= n - 1) else (v1 - v0) / dt
    u2, u3 = u * u, u * u * u
    h00 = 2 * u3 - 3 * u2 + 1
    h10 = u3 - 2 * u2 + u
    h01 = -2 * u3 + 3 * u2
    h11 = u3 - u2
    return h00 * v0 + h10 * dt * m0 + h01 * v1 + h11 * dt * m1


def eval_clip(clip, t):
    pose = {}
    for c in clip['curves']:
        v = eval_curve(c['keys'], t, c.get('interp', 'smooth'), clip.get('loop', False), clip['length'])
        pose.setdefault(c['target'], {})[c['prop']] = v
    return pose


def blend_pose(a, b, w):
    out = {}
    for k in set(a) | set(b):
        pa, pb = a.get(k, {}), b.get(k, {})
        d = {}
        for p in set(pa) | set(pb):
            default = 1.0 if p in ('sx', 'sy', 'alpha') else 0.0
            va, vb = pa.get(p, default), pb.get(p, default)
            d[p] = va + (vb - va) * w
        out[k] = d
    return out


# ----------------------------------------------------------------------------- transforms
def mat(tx, ty, rot_deg, sx=1.0, sy=1.0):
    r = math.radians(rot_deg)
    c, s = math.cos(r), math.sin(r)
    return np.array([[c * sx, -s * sy, tx], [s * sx, c * sy, ty], [0, 0, 1]], float)


def world_transforms(rig, pose):
    W = {}
    for b in rig['bones']:
        p = pose.get(b['name'], {})
        local = mat(b['pos'][0] + p.get('x', 0), b['pos'][1] + p.get('y', 0), b.get('rot', 0) + p.get('rot', 0), p.get('sx', 1), p.get('sy', 1))
        W[b['name']] = W[b['parent']] @ local if b['parent'] else local
    return W


def render(rig, pose, size=(600, 700), ppu_out=200.0, origin=None, bg=None, flip=False, slot_sprites=None,
           canvas=None, extra=None):
    """Render the rig. World units -> pixels at ppu_out, origin = pixel position of root."""
    w, h = size
    if origin is None:
        origin = (w / 2, h - 30)
    s = skia.Surface(w, h) if canvas is None else None
    c = s.getCanvas() if canvas is None else canvas
    if bg is not None and canvas is None:
        c.clear(skia.Color(*bg))
    elif canvas is None:
        c.clear(skia.ColorTRANSPARENT)
    Wt = world_transforms(rig, pose)
    ppu = rig['ppu']
    AH = rig['atlasSize'][1]
    paint = skia.Paint(AntiAlias=True)
    slot_sprites = slot_sprites or {}
    for slot in sorted(rig['slots'], key=lambda s_: s_['order']):
        sp_name = slot_sprites.get(slot['name'], slot['sprite'])
        sp = pose.get('slot:' + slot['name'], {})
        if sp.get('visible', 0 if slot.get('hidden') else 1) < 0.5 or not sp_name:
            continue
        spr = rig['sprites'][sp_name]
        x, y, sw, sh = spr['rect']
        img_y = AH - y - sh  # top-left origin in atlas image
        pvx, pvy = spr['pivot'][0] * sw, (1 - spr['pivot'][1]) * sh
        # sprite px -> bone-local units: ((px - pvx)/ppu, (pvy - py)/ppu)
        M = Wt[slot['bone']]
        # full: screen = O + ppu_out * diag(fx,-1) * M * [ (px-pvx)/ppu, (pvy-py)/ppu ]
        fx = -1 if flip else 1
        S_ = np.array([[fx * ppu_out, 0, origin[0]], [0, -ppu_out, origin[1]], [0, 0, 1]])
        P_ = np.array([[1 / ppu, 0, -pvx / ppu], [0, -1 / ppu, pvy / ppu], [0, 0, 1]])
        T = S_ @ M @ P_
        m = skia.Matrix()
        m.setAll(T[0, 0], T[0, 1], T[0, 2], T[1, 0], T[1, 1], T[1, 2], 0, 0, 1)
        c.save()
        c.concat(m)
        tint = slot.get('tint', [1, 1, 1, 1])
        alpha = sp.get('alpha', 1.0) * tint[3]
        p = skia.Paint(AntiAlias=True)
        if tint[:3] != [1, 1, 1]:
            cm = [tint[0], 0, 0, 0, 0, 0, tint[1], 0, 0, 0, 0, 0, tint[2], 0, 0, 0, 0, 0, alpha, 0]
            p.setColorFilter(skia.ColorFilters.Matrix(cm))
        elif alpha < 1:
            p.setAlphaf(alpha)
        img = rig['_skimg']
        c.drawImageRect(img, skia.Rect.MakeXYWH(x, img_y, sw, sh), skia.Rect.MakeXYWH(0, 0, sw, sh),
                        skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
        c.restore()
    if canvas is None:
        img = s.makeImageSnapshot()
        return Image.fromarray(img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType), 'RGBA')


def foot_bottom(rig, pose, which):
    """World-space y of the lowest sole point for a shoe slot (approx using sprite rect corners)."""
    Wt = world_transforms(rig, pose)
    spr = rig['sprites']['shoe']
    x, y, sw, sh = spr['rect']
    ppu = rig['ppu']
    pvx, pvy = spr['pivot'][0] * sw, (1 - spr['pivot'][1]) * sh
    M = Wt['ankle_' + which]
    pts = []
    for px in np.linspace(0, sw, 9):
        py = sh - 3
        v = M @ np.array([(px - pvx) / ppu, (pvy - py) / ppu, 1])
        pts.append((v[0], v[1]))
    return min(p[1] for p in pts), pts
