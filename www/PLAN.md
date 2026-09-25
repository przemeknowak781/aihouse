# Strona katalogowa „Dom LAMELA” — plan projektu (www/dist)

Marka FIKCYJNA: **PASMO I CIEŃ · katalog domów autorskich** (marka przykładowa; wyszukiwanie „Pasmo i Cień” pracownia —
brak trafień w dniu budowy; odrzucono „Kreślarnia …”, bo istnieją biura o tej nazwie).

Strona sprzedaje projekt jako „projekt gotowy” z katalogu. Wszystkie liczby i rysunki pochodzą z modelu
(`model/budynek.yaml`, `model/dzialka.yaml`, `model/wyposazenie.yaml`) przez `tools/buduj_www.py`; teksty marketingowe,
pakiety i ceny PRZYKŁADOWE — z `www/tresc.yaml` (bez liczb o budynku, tylko wstawki `{klucz}` z danych modelu).

## Paleta (tokeny CSS, motyw jasny → ciemny)

| rola | jasny | ciemny | skąd |
|---|---|---|---|
| grunt strony (beton architektoniczny) | `#E6E7E2` | `#151A1C` | chłodny szary betonu, lekko zielonkawy |
| arkusz (powierzchnie, rysunki) | `#F4F4F0` | `#1E2427` | kalka / arkusz rysunkowy |
| grafit (tekst) | `#1F2427` | `#E7E6E0` | ołówek / tusz |
| antracyt RAL 7016 (pasma, stopka) | `#383E42` | `#2A3135` | kolor ram i okładzin z modelu (`RAMA_C`, `PODSUF`) |
| termojesion (akcent) | `#9B6B41` (tekst `#7A5130`) | `#C8925E` | kolor lamel `DREWNO_TERMO` z modelu |
| sedum (drugi akcent: energia, woda) | `#5E7A2F` | `#9DBB63` | kolor `SUBSTRAT` dachu zielonego |

Kolory „4 linii” (izolacja, hydroizolacja, szczelność, warstwa zewnętrzna) i materiałów na elewacjach — z pól `kolor`
materiałów modelu (dane, nie dekoracja).

## Kroje (Google Fonts, z fallbackiem)

* **Archivo** w szerokości 125 (expanded), 700–800 — nagłówki; rozciągnięte, poziome litery = poziome pasma bryły.
* **IBM Plex Sans** — tekst; **IBM Plex Mono** — dane, podstawy prawne, etykiety rysunków (konwencja metryki arkusza),
  `tabular-nums` w tabelach.
* **Caveat** — wyłącznie adnotacje „szkicu Inwestora” (litery A–G na renderze i przy szkicu z serwetki).

## Układ

Redakcyjna strona-arkusz: wyrównanie do lewej, siatka 12 kolumn z wąską kolumną „metryki” (etykieta sekcji + podstawa),
szeroką kolumną treści. Hero: render od ogrodu na pełną szerokość (16:9 desktop, 4:3 telefon), nad nim odręczne litery
A–G wskazujące pasma bryły (pozycje rzutowane z modelu przez kamerę renderu), pod nim nazwa w rozciągniętym kroju
i pasek parametrów jak tabliczka rysunkowa. Separatory sekcji = trzy przesunięte kreski, których długości i przesunięcia
są liczone z obrysów kondygnacji P0/P1/P2 (sylweta „S”). Rysunki (rzuty, elewacje, przekrój, przegrody, schemat
działki) jako inline SVG na tokenach — działają w obu motywach. Jedno „ryzyko”: odręczna warstwa szkicu nałożona
na fotorealistyczny render. Ruch minimalny (przejścia zakładek, hover), wyłączany przy `prefers-reduced-motion`.

## Kontrola „nie-szablonowości”

Odrzucono: kremowe tło + serif + terakota (grunt jest chłodnym betonem, akcent to realny kolor drewna z modelu);
Inter/Space Grotesk (→ Archivo expanded + Plex); centrowanie (wszystko do lewej, asymetria metryka/treść);
numeracja 01/02/03 (sekcje nie są sekwencją — etykiety opisowe).
