"""Rebuilds every game texture, rig, animation clip and level layout, in dependency order.

    cd Tools/ArtPipeline && python3 build_all.py

Requirements: Python 3.10+, numpy, scipy, pillow, skia-python (pip install numpy scipy pillow skia-python).
Inputs: the reference sheets, logos and concept painting in Assets/References. Outputs: Assets/TheTesterGame/{Art,UI,Data,Animations}.
"""
import importlib
import time

STEPS = [
    ('build_character', 'build'),     # side cut-out rig + atlas (from the turnaround sheet)
    ('clips', 'build'),               # animation clips (needs the rig)
    ('extract_front', 'build'),       # front figure holding both awards + expressions
    ('extract_props', 'build'),       # awards, studio props, Zenith logo
    ('build_cars', 'build'),          # IONIQ 5 side views, wheel, 3/4 hero + hotspots
    ('paint_showroom', 'build'),      # showroom modules, exterior arrival, title painting
    ('paint_interior', 'build'),      # cabin for the detail test + clue crops
    ('paint_drive', 'build'),         # city layers and street props
    ('paint_zenith', 'build'),        # award plaques (+ studio kit kept as source art)
    ('paint_zenith_lobby', 'build'),  # final level from the client's office painting + finale backdrop
    ('paint_ui', 'build'),            # UI art + exterior inspection backdrop
    ('finalize_textures', 'main'),    # multiple-of-4 padding for GPU compression
    ('levels', None),                 # level layouts (JSON)
]

if __name__ == '__main__':
    t0 = time.time()
    for mod, fn in STEPS:
        t = time.time()
        m = importlib.import_module(mod)
        if fn:
            getattr(m, fn)()
        else:
            m.showroom(); m.drive(); m.zenith()
        print('%-18s %5.1fs' % (mod, time.time() - t))
    print('done in %.0fs' % (time.time() - t0))
