# Lista zadań do ponownego przeliczenia po rewizji v1.1 (zbierana na bieżąco)

## Agent rzutów (tools/model_pomieszczen.py, tools/rzuty.py)
- [ ] Numeracja: 9 numerów kończy się `.OCZ` zamiast numeru kolejnego (R-217: kod grupy + numer kolejny) – źródło: build/tabele/kontrola.md.
- [ ] Brak pomieszczeń dla pozycji programu: SW.03, SWD.05, SWD.06, PR.02, PPM.02 (SWD.* – w zakresie S-2) – kontrola.md.
- [ ] Antresola: pomieszczenia trzonów KW.A.* (97 m²) liczone podwójnie (S i ANT); pow. netto ANT 167 m² > pow. brutto 69,7 m² – poprawić bilans.
- [ ] Rzut antresoli (tight): pustka wypełniona na czarno – pokazać jako pustkę (biel + przekreślenie / szraf), nie poché.
- [ ] Ścieżki ogrodu na PZT i rzucie parteru pokrywają 101 m² zachowanych ogródków – po decyzji v1.1 przerysować trasy.
- [ ] KS rozdzielone między kond. 4 i 6, DRA na trzech kondygnacjach – sprawdzić z rozkładem v1.1.
- [ ] Wariant ciasny: limity wieży 216 × 166 mm (S-2 może przekroczyć) – kontrola rozmiary_tight.json.

## Agent 3D
- [ ] Usunąć `ZALOZENIA` (brama 4,0 m itd.) po v1.1 – brać z JSON.
- [ ] Dziób skrzydła wg v1.1 (tabela 4.1 vs JSON).
- [ ] Lamele korony – nowy rytm wg v1.1 (I-7, mora).

## Główna sesja (rysunki)
- [ ] elewacje, przekroje, PZT, aksonometria, schematy, nasłonecznienie, rzuty bloków – przegenerować na v1.1; PZT: drzewa wg M.06 (bilans v1.1), rampa/brama, ścieżki.
- [ ] tabele: `tools/tabele_konkursowe.py` (F.14.B z kosztów v1.1; usunąć znacznik „wersja robocza”).
- [ ] F.14.B: VAT 8 % w poz. 7.8 i 15.7 – zweryfikować (budynek biurowy → 23 %); podział instalacji elektrycznych/teletechnicznych [Z] – opisać założenie.
- [ ] Agent rzutów: okrągła ława na placu przeniesiona do (105,54; 75,73) – R 16,5 m (poza podcieniem); przeliczyć parter z otoczeniem.

## Po workflow „rysunki-v11” (wf_48dafa92-e77, 17.11 ok. 06:00) – do wykonania razem z v1.2
### Rysunki (główna sesja)
- [x] Elewacja segmentu od dziedzińca „Sg” (nowa, rzut ⟂ do lica S-W) – build/rysunki/elewacja_Sg_1-{200,500}.svg.
- [x] Przekroje: ZWG i strop glin QpB opisane; ściany szczelinowe z linią urwania.
- [x] Przekrój elewacyjny skrzydła 1:50 (UMWD_FRAG=skrzydlo) – przekroj_elewacyjny_skrzydlo_1-50.svg.
- [x] schematy_idei: aksonometrie były lustrzane (rgt po lewej) – naprawione right_of(f).
- [ ] **Plansze P7/P8**: wstawić Sg (263,5 × 288 mm) i skrzydło 1:50 (490 × 206 mm) – P7 bez miejsca; propozycja: skrzydło 1:50 na P8 obok korony (kosztem W4 lub zmniejszenia eco), Sg na P7 (przeorganizować rzędy). Przekroje 1:200 mają teraz 311 mm (A-A + B-B = 628/630 mm na P6).
- [ ] przekroje.section: przyciąć płyty/ściany BM −1/−2 do UG_K z koncepcja.json (pas dziedzińca 5,0 m, nie 7,0 m) – teraz tylko doraźnie w schemat_eko.py; dorysować strop nad −1 w pasie dziedzińca (wierzch −0,15).
- [ ] przekroje.py: `hash(t['nr']) % 5` → `zlib.crc32` (hash str losowy między przebiegami → korony drzew różne w różnych skalach).
- [ ] Przekroje 1:500: podpisy pomieszczeń nachodzą na siebie.
- [ ] PZT: 2 drzewa „w pasie 4,6 m od bulwaru” stoją poza pasem (0,98 i 8,1 m) – **decyzja: posadzić w pasie** (pas 87,3 m², skrzynki rozsączające 60,2 m² + 2 × ~9 m² strefy korzeniowej w systemie komór/strukturalnego gruntu = 78 m² ≤ 87,3 m²).
- [ ] PZT: linie dróg pożarowych na dalszym pasie jezdni (spec rozdz. 9: Mazowiecka 8,9–9,7 m, Wybrzeże 7,9–9,1 m od elewacji) – liczyć jako offset krawężników z site.json.
- [ ] PZT: dorysować 20 stojaków rowerowych na skwerze, 10 przy bramie ogrodowej (4 cargo) i obrys tarasu bistro (zach. część skweru).
- [ ] Nasłonecznienie: podpisy konturów 9/12/15 poza viewBox lub pod legendą; tabela – przecinek dziesiętny.
- [ ] Schemat dostępności: trasa dotykowa od wejścia ogrodowego (5) przecina narożnik WC – poprowadzić po krawędzi.
- [ ] schemat_eko: zbiornik 50 m³ narysować konturem przerywanym z podpisem „(−2, przy łuku – poza przekrojem)”.
### Specyfikacja (scalenie v1.2 / autor spec)
- [ ] Tynk od dziedzińca: opis materiałów = ETICS (tynk na wełnie, A2-s1,d0), tabela przegród 1:50 = „tynk 10 / pustka 40 / …” (niewykonalne bez płyty) → ujednolicić na ETICS: tynk 10 / wełna 240 λ 0,031 / żelbet 150 = 0,40 m, U ≈ 0,13.
- [ ] Fryz wklęsły 0,15 × 0,15 m – potwierdzić; dopisać do JSON: pochwyt 1,10, kaseta ZIP 0,18, ΔU 0,020, strop glin QpB 101,8–103,4, spadek dachu skrzydła 2,8 % (kalenica w osi traktu 15,00).
### Agent rzutów
- [ ] budynek.json: 3 okna na licu S-W segmentu (kond. P, 1, 3, 4) – sprzeczne z elewacją (żaluzje agregatu/trafo/dry-coolera, pełny parter); uzgodnić rzuty z elewacją Sg.
