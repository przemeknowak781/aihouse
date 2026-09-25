# Weryfikacja prawna tomu I — `PZT_PAB_ZL_2026.09.25.pdf`

*Weryfikator niezależny (PRAWO), 2026-09-25. Przedmiot: `projekt/wydanie/PZT_PAB_ZL_2026.09.25.pdf` (62 s., wydruk 07:18),
generatory `tools/dokumenty/tom_I_*.py`, `pab_*.py`, `pzt_*.py`, `zl_zalaczniki.py`, `zloz_tom_I.py`. Bez poprawek w plikach.*

## 1. Metoda

- Pełny tekst PDF wyodrębniono (PyMuPDF); strony 1, 7, 19, 29, 36, 44, 57, 59 obejrzano jako obrazy (czytelność, metryki).
- Przepisy porównano z tekstem urzędowym pobranym z API ELI Sejmu (`/eli/acts/DU/<rok>/<poz>/text.pdf`):
  PB t.j. 2026/524; nowela 2026/1161 (art. 102a); RPB t.j. 2022/1679 i zm. 2026/597; WT t.j. 2022/1225 i zm. 2023/2442;
  rozp. BIOZ 2003/1126; rozp. geotechniczne 2012/463; rozp. ppoż. woda i drogi 2009/1030; u.d.p. t.j. 2025/889;
  ustawa o ochronie ludności 2024/1907; rozp. OOŚ 2019/1839; ponadto rejestr `docs/10_podstawy_prawne/` (A.1, W-xxx, D-xx).

## 2. Przepisy sprawdzone — zgodne

| obszar | przepis (cytowany w tomie) | wynik |
|---|---|---|
| oświadczenie projektanta PZT/PAB | PB art. 34 ust. 3d pkt 3, ust. 3da, ust. 3e pkt 1–2 | brzmienie zgodne z ustawą (różnica „i”/„oraz” bez znaczenia) |
| oświadczenie o sieci ciepłowniczej | PB art. 33 ust. 2 pkt 10; art. 14 ust. 1 pkt 4 lit. b; art. 35 ust. 1 pkt 3a lit. b; klauzula karna | klauzula dosłowna; podstawy trafne |
| WT stosowane na podstawie art. 102a | art. 102a ust. 1, 2, 4 (Dz.U. 2026 poz. 1161); „obowiązującymi do dnia 19 września 2026 r.” | zgodne z tekstem ustawy |
| sprawdzający | PB art. 20 ust. 3 pkt 2 | zgodne (dom jednorodzinny) |
| uprawnienia > 1000 m³ | PB art. 15a ust. 3, 5, 21, 23 | zgodne |
| zjazd | u.d.p. art. 19 ust. 2 pkt 4; art. 29 ust. 1, 3, 3a, 5 | zgodne |
| forma i skład | RPB § 2a, § 2b ust. 1–4, § 5 ust. 1, 3, 4, § 6 ust. 1, 3, § 7 ust. 1, 1a, 2, 4a, 5, 7, 8, § 8, zał. 1 (nazwa `PZT_PAB_ZL_z`) | zgodne |
| PZT § 14 pkt 1–8, § 18 | w tym § 14 pkt 6a (2026/597, w mocy od 19.05.2026) | kompletne |
| PAB § 20 ust. 1 pkt 1–14, ust. 2 | pkt 8 w brzmieniu od 05.11.2026 — opisane poprawnie | kompletne |
| BIOZ | rozp. 2003/1126 § 2 ust. 2–3, § 6 pkt 1 lit. a, b, f, k; PB art. 21a ust. 1a pkt 1, ust. 2 | zgodne |
| geotechnika | rozp. 2012/463 § 4 ust. 2 pkt 1, ust. 3 pkt 1 lit. a i pkt 2 lit. a, § 6 ust. 3, § 7 ust. 1–3, § 8–10 | zgodne |
| WT — zagospodarowanie | § 12 ust. 1, 6 (zm. 2023/2442), § 13, § 14 ust. 1, § 18 ust. 2, § 19 ust. 2 pkt 1 lit. a, ust. 7, § 21 ust. 1 pkt 1, § 23 ust. 4, § 28 ust. 2, § 43, § 316 ust. 2 | zgodne |
| WT — budynek | § 8 pkt 1, § 135 ust. 7–9, § 183 ust. 2, § 213 pkt 1 lit. a, § 271 ust. 1 | zgodne (zastrzeżenia — pkt 3.2) |
| ppoż. | rozp. 2009/1030 § 3 ust. 2–3, § 12 ust. 1 | zgodne |
| inne | PB art. 29 ust. 1 pkt 38, ust. 2 pkt 36, ust. 4 pkt 3 lit. c; rozp. 2019/1839 § 3 ust. 1 pkt 55 lit. a; ustawa 2024/1907 art. 93–95 | zgodne |

Dane osobowe: nie wymyślono żadnej osoby, numeru uprawnień, pracowni ani sygnatury — wszystkie pola mają znacznik `[DO UZUPEŁNIENIA]`.
Wyjątek: metryki rysunków (pkt 3.1 ppkt 3). Dane fikcyjne (działka, MPZP, grunt, sieci, wyroby) są oznaczone `[DANE PRZYKŁADOWE – FIKCYJNE]`.
Czytelność PDF: dobra (strony A4, arkusze A1/A2/A3×3 wektorowe, zakładki, znak wodny nie zasłania treści).

## 3. Problemy

### 3.1. Istotne

1. **Opis PZT i opis PAB w tym samym tomie podają różne dane.**
   - Niecka chłonna: 28,0 m² (PZT pkt 3.1, 8.1, tab. 10) wobec 19,5 m² (PAB pkt 9.1).
   - Pompa ciepła: PC-R290-09, L_WA = 58/53 dB(A), na granicy 27,4 dB(A) (PZT tab. 9 i 11) wobec PC-R290-07, L_WA = 55 dB(A), na granicy 26,4 dB(A) (PAB pkt 9.4 i 12.2).
   - Przyczyna: `pab_opis_b.py` bierze `deszczowa.niecka_A_m2` (minimum obliczeniowe) i `pc.L_WA_dB` z innego wyrobu, a `pzt_opis_c.py` bierze `og.pc` i model `dzialka.retencja`.
   - Organ ocenia PZT i PAB łącznie pod kątem ochrony środowiska (PB art. 35 ust. 1 pkt 1 lit. b).
2. **Część rysunkowa PZT nie zgadza się z opisem PZT** (rysunki z 05:36, model z 07:16). Na PZT-01:
   - PBC 1269,84 m² (79,36 %) wobec 1270,15 m² (79,38 %) w opisie;
   - tarasy 67,27 wobec 66,75 m²; opaska 13,13 wobec 13,33 m²;
   - wysokość zabudowy 10,28 m (wywiewka, „ZAŁOŻENIE”) wobec 10,27 m (czerpnia);
   - lico od linii zabudowy 1,63 m wobec „0,95 m”;
   - notatka robocza „Limity: konfiguracja arkuszy (brief § 3) — BRAK W MODELU”.

   Organ sprawdza zgodność PZT z MPZP i przepisami (art. 35 ust. 1 pkt 1–2 PB). Kontrola K-PZT-AKT ma tylko status OSTRZEŻENIE i nie blokuje wydania.
3. **Metryki rysunków są niekompletne i nie zostały sprawdzone.** Na 13 arkuszach pola „imię i nazwisko” i „specjalność, nr uprawnień” są puste, bez znacznika (RPB § 10 ust. 1 pkt 3). Pole „Sprawdzający” jest puste zamiast „nie dotyczy (art. 20 ust. 3 pkt 2 PB)” (W-305, E-11). Lista TOM_I nie ma pozycji dla § 10, więc walidator tych braków nie liczy.
4. **Brak uzgodnienia PZT zjazdu z zarządcą drogi.**
   - PZT pkt 3.4 stwierdza, że PZT w zakresie zjazdu podlega uzgodnieniu z zarządcą drogi (u.d.p. art. 29 ust. 3 pkt 2).
   - ZL nie ma na ten dokument ani miejsca, ani strony zastępczej.
   - PAB pkt 3.3 stwierdza, że „nie ustalono pozwoleń, uzgodnień ani opinii”, co przeczy PZT.
   - Organ sprawdza dołączenie wymaganych uzgodnień (PB art. 35 ust. 1 pkt 3a lit. a).
5. **Raport kompletności zaniża liczbę braków.** Według podsumowania „DO UZUPEŁNIENIA (5)” to wyłącznie dane osobowe. Tymczasem pozycje ze statusem OK mają treść zastępczą:
   - C1-2-19: opinia geotechniczna fikcyjna, bez autora i bez badań;
   - C1-1-18: PZT na „podkładzie przykładowym”, a nie na mapie do celów projektowych (RPB § 15 ust. 1);
   - C1-3-10: decyzja zjazdowa jako strona zastępcza `[DOKUMENT ZEWNĘTRZNY]`;
   - C1-2-15: analiza z § 20 ust. 1 pkt 11 ze znacznikami `[DO UZUPEŁNIENIA]` zamiast wartości K i s.

### 3.2. Drobne

6. **Błędne przytoczenie RPB § 14 pkt 4 lit. a** (PZT pkt 4). W tomie: „tarasy naziemne, gzymsy, balkony i loggie”. W przepisie: „tarasy naziemne i podparte słupami, gzymsy oraz balkony”.
7. **EP_max = 70 kWh/(m²·rok) przypisano do WT § 329 ust. 1.** Tabela tej wartości jest w § 329 ust. 2, lp. 1 lit. a (PAB tab. 12).
8. **PWP opisano jako „zwolnienie; rekomendacja”** (PAB tab. 14). WT § 183 ust. 2 (stosowany na podstawie art. 102a) wymaga PWP w strefie pożarowej powyżej 1000 m³, a tu jest 1354,45 m³.
9. **W tekście urzędowym są odwołania robocze:**
   - „(brief: I — korekta)” i podwójna podstawa „Dz.U. 2012 poz. 463 § 4; … §4 ust. 3” (PAB tab. 1);
   - „brief § 9 pkt 1” (PAB 5.2);
   - „R8 3.5” jako podstawa odległości i spadku (PZT 3.6, tab. 10), choć W-144 jest nienormatywne;
   - „audyt A1”;
   - „ciezka” (PAB 10.4).
10. **Znaczniki `[ZAŁ]`, `[INT]` są objaśnione tylko w PAB.** Znacznik `[NZW]` (ZL, BIOZ pkt 6) nie jest objaśniony nigdzie w tomie.
11. **Niewłaściwe podstawy w nagłówkach i tabelach PAB:**
    - „ZAŁĄCZNIKI (§ 7 ust. 1a RPB)” nad opinią geotechniczną — to część opisu (§ 20 ust. 1 pkt 5). Przez to w łącznym spisie są dwa „Załączniki nr 1”.
    - Karta rysunków PAB powołuje „§ 7 ust. 1 pkt 4, § 10” zamiast § 21.
    - „upzp art. 2 pkt 35 lit. a” — pkt 35 nie ma liter.
    - Tab. 7 powołuje RPB bez zm. 2026/597.
    - Dokładność „0,01” przypisano RPB § 20 ust. 1 pkt 4, który jej nie określa.
12. **„0,95 m przed linią (T2)” jest dwuznaczne** (PZT tab. 8 poz. 8). Można to odczytać jako przekroczenie nieprzekraczalnej linii zabudowy. PAB mówi o „rezerwie 0,95 m”.
13. **ZL zawiera dokumenty spoza zakresu § 5 ust. 1 pkt 4 RPB:** wzór oświadczenia Inwestora z art. 102a (niepodpisany „WZÓR”) oraz oświadczenie z art. 33 ust. 2 pkt 10, które jest załącznikiem wniosku. Dodatkowo „w brzmieniu nadanym ustawą … 2026 poz. 1161” — art. 102a został tą ustawą dodany.
14. **PAB pkt 11:** część ekonomiczną analizy odesłano do PT-3 IS, a pola K i s oznaczono `[DO UZUPEŁNIENIA]`. RPB § 20 ust. 1 pkt 11 wymaga tej analizy w PAB.
15. **Oświadczenia projektanta PZT i PAB** („oświadczam”) nie wskazują, kto je składa. Jest tylko tabela uczestników.

## 4. Zalecenia (dla autora generatorów)

- Pkt 1: jedno źródło danych dla obu opisów (model `dzialka.retencja` oraz jeden wyrób PC). W PAB podawać powierzchnię projektową, a V_min tylko jako warunek.
- Pkt 2 i 3: złożyć tom z `--regeneruj-rysunki`. Ustawić K-PZT-AKT i K-PAB-AKT jako blokujące. Dodać kontrolę K-METRYKA (§ 10 ust. 1): puste pola traktować jako DO UZUPEŁNIENIA, a „Sprawdzający” wypełniać z `bloki`/`dane_obiektu` w warstwie rysunkowej.
- Pkt 4: dodać w ZL stronę zastępczą „Uzgodnienie PZT (zjazd) z zarządcą drogi — u.d.p. art. 29 ust. 3 pkt 2” i poprawić PAB 3.3.
- Pkt 5: w walidatorze nadawać pozycji status DO UZUPEŁNIENIA lub DOKUMENT ZEWNĘTRZNY, gdy jej sekcja zawiera znaczniki. Poprawić podsumowanie raportu.
- Pkt 6–15: poprawki redakcyjne w `pzt_opis_*.py`, `pab_opis_*.py`, `zl_zalaczniki.py` (cytaty, legenda znaczników, usunięcie odwołań roboczych).
