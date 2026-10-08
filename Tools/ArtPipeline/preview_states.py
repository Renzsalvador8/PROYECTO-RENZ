"""Composites key game states (as Unity would draw them) for art-direction QA."""
import json, copy, sys
from preview import render_level, load_level
import rigtools
from common import *

side = rigtools.load_rig('tester_side')
CLIPS = {c['name']: c for c in json.load(open(GAME + '/Animations/Resources/Animations/tester_clips.json'))['clips']}
META = json.load(open(DATA_OUT + '/Vehicles/ioniq5.json'))


def car_items(x, y, order_base):
    cm = META['sprites']['ioniq5_side_teal_cabin']
    it = lambda s, xx, yy, piv, o: {'sprite': s, 'x': xx, 'y': yy, 'ppu': 200, 'pivot': piv, 'sx': 1, 'sy': 1, 'alpha': 1,
                                    'tint': [1, 1, 1], 'order': o, 'rot': 0}
    items = [it('Art/Drive/cabin_interior', x, y, cm['pivot'], order_base), it(cm['sprite'], x, y, cm['pivot'], order_base + 20)]
    for ax in (META['rearAxleUnits'], META['frontAxleUnits']):
        items.append(it('Art/Vehicles/ioniq5_wheel', x + ax, y + META['wheelRadiusUnits'], [0.5, 0.5], order_base + 30))
    return items


def driver(x, y, clip='sit_drive', t=0.4, order=-850, head=None):
    pose = rigtools.eval_clip(CLIPS[clip], t)
    for s in ('thigh_f', 'thigh_b', 'shin_f', 'shin_b', 'shoe_f', 'shoe_b'):
        pose['slot:' + s] = {'visible': 0}
    a = {'rig': side, 'x': x + 0.446, 'y': y - 0.286, 'order': order, 'pose': pose}
    return a


def drive_state(x=300.0, lane_y=-3.58, cam=None, ortho=None, cam_y=None, out='drive_state.png'):
    lv = load_level('drive')
    l2 = copy.deepcopy(lv)
    for L in l2['layers']:
        if L['name'] == 'props':
            L['items'] += car_items(x, lane_y, 40)
    render_level(l2, cam if cam is not None else x + 2.5, cam_y=cam_y, ortho=ortho, out=SCRATCH + '/' + out, size=(1280, 720),
                 actors=[driver(x, lane_y, order=-850)])


if __name__ == '__main__':
    drive_state()
    drive_state(cam=300.6, cam_y=-3.58 + 1.75, ortho=1.25, out='drive_closeup.png')
