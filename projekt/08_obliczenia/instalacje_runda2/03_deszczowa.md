# Odwodnienie dachów i zagospodarowanie wód opadowych

Obiekt: Dom LAMELA. PN-EN 12056-3:2002; metodyka Aquanet 2024 (PANDa 2050, C = 10 lat). Dane przykładowe oznaczono [ZAŁ].

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
| D1 | plaski | 87,4 | 0,95 | 4,02 | 2× DN100, DN100 | 9,0 | 0,020 | 8,7 | 17,3 | 8,04 | 2× 20×10, 20×10 | 22,41 | 5,0 | −0,16 |
| D2 | plaski | 12,5 | 0,95 | 0,58 | 1× DN100 | 4,5 | 0,020 | 4,5 | 8,9 | 1,15 | 1× 20×10 | 11,21 | 2,2 | −0,58 |
| D3 | plaski | 11,2 | 0,95 | 0,52 | 1× DN100 | 4,5 | 0,020 | 4,3 | 8,5 | 1,03 | 1× 20×10 | 11,21 | 2,0 | −0,60 |
| D4 | zielony | 59,1 | 0,50 | 2,72 | 2× DN100, DN100 | 9,0 | 0,020 | 7,0 | 14,0 | 5,43 | 2× 20×10, 20×10 | 22,41 | 3,9 | −0,96 |
| PL-E | taras | 23,7 | 0,95 | 1,09 | 2× DN70, DN70 | 3,4 | 0,020 | 8,8 | 17,5 | 2,18 | 0×  | 0,00 | 0,0 | 0,00 |
| PL-DA | taras | 3,0 | 0,95 | 0,14 | 1× DN70 | 1,7 | 0,020 | 2,5 | 5,0 | 0,28 | 0×  | 0,00 | 0,0 | 0,00 |
| PL-2 | taras | 23,0 | 0,95 | 1,06 | 2× DN70, DN70 | 3,4 | 0,020 | 9,7 | 19,5 | 2,12 | 0×  | 0,00 | 0,0 | 0,00 |
| PL-3 | taras | 23,0 | 0,95 | 1,06 | 2× DN70, DN70 | 3,4 | 0,020 | 9,7 | 19,5 | 2,12 | 0×  | 0,00 | 0,0 | 0,00 |
| PL-D | wspornik | 6,1 | 0,95 | 0,28 | 1× DN70 | 1,7 | 0,020 | 4,9 | 9,7 | 0,56 | 0×  | 0,00 | 0,0 | 0,00 |

* Pole D1 (plaski): przepływ obliczeniowy: Q = r·A·C = 0,046·87,4·1,0 = **4,02** l/s — _PN-EN 12056-3 wzór (1)_
* Pole D1: przepływ dla przelewów awaryjnych: Q_aw = F_R·r·A·C = 2,0·4,02 = **8,04** l/s — _tabl. 2 [NZW]_
* Przepustowość przelewu 20×10 cm przy h = 8 cm: Q = ⅔·μ·b·√(2g)·h^1,5 = ⅔·0,6·0,20·√(2·9,81)·0,08^1,5 = **8,02** l/s — _Poleni [W]_
* Przepustowość rury spustowej DN100 (d_i = 96 mm), f = 0,33: Q_RWP = 2,5·10⁻⁴·k_b^−0,167·d_i^2,667·f^1,667 = 2,5·10⁻⁴·0,25^−0,167·96^2,667·0,33^1,667 = **9,61** l/s — _[NZW]_
* Pole D1: najdłuższa droga spływu i przyrost grubości izolacji spadkowej: ∆h = i·L_max = 0,020·8,67 = **0,173** m

**Pole D1:** RS1: rura wewnętrzna w szachcie — izolacja przeciwroszeniowa i akustyczna, rewizja u podstawy [ZAŁ]; przejście przez stropodach szczelne (paroizolacja!); RS2: rura wewnętrzna w szachcie — izolacja przeciwroszeniowa i akustyczna, rewizja u podstawy [ZAŁ]; przejście przez stropodach szczelne (paroizolacja!).

**Pole D2:** RS3: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ].

**Pole D3:** RS4: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ].

**Pole D4:** RS5: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ]; RS6: rura wewnętrzna w szachcie — izolacja przeciwroszeniowa i akustyczna, rewizja u podstawy [ZAŁ]; przejście przez stropodach szczelne (paroizolacja!).

**Pole PL-E:** RS8: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ]; RS7: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ].

**Pole PL-DA:** RS4: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ].

**Pole PL-2:** RS10: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ]; RS7: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ].

**Pole PL-3:** RS11: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ]; RS12: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ].

**Pole PL-D:** RS8: rura zewnętrzna — czyszczak ≥ 0,3 m nad terenem, osłona do 1,5 m, podgrzewanie wpustu/rury przewodem grzejnym (zamarzanie) [ZAŁ].

| Rura | Pole | DN | d_i [mm] | Trasa | Odbiornik | Q [l/s] | Q_RWP [l/s] |
|:---|:---|---:|---:|:---|:---|---:|---:|
| RS1 | D1 | 100 | 96 | wewn_szacht | zbiornik | 2,01 | 9,61 |
| RS2 | D1 | 100 | 96 | wewn_szacht | zbiornik | 2,01 | 9,61 |
| RS3 | D2 | 100 | 96 | zewn | zbiornik | 0,58 | 9,61 |
| RS4 | D3 | 100 | 96 | zewn | zbiornik | 0,52 | 9,61 |
| RS5 | D4 | 100 | 96 | zewn | zbiornik | 1,36 | 9,61 |
| RS6 | D4 | 100 | 96 | wewn_szacht | zbiornik | 1,36 | 9,61 |
| RS8 | PL-E | 80 | 76 | zewn | zbiornik | 0,55 | 5,15 |
| RS7 | PL-E | 80 | 76 | zewn | zbiornik | 0,55 | 5,15 |
| RS4 | PL-DA | 100 | 96 | zewn | zbiornik | 0,14 | 9,61 |
| RS10 | PL-2 | 80 | 76 | zewn | dach D4 | 0,53 | 5,15 |
| RS7 | PL-2 | 80 | 76 | zewn | zbiornik | 0,53 | 5,15 |
| RS11 | PL-3 | 70 | 66 | zewn | PL-2 | 0,53 | 3,54 |
| RS12 | PL-3 | 70 | 66 | zewn | PL-2 | 0,53 | 3,54 |
| RS8 | PL-D | 80 | 76 | zewn | zbiornik | 0,28 | 5,15 |

Obciążenie wodą spiętrzoną przy zablokowanych wpustach (q_woda) przekazać do obliczeń konstrukcji stropodachów (obciążenie wyjątkowe/zmienne wg decyzji konstruktora).

### 2.1 Dach zielony

* D4: A = 59,1 m²; retencja substratu i warstwy drenażowej ≈ 1,77 m³ (30 dm³/m² [ZAŁ — dane producenta]); ψ = 0,5 (bilans), C = 1,0 (wpusty).
* Warstwy w przegrodzie: bariera przeciwkorzenna: jest, warstwa drenażowa: jest, geowłóknina (filtracyjna): jest, substrat: jest.
* Przy attyce i wpustach opaska żwirowa ≥ 0,3–0,5 m (strefa bez roślin, kontrola wpustów) [ZAŁ; brief §9 pkt 3].

## 3. Odwodnienia liniowe (drzwi bezprogowe, brama garażowa)

| Otwór | Opis | L [m] | A zlewni [m²] | Q [l/s] | Klasa obciążenia | Odbiornik |
|:---|:---|---:|---:|---:|:---|:---|
| O0-03 | drzwi przesuwne HS bez progu (P0) | 2,42 | 6,7 | 0,31 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O0-04 | drzwi przesuwne HS bez progu (P0) | 2,42 | 6,7 | 0,31 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O0-06 | drzwi zewnętrzne bezprogowe (P0) | 1,10 | 2,7 | 0,12 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O0-07 | brama garażowa (P0) | 5,20 | 25,0 | 1,15 | C250 (PN-EN 1433) — ruch samochodów osobowych | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O0-08 | drzwi zewnętrzne bezprogowe (P0) | 1,20 | 3,0 | 0,14 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O0-09 | drzwi zewnętrzne bezprogowe (P0) | 1,30 | 3,3 | 0,15 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| O0-11 | drzwi przesuwne HS bez progu (P0) | 2,60 | 7,2 | 0,33 | A15 / B125 (taras, ruch pieszy) | zbiornik / niecka (przez osadnik) — nie do kanalizacji sanitarnej |
| OL-1 | odwodnienie liniowe z dzialka.yaml | — | — | — | — | SEP-1 → NT-E |
| OL-2 | odwodnienie liniowe z dzialka.yaml | — | — | — | — | opaska / KD-W |
| OL-2W | odwodnienie liniowe z dzialka.yaml | — | — | — | — | KD-W |
| OL-3 | odwodnienie liniowe z dzialka.yaml | — | — | — | — | KD-W |
| OL-4 | odwodnienie liniowe z dzialka.yaml | — | — | — | — | SEP-1 → NT-E |
| OL-5 | odwodnienie liniowe z dzialka.yaml | — | — | — | — | KD-E |
| OL-6 | odwodnienie liniowe z dzialka.yaml | — | — | — | — | RS8 → KD-E |

Odwodnienie liniowe przy drzwiach bez progu: korytko przed progiem na całej szerokości + 0,1 m z każdej strony, spadek nawierzchni tarasu/podjazdu od budynku ≥ 1,5–2 %, ruszt szczelinowy; posadzka wewnętrzna ≥ 2 cm nad rusztem [ZAŁ; brief §9 pkt 4]. Odpływ przez osadnik do zbiornika lub niecki.

## 4. Zbiornik ≤ 5 m³ i niecka (wariant bazowy)

* Powierzchnia zredukowana zlewni (dachy): A_red = Σψ_i·A_i = 0,95·87,4 + 0,95·12,5 + 0,95·11,2 + 0,50·59,1 + 0,95·23,7 + 0,95·3,0 + 0,95·23,0 + 0,95·23,0 + 0,95·6,1 = **210,0** m² — _Aquanet 2024 tab. 2 (W-143)_
* Zdolność chłonna niecki: Q_inf = 1000·A_inf·k_f,nn = 1000·A_n·0,5·k_f = 1000·19,5·5,00·10⁻⁵ = **0,975** l/s — _Aquanet 2024 wzór (2); k_f [ZAŁ — badania]_
* Objętość obliczeniowa (czasza niecki zasilana opadem ψ = 1,0), t_d = 30 min: V_obl = max_td[0,06·q(t_d)·(A_red + A_n)·t_d − 0,06·Q_inf·t_d] = 0,06·157,64·0,0230·30 − 0,06·0,975·30 = **4,76** m³ — _Aquanet 2024 wzór (1); PANDa 2050 C10_
* Minimalna objętość niecki (zbiornik ≤ 5 m³ pełny — bez zaliczenia): V_min = f_b·V_obl = 1,2·4,76 = **5,71** m³ — _f_b wg W-143_
* Wariant: zbiornik pusty na początku opadu (zaliczenie V_zb): V_min' = f_b·max(V_obl − V_zb; 0) = 1,2·max(4,76 − 5,0; 0) = **0,00** m³
* Przyjęta niecka (ogród deszczowy): A_n × h = 19,5 × 0,30 = **5,85** m³ — _W-145_
* Czas opróżniania niecki: t = V_min/Q_inf = 5,71/0,00098/3600 = **1,6** h

| Urządzenie | x, y (układ budynku) | Odl. od budynku [m] | Odl. od granicy [m] |
|:---|:---|---:|---:|
| zbiornik szczelny | 4,00; −7,00 | 6,70 | 11,60 |
| niecka / rozsączanie | 4,00; −15,00 | 12,70 | 8,10 |

### 4.1 Bilans roczny zbiornika (normy opadowe IMGW 1991–2020)

| Mies. | Opad [mm] | Dopływ [m³] | Podlewanie [m³] | Pokryte [m³] | Przelew do niecki [m³] | Stan końcowy [m³] |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 37,7 | 7,13 | 0,00 | 0,00 | 2,13 | 5,00 |
| 2 | 30,7 | 5,80 | 0,00 | 0,00 | 5,80 | 5,00 |
| 3 | 39,9 | 7,54 | 0,00 | 0,00 | 7,54 | 5,00 |
| 4 | 28,6 | 5,41 | 0,00 | 0,00 | 5,41 | 5,00 |
| 5 | 53,8 | 10,17 | 6,00 | 6,00 | 4,17 | 5,00 |
| 6 | 57,5 | 10,87 | 8,00 | 8,00 | 2,87 | 5,00 |
| 7 | 84,4 | 15,95 | 9,00 | 9,00 | 6,95 | 5,00 |
| 8 | 55,9 | 10,57 | 8,00 | 8,00 | 2,57 | 5,00 |
| 9 | 41,2 | 7,79 | 5,00 | 5,00 | 2,79 | 5,00 |
| 10 | 35,4 | 6,69 | 0,00 | 0,00 | 6,69 | 5,00 |
| 11 | 33,6 | 6,35 | 0,00 | 0,00 | 6,35 | 5,00 |
| 12 | 40,1 | 7,58 | 0,00 | 0,00 | 7,58 | 5,00 |

Rocznie: dopływ 101,8 m³, zapotrzebowanie na podlewanie 36,0 m³, pokryte 36,0 m³ (100 %), przelew do niecki 60,8 m³. Opad roczny 538,9 mm (IMGW-PIB, Portal Klimat — Normy klimatyczne 1991–2020 (OPAD_SUMA)).

## 5. Wariant opcjonalny: skrzynki rozsączające

* Skrzynki 8,40 × 1,20 × 0,66 m — powierzchnia infiltracji: A_inf = L·B + ½·2(L + B)·H = **16,42** m² — _Aquanet 2024_
* Zdolność chłonna: Q_inf = 1000·A_inf·k_f,nn = **0,821** l/s
* V_obl (t_d = 30 min) / V_min = f_b·V_obl: 4,48 / 5,38 = **5,38** m³
* Objętość netto skrzynek (porowatość 95 %): V_n = L·B·H·0,95 = **6,32** m³ — _dane producentów [W]_
* Czas opróżniania: t = V_min/Q_inf = **1,8** h — _≤ 24 h_

Skrzynki: osadnik przed urządzeniem; odległości wg W-144; wymagają stanowiska PGW Wody Polskie / pozwolenia wodnoprawnego (D-05) — dlatego nie stanowią wariantu bazowego.

## 6. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-142 | Pole D1: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | 0,03 m | ≥ 0,03 m | SPEŁNIONY | [ZAŁ] ≥ 3 cm — pokrycie przy wpuście (model) |
| W-142 | Pole D1: dno przelewu ≥ pokrycie w miejscu przelewu | 9,460 m | ≥ 9,441 m | SPEŁNIONY | izolacja spadkowa — pokrycie lokalne (model) |
| W-142 | Pole D1: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa) | 9,460 m | ≤ 9,636 m | SPEŁNIONY | brief §9 pkt 4 (wywinięcie ≥ 15 cm) |
| W-142 | Pole D1: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | 0,04 m | ≥ 0,03 m | SPEŁNIONY | [ZAŁ] ≥ 3 cm — pokrycie przy wpuście (model) |
| W-142 | Pole D1: dno przelewu ≥ pokrycie w miejscu przelewu | 9,470 m | ≥ 9,462 m | SPEŁNIONY | izolacja spadkowa — pokrycie lokalne (model) |
| W-142 | Pole D1: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa) | 9,470 m | ≤ 9,636 m | SPEŁNIONY | brief §9 pkt 4 (wywinięcie ≥ 15 cm) |
| W-142 | Pole D1: zwierciadło przy zablokowanych wpustach poniżej wywinięcia hydroizolacji | 9,510 m | < 9,676 m | SPEŁNIONY | PN-EN 12056-3 p. 7 [NZW]; brief §9 |
| W-142 | Rura spustowa RS1: Q ≤ Q_RWP(DN100, f = 0,33) | 2,01 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Rura spustowa RS2: Q ≤ Q_RWP(DN100, f = 0,33) | 2,01 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole D1: przepustowość wpustów ≥ Q | 9,00 l/s | ≥ 4,02 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Pole D1: spadek połaci | 0,020 | ≥ 0,020 | SPEŁNIONY | W-142: R3 H-04 (dobra praktyka) [zalozenie] |
| W-142 | Pole D1: przelewy awaryjne (Q_przel ≥ F_R·Q) | 22,41 l/s | ≥ 8,04 l/s | SPEŁNIONY | PN-EN 12056-3 p. 7, tabl. 2 [NZW]; brief §9 pkt 3 |
| W-142 | Pole D2: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | 0,03 m | ≥ 0,03 m | SPEŁNIONY | [ZAŁ] ≥ 3 cm — pokrycie przy wpuście (model) |
| W-142 | Pole D2: dno przelewu ≥ pokrycie w miejscu przelewu | 6,330 m | ≥ 6,308 m | SPEŁNIONY | izolacja spadkowa — pokrycie lokalne (model) |
| W-142 | Pole D2: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa) | 6,330 m | ≤ 6,520 m | SPEŁNIONY | brief §9 pkt 4 (wywinięcie ≥ 15 cm) |
| W-142 | Pole D2: zwierciadło przy zablokowanych wpustach poniżej wywinięcia hydroizolacji | 6,352 m | < 6,560 m | SPEŁNIONY | PN-EN 12056-3 p. 7 [NZW]; brief §9 |
| W-142 | Rura spustowa RS3: Q ≤ Q_RWP(DN100, f = 0,33) | 0,58 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole D2: przepustowość wpustów ≥ Q | 4,50 l/s | ≥ 0,58 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Pole D2: spadek połaci | 0,020 | ≥ 0,020 | SPEŁNIONY | W-142: R3 H-04 (dobra praktyka) [zalozenie] |
| W-142 | Pole D2: przelewy awaryjne (Q_przel ≥ F_R·Q) | 11,21 l/s | ≥ 1,15 l/s | SPEŁNIONY | PN-EN 12056-3 p. 7, tabl. 2 [NZW]; brief §9 pkt 3 |
| W-142 | Pole D3: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | 0,03 m | ≥ 0,03 m | SPEŁNIONY | [ZAŁ] ≥ 3 cm — pokrycie przy wpuście (model) |
| W-142 | Pole D3: dno przelewu ≥ pokrycie w miejscu przelewu | 6,330 m | ≥ 6,303 m | SPEŁNIONY | izolacja spadkowa — pokrycie lokalne (model) |
| W-142 | Pole D3: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa) | 6,330 m | ≤ 6,520 m | SPEŁNIONY | brief §9 pkt 4 (wywinięcie ≥ 15 cm) |
| W-142 | Pole D3: zwierciadło przy zablokowanych wpustach poniżej wywinięcia hydroizolacji | 6,350 m | < 6,560 m | SPEŁNIONY | PN-EN 12056-3 p. 7 [NZW]; brief §9 |
| W-142 | Rura spustowa RS4: Q ≤ Q_RWP(DN100, f = 0,33) | 0,52 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole D3: przepustowość wpustów ≥ Q | 4,50 l/s | ≥ 0,52 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Pole D3: spadek połaci | 0,020 | ≥ 0,020 | SPEŁNIONY | W-142: R3 H-04 (dobra praktyka) [zalozenie] |
| W-142 | Pole D3: przelewy awaryjne (Q_przel ≥ F_R·Q) | 11,21 l/s | ≥ 1,03 l/s | SPEŁNIONY | PN-EN 12056-3 p. 7, tabl. 2 [NZW]; brief §9 pkt 3 |
| W-142 | Pole D4: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | 0,04 m | ≥ 0,03 m | SPEŁNIONY | [ZAŁ] ≥ 3 cm — pokrycie przy wpuście (model) |
| W-142 | Pole D4: dno przelewu ≥ pokrycie w miejscu przelewu | 3,170 m | ≥ 3,146 m | SPEŁNIONY | izolacja spadkowa — pokrycie lokalne (model) |
| W-142 | Pole D4: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa) | 3,170 m | ≤ 3,415 m | SPEŁNIONY | brief §9 pkt 4 (wywinięcie ≥ 15 cm) |
| W-142 | Pole D4: dno przelewu nad pokryciem (odpływ normalny przez wpusty) | 0,04 m | ≥ 0,03 m | SPEŁNIONY | [ZAŁ] ≥ 3 cm — pokrycie przy wpuście (model) |
| W-142 | Pole D4: dno przelewu ≥ pokrycie w miejscu przelewu | 3,170 m | ≥ 3,149 m | SPEŁNIONY | izolacja spadkowa — pokrycie lokalne (model) |
| W-142 | Pole D4: dno przelewu poniżej wywinięcia hydroizolacji (− rezerwa) | 3,170 m | ≤ 3,415 m | SPEŁNIONY | brief §9 pkt 4 (wywinięcie ≥ 15 cm) |
| W-142 | Pole D4: zwierciadło przy zablokowanych wpustach poniżej wywinięcia hydroizolacji | 3,209 m | < 3,455 m | SPEŁNIONY | PN-EN 12056-3 p. 7 [NZW]; brief §9 |
| W-142 | Rura spustowa RS5: Q ≤ Q_RWP(DN100, f = 0,33) | 1,36 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Rura spustowa RS6: Q ≤ Q_RWP(DN100, f = 0,33) | 1,36 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole D4: przepustowość wpustów ≥ Q | 9,00 l/s | ≥ 2,72 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Pole D4: spadek połaci | 0,020 | ≥ 0,020 | SPEŁNIONY | W-142: R3 H-04 (dobra praktyka) [zalozenie] |
| W-142 | Pole D4: przelewy awaryjne (Q_przel ≥ F_R·Q) | 22,41 l/s | ≥ 5,43 l/s | SPEŁNIONY | PN-EN 12056-3 p. 7, tabl. 2 [NZW]; brief §9 pkt 3 |
| W-142 | Rura spustowa RS8: Q ≤ Q_RWP(DN80, f = 0,33) | 0,55 l/s | ≤ 5,15 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Rura spustowa RS7: Q ≤ Q_RWP(DN80, f = 0,33) | 0,55 l/s | ≤ 5,15 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole PL-E: przepustowość wpustów ≥ Q | 3,40 l/s | ≥ 1,09 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Rura spustowa RS4: Q ≤ Q_RWP(DN100, f = 0,33) | 0,14 l/s | ≤ 9,61 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole PL-DA: przepustowość wpustów ≥ Q | 1,70 l/s | ≥ 0,14 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Rura spustowa RS10: Q ≤ Q_RWP(DN80, f = 0,33) | 0,53 l/s | ≤ 5,15 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Rura spustowa RS7: Q ≤ Q_RWP(DN80, f = 0,33) | 0,53 l/s | ≤ 5,15 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole PL-2: przepustowość wpustów ≥ Q | 3,40 l/s | ≥ 1,06 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Rura spustowa RS11: Q ≤ Q_RWP(DN70, f = 0,33) | 0,53 l/s | ≤ 3,54 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Rura spustowa RS12: Q ≤ Q_RWP(DN70, f = 0,33) | 0,53 l/s | ≤ 3,54 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole PL-3: przepustowość wpustów ≥ Q | 3,40 l/s | ≥ 1,06 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-142 | Rura spustowa RS8: Q ≤ Q_RWP(DN80, f = 0,33) | 0,28 l/s | ≤ 5,15 l/s | SPEŁNIONY | PN-EN 12056-3 (rury spustowe) [NZW] |
| W-142 | Pole PL-D: przepustowość wpustów ≥ Q | 1,70 l/s | ≥ 0,28 l/s | SPEŁNIONY | PN-EN 12056-3 p. 6 |
| W-119 | Dach zielony D4: warstwa „bariera przeciwkorzenna” w przegrodzie DZ1 | 1 | ≥ 1 | SPEŁNIONY | brief §9 pkt 3; schemat modelu §6 |
| W-119 | Dach zielony D4: warstwa „warstwa drenażowa” w przegrodzie DZ1 | 1 | ≥ 1 | SPEŁNIONY | brief §9 pkt 3; schemat modelu §6 |
| W-119 | Dach zielony D4: warstwa „geowłóknina (filtracyjna)” w przegrodzie DZ1 | 1 | ≥ 1 | SPEŁNIONY | brief §9 pkt 3; schemat modelu §6 |
| W-119 | Dach zielony D4: warstwa „substrat” w przegrodzie DZ1 | 1 | ≥ 1 | SPEŁNIONY | brief §9 pkt 3; schemat modelu §6 |
| W-145 | Pojemność szczelnego zbiornika (bez zgłoszenia) | 5,00 m³ | ≤ 5,00 m³ | SPEŁNIONY | W-145: PB art. 29 ust. 2 pkt 36 (5–15 m³ — zgłoszenie, ust. 1 pkt 38) |
| W-143 | Niecka: pojemność ≥ V_min (zbiornik pełny — bez zaliczenia) | 5,85 m³ | ≥ 5,71 m³ | SPEŁNIONY | Aquanet 2024 wzór (1), f_b |
| W-145 | Niecka: głębokość | 0,30 m | ≤ 0,30 m | SPEŁNIONY | W-145 (≤ 0,3 m) |
| W-143 | Niecka: czas opróżniania | 1,6 h | ≤ 24,0 h | SPEŁNIONY | W-143: Aquanet 2024 zał. C [zalozenie] |
| W-144 | Dno niecki nad maks. zwierciadłem wód gruntowych | 3,50 m | ≥ 1,00 m | SPEŁNIONY | Aquanet 2024; W-144 |
| W-144 | niecka / rozsączanie: odległość od fundamentów | 12,70 m | ≥ 3,00 m | SPEŁNIONY | W-144 (S-4) |
| W-144 | niecka / rozsączanie: odległość od granicy działki | 8,10 m | ≥ 2,00 m | SPEŁNIONY | W-144 |

## Podsumowanie sprawdzeń

Warunków: 64; spełnionych: 64; niespełnionych: 0; informacyjnych: 0.

## Źródła

1. PN-EN 12056-3:2002 — p. 4 (Q = r·A·C), tabl. 2 (współczynnik ryzyka), rury spustowe [NZW — treść płatna]
2. Aquanet S.A., Załącznik C — Metodyka obliczania niezbędnej objętości zbiorników detencyjno-retencyjnych, 2024, wzory (1)–(2), tab. 2–3
3. IMGW-PIB, Normy klimatyczne 1991–2020, Poznań (12330) — sumy opadów https://klimat.imgw.pl/pl/climate-normals/OPAD_SUMA
4. Dąbrowski W., Dąbrowska B., Jasik H., Odwadnianie dachów — wymiarowanie rynien, Rynek Instalacyjny 12/2015 (r = 0,03–0,05 l/(s·m²))
5. Rejestr wymagań W-018, W-019, W-119, W-142…W-146; brief §9 (wymagania Inwestora 25.09.2026)
