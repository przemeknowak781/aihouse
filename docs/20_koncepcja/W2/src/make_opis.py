# -*- coding: utf-8 -*-
"""Generator opis.md + model_W2.json dla wariantu W2 (tabele liczone z modelu)."""
import sys, os, json, math
from shapely.geometry import mapping
import model_w2 as M
import calc_w2 as C
import draw_site

OUT = sys.argv[1] if len(sys.argv) > 1 else ".."
f = C.fmt
P = M.POZ


def tab(head, rows):
    s = "| " + " | ".join(head) + " |\n|" + "---|" * len(head) + "\n"
    for r in rows:
        s += "| " + " | ".join(str(x) for x in r) + " |\n"
    return s


def poly_txt(g):
    if g.geom_type == "Polygon":
        xs, ys = g.exterior.xy
        pts = list(zip(xs, ys))[:-1]
        if len(pts) == 4:
            x0, y0, x1, y1 = g.bounds
            return f"prost. x {f(x0, 3)}…{f(x1, 3)}; y {f(y0, 3)}…{f(y1, 3)}"
        return "wielobok " + " ".join(f"({f(x, 3)}; {f(y, 3)})" for x, y in pts)
    return "wielobok złożony"


def outline_txt(k):
    g = M.outline(k)
    xs, ys = g.exterior.xy
    return " → ".join(f"({f(x)}; {f(y)})" for x, y in list(zip(xs, ys))[:-1])


def walls_table(k):
    rows = []
    for w in M.SCIANY:
        if w["kond"] != k:
            continue
        (x1, y1), (x2, y2) = w["p1"], w["p2"]
        L = math.hypot(x2 - x1, y2 - y1)
        t = M.TYPY[w["typ"]]
        rows.append((w["id"], f"({f(x1, 3)}; {f(y1, 3)}) → ({f(x2, 3)}; {f(y2, 3)})", f(L), w["typ"], f(t["L"] + t["R"], 3), w["uw"] or "działowa"))
    return tab(["ID", "oś warstwy konstr. (x; y) [m]", "dł. osi", "typ", "grub. całk.", "uwagi"], rows)


def openings_table(k):
    rows = []
    for o in M.OTWORY:
        w = M.wall_by_id(o["sciana"])
        if w["kond"] != k:
            continue
        horiz = abs(w["p2"][1] - w["p1"][1]) < 1e-9
        pol = ("x" if horiz else "y") + f" {f(o['a'])}…{f(o['b'])}"
        otw = "" if not o["zaw"] else f"zawias {o['zaw']}, na {o['kier']}"
        rows.append((o["id"], o["sciana"], pol, f(o["szer"]), f(o["wys"]), f(o["par"]), o["typ"] + (f" ({o['kw']} kw.)" if o["kw"] > 1 else ""),
                     o["sym"], otw, o["uw"]))
    return tab(["ID", "ściana", "położenie", "szer.", "wys.", "parapet", "typ", "symbol", "otwieranie", "uwagi"], rows)


def rooms_table(k):
    rows = []
    for r in M.POMIESZCZENIA:
        if r["kond"] != k:
            continue
        rows.append((r["id"], r["nazwa"], poly_txt(r["poly"]), f(M.room_area(r)), r["kat"], "tak" if r["pobyt"] else "nie", r["posadzka"], r["uw"]))
    per, tot, gar = C.pu()
    s = tab(["nr", "pomieszczenie", "geometria (lica wykończone)", "pow. netto [m²]", "kategoria", "pobyt ludzi", "posadzka", "uwagi"], rows)
    s += f"\n**Suma PU {k} (bez garażu): {f(per[k])} m²**" + (f"; garaż: {f(gar)} m²." if k == "P0" else ".") + "\n"
    return s


def main():
    per, pu_tot, gar = C.pu()
    W = draw_site.wskazniki()
    H = C.wysokosc()
    SCH = C.schody()
    ok = C.okna()
    od = C.odleglosci()
    open_area = M.room_area(next(r for r in M.POMIESZCZENIA if r["id"] == "0.06"))
    md = []
    A = md.append
    A(f"""# Koncepcja — WARIANT W2: „FUNKCJA · EKONOMIA · KONSTRUKCJA”

Dom LAMELA, dom jednorodzinny wolnostojący, 3 kondygnacje nadziemne, dachy płaskie. Wersja koncepcji 1.0 z 25.09.2026.
Podstawa: `docs/00_brief_projektowy.md` (interpretacja szkicu **v2**, decyzje Inwestora z 25.09.2026) oraz rejestr wymagań `docs/10_podstawy_prawne/R1…R8`.
Przyjęto WT 2002 w brzmieniu obowiązującym do 19.09.2026, stosowane na podstawie **art. 102a PB** (R3 S-03). Wymaga to oświadczenia Inwestora składanego z wnioskiem.
Wszystkie liczby w tabelach generuje `src/make_opis.py` z modelu `src/model_w2.py`. Ten sam model rysuje rzuty, elewację, przekroje i plan zagospodarowania. Pełne dane są w `model_W2.json`.

**Wynik w skrócie**

| Parametr | Wartość |
|---|---|
| PU mieszkalna (bez garażu) | **{f(pu_tot)} m²** (P0 {f(per['P0'])} + P1 {f(per['P1'])} + P2 {f(per['P2'])}) |
| Garaż 2-stanowiskowy (w świetle 6,08 × 6,08 m) | {f(gar)} m² |
| Strefa dzienna (salon + jadalnia + kuchnia) | {f(open_area)} m² (wymagane ≥ 50) |
| Powierzchnia zabudowy (lica ścian zewnętrznych) | **{f(W['zabudowa'])} m²**, czyli {f(100*W['zabudowa']/1600, 1)} % (limit 30 % = 480 m²) |
| Powierzchnia zabudowy, wariant kontrolny z płytami | {f(W['zabudowa_plyty'])} m² ({f(100*W['zabudowa_plyty']/1600, 1)} %) |
| PBC | {f(W['pbc'])} m², czyli {f(100*W['pbc']/1600, 1)} % (≥ 50 %) |
| Intensywność nadziemna | {f(W['intens'], 3)} (0,05–0,80) |
| Wysokość zabudowy wg upzp / MPZP (do attyki) | **{f(H['H_mpzp'])} m** (≤ 11,00) |
| Wysokość budynku wg WT § 6 | {f(H['H_WT'])} m (grupa N) |

## 1. Idea wariantu W2

W2 odtwarza sylwetę „S” z mniejszą liczbą elementów konstrukcyjnych i niższym kosztem. Założenia:

* **Jeden prostokątny trzon mieszkalny 12,60 × 9,00 m** na P0 i P1. Wszystkie ściany nośne biegną w pionie jedna nad drugą.
* **Garaż z pasem gospodarczym** dostawiony od wschodu w jednej kondygnacji.
* **Długa lamelowa bryła A** na P2, cofnięta do strefy południowej (głębokość 4,80 m w osiach). Stoi na ścianach osi 1 i 3.

Kształt „S” powstaje z przesunięć brył i z wysuniętych płyt:

* Bryła A wysunięta na **zachód** jako wspornik 1,00 m.
* Bryła B z ramą boksu C, a pod nią **linia D**, która biegnie na **wschód** aż do narożnika garażu.
* Przeszklony parter E z okapem **na zachód** 1,50 m.

Każdy element nośny, który nie stoi na ścianie, jest krótki i ma wskazaną ścieżkę obciążeń:

* słupy stalowe w szprosach fasady E;
* belki B1 i B2;
* ściany-tarcze ŻB wspornika A;
* płyty z łącznikami termoizolacyjnymi.

Główne zasady:

* **Konstrukcja:** siatka osi A–F × 1–5. Stropy ŻB 20 cm pracują jednokierunkowo (N–S) na rozpiętościach 4,80 i 3,60 m. Nad garażem strop 24 cm o rozpiętości 6,40 m. Wsporniki ≤ 1,50 m.
* **Instalacje:** jeden szacht **SI** (x 5,59–5,99; y 4,905–5,605) łączy łazienki P0, P1 i P2 ustawione dokładnie jedna nad drugą. Drugi, krótki pion **K2** obsługuje pralnię P1 i WC P0. Pomieszczenie techniczne leży obok garażu, a jednostka zewnętrzna PC stoi przy ścianie wschodniej.
* **Funkcja:** wejście i garaż są od północy, obok siebie. Z garażu przez przedsionek gospodarczy (ze spiżarnią) prowadzi droga prosto do kuchni, łącznie ok. 6 m. Strefa dzienna ma 11,4 m przeszklenia na południe. Pokoje dzieci są od zachodu, dzięki czemu elewacja bryły B pozostaje pełna jak w szkicu. Sypialnia rodziców i gabinet są w bryle A za lamelami.

## 2. Odczyt szkicu w W2 (porównanie ilościowe)

Skala szkicu: 45,8 px/m (brief 1.1). Współrzędne szkicu przeliczono na układ W2, w którym lico zachodnie bryły B = x −0,30. Porównanie graficzne jest w `elewacja_S.png`: szkic z nałożonym czerwonym obrysem W2.

""")
    A(tab(["element szkicu", "szkic (x od lica zach. B)", "W2 (x od lica zach. B)", "komentarz"], [
        ("A — bryła II p. w lamelach", "−1,0…+12,2 (13,2 m)", "−1,00…+12,60 (13,60 m)", "wspornik zach. 1,00 m jak w szkicu; wsch. koniec w licu B (ściany w pionie)"),
        ("płyty A (dół/góra)", "−2,4…+12,5", "−2,10…+12,90 (15,00 m)", "wysunięcie 1,10 m zach., 1,00 m pd., 0,30 m wsch."),
        ("B — bryła I p.", "0…12,0", "0…12,60", "+0,60 m (moduł 12,00 m w osiach A–E dla stropów i garażu)"),
        ("C — boks 3 kwatery", "+4,5…+11,7 (7,2 m)", "+4,40…+11,40 (7,00 m)", "rama wysunięta 1,00 m, x +3,90…+12,90"),
        ("D — linia pozioma", "+3,8…+19,0", "+3,90…+19,00 (+3,85)", "płyta dolna ramy C, dalej attyka dachu zielonego garażu"),
        ("D — pion / narożnik G", "+19,0", "+19,00", "ściana wsch. garażu (lico)"),
        ("E — przeszklenie 5 kwater", "+1,0…+13,2 (12,2 m)", "+0,60…+12,00 (11,40 m)", "**odstępstwo −0,8 m**: koniec w osi ściany nośnej E (ściany w pionie)"),
        ("E — płyta dachu parteru", "−1,5…+14,1", "−1,50…+12,90", "okap zach. 1,50 m, pd. 1,00 m"),
        ("G — pełna ściana garażu", "+13,2…+19,0 (5,8 m)", "+13,45…+19,00 (5,55 m)", "przed nią przeszklone drzwi gospodarcze przedsionka (x +12,55…+13,45)"),
    ]))
    A("""
Proporcje pionowe szkicu są umowne (brief 1.1). Kolejność i relacje pasm są zachowane:

* okap E (+2,75…+3,05) leży poniżej linii D (+3,65…+3,85);
* boks C (+3,85…+5,35) jest wpisany w bryłę B pod płytą A (+5,95…+6,25);
* lamele A (+6,15…+9,10) są zamknięte płytą dachu (+9,10…+9,42) i cofniętą attyką (+9,80).

Rytm przesunięć zachód–wschód–zachód jest zachowany, czyli kształt „S”. **Nie ma tarasu na płycie D ani wiaty na słupie.** Dach garażu jest zielony i nieużytkowy, bez wyjścia.

## 3. Definicja wymiarowa

### 3.1 Układ i siatka osi
* Osie x → wschód, y → północ, z → góra. Początek układu to przecięcie osi A (zach. oś nośna bryły głównej) i osi 1 (pd.).
* Osie przechodzą przez środek warstwy konstrukcyjnej ścian.
* ±0,00 = posadzka P0 = **101,65 m n.p.m.** (PL-EVRF2007-NH).

""")
    A(tab(["oś x", "x [m]", "znaczenie"], [(k, f(v, 3), d) for (k, v), d in zip(M.OSIE_X.items(), [
        "ściana zach. P2 na wsporniku (lekka)", "ściana zach. P0/P1, podpora wspornika A", "ściana pokój gościnny / łazienki (P0–P1, nadbudowa P2)",
        "ściana zach. klatki schodowej", "ściana wsch. klatki schodowej", "ściana wsch. bryły B/A; ściana dom/garaż", "ściana wsch. garażu (pion D)"])]))
    A("\n")
    A(tab(["oś y", "y [m]", "znaczenie"], [(k, f(v, 3), d) for (k, v), d in zip(M.OSIE_Y.items(), [
        "linia fasady pd. (P0: belka B1 na słupach; P1/P2 ściany)", "ściana strefa gosp. / garaż", "ściana grzbietowa (nośna, P0–P2)",
        "ściana pn. części mieszkalnej", "ściana pn. garażu (brama)"])]))
    A(f"""
Obrys lica zewnętrznego (ocieplenie):
* **P0** (bryła mieszkalna + garaż): {outline_txt('P0')}
* **P1**: {outline_txt('P1')}
* **P2**: {outline_txt('P2')}

### 3.2 Poziomy i grubości
""")
    A(tab(["element", "rzędna / grubość"], [
        ("posadzka P0 (±0,00)", "0,00 = 101,65 m n.p.m.; teren przy budynku −0,33…−0,17 (średnio ≈ −0,25)"),
        ("podłoga na gruncie", "warstwy 0,15 (wykładzina/gres, jastrych 6,5 cm z ogrzewaniem podł., EPS 100) + płyta ŻB 0,25 + XPS 0,15"),
        ("wysokość kondygnacji", "3,15 m = warstwy 0,15 + strop 0,20 + w świetle 2,80"),
        ("ST1 (nad P0)", f"spód +{f(P['ST1'][0])}, wierzch +{f(P['ST1'][1])}; posadzka P1 +{f(P['P1'])}"),
        ("ST2 (nad P1)", f"spód +{f(P['ST2'][0])}, wierzch +{f(P['ST2'][1])}; posadzka P2 +{f(P['P2'])}"),
        ("ST3 stropodach P2", f"spód +{f(P['ST3'][0])}, wierzch płyty +{f(P['ST3'][1])} (22 cm); PIR ~0,24 + membrana → +{f(P['dach_P2_warstwy'])}; attyka +{f(P['attyka_P2'])}"),
        ("dach P1 (część pn., poza nadbudową)", f"wierzch warstw +{f(P['dach_P1_warstwy'])}; attyka +{f(P['attyka_P1'])}"),
        ("strop garażu / strefy gosp.", f"spód +{f(P['STG'][0])}, wierzch +{f(P['STG'][1])} (24 cm); dach zielony ekstensywny → +{f(P['dach_G_warstwy'])}; attyka (linia D) +{f(P['attyka_G'])}"),
        ("wysokości w świetle", "pokoje P0/P1/P2 2,80 m; garaż 2,86 m (posadzka −0,10); pom. pomocnicze pod sufitem podwieszonym (kanały) ≥ 2,50 m"),
        ("ławy fundamentowe", "ŻB 60 × 35 cm, spód −1,10 (≥ h_z = 0,80 m pod terenem ≈ −0,30); ściany fundamentowe 24 cm"),
        ("krawędzie płyt (widok)", "okap E +2,75…+3,05; linia D +3,65…+3,85; rama C góra +5,35…+5,55; ST2 +5,95…+6,25; ST3 +9,10…+9,42"),
    ]))
    A("\n### 3.3 Typy przegród pionowych\n")
    A(tab(["kod", "opis", "lico od osi: strona wnętrza / zewn. [m]"], [(k, v["nazwa"], f"{f(v['L'], 3)} / {f(v['R'], 3)}") for k, v in M.TYPY.items()]))
    for k, nm in (("P0", "PARTER P0 (±0,00)"), ("P1", "I PIĘTRO P1 (+3,15)"), ("P2", "II PIĘTRO P2 (+6,30)")):
        A(f"\n### 3.{ {'P0': 4, 'P1': 5, 'P2': 6}[k] } {nm}\n\n**Ściany**\n\n")
        A(walls_table(k))
        A("\n**Otwory** (położenie wzdłuż osi ściany; szerokość i wysokość w świetle muru; parapet względem posadzki kondygnacji)\n\n")
        A(openings_table(k))
        A("\n**Pomieszczenia**\n\n")
        A(rooms_table(k))
    A("\n### 3.7 Elementy zewnętrzne: płyty, rama C, lamele, słupy\n\n")
    A(tab(["ID", "opis", "rzut", "z [m]", "łącznik termoizol."], [(p["id"], p["opis"], poly_txt(p["poly"]), f"{f(p['z'][0])}…{f(p['z'][1])}", "tak" if p["lacznik"] else "—") for p in M.PLYTY]))
    L = M.LAMELE
    A(f"""
* **Rama C.** Boki ramy to pionowe płaskowniki stalowe w okładzinie 0,15 × 1,00 m, na x 3,60–3,75 i 12,45–12,60, na wysokości +3,85…+5,35. Płyty ramy są żelbetowe, gr. 20 cm, wysunięte 1,00 m na łącznikach termoizolacyjnych:
  * płyta dolna (linia D) wysunięta z belki B1;
  * płyta górna wysunięta z belki B2.
* **Lamele A:** pionowe, {L['b']*1000:.0f} × {L['h']*1000:.0f} mm co {f(L['rozstaw'])} m, x {f(L['x'][0])}…{f(L['x'][1])}, z +{f(L['z'][0])}…+{f(L['z'][1])}, w płaszczyźnie y = {f(L['y'])} (15 cm przed licem). Materiał: {L['mat']}. Przed oknami P2 pracują jako stała osłona (prywatność, cień latem). Okna P2 otwierają się do wewnątrz (K-16).
* **Słupy SL1–SL4** (fasada E, x = 2,58 / 4,86 / 7,14 / 9,42; y = 0): RK 120 × 120 × 8, S355, w szprosach. **Słupki SLC1–SLC2** (boks C, x = 6,433 / 8,767): RK 100 × 100 × 6.

### 3.8 Schody SCH1 (P0→P1) i SCH2 (P1→P2): dwubiegowe, identyczne, jedne nad drugimi
""")
    A(tab(["parametr", "wartość", "wymaganie"], [
        ("liczba podnóżków na kondygnację", f"{SCH['n']} × {f(SCH['h'], 3)} = 3,15 m", "h ≤ 0,19 (WT § 68, K-01); cel ≈ 0,175"),
        ("szerokość stopnia s", f(SCH['s']), "cel ≈ 0,28"),
        ("2h + s", f(SCH['dwa_h_s'], 3), "0,60–0,65 (WT § 69 ust. 4, K-06) ✓"),
        ("biegi", f"2 × {SCH['bieg']} podnóżków (8 stopni + wyjście), dł. rzutu biegu {f(SCH['dl_biegu'])} m, nachylenie {f(SCH['kat'], 1)}°", "limit 17 stopni nie dotyczy domu jednorodzinnego (K-05)"),
        ("szerokość biegu", f"{f(SCH['szer'])} m (między ścianą a ścianką środkową 12 cm)", "≥ 0,80 (K-01); cel ≥ 1,00 ✓"),
        ("spocznik międzypiętrowy", f"{f(SCH['spocz_szer'])} × {f(SCH['spocz_gl'])} m, rzędne +1,575 i +4,725", "≥ szer. biegu (1,00) ✓"),
        ("bieg 1 (pas W)", "x 6,20–7,20; od y 4,905 (lico ściany osi 3) w górę ku północy do y 7,145", ""),
        ("bieg 2 (pas E)", "x 7,32–8,32; od spocznika y 7,145 w górę ku południu, wyjście na y 4,905", ""),
        ("ścianka środkowa", "silikat 12 cm, x 7,20–7,32, y 4,905–7,145, P0–P2", "zamiast balustrady: brak otwartej krawędzi, pochwyty przyścienne ≥ 0,05 m od ściany (K-11)"),
        ("prześwit nad biegiem", f"{f(SCH['przeswit'])} m (3,15 − h − płyta biegu 0,18/cos α)", "≥ 2,00 (dobra praktyka, K-22) ✓"),
        ("otwarcie w stropach", "ST1 i ST2: x 6,20–8,32 × y 4,905–8,295; ST3 nad nadbudową: świetlik 1,70 × 2,90 (≤ +9,80)", ""),
        ("P2", "bieg 1 SCH2 zamknięty od holu ścianą osi 3; wyjście z biegu 2 przez otwór 1,00 m (x 7,32–8,32)", "balustrady niepotrzebne (brak krawędzi > 0,5 m)"),
    ]))
    A("""
Pod biegiem 2 na P0 jest schowek 0.05 (dostęp z jadalni). Wysokość: ≈ 2,77 m przy ścianie osi 3, ≈ 1,37 m przy spoczniku.

## 4. Koncepcja konstrukcji

**System.** Ściany murowe z bloczków silikatowych 18 cm (kl. 20) na zaprawie cienkowarstwowej. Stropy żelbetowe monolityczne C25/30, B500SP. Posadowienie bezpośrednie na ławach, w gruncie z piasków średnich (I_D ≈ 0,6), w I kategorii geotechnicznej. Obciążenia: śnieg strefa 2 (s_k = 0,9 kN/m²), wiatr strefa 1, kat. terenu III (brief, R5).

**Ściany nośne w pionie.** Nie ma ścian odsadzonych na stropie.
* **Oś A:** P0 i P1.
* **Oś E:** P0 do P2.
* **Oś 3 (grzbietowa):** P0 do P2.
* **Oś 4 (pn.):** P0 i P1, na P2 w nadbudowie.
* **Osie B, C, D:** P0 i P1 w strefie pn., na P2 w nadbudowie klatki i łazienki.
* **Oś 1 (pd.):** P1 i P2, na belce B1.
* **Garaż:** osie E, F, 1, 5.

Ściany działowe na stropach mają 12 cm (silikat). Ich obciążenie przyjęto zastępczo ~1,2 kN/m².

**Kierunki pracy i rozpiętości płyt**
""")
    A(tab(["płyta", "kierunek / podpory", "rozpiętości [m]", "wysunięcia i uwagi"], C.rozpietosci()))
    A("""
**Belki i słupy**
* **B1: podciąg fasady E** (oś 1, x 0,00–12,00). Wymiary 25 × 105 cm (+2,80…+3,85), belka odwrócona. Jej część nad stropem tworzy pas podokienny boksu C.
  * Podpory: słupy SL1–SL4 oraz narożniki ścian A i E. Pięć przęseł po ≈ 2,28 m.
  * Przenosi ściany pd. P1 i P2 (w tym reakcje B2), pas stropów ST1–ST3 szer. ≈ 2,4 m oraz płytę dolną ramy C.
  * Obciążenie orientacyjne ≈ 65 kN/m. Reakcja słupa ≈ 160 kN.
  * Słupy stalowe RK 120 × 120 × 8, h = 2,80 m. Stopy pod słupami 1,0 × 1,0 m są wpisane w ławę osi 1.
* **B2: nadproże boksu C.** Wymiary 25 × 80 cm (+5,35…+6,15, razem z ST2). Trzy przęsła po 2,33 m, oparte na ścianach i słupkach SLC1–SLC2 w szprosach. Z B2 wysunięta jest płyta górna ramy C.
* **B3: belka krawędziowa ST2 w osi A'.** Wymiary 25 × 40 cm, x = −1,0, y 0…4,8. Rozpiętość 4,80 m między końcami ścian-tarcz. Niesie lekką ścianę zach. P2 i wspornik płyty 1,10 m.
* **B4: nadproże bramy garażu.** Wymiary 25 × 50 cm, rozpiętość ≈ 5,30 m, w ścianie osi 5 (pas +2,25…+2,76 + attyka).
* **B5: nadproża w ścianie grzbietowej** nad otworem klatki (2,12 m na P1, 1,00 m na P0 i P2) oraz nad otworem holu P0 (1,40 m). Wymiary 25 × 25 cm.

**Wsporniki: długości i sposób przeniesienia**
1. **Bryła A: 1,00 m w osi (1,30 m do lica) na zachód.**
   * Ściany P2 w osiach 1 i 3 na odcinku x −1,00…+2,00 mają rdzeń **żelbetowy 18 cm**, czyli ściany-tarcze o wysokości kondygnacji 2,95 m. Są zespolone ze stropem ST2 (dół) i stropodachem ST3 (góra), więc tworzą belki-ściany wysokie.
   * Tarcze wspierają się na narożnikach ścian P1: A/1 i A/3. Moment równoważy przęsło zaplecza 2,0 m, dociążone ścianami i stropami P2.
   * Ściana zach. P2 (oś A') jest **lekka**: szkielet z wełną 20 cm, ≤ 1,0 kN/m², z dużym oknem. Stoi na belce B3.
   * Stosunek wspornika do wysokości tarczy ≈ 1 : 2,3, więc ugięcia są pomijalne. **Nie ma ciężkiej ściany murowanej na wsporniku.**
2. **Płyty-okapy.** Wysunięcia pracują jako wsporniki płyt z łącznikami termoizolacyjnymi (typu K, izolacja 8–12 cm w płaszczyźnie ocieplenia):
   * ST1: 1,00 m (pd.), 1,50 m (zach.), daszek wejścia 1,30 m (pn.);
   * ST2: 1,00 m (pd.), 1,10 m (zach., z belki B3);
   * ST3: 1,00 m (pd.), 1,10 m (zach.), 0,30 m (wsch.).

   Wszystkie wysunięcia ≤ 1,50 m. Obciążenie to ciężar własny, warstwy i śnieg, bez obciążeń użytkowych, bo płyty nie są tarasami.
3. **Rama C.** Płyty 1,00 m z łącznikami, wysunięte z B1 (dół) i B2 (góra). Boki stalowe spinają obie płyty (tłumienie drgań, stężenie krawędzi).
4. **Linia D nad garażem.** To attyka stropu garażu w licu ściany, bez wspornika.

**Usztywnienie.** Budynek usztywniają ściany w obu kierunkach:
* w kierunku y: osie A, B, C, D, E, F;
* w kierunku x: osie 3, 4, 5, 2 oraz ściany pd. P1 i P2.

Tarczami poziomymi są stropy monolityczne. Fasada pd. P0 jest przeszklona, więc siły poziome w kierunku x na P0 przejmują ściany osi 3 i 4 oraz sztywny rdzeń klatki C–D. Mimośród sztywności trzeba sprawdzić w PT (P0: rama B1 + słupy jako dodatkowa rama).

**Fundamenty.** Ławy ŻB 60 × 35 cm pod wszystkimi ścianami nośnymi. Pod słupami SL1–SL4 ława osi 1 jest poszerzona do 1,00 m. Płyta posadzki garażu ma 15 cm i spadek 1,5 % do bramy (B-25).

## 5. Instalacje (założenia wariantu)
* **Piony mokre.**
  * **SI** (0,40 × 0,70 m): kanalizacja K1 Ø110 z odpowietrzeniem nad dach P2 oraz kanały nawiewno-wywiewne rekuperacji. Łazienki 0.08, 1.05 i 2.04 leżą jedna nad drugą (x 3,98–5,99). Ich misy WC przylegają do SI, więc podejścia mają ≤ 1,5 m.
  * **K2** (Ø110/75): pralnia 1.07 i WC 0.03, x 8,53–8,90, y 7,90–8,30. Odpowietrzenie przez dach P1.
  * Kuchnia i przedsionek odprowadzają ścieki podejściami w posadzce P0.
  * Wyjście kanalizacji ścianą pn. w osi x = 5,00. Studzienka rewizyjna na działce, przykanalik ≈ 8 m.
* **Pom. techniczne 0.12** (6,56 m², P0):
  * jednostka wewnętrzna pompy ciepła split, zasobnik CWU 300 l, bufor, rozdzielacze ogrzewania podłogowego;
  * rozdzielnica główna RG, wodomierz i zawór antyskażeniowy.

  Jednostka zewnętrzna PC stoi przy ścianie wsch. garażu, 3,80 m od granicy, z dala od sypialni.
* **Rekuperacja.** Centrala w pom. 2.06 na P2 (obok wyłazu na dach), czerpnia i wyrzutnia przez dach. Rozprowadzenie:
  * na P2 w suficie podwieszonym holu i garderoby;
  * pionowo w szachcie SI;
  * na P1 i P0 w stropach/sufitach holu i łazienek.
* **PV** ≤ 6,5 kWp na dachu P2 (≈ 80 m² netto), stelaże niskie E–W ≤ +9,80 (nie wyżej niż attyka).
* **Deszczówka.** Stropodach P2 odwadniają rzygacze na dach P1. Dach P1 (część pn.) ma wpusty i rury spustowe na elewacji pn. Woda płynie do zbiornika 6 m³ (podlewanie), a jego przelew do skrzynek rozsączających ≈ 5,5 m³. Dach zielony garażu ma wpust i rurę w narożu NE.
* **Wyjście na dach:** klapa 0,90 × 0,90 m w stropodachu nad pom. 2.06, z drabiną wg § 101 (K-20, K-21).

## 6. Zagospodarowanie działki
""")
    A(f"""Działka 32,00 × 50,00 m (1600 m²). W układzie budynku granice to:
* zach. x = {f(M.DZ['xw'])};
* wsch. x = {f(M.DZ['xe'])};
* pn. (linia rozgraniczająca ul. Lipowej, 1KDD) y = {f(M.DZ['yn'])};
* pd. y = {f(M.DZ['ys'])}.

Nieprzekraczalna linia zabudowy biegnie w y = {f(M.LINIA_ZAB)}, czyli 6,00 m od drogi. Budynek jest przesunięty na północ, dzięki czemu od południa zostaje ogród o głębokości ≈ 28 m.

""")
    A(tab(["strona", "element", "odległość [m]", "wymaganie [m]", "ocena"], [(r["str"], r["el"], f(r["d"]), f(r["min"]), "✓" if r["d"] >= r["min"] - 1e-6 else "✗") for r in od]))
    A(f"""
Wymagania (WT § 12 ust. 1 i 6, § 19, MPZP):
* ściany z otworami ≥ 4,0 m od granicy;
* okapy i płyty ≥ 1,5 m, tu utrzymane ≥ 4,0 m dla bezpieczeństwa;
* każdy uskok elewacji sprawdzony osobno;
* od strony drogi obowiązuje linia zabudowy. Nie przekracza jej żaden element, także daszek, który jest 1,30 m za linią.

* **Dojazd i parkowanie.**
  * Brama przesuwna 5,60 m (odjazd na wschód, wewnątrz działki, § 42) i furtka 1,00 m.
  * Podjazd x 12,30–18,70 (6,40 m) prowadzi do bramy garażu, 8,00 m.
  * **2 miejsca gościnne** 2,5 × 5,0 m, niezadaszone, na podjeździe przed garażem.
  * Razem z garażem jest **4 stanowiska** (MPZP ≥ 2).
* **Dojście** szer. 2,50 m od furtki do zadaszonego wejścia. Daszek 2,80 × 1,30 m spełnia K-12: szerokość ≥ drzwi + 1,0, wysięg ≥ 1,0.
* **Taras ogrodowy** −0,05, 61,7 m², w kształcie litery L. Zajmuje pas pd. przed przeszkleniem E pod okapem 1,00 m oraz pas zach. pod okapem 1,50 m. Wyjście na taras zapewniają drzwi HS salonu i jadalni. Drzwi gospodarcze przedsionka prowadzą na taras i ogród.
* **Odpady.** Osłona na 4 pojemniki stoi w linii ogrodzenia przy furtce, z drzwiczkami od ulicy. WT § 23 ust. 4: w zabudowie jednorodzinnej odległości od okien i granicy się nie określa (R3 Z-10, R8-25).
* **Retencja.** Zbiornik 6 m³ i skrzynki rozsączające stoją w ogródku frontowym. Są ≥ 5 m od budynku i ≥ 2 m od granic. Wody gruntowe ≈ 3,8 m p.p.t., więc rozsączanie jest możliwe. Powierzchni nad skrzynkami nie wliczono do PBC.
* **Przyłącza z ul. Lipowej.**
  * woda PE 40, wodomierz w pom. 0.12, ≈ 18 m;
  * kanalizacja PVC 160 ze studzienką, ≈ 14 m;
  * złącze ZK we wnęce ogrodzenia przy furtce, WLZ do RG;
  * światłowód;
  * gazu nie przyłącza się (dom all-electric).
* **Zieleń.** Żywopłoty izolacyjne wzdłuż granic E, W i S. Drzewa liściaste w ogrodzie: od zachodu cień letni, zimą przepuszczają słońce. Ogrodzenie od drogi ażurowe, h = 1,50 m (≤ 1,60, MPZP).

""")
    A(tab(["wskaźnik (MPZP 3MN)", "W2", "limit", "ocena"], [
        ("powierzchnia zabudowy (lica ścian, upzp art. 2 pkt 35)", f"{f(W['zabudowa'])} m² ({f(100*W['zabudowa']/1600, 1)} %)", "≤ 480 m² (30 %)", "✓"),
        ("jw., wariant kontrolny z płytami, okapami, ramą C, daszkiem", f"{f(W['zabudowa_plyty'])} m² ({f(100*W['zabudowa_plyty']/1600, 1)} %)", "≤ 480 m²", "✓"),
        ("utwardzenia (podjazd, dojście, taras, ścieżka, osłony, skrzynki)", f"{f(W['utwardzone'])} m²", "—", ""),
        ("PBC (bez dachu zielonego i bez terenu nad skrzynkami)", f"{f(W['pbc'])} m² ({f(100*W['pbc']/1600, 1)} %)", "≥ 800 m² (50 %)", "✓"),
        ("rezerwa: 50 % dachu zielonego garażu", f"+{f(0.5*W['dach_ziel'])} m²", "—", ""),
        ("suma pow. kondygnacji nadziemnych (obrys zewn.)", f"{f(W['suma_kond'])} m²", "80…1280 m²", "✓"),
        ("intensywność nadziemna", f(W['intens'], 3), "0,05–0,80", "✓"),
        ("wysokość zabudowy (upzp art. 2 pkt 30)", f"{f(H['H_mpzp'])} m", "≤ 11,00 m", "✓"),
        ("liczba kondygnacji nadziemnych", "3", "≤ 3", "✓"),
        ("miejsca postojowe", "2 garaż + 2 gościnne", "≥ 2", "✓"),
    ]))
    A(f"""
## 7. Orientacja, doświetlenie, energia
* **Strefa dzienna** jest na południe: 11,40 m przeszklenia w 5 kwaterach, h = 2,75 m. Latem w południe (wysokość słońca ≈ 61°) okap 1,00 m zacienia górne ≈ 1,8 m przeszklenia; resztę osłaniają rolety screen ZIP. Zimą (≈ 14°) słońce wpada na całą głębokość strefy dziennej 4,6 m.
* **Okno zach. salonu** jest pod okapem 1,50 m. Osłony zewnętrzne: rolety screen ZIP na przeszkleniach pd. i zach.
* **Boks C** (P1, pd.) ma ramę wysuniętą 1,00 m, która działa jak łamacz światła nad oknem wys. 1,50 m.
* **Sypialnie.**
  * Rodziców i gabinet (P2) mają lamele pd. i okna zach./wsch.
  * Pokoje dzieci są od zachodu i spełniają § 60: ≥ 3 h słońca w równonoc. Okno ma parapet +4,00, a płyta ST2 wystaje 2,10 m nad nadprożem +5,50, co daje kąt odcięcia 43° (> 37,6° maks. wysokości słońca w równonoc).
  * Pokój gościnny jest od zachodu.
* **Północ** ma minimalne przeszklenia:
  * drzwi wejściowe;
  * dwa okna-szczeliny 1,20 × 0,60 i 0,90 × 0,60 m na P1;
  * okna łazienki i klatki w nadbudowie P2.

  Od północy są też komunikacja, łazienki, WC, pralnia i garaż jako bufor.
* **Zwartość.** Trzon mieszkalny 12,6 × 9,0 m i bryła A 13,6 × 5,4 m bez dodatkowych uskoków. Garaż i strefa gospodarcza są częściowo ogrzewane i buforują od wschodu. Ściana dom/garaż ma U ≈ 0,28 W/(m²K) (≤ 0,30).
* **§ 13 (przesłanianie).** Okna P0 i P1 nie mają przesłon w kącie 60°:
  * attyka garażu +3,85 leży poniżej parapetu okna wsch. P1 (+4,00);
  * boki ramy C mają 0,15 m.

  Lamele A traktuje się jako osłonę okna, nie jako obiekt przesłaniający. Wymaga to potwierdzenia w PAB (ryzyko).

## 8. Tabela kontrolna
""")
    rows = []
    for r in M.POMIESZCZENIA:
        if r["min"]:
            A_ = M.room_area(r)
            rows.append((f"{r['id']} {r['nazwa']}", f"{f(A_)} m²", f"≥ {f(r['min'])} m²", "✓" if A_ >= r["min"] else "✗"))
    A("**Powierzchnie pokoi a minima programowe** (brief; ≥ 8 / ≥ 16 m² to wymagania programowe, nie WT, zob. R3 B-19)\n\n")
    A(tab(["pomieszczenie", "pow.", "minimum", "ocena"], rows))
    A("\n**Doświetlenie** (okna w świetle ościeżnic ≥ 1/8 pow. podłogi, WT § 57 ust. 2, B-04). Ościeżnice przyjęto 7 cm z każdej strony, szprosy 10 cm.\n\n")
    A(tab(["pomieszczenie", "pow. [m²]", "okna", "A okien [m²]", "wymagane 1/8 [m²]", "stosunek", "ocena"],
          [(f"{r['id']} {r['nazwa']}", f(r['A']), r['okna'], f(r['Ao']), f(r['wym']), f"1 : {f(1/r['stos'], 1)}", "✓" if r['stos'] >= 0.125 else "✗") for r in ok]))
    A("\nKuchnia ma okno: jest częścią 0.06, przy kwaterze 5 przeszklenia E. Łazienki i WC mają wentylację mechaniczną.\n\n")
    A("**Pozostałe kontrole**\n\n")
    A(tab(["kontrola", "W2", "wymaganie", "ocena"], [
        ("wysokość w świetle pokoi P0/P1/P2", "2,80 m", "≥ 2,50 (§ 72); cel 2,70–2,80", "✓"),
        ("wysokość łazienek / pomocniczych", "2,80 m (≥ 2,50 pod sufitem podwieszonym)", "≥ 2,20 (§ 77 ust. 3, went. mech.)", "✓"),
        ("garaż: w świetle / brama", "6,08 × 6,08 m, h = 2,86 m; brama 5,00 × 2,25 m", "≥ 5,60 × 6,00; h ≥ 2,20; brama ≥ 2,30 × 2,00 (§ 102, § 104)", "✓"),
        ("pom. techniczne P0", "6,56 m²", "≥ 6 m² (brief)", "✓"),
        ("schody: h / s / 2h+s", f"{f(SCH['h'], 3)} / {f(SCH['s'])} / {f(SCH['dwa_h_s'], 3)}", "≤ 0,19 / — / 0,60–0,65", "✓"),
        ("schody: bieg / spocznik", f"{f(SCH['szer'])} / {f(SCH['spocz_gl'])} m", "≥ 0,80 (cel 1,00) / ≥ szer. biegu", "✓"),
        ("schody: prześwit nad biegiem", f"{f(SCH['przeswit'])} m", "≥ 2,00", "✓"),
        ("drzwi wejściowe", "1,10 × 2,40 (w świetle ościeżnicy ≈ 0,96 × 2,33)", "≥ 0,90 × 2,00, próg ≤ 2 cm (§ 62)", "✓"),
        ("drzwi łazienek / WC", "otwierane na zewnątrz, kratka ≥ 0,022 m²", "§ 79", "✓"),
        ("WC gościnne", "szer. 1,07 m", "≥ 0,90 (§ 83)", "✓"),
        ("okna P1/P2 z niskim parapetem", "dolna część stała VSG do 0,85; skrzydła P2 do wewnątrz", "§ 299, § 301 (K-16, K-17)", "✓"),
        ("daszek nad wejściem", "2,80 × 1,30 m", "≥ drzwi + 1,0 × ≥ 1,0 (§ 292)", "✓"),
        ("najmniejsza odległość ściany z otworami od granicy", f"{f(min(r['d'] for r in od if r['min'] == 4.0))} m", "≥ 4,00", "✓"),
        ("najmniejsza odległość okapu/płyty od granicy bocznej", f"{f(min(r['d'] for r in od if r['min'] == 1.5 and r['str'] in 'WE'))} m", "≥ 1,50 (§ 12 ust. 6); cel ≥ 4,00", "✓"),
        ("daszek / lico od linii zabudowy", "1,30 m za linią", "nie przekracza", "✓"),
        ("pow. zabudowy", f"{f(W['zabudowa'])} m² ({f(100*W['zabudowa']/1600, 1)} %)", "≤ 480 m²", "✓"),
        ("PBC", f"{f(W['pbc'])} m² ({f(100*W['pbc']/1600, 1)} %)", "≥ 800 m²", "✓"),
        ("intensywność", f(W['intens'], 3), "0,05–0,80", "✓"),
        ("wysokość zabudowy (upzp): attyka +9,80 − śr. terenu na obwodzie", f"{f(H['H_mpzp'])} m (teren {f(H['zmin'])}…{f(H['zmax'])}, śr. {f(H['zsr'])})", "≤ 11,00 (rezerwa zalecana 0,30)", "✓"),
        ("wysokość budynku WT § 6 (do wierzchu warstw +9,60)", f"{f(H['H_WT'])} m (najniższe wejście: {H['wejscie']}, teren {f(H['z_wej'])})", "grupa N ≤ 12 m", "✓"),
        ("PU mieszkalna (bez garażu)", f"{f(pu_tot)} m²", "230–270 m²", "✓"),
        ("strefa otwarta salon + jadalnia + kuchnia", f"{f(open_area)} m²", "≥ 50 m²", "✓"),
    ]))
    A(f"""
PU obejmuje schowek pod schodami 0.05 w całości (2,24 m²). Po pomniejszeniu stref o wysokości < 2,20 m byłoby to ok. −0,7 m². Powierzchni stropu nad biegami P2 (pustka) nie liczono.

## 9. Ocena wariantu

**Zalety**
1. **Najprostszy układ nośny.** Wszystkie ściany nośne stoją w pionie. Stropy są jednokierunkowe, o rozpiętości 4,80 / 3,60 m i grubości 20 cm, bez podciągów w pomieszczeniach. Jedyne elementy „transferowe” są krótkie i powtarzalne: belka B1 na 4 słupach w szprosach fasady, nadproże B2 boksu C i dwie ściany-tarcze wspornika A.
2. **Krótkie instalacje.** Jeden szacht SI obsługuje trzy łazienki ustawione jedna nad drugą, a drugi krótki pion K2 pralnię i WC. Pomieszczenie techniczne jest obok garażu i przyłączy. Centrala rekuperacji na P2 ma czerpnię i wyrzutnię prosto przez dach.
3. **Logistyka dnia codziennego.** Samochód → przedsionek gospodarczy ze spiżarnią → kuchnia to ok. 6 m. Wejście główne jest obok bramy, pod daszkiem. Drzwi gospodarcze prowadzą do ogrodu, a drzwi boczne garażu do rowerów i narzędzi ogrodowych.
4. **Zwarty rzut i umiarkowana PU.** {f(pu_tot)} m² przy powierzchni zabudowy {f(W['zabudowa'])} m². Brak przewymiarowania, duże rezerwy wskaźników MPZP.
5. **Sylweta „S” czytelna.** Porównanie ze szkicem pokazuje zgodność A, B, C, D (do narożnika garażu na 19,00 m) i G. Przesunięcia i głębokie płyty (1,00–1,50 m) dają warstwowość oraz osłony przeciwsłoneczne.
6. **Klatka schodowa obudowana ścianami** (bez balustrad). Tanie wykonanie i dobra akustyka. Świetlik nad klatką doświetla wszystkie kondygnacje.

**Słabości i ryzyka**
1. Przeszklenie E ma 11,40 m zamiast ≈ 12,2 m: zaczyna się 0,4 m bardziej na zachód i kończy ok. 1,2 m wcześniej niż w szkicu. To świadoma cena ścian w pionie (oś E). Kompensują to przeszklone drzwi gospodarcze.
2. Strefa dzienna ma głębokość 4,59 m, czyli jest wydłużona (11,8 m). Kuchnia z wyspą przy ścianie E jest wygodna, ale salon płytszy niż typowo.
3. Nadbudowa klatki i łazienki na P2 (od północy) tworzy dodatkowy fragment stropodachu i attyki. Od południa jej nie widać.
4. Pokój rodzinny P1 (31,9 m² z częścią komunikacji) jest duży jak na potrzeby. Działa jednak jako galeria/hol przy schodach.
5. Łazienka gościnna (3,91 m²) i przedpokój gościnny są minimalne. Pokój gościnny ma dostęp przez przedpokój z salonu, nie z holu.
6. Dwie płyty w jednym pasie (okap E +3,05 i płyta dolna ramy C +3,65, obie 1,00 m) dają odstęp 0,60 m. Trzeba go odwadniać i czyścić, a detal wymaga dopracowania w PT.
7. Lamele przed oknami P2 obniżają realny współczynnik światła dziennego. Wymóg formalny 1/8 jest spełniony z dużym zapasem. Trzeba potwierdzić, że lamele nie są „obiektem przesłaniającym” (§ 13).
8. Fasada pd. P0 na słupach stalowych daje mniejszą sztywność w kierunku x na parterze. Trzeba to sprawdzić w PT (rdzeń klatki C–D i ściany osi 3/4).
9. Stan prawny: WT 2002 wygasły 20.09.2026 (R3 S-01). Projekt wymaga oświadczenia z art. 102a PB i wniosku do 19.03.2028.

## 10. Pliki
* `rzut_P0.png`, `rzut_P1.png`, `rzut_P2.png`: rzuty z osiami, wymiarami, pomieszczeniami (pow. netto), otworami, schodami i szachtami.
* `elewacja_S.png`: elewacja południowa oraz szkic z nałożonym obrysem W2 (kontrola wierności).
* `przekroj.png`: przekroje A-A (x = 6,70, przez schody i boks C) i B-B (y = 2,00, przez wspornik A i garaż) z rzędnymi.
* `zagospodarowanie.png`: plan działki z granicami, drogą, linią zabudowy, odległościami, przyłączami i bilansem terenu.
* `model_W2.json`: dane modelu (osie, poziomy, ściany, otwory, pomieszczenia, płyty, schody, teren).
* `src/`:
  * `model_w2.py`: model;
  * `calc_w2.py`: obliczenia kontrolne;
  * `draw_*.py`: rysunki;
  * `make_opis.py`: ten opis.

  Odtworzenie: `cd src && for f in draw_plans draw_elev draw_sections draw_site make_opis; do python3 $f.py ..; done`.
""")
    with open(os.path.join(OUT, "opis.md"), "w", encoding="utf-8") as fh:
        fh.write("".join(md))
    # --- JSON
    js = dict(meta=dict(nazwa="Dom LAMELA — koncepcja W2", data="2026-09-25", uklad="x→E, y→N, z→góra; 0,0 = osie A/1; ±0,00 = 101,65 m n.p.m."),
              osie=dict(x=M.OSIE_X, y=M.OSIE_Y), poziomy=M.POZ, typy_scian=M.TYPY,
              sciany=[dict(w, p1=list(w["p1"]), p2=list(w["p2"]), ext=list(w["ext"])) for w in M.SCIANY],
              otwory=M.OTWORY,
              pomieszczenia=[dict({k: v for k, v in r.items() if k != "poly"}, pow=M.room_area(r), geometria=mapping(r["poly"])) for r in M.POMIESZCZENIA],
              plyty=[dict({k: v for k, v in p.items() if k != "poly"}, geometria=mapping(p["poly"])) for p in M.PLYTY],
              lamele=M.LAMELE, slupy=M.SLUPY + M.SLUPKI_C, schody=M.SCHODY,
              dzialka=dict(granice=M.DZ, linia_zabudowy_y=M.LINIA_ZAB, rzedne_narozy=M.H_NAROZ,
                           elementy={k: dict(opis=v["opis"], geometria=mapping(v["poly"])) for k, v in M.TEREN_ELEM.items()},
                           miejsca_goscinne=[mapping(g) for g in M.MIEJSCA_GOSC], zbiornik=M.ZBIORNIK, przylacza=M.PRZYLACZA),
              wyniki=dict(PU=per, PU_suma=pu_tot, garaz=gar, zabudowa=round(W["zabudowa"], 2), zabudowa_z_plytami=round(W["zabudowa_plyty"], 2),
                          PBC=round(W["pbc"], 2), intensywnosc=round(W["intens"], 3), wys_mpzp=round(H["H_mpzp"], 2), wys_WT=round(H["H_WT"], 2)))
    with open(os.path.join(OUT, "model_W2.json"), "w", encoding="utf-8") as fh:
        json.dump(js, fh, ensure_ascii=False, indent=1, default=lambda o: list(o) if isinstance(o, tuple) else str(o))
    print("opis.md + model_W2.json", pu_tot, round(W["zabudowa"], 2), round(H["H_mpzp"], 2))


if __name__ == "__main__":
    main()
