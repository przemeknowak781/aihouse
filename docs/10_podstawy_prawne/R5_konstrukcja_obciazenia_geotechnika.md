# R5 — Konstrukcja, obciążenia, geotechnika (Eurokody + NA) — rejestr wymagań dla „Dom LAMELA”

Wersja: 1.0 (2026-09-25). Zespół R5. Lokalizacja obliczeniowa: strefa podmiejska Poznania (pow. poznański),
A ≈ 101 m n.p.m. wg briefu (rzędna ±0,00 = 101,65 m; wartość z polecenia „80–90 m” nie zmienia żadnego wyniku — patrz R5-30, R5-40).
Pliki robocze, pobrane źródła i skrypty: `scratchpad/research/R5/` (m.in. `zones_check.py` + `zones_check.txt` — weryfikacja stref śniegu i wiatru).

Oznaczenia: **P** = źródło pierwotne (Dz.U. przez API ELI Sejmu, dokument urzędowy PKN/ITB); **W** = źródło wtórne (podręcznik,
publikacja naukowa lub branżowa, materiały producenta, oprogramowanie); **NIEZWERYFIKOWANE** = brak potwierdzenia w dostępnym źródle
(pełna treść norm jest płatna i nie była dostępna, a sklep PKN zwracał w czasie badania błędy HTTP 503 i błędy TLS).

---

## 1. Streszczenie

1. **Które normy stosować.** Konstrukcję projektujemy wg **Eurokodów 1. generacji w wersji polskiej z Załącznikami krajowymi (NA)**.
   Według PKN (strona zaktualizowana w czerwcu 2026 r.) 2. generacja ma być wprowadzona do 30.09.2027 r., a 1. generacja wycofana do 31.03.2028 r.
   Generacji nie wolno mieszać, a NA do 2. generacji powstaną później. Załącznik 1 do WT (poz. 49, przypis *) i **) wskazuje Eurokody
   „zatwierdzone i opublikowane w języku polskim”, stanowiące kompletny zestaw. Normy 2. generacji (np. PN-EN 1992-1-1:2024-05)
   są dostępne tylko po angielsku i nie tworzą jeszcze kompletnego zestawu.
2. **ISTOTNA KOREKTA BRIEFU — śnieg:** Poznań i cały powiat poznański leżą w **strefie 2**, nie w strefie 1:
   **s_k = 0,9 kN/m²**, a nie 0,7 kN/m². Sprawdzono to na poligonach mapy NA:2010 (Dlubal Geo-Zone, 12 miejscowości). Potwierdza to też
   publikacja w „Inżynierze Budownictwa” (2019). *Weryfikacja:* granica strefy 1 leży ok. 33 km na SSW od centrum Poznania
   i ok. 14 km od Mosiny, a nie „ponad 60 km na zachód”. Przykład Xella dotyczy Warszawy (R5-30).
   *Weryfikacja:* NA wymaga także **wyjątkowej sytuacji B2** (zaspy wg zał. B) — R5-33, R5-38.
3. **ISTOTNA KOREKTA BRIEFU — kategoria geotechniczna:** budynek ma **3 kondygnacje nadziemne**, wsporniki i statycznie niewyznaczalne
   stropy monolityczne, więc **nie mieści się w I kategorii** (§ 4 ust. 3 pkt 1 lit. a rozporządzenia Dz.U. 2012 poz. 463 obejmuje
   „1- lub 2-kondygnacyjne budynki mieszkalne” o statycznie wyznaczalnym schemacie). Przyjmujemy **II kategorię geotechniczną**.
   Wymaga ona opinii geotechnicznej, **dokumentacji badań podłoża gruntowego** i **projektu geotechnicznego** (§ 7 ust. 2).
   Rozporządzenie ma w ELI status „obowiązujący”, a jego podstawa (art. 34 ust. 6 pkt 2 Pb) nadal istnieje w t.j. Dz.U. 2026 poz. 524.
4. **Wiatr:** strefa 1 (potwierdzona na mapie NA): v_b,0 = 22 m/s, q_b = 0,30 kN/m². Dla h ≈ 10,5 m:
   q_p = 0,58 kN/m² przy terenie kategorii III i 0,70 kN/m² przy kategorii II (c_e = 2,3·(z/10)^0,24 wg NA; dla h = 11,0 m: 0,71).
   Od południa działka graniczy z terenem rolnym, dlatego proponujemy obwiednię **q_p = 0,71 kN/m²**.
5. **Kombinacje (PN-EN 1990 + NA):** NA zaleca **mniej korzystne z wyrażeń 6.10a i 6.10b** (γ_G = 1,35; ξ = 0,85, czyli ξ·γ_G = 1,15;
   γ_Q = 1,5). Klasa konsekwencji dla budynku mieszkalnego to wg zał. B **CC2/RC2 (K_FI = 1,0)**, nie CC1. Klasa CC1 dotyczy wyłącznie
   klasyfikacji odporności na oddziaływania wyjątkowe wg PN-EN 1991-1-7 (dom jednorodzinny do 4 kondygnacji).
6. **Beton (PN-EN 1992-1-1 + NA):** γ_c = 1,4 (NA; wartość europejska to 1,5), γ_s = 1,15. c_min,dur przy klasie konstrukcji S4:
   XC1 = 15 mm, XC2/XC3 = 25 mm, XC4 = 30 mm, Δc_dev = 10 mm. Wskazane klasy betonu: XC1 → C20/25, XC2 → C25/30,
   XC3/XC4/XF1 → C30/37. Stal B500SP (klasa ciągliwości C).
7. **Mur z silikatów (PN-EN 1996-1-1+A1 + NA):** K = 0,60 dla silikatów grupy 1 na zaprawie do cienkich spoin (poprawka NA Ap2:2014-09).
   Dla klasy 20: f_k = 0,60·20^0,85 = **7,66 MPa**, γ_M = 1,7 (klasa wykonania A) lub 2,0 (klasa B), f_d = 4,50 / 3,83 MPa.
8. **Geotechnika (PN-EN 1997-1 + NA):** do nośności podłoża stosujemy **DA2*** (A1+M1+R2, γ_R;v = 1,4, γ_R;h = 1,1;
   opór graniczny liczony z charakterystycznych efektów oddziaływań). W średnio zagęszczonych piaskach średnich (Ps, I_D ≈ 0,6)
   nośność ław z dużym zapasem pokrywa obciążenia domu; decydują osiadania i względy konstrukcyjne.
9. **Przemarzanie:** PN-B-03020:1981 **wycofano 31.03.2010 r.** (PKN) i żadna norma PN-EN nie zawiera mapy stref przemarzania.
   Praktyka nadal korzysta z mapy PN-81 (h_z = 0,8 m dla Poznania, strefa I). Według PKN wycofanie normy nie oznacza zakazu jej stosowania.
   Wymóg posadowienia na głębokości ≥ h_z dotyczy tylko **gruntów wysadzinowych**. Piaski średnie do nich nie należą; obowiązuje wtedy
   zagłębienie ≥ 0,5 m. Badania ITB (Żurański i Godlewski, 2017–2018) dają jednak dla stacji Poznań 50-letnią głębokość izotermy 0 °C
   równą 1,31 m. Zalecamy więc posadowienie ≥ 0,8 m p.p.t., a dla ścian zewnętrznych i stóp wiaty 1,0 m. Przykrycie przewodów wodnych:
   ≥ h_z + 0,4 m = 1,2 m.
10. **Pożar:** zgodnie z WT § 213 pkt 1 lit. a wymagania § 212 (klasa odporności pożarowej) i § 216 (klasy R/REI elementów)
    **nie dotyczą** budynku mieszkalnego jednorodzinnego do 3 kondygnacji nadziemnych. Dla Dom LAMELA **nie ma wymagań R**
    wobec konstrukcji. Status WT wymaga potwierdzenia przez R3: w ELI ma on status „uznany za uchylony” z datą 2026-09-21.
11. **Projektowa temperatura zewnętrzna:** Poznań leży w **strefie klimatycznej II**: θ_e = **−18 °C**, średnia roczna θ_m,e = **7,9 °C**
    (NA do PN-EN 12831:2006). Czy PN-EN 12831-1:2017-08 wprowadza zmiany w tych wartościach — NIEZWERYFIKOWANE (zespół instalacyjny).

---

## 2. Rejestr wymagań

### 2.A Status norm i przepisów, forma dokumentacji konstrukcyjnej

| ID | Wymaganie / reguła (konkretnie) | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-01 | Eurokody 2. edycji mają być wprowadzone do PN do **30.09.2027 r.**, a 1. edycja wycofana do **31.03.2028 r.** (koniec okresu przejściowego CEN). „Nie należy mieszać Eurokodów z 1. edycji i 2. edycji”. NA do 2. edycji zostaną „opracowane w czasie późniejszym”. | PKN, strona „Eurokody” (aktualizacja: czerwiec 2026 r.) | https://www.pkn.pl/normalizacja/sektory-normalizacji/budownictwo-i-konstrukcje-budowlane/eurokody | P | Stan na dzień badania. |
| R5-02 | „Jeśli komplet norm potrzebnych do zaprojektowania konstrukcji nie został jeszcze opublikowany w ramach 2. edycji Eurokodów, to stosuje się 1. edycję.” Aktualne NA (1. edycja, wersje polskie): PN-EN 1990:2004/NA:2010 (+A1:2008); PN-EN 1991-1-1:2004/NA:2010 (+AC:2009, Ap1:2010, Ap2:2011); PN-EN 1991-1-3:2005/NA:2010 (+AC:2009, Ap1:2010); PN-EN 1991-1-4:2008/NA:2010 (+AC, Ap1–Ap3:2011, A1:2010); PN-EN 1991-1-7:2008/NA:2015-02; **PN-EN 1992-1-1:2008/NA:2018-11** (po Ap2:2016-10 i Ap3:2018-08); PN-EN 1993-1-1:2006/NA:2010 (+A1:2014-07); **PN-EN 1996-1-1+A1:2013-05/NA:2014-03** (+Ap2:2014-09, Ap3:2016-04); PN-EN 1997-1:2008/NA:2011 (+AC:2009, Ap1/Ap2:2010, A1:2014-05). | ITB/PKN, „EUROKODY 1. edycja – wprowadzanie do zbioru PN – stan na 30 sierpnia 2024 r.” oraz PKN Zał. B (stan na 31.10.2023 r.) | https://www.itb.pl/wp-content/uploads/2025/05/1-edycja-EUROKODOW-wprowadzenie-do-zbioru-Polskich-Norm-stan-na-30-sierpnia-2024-r.pdf ; https://wiedza.pkn.pl/documents/14137/31883/Za%C5%82%C4%85cznik+B_Eurokody.pdf/97bf1e36-2c0c-4f50-8ed5-01c068ddd995 | P | Na liście z 2024 r. są już normy 2. edycji: PN-EN 1992-1-1:2024-05 (ang.) i PN-EN 1996-1-1:2023-08 (ang.). Nie tworzą one kompletu; nie stosować w projekcie. Zmiany z NA:2016 i NA:2018 do EC2 (m.in. rozdz. 5 i 6, zał. C i G) — treść NIEZWERYFIKOWANA. |
| R5-03 | § 204 ust. 4 WT: warunki bezpieczeństwa konstrukcji uznaje się za spełnione, jeżeli konstrukcja odpowiada PN dotyczącym projektowania. Zał. 1 poz. 49 wymienia PN-EN 1990–1999 („wszystkie części norm”). Przypis *): Eurokody „zatwierdzone i opublikowane w języku polskim” stosuje się, jeżeli stanowią **kompletny zestaw**; zawsze wymagane są PN-EN 1990 i PN-EN 1991. Przypis **): przy powołaniu niedatowanym stosuje się **najnowszą normę opublikowaną w języku polskim**. | WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) § 204 ust. 1–4, Zał. 1 poz. 49 wraz z przypisami | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | **Status WT do potwierdzenia przez R3.** W ELI: „uznany za uchylony”, repealDate 2026-09-21, „Uchylenia wynikające z: DU/2019/1696” (ustawa o zapewnianiu dostępności). |
| R5-04 | § 204 ust. 3 WT: w konstrukcji nie mogą wystąpić rysy ani lokalne uszkodzenia, odkształcenia lub przemieszczenia pogarszające przydatność, uszkadzające części niekonstrukcyjne i wykończenie, ani drgania dokuczliwe dla ludzi. **PN-B-02171:2017-06** „Ocena wpływu drgań na ludzi w budynkach” (PKN: aktualna) WT powołuje w Zał. 1 **poz. 2 (§ 96 ust. 1 — pomieszczenia techniczne z urządzeniami emitującymi drgania)** i **poz. 48 (§ 196 ust. 2 i 3 — dźwigi)**, a nie przy § 204 ust. 3. Dla § 204 ust. 3 PN-B-02171 jest tylko źródłem wiedzy technicznej. | WT § 204 ust. 3; § 96 ust. 1; Zał. 1 poz. 2 i 48 | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | *Poprawione w weryfikacji* (było: „Zał. 1 poz. 48 powołuje PN-B-02171 do § 204 ust. 3”). Dla Dom LAMELA ważne jest § 96 ust. 1: pomieszczenie techniczne z pompą ciepła/rekuperatorem przy pokojach. Status WT — R3 (art. 102a PB). |
| R5-05 | Pb art. 34 ust. 3: **PAB** zawiera „opinię geotechniczną oraz informację o sposobie posadowienia” (pkt 2 lit. d). **PT** zawiera „projektowane rozwiązania konstrukcyjne obiektu wraz z wynikami obliczeń statyczno-wytrzymałościowych” (pkt 3 lit. a) oraz, zależnie od potrzeb, „geotechniczne warunki posadowienia” (pkt 3 lit. d). PT musi być zgodny z PZT i PAB (ust. 3c). | Pb, t.j. Dz.U. 2026 poz. 524, art. 34 ust. 3 i 3c | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P | Nowele Dz.U. 2026 poz. 605, 646 i 1161 nie zmieniają art. 20 ani art. 34 ust. 3 (sprawdzono ich teksty). |
| R5-06 | Część opisowa PAB zawiera „opinię geotechniczną oraz informację o sposobie posadowienia” (§ 20 ust. 1 pkt 5). Część opisowa PT zawiera: rozwiązania konstrukcyjne, schematy statyczne, założenia obliczeń (w tym obciążenia), podstawowe wyniki obliczeń, rozwiązania konstrukcyjno-materiałowe (§ 23 pkt 1). Geotechniczne warunki i sposób posadowienia przedstawia się „w formie dokumentacji badań podłoża gruntowego i projektu geotechnicznego” (§ 23 pkt 2). | Rozp. MRPiT w sprawie szczegółowego zakresu i formy projektu budowlanego, t.j. Dz.U. 2022 poz. 1679, § 20 ust. 1 pkt 5, § 23 pkt 1–2 | https://api.sejm.gov.pl/eli/acts/DU/2022/1679/text.pdf | P | Zmiana Dz.U. 2026 poz. 597 (ogłoszona 04.05.2026) dotyczy dostępności, ochrony ludności i dokładności wymiarów w PZT. Nie zmienia § 20 ust. 1 pkt 5 ani § 23 pkt 1–2. *Uściślone w weryfikacji:* w życie 19.05.2026 weszła tylko część zmian. § 1 pkt 3 lit. b (wymiary w PZT z dokładnością 0,01 m, nowy § 15 ust. 3) i pkt 4 lit. a (§ 20 ust. 1 pkt 8) wchodzą w życie „po upływie 6 miesięcy od dnia ogłoszenia” (§ 3), czyli wg wyliczenia 05.11.2026. Przepisy przejściowe są w § 2 ust. 2–3. |
| R5-07 | Obowiązek sprawdzenia PAB i PT przez osobę z uprawnieniami bez ograniczeń (art. 20 ust. 2) **nie dotyczy** „projektów obiektów budowlanych o prostej konstrukcji, jak: budynki mieszkalne jednorodzinne” (art. 20 ust. 3 pkt 2). | Pb art. 20 ust. 2–3 | https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P | Rekomendacja R5: ze względu na wsporniki (bryła P2, płyta D) wykonać **dobrowolne sprawdzenie części konstrukcyjnej**. |

### 2.B PN-EN 1990 — podstawy projektowania

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-10 | STR/GEO, sytuacja trwała i przejściowa: NA **zaleca mniej korzystne z wyrażeń 6.10a i 6.10b**. Współczynniki: γ_G,sup = 1,35; γ_G,inf = 1,00; γ_Q = 1,50 (0 przy działaniu korzystnym); ξ = 0,85, czyli ξ·γ_G = 1,15. Dla jednego oddziaływania zmiennego kategorii A: 1,35·G_k + 1,05·Q_k albo 1,15·G_k + 1,5·Q_k. EQU: γ_G,sup = 1,10, γ_G,inf = 0,90, γ_Q = 1,50. Zestaw C (stateczność): 1,00 / 1,30. | PN-EN 1990:2004 + A1 + NA:2010, pkt 6.4.3.2, Tabl. A1.2(A–C) | http://pobierz.intersoft.pl/konkurs/EUROKODY/EUROKODY-Podstawy-projektowania-konstrukcji.pdf ; https://graitec.com/pl/blog/jak-stworzyc-kombinacje-wedlug-eurokodu-0-poznaj-blizej-ec0/ ; https://mjurkiewicz.weebly.com/uploads/2/5/1/8/25183076/wst%C4%99p_do_projektowania_konstrukcji_%C5%BCelbetowych_wg_pn-en_1992-1-1_2008_-_janusz_p%C4%99dziwiatr.pdf | W | Trzy niezależne źródła wtórne (Intersoft „Eurokody – praktyczne komentarze”, GRAITEC 2020, J. Pędziwiatr, DWE 2010) są zgodne. Treść NA nie była dostępna. |
| R5-11 | Wartości ψ₀/ψ₁/ψ₂: kategoria A: 0,7/0,5/0,3; kategoria H (dachy): 0/0/0; śnieg dla A ≤ 1000 m n.p.m.: 0,5/0,2/**0**; wiatr: 0,6/0,2/0; temperatura: ψ₀ = 0,6. | PN-EN 1990, Tabl. A1.1 (+ poprawka Ap1 dla ψ₂ śniegu) | http://www.pg.gda.pl/~krogu/Przyklad%20obliczeniowyx.pdf ; https://graitec.com/pl/blog/jak-stworzyc-kombinacje-wedlug-eurokodu-0-poznaj-blizej-ec0/ ; https://storefrontapi.commerce.xella.com/medias/sys_master/root/hee/h78/8850504450078/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03.pdf | W | GRAITEC: „poprawka Ap1 zmienia ψ₂ [śniegu] na 0” dla A < 1000 m. ψ₁ i ψ₂ dla temperatury (0,5/0) — NIEZWERYFIKOWANE; w domu jednorodzinnym bez znaczenia. |
| R5-12 | Klasy konsekwencji (Zał. B, Tabl. B1): **CC2** obejmuje budynki „użyteczności publicznej, mieszkalne, biurowe” o przeciętnych skutkach zniszczenia. CC1 to budynki rolnicze, w których ludzie zwykle nie przebywają, i szklarnie. RC1/RC2/RC3 → K_FI = 0,9 / 1,0 / 1,1. | PN-EN 1990, Zał. B (informacyjny), Tabl. B1, B3 | https://dos.piib.org.pl/wp-content/uploads/2020/03/1353512009_czesc-1-7.pdf ; http://pobierz.intersoft.pl/konkurs/EUROKODY/EUROKODY-Podstawy-projektowania-konstrukcji.pdf | W | Odpowiedź na pytanie z briefu („CC1/RC1?”): według przykładów Tabl. B1 dom jednorodzinny to **CC2/RC2, K_FI = 1,0**. Nie redukować obciążeń współczynnikiem 0,9. |
| R5-13 | PN-EN 1991-1-7, Zał. A, Tabl. A.1: **CC1** = „single occupancy houses not exceeding 4 storeys”. Dla CC1 wystarcza projekt wg PN-EN 1990–1999; szczególna analiza oddziaływań wyjątkowych z nieokreślonych przyczyn nie jest wymagana. | PN-EN 1991-1-7:2008 (+NA:2015-02), Zał. A, Tabl. A.1, p. A.4 | https://www.steelconstruction.info/Structural_robustness | W | Rozstrzygnięcie w PL NA:2015-02, czy Zał. A jest normatywny — NIEZWERYFIKOWANE. Nie ma to wpływu na projekt, bo i tak stosujemy wieńce i ściągi wg PN-EN 1992-1-1 p. 9.10 oraz PN-EN 1996. |
| R5-14 | Projektowy okres użytkowania: kategoria 4 („konstrukcje budynków i inne zwykłe”) = **50 lat**, co odpowiada klasie konstrukcji **S4** w PN-EN 1992-1-1. | PN-EN 1990, Tabl. 2.1; PN-EN 1992-1-1 p. 4.4.1.2 | https://www.przegladbudowlany.pl/2018/10/2018-10-PB-15-PROBL-Zybura-Zagadnienia.pdf | W | Zybura i Śliwka, Przegląd Budowlany 10/2018. |

### 2.C PN-EN 1991-1-1 — ciężary i obciążenia użytkowe

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-20 | Kategoria A (powierzchnie mieszkalne), przedziały EN: stropy q_k = 1,5–2,0 kN/m²; schody q_k = 2,0–4,0 kN/m²; balkony q_k = 2,5–4,0 kN/m²; Q_k w przedziale 2,0–3,0 kN (dla schodów do 4,0 kN). W przykładach projektowych dla stropów kategorii A przyjmuje się 2,0 kN/m². | PN-EN 1991-1-1:2004, Tabl. 6.1–6.2 (+NA:2010) | https://wbia.pollub.pl/fcp/8PREgARcJNScXKxEMUA9DBXljWXdFEjNQZ18Qc21Xcgpmc2oRPBIWBHJ-QQQUSg8/_global/public/wbia/files/81/attachment/354503.pdf ; https://www.specbud.pl/uploads/reports/SPECBUD_KONEN_Notka.pdf ; https://inzynierbudownictwa.pl/zestawianie-obciazen-zmiennych-wedlug-pn-en-1991-1-1-cz-i/ | W | **Wartości wybrane w PL NA — NIEZWERYFIKOWANE.** Według A. Rawskiej-Skotniczny (IB 2013) „polski załącznik krajowy jest wyjątkowo ubogi”. W projekcie przyjmujemy **górne granice przedziałów**, bezpieczne niezależnie od wyboru dokonanego w NA (sekcja 3.3). |
| R5-21 | Zastępcze obciążenie od przestawnych ścianek działowych, gdy strop zapewnia rozdział poprzeczny: ciężar ścianki ≤ 1,0 kN/m → q_k = 0,5 kN/m²; ≤ 2,0 kN/m → 0,8 kN/m²; ≤ 3,0 kN/m → 1,2 kN/m². Ścianki cięższe uwzględnia się jako rzeczywiste obciążenia liniowe. | PN-EN 1991-1-1 p. 6.3.1.2(8)–(9) | https://storefrontapi.commerce.xella.com/medias/sys_master/root/hee/h78/8850504450078/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03.pdf ; https://www.specbud.pl/uploads/reports/SPECBUD_KONEN2_Notka.pdf | W | Ścianka z silikatów 8 cm z tynkiem, h ≈ 2,6 m, waży ok. 4,5–5 kN/m (szacunek R5), czyli więcej niż 3 kN/m → **obciążenie liniowe w modelu**. |
| R5-22 | Dachy kategorii H (bez dostępu, poza utrzymaniem): NA przyjmuje **q_k = 0,4 kN/m²** i **Q_k = 1,0 kN** (przedziały EN: 0–1,0 kN/m² oraz 0,9–1,5 kN). Oba przypadki sprawdza się oddzielnie. | PN-EN 1991-1-1 p. 6.3.4.2, Tabl. 6.10 + NA | https://www.izolacje.com.pl/artykul/instalacje/175823,wybrane-zagadnienia-projektowania-dachow-plaskich | W | S. Dudziak, IZOLACJE 10/2016: „wartość zalecana przez załącznik krajowy to 1,0 kN … 0,4 kN/m²”. |
| R5-23 | Obciążenia użytkowego dachu nie przykłada się jednocześnie z obciążeniem śniegiem ani z wiatrem. | PN-EN 1991-1-1 p. 3.3.2(1); PN-EN 1990 zał. A1 | http://pobierz.intersoft.pl/konkurs/EUROKODY/EUROKODY-Podstawy-projektowania-konstrukcji.pdf | W | Dotyczy dachów kategorii H oraz tarasu na płycie D. Na tarasie decyduje większa z wartości: q_k tarasu albo śnieg z zaspą. |
| R5-24 | Dachy dostępne (kategoria I): obciążenie użytkowe przyjmuje się wg kategorii użytkowania A–D. Taras mieszkalny odpowiada balkonowi kategorii A. | PN-EN 1991-1-1 p. 6.3.4.1, Tabl. 6.9 | https://www.izolacje.com.pl/artykul/instalacje/175823,wybrane-zagadnienia-projektowania-dachow-plaskich | W | Taras na płycie D i ewentualne wyjścia na dach P1. |
| R5-25 | Ciężar objętościowy żelbetu: 25 kN/m³ (24 + 1 na zbrojenie). | PN-EN 1991-1-1, Zał. A, Tabl. A.1 | https://www.specbud.pl/uploads/reports/SPECBUD_KONEN2_Notka.pdf | W | Ciężary warstw przyjmować z deklaracji producentów (DWU). |

### 2.D PN-EN 1991-1-3 — śnieg

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-30 | **Poznań i powiat poznański: strefa 2 → s_k = 0,9 kN/m²** (w strefie 2 wartość stała, niezależna od A). Wzory NA dla stref: 1: s_k = 0,007A − 1,4 ≥ 0,70; 2: 0,9; 3: 0,006A − 0,6 ≥ 1,2; 4: 1,6; 5: 0,93·exp(0,00134A) ≥ 2,0 kN/m². | PN-EN 1991-1-3:2005 + AC:2009 + Ap1:2010 + NA:2010, rys. NA.1 | https://loadzones.dlubal.com/file.aspx?kml=snow-pn-en-1991-1-3-l46-v2384.kml ; https://www.dlubal.com/pl/strefy-obciazenia-sniegiem-wiatrem-trzesieniem-ziemi/snieg-pn-en-1991-1-3.html ; https://inzynierbudownictwa.pl/obciazenie-sniegiem-wg-eurokodu-1-norma-pn-en-1991-1-3/ | W | Test punkt-w-wielokącie (skrypt `zones_check.py`): Poznań, Swarzędz, Komorniki, Suchy Las, Kórnik, Buk, Murowana Goślina, Stęszew, Luboń, Tarnowo Podgórne, Kostrzyn, Mosina — wszystkie w strefie 2. Potwierdza to O. Donajko (IB 2019): „strefa 2 … (np. Poznań, Warszawa)”. Niektóre portale branżowe podają błędnie strefę 1. **Brief (0,7 kN/m²) do korekty.** *Poprawione w weryfikacji:* (a) poradnik Xella nie dotyczy Poznania; jego przykład to „II strefa śniegowa (Warszawa)”, więc nie potwierdza strefy dla Poznania. (b) Granica strefy 1 nie leży „ponad 60 km na zachód”. Według tego samego KML najbliższy wierzchołek strefy 1 jest ok. **33 km na SSW od centrum Poznania** (rejon Czempinia i Kościana, 52,11°N 16,86°E) i ok. **14 km od Mosiny**. Kościan leży już w strefie 1. Na 52,40°N strefa 1 obejmuje ok. 14,6–15,4°E. **Dla działki w południowej części powiatu (Mosina, Stęszew) strefę sprawdzić na mapie NA dla konkretnej lokalizacji.** |
| R5-31 | Współczynnik ekspozycji C_e: 0,8 (teren wystawiony na wiatr), **1,0 (teren normalny)**, 1,2 (teren osłonięty). Współczynnik termiczny C_t = 1,0. | PN-EN 1991-1-3 p. 5.2(7)–(8), Tabl. 5.1 | http://www.pg.gda.pl/~krogu/Przyklad%20obliczeniowyx.pdf | W | Teren podmiejski z sąsiednią zabudową, więc C_e = 1,0. Dachy ocieplone, więc C_t = 1,0. |
| R5-32 | Dach płaski (0° ≤ α ≤ 30°): μ₁ = 0,8, s = μ₁·C_e·C_t·s_k = **0,72 kN/m²**. | PN-EN 1991-1-3 p. 5.3.2, Tabl. 5.2 | https://www.specbud.pl/uploads/reports/SPECBUD_KONEN2_Notka.pdf | W | — |
| R5-33 | *Poprawione w weryfikacji.* W Polsce wg NA **nie uwzględnia się wyjątkowych opadów śniegu** (przypadki B1 i B3). NA **nakazuje jednak rozpatrywać przypadek B2**, czyli wyjątkowe zamiecie bez wyjątkowych opadów. Są więc dwie sytuacje: (1) trwała i przejściowa, przypadek A: s = μ_i·C_e·C_t·s_k wg rozdz. 5 i 6; (2) **wyjątkowa, zaspy wg zał. B**: s = μ_i·s_k, gdzie μ_i z zał. B dla kształtów tam ujętych: B.3 dach przy wyższej budowli, B.4 attyki i przeszkody. | PN-EN 1991-1-3 p. 3.2–3.3, zał. B + NA | https://inzynierbudownictwa.pl/wplyw-ksztaltu-dachu-na-jego-obciazenie-sniegiem-cz-ii/ ; https://inzynierbudownictwa.pl/obciazenie-sniegiem-wg-eurokodu-1-norma-pn-en-1991-1-3/ ; https://silo.tips/download/obcienie-niegiem-i-oddziaywania-wiatru-wedug-pn-en-1991 | W | Było: „nie uwzględnia się wyjątkowych opadów ani wyjątkowych zamieci”. Cytat z Intersoft dotyczy tylko **opadów**. IB: „Załącznik krajowy … nakazuje uwzględniać przypadek B2, kiedy występują wyjątkowe zamiecie śnieżne i na dachach powstają zaspy śnieżne”. To samo podaje drugie, niezależne opracowanie (silo.tips): „warunki wyjątkowe … (przypadek B2)”. Wzory zał. B — patrz R5-38 (NIEZWERYFIKOWANE). |
| R5-34 | Dach przylegający do wyższej części budowli (uskok brył P0/P1, P1/P2, taras D przy boksie C): μ₂ = μ_s + μ_w; μ_w = (b₁ + b₂)/(2h) ≤ γ·h/s_k, γ = 2 kN/m³, **0,8 ≤ μ_w ≤ 4,0**; μ_s = 0, gdy α wyższego dachu ≤ 15°. Długość zaspy l_s = 2h, przy czym **5 m ≤ l_s ≤ 15 m**. Jeżeli b₂ < l_s, zaspę obcina się na krawędzi. Obok zaspy działa też równomierne μ₁ = 0,8. | PN-EN 1991-1-3 p. 5.3.6, rys. 5.7 | https://www.specbud.pl/uploads/reports/SPECBUD_KONEN2_Notka.pdf ; http://www.vcmaster.com/documents/Templates-PDF-Files/PN-EN-1991_PL.pdf | W | Przedział 0,8–4,0 to wartość zalecana EN. Czy NA go zmienia — NIEZWERYFIKOWANE (przykłady SPECBUD i VCmaster dla PL stosują 0,8–4,0). |
| R5-35 | Zaspa przy attyce lub innej przeszkodzie: μ₂ = γ·h/s_k, **0,8 ≤ μ₂ ≤ 2,0**, l_s = 2h (5–15 m), rozkład trójkątny od μ₂ przy przeszkodzie do μ₁ w odległości l_s. | PN-EN 1991-1-3 p. 6.2 | https://inzynierbudownictwa.pl/wplyw-ksztaltu-dachu-na-jego-obciazenie-sniegiem-cz-ii/ | W | *Potwierdzone w weryfikacji* (IB, „Wpływ kształtu dachu na jego obciążenie śniegiem – cz. II”: „0,8 ≤ μ2 ≤ 2,0”, „l_s = 2h, z uwzględnieniem ograniczenia 5 m ≤ l_s ≤ 15 m”). Obliczenie dla attyk LAMELA — sekcja 3.4. Sytuację wyjątkową (B2) opisuje R5-38. |
| R5-36 | Nawisy śnieżne na krawędzi dachu (p. 6.3) NA każe uwzględniać tylko **powyżej 300 m n.p.m. oraz w całej strefie 4**. | PN-EN 1991-1-3 p. 6.3 + NA | https://www.specbud.pl/uploads/reports/SPECBUD_KONEN2_Notka.pdf | W | Dla Poznania (A ≈ 100 m, strefa 2) **nie dotyczy**. |
| R5-37 | Zmiana PN-EN 1991-1-3:2005/A1:2015-10 istnieje tylko w wersji angielskiej. | Lista PKN/ITB | https://www.itb.pl/wp-content/uploads/2025/05/1-edycja-EUROKODOW-wprowadzenie-do-zbioru-Polskich-Norm-stan-na-30-sierpnia-2024-r.pdf | P | Zgodnie z przypisem **) WT (R5-03) obowiązuje wersja polska z NA:2010. Treść A1 — NIEZWERYFIKOWANE. |
| R5-38 | *Dodane w weryfikacji.* Wyjątkowa sytuacja obliczeniowa, przypadek B2 (zał. B, kombinacja wyjątkowa, s = μ_i·s_k bez C_e i C_t). **B.3, dach przy wyższej budowli** (uskoki P0/P1, P1/P2, taras D przy boksie C): μ₁ = min{2h/s_k; 2b/l_s; 8}, b = większe z b₁, b₂; l_s = 5h, nie więcej niż b₁ i 15 m. **B.4, attyki i przeszkody**: współczynnik i długość zaspy odczytać z normy. Wg IB po AC:2009 zał. B p. B4(2) dopuszcza pominięcie zaspy wyjątkowej przy przeszkodach o wysokości ≤ 1 m (wcześniej „≤ 1 m²”). IB wskazuje sprzeczność między B4(2)a i B4(2)b. | PN-EN 1991-1-3 zał. B (+AC:2009) + NA | https://inzynierbudownictwa.pl/obciazenie-sniegiem-wg-eurokodu-1-norma-pn-en-1991-1-3/ | W | Wzory B.3 podano z pamięci weryfikatora: **NIEZWERYFIKOWANE**, do sprawdzenia w tekście normy przed PT. Rząd wielkości: przy h = 3 m μ₁ = min{6,7; …; 8}, co daje przy ścianie do ok. 6 kN/m² w sytuacji wyjątkowej (γ = 1,0). **Może to decydować o płytach przy uskokach brył** — wartość 3,6 kN/m² z R5-34 dotyczy tylko sytuacji trwałej. |

### 2.E PN-EN 1991-1-4 — wiatr

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-40 | **Poznań i powiat poznański: strefa 1.** Dla A ≤ 300 m: v_b,0 = **22 m/s**, q_b,0 = **0,30 kN/m²**; dla A > 300 m: v_b,0 = 22·[1 + 0,0006(A − 300)]. Strefa 2 (pas nadmorski): 26 m/s, 0,42 kN/m². | PN-EN 1991-1-4:2008 + NA:2010, Tabl. NA.1, rys. NA.1 | https://loadzones.dlubal.com/file.aspx?kml=wind-pn-en-1991-1-4-l47-v2384.kml ; https://www.dlubal.com/pl/strefy-obciazenia-sniegiem-wiatrem-trzesieniem-ziemi/wiatr-pn-en-1991-1-4.html ; https://www.specbud.pl/uploads/reports/SPECBUD_KONEN2_Notka.pdf | W | Test KML (źródło Dlubal: „PN-EN 1991-1-4/NA:2010-09”) daje strefę 1 dla wszystkich 12 miejscowości. q_b = ½·1,25·22² = 0,3025 kN/m². Brief poprawny. |
| R5-41 | Współczynnik kierunkowy c_dir podany w NA sektorowo (np. 0,8 dla sektora 1 w przykładzie PWr). **Przyjmujemy bezpiecznie c_dir = 1,0.** c_season = 1,0. | PN-EN 1991-1-4 p. 4.2 + NA | https://wbliw.pwr.edu.pl/d/sGBUXFA1dbQ1tBUJuREFCEUJQSWoqHwIMHWdNExIOCihBDUlnRkk9aDxUVmJbVh1BWFBJajwBT05LNT5YAlVAfFcCBw/obciazenie_wiatrem_przyklady_5.pdf | W | Mapa sektorów c_dir z NA — NIEZWERYFIKOWANE; c_dir = 1,0 jest zawsze bezpieczne. |
| R5-42 | Kategorie terenu: II — niska roślinność, pojedyncze przeszkody w odstępach ≥ 20 wysokości; III — obszary regularnie pokryte roślinnością lub budynkami, pojedyncze przeszkody w odstępach ≤ 20 wysokości (wsie, tereny podmiejskie, lasy); IV — ≥ 15% powierzchni zabudowane, średnia wysokość > 15 m. | PN-EN 1991-1-4, Tabl. 4.1 | https://obciazeniewiatrem.com/kategoria-terenu/ ; http://www.pg.gda.pl/~krogu/Przyklad%20obliczeniowyx.pdf | W | Na południe od działki jest teren rolny, więc dla wiatru z południa należy rozważyć **kategorię II** (sekcja 3.5). |
| R5-43 | NA, Tabl. NA.3: kategoria III: **c_e(z) = 1,9·(z/10)^0,26**, z_min = 5 m, c_r(z) = 0,8·(z/10)^0,19. Kategoria II: c_r(z) = 1,0·(z/10)^0,17, z_min = 2 m. Szczytowe ciśnienie prędkości: q_p(z) = c_e(z)·q_b. | PN-EN 1991-1-4 + NA:2010, Tabl. NA.3 | http://www.pg.gda.pl/~krogu/Przyklad%20obliczeniowyx.pdf ; https://wbliw.pwr.edu.pl/d/sGBUXFA1dbQ1tBUJuREFCEUJQSWoqHwIMHWdNExIOCihBDUlnRkk9aDxUVmJbVh1BWFBJajwBT05LNT5YAlVAfFcCBw/obciazenie_wiatrem_przyklady_5.pdf ; https://e-oze.pl/wiki/index.php/PN-EN_1991-1-4:2008 | W | Politechnika Gdańska: „c_e(z) = 1,9(z/10)^0,26 – współczynnik ekspozycji dla terenu kategorii III”. *Rozstrzygnięte w weryfikacji:* Tabl. NA.3 (przedruk: Politechnika Warszawska, MEiL, „Wykład 4 – Aerodynamika struktur urbanistycznych”) podaje dla **kategorii II: c_e(z) = 2,3·(z/10)^0,24, z_min = 2 m** (z₀ = 0,05 m). Pozostałe: 0 — 3,0·(z/10)^0,17 (z_min 1 m); I — 2,8·(z/10)^0,19 (1 m); IV — 1,5·(z/10)^0,29 (10 m); c_r: II — 1,0·(z/10)^0,17, III — 0,8·(z/10)^0,19. Wzór VCmaster (2,29·(z/10)^0,27) jest błędny. Dla z = 10,5 m: c_e = 2,33 (a nie 2,35 z c_r i I_v wg EN). Źródło: https://www.meil.pw.edu.pl/sms/content/download/61569/322567/file/Wyk%C5%82ad_4_Aero_S_U.pdf |
| R5-44 | Dla budynków o h < 15 m c_s·c_d = 1,0. | PN-EN 1991-1-4 p. 6.2(1)a | http://www.pg.gda.pl/~krogu/Przyklad%20obliczeniowyx.pdf | W | — |
| R5-45 | Współczynniki c_pe dla dachów płaskich z attykami (pola F/G/H/I, zależne od h_p/h) — tablica 7.2 EN. | PN-EN 1991-1-4, Tabl. 7.2 | — | — | Liczby z tablicy 7.2 — **NIEZWERYFIKOWANE** w tej sesji. Do odczytu z normy przy doborze balastu PV i obróbek attyk. |

### 2.F PN-EN 1992-1-1 — konstrukcje żelbetowe

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-50 | Częściowe współczynniki materiałowe: **γ_c = 1,4** („przyjęty do normy w ramach tak zwanych ustaleń krajowych”; w większości krajów UE 1,5), **γ_s = 1,15**. | PN-EN 1992-1-1:2008 + NA, p. 2.4.2.4 | https://mjurkiewicz.weebly.com/uploads/2/5/1/8/25183076/wst%C4%99p_do_projektowania_konstrukcji_%C5%BCelbetowych_wg_pn-en_1992-1-1_2008_-_janusz_p%C4%99dziwiatr.pdf | W | J. Pędziwiatr, „Wstęp do projektowania konstrukcji żelbetowych wg PN-EN 1992-1-1:2008”, DWE 2010 (plik udostępniony przez osobę trzecią). α_cc w NA — NIEZWERYFIKOWANE. Czy NA:2016/2018 zmieniły γ_c — NIEZWERYFIKOWANE. |
| R5-51 | Wskazane (minimalne) klasy betonu ze względu na trwałość (Zał. E): X0 → C12/15; **XC1 → C20/25**; **XC2 → C25/30**; **XC3 → C30/37**; **XC4 → C30/37**; **XF1 → C30/37**; XD1 → C30/37. | PN-EN 1992-1-1, Zał. E, Tabl. E.1N | https://mjurkiewicz.weebly.com/uploads/2/5/1/8/25183076/wst%C4%99p_do_projektowania_konstrukcji_%C5%BCelbetowych_wg_pn-en_1992-1-1_2008_-_janusz_p%C4%99dziwiatr.pdf | W | Pędziwiatr, Tab. 2.2 i 3.7. |
| R5-52 | Otulenie: c_nom = c_min + Δc_dev; c_min = max(c_min,b; c_min,dur + …; 10 mm); c_min,b ≥ φ pręta. **c_min,dur dla S4:** X0 = 10; **XC1 = 15**; **XC2/XC3 = 25**; **XC4 = 30**; XD1/XS1 = 35 mm. **Δc_dev = 10 mm** (5–10 mm przy pomiarach otulin; 0–10 mm dla prefabrykatów). | PN-EN 1992-1-1 p. 4.4.1, Tabl. 4.3N–4.4N + NA | https://mjurkiewicz.weebly.com/uploads/2/5/1/8/25183076/wst%C4%99p_do_projektowania_konstrukcji_%C5%BCelbetowych_wg_pn-en_1992-1-1_2008_-_janusz_p%C4%99dziwiatr.pdf ; https://www.przegladbudowlany.pl/2018/10/2018-10-PB-15-PROBL-Zybura-Zagadnienia.pdf | W | Pędziwiatr, Tab. 2.3 (S3/S4). Zybura: „wartość zalecana odchyłki wynosi Δc_dev = 10 mm”. Otulenie przy betonowaniu na podłożu (EN 4.4.1.3(4): ≥ 40 mm na podbetonie, ≥ 75 mm bezpośrednio na gruncie) — NIEZWERYFIKOWANE (pamięć). |
| R5-53 | Graniczna szerokość rys w_max (kombinacja quasi-stała): **0,4 mm** dla X0 i XC1; **0,3 mm** w pozostałych klasach. | PN-EN 1992-1-1 p. 7.3.1, Tabl. 7.1N | https://www.przegladbudowlany.pl/2018/10/2018-10-PB-15-PROBL-Zybura-Zagadnienia.pdf | W | Dla tarasu i płyty D z hydroizolacją 0,3 mm, a przy braku izolacji podpowierzchniowej rozważyć ostrzejsze ograniczenie. |
| R5-54 | Beton wg PN-EN 206+A2:2021-08 z uzupełnieniem krajowym PN-B-06265:2022-08. Wartości graniczne składu (Heidelberg, na podstawie prPN-B-06265:2016-10): XC1: w/c ≤ 0,70, min. C16/20; XC2: 0,65, C16/20; XC3: 0,60, C20/25; XC4: 0,55, C20/25; XF1: 0,55, **C30/37**, kruszywo F2. Przykłady: „Wiata garażowa XC4, XF1”; „Stropodach XC4, XF1”; „Fundament zbrojony (XC1) XC2”; „Ściana zewnętrzna z izolacją XC1”. | PN-EN 206+A2:2021-08; PN-B-06265:2022-08 | https://www.heidelbergmaterials.pl/sites/default/files/assets/document/8d/32/beton_wg_pn_en_206_z_kraj_uzup.pdf ; https://www.kieruneksurowce.pl/artykul,90149,projekt-nowelizacji-krajowego-zalacznika-do-normy-pn-en-206a22021-08-gotowy.html | W | Wymagania PN-B-06265 są łagodniejsze niż zał. E EC2. W projekcie decydują **klasy z R5-51**. Wartości tablicy wg wydania 2022 — NIEZWERYFIKOWANE (informator oparto na projekcie normy z 2016 r.). **KOREKTA STATUSU (weryfikacja, katalog PKN 25.09.2026):** **PN-EN 206+A2:2021-08** (PL i EN) oraz **PN-B-06265:2022-08** z Az1:2025-08 są **wycofane**. Zastąpiły je **PN-EN 206-1:2026-09** i **PN-EN 206-2:2026-09**, obie tylko **w wersji angielskiej**, status „aktualna”; PN-EN 206-1:2026-09 wprowadza EN 206-1:2026. Źródło: wyszukiwarka norm PKN, https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm (P). Por. N-11. |
| R5-55 | Klasy ciągliwości stali (Zał. C): A: k ≥ 1,05, ε_uk ≥ 2,5%; B: k ≥ 1,08, ε_uk ≥ 5,0%; **C: 1,15 ≤ k < 1,35, ε_uk ≥ 7,5%**. Gatunek **B500SP** (PN-H-93220:2018-02): f_yk = 500 MPa, spajalny, klasa C. | PN-EN 1992-1-1, Zał. C, Tabl. C.1; PN-H-93220:2018-02 | https://mjurkiewicz.weebly.com/uploads/2/5/1/8/25183076/wst%C4%99p_do_projektowania_konstrukcji_%C5%BCelbetowych_wg_pn-en_1992-1-1_2008_-_janusz_p%C4%99dziwiatr.pdf ; http://www.nbi.com.pl/assets/NBI-pdf/2018/5_80_2018/PDF/16_Stal_zbrojeniowa.pdf | W | *Weryfikacja (katalog PKN):* PN-H-93220:2018-02 „Stal do zbrojenia betonu – Spajalna stal zbrojeniowa B500SP – Pręty i walcówka żebrowana” ma status **aktualna**, z poprawką **Ap1:2018-04** (również aktualna). Zastąpiła PN-H-93220:2006. f_yd = 500/1,15 = 435 MPa. |
| R5-56 | Ugięcia: kombinacja quasi-stała, ugięcie ≤ l_eff/250; strzałka odwrotna ≤ l_eff/250. Uproszczone sprawdzenie przez l/d: K = 1,0 (belka swobodnie podparta), 1,3 (przęsło skrajne), 1,5 (przęsło wewnętrzne), **0,4 (wspornik)**. Przyrost ugięcia po wykonaniu elementów wrażliwych (ścianki, przeszklenia) ≤ l/500. | PN-EN 1992-1-1 p. 7.4.1(4)–(5), 7.4.2, Tabl. 7.4N | https://mjurkiewicz.weebly.com/uploads/2/5/1/8/25183076/wst%C4%99p_do_projektowania_konstrukcji_%C5%BCelbetowych_wg_pn-en_1992-1-1_2008_-_janusz_p%C4%99dziwiatr.pdf | W | l/250 i K potwierdzone u Pędziwiatra. Wartość l/500 z p. 7.4.1(5) — NIEZWERYFIKOWANE (pamięć). EC2 nie precyzuje, jak liczyć l_eff wspornika; R5 proponuje przyjąć 2 × wysięg, tak jak w NA do EC3 (R5-71). |

### 2.G PN-EN 1996-1-1 — konstrukcje murowe (silikaty)

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-60 | Wytrzymałość charakterystyczna muru na zaprawie do cienkich spoin: f_k = K·f_b^0,85. NA, Tabl. NA.5: **K = 0,60** dla silikatów grupy 1 z zaprawą do cienkich spoin (Ap2:2014-09 zmieniła 0,55 na 0,60); K = 0,45 dla zaprawy zwykłej (wg Xella). | PN-EN 1996-1-1+A1:2013-05, p. 3.6.1.2 + NA:2014-03 + Ap2:2014-09 | https://www.itb.pl/wp-content/uploads/2025/05/1-edycja-EUROKODOW-wprowadzenie-do-zbioru-Polskich-Norm-stan-na-30-sierpnia-2024-r.pdf ; https://storefrontapi.commerce.xella.com/medias/sys_master/root/hee/h78/8850504450078/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03.pdf | P (lista ITB) + W (Xella) | Lista ITB/PKN: „Ap2 – w Załączniku krajowym NA, Tablica NA.5, zmienia się wartość współczynnika K dla silikatów Grupy 1 i zaprawy do cienkich spoin z 0,55 na 0,60”. Zakres Ap3:2016-04 — NIEZWERYFIKOWANE. |
| R5-61 | Bloki Silka (grupa 1, kategoria I), mur grubości 18 i 24 cm: klasa 15 → f_k = 6,00 MPa; **klasa 20 → f_k = 7,66 MPa**; klasa 25 → f_k = 9,26 MPa (przy f_b równym klasie). | Xella, „Projektowanie architektoniczne i konstrukcyjne budynków w systemie Silka” (2017), Tab. 4.1 | https://storefrontapi.commerce.xella.com/medias/sys_master/root/hee/h78/8850504450078/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03.pdf | W (producent) | Sprawdzone rachunkiem: 0,60·20^0,85 = 7,656 MPa. Przed zamówieniem potwierdzić f_b znormalizowane z DWU wybranego wyrobu. |
| R5-62 | γ_M (NA, Tabl. NA.1): elementy kategorii I + zaprawa projektowana: **1,7 (klasa wykonania A) / 2,0 (klasa B)**; kategoria I + zaprawa przepisana: 2,0 / 2,2; kategoria II: 2,2 / 2,5. Ściany grubości 100–150 mm: 2,5 (kat. I, zaprawa projektowana, klasa A), w pozostałych przypadkach 2,7. Sytuacja wyjątkowa: γ_M = 1,3 (mur). Klasa A wymaga wyszkolonej brygady pod nadzorem mistrza, zaprawy fabrycznej i kontroli inspektora nadzoru. | PN-EN 1996-1-1 + NA, Tabl. NA.1 | https://storefrontapi.commerce.xella.com/medias/sys_master/root/hee/h78/8850504450078/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03.pdf | W | Dla klasy 20 i klasy wykonania A: f_d = 4,50 MPa; dla klasy B: 3,83 MPa. |
| R5-63 | Gdy pole przekroju ściany (filarka) jest < 0,3 m², f_d dzieli się przez η_A. Bezpośrednio pod obciążeniem skupionym dopuszcza się tylko elementy grupy 1 lub pełne. | PN-EN 1996-1-1 + NA | https://storefrontapi.commerce.xella.com/medias/sys_master/root/hee/h78/8850504450078/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03/Zeszyt-techniczny-Projektowanie-architektoniczne-i-konstrukcyjne-Silka-2017-03.pdf | W | Dotyczy filarków między przeszkleniami P0 (np. lico x = 500 px na szkicu). *Uzupełnione w weryfikacji* (Xella 2017, Tab. 4.5, wg NA): **η_A = 2,00** przy polu ≤ 0,05–0,09 m²; **1,43** przy 0,12 m²; **1,25** przy 0,20 m²; **1,00** przy ≥ 0,30 m². Wartości pośrednie interpolować liniowo. Źródło wtórne (producent). |

### 2.H PN-EN 1993-1-1 — stal (słupy i belki wiaty, elementy pomocnicze)

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-70 | **γ_M0 = 1,0; γ_M1 = 1,0** (NA). γ_M2 = 1,25 (połączenia, PN-EN 1993-1-8). Granice plastyczności: S235 → 235 MPa, S355 → 355 MPa przy t ≤ 40 mm. | PN-EN 1993-1-1:2006 + NA:2010, p. 6.1; Tabl. 3.1 | http://www.vcmaster.com/documents/Templates-PDF-Files/PN-EN-1993_PL.pdf | W | γ_M2 i f_y — NIEZWERYFIKOWANE w źródle w tej sesji (wartości EN, pamięć). |
| R5-71 | Graniczne ugięcia pionowe w_max (NA, zalecane): dźwigary dachowe L/250; płatwie L/200; blacha profilowana L/150; stropy — belki główne (podciągi) L/350, belki drugorzędne L/250; nadproża okien i bram L/500. **L = rozpiętość lub podwójny wysięg wspornika.** Przemieszczenia poziome: układy jednokondygnacyjne H/150, wielokondygnacyjne H/500. | PN-EN 1993-1-1 + NA (7.2) | http://pobierz.intersoft.pl/konkurs/EUROKODY/EUROKODY-Projektowanie-konstrukcji-stalowych.pdf | W | Wiata: belki/płyta D o konstrukcji stalowej ≤ L/250; słupy (układ jednokondygnacyjny) ≤ H/150. |
| R5-72 | Klasa wykonania konstrukcji stalowych wg PN-EN 1090-2: gdy nie określono inaczej, EXC2. | PN-EN 1090-2 p. 4.1.2 | https://wiedza.pkn.pl/web/guest/wyszukiwarka-norm | — | Reguła EXC2: NIEZWERYFIKOWANE (pamięć). Zalecenie: EXC2, konstrukcja cynkowana ogniowo. *Weryfikacja statusu (PKN):* aktualne wydanie to **PN-EN 1090-2+A1:2024-10** (wersja polska i angielska). PN-EN 1090-2:2018-09 jest wycofana. W projekcie powoływać wydanie 2024-10. |

### 2.I Geotechnika — rozporządzenie Dz.U. 2012 poz. 463 i PN-EN 1997-1 + NA

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-80 | Rozporządzenie ma w ELI status **„obowiązujący”** (od 29.04.2012 r., zmiany: brak). Wydano je na podstawie art. 34 ust. 6 pkt 2 Pb, który nadal istnieje w t.j. Dz.U. 2026 poz. 524. | Rozp. MTBiGM z 25.04.2012 r. w sprawie ustalania geotechnicznych warunków posadawiania obiektów budowlanych; Pb art. 34 ust. 6 pkt 2 | https://api.sejm.gov.pl/eli/acts/DU/2012/463 ; https://api.sejm.gov.pl/eli/acts/DU/2026/524/text.pdf | P | — |
| R5-81 | **I kategoria geotechniczna** obejmuje „niewielkie obiekty budowlane, o statycznie wyznaczalnym schemacie obliczeniowym w prostych warunkach gruntowych … takie jak: a) 1- lub 2-kondygnacyjne budynki mieszkalne i gospodarcze” (§ 4 ust. 3 pkt 1). **II kategoria** obejmuje obiekty w prostych i złożonych warunkach gruntowych, wymagające ilościowej i jakościowej oceny danych geotechnicznych, w tym „a) fundamenty bezpośrednie lub głębokie” (§ 4 ust. 3 pkt 2). Kategorię określa projektant na podstawie badań (§ 4 ust. 4); zmienia ją, jeśli warunki okażą się inne (§ 4 ust. 5). | Dz.U. 2012 poz. 463, § 4 ust. 3–5 | https://api.sejm.gov.pl/eli/acts/DU/2012/463/text.pdf | P | **Dom LAMELA (3 kondygnacje nadziemne, wsporniki, stropy ciągłe) = II kategoria.** Brief („I kategoria”) do korekty. *Uściślenie z weryfikacji:* wyliczenie w pkt 1 jest przykładowe („takich jak”). Rozstrzyga warunek „statycznie wyznaczalnego schematu”, którego LAMELA nie spełnia. Kategorię wskazuje opinia geotechniczna (§ 4 ust. 1, § 8), a projektant określa ją na podstawie badań (§ 4 ust. 4). |
| R5-82 | Warunki gruntowe **proste**: warstwy jednorodne genetycznie i litologicznie, zalegające poziomo, bez gruntów słabonośnych, organicznych i nasypów niekontrolowanych, **zwierciadło wody poniżej projektowanego poziomu posadowienia**, bez niekorzystnych zjawisk geologicznych. | Dz.U. 2012 poz. 463, § 4 ust. 2 pkt 1 | https://api.sejm.gov.pl/eli/acts/DU/2012/463/text.pdf | P | Piaski średnie z wodą gruntową na 3,8 m p.p.t. to warunki proste. Warstwa 0,0–0,4 m (ziemia urodzajna) — do usunięcia spod budynku. |
| R5-83 | Opinię geotechniczną sporządza się dla wszystkich kategorii (§ 7 ust. 1). Dla **II i III kategorii** opracowuje się dodatkowo **dokumentację badań podłoża gruntowego i projekt geotechniczny** (§ 7 ust. 2). Dokumentacja geologiczno-inżynierska jest wymagana tylko w III kategorii oraz w II kategorii w **złożonych** warunkach (§ 7 ust. 3), więc tu nie jest potrzebna. W II kategorii badania muszą określić parametry wytrzymałościowe i odkształceniowe z badań polowych (sondowania statyczne i dynamiczne) lub laboratoryjnych (§ 6 ust. 3). Zawartość projektu geotechnicznego określa § 10 pkt 1–10. | Dz.U. 2012 poz. 463, § 6 ust. 2–3, § 7, § 8–10 | https://api.sejm.gov.pl/eli/acts/DU/2012/463/text.pdf | P | Opinia → PAB (R5-05, R5-06). Dokumentacja badań i projekt geotechniczny → PT (§ 23 pkt 2 rozporządzenia o zakresie projektu). |
| R5-84 | Stany GEO i STR fundamentów: **podejście obliczeniowe DA2** (A1 + M1 + R2). Przy wyznaczaniu oporu granicznego podłoża stosuje się charakterystyczne wartości oddziaływań (**DA2***) — NA.2.6 (poprawka Ap2:2010). Opór R2: **γ_R;v = 1,4** (nośność), **γ_R;h = 1,1** (przesunięcie). Stateczność ogólna: DA3. | PN-EN 1997-1:2008 + Ap2:2010 (NA) pkt NA.2.6; zał. A, Tabl. A.3–A.5 | https://uwm.edu.pl/edu/piotrsrokosz/stopa_EC7.pdf ; https://www.intersoft.pl/pdf/podreczniki/Podrecznik_Konstruktor-fundamenty-bezposrednie-eurokod-pn-en.pdf ; http://agro.icm.edu.pl/agro/element/bwmeta1.element.agro-ae82b395-79fa-47c9-9855-94e2372feffb/c/art11_222.pdf | W | UWM (P. Srokosz): „Zgodnie z zaleceniami poprawki … PN-EN 1997-1:2008/Ap2 pkt NA.2.6 … opór graniczny … charakterystyczne wartości oddziaływań (podejście obliczeniowe DA2*)”. |
| R5-85 | Graniczne osiadania (NA.3.2, zał. H, Tabl. NA.3; przykład UWM): s_max = 50 mm „dla powszechnie stosowanych konstrukcji budynków”; strzałka ugięcia Δ_max = 10 mm; przechylenie ω_max = 0,003 rad. | PN-EN 1997-1 + Ap2:2010, NA.3.2, Tabl. NA.3 | https://uwm.edu.pl/edu/piotrsrokosz/stopa_EC7.pdf | W | Typ budynku w tablicy NA.3, do którego odnoszą się Δ i ω — NIEZWERYFIKOWANE. |
| R5-86 | Parametry wstępne z korelacji PN-81/B-03020 (norma wycofana): piaski grube i średnie, I_D = 0,5 → φ_u = 33°. Piaski grube/średnie wilgotne, średnio zagęszczone: ρ = 1,85 t/m³. Nie są to piaski wysadzinowe. | PN-B-03020:1981, rys. 3, Tabl. 1 (przez opracowanie AGH) | https://home.agh.edu.pl/~kowalski/files/param03020.pdf | W | Lokalne zależności korelacyjne dopuszcza się tylko w I kategorii (§ 6 ust. 2). **W II kategorii parametry muszą pochodzić z badań (CPT/DPL) — dane z briefu są przykładowe.** |

### 2.J Przemarzanie gruntu

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-90 | PN-B-03020:1981 „Grunty budowlane – Posadowienie bezpośrednie budowli – Obliczenia statyczne i projektowanie” **wycofano 31.03.2010 r.** i zastąpiono PN-EN 1997-1:2008. | PKN, Załącznik A „PN dotyczące projektowania … wycofane z dniem 31 marca 2010 r.” | https://wiedza.pkn.pl/documents/14137/31877/Eurokody_Za%C5%82%C4%85cznik+A_pop.pdf/e832256b-5f46-4217-a8bd-45724073b39f | P | Wycofano także PN-B-02010 (śnieg), PN-B-02011 (wiatr), PN-B-03264, PN-B-03002 i PN-B-03200. |
| R5-91 | „W normalizacji dobrowolnej faktu dezaktualizacji normy nie należy wiązać z zakazem stosowania normy wycofanej.” Norma wycofana może zawierać mniej nowoczesne rozwiązania, co nie czyni jej sprzeczną z zasadami wiedzy technicznej. | Stanowisko PKN w sprawie stosowania PN wycofanych | https://wiedza.pkn.pl/en/web/wiedza-normalizacyjna/stanowisko-pkn-w-sprawie-stosowania-pn-wycofanych | P | Stanowi podstawę korzystania z mapy h_z z PN-81 jako „wiedzy technicznej”. |
| R5-92 | PN-81/B-03020 p. 2.2.2: a) zagłębienie podstawy fundamentu względem przyległego terenu **≥ 0,5 m** (mniejsze wymaga uzasadnienia); b) **w gruntach wysadzinowych** głębokość posadowienia ≥ umownej głębokości przemarzania h_z wg rys. 1, mierzonej od projektowanego terenu. Grunty wysadzinowe to grunty zawierające > 10% cząstek < 0,02 mm oraz grunty organiczne. | PN-B-03020:1981 p. 2.2.2 | https://zanotowane.pl/1006/3167/ | W | Kopia tekstu normy w serwisie z notatkami — źródło wtórne. Wartości h_z z PN-81 „dotyczą gruntów spoistych” (Godlewski, ITB). |
| R5-93 | Mapa PN-81, rys. 1: strefy I = 0,8 m, II = 1,0 m, III = 1,2 m, IV = 1,4 m. **Poznań (Wielkopolska zachodnia i centralna) leży w strefie I → h_z = 0,8 m.** | PN-B-03020:1981 rys. 1 (przerys) | https://poradnikinzyniera.pl/strefy-przemarzania-gruntu/ | W | Źródła wtórne są niespójne: część portali podaje dla Poznania 1,0 m, a jeden artykuł 1,2 m. Przerys mapy jednoznacznie pokazuje strefę I. Weryfikacja na oryginale normy — do wykonania (Nierozstrzygnięte N-5). |
| R5-94 | Badania ITB (Żurański i Godlewski, 2017; monografia ITB 2018): głębokość izotermy 0 °C o okresie powrotu 50 lat dla stacji **Poznań Z₅₀ = 1,31 m** (grunt P/Gp). Po przeliczeniu na grunt referencyjny (żwiry, piaski grube i średnie, współczynnik 1,0 wobec 0,8 dla P/Gp) wychodzi 1,64 m. ITB proponuje nową mapę, która nie ma statusu normy. | T. Godlewski (ITB), „Nowa propozycja określania zasięgu i głębokości stref przemarzania”, konferencja WOIIB, Poznań, 13.06.2018 | https://woiib.org.pl/images/news/201806/Godlewski.pdf | W | Mróz sięga w piaskach głębiej, ale piasek średni nie jest wysadzinowy, więc przemarzanie nie wywołuje w nim wysadzin. Ryzyko pojawia się przy przewarstwieniach spoistych i przy zasypkach z gruntu wysadzinowego. |
| R5-95 | Przewody wodociągowe i kanalizacyjne poza budynkiem układa się tak, by wierzch przewodu był **0,4 m poniżej głębokości przemarzania** wg PN-81/B-03020 (PN-B-10736:1999). Dla wodociągów DN ≤ 1000: przykrycie = h_z + 0,4 m (PN-B-10725:1997). | PN-B-10736:1999; PN-B-10725:1997 (cyt. u Godlewskiego) | https://woiib.org.pl/images/news/201806/Godlewski.pdf | W | Dla Poznania: **≥ 1,2 m** do wierzchu przyłącza wody. Do przekazania zespołowi instalacji sanitarnych. *Weryfikacja statusu (katalog PKN 25.09.2026):* **PN-B-10736:1999 — wycofana; PN-B-10725:1997 — wycofana** (bez wskazanej normy zastępującej). Reguła „h_z + 0,4 m” jest więc tylko wiedzą techniczną (R5-91) i praktyką wytycznych wodociągów. Przykrycie przyłącza uzgodnić w warunkach technicznych gestora sieci. U Godlewskiego reguła „DN ≤ 1000 → +0,4 m, DN > 1000 → +0,2 m” pochodzi z wytycznych PWiK „Nysa” (2015). |

### 2.K Bezpieczeństwo pożarowe konstrukcji

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-100 | „Wymagania dotyczące klasy odporności pożarowej budynków określone w § 212 oraz dotyczące klas odporności ogniowej elementów budynków i rozprzestrzeniania ognia przez te elementy określone w § 216, z zastrzeżeniem § 271 ust. 8a, **nie dotyczą budynków: 1) do trzech kondygnacji nadziemnych włącznie: a) mieszkalnych: jednorodzinnych** … z zastrzeżeniem § 217 ust. 2”. § 217 ust. 2 (ściana między segmentami REI 60) dotyczy tylko zabudowy bliźniaczej i szeregowej. § 271 ust. 8a dotyczy odległości od lasu. | WT (t.j. Dz.U. 2022 poz. 1225 ze zm.) § 213 pkt 1 lit. a, § 217 ust. 2, § 271 ust. 8a | https://api.sejm.gov.pl/eli/acts/DU/2022/1225/text.pdf | P | **Wobec konstrukcji Dom LAMELA (wolnostojący, 3 kondygnacje) nie ma wymagań R/REI.** Warunek: 3 kondygnacje nadziemne — np. kondygnacja techniczna na dachu zwiększyłaby tę liczbę i odebrała zwolnienie. **Status WT — R3.** |
| R5-101 | Nowelizacje Dz.U. 2023 poz. 2442, 2024 poz. 474 i 2024 poz. 726 nie zmieniają § 212–217 (sprawdzono ich teksty). Poz. 2442 zmienia § 12 (odległości od granic, z odesłaniem do § 271–273). | Teksty nowelizacji z API ELI | https://api.sejm.gov.pl/eli/acts/DU/2023/2442/text.pdf | P | — |

### 2.L Klimat — projektowa temperatura zewnętrzna

| ID | Wymaganie / reguła | Podstawa | URL | P? | Uwagi |
|---|---|---|---|---|---|
| R5-110 | Strefy klimatyczne (NA do PN-EN 12831:2006, podział jak w PN-82/B-02403): I: θ_e = −16 °C, θ_m,e = 7,7 °C; **II: −18 °C, 7,9 °C**; III: −20 °C, 7,6 °C; IV: −22 °C, 6,9 °C; V: −24 °C, 5,5 °C. **Poznań leży w strefie II.** | PN-EN 12831:2006, NA (Tabl. NA.1, rys. NA.1) | https://www.purmo.com/docs/Poradnik-Purmo-nowa-metoda-obliczania_12831_01_2012.pdf ; https://wentylacja.com.pl/news/kluczowe-zmiany-w-metodyce-obliczania-zapotrzebowania-na-cieplo-zawarte-w-pn-en-12831-33009.html | W | M. Strzeszewski, P. Wereszczyński, poradnik Purmo 2012, rys. 2.1 i tab. 2.1: Poznań na mapie w strefie II. Czy **PN-EN 12831-1:2017-08** (wersja i NA/NB) zmienia te wartości — NIEZWERYFIKOWANE. *Weryfikacja statusu (PKN):* PN-EN 12831-1:2017-08 jest **aktualna, tylko w wersji angielskiej**, i **zastąpiła PN-EN 12831:2006** (wycofana). Wartości −18 °C i 7,9 °C pochodzą więc z NA do normy wycofanej (tabela potwierdzona w poradniku Purmo, Tab. 2.1). Czy nowa norma ma krajowy załącznik z temperaturami — NIEZWERYFIKOWANE. |

---

## 3. Implikacje dla projektu Dom LAMELA — wartości i reguły gotowe do użycia

### 3.1 Podstawa normowa (do wpisania w opis techniczny części konstrukcyjnej)
PN-EN 1990:2004 + A1:2008 + NA:2010; PN-EN 1991-1-1:2004 + AC:2009 + NA:2010; PN-EN 1991-1-3:2005 + AC:2009 + Ap1:2010 + NA:2010;
PN-EN 1991-1-4:2008 + A1:2010 + AC:2009 + NA:2010; PN-EN 1991-1-7:2008 + NA:2015-02; PN-EN 1992-1-1:2008 + AC:2011 + NA:2018-11;
PN-EN 1993-1-1:2006 + A1:2014-07 + NA:2010; PN-EN 1993-1-8:2006 + NA:2011; PN-EN 1996-1-1+A1:2013-05 + NA:2014-03 (+ Ap2:2014-09);
PN-EN 1996-2:2010 + NA:2010; PN-EN 1997-1:2008 + A1:2014-05 + Ap2:2010 + NA:2011; PN-EN 1997-2:2009; beton — patrz N-11
(PN-EN 206+A2:2021-08 i PN-B-06265:2022-08 są **wycofane**, zastąpione przez PN-EN 206-1:2026-09 / 206-2:2026-09, wersje angielskie);
PN-H-93220:2018-02 + Ap1:2018-04 (B500SP); PN-EN 1090-2+A1:2024-10; rozporządzenie Dz.U. 2012 poz. 463. **Stosować wyłącznie Eurokody 1. generacji; nie mieszać z 2. generacją** (R5-01…03).

### 3.2 Klasy i współczynniki ogólne
* Projektowy okres użytkowania: 50 lat (kategoria 4); klasa konstrukcji EC2: S4.
* Klasa konsekwencji i niezawodności: **CC2 / RC2, K_FI = 1,0** (PN-EN 1990 zał. B). Odporność na oddziaływania wyjątkowe wg PN-EN 1991-1-7:
  CC1 — wystarczają ciągłe wieńce, ściągi i połączenia wsporników z konstrukcją zaplecza (PN-EN 1992-1-1 p. 9.10; do potwierdzenia w PT).
* ULS STR/GEO: mniej korzystne z wyrażeń
  **6.10a: 1,35·ΣG_k + 1,5·ψ₀,₁·Q_k,1 + 1,5·Σψ₀,i·Q_k,i** oraz
  **6.10b: 1,15·ΣG_k + 1,5·Q_k,1 + 1,5·Σψ₀,i·Q_k,i**; G korzystne ×1,00; Q korzystne ×0.
* **EQU (wsporniki bryły P2 i płyty D, przewrócenie i unoszenie podpory tylnej):** 1,10·G_dst + 1,5·Q_dst ≤ 0,90·G_stb.
  Obciążenie zmienne na zapleczu pomija się, bo działa korzystnie.
* SLS: kombinacja charakterystyczna G + Q₁ + Σψ₀Q_i; częsta G + ψ₁Q₁ + Σψ₂Q_i; quasi-stała G + Σψ₂Q_i.
* ψ: kategoria A 0,7/0,5/0,3; dach H 0/0/0; śnieg 0,5/0,2/0; wiatr 0,6/0,2/0.

### 3.3 Obciążenia użytkowe przyjęte do projektu

| Powierzchnia | q_k [kN/m²] | Q_k [kN] | ψ₀/ψ₁/ψ₂ | Podstawa / uwaga |
|---|---|---|---|---|
| Stropy mieszkalne P0/P1/P2 (kat. A) | **2,0** | **3,0** | 0,7/0,5/0,3 | Górne granice przedziałów EN (R5-20) — bezpieczne niezależnie od wyboru w NA. |
| Schody wewnętrzne (kat. A) | **4,0** | **4,0** | 0,7/0,5/0,3 | Górna granica przedziału (R5-20); wpływ na koszt pomijalny. |
| Taras na płycie D, tarasy i balkony (kat. I → A „balkony”) | **4,0** | **3,0** | 0,7/0,5/0,3 | Górna granica przedziału (R5-20, R5-24). Nie łączyć ze śniegiem; decyduje większa wartość (R5-23). |
| Ścianki działowe lekkie (≤ 2,0 kN/m) | +0,8 | — | jak strop | R5-21. |
| Ścianki działowe z silikatów lub bloczków | wg rzeczywistego ciężaru, obciążenie liniowe | — | stałe | R5-21 (ciężar > 3 kN/m). |
| Dach P2, dach techniczny z PV (kat. H) | **0,4** | **1,0** | 0/0/0 | R5-22. Nie łączyć ze śniegiem ani wiatrem. Ciężar PV z balastem przyjąć jako obciążenie stałe wg danych dostawcy (NIEZWERYFIKOWANE). |
| Dachy P0 i P1 bez dostępu (kat. H) | 0,4 | 1,0 | 0/0/0 | Jw. |

### 3.4 Śnieg (Poznań: strefa 2, s_k = 0,90 kN/m², C_e = 1,0, C_t = 1,0)
* Obciążenie równomierne dachów płaskich: **s = 0,8·1,0·1,0·0,90 = 0,72 kN/m²** (obciążenie obliczeniowe 1,08 kN/m² przy γ_Q = 1,5).
* **Zaspy przy attykach** (R5-35 — wartości NIEZWERYFIKOWANE w źródle): μ₂ = 2h_attyki/0,9, w granicach 0,8–2,0, długość l_s = 5 m (minimum).
  Przykładowo: attyka 0,3 m → 0,72 kN/m² (bez zaspy); 0,5 m → 1,00 kN/m²; 0,6 m → 1,20 kN/m²; ≥ 0,9 m → 1,80 kN/m² przy attyce,
  malejąco liniowo do 0,72 kN/m² w odległości 5 m.
* **Zaspy przy uskokach brył** (R5-34): μ_w = (b₁ + b₂)/(2h), ograniczone przez 2h/0,9 i przedział 0,8–4,0; l_s = 2h (5–15 m).
  Dotyczy: (a) płyty dachu P0 przy ścianie bryły P1, (b) dachu P1 przy bryle P2, (c) tarasu D przy boksie C i bryłach P1/P2,
  (d) okapu płyty P0 wysuniętego 1,5 m na zachód, pod bryłą P2 wysuniętą o 1,0 m.
  Wartości h, b₁ i b₂ generować z `model/budynek.yaml`. Wynik: s = μ₂·0,9 kN/m², najwyżej 3,6 kN/m² przy ścianie — **tylko w sytuacji trwałej**.
* *Dodane w weryfikacji:* **Sytuacja wyjątkowa B2** (NA; R5-33, R5-38): przy tych samych uskokach sprawdzić zaspę wg zał. B.3,
  s = μ₁·s_k, μ₁ = min{2h/s_k; 2b/l_s; 8}, l_s = min(5h; b₁; 15 m). Stosować kombinację wyjątkową PN-EN 1990 (6.11b), γ = 1,0.
  Przy attykach sprawdzić zał. B.4. Wzory zał. B — NIEZWERYFIKOWANE, sprawdzić w normie.
* Nawisów śnieżnych (p. 6.3) nie uwzględniamy (A < 300 m, strefa 2). Wyjątkowych opadów również (NA: B1/B3 nie dotyczą Polski).

### 3.5 Wiatr (strefa 1: v_b,0 = 22 m/s, q_b = 0,30 kN/m², c_dir = c_season = 1,0, c_s·c_d = 1,0)
| z [m] | q_p, teren III [kN/m²] (c_e = 1,9·(z/10)^0,26; z_min = 5 m) | q_p, teren II [kN/m²] (c_e = 2,3·(z/10)^0,24; z_min = 2 m — NA, Tabl. NA.3) |
|---|---|---|
| ≤ 5,0 | 0,48 | 0,59 (dla z = 5,0) |
| 7,0 | 0,52 | 0,64 |
| 10,0 | 0,57 | 0,70 |
| 10,5 | 0,58 | 0,70 |
| 11,0 | 0,59 | 0,71 |

*Poprawione w weryfikacji:* kolumnę „teren II” przeliczono wzorem z NA (q_b = 0,3025 kN/m²). Było: 0,60/0,65/0,70/0,71/0,72, liczone z c_r wg NA i I_v wg EN. Kolumna III: dla z = 11 m 0,589, czyli 0,59 (było 0,58).

**Proponowana obwiednia projektowa: q_p(z_e = h ≤ 11,0 m) = 0,71 kN/m²** (teren II dla wiatru z sektorów południowych, od strony terenu rolnego). Wcześniej podane 0,72 kN/m² jest bezpiecznym zaokrągleniem w górę (+1,4%) i można je zachować.
Zastosowanie teren III dla wszystkich kierunków wymaga uzasadnienia pokryciem terenu (PN-EN 1991-1-4 zał. A.2 — NIEZWERYFIKOWANE).
c_pe dla ścian i dachu płaskiego z attyką (Tabl. 7.1 i 7.2) odczytać z normy (R5-45).

### 3.6 Materiały i trwałość — przypisanie do elementów

| Element | Klasa ekspozycji | Beton (min.) | c_min,dur [mm] | c_nom [mm] (Δc_dev = 10) | w_max [mm] |
|---|---|---|---|---|---|
| Stropy i wieńce wewnątrz obudowy ocieplonej | XC1 | **C25/30** (≥ C20/25) | 15 | **25** (≥ φ + 10) | 0,4 |
| Ławy lub płyta fundamentowa, ściany fundamentowe (zbrojone) | XC2 | **C25/30** | 25 | **35**; od strony gruntu ≥ 50 na podbetonie (R5-52: EN 4.4.1.3(4) zaleca k₁ = 40 mm na podbetonie, k₂ = 75 mm bezpośrednio na gruncie; 50 mm to zapas; wartości NIEZWERYFIKOWANE) | 0,3 |
| Spody wysięgów osłonięte przed deszczem (okap P0, spód bryły P2) | XC3 | **C30/37** | 25 | **35** | 0,3 |
| Płyta D (taras i wiata), attyki, płyty wystawione na deszcz i mróz | XC4 + XF1 | **C30/37**, kruszywo F2, w/c ≤ 0,55 | 30 | **40** | 0,3 |
| Stopy słupów wiaty | XC2 (+XF1 przy powierzchni) | C30/37 | 25–30 | 40 | 0,3 |

* Stal zbrojeniowa: **B500SP, klasa C**, f_yk = 500 MPa, f_yd = 435 MPa (R5-55). Beton: γ_c = 1,4, γ_s = 1,15 (R5-50).
* Połączenia wsporników z częścią ogrzewaną: łączniki termoizolacyjne z ETA/EAD. Nośność wg dokumentu producenta — do doboru w PT.
* **Mur nośny:** silikaty grupy 1, kategoria I, klasa 20, zaprawa do cienkich spoin: **f_k = 7,66 MPa; γ_M = 1,7 (klasa wykonania A,
  wymagana w projekcie) → f_d = 4,50 MPa**. Przy klasie wykonania B: 3,83 MPa. Filarki o przekroju < 0,3 m²: f_d/η_A.
  Ściany nośne ≥ 18 cm (γ_M dla ścian ≤ 15 cm wynosi 2,5–2,7).
* **Stal konstrukcyjna** (słupy i belki wiaty, podciągi pomocnicze): S355 (słupy smukłe) lub S235; γ_M0 = γ_M1 = 1,0;
  cynkowanie ogniowe; EXC2 (NIEZWERYFIKOWANE, R5-72).

### 3.7 Kryteria SLS
* Stropy i płyty żelbetowe: ugięcie od kombinacji quasi-stałej ≤ **L/250**. Przyrost ugięcia po wykonaniu ścianek murowanych
  i stolarki ≤ **L/500** (NIEZWERYFIKOWANE, R5-56). **Krytyczne miejsca:** krawędź płyty dachu P0 nad ciągłym przeszkleniem
  ok. 12,2 m oraz rama boksu C. Oprócz spełnienia limitu przewidzieć w nadprożach stolarki szczelinę dylatacyjną.
* **Wsporniki** (bryła P2 ok. 1,0 m, płyta dachu P0 1,5 m i 0,9 m, płyta D): L = 2 × wysięg, czyli ugięcie końca ≤ wysięg/125
  (quasi-stała) oraz przyrost ≤ wysięg/250. Liczyć z pełzaniem i skurczem, uwzględniając obrót podpory (rotację zaplecza).
  Proponowana strzałka odwrotna w deskowaniu ≤ L/250 (R5-56).
* Stal (wiata): belki ≤ L/250 (od obciążeń zmiennych L/350, jeżeli belka jest podciągiem płyty tarasu). Słupy: przemieszczenie
  poziome ≤ H/150 (R5-71).
* Rysy: 0,4 mm (XC1), 0,3 mm (XC2–XC4) (R5-53).
* Drgania: kryterium WT § 204 ust. 3 pkt 3 i PN-B-02171:2017-06. Częstotliwość graniczną dla stropów (np. wsporników P2 i płyty D)
  ustalić w PT — liczba NIEZWERYFIKOWANA.

### 3.8 Geotechnika i posadowienie
* **Kategoria geotechniczna: II** (R5-81). Do PAB: **opinia geotechniczna** z kategorią i informacją o sposobie posadowienia.
  Do PT: **dokumentacja badań podłoża gruntowego** oraz **projekt geotechniczny** (§ 10 pkt 1–10, m.in. obliczenie nośności,
  osiadań i ogólnej stateczności oraz specyfikacja badań odbiorczych robót ziemnych).
* Zakres badań w II kategorii: wiercenia oraz sondowania statyczne lub dynamiczne z parametrami φ′, M₀/E (§ 6 ust. 3).
  Liczba i głębokość punktów wg PN-EN 1997-2 zał. B.3 — NIEZWERYFIKOWANE; proponowane minimum: 3 punkty w obrysie,
  do głębokości ≥ 6 m poniżej poziomu posadowienia.
* Weryfikacja nośności podłoża: **DA2*** (A1: 1,35/1,5 na efekty; M1; R2: γ_R;v = 1,4, γ_R;h = 1,1). Osiadania s ≤ 50 mm (R5-85).
* Szacunek poglądowy (obliczenie R5 wg PN-EN 1997-1 zał. D, warunki z odpływem, ława B = 0,6 m, γ = 18,5 kN/m³, bez wpływu wody,
  bo GWL leży 2,8 m pod podstawą): φ′_k = 32° → R_k/A′ ≈ 497 kPa i R_d/A′ ≈ 355 kPa przy D = 0,8 m; φ′_k = 33° → 567 i 405 kPa.
  Dla domu 3-kondygnacyjnego nacisk obliczeniowy pod ławą wynosi zwykle znacznie poniżej 250 kPa (szacunek — do obliczenia w PT),
  więc **decydują osiadania i względy konstrukcyjne**. Parametry wyłącznie ilustracyjne (R5-86), nie do PT.
* **Głębokość posadowienia:** usunąć ziemię urodzajną (0,4 m). Spód ław ścian zewnętrznych i stóp słupów wiaty **≥ 1,0 m**
  poniżej projektowanego terenu. Ławy wewnętrzne ≥ 0,5 m poniżej przyległego terenu lub posadzki (PN-81 p. 2.2.2 a).
  Uzasadnienie: h_z = 0,8 m (PN-81, strefa I), grunt niewysadzinowy, rezerwa na dane ITB o przemarzaniu (Z₅₀ ≈ 1,3 m, R5-94)
  i na możliwe przewarstwienia. Zasypki przy fundamentach wykonać z niewysadzinowego piasku; odwodnienie powierzchniowe od budynku.
  Wariant: płyta fundamentowa z izolacją obwodową. Wymaga osobnego uzasadnienia termicznego wg PN-EN ISO 13793:2002 „Właściwości cieplne budynków – Projektowanie cieplne posadowień budynków w celu uniknięcia wysadzin mrozowych” (PKN: aktualna, wersja polska — zweryfikowano).
* **Przyłącza:** wodociąg ≥ 1,2 m przykrycia do wierzchu rury (h_z + 0,4 m, R5-95). Przekazać zespołom PZT i instalacji sanitarnych.

### 3.9 Pożar
* Brak wymagań R/REI dla konstrukcji (WT § 213 pkt 1 lit. a). Otulenia wg trwałości (sekcja 3.6) zapewniają w praktyce R30 w metodzie
  tabelarycznej PN-EN 1992-1-2 — ocena R5, nie wymóg; NIEZWERYFIKOWANE. **Utrzymać liczbę kondygnacji nadziemnych = 3.**
  Wyłaz na dach techniczny nie może tworzyć kondygnacji.

### 3.10 Dane klimatyczne dla zespołów fizyki budowli i instalacji
* θ_e = **−18 °C** (strefa II), θ_m,e = **7,9 °C** (R5-110). Status PN-EN 12831-1:2017-08 i jej NA — do potwierdzenia.

### 3.11 Propozycja wpisu do modelu (`model/budynek.yaml`, sekcja parametrów konstrukcyjnych — do uzgodnienia ze schematem)
```yaml
konstrukcja:
  normy_generacja: "Eurokody 1. edycja, wersje PL + NA"   # R5-01..03
  klasa_konsekwencji: {EN1990: CC2, K_FI: 1.0, EN1991_1_7: CC1}   # R5-12, R5-13
  okres_uzytkowania_lat: 50                                   # R5-14
  kombinacje: {STR: "6.10a/6.10b", gG_sup: 1.35, gG_inf: 1.00, xi: 0.85, gQ: 1.50, EQU: {gG_sup: 1.10, gG_inf: 0.90, gQ: 1.50}}
  snieg: {strefa: 2, s_k: 0.90, C_e: 1.0, C_t: 1.0, mu1: 0.8, s_dach: 0.72, gamma_sniegu: 2.0, mu_w_max: 4.0, przypadki: [A, B2]}   # B2 = zaspy wyjątkowe, zał. B (weryfikacja)
  wiatr: {strefa: 1, v_b0: 22.0, q_b: 0.30, c_dir: 1.0, kategoria_terenu_obwiednia: II, c_e_II: "2.3*(z/10)^0.24, zmin=2", q_p_h: 0.71}   # 0.72 dopuszczalne jako zaokrąglenie w górę
  uzytkowe: {strop_A: [2.0, 3.0], schody_A: [4.0, 4.0], taras_A: [4.0, 3.0], dach_H: [0.4, 1.0], dzialowe_lekkie: 0.8}
  beton: {gamma_c: 1.4, gamma_s: 1.15, XC1: {klasa: C25/30, c_nom: 25}, XC2: {klasa: C25/30, c_nom: 35}, XC3: {klasa: C30/37, c_nom: 35}, XC4_XF1: {klasa: C30/37, c_nom: 40}}
  stal_zbrojeniowa: {gatunek: B500SP, klasa_ciagliwosci: C, f_yk: 500}
  mur: {wyrob: "silikat gr.1 kat.I kl.20, zaprawa cienkowarstwowa", K: 0.60, f_k: 7.66, gamma_M: 1.7, klasa_wykonania: A}
  stal_konstrukcyjna: {gatunek: S355, gamma_M0: 1.0, gamma_M1: 1.0}
  geotechnika: {kategoria: II, podejscie: "DA2*", gR_v: 1.4, gR_h: 1.1, h_z: 0.8, D_min_zewn: 1.0, D_min_wewn: 0.5, s_max_mm: 50}
  pozar: {wymagania_R: brak, podstawa: "WT §213 pkt 1 lit. a (status R3)"}
klimat: {theta_e: -18, theta_me: 7.9, strefa: II}
```

---

## 4. Nierozstrzygnięte

* **N-1 (R3): status WT.** W ELI WT ma status „uznany za uchylony” od 2026-09-21. Przyczyną jest uchylenie wynikające z Dz.U. 2019 poz. 1696,
  czyli ustawy o dostępności. Tymczasem od powołań WT zależą ustalenia R5: § 204 ust. 4 z Zał. 1 poz. 49 (normy projektowania),
  § 213 (zwolnienie z wymagań pożarowych) i § 204 ust. 3 z PN-B-02171. Trzeba sprawdzić, czy nowe rozporządzenie ma odpowiedniki tych
  przepisów i czy nadal odsyła do Eurokodów w wersji polskiej. ~~Dodatkowo Dz.U. 2026 poz. 646 zmienia art. 7 ust. 2 Pb (delegacja WT).~~
  *Poprawione w weryfikacji:* Dz.U. 2026 poz. 646 (art. 5) zmienia w Pb **tylko art. 33 ust. 2 pkt 13** (oświadczenie o obiekcie ochrony ludności),
  a nie art. 7 ust. 2. Kluczowa jest **Dz.U. 2026 poz. 1161, art. 2 pkt 4**, która dodaje **art. 102a–102c PB**: przez 18 miesięcy od 20.09.2026
  PZT/PAB, a także PT (ust. 2), można sporządzić według przepisów z art. 7 ust. 2 pkt 1 obowiązujących do 19.09.2026, po złożeniu oświadczenia inwestora.
  R3 przyjął (R3_warunki_techniczne.md, pkt 3 i 7) projektowanie według WT w brzmieniu na 19.09.2026 na podstawie art. 102a PB.
  Powołania R5 na WT (§ 204 ust. 4 z Zał. 1 poz. 49, § 213, § 96 ust. 1) należy więc zapisywać jako „WT (t.j. Dz.U. 2022 poz. 1225 ze zm.)
  stosowane na podstawie art. 102a PB”.
* **N-2: wartości q_k i Q_k kategorii A w PL NA do PN-EN 1991-1-1.** Nie udało się ich potwierdzić. Zastosowano górne granice
  przedziałów EN, bezpieczne w każdym wariancie. Po uzyskaniu PN-EN 1991-1-1:2004/NA:2010 można je obniżyć,
  np. stropy 2,0 kN/m² i 2,0 kN, schody 3,0 kN/m².
* **N-3: PL NA do PN-EN 1992-1-1 — wydania NA:2016-11 i NA:2018-11 (Ap2, Ap3).** Nie zweryfikowano, czy zmieniły γ_c, α_cc, Tabl. 4.3N/4.4N
  (c_min,dur, modyfikacja klasy konstrukcji dla płyt i betonów ≥ C30/37) oraz zał. E. Wartości w rejestrze pochodzą ze źródeł
  opartych na NA:2010. Otulenia przy betonowaniu na podłożu (40 i 75 mm) oraz l/500 z p. 7.4.1(5) podano z pamięci.
* **N-4: ROZSTRZYGNIĘTE w weryfikacji** — NA, Tabl. NA.3: kategoria II c_e(z) = 2,3·(z/10)^0,24, z_min = 2 m (przedruk PW MEiL).
  Tabelę 3.5 przeliczono; q_p(11 m) = 0,71 kN/m². Otwarte pozostają wybór kategorii terenu dla sektorów i c_dir z mapy NA — do PT.
* **N-5: mapa h_z z PN-81/B-03020 dla Poznania.** Przerys wskazuje strefę I (0,8 m), ale źródła internetowe są niespójne (0,8 / 1,0 / 1,2 m).
  Należy potwierdzić na oryginale normy (egzemplarz archiwalny PKN). Zaleconą głębokość 1,0 m dla ścian zewnętrznych i słupów wiaty
  dobrano tak, by pokryć wartości 0,8 i 1,0 m.
* **N-6: Tabl. NA.3 do PN-EN 1997-1 (zał. H).** Nie ustalono, którego typu budynku dotyczą s_max = 50 mm, Δ = 10 mm i ω = 0,003 rad
  (przykład UWM). Należy to potwierdzić w tekście NA (Ap2:2010).
* **N-7: PN-EN 12831-1:2017-08.** *Częściowo rozstrzygnięte w weryfikacji (PKN):* norma jest aktualna, tylko w wersji angielskiej,
  i zastąpiła PN-EN 12831:2006 (wycofana). Nadal nieznana jest zawartość zał. NA/NB (tabela temperatur wg stacji?).
  Wartości −18 °C / 7,9 °C pochodzą z NA do PN-EN 12831:2006 (zespół instalacyjny).
* **N-8: zapisy EN podane z pamięci, bez weryfikacji w tej sesji.** Są to: μ₂ przy attykach (6.2), tablica c_pe 7.2, γ_M2 = 1,25,
  EXC2 jako domyślna klasa wykonania (PN-EN 1090-2), zakres badań PN-EN 1997-2 zał. B.3 i ψ₁/ψ₂ temperatury.
  Przed wydaniem PT sprawdzić je w tekstach norm.
* **N-9: parametry wyrobów.** Chodzi o f_b znormalizowane konkretnych bloków (DWU), ciężar i balast PV oraz nośność i ETA łączników
  termoizolacyjnych wsporników. Dane te uzupełnić przy doborze wyrobów.
* **N-10: sprawdzenie projektu.** Prawo tego nie wymaga dla domu jednorodzinnego (R5-07). R5 rekomenduje dobrowolne sprawdzenie
  części konstrukcyjnej ze względu na wsporniki. Decyzję podejmuje projektant lub inwestor.
* **N-11 (nowe z weryfikacji): norma betonowa.** W katalogu PKN (stan 25.09.2026) PN-EN 206+A2:2021-08 i PN-B-06265:2022-08 (+Az1:2025-08)
  są wycofane. Zastąpiły je PN-EN 206-1:2026-09 i PN-EN 206-2:2026-09, wyłącznie w wersji angielskiej. Eurokod 2 w 1. edycji
  (PN-EN 1992-1-1:2008 + NA) posługuje się klasami ekspozycji XC/XF z EN 206. Nie wiadomo, czy nowa EN 206-1:2026 je zachowuje,
  czy wprowadza klasy odporności ekspozycyjnej 2. generacji — NIEZWERYFIKOWANE. Propozycja: w PT specyfikować beton klasą wytrzymałości,
  klasą ekspozycji (XC/XF), maks. w/c, kruszywem F2 i konsystencją „wg PN-EN 206+A2:2021-08 i PN-B-06265:2022-08 (normy wycofane,
  stosowane jako wiedza techniczna — R5-91 — dla spójności z EC2 1. edycji)”. Przed wydaniem PT potwierdzić z wytwórnią betonu,
  wg której normy deklaruje zgodność.
* **N-12 (nowe z weryfikacji): sytuacja wyjątkowa śniegu B2.** NA wymaga B2 (R5-33). Wzory zał. B (B.3, B.4) trzeba potwierdzić
  w tekście normy. Dla uskoków brył LAMELA obciążenie zaspą wyjątkową może przekroczyć 3,6 kN/m².
