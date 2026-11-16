"""Export Wrocław-Strachowice (IMGW 351160424) climate normals 1991-2020, wind rose and sun data to CSV + figures.
Inputs: IMGW public data (danepubliczne.imgw.pl) unpacked to directories given as args. Run with python3 -I."""
import csv, sys, glob, os, collections, statistics as st, math, datetime
mon_dir, term_dir, out_dir = sys.argv[1], sys.argv[2], sys.argv[3]
cols_d = "NSP POST ROK MC TMAX WTMAX TMXS WTMXS TMIN WTMIN TMNS WTMNS STM WSTM TMNG WTMNG SUMM WSUMM OPMX WOPMX DN1 DN2 SUUS WSUUS PKSN WPKSN PSDN WPSDN DESD WDESD SNID WSNID DSND WDSND GRDD WGRDD MGLD WMGLD ZAMD WZAMD SADD WSADD GOLD WGOLD ZAND WZAND ZAWD WZAWD ZMED WZMED W10D WW10D W15D WW15D BURD WBURD ROSD WROSD SZRD WSZRD".split()
cols_t = "NSP POST ROK MC NOS WNOS FWS WFWS TEMP WTEMP CPW WCPW WLGS WWLGS PPPS WPPPS PPPM WPPPM WODZ WWODZ WONO WWONO".split()
def load(pattern):
    rows = {}
    for f in sorted(glob.glob(os.path.join(mon_dir, pattern))):
        with open(f, encoding='cp1250') as fh:
            for r in csv.reader(fh):
                if r[0].strip() == '351160424':
                    rows[(int(r[2]), int(r[3]))] = r
    return rows
rd, rt = load('s_m_d_*.csv'), load('s_m_t_*.csv')
def val(rows, cols, y, m, name):
    r = rows.get((y, m))
    if not r: return None
    i = cols.index(name)
    if (i+1 < len(r) and r[i+1].strip() == '8') or r[i].strip() == '': return None
    try: return float(r[i])
    except ValueError: return None
spec = [('STM','Tśr [°C]',rd,cols_d,'mean'),('TMXS','Tmax śr. [°C]',rd,cols_d,'mean'),('TMNS','Tmin śr. [°C]',rd,cols_d,'mean'),
        ('SUMM','Opad [mm]',rd,cols_d,'sum'),('SUUS','Usłonecznienie [h]',rd,cols_d,'sum'),('WLGS','Wilg. wzgl. [%]',rt,cols_t,'mean'),
        ('FWS','Wiatr śr. [m/s]',rt,cols_t,'mean'),('NOS','Zachmurzenie [okt.]',rt,cols_t,'mean'),('PSDN','Dni z pokrywą śn.',rd,cols_d,'sum'),
        ('MGLD','Dni z mgłą',rd,cols_d,'sum'),('BURD','Dni z burzą',rd,cols_d,'sum')]
with open(os.path.join(out_dir, 'klimat_wroclaw_normy_1991_2020.csv'), 'w', newline='', encoding='utf-8') as fo:
    w = csv.writer(fo); w.writerow(['element'] + [str(m) for m in range(1, 13)] + ['rok', 'braki_miesiecy'])
    for code, label, rows, cols, agg in spec:
        vals = []; miss = 0
        for m in range(1, 13):
            xs = [val(rows, cols, y, m, code) for y in range(1991, 2021)]
            ok = [x for x in xs if x is not None]; miss += len(xs) - len(ok)
            vals.append(st.mean(ok))
        ann = sum(vals) if agg == 'sum' else st.mean(vals)
        w.writerow([label] + [f"{v:.1f}" for v in vals] + [f"{ann:.1f}", miss])
# wind rose (synoptic hours 00,03,...,21; 1991-2020)
sect = ['N','NNE','NE','ENE','E','ESE','SE','SSE','S','SSW','SW','WSW','W','WNW','NW','NNW']
cnt = collections.Counter(); spd = collections.defaultdict(float); n = 0; calm = 0
for f in sorted(glob.glob(os.path.join(term_dir, 's_t_424_*.csv'))):
    with open(f, encoding='cp1250') as fh:
        for r in csv.reader(fh):
            y, gg = int(r[2]), int(r[5])
            if not (1991 <= y <= 2020) or gg % 3: continue
            if r[24].strip() == '8' or r[26].strip() == '8': continue
            try: dd = float(r[23]); ff = float(r[25])
            except ValueError: continue
            n += 1
            if ff == 0 or dd == 0: calm += 1; continue
            k = sect[int(((dd % 360) + 11.25) // 22.5) % 16]; cnt[k] += 1; spd[k] += ff
with open(os.path.join(out_dir, 'roza_wiatrow_wroclaw_1991_2020.csv'), 'w', newline='', encoding='utf-8') as fo:
    w = csv.writer(fo); w.writerow(['sektor', 'czestosc_%', 'predkosc_srednia_m_s'])
    for k in sect: w.writerow([k, f"{100*cnt[k]/n:.1f}", f"{spd[k]/cnt[k]:.2f}"])
    w.writerow(['cisza', f"{100*calm/n:.1f}", '0']); w.writerow(['n_obserwacji', n, ''])
# figures
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
fig = plt.figure(figsize=(5, 5), dpi=200); ax = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N'); ax.set_theta_direction(-1)
th = [math.radians(i*22.5) for i in range(16)]; fr = [100*cnt[k]/n for k in sect]
ax.bar(th, fr, width=math.radians(20), color='#8a7f72', edgecolor='white', linewidth=0.6)
ax.set_xticks(th); ax.set_xticklabels(sect, fontsize=7); ax.tick_params(axis='y', labelsize=6)
ax.set_title('Wrocław-Strachowice (IMGW) 1991–2020\nczęstość kierunków wiatru [proc.], cisza {:.1f} proc.'.format(100*calm/n), fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(out_dir, '..', 'img', 'roza_wiatrow_1991_2020.png')); plt.close(fig)
sys.path.insert(0, '/home/user/aihouse/umwd/src')
from umwd.sun import sun_position, TZ
LAT, LON = 51.1083, 17.0516
fig = plt.figure(figsize=(5.5, 5.5), dpi=200); ax = fig.add_subplot(111, projection='polar')
ax.set_theta_zero_location('N'); ax.set_theta_direction(-1); ax.set_rlim(90, 0)
for d, c, lab in [((2027, 6, 21), '#c0392b', '21 VI'), ((2027, 3, 20), '#7f8c8d', '20 III / 23 IX'), ((2027, 12, 21), '#2c3e50', '21 XII'), ((2025, 10, 29), '#d68910', '29 X (zdjęcia F.17)')]:
    pts = []
    for i in range(0, 24*60, 10):
        t = datetime.datetime(*d, 0, 0, tzinfo=TZ) + datetime.timedelta(minutes=i)
        az, el = sun_position(t, LAT, LON)
        if el > 0: pts.append((math.radians(az), el))
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=c, lw=1.4, label=lab)
for nm, a in [('N (most) 346°', 346), ('E (Oława) 76°', 76), ('W (Mazowiecka) 256°', 256)]:
    ax.plot([math.radians(a)]*2, [90, 0], color='#999', lw=0.6, ls='--'); ax.text(math.radians(a), 8, nm, fontsize=6, color='#555')
ax.set_title('Ścieżki Słońca – teren UMWD (51,108°N 17,052°E)\nwysokość [°] od środka, azymut od N', fontsize=8)
ax.legend(fontsize=6, loc='lower left', bbox_to_anchor=(-0.1, -0.12)); ax.tick_params(labelsize=6)
fig.tight_layout(); fig.savefig(os.path.join(out_dir, '..', 'img', 'sciezki_slonca_teren.png')); plt.close(fig)
print('ok', n, calm)
