# Wilgotność: f_Rsi i kondensacja międzywarstwowa

## Ryzyko rozwoju pleśni — czynnik temperaturowy f_Rsi (PN-EN ISO 13788:2013 rozdz. 5)

**Podstawa:** PN-EN ISO 13788:2013-05 rozdz. 5; WT § 321, zał. 2 pkt 2.2.1–2.2.3 (f_Rsi ≥ f_Rsi,kryt; dopuszczalnie 0,72); dane klimatyczne TMY Poznań (MIiR)

> Warunki wewnętrzne: φ_i = 50 % przy θ_i = 20 °C (WT zał. 2 pkt 2.2.2); kryterium φ_si ≤ 80 %.

| Mies. | θ_e [°C] | φ_e [%] | p_e [Pa] | p_i [Pa] | p_sat,min [Pa] | θ_si,min [°C] | f_Rsi,min |
|:---|:---|:---|:---|:---|:---|:---|:---|
| I | 0,2 | 86 | 534 | 1 168 | 1 461 | 12,6 | 0,628 |
| II | −1,8 | 86 | 456 | 1 168 | 1 461 | 12,6 | 0,661 |
| III | 2,7 | 79 | 585 | 1 168 | 1 461 | 12,6 | 0,573 |
| IV | 8,3 | 68 | 748 | 1 168 | 1 461 | 12,6 | 0,372 |
| V | 13,0 | 62 | 927 | 1 168 | 1 461 | 12,6 | −0,048 |
| VI | 16,8 | 70 | 1 336 | 1 168 | 1 461 | 12,6 | −1,327 |
| VII | 18,2 | 72 | 1 501 | 1 168 | 1 461 | 12,6 | −3,215 |
| VIII | 18,4 | 72 | 1 530 | 1 168 | 1 461 | 12,6 | −3,553 |
| IX | 13,5 | 81 | 1 254 | 1 168 | 1 461 | 12,6 | −0,138 |
| X | 7,0 | 88 | 882 | 1 168 | 1 461 | 12,6 | 0,432 |
| XI | 2,2 | 91 | 648 | 1 168 | 1 461 | 12,6 | 0,586 |
| XII | −0,1 | 93 | 561 | 1 168 | 1 461 | 12,6 | 0,634 |

Miesiąc krytyczny: **II**, f_Rsi,max = **0,661**; wartość dopuszczona przez WT: 0,72. Do sprawdzeń przyjęto zachowawczo f_Rsi,wym = max(f_Rsi,max; 0,72) = **0,720**.

| Element | Opis | f_Rsi | Źródło | f_Rsi ≥ 0,720 |
|:---|:---|---:|:---|:---|
| POD-0 | przegroda (podloga_grunt), U = 0,17 | 0,957 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | ✔ spełnia |
| SZ1 | przegroda (sciana_zewn), U = 0,17 | 0,959 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | ✔ spełnia |
| SD-D1 | przegroda (dach), U = 0,084 | 0,979 | 1 − U·0,25 (PN-EN ISO 13788 p. 4.3) | ✔ spełnia |
| AUTO-01 | ościeża, nadproża i progi/parapety otworów (obwód otworu) (oscieze) | — | do wyznaczenia — symulacja PN-EN ISO 10211 (mostki2d) | — |
| AUTO-02 | narożnik zewnętrzny (wypukły) ścian zewnętrznych (naroznik_wypukly) | — | do wyznaczenia — symulacja PN-EN ISO 10211 (mostki2d) | — |
| AUTO-03 | połączenie ściana zewnętrzna – podłoga na gruncie / płyta fundamentowa (cokół) (sciana_grunt) | — | do wyznaczenia — symulacja PN-EN ISO 10211 (mostki2d) | — |
| AUTO-04 | połączenie ściany zewnętrznej ze stropem pośrednim (strop_posredni) | — | do wyznaczenia — symulacja PN-EN ISO 10211 (mostki2d) | — |
| AUTO-05 | połączenie stropodachu ze ścianą zewnętrzną (attyka / okap) (attyka) | — | do wyznaczenia — symulacja PN-EN ISO 10211 (mostki2d) | — |
| AUTO-06 | płyta wspornikowa przechodząca przez ścianę zewnętrzną — łącznik termoizolacyjny (plyta_wspornikowa_lacznik) | 0,820 | deklaracja łącznika — dane przykładowe z deklaracji typowego łącznika termoizolacyjnego do płyt wspornikowych (lub równoważny) [DANE PRZYKŁADOWE – FIKCYJNE] | ✔ spełnia |

Dla porównania — klasa wilgotności 3 (PN-EN ISO 13788 zał. A): miesiąc krytyczny 12, f_Rsi,max = 0,800 (informacyjnie; wymaganie WT — φ_i = 50 %).

## Kondensacja międzywarstwowa — metoda Glasera (PN-EN ISO 13788:2013 rozdz. 6)

**Podstawa:** PN-EN ISO 13788:2013-05 rozdz. 6; WT § 321 ust. 2, zał. 2 pkt 2.2.4–2.2.5; dane klimatyczne TMY Poznań (MIiR, WMO 12330)

> s_d = μ·d; g_c = δ₀·[(p_{c−1} − p_c)/Δs' − (p_c − p_{c+1})/Δs''], δ₀ = 2·10⁻¹⁰ kg/(m·s·Pa).
> Wymagane s_d paroizolacji — najmniejsze s_d warstwy po ciepłej stronie izolacji: (1) przy którym nie występuje kondensacja w żadnym miesiącu; (2) przy którym kondensat wysycha w cyklu rocznym i M_a,max ≤ kryterium (WT zał. 2 pkt 2.2.5) — bisekcja do 1500 m.

| Przegroda | Nazwa | Rola | Kondensacja | M_a,max [g/m²] | Wysycha | s_d paroizol. istn. [m] | s_d wym. — brak kondensacji [m] | s_d wym. — kondensacja dopuszczalna [m] | Ocena |
|:---|:---|:---|---:|---:|---:|---:|---:|---:|:---|
| SZ1 | Ściana zewnętrzna nośna, silikat 18 + ETICS EPS 20 | sciana_zewn | nie | 0 | tak | brak | 0 (nie wymaga) | 0 (nie wymaga) | ✔ spełnia |
| SD-D1 | Stropodach pełny, odwrócony spadek PIR | dach | tak | 13 | tak | 100,0 | > 1500 (nieosiągalne) | 44,1 | ✔ spełnia |

### SZ1 — Ściana zewnętrzna nośna, silikat 18 + ETICS EPS 20

| Lp. | Warstwa (od wnętrza) | Funkcja | d [cm] | R [m²K/W] | μ | s_d [m] |
|---:|:---|:---|---:|---:|---:|---:|
| 1 | Tynk gipsowy maszynowy | tynk | 1,5 | 0,037 | 10 | 0,15 |
| 2 | Bloczek wapienno-piaskowy 18 cm, kl. 20 | konstrukcja | 18,0 | 0,234 | 15 | 2,70 |
| 3 | Styropian grafitowy EPS 031 | izolacja | 20,0 | 6,452 | 30 | 6,00 |
| 4 | Tynk silikonowy cienkowarstwowy, biały | tynk | 0,7 | 0,010 | 60 | 0,42 |

**Ocena:** brak kondensacji międzywarstwowej. Warunki wewnętrzne: klasa wilgotności 3 (PN-EN ISO 13788 zał. A: budynki o nieznanym zagęszczeniu), p_i = p_e + 1,10·Δp.

Wymagane s_d paroizolacji (po ciepłej stronie izolacji): brak kondensacji — 0 (nie wymaga) m; kondensacja dopuszczalna (wysycha, M_a ≤ 500 g/m²) — 0 (nie wymaga) m; istniejąca warstwa: brak.

![Glaser SZ1](glaser_SZ1.png)

### SD-D1 — Stropodach pełny, odwrócony spadek PIR

| Lp. | Warstwa (od wnętrza) | Funkcja | d [cm] | R [m²K/W] | μ | s_d [m] |
|---:|:---|:---|---:|---:|---:|---:|
| 1 | Tynk gipsowy maszynowy | tynk | 1,0 | 0,025 | 10 | 0,10 |
| 2 | Żelbet C30/37 | konstrukcja | 20,0 | 0,087 | 130 | 26,00 |
| 3 | Paroizolacja bitumiczna | paroizolacja | 0,2 | 0,009 | 50 000 | 100,00 |
| 4 | Płyty PIR (izolacja spadkowa) | izolacja | 22,0 | 10,000 | 60 | 13,20 |
| 5 | Membrana EPDM 1,5 mm | hydroizolacja | 0,1 | 0,006 | 75 000 | 112,50 |

| Mies. | θ_e | g_c pł.4 [g/m²] | M_a pł.4 [g/m²] |
|:---|:---|:---|:---|
| X | 7,0 | 1,2 | 1,2 |
| XI | 2,2 | 2,4 | 3,5 |
| XII | −0,1 | 3,0 | 6,6 |
| I | 0,2 | 2,6 | 9,2 |
| II | −1,8 | 2,5 | 11,7 |
| III | 2,7 | 1,6 | 13,3 |
| IV | 8,3 | −0,9 | 12,3 |
| V | 13,0 | −3,7 | 8,6 |
| VI | 16,8 | −4,3 | 4,3 |
| VII | 18,2 | −4,8 | 0,0 |
| VIII | 18,4 | 0,0 | 0,0 |
| IX | 13,5 | 0,0 | 0,0 |

Płaszczyzny kondensacji (numer granicy za warstwą): 4 — między „PIR” a „EPDM”

**Ocena:** kondensacja okresowa, M_a,max = 13 g/m² — wysycha w okresie letnim (dopuszczalna wg WT zał. 2 pkt 2.2.5). Warunki wewnętrzne: klasa wilgotności 3 (PN-EN ISO 13788 zał. A: budynki o nieznanym zagęszczeniu), p_i = p_e + 1,10·Δp.

Wymagane s_d paroizolacji (po ciepłej stronie izolacji): brak kondensacji — > 1500 (nieosiągalne) m; kondensacja dopuszczalna (wysycha, M_a ≤ 500 g/m²) — 44,1 m; istniejąca warstwa: PAROIZ, s_d = 100,0 m (✔ spełnia).

![Glaser SD-D1](glaser_SD-D1.png)

**Założenia i dane wejściowe:**

* Glaser: warunki wewnętrzne — klasa wilgotności 3 (budynki o nieznanym zagęszczeniu), θ_i = 20 °C, p_i = p_e + 1,10·Δp [ZAŁ] — źródło: PN-EN ISO 13788:2013 zał. A (zachowawczo: nieznane zagęszczenie)
* Kryterium akumulacji kondensatu 0,5 kg/m² (DIN 4108-3 — kryterium literaturowe) [ZAŁ]
* Dane klimatyczne: typowy rok meteorologiczny ISO (PN-EN ISO 15927-4:2007), stacja Poznań (Ławica) (WMO 12330), okres 1971–2000; Ministerstwo Inwestycji i Rozwoju (archiwum) — „Dane do obliczeń energetycznych budynków”, pliki wmo123300iso.zip (godzinowy) i wmo123300iso_stat.txt (statystyki miesięczne); https://www.gov.pl/web/archiwum-inwestycje-rozwoj/dane-do-obliczen-energetycznych-budynkow (pobrano 2026-09-25)

---
*Wygenerowano: 2026-09-25 — biblioteka `lamela.obliczenia` (PRZYKŁAD – NIE DO ZŁOŻENIA; dane wyrobów: [DANE PRZYKŁADOWE – FIKCYJNE]).*
