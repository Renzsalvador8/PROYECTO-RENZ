"""All level layouts. Run to export Data/Levels/*.json."""
from levelkit import *

GROUND = -3.5
WALL_BASE = -2.4


def showroom():
    L = Level('showroom', bounds=(-2.0, 74.0), ground_y=GROUND, background=(200, 210, 214))
    far = L.layer('far', 0.3, -1000, parallax_y=0.3)
    for a in (-6, 28, 62, 96):
        far.add('Art/Showroom/city_far', a, -2.6, ppu=60, pivot=(0.5, 0.0))
    shafts = L.layer('shafts', 0.88, -820)
    wall = L.layer('wall', 0.9, -800)
    seq = ['window', 'window_b', 'window', 'solid', 'solid', 'window', 'window_b', 'window', 'brand', None, None,
           'window', 'window_b', 'window', 'window', 'solid', 'window', 'window_b', 'exit', None]
    a = -12.0
    for k in seq:
        if k is None:
            continue
        name = 'bay_' + k
        w = img_size('Art/Showroom/' + name)[0] / 100.0
        wall.add('Art/Showroom/' + name, a + w / 2, WALL_BASE, pivot=(0.5, 0.0))
        if k == 'exit':
            L.marker('exit', a + w / 2)
        if k == 'brand':
            L.marker('brand', a + w / 2)
        a += w
    while a < 90:
        wall.add('Art/Showroom/bay_window', a + 2.0, WALL_BASE, pivot=(0.5, 0.0)); a += 4.0
    for ax in (2, 14, 34, 50):
        shafts.add('Art/Showroom/light_shaft', ax, -3.0, pivot=(0.5, 0.0), alpha=0.9)
    mid = L.layer('mid', 0.95, -600)
    mid.add('Art/Showroom/coffee_station', 3.0, WALL_BASE - 0.35, id='coffee')
    mid.add('Art/Showroom/reception', 8.5, WALL_BASE - 0.4, id='reception')
    mid.add('Art/Showroom/plant_mid', 12.2, WALL_BASE - 0.3)
    mid.add('Art/Showroom/plant_mid', 27.0, WALL_BASE - 0.3, flip=True)
    mid.add('Art/Showroom/platform', 53.0, WALL_BASE - 0.75, sx=0.85, sy=0.85)
    mid.add('Art/Vehicles/ioniq5_side_bronze', 53.0, WALL_BASE - 0.45, ppu=200, pivot=(0.5, 0.017), sx=-0.85, sy=0.85)
    mid.add('Art/Showroom/plant_mid', 57.5, WALL_BASE - 0.3)
    floor = L.layer('floor', 1.0, -500)
    floor.tile('Art/Showroom/floor', -14, 92, WALL_BASE, pivot=(0.0, 1.0))
    play = L.layer('play', 1.0, -100)
    # station 1 — exterior inspection (teal IONIQ 5 on a turntable)
    play.add('Art/Showroom/platform', 20.0, GROUND + 0.05, pivot=(0.5, 0.5), order=-20)
    play.add('Art/Vehicles/ioniq5_side_teal', 20.0, GROUND + 0.12, ppu=200, pivot=(0.5, 0.017), order=-10, id='car_station1')
    play.add('Art/Vehicles/ioniq5_side_teal', 20.0, GROUND + 0.16, ppu=200, pivot=(0.5, 0.017), sy=-0.55, alpha=0.16, order=-30)
    play.add('Art/Showroom/sign_station1', 15.2, WALL_BASE - 0.2, order=-40)
    play.add('Art/Showroom/spot_cone', 20.0, GROUND - 0.6, pivot=(0.5, 0.0), sx=1.1, sy=1.0, order=-5, alpha=0.9)
    play.add('Art/Showroom/spot_cone', 43.0, GROUND - 0.6, pivot=(0.5, 0.0), sx=1.1, sy=1.0, order=-5, alpha=0.9)
    play.add('Art/Showroom/brochure_stand', 31.5, GROUND + 0.1, order=-40, id='brochure')
    # station 2 — interior inspection (white IONIQ 5, driver's door open)
    play.add('Art/Showroom/platform', 43.0, GROUND + 0.05, pivot=(0.5, 0.5), order=-20)
    play.add('Art/Vehicles/ioniq5_side_white_dooropen', 43.0, GROUND + 0.12, ppu=200, pivot=(0.5, 0.017), order=-10, id='car_station2')
    play.add('Art/Vehicles/ioniq5_side_white_dooropen', 43.0, GROUND + 0.16, ppu=200, pivot=(0.5, 0.017), sy=-0.55, alpha=0.14, order=-30)
    play.add('Art/Showroom/sign_station2', 37.0, WALL_BASE - 0.2, order=-40)
    fg = L.layer('fg', 1.28, 500, parallax_y=1.1)
    for ax in (11.0, 33.8, 64.5):
        fg.add('Art/Showroom/column_fg', ax, -7.0, pivot=(0.5, 0.0), sx=0.8)
    for ax in (-1.0, 56.5):
        fg.add('Art/Showroom/plant_fg', ax, -6.4, pivot=(0.5, 0.0), sx=1.1, sy=1.1)
    # gameplay markers
    L.marker('spawn', 2.0)
    L.marker('station1', 21.5, prompt='PRESIONA E PARA INSPECCIONAR', radius=2.2)
    L.marker('station2', 41.6, prompt='PRESIONA E PARA INSPECCIONAR', radius=2.0)
    L.marker('coffee', 3.0, prompt='PRESIONA E PARA OBSERVAR', radius=1.2)
    L.marker('reception', 8.5, prompt='PRESIONA E PARA OBSERVAR', radius=1.6)
    L.marker('brochure', 31.5, prompt='PRESIONA E PARA OBSERVAR', radius=1.2)
    L.marker('bronze_car', 53.0, prompt='PRESIONA E PARA OBSERVAR', radius=2.0)
    L.colliders = None
    L.collider(-2.5, 0, 1.0, 12, 'wall_left')
    L.collider(74.5, 0, 1.0, 12, 'wall_right')
    return L.export()


if __name__ == '__main__':
    import sys
    showroom()
    print('levels exported')


ROAD_TOP = -1.9
FAR_LANE = -2.72
NEAR_LANE = -3.58


def drive():
    L = Level('drive', bounds=(-14.0, 640.0), ground_y=NEAR_LANE, background=(176, 196, 206))
    sk = L.layer('sky', 0.0, -2000, parallax_y=0.0)
    sk.add_local('Art/Drive/sky', 0, -5.6, ppu=100, pivot=(0.5, 0.0), sx=34, sy=1.15)
    an = L.layer('andes', 0.03, -1900, parallax_y=0.03)
    for lx in (-17, 17, 51):
        an.add_local('Art/Drive/andes', lx, -1.0, ppu=60, pivot=(0.5, 0.0))
    sl = L.layer('skyline', 0.12, -1800, parallax_y=0.12)
    for i in range(5):
        sl.add_local('Art/Drive/skyline', -14 + i * 29.2, -1.4, ppu=70, pivot=(0.5, 0.0), flip=(i % 2 == 1))
    mid = L.layer('city', 0.45, -1600, parallax_y=0.45)
    for i in range(22):
        mid.add_local('Art/Drive/city_mid_' + ('a' if i % 2 == 0 else 'b'), -14 + i * 14.7, -1.75, ppu=100, pivot=(0.5, 0.0),
                      sx=0.72, sy=0.72, tint=(0.86, 0.9, 0.95))
    near = L.layer('near', 0.8, -1400)
    import random
    rnd = random.Random(7)
    x = -12.0
    while x < 520:
        if rnd.random() < 0.55:
            k = rnd.uniform(0.8, 1.0)
            near.add_local('Art/Drive/' + rnd.choice(['tree', 'tree_b']), x, -1.75, ppu=100, pivot=(0.5, 0.0), sx=k, sy=k, tint=(0.8, 0.86, 0.84))
        else:
            near.add_local('Art/Drive/lamp', x, -1.75, ppu=100, pivot=(0.5, 0.0))
        x += rnd.uniform(7, 11)
    road = L.layer('road', 1.0, -1000)
    road.tile('Art/Drive/road', -24, 664, ROAD_TOP + 0.4, pivot=(0.0, 1.0))
    props = L.layer('props', 1.0, -900)
    props.add('Art/Drive/garage_exit', -6.0, ROAD_TOP + 0.3, pivot=(0.5, 0.0), order=-50)
    # traffic light + stop line
    props.add('Art/Drive/stop_line', 110.0, ROAD_TOP - 0.05, pivot=(0.5, 1.0), order=-60, id='stop_line')
    props.add('Art/Drive/traffic_light', 112.5, ROAD_TOP - 0.05, pivot=(0.5, 0.0), order=-40, id='traffic_light')
    # obstacle in the near lane: delivery van + cones
    for cx in (240.5, 242.5, 244.5):
        props.add('Art/Drive/cone', cx, NEAR_LANE - 0.05, pivot=(0.5, 0.0), order=40)
    props.add('Art/Drive/van', 252.0, NEAR_LANE - 0.1, pivot=(0.5, 0.06), order=30, id='van')
    # school zone
    props.add('Art/Drive/sign_school', 360.0, ROAD_TOP - 0.05, pivot=(0.5, 0.0), order=-40)
    props.add('Art/Drive/sign_school_end', 470.0, ROAD_TOP - 0.05, pivot=(0.5, 0.0), order=-40)
    # parking target
    props.add('Art/Drive/parking_box', 600.0, NEAR_LANE + 0.05, pivot=(0.5, 0.5), order=-80, id='parking_box')
    props.add('Art/Drive/sign_parking', 604.5, ROAD_TOP - 0.05, pivot=(0.5, 0.0), order=-40)
    fg = L.layer('fg', 1.35, 500, parallax_y=1.0)
    x = -20.0
    while x < 880:
        fg.add_local('Art/Drive/hedge_fg', x, -6.9, ppu=100, pivot=(0.5, 0.0))
        x += 30.0
    L.marker('start', 0.0, NEAR_LANE)
    L.marker('stop_line', 110.0, NEAR_LANE)
    L.marker('traffic_light', 112.5, ROAD_TOP + 5.0)
    L.marker('obstacle', 239.5, NEAR_LANE, length=19.0)
    L.marker('school_start', 360.0, NEAR_LANE, limit_kmh=30)
    L.marker('school_end', 470.0, NEAR_LANE)
    L.marker('parking', 600.0, NEAR_LANE, tolerance=1.2)
    L.marker('far_lane', 0.0, FAR_LANE)
    L.marker('near_lane', 0.0, NEAR_LANE)
    return L.export()


if __name__ == '__main__':
    drive()


def zenith():
    L = Level('zenith', bounds=(-2.0, 48.0), ground_y=GROUND, background=(6, 12, 20))
    wall = L.layer('wall', 0.9, -800)
    a = -12.0
    for k in ['led', 'plain', 'led', 'plain', 'plain', 'led', 'plain', 'plain', 'led', 'plain', 'logo', 'led', 'plain']:
        w = img_size('Art/Zenith/bay_' + k)[0] / 100.0
        wall.add('Art/Zenith/bay_' + k, a + w / 2, WALL_BASE, pivot=(0.5, 0.0))
        if k == 'logo':
            L.marker('logo', a + w / 2)
        a += w
    wall.add('Art/Zenith/stage', a + 7.0, WALL_BASE, pivot=(0.5, 0.0))
    L.marker('stage', a + 7.0)
    stage_x = a + 7.0
    a += 14.0
    while a < 70:
        wall.add('Art/Zenith/bay_plain', a + 2.0, WALL_BASE, pivot=(0.5, 0.0)); a += 4.0
    deco = L.layer('deco', 0.9, -780)
    deco.add('Art/Zenith/poster_car', 4.2, 1.35, pivot=(0.5, 0.0), sx=0.66, sy=0.66)
    deco.add('Art/Zenith/poster_mountain', 7.0, 1.35, pivot=(0.5, 0.0), sx=0.66, sy=0.66)
    deco.add('Art/Zenith/poster_tester', 11.4, 0.2, pivot=(0.5, 0.0), sx=0.66, sy=0.66, id='poster_tester')
    deco.add('Art/Zenith/storyboard', 20.5, -0.3, pivot=(0.5, 0.0), sx=0.85, sy=0.85, id='storyboard')
    mid = L.layer('mid', 0.95, -600)
    mid.add('Art/Zenith/desk', 8.0, WALL_BASE - 0.4, id='desk')
    mid.add('Art/Props/chair', 6.6, WALL_BASE - 0.95, ppu=150)
    mid.add('Art/Zenith/softbox', 14.6, WALL_BASE - 0.5, sx=0.85, sy=0.85)
    mid.add('Art/Showroom/plant_mid', 1.5, WALL_BASE - 0.3, tint=(0.7, 0.78, 0.86))
    mid.add('Art/Showroom/plant_mid', 27.5, WALL_BASE - 0.3, tint=(0.7, 0.78, 0.86), flip=True)
    floor = L.layer('floor', 1.0, -500)
    floor.tile('Art/Zenith/floor', -14, 70, WALL_BASE, pivot=(0.0, 1.0))
    play = L.layer('play', 1.0, -100)
    play.add('Art/Zenith/tripod_camera', 22.5, GROUND + 0.6, pivot=(0.5, 0.0), sx=0.75, sy=0.75, order=-40, id='camera')
    # awards: two pedestals under spotlights
    px1, px2 = stage_x - 2.2, stage_x + 2.2
    for px, aw, plq, ppu, idp in ((px1, 'award_lux_grand_prix', 'plaque_lux', 340, 'lux'), (px2, 'award_effie_bronze', 'plaque_effie', 420, 'effie')):
        play.add('Art/Showroom/spot_cone', px, GROUND - 0.4, pivot=(0.5, 0.0), sx=0.75, sy=1.05, order=-5, alpha=0.85, tint=(1.0, 0.95, 0.88))
        play.add('Art/Zenith/pedestal', px, GROUND + 0.55, pivot=(0.5, 0.0), sx=0.36, sy=0.36, order=-30, id='pedestal_' + idp)
        play.add('Art/Props/' + aw, px, GROUND + 0.55 + 4.2 * 0.36 - 0.12, ppu=ppu, pivot=(0.5, 0.02), order=-20, id='award_' + idp)
        play.add('Art/Zenith/' + plq, px, GROUND + 1.05, pivot=(0.5, 0.5), sx=0.42, sy=0.42, order=-25)
    fg = L.layer('fg', 1.3, 500, parallax_y=1.1)
    fg.add('Art/Zenith/boom_fg', 13.0, 2.4, pivot=(0.5, 0.0), alpha=0.95)
    fg.add('Art/Showroom/column_fg', 30.5, -7.0, pivot=(0.5, 0.0), sx=0.8)
    L.marker('spawn', 0.5)
    L.marker('awards', stage_x, prompt='PRESIONA E PARA RECIBIR EL PREMIO', radius=2.4)
    L.marker('award_lux', px1)
    L.marker('award_effie', px2)
    L.marker('reveal', stage_x - 9.0)
    L.marker('desk', 8.0, prompt='PRESIONA E PARA OBSERVAR', radius=1.6)
    L.marker('storyboard', 20.5, prompt='PRESIONA E PARA OBSERVAR', radius=1.6)
    L.marker('poster_tester', 11.4, prompt='PRESIONA E PARA OBSERVAR', radius=1.0)
    L.marker('camera', 22.5, prompt='PRESIONA E PARA OBSERVAR', radius=1.2)
    L.d['bounds'] = [-2.0, stage_x + 9.6]
    return L.export()


if __name__ == '__main__':
    zenith()
