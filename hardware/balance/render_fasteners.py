"""
render_fasteners.py — close-ups of where the screws and nuts go on the torsion head and the electrode bracket (docs/img/fasteners.jxl).

    ~/.venvs/lab-hw/bin/python hardware/balance/render_fasteners.py
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import balance as B
import render as R

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools"))
from to_jxl import to_jxl  # noqa: E402

HEAD_HIGHLIGHT = {"head": "#e67e22", "gantry": "#9fb6c9", "elec_bracket": "#e67e22", "base": "#c9c9c9"}


def draw(ax, parts, elev, azim):
    import numpy as np
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    for name, (wp, _, moving, _) in parts.items():
        verts, tris = wp.val().tessellate(0.1)
        v = np.array([(p.x, p.y, p.z) for p in verts]); t = np.array(tris)
        col, alpha = STYLE.get(name, ("#9fb6c9", 0.15))
        n = np.cross(v[t][:, 1] - v[t][:, 0], v[t][:, 2] - v[t][:, 0]); n = n / (np.linalg.norm(n, axis=1)[:, None] + 1e-12)
        shade = 0.55 + 0.45 * np.abs(n @ np.array([0.3, -0.5, 0.8]))
        base = np.array(matplotlib.colors.to_rgb(col))
        poly = Poly3DCollection(v[t], alpha=alpha, edgecolor="none")
        poly.set_facecolor([tuple(np.clip(base * k, 0, 1)) for k in shade])
        ax.add_collection3d(poly)
    ax.view_init(elev=elev, azim=azim)


STYLE = {"head": ("#e67e22", 0.95), "elec_bracket": ("#e67e22", 0.95), "gantry": ("#9fb6c9", 0.12), "base": ("#c9c9c9", 0.25),
         "strip": ("#d4a017", 0.9), "clamp_up_a": ("#2a7fff", 0.9), "clamp_up_b": ("#2a7fff", 0.9), "elec_board": ("#2a7fff", 0.5)}


def panel(fig, rect, parts, keep, box, elev, azim, title, notes):
    ax = fig.add_axes(rect, projection="3d")
    sub = {n: parts[n] for n in keep if n in parts}
    draw(ax, sub, elev, azim)
    (x0, x1), (y0, y1), (z0, z1) = box
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_zlim(z0, z1)
    ax.set_box_aspect((x1 - x0, y1 - y0, z1 - z0))
    ax.set_axis_off()
    ax.set_title(title, fontsize=11)
    for (x, y, z, text, dx, dy) in notes:
        ax.plot([x], [y], [z], "o", color="#c0392b", ms=5)
        fig.canvas.draw()
        from mpl_toolkits.mplot3d import proj3d
        x2, y2, _ = proj3d.proj_transform(x, y, z, ax.get_proj())
        ax.annotate(text, xy=(x2, y2), xytext=(dx, dy), textcoords="offset points", fontsize=8, ha="center",
                    arrowprops=dict(arrowstyle="-", color="0.3", lw=0.7), bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="0.7", alpha=0.92))


def main():
    bl, cl = B.balance_solve()
    parts = B.build(bl, cl)
    zc = (B.Z_UP0 + B.Z_UP1) / 2
    fig = plt.figure(figsize=(16, 8))
    notes_head = [
        (-5, -9, zc, "head: 2 holes in the -y wall.\nThe upper clamp bolts' tips\nhang in them (3.4 mm, no nut).", -190, -30),
        (5, -9, zc, "second hole", -70, -90),
        (24, -B.HEAD_BOSS_Y, 133, "gantry: M3x14 adjusting screw (one per side),\nthrough a nut captured in the +x extension;\nthe tip pushes the head's lever tab", 100, 70),
    ]
    panel(fig, [0.0, 0.05, 0.5, 0.85], parts, ["gantry", "head", "clamp_up_a", "clamp_up_b", "strip"], ((-20, 35), (-20, 20), (100, 140)), 20, -75,
          "torsion head in the gantry (seen from -y, below)", notes_head)
    eb = parts["elec_bracket"][0].val().BoundingBox()
    notes_br = [
        (80 - 8, eb.ymin + 12, 6, "bracket foot: 6.6 mm slack holes (x2).\nM3x14 screw + washer from above,\ninto a nut captured under the base", -190, 60),
        (80 + 8, eb.ymin + 12, 6, "", 0, 0),
        (80, 1.0, 55, "fixed electrode board taped to\nthe bracket's front pocket (no screws)", 150, 80),
    ]
    panel(fig, [0.5, 0.05, 0.5, 0.85], parts, ["base", "elec_bracket", "elec_board"], ((60, 100), (-5, 25), (0, 75)), 30, -55,
          "electrode bracket on the base", notes_br)
    fig.suptitle("Where the screws and nuts go (orange = the printed part in question)", fontsize=12)
    out = os.path.join(os.path.dirname(B.OUT), "..", "..", "docs", "img", "fasteners.png")
    fig.savefig(out, dpi=100, bbox_inches="tight")
    print("wrote", to_jxl(out))


if __name__ == "__main__":
    main()
