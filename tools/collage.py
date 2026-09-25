#!/usr/bin/env python3
"""Kolaż raportu postępu — arkusz A4 poziomo (297x210 mm @ 200 dpi) z dużym znacznikiem czasu.

Użycie:
    python3 tools/collage.py raporty/spec_01.json
Spec (JSON):
    {"nr": 1, "title": "...", "stages": [["Nazwa etapu", "done|running|todo"], ...],
     "images": [{"path": "...", "caption": "..."}], "notes": ["...", ...]}
Wynik: raporty/raport_NN_RRRRMMDD_HHMM.png (czas Europe/Warsaw).
"""
import json
import sys
import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H = 2339, 1654  # A4 poziomo, 200 dpi
M = 56
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_C = "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf"
ROOT = Path(__file__).resolve().parents[1]


def font(size, bold=False):
    return ImageFont.truetype(FONT_B if bold else FONT, size)


def wrap(draw, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_image(path, box_w, box_h):
    im = Image.open(path).convert("RGB")
    im = ImageOps.contain(im, (box_w, box_h), Image.LANCZOS)
    return im


def grid_shape(n):
    return {1: (1, 1), 2: (2, 1), 3: (3, 1), 4: (2, 2), 5: (3, 2), 6: (3, 2)}.get(n, (4, 2))


def main(spec_path):
    spec = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    now = datetime.datetime.now(ZoneInfo("Europe/Warsaw"))
    img = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(img)

    # ramka arkusza
    d.rectangle([20, 20, W - 20, H - 20], outline=(30, 30, 30), width=3)

    # znacznik czasu — prawy górny róg, duży i wyraźny
    ts_date = now.strftime("%d.%m.%Y")
    ts_time = now.strftime("%H:%M")
    tz = now.strftime("%Z")
    f_time, f_date = font(150, True), font(52, True)
    tw = max(d.textlength(ts_time, font=f_time), d.textlength(ts_date + "  " + tz, font=f_date))
    bx1 = W - M - int(tw) - 60
    d.rounded_rectangle([bx1, M - 10, W - M, M + 250], radius=26, fill=(17, 17, 17))
    d.text((bx1 + 30, M + 2), ts_time, font=f_time, fill=(255, 214, 0))
    d.text((bx1 + 30, M + 180), ts_date + "  " + tz, font=f_date, fill="white")

    # nagłówek
    d.text((M, M), "DOM LAMELA · projekt koncepcyjny, budowlany i techniczny", font=font(40, True), fill=(20, 20, 20))
    d.text((M, M + 60), f"Raport postępu nr {spec['nr']:02d}", font=font(66, True), fill=(200, 60, 20))
    y = M + 150
    for line in wrap(d, spec["title"], font(44), bx1 - M - 40):
        d.text((M, y), line, font=font(44), fill=(30, 30, 30))
        y += 56
    head_bottom = max(y, M + 260) + 20
    d.line([M, head_bottom, W - M, head_bottom], fill=(30, 30, 30), width=3)

    # lewa kolumna: etapy + uwagi
    col_w = 620
    y = head_bottom + 24
    d.text((M, y), "ETAPY PRAC", font=font(34, True), fill=(20, 20, 20))
    y += 52
    icons = {"done": ("✔", (22, 140, 60)), "running": ("►", (230, 120, 0)), "todo": ("○", (150, 150, 150))}
    for name, st in spec.get("stages", []):
        ic, col = icons.get(st, icons["todo"])
        d.text((M, y), ic, font=font(32, True), fill=col)
        lines = wrap(d, name, font(26, st == "running"), col_w - 60)
        for ln in lines:
            d.text((M + 48, y + 2), ln, font=font(26, st == "running"), fill=(20, 20, 20) if st != "todo" else (120, 120, 120))
            y += 33
        y += 4
    y += 14
    if spec.get("notes"):
        d.text((M, y), "NAJWAŻNIEJSZE", font=font(34, True), fill=(20, 20, 20))
        y += 50
        for n in spec["notes"]:
            for i, ln in enumerate(wrap(d, n, font(23), col_w - 40)):
                if y > H - 120:
                    break
                d.text((M + (0 if i == 0 else 28), y), ("• " if i == 0 else "") + ln, font=font(23), fill=(40, 40, 40))
                y += 30
            y += 6

    # prawa część: siatka obrazów
    gx0, gy0 = M + col_w + 30, head_bottom + 24
    gx1, gy1 = W - M, H - 100
    d.line([gx0 - 16, head_bottom + 10, gx0 - 16, H - 90], fill=(200, 200, 200), width=2)
    imgs = [i for i in spec.get("images", []) if Path(ROOT / i["path"]).exists() or Path(i["path"]).exists()]
    if imgs:
        cols, rows = grid_shape(len(imgs))
        asp = []
        for it in imgs:
            pp = Path(it["path"]) if Path(it["path"]).exists() else ROOT / it["path"]
            with Image.open(pp) as _im:
                asp.append(_im.width / _im.height)
        if len(imgs) == 2 and sum(asp) / len(asp) > 1.25:
            cols, rows = 1, 2
        if len(imgs) == 3:
            # układ: pierwszy obraz na całą szerokość u góry, dwa pozostałe obok siebie niżej
            gh = (gy1 - gy0 - 20) // 2
            boxes = [(gx0, gy0, gx1 - gx0, gh), (gx0, gy0 + gh + 20, (gx1 - gx0 - 20) // 2, gh),
                     (gx0 + (gx1 - gx0 - 20) // 2 + 20, gy0 + gh + 20, (gx1 - gx0 - 20) // 2, gh)]
            for it, (x0, y0, cw, ch) in zip(imgs, boxes):
                pth = Path(it["path"]) if Path(it["path"]).exists() else ROOT / it["path"]
                im = fit_image(pth, cw, ch - 46)
                img.paste(im, (x0 + (cw - im.width) // 2, y0 + (ch - 46 - im.height) // 2))
                d.rectangle([x0, y0, x0 + cw, y0 + ch - 46], outline=(210, 210, 210), width=2)
                cap, capf = it.get("caption", ""), font(23)
                while d.textlength(cap, font=capf) > cw and len(cap) > 4:
                    cap = cap[:-2]
                d.text((x0, y0 + ch - 38), cap, font=capf, fill=(40, 40, 40))
            imgs = []
            cols, rows = 1, 1
        cw = (gx1 - gx0 - (cols - 1) * 20) // cols if imgs else 0
        ch = (gy1 - gy0 - (rows - 1) * 20) // rows
        for k, it in enumerate(imgs[: cols * rows]):
            c, r = k % cols, k // cols
            x0, y0 = gx0 + c * (cw + 20), gy0 + r * (ch + 20)
            p = Path(it["path"]) if Path(it["path"]).exists() else ROOT / it["path"]
            im = fit_image(p, cw, ch - 46)
            img.paste(im, (x0 + (cw - im.width) // 2, y0 + (ch - 46 - im.height) // 2))
            d.rectangle([x0, y0, x0 + cw, y0 + ch - 46], outline=(210, 210, 210), width=2)
            cap = it.get("caption", "")
            capf = font(23)
            while d.textlength(cap, font=capf) > cw and len(cap) > 4:
                cap = cap[:-2]
            d.text((x0, y0 + ch - 38), cap, font=capf, fill=(40, 40, 40))

    # stopka
    d.line([M, H - 84, W - M, H - 84], fill=(30, 30, 30), width=2)
    d.text((M, H - 70), "Raport automatyczny · repozytorium przemeknowak781/aihouse · gałąź claude/single-family-house-project-2pkn7l",
           font=font(24), fill=(90, 90, 90))
    d.text((W - M - 520, H - 70), "A4 poziomo · 297 × 210 mm", font=font(24), fill=(90, 90, 90))

    out = ROOT / "raporty" / f"raport_{spec['nr']:02d}_{now.strftime('%Y%m%d_%H%M')}.png"
    out.parent.mkdir(exist_ok=True)
    img.save(out, dpi=(200, 200))
    print(out)


if __name__ == "__main__":
    main(sys.argv[1])
