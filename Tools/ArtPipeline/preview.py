"""Composite a level layout as the Unity camera would see it (for art direction QA)."""
import os, json, math, sys
import numpy as np
import skia
from PIL import Image
from common import *
import rigtools

_cache = {}


def load_sprite(path):
    if path not in _cache:
        if path.startswith('Art/'):
            f = os.path.join(ART_OUT, path[4:] + '.png')
        else:
            f = os.path.join(UI_OUT, path.split('UI/', 1)[1] + '.png')
        arr = np.asarray(Image.open(f).convert('RGBA')).copy()
        _cache[path] = skia.Image.fromarray(arr, colorType=skia.kRGBA_8888_ColorType)
    return _cache[path]


def render_level(level, cam_x, cam_y=None, size=(1920, 1080), ortho=None, actors=(), out=None):
    W, H = size
    ortho = ortho or level['camera']['size']
    cam_y = level['camera']['y'] if cam_y is None else cam_y
    ppu_screen = H / (2 * ortho)
    s = skia.Surface(W, H)
    c = s.getCanvas()
    c.clear(skia.Color(*level['background'], 255))
    draws = []
    for L in level['layers']:
        rx = cam_x * (1 - L['parallax'])
        ry = cam_y * (1 - L['parallaxY'])
        for it in L['items']:
            draws.append((L['order'] + it['order'], 'item', (it, rx, ry)))
    for a in actors:
        draws.append((a['order'], 'actor', a))
    draws.sort(key=lambda d: d[0])

    def to_screen(wx, wy):
        return (W / 2 + (wx - cam_x) * ppu_screen, H / 2 - (wy - cam_y) * ppu_screen)

    for _, kind, d in draws:
        if kind == 'item':
            it, rx, ry = d
            img = load_sprite(it['sprite'])
            iw, ih = img.width(), img.height()
            wx, wy = it['x'] + rx, it['y'] + ry
            sx, sy = it['sx'], it['sy']
            k = ppu_screen / it['ppu']
            px, py = to_screen(wx, wy)
            m = skia.Matrix()
            # sprite pixel (u,v) top-left origin -> screen
            pvx, pvy = it['pivot'][0] * iw, (1 - it['pivot'][1]) * ih
            m.setAll(k * sx * math.cos(math.radians(-it['rot'])), -k * sy * math.sin(math.radians(-it['rot'])), 0,
                     k * sx * math.sin(math.radians(-it['rot'])), k * sy * math.cos(math.radians(-it['rot'])), 0, 0, 0, 1)
            c.save()
            c.translate(px, py)
            c.concat(m)
            c.translate(-pvx, -pvy)
            p = skia.Paint(AntiAlias=True)
            t = it['tint']
            if t != [1, 1, 1] or it['alpha'] < 1:
                cm = [t[0], 0, 0, 0, 0, 0, t[1], 0, 0, 0, 0, 0, t[2], 0, 0, 0, 0, 0, it['alpha'], 0]
                p.setColorFilter(skia.ColorFilters.Matrix(cm))
            c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p)
            c.restore()
        else:
            a = d
            rig = a['rig']
            ox, oy = to_screen(a['x'], a['y'])
            rigtools.render(rig, a.get('pose', {}), size=(W, H), ppu_out=ppu_screen, origin=(ox, oy), canvas=c,
                            flip=a.get('flip', False), slot_sprites=a.get('slots'))
    img = s.makeImageSnapshot()
    im = Image.fromarray(img.toarray(colorType=skia.kRGBA_8888_ColorType, alphaType=skia.kUnpremul_AlphaType), 'RGBA')
    if out:
        im.convert('RGB').save(out)
    return im


def load_level(name):
    return json.load(open(os.path.join(DATA_OUT, 'Levels', name + '.json')))
