# Koncepcja — WARIANT W3: „ŚWIATŁO · OGRÓD · SEKWENCJA WEJŚCIA”

Dom LAMELA, dz. nr 123/4 (32,00 × 50,00 m), MPZP 3MN. Wersja robocza 2026-09-25. Interpretacja szkicu **v2** (decyzje Inwestora z 25.09.2026, brief §1.2).
Wszystkie liczby w tym opisie, na rzutach i w tabelach pochodzą z modelu `src/model_w3.py` (geometria: `src/base_w3.py`, `src/geo_p0.py`,
`src/geo_p1.py`, `src/geo_p2.py`, `src/geo_ext.py`). Tabele z §3–§4 i §8 wygenerowano skryptem `src/calc_w3.py`. Rysunki odtwarza się poleceniem
`cd src && python3 draw_plans.py .. && python3 draw_elev.py .. && python3 draw_sections.py .. && python3 draw_site.py ..`.

| Rysunek | Plik |
|---|---|
| Rzut parteru P0 | `rzut_P0.png` |
| Rzut I piętra P1 | `rzut_P1.png` |
| Rzut II piętra P2 | `rzut_P2.png` |
| Elewacja południowa + porównanie ze szkicem | `elewacja_S.png` |
| Przekroje A-A (oś widoku) i B-B (klatka schodowa) | `przekroj.png` |
| Zagospodarowanie działki | `zagospodarowanie.png` |

**Parametry wariantu (z modelu):** PU **262,61 m²** (P0 122,18 + P1 81,35 + P2 59,08; bez garażu 38,21 m²), powierzchnia zabudowy
**200,18 m²** (12,5 %), wysokość budynku wg MPZP **10,10 m**, 3 kondygnacje nadziemne, bez piwnicy, dachy płaskie.

---

## 1. Idea wariantu W3

Priorytet: **światło, ogród i sekwencja wejścia**. Dom jest ułożony wzdłuż jednej, prostej **osi widoku x = 8,00 m** poprowadzonej z północy na
południe przez całą działkę:

> furtka w ogrodzeniu → dojście z płyt (1,20 m) → daszek nad wejściem → drzwi wejściowe (1,10 × 2,40) → **wiatrołap** doświetlony
> świetlikiem SW2 w zielonym dachu skrzydła → **szklana przegroda** z drzwiami szklanymi → **hol** (3,10 × 3,37 m, obok schody za ekranem
> z drewnianych lamel) → wylot 2,60 m w ścianie grzbietowej → **jadalnia pod dwukondygnacyjną pustką** (h = 5,70–5,95 m, doświetlona przez
> boks C) → **drzwi HS w kwaterze 4** fasady → taras → **oś ogrodowa** z płyt w trawie → soliter (drzewo) na końcu osi (y ≈ −24,5 m).

Z progu drzwi wejściowych widać przez cały dom ogród i zamknięcie osi — sekwencja „ściśnięcie → rozprężenie”: niski (2,80 m), jasny od góry
wiatrołap i hol, a potem wysoka, rozświetlona jadalnia i ogród.

Pozostałe cechy wariantu:
* **Światło z trzech stron w strefie dziennej**: salon — przeszklenie S (kwatery 1–2) i przeszklenie zachodnie z HS na taras zachodni pod
  okapem 1,50 m (wieczorne słońce); jadalnia — S + światło z góry przez pustkę i boks C; kuchnia — S (kwatera 5) + drzwi przeszklone na
  **patio poranne** od wschodu (słońce przy śniadaniu).
* **Garaż cofnięty o 4,80 m** względem lica ogrodowego — między kuchnią a garażem powstaje osłonięte od północy **patio poranne** (5,10 × 4,80 m),
  a linia D (dolna płyta ramy C → attyka garażu) nadal czytelnie przebiega w elewacji do narożnika garażu 19,00 m od lica zach. bryły B.
* **Latarnia świetlna nad klatką schodową** (SW1, 1,85 × 2,90 m, w poziomie attyki) — światło zenitalne spada przez rdzeń 3 kondygnacji;
  klatka jest otwarta na hol parteru przez ekran z lamel, na galerię P1 i hol P2.
* **Loggia P2 za lamelami** — pokoje II piętra cofnięte do osi 1' (y = 1,20); ekran pionowych lamel w licu bryły A (jak w szkicu) jest
  jednocześnie osłoną przeciwsłoneczną i balustradą loggii 13,0 × 1,20 m (taras rodziców z widokiem na ogród, dostęp z gabinetu, holu i sypialni).
* **Galeria P1 nad pustką** — pokój rodzinny/biblioteka w boksie C jest otwarty na galerię i pustkę; dzieci i rodzina mają wizualny kontakt z
  jadalnią i ogrodem.
* Pomieszczenia pomocnicze i komunikacja od północy (skrzydło wejściowe z zielonym dachem, pom. techniczne, przedsionek gospodarczy,
  pralnia, łazienki), sypialnie od W (dzieci), S+E (rodzice) i W+S (gabinet/pokój).

## 2. Odczyt szkicu w W3 (porównanie ilościowe)

Skala szkicu wg briefu §1.1: bryła B (500…1050 px) = 12,0 m ⇒ 45,8 px/m; odniesienie = lico zach. bryły B (x = −0,30).

| Element szkicu | szkic (od lica zach. B) | W3 (od lica zach. B) | W3 — współrzędne x [m] | uwagi |
|---|---|---|---|---|
| A — bryła II piętra w lamelach | −1,0 … +12,2 (13,2 m) | −1,0 … +12,6 (13,6 m) | −1,30 … 12,30 | wspornik 1,00 m na zachód |
| A — płyta pod/nad bryłą | −2,4 … +12,6 | −1,9 … +12,9 | −2,20 … 12,60 | wysunięcie 0,90 m (S i W) |
| B — bryła I piętra | 0 … +12,0 | 0 … +12,6 | −0,30 … 12,30 | pełna, lewa część bez okien od S |
| C — boks przeszklony, 3 kwatery | +4,5 … +11,7 (7,2 m) | +4,8 … +12,0 (7,2 m) | 4,50 … 11,70 | kwatery 3 × 2,40 m |
| C — rama | +3,9 … +13,8 | +3,9 … +13,2 | 3,60 … 12,90 | wysunięcie 1,00 m |
| D — linia pozioma do narożnika | +3,8 … +19,0 | +3,9 … +19,0 | 3,60 … 18,70 | dolna płyta ramy C (+3,65) = attyka garażu (+3,65) |
| D — pion (narożnik garażu) | +19,0 | +19,0 | 18,70 | ściana wsch. garażu |
| E — przeszklenie parteru, 5 kwater | +1,0 … +13,2 | +1,3 … +12,15 | 1,00 … 11,85 | szer. kwater 1,60/1,90/2,40/2,40/2,55 — narastające ku wschodowi jak w szkicu |
| E — płyta dachu parteru | −1,5 … +14,1 | −1,5 … +14,1 | −1,80 … 13,80 | okap 1,50 m W, 1,00 m S, nad patio 1,50 m |
| G — garaż | +13,2 … +19,0 | +12,6 … +19,0 | 12,30 … 18,70 | 2 stanowiska, cofnięty w głąb o 4,80 m |

Sylweta „S” (zachód–wschód–zachód) jest zachowana wyłącznie przesunięciami brył: A wysunięta na zachód (wspornik), B z boksem C
przesunięta na wschód (rama C wychodzi 0,60 m poza lico wsch. B), E przesunięta na zachód (okap 1,50 m), a garaż G zamyka linię D na wschodzie
(`elewacja_S.png` — górny panel: obrys W3 na szkicu). Odstępstwo świadome: garaż w W3 jest cofnięty w głąb działki (w elewacji to samo
położenie w osi x, inna głębokość planu) — w widoku od ogrodu czyta się jako tło dla patio; wysokości pasm wg WT, nie wg umownych proporcji szkicu.
