import sys, datetime, math
sys.path.insert(0, '/home/user/aihouse/umwd/src')
from umwd.sun import sun_position, TZ
LAT, LON = 51.1083, 17.0516
# poprawione przez weryfikatora: front Mazowieckiej 282° (było 256°); geometria.md § 4.2, krawędź 9
normals = {'N (most, Odra) 346°': 346.0, 'E (Oława) 76°': 76.0, 'W (Mazowiecka) 282°': 282.0, 'S (podwórze) 166°': 166.0}
dates = [datetime.date(2027,3,20), datetime.date(2027,6,21), datetime.date(2027,10,29), datetime.date(2027,12,21)]
for d in dates:
    print('==', d)
    for name, nrm in normals.items():
        mins = 0; first = last = None
        for i in range(0, 24*60, 5):
            t = datetime.datetime(d.year, d.month, d.day, 0, 0, tzinfo=TZ) + datetime.timedelta(minutes=i)
            az, el = sun_position(t, LAT, LON)
            if el <= 2: continue
            diff = (az - nrm + 540) % 360 - 180
            if abs(diff) < 85:
                mins += 5; first = first or t; last = t
        if mins:
            print(f"  {name:22s} {mins/60:4.1f} h  ({first:%H:%M}–{last:%H:%M})")
        else:
            print(f"  {name:22s}  0.0 h")
