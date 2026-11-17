"""Shadow & sunlight-duration analysis (2.5D prisms) for § 60 / § 13 WT checks and equinox shadow diagrams.

Prism = (footprint Polygon, z_bottom, z_top) in the local grid (metres, z relative to a common datum).
Sun direction from umwd.sun (azimuth from geographic north); grid convergence γ = −0.738° → grid azimuth = az + 0.738.
"""
from __future__ import annotations
import math, datetime
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity
from .sun import sun_position, TZ

GAMMA = 0.738


def sun_grid(dt):
    az, el = sun_position(dt)
    return az + GAMMA, el


def shadow_of_prism(fp: Polygon, z0, z1, az, el, z_ground=0.0):
    """Ground shadow (at z_ground) of a vertical prism between z0..z1."""
    if el <= 0.5:
        return Polygon()
    h1 = z1 - z_ground
    if h1 <= 0:
        return Polygon()
    a = math.radians(az + 180.0)
    L1 = h1 / math.tan(math.radians(el))
    dx, dy = L1 * math.sin(a), L1 * math.cos(a)
    top = affinity.translate(fp, dx, dy)
    parts = [top]
    c = list(fp.exterior.coords)
    for i in range(len(c) - 1):
        p, q = c[i], c[i + 1]
        parts.append(Polygon([p, q, (q[0] + dx, q[1] + dy), (p[0] + dx, p[1] + dy)]).buffer(0))
    parts.append(fp)
    sh = unary_union(parts)
    return sh.difference(fp)


def times(day: datetime.date, t0="07:00", t1="17:00", step_min=5):
    h0, m0 = map(int, t0.split(":")); h1, m1 = map(int, t1.split(":"))
    t = datetime.datetime(day.year, day.month, day.day, h0, m0, tzinfo=TZ)
    end = datetime.datetime(day.year, day.month, day.day, h1, m1, tzinfo=TZ)
    while t <= end:
        yield t
        t += datetime.timedelta(minutes=step_min)


def blocked(pt, z, az, el, prisms, max_dist=400.0):
    """Is the ray from (pt, z) toward the sun blocked by any prism?"""
    a = math.radians(az)
    dx, dy = math.sin(a), math.cos(a)
    tan_el = math.tan(math.radians(el))
    ray = LineString([pt, (pt[0] + dx * max_dist, pt[1] + dy * max_dist)])
    for fp, z0, z1 in prisms:
        if not ray.intersects(fp):
            continue
        inter = ray.intersection(fp)
        geoms = getattr(inter, "geoms", [inter])
        for g in geoms:
            for c in g.coords:
                d = math.hypot(c[0] - pt[0], c[1] - pt[1])
                zr = z + d * tan_el
                if z0 - 1e-6 <= zr <= z1:
                    return True
    return False


def sunlight_minutes(pt, z, normal_az, prisms, day, t0="07:00", t1="17:00", step=5, min_alt=0.0, min_incidence=0.0):
    """Minutes of direct sun on a window (point, height z, outward normal azimuth in GRID degrees)."""
    total, runs, cur, best = 0, [], 0, 0
    for t in times(day, t0, t1, step):
        az, el = sun_grid(t)
        ok = el > min_alt
        if ok:
            d = (az - normal_az + 540) % 360 - 180
            ok = abs(d) < 90 - min_incidence
        if ok:
            ok = not blocked(pt, z, az, el, prisms)
        if ok:
            total += step; cur += step; best = max(best, cur)
        else:
            cur = 0
    return total, best


def equinox_dates(year=2027):
    return datetime.date(year, 3, 20), datetime.date(year, 9, 23)
