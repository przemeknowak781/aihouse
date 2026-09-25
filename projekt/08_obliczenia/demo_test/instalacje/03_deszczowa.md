# Odwodnienie dachów i zagospodarowanie wód opadowych

Obiekt: Dom testowy pipeline'u 3D. PN-EN 12056-3:2002; metodyka Aquanet 2024 (PANDa 2050, C = 10 lat). Dane przykładowe oznaczono [ZAŁ].

## 1. Podstawy i założenia

* WT §28–29, §126, §319 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-018, W-019, W-142…W-146.
* PN-EN 12056-3:2002 (PL, aktualna); PN-EN 1253-2 (wpusty dachowe); PN-EN 1433 (odwodnienia liniowe).
* Aquanet S.A., Załącznik C (2024) — metodyka bilansowa, PANDa 2050 RCP 4.5 Poznań-Ławica C10; DWA-A 138-1:2024 (tło).
* Wariant bazowy (D-05): szczelny zbiornik ≤ 5 m³ + przelew do niecki (ogród deszczowy ≤ 0,3 m); skrzynki rozsączające wyłącznie jako opcja po stanowisku PGW Wody Polskie (PW art. 16 pkt 65 lit. f, art. 389 pkt 6).
* Natężenie deszczu do wymiarowania odwodnienia dachów r = 0,046 l/(s·m²) (W-142: PANDa C10, 5 min (Aquanet 2024); zakres 0,03–0,05 — Rynek Instalacyjny 12/2015 [zalozenie]).
* C = 1,0 dla wszystkich dachów przy wymiarowaniu wpustów i przelewów (także zielonych — substrat nasycony lub zamarznięty) [ZAŁ]; ψ wg Aquanet (tab. 2) wyłącznie do bilansu retencji.
* Przelewy awaryjne: pełne zablokowanie wpustów, współczynnik ryzyka F_R = 2,0 (PN-EN 12056-3 tabl. 2 — spiętrzenie może spowodować przeciek do budynku) [NZW].
* Przepustowość wpustów przy 35 mm spiętrzenia: DN50 0,9 l/s, DN70 1,7 l/s, DN100 4,5 l/s, DN125 7,0 l/s, DN150 8,1 l/s [NZW — przyjąć z karty wyrobu wg PN-EN 1253-2].
* k_f gruntu = 1,00·10⁻⁴ m/s (piaski średnie) [ZAŁ — wymagane badania, E-04]; k_f,nn = 0,5·k_f.
* Zbiornik szczelny V = 5,0 m³ (dzialka.yaml / W-145), przelew do niecki; wody z utwardzeń spływają na przyległe powierzchnie biologicznie czynne (W-018).
* Bilans roczny: miesięczny (normy IMGW 1991–2020, Poznań), podlewanie V–IX [ZAŁ]; filtr deszczówki η = 0,9 [ZAŁ].

## 2. Pola dachów — wpusty, spadki, przelewy awaryjne, rury spustowe

| Pole | Rodzaj | A [m²] | ψ | Q [l/s] | Wpusty | ΣQ_wp [l/s] | Spadek | L_spł [m] | ∆h spadk. [cm] | Q_aw [l/s] | Przelewy | Q_prz [l/s] | h_spiętrz. [cm] | q_woda [kN/m²] |
|:---|:---|---:|---:|---:|:---|---:|---:|---:|---:|---:|:---|---:|---:|---:|
| D1 | plaski | 83,3 | 0,95 | 3,83 | 1× DN100 | 4,5 | 0,020 | 6,5 | 13,1 | 7,66 | 1× 20×10 | 8,09 | 7,8 | 1,27 |
| PL-D | taras | 19,6 | 0,95 | 0,90 | 1× DN100 (prop.) | 4,5 | brak | 3,2 | 6,4 | 1,80 | 0×  | 0,00 | 0,0 | 0,00 |

* Pole D1 (plaski): przepływ obliczeniowy: Q = r·A·C = 0,046·83,3·1,0 = **3,83** l/s — _PN-EN 12056-3 wzór (1)_
* Pole D1: przepływ dla przelewów awaryjnych: Q_aw = F_R·r·A·C = 2,0·3,83 = **7,66** l/s — _tabl. 2 [NZW]_
* Przepustowość przelewu 20×10 cm przy h = 8 cm: Q = ⅔·μ·b·√(2g)·h^1,5 = ⅔·0,6·0,20·√(2·9,81)·0,08^1,5 = **8,02** l/s — _Poleni [W]_
* Przepustowość rury spustowej DN100 (d_i = 96 mm), f = 0,33: Q_RWP = 2,5·10⁻⁴·k_b^−0,167·d_i^2,667·f^1,667 = 2,5·10⁻⁴·0,25^−0,167·96^2,667·0,33^1,667 = **9,61** l/s — _[NZW]_
* Pole D1: najdłuższa droga spływu i przyrost grubości izolacji spadkowej: ∆h = i·L_max = 0,020·6,53 = **0,131** m

**Pole D1:** brak przelewów awaryjnych w modelu — proponowane 1 × 20×10 cm, dno 5 cm nad pokryciem (uzupełnić `dachy[].przelewy_awaryjne`); brak rur spustowych w modelu — proponowane (trasa wewn. w szachcie izolowanym, odbiornik: zbiornik); RS-D1-1: rura wewnętrzna w szachcie — izolacja przeciwroszeniowa i akustyczna, rewizja u podstawy [ZAŁ]; przejście przez stropodach szczelne (paroizolacja!); wpusty: rozważyć podgrzewanie (wpust w strefie zacienionej / odpływ przez przestrzeń nieogrzewaną) [ZAŁ].

**Pole PL-D:** brak wpustów w modelu — proponowane 1 × DN100 (uzupełnić `dachy[].wpusty`); brak rur spustowych w modelu — proponowane (trasa wewn. w szachcie izolowanym, odbiornik: zbiornik); RS-PL-D-1: rura wewnętrzna w szachcie — izolacja przeciwroszeniowa i akustyczna, rewizja u podstawy [ZAŁ]; przejście przez stropodach szczelne (paroizolacja!).

| Rura | Pole | DN | d_i [mm] | Trasa | Odbiornik | Q [l/s] | Q_RWP [l/s] |
|:---|:---|---:|---:|:---|:---|---:|---:|
| RS-D1-1 | D1 | 100 | 96 | wewn_szacht | zbiornik | 3,83 | 9,61 |
| RS-PL-D-1 | PL-D | 100 | 96 | wewn_szacht | zbiornik | 0,90 | 9,61 |

Obciążenie wodą spiętrzoną przy zablokowanych wpustach (q_woda) przekazać do obliczeń konstrukcji stropodachów (obciążenie wyjątkowe/zmienne wg decyzji konstruktora).

## 3. Odwodnienia liniowe (drzwi bezprogowe, brama garażowa)

| Otwór | Opis | L [m] | A zlewni [m²] | Q [l/s] | Klasa obciążenia | Odbiornik |
|:---|:---|---:|---:|---:|:---|:---|
| O0-01 | drzwi przesuwne HS bez progu (P0) | 4,20 | 12,0 | 0,55 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O0-03 | drzwi zewnętrzne bezprogowe (P0) | 1,30 | 3,3 | 0,15 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O1-03 | drzwi przesuwne HS bez progu (P1) | 2,60 | 7,2 | 0,33 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |

Odwodnienie liniowe przy drzwiach bez progu: korytko przed progiem na całej szerokości + 0,1 m z każdej strony, spadek nawierzchni tarasu/podjazdu od budynku ≥ 1,5–2 %, ruszt szczelinowy; posadzka wewnętrzna ≥ 2 cm nad rusztem [ZAŁ; brief §9 pkt 4]. Odpływ przez osadnik do zbiornika lub niecki.

## 4. Zbiornik ≤ 5 m³ i niecka (wariant bazowy)

* Powierzchnia zredukowana zlewni (dachy): A_red = Σψ_i·A_i = 0,95·83,3 + 0,95·19,6 = **97,7** m² — _Aquanet 2024 tab. 2 (W-143)_
* Zdolność chłonna niecki: Q_inf = 1000·A_inf·k_f,nn = 1000·A_n·0,5·k_f = 1000·8,0·5,00·10⁻⁵ = **0,400** l/s — _Aquanet 2024 wzór (2); k_f [ZAŁ — badania]_
* Objętość obliczeniowa (czasza niecki zasilana opadem ψ = 1,0), t_d = 30 min: V_obl = max_td[0,06·q(t_d)·(A_red + A_n)·t_d − 0,06·Q_inf·t_d] = 0,06·157,64·0,0106·30 − 0,06·0,400·30 = **2,28** m³ — _Aquanet 2024 wzór (1); PANDa 2050 C10_
* Minimalna objętość niecki (zbiornik ≤ 5 m³ pełny — bez zaliczenia): V_min = f_b·V_obl = 1,2·2,28 = **2,73** m³ — _f_b wg W-143_
* Wariant: zbiornik pusty na początku opadu (zaliczenie V_zb): V_min' = f_b·max(V_obl − V_zb; 0) = 1,2·max(2,28 − 5,0; 0) = **0,00** m³
* Minimalna powierzchnia niecki (dobór): A_n,min: V_min ≤ A_n·h ∧ t_opr ≤ t_max = iteracja co 0,5 m² = **9,0** m²
* Przyjęta niecka (ogród deszczowy) — model (dzialka.yaml: retencja.rozsaczanie): A_n × h = 8,0 × 0,30 = **2,40** m³ — _W-145_
* Czas opróżniania niecki: t = V_min/Q_inf = 2,73/0,00040/3600 = **1,9** h

| Urządzenie | x, y (układ budynku) | Odl. od budynku [m] | Odl. od granicy [m] |
|:---|:---|---:|---:|
| zbiornik szczelny | 7,00; −10,00 | 9,70 | 8,00 |
| niecka / rozsączanie | 7,00; −13,00 | 11,70 | 4,00 |

### 4.1 Bilans roczny zbiornika (normy opadowe IMGW 1991–2020)

| Mies. | Opad [mm] | Dopływ [m³] | Podlewanie [m³] | Pokryte [m³] | Przelew do niecki [m³] | Stan końcowy [m³] |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37,7 | 3,31 | 0,00 | 0,00 | 0,00 | 3,31 |
| 2 | 30,7 | 2,70 | 0,00 | 0,00 | 1,01 | 5,00 |
| 3 | 39,9 | 3,51 | 0,00 | 0,00 | 3,51 | 5,00 |
| 4 | 28,6 | 2,51 | 0,00 | 0,00 | 2,51 | 5,00 |
| 5 | 53,8 | 4,73 | 6,00 | 6,00 | 0,00 | 3,73 |
| 6 | 57,5 | 5,06 | 8,00 | 8,00 | 0,00 | 0,78 |
| 7 | 84,4 | 7,42 | 9,00 | 8,20 | 0,00 | 0,00 |
| 8 | 55,9 | 4,91 | 8,00 | 4,91 | 0,00 | 0,00 |
| 9 | 41,2 | 3,62 | 5,00 | 3,62 | 0,00 | 0,00 |
| 10 | 35,4 | 3,11 | 0,00 | 0,00 | 0,00 | 3,11 |
| 11 | 33,6 | 2,95 | 0,00 | 0,00 | 1,07 | 5,00 |
| 12 | 40,1 | 3,53 | 0,00 | 0,00 | 3,53 | 5,00 |

Rocznie: dopływ 47,4 m³, zapotrzebowanie na podlewanie 36,0 m³, pokryte 30,7 m³ (85 %), przelew do niecki 11,6 m³. Opad roczny 538,9 mm (IMGW-PIB, Portal Klimat — Normy klimatyczne 1991–2020 (OPAD_SUMA)).

## 5. Wariant opcjonalny: skrzynki rozsączające

* Skrzynki 3,60 × 1,20 × 0,66 m — powierzchnia infiltracji: A_inf = L·B + ½·2(L + B)·H = **7,49** m² — _Aquanet 2024_
* Zdolność chłonna: Q_inf = 1000·A_inf·k_f,nn = **0,374** l/s
* V_obl (t_d = 30 min) / V_min = f_b·V_obl: 2,10 / 2,52 = **2,52** m³
* Objętość netto skrzynek (porowatość 95 %): V_n = L·B·H·0,95 = **2,71** m³ — _dane producentów [W]_
* Czas opróżniania: t = V_min/Q_inf = **1,9** h — _≤ 24 h_

Skrzynki: osadnik przed urządzeniem; odległości wg W-144; wymagają stanowiska PGW Wody Polskie / pozwolenia wodnoprawnego (D-05) — dlatego nie stanowią wariantu bazowego.

## 6. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-142 | Pole D1: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | 0,05 m | ≥ 0,03 m | SPEŁNIONY | [ZAŁ] ≥ 3 cm |
| W-142 | Pole D1: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa) | 6,243 m | ≤ 6,304 m | SPEŁNIONY | brief §9 pkt 4 (wywinięcie ≥ 15 cm) |
| W-142 | Pole D1: zwierciadło przy zablokowanych wpustach poniżej wywinięcia hydroizolacji | 6,321 m | < 6,343 m | SPEŁNIONY | PN-EN 12056-3 p. 7 [NZW]; brief §9 |
| W-142 | Rura spustowa RS-D1-1: Q ≤ Q_RWP(DN100, f = 0,33) | 3,83 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole D1: przepustowość wpustów ≥ Q | 4,50 l/s | ≥ 3,83 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Pole D1: spadek połaci | 0,020 | ≥ 0,020 | SPEŁNIONY | W-142: R3 H-04 (dobra praktyka) [zalozenie] |
| W-142 | Pole D1: przelewy awaryjne (Q_przel ≥ F_R·Q) | 8,09 l/s | ≥ 7,66 l/s | SPEŁNIONY | PN-EN 12056-3 p. 7, tabl. 2 [NZW]; brief §9 pkt 3 |
| W-142 | Rura spustowa RS-PL-D-1: Q ≤ Q_RWP(DN100, f = 0,33) | 0,90 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole PL-D: przepustowość wpustów ≥ Q | 4,50 l/s | ≥ 0,90 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-145 | Pojemność szczelnego zbiornika (bez zgłoszenia) | 5,00 m³ | ≤ 5,00 m³ | SPEŁNIONY | W-145: PB art. 29 ust. 2 pkt 36 (5–15 m³ — zgłoszenie, ust. 1 pkt 38) |
| W-143 | Niecka: pojemność ≥ V_min (zbiornik pełny — bez zaliczenia) | 2,40 m³ | ≥ 2,73 m³ | **NIESPEŁNIONY** | Aquanet 2024 wzór (1), f_b |
| W-145 | Niecka: głębokość | 0,30 m | ≤ 0,30 m | SPEŁNIONY | W-145 (≤ 0,3 m) |
| W-143 | Niecka: powierzchnia przyjęta ≥ minimalna z doboru | 8,0 m² | ≥ 9,0 m² | **NIESPEŁNIONY** | dobór (V_min ≤ A_n·h, t_opr ≤ 24 h); przyjęto: model (dzialka.yaml: retencja.rozsaczanie) |
| W-143 | Niecka: czas opróżniania | 1,9 h | ≤ 24,0 h | SPEŁNIONY | W-143: Aquanet 2024 zał. C [zalozenie] |
| W-144 | Dno niecki nad maks. zwierciadłem wód gruntowych | 3,50 m | ≥ 1,00 m | SPEŁNIONY | Aquanet 2024; W-144 |
| W-144 | niecka / rozsączanie: odległość od fundamentów | 11,70 m | ≥ 3,00 m | SPEŁNIONY | W-144 (S-4) |
| W-144 | niecka / rozsączanie: odległość od granicy działki | 4,00 m | ≥ 2,00 m | SPEŁNIONY | W-144 |

## Podsumowanie sprawdzeń

Warunków: 17; spełnionych: 15; niespełnionych: 2; informacyjnych: 0.

Niespełnione:

* W-143 — Niecka: pojemność ≥ V_min (zbiornik pełny — bez zaliczenia): 2,40 m³ (wymaganie >= 2,73 m³)
* W-143 — Niecka: powierzchnia przyjęta ≥ minimalna z doboru: 8,0 m² (wymaganie >= 9,0 m²)

## Źródła

1. PN-EN 12056-3:2002 — p. 4 (Q = r·A·C), tabl. 2 (współczynnik ryzyka), rury spustowe [NZW — treść płatna]
2. Aquanet S.A., Załącznik C — Metodyka obliczania niezbędnej objętości zbiorników detencyjno-retencyjnych, 2024, wzory (1)–(2), tab. 2–3
3. IMGW-PIB, Normy klimatyczne 1991–2020, Poznań (12330) — sumy opadów https://klimat.imgw.pl/pl/climate-normals/OPAD_SUMA
4. Dąbrowski W., Dąbrowska B., Jasik H., Odwadnianie dachów — wymiarowanie rynien, Rynek Instalacyjny 12/2015 (r = 0,03–0,05 l/(s·m²))
5. Rejestr wymagań W-018, W-019, W-119, W-142…W-146; brief §9 (wymagania Inwestora 25.09.2026)
