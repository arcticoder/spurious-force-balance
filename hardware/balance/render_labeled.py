"""
render_labeled.py — a labelled picture of the whole apparatus with scale references, for people (docs/img/apparatus.png).

    ~/.venvs/lab-hw/bin/python hardware/balance/render_labeled.py

Three views of the same assembly (balance.py's CAD): an oblique view, the view along the arm (what the arm hangs like), and the top view with a credit card for scale (85.6 x 54 mm).
The enclosure is drawn as faint glass; the arm board (blue), the strip (gold) and everything that moves are coloured; fixed parts are grey-blue.
"""

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import proj3d

import balance as B
import render as R

LABELS = [  # part name, label, text offset in points (dx, dy) from the part
    ("arm", "FR4 arm board\n208 x 60 x 1.2 mm, on edge", (-190, 130)),
    ("strip", "torsion strip: 50 um x 4 mm x 30 mm", (40, 175)),
    ("head", "torsion head (zero adjust)", (-60, 150)),
    ("gantry", "printed frame", (230, 120)),
    ("vane", "copper vane\nin the damper field", (215, 40)),
    ("magnet_up_0", "4 fixed N42 discs\n(eddy damper)", (250, 85)),
    ("sensor_bracket", "optical sensor: LED + photodiode;\nflag on the arm end", (-230, 20)),
    ("elec_board", "fixed electrode\n(force calibration)", (160, -70)),
    ("ballast", "brass ballast", (-190, -70)),
    ("dut_card", "device card\n(the thing under test)", (140, -130)),
    ("base", "base plate, 218 mm", (-60, -150)),
]


def centre(wp):
    verts, _ = wp.val().tessellate(0.5)
    v = np.array([(p.x, p.y, p.z) for p in verts])
    return (v.min(axis=0) + v.max(axis=0)) / 2


def scale_bar(ax, x0, y0, z0, length, label):
    ax.plot([x0, x0 + length], [y0, y0], [z0, z0], color="k", lw=2.5)
    ax.text(x0 + length / 2, y0, z0 - 12, label, ha="center", fontsize=8)


def main():
    bl, cl = B.balance_solve()
    parts = B.build(bl, cl)
    fig = plt.figure(figsize=(17, 9))
    spec = ((0.0, 0.0, 0.62, 0.93, 22, -58, "oblique view"), (0.62, 0.50, 0.38, 0.40, 0, -90, "side view: the arm hangs on its strip"), (0.62, 0.04, 0.38, 0.44, 90, -90, "top view (credit card for scale)"))
    for k, (x, y, w, h, e, a, t) in enumerate(spec):
        ax = fig.add_axes([x, y, w, h], projection="3d")
        R.draw(ax, parts, e, a, t)
        ax.set_axis_off()
        ax.set_title(t, fontsize=11, y=0.96 if k == 0 else 0.92)
        if k == 2:  # credit card on the base, lower-left of the top view
            cx, cy = -105.0, -105.0
            ax.plot([cx, cx + 85.6, cx + 85.6, cx, cx], [cy, cy, cy + 54, cy + 54, cy], [7, 7, 7, 7, 7], color="#c0392b", lw=1.5)
            ax.text(cx + 43, cy + 27, 7, "credit card", ha="center", va="center", fontsize=7, color="#c0392b")
        if k in (0, 1):
            scale_bar(ax, -100, -105 if k == 0 else 0, 2, 200, "200 mm")
        if k == 0:
            fig.canvas.draw()
            for name, text, (dx, dy) in LABELS:
                if name not in parts:
                    continue
                c = centre(parts[name][0])
                x2, y2, _ = proj3d.proj_transform(c[0], c[1], c[2], ax.get_proj())
                px, py = ax.transData.transform((x2, y2))
                ax.annotate(text, xy=(x2, y2), xytext=(dx, dy), textcoords="offset points", fontsize=8, ha="center",
                            arrowprops=dict(arrowstyle="-", color="0.3", lw=0.7), bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="0.7", alpha=0.9))
    fig.suptitle("Torsion balance for force measurements in air: arm 208 mm, the whole instrument about 250 x 250 x 200 mm inside a clear acrylic box", fontsize=12, y=0.985)
    out = os.path.join(os.path.dirname(B.OUT), "..", "..", "docs", "img", "apparatus.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    fig.savefig(out, dpi=100, bbox_inches="tight")
    print("wrote", os.path.relpath(out))


if __name__ == "__main__":
    main()
