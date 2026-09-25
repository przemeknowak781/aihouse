# Bilans mocy instalacji elektrycznej

Obiekt: Dom LAMELA. Dane przykładowe oznaczono [ZAŁ].

## 1. Podstawy i założenia

* WT §180–§189 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-180…W-195; rejestr R7 §3.1–3.3.
* Moc przyłączeniowa 27 kW / zabezpieczenie przedlicznikowe 40 A — założenie do wniosku o warunki przyłączenia (ENEA Operator, grupa V) [ZAŁ].
* Współczynniki jednoczesności: oswietlenie 0,7, gniazda 0,2, gniazda_kuchnia 0,5, gniazda_lazienka 0,3, gotowanie 0,6, agd 0,6, pc 1,0, grzalka 1,0, went 1,0, sterowanie 1,0, ev 1,0, zewn 0,3, tele 1,0, napedy 0,3, pompa 0,3, pv 0,0 [ZAŁ].
* Obwody gniazd: moc umowna 2,0 kW/obwód; oświetlenie LED 5 W/m² [ZAŁ].
* DLM (dynamiczne zarządzanie mocą): ograniczenie mocy ładowarki EV i blokada grzałki PC przy przekroczeniu mocy przyłączeniowej.

## 2. Odbiorniki

| Obw. | Odbiornik | Grupa | P [kW] | Fazy | cos φ | k_j | P_s [kW] | DLM | Faza |
|:---|:---|:---|---:|---:|---:|---:|---:|:---|:---|
| L1 | Oświetlenie P0 | oswietlenie | 0,56 | 1 | 0,95 | 0,70 | 0,39 | — | L1 |
| L2 | Oświetlenie P1 | oswietlenie | 0,43 | 1 | 0,95 | 0,70 | 0,30 | — | L2 |
| L3 | Oświetlenie P2 | oswietlenie | 0,33 | 1 | 0,95 | 0,70 | 0,23 | — | L3 |
| L4 | Oświetlenie garażu i pom. technicznego | oswietlenie | 0,26 | 1 | 0,95 | 0,70 | 0,18 | — | L1 |
| L5 | Oświetlenie zewnętrzne (wejście, elewacje, taras) | oswietlenie | 0,20 | 1 | 0,95 | 0,70 | 0,14 | — | L2 |
| G1 | Gniazda P0: 0.10 Pokój gościnny / gabinet, 0.08 Przedpokój gościnny, 0.14 Szacht instalacyjny SI, 0.04 Klatka schodowa, 0.16 Schowek pod spocznikiem (h < 1,40), 0.07 Pas komunikacyjny przy schodach, 0.05 Spiżarnia, 0.15 Schowek pod schodami (h 1,40–2,20), 0.02 Hol, 0.01 Wiatrołap, 0.11 Przedsionek gospodarczy | gniazda | 2,00 | 1 | 0,95 | 0,20 | 0,40 | — | L1 |
| G2 | Gniazda P1: 1.04 Pokój dziecka 2, 1.03 Pokój dziecka 1, 1.09 Szacht instalacyjny SI, 1.01 Hol, 1.06 Klatka schodowa | gniazda | 2,00 | 1 | 0,95 | 0,20 | 0,40 | — | L3 |
| G3 | Gniazda P1: 1.02 Pokój rodzinny / biblioteka (boks C) | gniazda | 2,00 | 1 | 0,95 | 0,20 | 0,40 | — | L2 |
| G4 | Gniazda P2: 2.02 Sypialnia rodziców, 2.03 Garderoba (przedpokój apartamentu), 2.08 Szacht instalacyjny SI, 2.06 Klatka schodowa (wyjście z biegu 2, pustka), 2.01 Hol | gniazda | 2,00 | 1 | 0,95 | 0,20 | 0,40 | — | L1 |
| G5 | Gniazda P2: 2.05 Gabinet / pokój gościnny okazjonalny | gniazda | 2,00 | 1 | 0,95 | 0,20 | 0,40 | — | L3 |
| G6 | Gniazda kuchenne 1 (0.06 Salon + jadalnia + kuchnia) | gniazda_kuchnia | 2,00 | 1 | 0,95 | 0,50 | 1,00 | — | L1 |
| G7 | Gniazda kuchenne 2 (0.06 Salon + jadalnia + kuchnia) | gniazda_kuchnia | 2,00 | 1 | 0,95 | 0,50 | 1,00 | — | L3 |
| G8 | Gniazda łazienki (0.03 WC gościnne) | gniazda_lazienka | 2,00 | 1 | 0,95 | 0,30 | 0,60 | — | L2 |
| G9 | Gniazda łazienki (0.09 Łazienka gościnna (natrysk)) | gniazda_lazienka | 2,00 | 1 | 0,95 | 0,30 | 0,60 | — | L1 |
| G10 | Gniazda łazienki (1.05 Łazienka dzieci (wanna)) | gniazda_lazienka | 2,00 | 1 | 0,95 | 0,30 | 0,60 | — | L3 |
| G11 | Gniazda łazienki (1.07 WC z natryskiem) | gniazda_lazienka | 2,00 | 1 | 0,95 | 0,30 | 0,60 | — | L2 |
| G12 | Gniazda łazienki (2.04 Łazienka rodziców) | gniazda_lazienka | 2,00 | 1 | 0,95 | 0,30 | 0,60 | — | L1 |
| G13 | Gniazda garażu / pom. technicznego (IP44) | gniazda | 2,00 | 1 | 0,95 | 0,20 | 0,40 | — | L2 |
| G14 | Gniazda zewnętrzne (taras, ogród; IP44/IP54) | zewn | 2,00 | 1 | 0,95 | 0,30 | 0,60 | — | L3 |
| D1 | Płyta indukcyjna | gotowanie | 7,40 | 3 | 1,00 | 0,60 | 4,44 | — | L1L2L3 |
| D2 | Piekarnik | gotowanie | 3,50 | 1 | 1,00 | 0,60 | 2,10 | — | L2 |
| D3 | Zmywarka | agd | 2,20 | 1 | 0,95 | 0,60 | 1,32 | — | L3 |
| D4 | Pralka | agd | 2,20 | 1 | 0,95 | 0,60 | 1,32 | — | L2 |
| D5 | Suszarka | agd | 2,50 | 1 | 0,95 | 0,60 | 1,50 | — | L3 |
| D6 | Pompa ciepła — jednostka zewnętrzna (PC-R290-07 (przykład)) | pc | 2,67 | 1 | 0,95 | 1,00 | 2,67 | — | L1 |
| D7 | Grzałka rezerwowa PC / zasobnika c.w.u. (6,0 kW) | grzalka | 6,00 | 3 | 1,00 | 1,00 | 6,00 | tak | L1L2L3 |
| D8 | Sterowanie PC, pompy obiegowe, listwy ogrzewania podłogowego | sterowanie | 0,30 | 1 | 0,95 | 1,00 | 0,30 | — | L3 |
| D9 | Rekuperator (V ≈ 365 m³/h) | went | 0,18 | 1 | 0,95 | 1,00 | 0,18 | — | L3 |
| D10 | Falownik PV 3f (6,0 kW AC) | pv | 6,00 | 3 | 1,00 | 0,00 | gen. | — | L1L2L3 |
| D11 | Ładowarka EV 11 kW (3f) — garaż; przewód na 22 kW | ev | 11,00 | 3 | 0,99 | 1,00 | 11,00 | tak | L1L2L3 |
| D12 | Napęd bramy garażowej | napedy | 0,30 | 1 | 0,95 | 0,30 | 0,09 | — | L3 |
| D13 | Brama wjazdowa, furtka, wideodomofon (linia ogrodzenia) | napedy | 0,50 | 1 | 0,95 | 0,30 | 0,15 | — | L1 |
| D14 | Teletechnika: ONT, router, szafka RACK, SSWiN | tele | 0,20 | 1 | 0,95 | 1,00 | 0,20 | — | L2 |
| D15 | Pompa zbiornika wody deszczowej (podlewanie) | pompa | 0,80 | 1 | 0,95 | 0,30 | 0,24 | — | L1 |
| D16 | Napędy osłon przeciwsłonecznych (19 szt.) | napedy | 1,90 | 1 | 0,95 | 0,30 | 0,57 | — | L2 |

## 3. Moc szczytowa i przyłączeniowa

* Moc zainstalowana (bez generacji PV): P_i = ΣP = **71,4** kW
* Moc szczytowa bez zarządzania mocą: P_s = Σk_j·P = **41,3** kW — _k_j [ZAŁ]_
* Granica zarządzania mocą (moc przyłączeniowa i prąd zabezpieczenia przy cos φ): P_lim = min(P_przył; √3·U·I_zab·cos φ) = min(27,0; √3·400·40·0,95/1000) = **26,33** kW
* Moc szczytowa z DLM (odbiorniki sterowane ograniczone): P_s,DLM = P_nst + min(P_st; P_lim − P_nst) = 24,32 + min(17,00; 26,33 − 24,32) = **26,2** kW
* Prąd szczytowy: I_B = P_s/(√3·U·cos φ) = 26210/(√3·400·0,95) = **39,8** A
* Kontrolnie N SEP-E-002: 30 kVA + ogrzewanie elektryczne (PC + grzałka): P = 30·cos φ + P_ogrz = 30·0,95 + 8,67 = **37,2** kW — _R7-L08 [W]_
* Moc odpowiadająca zabezpieczeniu przedlicznikowemu: P = √3·400·I_zab = √3·400·40 = **27,7** kW — _R7-L09_

## 4. Podział na fazy (moc szczytowa)

| Faza | P_s [kW] | I [A] |
|:---|---:|---:|
| L1 | 8,74 | 40,0 |
| L2 | 8,74 | 40,0 |
| L3 | 8,73 | 40,0 |

Asymetria (max − min)/średnia = 0 %. Odbiorniki 1-fazowe przypisano algorytmem zachłannym (najpierw największe, do najmniej obciążonej fazy).

## 5. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-192 | Moc szczytowa z DLM ≤ moc przyłączeniowa | 26,21 kW | ≤ 27,00 kW | SPEŁNIONY | W-192: R7 3.1 (zabezpieczenie przedlicznikowe 40 A) [zalozenie] |
| W-192 | Prąd szczytowy ≤ zabezpieczenie przedlicznikowe | 39,8 A | ≤ 40,0 A | SPEŁNIONY | R7-L09 |
| W-192 | Najbardziej obciążona faza: prąd ≤ zabezpieczenie przedlicznikowe | 40,0 A | ≤ 40,0 A | SPEŁNIONY |  |
| W-192 | Moc przyłączeniowa ≤ 40 kW (grupa V) | 27,00 kW | ≤ 40,00 kW | SPEŁNIONY | RSys §3 ust. 1 pkt 5 |
| W-192 | Moc przyłączeniowa ↔ zabezpieczenie (√3·400·I_zab, cos φ = 1) | 27,00 kW | ≤ 27,71 kW | SPEŁNIONY | R7-L09 |
| W-180 | Asymetria obciążenia faz (max − min)/średnia | 0,00 | ≤ 0,30 | SPEŁNIONY | praktyka [ZAŁ] |
| W-194 | Moc PV ≤ moc przyłączeniowa (zgłoszenie mikroinstalacji) | 6,45 kW | ≤ 27,00 kW | SPEŁNIONY | Pr. energ. art. 7 ust. 8d4 |
| W-192 | Moc szczytowa BEZ zarządzania mocą 41,3 kW > P_przył — DLM WYMAGANY (ograniczenie EV, blokada grzałek) | 41,32 kW | — | informacyjnie | R7 §3.1 |

## Podsumowanie sprawdzeń

Warunków: 8; spełnionych: 7; niespełnionych: 0; informacyjnych: 1.

## Źródła

1. WT §64, §102, §180–§189 (t.j. Dz.U. 2022 poz. 1225 ze zm.)
2. RSys (t.j. Dz.U. 2025 poz. 919) §3 ust. 1 pkt 5; Pr. energ. art. 7
3. N SEP-E-002 — wg SEP (Boczkowski 2013) [W]
4. Rejestr R7 §3.1 (bilans szacunkowy), R7-L08, R7-L09
