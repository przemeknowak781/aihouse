#!/usr/bin/env python3
"""Przekrój elewacyjny 1:50 z fragmentem elewacji (Etap II): korona wieży od strony Placu Mostowego (elewacja pn., hol
reprezentacyjny Sejmiku), z +19,10 (wariant pełny) lub +22,90 (UMWD_ZB=22.9 – wariant „korona”) do +37,70: kondygnacja 5
z kordonem kwartału, kondygnacja cienia (6), korona S z oknem 1,65 × 5,00, kratownica dachu, dach BIPV, attyka.
Warstwy wg koncepcji v1.1 (rozdz. 8, tabela przegród 1:50; JSON `elewacje.wieza`, `elewacje.U_scian`, `kondygnacje`):
filar – granit 40 / pustka 40 / wełna 260 λ 0,033 / żelbet; płycina – Al 3 / pustka 40 / wełna 260 / żelbet 200; konsole
nierdzewne z przekładką (U 0,147); ościeża 0,45 m z blachy Al (granit wyłącznie na licu filara); okna z parapetem 0,55
i nadprożem 3,00 (kaseta ZIP do +3,18 pod stropem +3,32); bez jakiegokolwiek wysięgu poza lico (czapa attyki, obróbki, parapety).

Wariant UMWD_FRAG=skrzydlo (v1.1, P7 „wieża i skrzydło”): przekrój przez oś okna skrzydła od ul. Mazowieckiej (kond. 4
i zwieńczenie: ceramika 40 / pustka 40 / wełna 240 λ 0,031 / żelbet 150 = 0,47 m, U 0,144; okno 1,20 × 2,35, parapet 0,60,
kwatera stała do 0,90, pochwyt 1,10, nadproże 2,95, ZIP do 3,13, ościeże 0,35 Al; gzyms-attyka 0,70 m bez wysięgu z fryzem
wklęsłym 0,15 m), fragment elewacji na styku posesji M1 | M2 oraz detal zwieńczenia od dziedzińca (tynk, wysięg 0,30 m).

Wynik: build/rysunki/przekroj_elewacyjny_1-50[_korona].svg + docs/70_rysunki/podglady/przekroj_elewacyjny_1-50[_korona].html;
UMWD_FRAG=skrzydlo → build/rysunki/przekroj_elewacyjny_skrzydlo_1-50.svg + docs/70_rysunki/podglady/przekroj_elewacyjny_skrzydlo_1-50.html
"""
import sys, json, re
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from umwd.svg import Svg

K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
INK = "#1f1d1a"
SC = 20.0                         # 1:50 → 20 mm per metre
import os
ZB, ZT = float(os.environ.get("UMWD_ZB", "19.10")), 37.70
GRAN, GRAN_H = "#ddd8cf", "#b9b2a6"
INS = "#f1e9cf"
MET = "#4a4541"
MET_V = "#8f877f"                 # blacha Al ościeża widziana w głębi (za płaszczyzną przekroju)
GLASS = "#4a6a85"
CONC = "#e4e2de"

# ------------------------------------------------------------------ dane (koncepcja.json v1.1)
Z0 = float(K["meta"]["zero"]["wzgl_0_00_m_npm"])
KOND = {kd["kondygnacja"]: kd for kd in K["kondygnacje"]}
F4, F5, F6, FS = (float(KOND[i]["posadzka_wzgl"]) for i in ("4", "5", "6", "S"))
FLOOR = round(F6 - float(KOND["5"]["strop_nad"]["wierzch"]), 3)                                 # podłoga podniesiona 0,15
SLAB = round(float(KOND["5"]["strop_nad"]["wierzch"]) - float(KOND["5"]["strop_nad"]["spod_wieza"]), 3)   # płyta 0,28
EWI = K["elewacje"]["wieza"]
PAR, NADPR, OSC = float(EWI["parapet_m"]), float(EWI["nadproze_m"]), float(EWI["osciez_m"])     # 0,55 / 3,00 / 0,45
WIN_W = float(EWI["okno_m"][0])                                                                   # 1,65
KW = 1.10                                                    # kwatera stała do +1,10 nad posadzką (WT § 301)
ZIP = 0.18                                                   # kaseta ZIP nad nadprożem (do +3,18 ≤ spód stropu +3,32)
U_W = float(K["elewacje"]["U_scian"]["wieza"])               # 0,147
_m = re.search(r"wełna\s+(\d+)", K["elewacje"]["U_scian"].get("opis", ""))
WOOL = (int(_m.group(1)) if _m else 260) / 1000.0            # 0,26
DACH = {b["id"]: b for b in K["bryly"]}["W"]["dach"]
Z_ROOF, Z_ROOF_MAX, Z_ATT = (float(DACH["najnizszy_pkt_pokrycia"]["wzgl"]), float(DACH["najwyzszy_pkt_pokrycia"]["wzgl"]),
                             float(DACH["attyka"]["wzgl"]))  # +36,20 / +36,45 / +37,20
Z_SUF = float(KOND["S"]["dach"]["rusz_spod"])                # +34,15
Z_KORD = float(K["elewacje"]["skrzydlo"]["linie"]["attyka_npm"]) - Z0          # kordon do +20,85 (= gzyms skrzydła 140,15)
Z6_0 = float(KOND["5"]["strop_nad"]["wierzch"])             # +23,40 – początek cofnięcia kond. 6
Z6_1 = float(KOND["6"]["strop_nad"]["spod_wieza"])          # +26,87 – spód stropu S (podniebienie wnęki)
# układ warstw ściany od lica (X = 0, lico filarów = obrys; X < 0 do wnętrza)
X_CL, X_CAV = 0.04, 0.08                                     # okładzina 40 / pustka 40
X_INS = X_CAV + WOOL                                         # wełna 260 → −0,34
X_RC = X_INS + 0.20                                          # żelbet płyciny 200 → −0,54
REC6 = 0.40                                                  # kond. 6: szkło i metal 0,40 m za licem filarów
X6_INS, X6_RC = REC6 + 0.04 + WOOL, REC6 + 0.04 + WOOL + 0.20


def fz(z):
    return ("+" if z >= 0 else "−") + f"{abs(z):.2f}".replace(".", ",")


# ------------------------------------------------------------------ wariant „skrzydło” (UMWD_FRAG=skrzydlo)
FRAG = os.environ.get("UMWD_FRAG", "").strip().lower()


def przekroj_skrzydla():
    """Przekrój elewacyjny 1:50 skrzydła (v1.1; rozdz. 8 – porządek kamieniczny, tabela przegród; P7 „wieża i skrzydło”).
    A – przekrój przez oś okna M1 od ul. Mazowieckiej, kond. 4 i zwieńczenie: ceramika 40 / pustka 40 / wełna 240 λ 0,031 /
        żelbet 150 = 0,47 m (U 0,144); okno 1,20 × 2,35 nad parapetem 0,60, kwatera stała do 0,90, pochwyt 1,10, nadproże
        2,95, kaseta ZIP do 3,13, ościeże 0,35 z blachy Al; gzyms-attyka granitowy 0,70 m (139,45–140,15) bez wysięgu
        (lico na granicy obszaru) z fryzem wklęsłym 0,15 m;
    B – fragment elewacji od ulicy na styku posesji M1 | M2 (fuga 0,20 m, relief M2 0,08 m, ceramika ryflowana co 0,135 m);
    C – detal zwieńczenia od dziedzińca: tynk mineralny cienkowarstwowy na wełnie (rozdz. 8, materiały), gzyms z wysięgiem 0,30 m.
    Dane: koncepcja.json `elewacje.skrzydlo`, `elewacje.U_scian`, `elewacje.materialy`, `kondygnacje`, `bryly.M.dach`."""
    sys.path.insert(0, str(ROOT / "tools"))
    import elewacje as EL                     # odcienie ceramiki i tynku jak w elewacjach 1:200
    ESK = K["elewacje"]["skrzydlo"]
    LIN, GZ = ESK["linie"], ESK["gzyms"]
    Z_GZ0, Z_GZ1 = LIN["spod_gzymsu_npm"] - Z0, LIN["attyka_npm"] - Z0             # +20,15 / +20,85
    FRYZ, WYS_GR, WYS_DZ = float(GZ["fryz_wklesly_m"]), float(GZ["wysieg_lica_przy_granicy_m"]), float(GZ["wysieg_dziedziniec_m"])
    Z_FR0 = Z_GZ0 - FRYZ                                                            # fryz 139,30–139,45
    WIN_S = tuple(float(x) for x in ESK["okno_m"])                                  # 1,20 × 2,35
    PAR_S, KW_S, NADPR_S, OSC_S = (float(ESK[k]) for k in ("parapet_m", "kwatera_stala_do_m", "nadproze_m", "osciez_m"))
    OS_S, FIL_S = float(ESK["os_m"]), float(ESK["filar_m"])                         # 2,025 / 0,825
    REL = {k: float(v) for k, v in ESK["relief_filarow_m"].items()}
    POCHWYT = 1.10                                           # pochwyt ochronny w świetle ościeży (rozdz. 8, WT § 301)
    ZIP_S = 0.18                                             # kaseta ZIP: nadproże 2,95 → 3,13 (E-I-5)
    F3, F4 = float(KOND["3"]["posadzka_wzgl"]), float(KOND["4"]["posadzka_wzgl"])
    ST3, SB3 = float(KOND["3"]["strop_nad"]["wierzch"]), float(KOND["3"]["strop_nad"]["spod_skrzydlo"])   # +15,90 / +15,50
    FLOOR_S = round(F4 - ST3, 3)                                                    # podłoga 0,15
    S4 = KOND["4"]["strop_nad"]
    Z_DS, Z_DW = float(S4["dach_skrzydla_spod"]), float(S4["dach_skrzydla_wierzch"])    # +19,40 / +19,80
    DM = {b["id"]: b for b in K["bryly"]}["M"]["dach"]
    Z_PK0, Z_PK1 = float(DM["najnizszy_pkt_pokrycia"]["wzgl"]), float(DM["najwyzszy_pkt_pokrycia"]["wzgl"])   # +20,20 / +20,40
    U_S = float(K["elewacje"]["U_scian"]["skrzydlo_segment"])                       # 0,144
    m = re.search(r"/\s*(\d+)\s*λ\s*(\d+[,.]\d+)\s*\(skrzydło\)", K["elewacje"]["U_scian"].get("opis", ""))
    WOOL_S, LAM_S = ((int(m.group(1)) / 1000.0, m.group(2).replace(".", ",")) if m else (0.24, "0,031"))
    # warstwy od lica (X = 0 = lico filarów = obrys; X < 0 do wnętrza)
    XCL, XCV = 0.04, 0.08                                     # ceramika 40 / pustka 40
    XI = XCV + WOOL_S                                       # wełna 240 → −0,32
    XR = XI + 0.15                                          # żelbet 150 → −0,47 (razem 0,47 m – trakt 15,00)
    if abs(XR - 0.47) > 0.005:
        print(f"  [przekroj_elewacyjny] uwaga: ściana skrzydła {XR:.3f} m ≠ 0,47 m (rozdz. 6/8)", file=sys.stderr)
    T_D, XI_D = 0.01, 0.01 + WOOL_S                         # od dziedzińca: tynk 10 na wełnie 240 / żelbet 150
    XR_D = XI_D + 0.15
    C_M1, C_M2 = EL.col(EL.NCS_C["M1"]), EL.col(EL.NCS_C["M2"])
    C_TY = EL.tynk(C_M1)
    SEP = 0.135                                              # ryflowanie M2 co 0,135 m
    SLOPE = (Z_PK1 - Z_PK0) / (15.0 / 2 - XR)                # spadek pokrycia od kalenicy w osi traktu 15,00 m

    ZB_S, ZT_S, ZD0 = 14.95, 21.35, 19.25                    # zakres A i B; C od +19,25 (nad kasetą ZIP)
    W_S = 490.0
    OY_S = 40.0 + (ZT_S - ZB_S) * SC
    H_S = OY_S + 38.0
    s = Svg(W_S, H_S)
    OXA, XA_IN = 140.0, -3.0                                 # A: lico w x = 140 mm, przerwanie wnętrza 3,0 m
    EXA = 2.35                                               # B: początek fragmentu 2,35 m za licem A
    OXC, XC_IN = 326.0, -1.9                                 # C: lico w x = 326 mm
    LX = 362.0

    def PA(X, Z):
        return (OXA + X * SC, OY_S - (Z - ZB_S) * SC)

    def PC(X, Z):
        return (OXC + X * SC, OY_S - (Z - ZB_S) * SC)

    def E(u, z):
        return (OXA + (EXA + u) * SC, OY_S - (z - ZB_S) * SC)

    def R(P, x0, z0, x1, z1, fill="none", stroke=INK, sw=0.18, extra=""):
        s.poly([P(x0, z0), P(x1, z0), P(x1, z1), P(x0, z1)], fill=fill, stroke=stroke, sw=sw, extra=extra)

    hc = s.hatch("beton", spacing=0.9, angle=45, stroke="#9c978f", sw=0.08, bg=CONC)
    hg = s.hatch("granit", spacing=0.6, angle=-30, stroke=GRAN_H, sw=0.08, bg=GRAN)
    hi = s.hatch("welna", spacing=0.7, angle=90, stroke="#d9cfa9", sw=0.1, bg=INS)
    hk = s.hatch("ceramika", spacing=0.45, angle=0, stroke="#b8a48c", sw=0.07, bg=C_M1)
    calls = []

    def call(P, n, X, Z, dx=0.0):
        calls.append((P, n, X, Z, dx))

    def okno(P, zs, zh, x_out, fixed_to=None, kap=-0.004):
        """Okno Al: rama X = x_out … x_out − 0,10; parapet zewn. Al ze spadkiem i kapinosem w X = kap; kaseta ZIP nad nadprożem."""
        R(P, x_out - 0.10, zs, x_out, zs + 0.08, MET, MET)
        R(P, x_out - 0.10, zh - 0.08, x_out, zh, MET, MET)
        for dx in (-0.025, -0.05, -0.075):
            s.line(P(x_out + dx, zs + 0.08), P(x_out + dx, zh - 0.08), stroke=GLASS, sw=0.22)
        if fixed_to:
            R(P, x_out - 0.10, fixed_to - 0.04, x_out, fixed_to + 0.04, MET, MET)
        s.poly([P(kap, zs - 0.035), P(x_out, zs + 0.015), P(x_out, zs - 0.015), P(kap, zs - 0.065)], fill=MET, stroke=MET, sw=0.1)
        R(P, kap - 0.008, zs - 0.10, kap, zs - 0.035, MET, MET, sw=0.08)
        R(P, x_out - 0.30, zs, x_out - 0.10, zs + 0.03, "#cfc8bc", sw=0.08)
        R(P, x_out - 0.12, zh, x_out + 0.015, zh + ZIP_S, hi, sw=0.08)                   # wełna nad ramą (za kasetą)
        R(P, x_out + 0.015, zh, x_out + 0.165, zh + ZIP_S, "#6b645e", INK, sw=0.1)
        R(P, x_out, zh - 0.012, 0.0, zh, MET, MET, sw=0.08)

    def osciez(P, z0, z1, x_out):
        R(P, x_out, z0, 0.0, z1, MET_V, "#6b645e", sw=0.1, extra='fill-opacity="0.38"')
        s.line(P(0.0, z0), P(0.0, z1), stroke="#6b645e", sw=0.14)

    def konsole(P, x_in, x_out, zs):
        for z in zs:
            s.line(P(x_in, z), P(x_out, z), stroke="#6b645e", sw=0.3)

    def strop(P, x_in, zb, zt, x_edge, podloga=None):
        R(P, x_in, zb, x_edge, zt, hc, sw=0.25)
        for q in range(1, 30):                                   # rury TABS
            x = x_in + q * 0.18
            if x < x_edge - 0.12:
                s.circle(P(x, zb + 0.08), 0.35, fill="none", stroke="#a8483a", sw=0.08)
        if podloga:
            x_pp, zf = podloga
            R(P, x_in, zt, x_pp, zf, "#ffffff", sw=0.12)
            for q in range(1, 12):
                x = x_in + q * 0.35
                if x < x_pp - 0.05:
                    s.line(P(x, zt), P(x, zf - 0.03), stroke="#8a857e", sw=0.08)

    def dach(P, x_in, x_rc, ups=0.10):
        """Dach skrzydła od wewnętrznego lica attyki (X = −x_rc) do przerwania: paroizolacja, wełna w spadku, membrana, BIPV."""
        z_ins0 = Z_PK0 - 0.10                                   # wierzch wełny przy attyce (pokrycie +20,20 na licu attyki)
        zi = lambda x: z_ins0 + SLOPE * (-x_rc - x)
        s.line(P(x_in, Z_DW + 0.008), P(-x_rc, Z_DW + 0.008), stroke=INK, sw=0.18)
        s.poly([P(x_in, Z_DW + 0.015), P(-x_rc - ups, Z_DW + 0.015), P(-x_rc - ups, zi(-x_rc - ups)), P(x_in, zi(x_in))], fill=hi, stroke=INK, sw=0.15)
        R(P, -x_rc - ups, Z_DW + 0.015, -x_rc, Z_GZ1 - 0.12, hi, sw=0.12)                 # wełna na wewn. licu attyki
        s.poly([P(x_in, zi(x_in) + 0.006), P(-x_rc - ups - 0.006, zi(-x_rc - ups) + 0.006), P(-x_rc - ups - 0.006, Z_GZ1 - 0.12)],
               fill="none", stroke=INK, sw=0.3, close=False)                                          # membrana wywinięta pod czapę
        x = x_in + 0.05
        while x < -x_rc - ups - 0.75:                            # moduły BIPV szkło-szkło na ruszcie
            xa, xb = x, x + 0.62
            s.poly([P(xa, zi(xa) + 0.07), P(xb, zi(xb) + 0.07), P(xb, zi(xb) + 0.10), P(xa, zi(xa) + 0.10)], fill="#2e3a48", stroke=INK, sw=0.08)
            for xx in (xa + 0.08, xb - 0.08):
                s.line(P(xx, zi(xx) + 0.01), P(xx, zi(xx) + 0.07), stroke="#6b645e", sw=0.12)
            x += 0.70

    def czapa(P, x_front, x_back):
        """Czapa granitowa gzymsu-attyki (wierzch 140,15 w licu, spadek do dachu) i obróbka Al membrany pod nią."""
        s.poly([P(x_front, Z_GZ1 - 0.12), P(x_back, Z_GZ1 - 0.12), P(x_back, Z_GZ1 - 0.06), P(x_front, Z_GZ1)], fill=hg, stroke=INK, sw=0.2)
        R(P, x_back, Z_GZ1 - 0.42, x_back + 0.006, Z_GZ1 - 0.10, MET, MET, sw=0.08)

    # ============================================================== A: przekrój od ul. Mazowieckiej (oś okna M1, relief 0,00)
    a0 = len(s.parts)
    P = PA
    zs3, zh3 = F3 + PAR_S, F3 + NADPR_S
    zs4, zh4 = F4 + PAR_S, F4 + NADPR_S
    strop(P, XA_IN, SB3, ST3, -XI, podloga=(-(XR + 0.16), F4))       # strop nad kond. 3 (0,40) + podłoga 0,15
    strop(P, XA_IN, Z_DS, Z_DW, -XI)                                  # strop dachu (0,40)
    R(P, -XR, zh3 + ZIP_S, -XI, SB3, hc, sw=0.2)                       # nadproże kond. 3
    R(P, -XR, ST3, -XI, zs4, hc, sw=0.2)                               # ściana podokienna kond. 4
    R(P, -XR, zh4 + ZIP_S, -XI, Z_DS, hc, sw=0.2)                      # nadproże kond. 4
    R(P, -XR, Z_DW, -XI, Z_GZ1 - 0.12, hc, sw=0.2)                     # attyka żelbetowa
    okno(P, zs3, zh3, -OSC_S, fixed_to=F3 + KW_S)
    osciez(P, zs3, zh3, -OSC_S)
    for z0, z1 in ((zh3, zs4), (zh4, Z_FR0)):                           # pasy w licu: ceramika 40 / pustka / wełna 240
        R(P, -XCL, z0, 0.0, z1, hk, sw=0.15)
        R(P, -XI, z0, -XCV, z1, hi, sw=0.12)
    konsole(P, -XI, -XCL, (zh3 + 0.35, zs4 - 0.25, zh4 + 0.45))
    okno(P, zs4, zh4, -OSC_S, fixed_to=F4 + KW_S)
    osciez(P, zs4, zh4, -OSC_S)
    s.circle(P(-0.18, F4 + POCHWYT), 0.45, fill=MET, stroke=INK, sw=0.08)                  # pochwyt Ø 40 w świetle ościeży
    # fryz wklęsły 0,15 m pod gzymsem (lico bez wysięgu): tło z blachy Al, zamknięcie okładziny i podniebienie granitu
    R(P, -XI, Z_FR0, -(FRYZ + 0.006), Z_GZ0, hi, sw=0.12)
    R(P, -(FRYZ + 0.006), Z_FR0, -FRYZ, Z_GZ0, MET, MET, sw=0.08)
    R(P, -FRYZ, Z_FR0 - 0.006, 0.0, Z_FR0, MET, MET, sw=0.08)
    R(P, -FRYZ, Z_GZ0, 0.0, Z_GZ0 + 0.03, hg, sw=0.15)
    # gzyms-attyka: granit 40 w licu (0,70 m z czapą), pustka, wełna, attyka żelbetowa
    R(P, -XCL, Z_GZ0 + 0.03, 0.0, Z_GZ1 - 0.12, hg, sw=0.2)
    R(P, -XI, Z_GZ0, -XCV, Z_GZ1 - 0.12, hi, sw=0.12)
    konsole(P, -XI, -XCL, (Z_GZ0 + 0.15, Z_GZ1 - 0.25))
    dach(P, XA_IN, XR)
    czapa(P, 0.0, -(XR + 0.11))
    s.line(P(XA_IN, ZB_S), P(XA_IN, ZT_S - 0.2), stroke=INK, sw=0.15, dash="1.5,0.8")
    a1 = len(s.parts)
    call(P, 1, -0.02, zh4 + 0.55, 0.75)
    call(P, 2, -0.20, zh3 + 0.55, 0.75)
    call(P, 3, -0.40, ST3 + 0.30, 1.45)
    call(P, 4, -OSC_S - 0.05, F4 + 2.0, 1.45)
    call(P, 5, -OSC_S - 0.05, F4 + KW_S, 0.75)
    call(P, 6, -OSC_S + 0.09, zh4 + 0.09, 1.45)
    call(P, 7, -0.18, F4 + POCHWYT, 1.45)
    call(P, 8, -OSC_S / 2, F4 + 1.55, 0.75)
    call(P, 9, -0.02, Z_GZ0 + 0.40, 0.75)
    call(P, 10, -FRYZ / 2, Z_FR0 + FRYZ / 2, 1.45)
    call(P, 11, -0.004, zs4 - 0.05, 1.45)
    call(P, 12, -1.55, SB3 + 0.20, -0.0)
    call(P, 13, -2.25, ST3 + 0.08, -0.0)
    call(P, 14, -1.45, Z_DW + 0.25, -0.0)
    # łańcuch wysokości okna od posadzki kond. 4 (po stronie wnętrza)
    xc = XA_IN + 0.40
    ticks = [(F4, ""), (zs4, "0,60 parapet"), (F4 + KW_S, "0,90 kwatera stała"), (F4 + POCHWYT, "1,10 pochwyt"),
             (zh4, "2,95 nadproże"), (zh4 + ZIP_S, "3,13 kaseta ZIP"), (Z_DS, f"{Z_DS - F4:.2f} spód stropu dachu".replace(".", ","))]
    s.line(P(xc, F4), P(xc, Z_DS), stroke=INK, sw=0.12)
    for z, lab in ticks:
        x, y = P(xc, z)
        s.line((x - 0.8, y + 0.8), (x + 0.8, y - 0.8), stroke=INK, sw=0.22)
        if lab:
            s.text((x + 1.6, y + (2.2 if z >= Z_DS - 0.01 else 0.7)), lab, size=1.75, fill="#2f2b28")
    x, y = P(XA_IN + 0.25, SB3 - 0.17)
    s.text((x, y), f"kond. 1–3: ZIP {NADPR_S + ZIP_S:.2f} < spód stropu {SB3 - F3:.2f}".replace(".", ","), size=1.6, fill="#2f2b28")

    # ============================================================== B: fragment elewacji od ulicy – styk posesji M1 | M2
    b0 = len(s.parts)
    UF, UE = OS_S, 2 * OS_S                                  # fuga posesji w osi filara; koniec fragmentu
    c1, c2 = UF - OS_S / 2, UF + OS_S / 2                    # osie okien M1 i M2
    hw = WIN_S[0] / 2
    rel2 = REL.get("M2", 0.08)

    def erect(u0, z0, u1, z1, fill, stroke=INK, sw=0.15, extra=""):
        s.poly([E(u0, z0), E(u1, z0), E(u1, z1), E(u0, z1)], fill=fill, stroke=stroke, sw=sw, extra=extra)

    def ewin(a, b, z0, z1):
        erect(a, z0, b, z1, "#7b8792", sw=0.12)
        erect(a, z0 + KW_S - PAR_S - 0.03, b, z0 + KW_S - PAR_S + 0.03, MET, stroke="none")          # poprzeczka kwatery stałej
        s.line(E(a, z0 + POCHWYT - PAR_S), E(b, z0 + POCHWYT - PAR_S), stroke="#9a948c", sw=0.3)      # pochwyt 1,10
        sh = min(OSC_S * 0.75, (z1 - z0) * 0.3)
        erect(a, z1 - sh, b, z1, INK, stroke="none", extra='fill-opacity="0.32"')
        erect(a, z0, a + OSC_S * 0.6, z1 - sh, INK, stroke="none", extra='fill-opacity="0.24"')
        erect(a - 0.02, z0 - 0.05, b + 0.02, z0, MET, stroke="none")                                 # parapet Al w licu

    erect(0, ZB_S, UF, Z_FR0, C_M1, stroke="none")
    erect(UF, ZB_S, UE, Z_FR0, C_M2, stroke="none")
    q = UF + SEP / 2
    while q < UE:                                            # M2: ceramika ryflowana co 0,135 m
        s.line(E(q, ZB_S), E(q, Z_FR0), stroke=EL.mix(C_M2, INK, 0.16), sw=0.07)
        q += SEP
    erect(c2 - hw, ZB_S, c2 + hw, Z_FR0, INK, stroke="none", extra=f'fill-opacity="{0.035 + rel2 * 0.25:.3f}"')   # relief M2
    erect(c2 - hw, ZB_S, c2 - hw + rel2 * 0.9, Z_FR0, INK, stroke="none", extra='fill-opacity="0.13"')
    for c in (c1, c2):
        ewin(c - hw, c + hw, zs3, zh3)
        ewin(c - hw, c + hw, zs4, zh4)
    erect(UF - 0.10, ZB_S, UF + 0.10, Z_FR0, MET, stroke="none")                                      # fuga 0,20 (cofnięta 0,15)
    erect(UF - 0.10, ZB_S, UF - 0.10 + 0.15 * 0.6, Z_FR0, INK, stroke="none", extra='fill-opacity="0.35"')
    erect(0, Z_FR0, UE, Z_GZ0, MET, stroke=INK, sw=0.1)                                               # fryz wklęsły 0,15 (tło Al
    erect(0, Z_FR0, UE, Z_GZ0, INK, stroke="none", extra='fill-opacity="0.45"')                       #  w cieniu gzymsu)
    erect(0, Z_GZ0, UE, Z_GZ1, EL.G, sw=0.18)                                                         # gzyms-attyka 0,70
    s.line(E(0, Z_GZ1 - 0.12), E(UE, Z_GZ1 - 0.12), stroke=GRAN_H, sw=0.12)
    for u in (OS_S / 2, OS_S, 1.5 * OS_S):
        s.line(E(u, Z_GZ0), E(u, Z_GZ1 - 0.12), stroke=GRAN_H, sw=0.12)
    erect(0, ZB_S, UE, Z_GZ1, "none", sw=0.2)
    b1 = len(s.parts)

    # ============================================================== C: detal zwieńczenia od dziedzińca (tynk, wysięg 0,30)
    c0_ = len(s.parts)
    P = PC
    strop(P, XC_IN, Z_DS, Z_DW, -XI_D)
    R(P, -XR_D, ZD0 - 0.5, -XI_D, Z_DS, hc, sw=0.2)                    # nadproże
    R(P, -XR_D, Z_DW, -XI_D, Z_GZ1 - 0.12, hc, sw=0.2)                 # attyka żelbetowa
    R(P, -XI_D, ZD0 - 0.5, -T_D, Z_GZ1 - 0.12, hi, sw=0.12)            # wełna 240 (ETICS)
    R(P, -T_D, ZD0 - 0.5, 0.0, Z_GZ0, C_TY, INK, sw=0.12)               # tynk mineralny 10
    # gzyms granitowy z wysięgiem 0,30 m: płyta czołowa i podniebienie z kapinosem na konsolach nierdzewnych
    R(P, WYS_DZ - 0.04, Z_GZ0 + 0.04, WYS_DZ, Z_GZ1 - 0.12, hg, sw=0.2)
    R(P, 0.0, Z_GZ0, WYS_DZ, Z_GZ0 + 0.04, hg, sw=0.2)
    R(P, WYS_DZ - 0.075, Z_GZ0, WYS_DZ - 0.06, Z_GZ0 + 0.015, "#ffffff", "#ffffff", sw=0.02)       # kapinos (wrąb)
    R(P, -T_D, Z_GZ0, 0.0, Z_GZ1 - 0.12, hi, sw=0.08)
    konsole(P, -XI_D, WYS_DZ - 0.04, (Z_GZ0 + 0.10, Z_GZ1 - 0.22))
    s.line(P(WYS_DZ - 0.06, Z_GZ0 + 0.04), P(WYS_DZ - 0.06, Z_GZ1 - 0.12), stroke="#6b645e", sw=0.3)
    dach(P, XC_IN, XR_D)
    czapa(P, WYS_DZ, -(XR_D + 0.11))
    s.line(P(XC_IN, ZD0), P(XC_IN, ZT_S - 0.2), stroke=INK, sw=0.15, dash="1.5,0.8")
    c1_ = len(s.parts)
    call(P, 15, -T_D / 2, ZD0 + 0.35, 1.0)
    call(P, 16, WYS_DZ - 0.02, Z_GZ0 + 0.40, 0.7)
    call(P, 17, WYS_DZ - 0.07, Z_GZ0 + 0.005, 0.7)

    # ---- przycięcie: A i B do +ZB, C do +ZD0 (bez resztek poniżej linii urwania)
    yA, yC = OY_S + 0.2, PC(0, ZD0)[1] + 0.2
    s.defs.append(f'<clipPath id="nad_zb_s"><rect x="0" y="0" width="{W_S:.3f}" height="{yA:.3f}"/></clipPath>')
    s.defs.append(f'<clipPath id="nad_zd"><rect x="{PC(XC_IN, 0)[0]:.3f}" y="0" width="{W_S:.3f}" height="{yC:.3f}"/></clipPath>')
    parts = s.parts
    s.parts = (parts[:a0] + ['<g clip-path="url(#nad_zb_s)">'] + parts[a0:b1] + ['</g>']
               + ['<g clip-path="url(#nad_zd)">'] + parts[c0_:c1_] + ['</g>'] + parts[c1_:])
    for P_, x0, x1, z in ((PA, XA_IN - 0.1, 0.4, ZB_S), (PC, XC_IN - 0.1, WYS_DZ + 0.3, ZD0)):
        s.line(P_(x0, z + 0.01), P_(x1, z + 0.01), stroke=INK, sw=0.15, dash="1.5,0.8")
    s.line(E(-0.15, ZB_S + 0.01), E(UE + 0.15, ZB_S + 0.01), stroke=INK, sw=0.15, dash="1.5,0.8")

    # ---- rzędne (z lewej strony A)
    for z, lab in ((Z_GZ1, f"{fz(Z_GZ1)} gzyms-attyka = {Z_GZ1 + Z0:.2f}".replace(".", ",")),
                   (Z_GZ0, f"{fz(Z_GZ0)} spód gzymsu = {Z_GZ0 + Z0:.2f}".replace(".", ",")),
                   (Z_DW, f"{fz(Z_DW)} strop dachu skrzydła"), (F4, f"{fz(F4)} posadzka 4 = {F4 + Z0:.2f}".replace(".", ","))):
        x, y = PA(XA_IN - 0.4, z)
        s.poly([(x, y), (x - 1.3, y - 1.5), (x + 1.3, y - 1.5)], fill=INK, stroke="none")
        s.line((x - 2.5, y), (x + 4, y), stroke=INK, sw=0.12)
        s.text((x - 3, y - 0.4), lab, size=2.1, anchor="end")

    # ---- odnośniki
    for P_, n, X, Z, dx in calls:
        x, y = P_(X, Z)
        bx = x + dx * SC
        if dx:
            s.line((x, y), (bx, y), stroke=INK, sw=0.12)
        cx = bx + (2.2 if dx > 0 else -2.2 if dx < 0 else 0)
        s.circle((cx, y), 2.2, fill="#ffffff", stroke="#a8483a", sw=0.25)
        s.text((cx, y + 0.8), str(n), size=2.2, anchor="middle", weight=700, fill="#a8483a")

    # ---- wymiary pod fragmentem B
    yd = OY_S + 6.5
    edges = [0.0, c1 - hw, c1 + hw, c2 - hw, c2 + hw, UE]
    for i, (u0, u1) in enumerate(zip(edges[:-1], edges[1:])):
        x0, x1 = E(u0, 0)[0], E(u1, 0)[0]
        s.line((x0, yd), (x1, yd), stroke=INK, sw=0.12)
        for x in (x0, x1):
            s.line((x - 0.8, yd + 0.8), (x + 0.8, yd - 0.8), stroke=INK, sw=0.2)
        t = {1: f"{WIN_S[0]:.2f}", 2: f"{FIL_S:.3f}", 3: f"{WIN_S[0]:.2f}"}.get(i, "")
        if t:
            s.text(((x0 + x1) / 2, yd - 1.0), t.replace(".", ","), size=1.9, anchor="middle")
    x0, x1 = E(c1, 0)[0], E(c2, 0)[0]
    s.line((x0, yd + 4.5), (x1, yd + 4.5), stroke=INK, sw=0.12)
    for x in (x0, x1):
        s.line((x - 0.8, yd + 5.3), (x + 0.8, yd + 3.7), stroke=INK, sw=0.2)
    s.text(((x0 + x1) / 2, yd + 3.6), f"oś {OS_S:.3f} (1,5 modułu 1,35)".replace(".", ",", 1), size=1.9, anchor="middle")
    s.text((E(c1, 0)[0], yd + 9.5), f"M1 · {EL.NCS_C['M1']} · gładka · relief {REL.get('M1', 0.0):.2f}".replace(".", ","),
           size=1.8, anchor="middle", fill="#4d4842")
    s.text((E(c2, 0)[0], yd + 9.5), f"M2 · {EL.NCS_C['M2']} · ryflowana co {SEP:.3f} · relief {rel2:.2f}".replace(".", ","),
           size=1.8, anchor="middle", fill="#4d4842")
    s.text((E(UF, 0)[0], yd + 13.0), "fuga posesji 0,20 m z ciemnego metalu cofnięta 0,15 m · gzyms i fryz wspólne", size=1.8, anchor="middle", fill="#4d4842")

    # ---- tytuły kolumn
    for xy, t in (((PA(-1.3, 0)[0], PA(0, ZT_S)[1] - 2), "A · PRZEKRÓJ PRZEZ OŚ OKNA – UL. MAZOWIECKA"),
                  ((E(UE / 2, 0)[0], PA(0, ZT_S)[1] - 2), "B · FRAGMENT ELEWACJI – STYK POSESJI M1 | M2"),
                  ((PC(-0.6, 0)[0], PA(0, ZT_S)[1] - 2), "C · ZWIEŃCZENIE OD DZIEDZIŃCA")):
        s.text(xy, t, size=2.4, anchor="middle", weight=600)

    # ---- legenda warstw (rozdz. 8, tabela przegród 1:50 – „Ściana skrzydła i segmentu”)
    u_txt = f"{U_S:.3f}".replace(".", ",")
    w_mm = int(round(WOOL_S * 1000))
    LEG = [
        f"1  ceramika glazurowana półmatowa, profile ekstrudowane 40 mm (A1), odcień posesji – M1 {EL.NCS_C['M1']}",
        f"2  pustka wentylowana 40 / wełna mineralna λ {LAM_S} – {w_mm} mm; konsole nierdzewne punktowe",
        f"    z przekładką (ΔU 0,020) → U = {u_txt} W/(m²K); całość A1 (NRO)",
        f"3  ściana żelbetowa 150; ściana razem {XR:.2f} m – trakt 15,00 = 2 × {XR:.2f} + 2 × 6,08 + 2 × 0,10 + 1,70".replace(".", ","),
        f"4  okno Al {WIN_S[0]:.2f} × {WIN_S[1]:.2f} m, pakiet 3-szybowy 54 mm, Uw ≤ 0,80, g = 0,33; parapet {PAR_S:.2f}, nadproże {NADPR_S:.2f}".replace(".", ","),
        f"5  dolna kwatera stała ze szkła bezpiecznego do {KW_S:.2f} m nad posadzką (WT § 301)".replace(".", ","),
        f"6  kaseta rolety ZIP w nadprożu do {NADPR_S + ZIP_S:.2f} m (kond. 1–3 spód stropu {SB3 - F3:.2f}; kond. 4 – {Z_DS - F4:.2f}),".replace(".", ","),
        "    tkanina poliestrowa (≤ 25 m)",
        f"7  pochwyt ochronny ze stali nierdzewnej Ø 40 na {POCHWYT:.2f} m w świetle ościeży".replace(".", ","),
        f"8  ościeże {OSC_S:.2f} m: blacha Al lakierowana proszkowo RAL 8019 na wełnie".replace(".", ","),
        f"9  gzyms-attyka: granit strzegomski płomieniowany {EL.MAT['G']['NCS']}, {Z_GZ1 - Z_GZ0:.2f} m ({Z_GZ0 + Z0:.2f}–{Z_GZ1 + Z0:.2f}),".replace(".", ","),
        "    czapa granitowa ze spadkiem do dachu; w linii attyki Mazowieckiej 19 (140,24)",
        f"10 lico na granicy obszaru (ul. Mazowiecka, skwer, Maz. 19): wysięg {WYS_GR:.2f} – cień daje".replace(".", ","),
        f"    fryz wklęsły {FRYZ:.2f} m pod gzymsem ({Z_FR0 + Z0:.2f}–{Z_GZ0 + Z0:.2f}), tło z blachy Al RAL 8019".replace(".", ","),
        "11 parapet zewnętrzny Al ze spadkiem, kapinos w licu – nic poza obrysem (G-K-1)",
        "12 strop sprężony 400 (14,20 m bez słupów) z aktywacją termiczną (TABS), sufit odsłonięty + wyspy",
        f"13 podłoga podniesiona {FLOOR_S * 1000:.0f} (instalacje); biura {K['wysokosci_w_swietle']['biura_skrzydlo']:.2f} m w świetle".replace(".", ","),
        "14 dach: BIPV szkło-szkło BROOF(t1) / membrana / spadki / wełna mineralna 300 / paroizolacja /",
        f"    płyta; U ≤ 0,12; pokrycie {fz(Z_PK0)}…{fz(Z_PK1)} ({Z_PK0 + Z0:.2f}–{Z_PK1 + Z0:.2f}) za gzymsem-attyką".replace(".", ","),
        f"15 od dziedzińca: tynk mineralny cienkowarstwowy 10 mm na wełnie {w_mm} λ {LAM_S} (A2-s1,d0)",
        "    w tonie ceramiki posesji / żelbet 150",
        f"16 gzyms od dziedzińca: wysięg {WYS_DZ:.2f} m – granit na konsolach nierdzewnych, cień rzucany".replace(".", ","),
        "17 kapinos (wrąb) w podniebieniu gzymsu",
    ]
    s.text((LX, 34), "WARSTWY (od zewnątrz)", size=2.4, weight=600)
    for i, t in enumerate(LEG):
        t = (" " * 6 + t.lstrip()) if t.startswith("    ") else t
        s.text((LX, 40 + i * 3.45), t, size=1.85, fill="#2f2b28")
    s.text((20.0, 12.0), "PRZEKRÓJ ELEWACYJNY I FRAGMENT ELEWACJI – SKRZYDŁO", size=4.4, weight=600)
    s.text((20.0, 18.0), "porządek kamieniczny: kond. 4 i zwieńczenie od ul. Mazowieckiej (wysięg 0,00, fryz wklęsły) "
                         "i od dziedzińca (wysięg 0,30, tynk) · 1:50", size=2.4, fill="#4d4842")
    sx, sy = 20.0, H_S - 8
    for i in range(4):
        s.poly([(sx + i * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy + 1.2), (sx + i * 0.5 * SC, sy + 1.2)],
               fill=INK if i % 2 == 0 else "#fff", stroke=INK, sw=0.12)
    s.text((sx + 2 * SC + 4, sy + 1.2), "0–2 m · 1:50", size=2.2, weight=600)

    out = ROOT / "build" / "rysunki" / "przekroj_elewacyjny_skrzydlo_1-50.svg"
    out.write_text(s.render(), encoding="utf-8")
    html = ROOT / "docs" / "70_rysunki" / "podglady" / "przekroj_elewacyjny_skrzydlo_1-50.html"
    html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{W_S + 10:.0f}mm {H_S + 10:.0f}mm;margin:0}}'
                    f'body{{margin:0;padding:5mm}}</style></head><body>{s.render()}</body></html>', encoding="utf-8")
    print(f"{W_S + 10:.0f} {H_S + 10:.0f}")


if FRAG in ("skrzydlo", "skrzydło"):
    przekroj_skrzydla()
    raise SystemExit(0)


W_MM, H_MM = 480.0, (ZT - ZB) * SC + 60
svg = Svg(W_MM, H_MM)
OX, OY = 178.0, 30.0 + (ZT - ZB) * SC        # section: façade plane X=0 at paper x=OX


def P(X, Z):
    return (OX + X * SC, OY - (Z - ZB) * SC)


def rect(x0, z0, x1, z1, fill="none", stroke=INK, sw=0.18, extra=""):
    svg.poly([P(x0, z0), P(x1, z0), P(x1, z1), P(x0, z1)], fill=fill, stroke=stroke, sw=sw, extra=extra)


hc = svg.hatch("beton", spacing=0.9, angle=45, stroke="#9c978f", sw=0.08, bg=CONC)
hg = svg.hatch("granit", spacing=0.6, angle=-30, stroke=GRAN_H, sw=0.08, bg=GRAN)
hi = svg.hatch("welna", spacing=0.7, angle=90, stroke="#d9cfa9", sw=0.1, bg=INS)

X_IN = -4.6        # interior break line
callouts = []


def call(n, X, Z, dx=0.0):
    callouts.append((n, X, Z, dx))


# ------------------------------------------------------------------ stropy
for zf in (F5, F6, FS):
    st, sb = zf - FLOOR, zf - FLOOR - SLAB
    x_pp = -((X6_RC if zf == F6 else X_RC) + 0.16)                    # podłoga kończy się 0,16 m przed attyką podokienną
    rect(X_IN, sb, -X_INS, st, fill=hc, sw=0.25)                       # strop sprężony 280 (TABS) do lica wełny
    rect(X_IN, st, x_pp, zf, fill="#ffffff", sw=0.12)                  # podłoga podniesiona 150
    for q in range(1, 12):
        x = X_IN + q * 0.35
        if x < x_pp - 0.05:
            svg.line(P(x, st), P(x, zf - 0.03), stroke="#8a857e", sw=0.08)
    for q in range(1, 22):                                             # rury TABS
        x = X_IN + q * 0.18
        if x < -(X_INS + 0.08):
            svg.circle(P(x, sb + 0.07), 0.35, fill="none", stroke="#a8483a", sw=0.08)
call(7, -2.4, F6 - 0.3)
call(8, -3.6, F6 - 0.07)


def spandrel_flush(z0, z1, cladding="metal"):
    """Pas w licu: okładzina X 0…−0,04 (granit) lub 0…−0,006 (Al 3 mm) / pustka 40 / wełna 260 (X −0,08…−0,34)."""
    if z1 - z0 < 0.005:
        return
    if cladding == "granite":
        rect(-X_CL, z0, 0.0, z1, fill=hg, sw=0.2)
    else:
        rect(-0.006, z0, 0.0, z1, fill=MET, stroke=MET, sw=0.1)
    rect(-X_INS, z0, -X_CAV, z1, fill=hi, sw=0.12)


def reveal_beyond(z0, z1, x_out):
    """Ościeże 0,45 m z blachy Al widziane w głębi (bok filara między licem a ramą okna)."""
    rect(x_out, z0, 0.0, z1, fill=MET_V, stroke="#6b645e", sw=0.1, extra='fill-opacity="0.38"')
    svg.line(P(0.0, z0), P(0.0, z1), stroke="#6b645e", sw=0.14)


def window(zs, zh, x_out=-OSC, transom=None, zip_box=True, fixed_to=None, soffit=True):
    """Okno Al: rama w X = x_out … x_out − 0,10; parapet zewn. Al z kapinosem w licu (bez wysięgu poza X = 0);
    kaseta ZIP nad nadprożem (zh … zh + 0,18); podniebienie ościeża z blachy Al."""
    rect(x_out - 0.10, zs, x_out, zs + 0.08, fill=MET, stroke=MET)          # rama dolna
    rect(x_out - 0.10, zh - 0.08, x_out, zh, fill=MET, stroke=MET)          # rama górna
    for dx in (-0.025, -0.05, -0.075):
        svg.line(P(x_out + dx, zs + 0.08), P(x_out + dx, zh - 0.08), stroke=GLASS, sw=0.22)
    if transom:
        rect(x_out - 0.10, zs + transom - 0.04, x_out, zs + transom + 0.04, fill=MET, stroke=MET)
    if fixed_to:
        rect(x_out - 0.10, fixed_to - 0.04, x_out, fixed_to + 0.04, fill=MET, stroke=MET)
    # parapet zewnętrzny Al ze spadkiem, kapinos w licu (X ≤ 0) i podokiennik wewnętrzny
    svg.poly([P(-0.004, zs - 0.035), P(x_out, zs + 0.015), P(x_out, zs - 0.015), P(-0.004, zs - 0.065)], fill=MET, stroke=MET, sw=0.1)
    rect(-0.012, zs - 0.10, -0.004, zs - 0.035, fill=MET, stroke=MET, sw=0.08)
    rect(x_out - 0.30, zs, x_out - 0.10, zs + 0.03, fill="#cfc8bc", sw=0.08)
    if zip_box:
        rect(x_out + 0.015, zh, x_out + 0.165, zh + ZIP, fill="#6b645e", stroke=INK, sw=0.1)
    if soffit:
        rect(x_out, zh - 0.012, 0.0, zh, fill=MET, stroke=MET, sw=0.08)     # podniebienie ościeża: blacha Al


# ------------------------------------------------------------------ kond. 4 (nadproże, częściowo – maskowane poniżej ZB)
window(F4 + PAR, F4 + NADPR, fixed_to=F4 + KW)
reveal_beyond(F4 + PAR, F4 + NADPR, -OSC)
rect(-X_RC, F4 + NADPR + ZIP, -X_INS, F5 - FLOOR - SLAB, fill=hc, sw=0.2)    # nadproże żelbetowe
spandrel_flush(F4 + NADPR, F5, "metal")                                      # płycina 4/5 pod kordonem

# ------------------------------------------------------------------ kond. 5: kordon granitowy +19,80–20,85 (w licu), okno
rect(-X_RC, F5 - FLOOR, -X_INS, Z_KORD, fill=hc, sw=0.2)                     # attyka podokienna żelbetowa
spandrel_flush(F5, Z_KORD, "granite")
call(9, 0.0, F5 + 0.55, 0.6)
window(Z_KORD, F5 + NADPR)                 # rama dolna 0,08 → szkło od +1,13 nad posadzką (≥ 1,10)
reveal_beyond(Z_KORD, F5 + NADPR, -OSC)
call(5, -OSC - 0.05, F5 + 2.3, -1.6)
call(16, -OSC / 2, F5 + 1.6, 1.25)
call(17, -0.02, Z_KORD - 0.05, 0.9)
# płycina 5/6 w licu (Al) do wierzchu stropu kond. 6; nadproże żelbetowe
spandrel_flush(F5 + NADPR, Z6_0, "metal")
rect(-X_RC, F5 + NADPR + ZIP, -X_INS, F6 - FLOOR - SLAB, fill=hc, sw=0.15)
call(4, 0.0, Z6_0 - 0.12, 0.6)
call(15, -0.20, F5 + NADPR + 0.12, 1.5)
# obróbka Al nad pasem płycin (na wierzchu stropu, ze spadkiem na zewnątrz, kapinos w licu)
svg.poly([P(0.0, Z6_0 + 0.005), P(-REC6, Z6_0 + 0.035), P(-REC6, Z6_0 + 0.055), P(0.0, Z6_0 + 0.025)], fill=MET, stroke=MET, sw=0.1)
# ------------------------------------------------------------------ kond. 6 – cofnięta 0,40 m: płycina Al + okno
rect(-(REC6 + 0.006), Z6_0 + 0.05, -REC6, F6 + PAR, fill=MET, stroke=MET, sw=0.1)
rect(-X6_INS, Z6_0, -(REC6 + 0.04), F6 + PAR, fill=hi, sw=0.12)
rect(-X6_RC, F6 - FLOOR, -X6_INS, F6 + PAR, fill=hc, sw=0.15)
rect(-REC6, Z6_0 + 0.05, 0.0, Z6_1, fill=MET_V, stroke="#6b645e", sw=0.1, extra='fill-opacity="0.30"')   # bok filara w głębi (Al)
window(F6 + PAR, F6 + NADPR, x_out=-REC6, fixed_to=F6 + KW, zip_box=True, soffit=False)
rect(-(REC6 + 0.006), F6 + NADPR + ZIP, -REC6, Z6_1, fill=MET, stroke=MET, sw=0.1)       # panel Al nad kasetą
call(10, -REC6, F6 + 2.0, 1.0)
call(6, -REC6 - 0.05, F6 + PAR + 0.25, -1.75)
# podniebienie wnęki (blacha Al) i lico granitowe korony od spodu stropu S
rect(-REC6, Z6_1 - 0.012, 0.0, Z6_1, fill=MET, stroke=MET, sw=0.08)
spandrel_flush(Z6_1, FS + 0.70, "granite")
rect(-X_RC, FS - FLOOR, -X_INS, FS + 0.70, fill=hc, sw=0.2)

# ------------------------------------------------------------------ korona S: okno holu 1,65 × 5,00, poprzeczka na +30,50
window(FS + 0.70, FS + 5.70, transom=2.5, zip_box=False)
reveal_beyond(FS + 0.70, FS + 5.70, -OSC)
call(11, -OSC - 0.05, FS + 4.0, -1.6)
ZR_DECK = 35.80
spandrel_flush(FS + 5.70, Z_ROOF, "granite")
rect(-X_RC, FS + 5.70, -X_INS, Z_ROOF, fill=hc, sw=0.2)                     # wieniec / attyka żelbetowa
call(1, 0.0, 34.6, 0.6)
call(2, -0.20, 33.6, 0.6)
call(3, -(X_INS + X_RC) / 2, 34.0, 0.6)
# kratownice stalowe 1,60 m (34,20–35,80), sufit akustyczny +34,15
zt0, zt1 = Z_SUF + 0.05, ZR_DECK
svg.line(P(X_IN, zt1 - 0.1), P(-X_RC, zt1 - 0.1), stroke=INK, sw=0.5)
svg.line(P(X_IN, zt0 + 0.1), P(-X_RC, zt0 + 0.1), stroke=INK, sw=0.5)
x = X_IN
while x < -(X_RC + 0.1):
    svg.line(P(x, zt0 + 0.1), P(min(-X_RC, x + 0.8), zt1 - 0.1), stroke=INK, sw=0.25)
    svg.line(P(min(-X_RC, x + 0.8), zt1 - 0.1), P(min(-X_RC, x + 1.6), zt0 + 0.1), stroke=INK, sw=0.25)
    x += 1.6
rect(X_IN, Z_SUF - 0.05, -(X_RC + 0.16), Z_SUF, fill="#bdb6ab", sw=0.08)
call(12, -2.6, 35.0)
# dach: płyta zespolona 35,80–35,95, paroizolacja, wełna w spadku, membrana, BIPV szkło-szkło (+36,20 … +36,45)
xr = -X_RC
rect(X_IN, ZR_DECK, xr, ZR_DECK + 0.15, fill=hc, sw=0.2)
svg.poly([P(X_IN, Z_ROOF_MAX - 0.08), P(xr, Z_ROOF - 0.05), P(xr, ZR_DECK + 0.15), P(X_IN, ZR_DECK + 0.15)], fill=hi, stroke=INK, sw=0.15)
svg.poly([P(X_IN, Z_ROOF_MAX - 0.05), P(xr, Z_ROOF - 0.02), P(xr, Z_ROOF - 0.05), P(X_IN, Z_ROOF_MAX - 0.08)], fill=INK, stroke="none")
dz = (Z_ROOF_MAX - Z_ROOF) - 0.03
for q in range(6):
    xa = X_IN + q * 0.7
    if xa < -0.9:
        za = Z_ROOF_MAX - 0.05 - (xa - X_IN) / (xr - X_IN) * dz
        svg.poly([P(xa, za + 0.02), P(xa + 0.62, za + 0.02 - 0.62 / (xr - X_IN) * dz), P(xa + 0.62, za + 0.07 - 0.62 / (xr - X_IN) * dz),
                  P(xa, za + 0.07)], fill="#2e3a48", stroke=INK, sw=0.08)
call(13, -2.0, 36.35)
# attyka: żelbet 200, wełna 260, granit 40; czapa granitowa i obróbka Al – wszystko w obrysie (X ≤ 0)
rect(-X_RC, Z_ROOF - 0.05, -X_INS, Z_ATT - 0.15, fill=hc, sw=0.2)
rect(-X_INS, Z_ROOF, -X_CAV, Z_ATT - 0.15, fill=hi, sw=0.12)
rect(-X_CL, Z_ROOF, 0.0, Z_ATT - 0.15, fill=hg, sw=0.2)
svg.poly([P(0.0, Z_ATT - 0.15), P(-(X_RC + 0.08), Z_ATT - 0.15), P(-(X_RC + 0.08), Z_ATT - 0.10), P(0.0, Z_ATT - 0.04)], fill=hg, stroke=INK, sw=0.2)
svg.poly([P(0.0, Z_ATT - 0.04), P(-(X_RC + 0.10), Z_ATT - 0.10), P(-(X_RC + 0.10), Z_ATT - 0.065), P(0.0, Z_ATT)], fill=MET, stroke=MET, sw=0.1)
rect(-(X_RC + 0.10), Z_ATT - 0.30, -(X_RC + 0.08), Z_ATT - 0.065, fill=MET, stroke=MET, sw=0.08)   # obróbka od strony dachu
call(14, -0.3, Z_ATT + 0.05, 0.8)
# break lines
svg.line(P(X_IN - 0.1, ZB + 0.05), P(0.4, ZB + 0.05), stroke=INK, sw=0.15, dash="1.5,0.8")
svg.line(P(X_IN, ZB), P(X_IN, ZT - 0.2), stroke=INK, sw=0.15, dash="1.5,0.8")

# ------------------------------------------------------------------ rzędne
for z, lab in ((Z_ATT, f"{fz(Z_ATT)} attyka = {Z_ATT + Z0:.2f}".replace(".", ",")),
               (Z_ROOF_MAX, f"{fz(Z_ROOF_MAX)} najwyższy pkt pokrycia"),
               (Z_ROOF, f"{fz(Z_ROOF)} najniższy pkt pokrycia (MPZP ≥ 35,0 m)"),
               (Z_SUF, f"{fz(Z_SUF)} sufit holu ({Z_SUF - FS:.2f} m)".replace(".", ",")), (FS, f"{fz(FS)} posadzka S"),
               (F6, f"{fz(F6)} posadzka 6"), (Z_KORD, f"{fz(Z_KORD)} kordon = gzyms skrzydła"), (F5, f"{fz(F5)} posadzka 5")):
    if z < ZB + 0.2:
        continue
    x, y = P(X_IN - 0.4, z)
    svg.poly([(x, y), (x - 1.3, y - 1.5), (x + 1.3, y - 1.5)], fill=INK, stroke="none")
    svg.line((x - 2.5, y), (x + 4, y), stroke=INK, sw=0.12)
    svg.text((x - 3, y - 0.4), lab, size=2.1, anchor="end")

# ------------------------------------------------------------------ odnośniki
for n, X, Z, dx in callouts:
    if Z < ZB + 0.1:
        continue
    x, y = P(X, Z)
    bx = x + dx * SC
    if dx:
        svg.line((x, y), (bx, y), stroke=INK, sw=0.12)
    svg.circle((bx + (2.2 if dx > 0 else -2.2 if dx < 0 else 0), y), 2.2, fill="#ffffff", stroke="#a8483a", sw=0.25)
    svg.text((bx + (2.2 if dx > 0 else -2.2 if dx < 0 else 0), y + 0.8), str(n), size=2.2, anchor="middle", weight=700, fill="#a8483a")

# ------------------------------------------------------------------ fragment elewacji (2 przęsła) po prawej
EX0 = 2.9      # paper offset (m at 1:50) from section façade plane


def E(u, z):
    return (OX + (EX0 + u) * SC, OY - (z - ZB) * SC)


def erect(u0, z0, u1, z1, fill, stroke=INK, sw=0.15, extra=""):
    svg.poly([E(u0, z0), E(u1, z0), E(u1, z1), E(u0, z1)], fill=fill, stroke=stroke, sw=sw, extra=extra)


def ewin(a, b, z0, z1, fill="#7b8792", mull=True, transom=None, osc=OSC):
    """Okno w elewacji z cieniem nadproża i ościeża 0,45 m (światło z lewej góry)."""
    erect(a, z0, b, z1, fill, sw=0.12)
    if mull:
        svg.line(E((a + b) / 2, z0), E((a + b) / 2, z1), stroke=MET, sw=0.35)
    if transom:
        erect(a, z0 + transom - 0.04, b, z0 + transom + 0.04, MET, stroke="none")
    sh = min(osc * 0.75, (z1 - z0) * 0.3)
    erect(a, z1 - sh, b, z1, "#1f1d1a", stroke="none", extra='fill-opacity="0.32"')
    erect(a, z0, a + osc * 0.6, z1 - sh, "#1f1d1a", stroke="none", extra='fill-opacity="0.24"')


piers = [(0.0, 0.525), (2.175, 3.225), (4.875, 5.4)]
bays = [(0.525, 2.175), (3.225, 4.875)]
erect(0, ZB, 5.4, Z_ROOF, MET, stroke="none")
for a, b in bays:
    ewin(a, b, F4 + PAR, F4 + NADPR, transom=KW - PAR)                          # kond. 4 (maskowana poniżej ZB)
    erect(a, F5, b, Z_KORD, hg)                                                 # kordon
    ewin(a, b, Z_KORD, F5 + NADPR)                                              # kond. 5
    # kond. 6 (cofnięta 0,40, ciemniejsza)
    erect(a, Z6_0, b, Z6_1, "#2e2b29", stroke="none")
    erect(a + 0.05, F6 + PAR, b - 0.05, F6 + NADPR, "#3d434a", stroke="#5d646b", sw=0.1)
    svg.line(E((a + b) / 2, F6 + PAR), E((a + b) / 2, F6 + NADPR), stroke=MET, sw=0.3)
    erect(a + 0.05, F6 + KW - 0.03, b - 0.05, F6 + KW + 0.03, MET, stroke="none")
    erect(a, Z6_1 - 0.45, b, Z6_1, "#1f1d1a", stroke="none", extra='fill-opacity="0.5"')
    # okno holu w koronie
    erect(a, Z6_1, b, FS + 0.70, hg)
    ewin(a, b, FS + 0.70, FS + 5.70, transom=2.5)
    erect(a, FS + 5.70, b, Z_ROOF, hg)
    for qz in range(12):          # nadruk punktowy na szkle korony (ochrona ptaków)
        for qu in range(7):
            svg.circle(E(a + 0.12 + qu * 0.24, FS + 0.9 + qz * 0.38), 0.18, fill="#ffffff", stroke="none", extra='fill-opacity="0.35"')
for a, b in piers:
    erect(a, ZB, b, Z_ROOF, hg, sw=0.2)
    zj = ZB + 0.6
    while zj < Z_ROOF:
        svg.line(E(a, zj), E(b, zj), stroke=GRAN_H, sw=0.1)
        zj += 1.25
    svg.line(E(b, ZB), E(b, Z_ROOF), stroke=INK, sw=0.1)
    erect(b, ZB, min(5.4, b + 0.12), Z_ROOF, "#1f1d1a", stroke="none", extra='fill-opacity="0.12"')
erect(0, Z_ROOF, 5.4, Z_ATT - 0.06, hg, sw=0.2)
erect(0, Z_ATT - 0.06, 5.4, Z_ATT, MET, stroke=MET, sw=0.1)                  # obróbka attyki w licu (bez wysięgu)
svg.text((E(2.7, 0)[0], E(0, ZT)[1] - 2), "FRAGMENT ELEWACJI PÓŁNOCNEJ (2 przęsła)", size=2.6, anchor="middle", weight=600)
svg.text((P(-2.3, 0)[0], P(0, ZT)[1] - 2), "PRZEKRÓJ PRZEZ OŚ OKNA", size=2.6, anchor="middle", weight=600)
# wszystko narysowane dotąd przycięte do ZB (bez resztek poniżej linii urwania), dodatkowo maska poniżej podstawy
svg.defs.append(f'<clipPath id="nad_zb"><rect x="0" y="0" width="{W_MM:.3f}" height="{OY + 0.3:.3f}"/></clipPath>')
svg.parts = ['<g clip-path="url(#nad_zb)">'] + svg.parts + ['</g>']
svg.poly([(0, OY + 0.3), (W_MM, OY + 0.3), (W_MM, H_MM + 120), (0, H_MM + 120)], fill="#ffffff", stroke="none")
svg.line((OX + (X_IN - 0.2) * SC, OY + 0.3), (OX + 0.5 * SC, OY + 0.3), stroke=INK, sw=0.15, dash="1.5,0.8")
# wymiary (pod fragmentem elewacji)
yd = E(0, ZB)[1] + 7
for u0, u1, t in ((0.525, 2.175, "1,65"), (2.175, 3.225, "1,05"), (3.225, 4.875, "1,65"), (0.0, 0.525, ""), (4.875, 5.4, "")):
    x0, x1 = E(u0, 0)[0], E(u1, 0)[0]
    svg.line((x0, yd), (x1, yd), stroke=INK, sw=0.12)
    for x in (x0, x1):
        svg.line((x - 0.8, yd + 0.8), (x + 0.8, yd - 0.8), stroke=INK, sw=0.2)
    if t:
        svg.text(((x0 + x1) / 2, yd - 1.0), t, size=2.0, anchor="middle")
x0, x1 = E(1.35, 0)[0], E(4.05, 0)[0]
svg.line((x0, yd + 5), (x1, yd + 5), stroke=INK, sw=0.12)
svg.text(((x0 + x1) / 2, yd + 4), "oś przęsła 2,70 (2 moduły 1,35)", size=2.0, anchor="middle")

# ------------------------------------------------------------------ legenda warstw (v1.1, tabela przegród 1:50)
u_txt = f"{U_W:.3f}".replace(".", ",")
w_mm = int(round(WOOL * 1000))
o_txt = f"{OSC:.2f}".replace(".", ",")
LEG = [
    "1  lico filarów: granit strzegomski płomieniowany 40 mm (S 1502-Y), kotwy nierdzewne",
    "    (okładzina nieodpadająca ≥ 60 min); ościeża i węgary bez granitu",
    f"2  pustka wentylowana 40 / wełna mineralna λ 0,033 – {w_mm} mm; konsole ze stali nierdzewnej",
    f"    z przekładką termiczną (ΔU 0,025) → U = {u_txt} W/(m²K); całość A1 (NRO)",
    "3  ściana-słup żelbetowy filara 300 / płycina i wieniec żelbet 200 / attyka żelbetowa 200",
    "4  płycina: aluminium anodowane grafitowy brąz RAL 8019, 3 mm, A1",
    "    (od dziedzińca ≤ 25 m: BIPV szkło-szkło 10 mm w tym kolorze, ≥ B-s1,d0)",
    "5  okno Al z przekładką, pakiet 3-szybowy 54 mm, Uw ≤ 0,80, g = 0,33; parapet 0,55,",
    f"    nadproże 3,00; kaseta ZIP do +3,18 (pod stropem +3,32), > 25 m tkanina szklano-silikonowa A2",
    f"6  dolna kwatera stała ze szkła bezpiecznego do +{KW:.2f} m nad posadzką (WT § 301)".replace(".", ","),
    "7  strop sprężony 280 z aktywacją termiczną (TABS), sufit odsłonięty + baffle",
    "8  podłoga podniesiona 150 (instalacje elektryczne i teletechniczne)",
    "9  kordon kwartału: granit +19,80–20,85 w linii gzymsu skrzydła (140,15) i attyki Maz. 19",
    "10 kondygnacja cienia: szkło i metal 0,40 m za licem filarów; obróbka Al nad pasem płycin",
    "11 okno holu Sejmiku 1,65 × 5,00 m, g = 0,27, R ≤ 12 %, nadruk punktowy (ochrona ptaków)",
    "12 kratownice stalowe h = 1,60 m, rozpiętość 19,5 m; sufit akustyczny +34,15",
    "13 dach: BIPV szkło-szkło BROOF(t1) / membrana / spadki / wełna mineralna 300 / paroizolacja /",
    "    płyta zespolona; U ≤ 0,12; bez urządzeń na dachu (zwody ≤ korony attyki)",
    "14 attyka 1,00 m: czapa granitowa i obróbka Al RAL 8019 w obrysie, bez wysięgu (+37,20 = 156,50)",
    "15 pas międzykondygnacyjny EI 60 ≥ 0,80 m; powyżej 25 m wszystkie warstwy i mocowania niepalne",
    f"16 ościeże {o_txt} m: blacha Al lakierowana proszkowo RAL 8019 na wełnie (granit tylko na licu filara)",
    "17 parapet zewnętrzny Al ze spadkiem, kapinos w licu – bez wysięgu poza obrys (lico wieży)",
]
svg.text((20.0, 12.0), "PRZEKRÓJ ELEWACYJNY I FRAGMENT ELEWACJI", size=4.4, weight=600)
svg.text((20.0, 18.0), "korona wieży od Placu Mostowego (elewacja pn., hol reprezentacyjny Sejmiku) · 1:50", size=2.4, fill="#4d4842")
LX = W_MM - 128
for i, t in enumerate(LEG):
    t = ("\u00a0" * 6 + t.lstrip()) if t.startswith("    ") else t      # wcięcie wiersza kontynuacji
    svg.text((LX, 40 + i * 3.6), t, size=2.0, fill="#2f2b28")
svg.text((LX, 34), "WARSTWY (od zewnątrz)", size=2.4, weight=600)
# podziałka 0–2 m
sx, sy = 20.0, H_MM - 8
for i in range(4):
    svg.poly([(sx + i * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy), (sx + (i + 1) * 0.5 * SC, sy + 1.2), (sx + i * 0.5 * SC, sy + 1.2)], fill=INK if i % 2 == 0 else "#fff", stroke=INK, sw=0.12)
svg.text((sx + 2 * SC + 4, sy + 1.2), "0–2 m · 1:50", size=2.2, weight=600)

SUF = "_korona" if ZB > 20 else ""
out = ROOT / "build" / "rysunki" / f"przekroj_elewacyjny_1-50{SUF}.svg"
out.write_text(svg.render(), encoding="utf-8")
html = ROOT / "docs" / "70_rysunki" / "podglady" / f"przekroj_elewacyjny_1-50{SUF}.html"
html.write_text(f'<!doctype html><html><head><meta charset="utf-8"><style>@page{{size:{W_MM + 10:.0f}mm {H_MM + 10:.0f}mm;margin:0}}body{{margin:0;padding:5mm}}</style></head><body>{svg.render()}</body></html>', encoding="utf-8")
print(f"{W_MM + 10:.0f} {H_MM + 10:.0f}")
