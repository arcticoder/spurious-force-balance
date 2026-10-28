"""
check_panel.py — pass/fail checks of the sensor-head panel's committed outputs (Part N): DRC, BOM against the head circuits, panel size, CPL, Gerber set.

    ~/.venvs/lab-hw/bin/python hardware/instrument/heads_panel/check_panel.py
(It reads out/; it does not rebuild: build_panel.py needs Freerouting and takes about 40 s.)
"""

import builtins
import collections
import csv
import json
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "schematic"))
sys.path.insert(0, os.path.join(HERE, ".."))
os.environ.setdefault("KICAD9_SYMBOL_DIR", "/usr/share/kicad/symbols")

import heads  # noqa: E402

OUT = os.path.join(HERE, "out")
failures = []


def check(label, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + label + (": " + detail if detail else ""))
    if not ok:
        failures.append(label)


def head_counts(builder):
    builder()
    return collections.Counter(int(p.fields["LCSC"][1:]) for p in builtins.default_circuit.parts if p.fields.get("LCSC") not in (None, "C0"))


want = collections.Counter()
for builder, copies in ((heads.sensor_head_1, 2), (heads.sensor_head_2, 2)):
    for lcsc, n in head_counts(builder).items():
        want[lcsc] += n * copies
got = collections.Counter()
for row in csv.DictReader(open(os.path.join(OUT, "bom.csv"))):
    got[int(row["LCSC Part #"][1:])] += len(row["Designator"].split(","))
check("the panel's BOM is exactly two head-1 and two head-2 boards from the head circuits (every LCSC number and count)", got == want, "%d parts: %s" % (sum(got.values()), dict(sorted(got.items()))))

drc = json.load(open(os.path.join(OUT, "drc.json")))
errs = collections.Counter(v["type"] for v in drc.get("violations", []) if v["severity"] == "error")
check("DRC: no unconnected nets", not drc.get("unconnected_items"), "%d unconnected" % len(drc.get("unconnected_items", [])))
check("DRC: the only errors are the intentional open board outlines at the tabs (no clearance, short or hole errors)", set(errs) <= {"invalid_outline"}, str(dict(errs)))

import pcbnew  # noqa: E402

bb = pcbnew.LoadBoard(os.path.join(OUT, "heads_panel.kicad_pcb")).GetBoardEdgesBoundingBox()
w, h = pcbnew.ToMM(bb.GetWidth()), pcbnew.ToMM(bb.GetHeight())
check("the panel is at least 70 x 70 mm (Standard PCBA minimum) and inside the cheap-parcel mass budget (5 panels at 1.6 mm under 100 g)", w >= 70 and h >= 70 and w * h * 1.6 * 1.85e-3 * 5 < 100, "%.0f x %.0f mm, %.0f g" % (w, h, w * h * 1.6 * 1.85e-3 * 5))

cpl = list(csv.DictReader(open(os.path.join(OUT, "cpl.csv"))))
check("the placement file lists every BOM designator once", len(cpl) == sum(got.values()) and len({r["Designator"] for r in cpl}) == len(cpl), "%d rows" % len(cpl))
names = zipfile.ZipFile(os.path.join(OUT, "heads_panel_gerbers.zip")).namelist()
need = ["F_Cu", "B_Cu", "F_Mask", "B_Mask", "F_Silkscreen", "Edge_Cuts", ".drl"]
check("the Gerber zip has both copper layers, both masks, silkscreen, the outline and drill files", all(any(n in f for f in names) for n in need), "%d files" % len(names))

print()
if failures:
    print("%d check(s) failed: %s" % (len(failures), failures))
    sys.exit(1)
print("All checks passed.")
