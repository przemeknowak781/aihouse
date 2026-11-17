#!/usr/bin/env python3
"""Elewacje 1:200 (Etap II, R.VII ust.2 pkt2 lit.c) — z koncepcja.json v1.1 (obrysy, kondygnacje, porządki elewacyjne
rozdz. 8, klucz `elewacje`, dachy brył) oraz sąsiadów (sasiedzi.json, site.json). Rysunek tonalny: granit (lico S 1502-Y,
cokół S 3502-Y) / ceramika (odcienie posesji wg v1.1) / tynk mineralny w tonie posesji (lica dziedzińcowe skrzydła i segmentu) /
metal (RAL 8019) / szkło / BIPV, cienie ościeży (światło z lewej góry), linie MPZP (18–25 m poza A; 35–45 m w strefie A), rzędne.

v1.1: okna skrzydła/segmentu 1,20 × 2,35 nad parapetem 0,60 z kwaterą stałą do 0,90 (nadproże 2,95), wieży 1,65 × 2,45 nad
parapetem 0,55 z kwaterą stałą do 1,10 (nadproże 3,00), ościeża wieży 0,45 m z blachy Al; gzyms bez wysięgu na licach przy
granicy (fryz wklęsły 0,15 m), wysięg 0,30 m tylko od dziedzińca; czerpnia zbiorcza w płycinach P/1 i 1/2 elewacji pd. wieży
(u 2–12), czerpnia nadciśnienia klatek ≥ 5 m od niej, płyciny wieży od dziedzińca ≤ 25 m jako BIPV, zadaszenie BIPV tarasu
ogrodowego (u 0,5–20,5, głęb. 4,0 m, h ≈ 4,0 m); lamele korony łuku 0,35 × 0,60 m w rozstawach Fibonacciego (21 szt.,
S 4005-Y20R, szkło z sitodrukiem na R 13,40); segment: ściana pd. BIPV w rysunku osi 2,025 m, attyka pd. 139,10 z balustradą
szklaną cofniętą 1,5 m, żaluzje agregatu i dry-coolera w licu zach.

Wynik: build/rysunki/elewacja_{E,N,W,S,Sd}_1-{SKALA}.svg + docs/70_rysunki/podglady/elewacje_1-{SKALA}.html (podgląd zbiorczy).
"""
import sys, json, math, re, random
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from umwd.svg import Svg
from umwd.facade_elev import Face, draw_faces, u_of, INK
from umwd.siteplan import load_site, poly_of
from umwd.runs import ccw

K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
SAS = json.loads((ROOT / "model" / "sasiedzi.json").read_text(encoding="utf-8"))
S = load_site()
Z0 = float(K["meta"]["zero"]["wzgl_0_00_m_npm"])          # ±0,00 = 119,30 m n.p.m.
import os
SCALE = int(os.environ.get('UMWD_SCALE', '200'))
DEBUG = '--debug' in sys.argv
k = 1000.0 / SCALE

# ---------------------------------------------------------------- dane z koncepcja.json (v1.1)
B = {b["id"]: b for b in K["bryly"]}
W_PTS, M_PTS, S_PTS = (B[i]["obrys_ccw"] for i in ("W", "M", "S"))
KOND = {kd["kondygnacja"]: kd for kd in K["kondygnacje"]}
LEV = {kid: float(kd["posadzka_wzgl"]) for kid, kd in KOND.items()}      # −2 … S
FLOORS_W = [LEV[i] for i in ("1", "2", "3", "4")]                        # skrzydło/segment kondygnacje 1–4
EL_ = K["elewacje"]
ESK, EWI = EL_["skrzydlo"], EL_["wieza"]
LIN = ESK["linie"]
Z_KORDON = LIN["kordon_npm"] - Z0                 # +4,80 (wierzch kordonu 124,10)
Z_NASW = LIN["naswietle_parteru_npm"] - Z0        # +3,47 (122,77 – pas nad parterem Maz. 19)
Z_GZ0 = LIN["spod_gzymsu_npm"] - Z0               # +20,15 (spód gzymsu 139,45)
Z_GZ1 = LIN["attyka_npm"] - Z0                    # +20,85 (gzyms-attyka 140,15)
WYS_GR = float(ESK["gzyms"]["wysieg_lica_przy_granicy_m"])   # 0,00
WYS_DZ = float(ESK["gzyms"]["wysieg_dziedziniec_m"])         # 0,30
FRYZ = float(ESK["gzyms"]["fryz_wklesly_m"])                 # 0,15
OS_SK, FIL_SK = float(ESK["os_m"]), float(ESK["filar_m"])    # 2,025 / 0,825
WIN_SK = tuple(ESK["okno_m"])                                # 1,20 × 2,35
PAR_SK, KW_SK, NADPR_SK = float(ESK["parapet_m"]), float(ESK["kwatera_stala_do_m"]), float(ESK["nadproze_m"])
OSC_SK = float(ESK["osciez_m"])                              # 0,35 (blacha Al)
SEGM = ESK["segmenty_m"]                                     # M1 12,15 | M2 16,20 | M3 16,20 | M4 12,15
RELIEF = ESK["relief_filarow_m"]                             # cofnięcie wypełnień 0 / 0,08 / 0,15 / 0,08
FAKTURA = ("M2", "M4")                                       # rozdz. 8: „faktura tylko dla M2 i M4” (ryflowanie co 0,135 m)
WIN_WI = tuple(EWI["okno_m"])                                # 1,65 × 2,45
PAR_WI, NADPR_WI = float(EWI["parapet_m"]), float(EWI["nadproze_m"])   # 0,55 / 3,00
OSC_WI = float(EWI["osciez_m"])                              # 0,45 (blacha Al, granit tylko na licu filara)
KW_WI = 1.10                                                 # kwatera stała do +1,10 nad posadzką (WT § 301; przekrój 1:50)
DW = B["W"]["dach"]
Z_ROOF_W = float(DW["najnizszy_pkt_pokrycia"]["wzgl"])       # +36,20
Z_ATT_W = float(DW["attyka"]["wzgl"])                        # +37,20
DS = B["S"]["dach"]
Z_TARAS = float(DS["taras_wykonczenie"]["wzgl"])             # +19,80 = 139,10
Z_ATT_SPD = float(DS["attyka"]["sciana_pd_npm"]) - Z0        # attyka ściany pd. segmentu 139,10
BAL_H, BAL_COF = 1.10, 1.5                                   # balustrada szklana 1,10 m cofnięta 1,5 m od lica pd. (do 140,20)
Z6_0 = float(KOND["5"]["strop_nad"]["wierzch"])              # +23,40 – pasmo „kondygnacji cienia” (cofnięcie 0,40)
Z6_1 = float(KOND["6"]["strop_nad"]["spod_wieza"])           # +26,87
Z_P_HEAD = 4.40                                              # nadproże witryn parteru wieży
Z_BIPV_MAX = 25.0                                            # BIPV wyłącznie ≤ 25 m (MPZP § 6 pkt 13, WT § 216 ust. 8)
# zadaszenie tarasu ogrodowego (rozdz. 4.4): wzdłuż elewacji pd. wieży u 0,5–20,5, głęb. 4,0 m, h ≈ 4,0 m, BIPV szkło-szkło
ZAD_U, ZAD_GLEB, ZAD_H = (0.5, 20.5), 4.0, 4.0
CZERPNIA_U = (2.0, 12.0)                                     # czerpnia zbiorcza: płyciny P/1 i 1/2 elewacji pd. wieży (E-I-3)
NADC_MIN = 5.0                                               # czerpnie nadciśnienia klatek ≥ 5 m od czerpni zbiorczej
LUK = B["W"]["luk"]
R_LUK, R_SZYB = float(LUK["R_zewn"]), float(LUK["R_szyb_korony"])     # 14,00 / 13,40 → głębokość lameli 0,60
LAM_W, LAM_A, LAM_B, LAM_N = 0.35, 1.35, 0.675, 21                    # lamela 0,35 × 0,60; rozstawy 1,35 / 0,675 (Fibonacci), 21 szt.


def uv(u, v):
    """Układ pomocniczy wieży (u, v) → (e, n) wg meta.uklad_pomocniczy_wiezy."""
    return (74.606 + 0.97155 * u - 0.23684 * v, 40.756 + 0.23684 * u + 0.97155 * v)


def fz(z):
    """Rzędna względna w zapisie polskim: +19,80 / ±0,00 / −4,20."""
    if abs(z) < 0.005:
        return "±0,00"
    return ("+" if z > 0 else "−") + f"{abs(z):.2f}".replace(".", ",")


def fnpm(z):
    return f"{z + Z0:.2f}".replace(".", ",")


# ---------------------------------------------------------------- paleta (NCS → sRGB, przybliżenia rysunkowe)
def _hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(round(c)))) for c in rgb)


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    ra, rb = _rgb(a), _rgb(b)
    return _hex(tuple(x + (y - x) * t for x, y in zip(ra, rb)))


def ncs_hex(code):
    """Zgrubne przybliżenie rysunkowe NCS „S ccbb-Y##R” (jasność zawyżona jak w palecie arkuszy)."""
    m = re.match(r"S\s*(\d\d)(\d\d)-(?:Y(\d\d)R|Y|N)", code or "")
    if not m:
        return "#dcd2c4"
    s, c = int(m.group(1)) / 100, int(m.group(2)) / 100
    yr = int(m.group(3) or 0) / 100
    base = 250 * (1 - 0.62 * s)
    hue = (245, 205 - 95 * yr, 80 - 40 * yr)
    f = min(0.6, 1.9 * c)
    return _hex(tuple(base * (1 - f) + h * f for h in hue))


# odcienie dobrane rysunkowo dla kodów NCS ze specyfikacji (rozdz. 8 / JSON elewacje.materialy); nieznany kod → ncs_hex()
HEX_NCS = {"S 1505-Y20R": "#dccfbf", "S 1010-Y30R": "#e2cdb4", "S 2005-Y20R": "#d0c4b5", "S 1510-Y30R": "#d4c0a8",
           "S 1005-Y20R": "#ebe2d5", "S 4005-Y20R": "#99928a", "S 1502-Y": "#e7e2d9", "S 3502-Y": "#bdb8ae"}
MAT = {m["id"]: m for m in EL_["materialy"]}
NCS_C = MAT["C"]["NCS"]


def col(code):
    return HEX_NCS.get(code) or ncs_hex(code)


G = col(MAT["G"]["NCS"])                                     # granit strzegomski płomieniowany S 1502-Y
GC = col(MAT["G"].get("NCS_cokol", "S 3502-Y").split(" (")[0])   # cokół parteru S 3502-Y (ta sama rodzina, ciemniejszy)
C = {"M1": col(NCS_C["M1"]), "M2": col(NCS_C["M2"]), "M3": col(NCS_C["M3"]), "M4": col(NCS_C["M4"]),
     "SEG": col(NCS_C["segment"]), "LUK": col(NCS_C["luk"]), "LAM": col(NCS_C["lamele_korony"])}
ME = "#4a4541"       # aluminium, grafitowy brąz RAL 8019
GL = "#7b8792"       # szkło neutralne R ≤ 12 %
GLD = "#3d434a"      # szkło w cieniu / podcień
GLF = "#85847f"      # szkło korony łuku z sitodrukiem ceramicznym 30 % (ton w ton z lamelami, ΔL* ≈ 8)
REC = "#2e2b29"      # głęboki cień (kond. 6, podcień)
PV_PL = "#433e3b"    # BIPV płycin wieży w kolorze grafitowego brązu
PV_PL_L = "#6a635e"  # siatka ogniw / ramek BIPV
PV_SEG = mix(C["SEG"], "#9aa3ab", 0.16)   # BIPV szkło satynowane w tonie ceramiki (ściana pd. segmentu)
LOUV = "#57514c"     # żaluzje czerpni / wyrzutni
NB_F, NB_S, NB_W = "#f2f0ec", "#8d877f", "#d9dcdf"   # sąsiedzi: tło, kreska, okna


def tynk(c):
    """Tynk mineralny cienkowarstwowy w tonie ceramiki posesji: jaśniejszy, matowy (bez profili)."""
    return mix(mix(c, "#f4f0ea", 0.42), "#e9e6e1", 0.12)


def _vi(pts, e, n):
    return min(range(len(pts)), key=lambda i: math.dist(pts[i], (e, n)))


def run(pts, i_from, i_to):
    """Ciąg wierzchołków obrysu CCW od i_from do i_to włącznie (z zawinięciem)."""
    out, i = [pts[i_from]], i_from
    while i != i_to:
        i = (i + 1) % len(pts)
        out.append(pts[i])
    return out


# wierzchołki charakterystyczne skrzydła (tabela 4.1) – odporne na zmianę liczby punktów łuku dziobu
IM = {nm: _vi(M_PTS, *xy) for nm, xy in {"ulica_maz19": (48.842, 9.683), "maz19_dz": (63.498, 6.487), "dz_pn": (70.839, 39.838),
                                          "wieza_pd": (74.557, 40.744), "wieza_pn": (67.494, 69.592)}.items()}


def window(F, s0, w, z0, h, reveal=OSC_SK, fill=GL, mull=True, transom=None):
    """Okno z cieniem nadproża i ościeża (światło z lewej góry); szerokość cienia ∝ głębokości ościeża."""
    F.rect(s0, s0 + w, z0, z0 + h, fill=fill, stroke=INK, sw=0.06)
    sh = min(reveal * 0.75, h * 0.3)
    F.rect(s0, s0 + w, z0 + h - sh, z0 + h, fill=INK, op=0.32)
    F.rect(s0, s0 + min(reveal * 0.6, w * 0.35), z0, z0 + h - sh, fill=INK, op=0.26)
    if mull and w > 1.4:
        F.vline(s0 + w / 2, z0, z0 + h, stroke=ME, sw=0.07)
    if transom:
        F.hline(s0, s0 + w, z0 + transom, stroke=ME, sw=0.06)


def zaluzja(F, s0, s1, z0, z1, pitch=0.16, akust=False):
    """Żaluzja (czerpnia / wyrzutnia / akustyczna) – lamele poziome z ramą."""
    F.rect(s0, s1, z0, z1, fill=(REC if akust else LOUV), stroke=INK, sw=0.05)
    n = max(1, int((z1 - z0) / pitch))
    for q in range(1, n):
        F.hline(s0, s1, z0 + (z1 - z0) * q / n, stroke=("#7a736c" if akust else "#2c2926"), sw=(0.05 if akust else 0.03))
    if akust and s1 - s0 > 2.0:
        nn = int((s1 - s0) / 1.3)
        for q in range(1, nn + 1):
            F.vline(s0 + (s1 - s0) * q / (nn + 1), z0, z1, stroke=ME, sw=0.05)


def bipv_plycina(F, s0, s1, z0, z1):
    """Płycina BIPV szkło-szkło w kolorze grafitowego brązu (moduły 3 × 2)."""
    F.rect(s0, s1, z0, z1, fill=PV_PL, stroke=INK, sw=0.04)
    for q in (1, 2):
        F.vline(s0 + (s1 - s0) * q / 3, z0, z1, stroke=PV_PL_L, sw=0.025)
    F.hline(s0, s1, (z0 + z1) / 2, stroke=PV_PL_L, sw=0.025)


def faktura(F, s0, s1, z0, z1, tint, step=0.135):
    """Ceramika ryflowana co 0,135 m (M2, M4); w skali ≥ 1:500 uproszczenie graficzne co 0,27 m."""
    st = step if SCALE <= 250 else step * 2
    c = mix(tint, INK, 0.16)
    q = s0 + st / 2
    while q < s1:
        F.vline(q, z0, z1, stroke=c, sw=0.022)
        q += st


# ---------------------------------------------------------------- skrzydło / segment: „porządek kamieniczny”
def kamienica_upper(F, s_lo, s_hi, tint, relief=0.0, axis=OS_SK, win=WIN_SK, sill=PAR_SK, anchor="hi", floors=FLOORS_W,
                    ryfl=False, skip=()):
    """Trzon (kond. 1–4): tło ceramiki/tynku, okna 1,20 × 2,35 nad parapetem 0,60 z kwaterą stałą do 0,90 (poprzeczka),
    nadproże 2,95, ościeże 0,35. relief = cofnięcie wypełnień (pas okienny) za lico filarów – cień od filara z lewej.
    skip: zbiór (indeks osi, rzędna kondygnacji) bez okna (np. żaluzje)."""
    F.rect(s_lo, s_hi, Z_KORDON, Z_GZ0, fill=tint, stroke="none")
    if ryfl:
        faktura(F, s_lo, s_hi, Z_KORDON, Z_GZ0, tint)
    n = int(round((s_hi - s_lo) / axis + 1e-6))
    cs = [(s_hi - (j + 0.5) * axis) if anchor == "hi" else (s_lo + (j + 0.5) * axis) for j in range(n)]
    for j, c in enumerate(cs):
        if relief > 0:      # wypełnienie cofnięte: cień rzucany przez filar na lewą krawędź pasa okiennego
            F.rect(c - win[0] / 2, c + win[0] / 2, Z_KORDON, Z_GZ0, fill=INK, op=0.035 + relief * 0.25)
            F.rect(c - win[0] / 2, c - win[0] / 2 + relief * 0.9, Z_KORDON, Z_GZ0, fill=INK, op=0.13)
        for zf in floors:
            if (j, zf) in skip:
                continue
            window(F, c - win[0] / 2, win[0], zf + sill, win[1], reveal=OSC_SK, mull=False, transom=KW_SK - sill)
    return cs


def cokol(F, s_lo, s_hi, z_g, plinth=0.0, step=4.05, pier=0.825, anchor="hi", gate=None, doors=()):
    """Parter (cokół, 4,80 m): filary co 4,05 m w odcieniu cokołu S 3502-Y, witryny na pełną wysokość z naświetlem
    na 122,77 (pas nad parterem Maz. 19); kordon granitowy 0,35 m na 124,10."""
    z_k0 = Z_KORDON - 0.35
    F.rect(s_lo, s_hi, z_g, Z_KORDON, fill=GC, stroke="none")
    n = int(round((s_hi - s_lo) / step + 1e-6))
    for j in range(n):
        a, b = (s_hi - (j + 1) * step, s_hi - j * step) if anchor == "hi" else (s_lo + j * step, s_lo + (j + 1) * step)
        a0, b0 = max(a + pier / 2, s_lo), min(b - pier / 2, s_hi)
        if gate and a >= gate[0] - 0.01 and b <= gate[1] + 0.01:
            continue
        zb = z_g + plinth
        window(F, a0, b0 - a0, zb, z_k0 - zb, reveal=OSC_SK, transom=Z_NASW - zb, mull=False)
    if gate:
        F.rect(gate[0], gate[1], z_g, z_k0, fill=REC, stroke=INK, sw=0.08)
        for q in range(1, 14):
            x = gate[0] + (gate[1] - gate[0]) * q / 14
            F.vline(x, z_g + 0.1, Z_NASW + 0.43, stroke="#b8b0a4", sw=0.05)
        F.hline(gate[0], gate[1], Z_NASW + 0.43, stroke="#b8b0a4", sw=0.08)
    for (a, b, h, lab) in doors:
        F.rect(a, b, z_g, z_g + h, fill=ME, stroke=INK, sw=0.07)
        for q in range(1, int(h / 0.3)):
            F.hline(a + 0.05, b - 0.05, z_g + q * 0.3, stroke="#6b645e", sw=0.03)
    F.rect(s_lo, s_hi, z_k0, Z_KORDON, fill=G, stroke=INK, sw=0.09)      # kordon 124,10 (granit 0,35 m)
    F.rect(s_lo, s_hi, z_k0 - 0.15, z_k0, fill=INK, op=0.18)


def gzyms(F, s_lo, s_hi, wysieg=WYS_GR):
    """Gzyms-attyka granitowy 0,70 m (139,45–140,15). Lico < 0,30 m od granicy: wysięg 0,00, linię cienia daje fryz
    wklęsły 0,15 m pod gzymsem; lico dziedzińcowe: wysięg 0,30 m → cień rzucany i cień podniebienia."""
    if wysieg > 0.01:
        F.rect(s_lo, s_hi, Z_GZ0 - wysieg, Z_GZ0, fill=INK, op=0.22)
        F.rect(s_lo, s_hi, Z_GZ0, Z_GZ1, fill=G, stroke=INK, sw=0.12)
        F.rect(s_lo, s_hi, Z_GZ0, Z_GZ0 + 0.06, fill=INK, op=0.22)
    else:
        F.rect(s_lo, s_hi, Z_GZ0 - FRYZ, Z_GZ0, fill=INK, op=0.58)
        F.hline(s_lo, s_hi, Z_GZ0 - FRYZ, stroke=INK, sw=0.05)
        F.rect(s_lo, s_hi, Z_GZ0, Z_GZ1, fill=G, stroke=INK, sw=0.12)
    F.hline(s_lo, s_hi, Z_GZ1 - 0.07, stroke=ME, sw=0.08)


def posesje_od_maz19():
    """[(nazwa, s0, s1)] wzdłuż osi s skrzydła od narożnika przy Maz. 19 (M1 → M4)."""
    out, s0 = [], 0.0
    for nm in ("M1", "M2", "M3", "M4"):
        out.append((nm, s0, s0 + float(SEGM[nm])))
        s0 += float(SEGM[nm])
    return out


def wing_west():
    """Lico od ul. Mazowieckiej z dziobem R 3,5 i licem pn. dziobu (od skweru) – wszystkie < 0,30 m od granicy."""
    pts = run(M_PTS, IM["wieza_pn"], IM["ulica_maz19"])       # (67,49; 69,59) → dziób R 3,5 → (48,84; 9,68)
    F = Face(pts, -1.0, Z_GZ1, "M-W", fill=G)
    L = F.L
    pos = posesje_od_maz19()
    for nm, a, b in pos:          # s rośnie od pn. (dziób) do Maz. 19 → posesja [a, b] od Maz. 19 to [L − b, L − a]
        kamienica_upper(F, L - b, L - a, C[nm], float(RELIEF[nm]), ryfl=nm in FAKTURA)
    naroze_hi = L - pos[-1][2]
    kamienica_upper(F, 0.35, naroze_hi, C["M4"], float(RELIEF["M4"]), ryfl="M4" in FAKTURA)
    z_g = -0.85
    m1 = float(SEGM["M1"])
    gate = (L - m1 - 4.05, L - m1)                              # brama ogrodowa w pierwszych 3 modułach M2
    cokol(F, 0, L, z_g, plinth=0.0, gate=gate)
    F.rect(L - m1, L, z_g, z_g + 0.70, fill=GC, stroke=INK, sw=0.07)    # cokół pełny 0,70 (M1, chodnik 118,60)
    for nm, a, b in pos[1:]:
        F.rect(L - a - 0.10, L - a + 0.10, Z_KORDON, Z_GZ0, fill=ME, stroke="none")   # fuga 0,20 m między posesjami
    F.rect(naroze_hi - 0.10, naroze_hi + 0.10, Z_KORDON, Z_GZ0, fill=ME, stroke="none")
    gzyms(F, 0, L, WYS_GR)
    # M1 – pierwsza oś przy szczycie Maz. 19 cofnięta 0,30 m (fuga/uskok): cień uskoku na całej wysokości trzonu i gzymsu
    F.rect(L - OS_SK, L, Z_KORDON, Z_GZ1, fill=INK, op=0.07)
    F.rect(L - OS_SK, L - OS_SK + 0.30 * 0.6, Z_KORDON, Z_GZ1, fill=INK, op=0.30)
    return F


def wing_east():
    """Lica dziedzińcowe skrzydła: tynk mineralny w tonie ceramiki posesji, gzyms z wysięgiem 0,30 m, brama ogrodowa."""
    pos = posesje_od_maz19()
    F1 = Face(run(M_PTS, IM["maz19_dz"], IM["dz_pn"]), -1.0, Z_GZ1, "M-E", fill=G)     # s od Maz. 19 (pd.) na pn.
    for nm, a, b in pos:
        a, b = max(0.0, a), min(F1.L, b)
        if b - a > 0.5:
            kamienica_upper(F1, a, b, tynk(C[nm]), 0.0, anchor="lo")
    m1 = float(SEGM["M1"])
    cokol(F1, 0, F1.L, -0.6, anchor="lo", gate=(m1, m1 + 4.05))
    for nm, a, b in pos[1:]:
        if 0.3 < a < F1.L - 0.3:
            F1.rect(a - 0.06, a + 0.06, Z_KORDON, Z_GZ0, fill=mix(ME, "#ffffff", 0.35), stroke="none")   # fuga tynku
    gzyms(F1, 0, F1.L, WYS_DZ)
    F2 = Face(run(M_PTS, IM["dz_pn"], IM["wieza_pd"]), -1.0, Z_GZ1, "M-Es", fill=G)    # krótkie lico pd. przy wieży
    s_mid = F1.L                                                                          # posesja na końcu lica wsch.
    nm2 = next((nm for nm, a, b in pos if a <= s_mid <= b), "M3")
    kamienica_upper(F2, 0.0, F2.L, tynk(C[nm2]), 0.0, anchor="lo")
    cokol(F2, 0, F2.L, -0.4, anchor="lo")
    gzyms(F2, 0, F2.L, WYS_DZ)
    return [F1, F2]


def segment_faces():
    p = S_PTS
    # ---- lico wsch. (Wybrzeże, 0,24 m od granicy): ceramika S 1010-Y30R, 5 osi, gzyms bez wysięgu (fryz), brama 4,0 m
    E = Face([p[1], p[2]], -1.0, Z_GZ1, "S-E", fill=G)
    L = E.L
    m = (L - 5 * OS_SK) / 2
    kamienica_upper(E, m, L - m, C["SEG"], 0.0, anchor="lo")
    E.rect(0, m, Z_KORDON, Z_GZ0, fill=C["SEG"]); E.rect(L - m, L, Z_KORDON, Z_GZ0, fill=C["SEG"])
    zg = -0.25
    z_k0 = Z_KORDON - 0.35
    E.rect(0, L, zg, z_k0, fill=GC)
    # brama 4,0 m na v −0,40…−4,40 (s = L−4,4 … L−0,4); próg 119,10 = chodnik + zapora samoczynna (G-K-2, G-I-1)
    g0, g1 = L - 4.4, L - 0.4
    E.rect(g0, g1, zg, zg + 4.0, fill=ME, stroke=INK, sw=0.08)
    for q in range(1, 13):
        E.hline(g0 + 0.05, g1 - 0.05, zg + q * 0.3, stroke="#6b645e", sw=0.03)
    # drzwi pełne od Wybrzeża (G-I-1, P-I5): punkt odpadów / dostawy ręczne przy dźwigu T (narożnik SE, v −9,70…−6,45)
    # oraz trafo SN/nn (między szybem T a bramą); rozdzielnia nn i BESS – dostęp od wewnątrz (wentylacja trafo do lica zach.)
    doors = [(1.85, 3.25, 2.40), (4.40, 6.00, 2.60)]          # odpady/T 1,40 · trafo 1,60 (dwuskrzydłowe)
    for a, b, h in doors:
        E.rect(a, b, zg, zg + h, fill=ME, stroke=INK, sw=0.07)
        for q in range(1, int(h / 0.3)):
            E.hline(a + 0.05, b - 0.05, zg + q * 0.3, stroke="#6b645e", sw=0.03)
        if b - a > 1.5:
            E.vline((a + b) / 2, zg, zg + h, stroke=INK, sw=0.05)
    for a in [x for d in doors for x in d[:2]] + [g0, g1]:
        E.vline(a, zg, z_k0, stroke=INK, sw=0.08)
    E.rect(0, L, z_k0, Z_KORDON, fill=G, stroke=INK, sw=0.09)
    gzyms(E, 0, L, WYS_GR)
    # ---- lico zach. (dziedziniec): tynk w tonie ceramiki segmentu, gzyms z wysięgiem 0,30 m, żaluzje techniki (E-I-1, E-I-3)
    Wf = Face([p[3], p[0]], -1.0, Z_GZ1, "S-W", fill=G)       # s = 0 przy wieży (pn.) → pd.
    m = (Wf.L - 3 * OS_SK) / 2
    f1, f3, f4 = LEV["1"], LEV["3"], LEV["4"]
    skip = {(j, f) for j in range(3) for f in (f1, f3, f4)}
    cs = kamienica_upper(Wf, m, Wf.L - m, tynk(C["SEG"]), 0.0, anchor="lo", skip=skip)
    Wf.rect(0, m, Z_KORDON, Z_GZ0, fill=tynk(C["SEG"])); Wf.rect(Wf.L - m, Wf.L, Z_KORDON, Z_GZ0, fill=tynk(C["SEG"]))
    hw = WIN_SK[0] / 2
    zaluzja(Wf, cs[0] - hw, cs[1] + hw, f1 + 0.45, f1 + 2.95)                 # kond. 1: powietrze agregatu HVO ≈ 8 m²
    zaluzja(Wf, cs[2] - hw, cs[2] + hw, f1 + 1.70, f1 + 2.95)                 # kond. 1: wentylacja trafo 1,5 m² (kanał z parteru)
    zaluzja(Wf, cs[0] - hw, cs[2] + hw, f3 + 0.60, f3 + 2.90, pitch=0.23, akust=True)   # kond. 3: dry-cooler 12 m²
    zaluzja(Wf, cs[0] - hw, cs[2] + hw, f4 + 0.40, f4 + 2.70, pitch=0.23, akust=True)   # kond. 4: dry-cooler 12 m²
    cokol(Wf, m, Wf.L - m, -0.35, anchor="lo")
    gzyms(Wf, 0, Wf.L, WYS_DZ)
    # ---- ściana pd. (od dz. 10/2, nie ulica, ≤ 25 m): BIPV satynowane w tonie ceramiki w rysunku osi 2,025 m,
    #      pilastry płytkie 0,12 m, fugi ciemnego metalu; parter – cokół z pnączami; attyka 139,10 = poziom tarasu
    Sf = Face([p[0], p[1]], -1.0, Z_ATT_SPD, "S-S", fill=PV_SEG)
    Ls = Sf.L
    z_k0 = Z_KORDON - 0.35
    nax = int(Ls / OS_SK)
    m = (Ls - nax * OS_SK) / 2
    for j in range(nax):          # panele BIPV między pilastrami: podział na moduły (fugi ciemnego metalu)
        a, b = m + j * OS_SK + FIL_SK / 2, m + (j + 1) * OS_SK - FIL_SK / 2
        for zf in FLOORS_W:
            for zz in (zf, zf + 1.875):
                Sf.hline(a, b, zz, stroke=ME, sw=0.04)
        Sf.vline(a, Z_KORDON, Z_ATT_SPD - 0.08, stroke=ME, sw=0.04)
        Sf.vline(b, Z_KORDON, Z_ATT_SPD - 0.08, stroke=ME, sw=0.04)
    for j in range(nax + 1):      # pilastry 0,825 m co 2,025 m (wysunięte 0,12 m → wąski cień z prawej)
        c = m + j * OS_SK
        a, b = max(0.0, c - FIL_SK / 2), min(Ls, c + FIL_SK / 2)
        Sf.rect(a, b, Z_KORDON, Z_ATT_SPD - 0.08, fill=mix(PV_SEG, "#ffffff", 0.18), stroke=ME, sw=0.04)
        Sf.rect(b, min(Ls, b + 0.12 * 0.6), Z_KORDON, Z_ATT_SPD - 0.08, fill=INK, op=0.16)
        for zf in FLOORS_W:
            Sf.hline(a, b, zf, stroke=ME, sw=0.035)
    Sf.rect(0, Ls, -1.0, z_k0, fill=GC, stroke=INK, sw=0.08)                   # parter: cokół (ściana pełna)
    Sf.rect(0, Ls, z_k0, Z_KORDON, fill=G, stroke=INK, sw=0.08)                # kordon
    Sf.rect(0, Ls, Z_ATT_SPD - 0.08, Z_ATT_SPD, fill=ME, stroke=INK, sw=0.04)  # obróbka attyki 139,10
    # narożne attyki lic wsch. i zach. (140,15) widziane w profilu oraz balustrada szklana tarasu cofnięta 1,5 m (do 140,20)
    Sf.rect(0, 0.47, Z_ATT_SPD, Z_GZ1, fill=G, stroke=INK, sw=0.08)
    Sf.rect(Ls - 0.47, Ls, Z_ATT_SPD, Z_GZ1, fill=G, stroke=INK, sw=0.08)
    Sf.rect(0.47, Ls - 0.47, Z_TARAS, Z_TARAS + BAL_H, fill="#c7d0d6", op=0.55, stroke="#6d7a85", sw=0.04)
    Sf.hline(0.47, Ls - 0.47, Z_TARAS + BAL_H, stroke="#55616b", sw=0.07)
    rnd = random.Random(7)
    z_top = z_k0 - 0.2
    for q in range(13):           # pnącza (winobluszcz) na linkach co 1,45 m – tylko w strefie parteru
        s = 0.8 + q * 1.45
        if s > Ls - 0.4:
            break
        h = z_top - 0.5 * abs(math.sin(q * 1.3 + 0.4))
        Sf.vline(s, 0.3, z_top, stroke="#6b7a55", sw=0.05)
        for _ in range(int(h * 9)):
            zz = rnd.uniform(0.2, h); taper = 1.0 - (zz / (h + 2.0)) * 0.5
            Sf.circle(s + rnd.gauss(0, 0.5 * taper), zz, rnd.uniform(0.16, 0.36) * taper,
                      fill=rnd.choice(("#6f8456", "#7f9462", "#5f7448", "#8c9d6c")), op=0.55)
    return [E, Wf, Sf]


# ---------------------------------------------------------------- wieża: „wielki porządek”
def plyciny_rows():
    """Pasy płycin (nadproże → parapet kondygnacji wyżej): P/1, 1/2, 2/3, 3/4, 4/5 (pod kordonem), 5/6 (lico przed kond. 6)."""
    rows = [("P/1", Z_P_HEAD, LEV["1"] + PAR_WI)]
    for lo, hi in (("1", "2"), ("2", "3"), ("3", "4")):
        rows.append((f"{lo}/{hi}", LEV[lo] + NADPR_WI, LEV[hi] + PAR_WI))
    rows.append(("4/5", LEV["4"] + NADPR_WI, LEV["5"]))
    rows.append(("5/6", LEV["5"] + NADPR_WI, Z6_0))
    return rows


def tower_bays(F, piers, crown, podcien=None, entries=(), czerpnia=None, nadcisnienie=False, bipv=False, zg=-0.2, kordon=True):
    """piers: posortowane (s0, s1). Przęsła między filarami: okna 1,65 × 2,45 (parapet 0,55 z kwaterą stałą do 1,10,
    nadproże 3,00, ościeże 0,45 Al), płyciny metalowe / BIPV / żaluzje czerpni."""
    F.rect(0, F.L, zg, Z_ROOF_W, fill=ME, stroke="none")
    bays = [(a1, b0) for (a0, a1), (b0, b1) in zip(piers[:-1], piers[1:]) if b0 - a1 >= 0.3]
    cz = set()
    if czerpnia:
        cz = {i for i, (a, b) in enumerate(bays) if min(b, czerpnia[1]) - max(a, czerpnia[0]) >= 0.6}
    nadc = None
    if nadcisnienie and cz:
        b_end = max(bays[i][1] for i in cz)
        nadc = next((i for i, (a, b) in enumerate(bays) if a >= b_end + NADC_MIN), None)
    rows = plyciny_rows()
    for i, (a, b) in enumerate(bays):
        w = min(WIN_WI[0], b - a)
        c0 = (a + b) / 2 - w / 2
        # parter
        in_pod = podcien and a >= podcien[0] - 0.01 and b <= podcien[1] + 0.01
        if in_pod:
            F.rect(a, b, zg, LEV["1"], fill=REC, op=0.92)
            F.rect(a + 0.15, b - 0.15, zg, 3.9, fill=GLD, stroke="#5d646b", sw=0.05)
        else:
            window(F, a + 0.08, b - a - 0.16, zg, Z_P_HEAD - zg, reveal=OSC_WI, transom=3.4 - zg)
        for (e0, e1, lab) in entries:
            if e0 < b and e1 > a:
                F.rect(max(a, e0), min(b, e1), zg, 3.2, fill=REC, op=0.9)
                F.rect(max(a, e0) + 0.2, min(b, e1) - 0.2, zg, 2.9, fill="#c9a96b", op=0.55, stroke=INK, sw=0.05)
        # płyciny
        for nm, z0, z1 in rows:
            if z1 - z0 < 0.2 or (in_pod and nm == "P/1"):
                continue
            if i in cz and nm in ("P/1", "1/2"):
                zaluzja(F, c0, c0 + w, z0 + 0.04, z1 - 0.04)                     # czerpnia zbiorcza (≈ 17 m²)
            elif i == nadc and nm == "P/1":
                zaluzja(F, c0, c0 + w, z0 + 0.04, z1 - 0.04, pitch=0.12)         # czerpnie nadciśnienia klatek A i B
                F.vline(c0 + w / 2, z0 + 0.04, z1 - 0.04, stroke=ME, sw=0.06)
            elif bipv and nm != "4/5" and z1 <= Z_BIPV_MAX:
                bipv_plycina(F, c0, c0 + w, z0, min(z1, Z6_0))
        # okna kondygnacji 1–5
        for f in ("1", "2", "3", "4", "5"):
            zf = LEV[f]
            sill = PAR_WI
            if f == "5" and kordon:
                F.rect(a, b, LEV["5"], Z_GZ1, fill=G, stroke=INK, sw=0.07)     # kordon kwartału +19,80–20,85
                sill = Z_GZ1 - LEV["5"]
            tr = (KW_WI - sill) if KW_WI - sill > 0.05 else None
            window(F, c0, w, zf + sill, NADPR_WI - sill, reveal=OSC_WI, transom=tr)
        # kond. 6 – „kondygnacja cienia”: szkło i metal 0,40 m za licem filarów
        F.rect(a, b, Z6_0, Z6_1, fill=REC)
        F.rect(a + 0.1, b - 0.1, LEV["6"] + PAR_WI, LEV["6"] + NADPR_WI, fill=GLD, stroke="#5d646b", sw=0.04)
        F.rect(a, b, Z6_1 - 0.45, Z6_1, fill=INK, op=0.35)
        # korona S
        zS = LEV["S"]
        F.rect(a, b, Z6_1, Z_ROOF_W, fill=G)
        if crown == "hall":
            window(F, c0, w, zS + 0.70, 5.0, reveal=OSC_WI, transom=2.5)
        elif crown == "komisje_lamele":
            window(F, c0, w, zS + 0.70, 4.2, reveal=OSC_WI, transom=2.6)
            F.rect(a, b, zS + 5.6, zS + 8.5, fill=GLD)
            q = a + 0.06
            while q < b - 0.2:      # pas lameli ceramicznych maskujących wyrzutnie (strona dziedzińca), ton lameli korony
                F.rect(q, q + 0.25, zS + 5.6, zS + 8.5, fill=C["LAM"], stroke=mix(C["LAM"], INK, 0.3), sw=0.03)
                q += 0.42
        else:
            window(F, c0, w, zS + 0.70, 4.2, reveal=OSC_WI, transom=2.6)
    for (p0, p1) in piers:
        F.rect(p0, p1, zg, Z_ROOF_W, fill=G, stroke=INK, sw=0.1)
        F.rect(p0, p1, zg, LEV["1"], fill=GC, stroke=INK, sw=0.1)       # cokół parteru S 3502-Y; filary ciągłe od +4,80
        F.rect(p1, min(F.L, p1 + 0.22), LEV["1"] if not podcien else zg, Z_ROOF_W, fill=INK, op=0.13)   # cień filara
    F.rect(0, F.L, Z_ROOF_W, Z_ATT_W, fill=G, stroke=INK, sw=0.12)       # attyka 1,00 m bez wysięgu
    F.rect(0, F.L, Z_ATT_W - 0.15, Z_ATT_W, fill=ME, stroke="none")


def pier_grid(L, start_pairs, massive=()):
    """start_pairs: list of pier centres; massive: list of (s0,s1) heavy piers (override overlaps)."""
    pr = [(c - 0.525, c + 0.525) for c in start_pairs]
    out = []
    for p in pr:
        if any(p[1] > m0 - 0.05 and p[0] < m1 + 0.05 for m0, m1 in massive):
            continue
        out.append((max(0, p[0]), min(L, p[1])))
    out += list(massive)
    return sorted(out)


def fib_word(n):
    a, b = "A", "AB"
    while len(b) < n:
        a, b = b, b + a
    return b[:n]


def lamele_luku(L):
    """Położenia osi 21 lameli na łuku (rozstawy 1,35 / 0,675 m w ciągu Fibonacciego, układ wyśrodkowany na łuku)."""
    pitches = [LAM_A if c == "A" else LAM_B for c in fib_word(LAM_N - 1)]
    tot = sum(pitches)
    s = (L - tot) / 2
    out = [s]
    for p in pitches:
        s += p
        out.append(s)
    return out


def zadaszenie_faces():
    """Zadaszenie tarasu ogrodowego BIPV (element elewacji dziedzińcowej): krawędź czołowa z podporami + krawędzie boczne."""
    u0, u1 = ZAD_U
    zg = -0.35
    t = 0.28
    F = Face([uv(u0, -ZAD_GLEB), uv(u1, -ZAD_GLEB)], zg, ZAD_H, "zadaszenie", fill=None)
    for s in [0.12 + (F.L - 0.24) * q / 4 for q in range(5)]:       # słupy stalowe co ≈ 5 m
        F.rect(s - 0.08, s + 0.08, zg, ZAD_H - t, fill=ME, stroke=INK, sw=0.04)
    F.rect(0, F.L, ZAD_H - t, ZAD_H, fill=ME, stroke=INK, sw=0.06)                  # belka krawędziowa
    F.rect(0, F.L, ZAD_H - 0.03, ZAD_H + 0.04, fill="#5d6b78", stroke="none")       # moduły BIPV szkło-szkło (półprzezierne)
    F.rect(0, F.L, ZAD_H - t - 0.35, ZAD_H - t, fill=INK, op=0.10)                  # cień pod krawędzią
    out = [F]
    for a, b in (((u0, 0.0), (u0, -ZAD_GLEB)), ((u1, -ZAD_GLEB), (u1, 0.0))):
        Fs = Face([uv(*a), uv(*b)], ZAD_H - t, ZAD_H, "zadaszenie-bok", fill=ME, outline=True)
        out.append(Fs)
    return out


def tower_faces():
    p = W_PTS
    i_arc0, i_arc1 = _vi(p, *LUK["poczatek"]), _vi(p, *LUK["koniec"])     # (109,75; 65,48) … (92,83; 75,77)
    # East (Wybrzeże): s from south (113.47,50.23) to arc start
    E = Face([p[1], p[i_arc0]], -1.0, Z_ATT_W, "W-E", fill=G)
    piersE = pier_grid(E.L, [0.525] + [0.525 + 2.7 * j for j in range(1, 5)], massive=[(E.L - 2.2, E.L)])
    tower_bays(E, piersE, "hall", entries=[(1.40, 6.80, "Wejście Obywatelskie")], zg=-0.15)   # v 1,40–6,80 (wnęka 1,5 m)
    # Arc R14
    A = Face(p[i_arc0:i_arc1 + 1], -1.0, Z_ATT_W, "W-luk", fill=G)
    A.rect(0, A.L, -0.15, LEV["1"], fill=REC, op=0.95)
    A.rect(0, A.L, -0.15, 3.9, fill=GLD, op=0.9)
    for kk in range(1, 6):
        s = R_LUK * math.radians(15 * kk)
        A.rect(s - 0.3, s + 0.3, -0.15, LEV["1"], fill=G, stroke=INK, sw=0.08)
    for f in ("1", "2", "3", "4", "5"):
        zf = LEV[f]
        A.rect(0, A.L, zf, zf + 1.30, fill=(G if f == "1" else C["LUK"]), stroke=INK, sw=0.08)   # nad podcieniem: granit z napisem
        A.rect(0, A.L, zf + 1.30, zf + 3.75, fill=GL, stroke=INK, sw=0.06)
        A.rect(0, A.L, zf + 3.25, zf + 3.75, fill=INK, op=0.25)
        q = 1.35
        while q < A.L:
            A.vline(q, zf + 1.30, zf + 3.75, stroke=ME, sw=0.05)
            q += 1.35
    zS = LEV["S"]
    A.rect(0, A.L, LEV["6"], zS, fill=REC)
    # korona łuku: szkło z sitodrukiem 30 % na R 13,40 (0,60 za licem) + 21 lameli 0,35 × 0,60 (R 13,40–14,00), Fibonacci
    A.rect(0, A.L, zS, Z_ROOF_W, fill=GLF)
    for zz in (zS + 0.70, zS + 4.0, zS + 7.3):
        A.hline(0, A.L, zz, stroke="#6c6b67", sw=0.04)                         # rygle fasady słupowo-ryglowej
    A.rect(0, A.L, Z_ROOF_W - 0.45, Z_ROOF_W, fill=INK, op=0.28)              # cień attyki na cofniętym szkle
    lam_side = (mix(C["LAM"], "#ffffff", 0.22), mix(C["LAM"], INK, 0.32))
    for s in lamele_luku(A.L):
        A.fin(s, LAM_W, R_LUK - R_SZYB, zS, Z_ROOF_W, fill=C["LAM"], side=lam_side, stroke=mix(C["LAM"], INK, 0.45), sw=0.03)
    A.rect(0, A.L, Z_ROOF_W, Z_ATT_W, fill=G, stroke=INK, sw=0.12)
    A.rect(0, A.L, Z_ATT_W - 0.15, Z_ATT_W, fill=ME, stroke="none")
    # North (Plac Mostowy): s from arc end (east) to NW corner; u = 26.0 − s
    N = Face([p[i_arc1], p[i_arc1 + 1]], -1.0, Z_ATT_W, "W-N", fill=G)
    Lu = N.L
    centres = [Lu - (0.525 + 2.7 * j) for j in range(0, 9)]
    piersN = pier_grid(Lu, centres, massive=[(0.0, 1.7)])
    tower_bays(N, piersN, "hall", podcien=(0.0, 12.5), entries=[(2.0, 5.0, "wejście od skweru")], zg=-0.1)
    # West (nad skrzydłem): s from NW corner (north) to SW corner
    Wf = Face([p[i_arc1 + 1], p[0]], -1.0, Z_ATT_W, "W-W", fill=G)
    piersW = pier_grid(Wf.L, [0.525 + 2.7 * j for j in range(0, 11)] + [Wf.L - 0.525])
    tower_bays(Wf, piersW, "komisje", zg=-0.1)
    # South (ogród, dziedziniec): s = u from SW (74.61,40.76) to SE (113.47,50.23)
    Sf = Face([p[0], p[1]], -1.0, Z_ATT_W, "W-S", fill=G)
    piersS = pier_grid(Sf.L, [0.525 + 2.7 * j for j in range(0, 15)], massive=[(37.8, 40.0)])   # filar narożny SE 2,2 m
    tower_bays(Sf, piersS, "komisje_lamele", entries=[(8.6, 11.4, "wejście ogrodowe"), (3.0, 4.6, "rowerownia")],
               czerpnia=CZERPNIA_U, nadcisnienie=True, bipv=True, zg=-0.35)
    return [E, A, N, Wf, Sf] + zadaszenie_faces()


# ---------------------------------------------------------------- neighbours
def merge_collinear(pts, tol_deg=12.0, min_len=0.6):
    """Drop vertices where the outline turns by < tol (survey outlines are split into many short edges)."""
    changed = True
    pts = list(pts)
    while changed and len(pts) > 3:
        changed = False
        for i in range(len(pts)):
            a, b, c = pts[i - 1], pts[i], pts[(i + 1) % len(pts)]
            h1 = math.atan2(b[1] - a[1], b[0] - a[0]); h2 = math.atan2(c[1] - b[1], c[0] - b[0])
            turn = abs(math.degrees((h2 - h1 + math.pi) % (2 * math.pi) - math.pi))
            if turn < tol_deg or math.dist(a, b) < min_len * 0.3:
                pts.pop(i); changed = True
                break
    return pts


def neighbour_faces(names):
    faces = []
    for b in S["budynki"]["items"]:
        if b.get("nazwa") not in names or b.get("czesciowy_przyciety_ramka"):
            continue
        pg = poly_of(b)
        pts = merge_collinear(ccw(list(pg.exterior.coords)[:-1]))
        zt = b.get("gora_szac_H", Z0 + b.get("wysokosc_szac_m", 20)) - Z0
        zg = b["teren_wokol_H"]["min"] - Z0
        n = len(pts)
        for i in range(n):
            a, c = pts[i], pts[(i + 1) % n]
            L = math.dist(a, c)
            if L < 0.4:
                continue
            F = Face([a, c], zg, zt, b["nazwa"], fill=NB_F, outline=False)
            F.rect(0, L, zg, zt, fill="none", stroke=NB_S, sw=0.12)
            nax = math.degrees(math.atan2(c[1] - a[1], c[0] - a[0]))
            nrm = (math.degrees(math.atan2(c[1] - a[1], -(c[0] - a[0]))) + 360) % 360
            gable = L < 8 or any(abs(((nrm - g + 180) % 360) - 180) < 8 for g in ())
            if b["nazwa"] == "Mazowiecka 19" and abs(L - 15.78) < 0.3:
                gable = True
            if b["nazwa"].startswith("Wybrzeze J. Slowackiego 5") and abs(L - 16.26) < 0.4:
                gable = True
            if not gable:
                nax_ = int(L / 2.3)
                m = (L - nax_ * 2.3) / 2
                floors = [zg + 0.8 + 3.75 * j for j in range(int((zt - zg - 2.5) / 3.75))]
                for j in range(nax_):
                    s0 = m + j * 2.3 + 0.64
                    for zf in floors:
                        F.rect(s0, s0 + 1.02, zf + 0.9, zf + 2.9 if zf > zg + 1 else zf + 2.7, fill=NB_W, stroke=NB_S, sw=0.05)
                F.hline(0, L, zt - 2.4, stroke=NB_S, sw=0.08)
                F.hline(0, L, zg + 4.2, stroke=NB_S, sw=0.06)
            faces.append(F)
    return faces


# ---------------------------------------------------------------- drawing
def ground_profile(view_az, pts):
    pr = sorted((u_of(view_az, e, n), z - Z0) for e, n, z in pts)
    return pr


def draw_cut(svg, view_az, cut, P):
    """Section profile where the vertical plane p·d = cut intersects the proposal volumes: outline + slabs."""
    from shapely.geometry import Polygon, LineString
    from umwd.facade_elev import frame
    d, r = frame(view_az)
    c0 = (d[0] * cut, d[1] * cut)
    line = LineString([(c0[0] - r[0] * 400, c0[1] - r[1] * 400), (c0[0] + r[0] * 400, c0[1] + r[1] * 400)])
    vols = [(W_PTS, Z_ATT_W, Z_ROOF_W, [LEV[i] for i in ("1", "2", "3", "4", "5", "6", "S")]),
            (M_PTS, Z_GZ1, float(B["M"]["dach"]["strop_wierzch"]), FLOORS_W),
            (S_PTS, Z_GZ1, float(B["S"]["dach"]["strop_wierzch"]), FLOORS_W)]
    z_m1 = LEV["-1"]                                        # posadzka −1 (−4,20)
    z_p0 = float(KOND["-1"]["strop_nad"]["wierzch"])        # wierzch stropu nad −1 (−0,15)
    hp = svg.hatch("ciecie", spacing=1.6, angle=45, stroke="#cfc9c0", sw=0.08)
    for pts, top, roof, floors in vols:
        x = Polygon(pts).buffer(0).intersection(line)
        segs = [x] if x.geom_type == "LineString" else list(getattr(x, "geoms", []))
        for sg in segs:
            if sg.is_empty or sg.length < 0.3:
                continue
            us = [u_of(view_az, *c) for c in sg.coords]
            ua, ub = min(us), max(us)
            svg.poly([P(ua, z_p0), P(ub, z_p0), P(ub, top), P(ua, top)], fill="#f3f1ed", stroke="none")
            svg.poly([P(ua, z_p0), P(ub, z_p0), P(ub, top), P(ua, top)], fill=hp, stroke="none")
            for zf in floors + [roof]:
                svg.poly([P(ua, zf - 0.28), P(ub, zf - 0.28), P(ub, zf), P(ua, zf)], fill=INK, stroke="none")
            svg.poly([P(ua, z_p0), P(ub, z_p0), P(ub, top), P(ua, top)], fill="none", stroke=INK, sw=0.5)
            svg.poly([P(ua, z_m1), P(ub, z_m1), P(ub, z_p0), P(ua, z_p0)], fill=INK, stroke="none", extra='fill-opacity="0.85"')


def elevation(name, title, sub, view_az, faces, ground_pts, mpzp, levels, u_pad=6.0, out_w=None, cut=None, debug=False):
    pad_l, pad_r, pad_t, pad_b = 34, 12, 22, 26
    from umwd.facade_elev import frame
    dd, _ = frame(view_az)
    us = []
    for F in faces:
        for (x, y) in F.pts:
            if cut is None or x * dd[0] + y * dd[1] >= cut - 0.5:
                us.append(u_of(view_az, x, y))
    u0, u1 = min(us) - u_pad, max(us) + u_pad
    # tight range: dry-run the painter to get the extent of what is actually visible (+ cut profile)
    _tmp = Svg(10, 10)
    _a, _b = draw_faces(_tmp, faces, view_az, lambda u, z: (u, z), cut=cut)
    if _a < _b:
        u0, u1 = _a - 2.0, _b + 2.0
    if cut is not None:
        u0 = min(u0, min(us) - 1.0); u1 = max(u1, max(us) + 1.0)
    pad_l = 30
    W = pad_l + (u1 - u0) * k + pad_r
    H = pad_t + 48 * k + pad_b
    svg = Svg(W, H)
    oy = pad_t + 46 * k

    def P(u, z):
        return (pad_l + (u - u0) * k, oy - z * k)

    # sky-light background band (very subtle) for legibility of the silhouette
    draw_faces(svg, faces, view_az, P, cut=cut, debug=debug)
    if cut is not None:
        draw_cut(svg, view_az, cut, P)
    # ground
    gp = ground_profile(view_az, ground_pts)
    gp = [(u0, gp[0][1])] + gp + [(u1, gp[-1][1])]
    poly = [P(u, z) for u, z in gp] + [P(u1, -4.0), P(u0, -4.0)]
    svg.poly(poly, fill="#ffffff", stroke="none")
    hp = svg.hatch("grunt", spacing=0.9, angle=45, stroke="#9a948c", sw=0.07)
    band = [P(u, z) for u, z in gp] + [P(u, z - 0.9) for u, z in reversed(gp)]
    svg.poly(band, fill=hp, stroke="none")
    svg.poly([P(u, z) for u, z in gp], fill="none", stroke=INK, sw=0.45, close=False)
    # MPZP limits
    for (ua, ub, z, lab, side) in mpzp:
        a, b = P(ua, z), P(ub, z)
        svg.line(a, b, stroke="#a8483a", sw=0.22, dash="2.2,1.0")
        if side == "r":
            svg.text((b[0] + 1.2, b[1] + 0.8), lab, size=1.9, fill="#a8483a")
        else:
            svg.text((a[0] - 1.2, a[1] + 0.8), lab, size=1.9, fill="#a8483a", anchor="end")
    # level marks
    x = pad_l - 8
    y_prev = -1e9
    for z, lab in sorted(levels, key=lambda q: -q[0]):
        y = P(0, z)[1]
        svg.poly([(x, y), (x - 1.3, y - 1.5), (x + 1.3, y - 1.5)], fill=INK, stroke="none")
        svg.line((x - 2.2, y), (pad_l - 2, y), stroke=INK, sw=0.12)
        if y - y_prev >= 2.3:            # w małej skali opis rzędnej zbyt bliskiej poprzedniej – tylko znacznik
            svg.text((x - 2.6, y - 0.4), lab, size=1.85, anchor="end")
            y_prev = y
    # titles
    svg.text((pad_l, 9), title, size=4.2, weight=600)
    svg.text((pad_l, 14.5), sub, size=2.3, fill="#4d4842")
    # scale bar 0–10 m
    sx, sy = pad_l, H - 9
    for i in range(5):
        svg.poly([(sx + i * 2 * k, sy), (sx + (i + 1) * 2 * k, sy), (sx + (i + 1) * 2 * k, sy + 1.2), (sx + i * 2 * k, sy + 1.2)],
                 fill=INK if i % 2 == 0 else "#ffffff", stroke=INK, sw=0.12)
    for i, t in enumerate(("0", "2", "4", "6", "8", "10 m")):
        svg.text((sx + i * 2 * k, sy + 4.0), t, size=1.8, anchor="middle")
    svg.text((sx + 10 * k + 10, sy + 1.2), f"1:{SCALE}", size=2.2, weight=600)
    out = ROOT / "build" / "rysunki" / f"elewacja_{name}_1-{SCALE}.svg"
    out.write_text(svg.render(), encoding="utf-8")
    return svg, out


def main():
    TW = tower_faces()
    WG = [wing_west()] + wing_east()
    SG = segment_faces()
    ours = TW + WG + SG
    A_min, A_max = 154.44 - Z0, 163.88 - Z0       # strefa A: 35 m nad najwyższym terenem w A, 45 m nad najniższym
    O_min, O_max = 137.41 - Z0, 143.33 - Z0       # poza A: 18 / 25 m
    LEVELS = [(Z_ATT_W, f"{fz(Z_ATT_W)} attyka ({fnpm(Z_ATT_W)})"), (Z_ROOF_W, fz(Z_ROOF_W)), (LEV["S"], f"{fz(LEV['S'])} sala Sejmiku"),
              (LEV["6"], fz(LEV["6"])), (Z_GZ1, f"{fz(Z_GZ1)} gzyms ({fnpm(Z_GZ1)})"),
              (Z_TARAS, f"{fz(Z_TARAS)} taras ({fnpm(Z_TARAS)})"), (LEV["1"], fz(LEV["1"])),
              (0.0, f"±0,00 = {fnpm(0.0)}")]
    res = []

    def spans(az, near_out=None):
        tw = [u_of(az, *p) for p in W_PTS]
        ot = [u_of(az, *p) for p in list(S_PTS) + list(M_PTS)]
        t0, t1 = min(tw), max(tw); o0, o1 = min(ot), max(ot)
        out = []
        if o0 < t0 - 0.5:
            out.append((o0 - 4, t0, "l"))
        if o1 > t1 + 0.5:
            out.append((t1, o1 + 4, "r"))
        lines = [(t0, t1, A_min, "MPZP min. 35,0 m (strefa A)", "r"), (t0, t1, A_max, "MPZP maks. 45,0 m (strefa A)", "r")]
        for (x0, x1, side) in out:
            lines += [(x0, x1, O_min, "18,0 m (poza A)", side), (x0, x1, O_max, "25,0 m (poza A)", side)]
        return lines

    az = 256.3
    res.append(elevation("E", "ELEWACJA WSCHODNIA", "od Wybrzeża J. Słowackiego (Oława / Odra) · z kamienicą Wybrzeże J. Słowackiego 5", az,
                         ours + neighbour_faces({"Wybrzeze J. Slowackiego 5"}),
                         [(118.3, 10.0, 118.85), (118.3, 28.2, 119.0), (115.98, 39.93, 118.91), (113.48, 50.18, 119.18), (109.75, 65.48, 119.44), (104.0, 76.0, 119.40)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 166.3
    res.append(elevation("N", "ELEWACJA PÓŁNOCNA", "od Placu Mostowego i przyczółka Mostu Grunwaldzkiego", az, ours + neighbour_faces({"Wybrzeze J. Slowackiego 5"}),
                         [(61.25, 66.05, 119.41), (67.57, 69.61, 119.41), (92.83, 75.77, 119.44), (109.75, 65.48, 119.44), (116.0, 40.0, 119.18), (118.5, 28.0, 119.0)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 102.4
    res.append(elevation("W", "ELEWACJA ZACHODNIA", "od ul. Mazowieckiej · z kamienicą Mazowiecka 19", az,
                         ours + neighbour_faces({"Mazowiecka 19"}),
                         [(40.0, -25.0, 118.45), (44.64, -8.38, 118.51), (48.84, 9.68, 118.40), (61.25, 66.05, 119.41), (64.0, 72.0, 119.45)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 346.3
    res.append(elevation("S", "ELEWACJA POŁUDNIOWA", "od Ogrodu Województwa (w przekroju przez ogród, bez kamienic w pierwszym planie)", az, ours,
                         [(63.5, 6.49, 118.70), (74.61, 40.76, 118.95), (96.69, 38.81, 118.95), (113.47, 50.23, 119.0), (118.3, 40.0, 119.0)],
                         spans(az), LEVELS, debug=DEBUG))
    az = 282.4
    res.append(elevation("Sd", "ELEWACJA SKRZYDŁA OD OGRODU", "elewacja wschodnia skrzydła w przekroju przez ogród · z oficyną kamienicy Mazowiecka 19", az,
                         ours + neighbour_faces({"Mazowiecka 19"}),
                         [(64.0, -8.0, 118.53), (63.5, 6.49, 118.70), (70.84, 39.84, 118.95), (74.0, 45.0, 118.95), (90.0, 46.0, 119.0)],
                         [], LEVELS, cut=-80.0, debug=DEBUG))
    # combined preview
    total_h = sum(s.h_mm for s, _ in res) + 10
    max_w = max(s.w_mm for s, _ in res)
    body = ""
    for s, _ in res:
        body += f'<div style="margin:0 0 4mm 0">{s.render()}</div>'
    html = ROOT / "docs" / "70_rysunki" / "podglady" / f"elewacje_1-{SCALE}.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{max_w+10:.0f}mm {total_h+10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{body}</body></html>', encoding="utf-8")
    print(f"{max_w + 10:.0f} {total_h + 10:.0f}")


if __name__ == "__main__":
    main()
