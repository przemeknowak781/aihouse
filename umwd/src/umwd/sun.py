"""Solar position (NOAA algorithm, accuracy ~0.01° for 1950–2050) for Wrocław site.

sun_position(dt_local_aware, lat, lon) -> (azimuth_deg_from_north_clockwise, elevation_deg)
"""
from __future__ import annotations
import math, datetime
from zoneinfo import ZoneInfo

WRO_LAT, WRO_LON = 51.1115, 17.0480   # approx. site (Mazowiecka / Wybrzeże Słowackiego)
TZ = ZoneInfo("Europe/Warsaw")


def sun_position(dt: datetime.datetime, lat: float = WRO_LAT, lon: float = WRO_LON):
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=TZ)
    ut = dt.astimezone(datetime.timezone.utc)
    jd = ut.timestamp() / 86400.0 + 2440587.5
    jc = (jd - 2451545.0) / 36525.0
    gml = (280.46646 + jc * (36000.76983 + jc * 0.0003032)) % 360
    gma = 357.52911 + jc * (35999.05029 - 0.0001537 * jc)
    ecc = 0.016708634 - jc * (0.000042037 + 0.0000001267 * jc)
    ceq = (math.sin(math.radians(gma)) * (1.914602 - jc * (0.004817 + 0.000014 * jc))
           + math.sin(math.radians(2 * gma)) * (0.019993 - 0.000101 * jc) + math.sin(math.radians(3 * gma)) * 0.000289)
    stl = gml + ceq
    sal = stl - 0.00569 - 0.00478 * math.sin(math.radians(125.04 - 1934.136 * jc))
    moe = 23 + (26 + ((21.448 - jc * (46.815 + jc * (0.00059 - jc * 0.001813)))) / 60) / 60
    oc = moe + 0.00256 * math.cos(math.radians(125.04 - 1934.136 * jc))
    dec = math.degrees(math.asin(math.sin(math.radians(oc)) * math.sin(math.radians(sal))))
    vy = math.tan(math.radians(oc / 2)) ** 2
    eot = 4 * math.degrees(vy * math.sin(2 * math.radians(gml)) - 2 * ecc * math.sin(math.radians(gma))
                           + 4 * ecc * vy * math.sin(math.radians(gma)) * math.cos(2 * math.radians(gml))
                           - 0.5 * vy * vy * math.sin(4 * math.radians(gml)) - 1.25 * ecc * ecc * math.sin(2 * math.radians(gma)))
    minutes = ut.hour * 60 + ut.minute + ut.second / 60
    tst = (minutes + eot + 4 * lon) % 1440
    ha = tst / 4 - 180 if tst / 4 >= 0 else tst / 4 + 180
    zen = math.degrees(math.acos(math.sin(math.radians(lat)) * math.sin(math.radians(dec))
                                 + math.cos(math.radians(lat)) * math.cos(math.radians(dec)) * math.cos(math.radians(ha))))
    el = 90 - zen
    # atmospheric refraction (approx.)
    if el > 85:
        r = 0
    elif el > 5:
        t = math.tan(math.radians(el)); r = 58.1 / t - 0.07 / t ** 3 + 0.000086 / t ** 5
    elif el > -0.575:
        r = 1735 + el * (-518.2 + el * (103.4 + el * (-12.79 + el * 0.711)))
    else:
        r = -20.772 / math.tan(math.radians(el))
    el += r / 3600
    if ha > 0:
        az = (math.degrees(math.acos(((math.sin(math.radians(lat)) * math.cos(math.radians(zen))) - math.sin(math.radians(dec)))
                                     / (math.cos(math.radians(lat)) * math.sin(math.radians(zen))))) + 180) % 360
    else:
        az = (540 - math.degrees(math.acos(((math.sin(math.radians(lat)) * math.cos(math.radians(zen))) - math.sin(math.radians(dec)))
                                           / (math.cos(math.radians(lat)) * math.sin(math.radians(zen)))))) % 360
    return az, el


def sun_vector(az_deg, el_deg):
    """Unit vector pointing TO the sun in (e, n, z)."""
    a, e = math.radians(az_deg), math.radians(el_deg)
    return (math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e))


if __name__ == "__main__":
    for d in ["2027-03-21 07:00", "2027-03-21 12:00", "2027-03-21 17:00", "2027-06-21 13:00", "2027-12-21 12:00"]:
        dt = datetime.datetime.strptime(d, "%Y-%m-%d %H:%M").replace(tzinfo=TZ)
        print(d, ["%.2f" % x for x in sun_position(dt)])
