"""Floor-plan renderer (SVG) for competition plans at 1:200 / 1:500.

Graphic language (white board background):
  * cut walls & cores: warm black poché (#1f1d1a)
  * rooms: very light tints by functional group; civic/public groups in a muted terracotta accent
  * furniture: hairlines in warm grey — shows that each 24 m² room really holds 3 workstations
  * labels: room number (semibold) + area (regular); names via legend next to the plan
"""
from __future__ import annotations
import math
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from .svg import Svg, View, model_rings, FONT

INK = "#1f1d1a"
HAIR = "#9a948c"
FILL = {
    # public / civic (accent)
    "SW": "#efe1d6", "SK": "#efe1d6", "SWD": "#e8d3c3", "KS": "#f1e6dc",
    # departments (neutral warm)
    "DEP": "#f4f2ee", "PS": "#ecebe6", "SN": "#e9ece8", "PP": "#ebe9e4", "PHS": "#e4e7ea",
    "PPT": "#e4e4e4", "IT": "#dedede", "PR": "#e6eae2", "PPM": "#ededed", "KW": "#ffffff",
}


def fill_for(code):
    if code in FILL:
        return FILL[code]
    return FILL["DEP"]


def _furniture_office(svg, v, poly, n_desks=3, facade_dir=None):
    """Draw n desks (1.6 x 0.8 m) along the window wall of a rectangular room polygon."""
    mrr = poly.minimum_rotated_rectangle
    c = list(mrr.exterior.coords)[:4]
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1]); e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    L1, L2 = math.hypot(*e1), math.hypot(*e2)
    if L1 < L2:
        c = c[1:] + c[:1]; e1, e2 = e2, (c[2][0] - c[1][0], c[2][1] - c[1][1]); L1, L2 = L2, L1
    # width along facade = shorter side? rooms are 4.05 wide x 5.9 deep -> width = shorter side
    W, D = (L2, L1) if L2 < L1 else (L1, L2)
    # choose axis: room width axis u (short), depth axis w (long)
    if math.hypot(*e1) <= math.hypot(*e2):
        u, w, o = e1, e2, c[0]
    else:
        u, w, o = e2, e1, c[1] if False else c[0]
    Lu, Lw = math.hypot(*u), math.hypot(*w)
    uu, ww = (u[0] / Lu, u[1] / Lu), (w[0] / Lw, w[1] / Lw)
    def pt(s, t):
        return v.p(o[0] + uu[0] * s + ww[0] * t, o[1] + uu[1] * s + ww[1] * t)
    # decide which end along w is the facade: the end farther from polygon centroid of building is unknown here;
    # facade_dir: +1 desks near t=0, -1 near t=Lw
    near0 = facade_dir is None or facade_dir > 0
    dd, dw = 0.8, 1.6
    gap = (Lu - n_desks * dw) / (n_desks + 1) if n_desks * dw < Lu else 0.05
    gap = max(gap, 0.05)
    if n_desks * dw > Lu - 0.2:
        # place desks perpendicular in two rows
        dw2 = min(1.4, (Lu - 0.3) / 2)
        for k in range(n_desks):
            row, col = divmod(k, 2)
            s0 = 0.15 + col * (dw2 + 0.0)
            t0 = 0.6 + row * 2.1 if near0 else Lw - 0.6 - (row + 1) * 0.8 - row * 1.3
            svg.poly([pt(s0, t0), pt(s0 + dw2, t0), pt(s0 + dw2, t0 + dd), pt(s0, t0 + dd)], fill="none", stroke=HAIR, sw=0.09)
        return
    for k in range(n_desks):
        s0 = gap + k * (dw + gap)
        t0 = 0.55 if near0 else Lw - 0.55 - dd
        svg.poly([pt(s0, t0), pt(s0 + dw, t0), pt(s0 + dw, t0 + dd), pt(s0, t0 + dd)], fill="none", stroke=HAIR, sw=0.09)
        # chair
        cc = pt(s0 + dw / 2, t0 + dd + 0.45) if near0 else pt(s0 + dw / 2, t0 - 0.45)
        svg.circle(cc, v.mm(0.24), stroke=HAIR, sw=0.08)


def _furniture_table(svg, v, poly, seats):
    """Conference table in the middle of a room with chairs around."""
    mrr = poly.minimum_rotated_rectangle
    c = list(mrr.exterior.coords)[:4]
    cx, cy = poly.centroid.x, poly.centroid.y
    e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1]); e2 = (c[2][0] - c[1][0], c[2][1] - c[1][1])
    if math.hypot(*e1) < math.hypot(*e2):
        e1, e2 = e2, e1
    L1, L2 = math.hypot(*e1), math.hypot(*e2)
    a = (e1[0] / L1, e1[1] / L1); b = (e2[0] / L2, e2[1] / L2)
    per_side = max(2, math.ceil(seats / 2))
    tl = min(L1 - 2.2, per_side * 0.75)
    tw = min(1.4, L2 - 2.4)
    if tl <= 1 or tw <= 0.6:
        return
    def p(s, t):
        return v.p(cx + a[0] * s + b[0] * t, cy + a[1] * s + b[1] * t)
    svg.poly([p(-tl / 2, -tw / 2), p(tl / 2, -tw / 2), p(tl / 2, tw / 2), p(-tl / 2, tw / 2)], fill="none", stroke=HAIR, sw=0.09)
    for k in range(per_side):
        s = -tl / 2 + (k + 0.5) * tl / per_side
        for t in (-tw / 2 - 0.4, tw / 2 + 0.4):
            svg.circle(p(s, t), v.mm(0.22), stroke=HAIR, sw=0.08)


def render_level(svg: Svg, v: View, level: dict, show_names=False, label_size=1.6, furniture=True, accent_codes=("SW", "SK", "SWD", "KS")):
    """level = {outline: Polygon, rooms: [{id, name, code, poly, furn, seats}], cores: [Polygon], walls: Polygon|None,
                columns: [(e,n)], glazing: [LineString], stairs: [Polygon], lifts: [Polygon], doors: [...]}"""
    rooms = level.get("rooms", [])
    # room fills
    for r in rooms:
        model_rings(svg, v, r["poly"], fill=fill_for(r.get("code")), stroke="none", sw=0)
    # furniture
    if furniture:
        for r in rooms:
            f = r.get("furn")
            if f == "office3":
                _furniture_office(svg, v, r["poly"], 3, r.get("facade_dir"))
            elif f == "office4":
                _furniture_office(svg, v, r["poly"], 4, r.get("facade_dir"))
            elif f == "office1":
                _furniture_office(svg, v, r["poly"], 1, r.get("facade_dir"))
            elif f == "table":
                _furniture_table(svg, v, r["poly"], r.get("seats", 10))
    # stairs (hatch lines) and lifts (cross)
    for st in level.get("stairs", []):
        model_rings(svg, v, st, fill="#ffffff", stroke=INK, sw=0.12)
        mrr = st.minimum_rotated_rectangle; c = list(mrr.exterior.coords)[:4]
        e1 = (c[1][0] - c[0][0], c[1][1] - c[0][1]); e2 = (c[3][0] - c[0][0], c[3][1] - c[0][1])
        L1, L2 = math.hypot(*e1), math.hypot(*e2)
        if L1 < L2:
            e1, e2 = e2, e1; L1, L2 = L2, L1
        n = int(L1 / 0.28)
        for k in range(1, n):
            f = k / n
            a = (c[0][0] + e1[0] * f, c[0][1] + e1[1] * f)
            svg.line(v.p(*a), v.p(a[0] + e2[0], a[1] + e2[1]), stroke=INK, sw=0.07)
    for lf in level.get("lifts", []):
        model_rings(svg, v, lf, fill="#ffffff", stroke=INK, sw=0.12)
        c = list(lf.exterior.coords)[:4]
        svg.line(v.p(*c[0]), v.p(*c[2]), stroke=INK, sw=0.07); svg.line(v.p(*c[1]), v.p(*c[3]), stroke=INK, sw=0.07)
    # walls poché
    if level.get("walls") is not None:
        model_rings(svg, v, level["walls"], fill=INK, stroke="none", sw=0)
    for cr in level.get("cores", []):
        model_rings(svg, v, cr, fill="none", stroke=INK, sw=0.35)
    # columns
    for (e, n) in level.get("columns", []):
        s = v.mm(0.4)
        x, y = v.p(e, n)
        svg.poly([(x - s / 2, y - s / 2), (x + s / 2, y - s / 2), (x + s / 2, y + s / 2), (x - s / 2, y + s / 2)], fill=INK, stroke="none")
    # glazing (window lines in façade)
    for gl in level.get("glazing", []):
        cs = list(gl.coords)
        svg.line(v.p(*cs[0]), v.p(*cs[1]), stroke="#ffffff", sw=v.mm(0.18))
        svg.line(v.p(*cs[0]), v.p(*cs[1]), stroke=INK, sw=0.1)
    # outline
    if level.get("outline") is not None:
        model_rings(svg, v, level["outline"], fill="none", stroke=INK, sw=0.25)
    # labels
    for r in rooms:
        if r.get("nolabel"):
            continue
        c = r["poly"].representative_point()
        x, y = v.p(c.x, c.y)
        a = r["poly"].area
        if show_names and r.get("name"):
            svg.text((x, y - label_size * 0.9), r["name"], size=label_size * 0.95, anchor="middle", weight=500)
            svg.text((x, y + label_size * 0.4), f'{r["id"]}  ·  {a:.1f} m²', size=label_size * 0.8, anchor="middle", fill="#4a4641")
        else:
            svg.text((x, y), r["id"], size=label_size * 0.85, anchor="middle", weight=600)
            svg.text((x, y + label_size * 0.95), f"{a:.1f}", size=label_size * 0.75, anchor="middle", fill="#4a4641")
