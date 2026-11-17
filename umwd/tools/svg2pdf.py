#!/usr/bin/env python3
"""SVG (mm) -> PDF 1:1 via Chromium (tools/plansze/html2pdf.js). Usage: svg2pdf.py OUTDIR SVG..."""
import sys, re, subprocess, html
from pathlib import Path
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
H2P = "/home/user/aihouse/umwd/tools/plansze/html2pdf.js"
for s in sys.argv[2:]:
    p = Path(s); t = p.read_text(encoding="utf-8")
    m = re.search(r'<svg[^>]*\swidth="([\d.]+)mm"[^>]*\sheight="([\d.]+)mm"', t, re.S)
    if not m:
        print("skip (no mm size):", p.name); continue
    w, h = float(m.group(1)), float(m.group(2))
    W, H = round(w + 20, 1), round(h + 20, 1)      # 10 mm white margin
    page = out / (p.stem + ".html")
    page.write_text(f"""<!doctype html><html><head><meta charset="utf-8"><style>
@page {{ size: {W}mm {H}mm; margin: 0 }} html,body {{ margin:0; background:#fff }}
img {{ position:absolute; left:10mm; top:10mm; width:{w}mm; height:{h}mm }}</style></head>
<body><img src="file://{p.resolve()}"></body></html>""", encoding="utf-8")
    pdf = out / (p.stem + ".pdf")
    r = subprocess.run(["node", H2P, str(page), str(pdf), str(W), str(H)], capture_output=True, text=True)
    page.unlink()
    print(("OK " if r.returncode == 0 and pdf.exists() else "FAIL ") + pdf.name, f"{W}x{H} mm", r.stderr[-200:] if r.returncode else "")
