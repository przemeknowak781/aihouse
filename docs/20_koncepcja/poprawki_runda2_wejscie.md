# Poprawki modelu — runda 2 (wejście, zbierane przez koordynatora 25.09.2026)

Runda 1 = poprawki po audytach A1–A3 (przepływ koncepcji, faza „Poprawki”). Runda 2 obejmuje ustalenia, które do rundy 1
NIE trafiły (runda 1 dostała wyłącznie listę uwag A1–A3). Źródła do przeczytania w całości:

1. `docs/20_koncepcja/weryfikacja_koncepcji.md` §6 (kategorie A — niezgodności, B — decyzje, C — rysunki/narzędzia).
2. `projekt/08_obliczenia/mostki/REKOMENDACJE.md` (katalog mostków rzeczywistego budynku, ISO 10211; woda: R-W1…).
3. `docs/10_podstawy_prawne/weryfikacja_upzp_art2_definicje.md` (definicje wskaźników — jedno źródło: `src/lamela/wskazniki.py`).

Ustalenia koordynatora z przeglądu rysunków (do weryfikacji i wprowadzenia):

| # | Miejsce | Problem | Kierunek poprawki | Podstawa |
|---|---|---|---|---|
| K-1 | teren przy budynku (PZT-02: teren na obwodzie 101,32–101,48 m, posadzka 101,65) | cokół tylko 0,17–0,33 m nad terenem; weryfikacja: 0,14 m przy DZ2 | teren/opaska ≤ −0,30 m wzdłuż ścian (z wyjątkiem drzwi bezprogowych z odwodnieniem liniowym i progów zgodnych z detalem D-03); spadek terenu ≥ 2 % od budynku na ≥ 1,5–2,0 m (W-019) | brief §9; DIN 18533-1 (pomocniczo), W-019 |
| K-2 | niecka chłonna NCH-1 w zasięgu korony drzewa DR1 (lipa, projektowane) | korzenie a infiltracja, zacienienie; opis „2,00 m od drzewa” mierzony od pnia | przesunąć drzewo DR1 poza nieckę albo nieckę poza rzut korony dojrzałego drzewa; zachować odległości od budynku/granicy | dobra praktyka (wytyczne retencji — [DO WERYFIKACJI źródła]) |
| K-3 | wysokość zabudowy — 4 różne wartości w dokumentach | różne metody | wszystkie dokumenty i narzędzia (audyt_wt.py, podglad_modelu.py, koncepcja.md, PZT) biorą wartości z `lamela.wskazniki` | upzp art. 2 pkt 30 (Dz.U. 2026 poz. 538) |
| K-4 | EP = 57,2 z PV, bez PV 81,8 (limit 70) | spełnienie zależy wyłącznie od PV i domyślnych ψ | po rundzie mostków (ψ z katalogu, H_TB) przeliczyć EP; rozważyć poprawę obudowy/odzysku, tak aby zapas był realny; PV jako element obowiązkowy w opisie | WT zał. 2 pkt 1.1; rozp. metodologia |
| K-5 | płyta fundamentowa — kontrola A_s niespełniona w paśmie przykrawędziowym (model bez żeber) | analiza niepełna | MES płyty z żebrami na podłożu sprężystym (zlecone agentowi BO) — wynik może zmienić grubość płyty/żeber w modelu | PN-EN 1992-1-1, PN-EN 1997-1 |
