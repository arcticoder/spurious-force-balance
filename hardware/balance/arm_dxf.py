"""
arm_dxf.py — the arm as a flat DXF (outline and holes, mm) for JLCCNC's sheet-metal quote and any laser or CNC cutter (Part J3), plus the panel numbers for the PCB quote.

    ~/.venvs/lab-hw/bin/python hardware/balance/arm_dxf.py        # writes boards/fab/arm_cnc.dxf and prints the panel layout

The outline and holes are the arm board's (boards.arm_board), viewed from the -y face with x to the right and the board's top edge up (the DXF's y is up, KiCad's is down).
Layers: CUT (outline, closed polyline) and HOLES (circles at the drill diameter). Nothing about copper is exported: an aluminium arm has no pads.
"""

import os
import sys

import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import boards as BD  # noqa: E402

FAB = BD.FAB

# panel of the four designs for the PCB quote (not a Gerber set): two columns beside the arm, 2 mm between boards
GAP = 2.0
SMALL = {"elec_board": (24.0, 34.0), "clamp_ground": (17.0, 19.0), "clamp_plate": (16.0, 14.0)}


def outline_pts(b):
    """Edge.Cuts lines of a board as an ordered closed polygon (the builders draw them in order)."""
    pts = []
    for it in b.graphicItems:
        if it.layer == "Edge.Cuts" and hasattr(it, "start"):
            pts.append((it.start.X, it.start.Y))
    return pts


def write_arm_dxf(path=None):
    b = BD.arm_board()
    pts = [(x, -y) for x, y in outline_pts(b)]
    doc = ezdxf.new("R2010", setup=True)
    doc.units = ezdxf.units.MM
    doc.layers.add("CUT", color=7)
    doc.layers.add("HOLES", color=1)
    msp = doc.modelspace()
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "CUT"})
    holes = BD.holes_mm(b)
    for x, y, d in holes:
        msp.add_circle((x, -y), d / 2, dxfattribs={"layer": "HOLES"})
    path = path or os.path.join(FAB, "arm_cnc.dxf")
    os.makedirs(FAB, exist_ok=True)
    doc.saveas(path)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return path, (max(xs) - min(xs), max(ys) - min(ys)), holes


def panel_layout():
    """Bounding size of the single panel: the arm, then a column of elec_board over clamp_ground, then a column of two clamp_plates."""
    x0, y0, x1, y1 = BD.board_outline_mm("arm")
    aw, ah = x1 - x0, y1 - y0
    col1_h = SMALL["elec_board"][1] + GAP + SMALL["clamp_ground"][1]
    col2_h = 2 * SMALL["clamp_plate"][1] + GAP
    w = aw + GAP + SMALL["elec_board"][0] + GAP + SMALL["clamp_plate"][0]
    h = max(ah, col1_h, col2_h)
    return w, h


def main():
    path, (w, h), holes = write_arm_dxf()
    print(f"{os.path.relpath(path, HERE)}: outline {w:.1f} x {h:.1f} mm, {len(holes)} holes: " + ", ".join(f"{d:g}" for _, _, d in holes))
    pw, ph = panel_layout()
    mass = pw * ph * BD.T_BOARD * BD.B.FR4_G_MM3 * 5
    sep = sum(BD.weight_estimate_g(n) for n in BD.BOARDS)
    print(f"panel of all four designs (arm + two columns of small boards, {BD.T_BOARD:.1f} mm): {pw:.0f} x {ph:.0f} mm; 5 panels give 5 arms, 5 elec_boards, 5 clamp_grounds and 10 clamp_plates; "
          f"mass by JLC's rule {mass:.0f} g against {sep:.0f} g for the four separate 5-piece orders")


if __name__ == "__main__":
    main()
