# Drenaż opaskowy i odwodnienie powierzchniowe — decyzja projektowa

Obiekt: Dom LAMELA. Wymaganie Inwestora 25.09.2026 (brief §9 pkt 6). Dane gruntowe przykładowe [ZAŁ].

## 1. Dane i kryteria

* Grunt: piaski średnie, k_f = 3,00·10⁻⁴ m/s (wartość typowa [W]; wymagane badania — E-04)
* Zwierciadło wody gruntowej 3,80 m p.p.t.; spód fundamentu −0,85 m (wzgl. ±0,00), teren przy budynku średnio −0,29 m → głębokość posadowienia 0,56 m; ZWG 3,24 m poniżej spodu fundamentu.
* Pomieszczenia poniżej terenu: brak (budynek niepodpiwniczony, posadzka parteru nad terenem)
* Grunt silnie przepuszczalny (k_f > 10⁻⁴ m/s) i ZWG ≥ 0,5 m pod fundamentem — woda opadowa infiltruje pionowo, nie powstaje woda zastoiskowa przy ścianach; wystarcza izolacja przeciwwilgociowa.

| Kryterium (DIN 18533-1 / DIN 4095 — wiedza techniczna) | Stan | Wniosek |
|:---|:---|:---|
| Przepuszczalność gruntu k_f > 10⁻⁴ m/s | 3,00·10⁻⁴ m/s | silnie przepuszczalny |
| ZWG ≥ 0,5 m pod spodem fundamentu | 3,24 m | spełnione |
| Zasypka wykopów z gruntu przepuszczalnego | tak | — |
| Klasa oddziaływania wody | W1.1-E (wilgoć gruntowa, woda nienaporowa) |  |

## 2. Decyzja

**Drenaż opaskowy: NIEWYMAGANY.**

## 3. Odwodnienie powierzchniowe i zalecenia

* Odwodnienie powierzchniowe: profilowanie terenu ze spadkiem ≥ 2 % od budynku na pasie ≥ 2,0 m (rzędne projektowane w dzialka.yaml: teren.punkty_projektowane) — wymagane niezależnie od drenażu.
* Opaska żwirowa szer. 0,5 m wokół budynku (żwir płukany 16/32 mm na geowłókninie, obrzeże), spadek od ściany; chroni cokół przed rozbryzgiem i ułatwia kontrolę izolacji [W].
* Izolacja przeciwwilgociowa ścian fundamentowych/cokołu i płyty (klasa W1.1-E), wywinięta ≥ 0,30 m ponad teren (brief §9 pkt 4); przy drzwiach bezprogowych odwodnienie liniowe (moduł deszczowa).
* Rury spustowe i odwodnienia liniowe nie mogą zrzucać wody przy fundamentach — odprowadzenie do zbiornika / niecki (≥ 3,0 m od fundamentów, W-144).
* Decyzję zweryfikować po badaniach podłoża (kategoria geotechniczna II — W-280): k_f in situ w strefie zasypki, obserwacje wody zawieszonej po roztopach.

| Ściana | L [m] | Teren przy ścianie [m] | Teren 2 m dalej [m] | Spadek |
|---:|---:|---:|---:|---:|
| 1 | 12,3 | −0,339 | −0,399 | 0,030 |
| 2 | 6,7 | −0,338 | −0,394 | 0,028 |
| 3 | 10,0 | −0,308 | −0,387 | 0,040 |
| 4 | 7,0 | −0,125 | −0,180 | 0,027 |
| 6 | 12,0 | −0,339 | −0,396 | 0,028 |
| 7 | 9,4 | −0,339 | −0,399 | 0,030 |

## 4. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-019 | Spadek terenu od budynku, ściana 1 (śr. 5,8; −0,3) | 0,030 | ≥ 0,020 | SPEŁNIONY | W-019; brief §9 pkt 6 (rzędne projektowane (dzialka.yaml)) |
| W-019 | Spadek terenu od budynku, ściana 2 (śr. 15,3; −0,3) | 0,028 | ≥ 0,020 | SPEŁNIONY | W-019; brief §9 pkt 6 (rzędne projektowane (dzialka.yaml)) |
| W-019 | Spadek terenu od budynku, ściana 3 (śr. 18,7; 4,7) | 0,040 | ≥ 0,020 | SPEŁNIONY | W-019; brief §9 pkt 6 (rzędne projektowane (dzialka.yaml)) |
| W-019 | Spadek terenu od budynku, ściana 4 (śr. 15,2; 9,7) | 0,027 | ≥ 0,020 | SPEŁNIONY | W-019; brief §9 pkt 6 (rzędne projektowane (dzialka.yaml)) |
| W-019 | Spadek terenu od budynku, ściana 6 (śr. 5,7; 9,1) | 0,028 | ≥ 0,020 | SPEŁNIONY | W-019; brief §9 pkt 6 (rzędne projektowane (dzialka.yaml)) |
| W-019 | Spadek terenu od budynku, ściana 7 (śr. −0,3; 4,4) | 0,030 | ≥ 0,020 | SPEŁNIONY | W-019; brief §9 pkt 6 (rzędne projektowane (dzialka.yaml)) |
| W-019 | Wysokość cokołu (posadzka parteru − teren), minimum na obwodzie poza strefami drzwi z odwodnieniem liniowym | 0,31 m | ≥ 0,30 m | SPEŁNIONY | brief §9 pkt 4 (≥ 0,30 m lub odwodnienie liniowe przy drzwiach bezprogowych) |
| W-019 | Strefa drzwi O0-01 (FX1; OL-2, OL-2W) — próg z odwodnieniem liniowym; cokół w strefie | 0,33 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-02 (FX1; OL-2) — próg z odwodnieniem liniowym; cokół w strefie | 0,33 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-03 (HS1; OL-2) — próg z odwodnieniem liniowym; cokół w strefie | 0,33 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-04 (HS1; OL-2) — próg z odwodnieniem liniowym; cokół w strefie | 0,33 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-05 (FX2; OL-2, OL-6) — próg z odwodnieniem liniowym; cokół w strefie | 0,33 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-06 (DZ3; OL-2, OL-6) — próg z odwodnieniem liniowym; cokół w strefie | 0,15 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-07 (BR1; OL-1, OL-3) — próg z odwodnieniem liniowym; cokół w strefie | 0,12 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-08 (DZ2; OL-5) — próg z odwodnieniem liniowym; cokół w strefie | 0,16 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-09 (DZ1; OL-3) — próg z odwodnieniem liniowym; cokół w strefie | 0,09 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-10 (FX3; OL-3) — próg z odwodnieniem liniowym; cokół w strefie | 0,05 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |
| W-019 | Strefa drzwi O0-11 (HS2; OL-2, OL-2W) — próg z odwodnieniem liniowym; cokół w strefie | 0,33 m | — | informacyjnie | brief §9 pkt 4; DIN 18533-1 (pomocniczo) — uszczelnienie progu wywinięte ≥ 0,15 m |

## Podsumowanie sprawdzeń

Warunków: 18; spełnionych: 7; niespełnionych: 0; informacyjnych: 11.

## Źródła

1. PN-EN 1997-1:2008 + NA (EC7) — sytuacje obliczeniowe z wodą gruntową [NZW numeracja]
2. DIN 18533-1:2017-07 Abdichtung von erdberührten Bauteilen — klasy W1.1-E, W1.2-E, W2.1-E [W]
3. DIN 4095:1990-06 Dränung zum Schutz baulicher Anlagen [W]
4. Wiłun Z., Zarys geotechniki, WKŁ — współczynniki filtracji gruntów [W]; Aquanet 2024 tab. 1
5. WT §28, §316; rejestr wymagań W-019, W-144, W-280, W-285; brief §9 pkt 4 i 6
