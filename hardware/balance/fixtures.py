"""
fixtures.py — printed jigs for cutting the balance's raw materials (no workshop tools needed beyond a hacksaw and a craft knife).

    ~/.venvs/lab-hw/bin/python hardware/balance/fixtures.py

  saw guide:   holds the 10 mm brass rod in a groove under a clamp plate (two M3 screws), with a stop so the hacksaw's kerf falls
               one ballast length (plus 0.5 mm to file off) from the rod's end.
  strip guide: a plate with a 0.8 mm knife slot exactly the strip width from a ridge the shim's straight edge butts against.
  gap gauge:   a 1.00 mm plate that sets the gap between the two calibration electrodes.
"""

import os

import cadquery as cq

import balance as B
import params as P

MM = 1e3
OUT = os.path.join(B.OUT)

ROD_D = 10.0  # mm, brass rod
KERF = 1.4  # mm, slot for a junior hacksaw blade (0.65 mm blade, set teeth)


def saw_guide(ballast_len):
    """Two printed pieces {name: solid}: the base block with a groove, and the clamp plate. x is along the rod."""
    cut_at = ballast_len + 0.5  # from the stop face to the kerf's near wall
    block_len = cut_at + KERF + 14.0  # stop + ballast piece + kerf + rod-side support
    base = B.box(0, block_len, 0, 30, 0, 18)
    base = base.cut(B.cyl_x(15, 18, -1, block_len + 1, ROD_D + 0.3))  # groove: the rod's axis in the block's top face
    # the stop: a wall closing the groove at x = 0 (the rod end butts against it)
    base = base.union(B.box(0, 3, 0, 30, 0, 18)).union(B.box(0, 3, 6, 24, 18, 24))
    stop = 3.0
    x_kerf = stop + cut_at
    base = base.cut(B.box(x_kerf, x_kerf + KERF, -1, 31, 4, 25))  # the saw slot, clear through the block above the floor
    for y in (4.5, 25.5):
        for x in (x_kerf + KERF + 5, stop + 4.0):  # two screws either side of the kerf
            base = base.cut(B.cyl_z(x, y, -1, 19, B.M3_PILOT))
    plate = B.box(stop, block_len, 0, 30, 18, 22).cut(B.box(x_kerf, x_kerf + KERF, -1, 31, 17, 23))
    plate = plate.cut(B.cyl_x(15, 18, -1, block_len + 1, ROD_D + 0.3))
    for y in (4.5, 25.5):
        for x in (x_kerf + KERF + 5, stop + 4.0):
            plate = plate.cut(B.cyl_z(x, y, 17, 23, B.M3_CLEAR))
    return {"fixture_saw_guide_base": base, "fixture_saw_guide_plate": plate}


def strip_guide(width_mm):
    """One plate lying on the shim: a ridge underneath for the shim's straight edge, a knife slot width_mm behind it."""
    fence = 2.0  # mm, ridge thickness
    slot_w = 0.8
    plate = B.box(0, 110, 0, 36, 0.5, 5.5)  # the plate's underside sits 0.5 mm above the board on the ridge
    ridge = B.box(0, 110, 0, fence, 0, 0.5)
    y_far = fence + width_mm  # the slot's far wall: the blade is pressed against it, so the cut falls exactly width_mm from the ridge
    plate = plate.cut(B.box(5, 105, y_far - slot_w, y_far, 0, 6))
    return {"fixture_strip_guide": plate.union(ridge)}, y_far


def gap_gauge():
    """A flat 1.00 mm (PLATE_GAP) gauge with a handle, to set the electrode gap between the arm board and the fixed electrode board."""
    return {"fixture_gap_gauge": B.box(0, 30, 0, P.PLATE_GAP * MM, 0, 20).union(B.box(10, 20, 0, P.PLATE_GAP * MM, 20, 45))}


def build_all():
    bl, by = B.balance_solve()
    parts = {}
    parts.update(saw_guide(bl))
    parts.update(gap_gauge())
    g, y_far = strip_guide(P.STRIP_WIDTH * MM)
    parts.update(g)
    return parts, bl, y_far


def main():
    parts, bl, y_far = build_all()
    os.makedirs(OUT, exist_ok=True)
    for n, solid in parts.items():
        bb = solid.val().BoundingBox()
        cq.exporters.export(solid, os.path.join(OUT, n + ".stl"))
        print(f"  {n:28s} {bb.xlen:.0f} x {bb.ylen:.0f} x {bb.zlen:.0f} mm")
    print(f"saw guide for a {bl:.1f} mm ballast; strip guide: slot wall {y_far - 2.0:.2f} mm from the ridge face")


if __name__ == "__main__":
    main()
