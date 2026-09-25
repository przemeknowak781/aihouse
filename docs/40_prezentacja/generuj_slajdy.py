from pathlib import Path
OUT = Path(__file__).parent / "project" / "slides"
MONO = "font-family:'IBM Plex Mono', 'Courier New', monospace"
DISP = "font-family:'Archivo', Arial, sans-serif"
SEC_L = "background:#F4F4F0; color:#1F2427; font-family:'IBM Plex Sans', Arial, sans-serif; padding:128px 128px 160px 128px; display:flex; flex-direction:column; gap:40px"
SEC_D = "background:#1F2427; color:#F4F4F0; font-family:'IBM Plex Sans', Arial, sans-serif; padding:128px 128px 160px 128px; display:flex; flex-direction:column; gap:40px"

def head(eyebrow, title, dark=False):
    acc = "#C8925E" if dark else "#7A5130"
    col = "#F4F4F0" if dark else "#1F2427"
    return (f'  <div style="display:flex; flex-direction:column; gap:16px">\n'
            f'    <p style="{MONO}; font-size:24px; letter-spacing:3px; text-transform:uppercase; color:{acc}">{eyebrow}</p>\n'
            f'    <h2 style="{DISP}; font-size:72px; font-weight:800; line-height:1.0; letter-spacing:-1px; color:{col}">{title}</h2>\n'
            f'  </div>\n')

def foot(label, dark=False):
    col = "#B9BDB8" if dark else "#4E5458"
    return (f'  <div style="position:absolute; left:128px; bottom:64px; width:1664px; display:flex; justify-content:space-between; {MONO}; font-size:24px; color:{col}">\n'
            f'    <p>Dom LAMELA · projekt przykładowy</p>\n    <p>{label}</p>\n  </div>\n')

def img(blob, alt, w, h, fit="contain", extra=""):
    return f'<img src="/_blob/{blob}" alt="{alt}" style="width:{w}px; height:{h}px; object-fit:{fit}; border-radius:8px; {extra}">'

def stat(num, label, width, numsize=72, dark=False):
    line = "#F4F4F0" if dark else "#1F2427"
    return (f'      <div style="display:flex; flex-direction:column; gap:8px; width:{width}px; border-top:2px solid {line}; padding-top:16px">\n'
            f'        <p style="{DISP}; font-size:{numsize}px; font-weight:800; line-height:1.0; letter-spacing:-1px">{num}</p>\n'
            f'        <p style="font-size:26px; line-height:1.35">{label}</p>\n      </div>\n')

def write(sid, body, notes, dark=False, transition=None):
    tr = f' data-transition="{transition}"' if transition else ""
    html = f'<section id="{sid}"{tr} style="{SEC_D if dark else SEC_L}">\n{body}  <aside>{notes}</aside>\n</section>\n'
    (OUT / f"{sid}.html").write_text(html, encoding="utf-8")

# ---------------------------------------------------------------- zadanie
rows = [("Koncepcja", "Układ funkcji, doświetlenie, orientacja, zagospodarowanie działki"),
        ("Model 3D", "Szczegółowy model spójny z rysunkami i obliczeniami"),
        ("Technologia", "Każdy element: nośność, współczynnik U, zgodność z WT 2021"),
        ("Rysunki", "PZT, projekt architektoniczno-budowlany i techniczny z instalacjami"),
        ("Opisy", "Oświadczenia, obliczenia i zestawienia spójne z rysunkami"),
        ("Sprzedaż", "Strona projektu gotowego")]
r = "".join(f'      <div style="display:flex; gap:24px; align-items:baseline; border-top:1px solid #D5D7D1; padding-top:14px">\n'
            f'        <p style="{MONO}; font-size:24px; color:#7A5130; width:220px">{a}</p>\n'
            f'        <p style="font-size:26px; line-height:1.3; width:596px">{b}</p>\n      </div>\n' for a, b in rows)
write("zadanie", head("Punkt wyjścia", "Szkic Inwestora i zakres zlecenia")
      + '  <div style="display:flex; gap:64px; align-items:start">\n    '
      + img("d66388030e2e5e27989b1b9d7382abb4", "Szkic koncepcyjny Inwestora: elewacja domu z przesuniętymi względem siebie bryłami", 760, 570, extra="background:#FFFFFF; border:1px solid #D5D7D1")
      + f'\n    <div style="display:flex; flex-direction:column; gap:18px; width:840px">\n{r}    </div>\n  </div>\n'
      + foot("Zadanie"),
      "Punktem wyjścia był odręczny szkic elewacji. Zlecenie objęło całą drogę do wniosku o pozwolenie na budowę: koncepcję, model 3D, "
      "dobór technologii z obliczeniami, komplet rysunków projektu zagospodarowania terenu, projektu architektoniczno-budowlanego i technicznego, "
      "część opisową oraz stronę sprzedażową projektu gotowego. Działka, plan miejscowy i grunt zostały przyjęte przykładowo.")

# ---------------------------------------------------------------- interpretacja
leg = [("A", "Bryła II piętra w pionowych lamelach; wspornik 1,00 m jak w szkicu"),
       ("B", "Pełna bryła I piętra"),
       ("C", "Boks w ramie stalowej: 3 kwatery przeszklenia wysunięte o 1,00 m"),
       ("D", "Głęboka krawędź na +3,85 m, ciągła do narożnika garażu"),
       ("E", "Parter: przeszklenie strefy dziennej w 5 kwaterach o narastającym rytmie"),
       ("G", "Garaż w bryle parteru, z dachem zielonym")]
l = "".join(f'      <div style="display:flex; gap:20px; align-items:start">\n'
            f'        <p style="width:48px; height:48px; border-radius:24px; background:#1F2427; color:#F4F4F0; {DISP}; font-size:26px; font-weight:800; line-height:48px; text-align:center">{a}</p>\n'
            f'        <p style="font-size:26px; line-height:1.3; width:620px">{b}</p>\n      </div>\n' for a, b in leg)
write("interpretacja", head("Interpretacja szkicu", "Sylweta „S” z przesuniętych brył")
      + '  <div style="display:flex; gap:56px; align-items:start">\n    '
      + img("8b8d097a1a123c7f53716ffccd01b044", "Interpretacja szkicu: bryły A, B, C, D, E i G oznaczone na elewacji", 920, 592, extra="background:#FFFFFF")
      + f'\n    <div style="display:flex; flex-direction:column; gap:16px; width:688px">\n{l}'
      + f'      <p style="font-size:24px; line-height:1.35; background:#E6E7E2; border-radius:8px; padding:16px 20px">Po korekcie Inwestora linia „S” wynika z przesunięcia brył, a nie z płyty tarasowej; garaż mieści się w bryle parteru.</p>\n'
      + '    </div>\n  </div>\n' + foot("Zadanie"),
      "Szkic odczytaliśmy jako układ brył przesuniętych względem siebie. Najwyższa bryła A wysuwa się o metr jak na szkicu, pod nią leży pełna bryła B, "
      "a boks C w stalowej ramie tworzy przeszklony pokój rodzinny. Pozioma krawędź D biegnie aż do narożnika garażu. Pierwsza interpretacja z płytą tarasową "
      "została odrzucona po uwagach Inwestora.")

# ---------------------------------------------------------------- metoda
cards = [("Obliczenia", "Konstrukcja, fizyka budowli, energia, instalacje"),
         ("Rysunki", "Zagospodarowanie, architektura, detale, konstrukcja, instalacje"),
         ("Tomy PDF", "5 tomów składanych automatycznie, z kontrolą kompletności"),
         ("3D i wizualizacje", "Model do obracania i rendery w kontekście działki"),
         ("Strona www", "Katalog projektu gotowego zasilany danymi z modelu")]
c = "".join(f'      <div style="height:84px; background:#FFFFFF; border:1px solid #D5D7D1; border-radius:10px; padding:0px 28px; display:flex; align-items:center; gap:24px">\n'
            f'        <p style="{DISP}; font-size:30px; font-weight:700; width:300px">{a}</p>\n'
            f'        <p style="font-size:24px; line-height:1.3; color:#4E5458; width:740px">{b}</p>\n      </div>\n' for a, b in cards)
write("metoda", head("Metoda", "Jeden model, wiele wyników")
      + '  <div style="display:flex; gap:32px; align-items:center">\n'
      + f'    <div style="width:420px; height:480px; background:#1F2427; color:#F4F4F0; border-radius:12px; padding:40px; display:flex; flex-direction:column; justify-content:center; gap:20px">\n'
      + f'      <p style="{MONO}; font-size:24px; letter-spacing:2px; text-transform:uppercase; color:#C8925E">Jedno źródło danych</p>\n'
      + f'      <p style="{DISP}; font-size:44px; font-weight:800; line-height:1.05">Model budynku</p>\n'
      + '      <p style="font-size:24px; line-height:1.4; color:#E6E7E2">Bryły, ściany, otwory, pomieszczenia, warstwy przegród, wyposażenie, instalacje i działka</p>\n    </div>\n'
      + f'    <p style="{DISP}; font-size:72px; font-weight:800; color:#7A5130; width:64px">→</p>\n'
      + f'    <div style="display:flex; flex-direction:column; gap:15px; width:1116px">\n{c}    </div>\n  </div>\n'
      + f'  <div style="background:#E6E7E2; border-radius:10px; padding:20px 28px; display:flex; gap:24px; align-items:center">\n'
      + f'    <p style="{MONO}; font-size:24px; letter-spacing:2px; text-transform:uppercase; color:#7A5130; width:180px">Kontrola</p>\n'
      + '    <p style="font-size:24px; line-height:1.35; width:1400px">Panel 3 sędziów koncepcji · audyty A1–A3 · weryfikacje krzyżowe tomów · nadzór pracy zespołów co 3 min · plansza postępu co 10 min</p>\n  </div>\n'
      + foot("Metoda"),
      "Wszystko wychodzi z jednego modelu budynku zapisanego w plikach tekstowych. Z niego powstają obliczenia, rysunki, tomy, wizualizacje i strona. "
      "Dzięki temu zmiana wprowadzona raz trafia wszędzie. Każdy etap sprawdzają niezależni weryfikatorzy, a postęp jest dokumentowany planszami.")

# ---------------------------------------------------------------- przebieg
write("przebieg", head("Przebieg prac", "Plansza postępu co 10 minut")
      + '  <div style="display:flex; gap:56px; align-items:start">\n    '
      + img("6024828c63d02691e24a954aa1562899", "Przykładowa plansza postępu A4 poziomo z godziną, kolażem rysunków i listą etapów", 860, 608, extra="background:#FFFFFF; border:1px solid #D5D7D1")
      + '\n    <div style="display:flex; flex-direction:column; gap:36px; width:748px">\n'
      + stat("46", "plansz postępu A4 z godziną wykonania — od analizy szkicu do etapu wydania (stan na 25.09, 7:42)", 748)
      + stat("co 3 min", "strażnik procesu sprawdza, czy zespoły pracują, i zgłasza zastoje", 748)
      + stat("3 kroki", "w każdym etapie: wykonanie → niezależna weryfikacja → poprawki", 748)
      + '    </div>\n  </div>\n' + foot("Metoda"),
      "Co dziesięć minut powstawała plansza A4 z godziną, najważniejszymi rysunkami i stanem etapów. Osobny strażnik co trzy minuty sprawdzał, czy prace "
      "nie utknęły. Każdy etap kończył się niezależną weryfikacją, a znalezione błędy wracały do poprawy, zanim prace poszły dalej.")

# ---------------------------------------------------------------- koncepcja
write("koncepcja", head("Koncepcja", "Trzy warianty i panel sędziów")
      + '  <div style="display:flex; gap:56px; align-items:start">\n    '
      + img("58a6fb4784dca3ff420fd5f9faf43efa", "Werdykt panelu trzech sędziów: oceny wariantów W1, W2 i W3 w kryteriach", 1100, 550, extra="background:#FFFFFF")
      + '\n    <div style="display:flex; flex-direction:column; gap:32px; width:508px">\n'
      + stat("72,7 pkt", "W2 — najwyższa średnia i 2 z 3 głosów (W1 70,7 · W3 66,0)", 508)
      + stat("15", "rozwiązań przeszczepionych z wariantów W1 i W3", 508)
      + stat("28", "poprawek obowiązkowych sędziów przed syntezą", 508)
      + '    </div>\n  </div>\n' + foot("Koncepcja"),
      "Powstały trzy niezależne warianty. Trzech sędziów oceniło je w tych samych kryteriach; wygrał wariant W2 z najwyższą średnią i dwoma głosami z trzech. "
      "Koncepcja ostateczna to W2 wzbogacony o piętnaście najlepszych rozwiązań z pozostałych wariantów i o wszystkie obowiązkowe poprawki sędziów.")

# ---------------------------------------------------------------- zgodnosc
write("zgodnosc", head("Zgodność ze szkicem", "Model wierny szkicowi")
      + '  <div style="display:flex; gap:64px; align-items:start">\n    '
      + img("c48ee26f24bec2f7d26417ac3ff4ae4b", "Nałożenie konturów modelu na szkic Inwestora z pomiarem odchyłek krawędzi brył", 800, 613, extra="background:#FFFFFF")
      + '\n    <div style="display:flex; flex-direction:column; gap:32px; width:800px">\n'
      + stat("0,59 m", "największa odchyłka krawędzi — bryła B (I piętro) wydłużona do 12,60 m", 800, numsize=96)
      + stat("≤ 0,37 m", "pozostałe krawędzie brył A, C, D i E; rama boksu C i linia pozioma D do 0,08 m", 800)
      + '      <p style="font-size:24px; line-height:1.4; color:#4E5458">Pomiar w skali szkicu (45,8 px na metr), od lica zachodniego bryły B. Odchyłki wynikają z modułu konstrukcji i wymiarów pomieszczeń.</p>\n'
      + '    </div>\n  </div>\n' + foot("Koncepcja"),
      "Kontury modelu nałożyliśmy na szkic w tej samej skali. Największa różnica to 59 centymetrów na długości bryły pierwszego piętra, "
      "pozostałe krawędzie mieszczą się w 37 centymetrach, a rama boksu i linia pozioma w kilku centymetrach. Sylweta ze szkicu została zachowana.")

# ---------------------------------------------------------------- rzuty
fl = [("Parter · 95,33 m²", "Salon z jadalnią i kuchnią 54,44 m², pokój gościnny, łazienka, pomieszczenie techniczne; garaż 37,42 m² liczony osobno"),
      ("I piętro · 84,39 m²", "Pokój rodzinny w boksie C 28,36 m², dwa pokoje dzieci, łazienka, WC z natryskiem, pralnia"),
      ("II piętro · 59,42 m²", "Sypialnia rodziców 21,43 m² z garderobą i łazienką, gabinet 16,25 m²")]
f = "".join(f'      <div style="display:flex; flex-direction:column; gap:6px; border-top:1px solid #D5D7D1; padding-top:14px">\n'
            f'        <p style="{DISP}; font-size:30px; font-weight:700">{a}</p>\n'
            f'        <p style="font-size:24px; line-height:1.35; color:#4E5458">{b}</p>\n      </div>\n' for a, b in fl)
write("rzuty", head("Funkcja", "Dom na trzech kondygnacjach")
      + '  <div style="display:flex; gap:56px; align-items:start">\n    '
      + img("f9ef4144dd3c5b7e92b23c6f96868a25", "Rzut parteru z otwartą strefą dzienną, garażem i pomieszczeniem technicznym", 978, 615, extra="background:#FFFFFF")
      + f'\n    <div style="display:flex; flex-direction:column; gap:20px; width:630px">\n{f}'
      + '      <p style="font-size:24px; line-height:1.4; color:#4E5458">Powierzchnia użytkowa bez klatek schodowych, garażu i pomieszczeń technicznych.</p>\n'
      + '    </div>\n  </div>\n' + foot("Koncepcja"),
      "Parter to otwarta strefa dzienna od strony ogrodu, pokój gościnny i garaż w bryle domu. Na pierwszym piętrze są pokoje dzieci i pokój rodzinny w przeszklonym boksie, "
      "a na drugim apartament rodziców z garderobą i gabinetem. Powierzchnię użytkową liczymy bez klatek, garażu i pomieszczeń technicznych.")

# ---------------------------------------------------------------- parametry (dark)
P = [("239,13 m²", "powierzchnia użytkowa", "P0 95,33 · P1 84,39 · P2 59,42 m²"),
     ("187,50 m²", "powierzchnia zabudowy: 11,7 % działki, limit 30 %", "upzp art. 2 pkt 35"),
     ("79,4 %", "powierzchnia biologicznie czynna, minimum 50 %", "upzp art. 2 pkt 28–29"),
     ("10,47 m", "wysokość zabudowy, limit 11,0 m; szczyt: wyrzutnia wentylacji", "upzp art. 2 pkt 30 lit. a"),
     ("35,6", "EP kWh/(m²·rok) z PV; 57,8 bez PV; limit 70", "WT 2021, zał. 2"),
     ("7,41 kW", "projektowe obciążenie cieplne budynku", "PN-EN 12831-1")]
cc = "".join(f'      <div style="width:533px; height:290px; background:#2A3034; border-radius:12px; padding:32px; display:flex; flex-direction:column; justify-content:space-between">\n'
             f'        <p style="{DISP}; font-size:72px; font-weight:800; line-height:1.0; letter-spacing:-1px; color:#F4F4F0">{a}</p>\n'
             f'        <div style="display:flex; flex-direction:column; gap:10px">\n'
             f'          <p style="font-size:26px; line-height:1.3; color:#E6E7E2">{b}</p>\n'
             f'          <p style="{MONO}; font-size:24px; color:#C8925E">{s}</p>\n        </div>\n      </div>\n' for a, b, s in P)
write("parametry", head("Parametry", "Liczby z modelu, z podstawą prawną", dark=True)
      + f'  <div style="display:flex; flex-wrap:wrap; gap:32px; width:1664px">\n{cc}  </div>\n'
      + foot("Koncepcja · wartości robocze przed zamrożeniem modelu", dark=True),
      "Wszystkie wskaźniki liczy jeden moduł z modelu, zgodnie z definicjami ustawy o planowaniu i zagospodarowaniu przestrzennym. Wysokość zabudowy mierzymy do najwyższego punktu "
      "razem z urządzeniami na dachu, od średniej rzędnej terenu przy ścianach. Wskaźnik EP spełnia wymaganie również bez fotowoltaiki. Wartości są robocze; ostateczne "
      "podamy po zamrożeniu modelu.", dark=True, transition="fade")

# ---------------------------------------------------------------- woda
W = [("Spadki", "każde pole dachu ma spadek co najmniej 2 %, własny wpust i przelew awaryjny"),
     ("Odprowadzenie", "wpusty zamiast rzygaczy; na dachu głównym z grzałką i pionami w izolowanym szachcie"),
     ("Retencja", "szczelny zbiornik 5 m³ do podlewania, przelew do niecki chłonnej w ogrodzie"),
     ("Ciągłość", "4 linie ciągłe: izolacja termiczna, paroizolacja i szczelność, hydroizolacja, wiatroizolacja"),
     ("Grunt", "piaski, woda gruntowa ok. 3,8 m p.p.t.: drenaż zbędny — do potwierdzenia badaniami")]
w = "".join(f'      <div style="display:flex; flex-direction:column; gap:4px; border-top:1px solid #D5D7D1; padding-top:12px">\n'
            f'        <p style="{MONO}; font-size:24px; color:#7A5130; text-transform:uppercase; letter-spacing:2px">{a}</p>\n'
            f'        <p style="font-size:24px; line-height:1.35">{b}</p>\n      </div>\n' for a, b in W)
write("woda", head("Woda i izolacje", "Każda kropla ma zaplanowaną drogę")
      + '  <div style="display:flex; gap:56px; align-items:start">\n    '
      + img("a4a5a3acb35bb4f427c15f073cf5d984", "Detal okna pod okapem: ciągłość izolacji cieplnej, wodochronnej i paroizolacji", 900, 463, extra="background:#FFFFFF")
      + f'\n    <div style="display:flex; flex-direction:column; gap:14px; width:708px">\n{w}    </div>\n  </div>\n'
      + foot("Technika"),
      "Na każdym dachu woda ma spadek, wpust i awaryjny przelew. Deszczówka trafia do zbiornika na podlewanie, a jego nadmiar do niecki w ogrodzie. "
      "Na każdym detalu sprawdzamy, czy cztery warstwy przechodzą bez przerw. Warunki gruntowe są przykładowe i wymagają potwierdzenia badaniami.")

# ---------------------------------------------------------------- mostki
M = [("22 węzły", "wg PN-EN ISO 10211, solver sprawdzony na przykładach z normy"),
     ("fRsi ≥ 0,836", "wszędzie powyżej wymaganych 0,72 (WT 2021, zał. 2)"),
     ("30,6 W/K", "strata przez mostki; z wartości domyślnych ok. 138 W/K")]
m = "".join(f'      <div style="width:533px; background:#FFFFFF; border:1px solid #D5D7D1; border-radius:12px; padding:22px 28px; display:flex; flex-direction:column; gap:8px">\n'
            f'        <p style="{DISP}; font-size:48px; font-weight:800; line-height:1.0">{a}</p>\n'
            f'        <p style="font-size:24px; line-height:1.3; color:#4E5458">{b}</p>\n      </div>\n' for a, b in M)
write("mostki", head("Mostki cieplne", "Mostki policzone, nie przyjęte")
      + '  ' + img("ee2e291d131cfc669d7a0632389694de", "Rozkład temperatur w węźle progu drzwi przesuwnych HS z izotermami", 1500, 391, extra="background:#FFFFFF") + '\n'
      + f'  <div style="display:flex; gap:32px">\n{m}  </div>\n'
      + foot("Technika"),
      "Zamiast wartości domyślnych policzyliśmy 22 najważniejsze węzły metodą elementów skończonych w dwóch wymiarach. Na ekranie próg dużych drzwi przesuwnych. "
      "Najzimniejszy punkt po wewnętrznej stronie przegród jest bezpieczny, a łączne straty przez mostki są ponad czterokrotnie mniejsze niż przy wartościach tabelarycznych.")

# ---------------------------------------------------------------- konstrukcja
write("konstrukcja", head("Konstrukcja", "Obliczenia i zbrojenie")
      + '  <div style="display:flex; gap:64px; align-items:start">\n    '
      + img("14603193b707990c663708aed3498bb8", "Rysunek zbrojenia schodów żelbetowych z zestawieniem prętów", 510, 631, extra="background:#FFFFFF; border:1px solid #D5D7D1")
      + '\n    <div style="display:flex; flex-direction:column; gap:28px; width:1090px">\n'
      + '      <div style="display:flex; gap:32px">\n'
      + stat("26", "arkuszy rysunków konstrukcji", 340, numsize=56)
      + stat("333 s.", "obliczeń statycznych: MES płyt, obwiednie, ugięcia", 340, numsize=56)
      + stat("273 / 275", "pozycji zbrojenia z As,prov ≥ As,req", 346, numsize=56)
      + '      </div>\n'
      + '      <div style="background:#E6E7E2; border-radius:10px; padding:24px 28px; display:flex; flex-direction:column; gap:10px">\n'
      + f'        <p style="{MONO}; font-size:24px; letter-spacing:2px; text-transform:uppercase; color:#7A5130">Otwarte w etapie wydania</p>\n'
      + '        <p style="font-size:24px; line-height:1.4">2 pozycje zbrojenia do poprawy; słup w osi C/3, filarki parteru i zakotwienie wspornika bryły A — pętla konstrukcyjna do pełnej zgodności.</p>\n'
      + '      </div>\n'
      + '      <p style="font-size:24px; line-height:1.4; color:#4E5458">Na rysunku: w narożu wklęsłym schodów pręty proste, krzyżowane z długością zakotwienia wg PN-EN 1992-1-1 (p. 8.4) — zamiast pręta giętego, który wyrywa otulinę.</p>\n'
      + '    </div>\n  </div>\n' + foot("Technika"),
      "Konstrukcja ma 26 arkuszy rysunków i ponad trzysta stron obliczeń, w tym analizę płyt metodą elementów skończonych. Kontrola zbrojenia wykazała dwie pozycje do poprawy, "
      "a kilka elementów przechodzi jeszcze przez pętlę konstrukcyjną w etapie wydania. Mówimy o tym otwarcie, bo projekt nie jest jeszcze zamknięty.")

# ---------------------------------------------------------------- dokumentacja
T = [("Tom I", "Zagospodarowanie terenu, projekt architektoniczno-budowlany, załączniki"),
     ("PT-1", "Projekt techniczny — architektura i detale"),
     ("PT-2", "Konstrukcja z obliczeniami statycznymi (333 s.)"),
     ("PT-3", "Instalacje sanitarne i charakterystyka energetyczna"),
     ("PT-4", "Instalacje elektryczne i fotowoltaika")]
t = "".join(f'      <div style="display:flex; gap:24px; align-items:center; border-top:1px solid #D5D7D1; padding:18px 0px">\n'
            f'        <p style="{DISP}; font-size:30px; font-weight:800; width:130px">{a}</p>\n'
            f'        <p style="font-size:26px; line-height:1.3; width:690px">{b}</p>\n'
            f'        <p style="{MONO}; font-size:24px; color:#7A5130; width:140px">roboczy</p>\n      </div>\n' for a, b in T)
write("dokumentacja", head("Dokumentacja", "5 tomów i oszczędny układ arkuszy")
      + '  <div style="display:flex; gap:64px; align-items:start">\n'
      + f'    <div style="display:flex; flex-direction:column; width:1040px">\n{t}    </div>\n'
      + '    <div style="display:flex; flex-direction:column; gap:14px; width:560px">\n      '
      + img("4dbc5148cfca8722a75ceb3e99aad14b", "Arkusz PB-AR-01 z rzutem parteru w formacie 630 na 594 mm", 520, 490, extra="background:#FFFFFF; border:1px solid #D5D7D1")
      + '\n      <p style="font-size:24px; line-height:1.35; color:#4E5458">PB-AR-01, 630×594 mm, wypełnienie 93 %. Komplet AR: 5 arkuszy zamiast 10, papier −42 %</p>\n'
      + '    </div>\n  </div>\n' + foot("Dokumentacja"),
      "Dokumentacja ma pięć tomów: tom pierwszy do wniosku o pozwolenie na budowę i cztery tomy projektu technicznego. Wszystkie są w wersji roboczej. "
      "Formaty arkuszy dobiera program pod rysunek zamiast sztywnych wielokrotności A3, dzięki czemu komplet architektury zmieścił się na pięciu arkuszach zamiast dziesięciu i zużywa o 42 procent mniej papieru, a arkusze nadal składają się do A4.")

# ---------------------------------------------------------------- wizualizacje
write("wizualizacje", head("Wizualizacje", "Bryła w kontekście działki")
      + '  <div style="display:flex; gap:32px; align-items:start">\n    '
      + img("322da07067d675d28344b2e1a39136d4", "Widok lotniczy domu na działce z ogrodem od południa", 1088, 612, fit="cover")
      + '\n    <div style="display:flex; flex-direction:column; gap:16px; width:544px">\n      '
      + img("dfe54a3f1abb658020f74ed2c2b329b9", "Widok domu od strony ulicy z podjazdem do garażu", 544, 298, fit="cover")
      + '\n      '
      + img("f3b02d2a3c605b036123c887be7f440c", "Aksonometria brył domu", 544, 298, fit="cover", extra="background:#FFFFFF")
      + '\n    </div>\n  </div>\n' + foot("Dokumentacja"),
      "Wizualizacje powstają z tego samego modelu co rysunki, więc pokazują dokładnie projektowaną bryłę. Widok lotniczy pokazuje dom w ogrodzie, "
      "widok od ulicy wjazd do garażu, a aksonometria układ przesuniętych brył.")

# ---------------------------------------------------------------- www
X = [("Marka przykładowa", "„Pasmo i Cień” — fikcyjna, wyraźnie oznaczona jako przykład"),
     ("Treść z modelu", "rzuty, parametry, model 3D do obracania i wizualizacje"),
     ("Oferta", "ceny przykładowe i formularz demonstracyjny, który nie wysyła danych"),
     ("Dostęp", "claude.ai/artifact/DVkqc1LzLnchNsDBNVnhTy — prywatna; wersja końcowa po wydaniu")]
x = "".join(f'      <div style="display:flex; flex-direction:column; gap:4px; border-top:1px solid #D5D7D1; padding-top:14px">\n'
            f'        <p style="{MONO}; font-size:24px; color:#7A5130; text-transform:uppercase; letter-spacing:2px">{a}</p>\n'
            f'        <p style="font-size:26px; line-height:1.35">{b}</p>\n      </div>\n' for a, b in X)
write("www", head("Sprzedaż", "Strona projektu gotowego")
      + '  <div style="display:flex; gap:56px; align-items:start">\n    '
      + img("16d49e3e0c0e46f51448320c708e58c1", "Strona katalogowa domu LAMELA: wizualizacja, parametry i przycisk zamówienia", 880, 611, fit="cover", extra="border:1px solid #D5D7D1")
      + f'\n    <div style="display:flex; flex-direction:column; gap:20px; width:728px">\n{x}'
      + '    </div>\n  </div>\n' + foot("Dokumentacja"),
      "Strona katalogowa sprzedaje dom jako projekt gotowy. Marka i ceny są przykładowe, a formularz tylko demonstracyjny. Liczby na stronie pochodzą z modelu, "
      "więc po zamrożeniu modelu wystarczy przebudować stronę.")

# ---------------------------------------------------------------- stan
COLS = [("Gotowe", "#5E7A2F", ["Koncepcja po dwóch rundach poprawek", "Model 3D i robocze rysunki wszystkich branż",
                                "Obliczenia: konstrukcja, mostki, energia, instalacje", "5 tomów i strona www w wersji roboczej"]),
        ("W toku: wydanie", "#7A5130", ["Domknięcie modelu i pętla konstrukcyjna", "Zamrożenie modelu i przeliczenie mostków",
                                         "Regeneracja rysunków i tomów", "Weryfikacja: liczby, prawo, rysunki, funkcja, woda"]),
        ("Przed złożeniem wniosku", "#1F2427", ["Dane Inwestora i oświadczenie o prawie do dysponowania nieruchomością",
                                                 "Projektanci z uprawnieniami: metryki i podpisy", "Mapa do celów projektowych i badania geotechniczne",
                                                 "Warunki przyłączenia, zgoda na zjazd, wybór wyrobów"])]
cols = ""
for nag, kol, items in COLS:
    it = "".join(f'        <p style="font-size:24px; line-height:1.35; border-top:1px solid #D5D7D1; padding-top:12px">{i}</p>\n' for i in items)
    cols += (f'    <div style="width:533px; display:flex; flex-direction:column; gap:14px">\n'
             f'      <p style="{DISP}; font-size:32px; font-weight:800; color:#F4F4F0; background:{kol}; border-radius:8px; padding:14px 20px">{nag}</p>\n{it}    </div>\n')
write("stan", head("Stan prac · 25 września 2026", "Gotowe, w toku, przed wnioskiem")
      + f'  <div style="display:flex; gap:32px; align-items:start">\n{cols}  </div>\n'
      + foot("Stan prac"),
      "Koncepcja, obliczenia i robocze wersje wszystkich tomów są gotowe. Trwa etap wydania: domykamy model, zamrażamy go i generujemy dokumentację na nowo, a potem sprawdzamy ją w pięciu przekrojach. "
      "Przed złożeniem wniosku potrzebne są rzeczy, których projekt przykładowy nie może zastąpić: dane Inwestora, projektanci z uprawnieniami i ich podpisy, mapa do celów projektowych, "
      "badania gruntu oraz uzgodnienia z gestorami sieci i zarządcą drogi.")
print("ok", sorted(p.name for p in OUT.glob("*.html")))
