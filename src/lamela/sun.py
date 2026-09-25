"""Położenie Słońca (azymut, wysokość) — algorytm NOAA (Meeus, „Astronomical Algorithms”), dokładność ~0,01°.

Domyślna lokalizacja: Poznań (52,4064° N, 16,9252° E), strefa czasowa Europe/Warsaw (CET/CEST).

    >>> from lamela.sun import sun_position
    >>> az, el = sun_position("2026-06-21 15:00")      # czas lokalny Europe/Warsaw
    >>> round(az), round(el)
    (232, 52)

Azymut: od północy geograficznej, zgodnie z ruchem wskazówek zegara (90° = E, 180° = S, 270° = W).
"""
from __future__ import annotations

import math
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

POZNAN = (52.4064, 16.9252)
TZ = "Europe/Warsaw"


def _julian_day(dt_utc: datetime) -> float:
    y, m = dt_utc.year, dt_utc.month
    d = dt_utc.day + (dt_utc.hour + (dt_utc.minute + dt_utc.second / 60.0) / 60.0) / 24.0
    if m <= 2:
        y -= 1
        m += 12
    a = y // 100
    b = 2 - a + a // 4
    return int(365.25 * (y + 4716)) + int(30.6001 * (m + 1)) + d + b - 1524.5


def sun_position(when, lat: float = POZNAN[0], lon: float = POZNAN[1], tz: str = TZ,
                 refraction: bool = True) -> tuple[float, float]:
    """Zwraca (azymut [°], wysokość [°]) dla czasu lokalnego ``when`` (datetime lub 'RRRR-MM-DD GG:MM')."""
    if isinstance(when, str):
        when = datetime.fromisoformat(when)
    if when.tzinfo is None:
        when = when.replace(tzinfo=ZoneInfo(tz))
    dt = when.astimezone(timezone.utc)
    jd = _julian_day(dt)
    T = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360.0
    M = 357.52911 + T * (35999.05029 - 0.0001537 * T)
    e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)
    Mr = math.radians(M)
    C = (math.sin(Mr) * (1.914602 - T * (0.004817 + 0.000014 * T)) + math.sin(2 * Mr) * (0.019993 - 0.000101 * T)
         + math.sin(3 * Mr) * 0.000289)
    true_long = L0 + C
    omega = 125.04 - 1934.136 * T
    lam = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))
    eps0 = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60.0) / 60.0
    eps = eps0 + 0.00256 * math.cos(math.radians(omega))
    decl = math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(lam)))
    y = math.tan(math.radians(eps / 2)) ** 2
    L0r = math.radians(L0)
    eot = 4 * math.degrees(y * math.sin(2 * L0r) - 2 * e * math.sin(Mr) + 4 * e * y * math.sin(Mr) * math.cos(2 * L0r)
                           - 0.5 * y * y * math.sin(4 * L0r) - 1.25 * e * e * math.sin(2 * Mr))
    minutes = dt.hour * 60 + dt.minute + dt.second / 60.0
    tst = (minutes + eot + 4 * lon) % 1440.0
    ha = tst / 4.0 - 180.0
    if ha < -180:
        ha += 360
    latr, har = math.radians(lat), math.radians(ha)
    cosz = math.sin(latr) * math.sin(decl) + math.cos(latr) * math.cos(decl) * math.cos(har)
    cosz = max(-1.0, min(1.0, cosz))
    zen = math.degrees(math.acos(cosz))
    el = 90.0 - zen
    az = (math.degrees(math.atan2(math.sin(har), math.cos(har) * math.sin(latr) - math.tan(decl) * math.cos(latr)))
          + 180.0) % 360.0
    if refraction and el > -0.575:
        te = math.tan(math.radians(el))
        if el > 85:
            r = 0.0
        elif el > 5:
            r = 58.1 / te - 0.07 / te ** 3 + 0.000086 / te ** 5
        else:
            r = 1735 + el * (-518.2 + el * (103.4 + el * (-12.79 + el * 0.711)))
        el += r / 3600.0
    return az, el


def sun_vector(az: float, el: float, azymut_osi_y: float = 0.0) -> tuple[float, float, float]:
    """Wersor kierunku DO Słońca w układzie budynku (x→E, y→N, z↑), z uwzględnieniem azymutu osi +y."""
    a = math.radians(az - azymut_osi_y)
    e = math.radians(el)
    return (math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), math.sin(e))


if __name__ == "__main__":
    for d in ("2026-03-21", "2026-06-21", "2026-12-21"):
        for h in (9, 12, 15):
            az, el = sun_position(f"{d} {h:02d}:00")
            print(f"{d} {h:02d}:00  azymut {az:6.1f}°  wysokość {el:5.1f}°")
