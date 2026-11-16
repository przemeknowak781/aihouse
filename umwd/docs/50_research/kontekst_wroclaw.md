# Kontekst Wrocławia – miasto, miejsce, klimat (dla budynku UMWD przy Moście Grunwaldzkim)

> Moduł: 50_research · Opracowano: 16.11.2026 · Status: rozpoznanie (etap badań)
>
> **Konwencja oznaczeń:**
> - **[Ź]** – fakt ze źródła (URL i data dostępu w § 9; dla publikacji naukowych: autorzy, rok, tytuł, czasopismo, DOI);
> - **[Ź-wt]** – fakt ze źródła wtórnego (portal, serwis dokumentacyjny, Wikipedia, fragment wyników wyszukiwania bez lektury pełnego tekstu);
> - **[D]** – dane policzone przez nas z oficjalnych danych źródłowych (IMGW, ISOK), z opisaną metodą;
> - **[O]** – obserwacja własna z materiałów konkursowych (zdjęcia M.10, F.17);
> - **WNIOSEK** – interpretacja lub rekomendacja projektowa.
>
> **Zakaz Inwestora:** pominięto wszelkie informacje o pracach nagrodzonych, wyróżnionych i konkurencyjnych w tym konkursie. Artykułów o wynikach nie otwierano. Strony o podwyższonym ryzyku sprawdzano filtrem (§ 9.4). Strony odrzucone i niedostępne wymieniono w § 9.4.
>
> **Powiązane opracowania (bez dublowania treści):** `docs/30_lokalizacja/historia.md` (historia kwartału, plan 1934, Most Grunwaldzki – chronologia), `docs/30_lokalizacja/konserwator.md` (DWKZ), `docs/30_lokalizacja/mpzp.md` (MPZP), `docs/50_research/elewacje_zasady.md` (teoria elewacji), `docs/50_research/wizualizacje_metodyka.md` (fotomontaże F.17).
>
> **Dane i rysunki wytworzone w tym module:**
> - `docs/50_research/data/klimat_wroclaw_normy_1991_2020.csv`;
> - `docs/50_research/data/roza_wiatrow_wroclaw_1991_2020.csv`;
> - `docs/50_research/img/roza_wiatrow_1991_2020.png`, `img/sciezki_slonca_teren.png`, `img/isok_mzp_teren.jpg`;
> - skrypty do odtworzenia wyników: `docs/50_research/data/skrypty/` (uruchamiać `python3 -I`; dane wejściowe pobierać z danepubliczne.imgw.pl do osobnego katalogu).

---

## 0. Synteza (najważniejsze ustalenia i wnioski)

1. **Wrocławska polityka wysokościowa przewiduje dominanty przy Placu Społecznym.**
   - [Ź] Studium z 2018 r. (projekt z 2017 r.) wymienia **Plac Społeczny** wśród czterech obszarów, w których mają powstawać „kompozycje wysokościowe” (Zakrzewska-Półtorak 2017, za Studium s. 124).
   - [Ź] Dominanty lokuje się m.in. „w bramach miasta”, „na zamknięciach osi widokowych” i przy węzłach komunikacyjnych.
   - WNIOSEK: dominanta do 45 m w obszarze A (MPZP 2010) jest spójna z długofalową polityką miasta. Przed Sądem trzeba ją uzasadnić **kompozycyjnie**: jako bramę przedmościa Mostu Grunwaldzkiego i zamknięcie osi z esplanady pl. Grunwaldzkiego. Wysokość sama w sobie nie jest argumentem.
2. **Nowy plan ogólny nie zmienia warunków konkursu.**
   - [Ź] Rada Miejska uchwaliła plan ogólny (wroclaw.pl, 26.08.2026). Zastępuje on Studium.
   - WNIOSEK: dla terenu nadal wiąże MPZP z 2010 r. Plan ogólny może jednak wpłynąć na przyszły MPZP dla Placu Społecznego (§ 2.4).
3. **Most Grunwaldzki zmieni wygląd w horyzoncie realizacji budynku.**
   - [Ź] Projekt remontu z odtworzeniem kopuł (hełmów) pylonów ma pozwolenie konserwatorskie (wroclaw.pl, 3.07.2025).
   - [Ź] Według wroclaw.pl z 22.01.2026 rozbiórka wschodniej estakady na pl. Społecznym ma się odbyć „w tym samym czasie, co remont Mostu Grunwaldzkiego”, i nie wcześniej niż w 2028 r.
   - [Ź] Pylony to murowany rdzeń ceglany oblicowany granitem. Obecnie mają ok. 20 m, a po odtworzeniu hełmów ok. 25,5 m.
   - [O] Stalowa konstrukcja mostu jest dziś pomalowana na **jasnoniebiesko**.
4. **Istniejące siedziby UMWD stoją w tym samym kwartale co działka.**
   - [Ź] Urząd mieści się przy Wybrzeżu Słowackiego 12–14 (siedziba główna), przy ul. Mazowieckiej 15 i 17 (budynki połączone łącznikami) oraz przy ul. Walońskiej 3–5.
   - [Ź] Deklaracja dostępności z 2021 r. wymienia bariery: „skomplikowana trasa dotarcia do budynków”, winda zewnętrzna uruchamiana przez ochronę, wejście od frontu Mazowieckiej 17 bez swobodnego dostępu do windy.
   - WNIOSEK: nowy budynek powinien porządkować cały zespół urzędu. Wspólny, czytelny adres i dostęp bez barier to mocny argument dla kryterium „dostępność i inkluzywność”.
5. **Lokalne nagrody premiują powściągliwość, czytelną bryłę i szlachetne materiały.**
   - [Ź] Jury i laureaci konkursu „Piękny Wrocław” cenią „elegancką w formie, o interesującej, ale czytelnej bryle, wykończoną bardzo dobrymi materiałami” realizację oraz „powściągliwość i elegancję”.
   - [Ź] Nowy Targ chwalono jako wzór, „jak bez arogancji można stawiać biurowce”: duża kubatura podzielona na moduły rozdzielone przeszklonymi patiami.
   - [Ź] W 2026 r. Grand Prix dostał Park Krzycki za adaptację do zmian klimatu i otwartą retencję.
   - [Ź] Grand Prix 2021 dostał klinkierowy hotel The Bridge nad Odrą (FORUM architekci).
   - WNIOSEK: lokalny „kanon” to umiar, podział dużej bryły na moduły, materiał mineralny i realna zieleń. Fajerwerki formy nie są w nim premiowane.
6. **Klimat (normy 1991–2020, IMGW, stacja Wrocław-Strachowice, obliczenie własne [D]).**
   - Średnia temperatura roczna **9,7 °C**. Lipiec 19,7 °C, styczeń 0,0 °C.
   - Roczny opad tylko **541 mm**; maksimum w lipcu (91 mm).
   - Usłonecznienie **ok. 1890 h/rok** (w latach 2011–2020 ok. 2040 h).
   - Średnia prędkość wiatru 3,1 m/s.
   - Liczba dni upalnych (Tmax ≥ 30 °C) wzrosła z 9,0/rok (1991–2005) do **19,0/rok (2016–2025)**.
   - Dni z przymrozkiem spadły ze 104 do 73.
   - Miejska wyspa ciepła w centrum: średnio +1,0 K, latem +2,4 K, maksymalnie do 9–10 K (Szymanowski i in. 2019).
7. **Wiatr.** [D] Przeważają kierunki **zachodnie**: W–WNW to łącznie 27,6% obserwacji, a NW 6,6%. Drugim ośrodkiem są kierunki ESE–SE (15,3%), co jest typowe dla przedpola Sudetów i Bramy Morawskiej. Wiatry silne (≥ 8 m/s) w **52%** wieją z sektora W.
   - WNIOSEK: elewacja od Mazowieckiej i otwartego pl. Społecznego jest najbardziej wystawiona na wiatr. Wejścia, tarasy i loggie dominanty lepiej sytuować od E/SE lub osłaniać.
8. **Słońce i orientacja elewacji (obliczenie NOAA [D]).**
   - Pierzeja od mostu jest zwrócona na **NNW (346°)**, od Oławy na **ENE (76°)**, od Mazowieckiej na **WSW (256°)**.
   - W dniu zdjęć F.17 (29.10, ok. 11:40–12:00, Słońce az 181–186°, wys. 25°) elewacje od mostu i od Oławy są **w cieniu**. Elewacja od Mazowieckiej dostaje światło skośne, ślizgowe.
   - Elewacja NNW dostaje bezpośrednie słońce tylko latem, rano i wieczorem: 21 czerwca ok. 20:00 CEST Słońce stoi na az 297°, wys. 8°.
   - Katedra na Ostrowie Tumskim leży na azymucie **332°** (0,75 km), czyli prawie na osi elewacji od mostu. Ślęża jest na azymucie 222° (36 km).
   - WNIOSEK: sala Sejmiku z dużym oknem na NNW miałaby widok na Ostrów Tumski i Odrę, równe światło północne, bez olśnienia i przegrzewania. To bardzo mocna narracja dla Sądu.
9. **Powódź.**
   - [D] Według usługi ISOK (MZP/MRP, stan na 16.11.2026) teren **nie leży** w obszarach zagrożenia Q10%, Q1% ani Q0,2%. Obszar Q0,2% dochodzi jednak do krawędzi nabrzeża Wybrzeża Słowackiego, kilka metrów od granicy działki.
   - [Ź] Opinia geotechniczna (M.05) stwierdza natomiast, że działki leżą „na obszarze narażonym na niebezpieczeństwo powodzi (rzeczne)” i w strefie podtopień od wód gruntowych (PIG).
   - [Ź] W 1997 r. estakada na pl. Społecznym stała pod wodą (podpis zdjęcia, wroclaw.pl).
   - WNIOSEK: projektować zachowawczo. Kondygnacje podziemne jako „biała wanna”. Krytyczne instalacje (rozdzielnie, serwerownia, agregat) powyżej terenu. Rampa garażu z progiem. Zawory przeciwzalewowe.
10. **Paleta kontekstu [O].**
    - W bezpośrednim otoczeniu dominują **jasne, ciepłe tynki i piaskowce**: Mazowiecka 17 (kremowa, z boniowanym cokołem i czerwoną dachówką) i gmach DUW (jasny tynk na murze ceglanym).
    - Kamienice Mazowiecka 19 i Wybrzeże Słowackiego 5 mają zszarzały, szarobeżowy tynk.
    - Granit pylonów i murów nabrzeży jest szarobrązowy.
    - Akcenty: czerwień dachówki i ceglany gotyk Ostrowa Tumskiego.
    - Kolorem „obcym” jest błękit stali mostu.
    - WNIOSEK: jasna, ciepła i matowa rodzina materiałów mineralnych. Granitowy cokół. Jeden ciepły akcent metaliczny lub ceramiczny w koronie dominanty. Bez ciemnego i niebieskawego szkła, które w cieniu na fotomontażach F.17 czyta się jako dziura.

---

## 1. Most Grunwaldzki (Kaiserbrücke, 1908–1910)

Pełna chronologia, autorstwo i rozbieżności źródeł są w `docs/30_lokalizacja/historia.md` § 3. Poniżej tylko fakty potrzebne do projektu i stan planów na 16.11.2026.

### 1.1 Fakty

| Temat | Ustalenie | Źródło |
|---|---|---|
| Typ i daty | Most wiszący przez Odrę; budowa 1908–1910, otwarcie 10.10.1910; od 6.09.1947 „Most Grunwaldzki” | [Ź-wt] pl.wikipedia (za: Biliszczuk i in. 2010); `historia.md` § 3.1 |
| Projektanci | Architektura: miejski radca budowlany **Richard Plüddemann**. Koncepcja konkursowa: M. Mayer i R. Weyrauch. Wykonawca: Beuchelt & Co. (Zielona Góra) | [Ź-wt] fotopolska.eu (opis z wynikami wyszukiwania); wroclaw.pl 2023; `historia.md` § 3.2 |
| Rejestr zabytków | A/1653/326/Wm z 15.10.1976 | [Ź-wt] fotopolska.eu; `historia.md` |
| **Pylony – materiał** | Elementy nośne „wsparte są na pylonach murowanych z cegły i oblicowanych granitem, o wysokości około 20 m” (opis rejestrowy cytowany przez fotopolska.eu). Przewodnik miejski pisze o „monumentalnych, granitowych pylonach”. Według pl.wikipedia zużyto ok. 2400 t granitu śląskiego | [Ź-wt] fotopolska.eu 1446371; [Ź] wroclaw.pl, trasa „Mosty i przeprawy” (PDF, wg wyników wyszukiwania); [Ź-wt] pl.wikipedia |
| Wysokość pylonów | Pierwotnie ok. 25,54 m. Po 1945 r. obniżone o ok. 5 m (obecnie ok. 20 m). Na rysunku M.11.F wierzchołek odtworzonego hełmu leży ok. 25,5 m nad chodnikiem (pomiar w `historia.md` § 3.2) | [Ź-wt] pl.wikipedia; [Ź] wroclaw.pl 3.07.2025; M.11.F |
| Kolor stali (stan obecny) | Kratownice, cięgna i wieszaki pomalowane na jasny, nasycony błękit. Granit pylonów jest ciepło szarobrązowy, z ciemnymi zaciekami | [O] M.10 (DJI_…0013, 0015, 0032, 0036), F.17.A/B |
| Plan remontu | 12.07.2023: przetarg ZDiUM na projekt. 2025: pozwolenie konserwatorskie dla projektu z **odtworzeniem kopuł pylonów**, latarni, nawierzchni i płaskorzeźb, „być może” z pierwotną kolorystyką; start „może to być rok 2027” | [Ź] wroclaw.pl 12.07.2023 i 3.07.2025 (za `historia.md`) |
| **Aktualizacja harmonogramu** | 22.01.2026 wroclaw.pl: rozbiórka wschodniej estakady na pl. Społecznym ma się odbyć „w tym samym czasie, co remont Mostu Grunwaldzkiego”, wstępnie w **2028 r.** i nie wcześniej. Remont mostu nastąpi po remoncie Mostu Pokoju, planowanym przez MPK na 2027 r. | [Ź] wroclaw.pl, B. Chochołowski, 22.01.2026; [Ź-wt] fragment wyników wyszukiwania (Most Pokoju 2027) |
| Inne źródło wtórne | „Prace mogą ruszyć w styczniu 2028 i potrwać do grudnia 2029” (nieoficjalnie) | [Ź-wt] cytowane w `elewacje_zasady.md` § 1.6 |

### 1.2 Wnioski (WNIOSEK)

- **Horyzont czasowy.** Remont mostu (2028–2029) i rozbiórka estakady zbiegną się z budową UMWD. W dniu oddania budynku most będzie najpewniej miał już hełmy, a przedmoście będzie przebudowane.
- **Co pokazać na wizualizacjach.** Na wizualizacjach obowiązkowych 1–2 (F.17) kontekst poza granicą opracowania studialnego musi zostać w stanie obecnym (Wyj. 9 odp. 61, por. `zdjecia_F17_metadane.md` § 0): most bez hełmów, niebieski, z estakadą. Organizator dołączył jednak rysunek M.11.F z hełmami, więc oczekuje świadomości tej zmiany. Sylwetę przyszłego portalu z hełmami (ok. 25,5 m) warto pokazać na **elewacji rozwiniętej / przekroju urbanistycznym** i w opisie, z dopiskiem „stan docelowy wg projektu remontu mostu”.
- **Relacja wysokościowa** (spójna z `konserwator.md` § 4):
  - gzyms skrzydeł ok. 21–22 m leży poniżej wierzchołka hełmu (ok. 25,5 m);
  - dominanta do 45 m wyrasta ponad portal, ale stoi ok. 60–65 m od niego;
  - zakończenie dominanty powinno być spokojne i poziome, bez iglicy, żeby nie konkurować z hełmami.
- **Materiał.** Granit pylonów i murów nabrzeży to naturalne odniesienie dla **cokołu** budynku i posadzki przedmościa.
- **Kolor mostu.** Błękitu mostu nie powtarzać w elewacji. Kolor może się też zmienić po remoncie (ewentualny powrót do kolorystyki pierwotnej).

---

## 2. Przedmieście Oławskie, Plac Społeczny, nabrzeża

Historia urbanistyczna (XIX-wieczne przedmieście czynszowe, wpis 538/A/05, zniszczenia 1945, odgruzowanie 1951) jest w `historia.md` § 2, 4 i 6. Tu jest stan dzisiejszy i plany.

### 2.1 Dzisiejszy charakter Przedmieścia Oławskiego

- [Ź] Według archiwalnego artykułu wroclaw.pl (6.11.2014) przedmieście ma 120 ha i ok. 24 tys. mieszkańców. Gęstość zaludnienia jest wyższa od średniej miejskiej. Dzielnica ma „negatywny wizerunek”, choć wskaźniki „nie odbiegają od średniej w pozostałych częściach miasta”. Wyremontowano m.in. ul. Pułaskiego, Krakowską i Muzeum Etnograficzne.
- [Ź-wt] Rewitalizacja trwa od 2008 r. W okresie PRL przylgnęła nazwa „Trójkąt (Bermudzki)”. Działają tu trzy Centra Aktywności Lokalnej. Dużo mieszkań komunalnych ogrzewa się piecami węglowymi. Źródła: wroclaw.pl i bip.um.wroc.pl, tylko fragmenty w wynikach wyszukiwania; pełnych tekstów nie czytano.
- [O] Bezpośrednie sąsiedztwo działki:
  - zachowane kamienice Mazowiecka 19 i Wybrzeże Słowackiego 5, z ciemnym, zszarzałym i nieodnowionym tynkiem;
  - odnowiony gmach Mazowiecka 17 z napisami „URZĄD MARSZAŁKOWSKI WOJEWÓDZTWA DOLNOŚLĄSKIEGO” i „DOLNY ŚLĄSK”;
  - po zachodniej stronie Mazowieckiej rozległy, pusty trawnik pl. Społecznego (M.10, DJI_…0036).
- WNIOSEK: nowy urząd będzie największą publiczną inwestycją w tej części przedmieścia. Kryterium „inkluzywności” można tu wypełnić dosłownie:
  - otwarty parter z funkcjami dla mieszkańców;
  - dostępny dziedziniec z ogródkami (Wyj. 20 odp. 77);
  - bulwar nad Oławą;
  - narracja „urząd, który naprawia kwartał”.

### 2.2 Plac Społeczny – stan i plany

| Temat | Ustalenie | Źródło |
|---|---|---|
| Estakada zachodnia | Rozebrana w 2019 r. (podpis zdjęcia „Rozbiórka estakady zachodniej – rok 2019”) | [Ź] wroclaw.pl 22.01.2026 |
| Estakada wschodnia (z Mostu Grunwaldzkiego w kierunku Traugutta/Pułaskiego) | Według ekspertyz ZDiUM „nadaje się już tylko do rozbiórki” („Stal zaczęła rdzewieć i pęcznieć”, T. Staruchowicz). Ma ją zastąpić skrzyżowanie w poziomie terenu z dwoma pasami do skrętu w lewo z Mostu Grunwaldzkiego. Termin: 2028, razem z remontem mostu | [Ź] wroclaw.pl 22.01.2026 |
| Przyszły plan miejscowy | W odpowiedzi na interpelację (23.10.2025) urząd miał podać, że brak harmonogramu. Miasto współpracuje z EBI nad studium wykonalności zagospodarowania placu, a nowy MPZP ma powstać na podstawie planu ogólnego | [Ź-wt] fragment wyników wyszukiwania (bip.um.wroc.pl, załącznik 165881; pełnego tekstu nie odczytano, serwer zwracał błąd 503) |
| Studium 2018 | Plac Społeczny wskazany jako obszar „kompozycji wysokościowych” (§ 4.4) | [Ź] Zakrzewska-Półtorak 2017 |
| 1997 | „Jedna z estakad na placu Społecznym pod wodą” (podpis zdjęcia) | [Ź] wroclaw.pl 12.07.2024 |

- WNIOSEK: teren na zachód od działki jest w trakcie przemian. Za 3–5 lat zniknie estakada wschodnia, a później może powstać nowy plan placu. Fasada od Mazowieckiej i narożnik NW będą wtedy bardziej eksponowane niż dziś. Projekt powinien „działać” zarówno dziś (estakady na F.17), jak i po przebudowie. Warto to pokazać na schemacie urbanistycznym jako zakres ideowy (por. `wizja_lokalna.md` § 3 pkt 3).

### 2.3 Bulwary nad Odrą i Oławą

- [Ź] Projekt rewitalizacji bulwarów **Xawerego Dunikowskiego** i **Marii i Lecha Kaczyńskich** obejmuje „obszar między mostem Grunwaldzkim a Piaskowym”, czyli prawie kilometr nabrzeża. Za gmachem urzędu wojewódzkiego przewidziano przystań statków wycieczkowych. Projekt jest „dość surowy” ze względu na wymogi przeciwpowodziowe (wroclaw.pl, 20.10.2014, artykuł archiwalny; stan realizacji niezweryfikowany).
- [Ź] MPZP: teren **6KDB/2** (Wybrzeże Słowackiego wzdłuż Oławy) przewiduje ciągi piesze i pieszo-rowerowe, przystanie i szpalery drzew. Teren **4KDPL/3** ma być powiązany z bulwarem nad Odrą w kierunku Wieży Ciśnień kładką (`mpzp.md` § 4).
- [Ź] Rewitalizacja nabrzeży Oławy (etap I) obejmowała odcinek między mostami Oławskim i Rakowieckim, powyżej działki (wroclaw.pl, 5.10.2015, archiwalne).
- WNIOSEK: działka jest **zawiasem** łączącym dwa systemy nabrzeży:
  - bulwar odrzański (Dunikowskiego – DUW – przyczółek Mostu Grunwaldzkiego);
  - nabrzeże Oławy (Wybrzeże Słowackiego – 4KDPL/3 – kładka do Wieży Ciśnień).

  Parter i przedmoście powinny ten ciąg spinać: przejście wzdłuż elewacji ENE, aktywny parter, punkt widokowy w miejscu dawnej przystani parowców. To argument dla kryteriów „trafność wpisania w tkankę” oraz „dostępność”.

### 2.4 Plan ogólny 2026

- [Ź] wroclaw.pl (26.08.2026): „Plan ogólny zastępuje w systemie prawnym Studium Uwarunkowań i Kierunków Zagospodarowania Przestrzennego”. Dzieli miasto na 9 901 stref planistycznych.
- [Ź] Obszar uzupełnienia zabudowy (OUZ), czyli tereny, gdzie można wydawać decyzje o warunkach zabudowy, usunięto m.in. w historycznych kwartałach. Artykuł nie wymienia Przedmieścia Oławskiego wprost.
- [Ź] Artykuł nie podaje numeru uchwały ani daty wejścia w życie. Wersja finalna jest w geoportal.wroclaw.pl/www/pog_app/.
- WNIOSEK: dla konkursu wiąże MPZP XLV/1366/10. Do sprawdzenia (zadanie dla modułu prawnego): strefa planistyczna planu ogólnego dla terenu i pl. Społecznego (maks. wysokość, wskaźniki). Ma to znaczenie dla argumentacji „długofalowej”, nie dla zgodności formalnej.

---

## 3. Obecne siedziby UMWD

### 3.1 Lokalizacje (fakty)

| Adres | Ustalenia | Źródło |
|---|---|---|
| **Wybrzeże J. Słowackiego 12–14**, 50-411 (siedziba główna) | Winda zewnętrzna od chodnika uruchamiana przez ochronę. Dwa wejścia: drzwi obrotowe i przeszklone. W holu Centrum Informacji o Urzędzie i swobodny dostęp do windy głównej. Kancelaria Ogólna na I piętrze. Program konkursu zakłada, że serwerownia główna zostaje w tym budynku (światłowód do nowej siedziby) | [Ź] Deklaracja dostępności UMWD, 13.12.2021; `docs/20_program/program_tabela.csv` |
| **Mazowiecka 15**, 50-529 | Wejście od ulicy zamknięte na stałe (tylko droga ewakuacyjna). Połączenie z Wybrzeżem Słowackiego łącznikiem na II i IV piętrze, dalej z Mazowiecką 17. Łącznik 15/17 to „szklane drzwi i trzy stopnie” | [Ź] Deklaracja 2021 |
| **Mazowiecka 17**, 50-412 | Wejście od frontu z dzwonkiem do ochrony. Osoba ze szczególnymi potrzebami jest kierowana na tył budynku, do windy uruchamianej przez ochronę. Na elewacji napisy „URZĄD MARSZAŁKOWSKI WOJEWÓDZTWA DOLNOŚLĄSKIEGO” i „DOLNY ŚLĄSK”. Historycznie dawny etablissement z 1873 r. (F. Barchewitz), przebudowany w 1913 r.; w zespole jest też Centrum Sztuki Impart | [Ź] Deklaracja 2021; [O] M.10 DJI_…0036; `historia.md` § 5 |
| **Walońska 3–5**, 50-413 | Trzy windy. Kancelaria Ogólna na parterze. Jedno z dwóch wejść zamknięte na stałe | [Ź] Deklaracja 2021 |
| Wspólne | „skomplikowana trasa dotarcia do budynków” | [Ź] Deklaracja 2021 |
| Dobrzyńska, Matejki | **Nie potwierdzono** w znalezionych źródłach, że UMWD ma tam siedziby (deklaracja z 2021 r. ich nie wymienia; mogą to być jednostki podległe). Do weryfikacji w BIP UMWD | – |
| Sala obrad Sejmiku | Obecnej lokalizacji nie ustalono w źródłach publicznych przeczytanych w tym module | – |

### 3.2 Architektura obecnych budynków

- **Wybrzeże Słowackiego 12–14.** [Ź-wt] Na podstawie podpisów zdjęć w polska-org.pl (obiekt 547250; źródło społecznościowe, niepewne):
  - teren w latach 1950–1970 był pusty („Teren pod przyszły Urząd Marszałkowski… zaplecze budowlane”);
  - budynek istnieje na zdjęciu z lat 1988–1990 („Według wcześniejszych planów to tu miało być Pogotowie Ratunkowe”);
  - budynek dzieli zespół z PKI Predom.

  WNIOSEK: to najpewniej późnopeerelowski budynek biurowy, bez wartości reprezentacyjnej na miarę siedziby samorządu województwa. Uzasadnia to potrzebę nowej siedziby z salą Sejmiku. Daty i autora nie potwierdzono w źródle oficjalnym.
- **Mazowiecka 17.** [O] Jasny, kremowy tynk, wielkie pilastry. Boniowany parter w odcieniu piaskowca, z oknami zamkniętymi łukiem. Stromy dach z czerwonopomarańczowej dachówki z lukarnami. Narożna wieżyczka z ciemną kopułką i masztem flagowym (M.10, DJI_…0036).
- WNIOSEK: dzisiejsze „oblicze” urzędu przy ul. Mazowieckiej to **jasny, klasycyzujący gmach z czerwonym dachem**. Nowy budynek dostawiony do Mazowieckiej 19 będzie stał 2 posesje dalej. Kolorystyka jasnych tynków i piaskowca łączy nowe ze starym bez kopiowania form.

---

## 4. Współczesna architektura Wrocławia i oczekiwania środowiska

### 4.1 Nagrody miejskie: co wygrywa we Wrocławiu

**Uwaga o nagrodach.** Nie znaleziono źródeł o „Nagrodzie Architektonicznej Prezydenta Wrocławia” jako odrębnej nagrodzie. Wyniki wyszukiwania dotyczyły nagrody Prezydenta **Warszawy**. Główną miejską nagrodą jest konkurs „**Piękny Wrocław**”:
- [Ź-wt] konkurs zainicjowało w 1990 r. Towarzystwo Miłośników Wrocławia, a od ok. 2015 r. organizuje go Urząd Miejski;
- [Ź] w 2021 r. Kapitule przewodniczył Architekt Miasta P. Fokczyński, w 2026 r. dyrektor Wydziału Architektury i Zabytków M. Wankowska.

[Ź] Kryterium według przewodniczącego Kapituły (2021): „W tym konkursie od 31 lat głównym kryterium wyboru są walory architektoniczne, przestrzenne oraz funkcjonalno-użytkowe.”

| Edycja (ogłoszenie) | Obiekt | Autorzy | Co doceniono / cecha | Źródło |
|---|---|---|---|---|
| XXVI | **Narodowe Forum Muzyki** (pl. Wolności), Grand Prix | Kuryłowicz & Associates (otwarcie 4.09.2015) | Elewacja z materiału imitującego drewno. Foyer czarno-białe, z czarną ścianą z Corianu. E. Kuryłowicz: „Zależało nam na czymś podniosłym, co dotrze do każdego, a nie chcieliśmy robić żadnych ornamentów” | [Ź] wroclaw.pl (lista Grand Prix; wywiad 3.07.2015); [Ź-wt] wyniki wyszukiwania (elewacja) |
| XXX (1.12.2021, za 2019) | **Hotel The Bridge**, pl. Katedralny 8, nad Odrą, Grand Prix | FORUM architekci (M. Goncerzewicz, M. Lose i zespół); wnętrza Medusa Group | Ponad 2000 m² elewacji klinkierowej. Według operatora fasada z klasycznej cegły nawiązuje do architektonicznej przeszłości miasta | [Ź] wroclaw.pl 1.12.2021; [Ź-wt] klinkier.pl, mgallery.accor.com |
| XXX | **Nowy Targ** (biurowiec, pl. Nowy Targ 28), II nagroda w kat. użyteczności publicznej; finał Nagrody Architektonicznej „Polityki” 2020 | Maćków Pracownia Projektowa | „Na szczęście bryła nie wydaje się ciężka i dominująca nad otoczeniem”, bo moduły rozdzielają przeszklone patia. „może stanowić wzór, jak bez arogancji można stawiać biurowce” (uzasadnienie nominacji „Polityki”) | [Ź] wroclaw.pl 1.12.2021 i 8.04.2020 |
| XXXI (1.12.2021, za 2020) | **Pixel House** (Legnicka/Niedźwiedzia), Grand Prix | Bzdęga-Wiśniewski | Budynek mieszkalno-usługowy w pierzei | [Ź] wroclaw.pl 1.12.2021 |
| XXXI | **Centrum Południe** (I nagroda, użyteczność publiczna) | APA Wojciechowski | Kompleks biurowy z wieżą, w strefie wysokościowej | [Ź] wroclaw.pl 1.12.2021 |
| XXXI | **Concordia Design**, Wyspa Słodowa 7 (II nagroda) | MVRDV i Q2Studio | Remont i przebudowa kamienicy z 1845 r. z oficyną; współczesna reinterpretacja bryły historycznej | [Ź] wroclaw.pl 1.12.2021; [Ź-wt] architizer, aluprof (2018–2020) |
| XXXII (XII 2023) | **Swoja Olimpia**, Grand Prix | PAG (dawniej Pracownia Architektury Głowacki) | Jury: „wygrała realizacja elegancka w formie, o interesującej, ale czytelnej bryle, wykończona bardzo dobrymi materiałami”. Autorzy: zasada „powściągliwość i elegancja” | [Ź] wroclaw.pl 24.12.2023 |
| XXXIII (17.04.2026) | **Park Krzycki**, Grand Prix | ZZM i MPWiK | „odpowiada na wyzwania, które wynikają ze zmian klimatu”; „Otwarta retencja jest najtańszym i najbardziej efektywnym sposobem” | [Ź] wroclaw.pl 17.04.2026 |
| XXXIII | **WUWA Point**, Al. Architektów 7 (I nagroda, użyteczność publiczna) | Maćków Pracownia Projektowa | „architektury funkcjonalnej (otwarty, elastyczny plan)”, dbałość o jakość wykończenia | [Ź] wroclaw.pl 17.04.2026 |
| XXXIII | **Nowodworska 43** (I nagroda, wielorodzinne) | b.d. | „Uzupełnił bardzo spójną kompozycję zabudowy przedwojennego osiedla” | [Ź] wroclaw.pl 17.04.2026 |
| XXXIII | Rewitalizacja kamienic **Szczytnicka 29, 29a, 31** (I nagroda, modernizacja) | b.d. | Rewitalizacja historycznej pierzei | [Ź] wroclaw.pl 17.04.2026 |

**Luka:** nie znaleziono nagradzanych realizacji na Nadodrzu z opisem jury. Brak też pełnego opisu elewacji NFM w źródle oficjalnym.

### 4.2 Wzorce (WNIOSEK, z krytycznym zastrzeżeniem)

1. **Umiar, czytelność, materiał.** We wszystkich edycjach powracają te same pojęcia: „elegancka”, „czytelna bryła”, „bardzo dobre materiały”, „powściągliwość”, „bez arogancji”, „bez ornamentów”. Lokalne jury nie nagradza ekspresji formy dla niej samej.
2. **Duża kubatura w historycznym centrum dzielona na moduły.** Nowy Targ i jego przeszklone patia to wrocławski precedens tego, czego wymaga DWKZ („optyczny podział bryły na mniejsze segmenty”).
3. **Cegła i ceramika w panoramie Odry są akceptowane i nagradzane** (The Bridge). W kwartale działki dominuje jednak jasny tynk, piaskowiec i granit (§ 6; por. `elewacje_zasady.md` § 5). Ceramika powinna więc być **jasna**, a nie czerwona.
4. **Klimat i woda zyskują wagę.** Grand Prix 2026 dla parku za otwartą retencję to sygnał zgodny z kryterium „rozwiązania proekologiczne”.
5. **Zastrzeżenie:** „Piękny Wrocław” to nagroda realizacyjna. Jury konkursu SARP ocenia koncepcję według kryteriów z Regulaminu. Wzorce te pokazują wrażliwość lokalnego środowiska, ale nie są dowodem na preferencje konkretnego Sądu.

### 4.3 Architekt Miasta Wrocławia i Zespół Architekta Miasta

- [Ź] **dr inż. arch. Jacek Barski** został powołany na Architekta Miasta przez Prezydenta Wrocławia (wroclaw.pl, 25.10.2024). Jest dyrektorem Departamentu Urbanistyki i Architektury. W latach 1989–2019 pracował w Katedrze Planowania Przestrzennego Wydziału Architektury PWr. Brał udział w przygotowaniu kilkuset MPZP.
- [Ź] Barski jest sędzią w tym konkursie z ramienia Zamawiającego (Regulamin, sąd konkursowy). To informacja z materiałów konkursowych, nie z wyników.
- [Ź] Zadania Zespołu Architekta Miasta (od 1.01.2025, co najmniej raz na dwa miesiące):
  - rekomendacje dla polityki inwestycyjnej;
  - konsultowanie koncepcji o istotnym znaczeniu dla miasta;
  - „opiniowanie oraz udział w konkursach architektonicznych”;
  - wspieranie rozwiązań „wysokiej jakości”, odpowiadających na wyzwania społeczne, kulturowe i środowiskowe, „z poszanowaniem ciągłości kulturowej i tożsamości przestrzennej miasta”.
- [Ź] Skład Zespołu (2024), m.in.:
  - Magdalena Wankowska, Miejski Konserwator Zabytków (wiceprzewodnicząca);
  - Piotr Zybura (SARP O/Wrocław), który według Regulaminu jest też sędzią referentem w tym konkursie;
  - dr Michał Duda (Muzeum Architektury);
  - Krzysztof Wartenberg (architekt obiektów zabytkowych).

  Zmiany z 11.05.2026: prof. M. Baborska-Narożny (dziekan WA PWr), R. Zarzycki (DOIIB), Ł. Komar (DOIA).
- [Ź] Wypowiedzi:
  - Barski (2024): „Wrocław jest przestrzenią, która często była kształtowana przez architektów dużego formatu”;
  - Barski (2026): „Mam nadzieję, że wiedza nowych członków pozwoli na tworzenie miasta zrównoważonego, dostępnego dla mieszkańców”;
  - M. Duda (2026, jako członek jury „Pięknego Wrocławia”): „Wszyscy mają prawo udziału w dyskusji o tym, jaka powinna być architektura”.
- [Ź] Sędzia rezerwowy, mgr inż. arch. Michał Goncerzewicz (SARP O/Wrocław, Regulamin), jest współautorem hotelu The Bridge (FORUM architekci; Grand Prix „Pięknego Wrocławia” XXX, elewacja klinkierowa nad Odrą; § 4.1). To informacja z materiałów konkursowych i źródeł miejskich, nie z wyników.
- **Luka:** nie znaleziono publicznych wypowiedzi J. Barskiego (2024–2026) wprost o pierzejach, wysokościowcach czy parterach. Artykuł wprost.pl „Wysoko czy nisko?” był niedostępny (403). Wywiad „5 pytań do…” (Strefa Kultury 2021) zwrócił 404.
- WNIOSEK: dwóch wrocławskich sędziów, Architekt Miasta i sędzia referent, zasiada w gremium, którego programem jest „jakość”, „ciągłość kulturowa i tożsamość przestrzenna”, „zrównoważenie” i „dostępność”. Barski ma przy tym zaplecze planisty. Należy oczekiwać wnikliwej oceny:
  1. ścisłej zgodności z MPZP (linie, wysokości, obszar A);
  2. logiki urbanistycznej (pierzeje, osie, przedmoście);
  3. dostępności i jakości przestrzeni publicznej.

  Opis pracy powinien prowadzić tę argumentację wprost, w języku planistycznym: osie, ciągi, kompozycja wysokościowa.

### 4.4 Polityka wysokościowa Wrocławia

[Ź] Zakrzewska-Półtorak A. (2017), na podstawie Studium 2010 i projektu Studium 2017 (uchwalone 11.01.2018, uchwała L/1177/18):
- **Obiekt wysokościowy** to obiekt ponad 55 m. W 2017 r. było we Wrocławiu ponad 190 budynków o co najmniej 10 kondygnacjach. Najwyższe: Sky Tower 212 m, katedra 97,5 m, św. Elżbieta 92 m.
- **Strefy wysokości (Studium 2017, s. 123–124):**
  - W1: obszar śródmiejski 25 m n.p.t., z możliwością podwyższenia do 55 m;
  - W2: 40 m; W3: 25 m; W4: 18 m; W5: 12 m;
  - W0: maks. wysokość określa MPZP.

  Wartości wyznaczono m.in. z istniejącej zabudowy (70% wysokości budynków w obszarze). Pojedyncze dominanty dopuszcza się poza tymi wartościami, w miejscach wskazanych.
- **Dominanty lokuje się m.in.:**
  - w miejscach szczególnie ważnych, np. węzłach komunikacyjnych;
  - „w bramach miasta lub jego części”;
  - wzdłuż głównych tras;
  - **„na zamknięciach osi widokowych”**;
  - w układach o zaburzonej hierarchii dominant;
  - tam, gdzie już stoją makroelementy kompozycji.
- **Obszary kolejnych kompozycji wysokościowych:** Centrum Południe, **Plac Społeczny**, oś Grunwaldzka przy moście Szczytnickim, Stadion Miejski.
- **Zasady (wybór):**
  - łagodzić dysproporcje w strefach styku różnych wysokości;
  - uwzględniać chronione widoki i osie;
  - **różnica wysokości po obu stronach ulicy lub placu maks. 2 kondygnacje**, chyba że zabudowa jest odległa lub izolowana zielenią;
  - nadwyżkę wysokości w śródmieściu dopuszcza się, gdy „dyktują to względy kompozycyjne i przestrzenne”, które są kryterium rozstrzygającym.
- Konkluzja autorki: budynków ponad 55 m nie przybywa, rośnie natomiast liczba budynków wysokich (22–55 m).

WNIOSEK:
- Dominanta do 45 m (MPZP, obszar A) mieści się w filozofii Studium. Plac Społeczny był przewidziany na kompozycję wysokościową, a przedmoście Mostu Grunwaldzkiego to „brama” Śródmieścia na osi pl. Grunwaldzki – Most Grunwaldzki – pl. Społeczny.
- Uzasadnienie dominanty w opisie i na schemacie: (1) zamknięcie osi widokowej z esplanady pl. Grunwaldzkiego (wskazanej na wizji lokalnej, pkt 6); (2) brama przedmościa; (3) „makroelement” w zespole z DUW, Pocztą Główną (pierwszy wrocławski wieżowiec, 1926–1929) i portalem mostu.
- Reguła „2 kondygnacji” wspiera podejście, w którym skrzydła mają wysokość kamienic (ok. 21–22 m wobec gzymsu Mazowieckiej 19). Dominanta jest wycofana i jako jedyna przekracza skalę.

---

## 5. Klimat Wrocławia

### 5.1 Normy 1991–2020 (stacja IMGW Wrocław-Strachowice, 351160424) [D]

Metoda: średnie miesięczne z lat 1991–2020 z danych publicznych IMGW-PIB (synop, miesięczne `s_m_d` i `s_m_t`; pobrane 16.11.2026). Suma roczna jest sumą średnich miesięcznych. W usłonecznieniu brakuje 6 miesięcy (IX i X 1992, IV 1994, VII 1998, X 2000, X 2004); średnią liczono z dostępnych lat. Kontrola: średnia roczna 9,7 °C zgadza się z wartością podawaną przez wroclaw.pl (20.11.2024). Stacja leży na lotnisku, ok. **11,6 km na zachód** od działki. W centrum należy doliczyć efekt miejskiej wyspy ciepła (§ 5.4). Plik: `data/klimat_wroclaw_normy_1991_2020.csv`.

| Element | I | II | III | IV | V | VI | VII | VIII | IX | X | XI | XII | **Rok** |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T średnia [°C] | 0,0 | 1,1 | 4,3 | 9,7 | 14,3 | 17,7 | 19,7 | 19,3 | 14,5 | 9,6 | 4,8 | 1,1 | **9,7** |
| T maks. średnia [°C] | 3,0 | 4,7 | 9,0 | 15,3 | 20,0 | 23,4 | 25,6 | 25,4 | 20,0 | 14,3 | 8,3 | 4,1 | **14,4** |
| T min. średnia [°C] | −3,3 | −2,5 | 0,0 | 3,8 | 8,3 | 12,0 | 13,9 | 13,4 | 9,4 | 5,2 | 1,3 | −2,1 | **4,9** |
| Opad [mm] | 28 | 26 | 35 | 31 | 60 | 65 | 91 | 60 | 48 | 38 | 31 | 28 | **541** |
| Usłonecznienie [h] | 59 | 82 | 129 | 204 | 246 | 248 | 260 | 251 | 170 | 120 | 67 | 53 | **1888** |
| Wilgotność wzgl. [%] | 84 | 80 | 75 | 68 | 70 | 70 | 70 | 70 | 77 | 82 | 86 | 85 | **76** |
| Prędkość wiatru [m/s] | 3,7 | 3,7 | 3,6 | 3,2 | 2,9 | 2,8 | 2,7 | 2,5 | 2,7 | 3,0 | 3,3 | 3,6 | **3,1** |
| Zachmurzenie [oktanty] | 6,0 | 5,8 | 5,4 | 4,9 | 5,0 | 5,0 | 4,8 | 4,6 | 4,8 | 5,3 | 6,0 | 6,0 | **5,3** |
| Dni z pokrywą śnieżną | 12,4 | 9,1 | 4,0 | 0,5 | 0 | 0 | 0 | 0 | 0 | 0,1 | 2,4 | 6,4 | **34,9** |
| Dni z mgłą | 5,3 | 3,2 | 3,6 | 2,5 | 2,4 | 2,2 | 1,6 | 2,7 | 5,5 | 8,0 | 8,1 | 5,3 | **50,5** |
| Dni z burzą | 0,1 | 0,1 | 0,3 | 1,3 | 4,7 | 5,5 | 6,3 | 4,9 | 1,4 | 0,1 | 0,1 | 0,0 | **24,9** |

### 5.2 Ekstrema i wskaźniki, trendy (dane dobowe IMGW 1991–2025) [D]

| Wskaźnik | 1991–2020 | 1991–2005 | 2006–2020 | 2016–2025 |
|---|---|---|---|---|
| Dni letnie (Tmax ≥ 25 °C) | 56,4 | 51,0 | 61,7 | **73,3** |
| Dni upalne (Tmax ≥ 30 °C) | 12,4 | 9,0 | 15,7 | **19,0** |
| Dni bardzo upalne (Tmax ≥ 35 °C) | 0,9 | 1,0 | 0,8 | 0,9 |
| Noce tropikalne (Tmin ≥ 20 °C) | 0,8 | 0,1 | 1,5 | 1,8 |
| Dni przymrozkowe (Tmin < 0 °C) | 93,9 | 103,7 | 84,0 | **73,3** |
| Dni mroźne (Tmax < 0 °C) | 19,9 | 21,9 | 17,9 | **8,8** |
| Dni z opadem ≥ 10 mm | 12,8 | 11,5 | 14,2 | 13,0 |
| Dni z opadem ≥ 20 mm | 3,7 | 3,4 | 4,1 | 4,4 |
| Stopniodni grzania (18/15 °C) | 3141 | 3296 | 2987 | 2782 |
| Stopniodni chłodzenia (baza 18 °C, uproszczone) | 190 | 151 | 228 | **272** |

- Maksimum absolutne: **37,9 °C** (8.08.2015). Minimum absolutne: **−22,5 °C** (23.01.2006). Percentyle dobowe 1991–2020: Tmin 1% = −14,2 °C, Tmax 99% = 32,7 °C.
- Maksymalny opad dobowy 1991–2024: **74,4 mm** (VII 2001); dalej 69,4 mm (VI 2020) i 62,5 mm (VIII 2006).
- Dni upalne w ostatnich latach: 2015 – 32, 2018 – 27, 2019 – 26, 2022 – 25, 2024 – 27, 2025 – 13.
- [Ź] Obserwatorium UWr w centrum zanotowało w 2015 r. 31 dni upalnych, w tym 8 dni ≥ 35 °C. Średnia 1946–1985 wynosiła 7–10 dni upalnych, a w ostatnich dwóch dekadach ok. 18 (wroclaw.pl, 20.11.2024). Liczba dni ≥ 35 °C w centrum jest wielokrotnie wyższa niż na lotnisku, co jest zgodne z efektem wyspy ciepła.
- Usłonecznienie rośnie: średnio ok. 1870 h w latach 2001–2010 (bez roku 2004 z brakiem) i **ok. 2040 h** w latach 2011–2020 [D].
- Uwaga krytyczna: wskaźniki z jednej stacji podmiejskiej nie oddają warunków nad rzeką w śródmieściu (inna wilgotność, nocne wychłodzenie od wody, wyspa ciepła). Trend ocieplenia jest wyraźny i spójny ze źródłem miejskim. Wartości bezwzględne dla centrum są jednak wyższe.

### 5.3 Wiatr (dane terminowe IMGW, 1991–2020, godziny synoptyczne co 3 h, n = 87 664) [D]

| Sektor | N | NE | E | SE | S | SW | W | NW | cisza |
|---|---|---|---|---|---|---|---|---|---|
| Częstość [%] | 6,1 | 4,3 | 10,7 | **15,0** | 8,4 | 11,1 | **23,1** | **16,3** | 5,0 |
| Prędkość średnia [m/s] | 2,4 | 2,4 | 3,1 | 3,2 | 3,4 | 3,7 | **3,8** | 3,1 | – |
| Zima (XII–II) [%] | 4,5 | 3,3 | 9,6 | 16,2 | 10,4 | 15,6 | 23,6 | 13,3 | 3,5 |
| Lato (VI–VIII) [%] | 7,2 | 4,7 | 8,7 | 11,9 | 6,4 | 8,4 | 25,7 | 20,9 | 6,0 |
| Udział w wiatrach ≥ 8 m/s [%] | 0,2 | 0,1 | 4,1 | 9,8 | 10,0 | 14,7 | **52,0** | 9,0 | – |

Rozkład w 16 sektorach jest w `data/roza_wiatrow_wroclaw_1991_2020.csv`, a róża w `img/roza_wiatrow_1991_2020.png`. Najczęstsze sektory to WNW (14,3%) i W (13,3%).

- Interpretacja: róża jest dwubiegunowa. Główny biegun to W–WNW (cyrkulacja zachodnia), drugi to ESE–SE. Latem rośnie udział NW, zimą udział SW i SE.
- [Ź] Badania UWr wyznaczyły korytarze przewietrzania Wrocławia na podstawie parametrów aerodynamicznych zabudowy z LiDAR dla 8 kierunków wiatru (Suder i Szymanowski 2014, za Szymanowski i in. 2019). Układ zabudowy w takich korytarzach „powinien być szczególnie uważnie rozpatrywany w procesach planistycznych”. Dolina Odry o przebiegu W–E przy przeważających wiatrach W jest naturalnym kanałem. Szczegółowej mapy korytarzy w rejonie działki nie weryfikowano.
- WNIOSEK projektowy:
  1. Elewacja WSW (Mazowiecka) jest otwarta na rozległy pl. Społeczny i przyjmuje najsilniejsze wiatry. Elewacja NNW i narożnik przy moście są otwarte na dolinę Odry.
  2. Dominanta o wysokości 45 m wytworzy przy podstawie zjawisko „downwash”, czyli spływ wiatru po elewacji do poziomu chodnika. Wejście główne przy narożniku NE wymaga zadaszenia lub podcienia. Analizę komfortu wiatrowego (np. CFD, kryteria Lawsona) warto wspomnieć w opisie jako element etapu projektowego.
  3. Tarasy i loggie dominanty oraz taras przy holu Sejmiku najlepiej sytuować po stronie E–SE (zawietrznej przy wiatrach W) albo osłaniać szklanymi parapetami.
  4. Nie blokować przewietrzania doliny Odry. Wycofane piętra i przerwy między segmentami poprawiają cyrkulację na dziedzińcu.

### 5.4 Miejska wyspa ciepła [Ź]

Szymanowski M., Drzeniecka-Osiadacz A., Sawiński T., Kryza M. (2019), za Szymanowski (2004):
- średnie roczne natężenie UHI w centrum: **1,0 K**; latem **2,4 K**, wiosną 2,2 K, zimą 1,2 K;
- maksimum z pomiarów stacjonarnych **9,0 K**; pomiary patrolowe pokazują zróżnicowanie powyżej 10 K;
- silna UHI (> 3 K) występuje latem pięciokrotnie częściej niż zimą;
- nocą natężenie jest 2–3 razy wyższe niż w dzień, latem nawet 4–5 razy;
- „jeziora chłodu” (zabudowa chłodniejsza od otoczenia) występują w 12% godzin roku.

WNIOSEK:
- Ciepłe noce w centrum wzmacniają potrzebę **nocnego przewietrzania**, masy termicznej i zewnętrznych osłon przeciwsłonecznych.
- Dziedziniec z zielenią i zachowanymi drzewami (wymóg Regulaminu) oraz zielone dachy na skrzydłach ograniczają lokalne przegrzewanie.
- To argument dla kryterium „rozwiązania proekologiczne” i dla standardu zeroemisyjności (M.12).

### 5.5 Położenie Słońca [D]

Współrzędne terenu: **51,1083° N, 17,0516° E**. To środek terenu, przeliczony przez pyproj z PL-2000 (X ≈ 5 664 130, Y ≈ 6 433 585; `wizualizacje_metodyka.md`). Algorytm NOAA z `umwd/src/umwd/sun.py`, czas lokalny (CET/CEST). Wschód i zachód liczono przy wysokości −0,833°.

> Uwaga: stała w `sun.py` (51,1115 N, 17,0480 E) leży ok. 430 m od terenu. Wpływ na wynik jest pomijalny (< 0,01°), ale dla porządku warto ją ujednolicić.

| Data (2027) | Wschód (azymut) | Górowanie: godz., wysokość | Zachód (azymut) | Długość dnia | Cień/wysokość w południe | Cień dominanty 45 m w południe |
|---|---|---|---|---|---|---|
| 20 III (równonoc) | 05:54 CET (89°) | 12:00, **38,8°** | 18:07 (271°) | 12,2 h | 1,25 | ok. 56 m |
| 21 VI (przesilenie) | 04:35 CEST (49°) | 12:54, **62,3°** | 21:14 (311°) | 16,7 h | 0,52 | ok. 23 m |
| 23 IX (równonoc) | 06:38 CEST (89°) | 12:44, **38,8°** | 18:51 (271°) | 12,2 h | 1,24 | ok. 56 m |
| 21 XII (przesilenie) | 07:51 CET (128°) | 11:50, **15,5°** | 15:49 (232°) | 8,0 h | 3,60 | ok. 162 m |

Położenia godzinowe (azymut / wysokość):
- **20 III:** 8:00 – 114°/18°; 10:00 – 144°/33°; 12:00 – 180°/39°; 14:00 – 217°/33°; 16:00 – 246°/18°.
- **21 VI:** 6:00 – 65°/10°; 8:00 – 87°/28°; 10:00 – 113°/47°; 12:00 – 154°/60°; 14:00 – 211°/60°; 16:00 – 250°/45°; 18:00 – 275°/26°; **20:00 – 297°/8°**; 20:30 – 303°/4°.
- **21 XII:** 10:00 – 154°/12°; 12:00 – 182°/15°; 14:00 – 210°/10°.
- **29 X 2025 (dzień zdjęć F.17, CET):** 08:00 – 127°/10°; 10:00 – 155°/22°; **11:38 – 181°/25,3°**; 14:00 – 217°/18°; 16:00 – 243°/4°.

Wykres ścieżek: `img/sciezki_slonca_teren.png`.

**Orientacja elewacji.** Normalne elewacji wyznaczono z narożników obszaru A w PL-2000 (`mpzp.md` § 3, poz. 12; azymut krawędzi pn. ok. 76°). Godziny bezpośredniego nasłonecznienia policzono bez przesłonięć, przy wysokości Słońca > 2° i kącie padania < 85° od normalnej:

| Elewacja (normalna) | 20 III | 21 VI | 29 X | 21 XII |
|---|---|---|---|---|
| **NNW – od mostu i Odry (346°)** | 0,6 h (17:15–17:45) | 5,6 h (rano do ok. 7:00 i wieczór od ok. 18:00) | 0 | 0 |
| **ENE – od Oławy (76°)** | 4,8 h (06:15–10:55) | 7,2 h (05:00–12:10) | 3,4 h (do ok. 11:20) | 2,2 h (08:15–10:25) |
| **WSW – od Mazowieckiej (256°)** | 6,2 h (11:35–17:45) | 8,2 h (12:40–20:45) | 5,2 h (od ok. 12:05) | 4,2 h (11:15–15:25) |
| **SSE – dziedziniec (166°)** | 10,2 h | 8,6 h | 9,2 h | 7,2 h |

Godziny dla 29.10.2027 podano w czasie letnim; w 2025 r. ten dzień był już w CET, czyli godzinę wcześniej.

**Azymuty do punktów orientacyjnych** (WGS84, współrzędne punktów przybliżone ±100 m):

| Punkt | Azymut | Odległość |
|---|---|---|
| Katedra św. Jana Chrzciciela | **332°** | 0,75 km |
| Rynek / Ratusz | 277° | 1,38 km |
| Poczta Główna (Krasińskiego) | 254° | 0,58 km |
| Sky Tower | 236° | 2,70 km |
| **Ślęża** (718 m n.p.m.) | **222°** | 36,2 km |
| Wieża ciśnień Na Grobli | 140° | 0,48 km |
| Hala Stulecia | 95° | 1,80 km |

[O] Ślęża jest widoczna nad horyzontem na zdjęciu z drona M.10 (DJI_…0015, ok. 88 m n.t.).

**WNIOSKI** (dla projektu i wizualizacji):
1. **Fotomontaże F.17 (29.10, południe).** Elewacje ENE (widoczna na F.17.A) i NNW są **w cieniu**: kąt między Słońcem a normalną przekracza 90°. Elewacja WSW (F.17.B) dostaje światło skośne, ok. 70–75° od normalnej, które wydobywa fakturę. Na F.17.A cieniste elewacje kamienic są wyraźnie niebieskawe (np. Wybrzeże Słowackiego 5, L ≈ 40%). Materiał elewacji od Oławy i od mostu musi więc „bronić się w cieniu”:
   - jasny i ciepły;
   - matowy;
   - z głębokimi ościeżami i reliefem, który czyta się przy świetle rozproszonym.

   Ciemne lub lustrzane szkło na tych elewacjach będzie na wizualizacji 1 wyglądać jak ciemna dziura.
2. **Ujęcie „emocjonalne” od mostu.** Wieczór letni jest fizycznie poprawny: 21 VI, 19:30–20:30 CEST, Słońce na az 292–303° i wys. 13–4° oświetla ciepło elewację NNW i pylony. Alternatywa (wg `wizualizacje_metodyka.md`): niebieska godzina z rozświetloną salą Sejmiku jako „latarnią” nad Odrą.
3. **Sala Sejmiku.** Okno na NNW:
   - otwiera się prawie dokładnie na Ostrów Tumski (az 332°) i Most Grunwaldzki;
   - daje stałe światło rozproszone, bez olśnienia i zysków słonecznych, czyli bez ciężkich osłon;
   - ewentualne okno lub loggia na SW kadruje Sky Tower i, przy dobrej przejrzystości powietrza, Ślężę (święta góra Śląska).

   To czytelna symbolika dla sejmiku województwa: z sali widać kolebkę miasta i najważniejszy szczyt regionu. Widoczność Ślęży z wysokości ok. 35–45 m trzeba **zweryfikować** (panorama 360° z M.09 lub model terenu). Na odległości 36 km zamglenie jest częste (ok. 50 dni z mgłą w roku, maksimum w X–XI).
4. **Cień dominanty** pada głównie na przedmoście, ulicę i Odrę (północ), a nie na kamienice mieszkalne położone na południe od obszaru A. Rano pada na zachód (pl. Społeczny), po południu na wschód (Oława). To argument dla sąsiadów i dla kryterium „trafność wpisania w tkankę”.
   - Dziedziniec i elewacje podwórzowe kamienic zacienia głównie wysokość skrzydeł (do 22 m).
   - Nasłonecznienie mieszkań w Wybrzeżu Słowackiego 5 i Mazowieckiej 19 (WT § 13: 3 h w dniach 21.03 i 21.09) wymaga sprawdzenia w modelu (zadanie dla modułu prawnego i modelowania).
5. **Osłony przeciwsłoneczne:**
   - ENE (poranek) i WSW (popołudnie, niskie Słońce): osłony pionowe lub skośne, ewentualnie głębokie ościeża;
   - SSE (dziedziniec): poziome okapy lub lamele;
   - NNW: bez osłon, z największym udziałem przeszkleń.

### 5.6 Ryzyko powodziowe i woda w gruncie

| Temat | Ustalenie | Źródło |
|---|---|---|
| ISOK, mapy zagrożenia powodziowego (II cykl, usługa INSPIRE) | Zapytanie GetFeatureInfo w środku terenu i w punkcie kontrolnym na działce zwraca **0 obiektów**. Na podkładzie ortofotomapy granice obszarów Q10% (zielona), Q1% (pomarańczowa) i Q0,2% (czerwona) biegną wzdłuż koryta Odry i Oławy. Linia Q0,2% przebiega **wzdłuż krawędzi nabrzeża Wybrzeża Słowackiego**, kilka metrów od działki. W oknie 1,4 × 1,4 km nie występuje scenariusz „całkowitego zniszczenia wału przy Q1%” | [D] WMS `wody.isok.gov.pl/wss/INSPIRE/INSPIRE_NZ_HY_MZPMRP_WMS`, warstwa NZ.Fluvial, EPSG:2180, 16.11.2026; `img/isok_mzp_teren.jpg` |
| Opinia geotechniczna (M.05) | „przedmiotowe działki znajdują się na obszarze narażonym na niebezpieczeństwo powodzi (rzeczne)” (wg Hydroportalu). „obszar badań znajduje się w granicach strefy narażonej na podtopienia od wód gruntowych” (wg PIG) | [Ź] M.05, s. 6 |
| Wody gruntowe | Rzędna terenu 118,67–119,44 m n.p.m. Zwierciadło ustabilizowane 3,2–3,8 m p.p.t., czyli 115,07–115,95 m n.p.m. (IX 2025), wahania ±0,5 m. W O-01 woda naporowa na 16,5 m p.p.t. | [Ź] M.05, tab. 1 |
| Powódź 1997 | Wrocławski Węzeł Wodny musiał przyjąć do 3650 m³/s (mierzone na wysokości Trestna). Prawie 40% miasta pod wodą. „Jedna z estakad na placu Społecznym pod wodą” (podpis zdjęcia) | [Ź] wroclaw.pl 12.07.2024 |
| Po 1997 | Węzeł zmodernizowano do przepustowości ok. 3100 m³/s (wcześniej 2200–2400 m³/s): nowe i wzmocnione wały, poszerzone koryta, nowy kanał Odra–Widawa | [Ź-wt] en.wikipedia (zdanie bez przypisu; do weryfikacji w źródłach Wód Polskich) |
| Powódź 2024 | Kulminacja na Odrze we Wrocławiu 19.09.2024. Stan w Trestnie 631 cm, niższy niż w najgorszym scenariuszu. Miasto nie zostało zalane; na Ostrowie Tumskim zabezpieczano obiekty workami z piaskiem. Alarm odwołano 25.09.2024 | [Ź-wt] Polskie Radio (wg wyników wyszukiwania); [Ź] wroclaw.pl (prognozy, wg wyników wyszukiwania) |

**Krytycznie.** Między usługą ISOK a opinią geotechniczną jest rozbieżność. Możliwe wyjaśnienia: inna wersja danych, inny zakres warstw (np. obszary narażone w scenariuszu awarii budowli piętrzących lub zniszczenia wału, publikowane osobno w iMap), albo uproszczenie w opinii. Rozstrzygnięcie wymaga sprawdzenia w przeglądarce Hydroportalu (`wody.isok.gov.pl/imap_kzgw/?gpmap=gpMZP`) lub wystąpienia do Wód Polskich. Do tego czasu przyjąć **wariant ostrożny**.

WNIOSEK projektowy:
- Kondygnacje podziemne:
  - szczelna konstrukcja „biała wanna”, ściany szczelinowe (por. M.05);
  - spód płyty ok. 2–3 m poniżej zwierciadła;
  - kontrola wyporu.
- **Krytyczna infrastruktura nie w piwnicy:**
  - rozdzielnia główna, UPS i agregat, serwerownia lokalna oraz węzeł cieplny w miarę możliwości na parterze lub piętrze technicznym;
  - jeśli muszą być pod ziemią, to z zabezpieczeniem przeciwzalewowym.
- Rampa garażu (od Mazowieckiej lub Wybrzeża) z **progiem** powyżej poziomu ulicy i odwodnieniem liniowym. Zawory przeciwzwrotne na kanalizacji.
- Woda opadowa:
  - roczny opad 541 mm, letnie nawalnice do 74 mm/dobę;
  - **retencja** na dachach zielonych, w ogrodzie deszczowym na dziedzińcu i w zbiorniku retencyjno-użytkowym (podlewanie, spłukiwanie);
  - spójne z lokalnie nagradzaną „otwartą retencją” (Park Krzycki).
- Cokół z kamienia (granit) jest odporny na zawilgocenie i rozbryzg. Ma też uzasadnienie kontekstowe (pylony, mury nabrzeży).

### 5.7 Obciążenia klimatyczne do koncepcji konstrukcji (orientacyjnie)

[Ź-wt] Według ogólnych opracowań do Eurokodów Wrocław leży najpewniej w **1. strefie obciążenia śniegiem** (sk = 0,7 kN/m², PN-EN 1991-1-3/NA) i w **1. strefie wiatrowej** (vb,0 = 22 m/s, qb,0 = 0,30 kN/m², PN-EN 1991-1-4/NA). **Nie zweryfikowano** w treści załączników krajowych; potwierdzić w module prawno-technicznym. Dla dominanty 45 m nad otwartą doliną Odry przyjąć kategorię terenu z uwzględnieniem powierzchni wody (niższa szorstkość od strony N).

---

## 6. Paleta materiałów i kolorów otoczenia

### 6.1 Metoda i zastrzeżenie

- [O] Obejrzano zmniejszone kopie F.17.A i F.17.B (`00_materialy/podglady/`) oraz 9 zdjęć z drona M.10 (29.10.2025, DJI Air 3), zmniejszone do 1400 px (miniatury robocze w scratchpad, nie do publikacji).
- [D] Dla wybranych fragmentów policzono kolory dominujące (kwantyzacja median-cut, 4 klasy; skrypt `data/skrypty/palette.py`).
- **Zastrzeżenie:** zdjęcia mają silną obróbkę w Lightroomie:
  - Saturation +17/+24, Dehaze +24/+29, Shadows +52/+54 (`zdjecia_F17_metadane.md` § 1);
  - automatyczny balans bieli ok. 5500 K.

  Wartości HEX są więc **przybliżone i zawyżone w nasyceniu**. Służą do relacji jasności i tonów, a nie do specyfikacji (por. `elewacje_zasady.md` § 5.3: przed fazą wykonawczą trzeba zmierzyć kolory wzornikiem NCS na miejscu).

### 6.2 Elementy otoczenia

| Element | Opis [O] | Kolory dominujące z fragmentu zdjęcia [D] (L = jasność HLS) | Uwagi |
|---|---|---|---|
| **Mazowiecka 17** (UMWD/Impart) | Jasny, kremowy tynk z pilastrami. Boniowany cokół w odcieniu piaskowca, z oknami w łukach. Dach z czerwonopomarańczowej dachówki z lukarnami; ciemna kopułka wieżyczki | dachówka: #A14E33 (L42), #9A2A0F (L33); tynk w świetle (DJI_…0036, ocena wzrokowa): kość słoniowa / jasny krem | Fragment z F.17.B trafił częściowo w cień i okna (wynik szary #788290, odrzucony) |
| **Mazowiecka 19** | Kamienica eklektyczna, 8 osi. Tynk szarobeżowy, zszarzały, z detalem (gzymsy, naczółki). Dach płaski za attyką | #8E9297 (L57), #737475 (L45) | Fasada nieodnowiona; po renowacji będzie zapewne jaśniejsza i cieplejsza |
| **Wybrzeże Słowackiego 5** | Bogata elewacja eklektyczna od Oławy, szary tynk | w cieniu (F.17.A): #6B7690 (L49), #565E75 (L40); od podwórza (F.17.B): #A49782 (L58), #7B705E (L43) | Dobra próbka tego, jak elewacja ENE wygląda w cieniu na fotomontażu 1 |
| **Gmach DUW** (pl. Powstańców Warszawy 1) | Monumentalny, symetryczny, 3 kondygnacje i poddasze. Jasny tynk. Spłaszczony dach dwuspadowy, szary, przerwany nad portykami. [Ź] Mur ceglany, pierwotnie nieotynkowany, otynkowany po wojnie; proj. Feliks Bräuler na podstawie wcześniejszych idei Müllera i Schmidta (konkurs 1927) | fasada w słońcu (F.17.B): **#F1EADF (L91), #E8E0D2 (L87)**; dach: #889094 (L56), #97A0A5 (L62) | Najjaśniejsza płaszczyzna w kadrze F.17.B, punkt odniesienia dla bieli |
| **Pylony mostu** | Granit ciepło szarobrązowy, z ciemnymi zaciekami i fugami | #978B7E (L54), #776D61 (L42), #BFBCB3 (L73) | Odniesienie dla cokołu i posadzek |
| **Stal mostu** | Jasny, nasycony błękit (kratownice, wieszaki, balustrady) | w zdjęciach od #BDC7C9 do intensywnego błękitu (DJI_…0032) | Kolor „obcy”, nie powtarzać; może zmienić się po remoncie |
| **Mury nabrzeży** | Kamień szarobrązowy | #746B5E (L41), #948C82 (L55) | jw. |
| **Poczta Główna** (1926–1929, proj. Lothar Neumann) | Wieża w ciemnoczerwonej cegle w tle kadru F.17.A | – (za mały fragment) | [Ź-wt] autor i daty: archiweb, wroclaw.pl (wg wyników wyszukiwania) |
| **Ostrów Tumski** | Ceglany gotyk, czerwone dachówki, zielona miedź | #9D5F52 (L47), #B6968D (L63) | Akcent ciepłej czerwieni w panoramie |
| **„Manhattan” pl. Grunwaldzki** | Białe wieże z prefabrykatów | #F5F5F5 (L96), #D3D3D4 (L83) | Biel chłodna |
| **Odra / Oława** | Woda oliwkowo-brązowa, przy niebie stalowoniebieska | #4E4E37 (L26), #7A92A6 (L56) | – |
| **Zieleń (X)** | Złote, ochrowe i rdzawe korony (topole, klony, platany); trawniki | #B68C4A (L50), #7C5A27 (L32); trawa #6C7721 (L30) | Pora roku na F.17 to pełna jesień, więc zieleń na wizualizacjach 1–2 musi być jesienna |

### 6.3 Synteza palety (WNIOSEK)

Tony podano w przybliżeniu, do kalibracji na próbkach:

1. **Tło (dominująca rodzina jasnych mineraliów), L 80–92:** kość słoniowa, jasny piaskowiec, ciepła biel tynku, ok. #EDE5D8 – #E3D8C6 – #D8CBB5. Odniesienia: Mazowiecka 17, DUW. Z tej rodziny budować skrzydła. **Segmenty różnicować w wąskim zakresie** tonu (ΔL ok. 5–10) i faktury (gładka / ryflowana / szlifowana), zgodnie z DWKZ („zróżnicowanie kolorystyki, materiałów elewacyjnych oraz artykulacji fasady”) i bez kontrastów.
2. **Szarobeże kamienic, L 50–65:** #A49782, #8E8A80. To pas styku z Mazowiecką 19 (pierwsze osie nowej pierzei) oraz ewentualne pasy i gzymsy.
3. **Granit, L 40–55:** #978B7E, #776D61, #5C5346. Cokół, posadzka przedmościa i nabrzeża, schody wejściowe. Kamień z rodziny granitów śląskich (np. strzegomskich) uzasadnia się historycznie: pylony mostu.
4. **Ciepły akcent (jeden):** brąz patynowany lub mosiądz szczotkowany, ewentualnie jasna terakota. Korona dominanty, portal wejścia, stolarka sali Sejmiku. Nawiązuje do czerwieni dachówek i cegły Ostrowa Tumskiego, ale w spokojnym, szlachetnym tonie.
5. **Stolarka:** ciemny brąz lub grafit ciepły (spójnie z `elewacje_zasady.md` § 0 pkt 8).
6. **Czego unikać:**
   - błękitów i chłodnych szarości, które konkurują z mostem i niebem;
   - ciemnego, refleksyjnego szkła kurtynowego w pierzejach;
   - czystej, chłodnej bieli (konkurencja z „Manhattanem”, olśnienie);
   - czerwonej cegły jako tła: to kod miasta, ale nie tego kwartału (`elewacje_zasady.md` § 5).
7. **Dach jako „piąta elewacja”.** Na obu obowiązkowych fotomontażach lotniczych dach jest bardzo dobrze widoczny. MPZP zakazuje urządzeń na dachach (`mpzp.md` poz. 19, K-05). Dachy skrzydeł trzeba zaprojektować jako zielone, ewentualnie z PV zintegrowanym jako materiał pokrycia, w spokojnym rysunku pasów. Nie mogą wyglądać jak „pole techniczne”. Kolor PV: ciemny grafit matowy w rytmie zgodnym z siatką elewacji.

---

## 7. Wnioski projektowe – zestawienie (dla orkiestratora)

| # | Wniosek | Kryterium Sądu | Źródło wniosku |
|---|---|---|---|
| 1 | Uzasadnić dominantę kompozycyjnie: brama przedmościa, zamknięcie osi z pl. Grunwaldzkiego, „kompozycja wysokościowa pl. Społecznego” (Studium 2018) | trafność wpisania w tkankę | § 4.4 |
| 2 | Poziome, spokojne zakończenie dominanty, bez iglic, niekonkurujące z odtworzonymi hełmami mostu (ok. 25,5 m). Na przekroju urbanistycznym pokazać stan docelowy mostu | tkanka, atrakcyjność | § 1.2 |
| 3 | Sala Sejmiku z głównym oknem na NNW, z kadrem na Ostrów Tumski i Most Grunwaldzki (światło północne, brak przegrzewania). Opcjonalny kadr SW na Ślężę po weryfikacji widoczności | atrakcyjność i oryginalność, funkcja, eko | § 5.5 |
| 4 | Materiały jasne, ciepłe, matowe, mineralne. Granitowy cokół. Jeden ciepły akcent metaliczny. Bez ciemnego szkła w pierzejach od Oławy i mostu (te elewacje są w cieniu na F.17) | atrakcyjność, tkanka | § 5.5, § 6 |
| 5 | Segmentacja skrzydeł tonem i fakturą w wąskim zakresie, precedens Nowego Targu (moduły rozdzielone patiami lub uskokami) | tkanka (DWKZ) | § 4.2, § 6.3 |
| 6 | Parter i przedmoście jako zawias bulwaru Odry (Dunikowskiego – DUW) i nabrzeża Oławy (6KDB/2 – 4KDPL/3); punkt widokowy w miejscu dawnej przystani | dostępność, tkanka | § 2.3 |
| 7 | Jeden czytelny adres i dostęp bez barier dla rozproszonego dziś urzędu (deklaracja dostępności wymienia bariery); powiązanie z Mazowiecką 17/19 | dostępność i inkluzywność, funkcja | § 3 |
| 8 | Ochrona przed wiatrem przy wejściu u stóp dominanty (podcień lub zadaszenie). Tarasy po stronie E–SE. W opisie wzmianka o analizie komfortu wiatrowego | funkcja, dostępność | § 5.3 |
| 9 | Ochrona przed upałem: osłony pionowe na ENE i WSW, poziome na SSE, masa termiczna, nocne przewietrzanie, zieleń dziedzińca i dachów (wyspa ciepła latem +2,4 K) | eko (zeroemisyjność) | § 5.2, 5.4, 5.5 |
| 10 | Woda: retencja (dachy zielone, ogród deszczowy, zbiornik), „biała wanna”, krytyczne instalacje nad terenem, próg rampy | eko, realność | § 5.6 |
| 11 | Dach jako piąta elewacja (zielony, z BIPV w rysunku elewacji), bo jest widoczny na obu fotomontażach | atrakcyjność, eko | § 6.3 pkt 7 |
| 12 | Wizualizacje: F.17 – jesień, południe, cienie na N, elewacje ENE i NNW w cieniu. Ujęcie od mostu – letni wieczór (21 VI ok. 20:00 CEST, az 297°, wys. 8°) albo niebieska godzina z rozświetloną salą Sejmiku | jakość graficzna | § 5.5 |
| 13 | Narracja w języku planisty (osie, ciągi, linie zabudowy, kompozycja wysokościowa), bo Architekt Miasta i sędzia referent zasiadają w Zespole Architekta Miasta | wszystkie | § 4.3 |

---

## 8. Ryzyka, sprzeczności, luki

1. **ISOK a M.05 (powódź).** Rozbieżność opisana w § 5.6. Wymaga weryfikacji w iMap Hydroportalu. Do tego czasu stosować wariant ostrożny.
2. **Harmonogram remontu mostu** jest niepewny: 2027 (wroclaw.pl 2025), „nie wcześniej niż 2028” (wroclaw.pl 2026), 2028–2029 (źródło wtórne). Wpływa na decyzję, czy na ilustracjach dodatkowych pokazać hełmy.
3. **Kolor mostu po remoncie** nie jest przesądzony („być może pierwotna kolorystyka”). Paleta budynku nie powinna zależeć od błękitu.
4. **Architektura i data budowy siedziby przy Wybrzeżu Słowackiego 12–14** są potwierdzone tylko podpisami zdjęć w serwisie społecznościowym. Siedzib przy ul. Dobrzyńskiej i Matejki nie potwierdzono. Nie ustalono obecnej sali obrad Sejmiku.
5. **Plan ogólny 2026:** brak numeru uchwały i daty wejścia w życie w przeczytanym źródle. Strefy planistycznej dla terenu nie sprawdzono.
6. **Studium 2018** cytowane za publikacją naukową (Zakrzewska-Półtorak 2017, projekt Studium 2017), a nie za tekstem uchwalonym. Ewentualne różnice w wersji końcowej nie zostały sprawdzone.
7. **Dane klimatyczne** pochodzą z jednej stacji podmiejskiej (Strachowice). Usłonecznienie ma 6 braków miesięcznych. Wskaźniki (dni upalne, CDD) są liczone przez nas, nie przez IMGW, więc mogą się różnić od oficjalnych opracowań (np. Atlas klimatu Polski 1991–2020). Bezwzględne wartości dla centrum są wyższe (wyspa ciepła).
8. **Kolory z dronowych zdjęć** są przybliżone (obróbka Lightroom), więc NCS trzeba zmierzyć na miejscu.
9. **Strefy obciążeń śniegiem i wiatrem** nie są zweryfikowane w załącznikach krajowych PN-EN.
10. **Wypowiedzi Architekta Miasta** o pierzejach i wysokościowcach nie znaleziono. Wnioski z § 4.3 to interpretacja ról i składu Zespołu, a nie deklaracji programowych.
11. **Ślęża z sali Sejmiku:** widoczność niezweryfikowana. Nie wolno jej pokazać na wizualizacji wnętrza bez sprawdzenia (ryzyko zarzutu manipulacji).

---

## 9. Źródła (data dostępu: 16.11.2026, o ile nie podano inaczej)

### 9.1 Materiały konkursowe (lokalne)

- `00_materialy/tekst/1089_Regulamin_Konkursu_tekst_jednolity_13.02.2026-sig.txt`: skład Sądu Konkursowego (s. 11–12 druku, wiersze 658–686 pliku).
- `00_materialy/tekst/M.05._Opinia_geotechniczna.txt`: s. 6 (tab. 1, wody gruntowe, Hydroportal, PIG); rzędne terenu.
- `00_materialy/_rozpak/5_Zalaczniki_Merytoryczne_M.01-M.14_pop.13.02.2026/M.10. ZDJĘCIA OTOCZENIA/`: DJI_20251029113800_0009, …114154_0013, …114435_0015, …115736_0025, …115937_0027, …120544_0029, …120917_0032, …121030_0033, …121250_0036.
- `00_materialy/podglady/F17A_small.jpg`, `F17B_small.jpg`; `docs/10_regulamin/img/F17A_annot.jpg`, `F17B_annot.jpg`.
- `docs/20_program/program_tabela.csv` (serwerownia główna przy Wybrzeżu Słowackiego 12–14).

### 9.2 Źródła oficjalne i dane

- IMGW-PIB, dane publiczne: miesięczne synop (`…/dane_meteorologiczne/miesieczne/synop/`), terminowe synop (`…/terminowe/synop/`, pliki `*_424_s.zip`), dobowe synop (`…/dobowe/synop/`); stacja 351160424 WROCŁAW-STRACHOWICE: https://danepubliczne.imgw.pl/data/dane_pomiarowo_obserwacyjne/dane_meteorologiczne/
- KZGW / Wody Polskie, ISOK: usługa WMS INSPIRE MZP/MRP (GetCapabilities, GetMap, GetFeatureInfo, GetLegendGraphic): https://wody.isok.gov.pl/wss/INSPIRE/INSPIRE_NZ_HY_MZPMRP_WMS ; przeglądarka: https://wody.isok.gov.pl/imap_kzgw/?gpmap=gpMZP
- GUGiK, Geoportal, ortofotomapa WMS (podkład analizy ISOK): https://mapy.geoportal.gov.pl/wss/service/PZGIK/ORTO/WMS/HighResolution
- UMWD, Deklaracja dostępności (sporządzona 13.12.2021): https://umwd.dolnyslask.pl/fileadmin/user_upload/Deklaracje/UMWD_deklaracja_dostepnosci.pdf.old
- wroclaw.pl (serwis Urzędu Miejskiego Wrocławia):
  - T. Wysocki, „W trosce o jakość projektowania Wrocław powołuje Architekta Miasta. Został nim Jacek Barski”, 25.10.2024: https://www.wroclaw.pl/dla-mieszkanca/w-trosce-o-jakosc-projektowania-wroclaw-powoluje-architekta-miasta-zostal-nim-jacek-barski
  - „Zmiany w składzie Zespołu Architekta Miasta”, 11.05.2026: https://www.wroclaw.pl/dla-mieszkanca/zmiany-w-skladzie-zespolu-architekta-miasta
  - „Mamy plan ogólny. Wrocław uchwalił kluczowy dokument dla polityki przestrzennej”, 26.08.2026: https://www.wroclaw.pl/dla-mieszkanca/mamy-plan-ogolny-wroclaw-uchwalil-kluczowy-dokument-dla-polityki-przestrzennej
  - B. Chochołowski, „Estakada na placu Społecznym będzie wyburzona”, 22.01.2026: https://www.wroclaw.pl/komunikacja/estakada-na-placu-spolecznym-bedzie-wyburzona
  - B. Chochołowski, „Remont mostu Grunwaldzkiego. Odzyska kopuły, na razie tylko na projekcie”, 3.07.2025: https://www.wroclaw.pl/komunikacja/remont-mostu-grunwaldzkiego-odzyska-kopuly-na-razie-tylko-na-projekcie
  - „Konkurs architektoniczny Piękny Wrocław – poznaj wyniki 33. edycji”, 17.04.2026: https://www.wroclaw.pl/dla-mieszkanca/konkurs-architektoniczny-piekny-wroclaw-poznaj-wyniki-33-edycji-prestizowego-konkursu
  - J. Ratajczak, „Konkurs Piękny Wrocław – edycja XXX”, 1.12.2021: https://www.wroclaw.pl/przedsiebiorczy-wroclaw/konkurs-piekny-wroclaw-edycja-xxx
  - „Konkurs Piękny Wrocław – edycja XXXI”, 1.12.2021: https://www.wroclaw.pl/przedsiebiorczy-wroclaw/konkurs-piekny-wroclaw-edycja-xxxi
  - „Laureaci Pięknego Wrocławia: chcieliśmy architektury budzącej emocje”, 24.12.2023: https://www.wroclaw.pl/dla-mieszkanca/laureaci-pieknego-wroclawia-chcielismy-architektury-budzacej-emocje
  - „Nagroda Architektoniczna Polityki – w finale dwa wrocławskie obiekty”, 8.04.2020: https://www.wroclaw.pl/nagroda-architektoniczna-polityki-w-finale-dwa-wroclawskie-obiekty
  - M. Talik, wywiad z E. Kuryłowicz o budynku NFM, 3.07.2015: https://www.wroclaw.pl/kultura/budynek-nfm-wroclaw-opowiada-architekt-ewa-kurylowicz
  - „Nieznany Wrocław: tajemnice gmachu Urzędu Wojewódzkiego”, 22.09.2014 (archiwalny): https://www.wroclaw.pl/dla-mieszkanca/nieznany-wroclaw-tajemnice-gmachu-urzedu-wojewodzkiego-zdjecia-wideo
  - „Wielka woda. Powódź 1997…”, 12.07.2024: https://www.wroclaw.pl/dla-mieszkanca/wielka-woda-powodz-1997-mapa-hydropolis-zdjecia-zalanego-miasta
  - K. Gut, „Zmiany klimatyczne we Wrocławiu…”, 20.11.2024: https://www.wroclaw.pl/zielony-wroclaw/zmiany-klimatyczne-we-wroclawiu-coraz-cieplejsze-lata-i-zimy-jakie-sa-prognozy-na-przyszlosc
  - „Rewitalizacja bulwaru Xawerego Dunikowskiego (wizualizacje)”, 20.10.2014 (archiwalny): https://www.wroclaw.pl/dla-mieszkanca/rewitalizacja-bulwaru-xawerego-dunikowskiego-wizualizacje
  - „Rewitalizacja nabrzeży Oławy na Przedmieściu Oławskim”, 5.10.2015 (archiwalny): https://www.wroclaw.pl/rewitalizacja-nabrzezy-olawy-na-przedmiesciu-olawskim
  - „Przedmieście Oławskie – rewitalizacja”, 6.11.2014 (archiwalny): https://www.wroclaw.pl/dla-mieszkanca/przedmiescie-olawskie-rewitalizacja
  - R. Migdał, rozmowa z J. Barskim o Miejskim Konserwatorze Zabytków, 2.11.2022: https://www.wroclaw.pl/dla-mieszkanca/miejski-konserwator-zabytkow-wroclaw-rozmowa-jacek-barski-dyrektor-departamentu-strategii
  - Trasa „Mosty i przeprawy” (PDF; tylko fragment w wynikach wyszukiwania): https://www.wroclaw.pl/files/Turystyka/trasa_Mosty_przeprawy.pdf

### 9.3 Publikacje naukowe

- Zakrzewska-Półtorak A. (2017). *Location of high-rise buildings in Wrocław / Lokalizacja budynków wysokościowych we Wrocławiu*. Biblioteka Regionalisty 17, s. 111–118. DOI: 10.15611/br.2017.1.10. Pełny tekst: https://dbc.wroc.pl/Content/45461/Zakrzewska-Poltorak_Location_Of_High_Rise_Buildings_In_Wroclaw.pdf
- Szymanowski M., Drzeniecka-Osiadacz A., Sawiński T., Kryza M. (2019). *Historia i współczesność badań nad klimatem Wrocławia – pomiary i badania modelowe*. Acta Geographica Lodziensia 108, s. 109–126. DOI: 10.26485/AGL/2019/108/8. https://journals.ltn.lodz.pl/Acta-Geographica-Lodziensia/article/view/555 (cytowane za nim: Szymanowski M. 2004, *Miejska wyspa ciepła we Wrocławiu*; Suder A., Szymanowski M. 2014, korytarze przewietrzania Wrocławia).
- Świtlińska-Robutka J. (2002). *Analiza kompozycji przestrzennej Przedmieścia Oławskiego we Wrocławiu*. Architectus 1, s. 145–149 (za `historia.md`).

### 9.4 Źródła wtórne (portale i serwisy; oznaczone [Ź-wt])

- polska-org.pl, ul. Wybrzeże Słowackiego Juliusza: https://polska-org.pl/587229,Wroclaw,ul_Wybrzeze_Slowackiego_Juliusza.html (lista obiektów).
- polska-org.pl, obiekt 547250 „Urząd Marszałkowski Województwa Dolnośląskiego (Wybrzeże Słowackiego)” (istniejąca siedziba nr 12–14) i podstrony zdjęć 747449, 9822298: https://polska-org.pl/547250,Wroclaw,Urzad_Marszalkowski_Wojewodztwa_Dolnoslaskiego_Wybrzeze_Slowackiego.html. **Metoda bezpieczeństwa:** stronę pobrano curl-em i przepuszczono przez filtr słów zakazanych (konkurs, nagrod*, zwyci*, wyróżn*, wizualiz*, koncepc*, pracowni*, nowa siedziba, SARP, 2025, 2026, sejmik). Wynik: **0 trafień**. Dopiero potem odczytano podpisy zdjęć (lata 1950–2020).
- fotopolska.eu, Most Grunwaldzki (opis rejestrowy; tylko fragment w wynikach wyszukiwania): https://fotopolska.eu/1446371,foto.html
- pl.wikipedia, „Most Grunwaldzki we Wrocławiu” (za `historia.md`); en.wikipedia, „1997 Central European flood in Wrocław”: https://en.wikipedia.org/wiki/1997_Central_European_flood_in_Wroc%C5%82aw
- Polskie Radio, English Section (2024; kulminacja 19.09.2024, Trestno 631 cm; wg wyników wyszukiwania): https://polskieradio.pl/395/7784/artykul/3428648,oder-river-falls-below-alarm-level-in-wroclaw-flood-situation-under-control oraz https://polskieradio.pl/395/7784/Artykul/3427451,polands-flood-situation-stabilizes
- klinkier.pl (The Bridge, elewacja klinkierowa; wg wyników wyszukiwania): https://klinkier.pl/en/the-bridge-hotel-wroclaw/ ; Accor MGallery: https://mgallery.accor.com/en/hotels/B1Z1/story.html
- Concordia Design (MVRDV, Q2/QStudio, 2018–2020; wg wyników wyszukiwania): https://architizer.com/projects/concordia-design-wroclaw ; https://aluprof.com/gb/company/news/concordia-design-on-wroclaw-s-slodowa-island-opens-its-doors
- In Your Pocket, DUW (F. Bräuler): https://www.inyourpocket.com/wroclaw/lower-silesian-voivodship-office_156086v
- Poczta Główna (L. Neumann, 1926–1929): https://archiweb.cz/en/b/postovni-urad-ve-vratislavi-muzeum-poczty-i-telekomunikacji ; https://www.wroclaw.pl/dla-mieszkanca/poczta-ulica-krasinskiego-pierwszy-wiezowiec-we-wroclawiu (wg wyników wyszukiwania)
- Rewitalizacja Przedmieścia Oławskiego, CAL, „Trójkąt Bermudzki” (tylko fragmenty w wynikach wyszukiwania): https://www.wroclaw.pl/rozmawia/mapa-rewitalizacji-przedmiescie-olawskie ; https://bip.um.wroc.pl/attachments/download/62430
- Interpelacja ws. pl. Społecznego, EBI (fragment w wynikach wyszukiwania; pełny tekst niedostępny, 503): https://bip.um.wroc.pl/attachments/download/165881
- Ogólne opracowania stref obciążeń wg Eurokodów (śnieg, wiatr): https://staff.uz.zgora.pl/akucharczyk/pliki/KB-O/Obciazenia%20klimatyczne.pdf ; https://inzynierbudownictwa.pl/obciazenie-sniegiem-wg-eurokodu-1-norma-pn-en-1991-1-3/

### 9.5 Źródła odrzucone, nieotwierane lub niedostępne

- **ODRZUCONE, nieotwierane (zakaz Inwestora):** https://www.wroclaw.pl/przedsiebiorczy-wroclaw/nowy-budynek-marszalkowskiego-we-wroclawiu-wyniki-wizualizacje. Tytuł z wyników wyszukiwania wskazuje na wyniki tego konkursu. Nie otwierano i nic z niego nie notowano.
- polska-org.pl, „Konkurs urbanistyczny na Plac Społeczny 2007” (id 523045): nieotwierane (za `historia.md` § 8.3).
- whitemad.pl, wprost.pl, kb.pl: artykuły o sporze wokół hełmów i napisu na moście. Nie używano treści.
- **Niedostępne technicznie (bez lektury):**
  - wprost.pl/11352610 „Wysoko czy nisko?” (403);
  - strefakultury.pl, „5 pytań do…” (2021) (404);
  - architekturaibiznes.pl „Wrocław standards” (403);
  - link.springer.com 10.1007/s00024-013-0659-9 (wymaga logowania);
  - wroclawskiefakty.pl „Nowa odsłona nabrzeży rzeki Oławy” (404);
  - yadda.icm.edu.pl, Łukaszewicz „Kolor i plastyka…” (zwrócono HTML zamiast PDF).
