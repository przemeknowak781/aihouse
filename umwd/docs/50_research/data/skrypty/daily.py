import csv, sys, glob, os, collections, statistics as st
d = sys.argv[1]
rows = {}
for f in sorted(glob.glob(os.path.join(d, 's_d_424_*.csv'))):
    with open(f, encoding='cp1250') as fh:
        for r in csv.reader(fh):
            y, m, dd = int(r[2]), int(r[3]), int(r[4])
            def v(i):
                if r[i+1].strip() == '8' or r[i].strip() == '': return None
                try: return float(r[i])
                except: return None
            rows[(y, m, dd)] = (v(5), v(7), v(9), v(13))  # tmax, tmin, tmean, precip
years = sorted(set(k[0] for k in rows))
per = {}
for y in years:
    ds = [rows[k] for k in rows if k[0] == y]
    hot = sum(1 for t in ds if t[0] is not None and t[0] >= 30)
    vhot = sum(1 for t in ds if t[0] is not None and t[0] >= 35)
    summer = sum(1 for t in ds if t[0] is not None and t[0] >= 25)
    trop = sum(1 for t in ds if t[1] is not None and t[1] >= 20)
    frost = sum(1 for t in ds if t[1] is not None and t[1] < 0)
    ice = sum(1 for t in ds if t[0] is not None and t[0] < 0)
    p10 = sum(1 for t in ds if t[3] is not None and t[3] >= 10)
    p20 = sum(1 for t in ds if t[3] is not None and t[3] >= 20)
    hdd = sum(max(0, 18 - t[2]) for t in ds if t[2] is not None and t[2] < 15)  # HDD base 18/15
    cdd = sum(max(0, t[2] - 18) for t in ds if t[2] is not None)
    per[y] = dict(n=len(ds), hot=hot, vhot=vhot, summer=summer, trop=trop, frost=frost, ice=ice, p10=p10, p20=p20, hdd=hdd, cdd=cdd)
def avg(key, y0, y1):
    return st.mean(per[y][key] for y in range(y0, y1+1) if y in per)
for key in ['summer', 'hot', 'vhot', 'trop', 'frost', 'ice', 'p10', 'p20', 'hdd', 'cdd']:
    print(f"{key:7s} 1991-2020 {avg(key,1991,2020):7.1f} | 1991-2005 {avg(key,1991,2005):7.1f} | 2006-2020 {avg(key,2006,2020):7.1f} | 2016-2025 {avg(key,2016,2025):7.1f}")
print('years', years[0], years[-1], 'days last year', per[years[-1]]['n'])
print('hot days by year (last 12):', [(y, per[y]['hot']) for y in years[-12:]])
# design temps: 1% / 99% percentiles of daily tmin/tmax 1991-2020
tmins = sorted(t[1] for k, t in rows.items() if 1991 <= k[0] <= 2020 and t[1] is not None)
tmaxs = sorted(t[0] for k, t in rows.items() if 1991 <= k[0] <= 2020 and t[0] is not None)
print('Tmin 1% percentile', tmins[int(0.01*len(tmins))], 'Tmax 99%', tmaxs[int(0.99*len(tmaxs))], 'abs', tmins[0], tmaxs[-1])
mx = max((t[0], k) for k, t in rows.items() if t[0] is not None); mn = min((t[1], k) for k, t in rows.items() if t[1] is not None)
print('abs max 1991-2025', mx, 'abs min', mn)
