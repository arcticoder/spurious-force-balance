"""
boards.py — the FR4 boards of the balance as KiCad files, from the same numbers as balance.py.

    ~/.venvs/lab-hw/bin/python hardware/balance/boards.py            # write boards/*.kicad_pcb
    ~/.venvs/lab-hw/bin/python hardware/balance/boards.py --fab      # also run DRC, export Gerbers + drill, zip them, render

Five boards (all unassembled, nothing soldered, 2 layers, ENIG, black mask, thickness from params.BOARD_T):
  arm            the balance arm, 200 x 60 mm on edge: strip contact pad and the moving electrode on the +y face (B.Cu), the flag finger, holes
  clamp_plate    plain 16 x 14 mm clamp plate (the lower plate and the upper -y plate)
  clamp_ground   the upper +y clamp plate: an ENIG pad against the strip, a trace to a tab with a 2 mm plated hole for the ground wire
  elec_board     the fixed calibration electrode: a 20 x 8 mm ENIG pad inside a grounded ENIG guard, two plated wire holes on a tab

Coordinates: KiCad X = the balance's x, KiCad Y = minus the balance's z (the board stands on edge, viewed from -y). F.Cu is the -y face
(the side the device card is on), B.Cu is the +y face (the side of the electrode, the strip and the vane).
"""

import os
import uuid
import subprocess
import sys

from kiutils.board import Board
from kiutils.footprint import DrillDefinition, Footprint, Pad
from kiutils.items.common import Effects, Font, Justify, Net, Position
from kiutils.items.fpitems import FpText  # noqa: F401
from kiutils.items.gritems import GrLine, GrRect, GrText
from kiutils.items.brditems import Segment, Via

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import balance as B  # noqa: E402
import params as P  # noqa: E402

OUT = os.path.join(HERE, "boards")
FAB = os.path.join(OUT, "fab")
MM = 1e3
T_BOARD = P.BOARD_T * MM
EDGE_W = 0.1


def new_board():
    b = Board.create_new()
    b.general.thickness = T_BOARD
    return b


def uid():
    return str(uuid.uuid4())


def pos(x, y):
    return Position(X=x, Y=y)


def edge_polygon(b, pts):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        b.graphicItems.append(GrLine(start=pos(x0, y0), end=pos(x1, y1), layer="Edge.Cuts", width=EDGE_W, tstamp=uid()))


def rect(b, layer, x0, y0, x1, y1):
    b.graphicItems.append(GrRect(start=pos(min(x0, x1), min(y0, y1)), end=pos(max(x0, x1), max(y0, y1)), layer=layer, width=0, fill="solid", tstamp=uid()))


def copper_pad(b, layer, x0, y0, x1, y1, exposed=True):
    """A copper rectangle; exposed=True also opens the solder mask over it (bare ENIG)."""
    rect(b, layer, x0, y0, x1, y1)
    if exposed:
        rect(b, layer.replace(".Cu", ".Mask"), x0, y0, x1, y1)


def add_net(b, number, name):
    if not b.nets:
        b.nets.append(Net(number=0, name=""))
    b.nets.append(Net(number=number, name=name))
    return Net(number=number, name=name)


def trace(b, layer, pts, width=0.5, net=0):
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        b.traceItems.append(Segment(start=pos(x0, y0), end=pos(x1, y1), width=width, layer=layer, net=net, tstamp=uid()))


def hole(b, x, y, d, plated=False, ring=None, net=None):
    """A mounting hole (not plated) or a plated wire hole with a copper ring on both faces."""
    fp = Footprint(libraryNickname="mech", entryName="hole", layer="F.Cu", position=pos(x, y), tstamp=uid())
    ring = ring or d + 1.5
    fp.pads.append(Pad(number="1" if plated else "", type="thru_hole" if plated else "np_thru_hole", shape="circle", position=pos(0, 0), size=pos(ring if plated else d, ring if plated else d),
                       drill=DrillDefinition(diameter=d), layers=["*.Cu", "*.Mask"], net=net))
    b.footprints.append(fp)


def silk(b, text, x, y, layer="F.SilkS", size=1.0):
    b.graphicItems.append(GrText(text=text, position=pos(x, y), layer=layer, effects=Effects(font=Font(height=size, width=size, thickness=0.15), justify=Justify(mirror=layer.startswith("B."))), tstamp=uid()))


def save(b, name):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"{name}.kicad_pcb")
    b.to_file(path)
    return path


def Y(z):  # balance z (mm) -> KiCad Y
    return -z


# ---- the arm ---------------------------------------------------------------------------------------------
def arm_board():
    b = new_board()
    L = B.L
    za0, za1, zv = B.ZA0, B.ZA1, B.Z_V
    edge_polygon(b, [(-L, Y(za1)), (L, Y(za1)), (L, Y(za0)), (-L, Y(za0)), (-L, Y(zv - 4)), (-L - 8, Y(zv - 4)), (-L - 8, Y(zv + 4)), (-L, Y(zv + 4))])
    for x in (-5.0, 5.0):
        hole(b, x, Y(za1 - B.CLAMP_H / 2), B.M3_CLEAR)
    hole(b, B.X_BALLAST, Y(B.Z_BALLAST), 10.2)
    for x in (B.X_VANE - 3, B.X_VANE + 3):
        hole(b, x, Y(zv - 4.5), B.M3_CLEAR)
    for dz in (-6.0, 6.0):
        hole(b, B.X_BOLT_DUT, Y(zv + dz), B.M3_CLEAR)
    # +y face (B.Cu): the strip's contact pad, a trace to the moving electrode, the electrode (ENIG)
    copper_pad(b, "B.Cu", -2.8, Y(za1 - 0.5), 2.8, Y(za1 - 12.5))
    ex0, ex1 = B.X_PLATE - 10, B.X_PLATE + 10
    copper_pad(b, "B.Cu", ex0, Y(zv + 4), ex1, Y(zv - 4))
    trace(b, "B.Cu", [(2.0, Y(za1 - 2.0)), (ex0 + 1.0, Y(za1 - 2.0)), (ex0 + 1.0, Y(zv + 4))], 0.6)
    # the flag finger: copper both faces under the black mask, so it is opaque to the infrared LED
    for layer in ("F.Cu", "B.Cu"):
        rect(b, layer, -L - 7.5, Y(zv + 3.5), -L + 0.5, Y(zv - 3.5))
    silk(b, f"ARM v1 {P.BOARD_T*MM:.1f}mm  +y=B.Cu: electrode, strip pad", 0, Y(zv + 8), "F.SilkS")
    silk(b, "device card on this face", B.X_BOLT_DUT - 40, Y(zv - 12), "F.SilkS", 0.8)
    return b


# ---- clamp plates -----------------------------------------------------------------------------------------
def clamp_plate():
    b = new_board()
    edge_polygon(b, [(-8, -7), (8, -7), (8, 7), (-8, 7)])
    for x in (-5.0, 5.0):
        hole(b, x, 0, B.M3_CLEAR)
    silk(b, "CLAMP", 0, 0, "F.SilkS", 0.8)
    return b


def clamp_ground():
    b = new_board()
    gnd = add_net(b, 1, "GND")
    edge_polygon(b, [(-8, -7), (8, -7), (8, 7), (9, 7), (9, 12), (3, 12), (3, 7), (-8, 7)])  # a tab below the strip's line, clear of the strip
    for x in (-5.0, 5.0):
        hole(b, x, 0, B.M3_CLEAR)
    # the strip-facing face of the +y plate is its -y face (F.Cu): an ENIG pad against the strip, a trace to the plated hole in the tab
    copper_pad(b, "F.Cu", -2.8, -6.0, 2.8, 6.0)
    hole(b, 6.0, 9.5, 1.6, plated=True, ring=3.2, net=gnd)
    trace(b, "F.Cu", [(2.0, 5.0), (6.0, 5.0), (6.0, 9.5)], 0.6, net=1)
    silk(b, "GND", 0, 0, "B.SilkS", 0.8)
    return b


# ---- fixed electrode --------------------------------------------------------------------------------------
def elec_board():
    b = new_board()
    guard = add_net(b, 1, "GUARD")
    sig = add_net(b, 2, "SIG")
    # local: X = x - X_PLATE, Y = -(z - Z_V); board z from Z_V-12 to Z_V+22 (a 10 mm tab above the 24 mm body)
    edge_polygon(b, [(-12, -22), (12, -22), (12, 12), (-12, 12)])
    hole(b, -6.0, -17.0, 1.6, plated=True, ring=3.2, net=sig)
    hole(b, 6.0, -17.0, 1.6, plated=True, ring=3.2, net=guard)
    # front face = the -y face = F.Cu: the 20 x 8 pad, its 0.5 mm gap, and the guard (ground) pour around it, all ENIG
    copper_pad(b, "F.Cu", -10, -4, 10, 4)
    g = 0.5
    copper_pad(b, "F.Cu", -11.5, -11.5, 11.5, -4 - g)  # above the pad
    copper_pad(b, "F.Cu", -11.5, 4 + g, 11.5, 11.5)  # below
    copper_pad(b, "F.Cu", -11.5, -4 - g, -10 - g, 4 + g)
    copper_pad(b, "F.Cu", 10 + g, -4 - g, 11.5, 4 + g)
    trace(b, "F.Cu", [(6.0, -11.0), (6.0, -17.0)], 0.8, net=1)  # guard to its wire hole
    # the pad's own wire: a via in the pad to the back face (B.Cu) and a trace to the other wire hole
    b.traceItems.append(Via(position=pos(0, -2.5), size=0.8, drill=0.4, layers=["F.Cu", "B.Cu"], net=2, tstamp=uid()))
    trace(b, "B.Cu", [(0, -2.5), (-6.0, -2.5), (-6.0, -17.0)], 0.6, net=2)
    silk(b, "SIG", -6, -20.0, "B.SilkS", 0.8)
    silk(b, "GUARD", 6, -20.0, "B.SilkS", 0.8)
    silk(b, "ELECTRODE: pad faces the arm", 0, 9.5, "B.SilkS", 0.8)
    return b


BOARDS = {"arm": arm_board, "clamp_plate": clamp_plate, "clamp_ground": clamp_ground, "elec_board": elec_board}


def board_outline_mm(name):
    """Bounding box (x0, y0, x1, y1) of a board's Edge.Cuts lines, mm."""
    b = Board.from_file(os.path.join(OUT, f"{name}.kicad_pcb"))
    xs, ys = [], []
    for it in b.graphicItems:
        if isinstance(it, GrLine) and it.layer == "Edge.Cuts":
            xs += [it.start.X, it.end.X]
            ys += [it.start.Y, it.end.Y]
    return min(xs), min(ys), max(xs), max(ys)


def holes_mm(b):
    """[(x, y, drill)] of every hole of a board object, KiCad coordinates."""
    out = []
    for fp in b.footprints:
        for pad in fp.pads:
            out.append((fp.position.X + pad.position.X, fp.position.Y + pad.position.Y, pad.drill.diameter))
    return out


def weight_estimate_g(name, qty=5):
    """JLC's quoted mass uses the bounding rectangle x thickness: FR4 plus copper (about 1 oz per layer) [assume]."""
    x0, y0, x1, y1 = board_outline_mm(name)
    vol = (x1 - x0) * (y1 - y0) * T_BOARD  # mm^3
    return vol * B.FR4_G_MM3 * qty


def run_fab():
    os.makedirs(FAB, exist_ok=True)
    report = []
    for name in BOARDS:
        path = os.path.join(OUT, f"{name}.kicad_pcb")
        rpt = os.path.join(FAB, f"{name}_drc.json")
        subprocess.run(["kicad-cli", "pcb", "drc", "--format", "json", "--severity-all", "--output", rpt, path], check=False, capture_output=True)
        gdir = os.path.join(FAB, name)
        os.makedirs(gdir, exist_ok=True)
        subprocess.run(["kicad-cli", "pcb", "export", "gerbers", "--output", gdir + "/", "--layers", "F.Cu,B.Cu,F.Mask,B.Mask,F.SilkS,B.SilkS,Edge.Cuts", path], check=False, capture_output=True)
        subprocess.run(["kicad-cli", "pcb", "export", "drill", "--output", gdir + "/", "--format", "excellon", "--drill-origin", "absolute", "--excellon-separate-th", path], check=False, capture_output=True)
        zpath = os.path.join(FAB, f"{name}_gerbers.zip")
        subprocess.run(["zip", "-q", "-j", zpath] + [os.path.join(gdir, f) for f in os.listdir(gdir)], check=False)
        report.append((name, rpt, zpath))
        subprocess.run(["kicad-cli", "pcb", "render", "--output", os.path.join(FAB, f"{name}.png"), "--side", "top", "--width", "1200", "--height", "500", path], check=False, capture_output=True)
    return report


def main():
    for name, fn in BOARDS.items():
        p = save(fn(), name)
        x0, y0, x1, y1 = board_outline_mm(name)
        print(f"{name:13s} {x1 - x0:6.1f} x {y1 - y0:5.1f} mm, ~{weight_estimate_g(name):5.1f} g for 5 -> {p}")
    if "--fab" in sys.argv:
        for name, rpt, z in run_fab():
            print("fab:", name, "->", os.path.relpath(z, HERE))


if __name__ == "__main__":
    main()
