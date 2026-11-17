# Rejestr poprawek – specyfikacja „BRAMA I LATARNIA” v1.0 → v1.1 (po weryfikacji)

**Stan:** 17.11.2026 · w toku (plik aktualizowany etapami) · Przedmiot: `koncepcja_wybrana.md`, `model/koncepcja.json`.
**Źródła zadań:** `weryfikacja_geometria.md` (G-), `weryfikacja_koszt_eko.md` (E-), `weryfikacja_program.md` (P-).
**Wyłączone:** kondygnacja Sejmiku (P-K1, P-K2, P-K3, P-I1, P-I4) – osobne opracowanie `kondygnacja_S2.md` + `kondygnacja_S2.json`; klucz `kondygnacja_sejmiku` w JSON i rozdz. 7 MD bez zmian (tylko odsyłacz).
**Zasada wyłączenia:** nie korzystano z informacji o rzeczywistych pracach ani wynikach konkursu.
**Dowody:** skrypty `docs/20_koncepcja/_rewizja_*.py` (uruchomienie z katalogu `umwd/`, interpreter `/home/user/aihouse/.venv-render/bin/python -I`).

| ID | Waga | Decyzja v1.1 | Dowód liczbowy (skrypt) | Rysunki / tabele do zmiany | Status |
|---|---|---|---|---|---|
| **PARK** | **KRYT.** (zlecenie koordynatora; model pomieszczeń: 37–41 m.p. wobec 109 deklarowanych) | **Wymagane:** MPZP § 13 – 12 m.p./1 000 m² PU (biura, konferencje) + 6/1 000 m² PU (gastronomia); PU wg PN-ISO 9836 = powierzchnia netto bez powierzchni ruchu i usługowej (instalacyjnej) = 8 400 m², w tym bistro 92 m² → 12 × 8,308 + 6 × 0,092 = 100,25 → **101 m.p.** (kontrolnie PU programu 8 582 m² → 103). **Rozwiązanie:** (1) −2 pod całym obrysem poza M1 przy Maz. 19 (wieża + segment + pas 5 m + skrzydło od s 12,15; 2 101 m²); (2) kondygnacja −1 podwyższona do 4,20 m (posadzka 115,10, w świetle 3,65 m), −2 na 112,10 (w świetle 2,70 m); (3) siatka słupów wieży v = 0 / 8,70 / 16,00 / 23,15 / 29,70 (słupy poza drogami, w licach ścian korytarzy – też uwaga modelu pomieszczeń o słupach w korytarzach); stanowiska w trójkach 3 × 2,50 m między słupami u co 8,10 m; (4) rampa wewn. −1/−2 przeniesiona do kieszeni wsch. wieży (u 34,6–38,5, 18 %, 19,7 m), rampa uliczna jednopasowa przy ścianie pn. segmentu (18 %, 25,2 m); (5) technika z garażu: tryskacze zbędne (nieobowiązkowe, `ppoz.md` pkt 7) – pompownia usunięta, agregat do segmentu (kond. 1), dźwig T do narożnika SE segmentu; centrale P i S oraz GPC przy trzonie B; (6) **stackery zależne 2-poziomowe bez zagłębienia** (jednostki podwójne 5,0 m) wyłącznie w 4 rzędach na −1 (dla pracowników z przydziałem parami; goście, OzN, dostawy – stanowiska zwykłe). **Wynik: 76 stanowisk na posadzce + 30 w stackerach = 109 pozycji; po 6 stanowiskach OzN 3,60 m → 106 m.p. ≥ 101 (zapas 5) / ≥ 103 (zapas 3).** Woda gruntowa: −2 pod skrzydłem – wypór 61 kPa (117,0) / 81 kPa (119,0) < 0,9 × 110 kPa ciężaru stałego; pas pod dziedzińcem – mikropale. Koszt: patrz E-K-1 | `_rewizja_parking.py` (układ stanowisk w shapely, spójność dróg, powierzchnie techniki) | rzuty −1, −2 (P3), przekroje A-A, B-B (P6), tabela 12, JSON `podziemie` | ✅ |
| G-K-1 | KRYT. | (w toku) | | | ⏳ |
| G-K-2 | KRYT. | (w toku) | | | ⏳ |
| G-I-1 | IST. | (w toku) | | | ⏳ |
| G-I-2 | IST. | Bilans wg **numeracji i położeń M.06** (położenia z wektorów PDF załącznika, georeferencja do D701/D702, ±0,5–1 m). Pas −1 pod dziedzińcem **7,0 → 5,0 m** (wierzchołki (72,001; 34,975), (96,193; 40,872)). Nr 58 (Z1): 5,45 m od lica −1 ≥ 4,2 + 1,0 ✔ – zachowany. **Nr 60 (Z2) – usuwany (kolizja)**, nasadzenie zastępcze; lica skrzydła nie przesuwamy (traktu 15,0 m nie da się zwęzić bez utraty pokoi 24 m²). Nr 78 (Z1) – zachowany z ochroną (2,99 m; wejście w strefę 0,11 m). **Usuwane kolizyjnie 8:** 1, 2 (obszar A), 60, 61 (1,3 m od ściany szczelinowej), 67 (Z1 = D897), 79, 80, 81 (Z2, w obrysie skrzydła = D867/D868/D882); **przesadzana 1:** 72 (P); **sanitarnie (U, martwe/zamierające, decyzja arborysty – niezależnie od inwestycji) 10:** 5, 13, 18, 19, 20, 38, 53, 57, 59, 62; **zachowane w miejscu 25** (w tym wszystkie Z1 poza 67 i wszystkie Z2 poza 60, 79–81). Zachowane 36 z 44 (82 %) bez usunięć sanitarnych / 26 z 44 (59 %) po usunięciach sanitarnych. **Nowe nasadzenia 26** (4 lipy – skwer, 6 – szpaler Wybrzeża, 2 – pas 4,6 m, 14 – ogród na gruncie rodzimym, poza stropem garażu) | `_rewizja_drzewa.py` (wynik: `_rewizja_drzewa_wynik.json`) | plan zagospodarowania 1:500, rozdz. 9, 10, JSON `zagospodarowanie` | ✅ |
| G-I-3 | IST. | (w toku) | | | ⏳ |
| G-I-4 | IST. | (w toku) | | | ⏳ |
| G-I-5 | IST. | (w toku) | | | ⏳ |
| E-K-1 | KRYT. | (w toku) | | | ⏳ |
| E-K-2 | KRYT. | Dachy (BIPV jako pokrycie, wykładnia K-05 utrzymana) dają realnie **351 kWp** < 400: wieża 948 m² netto (attyka 0,50 + pas 1,0 m, wyłaz, wpusty, zwody) × 0,215 = 204 kWp; skrzydło 685 m² (attyka 0,52 + pas 0,5 m, przerwa 1,0 m, wyłaz) × 0,215 = 147 kWp; gęstość 0,215 kWp/m² = η 22,5 % × pokrycie 0,955 (warunek przetargowy η ≥ 22,5 %). Uzupełnienie legalne i widoczne, wszystko ≤ 25 m i poza elewacjami od ulic: płyciny wieży od dziedzińca (38 × 2,145 m², bez czerpni) 11 kWp; **ściana pd. segmentu BIPV** (295 m², od dz. 10/2) 41 kWp; **zadaszenie tarasu ogrodowego** przy elewacji pd. wieży (80 m², BIPV półprzezierne) 13 kWp. **Razem 415 kWp (zapas 15 kWp), 328 MWh/rok; PV/EPB 111 %, PV/całość 51 %; EP 28,0 (bez PV 60); emisje EPB 6,7 kg/(m²·rok)**. Wrażliwość: przy η 21 % → 391 kWp (dlatego wymóg η ≥ 22,5 %) | `_rewizja_pv_ep.py` (uruchamia `40_prawo/_bilans_energii.py`) | rozdz. 2 (20), 8, 10, 15, P8 (KPI), JSON `elewacje.PV`, `bilans` | ✅ |
| E-I-1 | IST. | (w toku) | | | ⏳ |
| E-I-2 | IST. | (w toku) | | | ⏳ |
| E-I-3 | IST. | (w toku) | | | ⏳ |
| E-I-4 | IST. | (w toku) | | | ⏳ |
| E-I-5 | IST. | (w toku) | | | ⏳ |
| E-I-6 | IST. | (w toku) | | | ⏳ |
| E-I-7 | IST. | (w toku) | | | ⏳ |
| E-I-8 | IST. | (w toku) | | | ⏳ |
| E-I-9 | IST. | (w toku) | | | ⏳ |
| P-I2 | IST. | (w toku) | | | ⏳ |
| P-I3 | IST. | (w toku) | | | ⏳ |
| P-I5 | IST. | (w toku) | | | ⏳ |
| P-I6 | IST. | (w toku) | | | ⏳ |
| P-I8 | IST. | (w toku) | | | ⏳ |
