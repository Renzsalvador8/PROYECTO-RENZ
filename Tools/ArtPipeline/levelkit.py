"""Level layout authoring helpers. Layouts are exported as JSON (Data/Levels/*.json) and read by
LevelBuilder.cs at runtime. Parallax: a layer root is placed at camX * (1 - parallax), so an item
authored with anchor A (world x where it lines up when the camera is centred on A) has local x = A * p.
"""
import os, json
from PIL import Image
from common import *


def img_size(sprite):
    rel = sprite.split('Art/', 1)[1] if sprite.startswith('Art/') else sprite
    p = os.path.join(ART_OUT, rel + '.png')
    if not os.path.exists(p):
        p = os.path.join(UI_OUT, sprite.split('UI/', 1)[1] + '.png')
    with Image.open(p) as im:
        return im.size


class Layer:
    def __init__(self, name, parallax=1.0, order=0, parallax_y=None):
        self.d = {'name': name, 'parallax': parallax, 'parallaxY': parallax if parallax_y is None else parallax_y,
                  'order': order, 'items': []}

    def add(self, sprite, anchor_x, y, ppu=100.0, pivot=(0.5, 0.0), sx=1.0, sy=1.0, alpha=1.0, tint=(1, 1, 1),
            order=0, id='', flip=False, rot=0.0):
        p = self.d['parallax']
        item = {'sprite': sprite, 'x': round(anchor_x * p, 4), 'y': round(y, 4), 'ppu': ppu,
                'pivot': [pivot[0], pivot[1]], 'sx': sx * (-1 if flip else 1), 'sy': sy, 'alpha': alpha,
                'tint': [tint[0], tint[1], tint[2]], 'order': order, 'rot': rot}
        if id:
            item['id'] = id
        self.d['items'].append(item)
        return item

    def add_local(self, sprite, local_x, y, **kw):
        it = self.add(sprite, 0, y, **kw)
        it['x'] = round(local_x, 4)
        return it

    def tile(self, sprite, x0_local, x1_local, y, ppu=100.0, pivot=(0.0, 1.0), order=0, overlap=0.02, **kw):
        w, h = img_size(sprite)
        step = w / ppu - overlap
        x = x0_local
        while x < x1_local:
            self.add_local(sprite, x, y, ppu=ppu, pivot=pivot, order=order, **kw)
            x += step


class Level:
    def __init__(self, id, bounds, ground_y=-3.5, background=(9, 27, 45), cam_y=0.0, cam_size=5.4):
        self.d = {'id': id, 'bounds': list(bounds), 'groundY': ground_y, 'background': list(background),
                  'camera': {'y': cam_y, 'size': cam_size}, 'layers': [], 'markers': [], 'colliders': []}
        self.layers = []

    def layer(self, name, parallax=1.0, order=0, parallax_y=None):
        L = Layer(name, parallax, order, parallax_y)
        self.layers.append(L)
        return L

    def marker(self, id, x, y=None, **extra):
        m = {'id': id, 'x': x, 'y': self.d['groundY'] if y is None else y}
        m.update(extra)
        self.d['markers'].append(m)
        return m

    def collider(self, x, y, w, h, id=''):
        self.d['colliders'].append({'id': id, 'x': x, 'y': y, 'w': w, 'h': h})

    def export(self):
        self.d['layers'] = [L.d for L in self.layers]
        save_json(self.d, 'Levels/' + self.d['id'])
        return self.d
