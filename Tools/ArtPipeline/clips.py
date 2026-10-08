"""Authored animation clips for Jean Paul Tester (side rig). Baked to Data/Animations/tester_clips.json.

Angle convention: degrees, counter-clockwise positive, character facing +x (right).
  leg/arm forward swing = +, knee flex = -, elbow flex = +, torso lean forward = -, head look up = +.
"""
import math
import numpy as np
from common import save_json, GAME
import os
from rigtools import load_rig, eval_clip, foot_bottom, world_transforms


def C(target, prop, keys, interp='smooth'):
    return {'target': target, 'prop': prop, 'interp': interp, 'keys': [[round(t, 4), round(v, 4)] for t, v in keys]}


def shift(keys, dt, length):
    out = sorted(((t + dt) % length, v) for t, v in keys)
    return out


def loopify(keys, length):
    """ensure a closing key at t=length equal to t=0 isn't duplicated (loop handles wrap)."""
    return [k for k in keys if k[0] < length - 1e-6]


U0 = (0.016, -0.36)
F0 = (0.104, -0.364)


def ik(tx, ty, flip=False):
    """2-bone IK for an arm. Target = wrist position relative to the shoulder (torso space, units).
    Returns (shoulder_rot, elbow_rot) in degrees, elbow bending on the forward/down side."""
    L1, L2 = math.hypot(*U0), math.hypot(*F0)
    d = min(math.hypot(tx, ty), L1 + L2 - 1e-4)
    d = max(d, abs(L1 - L2) + 1e-4)
    a = math.acos((L1 * L1 + d * d - L2 * L2) / (2 * L1 * d))
    base = math.atan2(ty, tx)
    a1 = base + a if flip else base - a
    ex, ey = L1 * math.cos(a1), L1 * math.sin(a1)
    a2 = math.atan2(ty - ey, tx - ex)
    r_u, r_f = math.atan2(U0[1], U0[0]), math.atan2(F0[1], F0[0])
    sh = math.degrees(a1 - r_u)
    el = math.degrees((a2 - a1) - (r_f - r_u))
    el = (el + 180) % 360 - 180
    return round(sh, 2), round(el, 2)


# ----------------------------------------------------------------------------- walk
WALK_LEN = 1.1
THIGH = [(0.00, 21), (0.10, 17), (0.25, 4), (0.40, -11), (0.50, -19), (0.60, -15), (0.75, 5), (0.88, 19)]
KNEE = [(0.00, -3), (0.10, -15), (0.25, -7), (0.40, -5), (0.50, -24), (0.60, -52), (0.75, -50), (0.88, -14)]
ANKLE = [(0.00, 9), (0.10, 0), (0.25, 0), (0.40, -7), (0.50, -20), (0.60, -10), (0.75, 4), (0.88, 9)]


def scale_t(keys, L):
    return [(t * L, v) for t, v in keys]


def walk_clip(name='walk', L=WALK_LEN, amp=1.0, lean=-3.0):
    th, kn, an = scale_t(THIGH, L), scale_t(KNEE, L), scale_t(ANKLE, L)
    a = lambda ks: [(t, v * amp) for t, v in ks]
    curves = [
        C('thigh_f', 'rot', a(th)), C('knee_f', 'rot', a(kn)), C('ankle_f', 'rot', a(an)),
        C('thigh_b', 'rot', shift(a(th), L / 2, L)), C('knee_b', 'rot', shift(a(kn), L / 2, L)),
        C('ankle_b', 'rot', shift(a(an), L / 2, L)),
        C('shoulder_f', 'rot', [(0, -11 * amp), (L * 0.5, 10 * amp)]),
        C('elbow_f', 'rot', [(0, 6), (L * 0.5, 20 * amp)]),
        C('wrist_f', 'rot', [(0, -2), (L * 0.5, 6)]),
        C('shoulder_b', 'rot', [(0, 10 * amp), (L * 0.5, -11 * amp)]),
        C('elbow_b', 'rot', [(0, 20 * amp), (L * 0.5, 6)]),
        C('torso', 'rot', [(0, lean - 0.6), (L * 0.25, lean + 0.4), (L * 0.5, lean - 0.6), (L * 0.75, lean + 0.4)]),
        C('head', 'rot', [(0, 2.0), (L * 0.25, 1.0), (L * 0.5, 2.0), (L * 0.75, 1.0)]),
    ]
    return {'name': name, 'length': L, 'loop': True, 'curves': curves,
            'events': [{'t': 0.02 * L, 'name': 'footstep'}, {'t': 0.52 * L, 'name': 'footstep'}]}


# ----------------------------------------------------------------------------- idle & reactions
def idle_clip():
    L = 4.2
    return {'name': 'idle', 'length': L, 'loop': True, 'curves': [
        C('torso', 'rot', [(0, 0.0), (L * 0.5, -0.7)]),
        C('torso', 'sy', [(0, 1.0), (L * 0.5, 1.008)]),
        C('head', 'rot', [(0, 0.5), (L * 0.5, -0.4)]),
        C('shoulder_f', 'rot', [(0, 1.0), (L * 0.5, -0.4)]),
        C('shoulder_b', 'rot', [(0, -1.0), (L * 0.5, 0.4)]),
        C('elbow_f', 'rot', [(0, 3.0), (L * 0.5, 4.5)]),
        C('elbow_b', 'rot', [(0, 3.0), (L * 0.5, 4.0)]),
        C('stache', 'rot', [(0, 0), (L * 0.8, 0), (L * 0.85, 2.5), (L * 0.9, 0)]),
    ]}


def pose_clip(name, length, keys_by_target, loop=False, events=None):
    curves = []
    for (target, prop), ks in keys_by_target.items():
        interp = 'step' if prop in ('visible', 'sprite') else 'smooth'
        curves.append(C(target, prop, ks, interp))
    return {'name': name, 'length': length, 'loop': loop, 'curves': curves, 'events': events or []}


MAG_HOLD = ik(0.36, 0.14)
MAG_MID = ik(0.30, -0.18)
MAG_A = ik(0.39, 0.17)
MAG_B = ik(0.34, 0.10)
MAG_WRIST = -38


def raise_magnifier():
    # 0 -> 0.9s: lift magnifier toward the eye and lean in
    return pose_clip('magnifier_raise', 0.9, {
        ('slot:prop_f', 'visible'): [(0, 1)],
        ('shoulder_f', 'rot'): [(0, 0), (0.35, MAG_MID[0]), (0.9, MAG_HOLD[0])],
        ('elbow_f', 'rot'): [(0, 4), (0.35, MAG_MID[1]), (0.9, MAG_HOLD[1])],
        ('wrist_f', 'rot'): [(0, 0), (0.5, MAG_WRIST * 0.6), (0.9, MAG_WRIST)],
        ('torso', 'rot'): [(0, 0), (0.9, -7)],
        ('head', 'rot'): [(0, 0), (0.6, -2), (0.9, -5)],
        ('brow', 'y'): [(0, 0), (0.9, -0.004)],
        ('shoulder_b', 'rot'): [(0, 0), (0.9, -6)],
        ('elbow_b', 'rot'): [(0, 3), (0.9, 12)],
        ('thigh_f', 'rot'): [(0, 0), (0.9, 3)], ('knee_f', 'rot'): [(0, 0), (0.9, -6)], ('ankle_f', 'rot'): [(0, 0), (0.9, 3)],
    }, events=[{'t': 0.15, 'name': 'cloth'}, {'t': 0.6, 'name': 'magnifier'}])


def examine_loop():
    L = 2.4
    return pose_clip('examine', L, {
        ('slot:prop_f', 'visible'): [(0, 1)],
        ('shoulder_f', 'rot'): [(0, MAG_HOLD[0]), (L * 0.3, MAG_A[0]), (L * 0.6, MAG_B[0]), (L, MAG_HOLD[0])],
        ('elbow_f', 'rot'): [(0, MAG_HOLD[1]), (L * 0.3, MAG_A[1]), (L * 0.6, MAG_B[1]), (L, MAG_HOLD[1])],
        ('wrist_f', 'rot'): [(0, MAG_WRIST), (L * 0.5, MAG_WRIST + 6), (L, MAG_WRIST)],
        ('torso', 'rot'): [(0, -7), (L * 0.5, -8.5), (L, -7)],
        ('head', 'rot'): [(0, -5), (L * 0.35, -3), (L * 0.7, -6.5), (L, -5)],
        ('brow', 'y'): [(0, -0.004), (L * 0.5, -0.006), (L, -0.004)],
        ('shoulder_b', 'rot'): [(0, -6)], ('elbow_b', 'rot'): [(0, 12)],
        ('thigh_f', 'rot'): [(0, 3)], ('knee_f', 'rot'): [(0, -6)], ('ankle_f', 'rot'): [(0, 3)],
    }, loop=True)


def lower_magnifier():
    return pose_clip('magnifier_lower', 0.7, {
        ('slot:prop_f', 'visible'): [(0, 1), (0.62, 0)],
        ('shoulder_f', 'rot'): [(0, MAG_HOLD[0]), (0.35, MAG_MID[0]), (0.7, 0)],
        ('elbow_f', 'rot'): [(0, MAG_HOLD[1]), (0.35, MAG_MID[1]), (0.7, 4)],
        ('wrist_f', 'rot'): [(0, MAG_WRIST), (0.7, 0)],
        ('torso', 'rot'): [(0, -7), (0.7, 0)],
        ('head', 'rot'): [(0, -5), (0.7, 0)],
        ('shoulder_b', 'rot'): [(0, -6), (0.7, 0)], ('elbow_b', 'rot'): [(0, 12), (0.7, 3)],
        ('thigh_f', 'rot'): [(0, 3), (0.7, 0)], ('knee_f', 'rot'): [(0, -6), (0.7, 0)], ('ankle_f', 'rot'): [(0, 3), (0.7, 0)],
    }, events=[{'t': 0.3, 'name': 'cloth'}])


def look_around():
    L = 3.2
    return pose_clip('look_around', L, {
        ('head', 'rot'): [(0, 0), (0.35, 9), (1.1, 9), (1.4, -7), (2.2, -7), (2.6, 2), (L, 0)],
        ('torso', 'rot'): [(0, 0), (0.4, 1.5), (1.4, -1.0), (2.6, 0), (L, 0)],
        ('brow', 'y'): [(0, 0), (0.35, 0.008), (1.1, 0.008), (1.4, 0), (L, 0)],
        ('shoulder_f', 'rot'): [(0, 0), (1.0, 2), (2.0, -2), (L, 0)],
    }, events=[{'t': 1.25, 'name': 'flip'}, {'t': 2.35, 'name': 'flip'}])


def skeptical():
    L = 2.2
    return pose_clip('skeptical', L, {
        ('head', 'rot'): [(0, 0), (0.25, 4), (1.6, 4.5), (L, 0)],
        ('brow', 'y'): [(0, 0), (0.18, 0.016), (1.7, 0.016), (L, 0)],
        ('brow', 'rot'): [(0, 0), (0.18, 6), (1.7, 6), (L, 0)],
        ('torso', 'rot'): [(0, 0), (0.3, 2.0), (1.6, 2.0), (L, 0)],
        ('stache', 'rot'): [(0, 0), (0.3, -3), (1.6, -3), (L, 0)],
    })


STACHE_MID = ik(0.24, -0.16)
STACHE = ik(0.29, 0.03)


def mustache_adjust():
    L = 2.6
    return pose_clip('mustache_adjust', L, {
        ('shoulder_f', 'rot'): [(0, 0), (0.25, STACHE_MID[0]), (0.5, STACHE[0]), (2.0, STACHE[0]), (2.25, STACHE_MID[0]), (L, 0)],
        ('elbow_f', 'rot'): [(0, 4), (0.25, STACHE_MID[1]), (0.5, STACHE[1]), (2.0, STACHE[1]), (2.25, STACHE_MID[1]), (L, 4)],
        ('wrist_f', 'rot'): [(0, 0), (0.5, 14), (0.8, 24), (1.1, 8), (1.4, 24), (1.7, 10), (2.0, 14), (L, 0)],
        ('head', 'rot'): [(0, 0), (0.5, 5), (2.0, 5), (L, 0)],
        ('stache', 'rot'): [(0, 0), (0.8, 5), (1.1, -2), (1.4, 5), (1.7, -1), (2.1, 0)],
        ('stache', 'y'): [(0, 0), (0.8, 0.004), (1.4, 0.004), (2.1, 0)],
        ('torso', 'rot'): [(0, 0), (0.5, 1.5), (2.0, 1.5), (L, 0)],
        ('brow', 'y'): [(0, 0), (0.6, 0.006), (2.0, 0.006), (L, 0)],
    }, events=[{'t': 0.2, 'name': 'cloth'}, {'t': 0.8, 'name': 'stache'}, {'t': 1.4, 'name': 'stache'}])


def disappointed():
    L = 2.6
    return pose_clip('disappointed', L, {
        ('head', 'rot'): [(0, 0), (0.6, -11), (1.9, -12), (L, 0)],
        ('torso', 'rot'): [(0, 0), (0.6, -4), (1.9, -4.5), (L, 0)],
        ('torso', 'sy'): [(0, 1), (0.3, 1.015), (0.9, 0.985), (1.9, 0.985), (L, 1)],
        ('hip', 'y'): [(0, 0), (0.9, -0.012), (1.9, -0.012), (L, 0)],
        ('shoulder_f', 'rot'): [(0, 0), (0.7, -3), (1.9, -3), (L, 0)],
        ('shoulder_b', 'rot'): [(0, 0), (0.7, -3), (1.9, -3), (L, 0)],
        ('elbow_f', 'rot'): [(0, 4), (0.7, 1), (L, 4)],
        ('brow', 'y'): [(0, 0), (0.6, -0.006), (1.9, -0.006), (L, 0)],
        ('stache', 'rot'): [(0, 0), (0.6, -4), (1.9, -4), (L, 0)],
    }, events=[{'t': 0.25, 'name': 'sigh'}])


def impressed():
    L = 2.4
    return pose_clip('impressed', L, {
        ('head', 'rot'): [(0, 0), (0.35, 3), (0.8, -6), (1.1, 1), (1.8, 1.5), (L, 0)],
        ('brow', 'y'): [(0, 0), (0.3, 0.012), (1.8, 0.01), (L, 0)],
        ('stache', 'rot'): [(0, 0), (0.9, 0), (1.1, 6), (1.9, 6), (L, 0)],
        ('stache', 'y'): [(0, 0), (1.1, 0.006), (1.9, 0.006), (L, 0)],
        ('torso', 'rot'): [(0, 0), (0.4, 2.5), (1.8, 1.5), (L, 0)],
    })


REACH = ik(0.55, -0.22)
HOLD_F = ik(0.30, -0.26)
HOLD_B = ik(0.24, -0.20)


def receive_trophy():
    L = 1.6
    return pose_clip('receive', L, {
        ('shoulder_f', 'rot'): [(0, 0), (0.5, REACH[0]), (0.8, REACH[0]), (L, HOLD_F[0])],
        ('elbow_f', 'rot'): [(0, 4), (0.5, REACH[1]), (0.8, REACH[1]), (L, HOLD_F[1])],
        ('wrist_f', 'rot'): [(0, 0), (0.5, -10), (L, -30)],
        ('torso', 'rot'): [(0, 0), (0.5, -8), (0.8, -8), (L, 1)],
        ('head', 'rot'): [(0, 0), (0.5, -6), (L, -3)],
    }, events=[{'t': 0.75, 'name': 'grab'}])


def hold_trophies():
    L = 3.6
    return pose_clip('hold', L, {
        ('shoulder_f', 'rot'): [(0, HOLD_F[0]), (L * 0.5, HOLD_F[0] - 1)],
        ('elbow_f', 'rot'): [(0, HOLD_F[1]), (L * 0.5, HOLD_F[1] + 2)],
        ('wrist_f', 'rot'): [(0, -30), (L * 0.5, -28)],
        ('shoulder_b', 'rot'): [(0, HOLD_B[0]), (L * 0.5, HOLD_B[0] - 1)],
        ('elbow_b', 'rot'): [(0, HOLD_B[1]), (L * 0.5, HOLD_B[1] + 2)],
        ('wrist_b', 'rot'): [(0, -30), (L * 0.5, -28)],
        ('torso', 'rot'): [(0, 1.0), (L * 0.5, 0.4)],
        ('torso', 'sy'): [(0, 1.0), (L * 0.5, 1.007)],
        ('head', 'rot'): [(0, -3), (L * 0.5, -2)],
    }, loop=True)


DRIVE_F = ik(0.64, -0.16)
DRIVE_B = ik(0.60, -0.14)


def sit_drive():
    L = 3.0
    return pose_clip('sit_drive', L, {
        ('torso', 'rot'): [(0, 5.0), (L * 0.5, 4.4)],
        ('head', 'rot'): [(0, -4.0), (L * 0.3, -3.2), (L * 0.6, -4.4)],
        ('shoulder_f', 'rot'): [(0, DRIVE_F[0]), (L * 0.5, DRIVE_F[0] + 1)],
        ('elbow_f', 'rot'): [(0, DRIVE_F[1]), (L * 0.5, DRIVE_F[1] - 1.5)],
        ('wrist_f', 'rot'): [(0, -40), (L * 0.5, -38)],
        ('shoulder_b', 'rot'): [(0, DRIVE_B[0]), (L * 0.5, DRIVE_B[0] - 1)],
        ('elbow_b', 'rot'): [(0, DRIVE_B[1]), (L * 0.5, DRIVE_B[1] + 1)],
        ('wrist_b', 'rot'): [(0, -40)],
    }, loop=True)


def sit_stache():
    L = 2.6
    return pose_clip('sit_stache', L, {
        ('torso', 'rot'): [(0, 5.0), (L, 5.0)],
        ('head', 'rot'): [(0, -4.0), (0.5, 3.0), (2.0, 3.0), (L, -2.0)],
        ('shoulder_f', 'rot'): [(0, DRIVE_F[0]), (0.25, STACHE_MID[0]), (0.5, STACHE[0]), (2.0, STACHE[0]), (2.3, STACHE_MID[0]), (L, DRIVE_F[0])],
        ('elbow_f', 'rot'): [(0, DRIVE_F[1]), (0.25, STACHE_MID[1]), (0.5, STACHE[1]), (2.0, STACHE[1]), (2.3, STACHE_MID[1]), (L, DRIVE_F[1])],
        ('wrist_f', 'rot'): [(0, -40), (0.5, 14), (0.8, 24), (1.1, 8), (1.4, 24), (1.7, 10), (2.0, 14), (L, -40)],
        ('stache', 'rot'): [(0, 0), (0.8, 5), (1.1, -2), (1.4, 5), (1.7, -1), (2.1, 0)],
        ('shoulder_b', 'rot'): [(0, DRIVE_B[0])], ('elbow_b', 'rot'): [(0, DRIVE_B[1])], ('wrist_b', 'rot'): [(0, -40)],
    }, events=[{'t': 0.8, 'name': 'stache'}, {'t': 1.4, 'name': 'stache'}])


def bake_walk(rig, clip, samples=44):
    L = clip['length']
    ys = []
    stance_x = []
    for i in range(samples):
        t = L * i / samples
        pose = eval_clip(clip, t)
        yf, ptsf = foot_bottom(rig, pose, 'f')
        yb, ptsb = foot_bottom(rig, pose, 'b')
        ys.append((t, -min(yf, yb)))
        Wt = world_transforms(rig, pose)
        stance_x.append((t, Wt['ankle_f'][0, 2], yf <= yb))
    clip['curves'].append(C('hip', 'y', ys, 'linear'))
    # speed: average backward velocity of the planted (lower) front foot
    vs = []
    for (t0, x0, s0), (t1, x1, s1) in zip(stance_x, stance_x[1:]):
        if s0 and s1:
            vs.append(-(x1 - x0) / (t1 - t0))
    clip['speed'] = round(float(np.median(vs)), 4)
    return clip


def build():
    rig = load_rig('tester_side')
    clips = [bake_walk(rig, walk_clip()), idle_clip(), raise_magnifier(), examine_loop(), lower_magnifier(),
             look_around(), skeptical(), mustache_adjust(), disappointed(), impressed(), receive_trophy(), hold_trophies(),
             sit_drive(), sit_stache()]
    save_json({'clips': clips}, 'tester_clips', root=os.path.join(GAME, 'Animations', 'Resources', 'Animations'))
    return rig, clips


if __name__ == '__main__':
    rig, clips = build()
    for c in clips:
        print(c['name'], c['length'], c.get('speed', ''))
