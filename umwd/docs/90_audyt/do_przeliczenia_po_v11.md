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
