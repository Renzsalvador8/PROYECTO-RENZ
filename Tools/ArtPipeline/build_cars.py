"""Exports every car asset used by the game."""
import json
import numpy as np
from PIL import Image
from common import *
from car_model import *

SIDE_PPU = 200.0         # sprite pixels per world unit
MM_PER_UNIT = 770.0      # 1 world unit = 0.77 m (Tester is 2.4 units ~ 1.85 m)
SCALE = SIDE_PPU / MM_PER_UNIT   # px per mm


def side_sprite(paint, name, door_open=0.0, glass_alpha=1.0, wheels=False, lights=True):
    W = int(LEN * SCALE + 40)
    H = int(1700 * SCALE + 40)
    cam = Camera('side', size=(W, H), scale=SCALE, origin=(20, H - 20))
    cp = CarPainter(cam, paint, draw_wheels=wheels, door_open=door_open, glass_alpha=glass_alpha, lights_on=lights)
    img = cp.render().image(seed=hash(name) % 1000)
    save_png(img, 'Vehicles/' + name)
    # pivot: ground under the car centre, in normalised sprite coords (Unity: bottom-left origin)
    return {'sprite': 'Art/Vehicles/' + name, 'ppu': SIDE_PPU,
            'pivot': [round((20 + LEN * SCALE / 2) / W, 5), round(20 / H, 5)],
            'size': [W, H]}


def build():
    meta = {'mmPerUnit': MM_PER_UNIT, 'lengthUnits': round(LEN / MM_PER_UNIT, 4),
            'wheelRadiusUnits': round(WHEEL_R / MM_PER_UNIT, 4),
            'rearAxleUnits': round((R_AX - LEN / 2) / MM_PER_UNIT, 4),
            'frontAxleUnits': round((F_AX - LEN / 2) / MM_PER_UNIT, 4), 'sprites': {}}
    for paint in ('teal', 'white', 'bronze', 'midnight'):
        meta['sprites']['ioniq5_side_' + paint] = side_sprite(paint, 'ioniq5_side_' + paint, wheels=True)
    meta['sprites']['ioniq5_side_teal_cabin'] = side_sprite('teal', 'ioniq5_side_teal_cabin', glass_alpha=0.42)
    meta['sprites']['ioniq5_side_midnight_nowheels'] = side_sprite('midnight', 'ioniq5_side_midnight_nowheels')
    meta['sprites']['ioniq5_side_white_dooropen'] = side_sprite('white', 'ioniq5_side_white_dooropen', door_open=1.0, wheels=True)
    # wheel sprite
    wimg = render_wheel_sprite(SCALE)
    save_png(wimg, 'Vehicles/ioniq5_wheel')
    meta['sprites']['ioniq5_wheel'] = {'sprite': 'Art/Vehicles/ioniq5_wheel', 'ppu': SIDE_PPU, 'pivot': [0.5, 0.5],
                                       'size': list(wimg.size)}
    # three-quarter hero for the exterior inspection (1920x1080 composition, transparent background)
    cam = Camera('persp', pos=(7600, 1180, 4700), target=(2450, 690, 0), fov=25, size=(1920, 1080))
    cp = CarPainter(cam, 'teal').render()
    hero = cp.image(seed=21)
    save_png(hero, 'Inspection/ioniq5_34_teal')
    # hotspots for the five inspection targets (screen px, origin top-left of the 1920x1080 frame)
    F = lambda z, y: (4600 - (abs(z) / HALF_W) ** 2 * 70 - max(0, y - 700) * 0.12, y, z)
    def pt(p):
        x, y = cam.p(p)
        return [round(x, 1), round(y, 1)]
    hs = {
        'headlights': {'center': pt(F(HALF_W - 200, 840)), 'radius': 70},
        'wheels': {'center': pt((F_AX, WHEEL_R, HALF_W - 40)), 'radius': 105},
        'bodywork': {'center': pt((3700, 1045, 300)), 'radius': 85},
        'doors': {'center': pt((2420, 820, HALF_W)), 'radius': 70},
        'grille': {'center': pt(F(0, 500)), 'radius': 85},
    }
    meta['inspectionHotspots'] = hs
    save_json(meta, 'Vehicles/ioniq5')
    return meta


if __name__ == '__main__':
    m = build()
    print(json.dumps(m['inspectionHotspots']))
