"""Style rysunkowe: warstwy, grubości linii (grupy wg PN-EN ISO 128-2 / ISO 128-23), rodzaje linii, pismo.

Grubości linii są pojęciem PAPIEROWYM (mm na wydruku) i zależą od podziałki rzutni — dlatego elementy
rysunku odwołują się do ROLI pióra (``'b_cienka'``, ``'cienka'``, ``'srednia'``, ``'gruba'``, ``'b_gruba'``),
a konkretna grubość wynika z grupy linii dobranej do skali (``line_group(scale)``). Można też podać
grubość jawnie w mm (float).

Szereg grubości (PN-EN ISO 128-2): 0,13 · 0,18 · 0,25 · 0,35 · 0,5 · 0,7 · 1,0 · 1,4 · 2,0 mm.
"""
from __future__ import annotations

from dataclasses import dataclass, field

ISO_LINEWEIGHTS = (0.13, 0.18, 0.25, 0.35, 0.5, 0.7, 1.0, 1.4, 2.0)
PEN_ROLES = ("b_cienka", "cienka", "srednia", "gruba", "b_gruba")

# Grupy linii zależne od podziałki (stosunek cienka:gruba:b.gruba ≈ 1:2:4 wg ISO 128-23, z linią średnią
# stosowaną w polskiej praktyce dla krawędzi widocznych i warstw nienośnych).
LINE_GROUPS: dict[str, dict[str, float]] = {
    # arkusz (ramka, tabliczka, legendy — przestrzeń papieru)
    "arkusz": {"b_cienka": 0.13, "cienka": 0.18, "srednia": 0.25, "gruba": 0.35, "b_gruba": 0.7},
    # detale 1:1 … 1:25
    "detal": {"b_cienka": 0.13, "cienka": 0.18, "srednia": 0.35, "gruba": 0.7, "b_gruba": 1.0},
    # 1:50
    "1:50": {"b_cienka": 0.13, "cienka": 0.18, "srednia": 0.25, "gruba": 0.5, "b_gruba": 0.7},
    # 1:100
    "1:100": {"b_cienka": 0.13, "cienka": 0.18, "srednia": 0.25, "gruba": 0.35, "b_gruba": 0.7},
    # 1:200 … 1:1000 (PZT, sytuacje)
    "1:200+": {"b_cienka": 0.13, "cienka": 0.13, "srednia": 0.18, "gruba": 0.35, "b_gruba": 0.5},
}


def line_group_name(scale: float, paper: bool = False) -> str:
    """Nazwa grupy linii dla podziałki 1:scale (paper=True -> przestrzeń arkusza)."""
    if paper:
        return "arkusz"
    if scale <= 25:
        return "detal"
    if scale <= 50:
        return "1:50"
    if scale <= 100:
        return "1:100"
    return "1:200+"


def line_group(scale: float, paper: bool = False) -> dict[str, float]:
    return LINE_GROUPS[line_group_name(scale, paper)]


def pen_mm(pen, scale: float, default_role: str = "cienka", paper: bool = False) -> float:
    """Rozwiązuje pióro (rola lub mm) do grubości w mm dla danej podziałki."""
    if pen is None:
        pen = default_role
    if isinstance(pen, (int, float)):
        return float(pen)
    return line_group(scale, paper)[pen]


# ------------------------------------------------------------------------------------------------ linie
@dataclass(frozen=True)
class Linetype:
    name: str
    description: str
    pattern: tuple  # mm na papierze: >0 kreska, <0 przerwa, 0 kropka (jak w DXF)

    @property
    def period(self) -> float:
        return sum(abs(x) for x in self.pattern)


LINETYPES: dict[str, Linetype] = {lt.name: lt for lt in [
    Linetype("CIAGLA", "Linia ciągła ________", ()),
    Linetype("KRESKOWA", "Linia kreskowa (krawędzie niewidoczne, elementy nad płaszczyzną cięcia) __ __ __",
             (4.0, -1.5)),
    Linetype("KRESKOWA_DROBNA", "Linia kreskowa drobna _ _ _ _", (2.0, -1.0)),
    Linetype("PUNKTOWA", "Linia punktowa (osie, osie symetrii) ____ . ____ . ____", (12.0, -1.5, 0.0, -1.5)),
    Linetype("PUNKTOWA_KROTKA", "Linia punktowa krótka (linie cięcia) __ . __ . __", (6.0, -1.2, 0.0, -1.2)),
    Linetype("DWUPUNKTOWA", "Linia dwupunktowa (elementy usuwane/projektowane, granice) ____ .. ____",
             (12.0, -1.5, 0.0, -1.5, 0.0, -1.5)),
    Linetype("KROPKOWA", "Linia kropkowa . . . . . .", (0.0, -1.0)),
    Linetype("KRESKA_DLUGA", "Linia kreskowa długa (instalacje) ____  ____", (8.0, -2.0)),
]}


# ------------------------------------------------------------------------------------------------ pismo
# Wysokości pisma (h = wysokość wielkich liter, PN-EN ISO 3098-0): szereg 1,8 · 2,5 · 3,5 · 5 · 7 · 10 · 14 mm
TEXT_H = {"xs": 1.8, "s": 2.5, "m": 3.5, "l": 5.0, "xl": 7.0, "xxl": 10.0}

FONT_FILES = {
    "normal": ["/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "bold": ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
    "italic": ["/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"],
    "bolditalic": ["/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"],
}
# Czcionka w DXF: Liberation Sans jest metrycznie zgodna z Arial — układ napisów w CAD będzie identyczny.
DXF_FONTS = {"normal": "arial.ttf", "bold": "arialbd.ttf", "italic": "ariali.ttf", "bolditalic": "arialbi.ttf"}
DXF_TEXT_STYLES = {"normal": "PL_ARIAL", "bold": "PL_ARIAL_B", "italic": "PL_ARIAL_I", "bolditalic": "PL_ARIAL_BI"}


# ------------------------------------------------------------------------------------------------ warstwy
@dataclass(frozen=True)
class LayerDef:
    name: str
    description: str
    role: str = "cienka"          # domyślna rola pióra
    linetype: str = "CIAGLA"
    aci: int = 7                  # kolor ekranowy AutoCAD (7 = biały/czarny)
    plot_rgb: str | None = None   # kolor wydruku w trybie 'branze' (None = czarny)
    plot: bool = True
    z: int = 20                   # domyślna kolejność rysowania linii tej warstwy


_L = LayerDef
LAYERS: dict[str, LayerDef] = {l.name: l for l in [
    # ---- arkusz
    _L("R-RAMKA", "Ramka arkusza, znaki składania i centrowania", "gruba", aci=7, z=29),
    _L("R-TABLICZKA", "Tabliczka rysunkowa (PN-EN ISO 7200)", "cienka", aci=7, z=29),
    _L("R-OPISY", "Opisy arkusza: tytuły rzutni, uwagi, legendy", "cienka", aci=7),
    _L("R-LEGENDA", "Legenda oznaczeń", "cienka", aci=7),
    _L("R-RZUTNIA", "Obrys rzutni (nie drukowany)", "b_cienka", aci=8, plot=False),
    # ---- architektura
    _L("A-SCIANY-KONSTR", "Ściany i słupy konstrukcyjne w przekroju — kontur", "gruba", aci=7, z=22),
    _L("A-SCIANY-DZIAL", "Ścianki działowe w przekroju — kontur", "srednia", aci=7, z=22),
    _L("A-SCIANY-IZOL", "Warstwy izolacji termicznej ścian — kontur", "srednia", aci=4, z=21),
    _L("A-SCIANY-WYK", "Tynki, okładziny, warstwy wykończeniowe — kontur", "b_cienka", aci=8, z=21),
    _L("A-STROPY", "Stropy, płyty, stropodachy w przekroju — kontur", "gruba", aci=7, z=22),
    _L("A-WARSTWY", "Warstwy przegród poziomych (podłogi, dachy) — kontur", "cienka", aci=8, z=21),
    _L("A-IZOL-WODNA", "Izolacje przeciwwodne/przeciwwilgociowe/paroizolacje", "b_gruba", aci=5, z=23),
    _L("A-FUNDAMENTY", "Fundamenty w przekroju — kontur", "gruba", aci=7, z=22),
    _L("A-KRESKOWANIE", "Kreskowanie materiałów (PN-B-01030)", "b_cienka", aci=8, z=10),
    _L("A-WYPELNIENIA", "Wypełnienia (zaczernienia, tła)", "b_cienka", aci=9, z=5),
    _L("A-WIDOK", "Krawędzie widoczne (poza płaszczyzną cięcia)", "cienka", aci=7, z=18),
    _L("A-NIEWIDOCZNE", "Krawędzie niewidoczne", "cienka", "KRESKOWA", aci=8, z=17),
    _L("A-NAD-CIECIEM", "Elementy nad płaszczyzną cięcia (belki, nadproża, okapy)", "cienka", "KRESKOWA", aci=8, z=17),
    _L("A-OKNA", "Stolarka okienna", "srednia", aci=3, z=21),
    _L("A-DRZWI", "Stolarka drzwiowa", "srednia", aci=3, z=21),
    _L("A-SCHODY", "Schody, pochylnie, balustrady", "cienka", aci=6, z=19),
    _L("A-MEBLE", "Meble i wyposażenie ruchome", "b_cienka", aci=8, z=15),
    _L("A-SANITARNE", "Wyposażenie sanitarne i kuchenne", "cienka", aci=6, z=16),
    _L("A-WYMIARY", "Wymiarowanie (PN-B-01029)", "cienka", aci=1, z=25),
    _L("A-OPISY", "Opisy, odnośniki, opisy warstw", "cienka", aci=2, z=26),
    _L("A-POMIESZCZENIA", "Oznaczenia pomieszczeń (PN-EN ISO 4157)", "cienka", aci=2, z=26),
    _L("A-OSIE", "Osie konstrukcyjne", "cienka", "PUNKTOWA", aci=1, z=12),
    _L("A-RZEDNE", "Rzędne wysokościowe", "cienka", aci=1, z=25),
    _L("A-PRZEKROJE", "Oznaczenia przekrojów i widoków", "gruba", "PUNKTOWA_KROTKA", aci=1, z=24),
    _L("A-SYMBOLE", "Symbole ogólne (północ, spadki, odnośniki)", "cienka", aci=2, z=26),
    _L("A-TEREN", "Linia terenu, grunt", "gruba", aci=32, z=21),
    _L("A-ELEWACJE", "Elewacje — krawędzie", "srednia", aci=7, z=20),
    _L("A-MASKA", "Maski (tło napisów)", "b_cienka", aci=7, z=28),
    # ---- konstrukcja
    _L("K-KONSTR", "Konstrukcja — kontury elementów", "gruba", aci=7, z=22),
    _L("K-ZBROJENIE", "Zbrojenie — pręty (PN-EN ISO 3766)", "b_gruba", aci=1, z=24),
    _L("K-ZBROJENIE-OPIS", "Zbrojenie — opisy pozycji", "cienka", aci=2, z=26),
    _L("K-WYMIARY", "Konstrukcja — wymiary", "cienka", aci=1, z=25),
    _L("K-OSIE", "Konstrukcja — osie", "cienka", "PUNKTOWA", aci=1, z=12),
    # ---- instalacje sanitarne
    _L("S-WODA", "Instalacja wody zimnej", "srednia", aci=5, plot_rgb="#0050c8", z=23),
    _L("S-CWU", "Instalacja ciepłej wody użytkowej", "srednia", "KRESKOWA", aci=1, plot_rgb="#d00000", z=23),
    _L("S-CYRK", "Instalacja cyrkulacji CWU", "cienka", "PUNKTOWA_KROTKA", aci=6, plot_rgb="#b000b0", z=23),
    _L("S-KANAL", "Kanalizacja sanitarna", "gruba", aci=34, plot_rgb="#7a4500", z=23),
    _L("S-DESZCZ", "Kanalizacja deszczowa / odwodnienie", "srednia", "KRESKA_DLUGA", aci=150, plot_rgb="#00808a", z=23),
    _L("S-OGRZ", "Ogrzewanie (zasilanie/powrót, pętle podłogowe)", "cienka", aci=1, plot_rgb="#e05000", z=23),
    _L("S-WENT", "Wentylacja mechaniczna", "srednia", aci=3, plot_rgb="#008a00", z=23),
    _L("S-URZADZENIA", "Urządzenia i armatura instalacji sanitarnych", "srednia", aci=2, plot_rgb="#303030", z=24),
    _L("S-OPISY", "Instalacje sanitarne — opisy", "cienka", aci=2, z=26),
    # ---- instalacje elektryczne
    _L("E-GNIAZDA", "Gniazda wtyczkowe (PN-EN 60617)", "srednia", aci=1, plot_rgb="#c00000", z=24),
    _L("E-OSWIETLENIE", "Oprawy oświetleniowe", "srednia", aci=30, plot_rgb="#d06000", z=24),
    _L("E-LACZNIKI", "Łączniki, czujniki", "srednia", aci=30, plot_rgb="#d06000", z=24),
    _L("E-TRASY", "Trasy przewodów", "cienka", aci=8, plot_rgb="#606060", z=23),
    _L("E-ROZDZIELNICE", "Rozdzielnice, złącza, puszki", "srednia", aci=1, plot_rgb="#c00000", z=24),
    _L("E-TELETECH", "Instalacje teletechniczne (LAN, TV, domofon)", "srednia", aci=5, plot_rgb="#0050c8", z=24),
    _L("E-ODGROM", "Uziemienia, połączenia wyrównawcze, ochrona odgromowa", "srednia", aci=3, plot_rgb="#008a00", z=24),
    _L("E-OPISY", "Instalacje elektryczne — opisy", "cienka", aci=2, z=26),
    # ---- zagospodarowanie terenu
    _L("Z-GRANICE", "Granice działki, punkty graniczne", "gruba", "DWUPUNKTOWA", aci=1, z=23),
    _L("Z-ZABUDOWA", "Budynki projektowane i istniejące", "gruba", aci=7, z=22),
    _L("Z-LINIE-ZABUDOWY", "Linie zabudowy (MPZP)", "srednia", "PUNKTOWA", aci=1, plot_rgb="#c00000", z=22),
    _L("Z-UTWARDZENIA", "Nawierzchnie utwardzone", "cienka", aci=8, z=15),
    _L("Z-ZIELEN", "Zieleń: drzewa, krzewy, trawniki", "cienka", aci=3, plot_rgb="#1e7a1e", z=16),
    _L("Z-UZBROJENIE", "Uzbrojenie terenu, sieci i przyłącza", "srednia", aci=5, z=20),
    _L("Z-WARSTWICE", "Warstwice i punkty wysokościowe", "b_cienka", aci=32, plot_rgb="#8a5a2a", z=11),
    _L("Z-OGRODZENIE", "Ogrodzenie, bramy, furtki", "srednia", aci=7, z=20),
    _L("Z-OPISY", "Opisy zagospodarowania", "cienka", aci=2, z=26),
]}


def layer(name: str) -> LayerDef:
    """Definicja warstwy; nieznane nazwy dostają definicję domyślną (cienka, ciągła)."""
    ld = LAYERS.get(name)
    if ld is None:
        ld = LayerDef(name, name)
        LAYERS[name] = ld
    return ld


# Kolory pomocnicze wydruku
BLACK = "#000000"
WHITE = "#ffffff"
GREY_FILL = "#c8c8c8"
LIGHT_FILL = "#e6e6e6"
