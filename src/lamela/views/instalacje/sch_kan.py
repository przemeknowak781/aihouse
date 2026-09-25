"""Rozwinięcia (schematy pionowe) instalacji: kanalizacja sanitarna (piony, podejścia, przewody pod płytą, przykanalik,
studzienka) i wodociągowa (zestaw wodomierzowy, rozdzielacze, zasobnik, piony Wz/Wc/Cyrk, podejścia do przyborów).

Oś pionowa — rzędne w skali rzutni (rzędne rzeczywiste względem ±0,000), oś pozioma — umowna (piony co 5–6 m
rysunkowych). Wartości (DN, spadki, rzędne dna, wentylacja, średnice, przepływy) z ``lamela.obliczenia``."""
from __future__ import annotations


from ...draft import fmt, symbols as S
from ...draft.dims import arrowhead
from ...obliczenia.sanitarne.przybory import KATALOG
from ..common import Placer
from .wspolne import H_M, H_S, Legenda, legenda_arkusza, num, rura_krotko, table_block, tag_leader

SKR = {"wc": "WC", "umywalka": "UMY", "umywalka_blat": "UMY", "prysznic": "NAT", "wanna": "WAN", "zlew": "ZL",
       "zlewik": "ZLG", "zmywarka": "ZM", "pralka": "PR", "suszarka": "SU", "wpust_podlogowy": "WP",
       "wpust_podlogowy_100": "WP", "bidet": "BD", "zawor_ogrodowy": "ZO", "zawor_czerpalny": "ZC"}


def _poziomy(vp, pl, m, x0, x1, extra=()):
    """Linie poziomów kondygnacji (posadzki) i dodatkowych rzędnych z opisem po lewej stronie."""
    k = vp.k
    items = [(kk.rzedna, f"{kk.nazwa} {fmt.level(kk.rzedna)}") for kk in m.kondygnacje] + list(extra)
    for z, txt in items:
        vp.line((x0, z), (x1, z), "I-PODKLAD", pen=0.18, lt="KRESKA_DLUGA")
        n0 = len(vp.prims)
        vp.text((x0 + 0.1, z + 1.0 * k), txt, H_S, 0.0, "left", "baseline", "S-OPISY")
        pl.add_prims(vp.prims[n0:])


def rozwiniecie_kan(vp, ctx, W, res):
    m = ctx.model
    kn = W.kanalizacja
    k = vp.k
    pl = Placer(k)
    kids = [kk.id for kk in m.kondygnacje]
    odc = {o.id: o for o in kn.odcinki}
    went = {w["pion"]: w for w in kn.wentylacja}
    st = kn.studzienka or {}
    E_z = kn.rzedne.get("wyjście z budynku", -1.4)
    # kolejność: od najdalszego pionu (lewo) do wyjścia (prawo) — jak łańcuch kolektora w obliczeniach
    order = [p for p in sorted(kn.piony, key=lambda p: kn.rzedne.get(f"pion {p.id}", 0.0), reverse=True)]
    dx = 6.0
    xs = {p.id: 2.0 + i * dx for i, p in enumerate(order)}
    x_end = 2.0 + len(order) * dx
    teren = float(st.get("teren", -0.3))
    _poziomy(vp, pl, m, 0.0, x_end + 3.0, [(teren, f"teren przy studzience {fmt.level(teren)}")])
    leg = Legenda()
    leg.line("S-KANAL", "Ks — pion / podejście PP-HT (PN-EN 1451-1)", pen="gruba")
    leg.line("S-KANAL", "przewód pod płytą / przykanalik PVC-U SN8 (PN-EN 1401-1)", lt="KRESKOWA", pen="gruba")
    base_pts = []
    for p in order:
        x = xs[p.id]
        zb = kn.rzedne.get(f"pion {p.id}", E_z)
        top = max(kids.index(kk) for kk in p.kondygnacje)
        w = went.get(p.id) or {}
        o = odc.get(f"PION_{p.id}")
        z_up = w.get("z_wylotu") or (m.kondygnacje[top].rzedna + 1.2)
        vp.line((x, zb), (x, z_up), "S-KANAL", pen="gruba", lt="CIAGLA")
        if w.get("z_wylotu"):
            vp.line((x - 0.12, z_up), (x + 0.12, z_up), "S-KANAL", pen="gruba", lt="CIAGLA")
            txt = f"wywiewka Ø{o.rura.split()[-1] if o else 110} wylot {fmt.level(z_up)}"
        else:
            S.tag(vp, (x, z_up + 0.12), "ZN", shape="circle", r_mm=2.0, h=H_S, layer="S-KANAL")
            txt = "zawór napowietrzający (PN-EN 12380)"
        tag_leader(vp, pl, (x, z_up), [txt], "S-OPISY")
        vp.text((x - 0.15, (zb + m.kondygnacje[0].rzedna) / 2 + 1.5), f"Pion {p.id} {o.rura if o else ''}", H_M, 90.0,
                "center", "bottom", "S-OPISY", style="bold")
        S.cleanout(vp, (x + 0.15, m.kondygnacje[0].rzedna + 1.0), 0.0, s_mm=2.4, label="Cz")
        base_pts.append((x, zb))
        for kid in p.kondygnacje:
            z0 = m.kondygnacja(kid).rzedna
            zz = z0 + 0.10
            lst = [q for q in p.przybory if q.kond == kid]
            if not lst:
                continue
            xe = x + 0.6 + 0.85 * len(lst)
            vp.line((x, zz), (xe - 0.45, zz + 0.02 * (xe - x)), "S-KANAL", pen="gruba", lt="CIAGLA")
            arrowhead(vp, (x + 0.35, zz + 0.007), (-1.0, -0.02), 2.0, 14, True, "S-KANAL")
            for j, q in enumerate(sorted(lst, key=lambda q: -(KATALOG[q.typ].dn_kan or 0))):
                xf = x + 0.9 + 0.85 * j
                zf = zz + 0.02 * (xf - x)
                of = odc.get(q.id)
                vp.line((xf, zf), (xf, z0 + 0.45), "S-KANAL", pen="srednia", lt="CIAGLA")
                vp.text((xf, z0 + 0.55), f"{SKR.get(q.typ, q.typ[:3].upper())}", H_S, 0.0, "center", "baseline",
                        "S-OPISY")
                # średnica obok podejścia (1 mm w lewo), nie na jego osi (weryfikacja C 2.5)
                vp.text((xf - 1.0 * vp.k, z0 + 0.28), f"Ø{of.rura.split()[-1] if of else ''}", H_S, 90.0, "left",
                        "bottom",
                        "S-OPISY")
            rid = lst[0].pom
            zb_o = odc.get(f"PZ_{rid}")
            if zb_o is not None:
                vp.text((x + 0.25, zz - 1.2 * k), f"Ø{zb_o.rura.split()[-1]}, i = {num(100 * zb_o.i, 1)} %", H_S, 0.0,
                        "left", "top", "S-OPISY")
    # kolektor pod płytą: łańcuch pionów → wyjście → studzienka
    kols = [o for o in kn.odcinki if o.rodzaj == "poziom"]
    pts = base_pts + [(x_end, E_z)]
    for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
        vp.line(a, b, "S-KANAL", pen="gruba", lt="KRESKOWA")
        o = kols[i] if i < len(kols) else None
        if o is not None:
            tag_leader(vp, pl, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2),
                       [f"{o.rura}, i = {num(100 * (o.i or 0.02), 1)} %, L = {num(o.L, 2)} m"], "S-OPISY",
                       radii=(5.0, 8.0, 12.0))
        tag_leader(vp, pl, a, [f"dno {fmt.level(a[1])}"], "S-OPISY", radii=(4.0, 7.0, 10.0))
    prz = next((o for o in kn.odcinki if o.rodzaj == "przykanalik"), None)
    zs = float(st.get("dno", E_z - 0.06))
    xs_ = x_end + 3.0
    vp.line((x_end, E_z), (xs_ - 0.21, zs), "S-KANAL", pen="gruba", lt="KRESKOWA")
    vp.rect(xs_ - 0.21, zs - 0.25, xs_ + 0.21, teren, "S-KANAL", pen="srednia", lt="CIAGLA")
    tag_leader(vp, pl, (x_end, E_z), [f"wyjście z budynku, dno {fmt.level(E_z)}"], "S-OPISY")
    if prz is not None:
        tag_leader(vp, pl, ((x_end + xs_) / 2, (E_z + zs) / 2), [f"przykanalik {prz.rura}, i = {num(100 * prz.i, 1)} %"],
                   "S-OPISY")
    tag_leader(vp, pl, (xs_, teren), ["studzienka SR1 Ø425", f"dno {fmt.level(zs)} → sieć wg PZT"], "S-OPISY",
               style="bold")
    leg.sym(lambda c, p: S.cleanout(c, p, 0.0, s_mm=2.4, label=""), "czyszczak na pionie (1,0 m nad posadzką)")
    leg.sym(lambda c, p: S.tag(c, p, "ZN", shape="circle", r_mm=2.0, h=1.8, layer="S-KANAL"),
            "zawór napowietrzający pionu")
    from .schematy import rozsun_napisy
    _maski(vp)
    rozsun_napisy(vp)
    res.column_blocks.append(("legenda", legenda_arkusza(ctx, leg)))
    rows = [[o.id, o.rodzaj, f"Ø{o.rura.split()[-1]}", num(o.sum_DU, 1), num(o.Q, 2), num(o.L, 2)] for o in kn.odcinki
            if o.rodzaj in ("pion", "poziom", "przykanalik")]
    res.column_blocks.append(("tab", table_block("PIONY I PRZEWODY ODPŁYWOWE (obliczenia PN-EN 12056-2)",
                                                  [("Odcinek", 24), ("Rodzaj", 30), ("DN", 18), ("ΣDU", 18),
                                                   ("Q [l/s]", 20), ("L [m]", 18)], rows,
                                                  align=["left", "left", "center", "right", "right", "right"])))
    res.notes += ["Rozwinięcie kanalizacji: oś pionowa w skali rzędnych (1:50), oś pozioma umowna. Podejścia pokazano "
                  "schematycznie (kolejność przyborów wg średnic), rzędne dna przewodów pod płytą z obliczeń "
                  "(lamela.obliczenia.sanitarne.kanalizacja).",
                  "Wentylacja pionów: " + "; ".join(f"{w['pion']} — {w['wentylacja']}" for w in kn.wentylacja) + "."]


# ================================================================================================ woda
COL = {"ZW": "WZ", "CWU": "WC", "CYRK": "CYRK"}


def rozwiniecie_wody(vp, ctx, W, res):
    m = ctx.model
    wo = W.woda
    k = vp.k
    pl = Placer(k)
    kids = [kk.id for kk in m.kondygnacje]
    z0 = m.kondygnacje[0].rzedna
    odc = wo.odcinki
    by_do = {o.do: o for o in odc}
    piony = [p for p in wo.piony]
    xs = {p.id: 10.0 + i * 7.0 for i, p in enumerate(piony)}
    x_end = 10.0 + len(piony) * 7.0 + 1.0
    _poziomy(vp, pl, m, -1.0, x_end)
    leg = Legenda()
    leg.line("S-WODA", "Wz — woda zimna", pen="srednia")
    leg.line("S-CWU", "Wc — ciepła woda użytkowa", lt="KRESKOWA", pen="srednia")
    leg.line("S-CYRK", "Cyrk — cyrkulacja c.w.u.", lt="PUNKTOWA_KROTKA", pen="cienka")
    zm = {"ZW": z0 - 0.40, "CWU": z0 - 0.90, "CYRK": z0 - 1.40}     # przewody rozprowadzające (pod posadzką P0)

    def line(a, b, med, pen="srednia"):
        ly, _d, lt = S.media(COL[med])
        vp.line(a, b, ly, pen=pen, lt=lt)

    def lab(pos, txt, rot=0.0):
        vp.text(pos, txt, H_S, rot, "center", "bottom", "S-OPISY")
    # przyłącze, zestaw wodomierzowy, rozdzielacz Wz, zasobnik
    zw = zm["ZW"]
    line((-1.0, zw), (4.0, zw), "ZW", pen="gruba")
    arrowhead(vp, (-1.0, zw), (-1.0, 0.0), 2.5, 12, True, "S-WODA")
    prz = next((o for o in odc if o.typ == "przylacze"), None)
    lab((0.2, zw - 3.5 * k), f"przyłącze {prz.rura if prz else ''}")
    for x, fn in ((1.0, lambda p: S.valve(vp, p, 0.0, s_mm=2.6)), (1.6, lambda p: S.filter_(vp, p, 0.0, s_mm=3.0)),
                  (2.3, lambda p: S.water_meter(vp, p, 0.0, s_mm=4.0, label="WM")),
                  (3.0, lambda p: S.check_valve(vp, p, 0.0, s_mm=2.6)), (3.6, lambda p: S.valve(vp, p, 0.0, s_mm=2.6))):
        fn((x, zw))
    wm = wo.wodomierz
    tag_leader(vp, pl, (2.3, zw), [f"WM DN{wm['DN']} Q3 = {num(wm['Q3'], 1)} m³/h, F, EA (PN-EN 1717), RED"], "S-OPISY",
               radii=(9.0, 13.0, 18.0))
    vp.line((4.0, zw - 0.25), (4.0, z0 + 1.1), "S-URZADZENIA", pen="gruba", lt="CIAGLA")
    vp.text((3.9, z0 + 0.5), "rozdzielacz Wz", H_S, 90.0, "center", "bottom", "S-OPISY")
    # zasobnik
    zx = 6.2
    vp.rect(zx - 0.35, z0 + 0.9, zx + 0.35, z0 + 2.4, "S-URZADZENIA", pen="srednia", lt="CIAGLA")
    vp.text((zx, z0 + 1.65), f"{wo.cwu['V_zas']} dm³", H_S, 90.0, "center", "middle", "S-OPISY")
    lab((zx, z0 + 2.5), "zasobnik c.w.u.")
    t0zas = next((o for o in odc if o.od == "T0" and o.do == "ZAS"), None)
    line((4.0, z0 + 1.0), (zx - 0.35, z0 + 1.0), "ZW")
    if t0zas is not None:
        lab(((4.0 + zx) / 2 - 0.2, z0 + 1.0 + 1.0 * k), f"Wz {rura_krotko(t0zas.rura)}")
    line((zx, z0 + 2.4), (zx, z0 + 2.7), "CWU")
    line((zx, z0 + 2.7), (zx + 0.55, z0 + 2.7), "CWU")
    line((zx + 0.55, z0 + 2.7), (zx + 0.55, zm["CWU"]), "CWU")
    lab((zx + 0.25, z0 + 2.75), "TZM")
    if wo.cwu.get("cyrkulacja", "brak") != "brak":
        line((zx + 0.8, zm["CYRK"]), (zx + 0.8, z0 + 1.2), "CYRK", pen="cienka")
        line((zx + 0.8, z0 + 1.2), (zx + 0.35, z0 + 1.2), "CYRK", pen="cienka")
        S.pump(vp, (zx + 0.8, z0 + 0.4), 90.0, s_mm=3.0)
    cyrk = wo.cwu.get("cyrkulacja", "brak") != "brak"
    # główne do pionów i piony
    for ip, pn in enumerate(piony):
        x = xs[pn.id]
        top = max(kids.index(kk) for kk in pn.kondygnacje)
        for med, dxm, src in (("ZW", 0.0, 4.0), ("CWU", 0.3, zx + 0.55), ("CYRK", 0.6, zx + 0.8)):
            tag = {"ZW": "Z", "CWU": "C", "CYRK": "C"}[med]
            node = f"{pn.id}{tag}@{kids[0]}"
            o = by_do.get(node) if med != "CYRK" else by_do.get(f"{pn.id}C@{kids[0]}")
            if o is None or (med == "CYRK" and not cyrk):
                continue
            z = zm[med] - 0.12 * ip           # osobne przewody z rozdzielaczy do każdego pionu
            if ip:
                line((src, zm[med]), (src, z), med, pen="gruba" if med == "ZW" else "srednia")
            line((src, z), (x + dxm, z), med, pen="gruba" if med == "ZW" else "srednia")
            txt = f"{'Wz' if med == 'ZW' else 'Wc' if med == 'CWU' else 'Cyrk'} " + (rura_krotko(o.rura) if med != "CYRK"
                                                                                        else "16×2,0")
            lab((x - 2.2 + dxm * 3, z + 1.0 * k), txt)
            z_hi = m.kondygnacje[top].rzedna + (0.3 if med != "CYRK" else 0.5)
            line((x + dxm, z), (x + dxm, z_hi), med)
            for i in range(1, top + 1):
                up = next((q for q in odc if q.typ == "pion" and q.do == f"{pn.id}{tag}@{kids[i]}"), None)
                if up is not None and med != "CYRK":
                    zc = (m.kondygnacje[i - 1].rzedna + m.kondygnacje[i].rzedna) / 2
                    vp.text((x + dxm - 0.05, zc), f"{rura_krotko(up.rura)}", H_S, 90.0, "center", "bottom", "S-OPISY")
        vp.text((x - 0.4, z0 + 1.6), f"Pion {pn.id}", H_M, 90.0, "center", "bottom", "S-OPISY", style="bold")
        # gałęzie do przyborów
        for kid in pn.kondygnacje:
            zk = m.kondygnacja(kid).rzedna
            lst = [p for p in pn.przybory if p.kond == kid and (p.t.qn_zw > 0 or p.t.qn_cw > 0)]
            for j, p in enumerate(lst):
                xf = x + 1.3 + 0.8 * j
                for med, dxm, zz in (("ZW", 0.0, zk + 0.3), ("CWU", 0.3, zk + 0.55)):
                    if (med == "ZW" and p.t.qn_zw <= 0) or (med == "CWU" and p.t.qn_cw <= 0):
                        continue
                    if j == 0:
                        line((x + dxm, zz), (x + 1.3 + 0.8 * (len(lst) - 1) + dxm, zz), med)
                    line((xf + dxm, zz), (xf + dxm, zk + max(p.h_wyl, 0.9)), med, pen="cienka")
                vp.text((xf + 0.15, zk + max(p.h_wyl, 0.9) + 0.08), SKR.get(p.typ, p.typ[:3].upper()), H_S, 0.0,
                        "center", "baseline", "S-OPISY")
    # zawory ogrodowe (odejścia z rozdzielacza)
    taps = [o for o in odc if o.od == "T0" and o.do.startswith("ZAW")]
    for i, o in enumerate(taps):
        x = 7.6 + i * 0.9
        zt = z0 + 0.2 + 0.15 * i
        line((4.0, zt), (x, zt), "ZW", pen="cienka")
        line((x, zt), (x, z0 + 0.9), "ZW", pen="cienka")
        S.valve(vp, (x, z0 + 0.9), 90.0, s_mm=2.4)
        vp.text((x + 0.12, z0 + 1.05), f"ZO {rura_krotko(o.rura)}", H_S, 90.0, "left", "bottom", "S-OPISY")
    from .schematy import rozsun_napisy
    _maski(vp)
    rozsun_napisy(vp)
    leg.sym(lambda c, p: S.water_meter(c, p, 0.0, s_mm=4.0, label="WM"), "wodomierz; F — filtr; EA — zawór "
            "antyskażeniowy (zwrotny); zawory odcinające")
    res.column_blocks.append(("legenda", legenda_arkusza(ctx, leg)))
    pk = wo.punkt_krytyczny
    res.notes += ["Rozwinięcie instalacji wodociągowej: oś pionowa w skali rzędnych, oś pozioma umowna; wysokości "
                  "wypływów wg PN-92/B-01706 (praktyka projektowa). Średnice z obliczeń (lamela.obliczenia.sanitarne."
                  f"woda); punkt krytyczny {pk.przybor.id} ({pk.medium}), p_wym = {num(pk.p_wym, 0)} kPa.",
                  "Oznaczenia przyborów: WC — miska ustępowa, UMY — umywalka, NAT — natrysk, WAN — wanna, ZL — "
                  "zlewozmywak, ZLG — zlew gospodarczy, ZM — zmywarka, PR — pralka, ZO — zawór ogrodowy."]


def _maski(vp, m: float = 0.3):
    """Maska pod opisami rozwinięć: linie przewodów nie przecinają napisów (weryfikacja C 2.5)."""
    from ...draft.core import PText
    for p in vp.prims:
        if isinstance(p, PText) and p.layer == "S-OPISY" and not p.mask:
            p.mask = m
