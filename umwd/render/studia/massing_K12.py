"""Quick clay massing comparison of panel concepts K1 and K2 (approximate, from their dossiers)."""
import sys, json, math
sys.path.insert(0, '/home/user/aihouse/umwd/src')
from umwd.render import blib
from shapely.geometry import Polygon, LineString, Point
from shapely import affinity
import bpy
S = json.load(open('/home/user/aihouse/umwd/model/site.json'))
inv = Polygon(S['granice']['obszar_inwestycji']['pts']).buffer(0)
A = Polygon(S['granice']['wydzielenie_A_mpzp']['pts']).buffer(0).intersection(inv)
maz = [(48.84, 9.68), (61.79, 68.5)]
def band(line, d):
    (x0, y0), (x1, y1) = line; L = math.hypot(x1-x0, y1-y0); ux, uy = (x1-x0)/L, (y1-y0)/L; nx, ny = uy, -ux
    return Polygon([(x0, y0), (x1, y1), (x1+nx*d, y1+ny*d), (x0+nx*d, y0+ny*d)])
def rounded(poly, corner, R):
    # round the polygon at the vertex nearest to `corner`
    return poly.buffer(-R, join_style=1).buffer(R, join_style=1).union(poly.difference(Point(corner).buffer(R*1.6)))
variant = sys.argv[1]
sc = blib.reset()
blib.render_settings(sc, 1300, 900, samples=28, exposure=-0.1)
blib.sky_and_sun(sc, 215, 30, sun_strength=4.0, sky_strength=0.13)
ctx = blib.mat_basic('ctx', (0.66, 0.65, 0.63), rough=0.85)
clay = blib.mat_basic('clay', (0.93, 0.91, 0.88), rough=0.75)
acc = blib.mat_basic('acc', (0.72, 0.40, 0.30), rough=0.6)
blib.extrude_polygon('ground', [(-400, -400), (600, -400), (600, 600), (-400, 600)], -0.3, 0, blib.mat_basic('g', (0.86, 0.86, 0.84), rough=0.95))
for b in S['budynki']['items']:
    pg = Polygon(b['pts']).buffer(0)
    if pg.area > 5:
        blib.extrude_polygon('b', list(pg.exterior.coords)[:-1], 0, b.get('wysokosc_szac_m', 6), ctx)
def ext(pg, z0, z1, m):
    for g in ([pg] if pg.geom_type == 'Polygon' else list(pg.geoms)):
        if g.area > 1:
            blib.extrude_polygon('m', list(g.exterior.coords)[:-1], z0, z1, m)
if variant == 'K1':
    wing = band(maz, 13.5).intersection(inv).difference(A.buffer(0.01))
    ext(wing, 0, 21.0, clay)
    ext(wing.buffer(-1.5, join_style=2), 21.0, 23.6, clay)
    tower = A.buffer(-0.3, join_style=2)
    tower = rounded(tower, (106.3, 79.3), 13.0)
    ext(tower, 0, 26.4, clay); ext(tower, 26.4, 38.2, acc)
else:
    wing = band(maz, 13.5).intersection(inv).difference(A.buffer(0.01))
    ext(wing, 0, 20.3, clay)
    tower = A.buffer(-0.2, join_style=2)
    ext(tower, 0, 36.6, clay)
    camp = Polygon([(67.6, 69.7), (76.8, 71.9), (79.0, 62.7), (69.8, 60.5)])
    ext(camp, 0, 43.7, acc)
    gate = Polygon([(100, 37.5), (116.6, 38.4), (115.0, 47.0), (101, 44)]).intersection(inv).difference(A)
    ext(gate, 0, 20.3, clay)
blib.camera(sc, (-45, 175, 95), (82, 38, 12), lens_mm=45, level=False)
sc.render.filepath = f'/home/user/aihouse/umwd/render/studia/massing_{variant}.png'
bpy.ops.render.render(write_still=True)
print('ok', variant)
