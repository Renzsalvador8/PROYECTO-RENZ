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
    mid.add('Art/Showroom/plant_mid', 35.6, WALL_BASE - 0.3, flip=True)
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
    """Zenith Studio: the client's office painting as a single, fixed-camera room (see paint_zenith_lobby).
    Jean Paul enters from behind the crates on the right and walks left to the awards."""
    import paint_zenith_lobby as Z
    W, H = img_size('Art/Zenith/lobby')
    left, bottom = -W / Z.PPU / 2, Z.world_y(Z.CROP_Y1, GROUND)
    L = Level('zenith', bounds=(left + 0.02, -left - 0.02), ground_y=GROUND, background=(10, 20, 26),
              cam_y=round(bottom + 3.5 + 0.11, 3), cam_size=3.5)
    room = L.layer('room', 1.0, -800)
    room.add('Art/Zenith/lobby', 0.0, bottom, ppu=Z.PPU, pivot=(0.5, 0.0))
    sx, sy = Z.world_x(Z.SIGN_C[0]), Z.world_y(Z.SIGN_C[1], GROUND)
    halo_ppu = 512 / (2 * (Z.SIGN_R / Z.ORIG_PPU) / Z.HALO_INNER)
    room.add('Art/Zenith/sign_halo', sx, sy, ppu=round(halo_ppu, 2), pivot=(0.5, 0.5), order=5, alpha=0.8, id='sign_halo')
    play = L.layer('play', 1.0, -100)
    # awards: two concrete pedestals in the walking plane, framing the wall sconces
    px1, px2 = round(Z.world_x(300), 3), round(Z.world_x(556), 3)
    base = GROUND + 0.35
    ped_sx, ped_sy = 0.32, 0.36
    top = base + 4.2 * ped_sy * (1 - 38 / 420)
    for px, aw, plq, ppu, idp in ((px1, 'award_lux_grand_prix', 'plaque_lux', 340, 'lux'), (px2, 'award_effie_bronze', 'plaque_effie', 420, 'effie')):
        play.add('Art/Showroom/spot_cone', px, GROUND - 0.6, pivot=(0.5, 0.0), sx=0.62, sy=0.8, order=-5, alpha=0.4, tint=(1.0, 0.94, 0.84))
        play.add('Art/Zenith/pedestal_concrete', px, base, pivot=(0.5, 0.0), sx=ped_sx, sy=ped_sy, order=-30, id='pedestal_' + idp)
        play.add('Art/Props/' + aw, px, round(top - 0.02, 4), ppu=ppu, pivot=(0.5, 0.02), order=-20, id='award_' + idp)
        play.add('Art/Zenith/' + plq, px, base + 0.5, pivot=(0.5, 0.5), sx=0.3, sy=0.3, order=-25, tint=(0.86, 0.84, 0.82))
    # crates and filing cabinet in front of the walking line (cut from the same painting, stays registered)
    fw, fh = img_size('Art/Zenith/lobby_fg')
    fx0 = left + Z.foreground_offset()[0] / Z.PPU
    fg = L.layer('fg', 1.0, 400)
    fg.add('Art/Zenith/lobby_fg', fx0, bottom, ppu=Z.PPU, pivot=(0.0, 0.0))
    # invisible walls: left of the first pedestal, right behind the cabinet
    L.collider(px1 - 1.0, GROUND + 1.2, 0.4, 3.0, id='left')
    L.collider(6.4, GROUND + 1.2, 0.4, 3.0, id='right')
    L.marker('spawn', 5.9)
    L.marker('entry', 2.9)
    L.marker('reveal', round(sx, 3), round(sy, 3))           # the glowing sign: where the camera reveal starts
    L.marker('awards', round((px1 + px2) / 2, 3), prompt='PRESIONA E PARA RECIBIR EL PREMIO', radius=1.6)
    L.marker('award_lux', px1)
    L.marker('award_effie', px2)
    L.marker('storyboard', round(Z.world_x(650), 3), prompt='PRESIONA E PARA OBSERVAR', radius=0.5)   # clear of the Effie pedestal
    L.marker('sign', round(sx, 3), prompt='PRESIONA E PARA OBSERVAR', radius=0.9)
    L.marker('desk', round(Z.world_x(930), 3), prompt='PRESIONA E PARA OBSERVAR', radius=0.9)
    L.marker('reels', round(Z.world_x(1180), 3), prompt='PRESIONA E PARA OBSERVAR', radius=0.9)
    return L.export()


if __name__ == '__main__':
    zenith()
