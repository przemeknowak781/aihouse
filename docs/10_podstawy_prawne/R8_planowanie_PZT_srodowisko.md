# R8 — Planowanie przestrzenne, PZT, geodezja, środowisko („Dom LAMELA”)

**Data weryfikacji stanu prawnego: 2026-09-24/25.** Wykaz Dz.U. 2026 sprawdzono w API ELI 25.09.2026: ostatnia pozycja to poz. 1244 z 23.09.2026, a poz. 1245+ zwracają HTTP 404.

**Metoda.** Teksty aktów i ich metadane pobrano z API ELI Sejmu (`api.sejm.gov.pl/eli`). To **źródła pierwotne**: teksty jednolite, akty zmieniające, a przy każdym akcie sprawdzono listę „Akty zmieniające” po t.j. Komunikaty, artykuły i omówienia orzeczeń pochodzą z WebSearch/WebFetch. To **źródła wtórne**, oznaczone w tabeli jako „NIE”. Ich treść pochodzi z narzędzia streszczającego i należy ją traktować jako parafrazę.

**Pliki robocze:** `/tmp/claude-0/-home-user-aihouse/d6e847b4-aa7d-5319-ac6c-1cfc7e9fc1de/scratchpad/research/R8/`. Są tam m.in.:
- `t_2026_538.txt` (upzp t.j.), `t_2023_1688.txt`, `t_2026_781.txt`, `t_2026_1192.txt`;
- `t_2024_1151.txt` (PGiK), `t_2022_1670.txt` (standardy geodezyjne), `t_2021_1385.txt` (BDOT500);
- `t_2026_13.txt` (u.o.p.), `t_2014_112.txt` (hałas), `t_2025_647.txt` (POŚ), `t_2025_960.txt` (Prawo wodne);
- `t_2024_82.txt` (u.o.g.r.l.), `t_2019_1839.txt` (rozporządzenie OOŚ), `t_2022_1518.txt` (drogi).

Teksty WT (t.j. 2022/1225) i u.d.p. (t.j. 2025/889) pochodzą z plików wspólnych: `../R3/wt_clean.txt` i `../t_2025_889.txt`.

**Skróty:**

| Skrót | Akt |
|---|---|
| **upzp** | ustawa z 27.03.2003 o planowaniu i zagospodarowaniu przestrzennym (t.j. Dz.U. 2026 poz. 538, zm. poz. 781, 864, 912) |
| **u.zm.upzp** | ustawa z 7.07.2023 o zmianie upzp (Dz.U. 2023 poz. 1688 ze zm.) |
| **PB** | Prawo budowlane (t.j. Dz.U. 2026 poz. 524 ze zm.) |
| **WT** | rozporządzenie MI z 12.04.2002 w sprawie warunków technicznych, jakim powinny odpowiadać budynki i ich usytuowanie (t.j. Dz.U. 2022 poz. 1225, zm. Dz.U. 2023 poz. 2442 [od 1.08.2024, termin zm. Dz.U. 2024 poz. 474], Dz.U. 2024 poz. 726 [od 15.08.2024]; stosowane w brzmieniu obowiązującym do 19.09.2026 na podstawie art. 102a PB, zob. R1). **Uwaga:** § 12 WT cytować w brzmieniu po zmianach 2023/2442 i 2024/726, a nie według samego t.j. 2022/1225 |
| **RPB** | rozporządzenie MR z 11.09.2020 w sprawie szczegółowego zakresu i formy projektu budowlanego (t.j. Dz.U. 2022 poz. 1679, zm. Dz.U. 2023 poz. 2405 [od 1.04.2024] i Dz.U. 2026 poz. 597 [od 19.05.2026; m.in. § 15 ust. 3 — dokładność 0,01 m]) |
| **PGiK** | Prawo geodezyjne i kartograficzne (t.j. Dz.U. 2024 poz. 1151 ze zm.) |
| **rozp. standardów** | rozporządzenie MR z 18.08.2020 w sprawie standardów technicznych wykonywania geodezyjnych pomiarów sytuacyjnych i wysokościowych… (t.j. Dz.U. 2022 poz. 1670) |
| **u.d.p.** | ustawa o drogach publicznych (t.j. Dz.U. 2025 poz. 889 ze zm.) |
| **u.o.p.** | ustawa o ochronie przyrody (t.j. Dz.U. 2026 poz. 13 ze zm.) |
| **POŚ** | Prawo ochrony środowiska (t.j. Dz.U. 2025 poz. 647 ze zm.) |
| **PW** | Prawo wodne (t.j. Dz.U. 2025 poz. 960 ze zm.) |
| **u.o.g.r.l.** | ustawa o ochronie gruntów rolnych i leśnych (t.j. Dz.U. 2024 poz. 82 ze zm.) |
| **OO** | obszar oddziaływania obiektu |
| **PBC** | powierzchnia biologicznie czynna |

---

## 1. Streszczenie stanu prawnego (na 2026-09-25)

### 1.1 Planowanie przestrzenne: definicje wskaźników i status MPZP
1. **Upzp.** Tekst jednolity to **Dz.U. 2026 poz. 538** (obwieszczenie z 27.03.2026). Po t.j. wprowadzono trzy zmiany:
   - **poz. 781** (od 1.07.2026): m.in. inwestycja uzupełniająca, ZPI, WZ, terminy przejściowe reformy;
   - **poz. 912** (od 31.07.2026): związek metropolitalny pomorski;
   - **poz. 864** (od 1.10.2026): lotnictwo służb.

   Żadna z nich nie zmienia art. 2 pkt 28–35 ani art. 15 ust. 2 pkt 6.
2. **Definicje ustawowe wskaźników** wprowadziła reforma z 2023 r. (Dz.U. 2023 poz. 1688). Są w **art. 2 pkt 28–35 upzp**:
   - pkt 28 — **powierzchnia biologicznie czynna**, z zasadą **50% powierzchni tarasów i stropodachów** o powierzchni ≥10 m²;
   - pkt 29 — udział PBC;
   - pkt 30 — **wysokość zabudowy**;
   - pkt 31 — intensywność zabudowy;
   - pkt 32 — **nadziemna intensywność zabudowy**;
   - pkt 33 — powierzchnia kondygnacji;
   - pkt 34 — kondygnacja nadziemna;
   - pkt 35 — **udział powierzchni zabudowy**.

   Pełne brzmienia są w tabeli (R8-01…R8-06). Rozporządzenia o projekcie MPZP nie zawierają tych definicji. **Definicji „linii zabudowy” nie ma w żadnym akcie powszechnie obowiązującym.** O jej znaczeniu przesądza tekst MPZP.
3. **Zakres stosowania definicji (przepis przejściowy).** Art. 67 u.zm.upzp:
   - ust. 2: „Do zachowanych w mocy miejscowych planów zagospodarowania przestrzennego **nie stosuje się definicji, o których mowa w art. 2 pkt 27–35**”;
   - ust. 3 pkt 1: do planów sporządzanych, dla których **nie wystąpiono o opinie i uzgodnienia przed 24.09.2023**, stosuje się już nowe art. 2 pkt 28–35 i art. 15 ust. 2 pkt 6.

   Wniosek: czy definicje ustawowe obowiązują dla MPZP z 21.03.2024 (fikcyjnego), zależy od przebiegu procedury planistycznej. **Fikcyjny MPZP musi to jednoznacznie przesądzić** (zalecenie w pkt 3.1).
4. **Nowe rozporządzenie o projekcie MPZP.** Rozporządzenie MFiG z 7.09.2026 w sprawie sposobu przygotowania projektu MPZP (**Dz.U. 2026 poz. 1192**) obowiązuje **od 24.09.2026**. Zastąpiło rozp. MRiT z 17.12.2021 (Dz.U. 2021 poz. 2404), które uznano za uchylone z tym dniem.
   - Dotyczy **sporządzania planów**: klasy przeznaczenia, np. MN / **MNW** (zabudowa jednorodzinna wolnostojąca); oznaczenia linii zabudowy w zał. 2; dokumentowanie prac.
   - **Nie wpływa na ocenę zgodności projektu z już uchwalonym planem.** Do planów, których sporządzanie rozpoczęto przed 24.09.2026, stosuje się przepisy dotychczasowe (§ 10).
5. **Reforma 2023 a działka z MPZP.**
   - Dotychczasowe MPZP **zachowują moc** (art. 67 ust. 1 u.zm.upzp).
   - Studia uwarunkowań i kierunków zagospodarowania przestrzennego gmin (dalej: studia) straciły moc najpóźniej **31.08.2026**. Termin z art. 65 ust. 1 u.zm.upzp przesunięto z 30.06.2026 ustawą Dz.U. 2026 poz. 781, art. 5 pkt 6.
   - **Plan ogólny gminy nie stanowi podstawy sprawdzenia z art. 35 ust. 1 pkt 1 lit. a PB** (art. 13a ust. 6 pkt 3 upzp).
   - Dla wniosku o PnB na działce objętej MPZP wiążący jest wyłącznie MPZP i inne akty prawa miejscowego. Brak planu ogólnego (lub jego treść) nie wpływa na PnB. Wpływa tylko na zmianę MPZP (art. 67 ust. 4 u.zm.upzp).

### 1.2 Warunki techniczne usytuowania (WT)
Na PZT wpływają przede wszystkim przepisy działu II WT (§ 12–43) oraz § 13, 57, 60 i 271.
- WT z 2002 r. mają w ELI status „uznany za uchylony” z datą **2026-09-21** (sprawdzono ponownie 25.09.2026).
- Nowych WT dla budynków nie wydano (szczegóły: **R1, pkt 1.1**).
- WT **stosuje się do PZT i PAB po złożeniu oświadczenia inwestora z art. 102a ust. 1 PB** (Dz.U. 2026 poz. 1161; okres 18 miesięcy od 20.09.2026).
- Organ sprawdza zgodność **PZT** „z przepisami, w tym techniczno-budowlanymi” (art. 35 ust. 1 pkt 2 PB). Bez oświadczenia z art. 102a nie ma aktu wykonawczego, według którego organ oceni odległości, dojazdy i parkingi.

**Wszystkie wartości WT w tabeli obowiązują pod warunkiem złożenia oświadczenia z art. 102a PB.**

**Brzmienie WT.** Art. 102a PB odsyła do przepisów „obowiązujących do dnia 19 września 2026 r.”, czyli do WT z uwzględnieniem zmian Dz.U. 2023 poz. 2442 (od 1.08.2024) i Dz.U. 2024 poz. 726 (od 15.08.2024). Dla PZT istotne są zmiany § 12: ust. 1 (każda płaszczyzna uskoku lub załamania ściany to osobna ściana), nowy ust. 1a (3–4 m przy ścianie nierównoległej), ust. 10 (także publicznie dostępny plac) i zał. nr 1a. Sam t.j. 2022/1225 tych zmian nie zawiera.

### 1.3 Geodezja: mapa do celów projektowych
- **PGiK:** t.j. 2024 poz. 1151. Zmiany po t.j.:
  - 2024 poz. 1824: art. 53b;
  - 2025 poz. 1019: art. 45f, mObywatel;
  - 2025 poz. 1542: rejestr cen nieruchomości, od 13.02.2026;
  - 2025 poz. 1792: od 17.06.2027, art. 7a.

  Żadna nie zmienia definicji mapy do celów projektowych (**art. 2 pkt 7a**), art. 12b ust. 5–5c ani art. 28b.
- **Rozp. standardów:** t.j. Dz.U. 2022 poz. 1670, bez zmian po t.j. Istotne przepisy:
  - § 8: porównanie treści mapy z terenem;
  - § 30: podpis kierownika prac;
  - § 31: pomiar punktów granicznych przy budynku **≤ 4 m** od granicy;
  - § 32: treść mapy, w tym zieleń wysoka i pomniki przyrody, oraz znaki mapy zasadniczej;
  - § 33: opis mapy.
- **Rozporządzenie o BDOT500 i mapie zasadniczej** (Dz.U. 2021 poz. 1385): **obowiązuje, bez zmian**. Podstawowa skala mapy zasadniczej to **1:500** (§ 10 ust. 2), a znaki umowne określa zał. 4 (§ 10 ust. 3).
- **Aktualność mapy.** PB wymaga „aktualnej mapy do celów projektowych” (art. 34 ust. 3 pkt 1). **Żaden przepis nie określa terminu ważności.** Według NSA (II OSK 909/14; źródło wtórne) mapa jest aktualna, dopóki odzwierciedla stan faktyczny terenu.

### 1.4 Drogi: zjazd, pas drogowy, odległości
- **U.d.p.:** t.j. 2025 poz. 889. Zmiany po t.j.: 2026 poz. 815 (art. 20i, sytuacje kryzysowe) i poz. 982 (m.in. art. 13, 13k, 13naa, 40a — opłaty elektroniczne). **Nie zmieniają art. 29, 39, 40 ani 43.**
- **Zjazd:**
  - zezwolenie zarządcy drogi na lokalizację zjazdu (decyzja) określa miejsce i parametry techniczne;
  - zezwolenie **dołącza się do wniosku o PnB** (art. 29 ust. 3a);
  - **wygasa po 3 latach**, jeżeli zjazdu nie wybudowano (art. 29 ust. 5).
- **Parametry zjazdu.** Rozporządzenie techniczne dla dróg (Dz.U. 2022 poz. 1518, zm. 2025 poz. 1352) określa je **opisowo**, przez pojazd miarodajny (§ 54–56). Nie podaje minimalnej szerokości zjazdu indywidualnego. Parametry wyznacza zezwolenie zarządcy.

### 1.5 Przyroda: drzewa
- **U.o.p.:** t.j. 2026 poz. 13. Zmiany po t.j.: poz. 426, 737 (płoszenie zwierząt), 912. **Żadna nie zmienia art. 83f.**
- Osoba fizyczna, która usuwa drzewa na cele **niezwiązane z działalnością gospodarczą**, nie potrzebuje zezwolenia (art. 83f ust. 1 pkt 3a).
- Obowiązuje jednak **zgłoszenie** zamiaru usunięcia drzewa o obwodzie pnia na wysokości 5 cm powyżej **80 / 65 / 50 cm** (ust. 4). Następnie organ dokonuje oględzin w ciągu 21 dni i może wnieść sprzeciw w ciągu 14 dni (ust. 6–8).

### 1.6 Hałas: pompa ciepła
- Rozporządzenie MŚ z 14.06.2007 w sprawie dopuszczalnych poziomów hałasu w środowisku (t.j. **Dz.U. 2014 poz. 112**) **obowiązuje, bez zmian po 2012 r.**
- Dla **terenów zabudowy mieszkaniowej jednorodzinnej** i źródeł „pozostałych” (instalacje):
  - **L_Aeq,D = 50 dB** (8 najmniej korzystnych godzin dnia, 6:00–22:00);
  - **L_Aeq,N = 40 dB** (1 najmniej korzystna godzina nocy, 22:00–6:00).
- Pora dnia i nocy: art. 112a pkt 1 lit. b POŚ.
- Art. 144 ust. 2 POŚ: emisja hałasu z instalacji nie może przekraczać standardów **poza terenem, do którego prowadzący ma tytuł prawny**, czyli na granicy działek sąsiednich MN.
- Przydomowa pompa ciepła **nie wymaga zgłoszenia instalacji**. Rozporządzenie wydane na podstawie art. 152/153 POŚ (t.j. Dz.U. 2019 poz. 1510) nie wymienia takich instalacji.

### 1.7 Wody opadowe
- **PW:** t.j. 2025 poz. 960. Zmiany po t.j.:
  - 2025 poz. 1535;
  - 2026 poz. 445, 605, 815, 1033 (legalizacja ujęć);
  - 2026 poz. **1156** (od 1.01.2027; woda odzyskana ze ścieków komunalnych w chłodnictwie energetycznym).

  **Żadna nie zmienia art. 16 pkt 65 i 69, art. 33, art. 34 pkt 4, art. 234, art. 269 ust. 1 pkt 1, art. 389 ani art. 395.**
- **Opłata za zmniejszenie naturalnej retencji terenowej** dotyczy nieruchomości **> 3500 m²**, na których zabudowa wyłącza **> 70%** powierzchni z PBC, na obszarach nieujętych w systemy kanalizacji (art. 269 ust. 1 pkt 1 PW). **Działka 1600 m² jest poza zakresem.**
- **Zakazy:**
  - PW art. 234 ust. 1: nie wolno zmieniać odpływu wód opadowych ze szkodą dla gruntów sąsiednich ani odprowadzać wód na grunty sąsiednie;
  - WT § 29: nie wolno zmieniać naturalnego spływu w celu kierowania wód na sąsiednią nieruchomość;
  - u.d.p. art. 39 ust. 1 pkt 9: nie wolno odprowadzać wody do rowów przydrożnych ani na jezdnię.
- **Rozsączanie w ziemi: status wodnoprawny niejednoznaczny.**
  - Art. 16 pkt 65 lit. f PW zalicza do urządzeń wodnych „wyloty służące do wprowadzania wody do … ziemi”.
  - Art. 389 pkt 6 wymaga pozwolenia wodnoprawnego na wykonanie urządzeń wodnych.
  - Art. 395 nie zawiera zwolnienia dla rozsączania wód opadowych z dachów domów jednorodzinnych.
  - Źródła wtórne są sprzeczne. Szczelny zbiornik na deszczówkę **nie jest** urządzeniem wodnym (FAQ PGW Wody Polskie).
  - Pozycja w sekcji 4 (ryzyko R8-R3).
- **Odległości urządzeń rozsączających od budynków i granic nie są uregulowane normatywnie.** WT § 31–38 dotyczą studni, szamb i osadników. Wartości z poradników i instrukcji producentów to wytyczne, nie przepisy.

### 1.8 Grunty rolne i oddziaływanie na środowisko
- **U.o.g.r.l.:** t.j. 2024 poz. 82. Zmiany: 2026 poz. 781 (art. 7), poz. 1155 (od 16.09.2026, art. 20, 26, 28 — rekultywacja), poz. 875 (od 1.01.2027, art. 22). **Art. 11 i 12a bez zmian.**
- **Decyzję o wyłączeniu gruntów z produkcji** trzeba mieć, gdy grunt w ewidencji to:
  - użytek rolny klas **I–IIIb**;
  - użytek rolny klas **IV–VI pochodzenia organicznego**;
  - grunt z art. 2 ust. 1 pkt 2–10.

  Decyzję wydaje się **przed PnB** i **dołącza do wniosku** (art. 11 ust. 1, 4, 4a).
- **Zwolnienie z należności i opłat rocznych** obejmuje do **0,05 ha** pod budynek jednorodzinny (art. 12a pkt 1).
- **Decyzja o środowiskowych uwarunkowaniach (DŚU) nie jest wymagana.** Rozporządzenie RM z 10.09.2019 (Dz.U. 2019 poz. 1839, zm. 2022/1071, 2023/1724, 2026/706, 2026/1185 od 22.09.2026) kwalifikuje zabudowę mieszkaniową objętą MPZP jako przedsięwzięcie mogące potencjalnie znacząco oddziaływać dopiero od **2 ha** (obszary chronione) lub **4 ha** powierzchni zabudowy (§ 3 ust. 1 pkt 55 lit. a). Garaże i parkingi kwalifikuje od **0,5/1,0 ha** powierzchni użytkowej (pkt 58 w brzmieniu nadanym Dz.U. 2023 poz. 1724, od 13.09.2023). Zmiany z 2026 r. dotyczą wyłącznie elektrowni wiatrowych (pkt 6) i dróg (pkt 62).

---

## 2. Tabela wymagań

Legenda kolumny „pierwotne?”: TAK oznacza tekst aktu z Dz.U. (API ELI), NIE oznacza źródło wtórne. Adres `ELI/…` skraca `https://api.sejm.gov.pl/eli/acts/DU/…/text.pdf`.

### 2A. Planowanie przestrzenne i wskaźniki MPZP

| ID | Wymaganie (konkretnie, z wartościami) | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R8-01 | **PBC** to „teren zapewniający naturalną wegetację roślin i retencję wód opadowych i roztopowych, teren pokryty ciekami lub zbiornikami wodnymi, z wyłączeniem basenów rekreacyjnych i przemysłowych, a także **50 % powierzchni tarasów i stropodachów oraz innych powierzchni zapewniających naturalną wegetację roślin, o powierzchni niemniejszej niż 10 m²**”. | upzp art. 2 pkt 28 (Dz.U. 2026 poz. 538) | https://api.sejm.gov.pl/eli/acts/DU/2026/538/text.pdf | TAK | **Dach zielony garażu:** ≥10 m², liczy się 50% jego powierzchni. Dotyczy MPZP, do których stosuje się nowe definicje (R8-07). |
| R8-02 | **Udział PBC** to stosunek sumy PBC na działce budowlanej do powierzchni tej działki (dla MPZP). | upzp art. 2 pkt 29 lit. a | jw. | TAK | LAMELA: ≥50% × 1600 m² = **≥ 800,00 m²**. |
| R8-03 | **Wysokość zabudowy** to różnica między wysokością „najwyżej położonego punktu budynku na dachu, ścianie lub **attyce**, z wyłączeniem komina, nadbudówki mieszczącej maszynownię dźwigu lub innego pomieszczenia technicznego oraz wyjścia z klatki schodowej” a „**średnią wysokością najniższego i najwyższego poziomu terenu mierzoną na obwodzie rzutu poziomego ścian zewnętrznych budynku**”. | upzp art. 2 pkt 30 lit. a | jw. | TAK | Wyłączenia są zamknięte. **Balustrady, konstrukcje PV i wyłazy nie są wyłączone** (ryzyko R8-R5). Przepis nie mówi, czy chodzi o teren istniejący, czy projektowany. |
| R8-04 | **Intensywność zabudowy** to stosunek sumy powierzchni **wszystkich** kondygnacji budynków na działce do powierzchni działki. **Nadziemna intensywność** obejmuje tylko kondygnacje nadziemne. | upzp art. 2 pkt 31 lit. a, pkt 32 lit. a | jw. | TAK | Bez podpiwniczenia oba wskaźniki są równe. |
| R8-05 | **Powierzchnia kondygnacji** to powierzchnia rzutu poziomego kondygnacji „mierzona po zewnętrznym obrysie rzutu poziomego ścian zewnętrznych tej kondygnacji, **z wyłączeniem powierzchni balkonów, logii i tarasów**”. **Kondygnacja nadziemna** to taka, która „nie jest zagłębiona poniżej poziomu przylegającego do niej terenu o więcej niż połowę jej wysokości w świetle”. | upzp art. 2 pkt 33, 34 | jw. | TAK | Garaż w bryle parteru wlicza się do powierzchni kondygnacji. |
| R8-06 | **Udział powierzchni zabudowy** to stosunek „sumy powierzchni rzutu poziomego budynków, z wyłączeniem części zagłębionych poniżej poziomu terenu, **mierzonej po zewnętrznym obrysie rzutu poziomego ścian zewnętrznych** tych budynków” na działce do jej powierzchni. | upzp art. 2 pkt 35 lit. a | jw. | TAK | Wspornik bryły A i boks C (ściany zewnętrzne) **wchodzą** do rzutu. Wysunięte płyty i okapy (nie ściany) nie wchodzą. LAMELA: ≤30% = **≤ 480,00 m²**. |
| R8-07 | **Zakres stosowania definicji R8-01…R8-06.** Do **zachowanych w mocy** MPZP nie stosuje się art. 2 pkt 27–35. Do planów, dla których **nie wystąpiono o opinie i uzgodnienia przed 24.09.2023**, stosuje się art. 2 pkt 28–35 i art. 15 ust. 2 pkt 6 w nowym brzmieniu. | u.zm.upzp art. 67 ust. 2 i ust. 3 pkt 1 (Dz.U. 2023 poz. 1688) | https://api.sejm.gov.pl/eli/acts/DU/2023/1688/text.pdf | TAK | Fikcyjny MPZP z 21.03.2024 musi wskazać reżim definicji albo zawierać własne definicje (pkt 3.1). |
| R8-08 | MPZP obowiązkowo określa m.in. „maksymalną i minimalną **nadziemną** intensywność zabudowy, minimalny udział PBC, maksymalny udział powierzchni zabudowy, maksymalną wysokość zabudowy, minimalną liczbę i sposób realizacji miejsc do parkowania (…) oraz linie zabudowy i gabaryty obiektów”. Przed reformą: „intensywność zabudowy jako wskaźnik powierzchni całkowitej zabudowy w odniesieniu do powierzchni działki budowlanej” i „minimalny udział procentowy PBC”. | upzp art. 15 ust. 2 pkt 6 (t.j. 2026/538); brzmienie dawne: t.j. Dz.U. 2023 poz. 977 | https://api.sejm.gov.pl/eli/acts/DU/2026/538/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2023/977/text.pdf | TAK | Brief podaje „intensywność 0,05–0,80”. W nowym reżimie powinno to być „nadziemna intensywność”. |
| R8-09 | **Linia zabudowy nie ma definicji ustawowej ani rozporządzeniowej.** Rozp. 2026/1192, zał. 2, określa tylko oznaczenia graficzne: „obowiązująca” i „nieprzekraczalna linia zabudowy” (linia 0,35 mm z trójkątami o boku 3 mm) oraz „nieprzekraczalna linia zabudowy dla kondygnacji podziemnych”. Treść linii (co może ją przekroczyć) wynika wyłącznie z MPZP. | rozp. MFiG z 7.09.2026, zał. 2 (Dz.U. 2026 poz. 1192); upzp art. 15 ust. 2 pkt 6 | https://api.sejm.gov.pl/eli/acts/DU/2026/1192/text.pdf | TAK | Fikcyjny MPZP musi zdefiniować linię i dopuszczalne wysunięcia (okapy, płyty, zadaszenie wejścia). |
| R8-10 | Rozp. 2026/1192 obowiązuje **od 24.09.2026** i zastępuje rozp. 2021/2404. Dotyczy sporządzania projektu MPZP: klasy MN, **MNW**, MNB, MNS; skala 1:1000 (upzp art. 16 ust. 1), dopuszczalnie 1:500, 1:2000 lub 1:5000 (§ 3 ust. 3); dokumentacja prac. Do planów rozpoczętych wcześniej stosuje się przepisy dotychczasowe. | rozp. 2026/1192 § 1–4, § 10, § 11; ELI: 2021/2404 „uznany za uchylony” 24.09.2026 | https://api.sejm.gov.pl/eli/acts/DU/2026/1192/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2021/2404 | TAK | Nie wpływa na ocenę projektu względem uchwalonego MPZP. Symbol „3MN” w fikcyjnym planie z 2024 r. jest poprawny. |
| R8-11 | **Dotychczasowe MPZP zachowują moc** do wejścia w życie nowych planów. Studia zachowują moc do wejścia w życie planu ogólnego, nie dłużej niż do **31.08.2026**. | u.zm.upzp art. 67 ust. 1; art. 65 ust. 1 w brzmieniu z Dz.U. 2026 poz. 781, art. 5 pkt 6 | https://api.sejm.gov.pl/eli/acts/DU/2023/1688/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2026/781/text.pdf | TAK | Tekst art. 65 odtworzono z aktów zmieniających. Wersji skonsolidowanej u.zm.upzp brak. |
| R8-12 | **Plan ogólny nie jest podstawą** sprawdzenia z art. 35 ust. 1 pkt 1 lit. a PB (zgodność PZT i PAB z MPZP), choć jest aktem prawa miejscowego. | upzp art. 13a ust. 6 pkt 3 i ust. 7 | https://api.sejm.gov.pl/eli/acts/DU/2026/538/text.pdf | TAK | Dla LAMELI wiąże wyłącznie MPZP 3MN. |
| R8-13 | Organ przed PnB sprawdza zgodność PZT i PAB **z ustaleniami MPZP** i innymi aktami prawa miejscowego oraz zgodność **PZT z przepisami, w tym techniczno-budowlanymi**. | PB art. 35 ust. 1 pkt 1 lit. a, pkt 2 (t.j. 2026/524) | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | TAK | Wszystkie wskaźniki MPZP należy wykazać w zestawieniu PZT (R8-45). |
| R8-14 | MPZP przewidujący budynki „umożliwia również lokalizację zamontowanych na budynku instalacji OZE wykorzystujących (…) energię promieniowania słonecznego oraz **mikroinstalacji**”, chyba że plan tego zakazuje. | upzp art. 15 ust. 4 | jw. | TAK | PV na dachu LAMELI (≤ 6,5 kWp, zob. R1) jest zgodne z MPZP, o ile plan nie zakazuje. |
| R8-15 | **Dostęp do drogi publicznej** to „bezpośredni dostęp do tej drogi albo dostęp do niej przez drogę wewnętrzną lub przez ustanowienie odpowiedniej służebności drogowej”. **Działka budowlana** to działka, której „wielkość, cechy geometryczne, dostęp do drogi publicznej oraz wyposażenie w urządzenia infrastruktury technicznej spełniają wymogi realizacji obiektów budowlanych”. PB od 20.09.2026 odsyła do tej definicji. | upzp art. 2 pkt 12, 14; PB art. 3 pkt 26 (dodany Dz.U. 2025 poz. 1847, w mocy od 20.09.2026) | https://api.sejm.gov.pl/eli/acts/DU/2026/538/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2025/1847/text.pdf | TAK | LAMELA ma bezpośredni dostęp z drogi gminnej 1KDD. |
| R8-16 | **Zabudowa jednorodzinna** to „jeden budynek mieszkalny jednorodzinny lub zespół takich budynków, wraz z garażami lub budynkami gospodarczymi”. | PB art. 3 pkt 24 (od 20.09.2026); WT § 3 pkt 2 (analogicznie) | https://api.sejm.gov.pl/eli/acts/DU/2025/1847/text.pdf | TAK | Warunkuje ulgi w WT (§ 12 ust. 4, § 19 ust. 5–6, § 23 ust. 4, § 36 ust. 2). |

### 2B. Usytuowanie i zagospodarowanie działki (WT, stosowane na podstawie art. 102a PB)

| ID | Wymaganie | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R8-17 | **Warunek stosowania WT.** PZT i PAB „może zostać sporządzony zgodnie z przepisami wydanymi na podstawie art. 7 ust. 2 pkt 1, obowiązującymi do dnia 19 września 2026 r.” w okresie 18 miesięcy od 20.09.2026, po złożeniu **oświadczenia inwestora**. | PB art. 102a ust. 1 (Dz.U. 2026 poz. 1161, art. 2 pkt 4) | https://api.sejm.gov.pl/eli/acts/DU/2026/1161/text.pdf | TAK | Szczegóły w R1. Oświadczenie składa się razem z wnioskiem o PnB. |
| R8-18 | **Odległości budynku od granicy działki:** **4 m** dla ściany z oknami lub drzwiami; **3 m** dla ściany „bez okien lub drzwi”; „każdą płaszczyznę powstałą w wyniku załamania lub uskoku ściany traktuje się jako oddzielną ścianę” (ust. 1, sposób wyznaczania — zał. nr 1a, ust. 10a). **Ust. 1a:** ścianę z oknami/drzwiami dopuszcza się w odległości 3–4 m, jeżeli ściana nie jest równoległa do granicy, a zewnętrzna krawędź okna lub drzwi jest ≥ 4 m od granicy. Mniejsze odległości (1,5 m lub przy granicy) wyłącznie w przypadkach z ust. 2–4; wtedy sąsiednia działka wchodzi w OO (ust. 5). | WT § 12 ust. 1, 1a, 2, 4, 5, 10a (t.j. Dz.U. 2022 poz. 1225; ust. 1–3 zm. Dz.U. 2023 poz. 2442; ust. 1 część wspólna, ust. 1a, 10a i zał. 1a dodane Dz.U. 2024 poz. 726, od 15.08.2024) | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2023/2442/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2024/726/text.pdf | TAK | LAMELA: szerokość działki 32 m > 16 m, więc ulga z ust. 4 pkt 1 nie przysługuje. Uskoki brył (wspornik A, boks C) wymiarować do granicy **osobno dla każdej płaszczyzny ściany**. Z ust. 1a nie korzystać (ściany równoległe do granic). |
| R8-19 | Odległość od granicy **≥ 1,5 m do okapu lub gzymsu** zwróconego w stronę granicy, **balkonu, daszku nad wejściem, galerii, tarasu, schodów zewnętrznych, rampy, pochylni**. **≥ 4 m** do okna w dachu. Odległości z ust. 1–9 nie obowiązują, gdy sąsiednia działka jest działką drogową „lub publicznie dostępnym placem” (ust. 10). | WT § 12 ust. 6, ust. 10 (oba w brzmieniu Dz.U. 2023 poz. 2442) | jw. | TAK | Wysunięte płyty 0,8–1,5 m i taras przy salonie muszą mieć ≥ 1,50 m do granic bocznych (E, W) i południowej. |
| R8-20 | **Przesłanianie.** W kącie 60° od osi okna pomieszczenia na pobyt ludzi nie może być obiektu przesłaniającego (także części tego samego budynku) w odległości mniejszej niż **wysokość przesłaniania**. Wysokość mierzy się od dolnej krawędzi najniższych okien do najwyższej zacieniającej krawędzi. | WT § 13 ust. 1–2 | jw. | TAK | Sprawdzić: LAMELA względem okien sąsiadów (budynki ≥ 8 m od granic) oraz wewnętrznie (garaż i bryły P1/P2 względem okien parteru). |
| R8-21 | **Nasłonecznienie:** pokoje mieszkalne co najmniej **3 h w dniach równonocy w godz. 7:00–17:00**. W mieszkaniach wielopokojowych wystarczy co najmniej jeden pokój. Dotyczy także budynków sąsiednich (OO). | WT § 60 ust. 1–2 | jw. | TAK | Analiza cieni dla sąsiadów E i W w PZT lub PAB (część OO). |
| R8-22 | **Dojazd:** szerokość jezdni dojazdu **≥ 3 m**. Ciąg pieszo-jezdny ≥ 5 m. Dojścia pełniące funkcję dojazdu ≥ 4,5 m. Oświetlenie dojść nie jest wymagane dla budynków jednorodzinnych. | WT § 14 ust. 1–4 | jw. | TAK | Podjazd LAMELI ≥ 3,00 m (zalecane ≥ 5,0 m przed garażem 2-stanowiskowym). |
| R8-23 | **Stanowiska postojowe:** liczba według MPZP (§ 18). **2,5 × 5,0 m** dla samochodu osobowego (§ 21 ust. 1 pkt 1). Nawierzchnia utwardzona lub gruntowa stabilizowana, ze spadkiem (§ 21 ust. 3). | WT § 18 ust. 2, § 21 ust. 1 pkt 1, ust. 3 | jw. | TAK | MPZP: ≥ 2 miejsca na lokal (garaż 2-stanowiskowy wystarcza). Miejsca gościnne 1–2 na podjeździe. |
| R8-24 | **Odległość parkingów** (do 10 stanowisk, samochody osobowe): **7 m** od okien pomieszczeń na stały pobyt ludzi w budynkach mieszkalnych; **3 m** od granicy działki. Zwolnienia: od 7 m — niezadaszone parkingi 1–2 stanowisk na lokal przy budynku jednorodzinnym (ust. 5); od 3 m — gdy styka się z parkingiem sąsiada (ust. 6) albo gdy sąsiednia działka jest drogowa (ust. 7). Wjazdy do garażu zamkniętego podlegają odległościom tylko względem budynków opieki zdrowotnej i oświaty oraz placów zabaw (ust. 3). | WT § 19 ust. 1 pkt 1 lit. a, ust. 2 pkt 1 lit. a, ust. 3, 5, 6, 7 | jw. | TAK | **Miejsca gościnne ≥ 3,00 m od granic E i W.** Od granicy z działką drogową 1KDD odległość nie jest wymagana. |
| R8-25 | **Miejsce na pojemniki na odpady** z możliwością segregacji (§ 22 ust. 1). Utwardzone dojście do miejsca odbioru (§ 22 ust. 3). **W zabudowie jednorodzinnej odległości od okien, drzwi i granicy (10 m / 3 m) nie określa się** (§ 23 ust. 4). | WT § 22 ust. 1–3, § 23 ust. 4 | jw. | TAK | Proponowane: wiata lub osłona przy furtce, w linii ogrodzenia. |
| R8-26 | **Uzbrojenie:** możliwość przyłączenia do sieci wodociągowej, kanalizacyjnej, elektroenergetycznej i ciepłowniczej. Indywidualne źródło ciepła jest równorzędne (§ 26 ust. 2). | WT § 26 ust. 1–2 | jw. | TAK | Pompa ciepła spełnia § 26 ust. 2 (dom all-electric). |
| R8-27 | **Wody opadowe:** działka powinna mieć kanalizację do sieci deszczowej lub ogólnospławnej. **Dla budynków niskich** albo przy braku sieci „dopuszcza się odprowadzenie wód opadowych na własny teren nieutwardzony, do dołów chłonnych lub do zbiorników retencyjnych”. „Dokonywanie zmiany naturalnego spływu wód opadowych w celu kierowania ich na teren sąsiedniej nieruchomości jest zabronione.” | WT § 28 ust. 1–2, § 29 | jw. | TAK | LAMELA jest budynkiem niskim (N, § 8 pkt 1), a sieci deszczowej brak, więc stosuje się § 28 ust. 2. |
| R8-28 | **Ogrodzenie:** nie może zagrażać ludziom i zwierzętom. Ostre elementy i drut kolczasty poniżej **1,8 m** są zakazane (§ 41). Bramy i furtki **nie mogą otwierać się na zewnątrz działki** (§ 42 ust. 1). Brama **≥ 2,4 m** w świetle, furtka **≥ 0,9 m** (§ 43). | WT § 41 ust. 1–2, § 42 ust. 1, § 43 | jw. | TAK | Brama przesuwna spełnia § 42. Wysokość ≤ 1,60 m i ażurowość wynikają z MPZP. |
| R8-29 | **Wysokość budynku** do celów WT mierzy się od poziomu terenu przy najniżej położonym wejściu na pierwszej kondygnacji nadziemnej do górnej powierzchni najwyższego stropu z izolacją. Grupa **N (niskie):** do 12 m lub budynek mieszkalny do 4 kondygnacji nadziemnych. „Poziom terenu” to „przyjęta w projekcie rzędna terenu”. | WT § 6, § 8 pkt 1, § 3 pkt 15 | jw. | TAK | **Inna definicja niż wysokość zabudowy z upzp (R8-03).** Wysokość należy wykazać w obu ujęciach. |
| R8-30 | **Teren biologicznie czynny (WT)** to „teren o nawierzchni urządzonej w sposób zapewniający naturalną wegetację roślin i retencję wód opadowych, a także **50% powierzchni tarasów i stropodachów z taką nawierzchnią** oraz innych powierzchni zapewniających naturalną wegetację roślin, o powierzchni nie mniejszej niż 10 m², oraz wodę powierzchniową na tym terenie”. | WT § 3 pkt 22 | jw. | TAK | Dla planów „starego” reżimu (R8-07) praktyka sięga po tę definicję. Wynik jest zbieżny z R8-01. |
| R8-31 | **Odległość ppoż. między budynkami ZL:** **8 m** (ściany o klasie E na > 65% powierzchni). Zwiększa się przy ścianach lub dachach rozprzestrzeniających ogień (ust. 2). Odległość od granicy lasu (Ls w ewidencji lub las w MPZP) wynika z ust. 8–8a. | WT § 271 ust. 1, 2, 8, 8a | jw. | TAK | Pełna analiza należy do domeny ppoż. LAMELA: sąsiedzi ≥ 8 m od granic, LAMELA ≥ 4 m od granic, więc między budynkami ≥ 12 m. |

### 2C. Geodezja: mapa do celów projektowych i obsługa geodezyjna

| ID | Wymaganie | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R8-32 | **Mapa do celów projektowych** to „opracowanie kartograficzne, wykonane z wykorzystaniem wyników pomiarów geodezyjnych i materiałów [PZGiK], zawierające elementy stanowiące treść mapy zasadniczej (…), a także informacje niezbędne do sporządzenia dokumentacji projektowej oraz (…) **klauzulę urzędową** (…) albo **oświadczenie wykonawcy prac geodezyjnych o uzyskaniu pozytywnego wyniku weryfikacji**”. PB odsyła do tej definicji. | PGiK art. 2 pkt 7a (t.j. Dz.U. 2024 poz. 1151); PB art. 3 pkt 14a | https://api.sejm.gov.pl/eli/acts/DU/2024/1151/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | TAK | Zmiany PGiK 2024/1824, 2025/1019, 2025/1542 i 2025/1792 nie dotyczą art. 2 pkt 7a (sprawdzono). |
| R8-33 | **PZT sporządza się „na aktualnej mapie do celów projektowych lub jej kopii”.** Mapy używane w procesie budowlanym „powinny być opatrzone klauzulą urzędową (…) albo oświadczeniem wykonawcy prac geodezyjnych o uzyskaniu pozytywnego wyniku weryfikacji”. Mapę zapewnia **inwestor** (art. 27a pkt 1). | PB art. 34 ust. 3 pkt 1, art. 34b, art. 27a pkt 1 | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | TAK | Oświadczenie geodety zawiera m.in. nazwę organu, wykonawcę, numer uprawnień kierownika, numer i datę protokołu weryfikacji oraz klauzulę karną (PGiK art. 12b ust. 5a–5c). |
| R8-34 | **Aktualność mapy nie ma terminu ustawowego.** Według NSA mapa „jest aktualna tak długo, jak długo odzwierciedla obecny (teraźniejszy) stan rzeczy istniejący na danym terenie”. | PB art. 34 ust. 3 pkt 1; NSA II OSK 909/14 (za Mazowiecką OIA) | https://mazowiecka.iarp.pl/?p=1807 | NIE | Sygnatury nie zweryfikowano w CBOSA. Praktyka urzędów bywa różna. Przed złożeniem wniosku sprawdzić zgodność mapy z terenem. |
| R8-35 | Przy sporządzaniu mapy do celów projektowych geodeta **porównuje treść mapy zasadniczej ze stanem w terenie**. Wynik pokazuje na mapie porównania z terenem (kolor czerwony: elementy do usunięcia i do pomiaru). | rozp. standardów § 8 ust. 1 (t.j. Dz.U. 2022 poz. 1670) | https://api.sejm.gov.pl/eli/acts/DU/2022/1670/text.pdf | TAK | |
| R8-36 | Jeżeli **budynek** ma stanąć w odległości **≤ 4 m** (inne obiekty budowlane: **≤ 3 m**) od granicy, a w zasobie brak danych o punktach granicznych z dokładnością I grupy, wykonawca **mierzy punkty graniczne**. Gdy punkty nie są oznaczone lub jednoznaczne, najpierw ustala przebieg granic. | rozp. standardów § 31 ust. 1–2 | jw. | TAK | LAMELA: jeśli ściany są ≥ 4,01 m od granic, obowiązek z § 31 nie powstaje. Ogrodzenie, śmietnik i złącze leżą w granicy, więc zlecić pomiar granic tak czy inaczej (zalecenie). |
| R8-37 | **Treść mapy do celów projektowych:** szczegóły mapy zasadniczej, „**usytuowanie zieleni wysokiej ze wskazaniem pomników przyrody**”, szczegóły i informacje określone przez projektanta lub inwestora, w tym miary liniowe. Treść i skalę dostosowuje się do zamierzenia. Stosuje się **znaki mapy zasadniczej**; inne obiekty objaśnia legenda. | rozp. standardów § 32 ust. 1–3 | jw. | TAK | W zleceniu dla geodety zamówić: rzędne terenu (siatka co ≤ 10 m i narożniki), drzewa z obwodami pni (dla art. 83f u.o.p.), krawędź jezdni, uzbrojenie w pasie 1KDD, hydranty. |
| R8-38 | **Opis mapy:** tytuł „Mapa do celów projektowych”, skala, położenie obszaru, gmina, identyfikator i nazwa obrębu, wykonawca, **identyfikator zgłoszenia prac**, imię, nazwisko i numer uprawnień kierownika prac, **układ współrzędnych i wysokości**, obszar aktualizacji, data i opracowujący. Mapę podpisuje kierownik prac: własnoręcznie albo, w postaci elektronicznej, podpisem kwalifikowanym, osobistym lub zaufanym. | rozp. standardów § 33 pkt 1–11, § 30 ust. 3 | jw. | TAK | Układ PL-2000 i PL-EVRF2007-NH zgodnie z briefem. **Pas 6 (południk osiowy 18°E)** — rozp. RM z 15.10.2012 w sprawie PSOP § 13 ust. 2 i § 22 (t.j. Dz.U. 2024 poz. 342, zm. 2025 poz. 106): pasy PL-2000 o południkach 15°, 18°, 21°, 24°E (nr 5–8), granice pasów wzdłuż granic powiatów, południk graniczny 16,5°E; Poznań (~16,9°E) i przeważająca część powiatu poznańskiego leżą na wschód od 16,5°E. |
| R8-39 | **Mapa zasadnicza:** skala podstawowa **1:500**. Znaki umowne określa zał. 4, zdefiniowane dla 1:500; w innych skalach pomniejsza się je o 25%. Rozporządzenie obowiązuje bez zmian. | rozp. MRPiT z 23.07.2021 w sprawie BDOT500 i mapy zasadniczej, § 10 ust. 2–3, zał. 4 (Dz.U. 2021 poz. 1385) | https://api.sejm.gov.pl/eli/acts/DU/2021/1385/text.pdf | TAK | PZT: skala ≥ 1:500 (RPB § 9 ust. 5, zob. R2). |
| R8-40 | **Narady koordynacyjne (ZUD)** nie dotyczą **przyłączy** ani sieci uzbrojenia leżących wyłącznie w granicach działki budowlanej. | PGiK art. 28b ust. 1–2 | https://api.sejm.gov.pl/eli/acts/DU/2024/1151/text.pdf | TAK | Przyłącza LAMELI nie przechodzą przez ZUD. |
| R8-41 | **Geodezyjne wyznaczenie** w terenie i **inwentaryzacja powykonawcza** są wymagane dla obiektów objętych PnB. Wyznaczenia nie wymagają przyłącza z połączeniem z siecią na tej samej lub przyległej działce. | PB art. 43 ust. 1 pkt 1, ust. 1a | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | TAK | Na etapie realizacji. Do PZT wpisać punkty wytyczenia (osie, narożniki). |

### 2D. Droga publiczna: zjazd, pas drogowy, odległości

| ID | Wymaganie | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R8-42 | **Zjazd buduje właściciel nieruchomości** po uzyskaniu **decyzji zarządcy drogi o zezwoleniu na lokalizację zjazdu**. Zezwolenie jest bezterminowe, określa miejsce i parametry techniczne oraz poucza o obowiązkach:<br>• zezwolenie na roboty w pasie drogowym;<br>• **uzgodnienie z zarządcą drogi PZT i PAB zjazdu**, jeśli są wymagane.<br>Zezwolenie „**dołącza się do wniosku o pozwolenie na budowę**” i **wygasa, jeśli w ciągu 3 lat** zjazdu nie wybudowano. Za zjazd bez zezwolenia lub o innych parametrach grozi kara: 10-krotność opłaty (art. 29a). | u.d.p. art. 29 ust. 1, 3, 3a, 5; art. 29a ust. 1 (t.j. Dz.U. 2025 poz. 889) | https://api.sejm.gov.pl/eli/acts/DU/2025/889/text.pdf | TAK | Zmiany 2026/815 i 2026/982 nie dotyczą art. 29 (sprawdzono). **Wymagane dla nowego zjazdu na działkę 123/4.** Zjazd z drogi gminnej nie wymaga PnB ani zgłoszenia (zob. R1-38). |
| R8-43 | **Zakazy w pasie drogowym:** m.in. „odprowadzania wody i ścieków z urządzeń melioracyjnych, gospodarskich lub zakładowych do rowów przydrożnych lub na jezdnię” (pkt 9) oraz „usuwania, niszczenia i uszkadzania zadrzewień przydrożnych” (pkt 12). **Urządzenia obce** (w tym przyłącza) w pasie drogowym lokalizuje się za **zezwoleniem zarządcy drogi** (decyzja; ust. 3). **Zajęcie pasa drogowego** na roboty lub umieszczenie urządzeń wymaga zezwolenia (decyzja) i jest płatne. | u.d.p. art. 39 ust. 1 pkt 9 i 12, ust. 1a, ust. 3; art. 40 ust. 1–3 | jw. | TAK | Odwodnienie podjazdu: **spadek do działki, odwodnienie liniowe przed bramą**, nic nie spływa na 1KDD. Decyzje z art. 39 ust. 3 i art. 40 są potrzebne przed robotami, nie do wniosku o PnB. |
| R8-44 | **Odległość obiektów budowlanych od zewnętrznej krawędzi jezdni** drogi gminnej: **6 m w terenie zabudowy**, **15 m poza terenem zabudowy**. Mniejsza odległość jest dopuszczalna wyłącznie za zgodą zarządcy drogi, dołączaną do wniosku o PnB. | u.d.p. art. 43 ust. 1 (tabela lp. 3 lit. c), ust. 2, 2a | jw. | TAK | Linia zabudowy MPZP 6,0 m od linii rozgraniczającej daje ≥ 6 m od krawędzi jezdni. Pojęcie „teren zabudowy” jest autonomiczne, zob. R8-44a. |
| R8-44a | Według NSA (II OSK 2184/14, 24.05.2016) „teren zabudowy” z art. 43 ust. 1 u.d.p. to teren, na którym dominuje zabudowa, lub teren przeznaczony pod zabudowę w MPZP. Nie stosuje się do tego definicji z rozporządzenia o drogach. | orzecznictwo NSA (źródło wtórne) | https://wartowiedziec.pl/komunikacja-i-transport/31334-qteren-zabudowyq-a-drogi-publiczne-spojrzenie-nsa | NIE | Inne omówienia (INLEGIS) akcentują autonomię pojęcia. Działka w terenie MN z zabudowanymi sąsiadami oznacza niskie ryzyko (R8-R6). |
| R8-44b | **Parametry zjazdu** (droga publiczna): połączenie jezdni z nieruchomością projektuje się jako zjazd jedno- lub dwukierunkowy. Parametry geometryczne „powinny umożliwiać przejazd pojazdu miarodajnego” z uwzględnieniem ruchu pieszych i rowerów. Zjazdu nie lokalizuje się w obszarze skrzyżowania. | rozp. MI z 24.06.2022 w sprawie przepisów techniczno-budowlanych dotyczących dróg publicznych, § 54 ust. 1, 4; § 55 ust. 2; § 56 ust. 2 (Dz.U. 2022 poz. 1518, zm. 2025 poz. 1352) | https://api.sejm.gov.pl/eli/acts/DU/2022/1518/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2025/1352/text.pdf | TAK | **Brak liczbowej minimalnej szerokości.** Szerokość, łuki i przepust określi zezwolenie zarządcy. Założenie projektowe: jezdnia zjazdu 5,00 m, skosy lub łuki R ≥ 3 m (NIEZWERYFIKOWANE jako normatyw). |

### 2E. Zestawienia PZT (RPB)

| ID | Wymaganie | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R8-45 | **Zestawienie w części opisowej PZT:**<br>a) powierzchnia zabudowy projektowanych i istniejących obiektów, pomniejszona o „tarasy naziemne i podparte słupami, gzymsy oraz balkony” (od 1.04.2024 także loggie);<br>b) drogi, parkingi, place, chodniki;<br>c) **PBC**;<br>d) inne części terenu **niezbędne do sprawdzenia zgodności z MPZP**. | RPB § 14 pkt 4 lit. a–d (t.j. Dz.U. 2022 poz. 1679; lit. a zm. Dz.U. 2023 poz. 2405) | https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2023/2405/text.pdf | TAK | Szczegóły formalne w R2 (Z05). Pozycja d): intensywność, wysokość, miejsca postojowe, odległość od linii zabudowy. |
| R8-46 | **Informacja o OO:** (1) wskazanie przepisów, na podstawie których ustalono OO; (2) zasięg opisowo lub graficznie **albo** informacja, że OO mieści się w całości na działce. | RPB § 14 pkt 8, § 18 pkt 1–2; PB art. 3 pkt 20, art. 34 ust. 3 pkt 1 lit. e | https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf | TAK | Wykaz przepisów dla LAMELI: pkt 3.6. |
| R8-47 | Część opisowa PZT zawiera też informacje o ograniczeniach z aktów prawa miejscowego (MPZP), rejestrze lub ewidencji zabytków, terenie górniczym oraz „charakterze, cechach istniejących i przewidywanych **zagrożeń dla środowiska** oraz higieny i zdrowia”. | RPB § 14 pkt 5 lit. a–d | jw. | TAK | Hałas pompy ciepła, wody opadowe i drzewa należą do pkt 5 lit. d. |

### 2F. Środowisko: drzewa, hałas, wody, grunty rolne, OOŚ

| ID | Wymaganie | Podstawa | URL | pierwotne? | Uwagi |
|---|---|---|---|---|---|
| R8-48 | **Bez zezwolenia** usuwa się m.in.:<br>• drzewa o obwodzie pnia na wysokości 5 cm **≤ 80 cm** (topole, wierzby, klon jesionolistny, klon srebrzysty), **≤ 65 cm** (kasztanowiec zwyczajny, robinia akacjowa, platan klonolistny), **≤ 50 cm** (pozostałe gatunki) — pkt 3;<br>• drzewa i krzewy na nieruchomościach **osób fizycznych** usuwane **na cele niezwiązane z działalnością gospodarczą** — pkt 3a;<br>• krzewy w skupisku do 25 m²;<br>• drzewa owocowe (poza terenami zabytkowymi i zieleni). | u.o.p. art. 83f ust. 1 pkt 1, 3, 3a, 5 (t.j. Dz.U. 2026 poz. 13) | https://api.sejm.gov.pl/eli/acts/DU/2026/13/text.pdf | TAK | Zmiany 2026/426, 737 i 912 nie dotyczą art. 83f (sprawdzono). |
| R8-49 | **Zgłoszenie** do wójta w przypadku z pkt 3a, gdy obwód na wysokości 5 cm **> 80 / 65 / 50 cm**. Zgłoszenie zawiera imię i nazwisko, oznaczenie nieruchomości i rysunek lub mapkę. Organ dokonuje **oględzin w 21 dni** i może wnieść **sprzeciw w 14 dni** od oględzin. Usunięcie jest możliwe po upływie terminu lub po zaświadczeniu. Po 6 miesiącach od oględzin trzeba zgłosić ponownie. | u.o.p. art. 83f ust. 4–8, 12, 13; art. 83a ust. 1 | jw. | TAK | Ust. 17 (opłata przy budowie związanej z działalnością gospodarczą w 5 lat) **nie dotyczy** domu jednorodzinnego inwestora prywatnego. |
| R8-50 | **Prace w obrębie korzeni, pnia lub korony** drzew pozostawianych prowadzi się „w sposób najmniej szkodzący drzewom”. Usunięcie gałęzi ponad 30% korony jest zabronione (z wyjątkami), ale **zakaz z ust. 2 nie dotyczy drzew, o których mowa w art. 83f ust. 1** (ust. 6) — m.in. drzew na nieruchomości osoby fizycznej usuwanych na cele niegospodarcze (pkt 3a) i drzew poniżej progów obwodu (pkt 3). | u.o.p. art. 87a ust. 1–2, 6 | jw. | TAK | PZT: oznaczyć drzewa do zachowania i strefy ochronne; przyłącza prowadzić poza rzutem koron. |
| R8-51 | **Dopuszczalne poziomy hałasu** (tab. 1, lp. 2 lit. a, „tereny zabudowy mieszkaniowej jednorodzinnej”):<br>• „pozostałe obiekty i działalność będąca źródłem hałasu”: **L_Aeq,D = 50 dB** („8 najmniej korzystnym godzinom dnia kolejno po sobie następującym”), **L_Aeq,N = 40 dB** („1 najmniej korzystnej godzinie nocy”);<br>• drogi i koleje: 61 / 56 dB. | rozp. MŚ z 14.06.2007, zał. tab. 1 (t.j. Dz.U. 2014 poz. 112) | https://api.sejm.gov.pl/eli/acts/DU/2014/112/text.pdf | TAK | Akt obowiązuje. Ostatnia zmiana: Dz.U. 2012 poz. 1109 (ujęta w t.j.). Metadane ELI: brak późniejszych zmian i uchylenia. |
| R8-52 | **Pora dnia: 6:00–22:00, pora nocy: 22:00–6:00** (dla L_Aeq,D i L_Aeq,N). Rodzaje terenów chronionych przypisuje się **według MPZP** (art. 114). Bez planu decyduje faktyczne zagospodarowanie (art. 115). | POŚ art. 112a pkt 1 lit. b; art. 113 ust. 2 pkt 1; art. 114 ust. 1–2; art. 115 (t.j. Dz.U. 2025 poz. 647) | https://api.sejm.gov.pl/eli/acts/DU/2025/647/text.pdf | TAK | Sąsiedzi E i W (MN) są chronieni akustycznie. Teren rolny na południu nie jest (R, nie z art. 113 ust. 2 pkt 1). |
| R8-53 | **Pompa ciepła to „instalacja”** („stacjonarne urządzenie techniczne (…), którego eksploatacja może spowodować emisję”). Jej eksploatacja „nie powinna (…) powodować przekroczenia standardów jakości środowiska **poza terenem, do którego prowadzący instalację posiada tytuł prawny**”. | POŚ art. 3 pkt 6 lit. a; art. 144 ust. 1–2 | jw. | TAK | Cel projektowy: ≤ 40 dB w nocy na granicy działki (pkt 3.4). |
| R8-54 | **Pompa ciepła nie wymaga zgłoszenia instalacji.** Rozporządzenie o instalacjach wymagających zgłoszenia obejmuje m.in. przydomowe oczyszczalnie ścieków ≤ 5 m³/d, instalacje wytwarzające pole elektromagnetyczne i część instalacji emitujących do powietrza. Emisji hałasu z pomp ciepła nie wymienia. | rozp. MŚ z 2.07.2010, § 2 (t.j. Dz.U. 2019 poz. 1510) | https://api.sejm.gov.pl/eli/acts/DU/2019/1510/text.pdf | TAK | |
| R8-55 | **Wody opadowe lub roztopowe** to „wody będące skutkiem opadów atmosferycznych” (pkt 69). Nie są ściekami: definicja ścieków w pkt 61 ich nie obejmuje. **Urządzenia wodne** obejmują m.in. „wyloty służące do wprowadzania wody do wód, **do ziemi** lub do urządzeń wodnych” (pkt 65 lit. f). | PW art. 16 pkt 61, 65 lit. f, 69 (t.j. Dz.U. 2025 poz. 960) | https://api.sejm.gov.pl/eli/acts/DU/2025/960/text.pdf | TAK | Podstawa niejednoznaczności wodnoprawnej rozsączania (R8-R3). |
| R8-56 | **Pozwolenie wodnoprawne** jest wymagane m.in. na usługi wodne, szczególne korzystanie z wód i **wykonanie urządzeń wodnych** (art. 389 pkt 1, 2, 6). Usługą wodną jest odprowadzanie wód opadowych ujętych w **systemy kanalizacji deszczowej do wód lub urządzeń wodnych** (art. 35 ust. 3 pkt 7). Katalog zwolnień (art. 395) **nie obejmuje** rozsączania wód opadowych z domów jednorodzinnych. Zgłoszenia wodnoprawnego wymaga m.in. wykonanie urządzeń do wprowadzania do ziemi ścieków oczyszczonych z przydomowej oczyszczalni (art. 394 ust. 1 pkt 13), ale nie wód opadowych. | PW art. 35 ust. 3 pkt 7; art. 389 pkt 1, 2, 6; art. 394 ust. 1; art. 395 | jw. | TAK | Zob. R8-57 i R8-R3. |
| R8-57 | Według PGW Wody Polskie szczelny zbiornik na wody opadowe **nie jest urządzeniem wodnym**, a korzystanie z wody z takiego zbiornika nie wymaga zgody wodnoprawnej. Źródła wtórne zgodnie podają, że Wody Polskie uznają studnie chłonne i urządzenia rozsączające za urządzenia wodne. Praktyka jest niejednolita. | FAQ PGW Wody Polskie (gov.pl); omówienia branżowe | https://www.gov.pl/web/wody-polskie/faq ; https://creati-pro.pl/blog-post-2 | NIE | Stanowisko Wód Polskich w sprawie rozsączania: NIEZWERYFIKOWANE u źródła. Zob. pkt 3.5. |
| R8-58 | **Zakazy dotyczące spływu:** właściciel gruntu nie może „zmieniać kierunku i natężenia odpływu znajdujących się na jego gruncie wód opadowych lub roztopowych (…) – ze szkodą dla gruntów sąsiednich” ani „odprowadzać wód oraz wprowadzać ścieków na grunty sąsiednie”. Wójt może nakazać przywrócenie stanu poprzedniego (ust. 3). | PW art. 234 ust. 1–3 | jw. | TAK | Niwelacja: spadki od budynku do ogrodu i urządzeń retencyjnych, bez spływu na E, W i S. |
| R8-59 | **Opłata za zmniejszenie naturalnej retencji terenowej** (szczególne korzystanie z wód) dotyczy nieruchomości **> 3500 m²** z robotami lub obiektami, które wyłączają **> 70%** powierzchni z PBC, na obszarach nieujętych w systemy kanalizacji. | PW art. 34 pkt 4; art. 269 ust. 1 pkt 1; art. 272 ust. 8 | jw. | TAK | Nowelizacja Dz.U. 2026 poz. 1156 (od 1.01.2027) nie zmienia progów (sprawdzono). **LAMELA (1600 m²) nie podlega opłacie.** |
| R8-60 | **Pozwolenie wodnoprawne na nowy obiekt budowlany na obszarze szczególnego zagrożenia powodzią.** | PW art. 390 ust. 1 pkt 1 lit. b | jw. | TAK | LAMELA leży poza takim obszarem (fikcja z briefu). Na realnej działce sprawdzić mapy zagrożenia powodziowego. |
| R8-61 | **Decyzja o wyłączeniu gruntów z produkcji rolnej** jest wymagana dla użytków rolnych klas I, II, III, IIIa, IIIb oraz klas IV–VI pochodzenia organicznego. Wydaje się ją **przed PnB** i **dołącza do wniosku** o PnB. | u.o.g.r.l. art. 11 ust. 1, 4, 4a (t.j. Dz.U. 2024 poz. 82) | https://api.sejm.gov.pl/eli/acts/DU/2024/82/text.pdf | TAK | Zmiany 2026/781, 875 i 1155 nie dotyczą art. 11 (sprawdzono). Dla użytków IV–VI mineralnych decyzja nie jest wymagana. |
| R8-62 | **Brak należności i opłat rocznych** przy wyłączeniu „na cele budownictwa mieszkaniowego: do **0,05 ha** w przypadku budynku jednorodzinnego”. | u.o.g.r.l. art. 12a pkt 1 | jw. | TAK | Zwolnienie z opłat nie zwalnia z decyzji. |
| R8-63 | **Zabudowa mieszkaniowa objęta MPZP** jest przedsięwzięciem mogącym potencjalnie znacząco oddziaływać na środowisko dopiero od **powierzchni zabudowy ≥ 2 ha** (formy ochrony przyrody i otuliny) lub **≥ 4 ha** (pozostałe obszary). „Powierzchnia zabudowy” obejmuje tu także teren przekształcany. Garaże i parkingi: **≥ 0,5 / 1,0 ha** powierzchni użytkowej (pkt 58 lit. a/b w brzmieniu Dz.U. 2023 poz. 1724 § 1 pkt 3; wcześniej 0,2/0,5 ha). PV na dachach i elewacjach jest wyłączona z pkt 54a. | rozp. RM z 10.09.2019, § 1 ust. 2 pkt 2, § 3 ust. 1 pkt 55 lit. a, pkt 58, pkt 54a (Dz.U. 2019 poz. 1839; zm. 2022 poz. 1071, 2023 poz. 1724; 2026 poz. 706, 1185) | https://api.sejm.gov.pl/eli/acts/DU/2019/1839/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2026/1185/text.pdf | TAK | **LAMELA nie wymaga DŚU.** Zmiany z 2026 r. dotyczą elektrowni wiatrowych i dróg. |

---

## 3. Implikacje dla projektu „Dom LAMELA”

### 3.1 Fikcyjny MPZP (uchwała XII/123/2024, teren 3MN): doprecyzować przed PZT
Plan jest fikcyjny, więc należy go uzupełnić tak, aby nie było wątpliwości interpretacyjnych (R8-07, R8-09).

1. **Reżim definicji.** Do uchwały dodać § „Definicje”. Proponowane brzmienie: „Ilekroć w uchwale jest mowa o powierzchni biologicznie czynnej, udziale PBC, wysokości zabudowy, nadziemnej intensywności zabudowy, powierzchni kondygnacji, kondygnacji nadziemnej i udziale powierzchni zabudowy — należy przez to rozumieć pojęcia z art. 2 pkt 28–35 upzp”. Dopisać, że do planu stosuje się art. 67 ust. 3 pkt 1 u.zm.upzp (wystąpienie o opinie po 24.09.2023).
2. **Wskaźniki według art. 15 ust. 2 pkt 6 upzp:**
   - maksymalny udział powierzchni zabudowy 30%;
   - minimalny udział PBC 50%;
   - **nadziemna** intensywność zabudowy min. 0,05, maks. 0,80;
   - maksymalna wysokość zabudowy 11,0 m;
   - do 3 kondygnacji nadziemnych;
   - min. 2 miejsca do parkowania na lokal (w tym w garażu).
3. **Nieprzekraczalna linia zabudowy: 6,0 m od linii rozgraniczającej 1KDD.** Definicja w planie: linii nie może przekroczyć zewnętrzne lico ścian budynku. Wysunięcie do 1,5 m dopuszcza się dla: okapów, gzymsów, wysuniętych płyt stropowych i dachowych, zadaszeń nad wejściem, schodów zewnętrznych, pochylni i balkonów. **Zalecenie projektowe: żaden element LAMELI (także zadaszenie wejścia i płyty) nie przekracza linii 6,0 m.** Wtedy zgodność nie zależy od definicji.
4. Południowy sąsiad to **teren rolny R, nie las**. Uniknie się wymagań § 271 ust. 8–8a WT.

### 3.2 Parametry do sprawdzenia w PZT (wartości graniczne)

| Parametr | Wartość graniczna dla działki 1600,00 m² | Podstawa |
|---|---|---|
| Powierzchnia zabudowy (art. 2 pkt 35 upzp; równolegle RPB § 14 pkt 4 lit. a i PN-ISO 9836) | **≤ 480,00 m²** | MPZP, R8-06 |
| PBC | **≥ 800,00 m²** | MPZP, R8-01, R8-02 |
| Suma powierzchni kondygnacji nadziemnych | **80,00 … 1280,00 m²** | MPZP, R8-04 |
| Wysokość zabudowy (od średniej min./maks. rzędnej terenu na obwodzie ścian do najwyższego punktu attyki) | **≤ 11,00 m** | MPZP, R8-03 |
| Wysokość budynku według WT § 6 | wykazać osobno; grupa **N** | R8-29 |
| Liczba kondygnacji nadziemnych | 3 | MPZP |
| Miejsca postojowe | ≥ 2 (garaż) + 1–2 gościnne na podjeździe | MPZP, R8-23 |

Uwagi do obliczeń:
- **Powierzchnię zabudowy liczyć zachowawczo**: pełny rzut wszystkich ścian zewnętrznych, w tym wspornika bryły A na P2 i boksu C. W wariancie kontrolnym doliczyć także wysunięte płyty. Margines jest duży: szacunkowo 230–300 m² wobec 480 m².
- **PBC liczyć bez nawierzchni ażurowych i bez terenu nad skrzynkami rozsączającymi.** Dach zielony garażu (≥ 10 m², 50%) traktować jako rezerwę, nie jako podstawę spełnienia wskaźnika.
- **Wysokość:**
  - ±0,00 = 101,65 m n.p.m. leży ok. 0,30 m ponad średni teren;
  - do wysokości wlicza się attyki, balustrady i ewentualne konstrukcje PV (wyłączenia z art. 2 pkt 30 są zamknięte);
  - rezerwa ≥ 0,30 m, czyli najwyższy punkt ≤ 10,70 m ponad średnią rzędną terenu;
  - **PV nie wystaje ponad attykę**, a klapa lub wyłaz jest zlicowany.

### 3.3 Usytuowanie na działce (odległości; zapis wymiarów z dokładnością 0,01 m, RPB § 15 ust. 3 — zob. R2)
- **Granice E i W:**
  - ściany z oknami **≥ 4,00 m**, wymiarowane osobno dla każdej płaszczyzny uskoku ściany (WT § 12 ust. 1 i zał. 1a w brzmieniu Dz.U. 2024 poz. 726); zalecane ≥ 4,50 m, aby zachować zapas na tolerancję wytyczenia i uniknąć § 31 rozp. standardów;
  - ściany bez otworów ≥ 3,00 m;
  - okapy, wysunięte płyty, taras naziemny, schody zewnętrzne i daszek nad wejściem **≥ 1,50 m** (WT § 12 ust. 1, 6).
- **Budżet szerokości:** szerokość działki 32,00 m minus rozpiętość brył (ok. 20–21 m łącznie ze wspornikiem A na zachód) daje ok. 11 m na dwa odstępy boczne. Proponowane: ~5,5 m na W i ~5,5 m na E. Wymiary ostateczne przyjąć w modelu `model/dzialka.yaml`.
- **Granica N (droga):** lico ścian **≥ 6,00 m** od linii rozgraniczającej (MPZP). Daje to też ≥ 6 m od krawędzi jezdni (u.d.p. art. 43). Odległości WT § 12 od granicy z działką drogową nie obowiązują (§ 12 ust. 10).
- **Miejsca gościnne** 2,50 × 5,00 m, **≥ 3,00 m od granic E i W** (WT § 19 ust. 2). Dopuszczalne przy granicy z 1KDD (§ 19 ust. 7). Podjazd **≥ 3,00 m**, zalecane 5,0–6,0 m przed garażem.
- **Odpady:** osłona lub wiata na pojemniki (segregacja) przy furtce. Odległości nie są normowane dla zabudowy jednorodzinnej (WT § 23 ust. 4). Utwardzone dojście do drogi.
- **Ogrodzenie:** od drogi ażurowe, ≤ 1,60 m (MPZP). Brama przesuwna ≥ 2,40 m w świetle (zalecane ≥ 4,0 m dla dwóch samochodów). Furtka ≥ 0,90 m otwierana do wewnątrz. Brak ostrych zakończeń poniżej 1,8 m (WT § 41–43). Złącze kablowo-pomiarowe we wnęce ogrodzenia.
- **Sprawdzić przesłanianie i nasłonecznienie** dla okien sąsiadów E i W (WT § 13, § 60). Budynki sąsiadów stoją ≥ 8 m od granic, a LAMELA ≥ 4,5 m, więc dystans wynosi ≥ 12,5 m przy wysokości przesłaniania ≤ ~10 m. Wynik obliczeń podać w informacji o OO.

### 3.4 Hałas pompy ciepła (jednostka zewnętrzna)
- **Kryterium:** L_Aeq,N ≤ **40 dB** i L_Aeq,D ≤ **50 dB** na granicy działek sąsiednich E i W (MN). Wymóg dotyczy terenu poza działką inwestora (POŚ art. 144 ust. 2).
- **Cel projektowy (zapas 5 dB):** ≤ 35 dB(A) na granicy nocą, w trybie cichym.
- Szacunek inżynierski (półprzestrzeń, nie przepis): L_p ≈ L_WA − 20·log r − 8 dB, plus 3 dB przy ścianie. Przykład: L_WA nocne ≤ 55 dB(A) i r ≥ 6 m dają ≈ 32–35 dB(A).
- **Lokalizacja:** nie w narożniku wklęsłym, nie pod oknami sypialni. Proponowana: przy ścianie północnej lub wschodniej garażu, **≥ 6,0 m od granicy E**. Posadowienie na fundamencie z podkładkami antywibracyjnymi. W części opisowej PZT (RPB § 14 pkt 5 lit. d) podać L_WA z karty urządzenia i obliczenie na granicy.
- Pompa ciepła nie wymaga zgłoszenia instalacji (R8-54) ani DŚU.

### 3.5 Wody opadowe (MPZP: zagospodarowanie na działce, zakaz odprowadzania na drogę)
- **Bilans i retencja:** obliczyć spływ z dachów, podjazdu i tarasu. Nie ma normatywnego deszczu obliczeniowego dla domów jednorodzinnych. Przyjąć założenie projektowe (NIEZWERYFIKOWANE jako przepis) i podać je w opisie.
- **Rozwiązanie o najniższym ryzyku prawnym:**
  1. **Szczelny zbiornik retencyjny** (np. 5 m³ do podlewania). Nie jest urządzeniem wodnym (R8-57). Zbiornik bezodpływowy ≤ 5 m³ nie wymaga PnB ani zgłoszenia (R1-36), ale ujmujemy go w PZT.
  2. **Przelew** na własny teren nieutwardzony: niecka lub ogród deszczowy o głębokości ≤ 0,3 m w trawniku, wprost na podstawie WT § 28 ust. 2.
  3. **Skrzynki rozsączające** tylko jako uzupełnienie. **Przed złożeniem wniosku uzyskać stanowisko PGW Wody Polskie** (Zarząd Zlewni lub RZGW właściwy dla gminy), czy wylot do ziemi wymaga pozwolenia wodnoprawnego (PW art. 16 pkt 65 lit. f, art. 389 pkt 6). Pozwolenie nie jest załącznikiem do wniosku o PnB z mocy PB, ale jest potrzebne przed wykonaniem urządzenia.
- **Odległości skrzynek i niecek nie są normatywne.** Założenia projektowe (wytyczne, NIE przepis): ≥ 2,0 m od granic działki (ochrona z PW art. 234), ≥ 3,0 m od fundamentów budynku z izolacją przeciwwodną, ≥ 1,0 m od koron i pni drzew pozostawianych. Dno ≥ 1,0 m nad zwierciadłem wody gruntowej, które leży ok. 3,8 m p.p.t. (warunek praktyki projektowej, np. DWA-A 138: NIEZWERYFIKOWANE).
- **Podjazd:** spadek ku działce, odwodnienie liniowe przed bramą (u.d.p. art. 39 ust. 1 pkt 9; zakaz z MPZP). **Niwelacja:** spadki ≥ 2% od budynku. Na granicach E, W i S rzędne projektowane równe istniejącym (PW art. 234, WT § 29).
- **Opłata za zmniejszenie retencji nie dotyczy** działki (1600 m² < 3500 m²).

### 3.6 Obszar oddziaływania: wykaz przepisów do PZT (RPB § 18)
Jeżeli LAMELA spełnia wszystkie wartości z pkt 3.3–3.5, PZT stwierdza: „Obszar oddziaływania obiektu mieści się w całości na działce nr 123/4”. Podstawę stanowią:
- WT § 12, 13, 19, 23, 28–29, 60, 271 (stosowane na podstawie art. 102a PB);
- u.d.p. art. 43;
- POŚ art. 144 ust. 2 wraz z rozp. MŚ z 14.06.2007 (Dz.U. 2014 poz. 112);
- PW art. 234;
- ustalenia MPZP (uchwała XII/123/2024).

### 3.7 Drzewa, grunty rolne, OOŚ: decyzje dla fikcyjnej działki
- **Drzewa:**
  - mapa do celów projektowych pokazuje zieleń wysoką (R8-37);
  - przyjąć: brak drzew do usunięcia albo drzewa owocowe lub o obwodach poniżej progów;
  - jeżeli drzewo przekracza 50/65/80 cm obwodu, **zgłoszenie z art. 83f ust. 4 u.o.p.** (inwestor jest osobą fizyczną, cel nie jest gospodarczy);
  - drzewa przydrożne w pasie 1KDD nie są usuwane; zjazd lokalizować poza ich koronami (u.d.p. art. 39 ust. 1 pkt 12).
- **Grunty rolne:** przyjąć, że w EGiB działka to grunt orny **RIVb lub RV pochodzenia mineralnego**. Wtedy **decyzja o wyłączeniu nie jest wymagana** (u.o.g.r.l. art. 11 ust. 1). W wariancie z klasą IIIa/IIIb decyzję trzeba uzyskać przed PnB i dołączyć do wniosku; opłaty nie ma do 0,05 ha (art. 12a).
- **OOŚ:** DŚU nie jest wymagana (R8-63). W opisie PZT i PAB: „Przedsięwzięcie nie jest przedsięwzięciem mogącym znacząco oddziaływać na środowisko w rozumieniu rozporządzenia RM z 10.09.2019 (Dz.U. 2019 poz. 1839 ze zm.)”. Działka poza formami ochrony przyrody i obszarami Natura 2000 (fikcja; na realnej działce sprawdzić w GDOŚ).

### 3.8 Lista kontrolna PZT (część rysunkowa i opisowa): zakres R8
Zakres formalny (strona tytułowa, oświadczenia, nazewnictwo plików) jest w **R2**. Poniżej pozycje merytoryczne tej domeny.

**Dane wejściowe**
- [ ] Mapa do celów projektowych 1:500 z klauzulą urzędową albo oświadczeniem geodety (PB art. 34b; PGiK art. 12b ust. 5a–5c).
- [ ] Opis mapy według § 33 rozp. standardów; układ PL-2000 i PL-EVRF2007-NH.
- [ ] Na mapie: zieleń wysoka, krawędź jezdni 1KDD, uzbrojenie, rzędne terenu (R8-32…R8-38).
- [ ] Wypis i wyrys z MPZP 3MN.
- [ ] Informacja o klasach gruntów z EGiB (R8-61).
- [ ] Oświadczenie inwestora z art. 102a PB (R8-17).

**Rysunek PZT**
- [ ] Granice działki, północ, sąsiedztwo.
- [ ] **Linia rozgraniczająca 1KDD i nieprzekraczalna linia zabudowy 6,00 m**, zwymiarowana (RPB § 15 ust. 2 pkt 4).
- [ ] Obrys budynku; oddzielnie rzut ścian P0 i obrys brył P1/P2 (wspornik A, boks C) oraz obrysy wysuniętych płyt linią przerywaną.
- [ ] Wymiary do granic z dokładnością 0,01 m: ściany ≥ 4,00 m; okapy, płyty i taras ≥ 1,50 m (R8-18, R8-19).
- [ ] Liczba kondygnacji, wejścia, wjazd.
- [ ] Rzędne: ±0,00 = 101,65 m n.p.m., teren istniejący i projektowany, spadki.
- [ ] Zjazd (szerokość według zezwolenia), podjazd ≥ 3,00 m, miejsca gościnne 2,50 × 5,00 m (≥ 3,00 m od granic E i W), dojście do furtki.
- [ ] Miejsce na odpady, ogrodzenie (≤ 1,60 m od drogi), brama ≥ 2,40 m, furtka ≥ 0,90 m.
- [ ] Taras naziemny (≤ 35 m², jeśli ma być wolny od zgłoszenia — R1-36), pompa ciepła (≥ 6,0 m od granicy E), złącze nN.
- [ ] Przyłącza wod-kan i nN oraz teletechnika.
- [ ] Wody opadowe: rury spustowe, zbiornik, przelew, niecka lub skrzynki ze spadkami, średnicami, rzędnymi i odległościami (RPB § 15 ust. 2 pkt 11).
- [ ] Zieleń istniejąca, do usunięcia i projektowana, z drzewami zachowywanymi i strefami ochronnymi (R8-50).
- [ ] Najbliższy hydrant i dojście od drogi publicznej (dane ppoż. według R2 i domeny ppoż.).
- [ ] Legenda z objaśnieniem znaków spoza mapy zasadniczej (rozp. standardów § 32 ust. 3).

**Część opisowa PZT (RPB § 14)**
- [ ] Przedmiot zamierzenia i stan istniejący.
- [ ] Projektowane zagospodarowanie: urządzenia budowlane, ścieki do sieci, komunikacja i zjazd, dostęp do drogi publicznej, parametry przyłączy, ukształtowanie terenu i zieleń.
- [ ] **Zestawienie powierzchni i wskaźników MPZP** (tabela 3.2), z metodą liczenia według art. 2 pkt 28–35 upzp i RPB § 14 pkt 4.
- [ ] Ograniczenia z MPZP; zabytki (brak); teren górniczy (brak).
- [ ] Zagrożenia dla środowiska i zdrowia: hałas pompy ciepła z obliczeniem, wody opadowe, drzewa, brak DŚU, wyłączenie gruntów (nie dotyczy lub decyzja).
- [ ] Dane ppoż.
- [ ] Informacja o OO z wykazem przepisów (pkt 3.6).

**Załączniki do wniosku (zakres R8)**
- [ ] Zezwolenie zarządcy drogi na lokalizację zjazdu (u.d.p. art. 29 ust. 3a).
- [ ] Ewentualnie decyzja o wyłączeniu gruntów (u.o.g.r.l. art. 11 ust. 4a).
- [ ] Ewentualnie zgoda z art. 43 ust. 2a u.d.p. (nie dotyczy przy ≥ 6 m).

---

## 4. Nierozstrzygnięte / ryzyka

| ID | Kwestia | Status | Działanie |
|---|---|---|---|
| R8-R1 | **Reżim definicji wskaźników MPZP.** Czy do fikcyjnego MPZP z 21.03.2024 stosuje się art. 2 pkt 28–35 upzp, zależy od daty wystąpienia o opinie i uzgodnienia (art. 67 ust. 3 pkt 1 u.zm.upzp). W realnej gminie trzeba to ustalić z dokumentacji planistycznej. | Do ustalenia (fikcja) | Wpisać definicje do fikcyjnego MPZP (pkt 3.1). Liczyć wskaźniki w obu ujęciach (upzp i RPB z PN-ISO 9836). |
| R8-R2 | **Stosowanie WT** zależy od oświadczenia z art. 102a PB. Bez niego nie ma aktu wykonawczego z odległościami (R1). | Rozstrzygnięte warunkowo | Oświadczenie złożyć razem z wnioskiem. Termin: 18 miesięcy od 20.09.2026. |
| R8-R3 | **Rozsączanie wód opadowych w ziemi:** czy wylot lub skrzynki to urządzenie wodne wymagające pozwolenia wodnoprawnego (art. 16 pkt 65 lit. f i art. 389 pkt 6 PW, brak zwolnienia w art. 395). Źródła wtórne są sprzeczne, a artykułu naukowego (ejournals.eu) nie udało się pobrać (HTTP 503). | **NIEZWERYFIKOWANE** | Rozwiązanie z pkt 3.5 (zbiornik szczelny + powierzchniowe rozsączanie na podstawie WT § 28 ust. 2). Przed realizacją skrzynek uzyskać stanowisko PGW WP. |
| R8-R4 | **Normatywne odległości urządzeń rozsączających** od budynków i granic nie istnieją. Wartości 2 m / 5 m z poradników i instrukcji producentów nie mają podstawy prawnej. Wytyczne DWA-A 138 nie zostały zweryfikowane. | NIEZWERYFIKOWANE (wytyczne) | Przyjąć wartości zachowawcze z pkt 3.5 jako założenia projektanta, z uzasadnieniem technicznym. |
| R8-R5 | **Wysokość zabudowy (art. 2 pkt 30 upzp):** nie wiadomo, czy „poziom terenu” to teren istniejący, czy projektowany. Wyłączenia są zamknięte (PV, balustrady i wyłaz nie są wyłączone). | Interpretacyjne | Liczyć od niższej z rzędnych (istniejąca/projektowana), wliczać wszystkie elementy nadachowe. Rezerwa ≥ 0,30 m. |
| R8-R6 | **„Teren zabudowy” w art. 43 u.d.p.** (6 m vs 15 m od krawędzi jezdni) to pojęcie autonomiczne (NSA II OSK 2184/14, źródło wtórne). W terenie MN z istniejącą zabudową obowiązuje 6 m. | Niskie ryzyko | Ewentualnie potwierdzić w postępowaniu o zezwolenie na zjazd. |
| R8-R7 | **Aktualność mapy do celów projektowych** nie ma terminu ustawowego. Wyrok NSA II OSK 909/14 znany tylko ze źródeł wtórnych (nie sprawdzono w CBOSA). | Źródło wtórne | Mapa możliwie świeża (≤ 12 miesięcy, praktyka). Przy zmianach w terenie aktualizacja. |
| R8-R8 | **Powierzchnia zabudowy według PN-ISO 9836:2022-07.** Treści normy nie weryfikowano (norma płatna). Nie wiadomo, czy wysunięte płyty i okapy 0,8–1,5 m wchodzą do powierzchni zabudowy (zob. R2 R-06). | NIEZWERYFIKOWANE | Liczyć wariant zachowawczy z płytami. Margines do 30% jest duży. |
| R8-R9 | **Numer pasa układu PL-2000 dla Poznania:** pas 6 (18°E) — zweryfikowano w weryfikacji niezależnej (rozp. PSOP t.j. Dz.U. 2024 poz. 342, § 13 ust. 2, § 22). | Rozstrzygnięte | Przyjąć zgodnie z mapą do celów projektowych (oznaczenie układu w opisie mapy, § 33 pkt 9 rozp. standardów). |
| R8-R10 | **Szczegóły metodyki pomiaru hałasu** (korekty tonalne i impulsowe, przepisy wydane na podstawie art. 147a POŚ) nie zostały sprawdzone. | NIEZWERYFIKOWANE | Zapas 5 dB w celu projektowym (pkt 3.4). |
| R8-R11 | **Wymiary zjazdu** (szerokość, łuki, przepust) nie mają wartości liczbowych w rozporządzeniu 2022/1518. Określi je decyzja zarządcy drogi. | Do uzyskania (fikcja) | W PZT pokazać zjazd „wg zezwolenia zarządcy drogi nr … (do uzupełnienia)” i założenie 5,00 m. |
| R8-R12 | **Gotowość do złożenia.** Wszystkie dane są fikcyjne: MPZP, mapa, EGiB, zezwolenie na zjazd, drzewa, stanowisko Wód Polskich. Projekt nie może zostać złożony bez rzeczywistych dokumentów (zob. R1, pkt 7). | Ograniczenie zadania | Pola do uzupełnienia w metryce projektu. |
| R8-R13 | **Reforma planistyczna trwa.** Kolejne zmiany terminów (np. 30.11.2026 dla Rejestru Urbanistycznego) nie wpływają na PnB przy MPZP, ale mogą zmienić dostęp do danych planistycznych. | Monitorować | Przed złożeniem sprawdzić ELI (nowe pozycje Dz.U. 2026 > 1244). |

---

## 5. Źródła

### 5.1 Pierwotne (API ELI Sejmu, `https://api.sejm.gov.pl/eli/acts/DU/…/text.pdf`)
- **Planowanie:**
  - upzp t.j. **2026/538**; zm. 2026/781, 2026/864, 2026/912;
  - u.zm.upzp **2023/1688**; brzmienie sprzed reformy: t.j. 2023/977;
  - rozp. MFiG **2026/1192** (projekt MPZP); rozp. MRiT 2021/2404 (uchylone 24.09.2026).
- **Prawo budowlane:** PB t.j. **2026/524**; ustawa **2025/1847** (definicje od 20.09.2026); ustawa **2026/1161** (art. 102a).
- **Warunki techniczne i projekt:** WT t.j. **2022/1225**, zm. **2023/2442**, 2024/474, **2024/726** (status w ELI: uznany za uchylony 21.09.2026); RPB t.j. **2022/1679**, zm. 2023/2405, **2026/597**.
- **PSOP:** rozp. RM z 15.10.2012, t.j. **2024/342**, zm. 2025/106.
- **Geodezja:**
  - PGiK t.j. **2024/1151**; zm. 2024/1824, 2025/1019, 2025/1542, 2025/1792;
  - rozp. standardów t.j. **2022/1670**;
  - rozp. BDOT500 i mapy zasadniczej **2021/1385**.
- **Drogi:** u.d.p. t.j. **2025/889**; zm. 2026/815, 2026/982; rozp. MI **2022/1518**, zm. 2025/1352.
- **Środowisko:**
  - u.o.p. t.j. **2026/13**; zm. 2026/426, 2026/737;
  - rozp. MŚ hałas t.j. **2014/112**;
  - POŚ t.j. **2025/647**; zm. 2025/1080, 2025/1812, 2025/1863, 2026/176, 605, 607, 635, 1157 (nie dotyczą art. 112a–115, 144);
  - rozp. MŚ o instalacjach wymagających zgłoszenia t.j. **2019/1510**;
  - PW t.j. **2025/960**; zm. 2025/1535, 2026/445, 605, 815, 1033, **1156**;
  - u.o.g.r.l. t.j. **2024/82**; zm. 2026/781, 2026/875, 2026/1155;
  - rozp. RM **2019/1839**; zm. 2022/1071, **2023/1724** (m.in. pkt 54a i progi pkt 58), 2026/706, 2026/1185.
- **Metadane ELI** (statusy, listy zmian): `https://api.sejm.gov.pl/eli/acts/DU/{rok}/{poz}`.

### 5.2 Wtórne
- Mazowiecka OIA, „Ważność mapy do celów projektowych” (NSA II OSK 909/14): https://mazowiecka.iarp.pl/?p=1807
- wodkangaz.com, „Ważność mapy do celów projektowych” (2026, praktyka): https://wodkangaz.com/waznosc-mapy-do-celow-projektowych/
- Dziennik Warto Wiedzieć, „«Teren zabudowy» a drogi publiczne – spojrzenie NSA” (II OSK 2184/14): https://wartowiedziec.pl/komunikacja-i-transport/31334-qteren-zabudowyq-a-drogi-publiczne-spojrzenie-nsa
- INLEGIS, „Odległość drogi od budynku – ważny wyrok NSA” (II OSK 1567/23, 16.12.2025): https://www.inlegis.pl/baza-wiedzy/plan-zagospodarowania-przestrzennego/odleglosc-drogi-od-budynku-wazny-wyrok-nsa/
- PGW Wody Polskie, FAQ (szczelny zbiornik na deszczówkę): https://www.gov.pl/web/wody-polskie/faq
- Creati-Pro, „Studnia chłonna a pozwolenie wodnoprawne w 2026 r.” (restrykcyjne stanowisko Wód Polskich, omówienie): https://creati-pro.pl/blog-post-2
- Prawo.pl (2014; **nieaktualne**, oparte na PW z 2001 r., nie stosować): https://www.prawo.pl/biznes/czy-wprowadzanie-do-wod-lub-do-ziemi-wod-opadowych-lub-roztopowych-z-dachu-budynku-jednorodzinnego-wymaga-pozwolenia-wodnoprawnego,216402.html

---

## 6. Weryfikacja niezależna (2026-09-25)

**Metoda.** Weryfikator niezależny pobrał ponownie z API ELI teksty (PDF → tekst) i metadane wszystkich aktów z sekcji 5.1 oraz wszystkich aktów zmieniających wydanych po tekstach jednolitych. Pliki są w `scratchpad/research/r8v/`. Sprawdzono statusy, daty wejścia w życie, listy „Akty zmieniające” aktów bazowych i brzmienie przywołanych jednostek redakcyjnych. Wykaz Dz.U. 2026 sprawdzono 25.09.2026: ostatnia pozycja to poz. 1244 (23.09.2026), a poz. 1245, 1246 i 1250 zwracają HTTP 404. Portal CBOSA (orzeczenia.nsa.gov.pl) był niedostępny (błąd SSL / HTTP 503).

### 6.1 Potwierdzone (źródło pierwotne, tekst aktu)
- **R8-CF01:** upzp art. 2 pkt 28–35, t.j. 2026/538. Brzmienia są dosłownie zgodne. Zmiany 2026/781 (art. 2 pkt 5a, 8g, 8h, 15 ust. 2d, 17, 20, 37ea–37ebb), 2026/864 (art. 53) i 2026/912 (art. 8e, 17, 38b) nie dotyczą pkt 28–35, art. 15 ust. 2 pkt 6 ani art. 15 ust. 4.
- **R8-CF02:** u.zm.upzp art. 67 ust. 1, 2 i ust. 3 pkt 1. Ust. 3 pkt 1 obejmuje dodatkowo art. 15 ust. 3 pkt 11–13, art. 16 ust. 1a i art. 17 pkt 6.
- **R8-CF03:** rozp. 2026/1192. § 11: wchodzi w życie 14 dni po ogłoszeniu (9.09.2026), czyli 24.09.2026. § 10 ust. 1 dotyczy planów z uchwałą o przystąpieniu podjętą przed tą datą. Zał. 1 zawiera MN, MNW, MNB i MNS; zał. 2 — linie 0,35 mm z trójkątem o boku 3 mm. W ELI 2021/2404 ma status „uznany za uchylony” od 24.09.2026. Doprecyzowano skale: dopuszczalna jest także 1:5000 (§ 3 ust. 3 pkt 3).
- **R8-CF04:** art. 65 ust. 1 u.zm.upzp: termin 31.08.2026 wprowadził art. 5 pkt 6 ustawy 2026/781, który wszedł w życie 30.06.2026 (art. 15 pkt 1). Potwierdzono też art. 67 ust. 1 u.zm.upzp i upzp art. 13a ust. 6 pkt 3.
- **R8-CF06:** WT § 28 ust. 2, § 29; PW art. 234 ust. 1; u.d.p. art. 39 ust. 1 pkt 9.
- **R8-CF07:** PW art. 34 pkt 4, art. 269 ust. 1 pkt 1, art. 272 ust. 8 (progi > 3500 m² i > 70%). Ustawa 2026/1156 dodaje tylko art. 16 pkt 69a, art. 34 pkt 14a i art. 269 ust. 1 pkt 3; progów nie zmienia.
- **R8-CF08:** PW art. 16 pkt 65 lit. f, art. 389 pkt 6, art. 394 ust. 1 pkt 13, art. 395. W katalogu art. 395 nie ma zwolnienia dla wód opadowych. Zmiany 2025/1535, 2026/445, 605 (art. 16 pkt 70), 815, 1033 i 1156 nie dotyczą tych przepisów.
- **R8-CF09:** rozp. MŚ, t.j. 2014/112, tab. 1 lp. 2 lit. a: 61/56 dB (drogi i koleje), 50/40 dB (pozostałe źródła). Jedyna zmiana to 2012/1109. POŚ: art. 112a pkt 1 lit. b (6–22 / 22–6), art. 114, art. 115, art. 144 ust. 2, art. 3 pkt 6. Zmiany POŚ po t.j. 2025/647 nie dotyczą tych przepisów.
- **R8-CF10:** rozp. 2019/1510 § 2 ust. 1–4. Jedyna zmiana to 2017/2390.
- **R8-CF11:** PGiK art. 2 pkt 7a, art. 12b ust. 5a–5c, art. 28b ust. 2; PB art. 3 pkt 14a, art. 27a pkt 1, art. 34 ust. 3 pkt 1, art. 34b; rozp. standardów § 8, 30–33 (jedyna zmiana to 2021/1304, ujęta w t.j.). § 31 mówi o granicy „nieruchomości”.
- **R8-CF13:** rozp. 2021/1385 § 10 ust. 2–3; zał. 4 rozdz. 1: znaki umowne dla skali 1:500, w innych skalach pomniejszane o 25%. W ELI brak aktów zmieniających.
- **R8-CF14:** u.d.p. art. 29 ust. 1, 3, 3a, 4, 5 i art. 29a. Rozp. 2022/1518 § 54–56 w brzmieniu 2025/1352 nie podaje liczbowej szerokości zjazdu. Zmiany u.d.p. 2026/815 (art. 20h/20i) i 2026/982 (art. 13, 13i, 13k, 13naa, 40a) nie dotyczą art. 29, 39, 40 ani 43.
- **R8-CF15:** u.d.p. art. 43 ust. 1: tabela lp. 3 lit. c (gminna) — 6 m / 15 m. Potwierdzono też ust. 2 i 2a oraz art. 39 ust. 1a i ust. 3.
- **R8-CF16:** u.o.p. art. 83f ust. 1 pkt 3 i 3a, ust. 4–8, 12, 13; art. 83a ust. 1. T.j. 2026/13 obejmuje już zmianę 2025/1673. Zmiany 2026/426 (art. 8g), 737 (art. 56, 110, 131a) i 912 (art. 3, 16, 23) nie dotyczą art. 83f.
- **R8-CF17:** u.o.g.r.l. art. 11 ust. 1, 1b, 4, 4a; art. 12a pkt 1 (0,05 ha). Zmiany: 2026/875 dotyczy art. 22, 2026/1155 — art. 20, 26 i 28; 2026/781 zmienia u.o.g.r.l. tylko pośrednio (art. 61a u.zm.upzp, art. 7 ust. 3).
- **R8-CF19:** RPB § 14 pkt 4 lit. a–d (lit. a w brzmieniu 2023/2405, z loggiami), pkt 5, pkt 8 oraz § 18.
- **R8-CF20:** upzp art. 15 ust. 4.
- **Pozostałe pozycje tabeli:** potwierdzono WT § 13, 14, 18, 19 (ust. 1–7), 21, 22, 23 (ust. 4 wyłącza tylko pkt 1 i 2 ust. 1), 26, 41–43, § 3 pkt 15 i 22, § 6, § 8 i § 60 (7:00–17:00). Potwierdzono § 271 ust. 1 (ZL–ZL: 8 m); w tych jednostkach redakcyjnych po t.j. nie było zmian. Art. 102a PB (Dz.U. 2026 poz. 1161 art. 2 pkt 4) obowiązuje od 2.09.2026, choć reszta ustawy od 2.10.2026. PB art. 3 pkt 24 i 26 obowiązują od 20.09.2026 (Dz.U. 2025 poz. 1847 art. 13 pkt 1).

### 6.2 Poprawione (było → jest)
1. **Progi OOŚ dla garaży i parkingów** (sekcja 1.8, R8-63, CF18): było „0,2/0,5 ha” → jest „**0,5/1,0 ha** powierzchni użytkowej”. Podstawa: rozp. RM Dz.U. 2023 poz. 1724, § 1 pkt 3 lit. b–c (od 13.09.2023); https://api.sejm.gov.pl/eli/acts/DU/2023/1724/text.pdf. Wniosek „DŚU nie jest wymagana” pozostaje bez zmian.
2. **WT § 12** (skróty, sekcja 1.2, R8-18, R8-19, pkt 3.3, CF05): było — brzmienie według samego t.j. 2022/1225, z „wyłącznie” ust. 2–4. Jest — brzmienie po zmianach:
   - Dz.U. 2023 poz. 2442: ust. 1–3, 6, 8, 10 (+ „publicznie dostępny plac”) i 11;
   - Dz.U. 2024 poz. 726, od 15.08.2024: każda płaszczyzna uskoku to osobna ściana; nowy **ust. 1a** (3–4 m przy ścianie nierównoległej, okno ≥ 4 m); ust. 10a i zał. 1a.
   
   Źródła: https://api.sejm.gov.pl/eli/acts/DU/2023/2442/text.pdf ; https://api.sejm.gov.pl/eli/acts/DU/2024/726/text.pdf. Wartości 4 m / 3 m / 1,5 m są bez zmian.
3. **R8-50 (u.o.p. art. 87a):** było — „usunięcie > 30% korony zabronione (z wyjątkami)”. Jest — dopisano ust. 6: zakaz nie dotyczy drzew z art. 83f ust. 1, m.in. pkt 3 i 3a; https://api.sejm.gov.pl/eli/acts/DU/2026/13/text.pdf.
4. **RPB — brak zmiany Dz.U. 2026 poz. 597** (od 19.05.2026) w skrótach i źródłach: dopisano. Zmiana dodała m.in. § 15 ust. 3 (dokładność 0,01 m, przy pełnych metrach 0,1 m) i § 14 pkt 6a (obiekty zbiorowej ochrony; nie dotyczy LAMELI); https://api.sejm.gov.pl/eli/acts/DU/2026/597/text.pdf.
5. **R8-38 / R8-R9 (pas PL-2000):** było „NIEZWERYFIKOWANE” → jest „pas 6 (18°E)”. Podstawa: rozp. RM w sprawie PSOP, t.j. Dz.U. 2024 poz. 342, § 13 ust. 2 i § 22; https://api.sejm.gov.pl/eli/acts/DU/2024/342/text.pdf. Długość geograficzna Poznania (~16,9°E) to dana ogólnogeograficzna.
6. **R8-10:** uzupełniono skale dopuszczalne o 1:5000 (rozp. 2026/1192 § 3 ust. 3 pkt 3).

### 6.3 Niemożliwe do weryfikacji na źródle pierwotnym
- **R8-CF12 / R8-34 (NSA II OSK 909/14, aktualność mapy):** dostępne tylko omówienia wtórne. Jedno z nich podaje datę 10.01.2018 i Poznań, co jest niespójne z sygnaturą NSA. Orzeczenia w CBOSA nie udało się otworzyć. Sama teza „brak ustawowego terminu ważności mapy” jest zgodna z tekstem PB i PGiK: żaden przepis nie określa takiego terminu.
- **R8-CF21 / R8-44a (NSA II OSK 2184/14, 24.05.2016, „teren zabudowy”):** sygnatura i data występują w wynikach wyszukiwania CBOSA, ale strona zwróciła HTTP 503. Treść tezy (teren z dominującą zabudową lub przeznaczony pod zabudowę w MPZP) potwierdzają tylko źródła wtórne (wartowiedziec.pl).
- **R8-57 (stanowisko Wód Polskich w sprawie rozsączania)**, **R8-R4 (DWA-A 138)**, **R8-R8 (PN-ISO 9836)** i **R8-R10 (metodyka hałasu)**: status bez zmian — NIEZWERYFIKOWANE.

