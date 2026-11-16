import sys, datetime, math
sys.path.insert(0, '/home/user/aihouse/umwd/src')
from umwd.sun import sun_position, TZ
LAT, LON = 51.1083, 17.0516
def find_events(day):
    t0 = datetime.datetime(day.year, day.month, day.day, 0, 0, tzinfo=TZ)
    prev = None; rise = sset = None; best = (-99, None, None)
    for i in range(0, 24*60):
        t = t0 + datetime.timedelta(minutes=i)
        az, el = sun_position(t, LAT, LON)
        if prev is not None:
            if prev < -0.833 <= el: rise = (t, az)
            if prev >= -0.833 > el: sset = (t, az)
        if el > best[0]: best = (el, t, az)
        prev = el
    return rise, sset, best
for d in [datetime.date(2027,3,20), datetime.date(2027,6,21), datetime.date(2027,9,23), datetime.date(2027,12,21), datetime.date(2027,10,29), datetime.date(2027,5,15)]:
    rise, sset, best = find_events(d)
    dl = (sset[0]-rise[0]).total_seconds()/3600
    el = best[0]
    print(f"{d} rise {rise[0]:%H:%M} az {rise[1]:.0f} | noon {best[1]:%H:%M} alt {el:.1f} az {best[2]:.0f} | set {sset[0]:%H:%M} az {sset[1]:.0f} | day {dl:.2f} h | shadow/height at noon {1/math.tan(math.radians(el)):.2f}")
    row = []
    for h in [8, 10, 12, 14, 16, 18]:
        t = datetime.datetime(d.year, d.month, d.day, h, 0, tzinfo=TZ)
        az, e = sun_position(t, LAT, LON)
        row.append(f"{h}:00 az{az:.0f}/alt{e:.0f}")
    print('    ', '; '.join(row))
