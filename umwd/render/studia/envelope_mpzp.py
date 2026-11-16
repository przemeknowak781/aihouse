"""Clay study: MPZP building envelope (18–25 m band outside zone A, 35–45 m in zone A) over existing context."""
import sys, json, math
sys.path.insert(0, '/home/user/aihouse/umwd/src')
from umwd.render import blib
from shapely.geometry import Polygon
import bpy
S = json.load(open('/home/user/aihouse/umwd/model/site.json'))
Z0 = 119.25
sc = blib.reset()
blib.render_settings(sc, 1600, 1000, samples=32, exposure=-0.2)
blib.sky_and_sun(sc, 205, 32, sun_strength=4.2, sky_strength=0.14)
clay = blib.mat_basic('clay', (0.82, 0.80, 0.77), rough=0.8)
ctx = blib.mat_basic('ctx', (0.62, 0.61, 0.60), rough=0.85)
env25 = blib.mat_basic('env25', (0.90, 0.62, 0.45), rough=0.6, alpha=1.0)
envA = blib.mat_basic('envA', (0.70, 0.22, 0.16), rough=0.6)
ground = blib.extrude_polygon('ground', [(-400, -400), (600, -400), (600, 600), (-400, 600)], -0.3, 0.0, blib.mat_basic('g', (0.9, 0.9, 0.88), rough=0.9))
for b in S['budynki']['items']:
    pts = [tuple(p) for p in b['pts']]
    pg = Polygon(pts).buffer(0)
    if pg.area < 5: continue
    blib.extrude_polygon('b', list(pg.exterior.coords)[:-1], 0, b.get('wysokosc_szac_m', 6), ctx)
inv = Polygon(S['granice']['obszar_inwestycji']['pts']).buffer(0)
A = Polygon(S['granice']['wydzielenie_A_mpzp']['pts']).buffer(0)
outside = inv.difference(A)
geoms = [outside] if outside.geom_type == 'Polygon' else list(outside.geoms)
for g in geoms:
    if g.area > 1:
        o = blib.extrude_polygon('env25', list(g.exterior.coords)[:-1], 0, 25.0, env25)
inA = A.intersection(inv)
blib.extrude_polygon('envA', list(inA.exterior.coords)[:-1], 0, 45.0, envA)
# 18 m minimum line (thin slab) and 35 m line
for g in geoms:
    if g.area > 1:
        blib.extrude_polygon('min18', list(g.buffer(0.15).exterior.coords)[:-1], 17.95, 18.05, blib.mat_basic('l', (1, 1, 1), emission=(1, 1, 1), emission_strength=2))
blib.extrude_polygon('min35', list(inA.buffer(0.15).exterior.coords)[:-1], 34.95, 35.05, blib.mat_basic('l2', (1, 1, 1), emission=(1, 1, 1), emission_strength=2))
# trees as simple spheres
for t in S['zielen']['drzewa']:
    bpy.ops.mesh.primitive_uv_sphere_add(radius=3.6 if t['typ'] == 'lisciaste' else 2.4, location=(t['e'], t['n'], 6.0), scale=(1,1,1.15), segments=16, ring_count=8)
    o = bpy.context.object; o.data.materials.append(blib.mat_basic('tree', (0.55, 0.62, 0.45), rough=0.9))
    bpy.ops.mesh.primitive_cylinder_add(radius=0.2, depth=5, location=(t['e'], t['n'], 2.5))
blib.camera(sc, (300, 250, 175), (85, 35, 10), lens_mm=55, level=False)
sc.render.filepath = '/home/user/aihouse/umwd/render/studia/envelope_mpzp.png'
bpy.ops.render.render(write_still=True)
print('ok')
