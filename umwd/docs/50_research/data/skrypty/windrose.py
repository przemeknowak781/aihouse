# UWAGA (weryfikator, 16.11.2026): binowanie kierunkow co 10 st. (1991-2010) zawyza sektory N/E/S/W, a kod 999 trafia do W; wersja skorygowana: windrose_fix.py
import csv, sys, glob, os, collections
d = sys.argv[1]
sect8 = ['N','NE','E','SE','S','SW','W','NW']
def s8(deg):
    return sect8[int(((deg % 360) + 22.5) // 45) % 8]
tot = collections.Counter(); spd = collections.defaultdict(float); calm = 0; n = 0
season = {'DJF': collections.Counter(), 'JJA': collections.Counter()}; scalm = collections.Counter(); sn = collections.Counter()
strong = collections.Counter(); nstrong = 0
hours = set(range(0, 24, 3))
for f in sorted(glob.glob(os.path.join(d, 's_t_424_*.csv'))):
    with open(f, encoding='cp1250') as fh:
        for r in csv.reader(fh):
            y, m, gg = int(r[2]), int(r[3]), int(r[5])
            if not (1991 <= y <= 2020) or gg not in hours: continue
            if r[24].strip() == '8' or r[26].strip() == '8': continue
            try: dd = float(r[23]); ff = float(r[25])
            except: continue
            ss = 'DJF' if m in (12, 1, 2) else ('JJA' if m in (6, 7, 8) else None)
            n += 1
            if ss: sn[ss] += 1
            if ff == 0 or dd == 0:
                calm += 1
                if ss: scalm[ss] += 1
                continue
            k = s8(dd); tot[k] += 1; spd[k] += ff
            if ss: season[ss][k] += 1
            if ff >= 8: strong[k] += 1; nstrong += 1
print('obs', n, 'calm %.1f%%' % (100*calm/n))
print('sector  freq%  meanspeed  DJF%  JJA%  share_of_ff>=8m/s%')
for k in sect8:
    print(f"{k:3s} {100*tot[k]/n:6.1f} {spd[k]/tot[k]:6.2f} {100*season['DJF'][k]/sn['DJF']:6.1f} {100*season['JJA'][k]/sn['JJA']:6.1f} {100*strong[k]/max(nstrong,1):6.1f}")
print('calm DJF %.1f JJA %.1f' % (100*scalm['DJF']/sn['DJF'], 100*scalm['JJA']/sn['JJA']), 'n strong', nstrong)
