#!/usr/bin/env python3
"""Progress report board (English) — A4 landscape (297x210 mm @ 200 dpi) with a large timestamp.

Usage:
    python3 umwd/tools/report_board.py            # uses umwd/raporty/state.json (+ optional --img/--cap)
    python3 umwd/tools/report_board.py --img a.png b.png --cap "caption a" "caption b"
state.json: {"title": "...", "stages": [["Stage", "done|running|todo"], ...], "notes": ["...", ...],
             "images": [{"path": "...", "caption": "..."}]}
Output: umwd/raporty/report_NN_YYYYMMDD_HHMM.png (Europe/Warsaw time) + spec_NN.json
"""
import argparse, datetime, json, sys
from pathlib import Path
from zoneinfo import ZoneInfo
from PIL import Image, ImageDraw, ImageFont, ImageOps

W, H, M = 2339, 1654, 56
ROOT = Path(__file__).resolve().parents[2]
RAP = ROOT / "umwd" / "raporty"
F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
ACC = (176, 58, 46)      # brick red accent (Wrocław)
INK = (24, 24, 24)

def font(s, b=False):
    return ImageFont.truetype(FB if b else F, s)

def wrap(d, text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=fnt) <= width:
            cur = t
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def resolve(p):
    p = Path(p)
    return p if p.is_absolute() else ROOT / p

def boxes_for(n, x0, y0, x1, y1, gap=20):
    w, h = x1 - x0, y1 - y0
    if n == 1: return [(x0, y0, w, h)]
    if n == 2: return [(x0, y0, w, (h - gap)//2), (x0, y0 + (h + gap)//2, w, (h - gap)//2)]
    if n == 3:
        hh = (h - gap)//2; ww = (w - gap)//2
        return [(x0, y0, w, hh), (x0, y0 + hh + gap, ww, hh), (x0 + ww + gap, y0 + hh + gap, ww, hh)]
    cols = 2 if n == 4 else 3
    rows = (n + cols - 1)//cols
    ww, hh = (w - (cols-1)*gap)//cols, (h - (rows-1)*gap)//rows
    return [(x0 + (k % cols)*(ww+gap), y0 + (k//cols)*(hh+gap), ww, hh) for k in range(n)]

def render(spec, out):
    now = datetime.datetime.now(ZoneInfo("Europe/Warsaw"))
    img = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(img)
    d.rectangle([20, 20, W-20, H-20], outline=(30, 30, 30), width=3)
    # timestamp box
    t, dt = now.strftime("%H:%M"), now.strftime("%d.%m.%Y") + "  " + now.strftime("%Z")
    ft, fd = font(150, True), font(52, True)
    tw = max(d.textlength(t, font=ft), d.textlength(dt, font=fd))
    bx = W - M - int(tw) - 60
    d.rounded_rectangle([bx, M-10, W-M, M+250], radius=26, fill=(17, 17, 17))
    d.text((bx+30, M+2), t, font=ft, fill=(255, 214, 0))
    d.text((bx+30, M+180), dt, font=fd, fill="white")
    # header
    d.text((M, M), "MARSHAL'S OFFICE HQ · WROCŁAW — architectural competition entry", font=font(38, True), fill=INK)
    d.text((M, M+58), f"Progress report no. {spec['nr']:02d}", font=font(66, True), fill=ACC)
    y = M + 148
    for ln in wrap(d, spec["title"], font(42), bx - M - 40)[:3]:
        d.text((M, y), ln, font=font(42), fill=(30, 30, 30)); y += 54
    hb = max(y, M+260) + 20
    d.line([M, hb, W-M, hb], fill=(30, 30, 30), width=3)
    # left column
    cw = 640; y = hb + 24
    d.text((M, y), "WORK STAGES", font=font(34, True), fill=INK); y += 52
    icons = {"done": ("✔", (22, 140, 60)), "running": ("►", (230, 120, 0)), "todo": ("○", (150, 150, 150))}
    for name, st in spec.get("stages", []):
        ic, col = icons.get(st, icons["todo"])
        d.text((M, y), ic, font=font(30, True), fill=col)
        for ln in wrap(d, name, font(25, st == "running"), cw - 60):
            d.text((M+46, y+2), ln, font=font(25, st == "running"), fill=INK if st != "todo" else (125, 125, 125)); y += 32
        y += 5
    y += 12
    if spec.get("notes"):
        d.text((M, y), "KEY POINTS", font=font(34, True), fill=INK); y += 50
        for n in spec["notes"]:
            for i, ln in enumerate(wrap(d, n, font(22), cw - 40)):
                if y > H - 118: break
                d.text((M + (0 if i == 0 else 26), y), ("• " if i == 0 else "") + ln, font=font(22), fill=(40, 40, 40)); y += 29
            y += 6
    # images
    gx0, gy0, gx1, gy1 = M + cw + 30, hb + 24, W - M, H - 100
    d.line([gx0-16, hb+10, gx0-16, H-90], fill=(200, 200, 200), width=2)
    ims = [i for i in spec.get("images", []) if resolve(i["path"]).exists()][:6]
    for it, (x0, y0, bw, bh) in zip(ims, boxes_for(len(ims), gx0, gy0, gx1, gy1)):
        im = ImageOps.contain(Image.open(resolve(it["path"])).convert("RGB"), (bw, bh-46), Image.LANCZOS)
        img.paste(im, (x0 + (bw-im.width)//2, y0 + (bh-46-im.height)//2))
        d.rectangle([x0, y0, x0+bw, y0+bh-46], outline=(210, 210, 210), width=2)
        cap, cf = it.get("caption", ""), font(22)
        while d.textlength(cap, font=cf) > bw and len(cap) > 4: cap = cap[:-2]
        d.text((x0, y0+bh-38), cap, font=cf, fill=(40, 40, 40))
    if not ims:
        d.text((gx0+20, gy0+20), "(no images yet)", font=font(30), fill=(150, 150, 150))
    d.line([M, H-84, W-M, H-84], fill=(30, 30, 30), width=2)
    d.text((M, H-70), "Automatic report · repo przemeknowak781/aihouse · branch claude/wroclaw-marshal-office-project-ktx37s · folder umwd/",
           font=font(22), fill=(90, 90, 90))
    d.text((W-M-430, H-70), "A4 landscape · 297 × 210 mm", font=font(22), fill=(90, 90, 90))
    img.save(out, dpi=(200, 200))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title"); ap.add_argument("--img", nargs="*"); ap.add_argument("--cap", nargs="*")
    a = ap.parse_args()
    st = json.loads((RAP / "state.json").read_text(encoding="utf-8"))
    nr = max([int(p.name.split("_")[1]) for p in RAP.glob("report_*.png")] + [0]) + 1
    images = st.get("images", [])
    if a.img:
        caps = a.cap or [Path(p).stem for p in a.img]
        images = [{"path": p, "caption": c} for p, c in zip(a.img, caps)]
    spec = {"nr": nr, "title": a.title or st.get("title", "Progress"), "stages": st["stages"], "notes": st.get("notes", []), "images": images}
    (RAP / f"spec_{nr:02d}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1), encoding="utf-8")
    now = datetime.datetime.now(ZoneInfo("Europe/Warsaw"))
    out = RAP / f"report_{nr:02d}_{now.strftime('%Y%m%d_%H%M')}.png"
    render(spec, out); print(out)

if __name__ == "__main__":
    main()
