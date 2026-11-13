"""
enclosure_printed.py — proposal (2026-11-12): the draught shield's walls and lid printed in PLA instead of six 150 x 250 acrylic sheets.

    ~/.venvs/lab-hw/bin/python hardware/balance/enclosure_printed.py     # writes cad/encl_print_*.stl and docs/img/enclosure_printed_preview.jxl

Same frame as balance.py: the four corner posts (two already printed) keep their 2.6 mm slots, and every wall is still 250 x 150 x 2 mm in the pinwheel
layout. A 250 mm wall does not fit the K1's 220 mm bed, so each wall is two plates joined by a printed mullion (an H-section strip with a slot on each
side): a 148 mm plate and a 100 mm piece. The 100 mm piece is printed on three walls; on the front wall (-y) it can be a stock 100 x 150 x 2 mm clear
acrylic sheet, the one window for alignment. The lid is four 124 x 150 tiles and two lid mullions resting on the existing shelves and wall tops.
Not yet part of balance.py: it replaces the acrylic only after the user's go-ahead.
"""

import os

import cadquery as cq

import balance as B
import params as P

MM = 1e3
T = P.PANEL_T * MM                 # 2 mm plates, the same as the acrylic, so the posts' slots fit unchanged
SLOT = T + 2 * P.SEAL_T * MM + 0.2  # 2.8 mm, as in balance.py
DEPTH = 4.0                        # mm each plate goes into a mullion
WEB = 2.0                          # mm of mullion between the two slots
CHEEK_IN, CHEEK_OUT = 1.2, 2.5     # mullion cheeks: thin on the inside to keep the 10 mm clearance to the balance
A_LEN, B_LEN = 148.0, 100.0        # the two pieces of a 250 mm wall: A + B + WEB = 250
WIN = ()                           # no acrylic window (user, 2026-11-12): every wall piece is printed
PLATE_T = 1.2                      # mm, wall plate thickness (user, 2026-11-12); the slot-side edges keep a 2.0 mm rim
RIM_W = 6.0                        # mm, width of that rim along each vertical edge


def walls():
    """{name: (solid, kind)} for the four walls, split A | mullion | B along each wall's long axis. kind: 'pla' or 'acrylic'."""
    wi, di, hi = (v * MM for v in P.ENCL_INNER)
    hx, hy = wi / 2, di / 2
    out = {}
    # (name, axis, fixed coordinate range across the wall, start of the 250 mm run, direction along the run, side the inside lies on)
    spec = [("wall_py", "x", (hy, hy + T), -hx, +1, -1), ("wall_px", "y", (hx, hx + T), hy, -1, -1),
            ("wall_ny", "x", (-hy - T, -hy), hx, -1, +1), ("wall_nx", "y", (-hx - T, -hx), -hy, +1, +1)]
    for name, axis, (c0, c1), s0, d, inside in spec:
        def run(a, b):  # a box from distance a to b along the run
            u0, u1 = sorted((s0 + d * a, s0 + d * b))
            return (u0, u1, c0, c1) if axis == "x" else (c0, c1, u0, u1)

        def bx(r, z0=0.0, z1=hi):
            x0, x1, y0, y1 = r
            return B.box(x0, x1, y0, y1, z0, z1)
        mid_ = (c0 + c1) / 2

        def plate(a, b):
            """a 1.2 mm plate from distance a to b along the run with a 2.0 mm, RIM_W wide rim on both vertical edges (the rim fills the slot)"""
            u = run(a, b)
            thin = (u[0], u[1], mid_ - PLATE_T / 2, mid_ + PLATE_T / 2) if axis == "x" else (mid_ - PLATE_T / 2, mid_ + PLATE_T / 2, u[2], u[3])
            body = bx(thin)
            for r0, r1 in ((a, a + RIM_W), (b - RIM_W, b)):
                q = run(r0, r1)
                rim = (q[0], q[1], mid_ - T / 2, mid_ + T / 2) if axis == "x" else (mid_ - T / 2, mid_ + T / 2, q[2], q[3])
                body = body.union(bx(rim))
            return body
        out[name + "_a"] = (plate(0, A_LEN), "pla")
        out[name + "_b"] = (plate(A_LEN + WEB, A_LEN + WEB + B_LEN), "acrylic" if name in WIN else "pla")
        # mullion: spans DEPTH into each plate plus the web; cheeks outside the 2.8 mm slot, the inner one thin
        lo, hi_ = (c0, c1)
        mid = (lo + hi_) / 2
        cin = mid + inside * (SLOT / 2 + CHEEK_IN)
        cout = mid - inside * (SLOT / 2 + CHEEK_OUT)
        m0, m1 = sorted((cin, cout))
        r = run(A_LEN - DEPTH, A_LEN + WEB + DEPTH)
        r = (r[0], r[1], m0, m1) if axis == "x" else (m0, m1, r[2], r[3])
        mul = bx(r)
        s_lo, s_hi = mid - SLOT / 2, mid + SLOT / 2
        for a, b in ((A_LEN - DEPTH - 1, A_LEN), (A_LEN + WEB, A_LEN + WEB + DEPTH + 1)):
            q = run(a, b)
            q = (q[0], q[1], s_lo, s_hi) if axis == "x" else (s_lo, s_hi, q[2], q[3])
            mul = mul.cut(bx(q, -1, hi + 1))
        if axis == "y":  # the lid shelves run along the inside of the x walls in the top 6 mm: the mullion's inner cheek stops below them
            q = run(A_LEN - DEPTH - 1, A_LEN + WEB + DEPTH + 1)
            inner0, inner1 = sorted((mid + inside * T / 2, mid + inside * (SLOT / 2 + CHEEK_IN + 1)))
            mul = mul.cut(bx((inner0, inner1, q[2], q[3]), hi - P.LID_SEAT * MM - 0.5, hi + 1))
        out[name + "_mullion"] = (mul, "pla")
    return out


def lid():
    """Four 124 x 150 tiles and two flat mullions (150 mm, along y at x = 0), same outline as the two acrylic lid sheets."""
    hi = P.ENCL_INNER[2] * MM
    lx = P.PANEL_STOCK[0] * MM / 2
    lw = P.PANEL_STOCK[1] * MM
    out = {}
    for k, (y0, y1) in enumerate(((0.0, lw), (-lw, 0.0))):
        out[f"lid_{k}_a"] = (B.box(-lx, -WEB / 2, y0, y1, hi, hi + T), "pla")
        out[f"lid_{k}_b"] = (B.box(WEB / 2, lx, y0, y1, hi, hi + T), "pla")
        m = B.box(-WEB / 2 - DEPTH, WEB / 2 + DEPTH, y0, y1, hi - CHEEK_IN - (SLOT - T) / 2, hi + T + (SLOT - T) / 2 + CHEEK_OUT)
        for a, b in ((-WEB / 2 - DEPTH - 1, -WEB / 2), (WEB / 2, WEB / 2 + DEPTH + 1)):
            m = m.cut(B.box(a, b, y0 - 1, y1 + 1, hi - (SLOT - T) / 2, hi + T + (SLOT - T) / 2))
        out[f"lid_{k}_mullion"] = (m, "pla")
    return out


def preview(parts, path):
    """A shaded preview of the frame with the printed plates (grey walls, red lid lifted 40 mm, black mullions) and the acrylic window."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    from render import draw as _unused  # noqa: F401  (same environment as render.py)
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
    from to_jxl import to_jxl

    bal = B.build(*B.balance_solve())
    show = [(n, wp, "#7a5c3a" if n.startswith("encl_post") else "#8c8c8c" if n.startswith("encl_shelf") else "#c9c9c9", 0.9)
            for n, (wp, _, _, _) in bal.items() if n.startswith(("encl_post", "encl_shelf", "base"))]
    show += [(n, wp, "#2a7fff" if moving else "#9fb6c9", 0.9) for n, (wp, _, moving, _) in bal.items()
             if not n.startswith(("encl_", "panel_", "base"))]
    for n, (wp, kind) in parts.items():
        lifted = wp.translate((0, 0, 40)) if n.startswith("lid_") else wp
        col = "#bfe6ff" if kind == "acrylic" else "#222222" if "mullion" in n else "#b03030" if n.startswith("lid_") else "#9a9a9a"
        show.append((n, lifted, col, 0.25 if kind == "acrylic" else 0.95))
    fig = plt.figure(figsize=(14, 7))
    for i, (elev, azim, title) in enumerate(((22, -60, "front-left (window in the -y wall)"), (22, 120, "back-right"))):
        ax = fig.add_subplot(1, 2, i + 1, projection="3d")
        for n, wp, col, alpha in show:
            verts, tris = wp.val().tessellate(0.3)
            v = np.array([(p.x, p.y, p.z) for p in verts])
            t = np.array(tris)
            nrm = np.cross(v[t][:, 1] - v[t][:, 0], v[t][:, 2] - v[t][:, 0])
            nrm = nrm / (np.linalg.norm(nrm, axis=1)[:, None] + 1e-12)
            shade = 0.55 + 0.45 * np.abs(nrm @ np.array([0.3, -0.5, 0.8]))
            base = np.array(matplotlib.colors.to_rgb(col))
            poly = Poly3DCollection(v[t], edgecolor="none", alpha=alpha)
            poly.set_facecolor([tuple(np.clip(base * s, 0, 1)) for s in shade])
            ax.add_collection3d(poly)
        ax.set_xlim(-140, 140)
        ax.set_ylim(-140, 140)
        ax.set_zlim(-10, 270)
        ax.set_box_aspect((1, 1, 1))
        ax.view_init(elev, azim)
        ax.set_title(title)
        ax.set_axis_off()
    fig.suptitle("Printed draught shield (proposal): grey PLA walls, black mullions, red PLA lid (lifted 40 mm), no acrylic window", y=0.99)
    fig.tight_layout(rect=(0, 0, 1, 0.93))
    png = path[:-4] + ".png"
    fig.savefig(png, dpi=110)
    return to_jxl(png)


def main():
    parts = walls()
    parts.update(lid())
    vol = {"pla": 0.0, "acrylic": 0.0}
    for n, (wp, kind) in parts.items():
        bb = wp.val().BoundingBox()
        vol[kind] += wp.val().Volume()
        if kind == "pla":
            cq.exporters.export(wp, os.path.join(B.OUT, f"encl_print_{n}.stl"))
        print(f"  {n:18s} {kind:7s} {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm")
    print(f"PLA volume {vol['pla']/1e3:.0f} cm3 = {vol['pla']/1e3*1.24:.0f} g solid; acrylic window {vol['acrylic']/1e3:.0f} cm3")
    img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "img", "enclosure_printed_preview.jxl")
    print("preview:", preview(parts, img))


if __name__ == "__main__":
    main()
