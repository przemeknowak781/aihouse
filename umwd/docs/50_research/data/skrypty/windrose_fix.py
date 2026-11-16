"""Corrected wind rose for Wroclaw-Strachowice (IMGW 351160424), 1991-2020, synoptic hours every 3 h.
Added by the source verifier. Fixes two issues of the naive binning in export_climate.py / windrose.py:
 1) In 1991-2010 IMGW directions are reported in 10-degree steps (from 2011 mostly 1 degree). Binning
    10-degree values into 22.5/45-degree sectors gives cardinal sectors (N, E, S, W) 3 (or 5) reporting
    values and the others 2 (or 4), which inflates N/E/S/W. Here each 10-degree value is spread evenly over
    its +-5 degree reporting interval before binning (years with < 50 % of 1-degree values).
 2) dd = 999 (variable direction, 0.2 % of observations) was folded into sector W (999 mod 360 = 279).
    It is now counted separately.
Usage: python3 -I windrose_fix.py <dir with s_t_424_*.csv> <out_csv> <out_png>"""
import csv, sys, glob, os, collections, math
d, out_csv, out_png = sys.argv[1], sys.argv[2], sys.argv[3]
by_year = collections.defaultdict(lambda: [0, 0]); n = 0; calm = 0; var = 0; recs = []
for f in sorted(glob.glob(os.path.join(d, 's_t_424_*.csv'))):
    with open(f, encoding='cp1250') as fh:
        for r in csv.reader(fh):
            y, gg = int(r[2]), int(r[5])
            if not (1991 <= y <= 2020) or gg % 3: continue
            if r[24].strip() == '8' or r[26].strip() == '8': continue
            try: dd = float(r[23]); ff = float(r[25])
            except ValueError: continue
            n += 1
            if ff == 0 or dd == 0: calm += 1; continue
            if dd == 999: var += 1; continue
            by_year[y][0] += 1; by_year[y][1] += (dd % 10 != 0); recs.append((y, dd, ff))
def rose(nsec):
    w = 360 / nsec; cnt = collections.Counter(); spd = collections.Counter(); strong = collections.Counter(); ns = 0
    for y, dd, ff in recs:
        tenres = by_year[y][1] / by_year[y][0] < 0.5
        pts = [((dd - 5 + k + 0.5) % 360, 0.1) for k in range(10)] if tenres else [(dd % 360, 1.0)]
        for a, wt in pts:
            s = int(((a + w / 2) % 360) // w) % nsec; cnt[s] += wt; spd[s] += wt * ff
            if ff >= 8: strong[s] += wt
        ns += ff >= 8
    return cnt, spd, strong, ns
s16 = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
s8 = ['N','NE','E','SE','S','SW','W','NW']
c16, v16, st16, ns = rose(16); c8, v8, st8, _ = rose(8)
with open(out_csv, 'w', newline='', encoding='utf-8') as fo:
    wr = csv.writer(fo); wr.writerow(['sektory', 'sektor', 'czestosc_%', 'predkosc_srednia_m_s', 'udzial_w_wiatrach_ge_8_m_s_%'])
    for i, k in enumerate(s16): wr.writerow([16, k, f"{100*c16[i]/n:.1f}", f"{v16[i]/c16[i]:.2f}", f"{100*st16[i]/ns:.1f}"])
    for i, k in enumerate(s8): wr.writerow([8, k, f"{100*c8[i]/n:.1f}", f"{v8[i]/c8[i]:.2f}", f"{100*st8[i]/ns:.1f}"])
    wr.writerow(['-', 'cisza', f"{100*calm/n:.1f}", '0', '']); wr.writerow(['-', 'kierunek zmienny (999)', f"{100*var/n:.1f}", '', ''])
    wr.writerow(['-', 'n_obserwacji', n, '', '']); wr.writerow(['-', 'n_wiatr_ge_8_m_s', ns, '', ''])
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig = plt.figure(figsize=(5, 5), dpi=200); ax = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
th = [math.radians(i * 22.5) for i in range(16)]
ax.bar(th, [100 * c16[i] / n for i in range(16)], width=math.radians(20), color='#8a7f72', edgecolor='white', linewidth=0.6)
ax.set_xticks(th); ax.set_xticklabels(s16, fontsize=7); ax.tick_params(axis='y', labelsize=6)
ax.set_title('Wrocław-Strachowice (IMGW) 1991–2020, korekta binowania\nczęstość kierunków wiatru [proc.], cisza {:.1f} proc.'.format(100 * calm / n), fontsize=8)
fig.tight_layout(); fig.savefig(out_png); plt.close(fig)
print('ok', n, calm, var, ns)
