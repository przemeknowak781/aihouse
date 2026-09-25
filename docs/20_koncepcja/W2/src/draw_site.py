# -*- coding: utf-8 -*-
"""Plan zagospodarowania dzialki - wariant W2."""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon as MPoly
from shapely.geometry import box
from shapely.ops import unary_union
import model_w2 as M
import draw_common as D

OUT = sys.argv[1] if len(sys.argv) > 1 else "."
Z = M.DZ


def wskazniki():
    """Wskazniki zagospodarowania (liczone z geometrii modelu)."""
    dz = box(Z["xw"], Z["ys"], Z["xe"], Z["yn"])
    walls = unary_union([M.outline("P0"), M.outline("P1"), M.outline("P2")])
    plyty = unary_union([walls] + [p["poly"] for p in M.PLYTY])
    utw = unary_union([e["poly"] for e in M.TEREN_ELEM.values()] + [walls])
    pbc = dz.area - utw.area
    zielony_dach = box(12.30, -0.30, 18.70, 9.30).area - 0.3 * (6.4 + 9.6) * 2  # netto w attyce
    kond = sum(M.outline(k).area for k in ("P0", "P1", "P2"))
    return dict(dzialka=dz.area, zabudowa=walls.area, zabudowa_plyty=plyty.area, utwardzone=utw.area - walls.area,
                pbc=pbc, pbc_z_dachem=pbc + 0.5 * zielony_dach, dach_ziel=zielony_dach, suma_kond=kond, intens=kond / dz.area,
                walls=walls, plyty=plyty)


def main():
    W = wskazniki()
    fig, ax = plt.subplots(figsize=(14.5, 17.5))
    ax.set_aspect("equal")
    ax.set_xlim(-11.5, 36.0)
    ax.set_ylim(-35.5, 30.5)
    ax.axis("off")
    # droga
    ax.add_patch(Rectangle((-11.5, M.SIEC["pas"][0]), 40, 10, facecolor="#efefef", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-11.5, M.SIEC["jezdnia"][0]), 40, M.SIEC["jezdnia"][1] - M.SIEC["jezdnia"][0], facecolor="#bdbdbd", edgecolor="none", zorder=0.1))
    ax.plot([-11.5, 28.5], [M.SIEC["pas"][1]] * 2, color="black", lw=0.8, ls=(0, (10, 3, 2, 3)))
    ax.text(8.5, 22.3, "ul. Lipowa — droga gminna 1KDD (linie rozgraniczające 10 m)", fontsize=9, ha="center", va="center")
    for k, (y, c) in {"woda": (M.SIEC["woda"], "#1f6fb4"), "kan": (M.SIEC["kan"], "#8b4513"), "en": (M.SIEC["en"], "#d62728"),
                      "tel": (M.SIEC["tel"], "#7f7f7f"), "gaz": (M.SIEC["gaz"], "#e6b800")}.items():
        ax.plot([-11.5, 28.5], [y, y], color=c, lw=1.0, ls=(0, (6, 2)), zorder=0.5)
        lab = {"woda": "wodociąg PE 110", "kan": "kanalizacja sanitarna PVC 200", "en": "kabel nN 0,4 kV", "tel": "światłowód", "gaz": "gazociąg (niewykorzystywany)"}[k]
        ax.text(27.8, y + 0.15, lab, fontsize=6.3, ha="right", va="bottom", color=c)
    # dzialki sasiednie
    for x0, x1, t in ((-11.5, Z["xw"], "dz. sąsiednia MN\n(budynek ≥ 8 m od granicy)"), (Z["xe"], 28.5, "dz. sąsiednia MN\n(budynek ≥ 8 m od granicy)")):
        ax.add_patch(Rectangle((x0, Z["ys"]), x1 - x0, Z["yn"] - Z["ys"], facecolor="#f6f6f1", edgecolor="none", zorder=0))
        ax.text((x0 + x1) / 2 + (0.8 if x0 > 0 else 0), 8, t, fontsize=6.5, rotation=90, ha="center", va="center", color="#777")
    ax.text(8.5, -34.2, "teren rolny / zieleni (R)", fontsize=7, ha="center", color="#777")
    # dzialka
    ax.add_patch(Rectangle((Z["xw"], Z["ys"]), Z["xe"] - Z["xw"], Z["yn"] - Z["ys"], facecolor="#eef6e4", edgecolor="black", lw=1.6,
                           ls=(0, (12, 3, 2, 3)), zorder=0.3))
    ax.text(Z["xw"] + 0.4, Z["ys"] + 0.6, "dz. nr 123/4, obr. 0005 „Przykładowo”  —  32,00 × 50,00 m = 1600,00 m²", fontsize=7.5, ha="left")
    # zywoploty (zielen izolacyjna)
    for x0 in (Z["xw"], Z["xe"] - 1.0):
        ax.add_patch(Rectangle((x0, Z["ys"] + 1), 1.0, 30.0, facecolor="#9cc47a", edgecolor="none", alpha=0.7, zorder=0.6))
    ax.add_patch(Rectangle((Z["xw"] + 1, Z["ys"]), 30.0, 1.0, facecolor="#9cc47a", edgecolor="none", alpha=0.7, zorder=0.6))
    ax.text(Z["xw"] + 0.5, -20, "żywopłot — zieleń izolacyjna", fontsize=6, rotation=90, ha="center", va="center", color="#2f5d1a")
    for (x, y, r) in M.DRZEWA:
        ax.add_patch(Circle((x, y), r, facecolor="#b9d99a", edgecolor="#5a8a3a", lw=0.8, alpha=0.8, zorder=0.7))
        ax.plot([x], [y], marker="+", color="#3d6b22", zorder=0.8)
    # utwardzenia
    col = {"podjazd": "#cfcac1", "dojscie": "#d9d4ca", "taras": "#e6d9bf", "sciezka_E": "#e3e0da", "smietnik": "#9e9e9e", "pc_plyta": "#bdbdbd", "skrzynki": "#cfe3f3"}
    for k, e in M.TEREN_ELEM.items():
        D.draw_poly(ax, e["poly"], facecolor=col[k], edgecolor="#777", lw=0.6, zorder=1, hatch="///" if k == "skrzynki" else None)
    for i, mp in enumerate(M.MIEJSCA_GOSC):
        D.draw_poly(ax, mp, facecolor="none", edgecolor="#333", lw=0.8, zorder=2, ls=(0, (4, 2)))
        c = mp.centroid
        ax.text(c.x, c.y, f"P{i+1}\ngość\n2,5×5,0", fontsize=6.3, ha="center", va="center", zorder=2)
    zx, zy = M.ZBIORNIK["xy"]
    ax.add_patch(Rectangle((zx - 1.5, zy - 1.0), 3.0, 2.0, facecolor="#cfe3f3", edgecolor="#1f6fb4", lw=0.9, zorder=2))
    ax.text(zx, zy, "zbiornik\n6 m³", fontsize=6, ha="center", va="center", zorder=3)
    ax.text(-2.0, 14.6, "skrzynki rozsączające", fontsize=5.8, ha="center", va="center", zorder=3)
    # budynek
    D.draw_poly(ax, M.outline("P0"), facecolor="#8f8f8f", edgecolor="black", lw=1.2, zorder=3)
    D.draw_poly(ax, box(12.30, -0.30, 18.70, 9.30), facecolor="#b7d99a", edgecolor="black", lw=0.8, zorder=3.1, hatch="..")
    D.draw_poly(ax, M.outline("P2"), facecolor="#6e6e6e", edgecolor="black", lw=1.0, zorder=3.2)
    D.outline_dashed(ax, W["plyty"], color="#222", ls=(0, (2, 2)), lw=0.8, z=3.3)
    ax.text(5.3, 2.3, "BUDYNEK\nMIESZKALNY\njednorodzinny\n3 kond. nadz.\n±0,00 = 101,65\ndach P2 attyka +9,80", fontsize=7.2, ha="center", va="center",
            color="white", zorder=4, fontweight="bold")
    ax.text(15.5, 4.5, "garaż 2-st.\ndach zielony\n+3,85", fontsize=6.8, ha="center", va="center", zorder=4)
    ax.text(1.7, 7.0, "dach P1\n+6,70", fontsize=6, ha="center", va="center", color="white", zorder=4)
    ax.text(10.4, 7.0, "dach P1\n+6,70", fontsize=6, ha="center", va="center", color="white", zorder=4)
    ax.text(-2.2, 5.6, "wspornik\nP2", fontsize=5.5, ha="center", va="bottom", zorder=4)
    ax.text(11.0, 9.55, "wejście", fontsize=6, ha="center", va="center", zorder=4)
    ax.annotate("", xy=(15.5, 9.5), xytext=(15.5, 16.8), arrowprops=dict(arrowstyle="->", lw=1.2), zorder=4)
    ax.text(15.5, 16.0, "wjazd", fontsize=6.3, ha="center", va="bottom", zorder=4)
    ax.text(5.0, -2.3, "taras ogrodowy −0,05", fontsize=6.5, ha="center", zorder=4)
    ax.text(20.1, 1.1, "PC", fontsize=6, ha="center", va="center", zorder=4)
    ax.text(7.8, 16.65, "odpady", fontsize=5.5, ha="center", va="center", color="white", zorder=4)
    # linia zabudowy
    ax.plot([Z["xw"], Z["xe"]], [M.LINIA_ZAB] * 2, color="#c00000", lw=1.3, ls=(0, (8, 3)), zorder=5)
    for xx in range(-6, 24, 3):
        ax.add_patch(MPoly([(xx, M.LINIA_ZAB), (xx + 0.35, M.LINIA_ZAB + 0.45), (xx + 0.7, M.LINIA_ZAB)], closed=True, facecolor="#c00000", zorder=5))
    ax.text(Z["xw"] + 0.3, M.LINIA_ZAB + 0.6, "nieprzekraczalna linia zabudowy 6,0 m (MPZP 3MN)", fontsize=6.8, color="#c00000", ha="left", va="bottom")
    # ogrodzenie
    b0, b1 = M.OGRODZENIE["brama"]
    f0, f1 = M.OGRODZENIE["furtka"]
    for (a, b) in ((Z["xw"], M.TEREN_ELEM["smietnik"]["poly"].bounds[0]), (9.0, f0), (f1, b0)):
        ax.plot([a, b], [Z["yn"] - 0.1] * 2, color="#333", lw=2.2, zorder=5)
    ax.plot([b1, Z["xe"]], [Z["yn"] - 0.1] * 2, color="#333", lw=2.2, zorder=5)
    ax.plot([b0, b1], [Z["yn"] - 0.25] * 2, color="#333", lw=1.0, ls=(0, (3, 2)), zorder=5)
    ax.annotate("", xy=(b1 + 5.4, Z["yn"] - 0.6), xytext=(b1 + 0.3, Z["yn"] - 0.6), arrowprops=dict(arrowstyle="->", lw=0.8), zorder=5)
    ax.text(b1 + 0.4, Z["yn"] - 0.9, "brama przesuwna 5,60 m (odjazd na E)", fontsize=5.8, ha="left", va="top", zorder=5)
    ax.text((f0 + f1) / 2 - 0.6, Z["yn"] - 0.8, "furtka 1,0", fontsize=5.5, ha="center", va="top", zorder=5)
    ax.add_patch(Rectangle((M.ZK[0], Z["yn"] - 0.45), M.ZK[1] - M.ZK[0], 0.45, facecolor="#d62728", edgecolor="black", lw=0.5, zorder=6))
    ax.text(M.ZK[0] - 0.1, Z["yn"] + 0.3, "ZK", fontsize=6, ha="right", va="bottom", color="#d62728", zorder=6)
    ax.text(Z["xe"] - 0.2, Z["yn"] + 0.25, "ogrodzenie od drogi ażurowe h = 1,50 m", fontsize=6, ha="right", va="bottom")
    # przylacza
    cc = {"woda": "#1f6fb4", "kan": "#8b4513", "en": "#d62728", "tel": "#7f7f7f", "deszcz": "#17becf"}
    for k, p in M.PRZYLACZA.items():
        xs, ys = zip(*p["pts"])
        ax.plot(xs, ys, color=cc[k], lw=1.6, zorder=2.5)
    ax.add_patch(Circle((5.0, 15.0), 0.35, facecolor="white", edgecolor="#8b4513", lw=1.2, zorder=6))
    ax.text(5.5, 15.0, "Sr", fontsize=6, color="#8b4513", va="center", zorder=6)
    # wymiary odleglosci
    D.dim_h(ax, Z["xw"], -1.30, 3.0, "6,30", fs=6.5)
    D.dim_h(ax, Z["xw"], -2.40, 6.4, "5,20 (płyta)", fs=6.2)
    D.dim_h(ax, Z["xw"], -0.30, -6.0, "7,30", fs=6.5)
    D.dim_h(ax, 18.70, Z["xe"], 4.0, "5,70", fs=6.5)
    D.dim_h(ax, 20.60, Z["xe"], 1.0, "3,80", fs=6.0)
    D.dim_v(ax, 9.30, Z["yn"], 20.3, "8,00", fs=6.5, left=False)
    D.dim_v(ax, 10.00, Z["yn"], 9.3, "7,30", fs=6.2)
    D.dim_v(ax, M.LINIA_ZAB, Z["yn"], 22.5, "6,00", fs=6.5, left=False)
    D.dim_v(ax, Z["ys"], -1.30, 22.0, "31,40 (okap)", fs=6.5, left=False)
    D.dim_v(ax, Z["ys"], -4.30, 13.0, "28,40 (taras)", fs=6.2)
    D.dim_h(ax, Z["xw"], Z["xe"], -33.9 + 0.6, "32,00", fs=7)
    D.dim_v(ax, Z["ys"], Z["yn"], 25.0, "50,00", fs=7, left=False)
    D.north_arrow(ax, 31.0, 26.5, 1.3)
    # skala
    for i in range(5):
        ax.add_patch(Rectangle((26 + i * 2, -34.5), 2, 0.35, facecolor="black" if i % 2 == 0 else "white", edgecolor="black", lw=0.5))
    ax.text(26, -33.9, "0", fontsize=6); ax.text(36, -33.9, "10 m", fontsize=6, ha="right")
    # tabela
    rows = [("Powierzchnia działki", f"{D.fmt(W['dzialka'])} m²", ""),
            ("Pow. zabudowy (lica ścian zewn., upzp art. 2 pkt 35)", f"{D.fmt(W['zabudowa'])} m²", f"{D.fmt(100*W['zabudowa']/W['dzialka'],1)} % ≤ 30 %"),
            ("  wariant kontrolny z płytami/okapami/ramą C", f"{D.fmt(W['zabudowa_plyty'])} m²", f"{D.fmt(100*W['zabudowa_plyty']/W['dzialka'],1)} % ≤ 30 %"),
            ("Utwardzenia (podjazd, dojście, taras, ścieżka, osłony)", f"{D.fmt(W['utwardzone'])} m²", ""),
            ("Pow. biologicznie czynna (bez dachu zielonego)", f"{D.fmt(W['pbc'])} m²", f"{D.fmt(100*W['pbc']/W['dzialka'],1)} % ≥ 50 %"),
            ("  rezerwa: 50 % dachu zielonego garażu", f"+{D.fmt(0.5*W['dach_ziel'])} m²", ""),
            ("Suma pow. kondygnacji nadziemnych (obrys zewn.)", f"{D.fmt(W['suma_kond'])} m²", f"intens. {D.fmt(W['intens'],3)} (0,05–0,80)"),
            ("Miejsca postojowe", "2 w garażu + 2 gość.", "≥ 2 ✓")]
    y = -12.0
    ax.add_patch(Rectangle((24.8, y - len(rows) * 1.25 - 0.8), 11.0, len(rows) * 1.25 + 1.9, facecolor="white", edgecolor="black", lw=0.6, zorder=7))
    ax.text(25.1, y + 0.55, "BILANS TERENU / WSKAŹNIKI MPZP", fontsize=7.5, fontweight="bold", zorder=8)
    for i, (a, b, c) in enumerate(rows):
        yy = y - 0.6 - i * 1.25
        ax.text(25.1, yy, a, fontsize=5.4, zorder=8, va="center")
        ax.text(35.6, yy + 0.25, b, fontsize=6.0, zorder=8, ha="right", va="center", fontweight="bold")
        ax.text(35.6, yy - 0.3, c, fontsize=5.4, zorder=8, ha="right", va="center", color="#1c6b2a")
    # legenda przylaczy
    leg = [("woda", "przyłącze wody PE 40 → wodomierz w pom. techn."), ("kan", "przykanalik PVC 160, Sr = studzienka D425"),
           ("en", "WLZ z ZK → rozdzielnica RG"), ("tel", "światłowód"), ("deszcz", "deszczówka → zbiornik 6 m³ → skrzynki")]
    for i, (k, t) in enumerate(leg):
        yy = -26.0 - i * 1.0
        ax.plot([25.0, 26.6], [yy, yy], color=cc[k], lw=2)
        ax.text(26.9, yy, t, fontsize=5.8, va="center")
    fig.suptitle("W2 — ZAGOSPODAROWANIE DZIAŁKI (plan poglądowy, układ budynku: x → E, y → N)", fontsize=12.5, fontweight="bold", x=0.02, ha="left", y=0.99)
    fig.text(0.02, 0.965, "Odległości od granic mierzone od lica ocieplenia (WT §9 ust. 3, §12): ściany z otworami ≥ 4,0 m, okapy/płyty ≥ 1,5 m (tu ≥ 4,0 m bezpiecznie). "
             "Wszystkie elementy budynku (także daszek i płyty) za linią zabudowy. Miejsca gościnne niezadaszone ≥ 3 m od granic E/W (WT §19 ust. 2, 5). "
             "Pojemniki: WT §23 ust. 4 — odległości nie określa się w zabudowie jednorodzinnej.", fontsize=7.2, ha="left", va="top", wrap=True)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.94, bottom=0.01)
    fn = os.path.join(OUT, "zagospodarowanie.png")
    fig.savefig(fn, dpi=140)
    plt.close(fig)
    print(fn)
    return W


if __name__ == "__main__":
    W = main()
    for k, v in W.items():
        if not hasattr(v, "area"):
            print(k, round(v, 2))
