"""Renders documentation previews of key game states (composited from the real game data/art).
These approximate what Unity draws (no UI text, no runtime effects) — they are not in-engine screenshots."""
import json, copy, os
import skia
from PIL import Image, ImageDraw, ImageFilter
from preview import render_level, load_level, load_sprite
import rigtools
from preview_states import car_items, driver, CLIPS
from common import *

OUT = os.path.join(ROOT, 'Docs', 'previews')
os.makedirs(OUT, exist_ok=True)
W, H = 1280, 720
side = rigtools.load_rig('tester_side')
front = rigtools.load_rig('tester_front')


def finish(im, name, vignette=0.55):
    im = im.convert('RGBA')
    v = Image.open(UI_OUT + '/vignette.png').resize(im.size)
    a = v.split()[3].point(lambda p: int(p * vignette))
    v.putalpha(a)
    im.alpha_composite(v)
    im.convert('RGB').save(os.path.join(OUT, name + '.jpg'), quality=88)


def pose(clip, t):
    return rigtools.eval_clip(CLIPS[clip], t)


def main():
    # 1 title (camera centre (0.4, 0); Jean Paul at (-3.4, -4.2), scale 0.78)
    import numpy as np
    t = Image.open(ART_OUT + '/Menu/title_dusk.png').convert('RGBA')
    x0 = 1064 - 960
    t = t.crop((x0, 0, x0 + 1920, 1080))
    s = skia.Surface(1920, 1080); c = s.getCanvas()
    c.drawImage(skia.Image.fromarray(np.asarray(t).copy(), colorType=skia.kRGBA_8888_ColorType), 0, 0)
    rigtools.render(side, {}, size=(1920, 1080), ppu_out=78, origin=(960 + (-3.4 - 0.4) * 100, 540 + 4.2 * 100), canvas=c)
    img = Image.fromarray(s.makeImageSnapshot().toarray(colorType=skia.kRGBA_8888_ColorType))
    img.alpha_composite(Image.open(UI_OUT + '/title_lockup.png').resize((1200, 390)), (360, 65))
    finish(img.resize((W, H)), '01_title', 0.85)
    # 2 arrival
    a = Image.open(ART_OUT + '/Showroom/exterior_day.png').convert('RGBA').crop((64, 0, 1984, 1080)).resize((W, H))
    finish(a, '02_arrival')
    # 3 showroom station 1
    lv = load_level('showroom')
    im = render_level(lv, 20.5, size=(W, H), actors=[
        {'rig': side, 'x': 17.6, 'y': -3.5, 'order': -95, 'pose': pose('examine', 0.5), 'slots': {'prop_f': 'magnifier'}},
    ])
    finish(im, '03_showroom_station1')
    # 4 exterior inspection (lens composited)
    bg = Image.open(ART_OUT + '/Inspection/bg_exterior.png').convert('RGBA')
    hero = Image.open(ART_OUT + '/Inspection/ioniq5_34_teal.png')
    sc = bg.copy(); sc.alpha_composite(hero)
    hs = json.load(open(DATA_OUT + '/Vehicles/ioniq5.json'))['inspectionHotspots']
    cx, cy = hs['headlights']['center']; R = 125; Z = 2.1
    big = sc.resize((int(sc.width * Z), int(sc.height * Z)), Image.LANCZOS)
    ox, oy = int(cx * Z - cx), int(cy * Z - cy)
    crop = big.crop((ox, oy, ox + sc.width, oy + sc.height))
    m = Image.new('L', sc.size, 0); ImageDraw.Draw(m).ellipse([cx - R, cy - R, cx + R, cy + R], fill=255)
    sc.paste(crop, (0, 0), m)
    d = ImageDraw.Draw(sc, 'RGBA')
    d.ellipse([cx - R, cy - R, cx + R, cy + R], outline=(182, 120, 84, 255), width=14)
    d.arc([cx - R - 26, cy - R - 26, cx + R + 26, cy + R + 26], -90, 150, fill=(182, 120, 84, 255), width=8)
    nb = Image.open(UI_OUT + '/paper_card.png').resize((470, 860)); sc.alpha_composite(nb, (40, 110))
    finish(sc.resize((W, H)), '04_exterior_inspection')
    # 5 interior detail test
    it = Image.open(ART_OUT + '/Inspection/ioniq5_interior.png').convert('RGBA')
    nb = Image.open(UI_OUT + '/paper_card.png').resize((470, 860)); it.alpha_composite(nb, (40, 110))
    y = 310
    for k in ('volante', 'costura', 'rejilla', 'reloj'):
        c = Image.open(ART_OUT + '/Inspection/clue_' + k + '.png').resize((176, 126))
        it.alpha_composite(c, (100, y)); y += 152
    finish(it.resize((W, H)), '05_interior_detail_test')
    # 6 showroom station 2
    im = render_level(lv, 43.0, size=(W, H), actors=[{'rig': side, 'x': 41.2, 'y': -3.5, 'order': -95, 'pose': pose('skeptical', 1.0)}])
    finish(im, '06_showroom_station2')
    # 7 drive
    dl = load_level('drive')
    l2 = copy.deepcopy(dl)
    x = 248.0
    for L in l2['layers']:
        if L['name'] == 'props':
            L['items'] += car_items(x, -2.72, 5)
    im = render_level(l2, x + 2.5, size=(W, H), actors=[driver(x, -2.72, order=-893)])
    finish(im, '07_test_drive')
    # 8 drive close-up
    l3 = copy.deepcopy(dl)
    x = 600.0
    for L in l3['layers']:
        if L['name'] == 'props':
            L['items'] += car_items(x, -3.58, 40)
    im = render_level(l3, x + 0.5, cam_y=-3.58 + 1.62, ortho=1.25, size=(W, H), actors=[driver(x, -3.58, 'sit_stache', 1.2, -850)])
    finish(im, '08_drive_closeup', 0.7)
    # 9 zenith studio
    zl = load_level('zenith')
    im = render_level(zl, 10.0, size=(W, H), actors=[{'rig': side, 'x': 12.2, 'y': -3.5, 'order': -95, 'pose': pose('idle', 1.0)}])
    finish(im, '09_zenith_studio')
    # 10 awards stage
    st = [m for m in zl['markers'] if m['id'] == 'awards'][0]['x']
    im = render_level(zl, st, ortho=5.9, cam_y=0.45, size=(W, H), actors=[{'rig': side, 'x': st - 1.15, 'y': -3.5, 'order': -95, 'pose': pose('receive', 0.6)}])
    finish(im, '10_awards_stage')
    # 11 finale close-up
    head_y = -4.35 + front['bones'][2]['pos'][1]
    cy, size = head_y - 0.36, 0.98
    ppu = H / (2 * size)
    s = skia.Surface(W, H); c = s.getCanvas(); c.clear(skia.Color(6, 12, 20))
    def draw(sprite, x, y, pivot, sx=1, sy=1, alpha=1.0):
        img = load_sprite(sprite); iw, ih = img.width(), img.height(); k = ppu / 100
        c.save(); c.translate(W / 2 + x * ppu, H / 2 - (y - cy) * ppu); c.scale(k * sx, k * sy); c.translate(-pivot[0] * iw, -(1 - pivot[1]) * ih)
        p = skia.Paint(AntiAlias=True); p.setAlphaf(alpha)
        c.drawImage(img, 0, 0, skia.SamplingOptions(skia.FilterMode.kLinear, skia.MipmapMode.kLinear), p); c.restore()
    draw('Art/Zenith/stage', 0, -4.2, (0.5, 0))
    draw('UI/circle_soft', 0, -2.6, (0.5, 0.5), 2.2, 2.6, 0.22)
    rigtools.render(front, {}, size=(W, H), ppu_out=ppu, origin=(W / 2, H / 2 - (-4.35 - cy) * ppu), canvas=c, slot_sprites={'head': 'head_smile'})
    img = s.makeImageSnapshot()
    finish(Image.fromarray(img.toarray(colorType=skia.kRGBA_8888_ColorType)), '11_finale_smile', 0.75)
    # 12 end screen
    e = Image.new('RGBA', (W, H), (9, 27, 45, 255))
    lock = Image.open(UI_OUT + '/end_lockup.png').resize((860, 280))
    e.alpha_composite(lock, (210, 150))
    finish(e, '12_end_screen', 0.6)
    print('previews ->', OUT)


if __name__ == '__main__':
    main()
