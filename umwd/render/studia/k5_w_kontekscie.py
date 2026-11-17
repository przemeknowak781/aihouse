"""K5 massing (from the K5 dossier) inserted in the 3D context — integration test of the render pipeline."""
import sys, time, datetime
sys.path.insert(0, '/home/user/aihouse/umwd/src')
import bpy
from umwd.render import blib, context, facade2
from umwd.sun import sun_position, TZ
OFF = 119.30 - context.Z0          # K5 ±0.00 = 119.30 m a.s.l.
sc = blib.reset()
res = context.build_context(sc, {'pora_roku': 'jesien'})
ctx = res['ctx']
blib.render_settings(sc, 1000, 625, samples=28, adaptive=0.02, exposure=-0.25, look='AgX - Base Contrast')
gran = blib.mat_noise_color('granit', (0.62, 0.60, 0.56), var=0.08, rough=0.55, bump=0.03)
cer = blib.mat_noise_color('ceramika', (0.80, 0.72, 0.60), var=0.04, rough=0.4, bump=0.01)
met = blib.mat_basic('metal', (0.10, 0.09, 0.08), rough=0.35, metal=0.9)
gl = blib.mat_glass('szklo', reflect_only=True)
wall = blib.mat_basic('wnetrze', (0.08, 0.08, 0.08), rough=0.9)
tower = [(74.61, 40.76), (113.47, 50.23), (109.75, 65.48)]
import math
cx, cy, R = 96.15, 62.17, 14.0
a1, a2 = math.atan2(65.48 - cy, 109.75 - cx), math.atan2(75.77 - cy, 92.83 - cx)
for k in range(1, 18):
    a = a1 + (a2 - a1) * k / 18
    tower.append((cx + R * math.cos(a), cy + R * math.sin(a)))
tower += [(92.83, 75.77), (67.57, 69.61)]
wing = [(48.84, 9.68), (61.72, 68.18), (67.57, 69.61), (74.61, 40.76), (70.84, 39.84), (63.50, 6.49)]
seg = [(101.14, 37.45), (115.72, 41.00), (113.47, 50.23), (98.89, 46.68)]
lv_t = [(OFF + 0, 4.65)] + [(OFF + 4.65 + 3.7 * i, 3.7) for i in range(5)]
lv_w = [(OFF + 0, 4.65)] + [(OFF + 4.65 + 3.7 * i, 3.7) for i in range(4)]
spec_t = {"levels": lv_t + [(OFF + 23.15, 12.0)], "bay": 2.70, "pier_w": 0.55, "pier_d": 0.60, "sill": 0.8, "head": 0.6,
          "mat_wall": wall, "mat_pier": gran, "mat_band": gran, "mat_glass": gl, "mat_frame": met, "cornice_h": 1.2, "cornice_d": 0.05,
          "mat_cornice": met, "ground_glass_sill": 0.0}
facade2.build_volume('WIEZA', tower, OFF + 0, OFF + 35.15, spec_t)
spec_w = {"levels": lv_w, "bay": 1.35, "pier_w": 0.12, "pier_d": 0.25, "sill": 0.85, "head": 0.9,
          "mat_wall": wall, "mat_pier": cer, "mat_band": cer, "mat_glass": gl, "mat_frame": met, "cornice_h": 1.0, "cornice_d": 0.05,
          "mat_cornice": gran, "ground_glass_sill": 0.0}
facade2.build_volume('SKRZYDLO', wing, OFF + 0, OFF + 19.85, spec_w)
facade2.build_volume('SEGMENT', seg, OFF + 0, OFF + 19.85, spec_w)
out = '/home/user/aihouse/umwd/render/studia/'
for nm in ('lot_ptaka_pnwsch', 'skwer_pd'):
    for o in [o for o in sc.objects if o.type == 'LIGHT']:
        bpy.data.objects.remove(o)
    dt = datetime.datetime.strptime(context.KAMERY[nm]['czas'], '%Y-%m-%d %H:%M').replace(tzinfo=TZ)
    az, el = sun_position(dt)
    blib.sky_and_sun(sc, az + 0.738, el, sun_strength=6.0, sky_strength=0.18)
    context.dodaj_chmury(sc)
    context.ustaw_kamere(ctx, sc, nm)
    sc.render.filepath = out + f'k5_ctx_{nm}.png'
    t = time.time(); bpy.ops.render.render(write_still=True); print(nm, round(time.time() - t, 1))
