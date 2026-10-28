"""
jlc_parcel_mass.py — estimated mass of each planned JLC parcel against the 0.29 kg line of the cheap Global Standard Direct Line tier (Part I3).

    python3 tools/jlc_parcel_mass.py              # the table
    python3 tools/jlc_parcel_mass.py --combine "mechanical boards" "printed parts"

JLC estimates a board's mass from its bounding rectangle times its thickness (cut-outs and panel gaps count; petertanner.dev, 2024), so that rule is used for every board.
Printed and machined parts: volume of the CAD export (hardware/balance/cad/*.stl) times a density. Packing is calibrated on one data point (the user's quote of 2026-10-28, see PACKING_G); it may depend on the order. The price side (what a parcel costs at a given mass) is not modelled: it comes from the user's quote readings (`TODO-arcticoder.md`).
"""

import os
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
CAD = os.path.join(HERE, "..", "hardware", "balance", "cad")
sys.path.insert(0, os.path.join(HERE, "..", "hardware", "balance"))

LIMIT_G = 300.0  # the cheap tier's cliff is at 0.3 kg (user's quote 2026-10-28: 0.34 kg at 1.6 mm cost C$12.05, under 0.3 kg at 1.2 mm cost C$2.10)
PACKING_G = 155.0  # box, bags and filler of one JLC parcel, from that quote: five 208 x 60 x 1.6 mm arms are 185 g by the rule and the page showed 0.34 kg
FR4_G_CM3 = 1.85
DENSITY = {"PLA": 1.24, "ASA": 1.07, "nylon": 1.01, "resin": 1.15, "aluminium": 2.70}  # g/cm^3 [handbook values; resin varies]


def board_mass_g(w_mm, h_mm, t_mm, qty):
    """JLC's rule: bounding rectangle x thickness x density, per piece, times the pieces."""
    return w_mm * h_mm * t_mm * 1e-3 * FR4_G_CM3 * qty


def stl_volume_cm3(name):
    """Volume of an STL (binary or ASCII) by the signed-tetrahedron sum."""
    path = os.path.join(CAD, name + ".stl")
    data = open(path, "rb").read()
    n = struct.unpack("<I", data[80:84])[0]
    if len(data) == 84 + 50 * n:
        arr = np.frombuffer(data[84:], dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]), count=n)
        tri = arr["v"].astype(float)
    else:
        verts = [list(map(float, ln.split()[1:4])) for ln in data.decode().splitlines() if ln.strip().startswith("vertex")]
        tri = np.array(verts).reshape(-1, 3, 3)
    v = np.einsum("ij,ij->i", tri[:, 0], np.cross(tri[:, 1], tri[:, 2])).sum() / 6.0
    return abs(v) / 1000.0  # mm^3 -> cm^3


def part_mass_g(name, material, qty=1):
    return stl_volume_cm3(name) * DENSITY[material] * qty


def planned_parcels():
    import params as P

    arm_w = 2 * P.ARM_HALF_LENGTH * 1e3 + 8  # the board is the arm plus the finger (ORDER.md: 208 x 60)
    t = P.BOARD_T * 1e3
    arm = [("arm", board_mass_g(arm_w, P.ARM_HEIGHT * 1e3, t, 5))]
    small = [("clamp_ground", board_mass_g(17, 19, t, 5)), ("elec_board", board_mass_g(24, 34, t, 5)), ("clamp_plate", board_mass_g(16, 14, t, 5))]
    prints = [(n, part_mass_g(n, "PLA")) for n in ("head", "gantry", "damper_holder", "vane_holder")]  # candidates for JLC3DP in Part K, material PLA as a placeholder
    return {"arm board": arm, "small boards (3 designs)": small, "printed parts (candidates, PLA)": prints}


def parcel_total(items):
    return sum(m for _, m in items) + PACKING_G


def combined_total(parcels, names):
    """Mass of several orders shipped together (Combine Shipping): one packing allowance for the lot."""
    return sum(m for n in names for _, m in parcels[n]) + PACKING_G


def main():
    parcels = planned_parcels()
    for name, items in parcels.items():
        tot = parcel_total(items)
        print("%-34s %6.0f g with packing  (margin %+.0f g to %.0f g)" % (name, tot, LIMIT_G - tot, LIMIT_G))
        for n, m in items:
            print("    %-16s %6.1f g" % (n, m))
    names = list(parcels)
    c = combined_total(parcels, names)
    print("combined as one parcel (Combine Shipping on for all): %.0f g -> %s" % (c, "OK" if c <= LIMIT_G else "OVER the %.0f g line: ship separately" % LIMIT_G))
    if "--combine" in sys.argv:
        sel = sys.argv[sys.argv.index("--combine") + 1:]
        print("combined %s: %.0f g" % (sel, combined_total(parcels, sel)))


if __name__ == "__main__":
    main()
