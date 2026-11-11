"""Checks the trace-shape checker itself: one clean board, one with an off-45 segment, one with an acute joint.
Run: ~/.venvs/lab-hw/bin/python hardware/instrument/layout/test_mainboard_geometry.py   (exit 0 = pass)"""
import os, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import mainboard as M
from kiutils.board import Board
from kiutils.items.common import Position
from kiutils.items.brditems import Segment


def seg(a, b):
    return Segment(start=Position(X=a[0], Y=a[1]), end=Position(X=b[0], Y=b[1]), width=0.15, layer="F.Cu", net=1, tstamp=M.uid())


def run(segs):
    b = Board.create_new()
    b.traceItems = [seg(*s) for s in segs]
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "t.kicad_pcb")
        b.to_file(p)
        return M.geometry(pcb=p)


clean = run([((0, 0), (10, 0)), ((10, 0), (15, 5))])                     # 0 deg then 45 deg: a 135-degree interior angle
off45 = run([((0, 0), (10, 3))])                                          # about 16.7 deg
acute = run([((0, 0), (10, 0)), ((10, 0), (0, 0.0001 + 10))])             # hairpin back along the first segment
tee = run([((0, 0), (10, 0)), ((5, 0), (10, 5))])                         # tees into the middle of a segment: known blind spot
ok = (clean == ([], []) and len(off45[0]) == 1 and len(acute[1]) >= 1)
print("clean", clean, "| off45", len(off45[0]), "| acute", len(acute[1]), "| tee joints found", len(tee[1]), "(0 = known blind spot)")
sys.exit(0 if ok else 1)
