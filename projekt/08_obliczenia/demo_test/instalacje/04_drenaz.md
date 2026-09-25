# Drenaż opaskowy i odwodnienie powierzchniowe — decyzja projektowa

Obiekt: Dom testowy pipeline'u 3D. Wymaganie Inwestora 25.09.2026 (brief §9 pkt 6). Dane gruntowe przykładowe [ZAŁ].

## 1. Dane i kryteria

* Grunt: piaski średnie, k_f = 3,00·10⁻⁴ m/s (wartość typowa [W]; wymagane badania — E-04)
* Zwierciadło wody gruntowej 3,80 m p.p.t.; spód fundamentu −1,10 m (wzgl. ±0,00), teren przy budynku średnio −0,29 m → głębokość posadowienia 0,81 m; ZWG 2,99 m poniżej spodu fundamentu.
* Pomieszczenia poniżej terenu: brak (budynek niepodpiwniczony, posadzka parteru nad terenem)
* Grunt silnie przepuszczalny (k_f > 10⁻⁴ m/s) i ZWG ≥ 0,5 m pod fundamentem — woda opadowa infiltruje pionowo, nie powstaje woda zastoiskowa przy ścianach; wystarcza izolacja przeciwwilgociowa.

| Kryterium (DIN 18533-1 / DIN 4095 — wiedza techniczna) | Stan | Wniosek |
|:---|:---|:---|
| Przepuszczalność gruntu k_f > 10⁻⁴ m/s | 3,00·10⁻⁴ m/s | silnie przepuszczalny |
| ZWG ≥ 0,5 m pod spodem fundamentu | 2,99 m | spełnione |
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
| 1 | 10,6 | −0,320 | −0,327 | 0,004 |
| 2 | 8,6 | −0,268 | −0,250 | −0,009 |
| 3 | 10,6 | −0,255 | −0,236 | −0,010 |
| 4 | 8,6 | −0,306 | −0,309 | 0,002 |

## 4. Sprawdzenia

| ID | Warunek | Wartość | Wymaganie | Wynik | Podstawa / uwagi |
|:---|:---|---:|---:|:---|:---|
| W-019 | Spadek terenu od budynku (minimum na odcinku), ściana 1 (x 8,1; y −0,3) | 0,004 | ≥ 0,020 | **NIESPEŁNIONY** | W-019; brief §9 pkt 6 (teren z punktów działki (IDW); co 0,10 m) |
| W-019 | Spadek terenu od budynku (minimum na odcinku), ściana 2 (x 10,3; y 4,4) | −0,009 | ≥ 0,020 | **NIESPEŁNIONY** | W-019; brief §9 pkt 6 (teren z punktów działki (IDW); co 0,10 m) |
| W-019 | Spadek terenu od budynku (minimum na odcinku), ściana 3 (x 4,9; y 8,3) | −0,010 | ≥ 0,020 | **NIESPEŁNIONY** | W-019; brief §9 pkt 6 (teren z punktów działki (IDW); co 0,10 m) |
| W-019 | Spadek terenu od budynku (minimum na odcinku), ściana 4 (x −0,3; y 5,0) | 0,002 | ≥ 0,020 | **NIESPEŁNIONY** | W-019; brief §9 pkt 6 (teren z punktów działki (IDW); co 0,10 m) |
| W-019 | Wysokość cokołu (posadzka parteru − teren TIN, co 0,10 m), minimum na obwodzie | 0,20 m | ≥ 0,30 m | **NIESPEŁNIONY** | brief §9 pkt 4 (≥ 0,30 m lub odwodnienie liniowe przy drzwiach bezprogowych) |

## Podsumowanie sprawdzeń

Warunków: 5; spełnionych: 0; niespełnionych: 5; informacyjnych: 0.

Niespełnione:

* W-019 — Spadek terenu od budynku (minimum na odcinku), ściana 1 (x 8,1; y −0,3): 0,004  (wymaganie >= 0,020 )
* W-019 — Spadek terenu od budynku (minimum na odcinku), ściana 2 (x 10,3; y 4,4): −0,009  (wymaganie >= 0,020 )
* W-019 — Spadek terenu od budynku (minimum na odcinku), ściana 3 (x 4,9; y 8,3): −0,010  (wymaganie >= 0,020 )
* W-019 — Spadek terenu od budynku (minimum na odcinku), ściana 4 (x −0,3; y 5,0): 0,002  (wymaganie >= 0,020 )
* W-019 — Wysokość cokołu (posadzka parteru − teren TIN, co 0,10 m), minimum na obwodzie: 0,20 m (wymaganie >= 0,30 m)

## Źródła

1. PN-EN 1997-1:2008 + NA (EC7) — sytuacje obliczeniowe z wodą gruntową [NZW numeracja]
2. DIN 18533-1:2017-07 Abdichtung von erdberührten Bauteilen — klasy W1.1-E, W1.2-E, W2.1-E [W]
3. DIN 4095:1990-06 Dränung zum Schutz baulicher Anlagen [W]
4. Wiłun Z., Zarys geotechniki, WKŁ — współczynniki filtracji gruntów [W]; Aquanet 2024 tab. 1
5. WT §28, §316; rejestr wymagań W-019, W-144, W-280, W-285; brief §9 pkt 4 i 6
