# Ochrona odgromowa — ocena ryzyka (uproszczona), uziom, połączenia wyrównawcze

Obiekt: Dom testowy pipeline'u 3D. PN-EN 62305-2 (WT: 2008; aktualna PN-EN IEC 62305-2:2025-09). Wynik wstępny — [NZW].

## 1. Podstawy i założenia

* WT §53 ust. 2, §184 ust. 1–3 (t.j. Dz.U. 2022 poz. 1225 ze zm.; art. 102a PB); W-187, W-188, W-191; D-13.
* C_D = 1,0, L_L = 1000 m, C_I = 0,5, C_E = 0,5, r_t = 0,0100, r_p = 1,0, h_z = 1, L_T = L_F = 10⁻² [NZW — współczynniki wg R7-K05; pełna analiza w PT programem wg PN-EN IEC 62305-2:2025].
* Linia telekomunikacyjna: światłowód dielektryczny — pominięta w analizie.
* Niezależnie od wyniku: uziom (otokowy lub fundamentowy) z wyprowadzeniami pod LPS i SPD typu 1+2 w RG (R7 §3.7).

## 2. Częstość zagrożeń

* Wysokość budynku nad terenem (najwyższa attyka), części: 1: H = **6,85** m — _model_
* Powierzchnia zbierania wyładowań bezpośrednich: A_D = pole(∪ bufor(obrys_i; 3H_i)) = **2165** m² — _PN-EN 62305-2 zał. A (A.2)_
* Liczba wyładowań w obiekt: N_D = N_G·A_D·C_D·10⁻⁶ = 1,8·2165·1,0·10⁻⁶ = **0,0039** 1/rok — _W-186: SEP (Boczkowski 2013) z mapy PN-86/E-05003/01 — norma wycofana, dane historyczne (na północ od 51°30′) [niezweryfikowane]_
* Liczba wyładowań w linię zasilającą (kabel nN): N_L = N_G·40·L_L·C_I·C_E·C_T·10⁻⁶ = 1,8·40·1000·0,5·0,5·1,0·10⁻⁶ = **0,0180** 1/rok — _zał. A (A.4)_
* Klasa ryzyka pożaru: q_f,śr / q_f,80%: q_f = 780 / 948 MJ/m² = **zwykłe / wysokie** — _PN-EN 1991-1-2 zał. E tabl. E.4 [W]; progi 400/800 MJ/m² (R7-K02)_

## 3. Ryzyko R1 — scenariusze

| Scenariusz | Klasa pożarowa | R_A | R_B | R_U | R_V | R1 | R1 ≤ R_T = 10⁻⁵ |
|:---|:---|---:|---:|---:|---:|---:|:---|
| brak ochrony | zwykłe | 3,90·10⁻⁷ | 3,90·10⁻⁷ | 1,80·10⁻⁶ | 1,80·10⁻⁶ | 4,38·10⁻⁶ | tak |
| brak ochrony | wysokie | 3,90·10⁻⁷ | 3,90·10⁻⁶ | 1,80·10⁻⁶ | 1,80·10⁻⁵ | 2,41·10⁻⁵ | **NIE** |
| SPD typ 1 (LPL III–IV) — projektowane (W-186) | zwykłe | 3,90·10⁻⁷ | 3,90·10⁻⁷ | 9,00·10⁻⁸ | 9,00·10⁻⁸ | 9,59·10⁻⁷ | tak |
| SPD typ 1 (LPL III–IV) — projektowane (W-186) | wysokie | 3,90·10⁻⁷ | 3,90·10⁻⁶ | 9,00·10⁻⁸ | 9,00·10⁻⁷ | 5,28·10⁻⁶ | tak |
| SPD T1 + gaśnica (r_p = 0,5) | zwykłe | 3,90·10⁻⁷ | 1,95·10⁻⁷ | 9,00·10⁻⁸ | 4,50·10⁻⁸ | 7,20·10⁻⁷ | tak |
| SPD T1 + gaśnica (r_p = 0,5) | wysokie | 3,90·10⁻⁷ | 1,95·10⁻⁶ | 9,00·10⁻⁸ | 4,50·10⁻⁷ | 2,88·10⁻⁶ | tak |
| LPS IV + SPD T1 | zwykłe | 7,79·10⁻⁸ | 7,79·10⁻⁸ | 9,00·10⁻⁸ | 9,00·10⁻⁸ | 3,36·10⁻⁷ | tak |
| LPS IV + SPD T1 | wysokie | 7,79·10⁻⁸ | 7,79·10⁻⁷ | 9,00·10⁻⁸ | 9,00·10⁻⁷ | 1,85·10⁻⁶ | tak |
| LPS III + SPD T1 | zwykłe | 3,90·10⁻⁸ | 3,90·10⁻⁸ | 9,00·10⁻⁸ | 9,00·10⁻⁸ | 2,58·10⁻⁷ | tak |
| LPS III + SPD T1 | wysokie | 3,90·10⁻⁸ | 3,90·10⁻⁷ | 9,00·10⁻⁸ | 9,00·10⁻⁷ | 1,42·10⁻⁶ | tak |

**Decyzja: LPS NIEWYMAGANY (R1 ≤ R_T przy SPD T1 dla obu klas obciążenia ogniowego).**

## 4. Uziom

* Uziom fundamentowy w ławach: średnica zastępcza: D = √(4A/π) = √(4·91,0/π) = **10,77** m
* Rezystancja uziemienia (orientacyjnie, ρ = 400 Ω·m [ZAŁ]): R ≈ 2ρ/(πD) = 2·400/(π·10,77) = **23,7** Ω — _DEHN LPG [W]; pomiar po wykonaniu_

* Typ: fundamentowy w ławach (zbrojenie + płaskownik/pręt w betonie) — WT §184 ust. 1; UWAGA: przy izolacji przeciwwodnej z folii > 0,5 mm lub XPS pod/na fundamencie — uziom otokowy (PN-HD 60364-5-54 zał. C.2).
* Materiał: pręt stalowy Ø10 mm lub płaskownik 30×3,5 mm w betonie, otulina ≥ 5 cm, mocowany do zbrojenia co ≤ 2 m, bez drutu wiązałkowego (W-187).
* Wyprowadzenia: GSU w pomieszczeniu technicznym (≥ 16 mm² Cu, W-188); ZKP / rozdział PEN (jeśli wymaga OSD); 4 wyprowadzenia w narożnikach/co ≤ 15 m pod przewody odprowadzające LPS (rezerwa); konstrukcja PV (połączenie wyrównawcze, jeden punkt).
* TN-S: brak normowej wartości rezystancji uziemienia GSU; przy LPS zalecane R ≤ 10 Ω (PN-EN 62305-3) — sprawdzić pomiarem; OSD może określić wymagania dla uziemienia PEN w warunkach przyłączenia.

## 5. LPS — parametry (gdy wymagany / rezerwa)

* Klasa LPS: IV (III przy wyniku rozstrzygającym „wysokie”); oczka zwodów 20 × 20 m (III: 15 × 15 m); promień kuli 60 m (III: 45 m).
* Liczba przewodów odprowadzających: IV — 2, III — 3 (co 20/15 m obwodu).
* Odstęp separacyjny (PV, instalacje na dachu): s = k_i·(k_c/k_m)·l = 0,04·(0,66/1)·6,85 ≈ **0,18 m** [NZW].
* zwody poziome na attykach i w oczkach na dachach płaskich; iglice przy wywiewkach/czerpniach/PV; przewody odprowadzające w elewacji (pod okładziną w rurach niepalnych) do złączy kontrolnych i uziomu otokowego.

## 6. Połączenia wyrównawcze

| Element | Miejsce | Przekrój / uwagi |
|:---|:---|:---|
| Główna szyna uziemiająca (GSU) | pomieszczenie techniczne, przy RG | przewód uziemiający ≥ 16 mm² Cu (W-188) |
| Wodociąg metalowy (przed/za wodomierzem — mostek) | zestaw wodomierzowy | ≥ 6 mm² Cu (tylko przy rurach przewodzących) |
| Rury c.o./c.w.u. metalowe, zasobnik, bufor | pom. techniczne | ≥ 6 mm² Cu |
| Kanały wentylacyjne metalowe, obudowa rekuperatora |  | ≥ 6 mm² Cu (WT §183 ust. 1a) |
| Zbrojenie fundamentów / płyty | zaciski przyłączeniowe | ≥ 16 mm² Cu / Ø10 Fe |
| Konstrukcja PV (uziemienie funkcjonalne, jeden punkt) | dach | wg DTR i 5-54 (≥ 6 mm² Cu) (712.444.5.5.101) |
| Obudowa szafki teletechnicznej / RACK |  | ≥ 6 mm² Cu (WT §183 ust. 1a pkt 8) |
| Łazienki — miejscowe połączenia wyrównawcze | łazienki | wg PN-HD 60364-7-701:2025-02 (przy tworzywach zwykle niewymagane) |
| Balustrady, lamele stalowe/aluminiowe na elewacji, stolarka metalowa przy zwodach |  | przy LPS — w strefie odstępu separacyjnego |

## 7. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-191 | R1 (SPD T1, klasa „zwykłe”) ≤ R_T | 0,0000010 1/rok | ≤ 0,0000100 1/rok | SPEŁNIONY | W-191: PN-EN 62305-2 (ryzyko tolerowane R1) [niezweryfikowane] |
| W-191 | R1 (SPD T1, klasa „wysokie”) ≤ R_T | 0,0000053 1/rok | ≤ 0,0000100 1/rok | SPEŁNIONY | PN-EN 62305-2 [NZW] |
| W-191 | Odstęp separacyjny PV od zwodów LPS (jeśli LPS) — wymagany s | 0,18 m | — | informacyjnie | PN-EN 62305-3 p. 6.3 [NZW] |

## Podsumowanie sprawdzeń

Warunków: 3; spełnionych: 2; niespełnionych: 0; informacyjnych: 1.

## Źródła

1. PN-EN 62305-2:2008 (wycofana; wydanie powołane w zał. 1 WT) i PN-EN 62305-2:2012 (wycofana), zał. A–C — metodyka obliczeń; PN-EN IEC 62305-2:2025-09 (aktualna, wersja angielska) — sprawdzenie kontrolne nie wykonane, uzasadnienie w części opisowej PT
2. Rejestr R7: R7-A05, R7-K01…K05, R7-G01…G08; D-13
3. SEP (Boczkowski 2013) — N_G = 1,8 dla Poznania, z mapy PN-86/E-05003/01 (norma wycofana — dane historyczne) [W]
4. PN-EN 1991-1-2 zał. E tabl. E.4 — gęstość obciążenia ogniowego [W]
5. DEHN, Lightning Protection Guide — rezystancja uziomów otokowych/fundamentowych [W]
