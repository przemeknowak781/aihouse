#!/usr/bin/env python3
"""Plansze Etapu II – maks. 8 × 100×70 cm (R-101). Skład wg docs/10_regulamin/lista_kontrolna_etap2.md (1.2, zmodyfikowany):
P1 idea + wizualizacja 1 (F.17.A) + zagospodarowanie 1:500 + wskaźniki
P2 wizualizacja 2 (F.17.B) + wizualizacja 3 (wejście) + aksonometria funkcjonalna
P3 parter z otoczeniem 1:200, −1, −2 (rzuty od agenta rzutów)
P4 kondygnacje 1–4 1:200
P5 kondygnacje 5, 6, S, antresola, dach 1:200 + wizualizacje 7, 8 (hol i sala Sejmiku)
P6 przekroje A-A, B-B 1:200 + analiza zacienienia + schemat dostępności
P7 elewacje 1:200 (W z Maz. 19, S, E z WS 5, N)
P8 przekrój elewacyjny 1:50 + wizualizacje 4, 5, 6 + schemat proekologiczny
Rysunki skalowe wstawiane 1:1 (SVG w mm). Brak numeru identyfikacyjnego na planszach (R-133).
"""
import sys, re, json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from umwd.board import Board, M, W, H, ACC, img

OUT = ROOT / "build" / "plansze"
OUT.mkdir(parents=True, exist_ok=True)
R, V = "../rysunki/", "../../docs/60_wizualizacje/img/"
TITLE = "BRAMA I LATARNIA"
MOTTO = "Siedziba Urzędu Marszałkowskiego i Sejmiku Województwa Dolnośląskiego · Wrocław"
K = json.loads((ROOT / "model" / "koncepcja.json").read_text(encoding="utf-8"))
TOP = M + 26
BOT = H - M


def svg_size(name):
    p = ROOT / "build" / "rysunki" / name
    if not p.exists():
        return None
    m = re.search(r'width="([\d.]+)mm" height="([\d.]+)mm"', p.read_text(encoding="utf-8")[:600])
    return float(m.group(1)), float(m.group(2))


def drawing(name, s=1.0):
    sz = svg_size(name)
    if not sz:
        return None, 0, 0
    w, h = sz
    return f'<img src="{R}{name}" style="width:{w * s:.2f}mm;height:{h * s:.2f}mm;display:block">', w * s, h * s


def vis(*cands):
    for c in cands:
        if (ROOT / "docs" / "60_wizualizacje" / "img" / c).exists():
            return img(V + c)
    return '<div style="width:100%;height:100%;background:#f1efeb;display:flex;align-items:center;justify-content:center;color:#9a948c;font-size:14pt">wizualizacja w przygotowaniu</div>'


def placeholder(txt):
    return f'<div style="width:100%;height:100%;border:0.4mm dashed #c9c3ba;display:flex;align-items:center;justify-content:center;color:#9a948c;font-size:14pt;text-align:center">{txt}</div>'


def label(num, title, sub=""):
    return (f'<div style="font-size:11pt;font-weight:600;letter-spacing:0.6pt;text-transform:uppercase">'
            f'<span style="color:{ACC};margin-right:2mm">{num}</span>{title}</div>'
            + (f'<div class="cap" style="margin-top:0.6mm">{sub}</div>' if sub else ""))


def put(b, name, x, y, s=1.0, anchor="tl"):
    d, w, h = drawing(name, s)
    if d is None:
        b.add(x, y, 200, 120, placeholder(name))
        return 200, 120
    if anchor == "bl":
        y = y - h
    b.add(x, y, w, h, d)
    return w, h


def kpi_html():
    bl = K["bilans"]
    items = [(f'{bl["PU_m2"]:,.0f}'.replace(",", " "), "m² PU", "powierzchnia użytkowa"), (f'{bl["PC_nadziemna_m2"]:,.0f}'.replace(",", " "), "m² PC", "nadziemna"),
             (f'{bl["koszt_mln_netto"]:.1f}'.replace(".", ","), "mln zł", "koszt realizacji netto (limit 150)"),
             (f'{K["elewacje"]["PV"]["razem_kWp"]}', "kWp", "fotowoltaika na działce"), (f'{K["podziemie"]["razem_miejsc"]}', "m.p.", "garaż podziemny"),
             ("37,2", "m", "wieża Sejmiku w strefie A")]
    cells = "".join(f'<div style="padding:2.5mm 0;border-top:0.25mm solid #cfcac2"><span style="font-family:Inter Display,Inter;font-size:30pt;font-weight:300;color:{ACC}">{a}</span>'
                    f'<span style="font-size:12pt;margin-left:2mm">{u}</span><div class="cap" style="margin-top:0">{t}</div></div>' for a, u, t in items)
    return f'<div style="display:grid;grid-template-columns:1fr 1fr;column-gap:8mm">{cells}</div>'


MANIFEST = ("Brama i latarnia. Siedziba samorządu staje na przyczółku Mostu Grunwaldzkiego jako brama miasta i jego latarnia: "
            "wieża Sejmiku zwraca się łukiem do mostu, a w jej koronie, za ceramicznymi lamelami, obraduje Sejmik – widoczny z miasta, "
            "gdy pracuje. Skrzydło i segment domykają pierzeje kwartału w skali kamienic, oddając ulicom ich dawne linie. "
            "Przez podcień Bramy Mostowej i Halę Obywatelską prowadzi publiczna oś od mostu do otwartego Ogrodu Województwa.")


def p1():
    b = Board(1, 8, TITLE, MOTTO).header()
    b.add(M, TOP, 578, 340, vis("W1_F17A_final.jpg", "photomatch_F17A_nakladka.jpg"))
    b.add(M, TOP + 342, 578, 10, label("1", "Widok z lotu ptaka od wschodu", "wizualizacja nr 1 na zdjęciu F.17.A; poza granicą opracowania stan istniejący"))
    put(b, "schematy_idei.svg", M, TOP + 360, 1.04)
    b.add(612, TOP, 366, 64, f'<div style="font-family:Inter Display,Inter;font-size:15pt;font-weight:300;line-height:1.32;color:#2f2b28">{MANIFEST}</div>')
    b.add(612, TOP + 88, 366, 140, kpi_html())
    put(b, "zagospodarowanie_1-500.svg", 612 + 7, BOT, 1.0, anchor="bl")
    return b


def p2():
    b = Board(2, 8, TITLE, MOTTO).header()
    b.add(M, TOP, 578, 420, vis("W3_wejscie_final.jpg", "budynek_test_W3.jpg"))
    b.add(M, TOP + 422, 578, 10, label("3", "Brama Mostowa – główna strefa wejściowa", "wizualizacja nr 3 z poziomu człowieka"))
    b.add(612, TOP, 366, 206, vis("W2_F17B_final.jpg", "photomatch_F17B_nakladka.jpg"))
    b.add(612, TOP + 208, 366, 10, label("2", "Widok z lotu ptaka od zachodu", "wizualizacja nr 2 na zdjęciu F.17.B"))
    sz = svg_size("aksonometria_funkcjonalna.svg")
    s = min(366 / sz[0], (BOT - TOP - 226) / sz[1])
    put(b, "aksonometria_funkcjonalna.svg", 612 + (366 - sz[0] * s) / 2, BOT, s, anchor="bl")
    b.add(M, TOP + 440, 578, 170, '<div style="display:grid;grid-template-columns:1fr 1fr 1fr;column-gap:8mm" class="small">'
          '<div><h3>Strefa publiczna</h3><p>Parter otwarty na plac i ogród: Hala Obywatelska z informacją i kancelarią, centrum konferencyjne 200 + 80 os., bistro z tarasem na placu; galeria publiczności Sejmiku osiągana dźwigami publicznymi z Wejścia Obywatelskiego.</p></div>'
          '<div><h3>Urząd</h3><p>Kondygnacje 1–5 w powtarzalnym module 1,35 m: pokoje 24 m² i 32 m² wzdłuż elewacji, departamenty niedzielone, sale narad na każdej kondygnacji, rezerwa elastyczności bez zmian konstrukcji.</p></div>'
          '<div><h3>Sejmik</h3><p>Kondygnacja 6 – Prezydium i Kancelaria Sejmiku; korona S – sala obrad, komisje, kluby i hol reprezentacyjny na jednej kondygnacji w strefie A, z oddzielnym dojściem radnych i publiczności.</p></div></div>')
    return b


def p_plans(n, title, ids):
    b = Board(n, 8, TITLE, MOTTO).header()
    b.add(M, TOP, W - 2 * M, BOT - TOP, placeholder(f"{title}<br>rzuty 1:200 z numerami, nazwami i powierzchniami pomieszczeń – generuje agent rzutów ({', '.join(ids)})"))
    return b


def p6():
    b = Board(6, 8, TITLE, MOTTO).header()
    w, h = put(b, "przekroj_AA_1-200.svg", M, TOP)
    put(b, "przekroj_BB_1-200.svg", M, TOP + h + 6)
    put(b, "naslonecznienie.svg", 612 - 10, TOP, 1.0)
    put(b, "schemat_dostepnosci_1-500.svg", 612 - 10, BOT, 1.0, anchor="bl")
    return b


def p7():
    b = Board(7, 8, TITLE, MOTTO).header()
    w1, h1 = put(b, "elewacja_W_1-200.svg", M, TOP)
    put(b, "elewacja_S_1-200.svg", M + w1 + 8, TOP)
    w3, h3 = put(b, "elewacja_E_1-200.svg", M, TOP + h1 + 4)
    put(b, "elewacja_N_1-200.svg", M + w3 + 8, TOP + h1 + 4)
    return b


def p8():
    b = Board(8, 8, TITLE, MOTTO).header()
    w, h = put(b, "przekroj_elewacyjny_1-50_korona.svg", M, TOP, 1.0)
    put(b, "schemat_eko_1-250.svg", M, BOT, 1.0, anchor="bl")
    xr = M + 498
    b.add(xr, TOP, W - M - xr, 150, vis("W4_WS5_final.jpg", "budynek_test_W4.jpg"))
    b.add(xr, TOP + 152, W - M - xr, 10, label("4", "Relacja z kamienicą Wybrzeże J. Słowackiego 5", "wizualizacja nr 4"))
    b.add(xr, TOP + 168, W - M - xr, 150, vis("W5_Maz19_final.jpg", "budynek_test_W5.jpg"))
    b.add(xr, TOP + 320, W - M - xr, 10, label("5", "Relacja z kamienicą Mazowiecka 19", "wizualizacja nr 5"))
    b.add(xr + 40, TOP + 340, W - M - xr - 40, 230, vis("W6_hol_final.jpg"))
    b.add(xr + 40, TOP + 572, W - M - xr - 40, 10, label("6", "Hala Obywatelska – hol główny", "wizualizacja nr 6"))
    return b


def render(b, name):
    html = OUT / f"{name}.html"
    b.save(html)
    js = ROOT / "tools" / "plansze" / "html2pdf.js"
    subprocess.run(["node", str(js), str(html), str(OUT / f"{name}.pdf"), "1000", "700", "--png", str(OUT / f"{name}.png"), "--pngw", "2400"],
                   check=True, cwd=str(ROOT / "tools" / "plansze"), capture_output=True)
    return OUT / f"{name}.png"


if __name__ == "__main__":
    which = sys.argv[1:] or ["1", "2", "3", "4", "5", "6", "7", "8"]
    boards = {"1": p1, "2": p2, "3": lambda: p_plans(3, "PARTER Z OTOCZENIEM · −1 · −2", ["P", "-1", "-2"]),
              "4": lambda: p_plans(4, "KONDYGNACJE 1–4", ["1", "2", "3", "4"]),
              "5": lambda: p_plans(5, "KONDYGNACJE 5, 6, S, ANTRESOLA, DACH", ["5", "6", "S", "ANT", "D"]), "6": p6, "7": p7, "8": p8}
    for k in which:
        print(render(boards[k](), f"etap2_P{k}"))
